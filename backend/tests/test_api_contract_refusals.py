"""API contract tests for the untested High fail-closed paths in the app test gap map
(docs/research/2026-11-04-app-fail-closed-test-gap-map.md, rows B12 B13 B22 B23 B25 B26 B32 B33
B42 B44 B46 B47 B55 B64 B68 B89).

Rules: synthetic fixtures only, in-memory stores, no network, no LLM (memo generators are faked),
no application code touched. Each test pins the exact status code and a key part of the error body.

Where the app does NOT refuse today, the test is written as the correct (refusing) behaviour and
marked xfail(strict=True) with the file and line of the gap. Strict xfail means the test goes red
the day someone fixes the gap, which is the signal to remove the marker.
"""
import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("starlette")
pytest.importorskip("openpyxl")
import openpyxl  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import routers.deals as deals_router  # noqa: E402
import routers.export_excel as export_router  # noqa: E402
import routers.jobs as jobs_router  # noqa: E402
import routers.memo as memo_router  # noqa: E402
from routers.recalc import router as recalc_router  # noqa: E402
from jobs.analysts import StubAnalysts  # noqa: E402
from jobs.job_store import SQLiteJobStore  # noqa: E402
from store import SQLiteDealStore  # noqa: E402

NOW = "2026-11-04T12:00:00Z"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

ACQ_BODY = {
    "bridge_loan": 20_000_000, "bridge_rate": 0.07, "bridge_io_years": 2,
    "refi_loan": 25_000_000, "refi_rate": 0.06, "refi_io_years": 2,
    "total_equity": 10_000_000,
    "noi_series": [1_500_000, 1_800_000, 2_100_000, 2_300_000, 2_400_000, 2_500_000, 2_600_000, 2_700_000],
}


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

class FakeMemoGenerator:
    def __init__(self):
        self.calls = []

    def generate(self, inputs, model_results):
        self.calls.append((inputs, model_results))
        return "## Synthetic memo body"


SYNTH_JWT_SECRET = "contract-test-secret-0123456789abcdef0123456789"
_REAL_DB_MSG = "REAL DATABASE TOUCHED: a contract test reached a default store singleton"


def _real_db_forbidden(*_a, **_k):
    raise AssertionError(_REAL_DB_MSG)


@pytest.fixture
def synthetic_env(monkeypatch, tmp_path):
    """Pin every host setting these tests depend on, so the result never depends on the machine.

    Auth is pinned OFF (local-dev pass-through, stub user) and the allowlist is emptied. The database
    path points at a nonexistent file under tmp_path, and every default-store accessor raises, so any
    code path that would reach a configured host database fails loudly instead of quietly.
    """
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("DREAM_STRICT_OWNERSHIP", raising=False)
    monkeypatch.setattr("auth_dep.ALLOWED_EMAILS", set())
    guarded = tmp_path / "must_never_be_created.db"
    monkeypatch.setenv("DREAM_DB_PATH", str(guarded))
    import store.deal_store as _ds_mod
    import store.user_store as _us_mod
    import jobs.job_store as _js_mod
    import routers.auth_login as _login_mod
    import store as _store_pkg
    for mod, name in ((_ds_mod, "get_deal_store"), (_us_mod, "get_user_store"), (_js_mod, "get_job_store"),
                      (_store_pkg, "get_deal_store"), (_login_mod, "get_user_store"),
                      (_login_mod, "get_users")):
        monkeypatch.setattr(mod, name, _real_db_forbidden, raising=False)
    yield guarded
    assert not guarded.exists(), _REAL_DB_MSG


@pytest.fixture
def stores(monkeypatch, synthetic_env):
    """Fresh in-memory deal + job stores wired into every router singleton."""
    ds = SQLiteDealStore(":memory:")
    js = SQLiteJobStore(":memory:")
    fake = FakeMemoGenerator()
    for mod in (deals_router, jobs_router, memo_router, export_router):
        monkeypatch.setattr(mod, "get_deal_store", lambda ds=ds: ds, raising=False)
    for mod in (deals_router, jobs_router):
        monkeypatch.setattr(mod, "get_job_store", lambda js=js: js)
    monkeypatch.setattr(jobs_router, "get_analysts", lambda: StubAnalysts())
    monkeypatch.setattr(memo_router, "get_memo_generator", lambda: fake)
    return ds, js, fake


