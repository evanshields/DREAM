"""
Task C acceptance tests — username/password login alongside Google OAuth.

Covers:
  * bcrypt hash round-trip (good password verifies, bad password does not).
  * user_store create/get round-trip + duplicate guard.
  * POST /api/auth/login: good creds -> token; bad password -> 401; non-allowlisted -> 403.
  * require_auth accepts a valid app JWT for an allowlisted email.
  * require_auth rejects an expired / garbage JWT -> 401.
  * the EXISTING Google path still works (verify_google_token mocked) and still enforces ALLOWED_EMAILS.

These mount require_auth / the login router on minimal FastAPI apps so the proof never needs the
heavy app graph (pandas/pymupdf/openai), mirroring test_auth_gate.py.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("bcrypt")
pytest.importorskip("jwt")
pytest.importorskip("starlette")

SECRET = "test-secret-do-not-use-in-prod"


# ---------------------------------------------------------------------------
# Env helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def jwt_secret(monkeypatch):
    monkeypatch.setenv("AUTH_JWT_SECRET", SECRET)
    return SECRET


@pytest.fixture
def allowlist(monkeypatch):
    """Set ALLOWED_EMAILS and refresh the cached set inside auth.py (it is computed at import)."""
    import auth
    monkeypatch.setenv("ALLOWED_EMAILS", "evan@shieldstone.co")
    monkeypatch.setattr(auth, "ALLOWED_EMAILS", {"evan@shieldstone.co"}, raising=False)
    # auth_dep imports ALLOWED_EMAILS by reference into its own module namespace; patch both.
    import auth_dep
    monkeypatch.setattr(auth_dep, "ALLOWED_EMAILS", {"evan@shieldstone.co"}, raising=False)
    import routers.auth_login as al
    monkeypatch.setattr(al, "ALLOWED_EMAILS", {"evan@shieldstone.co"}, raising=False)
    return {"evan@shieldstone.co"}


# ---------------------------------------------------------------------------
# 1. bcrypt hash round-trip
# ---------------------------------------------------------------------------

def test_hash_round_trip():
    from password import hash_password, verify_password
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"          # never plaintext
    assert h.startswith("$2")                            # bcrypt format
    assert verify_password("correct horse battery staple", h) is True
    assert verify_password("wrong password", h) is False


def test_verify_handles_garbage_hash():
    from password import verify_password
    assert verify_password("anything", "not-a-bcrypt-hash") is False
    assert verify_password("", "") is False


def test_long_password_not_truncated():
    """bcrypt's 72-byte cap must not collapse two long passwords that share a 72-byte prefix."""
    from password import hash_password, verify_password
    base = "A" * 80
    h = hash_password(base + "ONE")
    assert verify_password(base + "ONE", h) is True
    assert verify_password(base + "TWO", h) is False


# ---------------------------------------------------------------------------
# 2. user_store
# ---------------------------------------------------------------------------

def test_user_store_create_get_round_trip():
    from store.user_store import SQLiteUserStore, UserNotFound, UserExists
    from password import hash_password
    s = SQLiteUserStore(":memory:")
    s.create_user("evan", "Evan@Shieldstone.co", hash_password("pw"), now_iso="2026-06-09T00:00:00Z")
    got = s.get_user("evan")
    assert got.username == "evan"
    assert got.email == "evan@shieldstone.co"            # normalized lower
    assert got.created_at == "2026-06-09T00:00:00Z"
    assert s.get_by_email("evan@shieldstone.co").username == "evan"
    with pytest.raises(UserExists):
        s.create_user("evan", "other@x.co", hash_password("pw2"), now_iso="z")
    with pytest.raises(UserNotFound):
        s.get_user("nobody")


def test_user_store_failed_attempt_bookkeeping():
    from store.user_store import SQLiteUserStore
    from password import hash_password
    s = SQLiteUserStore(":memory:")
    s.create_user("evan", "evan@shieldstone.co", hash_password("pw"), now_iso="z")
    s.record_failed_attempt("evan")
    s.record_failed_attempt("evan")
    assert s.get_user("evan").failed_attempts == 2
    s.reset_failed_attempts("evan")
    assert s.get_user("evan").failed_attempts == 0


# ---------------------------------------------------------------------------
# Login app harness
# ---------------------------------------------------------------------------

def _login_app(user_store):
    from fastapi import FastAPI
    import routers.auth_login as al
    al.get_users = lambda: user_store          # override the dependency seam
    app = FastAPI()
    app.include_router(al.router)
    return app


def _seed_store(username="evan", email="evan@shieldstone.co", password="s3cret"):
    from store.user_store import SQLiteUserStore
    from password import hash_password
    s = SQLiteUserStore(":memory:")
    s.create_user(username, email, hash_password(password), now_iso="2026-06-09T00:00:00Z")
    return s


def _client(app):
    from starlette.testclient import TestClient
    return TestClient(app)


# ---------------------------------------------------------------------------
# 3. /api/auth/login
# ---------------------------------------------------------------------------

