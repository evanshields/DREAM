# HANDOFF: app-frontend-tests-slice-1

Base: origin/cloud/2026-11-04-app-frontend-test-plan (PR 23), base SHA 521662a (full SHA in PR body).
Head SHA: see PR body and final message.

## Slice chosen
F14, useLiveCalc clears result on failed recalc (first of the plan's "write first" three, not on HOLD).
F29 and F05 were not started: they need jsdom and component rendering, same blocker.

## Files
- frontend/tests/livecalc.test.tsx (new, Vitest syntax, not wired to any script)
- this file

## Result: BLOCKED, tests not run
- No runner in package.json or either lockfile (vitest, jest, jsdom, testing-library all absent). node_modules is not installed.
- Plan section 0 says a runner needs Evan's approval. I added no package.
- Node 22 built-in test runner cannot load livecalc.tsx (JSX plus react and lucide-react imports) and the dependencies are not installed.
- No failure was recorded. By reading the code, the catch block in useLiveCalc never calls setResult(null), so the test should be red.
- No source code was changed.

## Skipped to avoid clashing with other open PRs
- F25 formatters: PR 25 edits frontend/src/lib/format.ts and adds frontend/tests/format.test.ts.
- PR 19 adds a runner (frontend/scripts/run-tests.mjs) and edits frontend/package.json, lib/api.ts, DealDetail.tsx. Not touched here. Its runner API may differ from the Vitest syntax used, so the test file may need small edits once PR 19 or a runner decision lands.
- PRs 7 and 8 edit api.ts, DealDetail.tsx and mono components. Not touched.

## Next step for Evan
Decide the runner (PR 19's or Vitest), then run the test, record red, and apply the one-line fix (setResult(null) in the catch).
