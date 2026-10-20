"""Durable Mono revision, human event and calculator job persistence.

Filesystem publication and business authorization belong to the service. This
store publishes only fully staged records through a transactional current pointer.
Every operation uses a fresh connection, including independent app instances.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class MonoConflict(Exception):
    """A write conflicts with immutable history or the current revision."""

    def __init__(self, message, current_revision=None):
        super().__init__(message)
        self.current_revision = current_revision


class MonoNotFound(KeyError):
    """The requested deal or deal-scoped job does not exist."""


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _load(row):
    return json.loads(row[0]) if row else None


_SUCCESS = frozenset({"complete", "completed"})
_TERMINAL = _SUCCESS | frozenset({"failed", "blocked", "stale", "cancelled", "canceled", "interrupted", "timed_out"})
_JOB_CHANGES = frozenset({
    "state", "result", "diagnostics", "warnings", "updated_at", "elapsed_seconds",
    "started_at", "finished_at", "completed_at", "cancel_requested", "error",
})


class MonoDealStore:
    """SQLite implementation of the frozen Phase 3 store protocol."""

    def __init__(self, path):
        if str(path) == ":memory:":
            raise ValueError("Mono storage requires a persistent database path")
        self.path = str(Path(path).resolve())
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection(write=True) as db:
            for statement in (
                "CREATE TABLE IF NOT EXISTS mono_deals (deal_id TEXT PRIMARY KEY, revision INTEGER NOT NULL, current_job_id TEXT)",
                "CREATE TABLE IF NOT EXISTS mono_revisions (deal_id TEXT NOT NULL, revision INTEGER NOT NULL, record TEXT NOT NULL, PRIMARY KEY(deal_id, revision), FOREIGN KEY(deal_id) REFERENCES mono_deals(deal_id))",
                "CREATE TABLE IF NOT EXISTS mono_decisions (sequence INTEGER PRIMARY KEY AUTOINCREMENT, deal_id TEXT NOT NULL, revision INTEGER NOT NULL, record TEXT NOT NULL, FOREIGN KEY(deal_id, revision) REFERENCES mono_revisions(deal_id, revision))",
                "CREATE TABLE IF NOT EXISTS mono_idempotency (deal_id TEXT NOT NULL, key TEXT NOT NULL, kind TEXT NOT NULL, digest TEXT NOT NULL, response TEXT NOT NULL, PRIMARY KEY(deal_id, key), FOREIGN KEY(deal_id) REFERENCES mono_deals(deal_id))",
                "CREATE TABLE IF NOT EXISTS mono_jobs (job_id TEXT PRIMARY KEY, deal_id TEXT NOT NULL, revision INTEGER NOT NULL, record TEXT NOT NULL, FOREIGN KEY(deal_id, revision) REFERENCES mono_revisions(deal_id, revision))",
                "CREATE TABLE IF NOT EXISTS mono_gates (sequence INTEGER PRIMARY KEY AUTOINCREMENT, deal_id TEXT NOT NULL, revision INTEGER NOT NULL, gate TEXT NOT NULL, record TEXT NOT NULL, FOREIGN KEY(deal_id, revision) REFERENCES mono_revisions(deal_id, revision))",
            ):
                db.execute(statement)

    @contextmanager
    def _connection(self, write=False):
        db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db
            db.commit()
        except sqlite3.IntegrityError as exc:
            db.rollback()
            raise MonoConflict("Record conflicts with immutable stored history") from exc
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _current(db, deal_id):
        record = _load(db.execute(
            "SELECT r.record FROM mono_revisions r JOIN mono_deals d ON r.deal_id=d.deal_id AND r.revision=d.revision WHERE d.deal_id=?",
            (deal_id,),
        ).fetchone())
        if record is None:
            raise MonoNotFound(deal_id)
        return record

    @staticmethod
    def _revision(db, deal_id, revision):
        record = _load(db.execute(
            "SELECT record FROM mono_revisions WHERE deal_id=? AND revision=?", (deal_id, revision),
        ).fetchone())
        if record is None:
            raise MonoNotFound((deal_id, revision))
        return record

    @staticmethod
    def _record(deal_id, revision_record, revision):
        record = json.loads(_json(revision_record))
        if record.get("deal_id", deal_id) != deal_id or record.get("revision") != revision:
            raise MonoConflict("Revision record scope or number does not match")
        record["deal_id"] = deal_id
        return record

    @staticmethod
    def _replay(db, deal_id, key, kind, digest):
        if not isinstance(key, str) or not key or not isinstance(digest, str) or not digest:
            raise MonoConflict("Idempotency key and request digest are required")
        row = db.execute(
            "SELECT kind, digest, response FROM mono_idempotency WHERE deal_id=? AND key=?", (deal_id, key),
        ).fetchone()
        if row:
            if row[0] != kind or row[1] != digest:
                raise MonoConflict("Idempotency key was already used with a different request")
            return json.loads(row[2])
        return None

    @staticmethod
    def _remember(db, deal_id, key, kind, digest, response):
        db.execute("INSERT INTO mono_idempotency VALUES (?, ?, ?, ?, ?)", (deal_id, key, kind, digest, _json(response)))

    def register(self, deal_id, revision_record):
        record = self._record(deal_id, revision_record, 1)
        with self._connection(write=True) as db:
            exists = db.execute("SELECT revision FROM mono_deals WHERE deal_id=?", (deal_id,)).fetchone()
            if exists:
                original = self._revision(db, deal_id, 1)
                if original != record:
                    raise MonoConflict("Deal is already registered with different inputs", exists[0])
                return self._current(db, deal_id)
            db.execute("INSERT INTO mono_deals VALUES (?, 1, NULL)", (deal_id,))
            db.execute("INSERT INTO mono_revisions VALUES (?, 1, ?)", (deal_id, _json(record)))
            return record

    def current(self, deal_id):
        with self._connection() as db:
            return self._current(db, deal_id)

    def revisions(self, deal_id):
        with self._connection() as db:
            self._current(db, deal_id)
            return [_load(row) for row in db.execute("SELECT record FROM mono_revisions WHERE deal_id=? ORDER BY revision", (deal_id,))]

    def commit_revision(self, deal_id, expected_revision, revision_record, decision, idempotency_key, request_digest):
        with self._connection(write=True) as db:
            replay = self._replay(db, deal_id, idempotency_key, "edit", request_digest)
            if replay is not None:
                return replay
            current = self._current(db, deal_id)
            if current["revision"] != expected_revision:
                raise MonoConflict("Revision changed. Read the current deal before retrying", current["revision"])
            record = self._record(deal_id, revision_record, expected_revision + 1)
            if decision.get("deal_id", deal_id) != deal_id:
                raise MonoConflict("Decision is scoped to a different deal")
            db.execute("INSERT INTO mono_revisions VALUES (?, ?, ?)", (deal_id, expected_revision + 1, _json(record)))
            db.execute("INSERT INTO mono_decisions(deal_id, revision, record) VALUES (?, ?, ?)", (deal_id, expected_revision + 1, _json(decision)))
            changed = db.execute("UPDATE mono_deals SET revision=?, current_job_id=NULL WHERE deal_id=? AND revision=?", (expected_revision + 1, deal_id, expected_revision)).rowcount
            if changed != 1:
                raise MonoConflict("Revision changed during publication", current["revision"])
            self._remember(db, deal_id, idempotency_key, "edit", request_digest, record)
            return record

    def decisions(self, deal_id):
        with self._connection() as db:
            self._current(db, deal_id)
            return [_load(row) for row in db.execute("SELECT record FROM mono_decisions WHERE deal_id=? ORDER BY sequence", (deal_id,))]

    def idempotent_result(self, deal_id, key, kind, digest):
        """Check an authorized request replay before service-level revision validation."""
        with self._connection() as db:
            self._current(db, deal_id)
            return self._replay(db, deal_id, key, kind, digest)

    def add_job(self, deal_id, job_record):
        record = json.loads(_json(job_record))
        if record.get("deal_id", deal_id) != deal_id or not record.get("job_id") or not record.get("state"):
            raise MonoConflict("Job scope, ID and state are required")
        record["deal_id"] = deal_id
        with self._connection(write=True) as db:
            revision = self._revision(db, deal_id, record["revision"])
            if record.get("identity") != revision.get("identity") or "identity" not in record:
                raise MonoConflict("Job identity must match its immutable revision")
            db.execute("INSERT INTO mono_jobs VALUES (?, ?, ?, ?)", (record["job_id"], deal_id, record["revision"], _json(record)))
            return record

    @staticmethod
    def _job(db, deal_id, job_id):
        record = _load(db.execute("SELECT record FROM mono_jobs WHERE deal_id=? AND job_id=?", (deal_id, job_id)).fetchone())
        if record is None:
            raise MonoNotFound((deal_id, job_id))
        return record

    def update_job(self, deal_id, job_id, changes):
        if set(changes) - _JOB_CHANGES:
            raise MonoConflict("Job identity and scope are immutable")
        with self._connection(write=True) as db:
            record = self._job(db, deal_id, job_id)
            updated = {**record, **changes}
            if record["state"] in _TERMINAL and updated != record:
                raise MonoConflict("Terminal job receipts are immutable")
            if not isinstance(updated.get("state"), str) or not updated["state"]:
                raise MonoConflict("Job state is required")
            db.execute("UPDATE mono_jobs SET record=? WHERE deal_id=? AND job_id=?", (_json(updated), deal_id, job_id))
            return updated

    def job(self, deal_id, job_id):
        with self._connection() as db:
            return self._job(db, deal_id, job_id)

    def jobs(self, deal_id):
        with self._connection() as db:
            self._current(db, deal_id)
            return [_load(row) for row in db.execute("SELECT record FROM mono_jobs WHERE deal_id=? ORDER BY rowid", (deal_id,))]

    def promote_result(self, deal_id, job_id, expected_revision, expected_identity):
        with self._connection(write=True) as db:
            current = self._current(db, deal_id)
            job = self._job(db, deal_id, job_id)
            if (current["revision"] != expected_revision or current.get("identity") != expected_identity
                    or job["revision"] != expected_revision or job.get("identity") != expected_identity
                    or job["state"] not in _SUCCESS or not isinstance(job.get("result"), dict)):
                return False
            result = job["result"]
            if not result.get("result_id"):
                return False
            return db.execute("UPDATE mono_deals SET current_job_id=? WHERE deal_id=? AND revision=?", (job_id, deal_id, expected_revision)).rowcount == 1

    def current_result(self, deal_id):
        with self._connection() as db:
            self._current(db, deal_id)
            row = db.execute("SELECT current_job_id FROM mono_deals WHERE deal_id=?", (deal_id,)).fetchone()
            return self._job(db, deal_id, row[0]) if row[0] else None

    def record_gate(self, deal_id, expected_revision, event, idempotency_key, request_digest):
        with self._connection(write=True) as db:
            replay = self._replay(db, deal_id, idempotency_key, "gate", request_digest)
            if replay is not None:
                return replay
            current = self._current(db, deal_id)
            if current["revision"] != expected_revision:
                raise MonoConflict("Gate review is for an older revision", current["revision"])
            if (event.get("deal_id", deal_id) != deal_id
                    or event.get("revision", expected_revision) != expected_revision
                    or event.get("gate") not in {"comps", "go_no_go"}):
                raise MonoConflict("Gate event scope is invalid")
            db.execute("INSERT INTO mono_gates(deal_id, revision, gate, record) VALUES (?, ?, ?, ?)", (deal_id, expected_revision, event["gate"], _json(event)))
            self._remember(db, deal_id, idempotency_key, "gate", request_digest, event)
            return json.loads(_json(event))

    def gates(self, deal_id):
        with self._connection() as db:
            current = self._current(db, deal_id)
            result = {"comps": None, "go_no_go": None}
            for gate, record in db.execute("SELECT gate, record FROM mono_gates WHERE deal_id=? AND revision=? ORDER BY sequence", (deal_id, current["revision"])):
                result[gate] = json.loads(record)
            return result

    def gate_history(self, deal_id):
        with self._connection() as db:
            self._current(db, deal_id)
            return [_load(row) for row in db.execute("SELECT record FROM mono_gates WHERE deal_id=? ORDER BY sequence", (deal_id,))]

    def recover_interrupted(self):
        changed = []
        with self._connection(write=True) as db:
            for job_id, raw in db.execute("SELECT job_id, record FROM mono_jobs").fetchall():
                record = json.loads(raw)
                if record["state"] in _TERMINAL:
                    continue
                record["state"] = "interrupted"
                record["updated_at"] = datetime.now(timezone.utc).isoformat()
                record["diagnostics"] = [*record.get("diagnostics", []), "App restart interrupted calculation. Native ownership and outcome were not proved. No automatic resubmission occurred."]
                db.execute("UPDATE mono_jobs SET record=? WHERE job_id=?", (_json(record), job_id))
                changed.append(job_id)
        return changed
