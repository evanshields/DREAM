"""
/api/deals/{deal_id}/export + /reconcile — Wave D (App -> Excel push).

Productizes the vendored fastpath/populator.py (populate + reconcile + deal_identity_check) as
on-demand endpoints. This is the THIRD product-arc step: push the app's assumptions onto the user's
Excel Mini Model, then reconcile the user's Excel-recalced workbook back against the Python engine
(CP-2). The populator already does the hard part (writes INPUT cells only, refuses formula cells,
enforces the BL gates, structural-diff guard); these endpoints wrap it for the server.

Templates are USER-SUPPLIED uploads (Mini Models live in the user's Drive/acquisitions folders, not
the repo). The deal's spec comes from the DealStore. Decimal never crosses this layer — populator
operates on the spec JSON + the .xlsx directly.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

# vendored populator (fastpath sits beside engine under underwriting-engine/)
_FASTPATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "underwriting-engine", "fastpath",
)
if _FASTPATH not in sys.path:
    sys.path.insert(0, _FASTPATH)

import populator as _pop  # noqa: E402
from populator import IdentityMismatchError  # noqa: E402

# DealStore (backend/store)
_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)
from store import get_deal_store, DealNotFound  # noqa: E402

router = APIRouter(prefix="/api/deals", tags=["export"])


def _write_report_dict(rep: "_pop.WriteReport") -> dict:
    """Serialize a WriteReport to JSON, surfacing every BL-gate refusal (BL-06 non-collapsible)."""
    return {
        "ok": rep.ok,
        "written": rep.written,
        "written_count": len(rep.written),
        "identity_blocked": rep.identity_blocked,
        "structural_diff_ok": rep.structural_diff_ok,
        "structural_diff_detail": rep.structural_diff_detail,
        "refusals": {
            "formula": [{"cell": c, "existing": f} for c, f in rep.refused_formula],
            "fee_bounds": [{"cell": c, "reason": r} for c, r in rep.refused_fee_bounds],
            "unit_count": rep.refused_unit_count,
            "ltv": rep.refused_ltv,
            "rubs": rep.refused_rubs,
            "exit_cap": rep.refused_exit_cap,
        },
        "missing_cells": rep.missing_cells,
        "patches_applied": rep.patches_applied,
        "patch_log": rep.patch_log,
        "draft_path": rep.draft_path,
    }


@router.post("/{deal_id}/export")
async def export_to_excel(
    deal_id: str,
    template: UploadFile = File(..., description="The Mini Model .xlsx template to populate into"),
    download: bool = Form(default=False, description="If true, stream the draft .xlsx back; else return the WriteReport JSON"),
):
    """Populate the deal's spec INPUT cells into a COPY of the uploaded Mini Model template.

    Returns the WriteReport (written cells + every BL-gate refusal + structural diff). If the
    populator blocked (identity mismatch / fee sentinel / unit-count / etc.), `ok` is false and the
    refusals enumerate why — nothing partial is hidden. With download=true and a clean populate,
    streams the draft .xlsx (marked PENDING EXCEL RECALC) for the user to open + recalc in Excel.
    """
    store = get_deal_store()
    try:
        rec = store.get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")

    if not str(template.filename or "").lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="template must be a .xlsx Mini Model")

    workdir = tempfile.mkdtemp(prefix=f"dream-export-{deal_id}-")
    spec_path = os.path.join(workdir, "underwrite-spec.json")
    template_path = os.path.join(workdir, "template.xlsx")
    try:
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(rec.spec, f)
        with open(template_path, "wb") as f:
            f.write(await template.read())

        report = _pop.populate(spec_path, template_path)
        payload = _write_report_dict(report)

        # A draft is shippable whenever one was written, the structure is intact, and identity
        # wasn't blocked. Formula-cell refusals are EXPECTED (the populator always refuses to
        # overwrite formulas) and do NOT make the draft un-shippable — they're reported, not fatal.
        draft_shippable = bool(
            report.draft_path
            and os.path.exists(report.draft_path)
            and report.structural_diff_ok
            and not report.identity_blocked
        )
        if download and draft_shippable:
            slug = (rec.spec.get("meta", {}) or {}).get("slug", deal_id)
            return FileResponse(
                report.draft_path,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"{slug}-DREAM-draft.xlsx",
            )
        return payload
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{deal_id}/reconcile")
async def reconcile_excel(
    deal_id: str,
    draft: UploadFile = File(..., description="The Excel-recalced draft .xlsx (opened + saved in Excel)"),
    require_identity_match: bool = Form(default=True),
):
    """CP-2 reconciliation: diff the user's Excel-recalced draft against the engine's headline_metrics
    at tiered tolerance (headlines 0.5% / line items 2%). A deal-identity mismatch raises (409) — never
    silently degrade to a transcript comparison (BL-05). A metric cell reading None => not recalced
    (flagged)."""
    store = get_deal_store()
    try:
        rec = store.get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")

    headline = (rec.spec.get("headline_metrics") or {})
    if not headline:
        raise HTTPException(status_code=409,
                            detail="deal has no headline_metrics to reconcile against (run the underwrite first)")
    identity = (rec.spec.get("meta", {}) or {}).get("deal_identity")

    workdir = tempfile.mkdtemp(prefix=f"dream-reconcile-{deal_id}-")
    draft_path = os.path.join(workdir, "draft-recalced.xlsx")
    try:
        with open(draft_path, "wb") as f:
            f.write(await draft.read())
        rows = _pop.reconcile(
            draft_path,
            {k: float(v) for k, v in headline.items() if isinstance(v, (int, float))},
            identity=identity,
            require_identity_match=require_identity_match,
        )
    except IdentityMismatchError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))

    out = [{"metric": r.metric, "python": r.python, "excel": r.excel,
            "delta_pct": r.delta_pct, "tolerance": r.tolerance, "flag": r.flag} for r in rows]
    any_flag = any(r["flag"] for r in out)
    not_recalced = any(r["excel"] is None for r in out)
    return {
        "deal_id": deal_id,
        "reconciled": not any_flag,
        "not_recalced": not_recalced,
        "rows": out,
        "note": "open the draft in Excel and save once before reconciling" if not_recalced else "",
    }
