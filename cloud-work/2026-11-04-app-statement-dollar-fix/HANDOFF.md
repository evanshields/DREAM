# Handoff: app-statement-dollar-fix (2026-11-04)

Bug: T-12 text extraction read `$4,800,000` as 0.0 (only the last digit kept). Found by draft PR 15 (head 584b9f23a7ba5aa79da6e6ca3ba87d51b166f5a8, test `test_b40b_single_t12_line_still_extracts`).

Fix: `backend/intake/intake_service.py`, `_DOLLAR` regex plus a lazy gap in `_first_dollar`. Unsupported forms (`$4.8M`, `12K`) now come back blank.

Tests: new `backend/tests/test_intake_t12_dollar_parse.py` (11 tests).
- main alone: 550 passed, 1 skipped
- new tests, before fix: 10 failed, 551 passed, 1 skipped
- after fix: 561 passed, 1 skipped (no failures)

Follow-up for PR 15: after this merges, its strict xfail `test_b40b_single_t12_line_still_extracts` turns into an XPASS failure, so drop that mark. The other xfail (conflicting lines) is a different gap and is untouched.

Behavior note: a line with two amounts still returns the first amount, as `_first_dollar` always intended.

## Repair round (Argon finding on head 4c6361418eacbec6aa29b66b1f7f8f1d49bf885e)

Finding: the optional-dollar pattern with a lazy label gap could pick an unrelated number before the real figure (a year), did not exclude multi-letter or spelled-out magnitudes (MM, million), and could skip an unsupported first amount to read a later column.

Fix (`backend/intake/intake_service.py`, dollar pattern and T-12 line extraction only): `_first_dollar` now reads only the first numeric token after the label on that line, via `_amount_after_label`. It returns a number only when that token is a plain amount (digits, thousands commas, optional cents, optional `$`). It returns None, never a guess, for: any letter-suffixed or spelled magnitude (K, MM, B, million, billion, thousand), a percent, a date or range (12/31/2025, 2025-26), a letter-prefixed token (FY2025, Q3), and a bare 1900-2100 number with no `$` (a year). It never skips forward to a second column. The percentage helper is untouched. The k/yr case is unchanged.

Tests: `backend/tests/test_intake_t12_dollar_parse.py` grew from 11 to 34 cases, all synthetic. Committed first and recorded failing at 4c636141.
- before the fix, full suite: 561 passed, 1 skipped
- new tests added, fix not yet applied: 20 failed, 564 passed, 1 skipped
- after the fix: 584 passed, 1 skipped (no failures)

Known tradeoff: a real amount between 1900 and 2100 with no `$` and no comma (for example `GPR 2025`) now reads blank, because it cannot be told apart from a year.
