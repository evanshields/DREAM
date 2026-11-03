# HANDOFF: app-screen-guard-tests (2026-11-04)

## Result
No frontend test runner exists in this repo, so no tests were written and no application code or config changed. This file is the only change.

## Evidence
- `frontend/package.json` and root `package.json` list no vitest, jest, jsdom, happy-dom or testing-library.
- Neither `package-lock.json` contains any of them (grep count 0 in both).
- No `*.test.*` or `*.spec.*` files exist outside node_modules.
- Task rule: install nothing beyond the repo's lockfiles. A runner would need new packages and a config change, so it was not set up here.

## Map rows covered now
None. Rows F01 to F28 in the gap map (draft PR 11) are all still untested.

## Map rows left (untested High, not on HOLD)
- F05 Underwrite submit stays disabled until every blocking question is answered (`pages/Underwrite.tsx:874-967`)
- F14 `useLiveCalc` keeps the last good result when a recalc fails (`components/livecalc.tsx:71-77`). Expected real bug, would need an expected-failure mark.
- F15 Sensitivity grid stays after an error (`components/AssumptionDashboard.tsx:421-433`). Expected real bug.
- Medium and Low rows (F01-F04, F09, F11-F13, F16-F20, F24-F26, F28) also left.

## Skipped on purpose (HOLD: snapshot panel or evidence viewer)
F06, F07, F08, F10, F21, F22, F23, F27.

## Proposed smallest setup (text only, not applied)
1. Dev dependencies in `frontend/`: `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`. Commit the updated lockfile.
2. Add `"test": "vitest run"` to `frontend/package.json` scripts.
3. Add a `test` block to `frontend/vite.config.ts`: `environment: 'jsdom'`, `setupFiles: ['./src/test/setup.ts']`, `globals: true`.
4. `src/test/setup.ts` imports `@testing-library/jest-dom/vitest` and makes `fetch` throw by default so no test can reach the network.
5. First tests, in order: `livecalc.tsx` (F14, F17), `AssumptionDashboard.tsx` sensitivity (F15, F16), `Underwrite.tsx` submit gating (F05), `BondScreen.tsx` (F18), `format.ts` (F25), an error boundary check (F24).
6. Known failing guards (F14, F15) go in as `it.fails(...)` with a comment naming file, line and gap.

## Next step
Approve the setup above, then rerun this job to write the tests.
