"""
backend/app_jwt.py — short-lived app JWT (Task C).

The username/password login issues one of these; require_auth accepts it as an alternative to a
Google ID token. Deliberately small: HS256, a server SECRET, a {sub, email} payload, an expiry.

LIBRARY: PyJWT (jpadilla/PyJWT) — the canonical, well-vetted Python JWT lib (pinned in
requirements). HS256 (symmetric) is correct here: the same server both signs and verifies, so a
shared secret is simpler and safer than managing an asymmetric keypair for this short-lived path.

SECRET: read from AUTH_JWT_SECRET at call time (not import time) so tests/migration can set it
after import. No default secret — if it is unset when a token is minted or verified we fail
closed (a missing secret must never silently accept tokens).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt  # PyJWT

# Token lifetime. Short-lived by design (this is the urgent stopgap before Google Test Users
# propagate); the user re-logs in when it expires. Override with AUTH_JWT_TTL_HOURS if needed.
_DEFAULT_TTL_HOURS = 12
_ALG = "HS256"
_ISS = "dream-app"


class JWTConfigError(RuntimeError):
    """Raised when AUTH_JWT_SECRET is not configured (fail closed — never sign/verify without it)."""


def _secret() -> str:
    secret = os.environ.get("AUTH_JWT_SECRET", "").strip()
    if not secret:
        raise JWTConfigError("AUTH_JWT_SECRET is not set on the server")
    return secret


def _ttl_hours() -> int:
    raw = os.environ.get("AUTH_JWT_TTL_HOURS", "").strip()
    try:
        return int(raw) if raw else _DEFAULT_TTL_HOURS
    except ValueError:
        return _DEFAULT_TTL_HOURS


def mint_token(username: str, email: str, now: Optional[datetime] = None) -> str:
    """Sign a {sub: username, email} HS256 token with iat/exp/iss. ``now`` is injectable for tests."""
    now = now or datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "email": email.lower(),
        "iss": _ISS,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=_ttl_hours())).timestamp()),
    }
    return jwt.encode(payload, _secret(), algorithm=_ALG)


def decode_token(token: str) -> dict:
    """Verify signature + expiry + issuer and return the claims. Raises jwt.PyJWTError (specifically
    ExpiredSignatureError / InvalidTokenError) on any failure — the caller maps that to a 401."""
    return jwt.decode(
        token,
        _secret(),
        algorithms=[_ALG],          # explicit allowlist — never trust the token's own alg header
        issuer=_ISS,
        options={"require": ["exp", "sub", "iss"]},
    )


def looks_like_app_jwt(token: str) -> bool:
    """Cheap shape check: a JWT is three base64url segments. Lets require_auth try the app-JWT path
    first without paying a Google network round-trip on tokens that clearly are not ours. This is a
    routing hint only — decode_token still fully verifies."""
    return isinstance(token, str) and token.count(".") == 2
