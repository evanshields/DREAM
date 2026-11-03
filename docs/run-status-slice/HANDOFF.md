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
