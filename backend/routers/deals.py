"""
backend/routers/deals.py — read-only deal list (PRD §6, APIRouter prefix /api/deals).

The Pipeline screen needs a list of the user's deals. `DealStore.list(owner, routing, status)`
already returns the records; this router is the thin HTTP surface over it. ONE endpoint:

  GET /api/deals   list deals (optional ?owner=&routing=&status= filters) ->
                   [{deal_id, deal_name, slug, routing, mode, status, owner, version,
                     created_at, updated_at, headline_metrics}]

`headline_metrics` is pulled from each record's spec (spec.headline_metrics), defaulting to {} for
un-computed drafts. Read-only — no writes, no LLM. The router mounts standalone in tests
(TestClient with an injected DealStore) exactly like routers/jobs.py, and is auth-gated at mount
time in main.py (the router file itself stays dependency-free so its test harness needs no token).
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store import get_deal_store, DealStore, DealRecord  # noqa: E402

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
