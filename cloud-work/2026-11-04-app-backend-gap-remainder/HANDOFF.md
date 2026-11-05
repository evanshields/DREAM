# Handoff: app backend gap remainder (2026-11-04)

Branch `cloud/2026-11-04-app-backend-gap-remainder`, cut from `main`. Draft PR, base `main`.
One new test file: `backend/tests/test_backend_gap_remainder.py`. No product code, config or conftest changed.

## Rows covered (new)
| Row | Result |
|---|---|
| B51 answer unknown job, unknown question, cancel unknown job | pass (404, job unchanged) |
| B71 memo save with a stale deal version | pass (409, nothing stored) |
| B76 CRM item update with no, string, float or null version | pass (400) |
| B76 CRM item update with JSON `true` as version | xfail, real gap |
| B77 CRM item update with stale version, task toggle with stale version | pass (409, newer data kept) |
| B49 reconcile with a non-numeric headline metric | xfail, real gap |
| B41 Kimi classification raises | pass for fallback to filename guess, xfail for the missing warning |
| B93 run status headline item that is not an object | xfail x3, real gap |

## Rows skipped on purpose
- Already tested by open PRs: PR 12 (B12 B13 B22 B23 B25 B26 B32 B33 B42 B44 B46 B47 B55 B64 B68 B89), PR 15 (B33 B40b B42 B46 B47 B52 B55 B57 B64 B68 B70 B89), PR 16 (B02 B08 B09 B12 B13 B21 B22 B23 B25 B26 B28 B32 B34 B35 B40 B44). PR 21 is a conftest isolation change and PR 22 is the intake percent parser, neither touches these rows.
- B94 is HOLD (snapshot data). B86 and B91 are HOLD (evidence viewer). Not touched.
- B56 weak test (W2): a real RED gate reaching the runner is not added here.

## xfail list (6, all strict)
- B76 boolean version bypasses the integer check
- B49 non-numeric headline dropped from reconcile
- B41 Kimi failure leaves `warnings` empty
- B93 non-dict headline item raises (3 cases: None, string, number)

## Totals
Run from `backend/` with `pytest.ini`, venv from `requirements.txt` plus `pytest==8.3.3`.
- This file: 16 passed, 6 xfailed.
- Full backend suite on this branch: 566 passed, 1 skipped, 6 xfailed, 0 failed.
- Each xfail was also run with `--runxfail` and fails on the stated reason.

## Notes
- The file clears auth env vars itself (autouse fixture) so it does not depend on PR 21.
- Stores are in-memory, Kimi is a fake client, no network.
