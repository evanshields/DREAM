"""
backend/routers/crm.py — Phase 5 CRM HTTP surface (APIRouter, prefix /api).

Thin HTTP over SQLiteCRMStore (backend/store/crm_store.py), mirroring routers/deals.py's shape:
LLM-FREE import graph (store package + job_store only — no analysts/agent modules), owner derived
from the authenticated user (never the request body), all mutations through the store's put/delete
(the opaque doc stays canonical; the store re-derives its index). No sqlite3 anywhere near here.

Endpoints:

  Contacts (person | company):
    POST   /api/contacts                      create -> _contact_view (201-style body, 200 status)
    GET    /api/contacts?kind=&role=&owner=   list (newest first)
    GET    /api/contacts/{contact_id}         one; 404 on unknown
    PUT    /api/contacts/{contact_id}         update (optimistic version); 404/409
    DELETE /api/contacts/{contact_id}         delete + link cascade; 404

  Items (task | note):
    POST   /api/items                         create
    GET    /api/items?kind=&status=&owner=    list
    GET    /api/items/{item_id}               one; 404
    PUT    /api/items/{item_id}               update (optimistic version); 404/409
    POST   /api/items/{item_id}/toggle        task: flip open<->done (Twenty's useCompleteTask,
                                              re-implemented — flips status, nothing more); 404/409/400
    DELETE /api/items/{item_id}               delete + link cascade; 404

  Links (attach / detach source --> target; the "pin X to a deal" join):
    POST   /api/links                         attach; idempotent; -> _link_view
    DELETE /api/links/{link_id}               detach; {"detached": bool}

  Deal-scoped read helpers (what the DealDetail rail + timeline consume):
    GET    /api/deals/{deal_id}/contacts      contacts pinned to this deal (with their link_id)
    GET    /api/deals/{deal_id}/items?kind=   tasks/notes pinned to this deal (with their link_id)
    GET    /api/deals/{deal_id}/timeline      the unified timeline: a READ-TIME merge of the deal's
                                              append-only job audit events with the notes + tasks
                                              pinned to it, one sorted events[] feed grouped into
                                              months. The audit log is NEVER mutated — the timeline
                                              is a VIEW, not a second source of truth.

Version contract for writes: the client PUTs the version it last read; a stale version answers 409
(VersionConflict) so a concurrent edit is never silently clobbered — same rule as the deal store.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from auth_dep import require_auth  # noqa: E402
from store import (  # noqa: E402
    get_crm_store, CRMStore, ContactRecord, ItemRecord, LinkRecord,
    ContactNotFound, ItemNotFound, VersionConflict,
    get_deal_store, DealNotFound,
    CONTACT_KINDS, CONTACT_ROLES, ITEM_KINDS, TASK_STATUSES, LINKABLE_KINDS,
)
from jobs.job_store import get_job_store  # noqa: E402

router = APIRouter(prefix="/api", tags=["crm"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    """Mint the write timestamp (same convention as routers/deals.py — the stores keep no clock)."""
    return datetime.now(timezone.utc).isoformat()


def _owner_of(user: Optional[Dict[str, Any]]) -> str:
    """Server identity wins over any client-supplied owner (a client must not file records as
    someone else). Lowercased to match how routers/jobs.py + deals.py normalize owner."""
    return ((user or {}).get("email") or "").strip().lower()


def _contact_view(rec: ContactRecord) -> Dict[str, Any]:
    return {
        "contact_id": rec.contact_id,
        "kind": rec.kind,
        "name": rec.name,
        "role": rec.role,
        "company_id": rec.company_id,
        "primary_email": rec.primary_email,
        "owner": rec.owner,
        "version": rec.version,
        "created_at": rec.created_at,
        "updated_at": rec.updated_at,
        "doc": rec.doc,
    }


def _item_view(rec: ItemRecord) -> Dict[str, Any]:
    return {
        "item_id": rec.item_id,
        "kind": rec.kind,
        "status": rec.status,
        "title": rec.title,
        "due_at": rec.due_at,
        "author": rec.author,
        "owner": rec.owner,
        "version": rec.version,
        "created_at": rec.created_at,
        "updated_at": rec.updated_at,
        "doc": rec.doc,
    }


def _link_view(rec: LinkRecord) -> Dict[str, Any]:
    return {
        "link_id": rec.link_id,
        "source_kind": rec.source_kind,
        "source_id": rec.source_id,
        "target_kind": rec.target_kind,
        "target_id": rec.target_id,
        "created_at": rec.created_at,
    }


def _validate_contact_doc(doc: Dict[str, Any]) -> None:
    """Reject a malformed contact BEFORE it hits the store (400, not a 500). kind must be valid;
    a person's role (when given) must be in the enum; a company needs a name."""
    if not isinstance(doc, dict):
        raise HTTPException(status_code=400, detail="contact body must be an object")
    kind = doc.get("kind", "person")
    if kind not in CONTACT_KINDS:
        raise HTTPException(status_code=400,
                            detail=f"contact.kind must be one of {list(CONTACT_KINDS)}")
    if kind == "person":
        role = doc.get("role", "")
        if role and role not in CONTACT_ROLES:
            raise HTTPException(status_code=400,
                                detail=f"contact.role must be one of {list(CONTACT_ROLES)}")
        if not str(doc.get("full_name", "")).strip():
            raise HTTPException(status_code=400, detail="person contact requires full_name")
    else:  # company
        if not str(doc.get("name", "")).strip():
            raise HTTPException(status_code=400, detail="company contact requires name")


