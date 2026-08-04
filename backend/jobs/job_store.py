"""
backend/jobs/job_store.py — Wave C-v1 JobStore (durable job lifecycle over SQLite).

Mirrors backend/store/deal_store.py's pattern exactly, for JOB records rather than deals:

  * The canonical record is the JobRecord (jobs/contracts.py), persisted as an OPAQUE JSON
    document in a 'jobs' table; a thin relational index (deal_id, status, owner, idempotency_key,
    timestamps) is DERIVED from it for listing/lookup — never a second source of truth.
  * The durable UnderwriteState (state_ledger.UnderwriteState — BL-17 critical inputs + phase
    ledger + parsed-source cache) is serialized as a SECOND opaque JSON column on the same row,
    so the run's resume file lives IN the store, NOT as a loose underwrite-state.json sibling
    (the skill's filesystem-as-database pattern stays out of the server).
  * NO sqlite3 import here. The architectural guard (test_deal_store.test_no_sqlite_or_filepath_
    outside_store) forbids a DB driver outside backend/store; we open the connection through
    store.open_sqlite() so jobs + deals share one DB file and the Postgres swap stays a
    single-package change.

Concurrency: every row carries an integer `version`; transition()/append_audit()/answer use an
optimistic compare-and-set (re-read inside the lock, bump version) so two writers cannot silently
clobber. Idempotency: create_job keys on (idempotency_key) — a retried intake returns the EXISTING
job instead of a duplicate (the chat-bot service may resubmit on a dropped connection).

Timestamps: the caller passes now_iso (this module never calls a clock — deterministic + testable,
consistent with DealStore and the state ledger).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import uuid
from typing import Any, Dict, List, Optional

# --- backend on path (conftest / app also do this) ---------------------------
_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

# DB driver comes from the store package ONLY (architectural guard).
from store import open_sqlite, default_db_path  # noqa: E402

from jobs.contracts import (  # noqa: E402
    JobRecord,
    JobStatus,
    JobPhase,
    OpenQuestion,
    assert_transition,
    ACTIVE_STATUSES,
    TERMINAL_STATUSES,
)

# state_ledger.UnderwriteState (vendored engine fastpath) — the durable resume ledger.
_ENGINE_FASTPATH = os.path.join(
    os.path.dirname(_BACKEND), "underwriting-engine", "fastpath",
)
if _ENGINE_FASTPATH not in sys.path:
    sys.path.insert(0, _ENGINE_FASTPATH)
try:
    from state_ledger import (  # noqa: E402
        UnderwriteState,
        CriticalInputs,
        PhaseRecord,
        ParsedSource,
    )
except Exception:  # pragma: no cover - vendored engine present in normal envs
    UnderwriteState = None  # type: ignore
    CriticalInputs = PhaseRecord = ParsedSource = None  # type: ignore


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class JobNotFound(KeyError):
    """Raised when a job_id does not exist."""


class JobConflict(Exception):
    """Raised on an optimistic-concurrency lost-update (version moved under us)."""

    def __init__(self, job_id: str, expected: int, actual: int):
        super().__init__(
            f"version conflict on job '{job_id}': expected {expected}, stored {actual}"
        )
        self.job_id = job_id
        self.expected = expected
        self.actual = actual


# ---------------------------------------------------------------------------
# UnderwriteState (de)serialization — opaque JSON, no loose files
# ---------------------------------------------------------------------------

def _state_to_json(state: Any) -> Optional[str]:
    if state is None:
        return None
    if isinstance(state, dict):
        return json.dumps(state)
    # dataclass UnderwriteState
    from dataclasses import asdict
    return json.dumps(asdict(state))


def _state_from_json(raw: Optional[str]) -> Any:
    if not raw:
        return None
    d = json.loads(raw)
    if UnderwriteState is None:  # pragma: no cover
        return d
    ci = CriticalInputs(**d.get("critical_inputs", {})) if d.get("critical_inputs") else CriticalInputs()
    ledger = [PhaseRecord(**r) for r in d.get("phase_ledger", [])]
    sources = [ParsedSource(**s) for s in d.get("parsed_sources", [])]
    return UnderwriteState(
        slug=d.get("slug", ""),
        deal_name=d.get("deal_name", ""),
        routing=d.get("routing", ""),
        critical_inputs=ci,
        phase_ledger=ledger,
        parsed_sources=sources,
        updated=d.get("updated", ""),
    )


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id          TEXT PRIMARY KEY,
    doc_json        TEXT NOT NULL,        -- opaque JobRecord.to_dict()
    state_json      TEXT,                 -- opaque UnderwriteState (resume ledger), nullable
    version         INTEGER NOT NULL,
    deal_id         TEXT,
    status          TEXT,
    phase           TEXT,
    owner           TEXT,
    idempotency_key TEXT,
    created_at      TEXT,
    updated_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_owner  ON jobs(owner);
CREATE INDEX IF NOT EXISTS idx_jobs_deal   ON jobs(deal_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_idem ON jobs(idempotency_key)
    WHERE idempotency_key IS NOT NULL AND idempotency_key <> '';
"""


