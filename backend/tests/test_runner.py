"""Wave C-v1 — runner acceptance tests. End-to-end Esplanade run STOPS at AWAITING_CP1 (HITL, never
auto-completes), headline reproduces ground truth + gates present; missing critical inputs STOP at
AWAITING_INPUT; a cooperative cancel mid-run lands CANCELLED."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.runner import run_job  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402
from jobs.contracts import JobStatus, JobPhase  # noqa: E402

TS = "2026-06-09T00:00:00Z"
READY_SUMMARY = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}


def _stores():
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    return ds, js


def _seed_deal_and_job(ds, js, summary=READY_SUMMARY):
    seed = {"meta": {"deal_name": "Esplanade", "slug": "esplanade", "routing": "ACQ",
                     "template": "acq", "mode": "HITL"}, "qa": {}, "cells": []}
    deal = ds.create(seed, owner="evan", now_iso=TS, status="draft")
    job = js.create_job(deal_id=deal.deal_id, routing="ACQ", owner="evan", now_iso=TS)
    return deal, job


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


def test_end_to_end_stops_at_cp1_with_ground_truth():
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js)
    final = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary=READY_SUMMARY, job_store=js, deal_store=ds)
    # HITL: stops at CP-1, never COMPLETED
    assert final.status == JobStatus.AWAITING_CP1
    assert final.phase == JobPhase.CP1

    # spec persisted to the deal; headline reproduces Esplanade
    deal = ds.get(job.deal_id)
    assert deal.status == "computed"
    hm = deal.spec["headline_metrics"]
    assert rel(hm["irr"], 0.2221) <= 0.02
    assert rel(hm["equity_multiple"], 2.72) <= 0.02
    # gates present
    assert "fee_bounds" in deal.spec["qa"]
    assert "unit_count" in deal.spec["qa"]
    # the llm-inferred cell surfaced as an open question
    assert any(q.field == "B31" for q in final.open_questions)


def test_audit_trail_records_phases():
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js)
    final = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary=READY_SUMMARY, job_store=js, deal_store=ds)
    kinds = [e.kind for e in final.audit]
    assert "phase" in kinds and "gate" in kinds and "spec_mutation" in kinds
    # monotonic seq
    assert [e.seq for e in final.audit] == list(range(len(final.audit)))


def test_missing_inputs_stop_at_awaiting_input():
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js)
    final = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary={"routing": "ACQ"},  # no critical inputs
                    job_store=js, deal_store=ds)
    assert final.status == JobStatus.AWAITING_INPUT
    assert final.has_blocking_questions() is True
    # deal not computed
    assert ds.get(job.deal_id).status == "draft"


def test_cancel_mid_run_lands_cancelled():
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js)

    class CancelingAnalysts(StubAnalysts):
        def __init__(self, js, job_id):
            super().__init__()
            self._js, self._job_id = js, job_id

        def run_all(self, deal_docs=None, intake_summary=None, critical_inputs=None):
            # request cancel BEFORE the slices complete; the runner checks between slices
            self._js.request_cancel(self._job_id)
            return super().run_all(deal_docs, intake_summary, critical_inputs)

    final = run_job(job.job_id, analysts=CancelingAnalysts(js, job.job_id), now_iso=TS,
                    intake_summary=READY_SUMMARY, job_store=js, deal_store=ds)
    assert final.status == JobStatus.CANCELLED
    # deal never got a computed spec
    assert ds.get(job.deal_id).status == "draft"


def test_rerun_paused_at_cp1_is_noop():
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js)
    first = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary=READY_SUMMARY, job_store=js, deal_store=ds)
    assert first.status == JobStatus.AWAITING_CP1
    audit_len = len(first.audit)
    deal_version = ds.get(job.deal_id).version
    # A job paused at CP-1 is HITL — a re-run must NOT re-drive the engine or reset progress.
    again = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary=READY_SUMMARY, job_store=js, deal_store=ds)
    assert again.status == JobStatus.AWAITING_CP1
    assert len(again.audit) == audit_len           # no new audit
    assert ds.get(job.deal_id).version == deal_version  # spec not re-written
