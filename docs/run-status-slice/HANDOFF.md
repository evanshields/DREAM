# Handoff: run status slice

## Bottom line
A read-only run status and evidence view is built on frozen sample runs and submitted as a draft PR. It is not connected to real runs.

## What was built
- Backend: `backend/run_status/` (loader, view), `backend/routers/run_status.py` (two GET routes), six fixtures, mounted in `backend/main.py`.
- Frontend: `runStatusApi.ts`, `pages/RunStatus.tsx`, `components/runstatus/RunStatusParts.tsx`, two routes in `App.tsx`.
- Tests: three new files under `backend/tests/` (112 tests).

## Commands run
See the PR body for exact last lines. Baseline backend suite: 260 passed, 1 skipped. After: 372 passed, 1 skipped.
Note: `pytest` and `httpx` are not in `backend/requirements.txt`, so they were installed into the local venv only.

## Cut list
Nothing cut.

## Open items
- Nav link in the app shell.
- Real run source after PR #7 and #8 land.
- Per-user access.
- Possible small merge fixes beside PR #7 and #8 (`backend/main.py` and `frontend/src/App.tsx` are shared edit points).

## Slice 2: engine run source (branch cloud/2026-11-03-dream-app-run-source, draft PR)

### Bottom line
The run status view can now read real engine runs from `DREAM_RUNS_DIR`, read-only, and the app nav has a Runs link. Nothing is deployed and the env var is unset by default.

### Built
`backend/run_status/adapter.py`, loader additions, router now uses `load_any_run`, two synthetic engine-format fixtures, `tests/test_run_status_engine_source.py` (46 tests), Runs nav link, a "missing" gate status in the frontend types. Details and the mapping table are in README.md.

### Commands run
Backend suite 470 passed, 1 skipped (baseline 414 passed). `npm run typecheck` clean, `npm run build` built. Pip packages pytest and httpx installed in a scratch venv only.

### Open items
- Engine writes no commit or inputs hash into run.json, so real runs read stale. Needs an engine change in dream-underwrite (not touched).
- No QA gates in run.json; read bond gates from bote.json later.
- Per-user access to runs; real runs for a deal are visible to every signed-in user.
- Setting `DREAM_RUNS_DIR` on the VPS is an Evan decision and a deploy step, not done.
- A `partial` run (stop_after) shows as failed; a friendlier state would need a view change.
