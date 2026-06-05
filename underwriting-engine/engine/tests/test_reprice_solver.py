"""
RepriceSolver (BL-19) validation.

Goal-seeks the purchase price that clears a return floor when a deal is below hurdle, by
re-running the VALIDATED ACQCashFlowProjector at trial prices (the cash-flow math is reused,
never reimplemented). Forensic origin: Envy Pompano Beach cleared the IRR/EM floor only around
$56-57M vs the $74-75M ask; the reprice loop surfaces that haircut at CP-3.

Test contract (from the task):
  - a below-hurdle deal returns a clearing price that, RE-RUN, hits the floor within tolerance;
  - a deal already above hurdle returns below_hurdle=False (no solve);
  - a pathological no-solution case returns converged=False (no crash, clearing_price=None).
"""
import os
import sys
from decimal import Decimal as D
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acq_engine import (
    LoanTerms, SeniorDebtCalculator, ACQCashFlowProjector,
    RepriceSolver, RepriceResult,
)

# ---- An Envy-like deal harness: price -> projector inputs --------------------
# Stabilized NOI is property-driven (fixed); only the debt sizing + equity move with price.
# 85% LTV bridge, refi to 75% of stabilized value, 7yr hold, exit 6%, 3% closing.
_STAB_NOI_Y3 = D("3500000")
_EXIT_CAP = D("0.06")
_CLOSING = D("0.03")
_SALE_YEAR = 7
_STABILIZED_VALUE = _STAB_NOI_Y3 / _EXIT_CAP
_NOI_SERIES = [D(str(round(v))) for v in
               ([2600000, 3050000] + [3500000 * (1.025 ** i) for i in range(8)])]


def price_to_inputs(price: D) -> Dict:
    price = D(str(price))
    bridge_loan = price * D("0.85")
    refi_loan = _STABILIZED_VALUE * D("0.75")
    terms = LoanTerms(
        bridge_loan=bridge_loan, bridge_rate=D("0.08"), bridge_io_years=2,
        refi_loan=refi_loan, refi_rate=D("0.06"), refi_io_years=3,
        refi_amort_years=30, refi_year=2, servicing_spread=D("0.0116"),
    )
    ds = SeniorDebtCalculator().build(terms, years=10)
    equity = price * (D("1") + _CLOSING) - bridge_loan
    return dict(
        noi_series=_NOI_SERIES, debt_service=ds, total_equity=equity,
        exit_cap=_EXIT_CAP, sale_year=_SALE_YEAR, costs_of_sale=D("0.02"),
        refi_loan=refi_loan, bridge_loan=bridge_loan, refi_year=2,
        refi_cost_pct=D("0.02"), exit_on_forward_noi=True,
    )


def _irr_at(price: D) -> float:
    return float(ACQCashFlowProjector().project(**price_to_inputs(price)).irr)


def _em_at(price: D) -> float:
    return float(ACQCashFlowProjector().project(**price_to_inputs(price)).equity_multiple)


# ============================================================================ #
# Below-hurdle IRR deal -> clearing price re-runs to the floor within tolerance
# ============================================================================ #

def test_below_hurdle_clearing_price_reruns_to_floor():
    """$74M ask underwrites ~5.5% IRR; want 16%. Solver returns a clearing price that,
    fed back through the projector, hits 16% within tolerance."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
    )
    assert r.below_hurdle is True
    assert r.converged is True
    assert r.clearing_price is not None
    assert float(r.current_value) < 0.16  # the deal really is below the hurdle at ask
    # the deal cleared at a DISCOUNT to ask (Envy: ~$56-57M vs $74-75M)
    assert r.clearing_price < D("74000000")
    assert r.price_delta_pct is not None and r.price_delta_pct < 0
    # RE-RUN the projector at the clearing price -> must hit the target within tolerance
    rerun_irr = _irr_at(r.clearing_price)
    assert abs(rerun_irr - 0.16) <= 0.003, f"re-run IRR {rerun_irr:.4f} != target 0.16"


def test_below_hurdle_equity_multiple_target():
    """EM floor target: 2.0x. Clearing price re-runs to ~2.0x."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="equity_multiple", target_value=D("2.0"),
    )
    assert r.below_hurdle is True
    assert r.converged is True
    assert r.clearing_price is not None
    rerun_em = _em_at(r.clearing_price)
    assert abs(rerun_em - 2.0) <= 0.01, f"re-run EM {rerun_em:.3f} != target 2.0"


