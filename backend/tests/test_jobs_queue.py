"""Phase 4a — async job queue tests (jobs/queue.py + the router's sync/async branch).

Mounts ONLY routers/jobs.py on a bare FastAPI app (the test_jobs_api.py idiom): in-memory
stores wired into the router's singletons, StubAnalysts, no main.py import, no live LLM.

Covers: async submit returns immediately + polls to CP-1, async answer/resume, the startup
stale-job sweep (running statuses fail; the human-paused pair is untouched), and the
DREAM_JOBS_SYNC=1 back-compat flag (v1 synchronous semantics locked)."""
import os
import sys
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.jobs as jobs_router  # noqa: E402
from jobs import queue  # noqa: E402
from jobs.contracts import JobStatus  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402
from store import SQLiteDealStore  # noqa: E402

READY = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}

NOW = "2026-07-12T00:00:00+00:00"


@pytest.fixture
def env(monkeypatch):
    """Fresh in-memory deal + job stores wired into the router's singletons; StubAnalysts.
    Teardown shuts the queue's executor down (wait=True) so worker threads never leak into,
    or keep writing during, the next test."""
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    app = FastAPI()
    app.include_router(jobs_router.router)
    client = TestClient(app)
    yield client, js, ds
    queue.shutdown(wait=True)


def _poll_until(client, job_id, want, deadline_s=10.0):
    """Poll GET /api/jobs/{id} until status == want (tight loop, hard deadline)."""
    end = time.monotonic() + deadline_s
    body = None
    while time.monotonic() < end:
        r = client.get(f"/api/jobs/{job_id}")
        assert r.status_code == 200, r.text
        body = r.json()
        if body["status"] == want:
            return body
        assert body["status"] not in ("failed", "cancelled"), body
        time.sleep(0.05)
    pytest.fail(f"timed out after {deadline_s}s waiting for '{want}'; last view: {body}")


def test_async_submit_returns_immediately(env, monkeypatch):
    client, _js, _ds = env
    monkeypatch.setenv("DREAM_JOBS_SYNC", "0")
    r = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    # Accepted, not finished: the run continues on the pool.
    assert body["status"] in ("submitted", "routing"), body
    final = _poll_until(client, body["job_id"], "awaiting_cp1")
    # The CP-1 view carries the spec + headline + gate summary, same as the sync path.
    assert final["spec"], "CP-1 view must carry the persisted spec"
    assert "irr" in final["headline_metrics"]
    assert "fee_bounds" in final["gate_summary"]


def test_async_answer_resume(env, monkeypatch):
    client, _js, _ds = env
    monkeypatch.setenv("DREAM_JOBS_SYNC", "0")
    r = client.post("/api/jobs", json={"intake_summary": {"routing": "ACQ"}, "owner": "evan"})
    assert r.status_code == 200, r.text
    jid = r.json()["job_id"]
    body = _poll_until(client, jid, "awaiting_input")
    assert len(body["blocking_questions"]) == 3  # all three BL-17 inputs missing

    answers = {
        "meta.critical_inputs.purchase_price": 55000000,
        "meta.critical_inputs.hold_years": 7,
        "meta.critical_inputs.exit_cap": 0.06,
    }
    last = None
    for q in body["blocking_questions"]:
        last = client.post(f"/api/jobs/{jid}/answer",
                           json={"question_id": q["id"], "answer": answers[q["field"]]})
        assert last.status_code == 200, last.text
    # The FINAL answer enqueues the resume and reports the job back at ROUTING (not CP-1).
    assert last.json()["status"] == "routing", last.json()
    final = _poll_until(client, jid, "awaiting_cp1")
    assert "irr" in final["headline_metrics"]


def test_sweep_stale_jobs(env):
    _client, js, _ds = env

    # A job stranded mid-run (walk legal transitions to ANALYZING).
    stale = js.create_job(deal_id="d-stale", routing="ACQ", owner="evan", now_iso=NOW)
    js.transition(stale.job_id, JobStatus.ROUTING, NOW)
    js.transition(stale.job_id, JobStatus.ANALYZING, NOW)

    # Human-paused jobs — durable waits the sweep must NEVER touch.
    paused_input = js.create_job(deal_id="d-input", routing="ACQ", owner="evan", now_iso=NOW)
    js.transition(paused_input.job_id, JobStatus.ROUTING, NOW)
    js.transition(paused_input.job_id, JobStatus.AWAITING_INPUT, NOW)

    paused_cp1 = js.create_job(deal_id="d-cp1", routing="ACQ", owner="evan", now_iso=NOW)
    js.transition(paused_cp1.job_id, JobStatus.ROUTING, NOW)
    js.transition(paused_cp1.job_id, JobStatus.ANALYZING, NOW)
    js.transition(paused_cp1.job_id, JobStatus.SYNTHESIZING, NOW)
    js.transition(paused_cp1.job_id, JobStatus.AWAITING_CP1, NOW)

    assert queue.sweep_stale_jobs(job_store=js, now_iso=NOW) == 1

    failed = js.get_job(stale.job_id)
    assert failed.status == JobStatus.FAILED
    assert "server restarted" in (failed.error or "")
    assert any(e.kind == "error" and "server restarted" in e.summary for e in failed.audit)

    assert js.get_job(paused_input.job_id).status == JobStatus.AWAITING_INPUT
    assert js.get_job(paused_cp1.job_id).status == JobStatus.AWAITING_CP1


def test_sync_mode_flag(env, monkeypatch):
    """DREAM_JOBS_SYNC=1 locks the v1 back-compat contract: POST runs the whole pipeline
    inside the request and returns the CP-1 view directly."""
    _client, _js, _ds = env
    client = _client
    monkeypatch.setenv("DREAM_JOBS_SYNC", "1")
    r = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "awaiting_cp1"
    assert body["phase"] == "cp1"
    assert "irr" in body["headline_metrics"]
