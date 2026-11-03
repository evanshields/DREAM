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
