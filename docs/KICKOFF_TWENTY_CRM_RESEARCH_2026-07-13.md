# KICKOFF: "DREAM CRM Exemplar Research (Twenty)"

Paste everything below the line into a fresh Claude Code session (working dir `c:\Users\evana\DREAM`).
Suggested chat name: **DREAM CRM Exemplar Research**.

---

You're running a **research session** to figure out what DREAM should borrow from **Twenty CRM**
(github.com/twentyhq/twenty), a well-regarded open-source CRM. Written deliverables only. You are
NOT modifying the DREAM app in this session. Run the deep-dive with **parallel Opus 4.8 subagents**
per the fan-out plan below.

## Context (what DREAM is)

DREAM is Shieldstone's multifamily underwriting app, LIVE at https://dream.shieldstone.co.
Repo `c:\Users\evana\DREAM`, branch `wave-a-foundation`. Users: Evan + Charles (investors, not
engineers). Stack: FastAPI + SQLite stores + a vendored deterministic Decimal engine (backend);
React 19 / TypeScript / Vite / Tailwind with hand-rolled primitives in `components/ui.tsx`, NO
component library (frontend). Phase 4 just shipped: async submit with polling, archive/delete on
deal cards, owner stamping, dashboard seeding.

Current surfaces: Pipeline (card grid, status filter pills, kebab menu), Underwrite intake (ACQ/EFB,
PDF drag-drop), DealDetail (Overview / Memo / Activity / Export tabs, audit timeline, live
assumption dashboard), Bond Screen calculators.

**What DREAM lacks that a CRM has (this is the research target):**
- No people or company records: brokers, sellers, lenders, bond counsel, issuers all live in prose.
- No tasks or follow-ups tied to deals. No notes. No reminders.
- Pipeline is a card grid only: no table view, no kanban-by-stage, no saved filters or views.
- Activity tab shows only the underwrite job audit, not a full deal timeline (calls, emails, docs).
- No custom fields on deals beyond the canonical spec.

Background reading (do this first): `docs/HANDOFF_2026-07-12.md`, `docs/DREAM_V3_BUILDOUT_PLAN_2026-07-11.md`,
`docs/CLAUDE_DESIGN_BRIEF.md` (an upcoming Claude Design restyle will consume part of your output).

## THE JOB: Twenty CRM repo exploration (Opus subagent fan-out)

Twenty is public code, no login. Clone it READ-ONLY to a scratch directory OUTSIDE the DREAM repo
(e.g. `c:\tmp\twenty-research`). Reading code requires no audit; do NOT `npm install` or run it
without doing Evan's third-party audit first (usually unnecessary, reading suffices).

Launch **5 parallel Opus 4.8 subagents**, each owning one area, each returning a structured report
with file paths and concrete examples:

1. **Agent A, data model:** How Twenty models objects, records, fields, and relations, including
   its custom-field/metadata system. Which schema ideas port to DREAM's SQLite store pattern
   (opaque canonical doc + derived index) for new `contacts` / `companies` / `tasks` / `notes`
   objects linked to deals. Be concrete about tables and shapes.
2. **Agent B, views layer:** Kanban and table views, filtering, sorting, saved views, quick search.
   What the interaction model is, what state drives it, and what a minimal DREAM version of
   "Pipeline as kanban-by-status + table with saved filters" would take.
3. **Agent C, record page + timeline:** Twenty's record detail layout, activity timeline, notes,
   tasks, and email/calendar surfaces. Map to DealDetail: what a unified deal timeline (job audit +
   notes + tasks + doc events) and a right-rail relations panel would look like.
4. **Agent D, frontend patterns:** Component architecture and UX polish patterns a hand-rolled
   Tailwind app can borrow AS PATTERNS (not imports): empty states, inline edit, command menu,
   keyboard nav, optimistic updates, toast patterns. Tag which items belong in the Claude Design
   restyle vs. real frontend engineering.
5. **Agent E, license + honesty check:** Read the actual LICENSE files per package (Twenty core is
   AGPL-3.0; some packages may differ). Spell out in plain English what AGPL means for copying code
   into Evan's private commercial repo vs. borrowing ideas. Verdict per Evan's audit protocol; save
   the audit to `c:\Users\evana\shieldstone_os\shieldstone_operations\third-party-audits\2026-07-13-twenty-crm.md`.
   Also state honestly where Twenty's stack (React SPA + NestJS + GraphQL + its own twenty-ui kit)
   diverges from DREAM's FastAPI/Vite world, so nobody pretends code is liftable when it isn't.

**Then synthesize (main session):** merge the five reports into ONE ranked borrow list.
Each item: what it is (with Twenty file refs), why it helps DREAM, rough effort (S/M/L), and a
classification: **liftable code** vs **inspiration only** vs **license-blocked**. Given AGPL,
expect most items to be inspiration-only; say so plainly. Close with a suggested build order
(what a "DREAM CRM layer" Phase 5 could look like in 2-3 sessions).

## Rules

- Research + written deliverables only. No DREAM app-code changes. Docs-only commits allowed.
- Confirm branch first (`git status -sb` in `c:\Users\evana\DREAM`, expect `wave-a-foundation`).
- Plain English + Smart Brevity when reporting to Evan (bold lead-ins, bullets). No em dashes in
  any deliverable. Clickable links to every file you create.
- License care: nothing gets recommended as "copy this code" unless Agent E's audit clears it.
- Keep Twenty's clone OUT of the DREAM repo and out of git.

## Definition of done

Two documents:
1. `c:\Users\evana\DREAM\docs\research\TWENTY-CRM-BORROW-LIST-2026-07-13.md`, the ranked borrow
   list + Phase 5 build-order sketch, committed to `wave-a-foundation` (docs only).
2. The Twenty license/security audit in `shieldstone_operations/third-party-audits/`.

Both concrete enough that a future build session (and the Claude Design restyle chat) can act on
them without re-reading Twenty.