@pytest.fixture
def client(stores):
    app = FastAPI()
    for r in (recalc_router, deals_router.router, memo_router.router, export_router.router):
        app.include_router(r)
    return TestClient(app)


def _spec(status_hint="computed", hm=None, identity_ok=True, slug="synthetic-heights"):
    return {
        "meta": {"deal_name": "Synthetic Heights", "slug": slug, "routing": "ACQ", "mode": "HITL",
                 "deal_identity": {"match": identity_ok, "reasons": [] if identity_ok else ["synthetic carryover"]}},
        "qa": {},
        "cells": [{"cell": "B10", "value": 34000000, "type": "currency", "source": "synthetic", "phase": 3}],
        "headline_metrics": {"irr": 0.2, "equity_multiple": 2.5} if hm is None else hm,
    }


def _mini_model_bytes():
    wb = openpyxl.Workbook()
    pf = wb.active
    pf.title = "Pro Forma"
    pf["B2"] = "Synthetic Heights"
    pf["B6"] = 240
    pf["B10"] = 0
    log = wb.create_sheet("Claude Log")
    log["A1"] = "Timestamp"; log["B1"] = "Phase"; log["C1"] = "Changed"
    log["D1"] = "Discovered"; log["E1"] = "Pending"
    for row in range(2, 6):
        log.cell(row=row, column=1, value=f"row{row}")
    log.cell(row=6, column=5, value="-")
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# B12 — every real router is mounted behind require_auth in main.app
# ---------------------------------------------------------------------------

_OPEN_PATHS = {"/api/health", "/api/auth/login"}


def _real_api_routes():
    import main
    out = []
    for r in main.app.routes:
        path = getattr(r, "path", "")
        methods = getattr(r, "methods", None) or set()
        if not path.startswith("/api") or path in _OPEN_PATHS:
            continue
        for m in sorted(methods - {"HEAD", "OPTIONS"}):
            out.append((m, path.replace("{deal_id}", "d1").replace("{job_id}", "j1")
                        .replace("{contact_id}", "c1").replace("{item_id}", "i1")
                        .replace("{link_id}", "l1").replace("{run_id}", "run-failed")))
    return out


@pytest.fixture
def synthetic_users(monkeypatch, synthetic_env):
    """In-memory synthetic user store patched in as login's get_users (never the host database)."""
    from store.user_store import SQLiteUserStore
    from password import hash_password
    import routers.auth_login as login_mod
    us = SQLiteUserStore(":memory:")
    us.create_user("synthetic-user", "synthetic@example.com", hash_password("synthetic-pass-123"), NOW)
    monkeypatch.setattr(login_mod, "get_users", lambda: us)
    monkeypatch.setattr(login_mod, "ALLOWED_EMAILS", set())
    return us


@pytest.fixture
def auth_on_main(monkeypatch, synthetic_env, synthetic_users):
    monkeypatch.setenv("AUTH_JWT_SECRET", SYNTH_JWT_SECRET)
    import main
    return TestClient(main.app)


def test_real_app_exposes_a_meaningful_number_of_gated_routes():
    # Guards the sweep below against silently testing nothing.
    routes = _real_api_routes()
    assert len(routes) >= 40
    assert ("POST", "/api/recalc") in routes
    assert ("GET", "/api/deals") in routes


