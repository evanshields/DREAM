"""
backend/routers/deals.py — read-only deal views (PRD §6, APIRouter prefix /api/deals).

The Pipeline screen needs a list of the user's deals, and the /deal/:id detail page needs the FULL
deal view (so a cold reload doesn't lose gates + open questions). `DealStore` already returns the
records; this router is the thin HTTP surface over it. TWO endpoints:

  GET /api/deals             list deals (optional ?owner=&routing=&status= filters) ->
                             [{deal_id, deal_name, slug, routing, mode, status, owner, version,
                               created_at, updated_at, headline_metrics}]
  GET /api/deals/{deal_id}   the full deal view: the list-item fields PLUS the opaque canonical
                             spec, gate_summary (spec.qa), and the latest job block
                             {job_id, status, phase, error, open_questions, blocking_questions}
                             (null when the deal has no job). 404 on an unknown deal_id.
  GET /api/deals/{deal_id}/audit   the readable audit trail (PRD C.5): every job that ever ran
                             for the deal (newest job first), each with its APPEND-ONLY AuditEvent
                             list in insertion order -> {deal_id, jobs: [{job_id, status,
                             created_at, events: [{kind, message, detail?, ts}]}]}. Read-only —
                             it surfaces exactly what the runner already recorded (llm_call /
                             gate / spec_mutation / phase / error); no new event kinds.

`headline_metrics` is pulled from each record's spec (spec.headline_metrics), defaulting to {} for
un-computed drafts. Read-only — no writes, no LLM (jobs.job_store imports contracts + the store
package only; the analysts/LLM modules stay out of this router's import graph). The router mounts
standalone in tests (TestClient with injected stores) exactly like routers/jobs.py, and is
auth-gated at mount time in main.py (the router file itself stays dependency-free so its test
harness needs no token).
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store import get_deal_store, DealStore, DealRecord, DealNotFound  # noqa: E402
from jobs.contracts import JobRecord  # noqa: E402
from jobs.job_store import get_job_store  # noqa: E402

router = APIRouter(prefix="/api/deals", tags=["deals"])


def _headline_metrics(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Pull headline_metrics off the canonical spec; {} for un-computed drafts."""
    if isinstance(spec, dict):
        hm = spec.get("headline_metrics")
        if isinstance(hm, dict):
            return hm
    return {}


def _deal_view(rec: DealRecord) -> Dict[str, Any]:
    """The list-item shape (PRD §5/§6). The spec stays the source of truth — we surface only the
    thin index + headline_metrics, never the full spec blob (that lives on the deal detail view)."""
    return {
        "deal_id": rec.deal_id,
        "deal_name": rec.deal_name,
        "slug": rec.slug,
        "routing": rec.routing,
        "mode": rec.mode,
        "status": rec.status,
        "owner": rec.owner,
        "version": rec.version,
        "created_at": rec.created_at,
        "updated_at": rec.updated_at,
        "headline_metrics": _headline_metrics(rec.spec),
    }


def _gate_summary(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the QA gate summary (spec.qa) off the canonical spec; {} for un-computed drafts."""
    if isinstance(spec, dict):
        qa = spec.get("qa")
        if isinstance(qa, dict):
            return qa
    return {}


def _deal_job_view(job: JobRecord) -> Dict[str, Any]:
    """The job block on the deal detail view — the slice of _job_view (routers/jobs.py) the
    /deal/:id page needs to restore gates + open questions on a cold reload."""
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "phase": job.phase.value,
        "error": job.error,
        "open_questions": [q.to_dict() for q in job.open_questions],
        "blocking_questions": [q.to_dict() for q in job.blocking_questions()],
    }


@router.get("")
@router.get("/")
def list_deals(
    owner: Optional[str] = Query(default=None),
    routing: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
) -> List[Dict[str, Any]]:
    """List deals (newest first), optionally filtered by owner/routing/status. Read-only."""
    ds: DealStore = get_deal_store()
    return [_deal_view(rec) for rec in ds.list(owner=owner, routing=routing, status=status)]


@router.get("/{deal_id}/audit")
def get_deal_audit(deal_id: str) -> Dict[str, Any]:
    """The deal's readable audit trail (PRD C.5): ALL jobs for the deal, newest first, each
    carrying its append-only AuditEvent list in insertion (seq) order. Read-only; 404 on an
    unknown deal_id; a deal with no jobs returns jobs: []."""
    ds: DealStore = get_deal_store()
    try:
        ds.get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")

    jobs = get_job_store().list_jobs(deal_id=deal_id)  # newest first (updated_at DESC)
    return {
        "deal_id": deal_id,
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "created_at": job.created_at,
                "events": [
                    {
                        "kind": ev.kind,
                        "message": ev.summary,
                        **({"detail": ev.detail} if ev.detail else {}),
                        "ts": ev.ts,
                    }
                    # insertion order == monotonic seq (append-only; never mutated)
                    for ev in sorted(job.audit, key=lambda e: e.seq)
                ],
            }
            for job in jobs
        ],
    }


@router.get("/{deal_id}")
def get_deal(deal_id: str) -> Dict[str, Any]:
    """The full deal view for /deal/:id — list-item fields + the opaque canonical spec +
    gate_summary + the MOST RECENT job for this deal (or null). Read-only; 404 on unknown id."""
    ds: DealStore = get_deal_store()
    try:
        rec = ds.get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")

    view = _deal_view(rec)
    view["spec"] = rec.spec
    view["gate_summary"] = _gate_summary(rec.spec)

    # Latest job for this deal: list_jobs(deal_id=...) is parametrized SQL inside the store
    # package and returns newest-first (ORDER BY updated_at DESC) — first row wins.
    jobs = get_job_store().list_jobs(deal_id=deal_id)
    view["job"] = _deal_job_view(jobs[0]) if jobs else None
    return view
