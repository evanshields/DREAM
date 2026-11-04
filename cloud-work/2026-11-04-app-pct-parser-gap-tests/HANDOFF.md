# Handoff: app-pct-parser-gap-tests

Branch: cloud/2026-11-04-app-pct-parser-gap-tests (base main 953cda4835602bbdfcf3df767adca936ddece3b5)

## What was done
- Added backend/tests/test_intake_pct_parse_gaps.py (test file only, no product code).
- Target: `_first_pct` in backend/intake/intake_service.py. Draft PR 17 edits that file, so it was not touched.

## Results (run from backend/ with its pytest.ini, Python venv, requirements.txt plus pytest 8.3.3)
- New file: 6 passed, 17 xfailed (strict).
- Full backend suite: 556 passed, 1 skipped, 17 xfailed.

## Findings
- Argon's four gaps are all real: negative or parenthesized values read positive, per-month and per-unit rates read as annual, year or count values accepted, and an n/a or dash first column borrows a later column.
- Extra finding: the greedy gap in the regex eats leading digits, so 95% reads as 0.05, 12% as 0.02, and 5.0 % as 0.0. Only single digit values like 5% read correctly. This is the most serious gap because it hits clean input.

## Next steps
- Red team, then CEO marks ready, then Evan reviews and merges.
- Whoever fixes the helper (draft PR 17 area) should delete the xfail marks. Strict mode fails loudly when a gap closes.
