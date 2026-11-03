"""Loads frozen JSON fixtures from backend/fixtures/run_status/ by run id. Read-only."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

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


def list_run_ids() -> list[str]:
    return sorted(p.stem for p in FIXTURE_DIR.glob("*.json") if valid_run_id(p.stem))


def load_all() -> list[dict[str, Any]]:
    runs = []
    for run_id in list_run_ids():
        run = load_run(run_id)
        if run is not None:
            runs.append(run)
    return runs
