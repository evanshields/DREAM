"""Layer 2 input tests: request validation and positive-input constraints must fail closed.

Source of truth: docs/research/2026-11-04-app-fail-closed-test-gap-map.md (draft PR 11). Each test
asserts the fail-closed behavior the gap map says is correct. Where the current code does NOT fail
closed the test is xfail(strict=True) with a "gap <ID>" reason, so the suite stays green and the gap
is pinned: when product code is fixed the xfail turns into an XPASS failure and must be removed.

Synthetic fixtures only. No network, no secrets, no product code changed. Any outside model client
(Kimi) is replaced by a local fake.
Rows: B02 B08 B09 B12 B13 B21 B22 B23 B25 B26 B28 B32 B34 B35 B40 B44.
Rows already covered by layer 1 (test_gate_headline_numbers.py) are not repeated here.
"""
import copy
import os
import sys

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.deals as deals_router  # noqa: E402
import routers.export_excel as export_router  # noqa: E402
import routers.recalc as recalc_router  # noqa: E402
from store import SQLiteDealStore  # noqa: E402

TS = "2026-11-04T00:00:00Z"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

ACQ = dict(
    bridge_loan=23800000.0, bridge_rate=0.08, bridge_io_years=2,
    refi_loan=31944864.0, refi_rate=0.06, refi_io_years=3,
    refi_amort_years=30, refi_year=2, total_equity=13145673.0,
    noi_series=[2387932, 2563041, 2742167, 2883487, 2983197,
                3134540, 3241781, 3352240, 3466013, 3583198],
    exit_cap=0.06, sale_year=7, costs_of_sale=0.02,
    servicing_spread=0.0116, refi_cost_pct=0.02, exit_on_forward_noi=True,
)
EXIT_CAP_OK = dict(going_in_cap=0.055)
AGENCY_OK = dict(stabilized_noi=4448271.31, stabilized_value=70000000.0, refi_rate=0.06)

# Every equity-based return the ACQ boundary (engine_boundary.run_acq_underwrite) emits. An accepted
# blank response must null or omit all of them, not just a subset.
EQUITY_DEPENDENT_HEADLINES = ("irr", "equity_multiple", "coc_year1", "coc_stabilized")

PYTHON_ERROR_TEXT = ("list index out of range", "division by zero", "Traceback",
                     "unsupported operand", "object has no attribute", "KeyError")


@pytest.fixture
def calc():
    app = FastAPI()
    app.include_router(recalc_router.router)
    return TestClient(app)


@pytest.fixture
def no_auth_env(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)


# ---------------------------------------------------------------------------
# B21 sale_year < 1, B22 raw Python text in 422, B23 zero equity
# ---------------------------------------------------------------------------

def test_b21_sale_year_below_one_is_422(calc):
    assert calc.post("/api/recalc", json=dict(ACQ, sale_year=0)).status_code == 422
    assert calc.post("/api/recalc", json=dict(ACQ, sale_year=-3)).status_code == 422


def test_b21_control_valid_payload_is_200(calc):
    """Control: the validation must not reject the Esplanade ground-truth payload."""
    r = calc.post("/api/recalc", json=ACQ)
    assert r.status_code == 200
    assert r.json()["headline_metrics"]["irr"] == pytest.approx(0.2251, rel=0.02)


@pytest.mark.xfail(strict=True, reason="gap B22: empty noi_series returns 422 with the raw Python text 'list index out of range'")
def test_b22_empty_noi_series_gives_plain_message_not_exception_text(calc):
    r = calc.post("/api/recalc", json=dict(ACQ, noi_series=[]))
    assert r.status_code == 422  # never a 200 with numbers
    detail = str(r.json().get("detail"))
    assert not any(t in detail for t in PYTHON_ERROR_TEXT), detail


@pytest.mark.xfail(strict=True, reason="gap B22: refi_amort_years 0 returns 422 with the raw Python text 'float division by zero'")
def test_b22_zero_amort_years_gives_plain_message_not_exception_text(calc):
    r = calc.post("/api/recalc", json=dict(ACQ, refi_amort_years=0))
    assert r.status_code == 422
    detail = str(r.json().get("detail"))
    assert not any(t in detail for t in PYTHON_ERROR_TEXT), detail


