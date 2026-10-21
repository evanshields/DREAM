"""Canonical comps lifecycle regressions with disposable protected SQLite stores."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mono.comps_admission import canonical_packet, protected_transport, assert_binding
from mono.service import MonoService
from store.mono_deal_store import MonoDealStore, MonoConflict
from store.mono_publish_store import MonoPublicationStore
from test_mono_result_evidence import receipt, saved_receipt


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def canonical(tmp_path):
    root = tmp_path / 'revisions' / 'fixture-r1'
    (root / 'model-inputs').mkdir(parents=True)
    packet = raw({'format': 'dream-canonical-comps-v1', 'deal_id': 'fixture'})
    (root / 'model-inputs/comps.json').write_bytes(packet)
    bundle = {'deal_id': 'fixture', 'sources': [{'id': 'comps', 'format': 'json',
        'path': 'model-inputs/comps.json', 'sha256': sha(packet)}]}
    (root / 'model-inputs/source-bundle.json').write_bytes(raw(bundle))
    identity = {key: 'a' * 64 for key in ('deal_sha256', 'map_sha256', 'template_sha256', 'code_sha256')}
    identity.update(bundle_sha256=sha(raw(bundle)), ledger_sha256=None, source_hashes={'comps': sha(packet)})
    record = {'deal_id': 'fixture', 'revision': 1, 'root': str(root), 'identity': identity,
              'bundle_snapshot': bundle}
    store = MonoDealStore(tmp_path / 'protected.sqlite')
    store.register('fixture', record)

    def event(key='first', decision='confirm'):
        current = store.current('fixture')
        value = {'event_id': sha(key.encode())[:32], 'deal_id': 'fixture', 'revision': current['revision'],
            'gate': 'comps', 'decision': decision, 'comps_sha256': identity['source_hashes']['comps'],
            'identity': current['identity'], 'reason': 'Disposable engineering test',
            'actor': {'issuer': 'dream-app', 'subject': 'tester', 'auth_method': 'app_jwt'},
            'at': '2026-10-21T00:00:00+00:00'}
        store.record_gate('fixture', current['revision'], value, key, key)
        return value
    event()
    admission = protected_transport(store, record, tmp_path, create=True)
    result = {'result_id': 'result', 'checks': {'release_passed': True}, 'artifact_sha256': 'b' * 64,
        'identity': {'trusted_comps_sha256': admission['pin']['sha256']},
        'comps_binding': admission['binding']}
    job = {'job_id': 'job', 'deal_id': 'fixture', 'revision': 1, 'state': 'running', 'identity': identity}
    store.add_job('fixture', job)
    return SimpleNamespace(store=store, record=record, root=tmp_path, admission=admission,
                           result=result, event=event)


def complete(c):
    return c.store.update_job('fixture', 'job', {'state': 'complete', 'result': c.result})


def promote(c):
    return c.store.promote_result('fixture', 'job', 1, c.record['identity'])


def go(c):
    event = {'event_id': 'c' * 32, 'gate': 'go_no_go', 'decision': 'go', 'identity': c.record['identity'],
             'result_id': 'result', 'comps_event_id': c.store.gates('fixture')['comps']['event_id']}
    c.store.record_gate('fixture', 1, event, 'go' + event['comps_event_id'], 'go')


def test_transport_is_exact_private_and_readiness_does_not_write(canonical):
    c = canonical
    pin = c.admission['pin']
    path = Path(pin['path'])
    assert path.name == 'comps-approval.json'
    assert not path.is_relative_to(Path(c.record['root']))
    before = {str(p): p.stat().st_mtime_ns for p in c.root.rglob('*') if p.is_file()}
    assert protected_transport(c.store, c.record, c.root) == c.admission
    assert before == {str(p): p.stat().st_mtime_ns for p in c.root.rglob('*') if p.is_file()}
    assert_binding(c.store, c.record, c.admission['binding'])


def test_readiness_refuses_unstaged_export_without_writes(canonical):
    c = canonical
    Path(c.admission['pin']['path']).unlink()
    with pytest.raises(ValueError, match='not staged'):
        protected_transport(c.store, c.record, c.root)
    assert not Path(c.admission['pin']['path']).exists()


def test_pinned_export_mutation_refused(canonical):
    c = canonical
    Path(c.admission['pin']['path']).write_bytes(b'{}')
    with pytest.raises(ValueError, match='transport changed'):
        protected_transport(c.store, c.record, c.root, create=True)


def test_packet_mutation_and_false_snapshot_cannot_admit(canonical):
    c = canonical
    (Path(c.record['root']) / 'model-inputs/comps.json').write_bytes(b'{}')
    with pytest.raises(ValueError, match='bytes changed'):
        canonical_packet(c.record)


@pytest.mark.parametrize('decision', ['confirm', 'refuse'])
def test_latest_event_blocks_completion_and_promotion(canonical, decision):
    c = canonical
    c.event('changed', decision)
    with pytest.raises(ValueError):
        assert_binding(c.store, c.record, c.admission['binding'])
    assert complete(c)['state'] == 'stale'
    assert not promote(c)


def test_reconfirmation_after_completion_cannot_promote(canonical):
    c = canonical
    assert complete(c)['state'] == 'complete'
    c.event('reconfirmed')
    assert not promote(c)


def test_revision_change_during_completion_marks_stale(canonical):
    c = canonical
    c.store.commit_revision('fixture', 1, dict(c.record, revision=2), {}, 'edit', 'edit')
    assert complete(c)['state'] == 'stale'
    assert not promote(c)


@pytest.mark.parametrize('field', ['event_id', 'event_sha256', 'canonical_comps_sha256',
                                 'trusted_comps_sha256', 'revision', 'identity'])
def test_transaction_rejects_detached_binding(canonical, field):
    c = canonical
    c.result['comps_binding'][field] = None
    assert complete(c)['state'] == 'stale'
    assert not promote(c)


def test_missing_binding_cannot_complete(canonical):
    c = canonical
    c.result.pop('comps_binding')
    assert complete(c)['state'] == 'stale'


def test_publication_reconfirmation_cannot_reuse_result_even_with_new_go(canonical):
    c = canonical
    assert complete(c)['state'] == 'complete'
    assert promote(c)
    go(c)
    publications = MonoPublicationStore(c.store)
    assert publications.snapshot('fixture')['result_id'] == 'result'
    c.event('new-review')
    go(c)
    with pytest.raises(MonoConflict, match='confirmation changed'):
        publications.snapshot('fixture')


def test_current_job_refuses_changed_event_before_file_access(canonical):
    c = canonical
    complete(c)
    assert promote(c)
    c.event('new-review')
    service = MonoService.__new__(MonoService)
    service.store = c.store
    service.builder = SimpleNamespace(verify=lambda record: None)
    assert service._current_job(c.record) is None


def test_native_source_identity_includes_direct_comps_and_preserves_legacy(receipt):
    from mono.verification import validate_evidence
    native, record, package = receipt
    record['identity']['source_hashes']['comps'] = 'whole-packet'
    assert validate_evidence(native, record, package)['release_passed']
    record['bundle_snapshot'] = {'sources': [{'id': 'comps', 'format': 'json'}]}
    with pytest.raises(ValueError, match='source identities differ'):
        validate_evidence(native, record, package)
    native['identity']['source_hashes']['comps'] = 'whole-packet'
    assert validate_evidence(native, record, package)['release_passed']


@pytest.mark.parametrize('extra', ['trusted_comps_context', 'trusted_context', 'trusted_comps', 'comps_binding'])
def test_public_calculation_cannot_supply_protected_context(extra):
    from routers.mono import create_router
    app = FastAPI()
    service = SimpleNamespace(calculate=lambda *args: pytest.fail('Public forged context reached service'))
    app.include_router(create_router(service, lambda: {'subject': 'fixture'}), prefix='/api/deals')
    body = {'expected_revision': 1, 'expected_deal_sha256': 'a' * 64, 'idempotency_key': 'request', extra: {}}
    assert TestClient(app).post('/api/deals/fixture/mono/calculations', json=body).status_code == 422


@pytest.mark.parametrize('timing', ['unchanged', 'before_launch', 'after_launch'])
def test_dispatch_uses_only_protected_transport_and_late_rechecks(canonical, receipt, monkeypatch, timing):
    import threading
    from mono import provider as module
    from mono import verification
    c = canonical
    native, _, _ = receipt
    native['comps_binding'] = c.admission['binding']
    native['identity']['trusted_comps_sha256'] = c.admission['pin']['sha256']
    config = SimpleNamespace(data_root=c.root, template=c.root / 'template.xlsx', map_path=c.root / 'map.json',
        capabilities=None, calculator_root=c.root, calculator_python=c.root / 'fake-python', expected_code_sha256='a' * 64)
    (c.root / 'bridge').mkdir()
    provider = module.MonoProvider.__new__(module.MonoProvider)
    provider.config, provider.store = config, c.store
    provider.builder = SimpleNamespace(verify=lambda record: None)
    provider._quarantine_path = c.root / 'quarantine.json'
    provider._closed = threading.Event()
    launched = []
    original_write = module.write_new

    def write(path, value):
        original_write(path, value)
        if Path(path).name == 'envelope.json' and timing == 'before_launch':
            c.event('before-launch')
    monkeypatch.setattr(module, 'write_new', write)

    class Bridge:
        pid = 987654
        def __init__(self, args, **kwargs):
            directory = Path(args[-1])
            registry = json.loads((directory / 'registry.json').read_bytes())
            envelope = json.loads((directory / 'envelope.json').read_bytes())
            assert registry['trusted_comps'] == c.admission['pin']
            assert envelope['trusted_comps_context'] == c.admission['context']
            assert set(envelope['request']) == {'deal_id', 'expected_revision', 'expected_bundle_sha256'}
            launched.append(directory)
            (directory / 'terminal.json').write_bytes(raw(native))
            if timing == 'after_launch':
                c.event('after-launch')
        def poll(self):
            return 0
    monkeypatch.setattr(module.subprocess, 'Popen', Bridge)

    def verified(native, record, config, terminal_path, **kwargs):
        assert kwargs['expected_comps_binding'] == c.admission['binding']
        assert native['comps_binding'] == c.admission['binding']
        return copy.deepcopy(c.result)
    monkeypatch.setattr(verification, 'verified_result', verified)
    if timing == 'before_launch':
        with pytest.raises(ValueError, match='not staged|event changed'):
            provider._run('fixture', 'job', c.record)
        assert not launched
    else:
        provider._run('fixture', 'job', c.record)
        assert len(launched) == 1
        assert c.store.job('fixture', 'job')['state'] == ('complete' if timing == 'unchanged' else 'stale')
        current = c.store.current_result('fixture')
        assert bool(current) == (timing == 'unchanged')


@pytest.mark.parametrize('change', ['missing', 'event', 'transport_identity'])
def test_verified_native_result_rejects_detached_protected_binding(saved_receipt, monkeypatch, change):
    from mono.verification import verified_result
    from mono import comps_admission
    native, record, config, terminal, _ = saved_receipt
    binding = {'trusted_comps_sha256': 'd' * 64, 'event_id': 'e' * 32}
    native['comps_binding'] = copy.deepcopy(binding)
    native['identity']['trusted_comps_sha256'] = 'd' * 64
    if change == 'missing':
        native.pop('comps_binding')
    elif change == 'event':
        native['comps_binding']['event_id'] = 'f' * 32
    else:
        native['identity']['trusted_comps_sha256'] = 'f' * 64
    terminal.write_bytes(raw(native))
    monkeypatch.setattr(comps_admission, 'canonical_packet', lambda record: 'packet-sha')
    with pytest.raises(ValueError, match='protected comps'):
        verified_result(native, record, config, terminal, expected_comps_binding=binding)


def test_verified_native_result_preserves_exact_binding(saved_receipt, monkeypatch):
    from mono.verification import verified_result
    from mono import comps_admission
    native, record, config, terminal, _ = saved_receipt
    binding = {'trusted_comps_sha256': 'd' * 64, 'event_id': 'e' * 32}
    native['comps_binding'] = copy.deepcopy(binding)
    native['identity']['trusted_comps_sha256'] = 'd' * 64
    terminal.write_bytes(raw(native))
    monkeypatch.setattr(comps_admission, 'canonical_packet', lambda record: 'packet-sha')
    result = verified_result(native, record, config, terminal, expected_comps_binding=binding)
    assert result['comps_binding'] == binding
    assert result['comps_binding'] is not binding



def test_same_revision_writer_cannot_change_event_inside_promotion_transaction(canonical, monkeypatch):
    import threading
    c = canonical
    complete(c)
    second = MonoDealStore(c.store.path)
    latest = copy.deepcopy(c.store.gates('fixture')['comps'])
    latest['event_id'] = 'f' * 32
    checked, release, written = threading.Event(), threading.Event(), threading.Event()
    original = MonoDealStore._comps_binding_current
    outcomes = []

    def held(db, current, result):
        accepted = original(db, current, result)
        checked.set()
        assert release.wait(3)
        return accepted
    monkeypatch.setattr(MonoDealStore, '_comps_binding_current', staticmethod(held))
    promoter = threading.Thread(target=lambda: outcomes.append(promote(c)))
    promoter.start()
    assert checked.wait(3)

    def change():
        second.record_gate('fixture', 1, latest, 'concurrent', 'concurrent')
        written.set()
    writer = threading.Thread(target=change)
    writer.start()
    try:
        assert not written.wait(0.1)
    finally:
        release.set()
        promoter.join(3)
        writer.join(3)
    assert not promoter.is_alive() and not writer.is_alive()
    assert outcomes == [True] and written.is_set()
    monkeypatch.setattr(MonoDealStore, '_comps_binding_current', staticmethod(original))
    assert not promote(c)
    with pytest.raises(MonoConflict, match='confirmation changed'):
        MonoPublicationStore(c.store).snapshot('fixture')
