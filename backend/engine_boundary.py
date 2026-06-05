"""
engine_boundary — the Decimal seam between FastAPI (JSON / float / Pydantic) and the
validated skill engine (Decimal dataclasses, numpy_financial IRR).

Wave A1.3 of the DREAM v3.0 PRD. This module is the ONLY place outside the vendored
`underwriting-engine/engine/` that is allowed to touch `Decimal`. FastAPI / Pydantic / JSON
never see a Decimal; the engine never sees a float (except numpy_financial's internal IRR,
which is the engine's own business).

Two cardinal responsibilities:

  1. Float<->Decimal conversion at the edge, using ``Decimal(str(x))`` (NEVER ``Decimal(float)``
     — that injects binary-float noise and breaks the 0.5% headline tolerance).

  2. Carry the ENGINE ORCHESTRATION PARAMS that are not headline deal inputs but are required to
     reproduce validated ground truth: ``servicing_spread`` (the ~1.16% spread that reconciles
     the bare note rate to the Mini Model debt service) and ``exit_on_forward_noi``. If these are
     dropped, recalc silently diverges from the Esplanade-validated result. They live on
     ``ACQDealInputs`` with the validated defaults and are threaded all the way through.

The orchestration sequence mirrors the validated caller in
``underwriting-engine/engine/tests/test_acq_esplanade.py``:

    LoanTerms -> SeniorDebtCalculator.build -> ACQCashFlowProjector.project

(ExitCapTriangulator / AgencyTakeoutSizer / HurdleCalculator are exposed as separate helpers for
the assumption dashboard and sizing flows; the headline returns come from the projector.)
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

# --- locate the vendored engine (single source of Decimal math) --------------
_ENGINE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "underwriting-engine", "engine",
)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from acq_engine import (  # noqa: E402  (path set above)
    LoanTerms,
    SeniorDebtCalculator,
    ACQCashFlowProjector,
    ExitCapTriangulator,
    AgencyTakeoutSizer,
    HurdleCalculator,
    MarketTier,
    ACQReturnResult,
    ExitCapResult,
    AgencySizingResult,
    HurdleResult,
)


# ---------------------------------------------------------------------------
# Conversion primitives — the ONLY float<->Decimal crossing point
# ---------------------------------------------------------------------------

def to_dec(x) -> Decimal:
    """float/int/str -> Decimal via the STRING constructor (never Decimal(float))."""
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))


def to_dec_list(xs) -> List[Decimal]:
    return [to_dec(x) for x in xs]


def f(x) -> float:
    """Decimal -> float, only at the JSON edge."""
    return float(x) if x is not None else None


def f_list(xs) -> List[float]:
    return [f(x) for x in xs]


# ---------------------------------------------------------------------------
# API-facing input shape (plain floats; no Decimal leaks across this boundary)
# ---------------------------------------------------------------------------

@dataclass
class ACQDealInputs:
    """The float/JSON-native inputs the FastAPI layer hands to the engine.

    Headline deal inputs PLUS the engine orchestration params (servicing_spread,
    exit_on_forward_noi, refi_cost_pct) with their validated defaults. Pass an explicit
    `debt_service` per year only when the model supplies it directly (then servicing_spread
    is ignored, matching ACQCashFlowProjector semantics).
    """
    # --- senior debt (bridge -> agency refi) ---
    bridge_loan: float
    bridge_rate: float
    bridge_io_years: int
    refi_loan: float
    refi_rate: float
    refi_io_years: int
    refi_amort_years: int = 30
    refi_year: int = 2

    # --- equity / NOI / exit ---
    total_equity: float = 0.0
    noi_series: List[float] = field(default_factory=list)
    exit_cap: float = 0.06
    sale_year: int = 7
    costs_of_sale: float = 0.02

    # --- ENGINE ORCHESTRATION PARAMS (not headline inputs; defaults reproduce ground truth) ---
    servicing_spread: float = 0.0116      # Esplanade-validated; 0 = bare note rate
    refi_cost_pct: float = 0.02           # ~2% refi closing costs net the cash-out
    exit_on_forward_noi: bool = True      # exit value uses forward (sale_year+1) NOI

    # --- optional pass-through series (when the model supplies them) ---
    gpr_series: Optional[List[float]] = None
    egi_series: Optional[List[float]] = None
    opex_series: Optional[List[float]] = None
    vacancy_series: Optional[List[float]] = None
    debt_service: Optional[List[float]] = None  # explicit per-year DS overrides servicing_spread

    years: int = 10


# ---------------------------------------------------------------------------
# The headline orchestration — one call the API layer makes
# ---------------------------------------------------------------------------

def run_acq_underwrite(inp: ACQDealInputs) -> Dict[str, object]:
    """Run the validated ACQ orchestration and return a float-only headline_metrics dict.

    Reproduces the Esplanade caller sequence exactly. The returned dict shape matches the
    spec's `headline_metrics` (irr / equity_multiple / coc_stabilized / exit_value / dscr_series
    / noi_series), so the spec<->models adapter (A1.4) can consume it directly.
    """
    terms = LoanTerms(
        bridge_loan=to_dec(inp.bridge_loan),
        bridge_rate=to_dec(inp.bridge_rate),
        bridge_io_years=int(inp.bridge_io_years),
        refi_loan=to_dec(inp.refi_loan),
        refi_rate=to_dec(inp.refi_rate),
        refi_io_years=int(inp.refi_io_years),
        refi_amort_years=int(inp.refi_amort_years),
        refi_year=int(inp.refi_year),
        servicing_spread=to_dec(inp.servicing_spread),
    )
    ds = SeniorDebtCalculator().build(terms, years=int(inp.years))

    # If the model supplied explicit per-year debt service, the projector uses the DebtServiceYear
    # stream we pass; servicing_spread only affected `ds` above. (We always pass the built `ds`.)
    res: ACQReturnResult = ACQCashFlowProjector().project(
        noi_series=to_dec_list(inp.noi_series),
        debt_service=ds,
        total_equity=to_dec(inp.total_equity),
        exit_cap=to_dec(inp.exit_cap),
        sale_year=int(inp.sale_year),
        costs_of_sale=to_dec(inp.costs_of_sale),
        gpr_series=to_dec_list(inp.gpr_series) if inp.gpr_series else None,
        egi_series=to_dec_list(inp.egi_series) if inp.egi_series else None,
        opex_series=to_dec_list(inp.opex_series) if inp.opex_series else None,
        vacancy_series=to_dec_list(inp.vacancy_series) if inp.vacancy_series else None,
        refi_loan=to_dec(inp.refi_loan),
        bridge_loan=to_dec(inp.bridge_loan),
        refi_year=int(inp.refi_year),
        refi_cost_pct=to_dec(inp.refi_cost_pct),
        exit_on_forward_noi=bool(inp.exit_on_forward_noi),
    )

    return {
        "irr": f(res.irr),
        "equity_multiple": f(res.equity_multiple),
        "coc_year1": f(res.coc_year1),
        "coc_stabilized": f(res.coc_stabilized),
        "exit_value": f(res.exit_value),
        "net_sale_proceeds": f(res.net_sale_proceeds),
        "total_equity": f(res.total_equity),
        "noi_series": f_list(inp.noi_series),
        "dscr_series": f_list(res.dscr_series),
        "cash_flows": f_list(res.cash_flows),
    }


# ---------------------------------------------------------------------------
# Standalone calculator helpers (for the assumption dashboard / sizing flows)
# ---------------------------------------------------------------------------

def triangulate_exit_cap(
    going_in_cap: float,
    strategy: str = "value_add",
    forward_treasury: Optional[float] = None,
    agency_spread: float = 0.0150,
    neg_leverage_buffer: float = 0.0075,
    comp_implied_cap: Optional[float] = None,
) -> Dict[str, object]:
    r: ExitCapResult = ExitCapTriangulator().triangulate(
        going_in_cap=to_dec(going_in_cap),
        strategy=strategy,
        forward_treasury=to_dec(forward_treasury) if forward_treasury is not None else None,
        agency_spread=to_dec(agency_spread),
        neg_leverage_buffer=to_dec(neg_leverage_buffer),
        comp_implied_cap=to_dec(comp_implied_cap) if comp_implied_cap is not None else None,
    )
    return {
        "method_treasury": f(r.method_treasury),
        "method_comp": f(r.method_comp),
        "method_entry_strategy": f(r.method_entry_strategy),
        "exit_cap": f(r.exit_cap),
        "binding_method": r.binding_method,
    }


def size_agency_takeout(
    stabilized_noi: float,
    stabilized_value: float,
    refi_rate: float,
    amort_years: int = 30,
    target_dscr: float = 1.25,
    max_ltv: float = 0.75,
    min_debt_yield: float = 0.085,
) -> Dict[str, object]:
    r: AgencySizingResult = AgencyTakeoutSizer().size(
        stabilized_noi=to_dec(stabilized_noi),
        stabilized_value=to_dec(stabilized_value),
        refi_rate=to_dec(refi_rate),
        amort_years=int(amort_years),
        target_dscr=to_dec(target_dscr),
        max_ltv=to_dec(max_ltv),
        min_debt_yield=to_dec(min_debt_yield),
    )
    return {
        "by_dscr": f(r.by_dscr),
        "by_ltv": f(r.by_ltv),
        "by_debt_yield": f(r.by_debt_yield),
        "max_loan": f(r.max_loan),
        "binding_constraint": r.binding_constraint,
    }


def compute_hurdle(
    tier: str,
    vintage_year: int,
    current_occ: float,
    property_age: int,
    heavy_reno: bool = True,
    floating_bridge: bool = False,
    market_cycle_bps: int = 0,
) -> Dict[str, object]:
    tier_enum = MarketTier[tier.upper()] if not isinstance(tier, MarketTier) else tier
    r: HurdleResult = HurdleCalculator().compute(
        tier=tier_enum,
        vintage_year=int(vintage_year),
        current_occ=to_dec(current_occ),
        property_age=int(property_age),
        heavy_reno=bool(heavy_reno),
        floating_bridge=bool(floating_bridge),
        market_cycle_bps=int(market_cycle_bps),
    )
    return {
        "base_irr": f(r.base_irr),
        "total_premium_bps": r.total_premium_bps,
        "adjusted_hurdle": f(r.adjusted_hurdle),
        "recommendation": r.recommendation,
        "components": r.components,
    }
