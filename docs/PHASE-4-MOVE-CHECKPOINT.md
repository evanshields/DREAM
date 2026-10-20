# Phase 4 move checkpoint

October 20, 2026. Work stopped at Evan's request so Claude Code can move the folders.

The app branch is codex/phase-4-publish-screen. This checkpoint is unfinished engineering work, not a release or phase acceptance.

## Saved change

The provider now calls a separate evidence validator before storing a releasable result. The validator checks submitted identities, complete named-output coverage, raw audit values, all-sheet error evidence, check row identities, route applicability and acquisition return interpretation. It preserves raw values and return evidence separately, records the receipt hash and verifies the saved workbook hash. It removes the former unconditional release flag and raw-value fallback.

Files: backend/mono/provider.py, backend/mono/verification.py and backend/tests/test_mono_result_evidence.py. Backend Python files retain CRLF line endings.

## Verification and limits

Focused evidence and bridge-watchdog tests passed: 40 tests. Command: py -m pytest backend/tests/test_mono_result_evidence.py backend/tests/test_mono_bridge_watchdog.py -q.

The attempted full backend run stopped during collection. The selected Python 3.14 environment lacks python-multipart and PyJWT. No packages were installed. Its report is in [the model evidence folder](C:/Users/evana/dream-hq/models/_phase4/app-remediation-001-junit.xml). Password and review tests also reported missing bcrypt or JWT dependencies. This is not a passing full-suite result.

The new validator has not been exercised through a fresh native run or the signed-in app. Full lifecycle repairs, publication receipt binding on both paths, independent review and full regression checks remain open. The existing native investment audit covers three acquisition IRRs and no Bond IRRs. Non-IRR investment outputs still need the publisher's separate semantic binding work. Do not describe this checkpoint as closing the entire finding.

## Resume

Start from [DREAM HQ](C:/Users/evana/dream-hq), read its AGENTS.md and HANDOFF.md, then verify the actual app worktree location and branch. Do not assume the proposed app child exists until migration verifies it.

Locate the phase loop state under the moved Mono worktree. The expected handoff location is [the future phase state](C:/Users/evana/dream-hq/work/mono/deals/_reviews/2026-10-18/headless-vision/DREAM-PHASE-LOOP-STATE.json). That destination was not present when this checkpoint was written.

Use the existing prepared test environment or the exact CI environment without silently installing or switching dependencies. Run the complete app checks before treating this work as ready. Continue the accepted remediation plan, Esplanade source reconciliation, final Phase 3 and 4 acceptance, then all Phase 5 and 6 requirements. Seven of the approved 32 extra model runs remain. Run 25 completed read-only with no implementation edits.

The latest deck direction is six core pages plus an optional construction-budget page. The editable brief is [saved outside the moving folders](C:/Users/evana/Downloads/DREAM-SIX-PAGE-MEMO-BRIEF-2026-10-20.md).

The recurring review loop is paused for the move. Resume only after Evan resumes this chat. No workbook was changed, no deployment occurred and no merge is authorized by this checkpoint.
