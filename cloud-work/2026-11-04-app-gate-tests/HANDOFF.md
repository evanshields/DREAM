# HANDOFF: app-backend-gate-tests (stack 1 of 2)

Branch cloud/2026-11-04-app-gate-tests, base main, draft PR. Layer 2 must branch from this head with base = this branch.

## What was added
One module: backend/tests/test_gate_headline_numbers.py. No product code changed. No test count or manifest exists in the repo, so none was updated.

## Results (executed)
Run in a sandbox virtualenv with backend/requirements.txt plus pytest==8.3.3, from backend/ with its pytest.ini. Observed at d73a0abb, then re-run after the repair commit.
- Before repair (d73a0abb): file 6 passed, 9 xfailed, 2 red (17 items collected, not 22).
- After repair: file 7 passed, 10 xfailed. Full backend suite 557 passed, 1 skipped, 10 xfailed.
- Red 1 fixed: b55_zero_exit_cap_is_treated_as_missing was XPASS(strict). The code already treats exit_cap 0 as missing, so the xfail mark was removed and it is a normal passing test.
- Red 2: b40b_single_t12_line_still_extracts failed with 0.0 == 4800000.0. The line DOES match. The cause is product behavior, not the fixture: _first_dollar uses a greedy [^\n]{0,80} before the number, so only the last digit is captured ($4,800,000 gives 0.0, "GPR 12" gives 2.0). No fixture can return the full amount. The test is now xfail(strict) under a new gap named B40c, and passes once the regex is fixed. No product code was changed.
- b40b conflicting-lines xfail: confirmed it fails because the first line is taken (gpr_annual is present, from the first line only). The value is truncated, as above.
Xfail list (10): B64 list/detail, B68, B70, B33, B42, B55 negative price, B89 (two fixtures), B40b conflicting lines, B40c single line.
Pass list (7): B64 control, B46, B47 (two), B55 zero exit cap, B57, B52.

## Rows not done
- B77 (stale item version 409): version conflict, not a gate or headline. Skipped.
- B94 (free-text headline string): marked HOLD in the gap map. Skipped.
- B71, B76, B93, B51: Low, not gate related.
- B26 (calculator bounds), B23, B25: Request validation section, outside the assigned B50-B96 range.
- B55 partly pinned: zero exit cap is already handled (passing test), negative purchase price is still accepted (xfail).

## Stack questions
- Observed: layer 2 PR 16 was opened as a draft with base = this branch at d73a0abb. This repair commit moves this branch ahead of that base, so layer 2 needs a merge or rebase of this branch to pick it up.
- The items below are still GUESS, not observed.
- Can a draft PR be the bottom of a stack? GUESS yes. GitHub allows a PR to target any branch, draft or not. A draft base only blocks merge of the draft itself. Observation: not tested.
- Pushing again to this branch: GUESS the layer-2 PR stays open with base = this branch, but its branch no longer contains the new head, so layer 2 needs a rebase or merge of this branch to pick it up. That makes a new layer-2 head, which means a fresh Argon review of layer 2. If layer 1 is force pushed or squash merged, layer 2 will likely show extra commits until rebased onto main. Not observed.
