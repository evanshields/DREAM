"""
backend/store/crm_store.py — Phase 5 CRM persistence (contacts + tasks/notes + links).

The app had deals and jobs but no way to record WHO is on a deal (the broker, the seller, the bond
counsel) or what still has to happen (a task, a note). This module owns that CRM layer, following
DealStore/JobStore's pattern exactly:

  * The canonical record is an OPAQUE JSON document (a contact doc, a task doc, a note doc). A thin
    relational index (kind, name/role/status/due, timestamps) is DERIVED from it for listing and
    filtering — never a second source of truth. The doc round-trips byte-for-byte.

  * ONE store, three tables, each row discriminated by a `kind` column (Evan's decision — not four
    sibling stores):
      - `crm_contacts`  kind ∈ {'person','company'}. Persons carry a DREAM-native `role`
                        ∈ {broker, seller, lender, bond_counsel, issuer, nonprofit_sponsor, other}
                        (issuer + nonprofit_sponsor serve EFB 501(c)(3) bond deals).
      - `crm_items`     kind ∈ {'task','note'}.
      - `crm_links`     an index-only join: (source_kind, source_id) --> (target_kind, target_id).
                        This is how a contact / task / note gets pinned to a deal (or to each other).
                        The simplified target-pointer pattern (plain columns, matched at query time,
                        no DB-enforced FK), adapted from Twenty's TaskTarget/NoteTarget join —
                        INSPIRATION ONLY, retyped in DREAM's naming; no Twenty source copied.

  * NO sqlite3 import here (architectural guard: test_deal_store.test_no_sqlite_or_filepath_
    outside_store). The connection comes from the store package (open_sqlite / default_db_path) so
    contacts + items + links + deals + jobs share ONE DB file and the Wave F Postgres swap stays a
    single-package change.

  * Optimistic concurrency: every contact/item row carries an integer `version`; put() takes the
    version the caller last read and raises the shared `VersionConflict` on a mismatch (re-use the
    deal store's error — do NOT redefine it). Link rows are immutable (create/delete only).

  * Timestamps are passed IN (`now_iso`); this module never calls a clock — deterministic and
    testable, consistent with DealStore/JobStore.

The CRM layer touches no financial math and never writes a deal spec (locked contract: the spec is
canonical; CRM records are their OWN canonical docs). A CRM bug can never corrupt a deal's numbers.
"""
from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

# DB driver + shared error come from the store package ONLY (architectural guard). Re-using
# VersionConflict (not redefining it) keeps a single lost-update exception across every store.
from .deal_store import open_sqlite, default_db_path, VersionConflict


# ---------------------------------------------------------------------------
# Vocabulary (retyped from Twenty's standard objects as a field checklist; DREAM-named)
# ---------------------------------------------------------------------------

CONTACT_KINDS = ("person", "company")
ITEM_KINDS = ("task", "note")
TASK_STATUSES = ("open", "done")
# DREAM-native role enum (Evan, 2026-07-13). issuer + nonprofit_sponsor serve EFB bond deals.
CONTACT_ROLES = (
    "broker", "seller", "lender", "bond_counsel", "issuer", "nonprofit_sponsor", "other",
)
# The entity kinds a link may point at. 'deal' is the primary target (pin a contact/note/task to a
# deal); contact/item let a note attach to a person, etc. Kept permissive — the store does not
# enforce that a target exists (a link is an index, not an FK), the router decides what to expose.
LINKABLE_KINDS = ("deal", "contact", "task", "note")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ContactNotFound(KeyError):
    """Raised by get_contact()/put_contact()/delete_contact() when the contact_id is unknown."""


class ItemNotFound(KeyError):
    """Raised by get_item()/put_item()/delete_item() when the item_id is unknown."""


# ---------------------------------------------------------------------------
# Records (opaque doc + derived index fields)
# ---------------------------------------------------------------------------

