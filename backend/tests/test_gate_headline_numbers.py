"""Layer 1 gate tests: the backend must never show a deal number or file after a failed gate,
a hold, a stale result or a mismatched deal.

Source of truth: docs/research/2026-11-04-app-fail-closed-test-gap-map.md (draft PR 11). Each test
asserts the fail-closed behavior the gap map says is correct. Where the current code does NOT fail
closed the test is xfail(strict=True) with a "gap <ID>" reason, so CI stays green and the gap is
pinned: when product code is fixed the xfail turns into an XPASS failure and must be removed.

Synthetic fixtures only. No network, no secrets, no product code changed.
Rows: B33 B40b B42 B46 B47 B52 B55 B57 B64 B68 B70 B89.
"""
import copy
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.deals as deals_router  # noqa: E402
import routers.export_excel as export_router  # noqa: E402
import routers.jobs as jobs_router  # noqa: E402
import routers.memo as memo_router  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402
from jobs.contracts import JobStatus  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.runner import run_job  # noqa: E402
from store import SQLiteDealStore  # noqa: E402

TS = "2026-11-04T00:00:00Z"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
HM = {"irr": 0.2221, "equity_multiple": 2.733, "coc_year1": 0.081}


def _spec(headline=None, identity=None, qa=None):
    meta = {"deal_name": "Gate Test", "slug": "gate-test", "routing": "ACQ", "mode": "HITL"}
    if identity is not None:
        meta["deal_identity"] = identity
    spec = {"meta": meta, "qa": qa or {}, "cells": []}
    if headline is not None:
        spec["headline_metrics"] = dict(headline)
    return spec


# ---------------------------------------------------------------------------
# B64 / B68: gate_failed deal must not expose or narrate headline numbers
# ---------------------------------------------------------------------------

class _FakeMemo:
    def __init__(self, body="Body prose."):
        self.body = body
        self.calls = []

    def generate(self, inputs, model_results):
        self.calls.append((inputs, model_results))
        return self.body


@pytest.fixture
def api(monkeypatch):
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    fake = _FakeMemo()
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(deals_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    monkeypatch.setattr(memo_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(memo_router, "get_memo_generator", lambda: fake)
    monkeypatch.setattr(export_router, "get_deal_store", lambda: ds)
    app = FastAPI()
    for r in (deals_router.router, jobs_router.router, memo_router.router, export_router.router):
        app.include_router(r)
    return ds, js, fake, TestClient(app)


@pytest.mark.xfail(strict=True, reason="gap B64: deals list/detail return headline_metrics for a gate_failed deal")
def test_b64_gate_failed_deal_hides_headline_metrics_in_list_and_detail(api):
    ds, _js, _fake, c = api
    rec = ds.create(_spec(HM, qa={"fee_bounds": {"ok": False}}), owner="evan", now_iso=TS,
                    status="gate_failed")
    listed = [d for d in c.get("/api/deals").json() if d["deal_id"] == rec.deal_id][0]
    assert listed["status"] == "gate_failed"
    assert listed["headline_metrics"] == {}
    detail = c.get(f"/api/deals/{rec.deal_id}").json()
    assert detail["headline_metrics"] == {}


def test_b64_computed_deal_still_shows_headline_metrics(api):
    """Control for B64: the fix must not blank a clean computed deal."""
    ds, _js, _fake, c = api
    rec = ds.create(_spec(HM), owner="evan", now_iso=TS, status="computed")
    detail = c.get(f"/api/deals/{rec.deal_id}").json()
    assert detail["headline_metrics"]["irr"] == HM["irr"]


@pytest.mark.xfail(strict=True, reason="gap B68: memo is generated for a gate_failed deal that has stored headline_metrics")
def test_b68_memo_refused_for_gate_failed_deal(api):
    ds, _js, fake, c = api
    rec = ds.create(_spec(HM), owner="evan", now_iso=TS, status="gate_failed")
    r = c.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 409
    assert fake.calls == []  # the generator was never handed the RED deal's numbers


# ---------------------------------------------------------------------------
# B70: memo prose carrying a number the engine never produced
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="gap B70: memo text is not checked against headline_metrics, an invented IRR is stored and returned")
def test_b70_memo_with_number_not_in_headline_is_flagged(api):
    ds, _js, fake, c = api
    fake.body = "The deal returns a 47.3% IRR and a 9.9x multiple."  # neither is in HM
    rec = ds.create(_spec(HM), owner="evan", now_iso=TS, status="computed")
    r = c.post(f"/api/deals/{rec.deal_id}/memo")
    flagged = r.status_code != 200 or bool(
        r.json().get("warnings") or r.json().get("unverified_numbers"))
    assert flagged, "invented numbers in memo prose went through unflagged"
    if r.status_code != 200:  # refused: nothing may be stored
        stored = ds.get(rec.deal_id).spec
        assert "memo" not in (stored.get("narrative") or {})


# ---------------------------------------------------------------------------
# B33: /api/agent/memo trusts client-sent model_results
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="gap B33: /api/agent/memo writes a memo from client-sent model_results with no tie to a stored engine result")
def test_b33_agent_memo_rejects_client_supplied_model_results(monkeypatch):
    import main

    class Gen:
        calls = []

        def generate(self, inputs, model_results):
            Gen.calls.append(model_results)
            return "memo"

        def generate_executive_summary(self, inputs, model_results):
            return "summary"

    monkeypatch.setattr(main, "get_memo_generator", lambda: Gen())
    c = TestClient(main.app)
    fabricated = {"irr": 0.99, "equity_multiple": 9.9}  # not from any engine run
    r = c.post("/api/agent/memo", json={"inputs": {}, "model_results": fabricated})
    assert r.status_code in (400, 401, 403, 404, 409, 422)
    assert Gen.calls == []


