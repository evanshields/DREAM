"""
backend/routers/jobs.py — Wave C-v1 fast-path job API (APIRouter, prefix /api/jobs).

The HTTP surface over the job runner (jobs/runner.py). Four endpoints:

  POST /api/jobs            submit a deal: create a DealStore deal + a JobRecord (idempotent on
                            idempotency_key), run Wave 0, then either STOP at AWAITING_INPUT
                            (blocking open questions) or run the full pipeline to AWAITING_CP1.
  GET  /api/jobs/{job_id}   status + phase + open_questions; at CP-1 also the spec + headline_metrics
                            + the gate summary (the one analytical glance).
  POST /api/jobs/{job_id}/answer   record a human answer to an OpenQuestion (resumes from
                            AWAITING_INPUT when the last blocking question is answered).
  POST /api/jobs/{job_id}/cancel   set the cooperative cancel flag.

v1 runs the pipeline SYNCHRONOUSLY inside the request (note in run_job where an async queue plugs
in later). The router mounts standalone in tests (TestClient(make_app())) with StubAnalysts — no
main.py import, no live LLM.
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store import get_deal_store, DealStore, DealNotFound  # noqa: E402
from jobs.contracts import JobStatus, JobRecord  # noqa: E402
from jobs.job_store import get_job_store, SQLiteJobStore, JobNotFound  # noqa: E402
from jobs.runner import run_job  # noqa: E402
from jobs.wave0 import run_wave0  # noqa: E402
from jobs.analysts import StubAnalysts, KimiAnalysts  # noqa: E402

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Request / response models (JSON-native floats; no Decimal)
# ---------------------------------------------------------------------------

class SubmitJobRequest(BaseModel):
    """Submit a deal to the fast path. `intake_summary` is the already-parsed deal-package summary
    (BL-17 critical inputs may be nested under 'critical_inputs' or flat). `deal_docs` is the
    excerpted source material the analysts read (ignored by StubAnalysts)."""
    intake_summary: Dict[str, Any] = Field(default_factory=dict)
    deal_docs: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = ""
    owner: str = ""
    deal_name: str = ""
    routing: str = "ACQ"


class AnswerRequest(BaseModel):
    question_id: str
    answer: Any = None


def _open_questions(job: JobRecord) -> List[Dict[str, Any]]:
    return [q.to_dict() for q in job.open_questions]


def _job_view(job: JobRecord, deal_store: DealStore) -> Dict[str, Any]:
    """The GET response. At CP-1 it also carries the spec + headline_metrics + gate summary (read
    off the persisted deal — the spec is the source of truth, not the job)."""
    view: Dict[str, Any] = {
        "job_id": job.job_id,
        "deal_id": job.deal_id,
        "status": job.status.value,
        "phase": job.phase.value,
        "routing": job.routing,
        "mode": job.mode,
        "cancel_requested": job.cancel_requested,
        "error": job.error,
        "open_questions": _open_questions(job),
        "blocking_questions": [q.to_dict() for q in job.blocking_questions()],
    }
    if job.status == JobStatus.AWAITING_CP1:
        try:
            deal = deal_store.get(job.deal_id)
            spec = deal.spec
            view["spec"] = spec
            view["headline_metrics"] = spec.get("headline_metrics", {})
            view["gate_summary"] = spec.get("qa", {})
        except DealNotFound:  # pragma: no cover
            pass
    return view


# ---------------------------------------------------------------------------
# Dependency seams (overridable in tests via app.dependency_overrides or module globals)
# ---------------------------------------------------------------------------

def get_analysts():
    """Select the Wave-1 analytical set (ENV-gated Kimi/Stub switch).

    Default is StubAnalysts (no LLM, no network) so the standard test/dev path stays
    deterministic and offline. The live KimiAnalysts set is opt-in and FAIL-SAFE:

      * DREAM_USE_KIMI must be truthy ("1", "true", "yes", "on"), AND
      * KIMI_API_KEY must be present and non-empty.

    If the flag is set but no key is configured, we log a warning and fall back to
    StubAnalysts rather than raising — the request must never 500 over a missing key.
    KimiAnalysts pins the long-deal-doc model via KIMI_MODEL_FASTPATH (default
    moonshot-v1-128k, read in jobs/analysts.py) and builds its Moonshot client LAZILY,
    so selecting it here performs no network call.
    """
    use_kimi = os.environ.get("DREAM_USE_KIMI", "").strip().lower() in ("1", "true", "yes", "on")
    if not use_kimi:
        return StubAnalysts()
    api_key = os.environ.get("KIMI_API_KEY", "").strip()
    if not api_key:
        logger.warning(
            "DREAM_USE_KIMI is set but KIMI_API_KEY is empty; falling back to StubAnalysts "
            "(fail-safe). Set KIMI_API_KEY to enable the live Kimi analytical set."
        )
        return StubAnalysts()
    logger.info(
        "DREAM_USE_KIMI enabled and KIMI_API_KEY present; using KimiAnalysts (model=%s).",
        os.environ.get("KIMI_MODEL_FASTPATH", "moonshot-v1-128k"),
    )
    return KimiAnalysts()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("")
@router.post("/")
def submit_job(req: SubmitJobRequest):
    """Create deal + job (idempotent), run Wave 0, and either stop at AWAITING_INPUT or run the
    full pipeline to CP-1 synchronously."""
    js: SQLiteJobStore = get_job_store()
    ds: DealStore = get_deal_store()
    ts = _now()

    # Idempotent replay FIRST — before any deal row is created. A retried POST (timeout, dropped
    # connection) must return the existing job's view and never orphan a draft deal.
    existing = js.find_by_idempotency(req.idempotency_key)
    if existing is not None:
        return _job_view(existing, ds)

    # --- create the canonical deal record (the spec is filled at synthesis) ---
    # intake_payload preserves the ORIGINAL submission so an AWAITING_INPUT resume re-runs with
    # the full deal package (docs + summary), not just the answered questions. It lives on the
    # seed spec only; the synthesis ds.put replaces the spec at CP-1, by which point resume is over.
    seed_spec = {
        "meta": {
            "deal_name": req.deal_name or req.intake_summary.get("deal_name", ""),
            "slug": (req.intake_summary.get("slug")
                     or (req.deal_name or "deal").lower().replace(" ", "-")),
            "routing": (req.routing or "ACQ").upper(),
            "template": "acq-mini-model",
            "mode": "HITL",
        },
        "qa": {},
        "cells": [],
        "intake_payload": {
            "intake_summary": req.intake_summary,
            "deal_docs": req.deal_docs,
        },
    }
    deal = ds.create(seed_spec, owner=req.owner, now_iso=ts, status="draft")
    job = js.create_job(
        deal_id=deal.deal_id, routing=(req.routing or "ACQ"), owner=req.owner,
        now_iso=ts, idempotency_key=req.idempotency_key,
    )

    # Idempotent replay: an existing job (same key) already past SUBMITTED — return its view as-is.
    if job.status != JobStatus.SUBMITTED:
        return _job_view(js.get_job(job.job_id), ds)

    analysts = get_analysts()
    try:
        final = run_job(
            job.job_id, analysts=analysts, now_iso=ts,
            intake_summary=req.intake_summary, deal_docs=req.deal_docs,
            job_store=js, deal_store=ds,
        )
    except Exception as e:  # noqa: BLE001 — runner already FAILed the job; surface the error
        raise HTTPException(status_code=422, detail=str(e))
    return _job_view(final, ds)


@router.get("/{job_id}")
def get_job(job_id: str):
    js = get_job_store()
    ds = get_deal_store()
    try:
        job = js.get_job(job_id)
    except JobNotFound:
        raise HTTPException(status_code=404, detail=f"job '{job_id}' not found")
    return _job_view(job, ds)


@router.post("/{job_id}/answer")
def answer_job(job_id: str, req: AnswerRequest):
    """Record a human answer to an OpenQuestion. When the job was AWAITING_INPUT and no blocking
    questions remain, the pipeline RESUMES synchronously to CP-1."""
    js = get_job_store()
    ds = get_deal_store()
    ts = _now()
    try:
        js.answer_open_question(job_id, req.question_id, req.answer, now_iso=ts)
    except JobNotFound:
        raise HTTPException(status_code=404, detail=f"job '{job_id}' not found")
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    job = js.get_job(job_id)
    # If we were blocked at AWAITING_INPUT and the answers cleared the blockers, resume the run.
    if job.status == JobStatus.AWAITING_INPUT and not job.has_blocking_questions():
        # Move back to ROUTING (legal: AWAITING_INPUT -> ROUTING) so the runner re-drives Wave 0.
        js.transition(job_id, JobStatus.ROUTING, ts)
        # Restore the ORIGINAL submission (persisted on the deal's seed spec at submit) and
        # overlay the answers — a resume must never analyze less than the user originally sent.
        answers = _summary_from_answers(job)
        intake_payload: Dict[str, Any] = {}
        try:
            intake_payload = ds.get(job.deal_id).spec.get("intake_payload") or {}
        except DealNotFound:  # pragma: no cover — deal created at submit
            pass
        resumed_summary = dict(intake_payload.get("intake_summary") or {})
        merged_ci = dict(resumed_summary.get("critical_inputs") or {})
        merged_ci.update(answers.get("critical_inputs") or {})
        resumed_summary["critical_inputs"] = merged_ci
        if "routing" in answers:  # an answered routing question overrides the original signal
            resumed_summary["routing"] = answers["routing"]
        deal_docs = intake_payload.get("deal_docs") or {}
        try:
            final = run_job(job_id, analysts=get_analysts(), now_iso=ts,
                            intake_summary=resumed_summary, deal_docs=deal_docs,
                            job_store=js, deal_store=ds)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=422, detail=str(e))
        return _job_view(final, ds)
    return _job_view(job, ds)


@router.post("/{job_id}/cancel")
def cancel_job(job_id: str):
    js = get_job_store()
    ds = get_deal_store()
    ts = _now()
    try:
        job = js.request_cancel(job_id, now_iso=ts)
    except JobNotFound:
        raise HTTPException(status_code=404, detail=f"job '{job_id}' not found")
    return _job_view(job, ds)


def _summary_from_answers(job: JobRecord) -> Dict[str, Any]:
    """Reconstruct an intake summary from answered OpenQuestions so a resumed Wave 0 passes.
    Maps meta.critical_inputs.* and meta.routing answers back into the flat summary shape."""
    summary: Dict[str, Any] = {"critical_inputs": {}}
    for q in job.open_questions:
        if not q.answered:
            continue
        if q.field == "meta.routing":
            summary["routing"] = q.answer
        elif q.field.startswith("meta.critical_inputs."):
            key = q.field.rsplit(".", 1)[-1]
            summary["critical_inputs"][key] = q.answer
    return summary
