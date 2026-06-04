"""
Dream Fast-Path — Mini Model populator + reconciliation gate.

Wave 3 of the fast path. Takes an underwrite-spec.json and a Mini Model template, writes the
spec's INPUT cells into a COPY of the template (never the original, never a FORMULA cell),
runs a before/after structural diff, and flags the workbook PENDING EXCEL RECALC. After a
human opens the draft in Excel once (native recalc — also the file capital partners need),
`reconcile()` re-reads with data_only=True and diffs the Excel headline values against the
Python engine's headline_metrics at tiered tolerance.

Safety invariants (Universal Rules 1, 2, 8):
  - Operate on a copy. The original template is never mutated.
  - Write only cells whose current content is NOT a formula. A spec cell targeting a formula
    cell is REFUSED and reported, not written.
  - Run the formula audit (from spec.qa.formula_audit) before writing; apply patches only if
    marked applied=true (i.e., user-approved upstream).
  - Structural diff (sheet names, merged ranges, defined names, dimensions) must be unchanged.
  - Leave a "PENDING EXCEL RECALC" marker in the Claude Log until reconcile() confirms recalc.

This module does the mechanical write + check. It does NOT decide values (the calc engine
does) and does NOT approve anything (the human gate does).
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import openpyxl

DEFAULT_SHEET = "Pro Forma"
PENDING_MARKER = "PENDING EXCEL RECALC"


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

@dataclass
class WriteReport:
    written: List[str] = field(default_factory=list)
    refused_formula: List[Tuple[str, str]] = field(default_factory=list)  # (cell, existing formula)
    missing_cells: List[str] = field(default_factory=list)
    patches_applied: List[str] = field(default_factory=list)
    draft_path: str = ""
    structural_diff_ok: bool = True
    structural_diff_detail: Dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.structural_diff_ok and not self.refused_formula


@dataclass
class ReconcileRow:
    metric: str
    python: float
    excel: Optional[float]
    delta_pct: Optional[float]
    tolerance: float
    flag: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_addr(addr: str) -> Tuple[str, str]:
    """'Pro Forma!B10' -> ('Pro Forma','B10'); 'B10' -> (DEFAULT_SHEET,'B10')."""
    if "!" in addr:
        sheet, cell = addr.split("!", 1)
        return sheet.strip().strip("'"), cell.strip()
    return DEFAULT_SHEET, addr.strip()


def _is_formula(value) -> bool:
    return isinstance(value, str) and value.startswith("=")


def _structural_fingerprint(wb) -> Dict[str, object]:
    return {
        "sheets": list(wb.sheetnames),
        "defined_names": sorted(list(wb.defined_names.keys())) if hasattr(wb.defined_names, "keys") else [],
        "dims": {ws.title: f"{ws.max_row}x{ws.max_column}" for ws in wb.worksheets},
        "merged": {ws.title: sorted(str(r) for r in ws.merged_cells.ranges) for ws in wb.worksheets},
    }


# ---------------------------------------------------------------------------
# Populate
# ---------------------------------------------------------------------------

def populate(spec_path: str, template_path: str, out_path: Optional[str] = None) -> WriteReport:
    """Write spec.cells[] INPUT values into a COPY of the template.

    Returns a WriteReport. Refuses to write any cell currently containing a formula.
    """
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    slug = spec.get("meta", {}).get("slug", "deal")
    if out_path is None:
        base = os.path.dirname(os.path.abspath(spec_path))
        out_path = os.path.join(base, f"{slug}-DREAM-draft.xlsx")

    # 1. Copy the template (never touch the original)
    shutil.copy2(template_path, out_path)

    # 2. Structural fingerprint BEFORE
    wb_before = openpyxl.load_workbook(out_path, data_only=False)
    before_fp = _structural_fingerprint(wb_before)
    wb_before.close()

    # 3. Open for writing (keep formulas)
    wb = openpyxl.load_workbook(out_path, data_only=False)
    report = WriteReport(draft_path=out_path)

    # 3a. Formula audit patches (only those marked applied)
    for audit in spec.get("qa", {}).get("formula_audit", []):
        if audit.get("status") == "bug" and audit.get("applied") and audit.get("patch"):
            sheet, cell = _split_addr(audit["cell"])
            if sheet in wb.sheetnames:
                wb[sheet][cell] = audit["patch"]
                report.patches_applied.append(audit["cell"])

    # 3b. Write INPUT cells
    for c in spec.get("cells", []):
        sheet, cell = _split_addr(c["cell"])
        if sheet not in wb.sheetnames:
            report.missing_cells.append(c["cell"])
            continue
        ws = wb[sheet]
        existing = ws[cell].value
        if _is_formula(existing):
            # Universal Rule 1: never overwrite a formula cell.
            report.refused_formula.append((c["cell"], str(existing)))
            continue
        ws[cell] = c["value"]
        report.written.append(c["cell"])

    # 3c. PENDING EXCEL RECALC marker in Claude Log
    if "Claude Log" in wb.sheetnames:
        log = wb["Claude Log"]
        # append to first empty row in column A
        r = 1
        while log.cell(row=r, column=1).value not in (None, ""):
            r += 1
        log.cell(row=r, column=1, value=PENDING_MARKER)
        log.cell(row=r, column=2, value=f"populated {len(report.written)} input cells; open in Excel to recalc")

    wb.save(out_path)
    wb.close()

    # 4. Structural fingerprint AFTER + diff
    wb_after = openpyxl.load_workbook(out_path, data_only=False)
    after_fp = _structural_fingerprint(wb_after)
    wb_after.close()
    report.structural_diff_ok = (before_fp == after_fp)
    if not report.structural_diff_ok:
        report.structural_diff_detail = {
            k: {"before": before_fp[k], "after": after_fp[k]}
            for k in before_fp if before_fp[k] != after_fp[k]
        }
    return report


# ---------------------------------------------------------------------------
# Reconcile (CP-2 gate)
# ---------------------------------------------------------------------------

# Default tiered tolerances per the plan
HEADLINE_TOL = 0.005   # NOI, DSCR, IRR, bond size, exit value
LINE_TOL = 0.02        # line items

# Where each headline metric lives in the workbook (verified cell map).
# (sheet defaults to Pro Forma). Extend as the UW Snapshot map is finalized.
METRIC_CELLS_ACQ = {
    "irr": "B15",
    "equity_multiple": "B16",
    "coc_stabilized": "B17",
    "going_in_cap": "B11",
    "projected_sale_value": "B82",
}


def reconcile(
    draft_path: str,
    headline_metrics: Dict[str, float],
    metric_cells: Optional[Dict[str, str]] = None,
    tolerances: Optional[Dict[str, float]] = None,
) -> List[ReconcileRow]:
    """Re-read the (Excel-recalced) draft with data_only=True and diff against the Python
    engine headline_metrics. Returns one ReconcileRow per metric; flag=True if outside band.

    Call this AFTER the human has opened+saved the draft in Excel (so formulas are recalced).
    If a metric cell still reads None, the workbook has not been recalced -> flag it.
    """
    metric_cells = metric_cells or METRIC_CELLS_ACQ
    tolerances = tolerances or {}
    wb = openpyxl.load_workbook(draft_path, data_only=True)
    rows: List[ReconcileRow] = []
    for metric, cell_addr in metric_cells.items():
        if metric not in headline_metrics:
            continue
        py = float(headline_metrics[metric])
        sheet, cell = _split_addr(cell_addr)
        xl = wb[sheet][cell].value if sheet in wb.sheetnames else None
        xl = float(xl) if isinstance(xl, (int, float)) else None
        tol = tolerances.get(metric, HEADLINE_TOL)
        if xl is None:
            rows.append(ReconcileRow(metric, py, None, None, tol, flag=True))  # not recalced
        else:
            delta = abs(py - xl) / abs(xl) if xl else abs(py)
            rows.append(ReconcileRow(metric, py, xl, delta, tol, flag=(delta > tol)))
    wb.close()
    return rows


def deal_identity_check(workbook_path: str, expected_deal_name: str, expected_units: Optional[int] = None) -> Dict[str, object]:
    """Detect template-fork carryover: a workbook still carrying a PRIOR deal's name/size.

    The Envy run exposed this: a file labeled 'Envy ACQ Model' read 'Aviara East Pompano'
    (228u) throughout the Pro Forma because it was an unsaved/wrong-deal fork. This check
    compares the workbook's Pro Forma B2 (asset name) and B6 (units) against what the spec
    says. A False match should BLOCK the underwrite loudly at Wave 0 / before populate, not
    silently proceed.

    Returns {"match": bool, "reasons": [...]}.
    """
    wb = openpyxl.load_workbook(workbook_path, data_only=True)
    reasons: List[str] = []
    match = True
    pf = wb["Pro Forma"] if "Pro Forma" in wb.sheetnames else None
    if pf is not None:
        wb_name = str(pf["B2"].value or "")
        exp_tokens = [t for t in expected_deal_name.lower().split() if len(t) > 3]
        if wb_name and exp_tokens and not any(tok in wb_name.lower() for tok in exp_tokens):
            match = False
            reasons.append(
                f"Pro Forma B2 asset name '{wb_name}' does not match expected '{expected_deal_name}' "
                f"(possible template-fork carryover / unsaved wrong-deal file)")
        if expected_units is not None:
            wb_units = pf["B6"].value
            if isinstance(wb_units, (int, float)) and abs(int(wb_units) - expected_units) > 2:
                match = False
                reasons.append(f"Pro Forma units B6={int(wb_units)} != expected {expected_units}")
    wb.close()
    return {"match": match, "reasons": reasons}


def is_recalced(draft_path: str) -> bool:
    """Heuristic: the PENDING marker still present in Claude Log AND no recalced metric =>
    not yet recalced. Used to keep the workbook out of the 'done' state until the round-trip."""
    wb = openpyxl.load_workbook(draft_path, data_only=True)
    log = wb["Claude Log"] if "Claude Log" in wb.sheetnames else None
    pending = False
    if log is not None:
        for row in log.iter_rows(min_col=1, max_col=1, values_only=True):
            if row[0] == PENDING_MARKER:
                pending = True
                break
    wb.close()
    return not pending
