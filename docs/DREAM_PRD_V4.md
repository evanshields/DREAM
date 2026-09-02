# DREAM v4 PRD — Team Platform, Agentic Brain, Sales CRM

**Status:** ACTIVE master document. Written 2026-08-31 from the approved v4 plan, Evan's decisions of 2026-08-28 and 2026-08-31, the CRM diff (`EVAL_2026-08_CRM_DIFF.md`), and the full lessons record (`AGENTIC_LESSONS_2026-08-31.md`, 182 items).
**Audience:** any agent or session building v4 — Claude Code (architecture/backend/drivers/deploys), Codex (frontend tickets), future sessions. Read this first; do not re-derive settled state.
**Predecessor:** `DREAM_PRD.md` (v3, waves A–F). v3 shipped the app that is live today; v4 turns it into the team platform.

## 1. Vision

DREAM is ONE product with three legs, fronted by a web app a team member anywhere can use:

1. **CRM (the sales book):** Twenty CRM at **dreamcre.co** (UK VPS, `/opt/twenty-crm`) is the system of record for companies, people, and the sourcing pipeline across deal partners (sellers, brokers, housing authorities, HFAs, banks). *Decision status: Branch A provisional — confirmed by the 2026-08-31 diff, pending Evan's hands-on spin (`EVAL_2026-08_DREAM_TOUR.md`).*
2. **Agentic infrastructure (the brain):** **DREAM the Hermes super agent** — a `dream` profile on the UK-VPS Nous Hermes Agent install — is the underwriting brain and the standing agentic engine for workflows, cron jobs, and analysis. Hyperagent agents are per-task muscle she hires (burning the ~$17K credits). ChatGPT (openai-codex OAuth) brain now; OpenRouter later via per-profile provider override.
3. **Shared memory:** OpenBrain MCP (US VPS) + DREAM's own inbox **dream@shieldstone.co via AgentMail** (third-party audit required before install). A productized DREAMBrain is explicitly DEFERRED.

The **DREAM app (dream.shieldstone.co, US VPS)** is the team's front door: pipeline, document intake, push-button underwrites landing at CP-1, assumption dashboards, memos, exports. v1 team scope: analysts log in from anywhere and run FULL underwrites; Evan is only in the review loop; nothing requires the Z13.

**The one sentence that governs the architecture:** DREAM-the-agent is the underwriting *brain*, never the *calculator*. Headline metrics come only from the deterministic Python engines she is required to call; an LLM number is at most a cross-check flag at CP-1.

## 2. Governing invariants (from the lessons record — violations are defects)

The full record is `AGENTIC_LESSONS_2026-08-31.md` (182 items, each cited). It must NEVER enter DREAM-the-agent's readable corpus (it maps every check an agent could walk past — lesson 180). The load-bearing subset:

