"""UW Snapshot read-only endpoint. Mounts routers/deals.py on a bare app with an in-memory store.

The fixture is SYNTHETIC (an invented property). The real deal shape must be confirmed by the UW Director.
The endpoint passes numbers through exactly as stored and never computes a headline metric.
"""
import copy
import json
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.deals as deals_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "uw_snapshot_synthetic.json")


def _snapshot():
    with open(FIXTURE, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def client(monkeypatch):
    ds = SQLiteDealStore(":memory:")
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    app = FastAPI()
    app.include_router(deals_router.router)
    return ds, TestClient(app)


def _make(ds, snapshot, name="Fakeville"):
    spec = {"meta": {"deal_name": name, "slug": "fakeville", "routing": "ACQ", "mode": "HITL"}}
    if snapshot is not None:
        spec["uw_snapshot"] = snapshot
    return ds.create(spec, owner="evan", now_iso="2026-11-03T00:00:00+00:00", status="computed").deal_id


def test_ready_snapshot_passes_numbers_through_exactly(client):
    ds, c = client
    snap = _snapshot()
    deal_id = _make(ds, snap)
    r = c.get(f"/api/deals/{deal_id}/uw-snapshot")
    assert r.status_code == 200
    body = r.json()
    assert body["state"] == "ready"
    assert body["blank_reason"] is None
    assert body["read_only"] is True
    assert body["snapshot"] == snap
    assert body["snapshot"]["stabilized_noi"] == 541234
    assert body["snapshot"]["exempt_dscr"] == 1.37
    assert body["snapshot"]["engine_version"] == "synthetic-engine-0.0.1"


def test_no_math_even_when_pieces_disagree(client):
    ds, c = client
    snap = _snapshot()
    snap["stabilized_noi"] = 999  # does not match anything. Must still come back as 999.
    snap["seller_t12_noi"] = 1
    body = c.get(f"/api/deals/{_make(ds, snap)}/uw-snapshot").json()
    assert body["snapshot"]["stabilized_noi"] == 999
    assert body["snapshot"]["seller_t12_noi"] == 1


@pytest.mark.parametrize("verdict", ["INCOMPLETE", "INCOMPLETE: no rent roll", "incomplete - waiting", "  INCOMPLETE"])
def test_incomplete_verdict_is_blank_and_withholds_numbers(client, verdict):
    ds, c = client
    snap = _snapshot()
    snap["verdict"] = verdict
    body = c.get(f"/api/deals/{_make(ds, snap)}/uw-snapshot").json()
    assert body["state"] == "blank"
    assert body["blank_reason"]
    assert body["snapshot"]["verdict"] == verdict
    assert body["snapshot"]["engine_version"] == "synthetic-engine-0.0.1"
    for key in ("unit_mix", "seller_t12", "seller_t12_noi", "stabilized_gpr", "stabilized_noi", "exempt_dscr"):
        assert key not in body["snapshot"], key


def test_deal_without_snapshot_is_blank_not_error(client):
    ds, c = client
    r = c.get(f"/api/deals/{_make(ds, None)}/uw-snapshot")
    assert r.status_code == 200
    body = r.json()
    assert body["state"] == "blank"
    assert body["snapshot"] is None
    assert body["blank_reason"]


@pytest.mark.parametrize("bad", [None, "", 5, [], {"x": 1}])
def test_missing_or_malformed_verdict_fails_closed_to_blank(client, bad):
    ds, c = client
    snap = _snapshot()
    snap["verdict"] = bad
    body = c.get(f"/api/deals/{_make(ds, snap)}/uw-snapshot").json()
    assert body["state"] == "blank"
    assert "stabilized_noi" not in (body["snapshot"] or {})


def test_non_dict_snapshot_is_blank(client):
    ds, c = client
    body = c.get(f"/api/deals/{_make(ds, ['not', 'a', 'dict'])}/uw-snapshot").json()
    assert body["state"] == "blank"
    assert body["snapshot"] is None


def test_unknown_deal_is_404(client):
    _ds, c = client
    assert c.get("/api/deals/nope/uw-snapshot").status_code == 404


def test_read_only_no_write_verbs(client):
    ds, c = client
    deal_id = _make(ds, _snapshot())
    for method in (c.post, c.put, c.patch, c.delete):
        assert method(f"/api/deals/{deal_id}/uw-snapshot").status_code == 405


def test_get_does_not_mutate_the_stored_deal(client):
    ds, c = client
    deal_id = _make(ds, _snapshot())
    before = ds.get(deal_id)
    c.get(f"/api/deals/{deal_id}/uw-snapshot")
    after = ds.get(deal_id)
    assert after.version == before.version
    assert after.spec == copy.deepcopy(before.spec)
