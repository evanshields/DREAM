"""Builds the read-only UW Snapshot response from spec.uw_snapshot. No math on any value.

Values pass through exactly as stored. This module only checks the verdict string and drops keys.
The stored shape is a placeholder until the UW Director confirms the real one.
"""
from __future__ import annotations

import copy
from typing import Any, Dict, Optional

# Keys that stay visible when the snapshot is blank. Every number is withheld.
BLANK_KEEP = ("property_name", "verdict", "engine_version")

BLANK_NO_SNAPSHOT = "No underwriting snapshot has been produced for this deal yet."
BLANK_BAD_VERDICT = "The snapshot has no readable verdict, so no numbers are shown."
BLANK_INCOMPLETE = "Underwriting is INCOMPLETE, so no numbers are shown."
BLANK_BAD_SHAPE = "The snapshot is not in the expected shape, so no numbers are shown."

# Collections the panel iterates. Each must be a list of objects whose cells are plain scalars.
COLLECTION_KEYS = ("unit_mix", "seller_t12")


def _verdict_is_incomplete(verdict: str) -> bool:
    return verdict.strip().upper().startswith("INCOMPLETE")


def _is_scalar(v: Any) -> bool:
    return v is None or (isinstance(v, (str, int, float)) and not isinstance(v, bool))


def _collections_ok(raw: Dict[str, Any]) -> bool:
    for key in COLLECTION_KEYS:
        if key not in raw or raw[key] is None:
            continue
        rows = raw[key]
        if not isinstance(rows, list):
            return False
        for row in rows:
            if not isinstance(row, dict) or not all(_is_scalar(c) for c in row.values()):
                return False
    return True


def _safe_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Retained metadata must be a string. Anything else is dropped, never passed to the UI."""
    return {k: raw[k] for k in BLANK_KEEP if isinstance(raw.get(k), str)}


def build_uw_snapshot_view(deal_id: str, spec: Any) -> Dict[str, Any]:
    raw: Optional[Any] = spec.get("uw_snapshot") if isinstance(spec, dict) else None
    view: Dict[str, Any] = {
        "deal_id": deal_id,
        "state": "blank",
        "blank_reason": BLANK_NO_SNAPSHOT,
        "snapshot": None,
        "read_only": True,
    }
    if not isinstance(raw, dict):
        return view
    verdict = raw.get("verdict")
    if not isinstance(verdict, str) or not verdict.strip():
        view["blank_reason"] = BLANK_BAD_VERDICT
        meta = _safe_metadata(raw)
        meta.pop("verdict", None)
        view["snapshot"] = meta
        return view
    if _verdict_is_incomplete(verdict):
        view["blank_reason"] = BLANK_INCOMPLETE
        view["snapshot"] = _safe_metadata(raw)
        return view
    if not _collections_ok(raw):
        view["blank_reason"] = BLANK_BAD_SHAPE
        view["snapshot"] = _safe_metadata(raw)
        return view
    view["state"] = "ready"
    view["blank_reason"] = None
    snap = copy.deepcopy(raw)
    for k in BLANK_KEEP:
        if k in snap and not isinstance(snap[k], str):
            del snap[k]
    view["snapshot"] = snap
    return view
