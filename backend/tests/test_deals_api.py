"""PRD §6 — deals API acceptance tests. Mounts routers/deals.py (plus routers/jobs.py for the
detail view's job block) on a bare FastAPI app (no main.py, no auth, StubAnalysts — no live LLM)
with in-memory deal + job stores. Covers the list shape, headline_metrics surfacing, the {}
default for un-computed drafts, owner/routing/status filters, newest-first ordering, and the
GET /api/deals/{deal_id} detail view (404, full shape, job block, job:null).

Mirrors test_jobs_api.py's harness style (monkeypatch the routers' store singletons)."""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.deals as deals_router  # noqa: E402
import routers.jobs as jobs_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402

# A BL-17-complete ACQ intake (mirrors test_jobs_api.py) — runs straight to CP-1 under StubAnalysts.
READY = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}


def _spec(deal_name, slug, routing, mode="HITL", headline_metrics=None):
    spec = {
        "meta": {"deal_name": deal_name, "slug": slug, "routing": routing, "mode": mode},
    }
    if headline_metrics is not None:
        spec["headline_metrics"] = headline_metrics
    return spec


@pytest.fixture
def client(monkeypatch):
    """Fresh in-memory deal + job stores wired into BOTH routers' singletons (the deals detail
    view reads the job store; the jobs router drives real jobs for the job-block tests)."""
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(deals_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    app = FastAPI()
    app.include_router(deals_router.router)
    app.include_router(jobs_router.router)
    return ds, js, TestClient(app)


def test_empty_list(client):
    _ds, _js, c = client
    r = c.get("/api/deals")
    assert r.status_code == 200
    assert r.json() == []


def test_list_shape_and_headline_metrics(client):
    ds, _js, c = client
    ds.create(
        _spec("Esplanade", "esplanade", "ACQ", headline_metrics={"irr": 0.2221, "equity_multiple": 2.733}),
        owner="evan", now_iso="2026-06-10T00:00:00+00:00", status="computed",
    )
    r = c.get("/api/deals")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    d = body[0]
    # exact list-item shape (PRD §5/§6)
    for key in ("deal_id", "deal_name", "slug", "routing", "mode", "status", "owner",
                "version", "created_at", "updated_at", "headline_metrics"):
        assert key in d, f"missing key {key}"
    assert d["deal_name"] == "Esplanade"
    assert d["slug"] == "esplanade"
    assert d["routing"] == "ACQ"
    assert d["status"] == "computed"
    assert d["owner"] == "evan"
    assert d["version"] == 1
    assert d["headline_metrics"]["irr"] == 0.2221


def test_draft_has_empty_headline_metrics(client):
    ds, _js, c = client
    ds.create(_spec("Draft Deal", "draft-deal", "EFB"), owner="evan",
              now_iso="2026-06-10T00:00:00+00:00", status="draft")
    body = c.get("/api/deals").json()
    assert body[0]["headline_metrics"] == {}


def test_filters_owner_routing_status(client):
    ds, _js, c = client
    ds.create(_spec("A", "a", "ACQ"), owner="evan", now_iso="2026-06-10T00:00:01+00:00", status="computed")
    ds.create(_spec("B", "b", "EFB"), owner="charles", now_iso="2026-06-10T00:00:02+00:00", status="draft")
    ds.create(_spec("C", "c", "ACQ"), owner="evan", now_iso="2026-06-10T00:00:03+00:00", status="draft")

    assert {d["deal_name"] for d in c.get("/api/deals?owner=evan").json()} == {"A", "C"}
    assert {d["deal_name"] for d in c.get("/api/deals?routing=EFB").json()} == {"B"}
    assert {d["deal_name"] for d in c.get("/api/deals?status=draft").json()} == {"B", "C"}
    # combined filter
    combined = c.get("/api/deals?owner=evan&status=draft").json()
    assert {d["deal_name"] for d in combined} == {"C"}


def test_newest_first_ordering(client):
    ds, _js, c = client
    ds.create(_spec("Old", "old", "ACQ"), owner="evan", now_iso="2026-06-01T00:00:00+00:00")
    ds.create(_spec("New", "new", "ACQ"), owner="evan", now_iso="2026-06-09T00:00:00+00:00")
    names = [d["deal_name"] for d in c.get("/api/deals").json()]
    assert names == ["New", "Old"]


# ---------------------------------------------------------------------------
# GET /api/deals/{deal_id} — the full deal view for /deal/:id
# ---------------------------------------------------------------------------

def test_get_deal_unknown_id_404(client):
    _ds, _js, c = client
    r = c.get("/api/deals/nope")
    assert r.status_code == 404


def test_get_deal_full_shape_and_job_null(client):
    """A computed deal with NO job: full detail shape, spec/headline/gates surfaced, job: null."""
    ds, _js, c = client
    spec = _spec("Esplanade", "esplanade", "ACQ",
                 headline_metrics={"irr": 0.2221, "equity_multiple": 2.733})
    spec["qa"] = {"fee_bounds": {"status": "PASS"}, "unit_count": {"status": "PASS"}}
    rec = ds.create(spec, owner="evan", now_iso="2026-06-10T00:00:00+00:00", status="computed")

    r = c.get(f"/api/deals/{rec.deal_id}")
    assert r.status_code == 200
    d = r.json()
    # the full detail shape: list-item fields + spec + gate_summary + job
    for key in ("deal_id", "deal_name", "slug", "routing", "mode", "status", "owner",
                "version", "created_at", "updated_at", "spec", "headline_metrics",
                "gate_summary", "job"):
        assert key in d, f"missing key {key}"
    assert d["deal_id"] == rec.deal_id
    assert d["deal_name"] == "Esplanade"
    assert d["status"] == "computed"
    # the FULL canonical spec comes back opaque
    assert d["spec"] == spec
    assert d["headline_metrics"]["irr"] == 0.2221
    assert d["gate_summary"] == spec["qa"]
    # no job ever ran for this deal
    assert d["job"] is None


def test_get_deal_draft_defaults(client):
    """An un-computed draft: headline_metrics and gate_summary default to {}."""
    ds, _js, c = client
    rec = ds.create(_spec("Draft Deal", "draft-deal", "EFB"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00", status="draft")
    d = c.get(f"/api/deals/{rec.deal_id}").json()
    assert d["headline_metrics"] == {}
    assert d["gate_summary"] == {}
    assert d["job"] is None


def test_get_deal_job_block_at_cp1(client):
    """Drive a real job to CP-1 through the jobs API; the deal detail view carries the job block
    (id/status/phase/questions) plus the persisted spec/headline/gates — a cold reload of
    /deal/:id restores everything the CP-1 job view showed."""
    _ds, _js, c = client
    r = c.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    jb = r.json()
    assert jb["status"] == "awaiting_cp1"

    d = c.get(f"/api/deals/{jb['deal_id']}").json()
    # spec + headline + gates persisted on the deal (same values the CP-1 job view carried)
    assert d["spec"], "computed deal must carry the full spec"
    assert abs(d["headline_metrics"]["irr"] - 0.2221) / 0.2221 <= 0.02
    assert "fee_bounds" in d["gate_summary"]
    # the job block: latest job, with open questions surfaced
    assert d["job"] is not None
    assert d["job"]["job_id"] == jb["job_id"]
    assert d["job"]["status"] == "awaiting_cp1"
    assert d["job"]["phase"] == "cp1"
    assert d["job"]["error"] is None
    assert any(q["field"] == "B31" for q in d["job"]["open_questions"])


def test_get_deal_job_block_blocking_questions(client):
    """A job stopped at AWAITING_INPUT: the deal detail's job block surfaces the open AND
    blocking questions so a cold reload of /deal/:id restores the question form."""
    _ds, _js, c = client
    r = c.post("/api/jobs", json={"intake_summary": {"routing": "ACQ"}, "owner": "evan"})
    assert r.status_code == 200, r.text
    jb = r.json()
    assert jb["status"] == "awaiting_input"

    d = c.get(f"/api/deals/{jb['deal_id']}").json()
    assert d["job"]["status"] == "awaiting_input"
    assert len(d["job"]["blocking_questions"]) == 3  # all three BL-17 inputs missing
    assert len(d["job"]["open_questions"]) >= 3
    # un-computed seed spec: defaults stay {}
    assert d["headline_metrics"] == {}


def test_get_deal_returns_most_recent_job(client):
    """Two jobs on one deal: the detail view carries the MOST RECENT one (updated_at DESC)."""
    ds, js, c = client
    rec = ds.create(_spec("Two Jobs", "two-jobs", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00")
    js.create_job(deal_id=rec.deal_id, routing="ACQ", owner="evan",
                  now_iso="2026-06-10T01:00:00+00:00")
    newer = js.create_job(deal_id=rec.deal_id, routing="ACQ", owner="evan",
                          now_iso="2026-06-10T02:00:00+00:00")
    d = c.get(f"/api/deals/{rec.deal_id}").json()
    assert d["job"]["job_id"] == newer.job_id
