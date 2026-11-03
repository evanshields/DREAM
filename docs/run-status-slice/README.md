# Run status and evidence view (fixtures only)

## What it is
A read-only screen that shows where a deal run stands: the quality gates, the headline numbers (and which are blank, with the reason), the evidence files, open holds and a timeline. It reads six frozen sample runs for an invented deal. It never writes, never runs the engine and never calls a model.

## Run it locally
1. Leave `GOOGLE_CLIENT_ID` and `AUTH_JWT_SECRET` unset so local auth is off.
2. Backend: `cd backend && python -m uvicorn main:app --port 8765`
3. Check: `curl -s localhost:8765/api/run-status`
4. Frontend: `cd frontend && npm ci && npm run dev`, then open `/runs`.
5. Tests: `cd backend && python -m pytest tests -q`

## Display states
The first row that matches wins.

| State | When |
|---|---|
| failed | status is failed or cancelled |
| blocked | any gate is red |
| stale | engine commit or input hash differs from the current one |
| in_progress | submitted, routing, analyzing or synthesizing |
| needs_input | awaiting_input |
| needs_human_check | awaiting_cp1 (a person must review, no button to advance) |
| complete | completed |

Blocked and stale runs still show their numbers, labelled "diagnostic only". A blank value shows "Blank" and its reason. A verified zero shows as 0 with its source.

## What it deliberately does not do
- No POST, PUT, PATCH or DELETE. Only two GET routes.
- No math on any value. It counts items and compares strings.
- No database, engine, model or network call.
- No real deal data. Every fixture is marked synthetic.
- No deploy steps.

## Follow-ups
- ~~Add a nav link in the app shell~~ done in the run source slice (below).
- Read real runs from the Mono publication record once PR #7 and #8 land.
- Per-user access to runs.

## Auth regression tests (repair round 1)
`backend/tests/test_run_status_auth.py` mounts the router the same way `backend/main.py` does (`dependencies=[Depends(require_auth)]`) with auth switched on. For both GET routes it checks: no token gives 401, a garbage or wrongly signed token gives 401, a valid token gives 200. A last test checks that `main.py` still contains the authenticated mount line. Run with the auth mount removed, 10 of the 13 tests fail, so the tests do guard it.

Real output, full backend suite (`cd backend && python -m pytest tests -q`):

```
..................s..................................................... [ 18%]
........................................................................ [ 37%]
........................................................................ [ 55%]
........................................................................ [ 74%]
........................................................................ [ 93%]
..........................                                               [100%]
385 passed, 1 skipped in 11.01s
```

## Fail-closed repair (repair round 2, Argon review of head 492866a6)
Each finding was reproduced with a failing test first (`backend/tests/test_run_status_failclosed.py`, 29 cases failed before the fix, all pass after).

| Finding | Real? | Test | Fix |
|---|---|---|---|
| 1. Unknown, missing or empty gate results read as finished | Real | `test_unknown_gate_status_is_blocked`, `test_gate_without_status_key_is_blocked`, `test_empty_gates_on_terminal_run_is_blocked`, `test_missing_gates_key_is_blocked` | Only green, amber, not_run and red are recognised. Any other gate status, a malformed gate, or no gates on a completed or awaiting_cp1 run shows as blocked. |
| 2. Missing commit or hash on both sides read as not stale | Real | `test_missing_provenance_both_sides_is_stale`, `test_absent_provenance_keys_is_stale` | A missing or blank commit or hash, on either side, counts as stale (unverifiable). |
| 3. Evidence "missing" or "hash_mismatch" and open holds ignored | Real | `test_bad_evidence_is_blocked`, `test_completed_without_evidence_is_blocked`, `test_open_hold_never_complete`, `test_missing_evidence_fixture_shows_blocked_and_missing` | Any evidence item not "ok", unknown state, or no evidence on a settled run shows as blocked. An open hold can never show as complete (needs_human_check). The run-missing-values fixture now shows blocked instead of needs_human_check, and its test expectation was updated. |
| 4. Loader served non-synthetic files and 500ed on a missing run_id | Real | `test_non_synthetic_file_rejected`, `test_missing_synthetic_flag_rejected`, `test_run_id_mismatch_rejected`, `test_missing_run_id_does_not_500`, `test_malformed_json_is_none` | `load_run` returns nothing (404, skipped in the list) unless the file is a JSON object with `synthetic` exactly true and `run_id` equal to the file name. Bad JSON is also rejected. `build_summary` no longer raises on a missing run_id. |

Not changed (outside the four findings, left for the next review): Argon items 5 to 8. Item 6 is partly handled here by refreshed numbers below; PR-BODY.md and HANDOFF.md still carry the older counts.

Real output, full backend suite (`cd backend && python -m pytest tests -q`):

```
414 passed, 1 skipped in 12.38s
```

`cd frontend && npm run typecheck`: `tsc --noEmit` finished with no errors.
`cd frontend && npm run build`: `✓ built in 7.29s` (only the usual chunk size warning).