@pytest.mark.parametrize("method,path", _real_api_routes() if os.path.exists(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")) else [])
def test_b12_every_real_route_without_token_is_401(auth_on_main, method, path):
    r = auth_on_main.request(method, path)
    assert r.status_code == 401, f"{method} {path} answered {r.status_code} with no token"
    assert r.json()["detail"] == "Authentication required"


def test_b12_open_paths_are_only_health_and_login(auth_on_main):
    assert auth_on_main.get("/api/health").status_code == 200
    # login is open by design: a bad login is refused by the login logic (401/422), not by the gate.
    r = auth_on_main.post("/api/auth/login", json={"username": "x", "password": "y"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid username or password"


# ---------------------------------------------------------------------------
# B13 — strict ownership answers 404 on another owner's deal
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method,suffix", [("POST", "/archive"), ("POST", "/unarchive"), ("DELETE", "")])
def test_b13_strict_ownership_other_owner_404(client, stores, monkeypatch, method, suffix):
    ds, _js, _ = stores
    rec = ds.create(_spec(), owner="someone-else@example.com", now_iso=NOW, status="computed")
    monkeypatch.setenv("DREAM_STRICT_OWNERSHIP", "1")
    r = client.request(method, f"/api/deals/{rec.deal_id}{suffix}")
    assert r.status_code == 404
    assert r.json()["detail"] == "deal not found"
    # and the deal is untouched
    assert ds.get(rec.deal_id).status == "computed"


def test_b13_permissive_mode_lets_other_owner_archive(client, stores, monkeypatch):
    ds, _js, _ = stores
    rec = ds.create(_spec(), owner="someone-else@example.com", now_iso=NOW, status="computed")
    monkeypatch.delenv("DREAM_STRICT_OWNERSHIP", raising=False)
    assert client.post(f"/api/deals/{rec.deal_id}/archive").status_code == 200


# ---------------------------------------------------------------------------
# B64 — gate_failed deals must not hand out headline numbers (HIGH)
# ---------------------------------------------------------------------------

GATE_FAILED_REASON = ("deals.py:19-42 and 283-285 return spec.headline_metrics whatever the status; "
                      "runner.py:200 keeps the spec of a gate_failed deal for forensics. Gap B64.")


@pytest.mark.xfail(strict=True, reason=GATE_FAILED_REASON)
def test_b64_list_hides_headline_metrics_for_gate_failed(client, stores):
    ds, _js, _ = stores
    ds.create(_spec(hm={"irr": 0.2}), owner="a@example.com", now_iso=NOW, status="gate_failed")
    rows = client.get("/api/deals").json()
    assert rows[0]["status"] == "gate_failed"
    assert rows[0]["headline_metrics"] == {}


@pytest.mark.xfail(strict=True, reason=GATE_FAILED_REASON)
def test_b64_detail_hides_headline_metrics_for_gate_failed(client, stores):
    ds, _js, _ = stores
    rec = ds.create(_spec(hm={"irr": 0.2}), owner="a@example.com", now_iso=NOW, status="gate_failed")
    body = client.get(f"/api/deals/{rec.deal_id}").json()
    assert body["status"] == "gate_failed"
    assert body["headline_metrics"] == {}


def test_b64_computed_deal_still_returns_headline_metrics(client, stores):
    """Control: the fix for B64 must not blank a healthy deal."""
    ds, _js, _ = stores
    rec = ds.create(_spec(hm={"irr": 0.2}), owner="a@example.com", now_iso=NOW, status="computed")
    assert client.get(f"/api/deals/{rec.deal_id}").json()["headline_metrics"] == {"irr": 0.2}


# ---------------------------------------------------------------------------
# B68 — memo for a gate_failed deal (HIGH)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason=(
    "routers/memo.py:173-179 only checks headline_metrics is non-empty, so a gate_failed deal "
    "gets a memo written over numbers that failed a RED gate. Gap B68."))
def test_b68_memo_refused_for_gate_failed_deal(client, stores):
    ds, _js, fake = stores
    rec = ds.create(_spec(hm={"irr": 0.2}), owner="a@example.com", now_iso=NOW, status="gate_failed")
    r = client.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 409
    assert fake.calls == []


def test_b68_memo_with_no_headline_is_409_and_calls_no_generator(client, stores):
    ds, _js, fake = stores
    rec = ds.create(_spec(hm={}), owner="a@example.com", now_iso=NOW, status="draft")
    r = client.post(f"/api/deals/{rec.deal_id}/memo")
    assert r.status_code == 409
    assert "no computed spec" in r.json()["detail"]
    assert fake.calls == []


# ---------------------------------------------------------------------------
# B25 / B23 / B26 / B22 — calc endpoints and invented numbers (HIGH)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("noi", [-5, 0])
@pytest.mark.xfail(strict=True, reason=(
    "routers/recalc.py:123-130 (EFBUnderwriteRequest.stabilized_noi has no bound) and 146-152: "
    "/api/underwrite/efb returns HTTP 200 with a bond amount for NOI <= 0 (-5 gives -71.79). "
    "The job path blocks this at jobs/wave0.py:188. Gap B25."))
def test_b25_efb_non_positive_noi_is_refused(client, noi):
    r = client.post("/api/underwrite/efb", json={"stabilized_noi": noi})
    assert r.status_code == 422


def test_b25_efb_target_dscr_zero_is_422(client):
    r = client.post("/api/underwrite/efb", json={"stabilized_noi": 3_000_000, "target_dscr": 0})
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str) and r.json()["detail"]


def test_b25_efb_positive_noi_returns_positive_bond(client):
    r = client.post("/api/underwrite/efb", json={"stabilized_noi": 3_000_000})
    assert r.status_code == 200
    assert r.json()["headline_metrics"]["bond_amount"] > 0


@pytest.mark.xfail(strict=True, reason=(
    "routers/recalc.py:43-52 and 73-77: ACQRecalcRequest.total_equity has no bound, so 0 returns "
    "HTTP 200 with equity_multiple 0.0 and coc 0.0 instead of a refusal or blanks. Gap B23."))
def test_b23_recalc_zero_equity_is_refused_or_blank(client):
    body = dict(ACQ_BODY, total_equity=0)
    r = client.post("/api/recalc", json=body)
    if r.status_code == 200:
        hm = r.json()["headline_metrics"]
        assert hm.get("equity_multiple") is None, "a 0.0x multiple is an invented number"
    else:
        assert r.status_code == 422


def test_b23_recalc_good_inputs_return_numbers(client):
    r = client.post("/api/recalc", json=ACQ_BODY)
    assert r.status_code == 200
    assert r.json()["headline_metrics"]["equity_multiple"] > 0


def test_recalc_missing_required_field_is_422_with_field_name(client):
    body = {k: v for k, v in ACQ_BODY.items() if k != "refi_loan"}
    r = client.post("/api/recalc", json=body)
    assert r.status_code == 422
    assert any("refi_loan" in str(e.get("loc")) for e in r.json()["detail"])


def test_recalc_sale_year_zero_is_422(client):
    r = client.post("/api/recalc", json=dict(ACQ_BODY, sale_year=0))
    assert r.status_code == 422
    assert any("sale_year" in str(e.get("loc")) for e in r.json()["detail"])


@pytest.mark.xfail(strict=True, reason=(
    "routers/recalc.py:76-77: an engine exception is returned as str(e), so an empty noi_series "
    "gives the raw Python text 'list index out of range' as the error body. Gap B22."))
def test_b22_empty_noi_series_gives_plain_message_not_exception_text(client):
    r = client.post("/api/recalc", json=dict(ACQ_BODY, noi_series=[]))
    assert r.status_code == 422
    assert "list index out of range" not in str(r.json()["detail"])


def test_b22_empty_noi_series_is_at_least_refused_with_422(client):
    r = client.post("/api/recalc", json=dict(ACQ_BODY, noi_series=[]))
    assert r.status_code == 422


def test_b22_zero_refi_amort_years_is_422(client):
    r = client.post("/api/recalc", json=dict(ACQ_BODY, refi_amort_years=0))
    assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason=(
    "routers/recalc.py:82-99 and 103-114: AgencySizingRequest.stabilized_value has no bound, "
    "so agency sizing with a value of 0 is not refused. Gap B26 (unprobed by the map)."))
