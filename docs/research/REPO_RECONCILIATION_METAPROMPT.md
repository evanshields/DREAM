# Metaprompt: DREAM repo reconciliation (PR #4 + stale `main`)

Paste everything below the line into a fresh Claude Code session (working dir `c:\Users\evana\DREAM`). This is a focused git-hygiene task, NOT a build task. Suggested chat name: DREAM Repo Reconciliation.

---

You are cleaning up the DREAM git repo. Two jobs: (1) land the docs-only research PR, (2) reconcile the stale `main` branch with the live app on `wave-a-foundation`. **Confirm the branch/worktree first** (`git worktree list`, `git status -sb`). Read-only investigation before any merge; nothing destructive without showing Evan the plan first. Plain English when you explain choices to Evan (he is a smart investor, not an engineer). No em dashes in anything you write.

## Background (verified 2026-07-13)

- The LIVE DREAM app lives on branch **`wave-a-foundation`** (repo `github.com/evanshields/DREAM`, local `c:\Users\evana\DREAM`). It has `backend/`, `frontend/`, `underwriting-engine/`, `docs/`: the whole product (Phases 1-4 shipped).
- **`main` is stale and pre-consolidation.** It does NOT have `backend/`, `docs/`, or the current app. It is an older codebase (an early `src/` + `gemini_ui/` scaffold).
- The two branches have **diverged, both sides carry unique commits** (this is the crux, it is NOT a simple fast-forward):
  - `main` has **3 commits `wave-a-foundation` lacks**, all `add-underwriting-engine` work: the PR #2 merge (`5af84fe`), plus two "Sync underwriting-engine to dream-underwrite Wave 2 / Wave 3" commits (`9b21bf7`, `8a439ec`).
  - `wave-a-foundation` has **~20 commits `main` lacks**, including the entire live app (Phase 1-4, the docs consolidation `2002bb4`, etc.).
- PR #3 (wave-a to main) was described in old handoffs as "awaiting Evan's one-click merge" but was **never merged**.
- **PR #4 is OPEN and MERGEABLE**: `research/twenty-crm-borrow-list` into `wave-a-foundation`, docs only (the Twenty CRM borrow list + Phase 5 plan). Title: "Research: Twenty CRM borrow list + Phase 5 CRM-layer plan (docs only)".

## Job 1: land PR #4 (easy, do first)

- PR #4 is docs-only into `wave-a-foundation`. Verify it is still docs-only (`gh pr diff 4 --name-only` should show only `docs/` files, no `backend/frontend/underwriting-engine/` paths).
- If clean, merge it (squash is fine). This puts the research docs on `wave-a-foundation` so the Fable Phase 5 build session reads them from the app branch.

## Job 2: reconcile `main` (the careful part)

The goal Evan wants: the repo's default branch should reflect the LIVE app, so "main" stops being a misleading stale codebase. There are two viable paths. **Investigate first, then recommend ONE to Evan with the tradeoff in plain English, and get his go-ahead before executing.**

**Investigation to do before recommending:**
1. Are the 3 `main`-only underwriting-engine commits (`5af84fe`, `9b21bf7`, `8a439ec`) already SUPERSEDED by the engine state on `wave-a-foundation`? Diff `underwriting-engine/` between the branches (`git diff origin/main origin/wave-a-foundation -- underwriting-engine/`). If wave-a's engine already contains (or moved past) those Wave 2/3 syncs, the main-only commits are dead weight and no real content is lost by replacing main.
2. Confirm nothing else unique and valuable lives only on `main` (`git log origin/wave-a-foundation..origin/main --stat`).

**Path A (recommended if investigation shows main-only commits are superseded): make `wave-a-foundation` the new `main`.**
- Options: either merge `wave-a-foundation` into `main` (a real merge, expect possible `underwriting-engine/` conflicts, resolve in favor of the live wave-a state after confirming step 1), OR change the GitHub default branch to `wave-a-foundation` and retire the old `main`. Merging keeps `main` as the name; re-pointing is cleaner but changes the default-branch name. Recommend the merge if Evan wants to keep "main" as the canonical name.
- If merging and conflicts appear only in already-superseded engine files, resolving to wave-a's version is correct (confirm with step 1 first).

**Path B (if step 1 shows the 3 main-only commits carry engine work wave-a genuinely lacks): cherry-pick, then merge.**
- Cherry-pick or re-apply the missing engine work onto `wave-a-foundation` first, run the full test suite green, THEN merge wave-a into main. Do NOT lose engine history.

**Guardrails:**
- Run the full test suite green before AND after any merge: `.venv/Scripts/python -m pytest underwriting-engine/engine/tests underwriting-engine/fastpath/tests backend/tests -q` and `cd frontend && npx tsc --noEmit && npm run build`.
- The app is LIVE at dream.shieldstone.co and deploys from the local `wave-a-foundation` clone. Do NOT change what deploys. This is git-history hygiene, not a deploy.
- Show Evan the branch-graph plan (which commits move where, any conflicts, which version wins) BEFORE executing. Get his one-word go-ahead.
- Honor the global rule: never mix workstreams in a commit; scope every commit to this reconciliation only.

## Definition of done

- PR #4 merged (docs on `wave-a-foundation`).
- `main` reflects the live app (either merged-up or re-pointed), with no engine history lost, tests green, and a one-paragraph plain-English summary to Evan of what moved and why.
