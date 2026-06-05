"""
DealStore — deal persistence for DREAM (Wave A1.2).

The app was stateless. The whole product arc (populate the app, tweak live, push to Excel,
Hermes lands the same deal instance) dereferences a deal that must persist. This module owns
ALL persistence. Two rules from the PRD:

  1. The canonical record is the ``underwrite-spec.json`` blob, stored as an OPAQUE DOCUMENT.
     A thin relational index (deal_id, slug, routing, mode, status, owner, version, timestamps)
     is derived from it for listing/filtering — it is NOT a second source of truth.

  2. **No module outside this one imports sqlite3 or builds a deal file path.** The rest of the
     app talks to the `DealStore` interface only. That keeps the Postgres swap (Wave F.2) a
     drop-in second implementation, not a logic migration, and keeps the skill's
     filesystem-as-database pattern out of the server.

Optimistic concurrency: every record carries an integer ``version``. ``put`` takes the version
the caller last read; a mismatch raises ``VersionConflict`` rather than silently clobbering a
concurrent write (the chat-bot service may populate a deal while the user is viewing it).

Timestamps: the caller passes ``now_iso`` (an ISO-8601 string). This module never calls a clock
— deterministic, testable, and consistent with the skill's "scripts cannot call Date.now()" rule.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Protocol


# ---------------------------------------------------------------------------
# Errors + record
# ---------------------------------------------------------------------------

class DealNotFound(KeyError):
    """Raised by get()/put() when the deal_id does not exist."""


class VersionConflict(Exception):
    """Raised by put() when the expected version != the stored version (lost-update guard)."""

    def __init__(self, deal_id: str, expected: int, actual: int):
        super().__init__(
            f"version conflict on deal '{deal_id}': expected {expected}, stored {actual} "
            f"(the deal was modified since you read it; re-read and retry)"
        )
        self.deal_id = deal_id
        self.expected = expected
        self.actual = actual


@dataclass
class DealRecord:
    """One persisted deal: the opaque spec blob + its derived index fields."""
    deal_id: str
    spec: Dict[str, object]          # the canonical underwrite-spec.json (opaque document)
    version: int = 1
    # --- derived index fields (read off the spec; never authored independently) ---
    slug: str = ""
    deal_name: str = ""
    routing: str = ""                # ACQ | EFB
    mode: str = ""                   # HITL | HOTL
    status: str = "draft"            # draft | computed | populated | exported | archived
    owner: str = ""
    created_at: str = ""
    updated_at: str = ""


def _index_from_spec(spec: Dict[str, object]) -> Dict[str, str]:
    """Pull the thin relational index out of the canonical spec. Spec is the source of truth."""
    meta = spec.get("meta", {}) if isinstance(spec, dict) else {}
    return {
        "slug": str(meta.get("slug", "")),
        "deal_name": str(meta.get("deal_name", "")),
        "routing": str(meta.get("routing", "")),
        "mode": str(meta.get("mode", "")),
    }


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

class DealStore(Protocol):
    """The persistence contract the rest of the app depends on. Implementations: SQLite (now),
    Postgres (Wave F.2). Nothing outside an implementation imports a DB driver."""

    def create(self, spec: Dict[str, object], owner: str, now_iso: str,
               deal_id: Optional[str] = None, status: str = "draft") -> DealRecord: ...

    def get(self, deal_id: str) -> DealRecord: ...

    def put(self, deal_id: str, spec: Dict[str, object], expected_version: int,
            now_iso: str, status: Optional[str] = None, owner: Optional[str] = None) -> DealRecord: ...

    def list(self, owner: Optional[str] = None, routing: Optional[str] = None,
             status: Optional[str] = None) -> List[DealRecord]: ...

    def delete(self, deal_id: str) -> None: ...


# ---------------------------------------------------------------------------
# SQLite implementation
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS deals (
    deal_id    TEXT PRIMARY KEY,
    spec_json  TEXT NOT NULL,          -- the opaque canonical document
    version    INTEGER NOT NULL,
    slug       TEXT,
    deal_name  TEXT,
    routing    TEXT,
    mode       TEXT,
    status     TEXT,
    owner      TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_deals_owner   ON deals(owner);
CREATE INDEX IF NOT EXISTS idx_deals_routing ON deals(routing);
CREATE INDEX IF NOT EXISTS idx_deals_status  ON deals(status);
"""


