"""Durable app job mappings around one queued first-party native worker."""
from __future__ import annotations

import copy
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import uuid

from .revisions import now, read, write_new


class MonoProvider:
    def __init__(self, config, store, builder):
        self.config, self.store, self.builder = config, store, builder
        self._queue = queue.Queue()
        self._closed = threading.Event()
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
        self.store.recover_interrupted()
        self._thread = threading.Thread(target=self._work, name='dream-mono-app', daemon=True)
        self._thread.start()

    def submit(self, deal_id, record):
        self.builder.verify(record)
        job = {'job_id': uuid.uuid4().hex, 'deal_id': deal_id, 'revision': record['revision'],
               'state': 'queued', 'created_at': now(), 'updated_at': now(), 'identity': copy.deepcopy(record['identity']),
               'elapsed_seconds': 0, 'diagnostics': [], 'warnings': [], 'result': None, 'is_current': False}
        self.store.add_job(deal_id, job)
        self._queue.put((deal_id, job['job_id'], copy.deepcopy(record)))
        return job

    def cancel(self, deal_id, job_id):
        job = self.store.job(deal_id, job_id)
        if job['state'] in ('queued', 'running'):
            directory = self.config.data_root / 'bridge' / job_id
            directory.mkdir(exist_ok=True)
            (directory / 'cancel-requested').touch(exist_ok=True)
            self.store.update_job(deal_id, job_id, {'cancel_requested': True, 'updated_at': now()})
        return self.store.job(deal_id, job_id)

    def close(self):
        self._closed.set()
        self._queue.put(None)

    def _work(self):
        try:
            self._dispatch()
        finally:
            self._lease.close()

    def _dispatch(self):
        while not self._closed.is_set():
            item = self._queue.get()
            if item is None:
                return
            deal_id, job_id, record = item
            try:
                self._run(deal_id, job_id, record)
            except Exception as exc:
                current = self.store.job(deal_id, job_id)
                if current['state'] in ('queued', 'running'):
                    self.store.update_job(deal_id, job_id, {'state': 'failed', 'result': None,
                        'diagnostics': [type(exc).__name__ + ': ' + str(exc)], 'updated_at': now()})

    def _run(self, deal_id, job_id, record):
        self.builder.verify(record)
        directory = self.config.data_root / 'bridge' / job_id
        directory.mkdir(exist_ok=True)
        if (directory / 'cancel-requested').exists():
            self.store.update_job(deal_id, job_id, {'state': 'cancelled', 'updated_at': now()})
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
        with (directory / 'worker-stdout.log').open('x') as stdout, (directory / 'worker-stderr.log').open('x') as stderr:
            process = subprocess.Popen([str(config.calculator_python), str(Path(__file__).with_name('native_bridge.py')), str(directory)],
                cwd=config.calculator_root, stdout=stdout, stderr=stderr,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            # Do not terminate a parent while its owned Excel worker may still be cleaning up.
            while process.poll() is None:
                if self._closed.is_set():
                    (directory / 'cancel-requested').touch(exist_ok=True)
                time.sleep(0.2)
        terminal_path = directory / 'terminal.json'
        if not terminal_path.exists():
            raise RuntimeError('Native bridge ended without an immutable terminal receipt. Inspect its local diagnostic log')
        native = read(terminal_path)
        state = native['state']
        result = None
        if state == 'complete':
            try:
                self.builder.verify(record)
            except ValueError:
                state = 'stale'
            if state == 'complete':
                result = {'result_id': native['identity']['calculation_id'], 'outputs': native['outputs'],
                          'output_metadata': native['output_metadata'], 'checks': dict(native['checks'], release_passed=True),
                          'artifact_sha256': native['identity']['workbook_sha256'], 'identity': native['identity'],
                          '_native_receipt': str(terminal_path), '_artifact': native['artifact']}
        current = self.store.job(deal_id, job_id)
        if current['state'] not in ('queued', 'running'):
            # A restarted process already marked this run interrupted. Preserve that outcome.
            return
        self.store.update_job(deal_id, job_id, {'state': state, 'result': result, 'updated_at': now(),
            'finished_at': now(), 'elapsed_seconds': time.monotonic() - started,
            'diagnostics': native.get('diagnostics', []), 'warnings': native.get('warnings', [])})
        if state == 'complete':
            self.store.promote_result(deal_id, job_id, record['revision'], record['identity'])
