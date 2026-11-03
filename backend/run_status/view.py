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


def count_red_gates(run: dict[str, Any]) -> int:
    return sum(1 for g in run.get("gates", []) if g.get("status") == "red")


def count_missing_values(run: dict[str, Any]) -> int:
    return sum(1 for h in run.get("headline", []) if h.get("value") is None)


def is_stale(run: dict[str, Any]) -> bool:
    return (
        run.get("engine_commit") != run.get("current_engine_commit")
        or run.get("inputs_hash") != run.get("current_inputs_hash")
    )


def display_state(run: dict[str, Any]) -> str:
    """First match wins: failed, blocked, stale, in_progress, needs_input, needs_human_check, complete."""
    status = run.get("status")
    if status in ("failed", "cancelled"):
        return "failed"
    if count_red_gates(run) > 0:
        return "blocked"
    if is_stale(run):
        return "stale"
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
        "run_id": run["run_id"],
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
    view["is_stale"] = is_stale(run)
    view["read_only"] = True
    return view
