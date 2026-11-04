# HANDOFF: app-backend-input-tests (stack layer 2 of 2)

Date 2026-11-04. Branch `cloud/2026-11-04-app-input-tests`, cut from layer 1 head `d73a0abbcf61732792dd06f71e0ba636c7edf843` (PR 15, branch `cloud/2026-11-04-app-gate-tests`). Layer 1 branch not touched.

## Step 1: layer 1 results at d73a0abb (file not edited)
Command: `pytest tests/test_gate_headline_numbers.py -rA` from `backend/`, venv with `requirements.txt` + `pytest==8.3.3`.
Result: **6 passed, 9 xfailed, 2 red** (17 collected items; the brief said 22 tests, the file collects 17 including 2 parametrized cases).

| Test | Result |
|---|---|
| b64_computed_deal_still_shows_headline_metrics | pass |
| b46_export_download_true_with_identity_mismatch_returns_json_not_file | pass |
| b47_reconcile_deal_with_no_headline_is_409 | pass |
| b47_reconcile_deal_with_empty_headline_is_409 | pass |
| b57_analyst_exception_fails_job_and_leaves_no_computed_deal | pass |
| b52_sync_runner_error_is_422_and_job_failed | pass |
| b64_gate_failed_deal_hides_headline_metrics_in_list_and_detail | xfail |
| b68_memo_refused_for_gate_failed_deal | xfail |
| b70_memo_with_number_not_in_headline_is_flagged | xfail |
| b33_agent_memo_rejects_client_supplied_model_results | xfail |
| b42_client_cannot_disable_identity_check_on_reconcile | xfail |
| b55_negative_purchase_price_is_treated_as_missing | xfail |
| b89_..._does_not_present_headline_values[run-failed] | xfail |
| b89_..._does_not_present_headline_values[run-in-progress] | xfail |
| b40b_conflicting_t12_lines_do_not_prefill_first_match | xfail |
| **b55_zero_exit_cap_is_treated_as_missing** | **RED: XPASS(strict)**. Wave 0 already treats exit_cap 0 as missing, so the xfail mark is wrong. Fix: remove the mark and keep the test as a plain pass. |
| **b40b_single_t12_line_still_extracts** | **RED: assertion** `0.0 == 4800000.0`. The synthetic line `Gross Potential Rent  $4,800,000` is not matched by `_extract_t12_from_text`, so the control fails and the sibling b40b xfail may be xfailing for the wrong reason. Fix: use a label/format the regex matches (read `intake_service.py:374+`). |

## Step 2: layer 2
New module `backend/tests/test_input_validation_fail_closed.py`: 66 items, **45 pass, 21 xfail strict, 0 red**. No product code changed.
Rows: B02 B08 B09 B12 B13 B21 B22 B23 B25 B26 B28 B32 B34 B35 B40 B44. No overlap with layer 1.

Fail closed already (plain passing tests): B21, B28, B08, B12 (24 routes parametrized), B13, B44, and B25 target_dscr 0.
Gaps pinned as xfail(strict): B02 (1), B09 (1), B22 (2), B23 (3), B25 (3), B26 (5), B32 (1), B34 (1), B35 (1), B40 (3).

Correction to the gap map: **B44 is already fail closed.** Text bytes named `a.xlsx` return a clean 422 JSON refusal, not a 500. Pinned as a normal passing test.
Note on B26: it was marked "unprobed" in the map. Probed now: agency-sizing with value 0, negative NOI, negative rate and exit-cap with going_in_cap 0 or negative all return 200.
Note on B34: the one xfail asserts a non-200 or a typed error event and no `[DONE]` after failure. A separate passing test pins today's `{"error": ...}` field.

## Full backend suite (from `backend/`, repo pytest.ini)
`2 failed, 601 passed, 1 skipped, 30 xfailed in 10.13s` at layer 1 head d73a0abb. The 2 failures were the layer 1 reds above. Baseline in the gap map was 550 passed, 1 skipped. See the restack section for the totals after the merge.

## Rows not done
None. All requested rows are covered.

## Stack observations
See the PR body. Observed facts are recorded there after the PR was opened.


## Restack onto new layer 1 head (2026-11-04, merge, no force push)
Observed:
- Layer 1 branch `cloud/2026-11-04-app-gate-tests` moved from `d73a0abb` to `584b9f23a7ba5aa79da6e6ca3ba87d51b166f5a8`. Layer 2 head before: `5674c679c0486fe0e0746d883715ee688c779c3e`.
- `git merge --no-ff origin/cloud/2026-11-04-app-gate-tests` made merge commit `6fec5cbb5d344844ffc4cd99568e09a36fcd9861` with no conflicts. The merge brought in edits to layer 1's `backend/tests/test_gate_headline_numbers.py` and its handoff file. No layer 2 file was changed by the merge.
- Own file `tests/test_input_validation_fail_closed.py`: 45 passed, 21 xfailed, 0 failed.
- Full backend suite from `backend/`: 602 passed, 1 skipped, 31 xfailed, 0 failed in 10.03s (venv from `requirements.txt` plus `pytest==8.3.3`).
- Read back through the GitHub API after the merge push: PR 16 head `6fec5cbb`, base sha `584b9f23` (was `d73a0abb`), 2 commits, 2 changed files, 614 additions, diff still shows only the layer 2 test file and this handoff file, mergeable state clean, still draft.
- Layer 1 branch and PR 15 were not touched.
Guess (not observed): the 2 earlier reds in layer 1 look fixed by the layer 1 update, since the suite is now 0 failed, but I did not rerun layer 1 alone.
