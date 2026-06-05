"""
BL-13 PropertyTaxRangeEstimator tests.

Validates:
- FL county-method: Year-1 carry-over + Year-2 reassessed range; low < point < high;
  exemption_delta positive when efb_preview=True.
- TX county-method: basic range correctness; basis tag.
- GA flat-ratio (statutory 40%): low == point == high (flat statutory ratio).
- Flat-ratio fallback (no assessed_value): basis="flat-ratio", still passes low<=point<=high.
- PropertyTaxCalculator.project() flat-ratio path: still works unmodified (non-regression).
"""
import os
import sys
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import acq_engine as ax


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rel(a, b):
    fa, fb = float(a), float(b)
    return abs(fa - fb) / abs(fb) if fb else abs(fa)


# ---------------------------------------------------------------------------
# FL county-method — waterfront scenario
# ---------------------------------------------------------------------------

# Scenario: FL waterfront multifamily, $36M purchase price.
# CoStar shows: current tax $187,432; current assessed $9,856,000 (seller's cycle).
# millage derived: 187432 / 9856000 ≈ 1.901%.
# agent-marketdata supplies Year-2 assessed_value = $36M × 0.80 = $28,800,000.
# Expected point (Year-2): $28,800,000 × 0.01901 ≈ $547,488.

FL_PP       = D("36000000")
FL_MILLAGE  = D(str(187432 / 9856000))       # ≈ 0.019019...
FL_AV       = D("28800000")                   # 80% × $36M (county-method)
FL_Y1_TAX   = D("187432")                     # carry-over Year-1 bill


def test_fl_waterfront_low_lt_point_lt_high():
    """Core BL-13 assertion: FL county-method produces low < point < high."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=FL_PP,
        state="FL",
        millage=FL_MILLAGE,
        assessed_value=FL_AV,
        fl_year1_tax=FL_Y1_TAX,
        citation="CoStar Property Summary (tax $187,432 / assessed $9,856,000 = 1.901%)",
    )
    assert r.basis == "county-method"
    assert r.low < r.point, f"low {float(r.low):,.0f} must be < point {float(r.point):,.0f}"
    assert r.point < r.high, f"point {float(r.point):,.0f} must be < high {float(r.high):,.0f}"


def test_fl_waterfront_point_matches_county_assessed():
    """POINT = agent-marketdata assessed_value × millage (Year-2 figure)."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=FL_PP,
        state="FL",
        millage=FL_MILLAGE,
        assessed_value=FL_AV,
        fl_year1_tax=FL_Y1_TAX,
        citation="test",
    )
    expected_point = FL_AV * FL_MILLAGE
    assert _rel(r.point, expected_point) < 1e-9, (
        f"point {float(r.point):,.0f} should equal assessed_value × millage "
        f"{float(expected_point):,.0f}"
    )


def test_fl_waterfront_low_is_year1_carryover():
    """LOW = fl_year1_tax (the pre-sale assessment carry-over, typically much lower)."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=FL_PP,
        state="FL",
        millage=FL_MILLAGE,
        assessed_value=FL_AV,
        fl_year1_tax=FL_Y1_TAX,
        citation="test",
    )
    # LOW should be the carry-over Year-1 bill.
    assert r.low == FL_Y1_TAX, (
        f"low {float(r.low):,.0f} should equal fl_year1_tax {float(FL_Y1_TAX):,.0f}"
    )


def test_fl_exemption_delta_positive_when_efb_preview():
    """When efb_preview=True, exemption_delta = POINT (annual saving going to $0 tax)."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=FL_PP,
        state="FL",
        millage=FL_MILLAGE,
        assessed_value=FL_AV,
        fl_year1_tax=FL_Y1_TAX,
        efb_preview=True,
        citation="test",
    )
    assert r.exemption_delta is not None
    assert r.exemption_delta > D("0"), "EFB exemption delta should be positive"
    assert r.exemption_delta == r.point, "exemption_delta should equal point"


def test_fl_no_efb_preview_delta_is_none():
    """When efb_preview=False (default), exemption_delta is None."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=FL_PP,
        state="FL",
        millage=FL_MILLAGE,
        assessed_value=FL_AV,
        fl_year1_tax=FL_Y1_TAX,
        citation="test",
    )
    assert r.exemption_delta is None


# ---------------------------------------------------------------------------
# TX county-method
# ---------------------------------------------------------------------------

TX_PP      = D("75000000")
TX_MILLAGE = D("0.0245")   # Denton ISD + county + city blended (from the reference example)
TX_AV      = D("48750000")  # 65% × $75M


def test_tx_county_method_basics():
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=TX_PP,
        state="TX",
        millage=TX_MILLAGE,
        assessed_value=TX_AV,
        citation="Denton CAD; cross-checked 3 comps (64%/67%/65%)",
    )
    assert r.basis == "county-method"
    assert r.point == TX_AV * TX_MILLAGE
    assert r.low <= r.point <= r.high
    assert r.assessed_value == TX_AV


def test_tx_county_method_range_uses_state_endpoints():
    """HIGH should be purchase_price × 0.70 × millage for TX."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=TX_PP,
        state="TX",
        millage=TX_MILLAGE,
        assessed_value=TX_AV,
        citation="test",
    )
    expected_high = TX_PP * D("0.70") * TX_MILLAGE
    assert _rel(r.high, expected_high) < 1e-9, (
        f"TX high {float(r.high):,.0f} should equal PP × 0.70 × millage "
        f"{float(expected_high):,.0f}"
    )


