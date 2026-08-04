"""
backend/routers/auth_login.py — username/password login (Task C, APIRouter prefix /api/auth).

The urgent stopgap so Evan can test the live app within 24h, before Google Test Users propagate.
Gates access ALONGSIDE Google OAuth: this endpoint mints a short-lived app JWT (app_jwt.mint_token)
that require_auth accepts as an alternative to a Google ID token.

  POST /api/auth/login   {username, password} -> {access_token, token_type, email}
                         401 on bad username/password; 403 if the user's email is not allowlisted.

The frontend sends the returned token as `Authorization: Bearer <access_token>` on API calls,
exactly like a Google ID token. A separate /api/me (main.py) returns the user for either auth type.

NO LLM imports here (keeps the recalc import-graph guard happy if ever co-imported) and the router
mounts standalone in tests with an injected user store.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store.user_store import get_user_store, SQLiteUserStore  # noqa: E402
from password import verify_password  # noqa: E402
from app_jwt import mint_token  # noqa: E402
from auth import ALLOWED_EMAILS  # noqa: E402

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


# Dependency seam — overridable in tests (module global or app.dependency_overrides).
def get_users() -> SQLiteUserStore:
    return get_user_store()


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """Verify username+password and issue a signed app JWT. Generic 401 on any auth failure
    (missing user, bad password) so the endpoint does not leak which usernames exist."""
    users = get_users()
    user = users.find_user(req.username)

    # Run verify even when the user is missing? bcrypt has no cheap dummy hash here; a generic 401
    # for both cases is the practical anti-enumeration measure for this stopgap.
    if user is None or not verify_password(req.password, user.password_hash):
        if user is not None:
            users.record_failed_attempt(req.username, now_iso=_now())
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Enforce the same allowlist the Google path enforces.
    if ALLOWED_EMAILS and user.email.lower() not in ALLOWED_EMAILS:
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to access this tool",
        )

    users.reset_failed_attempts(req.username)
    token = mint_token(user.username, user.email)
    return LoginResponse(access_token=token, email=user.email)
