"""PRD C.4 — deal-memo API acceptance tests. Mounts routers/memo.py (plus routers/deals.py +
routers/jobs.py so the GET detail view proves persistence) on a bare FastAPI app with in-memory
stores and a MOCKED MemoGenerator — no live Kimi/LLM anywhere (the generator seam
routers.memo.get_memo_generator is monkeypatched, mirroring the store-singleton harness style
of test_deals_api.py).

Covers: 404 unknown deal; 409 on an un-computed draft; the happy path (draft marker, routing-aware
payload the generator receives, persistence at spec.narrative.memo visible via GET /api/deals/{id},
version bump with status unchanged); regeneration overwrites; the determinism rule (memo writes
NEITHER headline_metrics NOR qa)."""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.deals as deals_router  # noqa: E402
import routers.jobs as jobs_router  # noqa: E402
import routers.memo as memo_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402


class FakeMemoGenerator:
    """Stands in for the Kimi-backed MemoGenerator: records every (inputs, model_results) call
    and returns a deterministic, numbered markdown body (so overwrite tests can tell runs apart)."""

    def __init__(self):
        self.calls = []

    def generate(self, inputs: dict, model_results: dict) -> str:
        self.calls.append((inputs, model_results))
        return f"## Fake Memo #{len(self.calls)}\n\nBody prose for {inputs.get('property_name')}."


def _spec(deal_name, slug, routing, headline_metrics=None, qa=None, cells=None,
          critical_inputs=None):
    meta = {"deal_name": deal_name, "slug": slug, "routing": routing, "mode": "HITL"}
    if critical_inputs is not None:
        meta["critical_inputs"] = critical_inputs
    spec = {"meta": meta, "qa": qa or {}, "cells": cells or []}
    if headline_metrics is not None:
        spec["headline_metrics"] = headline_metrics
    return spec


ACQ_HM = {"irr": 0.2221, "equity_multiple": 2.733, "coc_year1": 0.081, "total_equity": 20500000.0}
EFB_HM = {"bond_amount": 41200000.0, "annual_debt_service": 2965000.0, "year1_noi": 3700000.0,
          "year1_dscr": 1.2479, "target_dscr": 1.25, "bond_rate": 0.055,
          "tax_savings_10yr": 9500000.0}