def test_b26_agency_sizing_zero_value_is_refused(client):
    r = client.post("/api/recalc/agency-sizing", json={
        "stabilized_noi": 2_000_000, "stabilized_value": 0, "refi_rate": 0.06})
    assert r.status_code == 422


def test_b26_agency_sizing_missing_field_is_422(client):
    r = client.post("/api/recalc/agency-sizing", json={"stabilized_noi": 2_000_000})
    assert r.status_code == 422
    assert any("stabilized_value" in str(e.get("loc")) for e in r.json()["detail"])


def test_b26_exit_cap_calc_missing_field_is_422(client):
    r = client.post("/api/recalc/exit-cap", json={})
    assert r.status_code == 422
    assert any("going_in_cap" in str(e.get("loc")) for e in r.json()["detail"])


# ---------------------------------------------------------------------------
# B32 / B33 — /api/validate and /api/agent/memo in the real app
# ---------------------------------------------------------------------------

@pytest.fixture
def real_app_open(monkeypatch, synthetic_env):
    """Real main.app with auth off (local-dev mode) and a faked memo generator. No network."""
    import main
    return main, TestClient(main.app)


@pytest.mark.xfail(strict=True, reason=(
    "main.py:336-348 with models.py:31-35: /api/validate with an empty body validates an invented "
    "default deal (New Deal, 186 units, $1,200 rents) and returns 200 instead of 422. Gap B32."))
