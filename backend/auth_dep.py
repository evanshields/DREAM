"""
Configurable auth dependency (Wave A0.2) — extracted from main.py so it is importable without the
heavy app graph (pandas/pymupdf/openai). main.py imports `require_auth` from here.

Enforced when GOOGLE_CLIENT_ID is set (production / US VPS); a transparent local-dev pass-through
when unset. Flipping auth on at migration time is an env change, not a code change.

Task C — a Bearer token now satisfies require_auth if it is EITHER a valid app JWT (the
username/password login path, app_jwt.decode_token) OR a valid Google ID token (the original
path). The app-JWT check runs FIRST because it is cheap (local HMAC verify, no network); only a
token that is not a well-formed app JWT (or fails app verification) falls through to Google.
ALLOWED_EMAILS is enforced for BOTH paths.
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth import verify_google_token, ALLOWED_EMAILS


def auth_enabled() -> bool:
    """Read at request time (not import time) so tests can toggle the env per case.

    Enabled when EITHER Google OAuth (GOOGLE_CLIENT_ID) OR the app-JWT login (AUTH_JWT_SECRET) is
    configured. Either one being set means the server is a real deployment and must enforce auth.
    """
    return bool(
        os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        or os.environ.get("AUTH_JWT_SECRET", "").strip()
    )


_bearer = HTTPBearer(auto_error=False)


def _check_allowlist(email: str) -> None:
    """Enforce ALLOWED_EMAILS (when configured) — shared by both auth paths."""
    if ALLOWED_EMAILS and (email or "").lower() not in ALLOWED_EMAILS:
        raise HTTPException(
            status_code=403,
            detail="Your account is not authorized to access this tool",
        )


def _try_app_jwt(token: str) -> Optional[dict]:
    """Verify an app JWT. Returns a user dict on success, None if this is not an app JWT (so the
    caller falls back to Google). Raises 401 only when the token LOOKS like an app JWT but fails
    verification (bad signature / expired / malformed) — that should not silently fall through to
    a Google network call."""
    # Imported lazily so environments without PyJWT (none in prod) still import this module, and so
    # auth_enabled()/the Google path never depend on the JWT lib being present.
    try:
        from app_jwt import decode_token, looks_like_app_jwt, JWTConfigError
        import jwt as _pyjwt
    except Exception:  # pragma: no cover - PyJWT is a pinned dependency in prod
        return None

    if not os.environ.get("AUTH_JWT_SECRET", "").strip():
        return None  # app-JWT login not configured on this server -> defer to Google
    if not looks_like_app_jwt(token):
        return None  # not three-segment JWT shape -> let Google try it

    try:
        claims = decode_token(token)
    except JWTConfigError:
        return None
    except _pyjwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "sub": claims.get("sub"),
        "email": claims.get("email", ""),
        "name": claims.get("sub"),
        "auth": "app",
    }


def require_auth(
    creds: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> Optional[dict]:
    """Dependency for protected routes.

    When auth is enabled (GOOGLE_CLIENT_ID and/or AUTH_JWT_SECRET set):
      - no Bearer token -> 401
      - a valid app JWT for an allowlisted email -> OK (tried first, no network)
      - else a valid Google ID token for an allowlisted email -> OK
      - a token from a non-allowlisted email -> 403 (ALLOWED_EMAILS enforced for both paths)
      - an invalid/expired token -> 401
    When disabled (local dev): returns a stub user so the app still runs without keys.
    """
    if not auth_enabled():
        return {"email": "evan@shieldstone.co", "name": "Evan Shields", "local_dev": True}
    if creds is None:
        raise HTTPException(status_code=401, detail="Authentication required",
                            headers={"WWW-Authenticate": "Bearer"})

    token = creds.credentials

    # 1) App JWT first — cheap local HMAC verify, no network round-trip.
    app_user = _try_app_jwt(token)
    if app_user is not None:
        _check_allowlist(app_user.get("email", ""))
        return app_user

    # 2) Fall back to Google ID-token verification (original path). If GOOGLE_CLIENT_ID is unset
    #    verify_google_token raises 500; that is correct — a JWT-only server should never reach
    #    here with a non-app token, and a misconfigured server must fail loudly.
    user = verify_google_token(token)  # raises 401 on invalid/expired
    _check_allowlist(user.get("email", ""))
    return user
