"""Wave B.5/B.6 tests — routed /api/underwrite/v2 (ACQ+EFB) + the sensitivity sweep, exercised
through the recalc router in isolation (no main.py import, so no pandas needed). LLM-free."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("starlette")
from fastapi import FastAPI  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402
from routers.recalc import router  # noqa: E402

ESPLANADE = dict(
    bridge_loan=23800000.0, bridge_rate=0.08, bridge_io_years=2,
    refi_loan=31944864.0, refi_rate=0.06, refi_io_years=3,
    refi_amort_years=30, refi_year=2, total_equity=13145673.0,
    noi_series=[2387932, 2563041, 2742167, 2883487, 2983197,
                3134540, 3241781, 3352240, 3466013, 3583198],
    exit_cap=0.06, sale_year=7, costs_of_sale=0.02,
    servicing_spread=0.0116, refi_cost_pct=0.02, exit_on_forward_noi=True,
)
RAYZOR_NOI = 4448271.31


def _client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b))


# ---- B.5 routed underwrite ----

def test_underwrite_v2_acq():
    c = _client()
    r = c.post("/api/underwrite/v2?routing=ACQ", json=ESPLANADE)
    assert r.status_code == 200
    body = r.json()
    assert body["routing"] == "ACQ"
    assert rel(body["headline_metrics"]["irr"], 0.2251) <= 0.02


def test_underwrite_v2_efb():
    c = _client()
    r = c.post("/api/underwrite/v2?routing=EFB",
               json={"stabilized_noi": RAYZOR_NOI, "target_dscr": 1.15, "bond_rate": 0.05})
    assert r.status_code == 200
    body = r.json()
    assert body["routing"] == "EFB"
    assert rel(body["headline_metrics"]["year1_dscr"], 1.15) <= 0.02
    assert "irr" not in body["headline_metrics"]


def test_underwrite_v2_unknown_routing_400():
    c = _client()
    r = c.post("/api/underwrite/v2?routing=XYZ", json={})
    assert r.status_code == 400


def test_underwrite_efb_typed_endpoint():
    c = _client()
    r = c.post("/api/underwrite/efb", json={"stabilized_noi": RAYZOR_NOI})
    assert r.status_code == 200
    assert r.json()["headline_metrics"]["bond_amount"] > 0


# ---- B.6 sensitivity sweep ----

def test_sensitivity_exit_cap_sweep():
    c = _client()
    r = c.post("/api/recalc/sensitivity", json={
        "base": ESPLANADE, "field": "exit_cap", "values": [0.055, 0.06, 0.065], "metric": "irr",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["field"] == "exit_cap" and body["metric"] == "irr"
    assert len(body["grid"]) == 3
    irrs = [row["result"] for row in body["grid"]]
    # Lower exit cap (higher sale value) -> higher IRR; sweep must be monotonically decreasing.
    assert irrs[0] > irrs[1] > irrs[2]


def test_sensitivity_rejects_unknown_field():
    c = _client()
    r = c.post("/api/recalc/sensitivity", json={
        "base": ESPLANADE, "field": "purchase_price", "values": [1, 2], "metric": "irr",
    })
    assert r.status_code == 400


def test_sensitivity_rejects_unknown_metric():
    c = _client()
    r = c.post("/api/recalc/sensitivity", json={
        "base": ESPLANADE, "field": "exit_cap", "values": [0.06], "metric": "made_up",
    })
    assert r.status_code == 400


def test_sensitivity_equity_multiple_metric():
    c = _client()
    r = c.post("/api/recalc/sensitivity", json={
        "base": ESPLANADE, "field": "refi_rate", "values": [0.055, 0.06, 0.065],
        "metric": "equity_multiple",
    })
    assert r.status_code == 200
    assert all(row["result"] is not None for row in r.json()["grid"])
