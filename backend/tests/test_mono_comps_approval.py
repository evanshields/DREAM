"""Portable protected-store export checks using real disposable SQLite storage."""
import copy
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from mono.comps_approval import CompsApprovalError, export_comps_approval
from mono.service import MonoService
from store.mono_deal_store import MonoDealStore


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


@pytest.fixture
def evidence(tmp_path):
    root = tmp_path / 'revision'
    (root / 'model-inputs').mkdir(parents=True)
    # Deliberate formatting distinguishes RAW transport from semantic identity.
    # This engineering packet is not a claim of a production adapter schema.
    packet = {'deal_id': 'fixture', 'engineering_packet': {'all_selected_roles': ['a', 'b']}}
    raw = json.dumps(packet, indent=2).encode() + b'\n'
    packet_path = root / 'model-inputs/comps.json'
    packet_path.write_bytes(raw)
    bundle = {'deal_id': 'fixture', 'sources': [{'id': 'comps', 'format': 'json',
              'path': 'model-inputs/comps.json', 'sha256': sha(raw)}]}
    bundle_raw = canonical(bundle)
    (root / 'model-inputs/source-bundle.json').write_bytes(bundle_raw)
    identity = {key: 'a' * 64 for key in ['deal_sha256', 'map_sha256', 'template_sha256', 'code_sha256']}
    identity.update(bundle_sha256=sha(bundle_raw), ledger_sha256=None, source_hashes={'comps': sha(raw)})
    record = {'deal_id': 'fixture', 'revision': 1, 'root': str(root), 'identity': identity}
    store = MonoDealStore(tmp_path / 'protected.sqlite')
    store.register('fixture', record)
    # Exercise the actual existing gate writer. Unrelated calculation/view setup
    # is isolated because comps confirmation does not require a calculation.
    service = MonoService.__new__(MonoService)
    service.store = store
    service.config = SimpleNamespace(permits=lambda deal, actor: deal == 'fixture' and actor['subject'] == 'test-actor')
    service.builder = SimpleNamespace(verify=lambda record: None)
    service.view = lambda deal, actor: {'revision': store.current(deal)['revision'], 'gates': store.gates(deal)}
    actor = {'issuer': 'dream-app', 'subject': 'test-actor', 'auth_method': 'app_jwt', 'email': None}

    def confirm(key='first'):
        current = store.current('fixture')
        return service.gate('fixture', {'expected_revision': current['revision'],
            'expected_deal_sha256': current['identity']['deal_sha256'], 'gate': 'comps', 'decision': 'confirm',
            'reason': 'Disposable engineering review', 'idempotency_key': key,
            'comps_sha256': current['identity']['source_hashes']['comps']}, actor)['operation']['event']

    event = confirm()
    args = {'deal_id': 'fixture', 'expected_revision': 1, 'expected_identity': identity,
            'expected_canonical_comps_sha256': sha(raw)}
    return SimpleNamespace(store=store, record=record, args=args, event=event, confirm=confirm,
                           packet_path=packet_path, bundle=bundle)


def export(evidence, **changes):
    return export_comps_approval(evidence.store, **{**evidence.args, **changes})


def inject(evidence, **changes):
    event = {**copy.deepcopy(evidence.event), **changes}
    event.setdefault('event_id', 'b' * 32)
    evidence.store.record_gate('fixture', 1, event, 'injected', 'injected')


def test_actual_gate_export_is_exact_immutable_and_read_only(evidence):
    before = Path(evidence.store.path).read_bytes()
    exported = export(evidence)
    payload = json.loads(exported.content)
    assert exported.sha256 == sha(exported.content)
    assert payload['event'] == evidence.event
    assert payload['event_sha256'] == sha(canonical(evidence.event))
    assert payload['identity'] == evidence.record['identity']
    assert payload['comps_sha256'] == sha(evidence.packet_path.read_bytes())
    assert payload['artifact']['semantic_sha256'] != payload['comps_sha256']
    assert payload['provenance'] == {'type': 'protected_mono_store', 'writer': 'MonoService.gate'}
    assert payload['release_eligible'] is False
    assert export(evidence) == exported
    assert Path(evidence.store.path).read_bytes() == before
    with pytest.raises(FrozenInstanceError):
        exported.sha256 = 'forged'


def test_newer_revision_refuses_old_confirmation(evidence):
    newer = {**evidence.record, 'revision': 2}
    evidence.store.commit_revision('fixture', 1, newer, {}, 'edit', 'edit')
    with pytest.raises(CompsApprovalError, match='revision'):
        export(evidence)
    with pytest.raises(CompsApprovalError, match='event'):
        export(evidence, expected_revision=2)


def test_whole_packet_mutation_is_detected(evidence):
    evidence.packet_path.write_bytes(evidence.packet_path.read_bytes() + b' ')
    with pytest.raises(CompsApprovalError, match='bytes changed'):
        export(evidence)


def test_current_source_identity_must_equal_server_pinned_packet(evidence):
    with pytest.raises(CompsApprovalError, match='whole canonical packet'):
        export(evidence, expected_canonical_comps_sha256='f' * 64)


