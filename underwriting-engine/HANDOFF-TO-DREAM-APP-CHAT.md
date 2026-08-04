# Handoff: the `dream-underwrite` skill → the DREAM app build

**For:** the chat building the DREAM app (`github.com/evanshields/DREAM`).
**From:** the chat that just finished the `dream-underwrite` skill (Waves 1–3 of the Envy forensic backlog).
**Date:** 2026-06-05.
**Purpose:** brief you on the skill so you can decide how the app uses it as the **brain for its agents**. This is context + a recommended direction, not a spec you must follow — the app architecture is yours.

---

## TL;DR

`dream-underwrite` is a **complete multifamily underwriting playbook** — methodology + a validated Python calc engine + a deterministic populate/reconcile pipeline + hard gates. It was built to serve the **whole spectrum**: a human in Claude for Excel, a human-with-agent, and eventually a **fully autonomous agent**. The engine is already vendored into your repo at `underwriting-engine/` (merged to `main` via PR #2 on 2026-06-05). The recommended way for the app to use it is **skill-as-agent**: the app is the front door (intake, UI, orchestration); a Claude agent that has loaded this skill does the underwrite and returns artifacts.

---

## What the skill is (and where it lives)

- **Canonical source:** `evanshields/Shieldstone` repo, branch `dream-fastpath`, at `.skills/dream-underwrite/`. It is a **Claude Code skill** (must live under `.skills/` to be invokable as `/dream-underwrite`). Decided 2026-06-05 to keep it there, NOT move it into the app repo.
- **Synced copy in YOUR repo:** `underwriting-engine/` on `main` — a verbatim copy (minus a monorepo-only build script). This is what the app should consume. Re-sync from canonical when the skill changes (the prior chat did this per-wave).
- **It is Shieldstone estate.** LIHTC/EFB/multifamily UW is Shieldstone-only (per `feedback_usdv-vs-shieldstone-scope.md`); it is deliberately NOT in the USDV Skills repo (confirmed absent there 2026-06-05). Keep the app's use of it on the Shieldstone side of the house.

## Architecture (the three layers the app can call)

```
underwriting-engine/
├── SKILL.md                      # THE PLAYBOOK — 12-phase methodology + fast-path waves + Universal Rules
├── engine/
│   ├── acq_engine.py             # ACQ (conventional value-add) calc engine — validated vs Esplanade
│   └── lihtc_engine.py           # EFB / LIHTC bond engine — validated vs Rayzor
├── fastpath/
│   ├── underwrite-spec.schema.json  # THE CONTRACT: the analysis→populate→memo data shape
│   ├── agent-contracts.md           # the 5 parallel analytical subagents + Wave-2 synthesis steps
│   ├── populator.py                 # openpyxl populate + reconciliation + ALL the hard gates
│   └── state_ledger.py              # durable phase-state (restart-resume, critical-input gate)
├── references/                   # 17 scoped methodology docs (read-one-per-question)
└── templates/                    # exact Mini Model cell maps (ACQ + EFB)
```

**Three consumption surfaces, by how deterministic the need is:**

1. **The calc engine (`engine/`)** — pure deterministic compute. `acq_engine.py` does the full ACQ deal (bridge→agency-refi debt, exit-cap triangulation, levered IRR/EM/CoC, agency takeout sizing, property-tax range, NOAH detection, interest reserve, lease-up ramp, reprice solver). `lihtc_engine.py` does EFB bond sizing. **Decimal math, no side effects, unit-tested (162 tests).** The app can `import` these directly for any "compute this deal" need — no agent required.

2. **The populate/reconcile pipeline (`fastpath/populator.py`)** — takes an `underwrite-spec.json` + a Mini Model template, writes INPUT cells into a COPY (never a formula cell), runs the hard gates, and reconciles Python vs the Excel re-read. This is where the **safety gates** live (see below). The app can call `populate()` / `reconcile()` to produce the real .xlsx capital partners need.

3. **The playbook (`SKILL.md` + `references/` + `agent-contracts.md`)** — the methodology an AGENT follows to go from raw deal docs → spec. This is the part that needs a Claude agent (judgment: routing, tier strategy, comp curation). This is the "brain."

## The spec is the contract

Everything flows through `fastpath/underwrite-spec.schema.json` — one JSON file per deal. The analytical fan-out writes it, the engine fills `headline_metrics`, the populator consumes `cells[]`, the memo reads `memo_vars`. **If the app wants a clean integration boundary, the spec IS it:** the app (or its agent) produces a spec; the engine + populator turn it into a validated model + metrics. Gates surface as `qa.*` fields; the EFB routing recommendation as `meta.efb_route_signal`; durable state as a sibling `underwrite-state.json`.

## The hard gates (why this is safe enough for autonomy)

The Envy three-way forensic proved the bug in underwriting is **process discipline, not analytical skill** (the same skill produced 214 vs 244 units, opposite OpEx signs, a 9.5pp IRR spread). Waves 1–3 moved the mechanical 90% into deterministic gates the populator ENFORCES (it refuses to write a bad cell):

- **Deal-identity** (BL-02): refuses to populate a wrong-deal / template-fork workbook (foreign tabs, #REF! residuals, vintage mismatch).
- **Unit-count reconcile** (BL-01): blocks a raw unit count with no status/use filter + second source (stops the 244).
- **Fee bounds** (BL-03): refuses the 0.05 EFB sentinel fee on an ACQ deal.
- **Formula audit** (BL-07): named PASS/PATCH verdict on the 5 fragile cells; S40/row-78 auto-patch behind human-confirm.
- **CP-2 reconcile** (BL-05): identity-gated; raises rather than degrading to a transcript; self-render fallback when no external ground truth.
- **Exit-cap / LTV / RUBS** (BL-10/15/16): refuse B79 / B51-B67 / S54 when the gate fails.
- **Critical-input + durable state** (BL-17): Phase 0 blocks until purchase price + hold + exit cap are captured; restart resumes instead of re-parsing.
- **Non-collapsible phase gates** (BL-06): no bulk multi-phase write that hides errors.

**These three are the autonomy floor** (HOTL must not run unattended without them): deal-identity hard gate, unit-count hard gate, CP-2 identity-gated reconcile. They already exist.

## HITL vs HOTL is already modeled

`SKILL.md` §"HITL vs HOTL" + `meta.mode` in the spec: **HOTL** (internal screening) runs all waves to CP-3 unattended; **HITL** (anything outward — IC / lender / JV) stops at CP-1 for one human glance. The CP-2 reconciliation always runs. **BL-04 is locked to stop-at-CP-1**: when the conventional case fails and the asset is structurally EFB, the engine DETECTS + RECOMMENDS but does NOT auto-build the EFB model — a human flips routing. This is the judgment fork the forensic flagged.

---

## Recommended integration: skill-as-agent (Evan's lean)

The app is the **front door**; a skill-running Claude agent is the **underwriter**. This matches the autonomy design already written:

- **The design already exists.** `~/.claude/plans/this-skill-takes-wayyy-generic-aurora.md` Track 2 is the **Avery → Dream Hermes** architecture: register Dream as `dream.underwriter`, invoke via `HermesInvoke { agentId:"dream.underwriter", context:{slug, dealPackagePaths, routingHint, mode:"HITL"|"HOTL"} } → HermesResult { status, summary, artifacts:{specPath, draftXlsxPath, memoPath, gateReached} }`. Read that file — it's the blueprint for the autonomous path. (Also `inspire/HERMES_DESIGN.md` for the canonical Hermes runtime contract.)
- **What runs:** the agent loads `SKILL.md` §"Claude Code Fast Path", runs Wave 0 (route; stop+ask if ambiguous), Wave 1 (the 5 parallel analytical subagents from `agent-contracts.md`), Wave 2 (engine + spec), stops at the gate `mode` dictates. Dispatch via the Agent SDK / Claude Code headless.
- **Where the app fits:** deal intake (email/Drive/OM trigger), the dashboard UI (your `src/components/` — DealCard/MetricCard/ScoreBadge already render exactly the metrics the engine emits), orchestration + the human glance at CP-1, and persistence. The app does NOT need to reimplement the analytics — it invokes the agent and renders `headline_metrics` + the gate results.

**But you can also go skill-as-engine where it's deterministic.** For "just recompute this deal at a new price" or "size the bond," the app can `import` the engine directly — no agent, no tokens. The honest split: **engine = deterministic compute the app calls directly; agent = the full playbook run that needs judgment.** Your `src/` already looks built to display the engine's output shape.

## Practical notes for wiring it up

- **Run the tests** in `underwriting-engine/`: `pip install -r engine/requirements.txt && python -m pytest engine/tests/ fastpath/tests/ -q` → 162 pass. The engine docstrings are NOT a reliable oracle — the tests + the Mini Model workbooks are.
- **Ground truth:** `engine/tests/test_acq_esplanade.py` (Esplanade ACQ: IRR 22.51%, EM 2.72, exit 55.87M) and `test_efb_rayzor.py` are the regression guards. Any engine change must keep these green.
- **The real app runtime** (per Evan's memory) is on the UK VPS at `/opt/dream-app` (PM2 `dream-api`, FastAPI :8001 + Vite). The local `dream/` folder in shieldstone_os is an empty scaffold — don't confuse it for the app.
- **Rent data:** the skill pulls HUD FMR/SAFMR/LIHTC from the Mission Driven REST API (`rent-mcp.shieldstone.co/api/v1/*`, Bearer token). `agent-marketdata` (in `agent-contracts.md`) is the contract for that.
- **Re-sync discipline:** when the skill updates on `dream-fastpath`, re-copy `.skills/dream-underwrite/` → `underwriting-engine/` (exclude the workflow build-artifact). The prior chat used `core.autocrlf` to keep EOL noise out of the diff.

## Open questions to decide on the app side
1. Invoke mechanism: Agent SDK headless vs a reusable Workflow definition (Phase 6 of the plan) — the plan leans on whichever you build first.
2. Deal-intake trigger: email triage / Drive drop / explicit OM forward — Track 2 §3 evaluates these.
3. The HITL/HOTL gate policy is drafted in the skill but the plan says lock it after the forensic landed (it has) — you can finalize which phases run unattended.

---

**Bottom line:** the analytical brain is done, validated, gated, and in your repo. Decide how the app's agents call it — recommended skill-as-agent for full runs, direct engine import for deterministic compute. Start from `SKILL.md` (the playbook) and the Track 2 Hermes design (the autonomy blueprint).
