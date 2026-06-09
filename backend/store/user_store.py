"""
backend/store/user_store.py — minimal username/password user persistence (Task C).

A small SQLite-backed user store for the username/password login that gates the live app
ALONGSIDE Google OAuth (both independently satisfy require_auth). This is the urgent
short-lived path so Evan can test the live app before Google Test Users propagate; the full
lockout/reset story is the LATER Postgres wave.

Mirrors backend/store/deal_store.py + backend/jobs/job_store.py exactly:

  * NO ``import sqlite3`` here. The architectural guard
    (test_deal_store.test_no_sqlite_or_filepath_outside_store) forbids a DB driver outside
    backend/store; but this module IS inside backend/store, so it could import sqlite3 — we
    still go through ``open_sqlite``/``default_db_path`` so users co-locate in the one DB file
    and the Postgres swap (Wave F.2) stays a single-package change.
  * Thread-safe via a single shared connection + a lock (FastAPI worker threads).
  * Parametrized SQL only — never string-formatted values.
  * The caller passes ``now_iso`` (ISO-8601). This module never calls a clock —
    deterministic + testable, consistent with the sibling stores.

Passwords are stored ONLY as a bcrypt hash (``password_hash``). Plaintext never touches the DB.
Hashing/verification live in backend/password.py so this store stays persistence-only.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import List, Optional

# DB driver comes from the store package itself (open_sqlite/default_db_path live in deal_store).
from .deal_store import open_sqlite, default_db_path


# ---------------------------------------------------------------------------
# Errors + record
# ---------------------------------------------------------------------------

class UserNotFound(KeyError):
    """Raised when a username/email lookup misses."""


class UserExists(ValueError):
    """Raised by create_user when the username already exists."""


@dataclass
class UserRecord:
    """One persisted user. ``password_hash`` is a bcrypt hash string; plaintext is never stored."""
    username: str
    email: str
    password_hash: str
    created_at: str = ""
    failed_attempts: int = 0
    locked_until: str = ""          # ISO-8601; empty = not locked (reserved for the Postgres wave)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username        TEXT PRIMARY KEY,
    email           TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    created_at      TEXT,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""


class SQLiteUserStore:
    """File-backed (or :memory:) SQLite user store. Thread-safe via one connection + a lock,
    mirroring SQLiteDealStore / SQLiteJobStore. The connection is obtained from the store package
    (open_sqlite) so users share the deal DB file."""

    def __init__(self, path: str = ":memory:"):
        self._path = path
        self._conn = open_sqlite(path)
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # -- helpers --
    @staticmethod
    def _row_to_record(row) -> UserRecord:
        return UserRecord(
            username=row["username"],
            email=row["email"] or "",
            password_hash=row["password_hash"] or "",
            created_at=row["created_at"] or "",
            failed_attempts=row["failed_attempts"] or 0,
            locked_until=row["locked_until"] or "",
        )

    # -- public API --
    def create_user(self, username: str, email: str, password_hash: str,
                    now_iso: str) -> UserRecord:
        """Insert a user. ``password_hash`` MUST already be a bcrypt hash (this store never hashes
        — it only persists). Raises UserExists on a duplicate username."""
        rec = UserRecord(
            username=username,
            email=email.strip().lower(),
            password_hash=password_hash,
            created_at=now_iso,
        )
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO users (username, email, password_hash, created_at, "
                    "failed_attempts, locked_until) VALUES (?,?,?,?,?,?)",
                    (rec.username, rec.email, rec.password_hash, rec.created_at, 0, ""),
                )
                self._conn.commit()
            except Exception as e:  # sqlite3.IntegrityError lives in the driver we don't import
                if e.__class__.__name__ == "IntegrityError":
                    raise UserExists(f"user '{username}' already exists") from e
                raise
        return rec

    def get_user(self, username: str) -> UserRecord:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE username=?", (username,)
            ).fetchone()
        if row is None:
            raise UserNotFound(username)
        return self._row_to_record(row)

    def get_by_email(self, email: str) -> UserRecord:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM users WHERE email=?", (email.strip().lower(),)
            ).fetchone()
        if row is None:
            raise UserNotFound(email)
        return self._row_to_record(row)

    def find_user(self, username: str) -> Optional[UserRecord]:
        """Like get_user but returns None instead of raising (handy for the login path so a
        missing user and a bad password both yield a generic 401 with no user-enumeration leak)."""
        try:
            return self.get_user(username)
        except UserNotFound:
            return None

    def list_users(self) -> List[UserRecord]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM users ORDER BY created_at ASC"
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    # -- failed-attempt bookkeeping (basic; full lockout is the Postgres wave) --
    def record_failed_attempt(self, username: str, now_iso: str = "") -> None:
        """Increment failed_attempts (best-effort; no-op if the user does not exist)."""
        with self._lock:
            self._conn.execute(
                "UPDATE users SET failed_attempts = failed_attempts + 1 WHERE username=?",
                (username,),
            )
            self._conn.commit()

    def reset_failed_attempts(self, username: str) -> None:
        """Clear failed_attempts + any lock (called after a successful login)."""
        with self._lock:
            self._conn.execute(
                "UPDATE users SET failed_attempts = 0, locked_until = '' WHERE username=?",
                (username,),
            )
            self._conn.commit()

    def delete_user(self, username: str) -> None:
        with self._lock:
            cur = self._conn.execute("DELETE FROM users WHERE username=?", (username,))
            self._conn.commit()
        if cur.rowcount == 0:
            raise UserNotFound(username)


# ---------------------------------------------------------------------------
# Singleton accessor (the app's one entry point to user persistence)
# ---------------------------------------------------------------------------

_user_store: Optional[SQLiteUserStore] = None


def get_user_store() -> SQLiteUserStore:
    """Process-wide UserStore. Shares the deal DB file (DREAM_DB_PATH) so users + deals + jobs
    co-locate. Swap to a Postgres implementation here in Wave F.2 — callers never change."""
    global _user_store
    if _user_store is None:
        _user_store = SQLiteUserStore(default_db_path())
    return _user_store
