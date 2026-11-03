"""Read-only run status and evidence view over frozen synthetic fixtures.

Exactly two GET routes. Nothing here writes, runs the engine or calls a model.
Mounted auth-gated in main.py like the other routers.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from run_status.loader import list_run_ids, load_any_run, valid_run_id
from run_status.view import build_summary, build_view

router = APIRouter()


@router.get("/api/run-status")
def list_runs():
    runs = []
    for run_id in list_run_ids():
        run = load_any_run(run_id)
        if run is not None:
            runs.append(build_summary(run))
    return {"runs": runs}


@router.get("/api/run-status/{run_id}")
def get_run(run_id: str):
    if not valid_run_id(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    run = load_any_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return build_view(run)
