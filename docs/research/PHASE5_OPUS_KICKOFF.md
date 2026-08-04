# Metaprompt: Build DREAM Phase 5 CRM Layer (Opus High, solo)

Paste everything below the line into a FRESH Claude Code chat. Set the working directory to `c:\Users\evana\DREAM`, set the model to Opus 4.8, and set thinking/effort to High. Suggested chat name: DREAM Phase 5 CRM Build.

(Prerequisite: raise the monthly Claude spend cap at claude.ai/settings/usage first. A hit cap killed agents in the research session.)

---

You are building Phase 5 of DREAM: the CRM layer. This is a BUILD session, not research or planning. The plan already exists and every decision is made; your job is to implement it, session by session, to Evan's working standard.

## Read these first, fully, before writing any code

1. `docs/research/PHASE5_CRM_LAYER_KICKOFF.md` — the implementation plan. This is your blueprint: all 10 items mapped to exact files, API contracts, store shapes, the session plan, the collision boundaries, and the test bar. Build to it.
2. `docs/research/TWENTY-CRM-BORROW-LIST-2026-07-13.md` — the ranked borrowables and the explicit refuse-to-copy list, for context on WHY each item exists.
3. `docs/HANDOFF_2026-07-12.md` — the app's current live state and the LOCKED CONTRACTS.
4. `backend/store/deal_store.py` and `backend/jobs/job_store.py` — the store idiom every new CRM store must clone exactly.

## Confirm before you start

- `git status -sb` shows you are on branch `wave-a-foundation` (the live app). If not, stop and switch. Do NOT build on `main` (it is a stale pre-consolidation codebase).
- Cut a fresh working branch off `wave-a-foundation` for this build (e.g. `phase5-crm-layer`), so the work is isolated and reviewable as a PR.

## The three product decisions are ALREADY RESOLVED (do not re-ask)

1. Delete UX = optimistic remove + 6s "Deleted. Undo" toast (NOT a confirm popup; this supersedes the old design-brief confirm-before-delete).
2. DealDetail = right rail on the Overview tab (two-column on wide screens, stacks on narrow), NOT a fifth tab.
3. Contact roles enum = `broker | seller | lender | bond_counsel | issuer | nonprofit_sponsor | other`.

Also: the Claude Design restyle is FOLDED INTO this build (style components to match Twenty's patterns as you wire them; there is no separate restyle handoff).

## How to work (Evan's proven pattern, follow it every session)

- Build ONE session at a time (the plan defines Session 1 backend, Session 2 deal surfaces, Session 3 pipeline + polish). Do not start the next session until the current one is shipped and verified.
- Since you are solo (not fanning out to parallel builders), you still honor the collision boundaries as a build ORDER: finish and self-review one file-group before moving to the next, and serialize edits to the shared-surface files (`api.ts`, `ui.tsx`, `App.tsx`).
- After building each session: run the FULL test suite and it must be green:
  - Backend: `.venv/Scripts/python -m pytest underwriting-engine/engine/tests underwriting-engine/fastpath/tests backend/tests -q` plus your new `test_crm_store.py` / `test_crm_api.py`.
  - Frontend: `cd frontend && npx tsc --noEmit && npm run build` (only the recharts chunk-size warning is allowed).
- Then: commit, deploy with a timestamped VPS backup, and LIVE-VERIFY against production (dream.shieldstone.co) with a minted token per the HANDOFF. Every live verify has caught something a test did not; do not skip it.
- Show Evan the diff and the verify result at each session boundary and get his go-ahead before the next session. Pause at natural checkpoints; do not run all three sessions unattended.

## Non-negotiable guardrails (violate = failure)

- LOCKED CONTRACTS from the HANDOFF all still bind. Most relevant to CRM: no `sqlite3` import outside `backend/store/`; the CRM stores are their own canonical opaque-doc records and NEVER write into the deal spec; headline_metrics + qa never from an LLM; the vendored engine is untouched.
- Everything is INSPIRATION-ONLY from Twenty (AGPL + 305 commercial Enterprise files). Study Twenty's approach, write DREAM's own code, never paste Twenty source.
- Do not break the design-brief hard constraints: do not change `api.ts` / `format.ts` / `hooks/useJobPolling.ts` / auth files' logic, route paths, or existing component prop shapes. You may add NEW fetch functions to `api.ts` and NEW primitives to `ui.tsx`.
- Plain English when you explain choices to Evan (he is a smart investor, not an engineer). No em dashes in any user-facing writing.

## Definition of done (for the whole build)

- The CRM stores (contacts/companies/tasks/notes via `crm_store.py`), their routers, the unified deal timeline, the right-rail relations panel, task/note UX, toast + undo-delete, and (stretch) the pipeline table/kanban views are all live-verified on production.
- Full test suite green, tsc/build clean.
- The build log in `docs/DREAM_V3_BUILDOUT_PLAN_2026-07-11.md` is updated with a "Phase 5" section (same format as Phases 1-4).
- A PR is opened for Evan.

Start by reading the four docs above, confirming the branch, then propose your Session 1 plan back to Evan in plain English before you build.
