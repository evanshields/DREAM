"""Private publishing jobs bound to authenticated revisions and actual gates."""
from __future__ import annotations

import copy
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import uuid

from store.mono_deal_store import MonoConflict
from .config import canonical_hash, digest
from .provider import MonoProvider, wait_for_bridge
from .publication_files import verify_package
from .revisions import now, write_new


def registered_plan(config, registration, release):
    """Read only a server-pinned, already source-bound publication candidate."""
    planned='source_plan' in registration
    fields={'source_plan','source_plan_sha256','artifact_root','renderer_sha256'} if planned else {
        'projection','artifact_root','projection_sha256','renderer_sha256'}
    if set(registration) != fields:
        raise ValueError('Publication source registration is incomplete')
    from tools.mono_publish.contracts import load_projection
    from tools.mono_publish.identity import verify_renderer, publication_source_identities
    from tools.mono_publish.native_projection import normalized_identity
    from .revisions import read
    config.load_calculator()
    verify_renderer(registration['renderer_sha256'], config.calculator_root)
    if planned:
        from tools.mono_publish.source_plan import plan_identity,validate_source_plan
        source=read(registration['source_plan'])
        if plan_identity(source)!=registration['source_plan_sha256']:
            raise ValueError('Registered publication source plan changed')
        return validate_source_plan(source,registration['artifact_root'])
    source = read(registration['projection'])
    if canonical_hash(source) != registration['projection_sha256']:
        raise ValueError('Registered publication plan changed')
    projection = load_projection(registration['projection'], registration['artifact_root'], final=True)
    expected = normalized_identity(release['result_identity'], projection['identity']['deal_id'], release['revision'])
    if any(projection['identity'].get(key) != value for key, value in expected.items()):
        raise ValueError('Publication sources belong to a different calculation')
    if (projection['identity']['result_id'] != release['result_id']
            or projection['identity']['workbook_sha256'] != release['artifact_sha256']
            or projection['identity']['comps_event_id'] != release['comps_event_id']
            or projection['identity']['go_event_id'] != release['go_event_id']
            or projection['identity']['renderer_sha256'] != registration['renderer_sha256']
            or projection['identity']['calculator_sha256'] != config.expected_code_sha256):
        raise ValueError('Publication sources or human reviews changed')
    if any(projection['identity'][key] != value for key, value in publication_source_identities(source).items()):
        raise ValueError('Publication asset or narrative policy changed')
    return source