def test_b32_validate_empty_body_is_422(real_app_open):
    _main, c = real_app_open
    assert c.post("/api/validate", json={}).status_code == 422


def test_b32_validate_non_object_body_is_422(real_app_open):
    _main, c = real_app_open
    r = c.post("/api/validate", json=[1, 2, 3])
    assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason=(
    "main.py:437-448: /api/agent/memo writes a memo from model_results sent by the client, not "
    "from the stored engine output, so it accepts numbers that no engine produced. Gap B33."))
def test_b33_agent_memo_rejects_client_supplied_model_results(real_app_open, monkeypatch):
    main, c = real_app_open

    class _Gen:
        def generate(self, inputs, model_results):
            return "memo"

        def generate_executive_summary(self, inputs, model_results):
            return "summary"

    monkeypatch.setattr(main, "get_memo_generator", lambda: _Gen())
    r = c.post("/api/agent/memo", json={"inputs": {}, "model_results": {"irr": 9.99}})
    assert r.status_code in (400, 409, 410, 422)


def test_b33_agent_memo_generator_error_is_422_with_message(real_app_open, monkeypatch):
    main, c = real_app_open

    class _Boom:
        def generate(self, inputs, model_results):
            raise RuntimeError("synthetic generator failure")

    monkeypatch.setattr(main, "get_memo_generator", lambda: _Boom())
    r = c.post("/api/agent/memo", json={"inputs": {}, "model_results": {}})
    assert r.status_code == 422
    assert "synthetic generator failure" in r.json()["detail"]


# ---------------------------------------------------------------------------
# B42 / B44 / B46 / B47 — export and reconcile refusals (HIGH and Med)
# ---------------------------------------------------------------------------

def _post_export(c, deal_id, download, template=None, name="mini.xlsx"):
    files = {"template": (name, _mini_model_bytes() if template is None else template, XLSX)}
    return c.post(f"/api/deals/{deal_id}/export", files=files, data={"download": download})


def test_b46_export_download_true_with_identity_mismatch_returns_json_not_a_file(client, stores):
    ds, _js, _ = stores
    rec = ds.create(_spec(identity_ok=False), owner="a@example.com", now_iso=NOW, status="computed")
    r = _post_export(client, rec.deal_id, "true")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert not r.content.startswith(b"PK")
    body = r.json()
    assert body["identity_blocked"] is True
    assert body["ok"] is False


def test_b46_export_download_true_with_matching_identity_streams_xlsx(client, stores):
    """Control for B46: the same call with a matching identity does stream a workbook."""
    ds, _js, _ = stores
    rec = ds.create(_spec(identity_ok=True), owner="a@example.com", now_iso=NOW, status="computed")
    r = _post_export(client, rec.deal_id, "true")
    assert r.status_code == 200
    assert r.content[:2] == b"PK"


def _draft_bytes(client, deal_id):
    return _post_export(client, deal_id, "true").content


def test_b42_reconcile_identity_mismatch_default_is_409(client, stores):
    ds, _js, _ = stores
    ok = ds.create(_spec(identity_ok=True), owner="a@example.com", now_iso=NOW, status="computed")
    draft = _draft_bytes(client, ok.deal_id)
    bad = ds.create(_spec(identity_ok=False, slug="other-deal"), owner="a@example.com", now_iso=NOW,
                    status="computed")
    r = client.post(f"/api/deals/{bad.deal_id}/reconcile", files={"draft": ("d.xlsx", draft, XLSX)})
    assert r.status_code == 409
    assert r.json()["detail"]