# ---------------------------------------------------------------------------
# B42 / B46 / B47: export and reconcile identity gate
# ---------------------------------------------------------------------------

def _xlsx_bytes():
    import test_export_excel as ex  # reuse the synthetic Mini Model builder
    return ex._mini_model_bytes()


def _mismatch_spec(headline=HM):
    spec = _spec(headline, identity={"match": False, "reasons": ["fork carryover"]})
    spec["cells"] = [{"cell": "B10", "value": 34000000, "type": "currency", "source": "OM", "phase": 3}]
    return spec


def test_b46_export_download_true_with_identity_mismatch_returns_json_not_file(api):
    ds, _js, _fake, c = api
    rec = ds.create(_mismatch_spec(), owner="evan", now_iso=TS, status="computed")
    r = c.post(f"/api/deals/{rec.deal_id}/export",
               files={"template": ("mini.xlsx", _xlsx_bytes(), XLSX)}, data={"download": "true"})
    assert r.status_code == 200
    assert "json" in r.headers["content-type"]
    assert XLSX not in r.headers["content-type"]
    assert not r.content.startswith(b"PK")  # an xlsx is a zip, a refusal report is not
    body = r.json()
    assert body["identity_blocked"] is True
    assert body["ok"] is False


def test_b47_reconcile_deal_with_no_headline_is_409(api):
    ds, _js, _fake, c = api
    rec = ds.create(_spec(headline=None), owner="evan", now_iso=TS, status="draft")
    r = c.post(f"/api/deals/{rec.deal_id}/reconcile",
               files={"draft": ("d.xlsx", _xlsx_bytes(), XLSX)},
               data={"require_identity_match": "true"})
    assert r.status_code == 409


def test_b47_reconcile_deal_with_empty_headline_is_409(api):
    ds, _js, _fake, c = api
    rec = ds.create(_spec(headline={}), owner="evan", now_iso=TS, status="draft")
    r = c.post(f"/api/deals/{rec.deal_id}/reconcile",
               files={"draft": ("d.xlsx", _xlsx_bytes(), XLSX)},
               data={"require_identity_match": "true"})
    assert r.status_code == 409


@pytest.mark.xfail(strict=True, reason="gap B42: client form field require_identity_match=false skips the wrong-deal check")
def test_b42_client_cannot_disable_identity_check_on_reconcile(api):
    ds, _js, _fake, c = api
    rec = ds.create(_mismatch_spec(), owner="evan", now_iso=TS, status="computed")
    r = c.post(f"/api/deals/{rec.deal_id}/reconcile",
               files={"draft": ("d.xlsx", _xlsx_bytes(), XLSX)},
               data={"require_identity_match": "false"})
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# B55 / B57 / B52: runner gates
# ---------------------------------------------------------------------------

def _seed_job(ds, js):
    deal = ds.create(_spec(), owner="evan", now_iso=TS, status="draft")
    job = js.create_job(deal_id=deal.deal_id, routing="ACQ", owner="evan", now_iso=TS)
    return deal, job


