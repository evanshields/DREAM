# Twenty CRM to DREAM: Borrow List (2026-07-13)

Synthesis of a 5-agent study of github.com/twentyhq/twenty (clone studied at `c:\tmp\twenty-research`,
v2.20.0 era). Agents covered: data model, views layer, record page + timeline, frontend UX patterns,
and license/audit. Full license audit (absolute path, opens in VS Code):
`c:\Users\evana\shieldstone_os\shieldstone_operations\third-party-audits\2026-07-13-twenty-crm.md`.

## The license rule (governs everything below)

Twenty is AGPL-3.0 with an embedded commercial license; 305 files are marked `/* @license Enterprise */`
(commercial-only, folder names unreliable, per-file header is authoritative).

- **Copy code verbatim: RED.** AGPL would force DREAM's whole source open to its users. Never paste.
- **Copy field lists / schema shapes: YELLOW.** Field names are facts; use as a checklist, retype in
  DREAM's own naming. Not legal advice.
- **Re-implement ideas from study: GREEN.** Clean-room re-implementation is the mode for every item
  below. Every single borrowable is therefore classified inspiration-only.

## What DREAM is buying here, in one paragraph

Twenty solved four problems DREAM has: (1) what fields a contact/company/task/note record needs,
(2) how to attach notes and tasks to any record, (3) how to render one dataset as cards, table, or
kanban with filters and sorts, and (4) how to merge audit history and human activity into one
readable timeline. It solved them inside ~1,700 files of metadata-engine machinery that exists so
strangers can define custom databases at runtime. DREAM has 2 users and one fixed schema, so we take
the four answers and none of the machinery.

## Ranked borrow list

Effort: S = hours, M = a session, L = multiple sessions. All items inspiration-only per the license rule.

| # | Borrowable | What it gives DREAM | Effort |
|---|---|---|---|
| 1 | **CRM store trio** (contacts, tasks+notes, links) | New `backend/store/crm_store.py` following the existing opaque-doc + derived-index idiom of `deal_store.py`. One `contacts` table (person + company discriminated by `kind`, with DREAM-native `role`: broker / seller / lender / bond_counsel / issuer), one `crm_items` table (task + note by `kind`), one `crm_links` index table `(source_kind, source_id, target_kind, target_id)` adapted from Twenty's TaskTarget/NoteTarget join pattern. Field lists cribbed (retyped) from Twenty's Person/Company/Task/Note standard objects. Wire delete cascade like `job_store.delete_for_deal`. | M |
| 2 | **Unified deal timeline** | `GET /api/deals/{id}/timeline`: a READ-TIME projection interleaving the existing append-only job audit rows with new notes and tasks into one sorted `events[]` feed (`{id, source, kind, ts, actor, title, ...}`). The locked audit system is never touched; the timeline is a view, not a second source of truth. Twenty does this write-time with a queue; read-time is simpler and right at DREAM volume. Frontend: month-grouped feed with per-type rows (icon + connector line + relative time), replacing the Activity tab. | M |
| 3 | **Task row UX** | Checkbox toggles done, strikethrough title, overdue due-date turns red. The "next step" affordance DREAM completely lacks, and the cheapest high-value UI in the whole study. | S |
| 4 | **Right-rail relations on DealDetail** | Fixed 4-row rail (Broker / Seller / Lender / Counsel) with an inline attach-or-create-contact popover, plus note/task composers (plain markdown textarea, no rich-text editor). Simplified from Twenty's generic relations panel; DREAM does not need arbitrary relations. | M |
| 5 | **Pipeline views: table + kanban + presets + sort** | One dataset, three renderings: keep today's single `listDeals` fetch and `useMemo` filtering, add a cards/table/kanban layout toggle, kanban grouped by status, 3 hardcoded preset filters ("My open deals", "EFB pipeline", "Needs attention"), and column sort. Persist `{layout, filter, sort}` in localStorage (2 users; no backend). Filter objects use Twenty's `{field, op, value}` shape and can round-trip through the URL for shareable views. | M |
| 6 | **Kanban drag rule: archive column only** | A deal becomes "computed" by running the engine, not by dragging a card, so status columns are NOT drop targets. Only drags into/out of the Archived column act, mapped to the existing archive/unarchive endpoints. Do NOT add a generic status PATCH; it would let the UI desync status from the engine. | S |
| 7 | **Toast primitive + undo-delete** | Queued toast (auto-dismiss with countdown, hover-to-pause, action-button slot, dedupe). Then replace `window.confirm` hard delete with optimistic removal + 6s "Deleted. Undo" toast; the real DELETE fires only when the countdown completes, so Undo needs zero backend. **Needs an Evan product call**: the Claude Design brief currently pins confirm-before-delete as a constraint. | M |
| 8 | **Empty states + skeleton cards** | "No deals yet" (CTA: New Underwrite) rendered differently from "nothing matches this filter" (CTA: clear filter); skeleton cards shaped like DealCards instead of the loading spinner. Mostly a design-pass item. | S |
| 9 | **Cmd-K jump menu** | Global hotkey opens a search/action palette: fuzzy jump-to-deal + go-to-page + New Underwrite. Twenty's elegant bit: one item shape `{label, icon?, to?, onClick?}` where presence of `to` means navigation. Skip their side-panel; a simple modal suffices. | M |
| 10 | **Inline-edit event contract** | Enter = save, Escape = cancel, blur = save, and skip the network call when the value is unchanged (equality guard). Reusable keyboard model for any future click-to-edit cell; lower priority since DREAM's dashboards are already always-editable. | M |

## What we explicitly refuse to copy

- The metadata engine, runtime schema generation, and workspace multi-tenancy (~1,700 files). It
  exists so end-users can define objects at runtime. DREAM adds a field by editing a dataclass.
- The Recoil/GraphQL view engine and persisted view tables. DREAM's views are client state over one
  fetch.
- The PageLayout widget engine (user-configurable record pages). DealDetail stays hardcoded JSX.
- Queue-driven write-time timeline projection (BullMQ). Read-time merge is simpler and cannot drift
  from the locked audit log.
- BlockNote rich-text editor, SSE live refresh, drag-drop race machinery, sidebar + favorites nav,
  bulk select. All overkill at 2 users.

## Suggested Phase 5 build order (2-3 sessions)

1. **Session 1, backend:** `crm_store.py` (contacts, items, links, cascade) + FastAPI routes
   (contacts CRUD, notes/tasks CRUD, attach/detach) + `GET /api/deals/{id}/timeline` projection +
   tests in the standalone-mount idiom. Items 1-2.
2. **Session 2, DealDetail:** Timeline tab (month groups, per-type rows, task checkbox UX), right
   rail (4 relation slots + composers), toast primitive, undo-delete IF Evan approves, empty/skeleton
   states. Items 2-4, 7-8.
3. **Session 3, Pipeline:** layout toggle (cards/table/kanban), presets, sort, localStorage
   persistence, archive-column drag, optional Cmd-K. Items 5-6, 9.

Design-pass overlap: items 3, 8, and the timeline's visual language belong in the Claude Design
restyle conversation too; hand this doc to that chat alongside `docs/CLAUDE_DESIGN_BRIEF.md`.

## Decisions Evan owes before build

1. Undo-toast instead of confirm popup for delete? (Item 7; brief currently pins the popup.)
2. Are 4 fixed contact roles enough (broker/seller/lender/counsel), or add issuer/nonprofit sponsor
   for EFB deals? (Item 1 ships either way; the enum is one line.)
3. Green-light Phase 5 as the next DREAM build block, or park this list?