@pytest.mark.parametrize('bad', ['', 'a' * 63, 'a' * 65, 'A' * 64, 'g' * 64, None, 1, True])
def test_sha_is_strict(evidence, bad):
    with pytest.raises(CompsApprovalError, match='SHA-256'):
        export(evidence, expected_canonical_comps_sha256=bad)


@pytest.mark.parametrize('bad', [True, 0, '1', 1.0, None])
def test_revision_is_strict(evidence, bad):
    with pytest.raises(CompsApprovalError, match='strict revision'):
        export(evidence, expected_revision=bad)


@pytest.mark.parametrize('change', [
    {'actor': None}, {'actor': {'issuer': 'dream-app', 'subject': 'test-actor'}},
    {'actor': {'issuer': 'dream-app', 'subject': '', 'auth_method': 'app_jwt'}},
    {'actor': {'issuer': [], 'subject': 'test-actor', 'auth_method': 'app_jwt'}},
    {'actor': {'issuer': 'dream-app', 'subject': 'test-actor', 'auth_method': 'app_jwt', 'email': {}}},
    {'event_id': None}, {'event_id': 'caller'}, {'reason': ''}, {'at': 'yesterday'},
    {'at': '2026-13-21T00:00:00+00:00'}, {'at': '2026-10-21T00:00:00'},
    {'decision': 'go'}, {'identity': {}}, {'comps_sha256': 'f' * 64}, {'revision': True},
])
def test_malformed_protected_metadata_cannot_export(evidence, change):
    inject(evidence, **change)
    with pytest.raises(CompsApprovalError):
        export(evidence)


def test_missing_confirmation_cannot_export(evidence):
    store = MonoDealStore(Path(evidence.store.path).with_name('empty.sqlite'))
    store.register('fixture', evidence.record)
    with pytest.raises(CompsApprovalError, match='event'):
        export_comps_approval(store, **evidence.args)


def test_different_deal_is_not_a_confirmation_source(evidence):
    other = {**evidence.record, 'deal_id': 'other'}
    evidence.store.register('other', other)
    with pytest.raises(CompsApprovalError, match='event'):
        export(evidence, deal_id='other')


def test_new_confirmation_supersedes_old_even_after_idempotent_replay(evidence):
    old = export(evidence)
    latest = evidence.confirm('second')
    assert latest['event_id'] != evidence.event['event_id']
    assert evidence.confirm('first')['event_id'] == evidence.event['event_id']
    fresh = export(evidence)
    assert fresh != old
    assert json.loads(fresh.content)['event'] == latest


def test_duplicate_event_identity_cannot_replay_as_new_confirmation(evidence):
    inject(evidence)
    with pytest.raises(CompsApprovalError, match='reused'):
        export(evidence)


def test_caller_json_is_not_a_store_or_alternative_event_input(evidence):
    with pytest.raises(CompsApprovalError, match='handle'):
        export_comps_approval(evidence.event, **evidence.args)
    for name, value in [('event', evidence.event), ('event_id', evidence.event['event_id']), ('confirmed_by', 'evan')]:
        with pytest.raises(TypeError):
            export_comps_approval(evidence.store, **evidence.args, **{name: value})


def test_legacy_group_identity_has_no_direct_packet_source(evidence):
    bundle = copy.deepcopy(evidence.bundle)
    bundle['sources'][0]['id'] = 'legacy'
    raw = canonical(bundle)
    (evidence.packet_path.parent / 'source-bundle.json').write_bytes(raw)
    identity = {**evidence.record['identity'], 'bundle_sha256': sha(raw)}
    newer = {**evidence.record, 'identity': identity, 'revision': 2}
    evidence.store.commit_revision('fixture', 1, newer, {}, 'edit', 'edit')
    evidence.confirm('new')
    with pytest.raises(CompsApprovalError, match='direct whole canonical packet'):
        export(evidence, expected_revision=2, expected_identity=identity)


@pytest.mark.parametrize('raw', [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b'[]', b'\xff'])
def test_strict_packet_parser_refuses_ambiguous_or_nonfinite_json(evidence, raw):
    evidence.packet_path.write_bytes(raw)
    bundle = copy.deepcopy(evidence.bundle)
    bundle['sources'][0]['sha256'] = sha(raw)
    bundle_raw = canonical(bundle)
    (evidence.packet_path.parent / 'source-bundle.json').write_bytes(bundle_raw)
    identity = {**evidence.record['identity'], 'bundle_sha256': sha(bundle_raw), 'source_hashes': {'comps': sha(raw)}}
    evidence.store.commit_revision('fixture', 1, {**evidence.record, 'identity': identity, 'revision': 2}, {}, 'edit', 'edit')
    evidence.confirm('new')
    with pytest.raises(CompsApprovalError, match='JSON'):
        export(evidence, expected_revision=2, expected_identity=identity, expected_canonical_comps_sha256=sha(raw))


def test_observed_confirmation_race_fails_closed(evidence, monkeypatch):
    original = evidence.store.gate_history
    calls = 0

    def history(deal):
        nonlocal calls
        calls += 1
        if calls == 2:
            evidence.confirm('during-read')
        return original(deal)

    monkeypatch.setattr(evidence.store, 'gate_history', history)
    with pytest.raises(CompsApprovalError, match='changed during export'):
        export(evidence)
