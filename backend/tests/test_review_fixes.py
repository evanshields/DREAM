"""Regression tests for the 2026-06-09 production-readiness review fixes.

Covers, in finding order:
  1. Google ID tokens (3-segment JWTs with a non-app issuer) route to the GOOGLE verifier even
     when AUTH_JWT_SECRET is set (the shape-heuristic bug 401'd every Google login).
  2. A non-JWT token on a JWT-only server (no GOOGLE_CLIENT_ID) -> 401, never 500.
  3. Missing engine inputs -> AWAITING_INPUT with blocking questions (not a 422 crash after the
     Wave-1 spend); answering them resumes to CP-1 reproducing Esplanade.
  4. An AWAITING_INPUT resume re-runs with the ORIGINAL deal_docs + intake (not just the answers).
  5. A blocking RED gate FAILs the job closed (spec persisted as gate_failed, never computed/CP-1).
  6. Idempotent replay creates NO orphan deal row.
  7. engine_boundary.f() maps NaN/inf -> None (JSON-safe; no poisoned specs).
  8. /api/recalc rejects exit_cap<=0 (422) and exit_cap sweeps containing 0 (400).
"""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("jwt")

import routers.jobs as jobs_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402

SECRET = "test-secret-do-not-use-in-prod"

READY = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


# ---------------------------------------------------------------------------
# Jobs harness (mirrors test_jobs_api.py)
# ---------------------------------------------------------------------------

def _jobs_client(monkeypatch, analysts_factory):
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", analysts_factory)
    app = FastAPI()
    app.include_router(jobs_router.router)
    return TestClient(app), ds, js


# ---------------------------------------------------------------------------
# 1+2. Auth routing — issuer dispatch + 401-not-500
# ---------------------------------------------------------------------------

def _auth_app():
    from fastapi import Depends
    from auth_dep import require_auth
    app = FastAPI()

    @app.get("/api/me")
    def me(user: dict = Depends(require_auth)):
        return {"email": user.get("email")}

    return app


