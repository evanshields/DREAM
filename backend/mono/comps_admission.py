"""Server-owned canonical comps transport and exact-event lifecycle checks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .comps_approval import export_comps_approval, assert_current_comps_approval, _json


def canonical_packet(record):
    """Select canonical admission only from pinned registered bundle and packet bytes."""
    if not any(s.get('id') == 'comps' for s in record.get('bundle_snapshot', {}).get('sources', [])):
        return None
    root = Path(record['root']).resolve(strict=True)
    raw = (root / 'model-inputs/source-bundle.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['identity']['bundle_sha256']:
        raise ValueError('Registered source bundle changed')
    bundle = _json(raw)
    matches = [s for s in bundle.get('sources', []) if s.get('id') == 'comps']
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError('Duplicate direct comps sources')
    source = matches[0]
    if source.get('format') != 'json':
        return None
    path = (root / source['path']).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError('Canonical comps source escaped revision')
    packet_raw = path.read_bytes()
    sha = hashlib.sha256(packet_raw).hexdigest()
    if sha != source['sha256'] or sha != record['identity']['source_hashes'].get('comps'):
        raise ValueError('Registered canonical comps bytes changed')
    packet = _json(packet_raw)
    return sha if packet.get('format') == 'dream-canonical-comps-v1' else None


def protected_transport(store, record, data_root, *, create=False):
    packet_sha = canonical_packet(record)
    if packet_sha is None:
        return None
    receipt = export_comps_approval(store, deal_id=record['deal_id'],
        expected_revision=record['revision'], expected_identity=record['identity'],
        expected_canonical_comps_sha256=packet_sha)
    payload = json.loads(receipt.content)
    path = Path(data_root).resolve() / 'trusted' / 'comps' / receipt.sha256 / 'comps-approval.json'
    if path.is_relative_to(Path(record['root']).resolve()):
        raise ValueError('Trusted comps transport must be outside revision roots')
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open('xb') as stream:
                stream.write(receipt.content)
        except FileExistsError:
            pass
    if not path.is_file():
        raise ValueError('Canonical comps confirmation transport is not staged. Calculate to stage protected admission')
    if path.read_bytes() != receipt.content:
        raise ValueError('Pinned protected comps transport changed')
    return {'pin': {'path': str(path), 'sha256': receipt.sha256},
            'context': {'expected_revision': record['revision'], 'identity': record['identity']},
            'binding': {'event_id': payload['event']['event_id'], 'event_sha256': payload['event_sha256'],
                'canonical_comps_sha256': packet_sha, 'trusted_comps_sha256': receipt.sha256,
                'revision': record['revision'], 'identity': record['identity'],
                'historical_snapshot': True, 'release_eligible': False}}


def assert_binding(store, record, binding):
    if not isinstance(binding, dict):
        raise ValueError('Canonical result lacks protected comps binding')
    receipt = assert_current_comps_approval(store, deal_id=record['deal_id'],
        expected_revision=record['revision'], expected_identity=record['identity'],
        expected_canonical_comps_sha256=binding.get('canonical_comps_sha256'),
        expected_event_id=binding.get('event_id'), expected_event_sha256=binding.get('event_sha256'))
    if receipt.sha256 != binding.get('trusted_comps_sha256'):
        raise ValueError('Protected comps export identity changed')
