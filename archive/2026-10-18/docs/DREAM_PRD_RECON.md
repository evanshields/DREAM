# DREAM — PRD Recon (2026-06-05)

> READ-ONLY recon handoff for a fresh chat that will write the full DREAM PRD. Purpose: catalog
> **what already exists and where** so the PRD builds on it, not from scratch. All paths absolute.
> Nothing here was modified. Product vision (Evan-locked 2026-06-05) summarized in §0.

---

## 0. Product vision being recon'd FOR (context)

DREAM = the agentic framework for ALL Development / Real-Estate / Asset-Management analytical work.
The multifamily underwriter is ONE app of it. Product arc:
1. **Chat-bot in an app** — user drops deal docs → 5–20 min autonomous initial underwrite pass
   (the proven Claude Code "Dream fast path": 5 parallel analytical subagents → Python calc engine →
   openpyxl populate → memo) → full write-up of every assumption + open questions → wraps.
2. **Populate the app** — DECISION 2026-06-05: **broaden the already-built "EFB Underwriter" app**
   into a general Acquisition underwriter (reuse stack/UI/calc, do NOT rebuild). User tweaks
   assumptions live + runs sensitivities.
3. **Push to Excel** — export the app's assumptions onto the Excel Mini Model on demand.
4. **Hermes layer** — deals from Drive/email/Slack flow through the SAME pipeline and land as the
   SAME deal instance on the app.

**Cost discipline:** rote Python for every mechanical step; agents reserved for judgment forks.
Padawan already solved much of this.

---

## TL;DR — what already exists vs what's net-new

