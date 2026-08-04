"""
backend/routers/deals.py — deal views + lifecycle writes (PRD §6, APIRouter prefix /api/deals).

The Pipeline screen needs a list of the user's deals, and the /deal/:id detail page needs the FULL
deal view (so a cold reload doesn't lose gates + open questions). `DealStore` already returns the
records; this router is the thin HTTP surface over it. Read endpoints:

  GET /api/deals             list deals (optional ?owner=&routing=&status= filters) ->
                             [{deal_id, deal_name, slug, routing, mode, status, owner, version,
                               created_at, updated_at, headline_metrics}]. Archived deals are
                             HIDDEN from the default listing (opt back in with
                             ?include_archived=1 or an explicit ?status=archived).
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

Write endpoints (Phase 4b — deal lifecycle; all mutations go through ds.put/ds.delete, NEVER raw
SQL — the spec stays the canonical document and the store re-derives its index from it):

  POST   /api/deals/{deal_id}/archive    soft-hide the deal (status -> "archived"; the prior
                             status is stashed additively on spec.meta.pre_archive_status so
                             unarchive can restore it). Idempotent: archiving an archived deal
                             returns the current view WITHOUT a version bump. -> 200 _deal_view.
  POST   /api/deals/{deal_id}/unarchive  restore the stashed pre-archive status (fallback:
                             "computed" when the spec carries headline_metrics, else "draft").
                             Idempotent on a non-archived deal. -> 200 _deal_view.
  DELETE /api/deals/{deal_id}            hard delete: the deal row AND its job rows. 409 while a
                             job is actively RUNNING for the deal (submitted/routing/analyzing/
                             synthesizing — cancel it first; human-paused states do not block).
                             -> 200 {"deleted": true, "deal_id": ...}.

`headline_metrics` is pulled from each record's spec (spec.headline_metrics), defaulting to {} for
un-computed drafts. No LLM (jobs.job_store imports contracts + the store package only; the
analysts/LLM modules stay out of this router's import graph). The router mounts standalone in
tests (TestClient with injected stores) exactly like routers/jobs.py, and is auth-gated at mount
time in main.py; the write handlers ALSO take a handler-level require_auth (FastAPI's dependency
cache dedupes it with the mount-time gate) so they know WHO is acting — in standalone test mounts
with no auth env configured, require_auth returns the local-dev stub user.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from auth_dep import require_auth  # noqa: E402
from store import get_deal_store, DealStore, DealRecord, DealNotFound  # noqa: E402
from store import get_crm_store  # noqa: E402  (Phase 5 — deal-delete CRM link cascade)
from jobs.contracts import JobRecord, RUNNING_STATUSES  # noqa: E402
from jobs.job_store import get_job_store  # noqa: E402

router = APIRouter(prefix="/api/deals", tags=["deals"])

# The job states that BLOCK a deal delete — canonical set lives in contracts.py (shared with the
# restart sweep). awaiting_input / awaiting_cp1 are human-paused (nothing executing), never block.
_RUNNING_STATUSES: frozenset = RUNNING_STATUSES


def _now() -> str:
    """Mint the write timestamp (same convention as routers/jobs.py — the stores keep no clock)."""
    return datetime.now(timezone.utc).isoformat()


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


def _assert_can_touch(rec_owner: str, user: Optional[Dict[str, Any]]) -> None:
    """Ownership seam for the write endpoints (archive/unarchive/delete all call it).

    v1 is PERMISSIVE — everyone-sees-all, per the product decision — so the permissive body is a
    no-op. The STRICT variant ships here too, env-gated behind DREAM_STRICT_OWNERSHIP, so turning
    ownership enforcement on later is an env flip, not a code change. Strict mode answers 404
    (never 403) on another owner's deal so the response doesn't leak that the deal_id exists."""
    strict = os.environ.get("DREAM_STRICT_OWNERSHIP", "").strip().lower() in (
        "1", "true", "yes", "on")
    # .strip().lower() matches how routers/jobs.py normalizes owner on WRITE — the two sides must
    # normalize identically or strict mode locks real owners out of their own deals.
    if strict and rec_owner and rec_owner != ((user or {}).get("email") or "").strip().lower():
        raise HTTPException(status_code=404, detail="deal not found")


def _get_deal_or_404(ds: DealStore, deal_id: str) -> DealRecord:
    try:
        return ds.get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")


@router.get("")
@router.get("/")
def list_deals(
    owner: Optional[str] = Query(default=None),
    routing: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    include_archived: Optional[str] = Query(default=None),
) -> List[Dict[str, Any]]:
    """List deals (newest first), optionally filtered by owner/routing/status. Archived deals are
    hidden from the DEFAULT listing (no status filter, no include_archived flag); an explicit
    ?status=archived passes through the store untouched, and ?include_archived=1 (or true) keeps
    archived rows in the unfiltered list. The filter is applied AFTER ds.list — the store's
    contract is unchanged."""
    ds: DealStore = get_deal_store()
    # Owners are WRITTEN lowercased (routers/jobs.py); normalize the filter so a mixed-case
    # ?owner=Charles@Example.com still matches.
    owner = owner.strip().lower() if owner else owner
    recs = ds.list(owner=owner, routing=routing, status=status)
    if status is None and str(include_archived or "").strip().lower() not in ("1", "true", "yes", "on"):
        recs = [r for r in recs if r.status != "archived"]
    return [_deal_view(rec) for rec in recs]


@router.post("/{deal_id}/archive")
def archive_deal(deal_id: str, user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Soft-hide a deal: status -> "archived" via ds.put (the spec stays canonical; the store
    re-derives the index). The prior status is stashed ADDITIVELY on spec.meta.pre_archive_status
    so unarchive restores exactly where the deal was. Idempotent: an already-archived deal comes
    back as-is, with NO version bump. 404 on unknown deal_id."""
    ds: DealStore = get_deal_store()
    rec = _get_deal_or_404(ds, deal_id)
    _assert_can_touch(rec.owner, user)
    if rec.status == "archived":
        return _deal_view(rec)
    spec = dict(rec.spec)
    spec.setdefault("meta", {})["pre_archive_status"] = rec.status
    rec = ds.put(deal_id, spec, expected_version=rec.version, now_iso=_now(), status="archived")
    return _deal_view(rec)


