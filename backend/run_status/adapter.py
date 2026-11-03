"""Maps one engine run record (run/run.json, plus run/bote.json when present) into the run status view shape.

Pure Python. No arithmetic on any value: headline values are passed through exactly as stored,
and the only thing computed is a file hash for evidence (bytes, not a financial value).
Fails closed: a missing or unknown field shows as missing, never as complete.

Engine record, as written by dream-underwrite run.py:
  {slug, route, ran, stop_after, force, stages: [{stage, name, status, why|error|waiting_on+what_to_do|wrote|print}],
   failed: [stage numbers], waiting: [stage numbers]}
Stage statuses the engine writes: ok, skipped, failed, waiting, blocked.
The engine does not write an engine commit or inputs hash today. They are carried through when present
and shown as missing when absent, which the view treats as stale (unverifiable).
The engine also writes no output fingerprints today. When the record carries `output_sha256`
({file name: sha256}) each artifact is compared against it. Without it a present file is only "unverified".

Fail closed: complete needs exactly stages 1 to 8 once each, all ok, typed empty failed and waiting lists,
a boolean force, a null stop_after, well formed wrote lists, and bote.json written by stage 7, readable, and
matching its recorded fingerprint. Anything else is never complete.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path, PureWindowsPath
from typing import Any, Optional

MISSING = "missing"

# Supported engine record: eight stages, stage 7 writes bote.json. Route does not change the set today.
EXPECTED_STAGES = tuple(range(1, 9))
BOTE_STAGE = 7
BOTE_FILE = "bote.json"
# Evidence limits: bytes hashed per artifact, artifacts per run, chunk size. Over-limit evidence is never opened.
MAX_EVIDENCE_BYTES = 25_000_000
MAX_EVIDENCE_ITEMS = 32
_CHUNK = 1 << 16
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")

# Headline rows: (name, unit, bote.json pointer as path parts). Values are read, never computed.
HEADLINE_SPEC = (
    ("Purchase price", "usd", ("price",)),
    ("Year 1 net operating income", "usd", ("projection", "years", 0, "noi")),
    ("Bridge coverage (exempt)", "ratio", ("stack", "coverage", "bridge", "dscr_exempt")),
    ("Takeout coverage (exempt)", "ratio", ("stack", "coverage", "takeout", "dscr_exempt")),
    ("Return (IRR)", "ratio", ("stack", "irr")),
)

_ABSENT = object()


def _pointer(parts: tuple) -> str:
    return "".join(f"/{p}" for p in parts)


def _dig(doc: Any, parts: tuple) -> Any:
    cur = doc
    for p in parts:
        if isinstance(p, int):
            if not isinstance(cur, list) or p >= len(cur):
                return _ABSENT
            cur = cur[p]
        else:
            if not isinstance(cur, dict) or p not in cur:
                return _ABSENT
            cur = cur[p]
    return cur


def _text(value: Any) -> str:
    return value if isinstance(value, str) and value.strip() else ""


def _valid_number(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _stage_gate(stage: Any, gid: str) -> dict[str, Any]:
    if not isinstance(stage, dict):
        return {"id": gid, "name": "Unreadable stage record", "status": MISSING,
                "detail": "This stage record could not be read."}
    name = _text(stage.get("name")) or "Unnamed stage"
    status = stage.get("status")
    if status == "ok":
        return {"id": gid, "name": name, "status": "green", "detail": "Stage finished."}
    if status == "failed":
        return {"id": gid, "name": name, "status": "red",
                "detail": _text(stage.get("error")) or "Stage failed. The engine gave no reason."}
    if status == "skipped":
        reason = _text(stage.get("why")) or "No reason recorded."
        return {"id": gid, "name": name, "status": "amber", "detail": f"Skipped: {reason}"}
    if status == "waiting":
        who = _text(stage.get("waiting_on")) or "someone"
        todo = _text(stage.get("what_to_do"))
        return {"id": gid, "name": name, "status": "not_run",
                "detail": f"Waiting on {who}. {todo}".strip()}
    if status == "blocked":
        return {"id": gid, "name": name, "status": "not_run",
                "detail": _text(stage.get("why")) or "Blocked by an earlier stage."}
    return {"id": gid, "name": name, "status": MISSING, "detail": "Stage status missing or not recognised."}


def _gate_ids(stages: list[Any]) -> list[str]:
    """Unique id per stage. A repeated or unreadable stage number gets an index suffix, never a shared id."""
    ids, seen = [], set()
    for i, s in enumerate(stages):
        n = s.get("stage") if isinstance(s, dict) else None
        gid = f"stage-{n}" if _valid_number(n) else f"stage-unknown-{i}"
        if gid in seen:
            gid = f"{gid}-dup{i}"
        seen.add(gid)
        ids.append(gid)
    return ids


def _stage_set_problem(stages: list[Any]) -> Optional[str]:
    """None when the stages are exactly the expected set, once each. Otherwise what is wrong."""
    numbers = [s.get("stage") if isinstance(s, dict) else None for s in stages]
    if not all(_valid_number(n) for n in numbers):
        return "A stage record has a missing or invalid stage number."
    if len(set(numbers)) != len(numbers):
        return "The run record repeats a stage number."
    absent = [n for n in EXPECTED_STAGES if n not in numbers]
    extra = [n for n in numbers if n not in EXPECTED_STAGES]
    if absent:
        return f"The run record has no stage {', '.join(str(n) for n in absent)}."
    if extra:
        return f"The run record has an unexpected stage {', '.join(str(n) for n in extra)}."
    return None


def _sha256_file(path: Path) -> str:
    """sha256 of a file read in bounded chunks."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_bounded(path: Path) -> Optional[str]:
    """sha256 of the bytes read now, or None when the file is over MAX_EVIDENCE_BYTES (checked without opening it).

    Deliberately not cached: a cache keyed on size and modified time can return an old digest for changed bytes
    that kept the same size and time. The hash is always of what is on disk at the moment of the call.
    """
    if path.stat().st_size > MAX_EVIDENCE_BYTES:
        return None
    return _sha256_file(path)