| Capability | Exists where | Verdict |
|---|---|---|
| Proven 3-wave underwrite process (chat-bot's core loop) | `c:\Users\evana\shieldstone_os\.skills\dream-underwrite\` (SKILL.md §Fast Path, fastpath/, engine/) | **REUSE** — port server-side |
| Python calc engine (ACQ + LIHTC/EFB) | `.skills\dream-underwrite\engine\{acq_engine.py, lihtc_engine.py}` (19+ tests, validated) | **REUSE as-is** |
| Spec contract (assumptions as data) | `.skills\dream-underwrite\fastpath\underwrite-spec.schema.json` | **REUSE/EXTEND** — basis for app data model |
| 5 parallel analytical agent contracts | `.skills\dream-underwrite\fastpath\agent-contracts.md` | **REUSE** — these become server jobs |
| openpyxl populate + Python↔Excel reconcile + identity check | `.skills\dream-underwrite\fastpath\populator.py` | **REUSE** — this IS the "push to Excel" (step 3) |
| Cost-routing (Gemini/ChatGPT/Claude tiers) | Padawan `H:\My Drive\_ShieldstoneX\Corporate AI Agents\acquisition_pipeline\config\llm_router.py` | **REUSE/EXTEND** |
| LLM-tier routing strategy + cascade + assumption-dashboard design | `H:\My Drive\_ShieldstoneX\DREAM\_Artifacts\DREAM_AI_ARCHITECTURE_STRATEGIC_GUIDANCE.md` | **REUSE** — design input, not code |
| DreamVision product PRD (Domain 1) | `H:\My Drive\_ShieldstoneX\DREAM\dream_vision_claude_code\DreamVision_PRD_v3.md` (+ `_Artifacts\` copy) | **EXTEND** — prior PRD, partly stale |
| DREAM product GitHub repo | `github.com/evanshields/DREAM` (main; PR #2 open) | **EXTEND** — product home |
| "EFB Underwriter" app (the thing we broaden) | **UK VPS `/opt/dream-app/`** (PM2 `dream-api`, FastAPI :8001 + Vite) — near-complete v1, confirmed 2026-06-05 | **BROADEN** (EFB→ACQ, +Excel push, +Hermes) |
| App data model w/ "assumptions as first-class editable objects" | partial (spec.cells[] is the seed); no live app model | **BUILD** |
| Chat-bot orchestration server-side (replaces Claude Code as driver) | does not exist | **BUILD** |
| Hermes intake (Drive/email/Slack → same deal instance) | designed only ([[reference_shieldstone-hermes]], [[project_avery-orchestrator]]) | **BUILD** |

---

## 1. Prior PRDs

### 1a. DreamVision PRD v3.0 — `H:\My Drive\_ShieldstoneX\DREAM\dream_vision_claude_code\DreamVision_PRD_v3.md` (dup at `...\DREAM\_Artifacts\DreamVision_PRD_v3.md`)
- **Product:** DreamVision = DREAM.AI **Domain 1** (Acquisitions Intelligence). DREAM.AI framed as a
  4-domain super app (D1 Acquisitions, D2 IR/Capital, D3 Asset Mgmt, D4 Construction/Dev). This
  matches today's locked "DREAM = all Dev/RE/AM" definition — the PRD already conceived DREAM as the
  umbrella and the underwriter as one domain.
- **Scope:** deal intake/doc extraction, configurable investment criteria, market research
  (Perplexity), scoring, BOE memo, **Phase-2 full DCF + assumption engine + sensitivity + Excel
  export with working formulas + interactive dashboard**, pipeline CRM, multi-asset-class.
- **Stack (decided):** React+TS+Tailwind / Python+FastAPI / PostgreSQL (RLS) / Clerk|Auth0 /
  S3-compatible / Claude+Gemini+Perplexity routing / ReportLab|WeasyPrint / Docker.
- **Data model:** Organization → Users/Criteria/Integrations; **Deal → Property/Documents/Analyses/
  Stage/Notes/Tasks/Activity**; **Analysis → ExtractedData/MarketResearch/Scores/Recommendation/
  Reports/UserOverrides**; Market(cached). (PRD §4.3.)
- **Built vs planned:** Planning doc only — no code shipped against it that this recon found.
- **Stale?** Partially. Pre-dates: the validated Python engine, the fast-path 3-wave/agent-contract
  architecture, the rent-MCP, and the 2026-06-05 "broaden EFB app" decision. The Phase-1/2 feature
  list and data model are still highly relevant and should be **carried forward, not discarded**.
- **Reuse:** Data-model entities and the assumption-dashboard/Excel-export requirements are directly
  reusable as PRD scaffolding.

### 1b. DREAM AI Architecture — Strategic Guidance — `H:\My Drive\_ShieldstoneX\DREAM\_Artifacts\DREAM_AI_ARCHITECTURE_STRATEGIC_GUIDANCE.md`
- Not a product PRD but a **strategic architecture doc** explicitly written to feed the DREAM PRD.
- Covers: intelligent request routing (RequestType/DealComplexity enums + `route_request`), the
  **cascade** approach (open-source/Haiku → Sonnet → Opus), open-source model matrix, and — most
  relevant — **Part 4 "Interactive Assumption Tweaking"** with the exact pattern the vision needs:
  *Python financial model for instant recalculation, LLM only for async insight; never call an LLM to
  recalculate.* Also a 5-phase implementation roadmap and a "Critical Decisions for Dream PRD" list.
- **Reuse:** This is the single best design input for the cost-discipline + assumption-dashboard
  sections of the new PRD. Largely still valid.

### 1c. INSPIRE_V2_PRD — `c:\Users\evana\shieldstone_os\inspire\INSPIRE_V2_PRD.md`
- **DIFFERENT PRODUCT / DIFFERENT ESTATE (USDV/INSPIRE — DSCR/BPL/BTR loan origination).** Per
  memory `feedback_usdv-vs-shieldstone-scope`, **do not conflate** with DREAM. Noted, not analyzed.
  (Also `inspire/INSPIRE_V2_LINEAR_BACKLOG.md`, `inspire/INSPIRE_VPS_INVENTORY.md` etc. — all USDV.)

> Glob "**/*PRD*" across the whole repo timed out on node_modules; scoped search found the above.
> Other `*PRD*`/`*roadmap*` hits not surfaced — if the fresh chat needs exhaustive coverage, run a
> node_modules-excluded scan. Confirmed DREAM-relevant PRDs are 1a–1b; 1c is out-of-scope INSPIRE.

---

## 2. The "EFB Underwriter App" — THE THING WE BROADEN

**✅ LOCATED & CONFIRMED 2026-06-05 (correction to the original recon, which checked only this
machine):** the app is **NOT in the local repo** — it lives on the **Shieldstone UK VPS**
(`shieldstone-uk` / 187.124.113.118) at **`/opt/dream-app/`**, running (when up) as PM2 app
**`dream-api`** via FastAPI + uvicorn on **port 8001** (`ecosystem.config.js`, cwd
`/opt/dream-app/backend`). It was found **stopped**; restart with `pm2 start dream-api`.

### 2.0 — The real EFB Underwriter app (`/opt/dream-app/`, UK VPS) — CONFIRMED
`backend/calculations/__init__.py` self-identifies: *"Shieldstone EFB Underwriting — Calculations
Package."* Stack: **FastAPI backend + Vite frontend** (Playfair Display + Geist fonts, on-brand),
Python 3.13 venv (pandas + pymupdf). It is a near-complete v1 of the DREAM product arc — every step
already has an endpoint:

| DREAM arc step | Existing endpoint / module |
|---|---|
| Drop deal docs → parse | `POST /api/intake` → `intake/intake_service.py` + `field_mapper.py` (pymupdf PDF) |
| Chat-bot pass + open questions | `POST /api/agent/chat` (streaming) → `agent/` (`memo_generator.py`, `kimi_client.py` — **Kimi**, a cheap LLM; `prompts.py`) |
| Run the underwrite | `POST /api/underwrite` → `calculations/efb_engine.py` |
| Validate vs standards | `POST /api/validate` → `calculations/validator.py` (T-Manual V2 GREEN/AMBER/RED) |
| Memo write-up | `agent/memo_generator.py` |

**Data model** (`backend/models.py`, Pydantic): `PropertyInputs / UnitType / RevenueInputs /
ExpenseInputs / GeneralPartnerInputs / CapitalInputs / BondInputs` (+ `DealInputs`). Comments show
fields were **deliberately pruned to match Excel EFB Acquisition Sizing Tool V2** — so the app↔Excel
assumption contract for Step 3 (push to Excel) ALREADY EXISTS as a shared schema.

**Calc engine** (`backend/calculations/`): `efb_engine.py` (sources/uses, pro forma, exit,
sensitivity, EFB tax advantage), `bond_sizing.py` (size-to-DSCR/LTV + amortization), `returns.py`
(IRR/EM/CoC, numpy-only — no scipy), `validator.py`. This is the deterministic "tweak → instant
recalc" layer the strategic-guidance doc (§1b) demands.

**Built vs. gap (the broaden delta):** BUILT = data model, calc engine, intake, streaming chat,
validator, brand UI, all endpoints. GAPS to close for the DREAM vision = (1) **EFB-only → broaden to
general ACQ** (source: the skill's `acq_engine.py`, §5/§2c); (2) agent uses **Kimi** — decide keep
cheap-LLM vs. route via Padawan's `llm_router.py` (§3a); (3) **no app→Excel push** yet; (4) **no
Hermes intake** yet; (5) reconcile this app's `models.py` schema with the skill's
`underwrite-spec.schema.json` (§5) so the chat-bot fast path writes straight into the app. Also note
`/var/www/dream1400` on the same box (inspect) and the stopped `dream-api` shares the UK VPS with the
OpenBrain/BD stack.

**This is a BROADEN-don't-rebuild foundation — decision validated against real running code.** Saved
to memory `reference_efb-underwriter-app`.

### 2a. Local `c:\Users\evana\DREAM\docs\` — a DreamVision app **scaffold** (NOT the app)
*(Kept for clarity — this empty scaffold is what the first recon pass mistook for the missing app.
The real app is §2.0 above on the UK VPS.)*
- **Stack (observed):** Vite + React + TS + Tailwind frontend (`src/` with `components/ui`, `layouts`,
  `pages`, `lib/shieldstone`); **Python FastAPI backend** (`backend/api/`); **Supabase**
  (Postgres + Supabase Auth) per `backend/.env` (DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY,
  SUPABASE_SERVICE_ROLE_KEY). NOTE: memory says "Dream.AI stack: FastAPI + LangGraph + React +
  Railway" — the `.env` here shows **Supabase**, not Railway, and no LangGraph evidence. Reconcile w/
  Evan.
- **Reality check:** Almost no real source. `src/**` are `desktop.ini` placeholders + `react.svg`.
  `backend/api/` contains only `__pycache__/deals.cpython-314.pyc` — a `deals.py` **was** compiled here
  once but **no `deals.py` source is present** (likely a deals CRUD module that was deleted/never
  synced). `agent_architecture/agents/phase1..phase8/` dirs exist but are **empty** (desktop.ini only)
  — an 8-phase agent skeleton that was scaffolded but never filled.
- **Git:** part of the parent `shieldstone_os` repo (origin `github.com/evanshields/Shieldstone.git`),
  not its own repo.
- **`.claude/skills` here:** collaboration, theme-factory, web-artifacts-builder, repos (generic).
- **Verdict:** This is a stalled DreamVision web scaffold, NOT a working "EFB Underwriter app." It may
  be the intended home, or a dead start. Its **data model intent** (a `deals` API module) is the only
  signal. Treat as a possible UI/stack starting point, but the EFB underwriter app Evan referenced is
  either (a) elsewhere/another machine, (b) the INSPIRE/efb-uw skill conflated, or (c) not yet built.

### 2b. DREAM Drive scaffolds — `H:\My Drive\_ShieldstoneX\DREAM\{dreamvision, dream-vision, dream_vision_claude_code}\`
- All three are **default Vite+React+TS templates** (README is the stock Vite template text). Only
  `dream_vision_claude_code` carries real signal: the **DreamVision_PRD_v3.md** (see §1a) and a
  ShadCN `components.json`. These are empty UI shells, not the EFB app.

### 2c. Calc layer the app must share
- There IS a proven calc layer to wire any underwriter app to:
  `c:\Users\evana\shieldstone_os\.skills\dream-underwrite\engine\{acq_engine.py, lihtc_engine.py}`
  (see §5). The strategic-guidance doc (§1b Part 4) is explicit that the app's live "tweak an
  assumption → instant recalc" must call **this Python engine**, not an LLM. So the EFB app's calc
  layer = these engines exposed behind a recalculation endpoint.

**OPEN QUESTION for Evan (high priority): Where is the actual EFB Underwriter app code/deploy?**
(Repo name + URL + stack confirmation.) Everything downstream of "broaden it" depends on this.

---

## 3. Padawan — `H:\My Drive\_ShieldstoneX\` (folder: `Corporate AI Agents\`)

"Padawan" is the Shieldstone corporate-AI-agents body of work in `H:\My Drive\_ShieldstoneX\` (the
`Padawan AI Backend.gscript` file sits at the `_ShieldstoneX` root; the live code lives under
`Corporate AI Agents\`). Key reusable IP:

### 3a. Multi-LLM cost router — `...\Corporate AI Agents\acquisition_pipeline\config\llm_router.py`
- **This is the core cribbable cost-discipline IP.** `LLMRouter.route_task(TaskSpec, prompt)` routes by
  `TaskComplexity` (SIMPLE→Gemini ~$0.0001, MODERATE→ChatGPT/gpt-4o-mini ~$0.002, COMPLEX→Claude
  ~$0.03), with `critical_decision`/`quality_requirement>0.95` forcing Claude, automatic fallback
  cascade (Gemini→ChatGPT→Claude), and `usage_stats` cost tracking. `TaskCategory` enum
  (DATA_EXTRACTION / VALIDATION / FUZZY_MATCHING / CLASSIFICATION / BUSINESS_LOGIC /
  STRATEGIC_REASONING). Claimed **67% savings vs Claude-only** ($4 vs $12 per pipeline run).
- DREAM crib: lift this router pattern for the chat-bot's per-step model selection (mechanical
  extraction → cheap model; judgment forks → Claude). Aligns 1:1 with the §1b cascade strategy.

### 3b. Deterministic Python acquisition agents — `...\acquisition_pipeline\agents\01..08_*.py`
- 8 Python agents (data consolidation across 238 Excel files; ownership ID; fund-maturity scoring;
  seller-motivation scoring; NMHC attendee matching; exec-contact finder; LIHTC strategy classifier;
  state LIHTC collector). Pattern = **rote Python does the heavy mechanical lifting; LLM called only
  for fuzzy/judgment steps** — exactly DREAM's cost principle. Plus reusable utilities:
  `utils\string_matching.py` (fuzzy company-name matching), `utils\data_quality.py` (0–100 quality
  scoring), `integrations\google_sheets_client.py` (batch writes), `integrations\perplexity_client.py`
  (research wrapper), `config\settings.py` (criteria/paths). Checkpointing dir `state\checkpoints\`.
- Context doc: `...\Corporate AI Agents\HANDOFF_MEMO_Jan22_2026.md` (full architecture + cost table).
- **Note:** This is a *sourcing/prospecting* pipeline, not an underwriter — its reusable value is the
  **router + deterministic-agent + quality-scoring + checkpointing patterns**, not the deal logic.

### 3c. "The Ai Manager" — `...\Corporate AI Agents\The Ai Manager\` + `workflows\`
- Agent run logs (Mar–Apr 2026) for a manager/orchestrator agent (Fathom + Slack agents) and two n8n
  workflow JSONs (`workflow_1_intake_and_classification.json`, `workflow_2_auto_decline.json`). Signal
  for the **intake/classification + orchestration** pattern Hermes will need; logs are operational, not
  architecture, but the workflow JSONs are a concrete intake-routing reference.

**Reusable IP summary:** cost router (3a) > deterministic-Python-agent pattern + utils (3b) > intake
workflows (3c). Crib the router and the "Python owns ~90%, LLM owns the judgment fork" decomposition.

---

## 4. `_ShieldstoneX` DREAM assets inventory — `H:\My Drive\_ShieldstoneX\`

| Path | What it is | Cribbable? |
|---|---|---|
| `DREAM\_Artifacts\DREAM_AI_ARCHITECTURE_STRATEGIC_GUIDANCE.md` | Strategic architecture (routing/cascade/assumption-dashboard/roadmap) | **YES — top design input** |
| `DREAM\_Artifacts\DreamVision_PRD_v3.md` | Copy of DreamVision PRD v3 | YES — prior PRD |
| `DREAM\dream_vision_claude_code\` | Vite+React+TS scaffold + DreamVision_PRD_v3.md + ShadCN components.json | PRD yes; code = empty shell |
| `DREAM\dreamvision\`, `DREAM\dream-vision\` | Two more empty Vite+React+TS template scaffolds | Low — duplicate shells |
| `Corporate AI Agents\` (Padawan) | Cost router + 8 Python agents + utils + n8n workflows + manager logs | **YES — see §3** |
| `Padawan AI Backend.gscript` | Apps Script backend stub (157 bytes pointer) | Reference only |
| `Claude SKILLS\`, `SKILLS\` | Skill libraries (not opened in this pass) | Maybe — flag if PRD needs |
| `AI C-Suite\`, `AI Prompts & Data Lake\`, `Built Different Engine\` | Other agent estates | Out of scope for DREAM UW |

No prior *app version* of the EFB underwriter found in `_ShieldstoneX` — only scaffolds + the PRD + the
strategic guidance. The genuinely reusable assets are the **strategic-guidance doc, the DreamVision
PRD, and the Padawan router/agents** — everything else under DREAM\* is empty Vite boilerplate.

---

## 5. The proven fast-path process (the backend spec the chat-bot implements)

Source of truth: `c:\Users\evana\shieldstone_os\.skills\dream-underwrite\` — SKILL.md §"Claude Code
Fast Path (DEFAULT)", `fastpath\agent-contracts.md`, `fastpath\underwrite-spec.schema.json`,
`fastpath\populator.py`, `engine\{acq_engine.py, lihtc_engine.py}`. This is what the app's server-side
chat-bot must replicate (today it's driven by Claude Code; DREAM must run it as a service).

### 3 waves + checkpoints
- **Wave 0 — Routing + intake.** ACQ-vs-EFB auto-detect (`references/01-deal-routing.md`). Ambiguous →
  ask once and STOP, never guess. Stage docs to `shieldstone_acquisitions\underwrites\<slug>\`.
- **Wave 1 — 5 parallel analytical subagents** (each a pure function: doc paths + ONE scoped reference →
  JSON slice only; writes nothing; shares no state):
  - `agent-t12` — T-12 spread + forensic block (T12/T6/T3 NOI, vacancy trend, concessions,
    loss-to-lease, bad debt, anomalies, lease-up flag, takeaways). QA gate: `t12_unmapped` MUST be 0.
  - `agent-rentroll` — rent-roll spread + unit mix (R/S/T/U/W per bedroom×tier); QA:
    `rr_vs_t12_gpr_gap_pct` within 5%.
  - `agent-assumptions` — pricing/closing/fees/debt/sale INPUT cells (cols A–B); NEVER writes formula
    cells; whisper-bid sanity check; flags formula-audit cells.
  - `agent-comps` — sales/rent/construction-pipeline comps + `median_ppu` (ranked candidates, human
    curates at CP-1).
  - `agent-marketdata` — FMR/SAFMR/LIHTC/OpEx triangulation via Mission Driven REST API
    (`https://rent-mcp.shieldstone.co/api/v1/*`); every value carries an API citation.
- **Wave 2 — synthesis + calc engine (orchestrator, sequential, NOT an agent).** Merge 5 slices into one
  `underwrite-spec.json`, then run: rent tiers (NOAH/HAP/P75) → other income/OpEx → OpEx triangulation
  → vacancy curve → property tax (EFB $0 / ACQ reassessment) → **sizing** (`acq_engine` bridge→agency
  refi w/ DSCR+LTV+Debt-Yield MIN constraint, OR `lihtc_engine.BondSizingCalculator` for EFB) → exit
  cap (ACQ `ExitCapTriangulator`, take HIGHEST) → write `headline_metrics`. **→ CP-1** (the one
  analytical glance: full spec + headline_metrics + every QA gate ✅/❌).
- **Wave 3 — populate + reconcile + memo.** `populator.populate(spec, template)` writes INPUT cells into
  a COPY (refuses formula cells; structural-diff guard; PENDING EXCEL RECALC marker) → human opens in
  Excel once → `populator.reconcile()` diffs Excel headlines vs Python at tiered tolerance (headlines
  ~0.5%, line items ~2%). **→ CP-2.** Then Phase-12 HTML memo from `spec.memo_vars`. **→ CP-3.**
- **Modes:** `meta.mode` HOTL (internal screening, runs to CP-3 unattended) vs HITL (outward — stops at
  CP-1). CP-2 reconciliation always runs.

### The spec contract — `fastpath\underwrite-spec.schema.json` (THE app data-model seed)
One file per deal at `shieldstone_acquisitions\underwrites\<slug>\underwrite-spec.json`. Top-level:
`meta` (deal_name, slug, routing ACQ|EFB, template, freshness, mode), `qa` (t12_unmapped,
rr_vs_t12_gpr_gap_pct, formula_audit[], whisper_flag, **reconcile[]**, gates), **`cells[]`** (flat list,
each `{cell, value, type, source, phase, input_only}` — every value that lands in the Mini Model with a
citation), `headline_metrics` (noi_series, dscr_series, irr, equity_multiple, coc, bond_amount,
tax_savings_10yr…), `comps`, `forensic`, `narrative`, `memo_vars`. **This `cells[]` + assumptions block
is the natural basis for "assumptions as first-class editable objects" in the app.**

### Engine I/O — `engine\acq_engine.py` + `engine\lihtc_engine.py`
- **`acq_engine.py`** (conventional value-add) public classes: `SeniorDebtCalculator`,
  `InterestReserveSizer`, `LeaseUpRamp`, `FourTierOptimizer` (GPR), `AgencyTakeoutSizer` (DSCR+LTV+
  Debt-Yield binding constraint), `ExitCapTriangulator` (3-method, take HIGHEST), `PropertyTaxCalculator`
  (state-specific reassessment), `ACQCashFlowProjector` (year-by-year vacancy curve, bridge→agency-refi
  debt service), `HurdleCalculator`; result dataclasses `ACQReturnResult` (levered IRR / equity multiple
  / cash-on-cash), `DebtServiceYear`, `ExitCapResult`, `AgencySizingResult`, `HurdleResult`.
- **`lihtc_engine.py`** (LIHTC/EFB, proprietary) public calculators: `EligibleBasisCalculator`,
  `QualifiedBasisCalculator`, `CreditCalculator`, `EquityPricingCalculator`, `DeveloperFeeCalculator`,
  `SourcesAndUsesBalancer`, **`BondSizingCalculator.size_bonds(...)`** (monthly-compounding PV — docstring
  example is WRONG, trust the workbook), **`AMIRentCalculator`**, `RevenueProjector`, `OpExBenchmarker`,
  `CashFlowProjector`, `DeveloperReturnCalculator`, `PartnershipStructureCalculator`,
  `InvestorReturnCalculator`, `DealScoringEngine`, and a **`DreamAIOrchestrator`** workflow skeleton
  (`execute_workflow(initial_data)` → `WorkflowResult`) — note this orchestrator already exists as a
  Python class and is a candidate backbone for the server-side chat-bot loop.
- **Validation:** ACQ vs `shieldstone_acquisitions\deal-memos\build_esplanade_acq.py` (IRR 22.21% vs
  22.51%, EM 2.73 vs 2.72, exit value exact); EFB vs Rayzor Ranch EFB Mini Model. Tiered tolerance.
  Tests: `engine\tests\` + `fastpath\tests\` (PR #2 reports 25 passing).

### Populator — `fastpath\populator.py`
`populate()` (copy template, write INPUT cells only, refuse formulas, structural-diff guard, PENDING
marker), `reconcile()` (CP-2 Python↔Excel diff at tiered tolerance; `METRIC_CELLS_ACQ` cell map),
`deal_identity_check()` (template-fork carryover guard — catches a workbook still carrying a prior
deal's name/units, the Envy/Aviara bug), `is_recalced()`. **This module IS the "push to Excel" feature
(arc step 3) — already built.**

---

## 6. DREAM repo state — `github.com/evanshields/DREAM`

- **Repo:** `evanshields/DREAM` — "Repo for the DREAM super app for the CRE industry." Default branch
  **main**. Last push **2026-06-04 23:57**. This is the product home (DreamVision Phase 2 per memory).
- **No local clone of `evanshields/DREAM` found** under `c:\Users\evana\` (searched DREAM/dream*; only
  the in-repo `shieldstone_os\dream\` scaffold and the `_ShieldstoneX\DREAM\` Drive scaffolds exist).
  **Flag: clone the repo for the build chat.**
- **PR #2 — `add-underwriting-engine` — OPEN (created 2026-06-04 23:58).** Mirrors the canonical
  `.skills\dream-underwrite\` into the product repo under **`underwriting-engine/`** (engine/, fastpath/,
  references/, templates/, scripts/, SKILL.md). Body explicitly: *"that repo [shieldstone_os] stays the
  source of truth; this copy is for the DREAM product to consume."* Reports **25 tests passing** and ties
  to Esplanade/Rayzor ground truth. → The engine is being **vendored into the product** as we speak.
- **PR #1 — `Build sales funnel page` — DRAFT (2025-12-06).** Marketing funnel page (Cursor-generated),
  not core product. Stale-ish.
- **Staleness:** Repo is active (pushed yesterday). The substantive content is arriving via PR #2; main
  itself is likely still light (the DreamVision PRD + scaffolds). Confirm what's on `main` after cloning.

---

## 7. Gaps & open architecture questions for the PRD

Each is a **net-new build** (does not exist today) unless noted:

1. **[BLOCKER] Locate/confirm the "EFB Underwriter" app.** Not found on this machine. The entire
   "broaden, don't rebuild" decision hinges on it. Need repo + URL + stack confirmation from Evan.
   (Candidates: the empty `shieldstone_os\dream\` scaffold; an off-machine repo; or it's conceptual.)
2. **Server-side chat-bot orchestration.** Today the 3-wave flow is driven by Claude Code (a human's
   IDE). DREAM must run Wave 0–3 as a **backend service** (job queue, parallel agent dispatch, the
   `DreamAIOrchestrator` skeleton in lihtc_engine.py as a possible backbone). Net-new.
3. **App data model: "assumptions as first-class editable objects."** `underwrite-spec.json` `cells[]`
   is the seed but it's a flat cell list keyed to Excel addresses. The app needs a **semantic
   assumption model** (named, typed, ranged, benchmark-annotated, with provenance) that maps both to
   the engine inputs AND to Excel cells — per the §1b Part-4 assumption-dashboard design. Net-new
   (design exists, code doesn't).
4. **Live recalc endpoint.** Wire the Python engines (§5) behind a sub-100ms recalculation API so the UI
   "tweak → instant returns" works without LLM calls (the §1b cardinal rule). Net-new.
5. **App ↔ Excel export (productized).** `populator.py` does this in Claude Code today; needs to become a
   server endpoint operating on user-selected Mini Model templates. Mostly exists, needs productizing.
6. **Hermes intake** (Drive/email/Slack → same deal instance). Designed only
   ([[reference_shieldstone-hermes]], [[project_avery-orchestrator]], plan
   `~/.claude/plans/this-skill-takes-wayyy-generic-aurora.md`). Net-new.
7. **Cost-routing service.** Padawan's `llm_router.py` is a script, not a service; needs to become the
   shared model-selection layer (and model IDs are 2024-vintage — `claude-3-sonnet-20240229`,
   `gpt-4o-mini`, `gemini-1.5-flash` — update on adoption). Extend.
8. **Stack reconciliation.** Memory says "FastAPI + LangGraph + React + Railway"; the local scaffold
   `.env` shows **Supabase** (no Railway, no LangGraph). PRD must lock the real stack. Resolve w/ Evan.
9. **Multi-app framework vs single underwriter.** Vision says DREAM is the framework for ALL Dev/RE/AM
   work; the underwriter is app #1. PRD must define the **framework/shell** (auth, deal model, agent
   runtime, cost router, Hermes intake) separately from the **underwriter app** so D2/D3/D4 (per
   DreamVision PRD's 4-domain map) can plug in later. Architecture decision.

---

## 8. Recommended PRD shape (skeleton only — fresh chat details it)

Proposed **6 waves/epics**. Keep the "framework vs first app" split from gap #9 throughout.

- **Wave A — Framework foundation.** Lock stack (resolve gap #8), deal/assumption data model (gap #3),
  auth/org, deal instance store. Vendor the engine (PR #2's `underwriting-engine/`) as the shared calc
  core. Stand up the cost-routing service (gap #7, crib Padawan §3a).
- **Wave B — Broaden the underwriter app (REUSE).** Resolve gap #1 first. Extend the existing EFB app's
  UI/stack/calc into a general ACQ underwriter using `acq_engine.py` + `lihtc_engine.py`. Live recalc
  endpoint (gap #4). Assumption dashboard per §1b Part 4.
- **Wave C — Chat-bot initial-underwrite service.** Port the 3-wave fast path server-side (gap #2):
  doc upload → Wave 0 routing → 5 parallel agents (§5 agent-contracts as jobs) → Wave 2 synthesis +
  engine → produce the assumption write-up + open-questions list → populate the app. HITL/HOTL modes.
- **Wave D — App → Excel push (PRODUCTIZE).** Turn `populator.py` (populate + reconcile +
  identity-check) into an on-demand export endpoint against user Mini Model templates (gap #5).
- **Wave E — Hermes intake.** Drive/email/Slack → same pipeline → same deal instance (gap #6). Crib
  Padawan intake workflows (§3c) + [[reference_shieldstone-hermes]].
- **Wave F — Cost-optimization + multi-domain hooks.** Cascade/open-source per §1b roadmap; framework
  hooks so D2/D3/D4 (IR, Asset Mgmt, Construction) can attach. Sensitivities/scenarios polish.

**Carry-forward source docs for the PRD author:** §1b strategic-guidance (routing/cascade/assumption
dashboard), §1a DreamVision PRD (data model + feature set), §5 fast-path spec + agent-contracts +
schema (the backend contract), Padawan `llm_router.py` (§3a). Resolve the §7 BLOCKER (locate EFB app)
before Wave B.

---

### Provenance note
Recon performed read-only 2026-06-05. Whole-repo Glob for `*PRD*/*roadmap*/*backlog*` timed out on
`dream/node_modules`; findings used scoped searches + direct directory reads. The Drive `.git` under
`_ShieldstoneX\DREAM\dream_vision_claude_code` is not a working repo locally (git commands returned 128).
GitHub state read via `gh` CLI. `.env` values were inspected for keys only and are NOT reproduced here.