@router.post("/{deal_id}/unarchive")
def unarchive_deal(deal_id: str, user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Restore an archived deal to its stashed pre-archive status (meta.pre_archive_status is
    POPPED off the spec). Fallback when the stash is missing: "computed" if the spec carries a
    non-empty headline_metrics, else "draft". Idempotent: a deal that is not archived comes back
    as-is. 404 on unknown deal_id."""
    ds: DealStore = get_deal_store()
    rec = _get_deal_or_404(ds, deal_id)
    _assert_can_touch(rec.owner, user)
    if rec.status != "archived":
        return _deal_view(rec)
    spec = dict(rec.spec)
    meta = spec.setdefault("meta", {})
    restored = meta.pop("pre_archive_status", None)
    if not restored:
        restored = "computed" if spec.get("headline_metrics") else "draft"
    rec = ds.put(deal_id, spec, expected_version=rec.version, now_iso=_now(), status=restored)
    return _deal_view(rec)


@router.delete("/{deal_id}")
def delete_deal(deal_id: str, user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """HARD delete: remove the deal row (ds.delete) and every job row for it (the job store's
    delete_for_deal cascade — no orphaned jobs/audit). Guarded FIRST: while the deal's newest job
    is actively RUNNING (submitted/routing/analyzing/synthesizing) the delete answers 409 — cancel
    the job, then delete. Human-paused jobs (awaiting_input/awaiting_cp1) and terminal jobs never
    block. 404 on unknown deal_id."""
    ds: DealStore = get_deal_store()
    js = get_job_store()
    rec = _get_deal_or_404(ds, deal_id)
    _assert_can_touch(rec.owner, user)

    jobs = js.list_jobs(deal_id=deal_id)  # newest first (updated_at DESC)
    if jobs and jobs[0].status in _RUNNING_STATUSES:
        raise HTTPException(
            status_code=409,
            detail="a job is running for this deal; cancel it first",
        )

    ds.delete(deal_id)
    js.delete_for_deal(deal_id)
    # Phase 5 CRM cascade: a deleted deal leaves no dangling CRM links behind (contacts/tasks/notes
    # pinned to it are unpinned). The records themselves survive (a contact can belong to many
    # deals); only the target-pointers into THIS deal are removed. delete_links_for_target is a
    # single index DELETE in the store package (no sqlite3 here). 0 removed is fine (no CRM attached).
    get_crm_store().delete_links_for_target("deal", deal_id)
    return {"deleted": True, "deal_id": deal_id}


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
