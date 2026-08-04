"""Wave C-v1 — jobs API acceptance tests. Mounts ONLY routers/jobs.py on a bare FastAPI app (no
main.py, no live LLM — StubAnalysts). Covers submit->CP-1, GET at CP-1 (spec+headline+gates),
submit-with-missing-inputs->AWAITING_INPUT, answer->resume->CP-1, cancel, and idempotent resubmit."""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.jobs as jobs_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402

READY = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}


@pytest.fixture
def client(monkeypatch):
    """A fresh in-memory deal + job store wired into the router's singletons; StubAnalysts."""
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    app = FastAPI()
    app.include_router(jobs_router.router)
    return TestClient(app)


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


def test_submit_runs_to_cp1(client):
    r = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "awaiting_cp1"
    assert body["phase"] == "cp1"
    # CP-1 view carries the spec + headline + gate summary
    assert rel(body["headline_metrics"]["irr"], 0.2221) <= 0.02
    assert "fee_bounds" in body["gate_summary"]
    assert "unit_count" in body["gate_summary"]
    # the llm-inferred cell is an open question
    assert any(q["field"] == "B31" for q in body["open_questions"])


def test_get_job_returns_status(client):
    r = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    jid = r.json()["job_id"]
    g = client.get(f"/api/jobs/{jid}")
    assert g.status_code == 200
    assert g.json()["status"] == "awaiting_cp1"
    assert "spec" in g.json()


def test_get_missing_job_404(client):
    assert client.get("/api/jobs/nope").status_code == 404


def test_submit_missing_inputs_awaits_input(client):
    r = client.post("/api/jobs", json={"intake_summary": {"routing": "ACQ"}, "owner": "evan"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "awaiting_input"
    assert len(body["blocking_questions"]) == 3  # all three BL-17 inputs missing


def test_answer_resumes_to_cp1(client):
    r = client.post("/api/jobs", json={"intake_summary": {"routing": "ACQ"}, "owner": "evan"})
    body = r.json()
    jid = body["job_id"]
    assert body["status"] == "awaiting_input"
    # Answer each blocking critical-input question
    answers = {
        "meta.critical_inputs.purchase_price": 55000000,
        "meta.critical_inputs.hold_years": 7,
        "meta.critical_inputs.exit_cap": 0.06,
    }
    last = None
    for q in body["blocking_questions"]:
        last = client.post(f"/api/jobs/{jid}/answer",
                           json={"question_id": q["id"], "answer": answers[q["field"]]})
        assert last.status_code == 200
    # After the final answer, the run resumed to CP-1
    final = last.json()
    assert final["status"] == "awaiting_cp1"
    assert rel(final["headline_metrics"]["irr"], 0.2221) <= 0.02


def test_cancel_sets_flag(client):
    # cancel a job that already ran is a no-op (terminal-ish); test the flag path on a fresh job
    r = client.post("/api/jobs", json={"intake_summary": {"routing": "ACQ"}, "owner": "evan"})
    jid = r.json()["job_id"]  # AWAITING_INPUT (active)
    c = client.post(f"/api/jobs/{jid}/cancel")
    assert c.status_code == 200
    assert c.json()["cancel_requested"] is True


def test_idempotent_resubmit_returns_same_job(client):
    r1 = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan",
                                        "idempotency_key": "abc"})
    r2 = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan",
                                        "idempotency_key": "abc"})
    assert r1.json()["job_id"] == r2.json()["job_id"]
