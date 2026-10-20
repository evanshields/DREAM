"""Authenticated revision orchestration. No financial formulas or default fills."""
from __future__ import annotations

import copy
from pathlib import Path
import uuid

from fastapi import HTTPException
from store.mono_deal_store import MonoDealStore, MonoConflict, MonoNotFound
from .config import canonical_hash, digest
from .provider import MonoProvider
from .revisions import RevisionBuilder, now, read, edit_prefill


def public(value):
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items() if not k.startswith('_')}
    if isinstance(value, list):
        return [public(v) for v in value]
    return value


class MonoService:
    def __init__(self, config, *, start_provider=True):
        self.config = config
        config.load_calculator()
        self.builder = RevisionBuilder(config)
        self.store = MonoDealStore(config.data_root / 'mono.sqlite')
        for deal_id, registration in config.registrations.items():
            try:
                self.store.current(deal_id)
            except MonoNotFound:
                self.store.register(deal_id, self.builder.initial(deal_id, registration))
        self.provider = MonoProvider(config, self.store, self.builder) if start_provider else None
        from .publication_service import PublicationService
        try:
            self.publications = PublicationService(self, start_provider=start_provider)
        except Exception:
            if self.provider:
                self.provider.close()
                self.provider._thread.join(timeout=5)
            raise

    def _record(self, deal_id, actor):
        if not self.config.permits(deal_id, actor):
            raise HTTPException(403, 'This identity is not associated with this Mono deal')
        try:
            return self.store.current(deal_id)
        except MonoNotFound:
            raise HTTPException(404, 'Mono deal is not registered')

    @staticmethod
    def _conflict(exc):
        raise HTTPException(409, {'code': 'revision_conflict', 'message': str(exc), 'current_revision': exc.current_revision})

    def _expected(self, record, body):
        if body['expected_revision'] != record['revision'] or body['expected_deal_sha256'] != record['identity']['deal_sha256']:
            raise HTTPException(409, {'code': 'revision_conflict', 'message': 'Read the newer revision before saving', 'current_revision': record['revision']})
        try:
            self.builder.verify(record)
        except ValueError as exc:
            raise HTTPException(409, {'code': 'stale_input', 'message': str(exc), 'current_revision': record['revision']})

    def _prepared(self, record):
        from tools.deal_file.core import load_map
        from tools.mono_calc.contracts import Registry
        from tools.mono_calc.executor import _capability
        from tools.mono_calc.sources import prepare
        self.builder.verify(record)
        root = Path(record['root'])
        doc, bundle = read(root / 'model-inputs/deal-file.json'), read(root / 'model-inputs/source-bundle.json')
        config = self.config
        registry = Registry({record['deal_id']: root}, config.data_root / 'calculations', config.template, config.map_path,
                            config.capabilities, record.get('trusted_rulings'))
        mapping = load_map(config.map_path)
        prepared = prepare(doc, bundle, root, mapping, hybrid_proven=_capability(registry, 'hybrid'),
                           trusted_rulings=read(record['trusted_rulings']['path']) if record.get('trusted_rulings') else None)
        return doc, bundle, mapping, prepared

    def _current_job(self, record):
        job = self.store.current_result(record['deal_id'])
        if not job or job['revision'] != record['revision'] or job['identity'] != record['identity']:
            return None
        try:
            self.builder.verify(record)
            result = job['result']
            if digest(result['_artifact']) != result['artifact_sha256']:
                return None
            receipt = read(result['_native_receipt'])
            if receipt['identity'] != result['identity'] or receipt['outputs'] != result['outputs']:
                return None
        except (ValueError, OSError, KeyError):
            return None
        return job

    def view(self, deal_id, actor):
        record = self._record(deal_id, actor)
        valid = True
        try:
            doc, bundle, mapping, prepared = self._prepared(record)
        except (ValueError, OSError) as exc:
            from tools.deal_file.core import load_map
            valid = False
            doc, bundle = record['doc_snapshot'], record['bundle_snapshot']
            mapping = load_map(self.config.map_path)
            prepared = {'ready': False, 'problems': ['Registered evidence is stale: ' + str(exc)], 'applicability': {}}
        entries = {e['id']: e for e in mapping}
        assumptions = []
        by = {a['id']: a for a in doc['assumptions']}
        initial = {a['id']: a for a in self.store.revisions(deal_id)[0]['doc_snapshot']['assumptions']}
        for id_, entry in entries.items():
            a = copy.deepcopy(by.get(id_, {'id': id_, 'value': None, 'bucket': 'D', 'source': {}, 'missing_reason': 'Mapped input absent from registered deal'}))
            verified = prepared['applicability'].get(id_, {'status': 'unresolved', 'reason': 'Verified context is unavailable'})
            reasons = [p for p in prepared['problems'] if p.startswith(id_ + ':')]
            source = dict(a.get('source') or {})
            source.update(locator=bundle.get('claims', {}).get(id_, {}).get('locator'),
                          evidence=prepared.get('evidence', {}).get(id_),
                          initially_recorded_value=initial.get(id_, {}).get('value'))
            assumptions.append({**a, 'edit_value': edit_prefill(a.get('value'), a.get('unit') or entry.get('unit')),
                'label': a.get('label') or entry.get('label') or id_, 'group': entry.get('group') or 'Other inputs',
                'unit': a.get('unit') or entry.get('unit') or '', 'verified_applicability': verified,
                'source': source,
                'missing_reasons': reasons or ([a['missing_reason']] if a.get('missing_reason') else []),
                'history': [h for h in doc.get('history', []) if h.get('id') == id_]})
        current = self._current_job(record) if valid else None
        gates = self.store.gates(deal_id)
        go = gates.get('go_no_go') or {}
        comps = gates.get('comps') or {}
        if (not valid or go.get('decision') == 'go' and (
            not current or go.get('result_id') != current['result']['result_id']
            or go.get('comps_event_id') != comps.get('event_id'))):
            gates['go_no_go'] = None
        decision = (gates.get('go_no_go') or {}).get('decision')
        gates['status'] = 'approved' if decision == 'go' else 'no_go' if decision == 'no_go' else 'awaiting_cp1'
        jobs = []
        for job in self.store.jobs(deal_id):
            jobs.append(public(dict(job, is_current=bool(current and current['job_id'] == job['job_id']))))
        name = doc.get('name', deal_id)
        if self.config.registrations[deal_id].get('engineering_fixture'):
            name = 'Engineering fixture: ' + name
        return {'contract_version': 1, 'deal_id': deal_id, 'name': name, 'revision': record['revision'],
                'identity': record['identity'], 'assumptions': assumptions,
                'readiness': {'ready': bool(valid and prepared['ready']), 'recorded_d_count': sum(a.get('bucket') == 'D' for a in doc['assumptions']),
                    'unverified_field_count': sum(a['verified_applicability']['status'] == 'unresolved' for a in assumptions),
                    'diagnostic_count': len(prepared['problems']), 'problems': prepared['problems']},
                'gates': gates, 'current_result': public(current['result']) if current else None, 'jobs': jobs,
                'narrative': {'status': 'disabled', 'provider': 'none', 'revision': record['revision'], 'text': 'Live judgment has not been enabled or verified.', 'references': []},
                'can_edit': valid}

    def edit(self, deal_id, body, actor):
        record = self._record(deal_id, actor)
        request_digest = canonical_hash({'request': body, 'actor': actor})
        try:
            replay = self.store.idempotent_result(deal_id, body['idempotency_key'], 'edit', request_digest)
            if replay is not None:
                event = next(e for e in self.store.decisions(deal_id) if e['revision'] == replay['revision'])
                return self._operation_view(deal_id, actor, 'edit', event, True)
            self._expected(record, body)
            if not body['reason'].strip():
                raise HTTPException(422, 'A reason is required')
            revised, decision = self.builder.edit(record, body['field_id'], body['entered_value'], body['unit'], body['reason'], actor, body['idempotency_key'])
            committed = self.store.commit_revision(deal_id, record['revision'], revised, decision, body['idempotency_key'], request_digest)
            event = next(e for e in self.store.decisions(deal_id) if e['revision'] == committed['revision'])
        except MonoConflict as exc:
            self._conflict(exc)
        except PermissionError as exc:
            raise HTTPException(403, str(exc))
        except ValueError as exc:
            raise HTTPException(422, str(exc))
        return self._operation_view(deal_id, actor, 'edit', event, False)

    def _operation_view(self, deal_id, actor, kind, event, replayed):
        view = self.view(deal_id, actor)
        view['operation'] = {'kind': kind, 'event': public(event), 'applied_revision': event['revision'],
                             'current_revision': view['revision'], 'replayed': replayed}
        return view

    def calculate(self, deal_id, body, actor):
        record = self._record(deal_id, actor)
        request_digest = canonical_hash({'request': body, 'actor': actor})
        try:
            replay = self.store.idempotent_result(deal_id, body['idempotency_key'], 'calculate', request_digest)
        except MonoConflict as exc:
            self._conflict(exc)
        if replay is not None:
            return self.job(deal_id, replay['job_id'], actor)
        self._expected(record, body)
        if not self.provider:
            raise HTTPException(503, 'Native calculator is not running')
        from engine_boundary import submit_mono_calculation
        try:
            return submit_mono_calculation(self.provider, deal_id, record,
                idempotency_key=body['idempotency_key'], request_digest=request_digest)
        except MonoConflict as exc:
            self._conflict(exc)
        except ValueError as exc:
            raise HTTPException(409, {'code': 'stale_input', 'message': str(exc), 'current_revision': record['revision']})

    def job(self, deal_id, job_id, actor):
        record = self._record(deal_id, actor)
        try:
            job = self.store.job(deal_id, job_id)
        except MonoNotFound:
            raise HTTPException(404, 'No calculator job for this deal')
        current = self._current_job(record)
        return public(dict(job, is_current=bool(current and current['job_id'] == job_id)))

    def cancel(self, deal_id, job_id, actor):
        self.job(deal_id, job_id, actor)
        if not self.provider:
            raise HTTPException(503, 'Native calculator is not running')
        self.provider.cancel(deal_id, job_id)
        return self.job(deal_id, job_id, actor)

    def gate(self, deal_id, body, actor):
        record = self._record(deal_id, actor)
        request_digest = canonical_hash({'request': body, 'actor': actor})
        try:
            replay = self.store.idempotent_result(deal_id, body['idempotency_key'], 'gate', request_digest)
            if replay is not None:
                return self._operation_view(deal_id, actor, 'gate', replay, True)
            self._expected(record, body)
            if not body['reason'].strip():
                raise HTTPException(422, 'A review reason is required')
            view = self.view(deal_id, actor)
            if body['gate'] == 'comps':
                expected = record['identity']['source_hashes'].get('comps')
                if body['decision'] != 'confirm' or not expected or body.get('comps_sha256') != expected:
                    raise HTTPException(409, 'Confirm the current comparables source identity')
            elif body['decision'] == 'go':
                result, comps = view['current_result'], view['gates'].get('comps')
                if (not view['readiness']['ready'] or not result or not comps or comps['decision'] != 'confirm'
                    or result['result_id'] != body.get('result_id') or not result['checks'].get('release_passed')):
                    raise HTTPException(409, 'A go decision requires current verified results and confirmed comps')
            elif body['decision'] != 'no_go':
                raise HTTPException(422, 'Invalid decision for this gate')
            event = {'event_id': uuid.uuid4().hex, 'deal_id': deal_id, 'revision': record['revision'],
                     'gate': body['gate'], 'decision': body['decision'], 'reason': body['reason'], 'actor': actor,
                     'at': now(), 'identity': record['identity'], 'comps_sha256': body.get('comps_sha256'),
                     'result_id': body.get('result_id'), 'comps_event_id': (view['gates'].get('comps') or {}).get('event_id')}
            self.builder.verify(record)
            self.store.record_gate(deal_id, record['revision'], event, body['idempotency_key'], request_digest)
        except MonoConflict as exc:
            self._conflict(exc)
        return self._operation_view(deal_id, actor, 'gate', event, False)
