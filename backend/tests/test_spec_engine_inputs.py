"""Phase 4b — spec["engine_inputs"] persistence (the assumption-dashboard seed).

run_synthesis now stashes the EXACT engine-inputs dataclass it computed on (post-coercion,
post-critical-input overlay) onto the spec as `engine_inputs` = {"routing": ..., **fields},
None-valued fields dropped. The block is ADDITIVE and inert: floats/JSON only, written AFTER
run_gates returns (the gates never see the key), and headline_metrics must be byte-identical to
what the pipeline produced before the change (Esplanade ACQ + Rayzor EFB oracles).

Harness mirrors test_runner.py: drive run_job to CP-1 with the Stub analysts (no LLM, in-memory
stores), then load the PERSISTED deal and assert on deal.spec.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.runner import run_job  # noqa: E402
from jobs.analysts import (  # noqa: E402
    StubAnalysts,
    StubEFBAnalysts,
    _ESPLANADE_ENGINE_INPUTS,
    _RAYZOR_EFB_ENGINE_INPUTS,
)
from jobs.contracts import JobStatus  # noqa: E402

TS = "2026-07-12T00:00:00Z"

READY_ACQ = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}
READY_EFB = {
    "routing": "EFB", "deal_name": "Rayzor Ranch",
    "critical_inputs": {"stabilized_noi": _RAYZOR_EFB_ENGINE_INPUTS["stabilized_noi"]},
}


def _stores():
    return SQLiteDealStore(":memory:"), SQLiteJobStore(":memory:")


def _seed_deal_and_job(ds, js, routing="ACQ", name="Esplanade", slug="esplanade"):
    seed = {"meta": {"deal_name": name, "slug": slug, "routing": routing,
                     "template": "acq" if routing == "ACQ" else "efb-mini-model",
                     "mode": "HITL"}, "qa": {}, "cells": []}
    deal = ds.create(seed, owner="evan", now_iso=TS, status="draft")
    job = js.create_job(deal_id=deal.deal_id, routing=routing, owner="evan", now_iso=TS)
    return deal, job


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


def test_acq_engine_inputs_persisted_and_headline_unchanged():
    """ACQ run to CP-1: spec["engine_inputs"] exists, names the route, round-trips the stub's
    bridge/refi/equity/noi_series inputs verbatim, and the Esplanade headline oracle is untouched
    (the block is additive — same tolerance test_jobs_api.py asserts)."""
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js)
    final = run_job(job.job_id, analysts=StubAnalysts(), now_iso=TS,
                    intake_summary=READY_ACQ, job_store=js, deal_store=ds)
    assert final.status == JobStatus.AWAITING_CP1

    deal = ds.get(job.deal_id)
    assert deal.status == "computed"
    spec = deal.spec

    ei = spec.get("engine_inputs")
    assert ei, "spec must carry the persisted engine_inputs block"
    assert ei["routing"] == "ACQ"
    # Every stub-supplied engine input round-trips EXACTLY (the critical-input overlay values —
    # exit_cap 0.06, hold_years 7 -> sale_year 7 — equal the stub's, so nothing shifts).
    for key, expected in _ESPLANADE_ENGINE_INPUTS.items():
        assert ei[key] == expected, (key, ei[key], expected)
    # spot-check the load-bearing four the dashboard seeds from
    assert ei["bridge_loan"] == 23800000.0
    assert ei["refi_loan"] == 31944864.0
    assert ei["total_equity"] == 13145673.0
    assert len(ei["noi_series"]) == 10
    # None-valued optional series are DROPPED, not persisted as nulls
    for absent in ("gpr_series", "egi_series", "opex_series", "vacancy_series", "debt_service"):
        assert absent not in ei

    # headline_metrics unchanged vs the existing oracle (test_jobs_api.py / test_runner.py)
    hm = spec["headline_metrics"]
    assert rel(hm["irr"], 0.2221) <= 0.02
    assert rel(hm["equity_multiple"], 2.72) <= 0.02
    # gates still fired on the assembled spec (engine_inputs was added AFTER run_gates; the qa
    # block carries only gate verdicts, never the inputs)
    assert "fee_bounds" in spec["qa"]
    assert "engine_inputs" not in spec["qa"]


def test_efb_engine_inputs_persisted_and_headline_unchanged():
    """EFB variant (cheap via StubEFBAnalysts): the persisted block carries routing=EFB + the
    Rayzor bond-sizing inputs verbatim, and the Rayzor headline invariants hold unchanged."""
    ds, js = _stores()
    _deal, job = _seed_deal_and_job(ds, js, routing="EFB", name="Rayzor Ranch", slug="rayzor")
    final = run_job(job.job_id, analysts=StubEFBAnalysts(), now_iso=TS,
                    intake_summary=READY_EFB, job_store=js, deal_store=ds)
    assert final.status == JobStatus.AWAITING_CP1

    spec = ds.get(job.deal_id).spec
    ei = spec.get("engine_inputs")
    assert ei, "spec must carry the persisted engine_inputs block"
    assert ei["routing"] == "EFB"
    for key, expected in _RAYZOR_EFB_ENGINE_INPUTS.items():
        assert ei[key] == expected, (key, ei[key], expected)

    # headline unchanged vs the Rayzor oracle invariants (test_efb_jobs.py)
    hm = spec["headline_metrics"]
    assert rel(hm["year1_dscr"], 1.15) <= 0.02
    assert rel(hm["year1_noi"], _RAYZOR_EFB_ENGINE_INPUTS["stabilized_noi"]) <= 1e-9
    assert hm["tax_savings_10yr"] == 9000000
    assert "irr" not in hm  # EFB shape, never ACQ
