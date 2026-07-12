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
from auth_dep import require_auth  # noqa: E402
from store import SQLiteDealStore  # noqa: E402
from jobs.contracts import JobStatus  # noqa: E402
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


# ---------------------------------------------------------------------------
# GET /api/deals/{deal_id}/audit — the readable audit trail (PRD C.5)
# ---------------------------------------------------------------------------

def test_audit_unknown_deal_404(client):
    _ds, _js, c = client
    assert c.get("/api/deals/nope/audit").status_code == 404


def test_audit_deal_with_no_jobs_empty(client):
    """A deal that never ran: {deal_id, jobs: []} — not a 404, not null."""
    ds, _js, c = client
    rec = ds.create(_spec("No Jobs", "no-jobs", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00")
    r = c.get(f"/api/deals/{rec.deal_id}/audit")
    assert r.status_code == 200
    assert r.json() == {"deal_id": rec.deal_id, "jobs": []}


def test_audit_populated_after_driven_job(client):
    """Drive a real job to CP-1 through the jobs API; the audit endpoint surfaces the runner's
    append-only trail in insertion order — Wave 0 first, the five llm_call slices, the gate
    verdict, the spec_mutation persist, and the CP-1 stop last. Only kinds the store already
    records appear ({phase, llm_call, gate, spec_mutation, error})."""
    _ds, _js, c = client
    r = c.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    jb = r.json()
    assert jb["status"] == "awaiting_cp1"

    a = c.get(f"/api/deals/{jb['deal_id']}/audit")
    assert a.status_code == 200
    body = a.json()
    assert body["deal_id"] == jb["deal_id"]
    assert len(body["jobs"]) == 1
    job = body["jobs"][0]
    assert job["job_id"] == jb["job_id"]
    assert job["status"] == "awaiting_cp1"
    assert job["created_at"]

    events = job["events"]
    assert len(events) >= 8  # wave0 + 5 slices + gate + spec_mutation + cp1
    # exact event shape: kind + message + ts (detail optional)
    for ev in events:
        assert set(ev) - {"detail"} == {"kind", "message", "ts"}
        assert ev["ts"]
    # closed kind vocabulary — the endpoint exposes what the store records, nothing new
    assert {ev["kind"] for ev in events} <= {"phase", "llm_call", "gate", "spec_mutation", "error"}
    # insertion order: Wave 0 opens the trail, the CP-1 HITL stop closes it
    assert events[0]["kind"] == "phase"
    assert "Wave 0" in events[0]["message"]
    assert events[-1]["kind"] == "phase"
    assert "CP-1" in events[-1]["message"]
    # the five Wave-1 slices appear as llm_call events, in phase order
    llm_msgs = [ev["message"] for ev in events if ev["kind"] == "llm_call"]
    assert len(llm_msgs) == 5
    assert "wave1_t12" in llm_msgs[0] and "wave1_marketdata" in llm_msgs[-1]
    # the gate event carries its detail payload (the GateSummary dict)
    gate_evs = [ev for ev in events if ev["kind"] == "gate"]
    assert gate_evs and gate_evs[0]["detail"]["ok"] is True


def test_audit_multiple_jobs_newest_first(client):
    """Two jobs on one deal: newest job first (updated_at DESC), each with its OWN event list
    in insertion (seq) order."""
    ds, js, c = client
    rec = ds.create(_spec("Two Jobs", "two-jobs", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00")
    older = js.create_job(deal_id=rec.deal_id, routing="ACQ", owner="evan",
                          now_iso="2026-06-10T01:00:00+00:00")
    js.append_audit(older.job_id, "phase", "older first", ts="2026-06-10T01:00:01+00:00")
    js.append_audit(older.job_id, "error", "older failed", detail={"why": "test"},
                    ts="2026-06-10T01:00:02+00:00")
    newer = js.create_job(deal_id=rec.deal_id, routing="ACQ", owner="evan",
                          now_iso="2026-06-10T02:00:00+00:00")
    js.append_audit(newer.job_id, "phase", "newer first", ts="2026-06-10T02:00:01+00:00")

    body = c.get(f"/api/deals/{rec.deal_id}/audit").json()
    assert [j["job_id"] for j in body["jobs"]] == [newer.job_id, older.job_id]
    assert [e["message"] for e in body["jobs"][1]["events"]] == ["older first", "older failed"]
    assert body["jobs"][1]["events"][1]["detail"] == {"why": "test"}
    # an event with an EMPTY detail omits the key (the shape's `detail?`)
    assert "detail" not in body["jobs"][1]["events"][0]
    assert [e["message"] for e in body["jobs"][0]["events"]] == ["newer first"]


# ---------------------------------------------------------------------------
# POST /api/deals/{deal_id}/archive + /unarchive — soft hide / restore
# ---------------------------------------------------------------------------

def test_archive_hides_from_default_list(client):
    """Archived deals disappear from the DEFAULT list; ?status=archived passes through the store
    untouched; ?include_archived=1 (or true) keeps them in the unfiltered list."""
    ds, _js, c = client
    a = ds.create(_spec("A", "a", "ACQ"), owner="evan",
                  now_iso="2026-06-10T00:00:00+00:00", status="computed")
    ds.create(_spec("B", "b", "ACQ"), owner="evan",
              now_iso="2026-06-10T00:00:01+00:00", status="draft")

    r = c.post(f"/api/deals/{a.deal_id}/archive")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "archived"
    assert body["version"] == 2  # ds.put bumped (a real write, spec stays canonical)

    # hidden from the default list
    assert {d["deal_name"] for d in c.get("/api/deals").json()} == {"B"}
    # explicit status filter passes through untouched
    assert {d["deal_name"] for d in c.get("/api/deals?status=archived").json()} == {"A"}
    # opt back in with the flag ("1" and "true" both accepted)
    assert {d["deal_name"] for d in c.get("/api/deals?include_archived=1").json()} == {"A", "B"}
    assert {d["deal_name"] for d in c.get("/api/deals?include_archived=true").json()} == {"A", "B"}
    # the detail view still resolves an archived deal (soft hide, not delete)
    assert c.get(f"/api/deals/{a.deal_id}").status_code == 200


def test_archive_idempotent_no_version_bump(client):
    """Archiving an already-archived deal returns the current view WITHOUT a version bump, and
    the stashed pre-archive status keeps the ORIGINAL value (never 'archived')."""
    ds, _js, c = client
    rec = ds.create(_spec("A", "a", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00", status="computed")
    first = c.post(f"/api/deals/{rec.deal_id}/archive").json()
    second = c.post(f"/api/deals/{rec.deal_id}/archive").json()
    assert first["version"] == 2
    assert second["version"] == 2  # no bump on the idempotent repeat
    assert second["status"] == "archived"
    stored = ds.get(rec.deal_id)
    assert stored.version == 2
    assert stored.spec["meta"]["pre_archive_status"] == "computed"


def test_unarchive_restores_stashed_status(client):
    """Unarchive restores the stashed pre-archive status (a NON-draft one here: gate_failed) and
    pops the stash off the spec."""
    ds, _js, c = client
    rec = ds.create(_spec("GF", "gf", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00", status="gate_failed")
    c.post(f"/api/deals/{rec.deal_id}/archive")
    assert ds.get(rec.deal_id).spec["meta"]["pre_archive_status"] == "gate_failed"

    r = c.post(f"/api/deals/{rec.deal_id}/unarchive")
    assert r.status_code == 200
    assert r.json()["status"] == "gate_failed"
    # the stash is consumed (popped), not left to go stale on the spec
    assert "pre_archive_status" not in ds.get(rec.deal_id).spec["meta"]


def test_unarchive_fallback_and_idempotency(client):
    """No stash (deal born archived): fallback restores 'computed' when the spec carries a
    non-empty headline_metrics, else 'draft'. Unarchiving a non-archived deal is a no-op."""
    ds, _js, c = client
    computed = ds.create(_spec("C", "c", "ACQ", headline_metrics={"irr": 0.2}), owner="evan",
                         now_iso="2026-06-10T00:00:00+00:00", status="archived")
    draft = ds.create(_spec("D", "d", "ACQ"), owner="evan",
                      now_iso="2026-06-10T00:00:01+00:00", status="archived")
    assert c.post(f"/api/deals/{computed.deal_id}/unarchive").json()["status"] == "computed"
    assert c.post(f"/api/deals/{draft.deal_id}/unarchive").json()["status"] == "draft"
    # idempotent: unarchiving a deal that is not archived returns the view as-is (no version bump)
    again = c.post(f"/api/deals/{draft.deal_id}/unarchive").json()
    assert again["status"] == "draft"
    assert again["version"] == ds.get(draft.deal_id).version == 2


def test_archive_unarchive_delete_unknown_id_404(client):
    _ds, _js, c = client
    assert c.post("/api/deals/nope/archive").status_code == 404
    assert c.post("/api/deals/nope/unarchive").status_code == 404
    assert c.delete("/api/deals/nope").status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/deals/{deal_id} — hard delete + running-job guard
# ---------------------------------------------------------------------------

def test_delete_removes_deal_and_job_rows(client):
    """Delete a deal whose job is human-paused at CP-1 (awaiting_cp1 never blocks): the deal
    detail + audit both 404 afterwards and the job rows are gone (delete_for_deal cascade)."""
    _ds, js, c = client
    r = c.post("/api/jobs", json={"intake_summary": READY, "owner": "evan"})
    assert r.status_code == 200, r.text
    deal_id = r.json()["deal_id"]
    assert r.json()["status"] == "awaiting_cp1"  # paused, NOT running — must not block
    assert js.list_jobs(deal_id=deal_id)

    d = c.delete(f"/api/deals/{deal_id}")
    assert d.status_code == 200
    assert d.json() == {"deleted": True, "deal_id": deal_id}
    assert c.get(f"/api/deals/{deal_id}").status_code == 404
    assert c.get(f"/api/deals/{deal_id}/audit").status_code == 404
    assert js.list_jobs(deal_id=deal_id) == []


def test_delete_while_job_running_409(client):
    """A deal whose NEWEST job is actively running (walked to ANALYZING via legal transitions)
    refuses to delete with 409 until the job is cancelled; nothing is removed by the refusal."""
    ds, js, c = client
    rec = ds.create(_spec("Busy", "busy", "ACQ"), owner="evan",
                    now_iso="2026-06-10T00:00:00+00:00")
    job = js.create_job(deal_id=rec.deal_id, routing="ACQ", owner="evan",
                        now_iso="2026-06-10T00:00:01+00:00")
    # legal walk: SUBMITTED -> ROUTING -> ANALYZING (a running state)
    js.transition(job.job_id, JobStatus.ROUTING, "2026-06-10T00:00:02+00:00")
    js.transition(job.job_id, JobStatus.ANALYZING, "2026-06-10T00:00:03+00:00")

    r = c.delete(f"/api/deals/{rec.deal_id}")
    assert r.status_code == 409
    assert "cancel it first" in r.json()["detail"]
    # the refusal deleted nothing
    assert c.get(f"/api/deals/{rec.deal_id}").status_code == 200
    assert js.list_jobs(deal_id=rec.deal_id)

    # cancel the job (legal from ANALYZING) -> the delete now goes through
    js.transition(job.job_id, JobStatus.CANCELLED, "2026-06-10T00:00:04+00:00")
    r = c.delete(f"/api/deals/{rec.deal_id}")
    assert r.status_code == 200
    assert js.list_jobs(deal_id=rec.deal_id) == []


# ---------------------------------------------------------------------------
# Owner derivation — server identity wins over the request body (Track A's change;
# this file only TESTS the jobs router, it does not own it)
# ---------------------------------------------------------------------------

def test_job_submit_derives_owner_from_authenticated_user(client):
    """POST /api/jobs with an authenticated user must set the created deal's owner from the
    SERVER-side identity (lowercased email), not the client-supplied req.owner — a client must
    not be able to file deals as someone else."""
    ds, _js, c = client
    c.app.dependency_overrides[require_auth] = lambda: {"email": "CHARLES@Example.com"}
    try:
        r = c.post("/api/jobs", json={"intake_summary": READY, "owner": "mallory@evil.example"})
        assert r.status_code == 200, r.text
        deal = ds.get(r.json()["deal_id"])
        assert deal.owner == "charles@example.com"
    finally:
        c.app.dependency_overrides.pop(require_auth, None)
