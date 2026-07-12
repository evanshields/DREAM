# DREAM — Claude Context

> **Estate:** Shieldstone Hermes (`dream.*` namespace). Prepend `../HERMES_BOOTSTRAP.md` for identity +
> guardrails; see `../business-units.md` → DREAM for the org-map entry.

## What DREAM is

**DREAM** = the agentic framework for **all D**evelopment, **R**eal-**E**state, and **A**sset-**M**anagement
analytical work at Shieldstone (the acronym). The multifamily underwriter is the **first application**,
not the whole scope. Evan locked this definition 2026-06-05. Product home: GitHub `evanshields/DREAM`.

**Product arc (Evan-locked 2026-06-05):** chat-bot intake (5–20 min autonomous initial underwrite) →
populate the app (tweak assumptions live, run sensitivities — Python recalc, never an LLM call for
recalc) → push to Excel Mini Model → Hermes autonomy layer (Drive/email/Slack deals land as the same
app deal instance).

## ⚠️ Where the code actually runs

**The local `dream/` folder is a workspace, NOT the running app.** The *real, running* DREAM app lives
on the **UK VPS at `/opt/dream-app`** (PM2 process `dream-api`, FastAPI on :8001 + Vite frontend). It
has intake / agent-chat / underwrite / validate endpoints + a Python calc engine already wired. SSH:
alias `shieldstone-uk`, port 2222 (see `../memory/reference_uk-vps-ssh.md`).

**Core principle: broaden, don't rebuild.** DREAM v3.0 broadens the already-built "EFB Underwriter" app
into a general acquisition underwriter. Work the *delta* between EFB-only and the full vision — do not
start fresh. Source: `DREAM_PRD.md` (approved 2026-06-05) + `DREAM_PRD_RECON.md` ("what exists where").

## Cost discipline (the load-bearing rule)

Write **rote Python for every mechanical step** so DREAM agents do as little expensive LLM work as
possible — the engine owns the mechanical ~90%; agents are reserved for the judgment forks (routing,
tier strategy, reprice/verdict — per the Envy 3-way forensic). Crib from **Padawan**
(`H:\My Drive\_ShieldstoneX`), which already solved much of the low-cost-Python approach.

## The underwriting brain

The validated methodology + calc engines live in the **`dream-underwrite` skill**, not in this folder:
- Skill / playbook: `../.skills/dream-underwrite/SKILL.md` (`/dream-underwrite`).
- Calc engines: `../.skills/dream-underwrite/engine/{acq_engine.py, lihtc_engine.py}` (validated vs
  Rayzor EFB + Esplanade ACQ ground truth; 19-test suite).
- Fast-path spec/agents/populator: `../.skills/dream-underwrite/fastpath/`.
- A verbatim sync of the skill lives in the DREAM app repo at `underwriting-engine/` (re-sync from the
  canonical skill when it changes). Handoff: `../.skills/dream-underwrite/HANDOFF-TO-DREAM-APP-CHAT.md`.

## Local folder contents

- `DREAM_PRD.md` / `DREAM_PRD_RECON.md` — the v3.0 PRD + recon (read these first for product work).
- `backend/`, `src/`, `public/`, `agent_architecture/`, `tests/` — local Vite/React + backend scaffold
  (mirrors/seeds the VPS app; the authoritative deployment is the VPS).

## Hermes autonomy (design-only, blocked)

The autonomy layer (`dream.underwriter` invoked by Avery via Shieldstone Hermes) is **designed but
build-blocked** until Hermes is installed on the US VPS. See `../shieldstone_acquisitions/HERMES_DREAM_AUTONOMY_DESIGN.md`,
`../shieldstone_acquisitions/HERMES_DREAM_BUILD_SPEC.md`, and `../memory/project_dream-hermes-autonomy.md`.
**Outward verdicts stay HITL forever.**
