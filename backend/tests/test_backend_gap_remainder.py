"""Remaining backend fail-closed gap rows (gap map B41, B49, B51, B71, B76, B77, B93).

Source: docs/research/2026-11-04-app-fail-closed-test-gap-map.md. The other rows in the CRM, jobs,
runner and run-status groups are already tested by the open api, gate and input test files, or are
marked HOLD (B94). Synthetic data only: in-memory stores, a fake Kimi client, no network, no
product code change. Each strict xfail names the gap and turns red when the gap is fixed.
"""
import asyncio
import io
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl  # noqa: E402

import routers.crm as crm_router  # noqa: E402
import routers.deals as deals_router  # noqa: E402
import routers.export_excel as export_router  # noqa: E402
import routers.jobs as jobs_router  # noqa: E402
import routers.memo as memo_router  # noqa: E402
from intake.intake_service import IntakeService  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from run_status.view import build_view  # noqa: E402
from store import SQLiteCRMStore, SQLiteDealStore  # noqa: E402

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
NOW = "2026-07-01T00:00:00+00:00"


@pytest.fixture(autouse=True)
def synthetic_env(monkeypatch):
    """Auth off and no host secrets, so the host environment cannot change a result."""
    for name in ("AUTH_JWT_SECRET", "GOOGLE_CLIENT_ID", "ALLOWED_EMAILS", "DREAM_STRICT_OWNERSHIP"):
        monkeypatch.delenv(name, raising=False)


def _spec(name="Esplanade", slug="esplanade", routing="ACQ", headline=None):
    spec = {"meta": {"deal_name": name, "slug": slug, "routing": routing, "mode": "HITL",
                     "deal_identity": {"match": True, "reasons": []}}, "qa": {}, "cells": []}
    if headline is not None:
        spec["headline_metrics"] = headline
    return spec


