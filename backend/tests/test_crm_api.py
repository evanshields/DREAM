"""Phase 5 CRM API acceptance tests. Mounts routers/crm.py (plus routers/deals.py + routers/jobs.py
for deal existence + the timeline's audit source) on a bare FastAPI app with in-memory stores, in
the standalone-mount idiom of test_deals_api.py (monkeypatch the routers' store singletons; no auth
env -> require_auth returns the local-dev stub).

Covers: contact + item CRUD, validation 400s, optimistic-version 409s, task toggle, link
attach/detach + idempotency, the deal-scoped read helpers, the deal-delete link cascade, and the
UNIFIED TIMELINE projection (audit + note + task interleave, newest-first sort, month grouping)."""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.crm as crm_router  # noqa: E402
import routers.deals as deals_router  # noqa: E402
import routers.jobs as jobs_router  # noqa: E402
from store import SQLiteCRMStore, SQLiteDealStore  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402

READY = {
    "routing": "ACQ", "deal_name": "Esplanade",
    "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
}


def _spec(deal_name="Esplanade", slug="esplanade", routing="ACQ"):
    return {"meta": {"deal_name": deal_name, "slug": slug, "routing": routing, "mode": "HITL"}}


@pytest.fixture
def client(monkeypatch):
    """Fresh in-memory CRM + deal + job stores wired into every router that reads them. The CRM
    store is patched on BOTH the crm router AND the deals router (the deal-delete cascade calls
    get_crm_store) so nothing leaks into the on-disk dev DB."""
    crm = SQLiteCRMStore(":memory:")
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(crm_router, "get_crm_store", lambda: crm)
    monkeypatch.setattr(crm_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(crm_router, "get_job_store", lambda: js)
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(deals_router, "get_job_store", lambda: js)
    monkeypatch.setattr(deals_router, "get_crm_store", lambda: crm)
    monkeypatch.setattr(jobs_router, "get_deal_store", lambda: ds)
    monkeypatch.setattr(jobs_router, "get_job_store", lambda: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    app = FastAPI()
    app.include_router(crm_router.router)
    app.include_router(deals_router.router)
    app.include_router(jobs_router.router)
    return crm, ds, js, TestClient(app)


def _make_deal(ds, name="Esplanade", slug="esplanade"):
    return ds.create(_spec(name, slug), owner="evan", now_iso="2026-07-01T00:00:00+00:00").deal_id


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def test_create_and_get_person(client):
    _crm, _ds, _js, c = client
    r = c.post("/api/contacts", json={"kind": "person", "full_name": "Jane Broker",
                                      "role": "broker", "emails": ["jane@x.com"]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "person" and body["name"] == "Jane Broker"
    assert body["role"] == "broker" and body["primary_email"] == "jane@x.com"
    assert body["version"] == 1 and body["owner"] == "evan@shieldstone.co"  # server identity
    got = c.get(f"/api/contacts/{body['contact_id']}").json()
    assert got["doc"]["full_name"] == "Jane Broker"


def test_create_company(client):
    _crm, _ds, _js, c = client
    r = c.post("/api/contacts", json={"kind": "company", "name": "Acme Capital",
                                      "company_type": "lender", "domain": "acme.example"})
    assert r.status_code == 200
    assert r.json()["kind"] == "company" and r.json()["name"] == "Acme Capital"


def test_contact_validation_400s(client):
    _crm, _ds, _js, c = client
    assert c.post("/api/contacts", json={"kind": "person"}).status_code == 400  # no full_name
    assert c.post("/api/contacts", json={"kind": "company"}).status_code == 400  # no name
    assert c.post("/api/contacts", json={"kind": "alien", "full_name": "x"}).status_code == 400
    assert c.post("/api/contacts", json={"kind": "person", "full_name": "x",
                                         "role": "wizard"}).status_code == 400


def test_contact_bad_role_rejected_but_valid_roles_pass(client):
    _crm, _ds, _js, c = client
    for role in ("broker", "seller", "lender", "bond_counsel", "issuer", "nonprofit_sponsor", "other"):
        r = c.post("/api/contacts", json={"kind": "person", "full_name": f"P {role}", "role": role})
        assert r.status_code == 200, f"role {role}: {r.text}"


def test_update_contact_version_flow(client):
    _crm, _ds, _js, c = client
    cid = c.post("/api/contacts", json={"kind": "person", "full_name": "Jane"}).json()["contact_id"]
    # stale/missing version -> 400
    assert c.put(f"/api/contacts/{cid}", json={"kind": "person", "full_name": "J2"}).status_code == 400
    # correct version -> 200, bumps to 2
    r = c.put(f"/api/contacts/{cid}", json={"kind": "person", "full_name": "J2", "version": 1})
    assert r.status_code == 200 and r.json()["version"] == 2 and r.json()["name"] == "J2"
    # replaying version 1 -> 409
    assert c.put(f"/api/contacts/{cid}",
                 json={"kind": "person", "full_name": "J3", "version": 1}).status_code == 409


def test_delete_contact_and_404(client):
    _crm, _ds, _js, c = client
    cid = c.post("/api/contacts", json={"kind": "person", "full_name": "Jane"}).json()["contact_id"]
    assert c.delete(f"/api/contacts/{cid}").json() == {"deleted": True, "contact_id": cid}
    assert c.get(f"/api/contacts/{cid}").status_code == 404
    assert c.delete(f"/api/contacts/{cid}").status_code == 404


# ---------------------------------------------------------------------------
# Items (tasks + notes) + toggle
# ---------------------------------------------------------------------------

def test_create_task_and_note(client):
    _crm, _ds, _js, c = client
    t = c.post("/api/items", json={"kind": "task", "title": "Call lender", "due_at": "2026-07-20"})
    assert t.status_code == 200 and t.json()["status"] == "open"
    n = c.post("/api/items", json={"kind": "note", "body": "Motivated seller"})
    assert n.status_code == 200 and n.json()["kind"] == "note"


def test_item_validation_400s(client):
    _crm, _ds, _js, c = client
    assert c.post("/api/items", json={"kind": "task"}).status_code == 400        # no title
    assert c.post("/api/items", json={"kind": "note"}).status_code == 400        # no body
    assert c.post("/api/items", json={"kind": "task", "title": "x",
                                      "status": "maybe"}).status_code == 400


def test_task_toggle_flips_status(client):
    _crm, _ds, _js, c = client
    tid = c.post("/api/items", json={"kind": "task", "title": "Call lender"}).json()["item_id"]
    r1 = c.post(f"/api/items/{tid}/toggle")
    assert r1.status_code == 200 and r1.json()["status"] == "done"
    r2 = c.post(f"/api/items/{tid}/toggle")
    assert r2.json()["status"] == "open"


def test_toggle_rejects_note(client):
    _crm, _ds, _js, c = client
    nid = c.post("/api/items", json={"kind": "note", "body": "x"}).json()["item_id"]
    assert c.post(f"/api/items/{nid}/toggle").status_code == 400


def test_toggle_unknown_404(client):
    _crm, _ds, _js, c = client
    assert c.post("/api/items/nope/toggle").status_code == 404


# ---------------------------------------------------------------------------
# Links + deal-scoped read helpers
# ---------------------------------------------------------------------------

def test_attach_contact_to_deal_and_list(client):
    crm, ds, _js, c = client
    deal_id = _make_deal(ds)
    cid = c.post("/api/contacts", json={"kind": "person", "full_name": "Jane",
                                        "role": "broker"}).json()["contact_id"]
    r = c.post("/api/links", json={"source_kind": "contact", "source_id": cid,
                                   "target_kind": "deal", "target_id": deal_id})
    assert r.status_code == 200
    link_id = r.json()["link_id"]
    # idempotent re-attach returns same link
    assert c.post("/api/links", json={"source_kind": "contact", "source_id": cid,
                                      "target_kind": "deal", "target_id": deal_id}).json()["link_id"] == link_id
    # deal-scoped read helper surfaces the contact WITH its link_id
    listed = c.get(f"/api/deals/{deal_id}/contacts").json()
    assert len(listed) == 1 and listed[0]["contact_id"] == cid and listed[0]["link_id"] == link_id
    # detach
    assert c.delete(f"/api/links/{link_id}").json()["detached"] is True
    assert c.get(f"/api/deals/{deal_id}/contacts").json() == []


def test_link_into_missing_endpoint_404(client):
    crm, ds, _js, c = client
    deal_id = _make_deal(ds)
    # unknown contact source
    assert c.post("/api/links", json={"source_kind": "contact", "source_id": "nope",
                                      "target_kind": "deal", "target_id": deal_id}).status_code == 404
    # unknown deal target
    cid = c.post("/api/contacts", json={"kind": "person", "full_name": "J"}).json()["contact_id"]
    assert c.post("/api/links", json={"source_kind": "contact", "source_id": cid,
                                      "target_kind": "deal", "target_id": "nope"}).status_code == 404


def test_link_bad_kind_400(client):
    crm, ds, _js, c = client
    deal_id = _make_deal(ds)
    cid = c.post("/api/contacts", json={"kind": "person", "full_name": "J"}).json()["contact_id"]
    assert c.post("/api/links", json={"source_kind": "wizard", "source_id": cid,
                                      "target_kind": "deal", "target_id": deal_id}).status_code == 400


def test_deal_items_filter_by_kind(client):
    crm, ds, _js, c = client
    deal_id = _make_deal(ds)
    tid = c.post("/api/items", json={"kind": "task", "title": "T"}).json()["item_id"]
    nid = c.post("/api/items", json={"kind": "note", "body": "N"}).json()["item_id"]
    c.post("/api/links", json={"source_kind": "task", "source_id": tid,
                               "target_kind": "deal", "target_id": deal_id})
    c.post("/api/links", json={"source_kind": "note", "source_id": nid,
                               "target_kind": "deal", "target_id": deal_id})
    assert len(c.get(f"/api/deals/{deal_id}/items").json()) == 2
    assert len(c.get(f"/api/deals/{deal_id}/items?kind=task").json()) == 1
    assert c.get(f"/api/deals/{deal_id}/items?kind=note").json()[0]["item_id"] == nid


def test_deal_scoped_helpers_404_on_unknown_deal(client):
    _crm, _ds, _js, c = client
    assert c.get("/api/deals/nope/contacts").status_code == 404
    assert c.get("/api/deals/nope/items").status_code == 404
    assert c.get("/api/deals/nope/timeline").status_code == 404


# ---------------------------------------------------------------------------
# Deal-delete link cascade (integration across crm + deals routers)
# ---------------------------------------------------------------------------

def test_deal_delete_cascades_crm_links(client):
    crm, ds, _js, c = client
    deal_id = _make_deal(ds)
    cid = c.post("/api/contacts", json={"kind": "person", "full_name": "Jane"}).json()["contact_id"]
    nid = c.post("/api/items", json={"kind": "note", "body": "N"}).json()["item_id"]
    c.post("/api/links", json={"source_kind": "contact", "source_id": cid,
                               "target_kind": "deal", "target_id": deal_id})
    c.post("/api/links", json={"source_kind": "note", "source_id": nid,
                               "target_kind": "deal", "target_id": deal_id})
    assert crm.list_links(target_kind="deal", target_id=deal_id)  # linked

    r = c.delete(f"/api/deals/{deal_id}")
    assert r.status_code == 200 and r.json()["deleted"] is True
    # links to the deal are gone...
    assert crm.list_links(target_kind="deal", target_id=deal_id) == []
    # ...but the contact + note records SURVIVE (they can belong to other deals)
    assert c.get(f"/api/contacts/{cid}").status_code == 200
    assert c.get(f"/api/items/{nid}").status_code == 200


# ---------------------------------------------------------------------------
# Unified timeline — the headline projection
# ---------------------------------------------------------------------------

def test_timeline_empty_deal(client):
    crm, ds, _js, c = client
    deal_id = _make_deal(ds)
    r = c.get(f"/api/deals/{deal_id}/timeline")
    assert r.status_code == 200
    body = r.json()
    assert body == {"deal_id": deal_id, "events": [], "groups": []}


def test_timeline_interleaves_audit_notes_tasks_newest_first(client):
    """A deal with a real run (audit events) PLUS a pinned note and task: the timeline merges all
    three sources into one feed, newest-first, grouped by month. The audit rows are never mutated."""
    crm, ds, js, c = client
    # A real job driven to CP-1 seeds the append-only audit trail on a fresh deal.
    jb = c.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert jb.status_code == 200, jb.text
    deal_id = jb.json()["deal_id"]

    # Pin a note (August) and a task (June) so month grouping has >1 bucket alongside the audit.
    nid = crm.create_item({"kind": "note", "body": "Site visit went well", "author": "evan"},
                          owner="evan", now_iso="2026-08-15T10:00:00+00:00").item_id
    tid = crm.create_item({"kind": "task", "title": "Order appraisal", "due_at": "2026-08-20"},
                          owner="evan", now_iso="2026-06-02T09:00:00+00:00").item_id
    crm.create_link("note", nid, "deal", deal_id, now_iso="2026-08-15T10:00:00+00:00")
    crm.create_link("task", tid, "deal", deal_id, now_iso="2026-06-02T09:00:00+00:00")

    body = c.get(f"/api/deals/{deal_id}/timeline").json()
    events = body["events"]
    sources = {e["source"] for e in events}
    assert sources == {"audit", "note", "task"}, sources
    # the note + task appear with their content
    note_ev = next(e for e in events if e["source"] == "note")
    assert note_ev["body"] == "Site visit went well" and note_ev["item_id"] == nid
    task_ev = next(e for e in events if e["source"] == "task")
    assert task_ev["status"] == "open" and task_ev["due_at"] == "2026-08-20"
    # newest-first: timestamps are non-increasing down the feed
    ts = [e["ts"] for e in events if e["ts"]]
    assert ts == sorted(ts, reverse=True)
    # the August note precedes the June task in the feed (newest first)
    idx = {e["id"]: i for i, e in enumerate(events)}
    assert idx[f"note:{nid}"] < idx[f"task:{tid}"]
    # month grouping: every event id lands in exactly one bucket, buckets follow feed order
    all_ids = [i for g in body["groups"] for i in g["ids"]]
    assert all_ids == [e["id"] for e in events]
    months = [g["month"] for g in body["groups"]]
    assert "August 2026" in months and "June 2026" in months
    # August comes before June (newest month first)
    assert months.index("August 2026") < months.index("June 2026")


def test_timeline_audit_is_read_only_view(client):
    """The timeline surfaces the runner's audit kinds unchanged (phase/llm_call/gate/...) and does
    not invent event kinds — it is a projection, not a second source of truth."""
    crm, ds, js, c = client
    jb = c.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    deal_id = jb.json()["deal_id"]
    events = c.get(f"/api/deals/{deal_id}/timeline").json()["events"]
    audit_kinds = {e["kind"] for e in events if e["source"] == "audit"}
    assert audit_kinds <= {"phase", "llm_call", "gate", "spec_mutation", "error"}
    # audit event ids are stable + namespaced (job_id + seq), so the frontend can key on them
    for e in events:
        if e["source"] == "audit":
            assert e["id"].startswith("audit:") and e["job_id"]
