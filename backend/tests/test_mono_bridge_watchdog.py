"""A stuck bridge cannot publish success or silently release its dispatcher."""
from threading import Event
import time
from types import SimpleNamespace

import pytest

import mono.provider as provider_module
from mono.provider import wait_for_bridge
from store.mono_deal_store import MonoConflict, MonoDealStore


class Process:
    pid = 987654

    def __init__(self, clock, exit_at):
        self.clock, self.exit_at = clock, exit_at

    def poll(self):
        return 0 if self.clock[0] >= self.exit_at else None

    def terminate(self):
        raise AssertionError('Never terminate a bridge with uncertain Excel ownership')


def test_deadline_cancels_then_quarantines_but_keeps_waiting_for_owned_bridge(tmp_path):
    clock, observed = [0], []
    process = Process(clock, 20)

    def advance(_):
        clock[0] += 1

    quarantined = wait_for_bridge(process, tmp_path, lambda: False,
        lambda reason: observed.append((clock[0], reason, process.poll())),
        timeout=5, cancel_grace=3, clock=lambda: clock[0], sleep=advance)
    assert quarantined is True
    assert (tmp_path / 'cancel-requested').exists()
    assert len(observed) == 1
    assert observed[0][0] == 8
    assert observed[0][2] is None
    assert 'cleanup' in observed[0][1].lower()
    assert clock[0] == 20


def test_human_cancellation_has_its_own_grace_instead_of_full_job_timeout(tmp_path):
    clock, observed = [0], []
    (tmp_path / 'cancel-requested').touch()
    process = Process(clock, 10)

    def advance(_):
        clock[0] += 1

    assert wait_for_bridge(process, tmp_path, lambda: False,
        lambda reason: observed.append(clock[0]), timeout=1000, cancel_grace=3,
        clock=lambda: clock[0], sleep=advance)
    assert observed == [3]


def test_clean_cancellation_or_normal_exit_never_quarantines(tmp_path):
    clock, observed = [0], []

    def advance(_):
        clock[0] += 1

    assert not wait_for_bridge(Process(clock, 2), tmp_path, lambda: True,
        observed.append, timeout=100, cancel_grace=3,
        clock=lambda: clock[0], sleep=advance)
    assert observed == []
    assert (tmp_path / 'cancel-requested').exists()


def test_hung_bridge_fails_job_and_persists_restart_latch_without_killing_parent(tmp_path, monkeypatch):
    (tmp_path / 'bridge').mkdir()
    stop = Event()
    store = MonoDealStore(tmp_path / 'mono.sqlite')
    record = {'revision': 1, 'identity': {'deal_sha256': 'engineering-fixture', 'bundle_sha256': 'bundle'},
              'root': str(tmp_path)}
    store.register('fixture', record)
    config = SimpleNamespace(data_root=tmp_path, calculator_root=tmp_path,
        calculator_python=tmp_path / 'not-executed', template=tmp_path / 'not-opened.xlsx',
        map_path=tmp_path / 'not-read.json', capabilities=None, expected_code_sha256='fixture')
    builder = SimpleNamespace(verify=lambda record: None)

    class HungProcess:
        pid = 987654

        def poll(self):
            return 0 if stop.is_set() else None

        def terminate(self):
            raise AssertionError('Bridge must remain owned during unverified cleanup')

    monkeypatch.setattr(provider_module.subprocess, 'Popen', lambda *args, **kwargs: HungProcess())
    original_wait = wait_for_bridge
    monkeypatch.setattr(provider_module, 'wait_for_bridge',
        lambda process, directory, closing, quarantine: original_wait(
            process, directory, closing, quarantine, timeout=0, cancel_grace=0))
    provider = provider_module.MonoProvider(config, store, builder)
    try:
        job = provider.submit('fixture', record)
        deadline = time.monotonic() + 5
        while store.job('fixture', job['job_id'])['state'] != 'failed':
            assert time.monotonic() < deadline
            time.sleep(.01)
        failed = store.job('fixture', job['job_id'])
        assert failed['result'] is None
        assert (tmp_path / 'dispatcher-quarantine.json').is_file()
        assert provider._thread.is_alive()
        assert not provider._lease.closed
        with pytest.raises(MonoConflict, match='cleanup'):
            provider.submit('fixture', record)
        with pytest.raises(RuntimeError, match='owns'):
            provider_module.MonoProvider(config, store, builder)
    finally:
        provider.close()
        stop.set()
        provider._thread.join(timeout=5)
    assert not provider._thread.is_alive()
    assert provider._lease.closed
    assert store.job('fixture', job['job_id'])['state'] == 'failed'
    # An eventual parent exit alone does not prove Excel cleanup.
    reopened = provider_module.MonoProvider(config, store, builder)
    try:
        assert store.job('fixture', job['job_id'])['state'] == 'failed'
        with pytest.raises(MonoConflict, match='cleanup'):
            reopened.submit('fixture', record)
    finally:
        reopened.close()
        reopened._thread.join(timeout=5)


