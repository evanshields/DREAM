"""
Server-side QA-gate harness (Wave A1.6).

Closes the PRD's biggest hole: the BL safety gates (fee-bounds BL-03, unit-count BL-01,
formula-integrity BL-07, deal-identity BL-02) live in the populator's Excel-WRITE path. The
chat-bot service (Wave C) runs the engine and emits a spec WITHOUT touching the populator — so the
gates would never fire. This harness runs the gate FUNCTIONS on the spec at COMPUTE time, writes
their results into ``spec.qa.*`` as structured fields, and returns a summary the API surfaces
non-collapsibly (BL-06) and HOTL hard-stops on (any RED downgrades HOTL -> HITL).

It calls the SAME validated gate functions the populator uses (from the vendored engine), so the
server path and the Excel path can never diverge.

The harness mutates a deep copy of the spec's ``qa`` block and returns ``(spec, summary)``. It does
NOT decide values and does NOT write Excel — it only runs the gates and records verdicts.
"""
from __future__ import annotations

import copy
import os
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

_ENGINE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "underwriting-engine", "engine",
)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from acq_engine import (  # noqa: E402
    assert_fee_bounds,
    UnitCountReconciler,
    formula_integrity_check,
)


def _dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


@dataclass
class GateSummary:
    """The non-collapsible gate result the API returns and HOTL checks."""
    ok: bool = True                              # False if any RED gate fired
    blocking: List[str] = field(default_factory=list)   # names of RED (blocking) gates
    warnings: List[str] = field(default_factory=list)   # non-blocking flags (e.g. single-source unit count)
    details: Dict[str, object] = field(default_factory=dict)  # per-gate structured verdict

    def as_dict(self) -> Dict[str, object]:
        return {
            "ok": self.ok,
            "blocking": self.blocking,
            "warnings": self.warnings,
            "details": self.details,
        }


def run_gates(
    spec: Dict[str, object],
    *,
    fee_override: Optional[bool] = None,
    classified_units: Optional[List[Dict]] = None,
    summary_tab_count: Optional[int] = None,
    second_source_count: Optional[int] = None,
    user_exclusions: Optional[List[str]] = None,
    template_formulas: Optional[Dict[str, str]] = None,
) -> tuple[Dict[str, object], GateSummary]:
    """Run the BL gates on the spec at compute time; write verdicts into spec.qa.*.

    Inputs beyond the spec are the gate evidence the orchestrator gathered (unit classification,
    a 2nd-source count, template formulas). When evidence is absent, that gate is skipped (not
    failed) EXCEPT unit-count with no source, which the reconciler itself blocks.

    Per-route behavior (meta.routing):
      * deal_identity (BL-02) and unit_count (BL-01) are routing-agnostic — both routes run them.
      * fee_bounds (BL-03) reads B45 on ACQ, B39 on EFB; the vendored assert_fee_bounds already
        passes the EFB route with a documented reason (5% IS the EFB default).
      * formula_audit (BL-07) runs on ACQ only; on EFB it is skipped EXPLICITLY with a
        documented reason written into qa.formula_audit (the fragile-cell table is ACQ-template
        calibrated) — never silently.

    Returns (spec_copy_with_qa_filled, GateSummary).
    """
    spec = copy.deepcopy(spec)
    meta = spec.get("meta", {})
    qa = spec.setdefault("qa", {})
    routing = str(meta.get("routing", "ACQ")).upper()
    summary = GateSummary()

    # --- BL-02 deal identity (already decided at Wave 0; surface it as a gate) ---
    identity = meta.get("deal_identity")
    if isinstance(identity, dict):
        match = identity.get("match")
        summary.details["deal_identity"] = {"match": match, "reasons": identity.get("reasons", [])}
        if match is False:
            summary.ok = False
            summary.blocking.append("deal_identity")

    # --- BL-03 fee bounds (acquisition fee) ---
    fee_cell = "B45" if routing == "ACQ" else "B39"
    fee_val = _find_cell_value(spec, fee_cell)
    if fee_val is not None:
        override = bool(fee_override) if fee_override is not None else bool(
            qa.get("fee_bounds", {}).get("override"))
        res = assert_fee_bounds(_dec(fee_val), routing=routing, override=override)
        qa["fee_bounds"] = {
            "value": float(res.value),
            "ok": res.ok,
            "is_sentinel": res.is_sentinel,
            "override": override,
            "reason": res.reason,
        }
        summary.details["fee_bounds"] = qa["fee_bounds"]
        if not res.ok:
            summary.ok = False
            summary.blocking.append("fee_bounds")

    # --- BL-01 unit count ---
    if classified_units is not None or summary_tab_count is not None or second_source_count is not None:
        res = UnitCountReconciler().reconcile(
            classified_units=classified_units or [],
            summary_tab_count=summary_tab_count,
            second_source_count=second_source_count,
            user_exclusions=user_exclusions,
        )
        qa["unit_count"] = {
            "counted": res.counted,
            "summary_tab": res.summary_tab,
            "second_source": res.second_source,
            "excluded_segments": res.excluded_segments,
            "reconciled": res.reconciled,
            "blocked": res.blocked,
            "single_source_warning": res.single_source_warning,
            "reasons": res.reasons,
        }
        summary.details["unit_count"] = qa["unit_count"]
        if res.blocked:
            summary.ok = False
            summary.blocking.append("unit_count")
        elif res.single_source_warning:
            summary.warnings.append("unit_count:single_source")

    # --- BL-07 formula integrity ---
    if routing == "EFB":
        # EXPLICIT SKIP (never silent): the BL-07 fragile-cell table (S40/B66/B67/row31/row32/
        # row78 with their canonical formulas) is calibrated to the ACQ mini-model template. No
        # EFB-template audit table exists yet, so running the ACQ expectations against an EFB
        # workbook would emit false PATCH verdicts. The skip is recorded in qa so CP-1 shows the
        # gate was considered and why it did not run.
        qa["formula_audit"] = {
            "skipped": True,
            "routing": routing,
            "reason": ("BL-07 fragile-cell table is calibrated to the ACQ mini-model template; "
                       "no EFB-template audit table exists yet — gate skipped explicitly rather "
                       "than run against the wrong template"),
        }
        summary.details["formula_audit"] = qa["formula_audit"]
    elif template_formulas:
        res = formula_integrity_check(template_formulas)
        qa["formula_audit"] = [
            {"cell": v.cell, "status": v.status, "expected": v.expected,
             "actual": v.actual, "patch": v.patch, "auto": v.auto, "applied": False}
            for v in res.verdicts
        ]
        summary.details["formula_audit"] = {
            "any_bug": res.any_bug, "patch_log": res.patch_log,
        }
        if res.any_bug:
            # A detected formula bug is a WARNING at compute time (patches are human-confirmed
            # before the populator applies them); it does not block compute, but it must surface.
            summary.warnings.append("formula_audit:bug_detected")

    return spec, summary


def _find_cell_value(spec: Dict[str, object], bare_cell: str):
    """Return the value of a cell from spec.cells[] by its bare address (sheet-agnostic)."""
    for c in spec.get("cells", []):
        addr = str(c.get("cell", ""))
        bare = addr.split("!", 1)[1] if "!" in addr else addr
        if bare.strip().upper() == bare_cell.upper():
            return c.get("value")
    return None
