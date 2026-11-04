# Handoff: app-gap-item

**Item:** F25 from the app fail-closed test gap map (PR 11). The display formatters `fmtUSD`, `fmtUSDFull`, `fmtPct`, `fmtPct1`, `fmtEM` printed `NaN%`, `$NaN` or `NaNx` for a non-finite or missing number. They now print a dash.

**Why this item:** every backend gap row is already claimed by an open PR (the input tests, API contract tests, gate tests and backend gap remainder PRs). The React rows have no runner on main. `frontend/src/lib/format.ts` is a pure file that no open PR touches, and Node's built-in test runner can load it.

**Files (new or changed):**
- frontend/src/lib/format.ts (fix)
- frontend/tests/format.test.ts (new, 27 tests)
- cloud-work/2026-11-04-app-gap-item/HANDOFF.md

Not touched: package.json (open PR 19 edits it). The test runs with `node --test frontend/tests/format.test.ts`.

**Results:**
- Before fix: 27 tests, 2 pass, 25 fail (every bad input case printed a made-up string).
- After fix: 27 tests, 27 pass, 0 fail.
- `npm ci` (lockfile) then `npx tsc --noEmit`: exit 0. `npm run build`: built OK.
- Backend pytest: NOT RUN. pytest is not installed and no pinned version exists in backend/requirements.txt, so nothing was installed. No backend file changed.

**Base SHA:** 953cda4835602bbdfcf3df767adca936ddece3b5
**Head SHA:** see the PR and final message.
