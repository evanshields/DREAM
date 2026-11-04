# Handoff: app-statement-dollar-fix (2026-11-04)

Bug: T-12 text extraction read `$4,800,000` as 0.0 (only the last digit kept). Found by draft PR 15 (head 584b9f23a7ba5aa79da6e6ca3ba87d51b166f5a8, test `test_b40b_single_t12_line_still_extracts`).

Fix: `backend/intake/intake_service.py`, `_DOLLAR` regex plus a lazy gap in `_first_dollar`. Unsupported forms (`$4.8M`, `12K`) now come back blank.

Tests: new `backend/tests/test_intake_t12_dollar_parse.py` (11 tests).
- main alone: 550 passed, 1 skipped
- new tests, before fix: 10 failed, 551 passed, 1 skipped
- after fix: 561 passed, 1 skipped (no failures)

Follow-up for PR 15: after this merges, its strict xfail `test_b40b_single_t12_line_still_extracts` turns into an XPASS failure, so drop that mark. The other xfail (conflicting lines) is a different gap and is untouched.

Behavior note: a line with two amounts still returns the first amount, as `_first_dollar` always intended.
