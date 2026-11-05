# DREAM app: fail-closed test gap map (backend + React)

Date 2026-11-03 (branch dated 11-04). Read-only report. No code, test or config changed. Base: `main`.
Sister report scope was the engine. This one is `backend/` (FastAPI) and `frontend/` (React). `underwriting-engine/` and old root `src/` and `archive/` are not mapped.

**Legend.** Tests live in `backend/tests/test_<file>.py` and are written `file::name` without the `test_` prefix. `NONE` = no test exercises the path. Pri: H = a silent pass could show a wrong or invented number, M = mislabel or mis-route, L = other. `HOLD` = in the snapshot panel or evidence viewer area the other team builds tomorrow. Map only, do not write tests there. Line numbers are from `main` at this commit.

## 1. Summary

**Suites run (no secrets, no network):**
- Backend: `pytest backend/tests` from `backend/` → `550 passed, 1 skipped in 13.13s`. Whole repo (`underwriting-engine/engine/tests`, `fastpath/tests`, `backend/tests`) → `693 passed, 20 skipped in 16.95s`.
- Skips: 19 engine populator tests ("Rayzor ACQ template not present", a real model file that is not in the repo) and 1 `analysts::kimi_live_smoke` (needs a live Kimi key). Not run: those 20, nothing else.
- Frontend: **no test runner exists** (`frontend/package.json` has no vitest, jest, or testing-library, zero `*.test.*` files). Only `npx tsc --noEmit` (exit 0) and `npm run build` (`✓ built in 9.50s`, exit 0) ran. Types only, so every React row below is NONE.

**Counts of paths (rows in this file).** Boundary: every B or F row inside a numbered table, including B40b (intake extraction) and F29. Recounted with Python over this file: 85 backend rows (B) and 29 frontend rows (F), 114 in all. A row is Covered when its last column says covered, otherwise it is a gap and carries a priority. Rows with a test that exists but does not assert the stated condition (B32, B46, B49, B94) count as gaps.

| Area | Rows | Covered | NONE | NONE High | NONE Med | NONE Low | HOLD rows |
|---|---|---|---|---|---|---|---|
| Auth + permissions (B01-B13) | 13 | 8 | 5 | 0 | 3 | 2 | 0 |
| Request validation + recalc (B20-B35) | 16 | 6 | 10 | 4 | 3 | 3 | 0 |
| Upload, export, intake (B40-B49, B40b) | 11 | 3 | 8 | 3 | 4 | 1 | 0 |
| Jobs, runner, deals, memo, stores, CRM (B50-B77) | 28 | 18 | 10 | 3 | 4 | 3 | 0 |
| Run status (B80-B96) | 17 | 14 | 3 | 1 | 1 | 1 | 3 |
| React guards (F01-F29) | 29 | 0 | 29 | 7 | 13 | 9 | 8 |
| **Total** | **114** | **49** | **65** | **18** | **28** | **19** | **11** |

The run-status engine adapter and view are the best covered area (about 130 tests, most written as "never shows complete" checks). Everything user-facing in React is untested.

**Top 10 untested High paths (build these first, none are on HOLD unless marked):**
1. **B64** `GET /api/deals` and `/api/deals/{id}` return `headline_metrics` for a `gate_failed` (RED gate) deal. Probed: list returned `{'irr': 0.2}` with status `gate_failed`. The runner keeps that spec "for forensics" (`runner.py:202`), the API hands it to the screen.
2. **F14** `useLiveCalc` keeps the last good result when a recalc fails (`livecalc.tsx:71-77` sets error, never clears result). Old numbers stay on screen beside a small red line. Used by BondScreen and the EFB panel.
3. **B25** `POST /api/underwrite/efb` accepts `stabilized_noi` of -5 and 0. Probed: -5 → HTTP 200, `bond_amount -71.79`. 0 → 200, bond 0.0. The job path blocks this (`wave0.py:176-178`), the direct endpoint does not.
4. **B23** `POST /api/recalc` with `total_equity: 0` → HTTP 200, `equity_multiple 0.0`, `coc_stabilized 0.0`, IRR null. A blank should beat a 0.0x. Probed.
5. **B68** `POST /api/deals/{id}/memo` writes a memo for a `gate_failed` deal (checks only that `headline_metrics` is non-empty, `memo.py:173-179`).
6. **B89** `view.py:106` marks values diagnostic only for blocked and stale. A `failed` or `in_progress` run that carries headline values is passed through and the page prints them in bold (`RunStatusParts.tsx:141`) under "No result was produced". Fixtures hide this because both have empty headlines.
7. **B46** Export with `download=true` and an identity mismatch: `test_export_excel.py:153-164` already makes this call but stores the response in `exp` and never asserts it. The gap is a missing assertion. A regression would stream a wrong-deal workbook and the test would still pass.
8. **B42** `require_identity_match` is a client form field (`export_excel.py:128`). Sending `false` skips the wrong-deal check and can return `reconciled: true`.
9. **F06 (HOLD)** DealDetail shows the headline tiles whenever any metrics exist, with no check of `gate_failed` (`DealDetail.tsx:186-192`, `339-350`). Front half of #1. Do not build now.
10. **B33** `POST /api/agent/memo` writes a memo from `model_results` sent by the client (`main.py:437-448`), not from the stored engine output. Numbers in the memo are not tied to the engine.