def _validate_item_doc(doc: Dict[str, Any]) -> None:
    """Reject a malformed task/note BEFORE the store. task status (when given) must be valid; a
    note needs a body; a task needs a title."""
    if not isinstance(doc, dict):
        raise HTTPException(status_code=400, detail="item body must be an object")
    kind = doc.get("kind", "task")
    if kind not in ITEM_KINDS:
        raise HTTPException(status_code=400,
                            detail=f"item.kind must be one of {list(ITEM_KINDS)}")
    if kind == "task":
        status = doc.get("status", "open")
        if status not in TASK_STATUSES:
            raise HTTPException(status_code=400,
                                detail=f"task.status must be one of {list(TASK_STATUSES)}")
        if not str(doc.get("title", "")).strip():
            raise HTTPException(status_code=400, detail="task requires title")
    else:  # note
        if not str(doc.get("body", "")).strip():
            raise HTTPException(status_code=400, detail="note requires body")


def _deal_or_404(deal_id: str) -> None:
    """The deal-scoped read helpers 404 on an unknown deal (never leak a made-up timeline)."""
    try:
        get_deal_store().get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@router.post("/contacts")
def create_contact(body: Dict[str, Any] = Body(...),
                   user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Create a person or company contact. Owner is the authenticated user (body owner ignored)."""
    _validate_contact_doc(body)
    crm: CRMStore = get_crm_store()
    rec = crm.create_contact(body, owner=_owner_of(user), now_iso=_now())
    return _contact_view(rec)


@router.get("/contacts")
def list_contacts(kind: Optional[str] = Query(default=None),
                  role: Optional[str] = Query(default=None),
                  owner: Optional[str] = Query(default=None)) -> List[Dict[str, Any]]:
    crm: CRMStore = get_crm_store()
    owner = owner.strip().lower() if owner else owner
    return [_contact_view(r) for r in crm.list_contacts(kind=kind, role=role, owner=owner)]


@router.get("/contacts/{contact_id}")
def get_contact(contact_id: str) -> Dict[str, Any]:
    crm: CRMStore = get_crm_store()
    try:
        return _contact_view(crm.get_contact(contact_id))
    except ContactNotFound:
        raise HTTPException(status_code=404, detail=f"contact '{contact_id}' not found")


@router.put("/contacts/{contact_id}")
def update_contact(contact_id: str, body: Dict[str, Any] = Body(...),
                   user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Update a contact. Body carries the full doc + `version` (the version last read). 409 on a
    stale version; 404 on unknown id. Owner is preserved (not reassignable via this route)."""
    _validate_contact_doc(body)
    version = body.get("version")
    if not isinstance(version, int):
        raise HTTPException(status_code=400, detail="update requires integer 'version'")
    doc = {k: v for k, v in body.items() if k != "version"}
    crm: CRMStore = get_crm_store()
    try:
        rec = crm.put_contact(contact_id, doc, expected_version=version, now_iso=_now())
    except ContactNotFound:
        raise HTTPException(status_code=404, detail=f"contact '{contact_id}' not found")
    except VersionConflict as e:
        raise HTTPException(status_code=409, detail=str(e))
    return _contact_view(rec)


@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: str,
                   user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Delete a contact AND its link rows (cascade in the store). 404 on unknown id."""
    crm: CRMStore = get_crm_store()
    try:
        crm.delete_contact(contact_id)
    except ContactNotFound:
        raise HTTPException(status_code=404, detail=f"contact '{contact_id}' not found")
    return {"deleted": True, "contact_id": contact_id}


# ---------------------------------------------------------------------------
# Items (tasks + notes)
# ---------------------------------------------------------------------------

@router.post("/items")
def create_item(body: Dict[str, Any] = Body(...),
                user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Create a task or note. Owner is the authenticated user."""
    _validate_item_doc(body)
    crm: CRMStore = get_crm_store()
    rec = crm.create_item(body, owner=_owner_of(user), now_iso=_now())
    return _item_view(rec)


@router.get("/items")
def list_items(kind: Optional[str] = Query(default=None),
               status: Optional[str] = Query(default=None),
               owner: Optional[str] = Query(default=None)) -> List[Dict[str, Any]]:
    crm: CRMStore = get_crm_store()
    owner = owner.strip().lower() if owner else owner
    return [_item_view(r) for r in crm.list_items(kind=kind, status=status, owner=owner)]


@router.get("/items/{item_id}")
def get_item(item_id: str) -> Dict[str, Any]:
    crm: CRMStore = get_crm_store()
    try:
        return _item_view(crm.get_item(item_id))
    except ItemNotFound:
        raise HTTPException(status_code=404, detail=f"item '{item_id}' not found")


@router.put("/items/{item_id}")
def update_item(item_id: str, body: Dict[str, Any] = Body(...),
                user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Update a task/note. Body carries the full doc + `version`. 409 on a stale version."""
    _validate_item_doc(body)
    version = body.get("version")
    if not isinstance(version, int):
        raise HTTPException(status_code=400, detail="update requires integer 'version'")
    doc = {k: v for k, v in body.items() if k != "version"}
    crm: CRMStore = get_crm_store()
    try:
        rec = crm.put_item(item_id, doc, expected_version=version, now_iso=_now())
    except ItemNotFound:
        raise HTTPException(status_code=404, detail=f"item '{item_id}' not found")
    except VersionConflict as e:
        raise HTTPException(status_code=409, detail=str(e))
    return _item_view(rec)


@router.post("/items/{item_id}/toggle")
def toggle_item(item_id: str, body: Dict[str, Any] = Body(default=None),
                user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Flip a TASK's status open<->done (Twenty's useCompleteTask, re-implemented: flips status,
    nothing more). Optional body {version}; when omitted the current version is used (the toggle
    is a single well-defined mutation, so a blind flip is safe). 400 on a note; 404 unknown;
    409 on the rare concurrent write when a version was supplied."""
    crm: CRMStore = get_crm_store()
    try:
        rec = crm.get_item(item_id)
    except ItemNotFound:
        raise HTTPException(status_code=404, detail=f"item '{item_id}' not found")
    if rec.kind != "task":
        raise HTTPException(status_code=400, detail="only tasks can be toggled")
    version = (body or {}).get("version")
    version = version if isinstance(version, int) else rec.version
    doc = dict(rec.doc)
    doc["status"] = "done" if rec.status == "open" else "open"
    try:
        updated = crm.put_item(item_id, doc, expected_version=version, now_iso=_now())
    except VersionConflict as e:
        raise HTTPException(status_code=409, detail=str(e))
    return _item_view(updated)


@router.delete("/items/{item_id}")
def delete_item(item_id: str,
                user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Delete a task/note AND its link rows (cascade). 404 on unknown id."""
    crm: CRMStore = get_crm_store()
    try:
        crm.delete_item(item_id)
    except ItemNotFound:
        raise HTTPException(status_code=404, detail=f"item '{item_id}' not found")
    return {"deleted": True, "item_id": item_id}


# ---------------------------------------------------------------------------
# Links (attach / detach)
# ---------------------------------------------------------------------------

@router.post("/links")
def create_link(body: Dict[str, Any] = Body(...),
                user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Attach source --> target ({source_kind, source_id, target_kind, target_id}). Idempotent:
    an identical link returns the existing row. Validates the kinds against LINKABLE_KINDS and
    checks that a contact/item/deal endpoint actually exists (a link into nothing is a 400/404)."""
    for k in ("source_kind", "source_id", "target_kind", "target_id"):
        if not str(body.get(k, "")).strip():
            raise HTTPException(status_code=400, detail=f"link requires '{k}'")
    sk, si = body["source_kind"], body["source_id"]
    tk, ti = body["target_kind"], body["target_id"]
    for kind in (sk, tk):
        if kind not in LINKABLE_KINDS:
            raise HTTPException(status_code=400,
                                detail=f"link kind must be one of {list(LINKABLE_KINDS)}")
    _assert_endpoint_exists(sk, si)
    _assert_endpoint_exists(tk, ti)
    crm: CRMStore = get_crm_store()
    rec = crm.create_link(sk, si, tk, ti, now_iso=_now())
    return _link_view(rec)


def _assert_endpoint_exists(kind: str, entity_id: str) -> None:
    """A link endpoint must resolve (no pinning to a non-existent record). 'deal' checks the deal
    store; 'contact'/'task'/'note' check the CRM store. Answers 404 on a missing endpoint."""
    crm: CRMStore = get_crm_store()
    if kind == "deal":
        try:
            get_deal_store().get(entity_id)
        except DealNotFound:
            raise HTTPException(status_code=404, detail=f"deal '{entity_id}' not found")
    elif kind == "contact":
        try:
            crm.get_contact(entity_id)
        except ContactNotFound:
            raise HTTPException(status_code=404, detail=f"contact '{entity_id}' not found")
    elif kind in ("task", "note"):
        try:
            it = crm.get_item(entity_id)
        except ItemNotFound:
            raise HTTPException(status_code=404, detail=f"{kind} '{entity_id}' not found")
        if it.kind != kind:
            raise HTTPException(status_code=400,
                                detail=f"'{entity_id}' is a {it.kind}, not a {kind}")


@router.delete("/links/{link_id}")
def delete_link(link_id: str,
                user: Optional[dict] = Depends(require_auth)) -> Dict[str, Any]:
    """Detach one link. Idempotent: detaching an unknown link is a no-op (detached: false)."""
    crm: CRMStore = get_crm_store()
    detached = crm.delete_link(link_id)
    return {"detached": detached, "link_id": link_id}


# ---------------------------------------------------------------------------
# Deal-scoped read helpers (the DealDetail rail consumes these)
# ---------------------------------------------------------------------------

@router.get("/deals/{deal_id}/contacts")
def list_deal_contacts(deal_id: str) -> List[Dict[str, Any]]:
    """Contacts pinned to this deal, each carrying the link_id that attached it (so the rail can
    detach with one call). 404 on unknown deal."""
    _deal_or_404(deal_id)
    crm: CRMStore = get_crm_store()
    out: List[Dict[str, Any]] = []
    for link in crm.list_links(source_kind="contact", target_kind="deal", target_id=deal_id):
        try:
            rec = crm.get_contact(link.source_id)
        except ContactNotFound:
            continue  # a link whose contact was hard-deleted out of band — skip, do not 500
        view = _contact_view(rec)
        view["link_id"] = link.link_id
        out.append(view)
    return out


@router.get("/deals/{deal_id}/items")
def list_deal_items(deal_id: str,
                    kind: Optional[str] = Query(default=None)) -> List[Dict[str, Any]]:
    """Tasks/notes pinned to this deal (optionally filtered by kind), each with its link_id.
    404 on unknown deal."""
    _deal_or_404(deal_id)
    crm: CRMStore = get_crm_store()
    out: List[Dict[str, Any]] = []
    for link in crm.list_links(target_kind="deal", target_id=deal_id):
        if link.source_kind not in ("task", "note"):
            continue
        try:
            rec = crm.get_item(link.source_id)
        except ItemNotFound:
            continue
        if kind is not None and rec.kind != kind:
            continue
        view = _item_view(rec)
        view["link_id"] = link.link_id
        out.append(view)
    return out


# ---------------------------------------------------------------------------
# Unified deal timeline — READ-TIME merge (audit + notes + tasks), month-grouped
# ---------------------------------------------------------------------------

_MONTHS = ("", "January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")


def _month_bucket(ts: str) -> str:
    """'Month Year' bucket label from an ISO ts (e.g. '2026-07-13...' -> 'July 2026'). Falls back
    to 'Undated' when the ts is empty/unparseable — a real event with no timestamp still shows."""
    if not ts or len(ts) < 7:
        return "Undated"
    try:
        year = int(ts[0:4]); month = int(ts[5:7])
        if 1 <= month <= 12:
            return f"{_MONTHS[month]} {year}"
    except (ValueError, IndexError):
        pass
    return "Undated"


@router.get("/deals/{deal_id}/timeline")
def get_deal_timeline(deal_id: str) -> Dict[str, Any]:
    """The unified deal timeline: a READ-TIME projection interleaving THREE sources into one
    sorted, month-grouped feed —
      1. the deal's append-only job AUDIT events (every job's AuditEvent list; NEVER mutated),
      2. NOTES pinned to the deal,
      3. TASKS pinned to the deal.
    Newest first. The audit log is untouched (this is a view, not a second source of truth); the
    read-time merge is correct at DREAM's volume (Twenty's write-time queue is overkill here).

    Shape: {deal_id, events: [{id, source:'audit'|'note'|'task', kind, ts, actor?, title,
    detail?, ...}], groups: [{month, ids: [...]}]}. 404 on unknown deal."""
    _deal_or_404(deal_id)
    crm: CRMStore = get_crm_store()
    events: List[Dict[str, Any]] = []

    # 1) Job audit events (append-only; read via the job store, never rewritten).
    for job in get_job_store().list_jobs(deal_id=deal_id):
        for ev in sorted(job.audit, key=lambda e: e.seq):
            events.append({
                "id": f"audit:{job.job_id}:{ev.seq}",
                "source": "audit",
                "kind": ev.kind,                      # phase | llm_call | gate | spec_mutation | error
                "ts": ev.ts,
                "actor": None,
                "title": ev.summary,
                **({"detail": ev.detail} if ev.detail else {}),
                "job_id": job.job_id,
            })

    # 2 + 3) Notes and tasks pinned to the deal.
    for link in crm.list_links(target_kind="deal", target_id=deal_id):
        if link.source_kind not in ("task", "note"):
            continue
        try:
            rec = crm.get_item(link.source_id)
        except ItemNotFound:
            continue
        if rec.kind == "note":
            events.append({
                "id": f"note:{rec.item_id}",
                "source": "note",
                "kind": "note",
                "ts": rec.created_at,
                "actor": rec.author or rec.owner,
                "title": rec.title or (rec.doc.get("body", "")[:80] if isinstance(rec.doc, dict) else ""),
                "body": rec.doc.get("body", "") if isinstance(rec.doc, dict) else "",
                "item_id": rec.item_id,
                "link_id": link.link_id,
            })
        else:  # task
            events.append({
                "id": f"task:{rec.item_id}",
                "source": "task",
                "kind": "task",
                "ts": rec.created_at,
                "actor": rec.author or rec.owner,
                "title": rec.title,
                "status": rec.status,
                "due_at": rec.due_at,
                "item_id": rec.item_id,
                "link_id": link.link_id,
                "version": rec.version,
            })

    # Sort newest first (empty ts sorts last so a real dated event always precedes an undated one).
    events.sort(key=lambda e: (e.get("ts") or ""), reverse=True)

    # Month grouping (newest month first, following the event order). Preserves the exact sorted
    # sequence — the frontend renders a "Month Year" separator, then that month's events.
    groups: List[Dict[str, Any]] = []
    seen: Dict[str, int] = {}
    for ev in events:
        bucket = _month_bucket(ev.get("ts") or "")
        if bucket not in seen:
            seen[bucket] = len(groups)
            groups.append({"month": bucket, "ids": []})
        groups[seen[bucket]]["ids"].append(ev["id"])

    return {"deal_id": deal_id, "events": events, "groups": groups}