@dataclass
class ContactRecord:
    """One persisted contact (person or company): the opaque doc + its derived index."""
    contact_id: str
    doc: Dict[str, Any]              # canonical contact document (opaque)
    version: int = 1
    # --- derived index (read off the doc; never authored independently) ---
    kind: str = "person"            # person | company
    name: str = ""                  # person.full_name or company.name
    role: str = ""                  # persons only ('' for companies)
    company_id: str = ""            # persons only (link to a company contact, optional)
    primary_email: str = ""         # persons: emails[0]; companies: domain
    owner: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ItemRecord:
    """One persisted task or note: the opaque doc + its derived index."""
    item_id: str
    doc: Dict[str, Any]             # canonical task/note document (opaque)
    version: int = 1
    # --- derived index ---
    kind: str = "task"             # task | note
    status: str = ""               # tasks: open | done ('' for notes)
    title: str = ""
    due_at: str = ""               # tasks only
    author: str = ""               # notes: author; tasks: assignee (both stored here for the index)
    owner: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class LinkRecord:
    """One immutable link row (index-only): source --> target."""
    link_id: str
    source_kind: str
    source_id: str
    target_kind: str
    target_id: str
    created_at: str = ""


def _index_from_contact(doc: Dict[str, Any]) -> Dict[str, str]:
    """Pull the thin index out of the canonical contact doc. The doc is the source of truth."""
    kind = str(doc.get("kind", "person"))
    if kind == "company":
        return {
            "kind": "company",
            "name": str(doc.get("name", "")),
            "role": "",
            "company_id": "",
            "primary_email": str(doc.get("domain", "")),
        }
    emails = doc.get("emails") or []
    primary = str(emails[0]) if isinstance(emails, list) and emails else ""
    return {
        "kind": "person",
        "name": str(doc.get("full_name", "")),
        "role": str(doc.get("role", "")),
        "company_id": str(doc.get("company_id", "")),
        "primary_email": primary,
    }


def _index_from_item(doc: Dict[str, Any]) -> Dict[str, str]:
    """Pull the thin index out of the canonical task/note doc."""
    kind = str(doc.get("kind", "task"))
    if kind == "note":
        return {
            "kind": "note",
            "status": "",
            "title": str(doc.get("title", "")),
            "due_at": "",
            "author": str(doc.get("author", "")),
        }
    return {
        "kind": "task",
        "status": str(doc.get("status", "open")),
        "title": str(doc.get("title", "")),
        "due_at": str(doc.get("due_at", "")),
        "author": str(doc.get("assignee", "")),
    }


# ---------------------------------------------------------------------------
# Interface (the persistence contract the app depends on; SQLite now, Postgres in Wave F)
# ---------------------------------------------------------------------------

class CRMStore(Protocol):
    """The CRM persistence contract. Nothing outside an implementation imports a DB driver."""

    # contacts
    def create_contact(self, doc: Dict[str, Any], owner: str, now_iso: str,
                        contact_id: Optional[str] = None) -> ContactRecord: ...

    def get_contact(self, contact_id: str) -> ContactRecord: ...

    def put_contact(self, contact_id: str, doc: Dict[str, Any], expected_version: int,
                    now_iso: str, owner: Optional[str] = None) -> ContactRecord: ...

    def list_contacts(self, kind: Optional[str] = None, role: Optional[str] = None,
                       owner: Optional[str] = None) -> List[ContactRecord]: ...

    def delete_contact(self, contact_id: str) -> None: ...

    # items (tasks + notes)
    def create_item(self, doc: Dict[str, Any], owner: str, now_iso: str,
                    item_id: Optional[str] = None) -> ItemRecord: ...

    def get_item(self, item_id: str) -> ItemRecord: ...

    def put_item(self, item_id: str, doc: Dict[str, Any], expected_version: int,
                 now_iso: str, owner: Optional[str] = None) -> ItemRecord: ...

    def list_items(self, kind: Optional[str] = None, status: Optional[str] = None,
                   owner: Optional[str] = None) -> List[ItemRecord]: ...

    def delete_item(self, item_id: str) -> None: ...

    # links
    def create_link(self, source_kind: str, source_id: str, target_kind: str, target_id: str,
                    now_iso: str) -> LinkRecord: ...

    def delete_link(self, link_id: str) -> bool: ...

    def list_links(self, *, source_kind: Optional[str] = None, source_id: Optional[str] = None,
                   target_kind: Optional[str] = None,
                   target_id: Optional[str] = None) -> List[LinkRecord]: ...

    def delete_links_for(self, kind: str, entity_id: str) -> int: ...

    def delete_links_for_target(self, target_kind: str, target_id: str) -> int: ...


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS crm_contacts (
    contact_id    TEXT PRIMARY KEY,
    doc_json      TEXT NOT NULL,        -- opaque canonical contact document
    version       INTEGER NOT NULL,
    kind          TEXT,                 -- person | company
    name          TEXT,
    role          TEXT,                 -- persons only
    company_id    TEXT,
    primary_email TEXT,
    owner         TEXT,
    created_at    TEXT,
    updated_at    TEXT
);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_kind  ON crm_contacts(kind);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_role  ON crm_contacts(role);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_owner ON crm_contacts(owner);

