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

## Slice 2 repair (review of head b4008a17: Astra 4 REAL, Argon 7 REAL groups)

Each finding was reproduced with a failing test first (`backend/tests/test_run_status_pr10_repair.py`, 78 cases). Before the fix: 66 failed, 12 passed. The 12 that passed were the control case, three absent-bote and all-skipped cases the old blocking already caught, two `failed`/`waiting` cases, and the seven `stop_after` cases (finding 6, see below).

| Finding | Reproduced | Fix | Proving tests |
|---|---|---|---|
| Astra 1 / Argon 1: missing stages, duplicate or invalid stage numbers, untyped failed/waiting reach Complete | Yes (absent 6, 7, 8, duplicates, null lists) | Complete needs exactly stages 1 to 8 once each, `failed` and `waiting` real lists, else an unreadable "Run record check" gate (blocked) | `test_a1_*` |
| Astra 2 / Argon 2: rejected BOTE (bad JSON, array, oversized) shows Verified and Complete | Yes | Loader returns the rejection reason; evidence state `unreadable`, headline reason says rejected, blocked | `test_a2_*` |
| Astra 3 / Argon 3: fresh hash shown as Verified | Yes | Verified only when the file matches the run record's `output_sha256`. No recorded hash gives `unverified`, a different hash gives `hash_mismatch`. Real runs have no recorded hash today, so they show blocked until the engine writes one | `test_a3_*` |
| Astra 4 / Argon 4: unbounded evidence reads on list and detail | Yes | Chunked hashing, 25 MB cap per file (over-limit file is never opened), 32 items per run, hash cache keyed on path, size and mtime, and nothing is read when no recorded hash exists | `test_a4_*` |
| Argon 5: skipped stages bypass evidence, skipped stage 7 with no bote reaches Complete | Yes | Any skipped stage makes the run `partial` (never complete); stage 7 must be ok and list bote.json | `test_r5_*` |
| Argon 6: stop_after truthiness and untyped force, failed, waiting, wrote | stop_after: **No.** `is not None` already stops 0, "", False, [], {} (7 cases pass on the old code, left unchanged). Rest: Yes | `force` must be a boolean; malformed `wrote` (not a list, non-string entry, blank) is an `invalid` evidence item, blocked; failed and waiting overlap finding 1 | `test_r6_*` |
| Argon 7: duplicate stage numbers, evidence names, JSON keys | Yes | Gate, hold and evidence ids are unique; duplicate file names and items past the limit are `invalid`; a repeated key in run.json shows an error gate (blocked), in bote.json rejects the file | `test_r7_*` |
| Argon Likely 1: non-scalar headline values | Yes | Dict, list or boolean at a headline pointer shows blank with a reason | `test_l1_*` |

Not changed: schema difference between acq and bond bote.json (the five pointers are the acq shape; a bond run shows blanks with a reason, never a wrong number), process stages still stand in for QA gates, `partial` still displays as failed, per-user access.

Side effect to know: the synthetic complete fixture now carries `output_sha256`. Real engine runs show blocked (unverified evidence) until dream-underwrite writes output fingerprints, in addition to the existing stale state.

Real output, full backend suite (`cd backend && python -m pytest tests -q`):

```
548 passed, 1 skipped in 10.88s
```
New repair file only: `78 passed in 1.38s`. Baseline before repair: 470 passed, 1 skipped. `cd frontend && npm run typecheck`: `tsc --noEmit` no errors. `npm run build`: `built in 5.86s` (usual chunk size warning).