def test_hurdle_recommendation_drives_below_hurdle():
    """When HurdleResult.recommendation is REQUEST REPRICING/PASS, the solve runs regardless of
    the current metric (the recommendation, not a metric compare, sets below_hurdle)."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
        hurdle_recommendation="REQUEST REPRICING",
    )
    assert r.below_hurdle is True
    assert r.clearing_price is not None

    r2 = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
        hurdle_recommendation="PROCEED",
    )
    # PROCEED does NOT force a solve; below_hurdle falls back to the metric compare,
    # which here is True (5.5% < 16%) -> still solves. The point: the flag, not a crash.
    assert isinstance(r2, RepriceResult)


# ============================================================================ #
# Already-above-hurdle deal -> below_hurdle=False, no solve
# ============================================================================ #

def test_above_hurdle_returns_false_no_solve():
    """A cheap basis ($50M) already clears a 12% floor -> below_hurdle=False, no clearing price."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("50000000"),
        target_metric="irr", target_value=D("0.12"),
    )
    assert r.below_hurdle is False
    assert r.clearing_price is None
    assert r.price_delta_pct is None
    assert r.converged is True       # "nothing to solve" is a converged (clean) state
    assert r.iterations == 0
    assert float(r.current_value) >= 0.12


def test_explicit_below_hurdle_false_short_circuits():
    """An explicit below_hurdle=False short-circuits even if the metric would say otherwise."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
        below_hurdle=False,
    )
    assert r.below_hurdle is False
    assert r.clearing_price is None
    assert r.iterations == 0


# ============================================================================ #
# Pathological no-solution -> converged=False, clearing_price=None, no crash
# ============================================================================ #

def test_no_solution_within_bounds_returns_unconverged():
    """A 40% IRR is unreachable when the search floor is capped at 70% of ask. The solver must
    NOT crash, NOT loop forever, and must report converged=False with no clearing price."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.40"),
        price_floor_pct=D("0.70"), bracket_expansions=0,
    )
    assert r.below_hurdle is True
    assert r.converged is False
    assert r.clearing_price is None
    assert r.price_delta_pct is None
    assert "no clearing price" in r.reason.lower()


def test_degenerate_cashflow_does_not_crash():
    """A price so high that IRR goes NaN (no sign change) must be treated as below-floor, not
    propagate NaN. Solver still returns a clean result object."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("500000000"),  # absurd ask
        target_metric="irr", target_value=D("0.16"),
        price_floor_pct=D("0.95"), bracket_expansions=0,   # box it in near the absurd price
    )
    # Either it can't clear (converged False) — it must never raise / return NaN.
    assert isinstance(r, RepriceResult)
    assert r.clearing_price is None or float(r.clearing_price) > 0


def test_iterations_are_capped():
    """The solver never exceeds max_iter regardless of bracketing pathology."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
        max_iter=20,
    )
    assert r.iterations <= 20


def test_clearing_price_is_decimal_money_math():
    """All money outputs stay Decimal (no float leakage into the spec)."""
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
    )
    assert isinstance(r.clearing_price, D)
    assert isinstance(r.current_value, D)
    assert isinstance(r.target_value, D)
    assert isinstance(r.price_delta_pct, D)


if __name__ == "__main__":
    r = RepriceSolver().solve(
        price_to_inputs=price_to_inputs, current_price=D("74000000"),
        target_metric="irr", target_value=D("0.16"),
    )
    print(f"ask 74,000,000  IRR {float(r.current_value):.4f}  below_hurdle={r.below_hurdle}")
    print(f"clearing price {float(r.clearing_price):,.0f}  "
          f"({float(r.price_delta_pct)*100:.1f}% vs ask)  iters={r.iterations}")
    print(f"re-run IRR at clearing price: {_irr_at(r.clearing_price):.4f}")