CREATE TABLE IF NOT EXISTS crm_items (
    item_id     TEXT PRIMARY KEY,
    doc_json    TEXT NOT NULL,          -- opaque canonical task/note document
    version     INTEGER NOT NULL,
    kind        TEXT,                   -- task | note
    status      TEXT,                   -- tasks: open | done
    title       TEXT,
    due_at      TEXT,                   -- tasks only
    author      TEXT,                   -- notes.author / tasks.assignee
    owner       TEXT,
    created_at  TEXT,
    updated_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_crm_items_kind   ON crm_items(kind);
CREATE INDEX IF NOT EXISTS idx_crm_items_status ON crm_items(status);
CREATE INDEX IF NOT EXISTS idx_crm_items_owner  ON crm_items(owner);

CREATE TABLE IF NOT EXISTS crm_links (
    link_id     TEXT PRIMARY KEY,
    source_kind TEXT NOT NULL,
    source_id   TEXT NOT NULL,
    target_kind TEXT NOT NULL,
    target_id   TEXT NOT NULL,
    created_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_crm_links_source ON crm_links(source_kind, source_id);
CREATE INDEX IF NOT EXISTS idx_crm_links_target ON crm_links(target_kind, target_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_crm_links_uniq
    ON crm_links(source_kind, source_id, target_kind, target_id);
"""


class SQLiteCRMStore:
    """File-backed (or :memory:) SQLite CRM store. Thread-safe via a single connection + lock,
    mirroring SQLiteDealStore / SQLiteJobStore. The connection is obtained from the store package
    (no sqlite3 import here). ``path=':memory:'`` for tests."""

    def __init__(self, path: str = ":memory:"):
        self._path = path
        self._conn = open_sqlite(path)
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # -- row -> record helpers --------------------------------------------
    @staticmethod
    def _row_to_contact(row) -> ContactRecord:
        return ContactRecord(
            contact_id=row["contact_id"],
            doc=json.loads(row["doc_json"]),
            version=row["version"],
            kind=row["kind"] or "person",
            name=row["name"] or "",
            role=row["role"] or "",
            company_id=row["company_id"] or "",
            primary_email=row["primary_email"] or "",
            owner=row["owner"] or "",
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    @staticmethod
    def _row_to_item(row) -> ItemRecord:
        return ItemRecord(
            item_id=row["item_id"],
            doc=json.loads(row["doc_json"]),
            version=row["version"],
            kind=row["kind"] or "task",
            status=row["status"] or "",
            title=row["title"] or "",
            due_at=row["due_at"] or "",
            author=row["author"] or "",
            owner=row["owner"] or "",
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    @staticmethod
    def _row_to_link(row) -> LinkRecord:
        return LinkRecord(
            link_id=row["link_id"],
            source_kind=row["source_kind"],
            source_id=row["source_id"],
            target_kind=row["target_kind"],
            target_id=row["target_id"],
            created_at=row["created_at"] or "",
        )

    # =====================================================================
    # Contacts
    # =====================================================================
    def create_contact(self, doc: Dict[str, Any], owner: str, now_iso: str,
                        contact_id: Optional[str] = None) -> ContactRecord:
        contact_id = contact_id or uuid.uuid4().hex
        doc = dict(doc)
        doc.setdefault("kind", "person")
        idx = _index_from_contact(doc)
        rec = ContactRecord(
            contact_id=contact_id, doc=doc, version=1, owner=owner,
            created_at=now_iso, updated_at=now_iso, **idx,
        )
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO crm_contacts (contact_id, doc_json, version, kind, name, role, "
                    "company_id, primary_email, owner, created_at, updated_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (rec.contact_id, json.dumps(rec.doc), rec.version, rec.kind, rec.name,
                     rec.role, rec.company_id, rec.primary_email, rec.owner,
                     rec.created_at, rec.updated_at),
                )
                self._conn.commit()
            except Exception as e:  # sqlite3.IntegrityError (driver not imported here) -> dup id
                if "UNIQUE" in str(e) or "PRIMARY KEY" in str(e):
                    raise ValueError(f"contact_id '{contact_id}' already exists") from e
                raise
        return rec

    def get_contact(self, contact_id: str) -> ContactRecord:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM crm_contacts WHERE contact_id=?", (contact_id,)
            ).fetchone()
        if row is None:
            raise ContactNotFound(contact_id)
        return self._row_to_contact(row)

    def put_contact(self, contact_id: str, doc: Dict[str, Any], expected_version: int,
                    now_iso: str, owner: Optional[str] = None) -> ContactRecord:
        doc = dict(doc)
        doc.setdefault("kind", "person")
        idx = _index_from_contact(doc)
        with self._lock:
            row = self._conn.execute(
                "SELECT version, owner FROM crm_contacts WHERE contact_id=?", (contact_id,)
            ).fetchone()
            if row is None:
                raise ContactNotFound(contact_id)
            stored_version = row["version"]
            if stored_version != expected_version:
                raise VersionConflict(contact_id, expected_version, stored_version)
            new_version = stored_version + 1
            new_owner = owner if owner is not None else row["owner"]
            self._conn.execute(
                "UPDATE crm_contacts SET doc_json=?, version=?, kind=?, name=?, role=?, "
                "company_id=?, primary_email=?, owner=?, updated_at=? "
                "WHERE contact_id=? AND version=?",
                (json.dumps(doc), new_version, idx["kind"], idx["name"], idx["role"],
                 idx["company_id"], idx["primary_email"], new_owner, now_iso,
                 contact_id, expected_version),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM crm_contacts WHERE contact_id=?", (contact_id,)
            ).fetchone()
        return self._row_to_contact(row)

    def list_contacts(self, kind: Optional[str] = None, role: Optional[str] = None,
                      owner: Optional[str] = None) -> List[ContactRecord]:
        clauses, params = [], []
        if kind is not None:
            clauses.append("kind=?"); params.append(kind)
        if role is not None:
            clauses.append("role=?"); params.append(role)
        if owner is not None:
            clauses.append("owner=?"); params.append(owner)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM crm_contacts{where} ORDER BY updated_at DESC", params
            ).fetchall()
        return [self._row_to_contact(r) for r in rows]

    def delete_contact(self, contact_id: str) -> None:
        """Delete a contact AND every link it is an endpoint of (cascade — no orphaned links)."""
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM crm_contacts WHERE contact_id=?", (contact_id,)
            )
            if cur.rowcount == 0:
                self._conn.commit()
                raise ContactNotFound(contact_id)
            self._conn.execute(
                "DELETE FROM crm_links WHERE (source_kind='contact' AND source_id=?) "
                "OR (target_kind='contact' AND target_id=?)",
                (contact_id, contact_id),
            )
            self._conn.commit()

    # =====================================================================
    # Items (tasks + notes)
    # =====================================================================
    def create_item(self, doc: Dict[str, Any], owner: str, now_iso: str,
                    item_id: Optional[str] = None) -> ItemRecord:
        item_id = item_id or uuid.uuid4().hex
        doc = dict(doc)
        doc.setdefault("kind", "task")
        if doc["kind"] == "task":
            doc.setdefault("status", "open")
        idx = _index_from_item(doc)
        rec = ItemRecord(
            item_id=item_id, doc=doc, version=1, owner=owner,
            created_at=now_iso, updated_at=now_iso, **idx,
        )
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO crm_items (item_id, doc_json, version, kind, status, title, "
                    "due_at, author, owner, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (rec.item_id, json.dumps(rec.doc), rec.version, rec.kind, rec.status,
                     rec.title, rec.due_at, rec.author, rec.owner, rec.created_at, rec.updated_at),
                )
                self._conn.commit()
            except Exception as e:
                if "UNIQUE" in str(e) or "PRIMARY KEY" in str(e):
                    raise ValueError(f"item_id '{item_id}' already exists") from e
                raise
        return rec

    def get_item(self, item_id: str) -> ItemRecord:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM crm_items WHERE item_id=?", (item_id,)
            ).fetchone()
        if row is None:
            raise ItemNotFound(item_id)
        return self._row_to_item(row)

    def put_item(self, item_id: str, doc: Dict[str, Any], expected_version: int,
                 now_iso: str, owner: Optional[str] = None) -> ItemRecord:
        doc = dict(doc)
        doc.setdefault("kind", "task")
        if doc["kind"] == "task":
            doc.setdefault("status", "open")
        idx = _index_from_item(doc)
        with self._lock:
            row = self._conn.execute(
                "SELECT version, owner FROM crm_items WHERE item_id=?", (item_id,)
            ).fetchone()
            if row is None:
                raise ItemNotFound(item_id)
            stored_version = row["version"]
            if stored_version != expected_version:
                raise VersionConflict(item_id, expected_version, stored_version)
            new_version = stored_version + 1
            new_owner = owner if owner is not None else row["owner"]
            self._conn.execute(
                "UPDATE crm_items SET doc_json=?, version=?, kind=?, status=?, title=?, "
                "due_at=?, author=?, owner=?, updated_at=? WHERE item_id=? AND version=?",
                (json.dumps(doc), new_version, idx["kind"], idx["status"], idx["title"],
                 idx["due_at"], idx["author"], new_owner, now_iso, item_id, expected_version),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM crm_items WHERE item_id=?", (item_id,)
            ).fetchone()
        return self._row_to_item(row)

    def list_items(self, kind: Optional[str] = None, status: Optional[str] = None,
                   owner: Optional[str] = None) -> List[ItemRecord]:
        clauses, params = [], []
        if kind is not None:
            clauses.append("kind=?"); params.append(kind)
        if status is not None:
            clauses.append("status=?"); params.append(status)
        if owner is not None:
            clauses.append("owner=?"); params.append(owner)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM crm_items{where} ORDER BY updated_at DESC", params
            ).fetchall()
        return [self._row_to_item(r) for r in rows]

    def delete_item(self, item_id: str) -> None:
        """Delete a task/note AND every link it is an endpoint of (cascade)."""
        with self._lock:
            cur = self._conn.execute("DELETE FROM crm_items WHERE item_id=?", (item_id,))
            if cur.rowcount == 0:
                self._conn.commit()
                raise ItemNotFound(item_id)
            self._conn.execute(
                "DELETE FROM crm_links WHERE (source_kind IN ('task','note') AND source_id=?) "
                "OR (target_kind IN ('task','note') AND target_id=?)",
                (item_id, item_id),
            )
            self._conn.commit()

    # =====================================================================
    # Links (immutable index rows: source --> target)
    # =====================================================================
    def create_link(self, source_kind: str, source_id: str, target_kind: str, target_id: str,
                    now_iso: str) -> LinkRecord:
        """Pin source --> target. IDEMPOTENT: an identical link already present returns the
        EXISTING row (the UNIQUE index guards a double-attach; re-attaching is not an error)."""
        with self._lock:
            existing = self._conn.execute(
                "SELECT * FROM crm_links WHERE source_kind=? AND source_id=? AND target_kind=? "
                "AND target_id=?", (source_kind, source_id, target_kind, target_id),
            ).fetchone()
            if existing is not None:
                return self._row_to_link(existing)
            rec = LinkRecord(
                link_id=uuid.uuid4().hex, source_kind=source_kind, source_id=source_id,
                target_kind=target_kind, target_id=target_id, created_at=now_iso,
            )
            self._conn.execute(
                "INSERT INTO crm_links (link_id, source_kind, source_id, target_kind, target_id, "
                "created_at) VALUES (?,?,?,?,?,?)",
                (rec.link_id, rec.source_kind, rec.source_id, rec.target_kind, rec.target_id,
                 rec.created_at),
            )
            self._conn.commit()
        return rec

    def delete_link(self, link_id: str) -> bool:
        """Detach one link by id. Returns True if a row was removed, False if it did not exist
        (detaching an already-detached link is a no-op, not an error)."""
        with self._lock:
            cur = self._conn.execute("DELETE FROM crm_links WHERE link_id=?", (link_id,))
            self._conn.commit()
        return cur.rowcount > 0

    def list_links(self, *, source_kind: Optional[str] = None, source_id: Optional[str] = None,
                   target_kind: Optional[str] = None,
                   target_id: Optional[str] = None) -> List[LinkRecord]:
        """List links matching any combination of the source/target filters (all optional).
        With no filter, returns every link — used sparingly (tests); real callers scope it."""
        clauses, params = [], []
        if source_kind is not None:
            clauses.append("source_kind=?"); params.append(source_kind)
        if source_id is not None:
            clauses.append("source_id=?"); params.append(source_id)
        if target_kind is not None:
            clauses.append("target_kind=?"); params.append(target_kind)
        if target_id is not None:
            clauses.append("target_id=?"); params.append(target_id)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._lock:
            rows = self._conn.execute(
                f"SELECT * FROM crm_links{where} ORDER BY created_at ASC", params
            ).fetchall()
        return [self._row_to_link(r) for r in rows]

    def delete_links_for(self, kind: str, entity_id: str) -> int:
        """Remove every link where the entity is EITHER endpoint (source or target). Returns the
        count removed. Used by delete_contact/delete_item's cascade and callable directly."""
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM crm_links WHERE (source_kind=? AND source_id=?) "
                "OR (target_kind=? AND target_id=?)",
                (kind, entity_id, kind, entity_id),
            )
            self._conn.commit()
        return cur.rowcount

    def delete_links_for_target(self, target_kind: str, target_id: str) -> int:
        """Remove every link POINTING AT a target (target side only). This is the deal-delete
        cascade hook: deals.py::delete_deal calls delete_links_for_target('deal', deal_id) so a
        deleted deal leaves no dangling CRM links behind. Returns the count removed (0 is fine:
        a deal with no CRM attachments has no links)."""
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM crm_links WHERE target_kind=? AND target_id=?",
                (target_kind, target_id),
            )
            self._conn.commit()
        return cur.rowcount


# ---------------------------------------------------------------------------
# Singleton accessor (the app's one entry point to CRM persistence)
# ---------------------------------------------------------------------------

_crm_store: Optional[SQLiteCRMStore] = None


def get_crm_store() -> CRMStore:
    """Process-wide CRMStore. Shares the deal/job DB file (DREAM_DB_PATH) so CRM co-locates with
    deals + jobs. Swap to a Postgres implementation here in Wave F — callers never change."""
    global _crm_store
    if _crm_store is None:
        _crm_store = SQLiteCRMStore(default_db_path())
    return _crm_store
