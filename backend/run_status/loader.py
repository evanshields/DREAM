"""Loads frozen JSON fixtures from backend/fixtures/run_status/ by run id. Read-only."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from run_status.adapter import adapt_engine_run

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "run_status"
RUN_ID_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def valid_run_id(run_id: str) -> bool:
    return bool(RUN_ID_RE.fullmatch(run_id or ""))


def load_run(run_id: str) -> Optional[dict[str, Any]]:
    """Return the fixture for run_id, or None when the id is malformed or unknown."""
    if not valid_run_id(run_id):
        return None
    path = FIXTURE_DIR / f"{run_id}.json"
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            run = json.load(fh)
    except (OSError, ValueError):
        return None
    # Only frozen synthetic fixtures are served, and the file must say it is the run asked for.
    if not isinstance(run, dict) or run.get("synthetic") is not True or run.get("run_id") != run_id:
        return None
    return run


def list_fixture_ids() -> list[str]:
    return sorted(p.stem for p in FIXTURE_DIR.glob("*.json") if valid_run_id(p.stem))


# ---- Engine run source (read-only, opt in) ----------------------------------------------------

RUNS_DIR_ENV = "DREAM_RUNS_DIR"
MAX_RUN_FILE_BYTES = 2_000_000


def runs_root() -> Optional[Path]:
    """The engine runs folder when DREAM_RUNS_DIR is set to an existing directory, else None (fixtures only)."""
    raw = os.getenv(RUNS_DIR_ENV, "").strip()
    if not raw:
        return None
    root = Path(raw)
    try:
        return root.resolve() if root.is_dir() else None
    except OSError:
        return None


class _RepeatedKey(ValueError):
    pass


def _no_repeated_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """JSON object hook that refuses a repeated key at any depth, so two values are never silently merged."""
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise _RepeatedKey(k)
        out[k] = v
    return out


def _read_json_object(path: Path, root: Path) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    """Read a JSON object that really lives inside root, not through a link and not oversized.

    Returns (document, None) when accepted, (None, None) when the file is simply absent, and (None, reason)
    when the file exists but is rejected. The reason is plain English so callers can show it.
    """
    try:
        if path.is_symlink():
            return None, "the file is a link"
        if not path.is_file():
            return None, None
        resolved = path.resolve()
        if root not in resolved.parents:
            return None, "the file resolves outside the runs folder"
        if resolved.stat().st_size > MAX_RUN_FILE_BYTES:
            return None, "the file is larger than the size limit"
        with resolved.open("r", encoding="utf-8") as fh:
            doc = json.load(fh, object_pairs_hook=_no_repeated_keys)
    except _RepeatedKey as exc:
        return None, f"the file repeats the key {str(exc)!r}"
    except (OSError, ValueError):
        return None, "the file is not valid JSON or could not be read"
    if not isinstance(doc, dict):
        return None, "the file is not a JSON object"
    return doc, None


def _read_run_record(path: Path, root: Path) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    """Like _read_json_object, but a repeated key still yields the record (last value wins) with a problem flag.

    The caller must treat a flagged record as never complete. A repeated key is shown as an error, not merged.
    """
    doc, problem = _read_json_object(path, root)
    if doc is not None or not problem or "repeats the key" not in problem:
        return doc, None
    try:
        with path.resolve().open("r", encoding="utf-8") as fh:
            lenient = json.load(fh)
    except (OSError, ValueError):
        return None, None
    return (lenient, problem) if isinstance(lenient, dict) else (None, None)


def load_engine_run(run_id: str) -> Optional[dict[str, Any]]:
    """Adapt <DREAM_RUNS_DIR>/<run_id>/run/run.json (plus bote.json) into the view shape, or None."""
    if not valid_run_id(run_id):
        return None
    root = runs_root()
    if root is None:
        return None
    deal_dir = root.joinpath(run_id)
    if deal_dir.is_symlink() or deal_dir.resolve().parent != root:
        return None
    run_dir = deal_dir.joinpath("run")
    if run_dir.is_symlink():
        return None
    record, record_problem = _read_run_record(run_dir.joinpath("run.json"), root)
    if record is None or record.get("slug") != run_id:
        return None  # the record must say it belongs to the deal folder it sits in
    # Absent bote.json has no problem here (stage evidence reports it missing). A rejected one is passed on as a problem.
    bote, bote_problem = _read_json_object(run_dir.joinpath("bote.json"), root)
    return adapt_engine_run(
        record,
        bote,
        run_id=run_id,
        run_dir=run_dir.resolve(),
        current_engine_commit=os.getenv("DREAM_CURRENT_ENGINE_COMMIT", "").strip() or None,
        current_inputs_hash=os.getenv("DREAM_CURRENT_INPUTS_HASH", "").strip() or None,
        record_problem=(f"Run record: {record_problem}." if record_problem else None),
        bote_problem=bote_problem,
    )


def list_engine_ids() -> list[str]:
    root = runs_root()
    if root is None:
        return []
    try:
        return sorted(
            p.name for p in root.iterdir()
            if valid_run_id(p.name) and not p.is_symlink() and p.joinpath("run", "run.json").is_file()
        )
    except OSError:
        return []


def list_run_ids() -> list[str]:
    """Fixture ids, then engine run ids that do not collide with a fixture id."""
    fixtures = list_fixture_ids()
    taken = set(fixtures)
    return sorted(taken | {i for i in list_engine_ids() if i not in taken})


def load_any_run(run_id: str) -> Optional[dict[str, Any]]:
    """Fixture first (so a deal folder can never shadow a fixture), then the engine source."""
    run = load_run(run_id)
    return run if run is not None else load_engine_run(run_id)


def load_all() -> list[dict[str, Any]]:
    runs = []
    for run_id in list_run_ids():
        run = load_any_run(run_id)
        if run is not None:
            runs.append(run)
    return runs
