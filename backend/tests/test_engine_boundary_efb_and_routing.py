"""Wave B.1/B.4 tests — the EFB boundary path + the ACQ/EFB routing layer.

EFB sizing is validated against the same invariant as the engine's Rayzor test: size bonds to the
target DSCR on stabilized NOI and the IMPLIED DSCR (NOI / annual debt service) comes back at target
(within 2%). The routing layer dispatches a plain JSON-style dict to the correct engine path.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine_boundary import (  # noqa: E402
    EFBDealInputs, run_efb_underwrite,
    ACQDealInputs, run_acq_underwrite,
    run_underwrite, UnknownRoutingError,
)

# Rayzor EFB ground truth (from underwriting-engine/engine/tests/test_efb_rayzor.py)
RAYZOR_NOI = 4448271.31
RAYZOR_BOND_RATE = 0.05
TARGET_DSCR = 1.15
LINE_TOL = 0.02

# Esplanade ACQ (for the routing dispatch check)
ESPLANADE = dict(
    bridge_loan=23800000.0, bridge_rate=0.08, bridge_io_years=2,
    refi_loan=31944864.0, refi_rate=0.06, refi_io_years=3,
    refi_amort_years=30, refi_year=2, total_equity=13145673.0,
    noi_series=[2387932, 2563041, 2742167, 2883487, 2983197,
                3134540, 3241781, 3352240, 3466013, 3583198],
    exit_cap=0.06, sale_year=7, costs_of_sale=0.02,
    servicing_spread=0.0116, refi_cost_pct=0.02, exit_on_forward_noi=True,
)


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b))


# ---- EFB path ----

def test_efb_sizes_bonds_to_target_dscr():
    hm = run_efb_underwrite(EFBDealInputs(
        stabilized_noi=RAYZOR_NOI, target_dscr=TARGET_DSCR,
        bond_rate=RAYZOR_BOND_RATE, amortization_years=35,
    ))
    # The implied DSCR (NOI / annual DS) must come back at the target within 2%.
    assert rel(hm["year1_dscr"], TARGET_DSCR) <= LINE_TOL, \
        f"implied DSCR {hm['year1_dscr']:.3f} vs target {TARGET_DSCR}"
    assert hm["bond_amount"] > 0
    assert hm["year1_noi"] == pytest.approx(RAYZOR_NOI)


def test_efb_tax_savings_10yr_color():
    hm = run_efb_underwrite(EFBDealInputs(
        stabilized_noi=RAYZOR_NOI, annual_property_tax_exempted=900000, hold_years=10,
    ))
    assert hm["tax_savings_10yr"] == 9000000  # 900k * 10yr


def test_efb_outputs_are_float_not_decimal():
    from decimal import Decimal
    hm = run_efb_underwrite(EFBDealInputs(stabilized_noi=RAYZOR_NOI))
    for v in hm.values():
        assert not isinstance(v, Decimal)


# ---- routing layer ----

def test_routing_acq_dispatches_to_acq_engine():
    hm = run_underwrite("ACQ", dict(ESPLANADE))
    # ACQ headline shape: has irr + equity_multiple + exit_value
    assert "irr" in hm and "equity_multiple" in hm and "exit_value" in hm
    assert rel(hm["irr"], 0.2251) <= 0.02


def test_routing_efb_dispatches_to_bond_sizing():
    hm = run_underwrite("EFB", {
        "stabilized_noi": RAYZOR_NOI, "target_dscr": TARGET_DSCR,
        "bond_rate": RAYZOR_BOND_RATE, "amortization_years": 35,
    })
    # EFB headline shape: has bond_amount + year1_dscr, NOT irr
    assert "bond_amount" in hm and "year1_dscr" in hm
    assert "irr" not in hm
    assert rel(hm["year1_dscr"], TARGET_DSCR) <= LINE_TOL


def test_routing_is_case_insensitive():
    assert "bond_amount" in run_underwrite("efb", {"stabilized_noi": RAYZOR_NOI})
    assert "irr" in run_underwrite("acq", dict(ESPLANADE))


def test_routing_ignores_extra_keys():
    """The same JSON body can carry extra UI fields; the router drops unknown keys."""
    body = dict(ESPLANADE)
    body["ui_note"] = "user typed this"
    body["property_name"] = "Esplanade"
    hm = run_underwrite("ACQ", body)
    assert "irr" in hm


def test_routing_unknown_raises():
    with pytest.raises(UnknownRoutingError):
        run_underwrite("XYZ", {})
