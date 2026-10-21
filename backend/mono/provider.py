"""Durable app job mappings around one queued first-party native worker."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import uuid

from .revisions import now, write_new
from store.mono_deal_store import MonoConflict


_unsafe_roots = {}
_unsafe_roots_lock = threading.Lock()


def unsafe_root(root):
    """Share a fail-closed memory latch even when disk writes are unavailable."""
    key = str(Path(root).resolve())
    with _unsafe_roots_lock:
        return _unsafe_roots.setdefault(key, threading.Event())


def unresolved_launches(root):
    """Database terminal states do not resolve an unmatched native launch."""
    unresolved = []
    for parent in ('bridge', 'publications'):
        for prelaunch in (Path(root) / parent).glob('*/prelaunch.json'):
            try:
                exited = json.loads(prelaunch.with_name('bridge-exit.json').read_bytes())
                if not isinstance(exited, dict) or exited.get('quarantined') is not False:
                    unresolved.append(str(prelaunch.parent))
            except (OSError, ValueError, TypeError):
                unresolved.append(str(prelaunch.parent))
    return unresolved


def drain_owned_bridge(process, *, sleep=time.sleep):
    """An observation error cannot grant permission to release a live child."""
    while True:
        try:
            if process.poll() is not None:
                return
        except BaseException:
            pass
        try:
            sleep(0.2)
        except BaseException:
            # Keep ownership through an interrupted observation, including shutdown.
            pass


def wait_for_bridge(process, directory, closing, quarantine, *, timeout=1320,
                    cancel_grace=30, clock=time.monotonic, sleep=time.sleep):
    """Bound the visible job, retaining ownership while uncertain cleanup runs."""
    deadline = clock() + timeout
    cancel_started = None
    quarantined = False
    try:
        while process.poll() is None:
            current = clock()
            if closing() or current >= deadline:
                (directory / 'cancel-requested').touch(exist_ok=True)
            if (directory / 'cancel-requested').exists():
                if cancel_started is None:
                    cancel_started = current
                if current - cancel_started >= cancel_grace and not quarantined:
                    quarantine('Calculator did not finish cancellation within its cleanup grace. '
                               'This dispatcher is quarantined until owned-process cleanup is verified.')
                    quarantined = True
            sleep(0.2)
    except BaseException:
        try:
            quarantine('Native ownership observation failed. Owned-process cleanup must be verified.')
        except BaseException:
            pass
        try:
            (directory / 'cancel-requested').touch(exist_ok=True)
        except BaseException:
            pass
        drain_owned_bridge(process, sleep=sleep)
        raise
    return quarantined


class MonoProvider:
    def __init__(self, config, store, builder):
        self.config, self.store, self.builder = config, store, builder
        self._queue = queue.Queue()
        self._active_job = None
        self._closed = threading.Event()
        self._unsafe = unsafe_root(config.data_root)
        self._quarantine_path = config.data_root / 'dispatcher-quarantine.json'
        self._lease = (config.data_root / 'dispatcher.lock').open('a+b')
        self._lease.seek(0, 2)
        if self._lease.tell() == 0:
            self._lease.write(b'0')
            self._lease.flush()
        self._lease.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self._lease.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self._lease.close()
            raise RuntimeError('Another process owns this private Mono dispatcher') from exc
        # Previous process outcomes remain historical. Never blindly relaunch native jobs.
        interrupted = self.store.recover_interrupted()
        unmatched = unresolved_launches(config.data_root)
        if interrupted or unmatched:
            self._quarantine('App restart found interrupted calculations. '
                             'Owned native cleanup must be verified before new work.', jobs=interrupted,
                             unmatched_launches=unmatched)
        self._thread = threading.Thread(target=self._work, name='dream-mono-app', daemon=True)
        self._thread.start()

    def submit(self, deal_id, record, *, idempotency_key=None, request_digest=None):
        if self._closed.is_set() or not self._thread.is_alive():
            raise MonoConflict('Calculator dispatcher is unavailable. New calculations are blocked')
        if self._unsafe.is_set() or self._quarantine_path.exists():
            raise MonoConflict('Calculator cleanup is unverified. New calculations are blocked')
        self.builder.verify(record)
        job = {'job_id': uuid.uuid4().hex, 'deal_id': deal_id, 'revision': record['revision'],
               'state': 'queued', 'created_at': now(), 'updated_at': now(), 'identity': copy.deepcopy(record['identity']),
               'elapsed_seconds': 0, 'diagnostics': [], 'warnings': [], 'result': None, 'is_current': False}
        if idempotency_key is not None:
            job, created = self.store.claim_calculation(deal_id, job, idempotency_key, request_digest)
        else:
            self.store.add_job(deal_id, job)
            created = True
        if created:
            self._queue.put((deal_id, job['job_id'], copy.deepcopy(record)))
        return job

    def cancel(self, deal_id, job_id):
        job = self.store.job(deal_id, job_id)
        if job['state'] in ('queued', 'running'):
            directory = self.config.data_root / 'bridge' / job_id
            directory.mkdir(exist_ok=True)
            (directory / 'cancel-requested').touch(exist_ok=True)
            try:
                self.store.update_job(deal_id, job_id, {'cancel_requested': True, 'updated_at': now()})
            except MonoConflict:
                # A completed immutable job wins a late cancellation request.
                if self.store.job(deal_id, job_id)['state'] in ('queued', 'running'):
                    raise
        return self.store.job(deal_id, job_id)

    def close(self):
        self._closed.set()
        self._queue.put(None)

    def _work(self):
        try:
            self._dispatch()
        except BaseException as exc:
            self._quarantine('Calculator dispatcher stopped unexpectedly: ' + type(exc).__name__)
            if self._active_job is not None:
                deal_id, job_id = self._active_job
                current = self.store.job(deal_id, job_id)
                if current['state'] in ('queued', 'running'):
                    self.store.update_job(deal_id, job_id, {'state': 'failed', 'result': None,
                        'updated_at': now(), 'finished_at': now(),
                        'diagnostics': ['Calculator dispatcher stopped unexpectedly: ' + type(exc).__name__]})
            self.store.recover_interrupted()
        finally:
            self._lease.close()

    def _quarantine(self, reason, **details):
        # Set memory first. Failure to persist must not permit another dispatch.
        unsafe_root(self.config.data_root).set()
        try:
            write_new(self._quarantine_path, dict(details, recorded_at=now(), reason=reason,
                                                 cleanup_verified=False))
        except FileExistsError:
            # Keep the first unresolved ownership record, including across restart.
            pass

    def _observe_bridge(self, process, directory, job_id, closing, quarantine, wait):
        """Own launch, observation failures and exit persistence as one operation."""
        quarantined = True
        try:
            write_new(directory / 'launch.json', {'job_id': job_id, 'bridge_pid': process.pid,
                                                  'recorded_at': now()})
            quarantined = wait(process, directory, closing, quarantine)
            return quarantined
        except BaseException:
            unsafe_root(self.config.data_root).set()
            try:
                self._quarantine('Native bridge observation failed. Cleanup remains unverified.',
                                 job_id=job_id, bridge_pid=process.pid)
            except BaseException:
                pass
            try:
                (directory / 'cancel-requested').touch(exist_ok=True)
            except BaseException:
                pass
            drain_owned_bridge(process)
            raise
        finally:
            try:
                write_new(directory / 'bridge-exit.json', {'job_id': job_id, 'bridge_pid': process.pid,
                    'returncode': process.poll(), 'recorded_at': now(), 'quarantined': quarantined})
            except BaseException:
                unsafe_root(self.config.data_root).set()
                try:
                    self._quarantine('Native bridge exit receipt could not be saved.', job_id=job_id)
                except BaseException:
                    pass
                raise

    def _dispatch(self):
        while not self._closed.is_set():
            item = self._queue.get()
            if item is None:
                return
            deal_id, job_id, record = item
            self._active_job = (deal_id, job_id)
            try:
                self._run(deal_id, job_id, record)
            except Exception as exc:
                current = self.store.job(deal_id, job_id)
                if current['state'] in ('queued', 'running'):
                    state = 'cancelled' if current.get('cancel_requested') else 'failed'
                    self.store.update_job(deal_id, job_id, {'state': state, 'result': None,
                        'diagnostics': [type(exc).__name__ + ': ' + str(exc)],
                        'finished_at': now(), 'updated_at': now()})
            self._active_job = None

    def _run(self, deal_id, job_id, record):
        if unsafe_root(self.config.data_root).is_set() or self._quarantine_path.exists():
            raise RuntimeError('Calculator cleanup is unverified. No new native job was started')
        self.builder.verify(record)
        directory = self.config.data_root / 'bridge' / job_id
        directory.mkdir(exist_ok=True)
        if (directory / 'cancel-requested').exists():
            self.store.update_job(deal_id, job_id, {'state': 'cancelled', 'updated_at': now(), 'finished_at': now()})
            return
        config = self.config
        registry = {'deals': {deal_id: record['root']}, 'output_root': str(config.data_root / 'calculations'),
                    'template': str(config.template), 'map_path': str(config.map_path)}
        if config.capabilities:
            registry['capabilities'] = config.capabilities
        if record.get('trusted_rulings'):
            registry['trusted_rulings'] = record['trusted_rulings']
        write_new(directory / 'registry.json', registry)
        write_new(directory / 'envelope.json', {'calculator_root': str(config.calculator_root),
            'expected_code_sha256': config.expected_code_sha256,
            'request': {'deal_id': deal_id, 'expected_revision': record['identity']['deal_sha256'],
                        'expected_bundle_sha256': record['identity']['bundle_sha256']}})
        self.store.update_job(deal_id, job_id, {'state': 'running', 'started_at': now(), 'updated_at': now()})
        started = time.monotonic()
        write_new(directory / 'prelaunch.json', {'job_id': job_id, 'identity': record['identity'],
            'recorded_at': now(), 'expected_code_sha256': config.expected_code_sha256})
        with (directory / 'worker-stdout.log').open('x') as stdout, (directory / 'worker-stderr.log').open('x') as stderr:
            process = subprocess.Popen([str(config.calculator_python), str(Path(__file__).with_name('native_bridge.py')), str(directory)],
                cwd=config.calculator_root, stdout=stdout, stderr=stderr,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            def quarantine(reason):
                # Durable latch survives app restarts. Do not clear it merely
                # because a PID later exits or a terminal receipt appears.
                self._quarantine(reason, job_id=job_id, bridge_pid=process.pid)
                current = self.store.job(deal_id, job_id)
                if current['state'] in ('queued', 'running'):
                    self.store.update_job(deal_id, job_id, {'state': 'failed', 'result': None,
                        'updated_at': now(), 'finished_at': now(),
                        'elapsed_seconds': time.monotonic() - started,
                        'diagnostics': [reason]})
            quarantined = self._observe_bridge(process, directory, job_id, self._closed.is_set,
                                              quarantine, wait_for_bridge)
            if quarantined:
                return
        terminal_path = directory / 'terminal.json'
        if not terminal_path.exists():
            self._quarantine('Native bridge ended without a terminal receipt. Native cleanup is unverified.',
                             job_id=job_id, bridge_pid=process.pid)
            raise RuntimeError('Native bridge ended without an immutable terminal receipt. Inspect its local diagnostic log')
        try:
            receipt_bytes = terminal_path.read_bytes()
            native = json.loads(receipt_bytes)
            if not isinstance(native, dict):
                raise ValueError('Calculator terminal receipt must be an object')
        except (OSError, ValueError, TypeError):
            self._quarantine('Calculator terminal receipt is unreadable. Native cleanup is unverified.',
                             job_id=job_id, bridge_pid=process.pid)
            raise
        current = self.store.job(deal_id, job_id)
        if current['state'] not in ('queued', 'running'):
            return
        if current.get('cancel_requested') or (directory / 'cancel-requested').exists():
            self.store.update_job(deal_id, job_id, {'state': 'cancelled', 'result': None,
                'updated_at': now(), 'finished_at': now(), 'elapsed_seconds': time.monotonic() - started,
                'diagnostics': native.get('diagnostics', []), 'warnings': native.get('warnings', [])})
            return
        state = native['state']
        result = None
        if state == 'complete':
            try:
                self.builder.verify(record)
            except ValueError:
                state = 'stale'
            if state == 'complete':
                from .verification import verified_result
                try:
                    result = verified_result(native, record, config, terminal_path, receipt_bytes=receipt_bytes)
                except ValueError:
                    # A changed package is stale, while invalid evidence on the same
                    # package remains a failed validation with its useful diagnostic.
                    try:
                        self.builder.verify(record)
                    except ValueError:
                        state = 'stale'
                    if state != 'stale':
                        raise
        current = self.store.job(deal_id, job_id)
        if current['state'] not in ('queued', 'running'):
            # A restarted process already marked this run interrupted. Preserve that outcome.
            return
        if current.get('cancel_requested') or (directory / 'cancel-requested').exists():
            state, result = 'cancelled', None
        self.store.update_job(deal_id, job_id, {'state': state, 'result': result, 'updated_at': now(),
            'finished_at': now(), 'elapsed_seconds': time.monotonic() - started,
            'diagnostics': native.get('diagnostics', []), 'warnings': native.get('warnings', [])})
        if state == 'complete':
            self.store.promote_result(deal_id, job_id, record['revision'], record['identity'])
