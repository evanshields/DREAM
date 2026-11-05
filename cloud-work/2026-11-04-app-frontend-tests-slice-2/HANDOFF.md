# HANDOFF: app-frontend-tests-slice-2 (rows F01 to F09)

Base: cloud/2026-11-04-app-frontend-tests-slice-1 (PR 26).

## Rows
- F01 RequireAuth.test.tsx. F02 and F03 api-auth.test.tsx. F04 and F05 Underwrite.test.tsx. F09 DealDetailSeed.test.tsx.
- F06, F07, F08 skipped: HOLD in the gap map.
- PRs 25 and 26 cover F25 and F14 only, so no F01 to F09 row was already tested.
- Expected failures (it.fails): F05 abc and F05 Infinity. The panel only checks for non-blank text.
- F09 asserts a series with any non-number is dropped whole (plan open decision). Code does this today.

## Result: NOT RUN
PR 26 pinned no runner (no vitest, jsdom or testing-library in package.json, no node_modules). Rule says install only what PR 26 pinned, so nothing was installed.
Totals before: 0 run. After: 0 run. Tests are written for Vitest + jsdom + Testing Library + user-event (plan section 0).
Needs: runner approval, then run, confirm F05 it.fails cases are red-as-expected.