class SQLiteDealStore:
    """File-backed (or in-memory) SQLite DealStore. Thread-safe via a single connection + lock.

    ``path=":memory:"`` is supported for tests. For an on-disk DB, the FILE is a DB file, not a
    per-deal document tree — the filesystem-as-database anti-pattern stays out of the app.
    """

    def __init__(self, path: str = ":memory:"):
        self._path = path
        # check_same_thread=False + an explicit lock: FastAPI may touch the store from worker
        # threads. A single shared connection keeps SQLite's single-writer semantics simple.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # -- helpers --
    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> DealRecord:
        return DealRecord(
            deal_id=row["deal_id"],
            spec=json.loads(row["spec_json"]),
            version=row["version"],
            slug=row["slug"] or "",
            deal_name=row["deal_name"] or "",
            routing=row["routing"] or "",
            mode=row["mode"] or "",
            status=row["status"] or "draft",
            owner=row["owner"] or "",
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    # -- interface --
    def create(self, spec: Dict[str, object], owner: str, now_iso: str,
               deal_id: Optional[str] = None, status: str = "draft") -> DealRecord:
        deal_id = deal_id or uuid.uuid4().hex
        idx = _index_from_spec(spec)
        rec = DealRecord(
            deal_id=deal_id, spec=spec, version=1, owner=owner, status=status,
            created_at=now_iso, updated_at=now_iso, **idx,
        )
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO deals (deal_id, spec_json, version, slug, deal_name, routing, "
                    "mode, status, owner, created_at, updated_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (rec.deal_id, json.dumps(rec.spec), rec.version, rec.slug, rec.deal_name,
                     rec.routing, rec.mode, rec.status, rec.owner, rec.created_at, rec.updated_at),
                )
                self._conn.commit()
            except sqlite3.IntegrityError as e:
                raise ValueError(f"deal_id '{deal_id}' already exists") from e
        return rec

    def get(self, deal_id: str) -> DealRecord:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM deals WHERE deal_id=?", (deal_id,)
            ).fetchone()
        if row is None:
            raise DealNotFound(deal_id)
        return self._row_to_record(row)

    def put(self, deal_id: str, spec: Dict[str, object], expected_version: int,
            now_iso: str, status: Optional[str] = None,
            owner: Optional[str] = None) -> DealRecord:
        idx = _index_from_spec(spec)
        with self._lock:
            row = self._conn.execute(
                "SELECT version, status, owner FROM deals WHERE deal_id=?", (deal_id,)
            ).fetchone()
            if row is None:
                raise DealNotFound(deal_id)
            stored_version = row["version"]
            if stored_version != expected_version:
                raise VersionConflict(deal_id, expected_version, stored_version)
            new_version = stored_version + 1
            new_status = status if status is not None else row["status"]
            new_owner = owner if owner is not None else row["owner"]
            self._conn.execute(
                "UPDATE deals SET spec_json=?, version=?, slug=?, deal_name=?, routing=?, "
                "mode=?, status=?, owner=?, updated_at=? WHERE deal_id=? AND version=?",
                (json.dumps(spec), new_version, idx["slug"], idx["deal_name"], idx["routing"],
                 idx["mode"], new_status, new_owner, now_iso, deal_id, expected_version),
            )
            self._conn.commit()
            row = self._conn.execute("SELECT * FROM deals WHERE deal_id=?", (deal_id,)).fetchone()
        return self._row_to_record(row)

    def list(self, owner: Optional[str] = None, routing: Optional[str] = None,
             status: Optional[str] = None) -> List[DealRecord]:
        clauses, params = [], []
        if owner is not None:
            clauses.append("owner=?"); params.append(owner)
        if routing is not None:
            clauses.append("routing=?"); params.append(routing)
        if status is not None:
            clauses.append("status=?"); params.append(status)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM deals{where} ORDER BY updated_at DESC", params
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def delete(self, deal_id: str) -> None:
        with self._lock:
            cur = self._conn.execute("DELETE FROM deals WHERE deal_id=?", (deal_id,))
            self._conn.commit()
        if cur.rowcount == 0:
            raise DealNotFound(deal_id)


# ---------------------------------------------------------------------------
# Singleton accessor (the app's one entry point to persistence)
# ---------------------------------------------------------------------------

_store: Optional[DealStore] = None


def get_deal_store() -> DealStore:
    """Return the process-wide DealStore. Path from DREAM_DB_PATH env (default: ./dream_deals.db).
    Swap to a Postgres implementation here in Wave F.2 — callers never change."""
    global _store
    if _store is None:
        path = os.environ.get("DREAM_DB_PATH", os.path.join(os.getcwd(), "dream_deals.db"))
        _store = SQLiteDealStore(path)
    return _store