Also High, just outside the top 10: B40b (intake number extraction), F15 (sensitivity grid stays after an error), F10 (Pipeline card shows IRR on gate_failed, HOLD), B55 (job path does not check ACQ inputs are positive, not probed), F29 (main recalc error keeps old metrics on screen), B26 (calculators have no bounds, not probed).

**Tests that pass for the wrong reason:**
- **W1** `auth_gate::*` (4 tests) prove `require_auth` on a toy app with one route (`/api/me`). They keep passing if a real router loses `dependencies=[Depends(require_auth)]` (`main.py:90-114`). Only run-status (`run_status_auth::main_mounts_router_with_require_auth`) and intake (AST check) prove the mount. Six other routers have no such proof. `auth_enabled_rejects_invalid_token` uses the string `not-a-real-token`, which fails before any Google check, so a well-formed expired token is never tried.
- **W2** `review_fixes::red_gate_fails_closed` swaps `run_synthesis` for a fake result with `ok=False`. It proves the runner reacts to a RED summary, not that a real RED gate reaches it.
- **W3** `legacy_underwrite_retired::validate_still_works_with_minimal_body` locks in that `{}` validates. It only works because `models.py:31-35` invents a deal ("New Deal", 186 units, $1,200 rents).
- **W4** `run_status_view::diagnostic_flag_only_for_blocked_and_stale` and `blocked_and_stale_still_show_values` pass because the failed and in-progress fixtures have empty headlines. They never test a failed run that has values.
- **W5** `run_status_boundaries::no_arithmetic_operators_in_slice_code`, `forbidden_words_absent` scan source text, not behavior. They are fine as guards but do not prove a number path.

## 2. Backend

### 2a. Auth and permissions
| ID | Where | Condition → response | Test | Red test / Pri |
|---|---|---|---|---|
| B01 | auth_dep.py:100-101 | No `GOOGLE_CLIENT_ID` and no `AUTH_JWT_SECRET` → stub user, every route open | auth_gate::auth_disabled_returns_stub_user | covered (pins the open mode) |
| B02 | auth_dep.py:100 | Production server started with both env vars missing stays open, no refusal | NONE | app with `DREAM_ENV=prod` and no auth env → 401 or startup error. M |
| B03 | auth_dep.py:102-104 | No bearer token → 401 | auth_gate::auth_enabled_blocks_unauthenticated (W1) | covered |
| B04 | auth_dep.py:73-78 | Bad, expired, wrong-secret app JWT → 401 | password_login::require_auth_rejects_expired_app_jwt, _garbage_jwt, _jwt_signed_with_wrong_secret | covered |
| B05 | auth_dep.py:40-46 | Email not in ALLOWED_EMAILS → 403 (app JWT and Google) | password_login::require_auth_app_jwt_non_allowlisted_403, _google_path_enforces_allowlist | covered |
| B06 | auth_dep.py:117-119 | JWT-only server, non-app token → 401 not 500 | review_fixes::jwt_only_server_bad_token_is_401_not_500 | covered |
| B07 | auth_dep.py:120 | Invalid Google token → 401 | auth_gate::auth_enabled_rejects_invalid_token (W1) | covered |
| B08 | auth.py:52 | `GOOGLE_CLIENT_ID` unset inside `verify_google_token` → 500 | NONE | call with env unset → 500 and message names no secret. L |
| B09 | app_jwt.py:37, auth_login.py:84 | `AUTH_JWT_SECRET` unset at login → `JWTConfigError` (unhandled, 500) | NONE | login with secret unset → clean 503/401. L |
| B10 | auth_login.py:67-74 | Wrong password or unknown user → same 401 | password_login::login_bad_password_401, login_unknown_user_401 | covered |
| B11 | auth_login.py:77-81 | Login for non-allowlisted email → 403 | password_login::login_non_allowlisted_403 | covered |
| B12 | main.py:90-114 | 6 routers (recalc, export, jobs, deals, crm, memo) and `/api/me`, `/api/validate`, `/api/agent/*` mounted with `require_auth` | NONE for the mount (run-status and intake have one) | with auth env set, GET each router's path with no token → 401. M |
| B13 | deals.py:134-139 | `DREAM_STRICT_OWNERSHIP` on: other owner's deal → 404 | NONE (grep finds no `STRICT` in tests) | strict env + other owner archive → 404. M |

