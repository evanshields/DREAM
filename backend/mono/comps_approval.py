"""Read-only protected-store evidence for a future canonical comps adapter.

This is a server-only primitive, with no HTTP route or caller-event parser.
Possession of the real protected store is the trust boundary. Actor text in a
JSON document is not authentication. Existing MonoService.gate writes are the
provenance relied on here, subject to the store's existing write protections.

The server must independently validate the canonical packet and choose its
whole-file digest before calling. This module verifies transport identity, not
the packet's financial or seven-artifact semantics. Legacy comparables group
hashes cannot stand in for a directly registered canonical packet.

Public store reads do not provide an atomic snapshot. Repeated reads detect
observed supersession, but consumption needs an atomic current-event recheck
and pinned transport verification. No external admission is implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from store.mono_deal_store import MonoDealStore


class CompsApprovalError(ValueError):
    """Current protected evidence cannot support the requested binding."""


@dataclass(frozen=True)
class CompsApprovalExport:
    """Immutable bytes to pin in a transport artifact, never a release grant."""

    content: bytes
    sha256: str


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, UnicodeError) as exc:
        raise CompsApprovalError('Evidence is not finite canonical JSON') from exc


def _sha(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise CompsApprovalError('An exact lowercase SHA-256 digest is required')
    return value


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and not any(ord(c) < 32 for c in value)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CompsApprovalError('Duplicate JSON keys are not allowed')
        result[key] = value
    return result


def _json(raw):
    def invalid(_):
        raise CompsApprovalError('Nonfinite JSON values are not allowed')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=invalid)
        _canonical(value)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise CompsApprovalError('Strict UTF-8 JSON evidence is required') from exc
    if not isinstance(value, dict):
        raise CompsApprovalError('A JSON object artifact is required')
    return value


def _identity(value):
    required = {'deal_sha256', 'bundle_sha256', 'map_sha256', 'template_sha256',
                'code_sha256', 'ledger_sha256', 'source_hashes'}
    if not isinstance(value, dict) or set(value) != required:
        raise CompsApprovalError('The complete current Mono identity is required')
    for key in required - {'ledger_sha256', 'source_hashes'}:
        _sha(value[key])
    if value['ledger_sha256'] is not None:
        _sha(value['ledger_sha256'])
    if not isinstance(value['source_hashes'], dict) or not value['source_hashes']:
        raise CompsApprovalError('Current source identities are unavailable')
    for key, digest in value['source_hashes'].items():
        if not _text(key):
            raise CompsApprovalError('Source identifiers must be nonempty text')
        _sha(digest)


def _artifact(record, expected):
    root = Path(record.get('root', '')).resolve(strict=True)
    bundle_raw = (root / 'model-inputs/source-bundle.json').read_bytes()
    if hashlib.sha256(bundle_raw).hexdigest() != record['identity']['bundle_sha256']:
        raise CompsApprovalError('Current source bundle bytes changed')
    bundle = _json(bundle_raw)
    if bundle.get('deal_id') != record['deal_id'] or not isinstance(bundle.get('sources'), list):
        raise CompsApprovalError('Source bundle scope is invalid')
    sources = [s for s in bundle['sources'] if isinstance(s, dict) and s.get('id') == 'comps']
    if len(sources) != 1:
        raise CompsApprovalError('A direct whole canonical packet source named comps is required')
    source = sources[0]
    relative = source.get('path')
    if (source.get('format') != 'json' or source.get('sha256') != expected
            or not _text(relative) or '\\' in relative or Path(relative).is_absolute()
            or any(part in {'.', '..'} for part in relative.split('/'))):
        raise CompsApprovalError('Canonical packet source registration is invalid')
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise CompsApprovalError('Canonical packet must be a file within its revision')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise CompsApprovalError('Canonical packet bytes changed')
    packet = _json(raw)
    # Schema and role-inventory checks belong to the forthcoming pinned adapter.
    # This check prevents an explicit contradictory deal label without inventing
    # an unapproved packet format here.
    if 'deal_id' in packet and packet['deal_id'] != record['deal_id']:
        raise CompsApprovalError('Canonical packet identifies a different deal')
    return relative, hashlib.sha256(_canonical(packet)).hexdigest()


def _event(event, record, expected):
    if not isinstance(event, dict):
        raise CompsApprovalError('A current protected comps event is required')
    if (event.get('gate') != 'comps' or event.get('decision') != 'confirm'
            or event.get('deal_id') != record['deal_id']
            or type(event.get('revision')) is not int or event['revision'] != record['revision']
            or event.get('identity') != record['identity'] or event.get('comps_sha256') != expected
            or not isinstance(event.get('event_id'), str)
            or re.fullmatch('[0-9a-f]{32}', event['event_id']) is None
            or not _text(event.get('reason'))):
        raise CompsApprovalError('Current comps event binding is invalid')
    actor = event.get('actor')
    if (not isinstance(actor, dict) or not _text(actor.get('subject'))
            or not _text(actor.get('issuer')) or not _text(actor.get('auth_method'))
            or (actor.get('email') is not None and not _text(actor['email']))
            or set(actor) - {'issuer', 'subject', 'auth_method', 'email'}
            or (actor.get('issuer'), actor.get('auth_method')) not in {
                ('dream-app', 'app_jwt'), ('accounts.google.com', 'google_oidc'),
                ('https://accounts.google.com', 'google_oidc')}):
        raise CompsApprovalError('Protected event actor metadata is incomplete')
    at = event.get('at')
    if not isinstance(at, str) or re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:\+00:00|Z)', at) is None:
        raise CompsApprovalError('Protected event needs an explicit UTC timestamp')
    try:
        datetime.fromisoformat(at.replace('Z', '+00:00'))
    except ValueError as exc:
        raise CompsApprovalError('Protected event timestamp is invalid') from exc
    _canonical(event)


def export_comps_approval(store, *, deal_id, expected_revision, expected_identity,
                          expected_canonical_comps_sha256):
    """Export only the latest current stored confirmation for server-pinned bytes.

    expected_identity and the packet digest must come from trusted server
    context. No supplied event, event ID, actor or confirmed_by is accepted.
    The result is a point-in-time export and must never be used as a standalone
    approval parser or to bypass provider, engine or financial readiness gates.
    """
    if type(store) is not MonoDealStore:
        raise CompsApprovalError('The actual protected MonoDealStore handle is required')
    if not isinstance(deal_id, str) or re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}', deal_id) is None:
        raise CompsApprovalError('A strict deal identifier is required')
    if type(expected_revision) is not int or expected_revision < 1:
        raise CompsApprovalError('A positive strict revision is required')
    expected = _sha(expected_canonical_comps_sha256)
    _identity(expected_identity)
    # Freeze caller context before any I/O. The caller is trusted server code.
    identity = _json(_canonical(expected_identity))
    record = store.current(deal_id)
    if (record.get('deal_id') != deal_id or type(record.get('revision')) is not int
            or record['revision'] != expected_revision or record.get('identity') != identity):
        raise CompsApprovalError('Current revision or identity changed')
    if identity['source_hashes'].get('comps') != expected:
        raise CompsApprovalError('Current comps identity does not bind the whole canonical packet')
    gates = store.gates(deal_id)
    event = gates.get('comps')
    _event(event, record, expected)
    history = store.gate_history(deal_id)
    current_comps = [e for e in history if e.get('gate') == 'comps' and e.get('revision') == expected_revision]
    if not current_comps or current_comps[-1] != event:
        raise CompsApprovalError('The selected confirmation has been superseded')
    if sum(e.get('event_id') == event['event_id'] for e in history) != 1:
        raise CompsApprovalError('Protected event identity was reused')
    try:
        relative, semantic_sha = _artifact(record, expected)
    except (OSError, RuntimeError) as exc:
        raise CompsApprovalError('Current canonical packet is unavailable') from exc
    if (store.current(deal_id) != record or store.gates(deal_id) != gates
            or store.gate_history(deal_id) != history):
        raise CompsApprovalError('Protected state changed during export')
    payload = {
        'format': 'dream-protected-comps-export-v1', 'deal_id': deal_id,
        'revision': expected_revision, 'identity': identity, 'comps_sha256': expected,
        'artifact': {'path': relative, 'sha256': expected, 'semantic_sha256': semantic_sha},
        'event': event, 'event_sha256': hashlib.sha256(_canonical(event)).hexdigest(),
        'provenance': {'type': 'protected_mono_store', 'writer': 'MonoService.gate'},
        'release_eligible': False,
    }
    content = _canonical(payload)
    return CompsApprovalExport(content, hashlib.sha256(content).hexdigest())