class PublicationProvider:
    _quarantine = MonoProvider._quarantine

    def __init__(self, config, store, builder):
        self.config, self.store, self.builder = config, store, builder
        self._queue = queue.Queue()
        self._active_job = None
        self._closed = threading.Event()
        self._quarantine_path = config.data_root/'dispatcher-quarantine.json'
        self._lease = (config.data_root/'publication-dispatcher.lock').open('a+b')
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
        except OSError as error:
            self._lease.close()
            raise RuntimeError('Another process owns this private publisher') from error
        interrupted = self.store.recover_interrupted()
        if interrupted:
            self._quarantine('Publisher restart found interrupted jobs. Owned Office cleanup must be verified.',
                             kind='publication', jobs=interrupted)
        self._thread = threading.Thread(target=self._work, name='dream-publication', daemon=True)
        self._thread.start()

    def submit(self, deal_id, revision, registration, release, projection, *, key, request_digest):
        if self._closed.is_set() or not self._thread.is_alive() or self._quarantine_path.exists():
            raise MonoConflict('Publishing is unavailable until owned-process cleanup is verified')
        self.builder.verify(revision)
        planned='source_plan' in registration
        identity={'release':release,'renderer_sha256':registration['renderer_sha256']}
        if planned:
            identity['source_plan_sha256']=registration['source_plan_sha256']
        else:
            identity.update(projection_sha256=registration['projection_sha256'],
                **{name:projection['identity'][name] for name in ('asset_policy_sha256','narrative_sha256')})
        calculation = self.store.deals.job(deal_id, release['calculation_job_id'])['result']
        receipt_hash = calculation.get('_native_receipt_sha256')
        if not isinstance(receipt_hash, str) or len(receipt_hash) != 64 or digest(calculation['_native_receipt']) != receipt_hash:
            raise ValueError('Native calculation receipt differs from the evidence verified by the app')
        job = {'job_id':uuid.uuid4().hex, 'deal_id':deal_id, 'revision':release['revision'],
            'state':'queued', 'created_at':now(), 'updated_at':now(), 'elapsed_seconds':0,
            'identity':identity, 'diagnostics':[], 'steps':['Sources and human reviews verified'], 'package':None,
            '_registration':copy.deepcopy(registration), '_revision_record':copy.deepcopy(revision),
            '_publication_identity':None if planned else copy.deepcopy(projection['identity']),
            '_native_receipt_sha256':receipt_hash,
            '_artifact':calculation['_artifact'], '_native_receipt':calculation['_native_receipt']}
        job, created = self.store.claim(deal_id, job, key, request_digest)
        if created:
            self._queue.put((deal_id, job['job_id']))
        return job

    def cancel(self, deal_id, job_id):
        job = self.store.job(deal_id, job_id)
        if job['state'] in ('queued', 'running'):
            directory = self.config.data_root/'publications'/job_id
            directory.mkdir(parents=True, exist_ok=True)
            (directory/'cancel-requested').touch(exist_ok=True)
            try:
                self.store.update(deal_id, job_id, {'cancel_requested':True, 'updated_at':now()})
            except MonoConflict:
                if self.store.job(deal_id, job_id)['state'] in ('queued', 'running'):
                    raise
        return self.store.job(deal_id, job_id)

    def close(self):
        self._closed.set()
        self._queue.put(None)

    def _work(self):
        try:
            while not self._closed.is_set():
                item = self._queue.get()
                if item is None:
                    return
                deal_id, job_id = item
                self._active_job = (deal_id, job_id)
                try:
                    self._run(deal_id, job_id)
                except Exception as error:
                    job = self.store.job(deal_id, job_id)
                    if job['state'] in ('queued', 'running'):
                        self.store.update(deal_id, job_id, {'state':'failed', 'package':None,
                            'finished_at':now(), 'updated_at':now(),
                            'diagnostics':[type(error).__name__+': publication verification failed. Sources remain private.']})
                self._active_job = None
        except BaseException as error:
            self._quarantine('Publisher dispatcher stopped unexpectedly: ' + type(error).__name__, kind='publication')
            if self._active_job is not None:
                deal_id, job_id = self._active_job
                job = self.store.job(deal_id, job_id)
                if job['state'] in ('queued', 'running'):
                    self.store.update(deal_id, job_id, {'state':'failed', 'package':None,
                        'finished_at':now(), 'updated_at':now(),
                        'diagnostics':['Publisher dispatcher stopped unexpectedly: ' + type(error).__name__]})
            self.store.recover_interrupted()
        finally:
            self._lease.close()

    def _run(self, deal_id, job_id):
        from .revisions import read
        job = self.store.job(deal_id, job_id)
        directory = self.config.data_root/'publications'/job_id
        directory.mkdir(parents=True, exist_ok=True)
        if job.get('cancel_requested') or (directory/'cancel-requested').exists():
            self.store.update(deal_id, job_id, {'state':'cancelled', 'updated_at':now()})
            return
        if self._quarantine_path.exists():
            raise MonoConflict('Office cleanup is unverified')
        self.builder.verify(job['_revision_record'])
        release = job['identity']['release']
        if self.store.snapshot(deal_id) != release:
            raise MonoConflict('Publication reviews changed before rendering')
        projection = registered_plan(self.config, job['_registration'], release)
        planned='source_plan_sha256' in job['identity']
        if not planned and projection['identity']['deal_id'] != deal_id:
            raise MonoConflict('Publication belongs to a different deal')
        if digest(job['_native_receipt']) != job['_native_receipt_sha256']:
            raise ValueError('Original native calculation receipt changed before publication')
        envelope={
            'workbook':job['_artifact'], 'native_receipt':job['_native_receipt'],
            'expected_renderer_sha256':job['identity']['renderer_sha256'],
            'expected_calculator_sha256':self.config.expected_code_sha256, 'final':True}
        if planned:
            from tools.mono_publish.source_plan import freeze_source_plan
            from tools.mono_publish.native_projection import normalized_identity
            frozen=freeze_source_plan(projection,job['_registration']['artifact_root'],directory/'request-sources')
            if frozen['source_plan_sha256']!=job['identity']['source_plan_sha256']:
                raise ValueError('Publication source plan changed before freezing')
            if digest(job['_native_receipt'])!=job['_native_receipt_sha256']:
                raise ValueError('Original native calculation receipt changed before preparation')
            envelope.update(frozen,native_receipt_sha256=job['_native_receipt_sha256'],
                expected_native_identity=normalized_identity(release['result_identity'],deal_id,release['revision']),
                created_at=job['created_at'],comps_event_id=release['comps_event_id'],go_event_id=release['go_event_id'])
        else:
            envelope.update(projection=job['_registration']['projection'],artifact_root=job['_registration']['artifact_root'])
        write_new(directory/'envelope.json',envelope)
        self.store.update(deal_id, job_id, {'state':'running', 'started_at':now(), 'updated_at':now(),
            'steps':[*job['steps'], 'Reopening workbook and building four deliverables']})
        started = time.monotonic()
        write_new(directory/'prelaunch.json', {'job_id':job_id, 'identity':job['identity'],
            'native_receipt_sha256':job['_native_receipt_sha256'], 'recorded_at':now()})
        with (directory/'worker-stdout.log').open('x') as stdout, (directory/'worker-stderr.log').open('x') as stderr:
            process = subprocess.Popen([str(self.config.calculator_python), '-m', 'tools.mono_publish', str(directory)],
                cwd=self.config.calculator_root, stdout=stdout, stderr=stderr,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            try:
                write_new(directory/'launch.json', {'job_id':job_id, 'bridge_pid':process.pid, 'recorded_at':now()})
            except BaseException:
                self._quarantine('Publisher launched but its launch receipt could not be saved.',
                                 kind='publication', job_id=job_id, bridge_pid=process.pid)
                (directory/'cancel-requested').touch(exist_ok=True)
                wait_for_bridge(process, directory, lambda: True, lambda reason: None)
                raise

            def quarantine(reason):
                self._quarantine(reason, kind='publication', job_id=job_id, bridge_pid=process.pid)
                current = self.store.job(deal_id, job_id)
                if current['state'] in ('queued', 'running'):
                    self.store.update(deal_id, job_id, {'state':'failed', 'package':None,
                        'finished_at':now(), 'updated_at':now(), 'diagnostics':[reason]})

            observed_steps=[]
            def closing():
                steps=[]
                for path in sorted(directory.glob('step-*.json')):
                    try:
                        step=read(path)['step']
                        if isinstance(step,str) and len(step)<=500:
                            steps.append(step)
                    except (ValueError,OSError,KeyError):
                        pass
                if steps and steps!=observed_steps:
                    observed_steps[:]=steps
                    current=self.store.job(deal_id,job_id)
                    if current['state'] in ('queued','running'):
                        self.store.update(deal_id,job_id,{'steps':[*job['steps'],*steps],'updated_at':now()})
                return self._closed.is_set()
            quarantined = wait_for_bridge(process, directory, closing, quarantine)
            write_new(directory/'bridge-exit.json', {'job_id':job_id, 'bridge_pid':process.pid,
                'recorded_at':now(), 'returncode':process.poll(), 'quarantined':quarantined})
            if quarantined:
                return
        if not (directory/'terminal.json').exists():
            quarantine('The document worker exited without a terminal receipt. Owned-process cleanup must be verified')
            return
        terminal = read(directory/'terminal.json')
        if terminal.get('cleanup_verified') is False:
            quarantine('The document exporter did not verify owned-process cleanup. New native work is blocked')
            return
        state = terminal['state']
        package = None
        if state == 'complete':
            if digest(job['_native_receipt']) != job['_native_receipt_sha256']:
                raise ValueError('Original native calculation receipt changed during publication')
            self.builder.verify(job['_revision_record'])
            registered_plan(self.config, job['_registration'], release)
            if planned:
                from .publication_verification import verify_planned_package
                verified=verify_planned_package(self.config,job,directory/'package')
            else:
                verified = verify_package(directory/'package', identity=job['_publication_identity'],
                    projection_sha256=job['identity']['projection_sha256'])
                proof = read(verified['workbook_verification']['path'])
                if proof.get('receipt_sha256') != job['_native_receipt_sha256']:
                    raise ValueError('Reopened workbook proof uses another native receipt')
            package = {'identity':job['identity'], 'validation':{'passed':True},
                'projection_sha256':verified['projection_sha256'],
                'deliverables':verified['deliverables'], '_receipt':verified, '_root':str(directory/'package')}
        elif state not in ('failed', 'cancelled', 'blocked', 'stale'):
            raise ValueError('Unexpected publication terminal state')
        current = self.store.job(deal_id, job_id)
        if current['state'] not in ('queued', 'running'):
            return
        if current.get('cancel_requested') or (directory/'cancel-requested').exists():
            state, package = 'cancelled', None
        changes = {'state':state, 'package':package,
            'elapsed_seconds':time.monotonic()-started, 'finished_at':now(), 'updated_at':now(),
            'steps':[*job['steps'], 'All deliverables verified'] if state == 'complete' else job['steps'],
            'diagnostics':terminal.get('validation', {}).get('reasons', [])}
        try:
            self.store.update(deal_id, job_id, changes)
        except MonoConflict:
            latest = self.store.job(deal_id, job_id)
            if latest['state'] not in ('queued', 'running'):
                return
            if not latest.get('cancel_requested'):
                raise
            self.store.update(deal_id, job_id, {**changes, 'state':'cancelled', 'package':None})
            return
        if state == 'complete':
            self.store.promote(deal_id, job_id)