### 2b. Request validation and calc endpoints
| ID | Where | Condition → response | Test | Red test / Pri |
|---|---|---|---|---|
| B20 | recalc.py:54 | `exit_cap` ≤ 0 → 422 | review_fixes::recalc_rejects_zero_exit_cap | covered |
| B21 | recalc.py:55 | `sale_year` < 1 → 422 | NONE | post `sale_year:0` → 422. L |
| B22 | recalc.py:76-77, 142-143, 151-152 | Any engine exception → 422 with raw Python text (`list index out of range` for empty `noi_series`, `float division by zero` for `refi_amort_years:0`, probed) | NONE | empty `noi_series` → 422 with a plain message, not an exception string. M |
| B23 | recalc.py:43-52 | Fields have no bounds. `total_equity:0` → 200 with `equity_multiple 0.0`, `coc 0.0` (probed). Negative loans also accepted | NONE | `total_equity:0` → 422 or null multiple. **H** |
| B24 | recalc.py:138-141 | Unknown routing → 400 | underwrite_v2_and_sensitivity::underwrite_v2_unknown_routing_400 | covered |
| B25 | recalc.py:123-130, 146-152 | EFB: `stabilized_noi` -5 → 200 `bond_amount -71.79`, 0 → 200 bond 0.0, `target_dscr:0` → 422 (all probed) | NONE (`underwrite_efb_typed_endpoint` is the happy path) | `stabilized_noi:-5` → 422. **H** |
| B26 | recalc.py:82-114 | exit-cap and agency-sizing calculators: no bounds (value 0, negative rate). Not probed | NONE | `stabilized_value:0` → 422. **H** (unprobed) |
| B27 | recalc.py:180-188 | Sensitivity: unknown field or metric → 400, exit_cap sweep value ≤ 0 → 400 | underwrite_v2_and_sensitivity::sensitivity_rejects_unknown_field, _unknown_metric, review_fixes::sensitivity_rejects_zero_in_exit_cap_sweep | covered |
| B28 | recalc.py:196 | `hm.get(metric)` missing → null in grid (blank) | NONE | metric absent from result → null, not 0. L |
| B29 | engine_boundary.py:81-87 | NaN or inf → None (blank) | review_fixes::f_maps_non_finite_to_none | covered |
| B30 | engine_boundary.py:329-349 | Unknown routing → `UnknownRoutingError` | engine_boundary_efb_and_routing::routing_unknown_raises | covered |
| B31 | main.py:333 | `/api/underwrite` retired → 410 | legacy_underwrite_retired::legacy_underwrite_returns_410 | covered |
| B32 | main.py:336-348, models.py:31-35 | `/api/validate` with `{}` validates a made-up default deal (W3) | validate_still_works_with_minimal_body (W3) | `{}` → 422 missing fields. M |
| B33 | main.py:437-450 | `/api/agent/memo` writes from client-sent `model_results`, any error → 422 | NONE | memo input differing from stored deal → rejected. **H** |
| B34 | main.py:376-434 | `/api/agent/chat`: stream errors sent as `data:{error}` inside HTTP 200 | NONE | Kimi raises → client sees non-200 or `error` event type. M |
| B35 | main.py:372-373 | Intake: any exception → 422 with `str(e)` | NONE | corrupt bytes → 422 with fixed text. L |

