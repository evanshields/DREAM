"""A0.2 acceptance tests (code portion) — configurable Google OAuth.

Tests the `auth_dep.require_auth` dependency in isolation on a minimal FastAPI app, so the proof
does not require importing the full app graph (pandas/pymupdf). Same dependency main.py mounts.

- auth disabled (no GOOGLE_CLIENT_ID): protected route returns a stub user, app runs locally.
- auth enabled (GOOGLE_CLIENT_ID set): unauthenticated request to a protected route -> 401.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _app():
    """A minimal app that mounts require_auth on a protected route + a public health route."""
    from fastapi import Depends, FastAPI
    from auth_dep import require_auth
    app = FastAPI()

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/me")
    def me(user: dict = Depends(require_auth)):
        return {"email": user.get("email")}

    return app


def _client(app):
    from starlette.testclient import TestClient
    return TestClient(app)


def test_health_public(monkeypatch):
    pytest.importorskip("starlette")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    r = _client(_app()).get("/api/health")
    assert r.status_code == 200


def test_auth_disabled_returns_stub_user(monkeypatch):
    pytest.importorskip("starlette")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)  # local dev
    from auth_dep import auth_enabled
    assert auth_enabled() is False
    r = _client(_app()).get("/api/me")
    assert r.status_code == 200
    assert r.json()["email"] == "evan@shieldstone.co"


def test_auth_enabled_blocks_unauthenticated(monkeypatch):
    pytest.importorskip("starlette")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    from auth_dep import auth_enabled
    assert auth_enabled() is True
    r = _client(_app()).get("/api/me")  # no Bearer token
    assert r.status_code == 401


def test_auth_enabled_rejects_invalid_token(monkeypatch):
    pytest.importorskip("starlette")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    r = _client(_app()).get("/api/me", headers={"Authorization": "Bearer not-a-real-token"})
    # verify_google_token raises 401 on an unverifiable token.
    assert r.status_code == 401
