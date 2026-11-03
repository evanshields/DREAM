"""Builds the run status response from a fixture. Pure Python, no math on any value.

Values pass through exactly as stored. This module only counts items and compares strings.
"""
from __future__ import annotations

import copy
from typing import Any

IN_PROGRESS = ("submitted", "routing", "analyzing", "synthesizing")

STATE_SENTENCES = {
    "failed": "This run failed. No result was produced.",
    "blocked": "A quality check failed, so these numbers are for diagnosis only and are not a finished result.",
    "stale": "The engine version or the inputs changed since this run, so these numbers are out of date and are for diagnosis only.",
    "in_progress": "This run is still working. No numbers exist yet.",
    "needs_input": "This run is waiting for an answer from a person.",
    "needs_human_check": "A person must review this run. It cannot move forward from this screen.",
    "complete": "This run is complete.",
}


KNOWN_GATE_STATUSES = ("green", "amber", "not_run", "red")
SETTLED = ("completed", "awaiting_cp1")


def _gates(run: dict[str, Any]) -> list[Any]:
    gates = run.get("gates")
    return gates if isinstance(gates, list) else []


def count_red_gates(run: dict[str, Any]) -> int:
    return sum(1 for g in _gates(run) if isinstance(g, dict) and g.get("status") == "red")


def has_unverified_gates(run: dict[str, Any]) -> bool:
    """True when a gate result is unknown or malformed, or a settled run has no gates at all."""
    gates = _gates(run)
    if run.get("status") in SETTLED and not gates:
        return True
    return any(not isinstance(g, dict) or g.get("status") not in KNOWN_GATE_STATUSES for g in gates)


def has_bad_evidence(run: dict[str, Any]) -> bool:
    """True when evidence is missing, hash mismatched, unknown, or absent on a settled run."""
    evidence = run.get("evidence")
    items = evidence if isinstance(evidence, list) else []
    if run.get("status") in SETTLED and not items:
        return True
    return any(not isinstance(e, dict) or e.get("state") != "ok" for e in items)


def has_open_holds(run: dict[str, Any]) -> bool:
    return bool(run.get("holds"))


def count_missing_values(run: dict[str, Any]) -> int:
    return sum(1 for h in run.get("headline", []) if h.get("value") is None)


def is_stale(run: dict[str, Any]) -> bool:
    """Stale when provenance differs, or cannot be verified because a value is absent or blank."""
    pairs = (
        (run.get("engine_commit"), run.get("current_engine_commit")),
        (run.get("inputs_hash"), run.get("current_inputs_hash")),
    )
    return any(not a or not b or a != b for a, b in pairs)


def display_state(run: dict[str, Any]) -> str:
    """First match wins: failed, blocked, stale, in_progress, needs_input, needs_human_check, complete."""
    status = run.get("status")
    if status in ("failed", "cancelled"):
        return "failed"
    if count_red_gates(run) > 0 or has_unverified_gates(run) or has_bad_evidence(run):
        return "blocked"
    if is_stale(run):
        return "stale"
    if has_open_holds(run):
        return "needs_human_check"
    if status in IN_PROGRESS:
        return "in_progress"
    if status == "awaiting_input":
        return "needs_input"
    if status == "awaiting_cp1":
        return "needs_human_check"
    if status == "completed":
        return "complete"
    return "failed"  # unknown status fails closed


def build_summary(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run.get("run_id"),
        "deal_label": run.get("deal_label"),
        "display_state": display_state(run),
        "synthetic": run.get("synthetic") is True,
    }


def build_view(run: dict[str, Any]) -> dict[str, Any]:
    state = display_state(run)
    view = copy.deepcopy(run)
    view["display_state"] = state
    view["state_sentence"] = STATE_SENTENCES[state]
    view["values_are_diagnostic"] = state in ("blocked", "stale")
    view["missing_value_count"] = count_missing_values(run)
    view["red_gate_count"] = count_red_gates(run)
    view["unverified_gate_count"] = sum(
        1 for g in _gates(run) if not isinstance(g, dict) or g.get("status") not in KNOWN_GATE_STATUSES
    )
    view["is_stale"] = is_stale(run)
    view["read_only"] = True
    return view
