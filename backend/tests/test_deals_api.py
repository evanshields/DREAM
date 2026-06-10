"""PRD §6 — deals API acceptance tests. Mounts ONLY routers/deals.py on a bare FastAPI app (no
main.py, no auth) with an in-memory DealStore. Covers the list shape, headline_metrics surfacing,
the {} default for un-computed drafts, owner/routing/status filters, and newest-first ordering.

Mirrors test_jobs_api.py's harness style (monkeypatch the router's get_deal_store singleton)."""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.deals as deals_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402


def _spec(deal_name, slug, routing, mode="HITL", headline_metrics=None):
    spec = {
        "meta": {"deal_name": deal_name, "slug": slug, "routing": routing, "mode": mode},
    }
    if headline_metrics is not None:
        spec["headline_metrics"] = headline_metrics
    return spec


@pytest.fixture
def client(monkeypatch):
    """A fresh in-memory deal store wired into the router's singleton."""
    ds = SQLiteDealStore(":memory:")
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    app = FastAPI()
    app.include_router(deals_router.router)
    return ds, TestClient(app)


def test_empty_list(client):
    _ds, c = client
    r = c.get("/api/deals")
    assert r.status_code == 200
    assert r.json() == []


def test_list_shape_and_headline_metrics(client):
    ds, c = client
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
    ds, c = client
    ds.create(_spec("Draft Deal", "draft-deal", "EFB"), owner="evan",
              now_iso="2026-06-10T00:00:00+00:00", status="draft")
    body = c.get("/api/deals").json()
    assert body[0]["headline_metrics"] == {}


def test_filters_owner_routing_status(client):
    ds, c = client
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
    ds, c = client
    ds.create(_spec("Old", "old", "ACQ"), owner="evan", now_iso="2026-06-01T00:00:00+00:00")
    ds.create(_spec("New", "new", "ACQ"), owner="evan", now_iso="2026-06-09T00:00:00+00:00")
    names = [d["deal_name"] for d in c.get("/api/deals").json()]
    assert names == ["New", "Old"]
