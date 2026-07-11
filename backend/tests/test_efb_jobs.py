"""The EFB unlock — jobs-pipeline acceptance tests (explicit routing=EFB flows wave0 -> slices ->
EFB synthesis -> CP-1). NO LLM (StubEFBAnalysts, the Rayzor-equivalent fixture).

Oracle: the Rayzor EFB ground truth (underwriting-engine/engine/tests/test_efb_rayzor.py +
backend/tests/test_engine_boundary_efb_and_routing.py) — size bonds to the 1.15x target DSCR on
stabilized NOI $4,448,271.31 @ 5% / 35yr and the IMPLIED Y1 DSCR comes back at target within 2%.
The end-to-end headline must equal run_efb_underwrite on the same inputs EXACTLY (same validated
engine, no LLM in between), and must carry the EFB shape (bond_amount / year1_dscr), never irr.
"""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.jobs as jobs_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubEFBAnalysts, merge_slices, _RAYZOR_EFB_ENGINE_INPUTS  # noqa: E402
from jobs.synthesis import run_synthesis, _coerce_efb_inputs, MissingEngineInputsError  # noqa: E402
from engine_boundary import EFBDealInputs, run_efb_underwrite  # noqa: E402

TS = "2026-07-11T00:00:00Z"

# Rayzor EFB ground truth (mirrors test_engine_boundary_efb_and_routing.py)
RAYZOR_NOI = 4448271.31
TARGET_DSCR = 1.15
LINE_TOL = 0.02

# The exact oracle: the validated engine run on the fixture inputs. The jobs pipeline must
# reproduce this headline byte-for-byte (floats from the same Decimal path — no LLM in between).
ORACLE_HM = run_efb_underwrite(EFBDealInputs(**_RAYZOR_EFB_ENGINE_INPUTS))

READY_EFB = {
    "routing": "EFB", "deal_name": "Rayzor Ranch",
    "critical_inputs": {"stabilized_noi": RAYZOR_NOI},
}


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


def _client(monkeypatch, analysts_factory=None):
    """Mirrors the test_jobs_api harness: fresh in-memory stores + StubEFBAnalysts."""
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts",
                        analysts_factory or (lambda: StubEFBAnalysts()))
    app = FastAPI()
    app.include_router(jobs_router.router)
    return TestClient(app), ds, js


def _assert_rayzor_headline(hm):
    """The Rayzor-truth assertions every CP-1 in this file converges to."""
    # exact match vs the validated engine on the same inputs (the pipeline adds nothing)
    for key, expected in ORACLE_HM.items():
        assert hm[key] == expected, (key, hm[key], expected)
    # and the independent ground-truth invariants (never trust only self-consistency)
    assert rel(hm["year1_dscr"], TARGET_DSCR) <= LINE_TOL
    assert hm["year1_noi"] == pytest.approx(RAYZOR_NOI)
    assert hm["bond_amount"] > 0
    assert hm["tax_savings_10yr"] == 9000000  # 900k exempted * 10yr hold
    assert "irr" not in hm  # EFB shape, not ACQ


# ---------------------------------------------------------------------------
# End-to-end: explicit routing=EFB + stabilized_noi -> CP-1 with Rayzor truth
# ---------------------------------------------------------------------------