## Engine run source (slice 2, branch cloud/2026-11-03-dream-app-run-source)

Reads real engine run records, read-only, behind an env var.

- `DREAM_RUNS_DIR` unset (or empty, or not a directory): the six fixtures only, exactly as before.
- `DREAM_RUNS_DIR` set: the list and detail endpoints also serve `<DREAM_RUNS_DIR>/<deal>/run/run.json`, plus `run/bote.json` when present. The run id is the deal folder name and must match `^[a-z0-9-]{1,64}$`. A fixture with the same id always wins. Still two GET routes.
- Optional `DREAM_CURRENT_ENGINE_COMMIT` and `DREAM_CURRENT_INPUTS_HASH`: what "current" means for the stale check. Unset, a run reads as stale (cannot be verified), never complete.
- Run it: `DREAM_RUNS_DIR=backend/fixtures/run_status_engine DREAM_CURRENT_ENGINE_COMMIT=synthetic-commit-0001 DREAM_CURRENT_INPUTS_HASH=synthetic-hash-0001 python -m uvicorn main:app --port 8765` then open `/runs`.

### What the engine writes (from dream-underwrite `run.py`, `write_output(run_dir, "run.json", record)`)
`{slug, route, ran, stop_after, force, stages: [{stage, name, status, why | error | waiting_on + what_to_do + files | wrote | print}], failed: [n], waiting: [n]}`. Stage status is one of ok, skipped, failed, waiting, blocked. `bote.json` is the stage 7 output. The engine writes no engine commit, no inputs hash and no gates today.

### Mapping (`backend/run_status/adapter.py`, pure Python, no arithmetic)
| Engine | View |
|---|---|
| stage ok | gate green |
| stage failed | gate red, detail is the engine error |
| stage waiting or blocked | gate not_run (a waiting stage also becomes an open hold with the engine instruction) |
| stage skipped | gate amber, detail "Skipped: <why>" |
| status absent or unknown, stage unreadable, no stage list | gate "missing" (shows blocked) |
| exactly stages 1 to 8 once each and all ok, `stop_after` null, `force` boolean, `failed` and `waiting` lists present and empty, stage 7 wrote bote.json | run status completed |
| any skipped stage | partial (shows failed, fail closed) |
| any failure | stopped (shows blocked via the red gate) |
| any waiting | awaiting_input (never complete) |
| `stop_after` set, or no stages | partial (shows failed, fail closed) |
| lists missing, or any unreadable gate | unreadable (shows blocked) |

Headline rows are read from `bote.json` and passed through exactly as stored (floats stay floats, a stored 0 stays 0, a stored null stays null with a blank reason): price, year 1 NOI, bridge and takeout coverage (exempt case), IRR. A value that is absent or has no bote.json is blank with its reason. Evidence is one item per file a finished stage says it wrote, matched by file name inside the run folder and hashed (sha256 of the bytes): ok only when it matches the record's `output_sha256`; present with no recorded hash is `unverified`, a different hash is `hash_mismatch`, a rejected bote.json is `unreadable`, bad or repeated entries are `invalid`, otherwise missing. Only ok lets a run show complete. Files over 25 MB are never opened. Engine commit and inputs hash are carried through when the record has them.

### Hardening
Deal folder and `run/` may not be symlinks, resolved paths must stay under the runs root, files over 2 MB are ignored, the record's `slug` must equal its folder name, bad JSON is skipped in the list and 404 on detail.

### Gaps found (not fixed here, engine side)
1. The engine record has no engine commit or inputs hash, so every real run reads stale until the engine writes them (or the two current-value env vars match and the record carries them).
2. The engine has no gate results in `run.json`; stages stand in for gates here. Real QA gates (inside `bote.json` for bond deals) are not read yet.
3. Engine `wrote` paths are absolute paths from the machine that ran it, so only the file name is used.

### Fixtures
`backend/fixtures/run_status_engine/`: `synthetic-stopped-stage6` (stages 1 to 5 ok, 6 failed, 7 waiting, 8 blocked, no bote.json) and `synthetic-complete` (all ok, bote.json with a stored null IRR and a stored zero). Both say `synthetic: true` and use obviously fake values. The stopped fixture has stage 7 waiting beside a failed stage 6 because that was the case asked for; the real engine would write 7 as blocked, which a separate test covers.

### Nav
`AppShell.tsx` has a Runs link to `/runs` (desktop and mobile nav). The gate type gained a "missing" value so an unreadable stage shows a red "Missing" badge.

Real output, full backend suite (`cd backend && python -m pytest tests -q`):

```
.......................................                                  [100%]
470 passed, 1 skipped in 10.54s
```
New file only: `tests/test_run_status_engine_source.py`, 46 passed. Baseline before this slice: 414 passed, 1 skipped.
`cd frontend && npm run typecheck`: `tsc --noEmit` no errors. `npm run build`: `✓ built in 7.02s` (usual chunk size warning).
The existing boundary tests (no arithmetic tokens, no `os.environ`, no network words) apply to the new files and pass.
