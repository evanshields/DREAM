# DREAM Phase 5: CRM Layer — Full Implementation Plan (for Fable orchestration)

**Date:** 2026-07-13
**Status:** Ready to hand to Fable as the orchestration blueprint.
**Source:** [TWENTY-CRM-BORROW-LIST-2026-07-13.md](TWENTY-CRM-BORROW-LIST-2026-07-13.md) (the 10 ranked items) + the license audit at the absolute path `c:\Users\evana\shieldstone_os\shieldstone_operations\third-party-audits\2026-07-13-twenty-crm.md` (in the shieldstone_os repo, opens directly in VS Code).
**Branch to build on:** `wave-a-foundation` (the live app lives here; `main` is a stale pre-consolidation codebase, see Cross-Phase Impact below).

---

## How to use this document

This is the plan Fable builds FROM. It maps all 10 borrow-list items to exact DREAM files, API contracts, the locked-constraint guardrails each must honor, per-session collision boundaries (so parallel builders never touch the same file), and the test bar. Every item is inspiration-only per the license audit: study Twenty's approach, write DREAM's own code, never paste Twenty source.

Fable's job: orchestrate parallel builders against the session boundaries below, using DREAM's proven working pattern (builders draft in the working tree with no commit, main session reviews the diff, full test suite + tsc/build green, commit, deploy with timestamped VPS backups, live-verify against production).

---

## LOCKED CONTRACTS (violate = failure) — copied from HANDOFF, every builder honors these

- Decimal only in `engine_boundary.py` + the vendored engine. The CRM layer touches no financial math, so this is a non-issue, but do not introduce floats anywhere near a metric.
- The spec is the canonical document. The CRM stores are NEW canonical documents of their own kind (a contact doc, a task doc), following the same opaque-doc + derived-index rule. They never mutate the deal spec.
- HITL stops at AWAITING_CP1. Unchanged; CRM does not touch the job pipeline.
- **No `sqlite3` import outside `backend/store/`.** Every new CRM store lives in `backend/store/` and uses `open_sqlite()` / `default_db_path()` from the store package. This keeps the Wave F Postgres swap a drop-in.
- headline_metrics + qa.* NEVER from an LLM. CRM notes/tasks are user-authored or plain CRUD; no LLM writes a metric.
- Fail closed on RED gates. Unchanged.
- The vendored `underwriting-engine/` is untouched.
- LLM slices receive ONLY wave0's scalar critical inputs. Unchanged; CRM does not feed the LLM.

**One product constraint to resolve before building (Decision 1 below):** the [CLAUDE_DESIGN_BRIEF.md](../CLAUDE_DESIGN_BRIEF.md) pins "confirm-before-delete" as a hard constraint. Item 7 (undo-delete toast) would replace it. Evan must approve the swap or item 7 keeps the confirm popup.

---

## The store idiom every CRM store must follow

Clone the shape of [deal_store.py](../../backend/store/deal_store.py) and [job_store.py](../../backend/jobs/job_store.py) exactly:

- Opaque JSON document is the source of truth; a thin relational index is DERIVED from it via a `_index_from_spec()`-style function, never authored independently.
- A `Protocol` (create / get / put / list / delete) is the only interface the app depends on. SQLite now, Postgres later.
- Optimistic concurrency: integer `version` + the existing `VersionConflict` (import from the store package, do not redefine).
- Timestamps are passed IN (`now_iso`), never generated inside the store.
- Share the one DB file via `open_sqlite()` + `default_db_path()`. Register the new table's `CREATE TABLE IF NOT EXISTS` in the store's own `_SCHEMA`.
- Cascade deletes follow `job_store.delete_for_deal(deal_id)` (returns count).
- Router tests use the standalone-mount idiom (see `backend/tests/test_deals_api.py`): TestClient with injected stores, `require_auth` returns the local-dev stub when no auth env is set.
- Store unit tests follow `backend/tests/test_deal_store.py`.

Per Evan's decision, use ONE `crm_store.py` with `kind`-discriminated tables (not four separate sibling stores):
- `contacts` table: person + company rows discriminated by `kind` ('person' | 'company'), with a DREAM-native `role` on persons: `'broker' | 'seller' | 'lender' | 'bond_counsel' | 'issuer' | 'nonprofit_sponsor' | 'other'` (Decision 3, 6+ roles; issuer + nonprofit_sponsor serve EFB bond deals).
- `crm_items` table: task + note rows discriminated by `kind` ('task' | 'note').
- `crm_links` index table: `(source_kind, source_id, target_kind, target_id)` — the simplified target-pointer pattern (two-plus-two plain columns, matched at query time, no DB-enforced FK), adapted from Twenty's TaskTarget/NoteTarget join.

