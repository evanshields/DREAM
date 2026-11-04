# HANDOFF: app-backend-gate-tests (stack 1 of 2)

Branch cloud/2026-11-04-app-gate-tests, base main, draft PR. Layer 2 must branch from this head with base = this branch.

## What was added
One module: backend/tests/test_gate_headline_numbers.py. No product code changed. No test count or manifest exists in the repo, so none was updated.

## NOT EXECUTED (important)
The cloud sandbox has pytest but not fastapi, numpy_financial or the other backend requirements, and the job rule was install nothing. The module was only byte-compiled (python3 -m py_compile). Pass/xfail outcomes below are from reading the code, not from a run. First CI run is the real check. A wrong guess shows as either a failure (test expected to pass did not) or an XPASS strict failure (expected gap is already fixed).

## Rows covered
B33 B40b B42 B46 B47 B52 B55 B57 B64 B68 B70 B89 (plus control tests for B64 and B40b).
Expected xfail(strict): B33, B40b, B42, B55 (zero exit cap, negative price), B64, B68, B70, B89 (two fixtures).
Expected pass: B46, B47 (two), B52, B57, B64 control, B40b control.

## Rows not done
- B77 (stale item version 409): version conflict, not a gate or headline. Skipped.
- B94 (free-text headline string): marked HOLD in the gap map. Skipped.
- B71, B76, B93, B51: Low, not gate related.
- B26 (calculator bounds), B23, B25: Request validation section, outside the assigned B50-B96 range.
- B55 only partly pinned: gap map says not probed. Tests assume Wave 0 passes zero and negative values.

## Stack questions (nothing here was observed, all GUESS)
- Can a draft PR be the bottom of a stack? GUESS yes. GitHub allows a PR to target any branch, draft or not. A draft base only blocks merge of the draft itself. Observation: not tested.
- Pushing again to this branch: GUESS the layer-2 PR stays open with base = this branch, but its branch no longer contains the new head, so layer 2 needs a rebase or merge of this branch to pick it up. That makes a new layer-2 head, which means a fresh Argon review of layer 2. If layer 1 is force pushed or squash merged, layer 2 will likely show extra commits until rebased onto main. Not observed.