@pytest.mark.xfail(strict=True, reason="gap B23: total_equity 0 returns 200 with equity_multiple 0.0 and coc 0.0 instead of 422 or a blank")
def test_b23_zero_equity_is_rejected_or_blank_never_a_zero_multiple(calc):
    r = calc.post("/api/recalc", json=dict(ACQ, total_equity=0.0))
    if r.status_code == 200:
        hm = r.json()["headline_metrics"]
        for k in EQUITY_DEPENDENT_HEADLINES:
            assert hm.get(k) is None, f"{k}={hm.get(k)!r} shown as a number with no equity"
    else:
        assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B23: a negative total_equity is accepted (200) and produces headline numbers")
def test_b23_negative_equity_is_rejected(calc):
    r = calc.post("/api/recalc", json=dict(ACQ, total_equity=-1000000.0))
    assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B23: a negative bridge_loan is accepted (200) and produces headline numbers")
def test_b23_negative_loan_is_rejected(calc):
    r = calc.post("/api/recalc", json=dict(ACQ, bridge_loan=-23800000.0))
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# B25 EFB stabilized_noi must be positive, target_dscr must be positive
# ---------------------------------------------------------------------------

def test_b25_efb_control_positive_noi_is_200(calc):
    r = calc.post("/api/underwrite/efb", json={"stabilized_noi": 4448271.31})
    assert r.status_code == 200
    assert r.json()["headline_metrics"]["bond_amount"] > 0


@pytest.mark.xfail(strict=True, reason="gap B25: stabilized_noi -5 returns 200 with a negative bond_amount")
def test_b25_efb_negative_noi_is_422(calc):
    assert calc.post("/api/underwrite/efb", json={"stabilized_noi": -5}).status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B25: stabilized_noi 0 returns 200 with bond_amount 0.0 (a number, not a refusal)")
def test_b25_efb_zero_noi_is_422(calc):
    assert calc.post("/api/underwrite/efb", json={"stabilized_noi": 0}).status_code == 422


def test_b25_efb_zero_target_dscr_is_422(calc):
    """Already fail closed today (division guard); pinned so it stays that way."""
    r = calc.post("/api/underwrite/efb", json={"stabilized_noi": 4448271.31, "target_dscr": 0})
    assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B25: the routed /api/underwrite/v2 EFB path also accepts stabilized_noi -5 with a 200")
def test_b25_v2_efb_negative_noi_is_rejected(calc):
    r = calc.post("/api/underwrite/v2?routing=EFB", json={"stabilized_noi": -5})
    assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# B26 exit-cap and agency-sizing calculators have no bounds
# ---------------------------------------------------------------------------

def test_b26_control_valid_calculators_are_200(calc):
    assert calc.post("/api/recalc/exit-cap", json=EXIT_CAP_OK).status_code == 200
    assert calc.post("/api/recalc/agency-sizing", json=AGENCY_OK).status_code == 200


@pytest.mark.xfail(strict=True, reason="gap B26: agency-sizing with stabilized_value 0 is not rejected with a 4xx")
def test_b26_agency_sizing_zero_value_is_422(calc):
    assert calc.post("/api/recalc/agency-sizing", json=dict(AGENCY_OK, stabilized_value=0)).status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B26: agency-sizing with negative stabilized_noi is not rejected with a 4xx")
def test_b26_agency_sizing_negative_noi_is_422(calc):
    assert calc.post("/api/recalc/agency-sizing", json=dict(AGENCY_OK, stabilized_noi=-1000000)).status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B26: agency-sizing with a negative refi_rate is not rejected with a 4xx")
def test_b26_agency_sizing_negative_rate_is_422(calc):
    assert calc.post("/api/recalc/agency-sizing", json=dict(AGENCY_OK, refi_rate=-0.06)).status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B26: exit-cap calculator with going_in_cap 0 is not rejected with a 4xx")
def test_b26_exit_cap_zero_going_in_cap_is_422(calc):
    assert calc.post("/api/recalc/exit-cap", json=dict(going_in_cap=0)).status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B26: exit-cap calculator with a negative going_in_cap is not rejected with a 4xx")
def test_b26_exit_cap_negative_going_in_cap_is_422(calc):
    assert calc.post("/api/recalc/exit-cap", json=dict(going_in_cap=-0.05)).status_code == 422


# ---------------------------------------------------------------------------
# B28 sensitivity: a metric absent from the engine result is null in the grid, never 0
# ---------------------------------------------------------------------------

