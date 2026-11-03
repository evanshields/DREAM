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
- Add a nav link in the app shell (not done here).
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