def _expected_hashes(record: dict[str, Any]) -> dict[str, str]:
    """The run's own recorded fingerprints, or {} when absent or malformed (nothing is then verifiable)."""
    raw = record.get("output_sha256")
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if isinstance(k, str) and isinstance(v, str) and _SHA_RE.fullmatch(v)}


def _evidence(stages: list[Any], run_dir: Optional[Path], expected: dict[str, str],
              bote_problem: Optional[str], bote_sha256: Optional[str] = None) -> list[dict[str, Any]]:
    """One item per file a finished stage says it wrote.

    States: ok (matches the run's recorded fingerprint), hash_mismatch (differs from it), unverified (present, but
    there is no usable recorded fingerprint or it is over the size limit), missing, unreadable (rejected by the JSON
    loader), invalid (malformed wrote entry, duplicate name, or past the item limit). Only ok verifies.
    """
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(name: str, path: str, digest: str, state: str, why: str = "") -> None:
        item = {"name": name, "path": path, "sha256": digest, "state": state}
        if why:
            item["detail"] = why
        items.append(item)

    for stage in stages:
        if not isinstance(stage, dict) or stage.get("status") != "ok":
            continue
        n = stage.get("stage")
        if "wrote" in stage and not isinstance(stage.get("wrote"), list):
            add(f"stage {n} wrote list", f"run/stage-{n}-wrote-invalid-{len(items)}", "", "invalid",
                "The wrote entry is not a list.")
            continue
        for raw in stage.get("wrote") or []:
            if not isinstance(raw, str) or not raw.strip():
                add(f"stage {n} wrote entry", f"run/stage-{n}-wrote-invalid-{len(items)}", "", "invalid",
                    "A wrote entry is not a file name.")
                continue
            # Engine paths come from another machine, so only the file name is used, inside run_dir.
            fname = PureWindowsPath(raw).name
            if len(items) >= MAX_EVIDENCE_ITEMS:
                add(fname or "unnamed", f"run/{fname}#over-limit-{len(items)}", "", "invalid",
                    "More evidence files than the per-run limit.")
                continue
            if fname in seen:
                add(fname, f"run/{fname}#duplicate-{len(items)}", "", "invalid", "This file is listed more than once.")
                continue
            seen.add(fname)
            digest, state = "", "missing"
            if run_dir is not None and fname and fname not in (".", ".."):
                p = run_dir.joinpath(fname)
                try:
                    if p.is_file() and not p.is_symlink() and p.resolve().parent == run_dir:
                        if fname == BOTE_FILE and bote_problem:
                            state = "unreadable"
                        else:
                            state = "unverified"
                            want = expected.get(fname)
                            if want is not None:
                                # bote.json: the digest of the very bytes the loader parsed for the headline.
                                within = p.stat().st_size <= MAX_EVIDENCE_BYTES
                                got = bote_sha256 if (fname == BOTE_FILE and bote_sha256 and within) else _hash_bounded(p)
                                if got is not None:
                                    digest = got
                                    state = "ok" if got == want else "hash_mismatch"
                except OSError:
                    state = "missing"
            add(fname, f"run/{fname}", digest, state)
    return items


def _headline(bote: Optional[dict[str, Any]], bote_problem: Optional[str] = None) -> list[dict[str, Any]]:
    rows = []
    for name, unit, parts in HEADLINE_SPEC:
        value = _dig(bote, parts) if isinstance(bote, dict) and not bote_problem else _ABSENT
        value_out, reason = None, None
        if bote_problem:
            reason = f"bote.json was rejected: {bote_problem}"
        elif value is _ABSENT:
            reason = "No bote.json for this run." if not isinstance(bote, dict) else "Not present in bote.json."
        elif value is None:
            reason = "bote.json stores no figure here (null)."
        elif isinstance(value, bool) or not isinstance(value, (int, float, str)):
            reason = "bote.json holds something other than a number or text here."
        else:
            value_out = value
        rows.append({"name": name, "value": value_out, "unit": unit, "blank_reason": reason,
                     "source_file": "bote.json", "source_pointer": _pointer(parts)})
    return rows


