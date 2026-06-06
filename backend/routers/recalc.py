"""
/api/recalc — instant, deterministic recalculation (Wave A1.5).

This is the "tweak an assumption -> instant new returns" endpoint. The cardinal rule (PRD §6,
strategic-guidance Part 4): **never call an LLM to recalculate.** This module's ONLY heavy import
is ``engine_boundary`` (the Decimal seam over the validated skill engine). It deliberately does NOT
import the Kimi client or anything under ``agent/`` — the no-LLM import-graph test
(test_recalc_no_llm.py) asserts that, so a future regression that pulls an LLM into the recalc path
fails CI.

It is a separate router (not inline in main.py) precisely so its import graph stays LLM-free even
though main.py imports the Kimi client for the chat endpoints.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from engine_boundary import (
    ACQDealInputs,
    EFBDealInputs,
    run_acq_underwrite,
    run_efb_underwrite,
    run_underwrite,
    triangulate_exit_cap,
    size_agency_takeout,
    compute_hurdle,
    UnknownRoutingError,
)

router = APIRouter(prefix="/api", tags=["recalc"])


# ---------------------------------------------------------------------------
# Request / response models (floats; JSON-native; no Decimal anywhere)
# ---------------------------------------------------------------------------

class ACQRecalcRequest(BaseModel):
    """ACQ recalc inputs — mirrors engine_boundary.ACQDealInputs. Orchestration params have the
    Esplanade-validated defaults so a partial payload still reproduces ground truth."""
    bridge_loan: float
    bridge_rate: float
    bridge_io_years: int
    refi_loan: float
    refi_rate: float
    refi_io_years: int
    refi_amort_years: int = 30
    refi_year: int = 2

    total_equity: float = 0.0
    noi_series: List[float] = Field(default_factory=list)
    exit_cap: float = 0.06
    sale_year: int = 7
    costs_of_sale: float = 0.02

    servicing_spread: float = 0.0116
    refi_cost_pct: float = 0.02
    exit_on_forward_noi: bool = True

    gpr_series: Optional[List[float]] = None
    egi_series: Optional[List[float]] = None
    opex_series: Optional[List[float]] = None
    vacancy_series: Optional[List[float]] = None
    debt_service: Optional[List[float]] = None
    years: int = 10


@router.post("/recalc")
def recalc(req: ACQRecalcRequest):
    """Run the validated ACQ orchestration and return headline_metrics. Pure Python, no LLM."""
    try:
        inp = ACQDealInputs(**req.model_dump())
        return {"headline_metrics": run_acq_underwrite(inp)}
    except Exception as e:  # noqa: BLE001 — surface engine errors as 422
        raise HTTPException(status_code=422, detail=str(e))


# --- standalone calculators for the assumption dashboard (also LLM-free) ---

class ExitCapRequest(BaseModel):
    going_in_cap: float
    strategy: str = "value_add"
    forward_treasury: Optional[float] = None
    agency_spread: float = 0.0150
    neg_leverage_buffer: float = 0.0075
    comp_implied_cap: Optional[float] = None


@router.post("/recalc/exit-cap")
def recalc_exit_cap(req: ExitCapRequest):
    try:
        return triangulate_exit_cap(**req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))


class AgencySizingRequest(BaseModel):
    stabilized_noi: float
    stabilized_value: float
    refi_rate: float
    amort_years: int = 30
    target_dscr: float = 1.25
    max_ltv: float = 0.75
    min_debt_yield: float = 0.085


@router.post("/recalc/agency-sizing")
def recalc_agency_sizing(req: AgencySizingRequest):
    try:
        return size_agency_takeout(**req.model_dump())
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))


# ---------------------------------------------------------------------------
# B.5 — routed /api/underwrite/v2 (ACQ + EFB) via the validated skill engine.
# The legacy /api/underwrite (app's own efb_engine + DealInputs) stays untouched for the
# existing frontend; this is the new routed compute path. Also LLM-free.
# ---------------------------------------------------------------------------

class EFBUnderwriteRequest(BaseModel):
    stabilized_noi: float
    target_dscr: float = 1.15
    bond_rate: float = 0.05
    amortization_years: int = 35
    annual_property_tax_exempted: Optional[float] = None
    hold_years: int = 10


@router.post("/underwrite/v2")
def underwrite_v2(routing: str, body: dict):
    """Routed underwrite via the validated skill engine.
    routing=ACQ -> levered returns (acq_engine); routing=EFB -> bond sizing (lihtc_engine).
    `body` is the route's input fields (ACQRecalcRequest shape for ACQ, EFBUnderwriteRequest for EFB).
    Unknown keys are ignored so the body can carry extra UI fields."""
    try:
        return {"routing": routing.upper(), "headline_metrics": run_underwrite(routing, body)}
    except UnknownRoutingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/underwrite/efb")
def underwrite_efb(req: EFBUnderwriteRequest):
    """EFB-only convenience endpoint (typed body)."""
    try:
        return {"headline_metrics": run_efb_underwrite(EFBDealInputs(**req.model_dump()))}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))


# ---------------------------------------------------------------------------
# B.6 — sensitivity sweep (the assumption dashboard's grid). N deterministic recalcs over one
# input field's range. Pure Python, no LLM. (Goal-seek/reprice is a separate, future endpoint.)
# ---------------------------------------------------------------------------

class SensitivityRequest(BaseModel):
    """Sweep `field` across `values`, holding the rest of `base` fixed, and report `metric`
    for each. ACQ only (the sweep targets headline returns). Example:
    field='exit_cap', values=[0.055,0.06,0.065], metric='irr'."""
    base: ACQRecalcRequest
    field: str
    values: List[float]
    metric: str = "irr"


_ALLOWED_SWEEP_FIELDS = {
    "exit_cap", "refi_rate", "bridge_rate", "servicing_spread", "costs_of_sale",
    "total_equity", "refi_loan", "bridge_loan",
}
_ALLOWED_METRICS = {"irr", "equity_multiple", "coc_stabilized", "exit_value"}


@router.post("/recalc/sensitivity")
def recalc_sensitivity(req: SensitivityRequest):
    """Run one recalc per value in `values`, sweeping `field`. Returns a grid the dashboard plots."""
    if req.field not in _ALLOWED_SWEEP_FIELDS:
        raise HTTPException(status_code=400,
                            detail=f"field must be one of {sorted(_ALLOWED_SWEEP_FIELDS)}")
    if req.metric not in _ALLOWED_METRICS:
        raise HTTPException(status_code=400,
                            detail=f"metric must be one of {sorted(_ALLOWED_METRICS)}")
    base = req.base.model_dump()
    grid = []
    try:
        for v in req.values:
            trial = dict(base)
            trial[req.field] = v
            hm = run_acq_underwrite(ACQDealInputs(**trial))
            grid.append({"value": v, "metric": req.metric, "result": hm.get(req.metric)})
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=str(e))
    return {"field": req.field, "metric": req.metric, "grid": grid}
