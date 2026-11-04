# Handoff: app frontend test plan

Date 2026-11-04. Chat: [cloud] app-frontend-test-plan. Report only.

## What was done
- Read the gap map `docs/research/2026-11-04-app-fail-closed-test-gap-map.md` from branch `cloud/2026-11-04-app-test-gap-map`.
- Wrote `docs/research/2026-11-04-frontend-test-plan.md`: one exact test for each of F01 to F29, grouped by component, with component, setup, user action and fail-closed assertion.
- Added only those two files. No code, config or package changed. Nothing installed. No test run (no runner exists).

## Findings
- All 29 rows need a frontend test runner. None exists.
- 8 rows are HOLD (F06, F07, F08, F10, F21, F22, F23, F27). Plan written, tests to wait.
- Several tests are red-first, meaning they fail on today's code: F14, F15, F29, F06, F08, F10, F24.
- Top 3 to write first: F14, F29, F05.

## Needs Evan
- Approve a runner (Vitest proposed) before any install.
- Decide F08/F25 negative display, F09 series handling, F24 ErrorBoundary.

## Next step
After the red team passes and the CEO marks the PR ready, Evan reviews and merges. Then a build task adds the runner and the first three tests.