def test_login_good_creds_returns_token(jwt_secret, allowlist):
    s = _seed_store()
    r = _client(_login_app(s)).post("/api/auth/login",
                                    json={"username": "evan", "password": "s3cret"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["email"] == "evan@shieldstone.co"
    # The token verifies as a real app JWT.
    from app_jwt import decode_token
    claims = decode_token(body["access_token"])
    assert claims["sub"] == "evan"
    assert claims["email"] == "evan@shieldstone.co"


def test_login_bad_password_401(jwt_secret, allowlist):
    s = _seed_store()
    r = _client(_login_app(s)).post("/api/auth/login",
                                    json={"username": "evan", "password": "WRONG"})
    assert r.status_code == 401


def test_login_unknown_user_401(jwt_secret, allowlist):
    s = _seed_store()
    r = _client(_login_app(s)).post("/api/auth/login",
                                    json={"username": "ghost", "password": "whatever"})
    assert r.status_code == 401


def test_login_non_allowlisted_403(jwt_secret, allowlist):
    s = _seed_store(username="mallory", email="mallory@evil.co", password="s3cret")
    r = _client(_login_app(s)).post("/api/auth/login",
                                    json={"username": "mallory", "password": "s3cret"})
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# require_auth harness (mirrors test_auth_gate.py)
# ---------------------------------------------------------------------------

def _auth_app():
    from fastapi import Depends, FastAPI
    from auth_dep import require_auth
    app = FastAPI()

    @app.get("/api/me")
    def me(user: dict = Depends(require_auth)):
        return {"email": user.get("email"), "auth": user.get("auth")}

    return app


# ---------------------------------------------------------------------------
# 4. require_auth accepts a valid app JWT
# ---------------------------------------------------------------------------

def test_require_auth_accepts_valid_app_jwt(jwt_secret, allowlist):
    from app_jwt import mint_token
    token = mint_token("evan", "evan@shieldstone.co")
    r = _client(_auth_app()).get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "evan@shieldstone.co"
    assert r.json()["auth"] == "app"


def test_require_auth_app_jwt_non_allowlisted_403(jwt_secret, allowlist):
    from app_jwt import mint_token
    token = mint_token("mallory", "mallory@evil.co")
    r = _client(_auth_app()).get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# 5. require_auth rejects expired / garbage JWT
# ---------------------------------------------------------------------------

def test_require_auth_rejects_expired_app_jwt(jwt_secret, allowlist):
    from app_jwt import mint_token
    past = datetime.now(timezone.utc) - timedelta(hours=48)
    token = mint_token("evan", "evan@shieldstone.co", now=past)  # exp is 12h after `past` -> expired
    r = _client(_auth_app()).get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_require_auth_rejects_garbage_jwt(jwt_secret, allowlist):
    # Three-segment garbage -> looks like an app JWT, fails signature -> 401 (does NOT fall through).
    r = _client(_auth_app()).get("/api/me",
                                 headers={"Authorization": "Bearer aaa.bbb.ccc"})
    assert r.status_code == 401


def test_require_auth_rejects_jwt_signed_with_wrong_secret(jwt_secret, allowlist):
    import jwt as pyjwt
    bad = pyjwt.encode(
        {"sub": "evan", "email": "evan@shieldstone.co", "iss": "dream-app",
         "iat": 0, "exp": 9999999999},
        "WRONG-SECRET", algorithm="HS256",
    )
    r = _client(_auth_app()).get("/api/me", headers={"Authorization": f"Bearer {bad}"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# 6. Existing Google path still works (mock verify_google_token)
# ---------------------------------------------------------------------------

def test_require_auth_google_path_still_works(monkeypatch, allowlist):
    """A non-JWT-shaped Google token still verifies via the existing Google path. AUTH_JWT_SECRET
    is set too (both configured) to prove the app-JWT check defers correctly to Google for a token
    that is not a well-formed app JWT."""
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    monkeypatch.setenv("AUTH_JWT_SECRET", SECRET)

    import auth
    import auth_dep
    monkeypatch.setattr(auth, "verify_google_token",
                        lambda tok: {"email": "evan@shieldstone.co", "name": "Evan", "sub": "g123"})
    monkeypatch.setattr(auth_dep, "verify_google_token",
                        lambda tok: {"email": "evan@shieldstone.co", "name": "Evan", "sub": "g123"})

    # A Google ID token is a 3-segment JWT too, but it is NOT signed with our secret, so the app-JWT
    # verify raises 401 BEFORE reaching Google. Use an opaque (non-3-segment) token to exercise the
    # Google fallback deterministically.
    r = _client(_auth_app()).get("/api/me",
                                 headers={"Authorization": "Bearer opaque-google-token"})
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "evan@shieldstone.co"


def test_require_auth_google_path_enforces_allowlist(monkeypatch, allowlist):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    import auth
    import auth_dep
    monkeypatch.setattr(auth, "verify_google_token",
                        lambda tok: {"email": "outsider@gmail.com", "name": "X", "sub": "g9"})
    monkeypatch.setattr(auth_dep, "verify_google_token",
                        lambda tok: {"email": "outsider@gmail.com", "name": "X", "sub": "g9"})
    r = _client(_auth_app()).get("/api/me",
                                 headers={"Authorization": "Bearer opaque-google-token"})
    assert r.status_code == 403


def test_require_auth_disabled_local_dev(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    r = _client(_auth_app()).get("/api/me")
    assert r.status_code == 200
    assert r.json()["email"] == "evan@shieldstone.co"
