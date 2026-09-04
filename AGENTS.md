# DREAM — Agent Boot File

This file boots ANY coding agent (Codex, Claude Code, future sessions) identically. Read in this order before writing code:

1. **`docs/DREAM_PRD_V4.md`** — THE master document: vision (three-legged stool), phases 0–5, decisions record, topology, risk register. Do not re-derive settled state; do not re-litigate dated decisions.
2. **`docs/AGENTIC_LESSONS_2026-08-31.md`** — 182 hard-won constraints from prior harness experiments. Builder-only: this file must NEVER be exposed to DREAM-the-agent's runtime corpus.
3. **`docs/HANDOFF_2026-07-12.md`** — current app state, deploy runbook, live-verify pattern (minted token).
4. When your phase touches them: `backend/WAVE_F_FULL_AUTH_DESIGN.md` (Phase 1), `backend/store/WAVE_F_POSTGRES_DESIGN.md` (Phase 2), `backend/jobs/HERMES_INTAKE_SEAM.md` (Phase 3).

## What this repo is

The deterministic DREAM underwriting web app — FastAPI (Python 3.13) + React 19/Vite/Tailwind — is LIVE at dream.shieldstone.co (US VPS, PM2 `dream-api` :8001 behind Caddy). 422+ tests. The Twenty-derived DREAM CRM shell lives separately at `app.dreamcre.co` and is the target team front door; the agentic brain (Hermes `dream` profile, UK VPS) connects through the drivers/APIs defined in the PRD.

## Non-negotiables (full list in the PRD §2–3)

- Headline metrics + QA gates NEVER from an LLM; deterministic engines only, reached through `backend/engine_boundary.py` (the sole Decimal seam). Vendored `underwriting-engine/` is untouchable.
- Fail closed on RED gates; HITL hard stop at AWAITING_CP1; fabricated numbers are worse than blanks.
- No sqlite3/psycopg outside `backend/store/`. CRM never writes deal spec.
- Oracles must stay byte-identical: Esplanade ACQ IRR 0.2251, Rayzor EFB $63,868,907.
- Backend `.py` files are CRLF (repo `core.autocrlf=true`).
- Secrets NEVER in repo, logs, or chat — LastPass is the vault; VPS secrets use the root-owned 0600 pattern.
- Twenty CRM is AGPL: API/webhook integration and UI inspiration only; NEVER copy its code here.
- No Anthropic/OpenAI subscription-auth for unattended server automation; metered API keys only.

## Working pattern (every change)

Full pytest suite green → `tsc --noEmit` + `npm run build` green → commit with scoped staging → deploy per `docs/backend/DEPLOY_US_VPS.md` with timestamped VPS backup → live-verify on production with a minted token → then the next task. Never deploy unverified; never hand-edit the server.

## Parallel-agent preference

When work can be divided into independent, well-bounded tasks, use Sol, Terra, Luna, and—when demonstrably sufficient—GPT-5.5 sub-agents in parallel to save time and primary-agent context. Match the model to the work: Sol for higher-risk architecture and final review, Terra for implementation, Luna for focused audits and fast verification, and GPT-5.5 for bounded work where it offers a practical speed or cost advantage. The primary agent remains responsible for reconciling results, enforcing this file's guardrails, and completing end-to-end validation. Do not split tightly coupled edits merely to create parallel activity.

## Repo boundaries

- App code + docs: THIS repo (`evanshields/DREAM`).
- Agent payload (engines mirror, gates, six-phase design, courier rules): `evanshields/dream-underwrite` (local clone `C:/tmp/du-v3`).
- NEVER commit DREAM work into `shieldstone_os` (that's the Built Different monorepo; its checked-out branch is usually an unrelated workstream).
- Confirm `git status -sb` matches your task before every commit.