@pytest.fixture
def client(monkeypatch):
    """Fresh in-memory deal + job stores wired into all three routers' singletons, plus the
    mocked memo generator wired into routers.memo's seam. Returns (ds, fake, TestClient)."""
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    fake = FakeMemoGenerator()
    monkeypatch.setattr(memo_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(memo_router, "get_memo_generator", lambda: fake)
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(deals_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    app = FastAPI()
    app.include_router(memo_router.router)
    app.include_router(deals_router.router)
    app.include_router(jobs_router.router)
    return ds, fake, TestClient(app)


def test_memo_unknown_deal_404(client):
    _ds, fake, c = client
    r = c.post("/api/deals/nope/memo")
    assert r.status_code == 404
    assert fake.calls == []  # no LLM call on a 404


def test_memo_uncomputed_draft_409(client):
    """A draft with no headline_metrics has nothing deterministic to write prose over — 409,
    and the generator is never invoked."""
    ds, fake, c = client
    rec = ds.create(_spec("Draft Deal", "draft-deal", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00", status="draft")
    r = c.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 409
    assert "no computed spec" in r.json()["detail"]
    assert fake.calls == []


def test_memo_empty_headline_metrics_409(client):
    """headline_metrics present but EMPTY ({}) is still un-computed — 409."""
    ds, fake, c = client
    rec = ds.create(_spec("Empty HM", "empty-hm", "ACQ", headline_metrics={}), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00", status="draft")
    assert c.post(f"/api/deals/{rec.deal_id}/memo").status_code == 409
    assert fake.calls == []


def test_memo_happy_path_acq(client):
    """Computed ACQ deal: 200 with the draft marker + generated_at; the generator receives the
    ROUTING-AWARE payload (irr surfaced as levered_irr, gates + critical inputs + assumptions
    included); the memo persists at spec.narrative.memo and is visible via GET /api/deals/{id}
    with the version bumped and status UNCHANGED."""
    ds, fake, c = client
    qa = {"fee_bounds": {"status": "PASS"}, "unit_count": {"status": "PASS"}}
    cells = [{"cell": "B31", "value": 0.03, "source": "llm-inferred"},
             {"cell": "B12", "value": 55000000, "source": "OM p.3"}]
    rec = ds.create(
        _spec("Esplanade", "esplanade", "ACQ", headline_metrics=ACQ_HM, qa=qa, cells=cells,
              critical_inputs={"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06}),
        owner="evan", now_iso="2026-06-10T00:00:00+00:00", status="computed",
    )

    r = c.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) == {"memo_markdown", "generated_at"}
    # the generated-draft marker leads the markdown (provenance travels WITH the memo)
    assert body["memo_markdown"].startswith(memo_router.GENERATED_DRAFT_MARKER)
    assert "Fake Memo #1" in body["memo_markdown"]
    assert body["generated_at"]

    # --- the routing-aware payload the (mocked) generator received --------------------------
    assert len(fake.calls) == 1
    inputs, model_results = fake.calls[0]
    assert inputs["property_name"] == "Esplanade"
    assert inputs["routing"] == "ACQ"
    assert inputs["purchase_price"] == 55000000      # critical inputs folded in
    assert inputs["hold_years"] == 7
    assert "B12" in inputs["key_assumptions"]        # cited assumption cell, provenance attached
    assert "OM p.3" in str(inputs["key_assumptions"]["B12"])
    assert model_results["levered_irr"] == 0.2221    # ACQ mapping: irr -> levered_irr
    assert model_results["equity_multiple"] == 2.733
    assert model_results["qa_gates"] == qa           # deterministic gate verdicts ride along
    # determinism: the generator only ever READS the engine outputs it was handed
    assert model_results["irr"] == 0.2221

    # --- persistence: spec.narrative.memo, visible via GET /api/deals/{id} ------------------
    d = c.get(f"/api/deals/{rec.deal_id}").json()
    assert d["spec"]["narrative"]["memo"]["markdown"] == body["memo_markdown"]
    assert d["spec"]["narrative"]["memo"]["generated_at"] == body["generated_at"]
    assert d["version"] == rec.version + 1           # optimistic put bumped the version
    assert d["status"] == "computed"                  # status UNCHANGED by memo generation
    # determinism rule: memo NEVER writes headline_metrics / qa
    assert d["spec"]["headline_metrics"] == ACQ_HM
    assert d["spec"]["qa"] == qa


def test_memo_happy_path_efb_bond_metrics(client):
    """Computed EFB deal: the generator receives the BOND-metric shape (year1_dscr surfaced as
    yr1_dscr, bond_amount / tax savings present, NO levered_irr fabricated)."""
    ds, fake, c = client
    rec = ds.create(
        _spec("Rayzor Ranch", "rayzor-ranch", "EFB", headline_metrics=EFB_HM,
              critical_inputs={"stabilized_noi": 3700000, "annual_property_tax_exempted": 950000}),
        owner="evan", now_iso="2026-06-10T00:00:00+00:00", status="computed",
    )
    r = c.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 200, r.text

    inputs, model_results = fake.calls[0]
    assert inputs["routing"] == "EFB"
    assert inputs["stabilized_noi"] == 3700000
    assert model_results["bond_amount"] == 41200000.0
    assert model_results["yr1_dscr"] == 1.2479        # EFB mapping: year1_dscr -> yr1_dscr
    assert model_results["tax_savings_10yr"] == 9500000.0
    assert model_results["annual_tax_savings"] == 950000
    assert "levered_irr" not in model_results         # never fabricate ACQ metrics on the bond route


def test_memo_regeneration_overwrites(client):
    """A second POST regenerates and OVERWRITES spec.narrative.memo (no memo history in the spec),
    bumping the version again. Pre-existing narrative keys survive."""
    ds, fake, c = client
    spec = _spec("Esplanade", "esplanade", "ACQ", headline_metrics=ACQ_HM)
    spec["narrative"] = {"thesis": "hold-period value-add"}
    rec = ds.create(spec, owner="evan", now_iso="2026-06-10T00:00:00+00:00", status="computed")

    first = c.post(f"/api/deals/{rec.deal_id}/memo").json()
    second = c.post(f"/api/deals/{rec.deal_id}/memo").json()
    assert "Fake Memo #1" in first["memo_markdown"]
    assert "Fake Memo #2" in second["memo_markdown"]

    d = c.get(f"/api/deals/{rec.deal_id}").json()
    memo = d["spec"]["narrative"]["memo"]
    assert memo["markdown"] == second["memo_markdown"]        # overwritten, not appended
    assert "Fake Memo #1" not in memo["markdown"]
    assert d["spec"]["narrative"]["thesis"] == "hold-period value-add"  # siblings preserved
    assert d["version"] == rec.version + 2                    # one bump per generation


def test_memo_after_driven_job(client):
    """End-to-end: drive a real job to CP-1 (StubAnalysts), then generate the memo off the
    PERSISTED computed spec — the full C.4 arc 'a completed run yields a deal instance + memo'."""
    _ds, fake, c = client
    r = c.post("/api/jobs", json={
        "intake_summary": {
            "routing": "ACQ", "deal_name": "Esplanade",
            "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
        },
        "owner": "evan",
    })
    assert r.status_code == 200, r.text
    jb = r.json()
    assert jb["status"] == "awaiting_cp1"

    m = c.post(f"/api/deals/{jb['deal_id']}/memo")
    assert m.status_code == 200, m.text
    inputs, model_results = fake.calls[0]
    assert inputs["property_name"] == "Esplanade"
    assert abs(model_results["levered_irr"] - 0.2221) / 0.2221 <= 0.02  # the engine's real number
    d = c.get(f"/api/deals/{jb['deal_id']}").json()
    assert d["spec"]["narrative"]["memo"]["markdown"] == m.json()["memo_markdown"]
    assert d["status"] == "computed"


def test_memo_generator_failure_502(client, monkeypatch):
    """An upstream LLM failure surfaces as 502 and persists NOTHING."""
    ds, _fake, c = client

    class ExplodingGenerator:
        def generate(self, inputs, model_results):
            raise RuntimeError("moonshot down")

    monkeypatch.setattr(memo_router, "get_memo_generator", lambda: ExplodingGenerator())
    rec = ds.create(_spec("Esplanade", "esplanade", "ACQ", headline_metrics=ACQ_HM),
                    owner="evan", now_iso="2026-06-10T00:00:00+00:00", status="computed")
    r = c.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 502
    d = c.get(f"/api/deals/{rec.deal_id}").json()
    assert "narrative" not in d["spec"] or "memo" not in d["spec"].get("narrative", {})
    assert d["version"] == rec.version  # no write happened