### 2c. Upload, export, intake
| ID | Where | Condition → response | Test | Red test / Pri |
|---|---|---|---|---|
| B40 | main.py:360 | Intake reads whole file: no size cap, no extension allowlist, no empty-file check, unknown extension tries PDF (`intake_service.py:230-235`) | NONE | 0-byte file and 100 MB file → 4xx. M |
| B41 | intake_service.py:140-160 | Kimi classification failure → warning, falls back to filename guess | NONE | Kimi raises → `warnings` non-empty, doc_type from filename. M |
| B42 | export_excel.py:128 | `require_identity_match=false` from client skips the wrong-deal check | NONE | mismatch + `false` → still 409. **H** |
| B43 | export_excel.py:88-89 | Template not `.xlsx` by file name → 400 | export_excel::export_rejects_non_xlsx_template | covered (name only, no content check) |
| B44 | export_excel.py:98 | Template bytes not read for size or type, `.xlsx` name on text bytes | NONE | text bytes named `a.xlsx` → 422 not 500. M |
| B45 | export_excel.py:85-86, 137-138 | Unknown deal → 404 | export_excel::export_unknown_deal_404, reconcile_unknown_deal_404 | covered |
| B46 | export_excel.py:106-119 | Identity blocked or diff not ok → JSON report, no file | `export_blocks_on_identity_mismatch` asserts `download=false`. `reconcile_identity_mismatch_409` (lines 153-164) calls `download=true` with a mismatched identity but never asserts `exp` (missing assertion) | assert `exp` is a JSON report, not a file. **H** |
| B47 | export_excel.py:140-143 | Reconcile on deal with no headline → 409 | NONE | draft deal → 409. M |
| B48 | export_excel.py:157-158 | Identity mismatch on reconcile → 409 | export_excel::reconcile_identity_mismatch_409 | covered |
| B40b | intake_service.py:347-372, 572-583, field_mapper.py | Intake number extraction (`_first_dollar`, `_first_pct`, unit-mix parsing) takes the first match. A wrong pull from an OM becomes a prefilled form value | NONE (zero tests for `process_file` or `field_mapper`) | rent roll with two "Total" lines → prefill blank, not first match. **H** |
| B49 | export_excel.py:153, 164-171 | Non-numeric headline silently dropped, None excel cell → `not_recalced` | export_excel::reconcile_flags_unrecalced_draft (flag only) | non-numeric headline surfaces as a row, not dropped. L |