def test_efb_submit_runs_to_cp1_with_rayzor_truth(monkeypatch):
    client, ds, js = _client(monkeypatch)
    r = client.post("/api/jobs", json={"intake_summary": READY_EFB, "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "awaiting_cp1"
    assert body["phase"] == "cp1"
    assert body["routing"] == "EFB"

    _assert_rayzor_headline(body["headline_metrics"])

    # spec is canonical: persisted with routing + critical inputs on meta
    spec = body["spec"]
    assert spec["meta"]["routing"] == "EFB"
    assert spec["meta"]["critical_inputs"]["stabilized_noi"] == RAYZOR_NOI

    # gates ran on the assembled spec
    qa = body["gate_summary"]
    assert qa["fee_bounds"]["ok"] is True                      # B39 @ 5% passes on EFB
    assert "EFB" in qa["fee_bounds"]["reason"]                 # ...with the documented reason
    assert qa["unit_count"]["reconciled"] is True              # routing-agnostic gate still fires
    assert qa["formula_audit"]["skipped"] is True              # BL-07: explicit skip, never silent
    assert "ACQ mini-model" in qa["formula_audit"]["reason"]

    # the llm-inferred judgment cell surfaced as a (non-blocking) open question
    assert any(q["field"] == "B31" and not q["blocking"] for q in body["open_questions"])

    # HITL: the deal spec persisted as computed; job stopped at CP-1 (never auto-completes)
    deal = ds.get(body["deal_id"])
    assert deal.status == "computed"


def test_efb_missing_stabilized_noi_awaits_then_resumes_to_cp1(monkeypatch):
    client, ds, js = _client(monkeypatch)
    r = client.post("/api/jobs", json={"intake_summary": {"routing": "EFB", "deal_name": "Rayzor"},
                                       "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "awaiting_input"
    assert [q["field"] for q in body["blocking_questions"]] == \
        ["meta.critical_inputs.stabilized_noi"]

    q = body["blocking_questions"][0]
    r = client.post(f"/api/jobs/{body['job_id']}/answer",
                    json={"question_id": q["id"], "answer": RAYZOR_NOI})
    assert r.status_code == 200, r.text
    final = r.json()
    assert final["status"] == "awaiting_cp1"
    _assert_rayzor_headline(final["headline_metrics"])


class _BadBondRateStub(StubEFBAnalysts):
    """Assumptions slice extracted an invalid bond_rate — synthesis must ASK (EFB namespace),
    not crash, and the human answer must beat the slice value on resume."""

    def slice_assumptions(self):
        out = super().slice_assumptions()
        out["assumptions_engine_inputs"]["bond_rate"] = -0.01
        return out


def test_efb_invalid_engine_field_asks_and_answer_wins_on_resume(monkeypatch):
    client, ds, js = _client(monkeypatch, lambda: _BadBondRateStub())
    r = client.post("/api/jobs", json={"intake_summary": READY_EFB, "owner": "evan"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "awaiting_input"
    qs = body["blocking_questions"]
    assert [q["field"] for q in qs] == ["meta.critical_inputs.bond_rate"]
    assert "EFB engine" in qs[0]["question"]  # routing-aware question text

    # answer rides meta.critical_inputs.* back through the resume and BEATS the slice's -0.01
    r = client.post(f"/api/jobs/{body['job_id']}/answer",
                    json={"question_id": qs[0]["id"], "answer": 0.05})
    assert r.status_code == 200, r.text
    final = r.json()
    assert final["status"] == "awaiting_cp1"
    _assert_rayzor_headline(final["headline_metrics"])


def test_ambiguous_signal_answered_efb_then_noi_then_cp1(monkeypatch):
    """The two-round flow: ambiguous prose -> routing question -> EFB answer -> stabilized_noi
    question -> CP-1. Wave 0 never guesses; the human decides the route."""
    client, ds, js = _client(monkeypatch)
    r = client.post("/api/jobs", json={
        "intake_summary": {"deal_name": "Mystery",
                           "notes": "tax-exempt bond workforce housing play"},
        "owner": "evan"})
    body = r.json()
    assert body["status"] == "awaiting_input"
    assert [q["field"] for q in body["blocking_questions"]] == ["meta.routing"]

    q = body["blocking_questions"][0]
    r = client.post(f"/api/jobs/{body['job_id']}/answer",
                    json={"question_id": q["id"], "answer": "EFB"})
    body = r.json()
    assert body["status"] == "awaiting_input"  # round 2: now the EFB critical input
    assert [q["field"] for q in body["blocking_questions"]] == \
        ["meta.critical_inputs.stabilized_noi"]

    q = body["blocking_questions"][0]
    r = client.post(f"/api/jobs/{body['job_id']}/answer",
                    json={"question_id": q["id"], "answer": RAYZOR_NOI})
    final = r.json()
    assert final["status"] == "awaiting_cp1"
    assert final["spec"]["meta"]["routing"] == "EFB"
    _assert_rayzor_headline(final["headline_metrics"])


# ---------------------------------------------------------------------------
# Synthesis-level: dispatch, coercion, overlay, fail-closed
# ---------------------------------------------------------------------------

def _efb_merged():
    merged = merge_slices(StubEFBAnalysts().run_all(None, {}, {"stabilized_noi": RAYZOR_NOI}))
    merged.setdefault("meta", {})["routing"] = "EFB"
    return merged


def test_synthesis_efb_reproduces_rayzor_truth():
    res = run_synthesis(_efb_merged(), {"stabilized_noi": RAYZOR_NOI, "hold_years": None},
                        TS, return_result=True)
    _assert_rayzor_headline(res.headline_metrics)
    assert res.gate_summary.ok is True
    assert res.gate_summary.blocking == []
    assert res.spec["qa"]["formula_audit"]["skipped"] is True
    assert res.spec["meta"]["routing"] == "EFB"
    assert [q.field for q in res.open_questions] == ["B31"]


def test_synthesis_efb_critical_input_overlay_beats_slice_value():
    """Human answers are authoritative: a stabilized_noi in critical inputs overrides the
    slices' assumptions_engine_inputs value."""
    res = run_synthesis(_efb_merged(), {"stabilized_noi": 5000000.0}, TS, return_result=True)
    hm = res.headline_metrics
    assert hm["year1_noi"] == pytest.approx(5000000.0)
    assert rel(hm["year1_dscr"], TARGET_DSCR) <= LINE_TOL  # still sized to target on the new NOI


def test_coerce_efb_missing_noi_raises_questionable_error():
    with pytest.raises(MissingEngineInputsError) as ei:
        _coerce_efb_inputs({}, {})
    assert ei.value.missing == ["stabilized_noi"]
    assert ei.value.routing == "EFB"
    assert "EFB engine inputs missing" in str(ei.value)


def test_coerce_efb_flags_non_positive_optionals():
    with pytest.raises(MissingEngineInputsError) as ei:
        _coerce_efb_inputs({"stabilized_noi": RAYZOR_NOI, "target_dscr": 0, "bond_rate": -1},
                           {})
    assert set(ei.value.missing) == {"target_dscr", "bond_rate"}


def test_coerce_efb_defaults_apply_when_optionals_absent():
    inp = _coerce_efb_inputs({"stabilized_noi": RAYZOR_NOI}, {})
    assert inp.target_dscr == 1.15 and inp.bond_rate == 0.05
    assert inp.amortization_years == 35 and inp.hold_years == 10


def test_synthesis_unknown_routing_still_fails_closed():
    merged = _efb_merged()
    merged["meta"]["routing"] = "XYZ"
    with pytest.raises(ValueError, match="ACQ or EFB"):
        run_synthesis(merged, {"stabilized_noi": RAYZOR_NOI}, TS)


# ---------------------------------------------------------------------------
# Gate harness: BL-07 is explicitly skipped on EFB even when formulas were read
# ---------------------------------------------------------------------------

def test_gates_efb_formula_audit_explicit_skip_even_with_formulas():
    from qa_gates import run_gates
    spec = {"meta": {"routing": "EFB"}, "qa": {}, "cells": []}
    out, summary = run_gates(spec, template_formulas={"S40": "=U36"})  # would be a "bug" on ACQ
    assert out["qa"]["formula_audit"]["skipped"] is True
    assert out["qa"]["formula_audit"]["reason"]
    assert "formula_audit" in summary.details          # documented, not silent
    assert summary.warnings == [] and summary.ok is True
