"""Auth regression tests for the run-status routes. The router is mounted exactly as
backend/main.py mounts it: include_router(router, dependencies=[Depends(require_auth)]).
Auth is switched on with AUTH_JWT_SECRET (app-JWT path), so no network or Google call is made."""
import os
import sys

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_dep import require_auth  # noqa: E402
from routers.run_status import router  # noqa: E402

PATHS = ["/api/run-status", "/api/run-status/run-failed"]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret-for-run-status-auth-tests-0123456789")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.setattr("auth_dep.ALLOWED_EMAILS", set())
    app = FastAPI()
    app.include_router(router, dependencies=[Depends(require_auth)])  # same as main.py
    return TestClient(app)


def _token():
    from app_jwt import mint_token
    return mint_token("tester", "tester@example.com")


@pytest.mark.parametrize("path", PATHS)
def test_missing_token_401(client, path):
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("bad", ["garbage", "a.b.c", "Bearer"])
def test_invalid_token_401(client, path, bad):
    r = client.get(path, headers={"Authorization": f"Bearer {bad}"})
    assert r.status_code == 401


@pytest.mark.parametrize("path", PATHS)
def test_token_signed_with_other_secret_401(client, monkeypatch, path):
    monkeypatch.setenv("AUTH_JWT_SECRET", "a-different-secret-for-minting-0123456789abcdef")
    forged = _token()
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-secret-for-run-status-auth-tests-0123456789")
    r = client.get(path, headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


@pytest.mark.parametrize("path", PATHS)
def test_valid_token_200(client, path):
    r = client.get(path, headers={"Authorization": f"Bearer {_token()}"})
    assert r.status_code == 200


def test_main_mounts_router_with_require_auth():
    """Guard the production mount itself (text check, avoids importing the heavy app graph)."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")).read()
    assert "app.include_router(run_status_router, dependencies=[Depends(require_auth)])" in src
