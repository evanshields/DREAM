"""
backend/jobs/queue.py — Phase 4a in-process job queue (async fast-path execution).

The thin asynchrony layer between the jobs router and the runner. The router's direct
run_job(...) call (v1 synchronous behavior) is swapped for enqueue_run(...): the request
returns immediately with the job's current view (submitted/routing) and the pipeline runs
on a small ThreadPoolExecutor. run_job (jobs/runner.py) is the worker body unchanged — it
is idempotent-guarded (only runs from SUBMITTED/ROUTING), fails closed (transitions the
JobRecord to FAILED and re-raises on error), and ALWAYS stops at the HITL checkpoints
(AWAITING_INPUT / AWAITING_CP1). Nothing here may auto-advance a job past AWAITING_CP1.

Modes:
  * DREAM_JOBS_SYNC=1 (also "true"/"yes"/"on", case-insensitive): the router keeps the exact
    v1 SYNCHRONOUS behavior — run_job inside the request, errors surfaced as HTTP 422. This
    is the tests' default (see tests/conftest.py) and the back-compat escape hatch.
  * unset / anything else: ASYNC (production default) — the router enqueues here and clients
    poll GET /api/jobs/{job_id} to the HITL stop.

Restart hygiene: an in-process queue loses in-flight work when the server dies. On startup
(main.py lifespan) sweep_stale_jobs() fails any job stranded in a RUNNING status
(SUBMITTED/ROUTING/ANALYZING/SYNTHESIZING) so it never sits "running" forever. The two
human-paused statuses (AWAITING_INPUT, AWAITING_CP1) are durable waits, NOT strandings —
the sweep must never touch them.

Stores are thread-safe (per-store lock + WAL + busy_timeout, check_same_thread=False), so
worker threads share the request's store instances safely. No sqlite3 import here — all
persistence goes through the jobs/deal store accessors (architectural guard).
"""
from __future__ import annotations

import logging
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from jobs.contracts import JobStatus  # noqa: E402
from jobs.job_store import get_job_store, SQLiteJobStore  # noqa: E402
from jobs.runner import run_job, _now as _resolve_now_iso  # noqa: E402

logger = logging.getLogger(__name__)

# Statuses a dead server strands mid-run. NEVER the human-paused pair (AWAITING_INPUT,
# AWAITING_CP1) — those are waiting on a person, not on a lost worker thread.
STALE_STATUSES: tuple = (
    JobStatus.SUBMITTED,
    JobStatus.ROUTING,
    JobStatus.ANALYZING,
    JobStatus.SYNTHESIZING,
)

_STALE_ERROR = "server restarted mid-run; resubmit the deal"

# Module-level executor: created lazily (first enqueue), guarded by a lock so concurrent
# first-requests don't race the constructor. shutdown() clears it so tests get a fresh pool.
_executor: Optional[ThreadPoolExecutor] = None
_executor_lock = threading.Lock()


def sync_mode() -> bool:
    """True when DREAM_JOBS_SYNC requests the v1 synchronous router behavior (tests/back-compat).
    Read at request time so tests can toggle per case."""
    return os.environ.get("DREAM_JOBS_SYNC", "").strip().lower() in ("1", "true", "yes", "on")


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    with _executor_lock:
        if _executor is None:
            try:
                workers = int(os.environ.get("DREAM_JOB_WORKERS", "2") or 2)
            except ValueError:
                workers = 2
            _executor = ThreadPoolExecutor(
                max_workers=max(1, workers), thread_name_prefix="dream-job"
            )
        return _executor


def enqueue_run(
    job_id: str,
    *,
    analysts: Any,
    now_iso: Optional[str],
    intake_summary: Optional[dict],
    deal_docs: Optional[dict],
    job_store: Any,
    deal_store: Any,
) -> None:
    """Submit one run_job(...) execution to the pool. Fire-and-forget: the caller returns the
    job's current view and clients poll. run_job already fails closed (JobRecord -> FAILED +
    re-raise), so the worker only has to keep the pool thread alive — log, never crash.

    now_iso: pass None from async routers so the WORKER mints the clock at execution time —
    a request-time stamp would date every transition of a minutes-later run at submit time."""

    def _worker() -> None:
        try:
            run_job(
                job_id,
                analysts=analysts,
                now_iso=now_iso,
                intake_summary=intake_summary,
                deal_docs=deal_docs,
                job_store=job_store,
                deal_store=deal_store,
            )
        except Exception:  # noqa: BLE001 — runner already FAILed the JobRecord and re-raised
            logger.exception("background run for job %s failed", job_id)

    _get_executor().submit(_worker)


def sweep_stale_jobs(job_store: Optional[SQLiteJobStore] = None,
                     now_iso: Optional[str] = None) -> int:
    """Fail every job stranded in a running status by a dead server (startup hygiene; called
    from main.py's lifespan). Leaves the human-paused statuses untouched. Returns the count."""
    js = job_store or get_job_store()
    ts = _resolve_now_iso(now_iso)
    swept = 0
    for st in STALE_STATUSES:
        for job in js.list_jobs(status=st.value):
            js.transition(job.job_id, JobStatus.FAILED, ts, error=_STALE_ERROR)
            # Same kind/shape as the runner's failure audit (runner.py run_job except-path).
            js.append_audit(job.job_id, "error", f"run failed: {_STALE_ERROR}", ts=ts)
            swept += 1
    if swept:
        logger.warning("sweep_stale_jobs: failed %d job(s) stranded by a restart", swept)
    return swept


def shutdown(wait: bool = False) -> None:
    """Shut down and clear the module executor (main.py lifespan teardown; test fixture
    teardown). The next enqueue lazily creates a fresh pool."""
    global _executor
    with _executor_lock:
        ex, _executor = _executor, None
    if ex is not None:
        ex.shutdown(wait=wait)