# ---------------------------------------------------------------------------
# GA flat-ratio (statutory 40%, lo=mid=hi)
# ---------------------------------------------------------------------------

GA_PP      = D("86750000")
GA_MILLAGE = D("0.045")   # DeKalb blended (reference example)


def test_ga_flat_ratio_fallback_low_eq_point_eq_high():
    """GA statutory ratio is fixed at 40%; LOW == POINT == HIGH when no county method."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=GA_PP,
        state="GA",
        millage=GA_MILLAGE,
        citation="statutory GA 40% ratio",
    )
    assert r.basis == "flat-ratio"
    assert r.low == r.point == r.high, (
        f"GA statutory: low={float(r.low):,.0f} point={float(r.point):,.0f} "
        f"high={float(r.high):,.0f} — should all be equal"
    )
    expected = GA_PP * D("0.40") * GA_MILLAGE
    assert _rel(r.point, expected) < 1e-9


def test_ga_county_method_range_is_tight():
    """With a county-supplied assessed value in GA, range still valid."""
    est = ax.PropertyTaxRangeEstimator()
    av = GA_PP * D("0.40")
    r = est.estimate(
        purchase_price=GA_PP,
        state="GA",
        millage=GA_MILLAGE,
        assessed_value=av,
        citation="DeKalb County Assessor",
    )
    assert r.basis == "county-method"
    assert r.low <= r.point <= r.high


# ---------------------------------------------------------------------------
# FL flat-ratio fallback (no assessed_value from agent-marketdata)
# ---------------------------------------------------------------------------

def test_fl_flat_ratio_fallback_produces_valid_range():
    """When no county assessed_value is supplied, falls back to flat-ratio FL 80%."""
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=FL_PP,
        state="FL",
        millage=FL_MILLAGE,
        citation="flat-ratio fallback (no agent-marketdata county assessed value)",
    )
    assert r.basis == "flat-ratio"
    assert r.assessed_value is None
    # POINT = 80% × PP × millage (FL_REASSESSMENT_FACTOR)
    expected_point = FL_PP * D("0.80") * FL_MILLAGE
    assert _rel(r.point, expected_point) < 1e-9
    assert r.low <= r.point <= r.high


# ---------------------------------------------------------------------------
# Non-regression: existing PropertyTaxCalculator flat-ratio path
# ---------------------------------------------------------------------------

def test_property_tax_calculator_flat_ratio_unchanged():
    """PropertyTaxCalculator.project() still works; non-regression for existing tests."""
    calc = ax.PropertyTaxCalculator()
    taxes = calc.project(
        purchase_price=D("36000000"),
        millage=D("0.019"),
        state="FL",
        years=10,
        growth=D("0.02"),
    )
    assert len(taxes) == 10
    # Year-1: 36M × 0.725 × 0.019 = 495,630
    expected_y1 = D("36000000") * D("0.725") * D("0.019")
    assert _rel(taxes[0], expected_y1) < 1e-9, (
        f"PropertyTaxCalculator Y1 {float(taxes[0]):,.0f} != expected {float(expected_y1):,.0f}"
    )
    # Monotonically increasing (2% growth)
    for i in range(1, len(taxes)):
        assert taxes[i] >= taxes[i - 1], "expected year-over-year tax growth"


def test_property_tax_calculator_tx():
    calc = ax.PropertyTaxCalculator()
    taxes = calc.project(
        purchase_price=D("75000000"),
        millage=D("0.0245"),
        state="TX",
        years=5,
    )
    expected_y1 = D("75000000") * D("0.65") * D("0.0245")
    assert _rel(taxes[0], expected_y1) < 1e-9


# ---------------------------------------------------------------------------
# Range bounds invariant: low <= point <= high for all states
# ---------------------------------------------------------------------------

import pytest

@pytest.mark.parametrize("state,pp,millage,av", [
    ("FL", D("36000000"),  D("0.019"),  D("28800000")),
    ("TX", D("75000000"),  D("0.0245"), D("48750000")),
    ("GA", D("86750000"),  D("0.045"),  D("34700000")),
    ("NC", D("50000000"),  D("0.012"),  None),          # unknown state -> fallback
    ("CA", D("100000000"), D("0.0115"), D("100000000")),
])
def test_range_invariant_low_le_point_le_high(state, pp, millage, av):
    est = ax.PropertyTaxRangeEstimator()
    r = est.estimate(
        purchase_price=pp,
        state=state,
        millage=millage,
        assessed_value=av,
        citation="parametrized invariant test",
    )
    assert r.low <= r.point, f"{state}: low {float(r.low):,.0f} > point {float(r.point):,.0f}"
    assert r.point <= r.high, f"{state}: point {float(r.point):,.0f} > high {float(r.high):,.0f}"
