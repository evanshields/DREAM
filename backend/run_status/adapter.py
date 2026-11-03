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
"""
from __future__ import annotations

import hashlib
from pathlib import Path, PureWindowsPath
from typing import Any, Optional

MISSING = "missing"

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


def _stage_gate(stage: Any) -> dict[str, Any]:
    if not isinstance(stage, dict):
        return {"id": "stage-unknown", "name": "Unreadable stage record", "status": MISSING,
                "detail": "This stage record could not be read."}
    number = stage.get("stage")
    gid = f"stage-{number}" if isinstance(number, int) and not isinstance(number, bool) else "stage-unknown"
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


def _evidence(stages: list[Any], run_dir: Optional[Path]) -> list[dict[str, Any]]:
    """One item per file a finished stage says it wrote. Present on disk and hashed is ok, otherwise missing."""
    items: list[dict[str, Any]] = []
    for stage in stages:
        if not isinstance(stage, dict) or stage.get("status") != "ok":
            continue
        wrote = stage.get("wrote")
        for raw in wrote if isinstance(wrote, list) else []:
            if not isinstance(raw, str) or not raw.strip():
                continue
            # Engine paths come from another machine, so only the file name is used, inside run_dir.
            fname = PureWindowsPath(raw).name
            digest, state = "", "missing"
            if run_dir is not None and fname and fname not in (".", ".."):
                p = run_dir.joinpath(fname)
                try:
                    if p.is_file() and not p.is_symlink():
                        digest, state = hashlib.sha256(p.read_bytes()).hexdigest(), "ok"
                except OSError:
                    pass
            items.append({"name": fname, "path": f"run/{fname}", "sha256": digest, "state": state})
    return items


def _headline(bote: Optional[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for name, unit, parts in HEADLINE_SPEC:
        value = _dig(bote, parts) if isinstance(bote, dict) else _ABSENT
        if value is _ABSENT:
            reason = "No bote.json for this run." if not isinstance(bote, dict) else "Not present in bote.json."
            rows.append({"name": name, "value": None, "unit": unit, "blank_reason": reason,
                         "source_file": "bote.json", "source_pointer": _pointer(parts)})
        elif value is None:
            rows.append({"name": name, "value": None, "unit": unit,
                         "blank_reason": "bote.json stores no figure here (null).",
                         "source_file": "bote.json", "source_pointer": _pointer(parts)})
        else:
            rows.append({"name": name, "value": value, "unit": unit, "blank_reason": None,
                         "source_file": "bote.json", "source_pointer": _pointer(parts)})
    return rows


def _status(record: dict[str, Any], stages: list[Any], gates: list[dict[str, Any]]) -> str:
    """completed only when every stage is ok or skipped, the run was not cut short, and nothing failed or waits."""
    statuses = [g["status"] for g in gates]
    if MISSING in statuses:
        return "unreadable"
    if "red" in statuses or record.get("failed"):
        return "stopped"
    if "not_run" in statuses or record.get("waiting"):
        return "awaiting_input"
    if not stages or record.get("stop_after") is not None:
        return "partial"
    if "failed" not in record or "waiting" not in record:
        return "unreadable"  # the engine always writes both lists; absent means an unreadable record
    return "completed"


def adapt_engine_run(
    record: Any,
    bote: Any = None,
    run_id: str = "",
    run_dir: Optional[Path] = None,
    current_engine_commit: Optional[str] = None,
    current_inputs_hash: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Return a view-shaped run dict, or None when the record is not a JSON object."""
    if not isinstance(record, dict):
        return None
    raw_stages = record.get("stages")
    stages = raw_stages if isinstance(raw_stages, list) else []
    gates = [_stage_gate(s) for s in stages]
    if not isinstance(raw_stages, list):
        gates = [{"id": "stages", "name": "Stage list", "status": MISSING, "detail": "The run record has no stage list."}]
    status = _status(record, stages, gates)

    holds = []
    for s in stages:
        if isinstance(s, dict) and s.get("status") == "waiting":
            holds.append({"id": f"hold-stage-{s.get('stage')}",
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
        "headline": _headline(bote),
        "evidence": _evidence(stages, run_dir),
        "holds": holds,
        "events": events,
    }