@pytest.mark.xfail(strict=True, reason=(
    "routers/export_excel.py:128: require_identity_match is a client form field. Sending false "
    "skips the wrong-deal check, so a mismatched deal reconciles instead of returning 409. Gap B42."))
def test_b42_reconcile_client_cannot_turn_off_identity_check(client, stores):
    ds, _js, _ = stores
    ok = ds.create(_spec(identity_ok=True), owner="a@example.com", now_iso=NOW, status="computed")
    draft = _draft_bytes(client, ok.deal_id)
    bad = ds.create(_spec(identity_ok=False, slug="other-deal"), owner="a@example.com", now_iso=NOW,
                    status="computed")
    r = client.post(f"/api/deals/{bad.deal_id}/reconcile",
                    files={"draft": ("d.xlsx", draft, XLSX)}, data={"require_identity_match": "false"})
    assert r.status_code == 409


def test_b47_reconcile_deal_without_headline_is_409(client, stores):
    ds, _js, _ = stores
    rec = ds.create(_spec(hm={}), owner="a@example.com", now_iso=NOW, status="draft")
    r = client.post(f"/api/deals/{rec.deal_id}/reconcile",
                    files={"draft": ("d.xlsx", _mini_model_bytes(), XLSX)})
    assert r.status_code == 409
    assert "no headline_metrics" in r.json()["detail"]


@pytest.mark.parametrize("route,field", [("export", "template"), ("reconcile", "draft")])
def test_b44_xlsx_named_text_bytes_is_422_not_500(client, stores, route, field):
    ds, _js, _ = stores
    rec = ds.create(_spec(), owner="a@example.com", now_iso=NOW, status="computed")
    r = client.post(f"/api/deals/{rec.deal_id}/{route}",
                    files={field: ("fake.xlsx", b"this is plain text, not a workbook", XLSX)})
    assert r.status_code == 422
    assert isinstance(r.json()["detail"], str) and r.json()["detail"]


def test_export_missing_file_part_is_422_with_field_name(client, stores):
    ds, _js, _ = stores
    rec = ds.create(_spec(), owner="a@example.com", now_iso=NOW, status="computed")
    r = client.post(f"/api/deals/{rec.deal_id}/export", data={"download": "false"})
    assert r.status_code == 422
    assert any("template" in str(e.get("loc")) for e in r.json()["detail"])


# ---------------------------------------------------------------------------
# B55 — wave 0 accepts nonsense ACQ inputs (HIGH, unprobed by the map)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason=(
    "jobs/wave0.py:129 checks ACQ critical inputs only for None or empty string, so exit_cap 0 "
    "and a negative purchase price pass wave 0 as present. Gap B55."))
@pytest.mark.parametrize("field,value", [("exit_cap", 0), ("purchase_price", -1)])
def test_b55_wave0_treats_non_positive_acq_input_as_missing(field, value):
    from jobs import wave0
    summary = {"critical_inputs": {"purchase_price": 30_000_000, "hold_years": 5, "exit_cap": 0.06}}
    summary["critical_inputs"][field] = value
    ci = wave0._extract_critical_inputs(summary)
    assert field in ci.missing()


# ---------------------------------------------------------------------------
# B89 — run status view: a failed or in-progress run carrying values (HIGH)
# ---------------------------------------------------------------------------

def _run_with_values(status):
    return {
        "run_id": "run-synthetic", "synthetic": True, "deal_label": "Synthetic", "status": status,
        "engine_commit": "c1", "current_engine_commit": "c1",
        "inputs_hash": "h1", "current_inputs_hash": "h1",
        "gates": [{"id": "g1", "name": "Gate", "status": "green", "detail": "ok"}],
        "evidence": [{"name": "e", "path": "p", "sha256": "0" * 64, "state": "ok"}],
        "holds": [],
        "headline": [{"key": "irr", "label": "IRR", "value": 0.31}],
    }


@pytest.mark.parametrize("status,state", [("failed", "failed"), ("synthesizing", "in_progress")])
@pytest.mark.xfail(strict=True, reason=(
    "run_status/view.py:106: values_are_diagnostic is True only for blocked and stale, so a failed "
    "or in-progress run that carries headline values passes them through as if they were results. "
    "Gap B89."))
