"""
A1.3 acceptance test — the engine_boundary reproduces Esplanade ground truth at the API edge.

This is the critical test for the Decimal seam: it drives the engine through `ACQDealInputs`
(plain floats, as FastAPI would) and `run_acq_underwrite`, NOT by constructing Decimal engine
objects directly. If the boundary drops an orchestration param (servicing_spread,
exit_on_forward_noi, refi_cost_pct) or injects float noise via Decimal(float), these assertions
fail. Same ground truth + tolerances as underwriting-engine/engine/tests/test_acq_esplanade.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine_boundary import ACQDealInputs, run_acq_underwrite, to_dec  # noqa: E402

# ---- Esplanade ground truth (floats — the API-edge representation) ----------
TOTAL_EQUITY = 13145673.0
BRIDGE_LOAN = 23800000.0
BRIDGE_RATE = 0.08
BRIDGE_IO = 2
REFI_LOAN = 31944864.0
REFI_RATE = 0.06
REFI_IO = 3
REFI_AMORT = 30
REFI_YEAR = 2
EXIT_CAP = 0.06
SALE_YEAR = 7
COSTS_OF_SALE = 0.02
SERVICING_SPREAD = 0.0116

NOI_SERIES = [2387932, 2563041, 2742167, 2883487, 2983197,
              3134540, 3241781, 3352240, 3466013, 3583198]
EXPECT_DSCR = [1.226, 1.329, 1.414, 1.487, 1.538, 1.348, 1.394]
EXPECT_IRR = 0.2251
EXPECT_EM = 2.72
EXPECT_EXIT_VALUE = 55870669
EXPECT_COC_STAB = 0.0584

HEADLINE_TOL = 0.005   # 0.5%
LINE_TOL = 0.02        # 2%


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


def _hm():
    inp = ACQDealInputs(
        bridge_loan=BRIDGE_LOAN, bridge_rate=BRIDGE_RATE, bridge_io_years=BRIDGE_IO,
        refi_loan=REFI_LOAN, refi_rate=REFI_RATE, refi_io_years=REFI_IO,
        refi_amort_years=REFI_AMORT, refi_year=REFI_YEAR,
        total_equity=TOTAL_EQUITY, noi_series=[float(v) for v in NOI_SERIES],
        exit_cap=EXIT_CAP, sale_year=SALE_YEAR, costs_of_sale=COSTS_OF_SALE,
        servicing_spread=SERVICING_SPREAD, refi_cost_pct=0.02, exit_on_forward_noi=True,
    )
    return run_acq_underwrite(inp)


def test_boundary_exit_value():
    hm = _hm()
    assert rel(hm["exit_value"], EXPECT_EXIT_VALUE) <= HEADLINE_TOL, \
        f"exit value {hm['exit_value']:,.0f} vs {EXPECT_EXIT_VALUE:,.0f}"


def test_boundary_irr():
    hm = _hm()
    assert rel(hm["irr"], EXPECT_IRR) <= HEADLINE_TOL * 4, \
        f"IRR {hm['irr']:.4f} vs {EXPECT_IRR}"  # IRR sensitive; 2% rel


def test_boundary_equity_multiple():
    hm = _hm()
    assert rel(hm["equity_multiple"], EXPECT_EM) <= LINE_TOL, \
        f"EM {hm['equity_multiple']:.3f} vs {EXPECT_EM}"


def test_boundary_dscr_series():
    hm = _hm()
    got = hm["dscr_series"]
    assert len(got) == len(EXPECT_DSCR)
    for g, e in zip(got, EXPECT_DSCR):
        assert rel(g, e) <= LINE_TOL, f"DSCR {g:.3f} vs {e:.3f} (rel {rel(g, e):.3%})"


def test_boundary_outputs_are_float_not_decimal():
    """The boundary must NOT leak Decimal across the API edge."""
    from decimal import Decimal
    hm = _hm()
    for k, v in hm.items():
        if isinstance(v, list):
            assert all(not isinstance(x, Decimal) for x in v), f"{k} leaks Decimal"
        else:
            assert not isinstance(v, Decimal), f"{k} leaks Decimal"


def test_string_constructor_not_float_constructor():
    """to_dec must use Decimal(str(x)), provable: Decimal(0.1) != Decimal('0.1')."""
    from decimal import Decimal
    assert to_dec(0.1) == Decimal("0.1")
    assert to_dec(0.1) != Decimal(0.1)  # the buggy path we must avoid


def test_servicing_spread_matters():
    """Dropping the orchestration param visibly changes IRR — proves it's threaded, not ignored."""
    base = _hm()
    inp = ACQDealInputs(
        bridge_loan=BRIDGE_LOAN, bridge_rate=BRIDGE_RATE, bridge_io_years=BRIDGE_IO,
        refi_loan=REFI_LOAN, refi_rate=REFI_RATE, refi_io_years=REFI_IO,
        refi_amort_years=REFI_AMORT, refi_year=REFI_YEAR,
        total_equity=TOTAL_EQUITY, noi_series=[float(v) for v in NOI_SERIES],
        exit_cap=EXIT_CAP, sale_year=SALE_YEAR, costs_of_sale=COSTS_OF_SALE,
        servicing_spread=0.0, refi_cost_pct=0.02, exit_on_forward_noi=True,  # spread dropped
    )
    no_spread = run_acq_underwrite(inp)
    # With no servicing spread, debt service drops, CFBT rises, IRR moves — must differ.
    assert abs(no_spread["irr"] - base["irr"]) > 1e-4