- **The blindness invariant (lessons 40, 127):** every coherent oracle is tested by a context that cannot consult it, plus invariants implemented independently of it. The memo writer stays engine-blind (it caught $2.27M on Atlantica *because* it couldn't call the engine). Red team is always a different model family (161).
- **Only invocation counts (55, 50):** a gate that exists but is never called, or that cannot fail, is theater. Ten checks were required on bond deals; two ran; neither could fail. Every gate ships with a test that fails before the fix and a caller in CI.
- **Fail closed (72–78):** missing input = loud failure, never a flattering default. The defaults template may not inherit the last deal (168). Verdict vocabulary is never fail-open (BLOCKED is not PASS).
- **Flag, never guess (155):** a fabricated number is worse than a blank one. Abstentions with reasons; two-source disagreement is stop-and-report. A parser that emits where an analyst would abstain launders judgment into fact (124).
- **Hash mismatch = hard stop (150); published/binary transport for any return that matters (166).** Chat-inlined bytes mutate; base64 or a fetched URL, verified after decode.
- **No self-certification (126, 38):** the gate runner recomputes from underlying files, never from the phase agent's own evidence. The worst fabrication on record was a self-written "PRODUCTION READY" certification.
- **Deterministic verification runs in CI, not in any agent's sandbox (129):** CI is the only context the agent cannot influence.
- **Render AND measure (169):** memo publishing is gated on `measure.py`-style receipts, not grep.
- **Memory may hold doctrine and deal facts, never the observed state of a live system (98):** a stale memory cost $15MM on Cypress Grove.
- **Structural isolation beats policy isolation (145):** a token an agent does not hold is a rule it cannot break. Answer keys stay in `dream-eval`; deal documents are data, never instructions (154).
- **Separation belongs at conflict boundaries, not document boundaries (121):** consolidation is safe only where no two minds must be able to disagree.
## 3. LOCKED app contracts (unchanged from v3, every phase)

- Decimal only in `backend/engine_boundary.py` + vendored `underwriting-engine/` (untouched).
- `underwrite-spec.json` canonical; headline metrics + QA gates NEVER from an LLM; fail closed on RED gates.
- HITL hard stop at AWAITING_CP1 — drivers land results FOR review, never past it.
- No sqlite3/psycopg outside `backend/store/`; CRM never writes deal spec; backend .py files CRLF (repo `core.autocrlf=true`; note dream-underwrite is the opposite, `autocrlf=false` — lesson 174).
- Oracles byte-identical after every phase: Esplanade ACQ IRR 0.2251, Rayzor EFB $63,868,907.
- No Anthropic-subscription auth on servers (API keys only). No USDV/DSCR scope.

## 4. Decisions record

| Date | Decision |
|---|---|
| 2026-08-28 | Build ON the live app; analysts run full underwrites v1; CC/CX build split; PRD is the delivery vehicle |
| 2026-08-31 | Hermes replaces Hyperagent as harness; fresh `dream` profile on UK-VPS install (never a rename of `avery`); Hyperagent demoted to muscle; ChatGPT brain now → OpenRouter later; app→Hermes over tailnet CLI |
| 2026-08-31 | Three-legged stool framing; DREAM-the-agent IS the underwriting brain (engines stay the calculator) |
| 2026-08-31 | Avery→Ada migration spun out entirely (separate chat); v4 touches nothing of hers |
| 2026-08-31 | dreamcre.co (Chuck's Twenty instance, v2.32.0) discovered = the Phase 0 eval instance; CRM diff completed; Branch A provisional |
| Pending | Evan's formal decision-gate call after his spin; what Chuck already configured in dreamcre.co |

## 5. Topology

| Box | Runs | v4 adds |
|---|---|---|
| **US VPS** (72.61.5.208, tailnet `shieldstone-us`) | dream-api (PM2 :8001, Caddy), OpenBrain, Mission Driven's production Twenty (crm.mission-driven.ai — NEVER touch) | Postgres 16 (Docker), job worker with drivers, CI/CD deploy target |
| **UK VPS** (srv1476276, tailnet `shieldstone-uk-avery`) | Hermes v0.16.0 (avery + execs — frozen, another workstream), Twenty at dreamcre.co (`/opt/twenty-crm`), bd-edit | `dream` Hermes profile; Twenty hardening (pin tag, Google OAuth, pg_dump cron); swapfile (neither box has swap; UK ~3.4GB free) |

Connectivity: app worker (US) → tailnet SSH → `hermes -p dream -z '<HermesInvoke JSON>'` (UK); results back via `ssh cat` (no scp on UK box). v0.16 has no HTTP invoke endpoint. DREAM-agent → Twenty via its built-in MCP server (`https://dreamcre.co/mcp`) and role-scoped API key. DREAM-agent → OpenBrain via MCP over tailnet.

## 6. Phases

Working pattern every phase: full suite green (422+) → `tsc --noEmit` + build → commit/push → VPS timestamped backup → deploy → live-verify with minted token (`docs/HANDOFF_2026-07-12.md`). Each phase ships live-verified before the next.

### Phase 0 — Evaluation + decision gate (mostly DONE)
- ~~Twenty instance~~ (exists: dreamcre.co). ~~CRM diff~~ (`EVAL_2026-08_CRM_DIFF.md`). Checklist written (`EVAL_2026-08_DREAM_TOUR.md`).
- REMAINING: Evan's two spins + decision-gate call; Chuck sync on what's configured; dreamcre.co credentials → authenticated walkthrough + role-scoped API key.
- No-regrets now (CC): pin the Twenty image tag (runs `:latest` = silent 5-version jumps), nightly pg_dump + off-box copy, Google OAuth app for email sync, verify webhook filtering in UI, UK swapfile.

### Phase 1 — Full auth + RBAC (CC + CX)
Build `backend/WAVE_F_FULL_AUTH_DESIGN.md` on SQLite first (its §7 migration path): lockout, revocable sessions, reset/invite flows (thin SMTP mailer), DB allowlist union, role column admin|analyst|viewer with `require_role` — analysts write own deals (activate `DREAM_STRICT_OWNERSHIP` for writes only; reads stay everyone-sees-all), admin = user mgmt/driver selection/delete. Pull-forward CI-lite (GitHub Actions: pytest + tsc/build on every PR). CX tickets: login page, reset/invite landing, `/admin/users`.
Verify: 403 matrix green; a REAL second analyst invited end-to-end live; oracles byte-identical.

### Phase 2 — Postgres (CC)
`backend/store/WAVE_F_POSTGRES_DESIGN.md` extended to all four stores behind `DREAM_DB_BACKEND=sqlite|postgres`; Postgres 16 Docker (own volume, local bind); psycopg confined to `store/` by guard test; dual-backend parametrized tests; idempotent migration script; SQLite kept as one-cycle rollback; nightly pg_dump starts immediately.
Verify: Esplanade persist/reload byte-identical; live flip.

### Phase 3 — Push-button agentic underwriting (CC bridge + CX UI)
**3.0 Driver abstraction first:** `backend/agent/drivers/` protocol `start/poll/fetch_results/cancel`. KimiDriver = refactor of today's in-process path (zero behavior change; PERMANENT fallback). HermesDriver primary; OpenRouterDriver stub. Results contract for ALL drivers: driver output is narrative/extraction/claims ONLY; the app re-runs wave0 validation + the deterministic engine on returned spec inputs; driver numeric claims render at CP-1 as cross-check flags (blindness invariant applied to the app boundary).
**3.1 HermesDriver spike (short, low-risk):** create `dream` profile from `shieldstone-base` → SOUL from the v5 orchestrator design (DREAM reviews and gates, never authors deal content — lesson 162) → prove app-worker → tailnet invoke → six-phase run (Hermes sub-agents; Hyperagent workers optional per phase via the courier rules: identity prefixes 146/147, published/binary transport 166, budget caps 173) → artifacts back → AWAITING_CP1. Success: two consecutive unattended Esplanade runs to CP-1, engine-verified IRR 0.2251. Pivot: OpenRouterDriver behind the same interface.
**3.2 Productionize:** job state machine QUEUED→SUBMITTING→RUNNING(phase,round)→COLLECTING→VERIFYING(engine re-run)→AWAITING_CP1 (+TIMED_OUT/STALLED/FAILED/FALLBACK_QUEUED); watchdog with real cancel (our runtime); 3-round correction loop with disputed-fragments packages (94), then CP-1 escalation flag with both positions; run ledger per delegation (111) — phase, model, tokens where measurable, outcome; Hyperagent credit ledger + governors for worker calls only.
**3.3 CX tickets:** run button + cost/governor modal; progress panel; CP-1 review upgrade (claims vs engine values, gate receipts, escalation flags); admin runs ledger.
**3.4 Leg 3 wiring:** OpenBrain MCP into the `dream` profile; AgentMail mailbox dream@shieldstone.co (AUDIT FIRST per global third-party rule) feeding the existing `backend/jobs/HERMES_INTAKE_SEAM.md` seam. Memory rule 98 applies: DREAM's memories hold doctrine and deal facts, never live-system state.
Verify: push-button Esplanade by a non-Evan analyst from a non-Z13 machine; forced-stall → automatic Kimi fallback delivers.

### Phase 4 — CRM integration, Branch A (CC backend + CX frontend) — pending formal gate call
- Twenty owns companies/people/sourcing pipeline (Target→Contacted→OM received→Underwriting→LOI→Dead/Won), email capture, team permissions (object+field level; row-level is paywalled — plan everyone-sees-all).
- The weld: `backend/adapters/twenty_client.py` (GraphQL, role-scoped key in env); deal↔opportunity link table; DREAM headline metrics write back to the opportunity; webhook receiver (HMAC-verified) for stage changes — stage hits "Underwriting" → deal created/linked; deep links both ways; the app's CRM rail becomes Twenty-backed; one-time crm_store export into Twenty, crm_store read-only legacy.
- DREAM-the-agent reads/writes the sales book via Twenty's MCP; a Hermes cron covers the shared no-reminders gap (neither system pings due dates).
- AGPL guard: Twenty code NEVER copied into DREAM — API/webhooks + UI inspiration only (audit 2026-07-13). CI grep for Twenty source headers.
- Rate limits: 100 req/min, 60-record batches — incremental sync fine; backfills via import path.
Verify: one real week of Evan's partner outreach lives in Twenty and shows against real deals.

### Phase 5 — Hardening, CI/CD, ops (CC)
Full CI (PG service container, oracle assertions, architectural guards as required checks); CD on tag (dedicated deploy key, release dirs, post-deploy smoke + auto-rollback; pipeline becomes the only writer); secrets rotation (Kimi key + Google client secret — open since July) and 0600 secrets pattern; uptime monitor, restore drills, log rotation, auth rate limits; execute `docs/REPO_SCRUB_PLAN_2026-07-12.md`.
Verify: tagged deploy ships; deliberate smoke failure rolls back.

## 7. Risk register

1. **Hermes six-phase orchestration is unproven at this depth** (v0.16 sub-agent capabilities must carry what Hyperagent's depth limit forbade). Bounded by the spike; fallback chain HermesDriver → KimiDriver; OpenRouterDriver slot ready.
2. **ChatGPT OAuth for unattended volume is a ToS gray area** — same class as the Anthropic ban we honor. Prove the loop, then move automation to OpenRouter (a config flip per profile).
3. **UK box concentration:** Hermes + Twenty + bd-edit + agent runs on 7.8GB/no-swap. Swapfile now; resize trigger = sustained pressure during Phase 3.
4. **Hyperagent worker calls inherit all platform risks** (approval hangs, no cancel/telemetry, non-revocable token — lessons 7–9, 19): per-task use only, budget caps, dedicated workspace, no OAuth apps ever (170).
5. **Twenty as system of record before hardening** = data loss / silent version jump risk. The Phase 0 no-regrets items land before real partner data does.
6. **Codex ticket drift** — every CX ticket carries exact API contract + acceptance criteria; CC reviews against the running app.
7. **Two-chat collision on the UK Hermes install** (this plan adds `dream`; the Ada chat migrates `avery`) — each chat touches only its own profiles.

## 8. Verification map

- P0: Evan's filled checklist + decision doc + authenticated Twenty walkthrough.
- P1: 403 matrix; real analyst end-to-end; oracles.
- P2: dual-backend suite; live PG flip; rollback retained.
- P3: 2 consecutive unattended Esplanade runs to CP-1 (IRR 0.2251); forced-stall fallback drill.
- P4: one real week of sales-book activity against real deals.
- P5: tagged deploy + rollback drill; rotated secrets.

## 9. Critical files

- `backend/WAVE_F_FULL_AUTH_DESIGN.md` · `backend/store/WAVE_F_POSTGRES_DESIGN.md` (build as written)
- `backend/routers/jobs.py` + `backend/jobs/` (state machine + driver seam) · `backend/jobs/HERMES_INTAKE_SEAM.md`
- `backend/store/crm_store.py` (Phase 4 export point)
- `docs/EVAL_2026-08_CRM_DIFF.md` · `docs/EVAL_2026-08_DREAM_TOUR.md` · `docs/AGENTIC_LESSONS_2026-08-31.md` (builder-only; never in DREAM-agent corpus)
- dream-underwrite repo: `ARCHITECTURE-V5-HYPERAGENT.md` (six-phase payload), `fastpath/underwrite-spec.schema.json`, `fastpath/agent-contracts.md`, `deployments/gates/REGISTRY.json` (reusable assets — lesson 144)
