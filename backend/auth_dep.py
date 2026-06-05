"""
Configurable auth dependency (Wave A0.2) — extracted from main.py so it is importable without the
heavy app graph (pandas/pymupdf/openai). main.py imports `require_auth` from here.

Enforced when GOOGLE_CLIENT_ID is set (production / US VPS); a transparent local-dev pass-through
when unset. Flipping auth on at migration time is an env change, not a code change.
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth import verify_google_token, ALLOWED_EMAILS


def auth_enabled() -> bool:
    """Read at request time (not import time) so tests can toggle the env per case."""
    return bool(os.environ.get("GOOGLE_CLIENT_ID", "").strip())


_bearer = HTTPBearer(auto_error=False)


def require_auth(
    creds: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
) -> Optional[dict]:
    """Dependency for protected routes.

    When auth is enabled (GOOGLE_CLIENT_ID set):
      - no/invalid Bearer token -> 401
      - valid token from a non-allowlisted email -> 403 (ALLOWED_EMAILS enforced)
    When disabled (local dev): returns a stub user so the app still runs without keys.
    """
    if not auth_enabled():
        return {"email": "evan@shieldstone.co", "name": "Evan Shields", "local_dev": True}
    if creds is None:
        raise HTTPException(status_code=401, detail="Authentication required",
                            headers={"WWW-Authenticate": "Bearer"})
    user = verify_google_token(creds.credentials)  # raises 401 on invalid/expired
    if ALLOWED_EMAILS and user.get("email", "").lower() not in ALLOWED_EMAILS:
        raise HTTPException(status_code=403,
                            detail="Your account is not authorized to access this tool")
    return user