def test_b28_missing_metric_is_null_in_grid_not_zero(calc, monkeypatch):
    monkeypatch.setattr(recalc_router, "run_acq_underwrite", lambda inp: {"irr": 0.2})
    r = calc.post("/api/recalc/sensitivity",
                  json={"base": ACQ, "field": "exit_cap", "values": [0.055, 0.06],
                        "metric": "exit_value"})
    assert r.status_code == 200
    grid = r.json()["grid"]
    assert len(grid) == 2
    assert all(g["result"] is None for g in grid)


def test_b28_present_metric_is_kept_in_grid(calc, monkeypatch):
    monkeypatch.setattr(recalc_router, "run_acq_underwrite", lambda inp: {"irr": 0.2})
    r = calc.post("/api/recalc/sensitivity",
                  json={"base": ACQ, "field": "exit_cap", "values": [0.06], "metric": "irr"})
    assert r.json()["grid"][0]["result"] == 0.2


# ---------------------------------------------------------------------------
# B32 /api/validate with an empty body must not invent a deal
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="gap B32: /api/validate with {} validates a made-up default deal and returns 200")
def test_b32_validate_empty_body_is_422(no_auth_env):
    import main
    r = TestClient(main.app).post("/api/validate", json={})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# B34 /api/agent/chat: a model failure must not look like a normal 200 stream
# ---------------------------------------------------------------------------

class _BoomKimi:
    async def stream(self, messages):
        raise RuntimeError("synthetic upstream failure")
        yield  # pragma: no cover  (makes this an async generator)


class _OkKimi:
    async def stream(self, messages):
        yield "hello"


def _sse_events(text):
    import json
    out = []
    for line in text.splitlines():
        if line.startswith("data: ") and line != "data: [DONE]":
            out.append(json.loads(line[6:]))
    return out


