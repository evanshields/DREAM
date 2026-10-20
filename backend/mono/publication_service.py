"""Authenticated publishing operations composed with the Mono deal service."""
from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse

from store.mono_deal_store import MonoConflict, MonoNotFound
from store.mono_publish_store import MonoPublicationStore
from .config import canonical_hash
from .publication import PublicationProvider, registered_plan
from .publication_files import verify_package, download_entry, output_file


def public_job(job, *, current=False):
    fields = ('job_id', 'deal_id', 'revision', 'state', 'created_at', 'updated_at', 'started_at',
              'finished_at', 'elapsed_seconds', 'diagnostics', 'steps', 'identity', 'cancel_requested')
    return {**{key:job[key] for key in fields if key in job}, 'is_current':current}


class PublicationService:
    def __init__(self, mono, *, start_provider=True):
        self.mono = mono
        self.config = mono.config
        self.store = MonoPublicationStore(mono.store)
        enabled = any('publication' in reg for reg in self.config.registrations.values())
        self.provider = PublicationProvider(self.config, self.store, mono.builder) if enabled and start_provider else None

    def _registration(self, deal_id):
        registration = self.config.registrations[deal_id].get('publication')
        if not isinstance(registration, dict):
            raise ValueError('Document sources are not ready for this deal')
        return registration

    def _verified(self, deal_id, job, *, current=False):
        self.mono.builder.verify(job['_revision_record'])
        registration = self._registration(deal_id)
        if registration != job['_registration']:
            raise ValueError('Registered publication sources changed')
        registered_plan(self.config, registration, job['identity']['release'])
        if current and (self.mono._current_job(self.mono.store.current(deal_id)) is None
                or self.store.current(deal_id) is None
                or self.store.current(deal_id)['job_id'] != job['job_id']):
            raise ValueError('Publication is historical because its inputs or reviews changed')
        expected_root = (self.config.data_root/'publications'/job['job_id']/'package').resolve(strict=True)
        if Path(job['package']['_root']).resolve(strict=True) != expected_root:
            raise ValueError('Publication package scope changed')
        if 'source_plan_sha256' in job['identity']:
            from .publication_verification import verify_planned_package
            verified=verify_planned_package(self.config,job,expected_root)
        else:
            verified = verify_package(expected_root, identity=job['_publication_identity'],
                projection_sha256=job['identity']['projection_sha256'])
        return expected_root, verified

    def state(self, deal_id, actor):
        record = self.mono._record(deal_id, actor)
        reasons = []
        warnings = []
        current = None
        try:
            registration = self._registration(deal_id)
            self.mono.builder.verify(record)
            if not self.mono._prepared(record)[3]['ready'] or self.mono._current_job(record) is None:
                raise ValueError('Publishing requires complete evidence and a current verified calculation')
            release = self.store.snapshot(deal_id)
            plan = registered_plan(self.config, registration, release)
            if 'source_plan' not in registration and plan['identity']['deal_id'] != deal_id:
                raise ValueError('Publication sources belong to a different deal')
            current = self.store.current(deal_id)
            if current:
                try:
                    self._verified(deal_id, current, current=True)
                except (ValueError, OSError, KeyError, MonoConflict):
                    current = None
                    warnings.append('The earlier package could not be verified. Build a new package from the reviewed result')
            if self.provider is None:
                reasons.append('The private document publisher is not running')
            elif self.provider._quarantine_path.exists():
                reasons.append('Office cleanup must be verified before publishing')
        except (ValueError, OSError, KeyError, MonoConflict) as error:
            current = None
            reasons.append(str(error) if isinstance(error, (ValueError, MonoConflict)) else 'Publication sources are unavailable')
        jobs = [public_job(job, current=bool(current and current['job_id'] == job['job_id']))
                for job in self.store.jobs(deal_id)]
        return {'deal_id':deal_id, 'revision':record['revision'], 'can_publish':not reasons,
                'blocking_reasons':reasons, 'current':public_job(current, current=True) if current else None,
                'jobs':jobs, 'warnings':warnings, 'external_distribution_authorized':False}

    def submit(self, deal_id, body, actor):
        record = self.mono._record(deal_id, actor)
        request_digest = canonical_hash({'request':body, 'actor':actor})
        try:
            replay = self.mono.store.idempotent_result(deal_id, body['idempotency_key'], 'publish', request_digest)
            if replay is not None:
                return self.job(deal_id, replay['job_id'], actor)
            self.mono._expected(record, body)
            if self.provider is None:
                raise HTTPException(503, 'The private document publisher is not running')
            if not self.mono._prepared(record)[3]['ready'] or self.mono._current_job(record) is None:
                raise MonoConflict('Publishing requires complete evidence and a current verified calculation', record['revision'])
            release = self.store.snapshot(deal_id)
            registration = self._registration(deal_id)
            projection = registered_plan(self.config, registration, release)
            if 'source_plan' not in registration and projection['identity']['deal_id'] != deal_id:
                raise ValueError('Publication sources belong to a different deal')
            job = self.provider.submit(deal_id, record, registration, release, projection,
                key=body['idempotency_key'], request_digest=request_digest)
            return public_job(job)
        except MonoConflict as error:
            self.mono._conflict(error)
        except (ValueError, OSError, KeyError):
            raise HTTPException(409, 'Verified publication sources are missing or changed. Refresh the deal before publishing')

    def job(self, deal_id, job_id, actor):
        self.mono._record(deal_id, actor)
        try:
            job = self.store.job(deal_id, job_id)
        except MonoNotFound:
            raise HTTPException(404, 'No publication job for this deal')
        current = self.state(deal_id, actor)['current']
        return public_job(job, current=bool(current and current['job_id'] == job_id))

    def cancel(self, deal_id, job_id, actor):
        self.job(deal_id, job_id, actor)
        if self.provider is None:
            raise HTTPException(503, 'The private document publisher is not running')
        self.provider.cancel(deal_id, job_id)
        return self.job(deal_id, job_id, actor)

    def download(self, deal_id, job_id, deliverable, variant, actor):
        self.mono._record(deal_id, actor)
        try:
            job = self.store.job(deal_id, job_id)
            if job['state'] != 'complete' or not job.get('package'):
                raise ValueError('Publication is not complete')
            root, receipt = self._verified(deal_id, job, current=True)
            entry = download_entry(receipt, deliverable, variant)
            path = output_file(root, entry['path'])
        except MonoNotFound:
            raise HTTPException(404, 'No publication job for this deal')
        except (ValueError, OSError, KeyError, MonoConflict):
            raise HTTPException(409, 'This publication is unavailable or historical. Generate a package from the current reviewed result')
        filename = 'underwriting-package.zip' if deliverable == 'package' else deliverable+path.suffix.lower()
        return FileResponse(path, media_type=entry['media_type'], filename=filename,
            headers={'Cache-Control':'private, no-store', 'X-Content-Type-Options':'nosniff'})

    def close(self):
        if self.provider:
            self.provider.close()
