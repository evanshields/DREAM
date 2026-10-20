"""Durable publication requests bound to current Mono results and human gates.

The publisher verifies immutable files and financial claims before completion.
This store owns transactional identity and scope, never business approvals.
"""
from __future__ import annotations

import json

from .mono_deal_store import MonoConflict, MonoNotFound, _json, _load, _TERMINAL


class MonoPublicationStore:
    def __init__(self, deal_store):
        self.deals = deal_store
        with self.deals._connection(write=True) as db:
            db.execute('CREATE TABLE IF NOT EXISTS mono_publications '
                '(job_id TEXT PRIMARY KEY, deal_id TEXT NOT NULL, revision INTEGER NOT NULL, record TEXT NOT NULL, '
                'FOREIGN KEY(deal_id, revision) REFERENCES mono_revisions(deal_id, revision))')
            db.execute('CREATE TABLE IF NOT EXISTS mono_current_publication '
                '(deal_id TEXT PRIMARY KEY, job_id TEXT NOT NULL, '
                'FOREIGN KEY(deal_id) REFERENCES mono_deals(deal_id), '
                'FOREIGN KEY(job_id) REFERENCES mono_publications(job_id))')

    def _snapshot(self, db, deal_id):
        current = self.deals._current(db, deal_id)
        row = db.execute('SELECT current_job_id FROM mono_deals WHERE deal_id=?', (deal_id,)).fetchone()
        if not row[0]:
            raise MonoConflict('Publishing requires a current verified calculation', current['revision'])
        job = self.deals._job(db, deal_id, row[0])
        result = job.get('result')
        if (job['state'] != 'complete' or job.get('cancel_requested') or not isinstance(result, dict)
                or job['revision'] != current['revision'] or job.get('identity') != current['identity']
                or not result.get('checks', {}).get('release_passed') or not result.get('result_id')
                or not result.get('artifact_sha256')):
            raise MonoConflict('Current result is not eligible for publication', current['revision'])
        gates = {}
        for gate, raw in db.execute('SELECT gate, record FROM mono_gates '
                'WHERE deal_id=? AND revision=? ORDER BY sequence', (deal_id, current['revision'])):
            gates[gate] = json.loads(raw)
        comps, go = gates.get('comps'), gates.get('go_no_go')
        expected_comps = current['identity'].get('source_hashes', {}).get('comps')
        if (not expected_comps or not comps or comps.get('decision') != 'confirm'
                or comps.get('comps_sha256') != expected_comps or comps.get('identity') != current['identity']
                or not go or go.get('decision') != 'go' or go.get('identity') != current['identity']
                or go.get('result_id') != result['result_id']
                or go.get('comps_event_id') != comps.get('event_id')
                or not comps.get('event_id') or not go.get('event_id')):
            raise MonoConflict('Publishing requires matching current comps and go reviews', current['revision'])
        return {'revision': current['revision'], 'revision_identity': current['identity'],
                'calculation_job_id': job['job_id'], 'result_id': result['result_id'],
                'result_identity': result.get('identity'), 'artifact_sha256': result['artifact_sha256'],
                'comps_event_id': comps['event_id'], 'go_event_id': go['event_id'],
                'comps_sha256': expected_comps}

    def snapshot(self, deal_id):
        with self.deals._connection() as db:
            return self._snapshot(db, deal_id)

    @staticmethod
    def _job(db, deal_id, job_id):
        record = _load(db.execute('SELECT record FROM mono_publications WHERE deal_id=? AND job_id=?',
                                 (deal_id, job_id)).fetchone())
        if record is None:
            raise MonoNotFound((deal_id, job_id))
        return record

    def claim(self, deal_id, job_record, key, request_digest):
        record = json.loads(_json(job_record))
        if (record.get('deal_id') != deal_id or not record.get('job_id')
                or record.get('state') != 'queued' or not isinstance(record.get('identity'), dict)):
            raise MonoConflict('A scoped immutable queued publication is required')
        with self.deals._connection(write=True) as db:
            self.deals._current(db, deal_id)
            replay = self.deals._replay(db, deal_id, key, 'publish', request_digest)
            if replay is not None:
                return self._job(db, deal_id, replay['job_id']), False
            snapshot = self._snapshot(db, deal_id)
            if record.get('revision') != snapshot['revision'] or record['identity'].get('release') != snapshot:
                raise MonoConflict('Publication inputs changed before dispatch', snapshot['revision'])
            planned = 'source_plan_sha256' in record['identity']
            if planned and any(name in record['identity'] for name in ('projection_sha256','asset_policy_sha256','narrative_sha256')):
                raise MonoConflict('A source plan is not an already compiled projection')
            names = ('renderer_sha256','source_plan_sha256') if planned else (
                'renderer_sha256','projection_sha256','asset_policy_sha256','narrative_sha256')
            for name in names:
                value = record['identity'].get(name)
                if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
                    raise MonoConflict('Publication code and source hashes are required')
            db.execute('INSERT INTO mono_publications VALUES (?, ?, ?, ?)',
                       (record['job_id'], deal_id, record['revision'], _json(record)))
            self.deals._remember(db, deal_id, key, 'publish', request_digest, {'job_id': record['job_id']})
            return record, True

    def job(self, deal_id, job_id):
        with self.deals._connection() as db:
            self.deals._current(db, deal_id)
            return self._job(db, deal_id, job_id)

    def jobs(self, deal_id):
        with self.deals._connection() as db:
            self.deals._current(db, deal_id)
            return [_load(row) for row in db.execute('SELECT record FROM mono_publications '
                'WHERE deal_id=? ORDER BY rowid', (deal_id,))]

    def update(self, deal_id, job_id, changes):
        allowed = {'state', 'package', 'diagnostics', 'updated_at', 'started_at', 'finished_at',
                   'cancel_requested', 'steps', 'elapsed_seconds'}
        if not isinstance(changes, dict) or not set(changes) <= allowed:
            raise MonoConflict('Publication identity and scope are immutable')
        with self.deals._connection(write=True) as db:
            record = self._job(db, deal_id, job_id)
            updated = {**record, **changes}
            if record['state'] in _TERMINAL and updated != record:
                raise MonoConflict('Terminal publication receipts are immutable')
            if updated.get('state') not in {'queued', 'running', 'complete', 'blocked', 'failed', 'cancelled', 'stale', 'interrupted'}:
                raise MonoConflict('Unknown publication state')
            if updated['state'] == 'complete':
                package = updated.get('package')
                if (not isinstance(package, dict) or package.get('identity') != record['identity']
                        or package.get('validation', {}).get('passed') is not True
                        or set(package.get('deliverables', {})) != {'memo', 'onepager', 'deck', 'workbook'}):
                    raise MonoConflict('All four verified deliverables are required for package completion')
                if updated.get('cancel_requested'):
                    raise MonoConflict('Cancelled publication cannot complete')
                if 'source_plan_sha256' in record['identity']:
                    value=package.get('projection_sha256')
                    if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
                        raise MonoConflict('A completed source-plan package needs its actual projection identity')
            db.execute('UPDATE mono_publications SET record=? WHERE deal_id=? AND job_id=?',
                       (_json(updated), deal_id, job_id))
            return updated

    def promote(self, deal_id, job_id):
        with self.deals._connection(write=True) as db:
            record = self._job(db, deal_id, job_id)
            if record['state'] != 'complete' or record.get('cancel_requested') or not record.get('package'):
                return False
            try:
                snapshot = self._snapshot(db, deal_id)
            except MonoConflict:
                return False
            if record['identity']['release'] != snapshot:
                return False
            db.execute('INSERT INTO mono_current_publication VALUES (?, ?) '
                       'ON CONFLICT(deal_id) DO UPDATE SET job_id=excluded.job_id', (deal_id, job_id))
            return True

    def current(self, deal_id):
        with self.deals._connection() as db:
            self.deals._current(db, deal_id)
            row = db.execute('SELECT job_id FROM mono_current_publication WHERE deal_id=?', (deal_id,)).fetchone()
            if row is None:
                return None
            job = self._job(db, deal_id, row[0])
            try:
                snapshot = self._snapshot(db, deal_id)
            except MonoConflict:
                return None
            return job if job['state'] == 'complete' and job['identity']['release'] == snapshot else None

    def recover_interrupted(self):
        changed = []
        with self.deals._connection(write=True) as db:
            for job_id, raw in db.execute('SELECT job_id, record FROM mono_publications').fetchall():
                record = json.loads(raw)
                if record['state'] in _TERMINAL:
                    continue
                record.update(state='interrupted', package=None,
                    diagnostics=[*record.get('diagnostics', []), 'Publisher restarted. No automatic retry or package promotion occurred.'])
                db.execute('UPDATE mono_publications SET record=? WHERE job_id=?', (_json(record), job_id))
                changed.append(job_id)
        return changed
