# Handoff: app API contract tests (2026-11-04)

New file: `backend/tests/test_api_contract_refusals.py` (83 passing, 15 strict xfail). No application code or config changed.

## Third repair: real archive and unarchive transitions (same branch)
- `test_b13_strict_ownership_same_owner_succeeds` now proves the transitions, not just status 200. Archive: the owner archives an active computed deal, the in-memory store shows `archived` and `meta.pre_archive_status` is `computed`. Unarchive: the owner first archives the deal (store shows `archived`), then unarchives it, and the store shows `computed` again with the stash consumed, so the idempotent no-op path cannot satisfy it. Delete keeps its removal assertion. Other-owner denial checks kept.
- Isolation seams and dotenv handling untouched. Tests only, no product code change.
- Totals: this file 83 passed, 15 xfailed. Full backend 633 passed, 1 skipped, 15 xfailed.

## Second repair: strict ownership same-owner control (same branch)
- B13 now proves strict mode both ways. New `test_b13_strict_ownership_same_owner_succeeds` runs archive, unarchive and delete as the owner (in-memory synthetic login user) with `DREAM_STRICT_OWNERSHIP` ON and expects 200, then the same call on another owner's deal and expects 404 with the deal untouched.
- The hostile-host ownership control got a matching same-owner success test, `test_control_strict_ownership_allows_same_owner_under_hostile_host`.
- Delete reaches CRM link cleanup, so the new `synthetic_crm` fixture swaps in an in-memory CRM store. No network, no product code change.
- Raw dotenv handling left alone, that finding was rejected because the module-level parametrization already imports main at collection.
- Totals: this file 83 passed, 15 xfailed. Full backend 633 passed, 1 skipped, 15 xfailed.

## Repair after Argon red team (same branch)
- Ownership and real-app tests no longer inherit the host `AUTH_JWT_SECRET`, `GOOGLE_CLIENT_ID`, `DREAM_STRICT_OWNERSHIP` or `DREAM_DB_PATH`. New fixture `synthetic_env` pins them (auth off, empty allowlist, DB path under tmp_path).
- `auth_on_main` login now uses an in-memory synthetic user store through `get_users`, so login can no longer reach the configured host database.
- `synthetic_env` makes every default store accessor raise `REAL DATABASE TOUCHED`, and fails the test if the guarded db file appears.
- New controls: ownership 404 and login both pass under a bogus host secret and DB path, a guard test, and a negative control showing an unpatched login trips the guard.
- Rejected raw claim (silent zero-route) unchanged, the route-count test still guards it.
- Known and out of scope: with a bogus host `AUTH_JWT_SECRET` set, 49 older tests in other files (for example `test_review_fixes.py`) fail on `main` too. This PR's file does not.
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