### 2d. Jobs, runner, deals, memo, stores, CRM
| ID | Where | Condition → response | Test | Red test / Pri |
|---|---|---|---|---|
| B50 | jobs.py:238, 305 | Unknown job → 404 (get) | jobs_api::get_missing_job_404 | covered |
| B51 | jobs.py:253-255, 305 | Unknown job or question on answer / cancel → 404 | NONE | answer unknown question id → 404. L |
| B52 | jobs.py:214-215, 283-284 | Sync runner error → 422 | NONE | analyst raises → 422 and job FAILED. M |
| B53 | runner.py:99-101 | Job at CP-1 or terminal re-run → no-op | runner::rerun_paused_at_cp1_is_noop | covered |
| B54 | wave0.py:176-178, 188-190, 255-285 | Missing purchase_price, hold_years, exit_cap, or EFB NOI ≤ 0 → blocking question, AWAITING_INPUT | wave0::missing_input_blocks_with_open_question_per_missing, efb_non_positive_noi_treated_as_missing, jobs_api::submit_missing_inputs_awaits_input, runner::missing_inputs_stop_at_awaiting_input | covered |
| B55 | wave0.py:105-129 and the imported `state_ledger.CriticalInputs` contract (`wave0.py:52-55`) | Main ACQ extraction casts to float or int and only checks for None or "" (the `_Shim.missing` at line 129 is a fallback, not the main path), so `exit_cap:0` or negative price pass Wave 0 (not probed) | NONE | `exit_cap:0` answer → asked again. **H** (unprobed) |
| B56 | runner.py:197-209 | Blocking gate → deal `gate_failed`, job FAILED | review_fixes::red_gate_fails_closed (W2) | covered (weak) |
| B57 | runner.py:234-236 | Any exception inside run → job FAILED, error stored | NONE | analyst raises → FAILED, deal not `computed`. M |
| B58 | queue.py:128 | Restart sweep marks stranded jobs FAILED, spares paused ones | jobs_queue::sweep_stale_jobs | covered |
| B59 | contracts.py:155 | Illegal job transition → `InvalidTransition` | job_store::transition_enforces_state_machine | covered |
| B60 | analysts.py:253-299 | Bad slice output → `SchemaValidationError` | analysts::validate_slice_rejects_bad_cell | covered |
| B61 | synthesis (routing) | Unknown routing fails closed in synthesis | efb_jobs::synthesis_unknown_routing_still_fails_closed | covered |
| B62 | jobs.py:99-102 | Headline metrics shown only at AWAITING_CP1 | jobs_api::submit_runs_to_cp1 | covered |
| B63 | jobs.py:46-50 | LLM-inferred cell → OpenQuestion, never a headline | analysts::stub_has_one_llm_inferred_open_question | covered |
| B64 | deals.py:78-101 (list), 273-291 (detail) | List and detail return `headline_metrics` and `spec` whatever the status, including `gate_failed` (probed) | NONE | `gate_failed` deal → `headline_metrics == {}` in list and detail. **H** |
| B65 | deals.py:139, 146, 247, 281 | Unknown deal → 404 | deals_api::get_deal_unknown_id_404, audit_unknown_deal_404, archive_unarchive_delete_unknown_id_404 | covered |
| B66 | deals.py:222-226 | Delete while job running → 409 | deals_api::delete_while_job_running_409 | covered |
| B67 | memo.py:169-170, 174-179 | Memo for unknown deal → 404, no headline → 409 | memo_api::memo_unknown_deal_404, memo_uncomputed_draft_409, memo_empty_headline_metrics_409 | covered |
| B68 | memo.py:174 | Memo for `gate_failed` deal with stored headline → generated | NONE | `gate_failed` + headline → 409. **H** |
| B69 | memo.py:185-186 | LLM failure → 502, nothing stored | memo_api::memo_generator_failure_502 | covered |
| B70 | memo.py:188-195 | Memo prose is not checked against engine numbers (only a draft marker) | NONE | memo text with a number not in `headline_metrics` → flagged. M |
| B71 | memo.py:198-199 | Version conflict on save → 409 | NONE | stale `expected_version` → 409. L |
| B72 | deal_store.py:194-209 | Not found and version conflict raise | deal_store (line 61 region), crm_store (88) | covered |
| B73 | crm.py:130-165, 340-374 | Contact, item, link body checks → 400, unknown ids → 404 | crm_api::contact_validation_400s, item_validation_400s, link_bad_kind_400, link_into_missing_endpoint_404 | covered |
| B74 | crm.py:214-216 | Contact update without integer `version` → 400 | crm_api::update_contact_version_flow (test lines 104-114) | covered |
| B75 | crm.py:220-224 | Contact update with stale `version` → 409 | crm_api::update_contact_version_flow (replay of version 1) | covered |
| B76 | crm.py:277-279 | Item update without integer `version` → 400 (contact path is B74) | NONE (no item version test) | item PUT without version → 400. L |
| B77 | crm.py:283-287, 305-312 | Item update stale `version` → 409, and task toggle with a stale supplied version → 409 (contact path is B75) | NONE via API (store-level conflict only) | stale item PUT and stale toggle → 409. M |

