"""Stage immutable revision bytes before the store publishes their pointer."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil
import uuid

from .config import digest, canonical_hash


def now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def read(path):
    from tools.mono_calc.contracts import read_json
    return read_json(path)


def normalize(entry, entered, unit):
    from tools.deal_file.readiness import _text_id
    from tools.mono_calc.adapters import safe_scalar
    if unit != (entry.get('unit') or ''):
        raise ValueError('Unit does not match the registered field')
    if entered is None:
        return None
    if isinstance(entered, bool):
        raise ValueError('Use the workbook selector or a number rather than a Boolean')
    if entry.get('dropdown'):
        if isinstance(entered, str):
            matches = [option for option in entry['dropdown'] if str(option) == entered]
            if len(matches) == 1:
                entered = matches[0]
        if entered not in entry['dropdown']:
            raise ValueError('Value is outside the registered workbook choices')
        return entered
    if entry.get('type') == 'text' or unit == 'text' or _text_id(entry['id']):
        if not isinstance(entered, str) or not safe_scalar(entered):
            raise ValueError('A safe text value is required')
        return entered
    if isinstance(entered, str):
        text = entered.strip()
        if not text:
            raise ValueError('Use explicit null to clear a field')
        if unit == 'date' and len(text) == 10 and text[4] == '-' and text[7] == '-':
            from datetime import date
            return (date.fromisoformat(text) - date(1899, 12, 30)).days
        percent = text.endswith('%')
        if percent and unit not in ('rate', '%'):
            raise ValueError('A percentage cannot be used in this unit')
        text = text.removesuffix('%').replace(',', '')
        if text.startswith('$'):
            if not unit.startswith('$') and unit not in ('usd', 'usd_per_unit', 'usd_per_sf'):
                raise ValueError('Currency does not match this field')
            text = text[1:]
        try:
            entered = float(text)
        except ValueError as exc:
            raise ValueError('A finite numeric value is required') from exc
        if percent:
            entered = entered / 100
    if not isinstance(entered, (int, float)) or not math.isfinite(entered):
        raise ValueError('A finite numeric value is required')
    if unit in ('count', 'months', 'years') and int(entered) != entered:
        raise ValueError('A whole number is required in this unit')
    if not safe_scalar(entered):
        raise ValueError('Unsafe workbook value')
    return entered


class RevisionBuilder:
    def __init__(self, config):
        self.config = config
        for folder in ('revisions', 'trusted', 'calculations', 'bridge'):
            (config.data_root / folder).mkdir(parents=True, exist_ok=True)

    def _identity(self, root, ledger):
        from tools.mono_calc.executor import code_identity
        from tools.mono_calc.contracts import safe_file
        self.config.verify_pins(code_identity())
        bundle = read(root / 'model-inputs/source-bundle.json')
        hashes = {}
        for source in bundle['sources']:
            value = digest(safe_file(root, source['path']))
            if value != source['sha256']:
                raise ValueError('Registered source bytes changed')
            hashes[source['id']] = value
        comps = bundle.get('groups', {}).get('comparables')
        if comps and comps.get('source_id') in hashes:
            hashes.setdefault('comps', canonical_hash({'group': comps, 'source_sha256': hashes[comps['source_id']]}))
        if ledger:
            if digest(ledger['path']) != ledger['sha256']:
                raise ValueError('Registered trusted decision ledger changed')
        return {'deal_sha256': digest(root / 'model-inputs/deal-file.json'),
                'bundle_sha256': digest(root / 'model-inputs/source-bundle.json'),
                'map_sha256': self.config.map_sha256, 'template_sha256': self.config.template_sha256,
                'code_sha256': self.config.expected_code_sha256, 'ledger_sha256': ledger['sha256'] if ledger else None,
                'source_hashes': hashes}

    def verify(self, record):
        identity = self._identity(Path(record['root']), record.get('trusted_rulings'))
        if identity != record['identity']:
            raise ValueError('The registered revision identity changed')
        return identity

    def _copy_sources(self, source_root, destination, bundle):
        from tools.mono_calc.contracts import safe_file
        for source in bundle['sources']:
            source_path = safe_file(source_root, source['path'])
            target = safe_file(destination, source['path'], must_exist=False)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError('Duplicate staged source target')
            shutil.copyfile(source_path, target)
            if digest(target) != source['sha256']:
                raise ValueError('Staged source identity changed')

    def initial(self, deal_id, registration):
        from tools.mono_calc.contracts import identifier
        identifier(deal_id)
        source = Path(registration['root'])
        doc = read(source / 'model-inputs/deal-file.json')
        bundle = read(source / 'model-inputs/source-bundle.json')
        if doc['slug'] != deal_id or bundle['deal_id'] != deal_id:
            raise ValueError('Registered deal identity differs from its source document')
        root = self.config.data_root / 'revisions' / (deal_id + '-r1-' + uuid.uuid4().hex)
        root.mkdir()
        self._copy_sources(source, root, bundle)
        write_new(root / 'model-inputs/deal-file.json', doc)
        write_new(root / 'model-inputs/source-bundle.json', dict(bundle, deal_revision=digest(root / 'model-inputs/deal-file.json')))
        ledger = None
        if registration.get('trusted_rulings'):
            original = registration['trusted_rulings']
            if digest(original['path']) != original['sha256']:
                raise ValueError('Initial trusted ledger identity changed')
            ledger_path = self.config.data_root / 'trusted' / (uuid.uuid4().hex + '.json')
            write_new(ledger_path, read(original['path']))
            ledger = {'path': str(ledger_path), 'sha256': digest(ledger_path)}
        return {'deal_id': deal_id, 'revision': 1, 'root': str(root), 'trusted_rulings': ledger,
                'identity': self._identity(root, ledger), 'doc_snapshot': doc, 'bundle_snapshot': bundle, 'created_at': now()}

    def edit(self, current, field_id, entered, unit, reason, actor, request_id):
        from tools.deal_file.core import load_map, validate
        self.verify(current)
        mapping = {e['id']: e for e in load_map(self.config.map_path)}
        if field_id not in mapping:
            raise ValueError('Unknown registered assumption')
        value = normalize(mapping[field_id], entered, unit)
        source_root = Path(current['root'])
        doc = read(source_root / 'model-inputs/deal-file.json')
        bundle = read(source_root / 'model-inputs/source-bundle.json')
        a = next(a for a in doc['assumptions'] if a['id'] == field_id)
        if (a['source']['type'] == 'evan_override'
            and actor['issuer'] + '|' + actor['subject'] not in self.config.evan_principals):
            raise PermissionError('Existing Evan rulings require Evan-specific supersession authority')
        ledger = read(current['trusted_rulings']['path']) if current.get('trusted_rulings') else {'format': 'dream-trusted-rulings-v2', 'records': []}
        records = ledger['records']
        prior = [r for r in records if (r['deal_id'], r['assumption_id']) == (doc['slug'], field_id)]
        event = {'format': 'dream-authenticated-decision-v1', 'decision_id': 'decision-' + uuid.uuid4().hex,
                 'deal_id': doc['slug'], 'assumption_id': field_id, 'old': a['value'], 'new': value, 'unit': a.get('unit'),
                 'reason': reason, 'actor': copy.deepcopy(actor), 'parent_revision': current['revision'],
                 'revision': current['revision'] + 1, 'request_id': request_id, 'at': now(),
                 'supersedes': prior[0]['decision_id'] if prior else None}
        root = self.config.data_root / 'revisions' / (doc['slug'] + '-r' + str(event['revision']) + '-' + uuid.uuid4().hex)
        root.mkdir()
        self._copy_sources(source_root, root, bundle)
        event_path = 'model-inputs/decisions/' + event['decision_id'] + '.json'
        write_new(root / event_path, event)
        a.update(value=value, source={'type': 'authenticated_human_override', 'detail': reason}, changed_by=actor['subject'],
                 changed_at=event['at'], bucket='B', supplied=True, applicability='applies')
        a.pop('missing_reason', None)
        doc['history'].append({'id': field_id, 'old': event['old'], 'new': value, 'by': actor['subject'], 'at': event['at'], 'reason': reason})
        if validate(doc):
            raise ValueError('Edited deal does not satisfy the deal-file schema')
        write_new(root / 'model-inputs/deal-file.json', doc)
        source_id = event['decision_id']
        bundle['sources'].append({'id': source_id, 'path': event_path, 'sha256': digest(root / event_path), 'format': 'json',
                                  'as_of': event['at'][:10], 'extraction_version': 'dream-authenticated-decision-v1'})
        bundle['claims'][field_id] = {'source_id': source_id, 'locator': {'pointer': ''}}
        bundle['deal_revision'] = digest(root / 'model-inputs/deal-file.json')
        write_new(root / 'model-inputs/source-bundle.json', bundle)
        record = {'decision_id': event['decision_id'], 'deal_id': doc['slug'], 'assumption_id': field_id, 'value': value,
                  'reason': reason, 'provenance': {'type': 'authenticated_decision', 'event': event, 'event_sha256': canonical_hash(event)}}
        new_ledger = {'format': 'dream-trusted-rulings-v2', 'records': [r for r in records if r not in prior] + [record]}
        ledger_path = self.config.data_root / 'trusted' / (uuid.uuid4().hex + '.json')
        write_new(ledger_path, new_ledger)
        trusted = {'path': str(ledger_path), 'sha256': digest(ledger_path)}
        self.verify(current)
        return {'deal_id': doc['slug'], 'revision': event['revision'], 'root': str(root), 'trusted_rulings': trusted,
                'identity': self._identity(root, trusted), 'doc_snapshot': doc, 'bundle_snapshot': bundle, 'created_at': now()}, event