---

## The 10 items mapped to files, contracts, and tests

### Item 1 — CRM store (contacts + tasks/notes + links)  [Session 1, backend]
- **New file:** `backend/store/crm_store.py`. Export from `backend/store/__init__.py`.
- **Shapes (opaque docs):**
  - contact(person): `{contact_id, kind:'person', full_name, role, company_id?, emails[], phones[], linkedin_url?, notes?, tags[], created_at, updated_at, version}`. Index: `contact_id, kind, full_name, role, company_id, primary_email, created_at, updated_at`.
  - contact(company): `{contact_id, kind:'company', name, company_type, domain?, address?, notes?, ...}`. Index: `contact_id, kind, name, company_type, domain, ...`.
  - task: `{item_id, kind:'task', title, body?, status:'open'|'done', due_at?, assignee?, created_at, updated_at, version}`. Index: `item_id, kind, status, due_at, assignee, created_at, updated_at`.
  - note: `{item_id, kind:'note', title?, body, author?, created_at, updated_at, version}`. Index: `item_id, kind, author, created_at, updated_at`.
  - link: index-only row `(link_id, source_kind, source_id, target_kind, target_id, created_at)`.
- **Field vocabulary** cribbed (retyped, DREAM-named) from Twenty's `person/company/task/note.workspace-entity.ts`. Do not paste.
- **Cascade:** `delete_contact` / `delete_item` also delete their `crm_links` rows. A deal delete (`deals.py::delete_deal`) also calls `crm_store.delete_links_for_target('deal', deal_id)` — extend `delete_deal`, do NOT change its 409-while-running guard.
- **Tests:** `backend/tests/test_crm_store.py` (CRUD, version conflict, link attach/detach, cascade).

