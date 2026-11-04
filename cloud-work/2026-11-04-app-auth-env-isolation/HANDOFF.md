# Handoff: app-auth-env-isolation

Branch: cloud/2026-11-04-app-auth-env-isolation, base main at 953cda4835602bbdfcf3df767adca936ddece3b5.

## What was done
- Reproduced: 49 backend tests fail when AUTH_JWT_SECRET=junk and GOOGLE_CLIENT_ID=junk are set in the host environment.
- Added one autouse fixture in backend/tests/conftest.py that clears AUTH_JWT_SECRET, AUTH_JWT_TTL_HOURS, GOOGLE_CLIENT_ID, ALLOWED_EMAILS and DREAM_STRICT_OWNERSHIP with monkeypatch.delenv(raising=False) before every test.
- Only that one file changed. No product code touched.

## Results (run from backend/ with its pytest.ini)
| Run | Before | After |
|---|---|---|
| Normal | 550 passed, 1 skipped | 550 passed, 1 skipped |
| AUTH_JWT_SECRET=junk GOOGLE_CLIENT_ID=junk | 49 failed, 501 passed, 1 skipped | 550 passed, 1 skipped |
| All five auth vars set to junk values | not run before | 550 passed, 1 skipped |

## Known limit
auth.py reads GOOGLE_CLIENT_ID and ALLOWED_EMAILS into module constants at import time. Those are read before any fixture runs, so a host value would still be captured there. In practice GOOGLE_CLIENT_ID is also re-read from the live environment at call time, and the all-vars-set run above passed. Fixing import-time capture would need a product code change, which was out of scope.

## Failing list before the fix (junk run)
- tests/test_auth_gate.py::test_auth_disabled_returns_stub_user
- tests/test_crm_api.py::test_attach_contact_to_deal_and_list
- tests/test_crm_api.py::test_contact_bad_role_rejected_but_valid_roles_pass
- tests/test_crm_api.py::test_contact_validation_400s
- tests/test_crm_api.py::test_create_and_get_person
- tests/test_crm_api.py::test_create_company
- tests/test_crm_api.py::test_create_task_and_note
- tests/test_crm_api.py::test_deal_delete_cascades_crm_links
- tests/test_crm_api.py::test_deal_items_filter_by_kind
- tests/test_crm_api.py::test_delete_contact_and_404
- tests/test_crm_api.py::test_item_validation_400s
- tests/test_crm_api.py::test_link_bad_kind_400
- tests/test_crm_api.py::test_link_into_missing_endpoint_404
- tests/test_crm_api.py::test_task_toggle_flips_status
- tests/test_crm_api.py::test_timeline_audit_is_read_only_view
- tests/test_crm_api.py::test_timeline_interleaves_audit_notes_tasks_newest_first
- tests/test_crm_api.py::test_toggle_rejects_note
- tests/test_crm_api.py::test_toggle_unknown_404
- tests/test_crm_api.py::test_update_contact_version_flow
- tests/test_deals_api.py::test_archive_hides_from_default_list
- tests/test_deals_api.py::test_archive_idempotent_no_version_bump
- tests/test_deals_api.py::test_archive_unarchive_delete_unknown_id_404
- tests/test_deals_api.py::test_audit_populated_after_driven_job
- tests/test_deals_api.py::test_delete_removes_deal_and_job_rows
- tests/test_deals_api.py::test_delete_while_job_running_409
- tests/test_deals_api.py::test_get_deal_job_block_at_cp1
- tests/test_deals_api.py::test_get_deal_job_block_blocking_questions
- tests/test_deals_api.py::test_unarchive_fallback_and_idempotency
- tests/test_deals_api.py::test_unarchive_restores_stashed_status
- tests/test_efb_jobs.py::test_ambiguous_signal_answered_efb_then_noi_then_cp1
- tests/test_efb_jobs.py::test_efb_invalid_engine_field_asks_and_answer_wins_on_resume
- tests/test_efb_jobs.py::test_efb_missing_stabilized_noi_awaits_then_resumes_to_cp1
- tests/test_efb_jobs.py::test_efb_submit_runs_to_cp1_with_rayzor_truth
- tests/test_jobs_api.py::test_answer_resumes_to_cp1
- tests/test_jobs_api.py::test_cancel_sets_flag
- tests/test_jobs_api.py::test_get_job_returns_status
- tests/test_jobs_api.py::test_idempotent_resubmit_returns_same_job
- tests/test_jobs_api.py::test_submit_missing_inputs_awaits_input
- tests/test_jobs_api.py::test_submit_runs_to_cp1
- tests/test_jobs_queue.py::test_async_answer_resume
- tests/test_jobs_queue.py::test_async_submit_returns_immediately
- tests/test_jobs_queue.py::test_sync_mode_flag
- tests/test_memo_api.py::test_memo_after_driven_job
- tests/test_review_fixes.py::test_deal_name_survives_synthesis
- tests/test_review_fixes.py::test_idempotent_replay_creates_no_orphan_deal
- tests/test_review_fixes.py::test_missing_engine_inputs_pauses_with_questions_then_resumes
- tests/test_review_fixes.py::test_red_gate_fails_closed
- tests/test_review_fixes.py::test_resume_rehydrates_original_docs_and_intake
- tests/test_review_fixes.py::test_slices_receive_only_bl17_trio_not_engine_answers
