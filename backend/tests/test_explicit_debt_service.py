"""The accepted annual-payment input reaches deterministic cash flow and DSCR.

These assertions use payment/NOI arithmetic, not an adjusted financial oracle.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine_boundary import ACQDealInputs, run_acq_underwrite, run_underwrite
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routers.recalc import router


def inputs(**overrides):
    values = dict(
        bridge_loan=1000000, bridge_rate=0.08, bridge_io_years=2,
        refi_loan=1200000, refi_rate=0.06, refi_io_years=3,
        refi_amort_years=30, refi_year=2, total_equity=600000,
        noi_series=[150000, 160000, 170000, 180000, 190000],
        exit_cap=0.06, sale_year=4, years=5, servicing_spread=0,
    )
    values.update(overrides)
    return values


def test_explicit_payment_changes_cashflow_and_dscr_without_changing_exit():
    base = run_acq_underwrite(ACQDealInputs(**inputs()))
    override = run_underwrite("ACQ", inputs(debt_service=[100000] * 5))
    # First year has no refi or sale: NOI minus the stated annual payment.
    assert override["cash_flows"][1] == 50000
    assert override["dscr_series"][0] == 1.5
    assert base["cash_flows"][1] == 70000
    assert override["cash_flows"][1] != base["cash_flows"][1]
    assert override["irr"] != base["irr"]
    assert override["exit_value"] == base["exit_value"]
    assert override["net_sale_proceeds"] == base["net_sale_proceeds"]
    # Payment override preserves sale/refi timing and principal metadata.
    assert override["cash_flows"][2] - base["cash_flows"][2] == -20000


def test_complete_derived_payment_override_matches_default():
    # Derived IO stream: two bridge years at80k, then three refi years at72k.
    base = run_acq_underwrite(ACQDealInputs(**inputs()))
    explicit = run_acq_underwrite(ACQDealInputs(**inputs(debt_service=[80000, 80000, 72000, 72000, 72000])))
    assert explicit == base


def test_explicit_payment_ignores_derived_servicing_spread():
    supplied = inputs(debt_service=[100000] * 5)
    assert run_underwrite("ACQ", supplied) == run_underwrite("ACQ", dict(supplied, servicing_spread=0.02))


@pytest.mark.parametrize("schedule", [[], [100000] * 4, [100000] * 6,
    [-1] * 5, [float('nan')] * 5, [float('inf')] * 5, [float('-inf')] * 5])
def test_invalid_schedule_fails_closed(schedule):
    with pytest.raises(ValueError, match="debt_service"):
        run_acq_underwrite(ACQDealInputs(**inputs(debt_service=schedule)))


def test_recalc_http_consumes_override_and_refuses_partial_schedule():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    response = client.post("/api/recalc", json=inputs(debt_service=[100000] * 5))
    assert response.status_code == 200
    assert response.json()["headline_metrics"]["cash_flows"][1] == 50000
    invalid = client.post("/api/recalc", json=inputs(debt_service=[100000] * 4))
    assert invalid.status_code == 422
    assert "debt_service" in invalid.json()["detail"]


@pytest.mark.parametrize("schedule", ["12345", {str(i): 999999 for i in range(1, 6)}, 100000])
def test_raw_routed_http_refuses_non_list_schedule(schedule):
    # /underwrite/v2 takes a raw dict, so its boundary also enforces the shape.
    app = FastAPI()
    app.include_router(router)
    response = TestClient(app).post("/api/underwrite/v2?routing=ACQ", json=inputs(debt_service=schedule))
    assert response.status_code == 422
    assert "debt_service" in response.json()["detail"]