class SQLiteJobStore:
    """File-backed (or :memory:) SQLite job store. Thread-safe via a single connection + lock,
    mirroring SQLiteDealStore. The connection is obtained from the store package (no sqlite3 here)."""

    def __init__(self, path: str = ":memory:"):
        self._path = path
        self._conn = open_sqlite(path)
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # -- index helpers --
    @staticmethod
    def _index(rec: JobRecord) -> Dict[str, str]:
        return {
            "deal_id": rec.deal_id,
            "status": rec.status.value,
            "phase": rec.phase.value,
            "owner": rec.owner,
            "idempotency_key": rec.idempotency_key or "",
            "created_at": rec.created_at,
            "updated_at": rec.updated_at,
        }

    def _insert(self, rec: JobRecord, state: Any) -> None:
        idx = self._index(rec)
        self._conn.execute(
            "INSERT INTO jobs (job_id, doc_json, state_json, version, deal_id, status, phase, "
            "owner, idempotency_key, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (rec.job_id, json.dumps(rec.to_dict()), _state_to_json(state), 1,
             idx["deal_id"], idx["status"], idx["phase"], idx["owner"],
             idx["idempotency_key"], idx["created_at"], idx["updated_at"]),
        )
        self._conn.commit()

    def _row_version(self, job_id: str) -> int:
        row = self._conn.execute("SELECT version FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise JobNotFound(job_id)
        return row["version"]

    def _read_locked(self, job_id: str) -> tuple[JobRecord, Any, int]:
        row = self._conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise JobNotFound(job_id)
        rec = JobRecord.from_dict(json.loads(row["doc_json"]))
        state = _state_from_json(row["state_json"])
        return rec, state, row["version"]

    def _write_locked(self, rec: JobRecord, state: Any, expected_version: int) -> JobRecord:
        actual = self._row_version(rec.job_id)
        if actual != expected_version:
            raise JobConflict(rec.job_id, expected_version, actual)
        idx = self._index(rec)
        self._conn.execute(
            "UPDATE jobs SET doc_json=?, state_json=?, version=?, deal_id=?, status=?, phase=?, "
            "owner=?, idempotency_key=?, updated_at=? WHERE job_id=? AND version=?",
            (json.dumps(rec.to_dict()), _state_to_json(state), expected_version + 1,
             idx["deal_id"], idx["status"], idx["phase"], idx["owner"],
             idx["idempotency_key"], idx["updated_at"], rec.job_id, expected_version),
        )
        self._conn.commit()
        return rec

    # -- public API --
    def create_job(self, deal_id: str, routing: str, owner: str, now_iso: str,
                   idempotency_key: str = "") -> JobRecord:
        """Create a SUBMITTED job. IDEMPOTENT: a non-empty idempotency_key already present returns
        the EXISTING job (a retried intake never spawns a duplicate)."""
        with self._lock:
            if idempotency_key:
                row = self._conn.execute(
                    "SELECT doc_json FROM jobs WHERE idempotency_key=?", (idempotency_key,)
                ).fetchone()
                if row is not None:
                    return JobRecord.from_dict(json.loads(row["doc_json"]))
            rec = JobRecord(
                job_id=uuid.uuid4().hex,
                deal_id=deal_id,
                routing=(routing or "ACQ").upper(),
                status=JobStatus.SUBMITTED,
                phase=JobPhase.WAVE0_ROUTING,
                created_at=now_iso,
                updated_at=now_iso,
                owner=owner,
                idempotency_key=idempotency_key,
            )
            self._insert(rec, None)
            return rec

    def find_by_idempotency(self, idempotency_key: str) -> Optional[JobRecord]:
        """Return the existing job for a non-empty idempotency key, else None. Lets the router
        detect a replay BEFORE creating any deal record (a retry must never orphan a deal)."""
        if not idempotency_key:
            return None
        with self._lock:
            row = self._conn.execute(
                "SELECT doc_json FROM jobs WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
        return JobRecord.from_dict(json.loads(row["doc_json"])) if row is not None else None

    def get_job(self, job_id: str) -> JobRecord:
        with self._lock:
            rec, _state, _v = self._read_locked(job_id)
        return rec

    def get_state(self, job_id: str) -> Any:
        """The durable UnderwriteState resume ledger for this job (or None if never set)."""
        with self._lock:
            _rec, state, _v = self._read_locked(job_id)
        return state

    def save_state(self, job_id: str, state: Any) -> None:
        """Persist the UnderwriteState resume ledger (opaque JSON column; no loose file)."""
        with self._lock:
            rec, _old, version = self._read_locked(job_id)
            self._write_locked(rec, state, version)

    def list_jobs(self, owner: Optional[str] = None, status: Optional[str] = None,
                  deal_id: Optional[str] = None) -> List[JobRecord]:
        clauses, params = [], []
        if owner is not None:
            clauses.append("owner=?"); params.append(owner)
        if status is not None:
            clauses.append("status=?"); params.append(status)
        if deal_id is not None:
            clauses.append("deal_id=?"); params.append(deal_id)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._lock:
            rows = self._conn.execute(
                f"SELECT doc_json FROM jobs{where} ORDER BY updated_at DESC", params
            ).fetchall()
        return [JobRecord.from_dict(json.loads(r["doc_json"])) for r in rows]

    def delete_for_deal(self, deal_id: str) -> int:
        """Hard-delete every job row for a deal (the deal-delete cascade — a deleted deal must
        leave no orphaned jobs/audit behind). Returns the number of rows removed (0 is fine:
        a never-run deal has no jobs). Same connection/lock discipline as the neighbors —
        NO sqlite3 import here (architectural guard)."""
        with self._lock:
            cur = self._conn.execute("DELETE FROM jobs WHERE deal_id=?", (deal_id,))
            self._conn.commit()
        return cur.rowcount

    def transition(self, job_id: str, new_status: JobStatus, now_iso: str,
                   phase: Optional[JobPhase] = None, error: Optional[str] = None) -> JobRecord:
        """Move the job to new_status, enforcing the contracts state machine (assert_transition
        raises InvalidTransition on an illegal change — fail closed). Optionally advances phase
        and records an error string (set when new_status == FAILED)."""
        with self._lock:
            rec, state, version = self._read_locked(job_id)
            assert_transition(rec.status, new_status)  # raises InvalidTransition if illegal
            rec.status = new_status
            if phase is not None:
                rec.phase = phase
            if error is not None:
                rec.error = error
            rec.updated_at = now_iso
            return self._write_locked(rec, state, version)

    def request_cancel(self, job_id: str, now_iso: str = "") -> JobRecord:
        """Set the cooperative cancel flag (honored at the next runner checkpoint). No-op /
        idempotent on a terminal job."""
        with self._lock:
            rec, state, version = self._read_locked(job_id)
            if rec.status in TERMINAL_STATUSES:
                return rec
            rec.cancel_requested = True
            if now_iso:
                rec.updated_at = now_iso
            return self._write_locked(rec, state, version)

    def append_audit(self, job_id: str, kind: str, summary: str,
                     detail: Optional[Dict[str, Any]] = None, ts: str = "") -> JobRecord:
        """Append one AuditEvent (monotonic seq, supplied ts). Append-only, like the Claude Log."""
        with self._lock:
            rec, state, version = self._read_locked(job_id)
            rec.add_audit(kind, summary, detail=detail, ts=ts)  # validates kind
            if ts:
                rec.updated_at = ts
            return self._write_locked(rec, state, version)

    def add_open_question(self, job_id: str, q: OpenQuestion, now_iso: str = "") -> JobRecord:
        with self._lock:
            rec, state, version = self._read_locked(job_id)
            rec.add_open_question(q)
            if now_iso:
                rec.updated_at = now_iso
            return self._write_locked(rec, state, version)

    def answer_open_question(self, job_id: str, question_id: str, answer: Any,
                             now_iso: str = "") -> JobRecord:
        """Record a human answer to an OpenQuestion (marks it answered + stores the value).
        Raises KeyError if the question_id is not on this job."""
        with self._lock:
            rec, state, version = self._read_locked(job_id)
            found = False
            for q in rec.open_questions:
                if q.id == question_id:
                    q.answered = True
                    q.answer = answer
                    found = True
                    break
            if not found:
                raise KeyError(f"open question '{question_id}' not found on job '{job_id}'")
            if now_iso:
                rec.updated_at = now_iso
            return self._write_locked(rec, state, version)


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_job_store: Optional[SQLiteJobStore] = None


def get_job_store() -> SQLiteJobStore:
    """Process-wide JobStore. Shares the deal DB file (DREAM_DB_PATH) so jobs + deals co-locate.
    Swap to a Postgres implementation here in Wave F.2 — callers never change."""
    global _job_store
    if _job_store is None:
        _job_store = SQLiteJobStore(default_db_path())
    return _job_store