@pytest.mark.xfail(strict=True, reason="gap B55: Wave 0 accepts exit_cap 0 as present, the run is not stopped to ask again")
def test_b55_zero_exit_cap_is_treated_as_missing():
    ds, js = SQLiteDealStore(":memory:"), SQLiteJobStore(":memory:")
    _deal, job = _seed_job(ds, js)
    summary = {"routing": "ACQ", "deal_name": "Gate Test",
               "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0}}
    try:
        final = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                        intake_summary=summary, job_store=js, deal_store=ds)
    finally:
        # whatever happened, a zero exit cap must never leave a computed deal behind
        assert ds.get(job.deal_id).status != "computed"
    assert final.status == JobStatus.AWAITING_INPUT


@pytest.mark.xfail(strict=True, reason="gap B55: Wave 0 accepts a negative purchase_price as present")
def test_b55_negative_purchase_price_is_treated_as_missing():
    ds, js = SQLiteDealStore(":memory:"), SQLiteJobStore(":memory:")
    _deal, job = _seed_job(ds, js)
    summary = {"routing": "ACQ", "deal_name": "Gate Test",
               "critical_inputs": {"purchase_price": -1, "hold_years": 7, "exit_cap": 0.06}}
    final = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary=summary, job_store=js, deal_store=ds)
    assert final.status == JobStatus.AWAITING_INPUT


class _RaisingAnalysts(StubAnalysts):
    def run_all(self, *a, **k):
        raise RuntimeError("synthetic analyst failure")


READY = {"routing": "ACQ", "deal_name": "Gate Test",
         "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06}}


def test_b57_analyst_exception_fails_job_and_leaves_no_computed_deal():
    ds, js = SQLiteDealStore(":memory:"), SQLiteJobStore(":memory:")
    deal, job = _seed_job(ds, js)
    with pytest.raises(RuntimeError):
        run_job(job.job_id, analysts=_RaisingAnalysts(), now_iso=TS,
                intake_summary=READY, job_store=js, deal_store=ds)
    failed = js.get_job(job.job_id)
    assert failed.status == JobStatus.FAILED
    assert "synthetic analyst failure" in (failed.error or "")
    after = ds.get(deal.deal_id)
    assert after.status != "computed"
    assert not (after.spec.get("headline_metrics"))


def test_b52_sync_runner_error_is_422_and_job_failed(api, monkeypatch):
    ds, js, _fake, c = api
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: _RaisingAnalysts())
    r = c.post("/api/jobs", json={"routing": "ACQ", "deal_name": "Gate Test",
                                  "intake_summary": READY})
    assert r.status_code == 422
    jobs = js.list_jobs()
    assert jobs and all(j.status == JobStatus.FAILED for j in jobs)
    assert all(d.status != "computed" for d in ds.list())


# ---------------------------------------------------------------------------
# B89: run status view must not present values for failed / in-progress runs
# ---------------------------------------------------------------------------

def _headline_item(value="10000000"):
    return {"name": "Purchase price", "value": value, "unit": "usd", "blank_reason": None,
            "source_file": "fixture-model.json", "source_pointer": "/outputs/purchase_price"}


@pytest.mark.xfail(strict=True, reason="gap B89: view.py marks values diagnostic only for blocked and stale, failed and in_progress runs pass headline values through")
@pytest.mark.parametrize("fixture_id", ["run-failed", "run-in-progress"])
def test_b89_failed_or_in_progress_run_does_not_present_headline_values(fixture_id):
    from run_status.loader import load_run
    from run_status.view import build_view

    run = copy.deepcopy(load_run(fixture_id))
    run["headline"] = [_headline_item()]
    view = build_view(run)
    shown = [h.get("value") for h in view["headline"]]
    assert view["values_are_diagnostic"] is True or all(v in (None, "") for v in shown)


# ---------------------------------------------------------------------------
# B40b: intake number extraction takes the first match
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="gap B40b: _first_dollar takes the first match, two conflicting Gross Potential Rent lines prefill the first one")
def test_b40b_conflicting_t12_lines_do_not_prefill_first_match():
    from intake.intake_service import _extract_t12_from_text

    text = (
        "Gross Potential Rent  $4,800,000\n"
        "Gross Potential Rent  $5,950,000\n"
    )
    out = _extract_t12_from_text(text)
    assert "gpr_annual" not in out or out["gpr_annual"] is None


def test_b40b_single_t12_line_still_extracts():
    """Control for B40b: a fix must keep the unambiguous case working."""
    from intake.intake_service import _extract_t12_from_text

    out = _extract_t12_from_text("Gross Potential Rent  $4,800,000\n")
    assert out["gpr_annual"] == 4800000.0