@pytest.fixture
def stores(monkeypatch):
    crm, ds, js = SQLiteCRMStore(":memory:"), SQLiteDealStore(":memory:"), SQLiteJobStore(":memory:")
    for mod in (crm_router, deals_router):
        monkeypatch.setattr(mod, "get_crm_store", lambda: crm, raising=False)
    for mod in (crm_router, deals_router, jobs_router, memo_router, export_router):
        monkeypatch.setattr(mod, "get_deal_store", lambda: ds)
    for mod in (crm_router, deals_router, jobs_router):
        monkeypatch.setattr(mod, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    return crm, ds, js


@pytest.fixture
def client(stores):
    app = FastAPI()
    for r in (crm_router.router, deals_router.router, jobs_router.router,
              memo_router.router, export_router.router):
        app.include_router(r)
    return TestClient(app)


# ---------------------------------------------------------------------------
# B51 jobs: unknown job or question on answer and cancel
# ---------------------------------------------------------------------------

def _awaiting_input_job(client):
    r = client.post("/api/jobs", json={"intake_summary": {"routing": "ACQ"}, "owner": "evan"})
    assert r.status_code == 200 and r.json()["status"] == "awaiting_input"
    return r.json()


def test_b51_answer_unknown_job_404(client):
    r = client.post("/api/jobs/nope/answer", json={"question_id": "q1", "answer": 1})
    assert r.status_code == 404


def test_b51_answer_unknown_question_404_and_job_unchanged(client):
    body = _awaiting_input_job(client)
    r = client.post(f"/api/jobs/{body['job_id']}/answer",
                    json={"question_id": "no-such-question", "answer": 5})
    assert r.status_code == 404
    after = client.get(f"/api/jobs/{body['job_id']}").json()
    assert after["status"] == "awaiting_input"
    assert len(after["blocking_questions"]) == len(body["blocking_questions"])


def test_b51_cancel_unknown_job_404(client):
    assert client.post("/api/jobs/nope/cancel").status_code == 404


# ---------------------------------------------------------------------------
# B71 memo: version conflict on save
# ---------------------------------------------------------------------------

def test_b71_memo_save_with_stale_version_is_409_and_stores_nothing(client, stores, monkeypatch):
    _crm, ds, _js = stores
    rec = ds.create(_spec(headline={"irr": 0.2221, "equity_multiple": 2.7}), owner="evan",
                    now_iso=NOW, status="computed")

    class RacingGenerator:
        """A second writer moves the deal version while the memo is being written."""
        def generate(self, inputs, model_results):
            cur = ds.get(rec.deal_id)
            ds.put(rec.deal_id, cur.spec, expected_version=cur.version, now_iso=NOW)
            return "## Memo body"

    monkeypatch.setattr(memo_router, "get_memo_generator", lambda: RacingGenerator())
    r = client.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 409
    assert "narrative" not in ds.get(rec.deal_id).spec


# ---------------------------------------------------------------------------
# B76 and B77 CRM items: version required, stale version refused
# ---------------------------------------------------------------------------

def _task(client, title="Call broker"):
    r = client.post("/api/items", json={"kind": "task", "title": title, "status": "open"})
    assert r.status_code == 200, r.text
    return r.json()


def _item_doc(item):
    return {"kind": "task", "title": item["title"], "status": "open"}


def test_b76_item_update_without_version_is_400(client):
    item = _task(client)
    r = client.put(f"/api/items/{item['item_id']}", json={**_item_doc(item), "title": "Changed"})
    assert r.status_code == 400
    assert client.get(f"/api/items/{item['item_id']}").json()["title"] == "Call broker"


@pytest.mark.parametrize("bad", ["1", 1.5, None])
def test_b76_item_update_with_non_integer_version_is_400(client, bad):
    item = _task(client)
    r = client.put(f"/api/items/{item['item_id']}",
                   json={**_item_doc(item), "title": "Changed", "version": bad})
    assert r.status_code == 400


@pytest.mark.xfail(strict=True, reason="gap B76: JSON true counts as integer version 1 "
                   "because bool is an int in Python, so the version check is bypassed")
def test_b76_item_update_with_boolean_version_is_400(client):
    item = _task(client)
    r = client.put(f"/api/items/{item['item_id']}",
                   json={**_item_doc(item), "title": "Changed", "version": True})
    assert r.status_code == 400


def test_b76_item_update_unknown_id_404(client):
    r = client.put("/api/items/nope", json={"kind": "task", "title": "x", "status": "open",
                                            "version": 1})
    assert r.status_code == 404


def test_b77_item_update_with_stale_version_is_409_and_keeps_newer_data(client):
    item = _task(client)
    iid = item["item_id"]
    ok = client.put(f"/api/items/{iid}", json={**_item_doc(item), "title": "First", "version": 1})
    assert ok.status_code == 200 and ok.json()["version"] == 2
    stale = client.put(f"/api/items/{iid}", json={**_item_doc(item), "title": "Lost", "version": 1})
    assert stale.status_code == 409
    got = client.get(f"/api/items/{iid}").json()
    assert got["title"] == "First" and got["version"] == 2


def test_b77_task_toggle_with_stale_version_is_409_and_status_unchanged(client):
    item = _task(client)
    iid = item["item_id"]
    client.put(f"/api/items/{iid}", json={**_item_doc(item), "title": "Moved", "version": 1})
    stale = client.post(f"/api/items/{iid}/toggle", json={"version": 1})
    assert stale.status_code == 409
    assert client.get(f"/api/items/{iid}").json()["status"] == "open"


def test_b77_toggle_without_version_flips_once(client):
    """Control: a blind toggle is allowed and flips exactly once."""
    item = _task(client)
    r = client.post(f"/api/items/{item['item_id']}/toggle")
    assert r.status_code == 200 and r.json()["status"] == "done"


def test_b77_toggle_note_is_400(client):
    r = client.post("/api/items", json={"kind": "note", "title": "n", "body": "text"})
    if r.status_code != 200:
        pytest.skip("note shape differs: " + r.text)
    assert client.post(f"/api/items/{r.json()['item_id']}/toggle").status_code == 400


# ---------------------------------------------------------------------------
# B49 reconcile: a non-numeric headline must not be silently dropped
# ---------------------------------------------------------------------------

def _mini_xlsx():
    wb = openpyxl.Workbook()
    pf = wb.active
    pf.title = "Pro Forma"
    pf["B2"] = "Esplanade"
    log = wb.create_sheet("Claude Log")
    log["A1"] = "Timestamp"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.xfail(strict=True, reason="gap B49: reconcile drops a non-numeric headline metric, "
                   "so no row, no flag and reconciled can read true")
def test_b49_non_numeric_headline_surfaces_as_a_flagged_row(client, stores):
    _crm, ds, _js = stores
    rec = ds.create(_spec(headline={"irr": "n/a", "equity_multiple": 2.72}), owner="evan",
                    now_iso=NOW, status="computed")
    r = client.post(f"/api/deals/{rec.deal_id}/reconcile",
                    files={"draft": ("d.xlsx", _mini_xlsx(), XLSX)},
                    data={"require_identity_match": "true"})
    assert r.status_code == 200, r.text
    body = r.json()
    rows = {row["metric"]: row for row in body["rows"]}
    assert "irr" in rows and rows["irr"]["flag"], "non-numeric irr must show as a flagged row"
    assert body["reconciled"] is False


def test_b49_control_numeric_headline_appears_as_row(client, stores):
    _crm, ds, _js = stores
    rec = ds.create(_spec(headline={"irr": 0.2251}), owner="evan", now_iso=NOW, status="computed")
    r = client.post(f"/api/deals/{rec.deal_id}/reconcile",
                    files={"draft": ("d.xlsx", _mini_xlsx(), XLSX)},
                    data={"require_identity_match": "true"})
    assert r.status_code == 200
    assert any(row["metric"] == "irr" for row in r.json()["rows"])
    assert r.json()["reconciled"] is False  # blank excel cell is not a pass


# ---------------------------------------------------------------------------
# B41 intake: Kimi classification failure
# ---------------------------------------------------------------------------

class _RaisingKimi:
    """Fake OpenAI-compatible client whose call always raises. No network."""
    def __init__(self):
        self.calls = 0
        outer = self

        class _Completions:
            async def create(self, **kwargs):
                outer.calls += 1
                raise RuntimeError("kimi down")

        class _Chat:
            completions = _Completions()

        self.chat = _Chat()


def _csv_bytes():
    return b"Line,Amount\nMisc,100\n"


def test_b41_kimi_failure_still_returns_a_result_from_the_filename_guess():
    kimi = _RaisingKimi()
    res = asyncio.run(IntakeService(kimi_client=kimi).process_file(_csv_bytes(), "mystery.csv"))
    assert kimi.calls == 1, "the fallback should have tried Kimi once"
    assert res.detection_method == "filename_heuristic"
    assert res.confidence < 0.7


@pytest.mark.xfail(strict=True, reason="gap B41: a Kimi failure is swallowed in _classify_with_kimi, "
                   "so warnings stay empty and the user is not told the guess is filename only")
def test_b41_kimi_failure_adds_a_warning():
    res = asyncio.run(IntakeService(kimi_client=_RaisingKimi()).process_file(_csv_bytes(), "mystery.csv"))
    assert res.warnings, "the caller must be told AI classification failed"


# ---------------------------------------------------------------------------
# B93 run status: odd headline shape must block, not 500
# ---------------------------------------------------------------------------

def _run(headline):
    return {"run_id": "r1", "status": "completed", "synthetic": True,
            "engine_commit": "a", "current_engine_commit": "a",
            "inputs_hash": "h", "current_inputs_hash": "h",
            "gates": [{"status": "green"}], "evidence": [{"state": "ok"}],
            "holds": [], "headline": headline}


def test_b93_control_well_formed_headline_builds():
    view = build_view(_run([{"label": "IRR", "value": None}]))
    assert view["missing_value_count"] == 1


@pytest.mark.parametrize("headline", [[None], ["IRR"], [3.5]])
@pytest.mark.xfail(strict=True, reason="gap B93: count_missing_values calls .get on every headline "
                   "item, so a non-dict item raises AttributeError (HTTP 500)")
def test_b93_non_dict_headline_item_is_blocked_not_an_exception(headline):
    view = build_view(_run(headline))
    assert view["display_state"] in ("blocked", "failed")
    assert view["display_state"] != "complete"