def test_b34_control_ok_stream_has_tokens_and_done(no_auth_env, monkeypatch):
    import main
    monkeypatch.setattr(main, "get_kimi_client", lambda: _OkKimi())
    r = TestClient(main.app).post("/api/agent/chat",
                                  json={"mode": "free", "messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 200
    assert _sse_events(r.text) == [{"token": "hello"}]
    assert "data: [DONE]" in r.text


@pytest.mark.xfail(strict=True, reason="gap B34: a model failure is sent as a data:{error} event inside HTTP 200, with no typed error event and a client cannot tell it from success")
def test_b34_model_failure_is_not_a_plain_200_stream(no_auth_env, monkeypatch):
    import main
    monkeypatch.setattr(main, "get_kimi_client", lambda: _BoomKimi())
    r = TestClient(main.app).post("/api/agent/chat",
                                  json={"mode": "free", "messages": [{"role": "user", "content": "hi"}]})
    events = _sse_events(r.text)
    non_200 = r.status_code != 200
    typed_error = any(e.get("type") == "error" or e.get("event") == "error" for e in events)
    assert non_200 or typed_error
    assert "data: [DONE]" not in r.text  # a failed stream must not be closed like a good one


def test_b34_failure_text_reaches_client_as_error_field(no_auth_env, monkeypatch):
    """Pins today's observable behavior so a change to the error contract is noticed."""
    import main
    monkeypatch.setattr(main, "get_kimi_client", lambda: _BoomKimi())
    r = TestClient(main.app).post("/api/agent/chat",
                                  json={"mode": "free", "messages": [{"role": "user", "content": "hi"}]})
    assert any("error" in e for e in _sse_events(r.text))


# ---------------------------------------------------------------------------
# B35 / B40 intake: corrupt, empty, wrong-extension, oversize uploads
# ---------------------------------------------------------------------------

class _FakeIntake:
    """Stands in for IntakeService so the route is tested without any Kimi client."""
    def __init__(self, exc=None):
        self.exc = exc
        self.calls = []

    async def process_file(self, file_bytes, filename):
        self.calls.append((len(file_bytes), filename))
        if self.exc:
            raise self.exc
        from intake.intake_service import IntakeResult
        return IntakeResult(doc_type="T-12", confidence=0.9, detection_method="filename_heuristic",
                            extracted_fields={}, prefill_map={}, warnings=[], raw_text="")


@pytest.mark.xfail(strict=True, reason="gap B35: intake returns str(exception) to the client in the 422 detail instead of a fixed message")
def test_b35_intake_failure_detail_is_fixed_text_not_exception_string(no_auth_env, monkeypatch):
    import main
    secret_ish = "/srv/dream/internal/path.py line 42 sk-should-not-leak"
    monkeypatch.setattr(main, "get_intake_service", lambda: _FakeIntake(RuntimeError(secret_ish)))
    r = TestClient(main.app).post("/api/intake", files={"file": ("t12.pdf", b"%PDF-bad", "application/pdf")})
    assert r.status_code == 422
    assert secret_ish not in str(r.json())


def test_b35_intake_failure_is_a_4xx_never_a_200(no_auth_env, monkeypatch):
    import main
    monkeypatch.setattr(main, "get_intake_service", lambda: _FakeIntake(RuntimeError("boom")))
    r = TestClient(main.app).post("/api/intake", files={"file": ("t12.pdf", b"%PDF-bad", "application/pdf")})
    assert r.status_code == 422


@pytest.mark.xfail(strict=True, reason="gap B40: a 0-byte upload is passed to the intake service instead of being refused with a 4xx")
def test_b40_empty_file_is_4xx_and_never_reaches_service(no_auth_env, monkeypatch):
    import main
    svc = _FakeIntake()
    monkeypatch.setattr(main, "get_intake_service", lambda: svc)
    r = TestClient(main.app).post("/api/intake", files={"file": ("t12.pdf", b"", "application/pdf")})
    assert 400 <= r.status_code < 500
    assert svc.calls == []


@pytest.mark.xfail(strict=True, reason="gap B40: an unknown file extension (.exe) is passed to the intake service instead of being refused with a 4xx")
def test_b40_unknown_extension_is_4xx_and_never_reaches_service(no_auth_env, monkeypatch):
    import main
    svc = _FakeIntake()
    monkeypatch.setattr(main, "get_intake_service", lambda: svc)
    r = TestClient(main.app).post("/api/intake",
                                  files={"file": ("payload.exe", b"MZ\x90\x00 not a deal doc", "application/octet-stream")})
    assert 400 <= r.status_code < 500
    assert svc.calls == []


@pytest.mark.xfail(strict=True, reason="gap B40: there is no upload size cap, a 25 MB body is read whole and handed to the intake service")
def test_b40_oversize_file_is_4xx_and_never_reaches_service(no_auth_env, monkeypatch):
    import main
    svc = _FakeIntake()
    monkeypatch.setattr(main, "get_intake_service", lambda: svc)
    big = b"0" * (25 * 1024 * 1024)  # in-memory zeros, no file written
    r = TestClient(main.app).post("/api/intake", files={"file": ("rent_roll.csv", big, "text/csv")})
    assert 400 <= r.status_code < 500
    assert svc.calls == []


def test_b40_unknown_extension_in_service_falls_back_to_pdf_and_warns_or_blank():
    """Service-level pin, no Kimi: an unknown extension with junk bytes must not invent fields."""
    import asyncio
    from intake.intake_service import IntakeService

    class NoKimi:  # classification must not be needed for this filename
        class chat:
            class completions:
                @staticmethod
                async def create(**kw):
                    raise AssertionError("no model call expected")

    res = asyncio.run(IntakeService(NoKimi()).process_file(b"\x00\x01 junk", "t12_2025.bin"))
    assert not [v for v in res.prefill_map.values() if v not in (None, "", 0, 0.0)]


# ---------------------------------------------------------------------------
# B44 export: bytes that are not an xlsx but are named .xlsx
# ---------------------------------------------------------------------------

@pytest.fixture
def export_api(monkeypatch):
    ds = SQLiteDealStore(":memory:")
    monkeypatch.setattr(export_router, "get_deal_store", lambda: ds)
    app = FastAPI()
    app.include_router(export_router.router)
    spec = {"meta": {"deal_name": "In Test", "slug": "in-test", "routing": "ACQ", "mode": "HITL"},
            "qa": {}, "cells": [], "headline_metrics": {"irr": 0.2}}
    rec = ds.create(spec, owner="evan", now_iso=TS, status="computed")
    return rec.deal_id, TestClient(app, raise_server_exceptions=False)


def test_b44_text_bytes_named_xlsx_is_clean_4xx_on_export(export_api):
    """Gap map said 500. Observed on this commit: the populator error is caught and returned as a
    clean 422 JSON refusal, so this row is fail closed today and is pinned as a plain test."""
    deal_id, c = export_api
    r = c.post(f"/api/deals/{deal_id}/export",
               files={"template": ("a.xlsx", b"this is plain text, not a workbook", XLSX)})
    assert r.status_code == 422
    assert "json" in r.headers["content-type"]
    assert not r.content.startswith(b"PK")
    assert r.json().get("ok") is not True


def test_b44_text_bytes_named_xlsx_never_returns_a_file_or_success(export_api):
    """Holds today: whatever the status, junk bytes never produce a downloadable workbook."""
    deal_id, c = export_api
    r = c.post(f"/api/deals/{deal_id}/export",
               files={"template": ("a.xlsx", b"this is plain text, not a workbook", XLSX)},
               data={"download": "true"})
    assert r.status_code >= 400 or r.json().get("ok") is False
    assert XLSX not in r.headers.get("content-type", "")


def test_b44_text_bytes_named_xlsx_reconcile_is_not_a_success(export_api):
    deal_id, c = export_api
    r = c.post(f"/api/deals/{deal_id}/reconcile",
               files={"draft": ("a.xlsx", b"this is plain text, not a workbook", XLSX)})
    assert r.status_code >= 400


# ---------------------------------------------------------------------------
# B02 / B08 / B09 / B12 / B13 auth and ownership input checks
# ---------------------------------------------------------------------------

def _auth_probe_app():
    from auth_dep import require_auth
    app = FastAPI()

    @app.get("/api/me")
    def me(user: dict = Depends(require_auth)):
        return {"email": user.get("email")}

    return app


@pytest.mark.xfail(strict=True, reason="gap B02: with DREAM_ENV=prod and no auth env vars the server stays open, no 401 and no startup refusal")
def test_b02_production_with_no_auth_config_is_not_open(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    monkeypatch.setenv("DREAM_ENV", "prod")
    c = TestClient(_auth_probe_app(), raise_server_exceptions=False)
    r = c.get("/api/me")
    assert r.status_code in (401, 403, 500, 503)


def test_b02_control_local_dev_with_no_auth_config_is_open(monkeypatch):
    """Control: the local-dev stub user must keep working when DREAM_ENV is not prod."""
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    monkeypatch.delenv("DREAM_ENV", raising=False)
    assert TestClient(_auth_probe_app()).get("/api/me").status_code == 200


def test_b08_google_verify_without_client_id_is_500_and_leaks_no_value(monkeypatch):
    import auth
    from fastapi import HTTPException
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.setattr(auth, "GOOGLE_CLIENT_ID", "", raising=False)
    token = "eyJ.synthetic-token-value.sig"
    with pytest.raises(HTTPException) as ei:
        auth.verify_google_token(token)
    assert ei.value.status_code == 500
    assert token not in str(ei.value.detail)
    assert "GOOGLE_CLIENT_ID not configured" in ei.value.detail  # names the setting, no value


@pytest.mark.xfail(strict=True, reason="gap B09: login with AUTH_JWT_SECRET unset raises an unhandled JWTConfigError (500), not a clean 503 or 401")
def test_b09_login_without_jwt_secret_is_clean_503_or_401(monkeypatch):
    import routers.auth_login as al
    from password import hash_password
    from store.user_store import SQLiteUserStore
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    store = SQLiteUserStore(":memory:")
    store.create_user("evan", "evan@shieldstone.co", hash_password("s3cret"), now_iso=TS)
    monkeypatch.setattr(al, "get_users", lambda: store)
    monkeypatch.setattr(al, "ALLOWED_EMAILS", set(), raising=False)
    app = FastAPI()
    app.include_router(al.router)
    r = TestClient(app, raise_server_exceptions=False).post(
        "/api/auth/login", json={"username": "evan", "password": "s3cret"})
    assert r.status_code in (401, 503)
    assert "access_token" not in r.text


def test_b09_login_without_jwt_secret_never_issues_a_token(monkeypatch):
    """Holds today: the failure is a 5xx, but a token is never minted without a secret."""
    import routers.auth_login as al
    from password import hash_password
    from store.user_store import SQLiteUserStore
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    store = SQLiteUserStore(":memory:")
    store.create_user("evan", "evan@shieldstone.co", hash_password("s3cret"), now_iso=TS)
    monkeypatch.setattr(al, "get_users", lambda: store)
    monkeypatch.setattr(al, "ALLOWED_EMAILS", set(), raising=False)
    app = FastAPI()
    app.include_router(al.router)
    r = TestClient(app, raise_server_exceptions=False).post(
        "/api/auth/login", json={"username": "evan", "password": "s3cret"})
    assert r.status_code != 200
    assert "access_token" not in r.text


PROTECTED = [
    ("POST", "/api/recalc"),
    ("POST", "/api/recalc/exit-cap"),
    ("POST", "/api/recalc/agency-sizing"),
    ("POST", "/api/recalc/sensitivity"),
    ("POST", "/api/underwrite/efb"),
    ("POST", "/api/underwrite/v2?routing=ACQ"),
    ("POST", "/api/deals/some-id/export"),
    ("POST", "/api/deals/some-id/reconcile"),
    ("POST", "/api/deals/some-id/memo"),
    ("GET", "/api/deals"),
    ("GET", "/api/deals/some-id"),
    ("POST", "/api/deals/some-id/archive"),
    ("DELETE", "/api/deals/some-id"),
    ("POST", "/api/jobs"),
    ("GET", "/api/jobs/some-id"),
    ("POST", "/api/jobs/some-id/cancel"),
    ("GET", "/api/contacts"),
    ("POST", "/api/contacts"),
    ("GET", "/api/items"),
    ("GET", "/api/me"),
    ("POST", "/api/validate"),
    ("POST", "/api/intake"),
    ("POST", "/api/agent/chat"),
    ("POST", "/api/agent/memo"),
]


@pytest.mark.parametrize("method,path", PROTECTED)
def test_b12_real_app_routes_reject_missing_token_when_auth_is_on(monkeypatch, method, path):
    """Mount proof on the REAL main.app: with auth configured, no token means 401 on every router."""
    import main
    monkeypatch.setenv("AUTH_JWT_SECRET", "synthetic-test-secret")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    r = TestClient(main.app, raise_server_exceptions=False).request(method, path)
    assert r.status_code == 401, f"{method} {path} -> {r.status_code}"


def test_b12_control_login_route_is_public_when_auth_is_on(monkeypatch):
    """Control: the login route must stay reachable without a token (it is how a token is obtained)."""
    import main
    monkeypatch.setenv("AUTH_JWT_SECRET", "synthetic-test-secret")
    r = TestClient(main.app, raise_server_exceptions=False).post("/api/auth/login", json={})
    assert r.status_code != 401  # 422 for the empty body, not the auth gate


def _owned_by_other(monkeypatch, strict):
    ds = SQLiteDealStore(":memory:")
    monkeypatch.setattr(deals_router, "get_deal_store", lambda: ds)
    from jobs.job_store import SQLiteJobStore
    js = SQLiteJobStore(":memory:")
    monkeypatch.setattr(deals_router, "get_job_store", lambda: js)
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)  # stub user is evan@shieldstone.co
    if strict:
        monkeypatch.setenv("DREAM_STRICT_OWNERSHIP", "1")
    else:
        monkeypatch.delenv("DREAM_STRICT_OWNERSHIP", raising=False)
    spec = {"meta": {"deal_name": "Theirs", "slug": "theirs", "routing": "ACQ", "mode": "HITL"},
            "qa": {}, "cells": []}
    other = ds.create(spec, owner="someone.else@example.com", now_iso=TS, status="draft")
    mine = ds.create(copy.deepcopy(spec), owner="evan@shieldstone.co", now_iso=TS, status="draft")
    app = FastAPI()
    app.include_router(deals_router.router)
    return ds, other.deal_id, mine.deal_id, TestClient(app)


def test_b13_strict_ownership_hides_other_owners_deal_with_404(monkeypatch):
    ds, other_id, _mine, c = _owned_by_other(monkeypatch, strict=True)
    assert c.post(f"/api/deals/{other_id}/archive").status_code == 404
    assert c.post(f"/api/deals/{other_id}/unarchive").status_code == 404
    assert c.delete(f"/api/deals/{other_id}").status_code == 404
    assert ds.get(other_id).status == "draft"  # untouched
    assert ds.get(other_id) is not None


def test_b13_strict_ownership_still_lets_the_owner_act(monkeypatch):
    _ds, _other, mine_id, c = _owned_by_other(monkeypatch, strict=True)
    r = c.post(f"/api/deals/{mine_id}/archive")
    assert r.status_code == 200
    assert r.json()["status"] == "archived"


def test_b13_permissive_mode_is_the_documented_default(monkeypatch):
    """Pins the v1 product decision (everyone sees all) so turning strict on is visibly a change."""
    _ds, other_id, _mine, c = _owned_by_other(monkeypatch, strict=False)
    assert c.post(f"/api/deals/{other_id}/archive").status_code == 200