### Item 2 — Unified deal timeline  [Session 1 backend + Session 2 frontend]
- **New endpoint:** `GET /api/deals/{deal_id}/timeline` in a new `backend/routers/crm.py` (or extend `deals.py`; prefer a new router to keep collision boundaries clean). READ-TIME projection: interleave the existing job-audit events (reuse `deals.py::get_deal_audit` logic / the job store) with `crm_items` (notes + tasks) linked to this deal, sorted by ts. Shape: `{deal_id, events: [{id, source:'audit'|'note'|'task', kind, ts, actor?, title, detail?}]}`.
- **Guardrail:** the append-only audit system is NEVER mutated. The timeline is a view, not a second source of truth. Do not write timeline rows (that is Twenty's queue-driven approach; read-time merge is correct at DREAM volume).
- **Frontend:** extend [DealAudit.tsx](../../frontend/src/components/DealAudit.tsx). Add `note` / `task` / `doc_event` to the `KIND_STYLE` map (icon + color). The component becomes the "Activity" tab's unified feed.
- **Month-grouping is a firm spec, not optional** (confirmed from Twenty's `activities/timeline-activities/components/EventsGroup.tsx` + `utils/groupEventsByMonth`): group events under a "Month Year" separator line, newest month first, with the vertical connector spine DealAudit already draws. This is the standard CRM timeline shape; match it.
- **Tests:** timeline projection test (audit + note + task interleave, correct sort, correct month buckets) in `test_crm_api.py`.

### Item 3 — Task row UX  [Session 2, frontend, mostly DESIGN]
- **New component:** `frontend/src/components/TaskList.tsx`. Confirmed mechanics from Twenty's `activities/tasks/components/TaskRow.tsx` + `hooks/useCompleteTask.ts` (replicate as patterns, do not paste):
  - Rounded checkbox toggles status; **`line-through` on title when done**.
  - **Due date shows in `text-danger` ONLY when past AND still open** (`isPast = hasDatePassed(due) && status === 'open'`), with a calendar icon. A past date on a DONE task is NOT red.
  - Empty-title placeholder ("Task title") so a blank row is still clickable.
  - Group by status (open first, done below), each group with an "add task" button on the open group. Warm empty state ("All tasks addressed") echoing Twenty's.
- Toggle completion = flip `status` between `'open'`/`'done'` (Twenty's `useCompleteTask` does exactly this, nothing more) via a `put` through the item store's route. Optimistic (see item 9 pattern).
- Hand-rolled Tailwind, reuse `ui.tsx` primitives; no rich-text editor (Twenty uses BlockNote for the body, DREAM uses a plain textarea per the refuse-to-copy list).

### Item 4 — Right-rail relations on DealDetail  [Session 2, frontend]
- **Edit:** [DealDetail.tsx](../../frontend/src/pages/DealDetail.tsx). Build a RIGHT RAIL on the Overview tab (Decision 2): two-column layout on wide screens (metrics/dashboard left, rail right), stacking below on narrow screens. Rail shows role slots (Broker / Seller / Lender / Bond Counsel / Issuer / Nonprofit Sponsor) with attach-or-create-contact, plus note/task composers (plain textarea, no rich-text editor).
- **Constraint:** DealDetail tab ids stay EXACTLY `'overview' | 'memo' | 'activity' | 'export'` (no fifth tab, per Decision 2). Do not rename ids. Prop shapes of existing components stay byte-for-byte.
- **Pattern backing:** Twenty's record page is a left main panel + a right side panel (`object-record/record-show/`, `useOpenRecordInSidePanel`); clicking a related record (e.g. a task) opens it in that side panel. DREAM's right-rail-on-Overview is the right-sized version. Clicking a contact/task/note in the rail can navigate to its own view later; for Phase 5, an inline expand or a simple modal is enough (do not build Twenty's full side-panel navigation stack).

### Item 5 — Pipeline views (table + kanban + presets + sort)  [Session 3, frontend]
- **Edit:** [Pipeline.tsx](../../frontend/src/pages/Pipeline.tsx). Keep the single `listDeals({include_archived})` fetch. Add a `viewMode: 'cards'|'table'|'kanban'` toggle, a generalized filter object, 3 hardcoded presets, and column sort. Persist `{layout, filter, sort}` in `localStorage` (2 users, no backend view store).
- **Table:** hand-rolled `<table>` from `DealListItem` fields, no table library, `useMemo` sort comparator.
- **Kanban:** group by `status`, reuse the existing `DealCard` (do not change its props).

### Item 6 — Kanban drag rule: archive column only  [Session 3, frontend]
- Status columns are NOT drop targets (status is engine-derived; dragging must not fake it). Only drag into/out of the Archived column, mapped to the existing `archiveDeal` / `unarchiveDeal` endpoints. Do NOT add a generic status PATCH.
- If a true draggable pipeline board is wanted later, that is a SEPARATE user-owned `pipeline_stage` field (out of Phase 5 scope; note it).

### Item 7 — Toast primitive + undo-delete  [Session 2, frontend; needs Decision 1]
- **New:** `frontend/src/contexts/ToastContext.tsx` (queue, auto-dismiss countdown, hover-pause, action-button slot, dedupe) + a `ToastViewport` reusing `ok`/`danger`/`teal-panel` tone classes. Wrap `App.tsx` once.
- **Undo-delete** (Decision 1 = YES, build it): remove the `window.confirm`; optimistic removal + a 6s "Deleted. Undo" toast; the real DELETE fires when the countdown completes, so Undo needs zero backend.

### Item 8 — Empty states + skeleton cards  [Session 2/3, frontend, DESIGN]
- Distinguish "no deals yet" (CTA New Underwrite) from "nothing matches this filter" (CTA clear filter). Skeleton cards shaped like `DealCard` instead of the spinner. Built in-session, styled to Twenty's empty-state feel (minus the parallax illustration pipeline, which is overkill for 2 users).

### Item 9 — Cmd-K jump menu  [Session 3, frontend, ENG]
- **New:** `frontend/src/components/CommandMenu.tsx`. Global `keydown` (Cmd/Ctrl-K) opens a centered modal; fuzzy jump-to-deal (client-side `includes`, no library at this scale) + nav actions. Item shape `{label, icon?, to?, onClick?}` (presence of `to` = navigation). Skip Twenty's side-panel.

### Item 10 — Inline-edit event contract  [Session 3, frontend, ENG, lowest priority]
- **New primitive in [ui.tsx](../../frontend/src/components/ui.tsx):** `InlineEdit` (~25 lines): Enter=save, Escape=cancel, blur=save, skip network on unchanged value. Build only where a concrete field needs it (deal name, note/task title).

---

## Session plan + collision boundaries (Fable orchestrates against these)

**Session 1 — data spine (backend).** Owners: one builder on `crm_store.py` + `__init__.py`; one builder on `routers/crm.py` (CRUD + timeline projection) + `main.py` mount; one builder on tests. No frontend files touched. Extend `deals.py::delete_deal` for the link cascade (single small edit, main session does it to avoid collision). Ship + live-verify the API.

**Session 2 — surface on the deal (frontend).** Owners: one builder on `DealAudit.tsx` (timeline kinds); one on `DealDetail.tsx` (rail/tab + composers); one on `TaskList.tsx` + `ToastContext.tsx` + `App.tsx` wrap. `api.ts` gets new fetch functions (main session owns `api.ts` edits to avoid collisions, per design-brief do-not-break rule). Ship + verify.

**Session 3 — pipeline power + polish (frontend, optional/stretch).** Owners: one builder on `Pipeline.tsx` (views + kanban + drag); one on `CommandMenu.tsx` + `App.tsx` hotkey; one on empty/skeleton states + `InlineEdit` in `ui.tsx`. Ship + verify.

**Hard rule:** two builders never edit the same file in the same session. `api.ts`, `ui.tsx`, and `App.tsx` are shared-surface files — the main session serializes edits to them.

---

## Test bar (per session, all must be green before commit)

- Backend: `.venv/Scripts/python -m pytest underwriting-engine/... backend/tests -q` stays green, plus the new `test_crm_store.py` / `test_crm_api.py`. Match the existing 380-test baseline plus additions.
- Frontend: `cd frontend && npx tsc --noEmit && npm run build` clean (recharts chunk-size warning is the only allowed warning).
- Live-verify every session against production with a minted token (SSH mint per HANDOFF). Every live verify has caught something a test did not at least once; do not skip it.

---

## Decisions (RESOLVED by Evan 2026-07-13 — build to these)

1. **Delete UX = undo-toast, NOT confirm popup.** Item 7 ships in full: optimistic remove + 6s "Deleted. Undo" toast; the real DELETE fires only when the countdown completes (zero backend for undo). This SUPERSEDES the old design brief's confirm-before-delete constraint. Remove the `window.confirm` on delete.
2. **DealDetail = right rail on Overview, NOT a new tab.** Item 4 builds a two-column Overview on wide screens: metrics/dashboard on the left, a contacts + tasks + notes rail on the right. The tab set stays `overview | memo | activity | export` (no fifth tab). On narrow screens the rail stacks below the main content.
3. **Contact roles = 6+.** The role enum is: `broker | seller | lender | bond_counsel | issuer | nonprofit_sponsor | other`. Issuer and nonprofit_sponsor matter for EFB 501(c)(3) bond deals (a primary DREAM path). Ship the full enum in Session 1.

---

## Cross-phase impact (how Phase 5 affects the rest of DREAM's roadmap)

- **Claude Design restyle folded IN, not separate (Evan, 2026-07-13).** Twenty's UX is rich enough that it supersedes the planned standalone Claude Design restyle. So the [DESIGN] items (3, 8, timeline visual language) are built INSIDE the Phase 5 sessions by the same builders, styled to match Twenty's patterns directly, not handed to a separate restyle chat. The old design brief's hard constraints (do not touch api.ts / format.ts / hooks / auth / route paths / prop shapes) still bind as engineering guardrails, but there is no separate restyle handoff step. This removes a whole coordination seam and lets each component ship styled-and-wired in one pass.
- **Wave F Postgres.** The `crm_store.py` MUST obey "no sqlite3 outside the store package" so the Postgres swap stays a drop-in second implementation. This is a locked contract, not a nice-to-have.
- **Stale `main` branch.** `main` is a pre-consolidation codebase missing `backend/`, `docs/`, and the engine; PR #3 (wave-a-foundation to main) was never merged. Phase 5 builds on `wave-a-foundation`. Before or after Phase 5, resolve `main` (merge wave-a-foundation into it, or make wave-a-foundation the default branch) so the repo's "main" reflects the live app. Not a Phase 5 blocker, but do not let Phase 5 compound the drift.
- **Ownership model.** DREAM's ownership seam (`DREAM_STRICT_OWNERSHIP`, permissive v1 = everyone-sees-all) should extend to CRM records the same way: derive owner from auth email, permissive by default, strict-mode ready. Do not invent a new ownership model for CRM.
- **Deal spec independence.** CRM records are their own canonical docs; they never write into the deal spec. This keeps the underwrite pipeline and the CRM layer decoupled, so a CRM bug can never corrupt a deal's numbers.

---

## Paste-prompt for the Fable session

> Read `docs/research/PHASE5_CRM_LAYER_KICKOFF.md` fully (the implementation plan) and `docs/research/TWENTY-CRM-BORROW-LIST-2026-07-13.md` (the ranked items) before doing anything. Confirm you are on branch `wave-a-foundation`. Build the DREAM CRM layer (Phase 5) per the session plan and collision boundaries, honoring every LOCKED CONTRACT and the working pattern (builders draft, main reviews diff, full test suite + tsc/build green, commit, deploy with VPS backups, live-verify against production). Everything is inspiration-only per the license audit: never paste Twenty source. Get Evan's answers to the three Decisions before starting Session 1. Keep this plan updated as you ship.
