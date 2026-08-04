"""
backend/password.py — bcrypt password hashing (Task C).

Hashing/verification is isolated here so the user store (backend/store/user_store.py) stays
persistence-only and the login endpoint stays thin.

LIBRARY CHOICE — the standalone ``bcrypt`` (pyca/bcrypt), NOT ``passlib[bcrypt]``:
  * passlib 1.7.4 (last release 2020) is effectively unmaintained and crashes on modern
    bcrypt>=4.1 because it reads the removed ``bcrypt.__about__.__version__`` attribute.
    Avoiding the wrapper avoids that whole failure class.
  * pyca/bcrypt is actively maintained, audited, and the canonical Python bcrypt binding.
  * bcrypt enforces a 72-byte input limit. We sha256-pre-hash to a fixed-length hex digest
    before bcrypt so long passwords are not silently truncated (a documented bcrypt footgun).

Cost factor 12 (rounds) — a sensible 2026 default for an interactive login.
"""
from __future__ import annotations

import hashlib

import bcrypt

# bcrypt work factor. 12 ~ tens of ms on a modern VPS — fine for interactive login, costly to brute.
_ROUNDS = 12


def _prehash(password: str) -> bytes:
    """Map an arbitrary-length password to a fixed 64-byte hex digest so bcrypt's 72-byte cap
    never silently truncates the input. Hex (not raw digest) avoids any NUL-byte truncation too."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


def hash_password(password: str) -> str:
    """Return a bcrypt hash string (safe to store). Plaintext is never persisted."""
    if not isinstance(password, str) or password == "":
        raise ValueError("password must be a non-empty string")
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt(rounds=_ROUNDS)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time verify a plaintext password against a stored bcrypt hash. Returns False on
    any malformed hash rather than raising (login should yield a generic 401, not a 500)."""
    if not password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(_prehash(password), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False