### 2e. Run status (engine output: missing, stale, failed)
| ID | Where | Condition → response | Test | Red test / Pri |
|---|---|---|---|---|
| B80 | run_status.py:28-32 | Bad or unknown run id → 404 | run_status_api::bad_ids_404, unknown_id_404, max_length_id_is_just_unknown, engine_source::traversal_and_bad_ids_404 | covered |
| B81 | loader.py:21-36 | Fixture not synthetic, id mismatch, bad JSON → ignored | run_status_failclosed::non_synthetic_file_rejected, missing_synthetic_flag_rejected, run_id_mismatch_rejected, malformed_json_is_none | covered |
| B82 | loader.py:49-58 | `DREAM_RUNS_DIR` unset or bad → fixtures only | engine_source::unset_env_serves_fixtures_only, blank_or_missing_dir_serves_fixtures_only | covered |
| B83 | loader.py:75-105, 137-144 | Symlink, outside root, oversize, repeated key, non-object, wrong slug → rejected | engine_source::symlinked_*_rejected, record_for_other_deal_rejected, malformed_run_json_404_and_not_listed, pr10_repair::r7_duplicate_key_*, a2_oversized_bote_* | covered |
| B84 | view.py:36-41 | Unknown, malformed or missing gates → blocked | run_status_failclosed::unknown_gate_status_is_blocked, gate_without_status_key_is_blocked, empty_gates_on_terminal_run_is_blocked, missing_gates_key_is_blocked | covered |
| B85 | view.py:61-67 | Provenance missing or different → stale | run_status_failclosed::missing_provenance_both_sides_is_stale, absent_provenance_keys_is_stale, view::stale_by_input_hash | covered |
| B86 | view.py:44-50 | Evidence missing, mismatched, absent on settled run → blocked. **HOLD (evidence viewer)** | run_status_failclosed::bad_evidence_is_blocked, completed_without_evidence_is_blocked | covered |
| B87 | view.py:70-89 | Order failed → blocked → stale → human check, unknown status → failed | view::status_mapping, blocked_beats_in_progress, stale_beats_in_progress | covered |
| B88 | adapter.py:222-239 | Headline blank with reason when bote missing, null, rejected, non-scalar | engine_source::no_bote_gives_blank_values_with_reason, pr10_repair::a2_*, l1_non_scalar_headline_value_is_blank_with_reason, view::null_stays_null, verified_zero_stays_zero | covered |
| B89 | view.py:106 | Values flagged diagnostic only for blocked and stale. `failed` or `in_progress` with values pass through (W4) | NONE (fixtures have empty headlines) | failed fixture with `headline` values → blanked or diagnostic. **H** |
| B90 | adapter.py:242-262 | Complete only if stages 1-8 once each, all ok, typed lists, not cut short, not skipped | pr10_repair::a1_*, r5_*, r6_*, engine_source::waiting_*_never_complete, stop_after_run_is_not_complete | covered |
| B91 | adapter.py:159-220 | Evidence file hash missing, changed, oversize, duplicate → not verified. **HOLD (evidence viewer)** | pr10_repair::a3_*, a4_*, r7_*, r8_* | covered |
| B92 | adapter.py:77-99 | Stage statuses → gates, unreadable stage → missing | engine_source::unknown_or_missing_stage_data_is_blocked_never_complete, stage6_failure_shows_blocked_and_red | covered |
| B93 | view.py:58 | `count_missing_values` assumes dict items (`h.get`) → AttributeError 500 on odd shape | NONE | headline item `None` → blocked, not 500. L |
| B94 | adapter.py:235 | Headline value allowed as free text string, shown as-is | pr10_repair::l1_non_scalar... (non-scalars only) | `"n/a"` string value → blank. M. **HOLD (snapshot data)** |
| B95 | run_status.py:16-23 | List endpoint builds summary for every run | run_status_api::list_returns_six_runs | covered |
| B96 | run_status.py (methods) | Non-GET → 405 | run_status_api::write_methods_405, router_only_registers_get | covered |

