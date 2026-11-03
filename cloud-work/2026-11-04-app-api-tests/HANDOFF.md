# Handoff: app API contract tests (2026-11-04)

New file: `backend/tests/test_api_contract_refusals.py` (74 passing, 15 strict xfail). No application code or config changed.
Source of rows: `docs/research/2026-11-04-app-fail-closed-test-gap-map.md` (branch `cloud/2026-11-04-app-test-gap-map`).

## Rows now covered
| Row | Result |
|---|---|
| B12 every real route 401 without a token (swept over `main.app`) | passes |
| B13 strict ownership 404 on archive, unarchive, delete | passes |
| B64 gate_failed deal returns headline_metrics (list and detail) | xfail, real gap |
| B68 memo written for a gate_failed deal | xfail, real gap |
| B25 EFB endpoint accepts NOI of -5 and 0 | xfail, real gap (target_dscr 0 refusal passes) |
| B23 recalc with total_equity 0 gives equity_multiple 0.0 | xfail, real gap |
| B22 raw Python text in error body (empty noi_series) | xfail, real gap (plain 422 still passes) |
| B26 agency sizing with value 0; missing fields on exit-cap and agency calculators | xfail for value 0, rest pass |
| B32 /api/validate with `{}` | xfail, real gap (non-object body 422 passes) |
| B33 /api/agent/memo accepts client model_results | xfail, real gap (generator error 422 passes) |
| B42 client can send require_identity_match=false | xfail, real gap (default 409 passes) |
| B44 text bytes named .xlsx on export and reconcile | passes (422) |
| B46 export download=true with identity mismatch returns JSON, no file | passes |
| B47 reconcile with no headline | passes (409) |
| B55 wave 0 accepts exit_cap 0 and negative price | xfail, real gap |
| B89 failed or in-progress run with values is not marked diagnostic | xfail, real gap (never "complete" passes) |

## Left
- B40 intake upload size, extension, empty file, and B40b number extraction (intake needs a Kimi seam fake, not done in time)
- B34 agent chat stream errors inside HTTP 200
- B57 / B52 runner exception paths, B70 memo prose vs engine numbers, B71 memo version conflict
- B02 prod env with no auth, B08 / B09 secret-unset 500s, B21, B28, B35, B41, B49, B51, B74, B75, B93
- Skipped on purpose: every snapshot panel and evidence viewer row (F06 F07 F08 F10, B86 B91 B94, F21-F23 F27)
- All React rows: no frontend test runner exists

## Notes
- pytest is not in `backend/requirements.txt`. I installed requirements plus pytest into a throwaway venv outside the repo.
- Each xfail is strict, so fixing a gap turns its test red until the marker is removed.
