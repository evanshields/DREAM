# DREAM repo scrub plan (2026-07-12) — DO NOT EXECUTE while another session is mid-Phase-4

Written by the consolidation session (read-only audit). Execute AFTER the active Phase-4 work
lands, in whichever chat is free. Uncommitted on purpose — commit rides with the scrub itself.

## Why
The repo carries THREE frontends (only one is real) plus a dead root build system and Windows
junk. Everything below is preserved in git history forever — deletion is fully recoverable, so
no archive/ folder is needed. Tag first for one-command recovery.

## Step 0 — safety tag
```
git tag pre-scrub-2026-07-12 && git push origin pre-scrub-2026-07-12
```

## DELETE (git rm -r) — dead code, ~110 tracked files

| Path | What it is | Why safe |
|---|---|---|
| `src/` | "dream-vision-temp" frontend #3 — pure UI shell, NO API calls, NO auth, never deployed | superseded by `frontend/`; H: drive copy exists too |
| `gemini_ui/` | frontend #2 (June dashboard build) | Evan rejected the look; the useful parts (api client pattern, AssumptionDashboard logic) were LIFTED into `frontend/` in July |
| Root build config for the dead frontends: `index.html`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `tailwind.config.js`, `postcss.config.js`, `eslint.config.js`, `components.json`, `public/` | the dream-vision-temp toolchain; the root `postcss.config.js` is the file that BROKE gemini_ui builds in June | `frontend/` has its own complete toolchain |
| `DreamVision_PRD_v3.md` (root) | pre-v3.0 PRD | superseded by `docs/DREAM_PRD.md` |
| ALL tracked `desktop.ini` (10 files: root, `.claude/`, `public/`, 7 under `src/`) | Windows Explorer junk | never belonged in git |

Also ADD to `.gitignore`: `desktop.ini`, `dream_deals.db`, `*.db` (root test DB is untracked
today — keep it that way).

## KEEP — do not touch

| Path | Why |
|---|---|
| `backend/`, `frontend/`, `docs/`, `README.md`, `.gitignore`, `.claude/` (minus desktop.ini) | the live app |
| `underwriting-engine/` | vendored validated engine — LOCKED, never modify |
| `backend/calculations/`, `backend/models.py`, `backend/intake/`, `backend/agent/` | LEGACY but still WIRED: `/api/intake` (PDF extraction uses IntakeService + models), `/api/underwrite` + `/api/validate` (old engine), memo generator. Retiring the old-engine routes is Phase-4c CODE work, not a file scrub. Do NOT delete in this pass. |

## Stale remote branches — delete on GitHub after PR #3 merges
`add-underwriting-engine` (merged into wave-a-foundation long ago) · `cursor/build-sales-funnel-...`
· `cursor/composer-1-...` (two Cursor experiments) · `monochrome-pro`.
```
git push origin --delete add-underwriting-engine "cursor/build-sales-funnel-page-claude-4.5-opus-high-thinking-e883" "cursor/composer-1-compatibility-issue-3f59" monochrome-pro
```
(Verify none has unmerged work first: `git log origin/<branch> --not origin/wave-a-foundation --oneline` — expect empty or junk.)

## Execution checklist
1. Confirm no other session mid-work in `c:\Users\evana\DREAM` (git status clean-ish, no builder running).
2. Tag (Step 0).
3. `git rm -r` the DELETE table + .gitignore additions — ONE commit ("repo scrub: remove dead frontends + root toolchain + junk; see docs/REPO_SCRUB_PLAN_2026-07-12.md").
4. Full suite (356+ expected — nothing in DELETE is imported by backend/frontend; verify: `grep -r "gemini_ui\|dream-vision" backend/ frontend/src/` → expect no code imports).
5. `cd frontend && npx tsc --noEmit && npm run build` — must stay clean.
6. Push. Live app unaffected (server has no git; nothing deleted is deployed).
7. Branch cleanup AFTER PR #3 merge (verify-then-delete per above).