def test_b89_failed_or_in_progress_run_with_values_is_marked_diagnostic(status, state):
    from run_status.view import build_view
    view = build_view(_run_with_values(status))
    assert view["display_state"] == state
    assert view["values_are_diagnostic"] is True


@pytest.mark.parametrize("status,state", [("failed", "failed"), ("synthesizing", "in_progress")])
def test_b89_state_for_failed_or_in_progress_run_with_values_is_never_complete(status, state):
    from run_status.view import build_view
    view = build_view(_run_with_values(status))
    assert view["display_state"] == state
    assert view["display_state"] != "complete"


def test_b89_clean_completed_run_is_complete_and_not_diagnostic():
    from run_status.view import build_view
    view = build_view(_run_with_values("completed"))
    assert view["display_state"] == "complete"
    assert view["values_are_diagnostic"] is False


# ---------------------------------------------------------------------------
# Isolation controls: prove the repaired tests do not depend on, or touch, the host
# ---------------------------------------------------------------------------

@pytest.fixture
def hostile_host_env(monkeypatch):
    """Simulates a developer machine or CI box that has real-looking auth and database settings.
    Applied BEFORE synthetic_env, which must override all of it."""
    monkeypatch.setenv("AUTH_JWT_SECRET", "BOGUS-HOST-SECRET")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "bogus-host.apps.googleusercontent.com")
    monkeypatch.setenv("DREAM_STRICT_OWNERSHIP", "0")
    monkeypatch.setenv("DREAM_DB_PATH", "/nonexistent-host-dir/real_host.db")


def test_control_ownership_404_survives_hostile_host_auth(hostile_host_env, client, stores):
    ds, _js, _ = stores
    rec = ds.create(_spec(), owner="someone-else@example.com", now_iso=NOW, status="computed")
    import os as _os
    assert _os.environ.get("AUTH_JWT_SECRET") is None, "synthetic_env must clear host auth settings"
    _os.environ["DREAM_STRICT_OWNERSHIP"] = "1"  # restored by monkeypatch teardown of hostile_host_env
    r = client.delete(f"/api/deals/{rec.deal_id}")
    assert r.status_code == 404
    assert r.json()["detail"] == "deal not found"


def test_control_login_and_gate_survive_hostile_host_db_and_auth(hostile_host_env, auth_on_main):
    import os as _os
    assert _os.environ["AUTH_JWT_SECRET"] == SYNTH_JWT_SECRET, "synthetic secret must win over the host's"
    assert "GOOGLE_CLIENT_ID" not in _os.environ
    r = auth_on_main.post("/api/auth/login", json={"username": "synthetic-user", "password": "synthetic-pass-123"})
    assert r.status_code == 200
    assert r.json()["email"] == "synthetic@example.com"
    token = r.json()["access_token"]
    assert auth_on_main.get("/api/deals").status_code == 401  # no token: still refused
    assert auth_on_main.get("/api/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_control_login_wrong_password_is_401_from_synthetic_store(auth_on_main):
    r = auth_on_main.post("/api/auth/login", json={"username": "synthetic-user", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid username or password"


def test_guard_default_store_accessors_fail_loudly(synthetic_env):
    """If any code path reaches the default singleton (the real database), the guard raises."""
    from store.user_store import get_user_store
    from jobs.job_store import get_job_store
    from store import get_deal_store
    for accessor in (get_user_store, get_job_store, get_deal_store):
        with pytest.raises(AssertionError, match="REAL DATABASE TOUCHED"):
            accessor()


def test_guard_unpatched_login_would_fail_loudly(monkeypatch, synthetic_env):
    """Negative control: login with NO synthetic user store patched in must trip the guard, not
    quietly open the configured host database."""
    monkeypatch.setenv("AUTH_JWT_SECRET", SYNTH_JWT_SECRET)
    import main
    c = TestClient(main.app, raise_server_exceptions=True)
    with pytest.raises(AssertionError, match="REAL DATABASE TOUCHED"):
        c.post("/api/auth/login", json={"username": "x", "password": "y"})
