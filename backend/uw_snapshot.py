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


def _verdict_is_incomplete(verdict: str) -> bool:
    return verdict.strip().upper().startswith("INCOMPLETE")


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
        view["snapshot"] = {k: raw[k] for k in BLANK_KEEP if k in raw and k != "verdict"}
        return view
    if _verdict_is_incomplete(verdict):
        view["blank_reason"] = BLANK_INCOMPLETE
        view["snapshot"] = {k: copy.deepcopy(raw[k]) for k in BLANK_KEEP if k in raw}
        return view
    view["state"] = "ready"
    view["blank_reason"] = None
    view["snapshot"] = copy.deepcopy(raw)
    return view
