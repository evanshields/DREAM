**This adds a read-only screen that shows where a deal run stands, which checks failed and which numbers are blank, and it refuses to show a blocked or out-of-date run as finished.**

- **What changes:** A new Run status page lists sample runs and opens one to show its checks, headline numbers, evidence files, open holds and timeline. Blocked and out-of-date runs are labelled diagnostic only.
- **Why it matters:** It gives the team a plain view of whether a run can be trusted, and it keeps a blank number different from a real zero.
- **Proof:** I ran the new tests, the full backend suite, the type check and the production build, and all passed. I also fetched the list from a local server. No independent reviewer has looked yet.
- **What could go wrong:** It reads sample data only and is not connected to real runs. It may need small merge fixes beside the two open Mono draft PRs, since all three touch the app entry files.
- **Your click:** Assign a different-family reviewer, merge after the two open Mono PRs are settled, and do not deploy until you are present.

## Definition of Done

| Criterion | Status | Proof |
|---|---|---|
| New tests pass (at least 25) | Met | `python -m pytest tests/test_run_status_view.py tests/test_run_status_api.py tests/test_run_status_boundaries.py -q` ends `112 passed in 0.46s` |
| Full backend suite, no new failures | Met | Baseline on origin/main: `260 passed, 1 skipped in 8.33s`. After: `372 passed, 1 skipped in 7.72s` |
| Frontend typecheck | Met | `npm ci && npm run typecheck` exit 0 |
| Frontend build | Met | `npm run build` exit 0, ends `built in 4.71s` |
| Diff limited to allowed files | Met | Only `backend/main.py` (2 lines) and `frontend/src/App.tsx` (routes and one import) edited |
| Protected paths untouched | Met | the protected-path diff `wc -l` gives `0` |
| No em dashes in new files | Met | grep returned no output |
| Local curl check on fixtures | Met | `curl localhost:8765/api/run-status` returned `{"runs":[{"run_id":"run-blocked-red-gate",...` |
| Deliverables 1 to 14 | Met | All present |

## Technical detail

**Added:** `backend/run_status/`, `backend/routers/run_status.py`, six fixtures, three test files, `frontend/src/lib/runStatusApi.ts`, `frontend/src/pages/RunStatus.tsx`, `frontend/src/components/runstatus/RunStatusParts.tsx`, `docs/run-status-slice/`.
**Edited:** `backend/main.py` (2 lines), `frontend/src/App.tsx` (import plus two gated routes).

**Display state precedence:** failed, blocked, stale, in_progress, needs_input, needs_human_check, complete (first match wins; unknown status fails closed).

**Cut list:** nothing cut. Nav link is a follow-up.

**Notes:** `pytest` and `httpx` are not in `requirements.txt`, installed in the local venv only. The failed fixture has an extra `error_message` field. Open questions: real run source after #7 and #8, and per-user access.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