def test_google_issuer_jwt_routes_to_google_even_with_app_secret_set(monkeypatch):
    """THE critical auth fix: a 3-segment JWT whose iss is NOT ours must reach the Google
    verifier, not die in the HS256 path. Before the fix this returned 401 for every Google
    login whenever AUTH_JWT_SECRET was configured."""
    import jwt as pyjwt
    import auth_dep
    monkeypatch.setenv("AUTH_JWT_SECRET", SECRET)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    monkeypatch.setattr(auth_dep, "ALLOWED_EMAILS", {"evan@shieldstone.co"}, raising=False)
    monkeypatch.setattr(auth_dep, "verify_google_token",
                        lambda tok: {"email": "evan@shieldstone.co", "name": "Evan", "sub": "g1"})
    google_like = pyjwt.encode(
        {"iss": "https://accounts.google.com", "sub": "g1", "email": "evan@shieldstone.co",
         "exp": 9999999999},
        "googles-own-key", algorithm="HS256",
    )
    r = TestClient(_auth_app()).get("/api/me", headers={"Authorization": f"Bearer {google_like}"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "evan@shieldstone.co"


def test_jwt_only_server_bad_token_is_401_not_500(monkeypatch):
    """JWT-only config (the 24h stopgap): client garbage must map to 401, not a 500 from the
    unconfigured Google path."""
    monkeypatch.setenv("AUTH_JWT_SECRET", SECRET)
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    for bad in ("opaque-not-a-jwt", "aaa.bbb.ccc"):
        r = TestClient(_auth_app()).get("/api/me", headers={"Authorization": f"Bearer {bad}"})
        assert r.status_code == 401, (bad, r.status_code, r.text)


# ---------------------------------------------------------------------------
# 3. Missing engine inputs -> AWAITING_INPUT (ask, don't crash) -> answer -> CP-1
# ---------------------------------------------------------------------------

class _NoDebtStub(StubAnalysts):
    """Stub whose assumptions slice 'failed to extract' the bridge debt terms — the live-Kimi
    sparse-intake scenario that crashed with a TypeError 422 in production."""

    def run_all(self, deal_docs=None, intake_summary=None, critical_inputs=None):
        outs = super().run_all(deal_docs, intake_summary, critical_inputs)
        ei = outs[2].get("assumptions_engine_inputs", {})
        for k in ("bridge_loan", "bridge_rate", "bridge_io_years"):
            ei.pop(k, None)
        return outs


def test_missing_engine_inputs_pauses_with_questions_then_resumes(monkeypatch):
    client, ds, js = _jobs_client(monkeypatch, lambda: _NoDebtStub())

    r = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text          # NOT a 422 — the crash is now a pause
    body = r.json()
    assert body["status"] == "awaiting_input"
    blocking_fields = {q["field"] for q in body["blocking_questions"]}
    assert {"meta.critical_inputs.bridge_loan", "meta.critical_inputs.bridge_rate",
            "meta.critical_inputs.bridge_io_years"} <= blocking_fields

    # Answer the three engine questions with the Esplanade values -> resume -> CP-1.
    jid = body["job_id"]
    answers = {"bridge_loan": 23800000, "bridge_rate": 0.08, "bridge_io_years": 2}
    for q in body["blocking_questions"]:
        name = q["field"].rsplit(".", 1)[-1]
        r = client.post(f"/api/jobs/{jid}/answer",
                        json={"question_id": q["id"], "answer": answers[name]})
        assert r.status_code == 200, r.text
    final = r.json()
    assert final["status"] == "awaiting_cp1", final
    assert rel(final["headline_metrics"]["irr"], 0.2221) <= 0.02


# ---------------------------------------------------------------------------
# 4. Resume preserves the ORIGINAL deal_docs + intake
# ---------------------------------------------------------------------------

class _DocsSpy(StubAnalysts):
    calls: list = []

    def run_all(self, deal_docs=None, intake_summary=None, critical_inputs=None):
        type(self).calls.append({"deal_docs": dict(deal_docs or {}),
                                 "intake_summary": dict(intake_summary or {})})
        return super().run_all(deal_docs, intake_summary, critical_inputs)


def test_resume_rehydrates_original_docs_and_intake(monkeypatch):
    _DocsSpy.calls = []
    client, ds, js = _jobs_client(monkeypatch, lambda: _DocsSpy())

    intake = {"routing": "ACQ", "deal_name": "DocsDeal",
              "critical_inputs": {"purchase_price": 55000000, "hold_years": 7}}  # exit_cap missing
    r = client.post("/api/jobs", json={"intake_summary": intake, "owner": "evan",
                                       "deal_docs": {"t12": "THE-ORIGINAL-T12"}})
    body = r.json()
    assert body["status"] == "awaiting_input"
    assert len(_DocsSpy.calls) == 0              # Wave 0 blocked BEFORE the slices ran

    q = body["blocking_questions"][0]
    r = client.post(f"/api/jobs/{body['job_id']}/answer",
                    json={"question_id": q["id"], "answer": 0.06})
    assert r.json()["status"] == "awaiting_cp1", r.text
    assert len(_DocsSpy.calls) == 1
    assert _DocsSpy.calls[0]["deal_docs"] == {"t12": "THE-ORIGINAL-T12"}
    assert _DocsSpy.calls[0]["intake_summary"].get("deal_name") == "DocsDeal"


# ---------------------------------------------------------------------------
# 5. Blocking RED gate -> FAILED (fail closed), spec persisted as gate_failed
# ---------------------------------------------------------------------------

def test_red_gate_fails_closed(monkeypatch):
    import jobs.runner as runner_mod

    class _FakeGate:
        ok = False
        blocking = ["fee_bounds"]

        def as_dict(self):
            return {"ok": False, "blocking": ["fee_bounds"]}

    class _FakeResult:
        spec = {"meta": {"deal_name": "RedDeal"}, "qa": {"fee_bounds": {"ok": False}},
                "cells": [], "headline_metrics": {"irr": 0.2}}
        headline_metrics = {"irr": 0.2}
        gate_summary = _FakeGate()
        open_questions = []

    monkeypatch.setattr(runner_mod, "run_synthesis", lambda *a, **k: _FakeResult())
    client, ds, js = _jobs_client(monkeypatch, lambda: StubAnalysts())

    r = client.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "failed"
    assert "fee_bounds" in (body["error"] or "")
    deals = ds.list()
    assert len(deals) == 1 and deals[0].status == "gate_failed"   # never 'computed'


# ---------------------------------------------------------------------------
# 6. Idempotent replay leaves NO orphan deal
# ---------------------------------------------------------------------------

def test_idempotent_replay_creates_no_orphan_deal(monkeypatch):
    client, ds, js = _jobs_client(monkeypatch, lambda: StubAnalysts())
    payload = {"intake_summary": READY, "owner": "evan", "idempotency_key": "retry-123"}
    r1 = client.post("/api/jobs", json=payload)
    r2 = client.post("/api/jobs", json=payload)
    assert r1.json()["job_id"] == r2.json()["job_id"]
    assert len(ds.list()) == 1                   # the retry inserted no second deal row


# ---------------------------------------------------------------------------
# 7. f() non-finite guard
# ---------------------------------------------------------------------------

def test_f_maps_non_finite_to_none():
    from engine_boundary import f
    assert f(float("nan")) is None
    assert f(float("inf")) is None
    assert f(float("-inf")) is None
    assert f(1.5) == 1.5
    assert f(None) is None


# ---------------------------------------------------------------------------
# 8. recalc rejects exit_cap <= 0
# ---------------------------------------------------------------------------

def _recalc_client():
    from routers.recalc import router as recalc_router
    app = FastAPI()
    app.include_router(recalc_router)
    return TestClient(app)

ESPLANADE_BODY = {
    "bridge_loan": 23800000, "bridge_rate": 0.08, "bridge_io_years": 2,
    "refi_loan": 31944864, "refi_rate": 0.06, "refi_io_years": 3,
    "total_equity": 13145673,
    "noi_series": [2387932, 2563041, 2742167, 2883487, 2983197,
                   3134540, 3241781, 3352240, 3466013, 3583198],
    "sale_year": 7, "costs_of_sale": 0.02,
}


def test_recalc_rejects_zero_exit_cap():
    r = _recalc_client().post("/api/recalc", json={**ESPLANADE_BODY, "exit_cap": 0})
    assert r.status_code == 422


def test_sensitivity_rejects_zero_in_exit_cap_sweep():
    r = _recalc_client().post("/api/recalc/sensitivity", json={
        "base": {**ESPLANADE_BODY, "exit_cap": 0.06},
        "field": "exit_cap", "values": [0.0, 0.05, 0.06], "metric": "irr",
    })
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# 9. Live-Kimi resume bug (2026-07-10): array answers must not reach the LLM slices
#    as critical inputs, and an LLM echoing a non-scalar cell must not kill the run.
# ---------------------------------------------------------------------------

class _CISpy(StubAnalysts):
    """Records the critical_inputs each run_all call receives."""
    seen: list = []

    def run_all(self, deal_docs=None, intake_summary=None, critical_inputs=None):
        type(self).seen.append(dict(critical_inputs or {}))
        return super().run_all(deal_docs, intake_summary, critical_inputs)


def test_slices_receive_only_bl17_trio_not_engine_answers(monkeypatch):
    """Answered engine fields (esp. arrays like noi_series) go to SYNTHESIS only — the analyst
    slices get wave0's three scalar BL-17 inputs (their contract). Feeding arrays to the live LLM
    made it echo them back as schema-invalid cells (the 2026-07-10 production failure)."""
    _CISpy.seen = []
    client, ds, js = _jobs_client(monkeypatch, lambda: _CISpy())
    intake = {"routing": "ACQ", "deal_name": "SpyDeal",
              "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06,
                                  "noi_series": [1.0, 2.0, 3.0],       # engine answer riding along
                                  "bridge_loan": 23800000}}
    r = client.post("/api/jobs", json={"intake_summary": intake, "owner": "evan"})
    assert r.status_code == 200, r.text
    assert len(_CISpy.seen) == 1
    ci_seen = _CISpy.seen[0]
    assert set(ci_seen.keys()) == {"purchase_price", "hold_years", "exit_cap"}
    assert "noi_series" not in ci_seen and "bridge_loan" not in ci_seen


def test_validate_slice_drops_non_scalar_cells_instead_of_raising():
    from jobs.analysts import validate_slice
    out = {"t12_cells": [
        {"cell": "B10", "value": 55000000, "source": "OM p.3"},
        {"cell": "noi_series", "value": [1, 2, 3], "source": "BL-17"},   # LLM echo — drop
    ]}
    cleaned = validate_slice(out)
    assert cleaned is out                                    # identity preserved
    assert [c["cell"] for c in cleaned["t12_cells"]] == ["B10"]