def _status(record: dict[str, Any], stages: list[Any], gates: list[dict[str, Any]],
            stage_problem: Optional[str], record_problem: Optional[str]) -> str:
    """completed only when exactly the expected stages are all ok, the run was not cut short, and nothing failed or waits."""
    statuses = [g["status"] for g in gates]
    if MISSING in statuses:
        return "unreadable"
    if "red" in statuses or (isinstance(record.get("failed"), list) and record["failed"]):
        return "stopped"
    if "not_run" in statuses or (isinstance(record.get("waiting"), list) and record["waiting"]):
        return "awaiting_input"
    if not stages or record.get("stop_after") is not None:
        return "partial"
    if "amber" in statuses:
        return "partial"  # a skipped stage did not run this time, so the run is not shown as complete
    if record_problem or stage_problem:
        return "unreadable"
    if not isinstance(record.get("failed"), list) or not isinstance(record.get("waiting"), list):
        return "unreadable"  # the engine always writes both lists; anything else is an unreadable record
    if not isinstance(record.get("force"), bool):
        return "unreadable"
    return "completed"


def _bote_problem_text(stages: list[Any]) -> Optional[str]:
    """Stage 7 must be ok and must list bote.json among the files it wrote."""
    for st in stages:
        if isinstance(st, dict) and st.get("stage") == BOTE_STAGE:
            wrote = st.get("wrote")
            names = [PureWindowsPath(w).name for w in wrote if isinstance(w, str)] if isinstance(wrote, list) else []
            if st.get("status") == "ok" and BOTE_FILE not in names:
                return "Stage 7 finished but does not say it wrote bote.json."
    return None


def adapt_engine_run(
    record: Any,
    bote: Any = None,
    run_id: str = "",
    run_dir: Optional[Path] = None,
    current_engine_commit: Optional[str] = None,
    current_inputs_hash: Optional[str] = None,
    record_problem: Optional[str] = None,
    bote_problem: Optional[str] = None,
    bote_sha256: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Return a view-shaped run dict, or None when the record is not a JSON object.

    record_problem: the loader found the run record malformed (for example a repeated key). Never complete.
    bote_sha256: sha256 of the exact bote.json bytes the loader parsed, so the shown hash matches the shown numbers.
    bote_problem: bote.json exists but the loader rejected it (bad JSON, not an object, too large, repeated key).
    """
    if not isinstance(record, dict):
        return None
    raw_stages = record.get("stages")
    stages = raw_stages if isinstance(raw_stages, list) else []
    ids = _gate_ids(stages)
    gates = [_stage_gate(s, gid) for s, gid in zip(stages, ids)]
    if not isinstance(raw_stages, list):
        gates = [{"id": "stages", "name": "Stage list", "status": MISSING, "detail": "The run record has no stage list."}]
    stage_problem = _stage_set_problem(stages) or _bote_problem_text(stages)
    status = _status(record, stages, gates, stage_problem, record_problem)
    if record_problem:
        status = "unreadable"  # a repeated key can hide a failure, so even a stopped record shows as an error
    if status == "unreadable" and (record_problem or MISSING not in [g["status"] for g in gates]):
        why = record_problem or stage_problem or "Failed, waiting or force fields are missing or the wrong type."
        gates.append({"id": "run-record", "name": "Run record check", "status": MISSING, "detail": why})

    holds = []
    for s, gid in zip(stages, ids):
        if isinstance(s, dict) and s.get("status") == "waiting":
            holds.append({"id": f"hold-{gid}",
                          "reason": _text(s.get("what_to_do")) or "Waiting on a person. The engine gave no instruction.",
                          "owner": _text(s.get("waiting_on")) or "unknown"})

    ran = _text(record.get("ran"))
    events = [{"at_utc": ran, "text": "Engine run recorded."}] if ran else []

    synthetic = record.get("synthetic") is True
    return {
        "run_id": run_id,
        "synthetic": synthetic,
        "deal_label": _text(record.get("slug")) or run_id,
        "route": _text(record.get("route")) or MISSING,
        "status": status,
        "phase": "engine_run",
        "engine_commit": _text(record.get("engine_commit")),
        "current_engine_commit": current_engine_commit or "",
        "inputs_hash": _text(record.get("inputs_hash")),
        "current_inputs_hash": current_inputs_hash or "",
        "gates": gates,
        "headline": _headline(bote, bote_problem),
        "evidence": _evidence(stages, run_dir, _expected_hashes(record), bote_problem, bote_sha256),
        "holds": holds,
        "events": events,
    }