## 3. React (`frontend/src`). No tests exist. All NONE.
| ID | Where | Guard | Red test (needs a runner, none installed) / Pri |
|---|---|---|---|
| F01 | auth/RequireAuth.tsx:12-22 | Wait for `ready`, no token → `/login` | render with no token → redirect, no child. M |
| F02 | lib/api.ts:66-69, 858-861, AuthContext.tsx:61-80 | 401 clears token, "session expired", stored token checked with `/api/me` | 401 response → token removed. M |
| F03 | lib/api.ts:72-80 | Non-OK → `ApiError` with server `detail` | 422 `{detail}` → message shown. L |
| F04 | pages/Underwrite.tsx:222-224, 385-388 | Job `failed` → FailedPanel, no tiles | failed job view → no metrics. M |
| F05 | pages/Underwrite.tsx:874-967 | Submit disabled until every blocking question answered, numeric parse `Number.isFinite` | blank answer → button disabled. H |
| F06 | pages/DealDetail.tsx:186-192, 339-350 | **HOLD (snapshot).** Headline from job or deal, no `gate_failed` check, empty-state text when none | gate_failed deal → no tiles. **H** |
| F07 | pages/DealDetail.tsx:419-434 | **HOLD (snapshot).** `typeof number` else `—` | string irr → `—`. M |
| F08 | components/EFBMetricTiles.tsx:45-109 | **HOLD (snapshot).** `!= null` else `—`. `fmtUSD(-72)` prints `$-72` | negative bond → `—`. **H** |
| F09 | pages/DealDetail.tsx:264-274, 105-120 | Seeds only finite numbers and number arrays from stored spec | NaN series dropped. L |
| F10 | pages/Pipeline.tsx:410-471 | **HOLD (snapshot).** Card shows IRR/bond when present, status badge only, "Not yet computed" else | gate_failed card → no IRR. **H** |
| F11 | pages/Pipeline.tsx:99, 842-844 | `gate_failed` / failed / cancelled grouped as attention column | gate_failed deal lands in attention column. M |
| F12 | pages/Pipeline.tsx:269-272, 291 | Error banner, empty list text | fetch fails → banner. L |
| F13 | hooks/useJobPolling.ts:28, 74-82 | 3 failures in a row → stop and report, terminal statuses stop | 3 errors → onError once. M |
| F14 | components/livecalc.tsx:71-77 | Error sets a message but **keeps last result** (stale numbers beside a red line) | failing second call → result cleared. **H** |
| F15 | components/AssumptionDashboard.tsx:419-435, 488-490 | Sensitivity error sets message, grid data kept | failing sweep → chart cleared. **H** |
| F16 | components/AssumptionDashboard.tsx:287, 581 | `—` when no value / null point | null point → `—`. L |
| F17 | components/livecalc.tsx:18-24, 36, 141-142 | Null → `—`, non-finite input ignored, required field can't be blanked | `abc` input ignored. L |
| F18 | pages/BondScreen.tsx:95, 112, 228, 245 | `!= null` else `—` | null max_loan → `—`. L |
| F19 | components/DealMemo.tsx:27-36, 130 | Error state for 409/502, empty-memo text, generated memo wins over stored | 409 → "not computed" message. M |
| F20 | components/DealExport.tsx:108-123 | Refusal groups always shown, none collapsible | refusals visible. M |
| F21 | pages/RunStatus.tsx:17-34, 60, 91 | **HOLD (evidence viewer).** Loading / error / empty states, abort on change | 404 → message, no data. M |
| F22 | components/runstatus/RunStatusParts.tsx:65-77, 109-148 | **HOLD (evidence viewer).** Loud banner for blocked/stale/failed, `null` → "Blank" plus reason, diagnostic notice. `value === null` only, so `undefined` prints "undefined" | undefined value → "Blank". M |
| F23 | components/runstatus/RunStatusParts.tsx:40-46, 173 | **HOLD (evidence viewer).** Evidence badge per state (unverified, mismatch shown) | hash_mismatch → red badge. M |
| F24 | whole app (grep: no `ErrorBoundary`, `componentDidCatch`) | No error boundary. A render throw (for example `.toFixed` on a string) blanks the whole app | child throws → fallback shown. M |
| F25 | lib/format.ts:3-13 | `fmtUSD/fmtPct/fmtEM` have no null, NaN or negative guard, callers must guard (most do) | `fmtPct(NaN)` → `—`. L |
| F26 | App.tsx:84-86 | Unknown URL → `/pipeline` (RequireAuth bounces if signed out) | unknown path → redirect. L |
| F27 | lib/runStatusApi.ts:88-90 | **HOLD (evidence viewer).** Non-OK → `ApiError`, 404 text | 404 → "Run not found." L |
| F28 | lib/download.ts, api.ts:839-870 | Export download branches on Content-Type, error JSON not saved as xlsx | JSON body → no file. M |
| F29 | components/AssumptionDashboard.tsx:173-190 | Main `runRecalc` error path sets the message but never clears `metrics`, so old headline numbers stay visible beside the error (compare F14 for the hook, F15 for the sweep) | failing recalc → metrics cleared. **H** |

## 4. Not covered here
- `backend/intake/field_mapper.py` and `intake_service.py` number extraction is row **B40b** in table 2c (High). It is counted in the summary, not outside it.
- `store/user_store.py` password-attempt tracking records failures but never locks out (no rate limit on `/api/login`). Not a number risk. L.
- Old root `src/`, `archive/`, `underwriting-engine/` (sister report).
- Run-status fixtures only, real engine runs need `DREAM_RUNS_DIR` (the 27 `engine_source` tests build synthetic folders).

## 5. Method
Read each backend router, store, job, run_status and auth file for `raise`, `HTTPException`, pydantic `Field`, env gates. Read each React page and component for null, error, empty and finite checks. Matched against test names and bodies. Three probe scripts in the scratchpad (not committed) used FastAPI `TestClient` on in-memory stores to confirm B23, B25, B22 and B64. No network, no live app, no secrets.