def dispatcher_fixture(tmp_path):
    (tmp_path / 'bridge').mkdir()
    store = MonoDealStore(tmp_path / 'mono.sqlite')
    record = {'revision': 1, 'identity': {'deal_sha256': 'fixture', 'bundle_sha256': 'bundle'},
              'root': str(tmp_path)}
    store.register('fixture', record)
    config = SimpleNamespace(data_root=tmp_path, calculator_root=tmp_path,
        calculator_python=tmp_path / 'not-executed', template=tmp_path / 'not-opened.xlsx',
        map_path=tmp_path / 'not-read.json', capabilities=None, expected_code_sha256='fixture')
    return store, record, config, SimpleNamespace(verify=lambda record: None)


def test_restart_with_interrupted_job_quarantines_before_another_launch(tmp_path):
    store, record, config, builder = dispatcher_fixture(tmp_path)
    store.add_job('fixture', {'job_id': 'previous-launch', 'revision': 1,
        'state': 'running', 'identity': record['identity'], 'result': None})
    provider = provider_module.MonoProvider(config, store, builder)
    try:
        assert store.job('fixture', 'previous-launch')['state'] == 'interrupted'
        assert (tmp_path / 'dispatcher-quarantine.json').is_file()
        with pytest.raises(MonoConflict, match='cleanup'):
            provider.submit('fixture', record)
    finally:
        provider.close()
        provider._thread.join(timeout=5)


def test_unexpected_dispatcher_death_is_visible_and_cannot_accept_more_jobs(tmp_path, monkeypatch):
    store, record, config, builder = dispatcher_fixture(tmp_path)

    def crash(*args):
        raise KeyboardInterrupt('Portable simulated dispatcher death')

    monkeypatch.setattr(provider_module.MonoProvider, '_run', crash)
    provider = provider_module.MonoProvider(config, store, builder)
    try:
        job = provider.submit('fixture', record)
        provider._thread.join(timeout=5)
        assert not provider._thread.is_alive()
        saved = store.job('fixture', job['job_id'])
        assert saved['state'] == 'failed'
        assert saved['result'] is None
        assert saved['finished_at']
        assert (tmp_path / 'dispatcher-quarantine.json').is_file()
        with pytest.raises(MonoConflict, match='unavailable'):
            provider.submit('fixture', record)
    finally:
        provider.close()
        provider._thread.join(timeout=5)


def test_bridge_exit_without_terminal_receipt_blocks_future_native_work(tmp_path, monkeypatch):
    store, record, config, builder = dispatcher_fixture(tmp_path)
    monkeypatch.setattr(provider_module.subprocess, 'Popen',
                        lambda *args, **kwargs: SimpleNamespace(pid=987654, poll=lambda: 0))
    provider = provider_module.MonoProvider(config, store, builder)
    try:
        job = provider.submit('fixture', record)
        deadline = time.monotonic() + 5
        while store.job('fixture', job['job_id'])['state'] in ('queued', 'running'):
            assert time.monotonic() < deadline
            time.sleep(.01)
        assert store.job('fixture', job['job_id'])['state'] == 'failed'
        assert (tmp_path / 'dispatcher-quarantine.json').is_file()
        with pytest.raises(MonoConflict, match='cleanup'):
            provider.submit('fixture', record)
    finally:
        provider.close()
        provider._thread.join(timeout=5)
