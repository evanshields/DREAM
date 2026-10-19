# DREAM v3.0 — Product Requirements Document

**Status:** Approved (Evan Shields, 2026-06-05) · **Owner:** Evan Shields · **Author:** Claude Code
**Supersedes:** DreamVision_PRD_v3 (Domain-1 framing carried forward; see §11)
**Companion recon:** [`docs/DREAM_PRD_RECON.md`](./DREAM_PRD_RECON.md) (read-only "what exists where")

---

## 1. Summary

**DREAM** is the agentic framework for **all D**evelopment, **R**eal-**E**state, and **A**sset-**M**anagement
analytical work at Shieldstone. The multifamily underwriter is the **first application** of DREAM, not
its whole scope. This PRD covers building DREAM v3.0 by **broadening the already-built "EFB
Underwriter" app** into a general acquisition underwriter, adding a server-side chat-bot that runs an
autonomous initial underwrite, productizing the Excel push, and leaving a clean intake seam for a
future Hermes autonomy layer.

We **broaden, we do not rebuild.** The app is real, running code on a VPS with every product-arc step
already wired to an endpoint. The work is the *delta* between EFB-only and the full DREAM vision.

---

## 2. Product arc (Evan-locked, 2026-06-05)

1. **Chat-bot in the app.** User drops all deal docs → DREAM runs a 5–20 min **autonomous initial
   underwrite** (the same 3-wave process Claude Code's "Dream fast path" ran on the Envy deal: 5
   parallel analytical subagents → Python calc engine → openpyxl populate → memo) → produces a **full
   write-up of every assumption + a list of open questions** the user answers to "tune in" the
   underwrite → wraps.
2. **DREAM populates the app** with those assumptions. The user then **tweaks assumptions live and
   runs sensitivities** — instant Python recalculation, *never* an LLM call for recalc.
3. **Push to Excel** — export the app's assumptions onto the Excel Mini Model on demand (the file
   capital partners need to port assumptions into their own models).
4. **Hermes autonomy layer** *(design-only here)* — deals from Drive / email / Slack flow through the
   **same pipeline** and land as the **same deal instance** on the app, as if the user uploaded them.

---

## 3. Locked decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | **Keep the app's Kimi LLM client only.** No Padawan cost-router dependency. | Padawan's router is *design inspiration* (the "deterministic Python owns ~90%, LLM owns the judgment forks" principle), not a build dependency. Kimi already works and is cheap. |
| 2 | **Migrate the app from the UK VPS to the US VPS** (72.61.5.208). | US is now primary infra, co-resident with OpenBrain + the future Shieldstone Hermes → the Hermes intake seam becomes localhost, not cross-VPS. Isolated as Wave A0. |
| 3 | **The `underwrite-spec.json` is the canonical master record;** the app's Pydantic `models.py` is a derived **view**, joined by a tested bidirectional **spec↔models adapter**. | The spec carries every value's **citation** and the **QA safety gates** — the "show your work" audit trail that outward-facing underwriting requires. The model is the clean shape the screen needs. |
| 4 | **Ship Wave A clean and standalone;** fully specify Waves B & C so they start immediately. | Evan wants B & C ASAP; A is the foundation everything dereferences. |

---

## 4. The broaden delta (net-new on top of the built app)

1. EFB-only → **general ACQ** — source the ACQ math from the validated skill engine `acq_engine.py`
   (+ `lihtc_engine.py` for EFB).
2. **Server-side chat-bot fast path** — replicate the skill's 3-wave process as a backend service
   that emits assumptions + open questions written into the app's data model.
3. **One canonical object** — reconcile `models.py` with `underwrite-spec.json` (spec master, model
   view) via a tested adapter.
4. **App → Excel push** — productize `populator.py` (populate + reconcile + identity-check) as an
   on-demand export endpoint.
5. **Hermes intake seam** — leave the seam; do **not** build the runtime.

---

## 5. Verified ground truth (confirmed against live code, 2026-06-05)

### 5.1 The built app — UK VPS `/opt/dream-app`
PM2 `dream-api` (found **stopped**), FastAPI + uvicorn **:8001**, Python 3.13 venv. **Stateless — no
database.** Frontend = a **compiled Vite build only** (no source on the box) and is **not wired into
nginx** (no public route today). `requirements.txt` has openpyxl/pandas/numpy but **not
`numpy_financial`**.

- **`backend/models.py`** — Pydantic, **EFB-shaped**. `DealInputs` wraps `PropertyInputs`,
  `RevenueInputs`, `ExpenseInputs`, `GeneralPartnerInputs`, `CapitalInputs`, `ClosingCostInputs`,
  `BondInputs`, `PropertyTaxInputs`, `ExitInputs`, `WaterfallInputs`. EFB-centric:
  `BondInputs` (A-bond/B-note), `EFBTaxAdvantage`, `exit_cap_rate` is a **direct input** (no
  triangulation), `acquisition_fee_pct` default 0.10, `RevenueInputs` pruned (single `revenue_growth`;
  only `vacancy_yr1`/`vacancy_stable`, **no per-year vacancy curve**).
- **`backend/main.py`** — `GET /api/health`, `GET /api/me` (stub), `POST /api/underwrite` (calls the
  app's **own** `calculations.efb_engine`, *not* the skill engine), `POST /api/validate`
  (`DealValidator` GREEN/AMBER/RED), `POST /api/intake` (pymupdf), `POST /api/agent/chat` (SSE, Kimi),
  `POST /api/agent/memo` (`MemoGenerator`). `flatten_inputs()` converts nested→flat. **Auth disabled**
  (import commented) but `auth.py` implements Google OAuth Bearer verification + `ALLOWED_EMAILS`.
- **`backend/calculations/`** — the app's **own** engine (`efb_engine.py`, `bond_sizing.py`,
  `returns.py` numpy-only, `validator.py`). Separate from the skill engine below.

### 5.2 The skill engine — `.skills/dream-underwrite/engine/` (validated, ~25 tests, Decimal-based)
- **`acq_engine.py`** (conventional value-add) calculators: `SeniorDebtCalculator`,
  `InterestReserveSizer`, `LeaseUpRamp`, `FourTierOptimizer`, `AgencyTakeoutSizer` (refi = **MIN of
  DSCR/LTV/Debt-Yield**), `ExitCapTriangulator` (3-method, **take HIGHEST**), `PropertyTaxCalculator`
  (FL .725 / TX .65 / GA .40), `ACQCashFlowProjector.project()` → `ACQReturnResult` (IRR via
  `numpy_financial`, EM, CoC, dscr_series), `HurdleCalculator`. **Stateless gate functions:**
  `assert_fee_bounds()`→`FeeBoundsResult`, `UnitCountReconciler.reconcile()`→`UnitCountResult`,
  `formula_integrity_check()`→`FormulaAuditResult`.
- **No "run from a dict" entry point** — the caller orchestrates: `SeniorDebtCalculator.build` →
  `ACQCashFlowProjector.project` → `ExitCapTriangulator.triangulate` → `AgencyTakeoutSizer.size` →
  `HurdleCalculator.compute` + the gates.
- **Orchestration-param trap (critical):** reproducing Esplanade ground truth requires
  `servicing_spread=Decimal("0.0116")` and `exit_on_forward_noi=True` — these are *engine knobs*, not
  headline deal inputs, and **must survive the adapter/boundary or recalc silently diverges** from the
  validated result.
- **`lihtc_engine.py`** (EFB/LIHTC): `BondSizingCalculator.size_bonds`, `AMIRentCalculator`, and a
  `DreamAIOrchestrator.execute_workflow(dict)` that is a **minimal stub — NOT the production
  orchestrator** (production = the caller sequence above).
- `numpy_financial.irr` is used by `ACQCashFlowProjector` and two LIHTC calculators; **Decimal**
  everywhere else (a hard serialization boundary vs. the app's float/numpy world).

### 5.3 The skill fast-path contract — `.skills/dream-underwrite/fastpath/`
- **`underwrite-spec.schema.json`** — per-deal master record:
  `meta{deal_name, slug, routing ACQ|EFB, template, mode HITL|HOTL, deal_identity}`,
  `qa{t12_unmapped, rr_vs_t12_gpr_gap_pct, formula_audit[], whisper_flag, fee_bounds (BL-03),
  unit_count (BL-01), reconcile[] (CP-2), gates}`, `cells[]` (flat
  `{cell, value, type, source, phase, input_only}` — **every value with an Excel address + a
  citation**), `headline_metrics` (noi/dscr series, irr, equity_multiple, coc, bond_amount,
  tax_savings_10yr — already carries **both** ACQ and EFB fields), `comps`, `forensic`, `narrative`,
  `memo_vars`.
- **`agent-contracts.md`** — 5 parallel **pure-function** subagents (`agent-t12`, `agent-rentroll`,
  `agent-assumptions`, `agent-comps`, `agent-marketdata`) → JSON slices; then the **Wave-2
  orchestrator (sequential, explicitly NOT an agent)** merges + runs the engine + writes
  headline_metrics → CP-1.
- **`populator.py`** — `populate(spec_path, template_path)` → `WriteReport` (copies the template,
  writes INPUT cells only, **refuses formula cells**, enforces **BL-02 deal-identity / BL-03 fee
  bounds / BL-01 unit-count** blocks, structural-diff guard, PENDING marker). `reconcile()` →
  `[ReconcileRow]` (CP-2 Python↔Excel diff at tiered tolerance; **raises `IdentityMismatchError`**).
  `reconcile_self_render()` (HOTL floor). `deal_identity_check()` (template-fork carryover guard).
  **The gates live in the populator (Excel-write path), NOT in the engine compute path** — the key
  hole the chat-bot service must close (§ Wave A1.6).

### 5.4 The DREAM product repo — `github.com/evanshields/DREAM` (`main`)
`DreamVision_PRD_v3.md` + a `gemini_ui/` Vite + React + TS app (pages Dashboard / DealIntake /
AnalysisView / PipelineBoard) + a `src/` ShadCN component lib. **PR #2 (open)** vendors the skill
engine into `underwriting-engine/`. **No local clone exists** (local `DREAM/docs/` is an
empty scaffold).

### 5.5 Validation oracles
- **Esplanade ACQ ground truth** (`engine/tests/test_acq_esplanade.py`): IRR **0.2251**, EM **2.72**,
  exit value **55,870,669**, CoC-stab **0.0584**.
- **Tolerances:** HEADLINE **0.5%**; **IRR 2% relative** (HEADLINE × 4 — IRR is sensitive); line
  items **2%**.
- **EFB** validated vs. the Rayzor Ranch EFB Mini Model.

---

## 6. Cost-discipline principle

Rote Python owns every mechanical step (~90%); the LLM is reserved for the judgment forks. The engine
computes all `headline_metrics` and all `qa.*` deterministically. The Kimi LLM produces **only**
judgment slices — T-12 forensic narrative, comp curation candidates, assumption rationale, and the
open-questions write-up. **No LLM is ever called to recalculate** (the cardinal rule from the
strategic-guidance doc). `/api/recalc` proves this with a Kimi-mocked-to-raise test and an
import-graph assertion.

---

## 7. Waves → Epics → Acceptance Criteria

### Wave A0 — Ops migration *(independently shippable, has rollback)*
- **A0.1 — Migrate `/opt/dream-app` UK → US VPS (72.61.5.208).**
  *AC:* health + one Esplanade underwrite + OAuth login pass on US; UK instance kept re-startable
  until the US smoke test passes; **one-command rollback documented**; no PM2-name/port/env collision
  with OpenBrain on the US box.
- **A0.2 — First-ever public nginx route for the SPA + re-enable Google OAuth.**
  *AC:* SPA served behind nginx (net-new config, not a copy — there is no route today); OAuth Bearer +
  `ALLOWED_EMAILS` enforced; unauthenticated request to a protected route → 401.

### Wave A1 — Foundation code *(THE FIRST CODING MILESTONE)*
- **A1.1 — Vendor the engine + pin deps.** *AC:* merge PR #2 engine into the backend; **pin
  `numpy-financial`**; the skill's engine + fastpath suites run green in CI against the **unmodified**
  vendored engine.
- **A1.2 — `DealStore` persistence (SQLite-first, Postgres-ready).** The app is stateless today; the
  whole arc needs a deal store. *AC:* a `DealStore` interface (get/put/list by `deal_id`; spec stored
  as an **opaque document**; thin relational index of deal_id/slug/routing/mode/status/owner;
  **optimistic-concurrency version field**); **no module outside `DealStore` imports sqlite3 or builds
  a deal file path** (keeps the skill's filesystem-as-DB pattern out of the server).
- **A1.3 — `engine_boundary` module (the Decimal seam).** *AC:* Decimal confined to engine +
  boundary; uses `Decimal(str(x))` (never `Decimal(float)`); **carries the orchestration params**
  (`servicing_spread`, `exit_on_forward_noi`); an **API-edge** round-trip test reproduces Esplanade
  (exit ≤0.5%, IRR ≤2% rel of 0.2251, EM ≤2% of 2.72).
- **A1.4 — spec↔models adapter (spec-canonical, routing-aware, EFB view first).** *AC:* lossless
  round-trip property test — full-spec byte-identity on **pass-through** fields (no silent drop of
  `qa` / `cells` / `meta.deal_identity`); reverse direction for the view subset; **adapter is
  view-pluggable** so Wave B adds the ACQ view without rewriting the core.
- **A1.5 — `/api/recalc` (instant, no LLM) + repoint `/api/underwrite` at the skill engine via a
  router.** *AC:* a test that mocks the Kimi client **to raise on any call** passes for recalc +
  underwrite; recalc's import graph **excludes** the LLM client module; recalc **P95 < 500ms** (a
  behavioral tripwire — an LLM cannot meet it).
- **A1.6 — Server-side QA-gate harness.** Closes the §5.3 hole. *AC:* `assert_fee_bounds` /
  `UnitCountReconciler` / `deal_identity_check` / `formula_integrity_check` run on the spec at
  **compute time** and populate `qa.*` as **non-collapsible structured response fields** (BL-06);
  skill gate tests reused at the API layer; any RED gate is exposed in the API response, not buried in
  a log.

### Wave B — Broaden EFB → general ACQ
- **B.1 — Extend `models.py` into an ACQ view** (per-year vacancy curve, 3-method exit-cap inputs, ACQ
  fee bounds, market tier / hurdle). *AC:* the adapter's ACQ view is added **without rewriting** the
  adapter core; the round-trip test is extended to ACQ and stays green.
- **B.2 — Broaden `DealValidator`** for ACQ thresholds. *AC:* an ACQ deal validates with the correct
  band; EFB validation unchanged.
- **B.3 — Frontend assumption dashboard + live recalc + sensitivity grid.** Assumptions become
  first-class objects: **named / typed / ranged / benchmarked / provenance-annotated** (per the
  strategic-guidance Part 4). *AC:* each assumption shows value + type + range + benchmark + source;
  edits call `/api/recalc` and update `headline_metrics` **with no LLM call**; the sensitivity grid is
  N Python-computed recalcs.
- **B.4 — Routing layer** ACQ → `acq_engine` / EFB → `lihtc_engine`. *AC:* the route is decided from
  `meta.routing`; wrong-route inputs are rejected, never silently mis-computed.

### Wave C — Chat-bot fast-path service *(headline feature)*
> **C-v1 = sequential, ACQ-only, HITL.** The 5 slices run **sequentially** in the Wave-2 orchestrator
> (which is already sequential and not an agent), **ACQ route only** (validated by Esplanade), **HITL
> only** (always stops at CP-1). Parallel fan-out is deferred to Wave F. Reuse the existing
> `/api/intake` and `MemoGenerator`. The LLM produces **only** judgment slices; all `headline_metrics`
> + `qa.*` come from Python.

- **C.1 — Long-job system + state machine** (submit / status / **cancel**; HITL pause-resume for
  Wave-0 routing ambiguity — "ask once and stop"). *AC:* kill switch cancels mid-run; **idempotent
  intake** (no duplicate deal instance, no double LLM spend); the job parks on ambiguous routing and
  resumes on the user's answer.
- **C.2 — Wave-0 routing + sequential analytical slices.** *AC:* each slice validates against
  `underwrite-spec.schema.json` **before merge** (an invalid slice fails the job, it is not silently
  coerced); deterministic values are never LLM-sourced.
- **C.3 — Wave-2 synthesis + engine + spec emission + open-questions ledger** (the documented caller
  sequence, **not** the `lihtc` stub). *AC:* an Esplanade end-to-end run reproduces ground truth within
  tolerances; every LLM-inferred cell is enumerated as an open question; a zero-open-question HOTL run
  warns (over-confidence flag).
- **C.4 — Populate the app deal instance + memo** (reuse `MemoGenerator`). *AC:* a completed run yields
  a tweakable deal instance with **all gates surfaced**.
- **C.5 — Audit log (the assumption ledger).** *AC:* an append-only record of every LLM call, gate
  result, and spec mutation; readable per deal.
- **HOTL unlock gate (cross-epic):** HOTL stays **OFF** until all four hold — (1) the gate harness
  blocks HOTL on any RED; (2) `reconcile_self_render()` passes (BL-05 HOTL floor); (3) the golden-deal
  (Esplanade) reproduction passes; (4) the audit log + kill switch are present.

### Wave D — App → Excel push *(productize `populator.py`)*
- **D.1 — Export endpoint** wrapping `populate()` / `reconcile()` / `deal_identity_check()` on a
  user-selected Mini Model template. *AC:* writes INPUT cells only, refuses formula cells; BL-01/02/03
  refusals are returned to the UI; PENDING EXCEL RECALC marker is set.
- **D.2 — Surface CP-2 reconciliation in the UI** (tiered tol 0.5% / 2%). *AC:* `IdentityMismatchError`
  on a mismatched ground-truth workbook **blocks** reconcile and is shown, not swallowed.

### Wave E — Hermes intake *(DESIGN-ONLY — do not build the runtime)*
- **E.1 — Normalized "deal source" envelope** that lands as the **same deal instance** via `DealStore`.
  *AC:* documented seam only; the envelope schema is reviewed against C.1's intake and mirrors the
  Shieldstone Hermes `HermesInvoke` / `HermesResult` contract ([[reference_shieldstone-hermes]]).

### Wave F — Cost-opt + multi-domain hooks + parallel fan-out
- **F.1 — Parallelize the C.2 slices** (latency only). *AC:* parallel output == sequential output.
- **F.2 — Postgres `DealStore` implementation.** *AC:* the swap is config-only; no business-logic
  change.
- **F.3 — D2/D3/D4 attachment hooks** (IR / Asset Mgmt / Construction, per the DreamVision 4-domain
  map) + sensitivity / scenario polish. *(Cost router explicitly deferred — Kimi-only is locked.)*

---

## 8. Sharpest risks (named to their mitigation)

1. **Adapter built tight to EFB → forced rewrite in B.1.** → spec-canonical, routing-aware,
   view-pluggable from A1.4.
2. **Orchestration params dropped at the boundary → recalc silently diverges from validated truth.** →
   A1.3 boundary carries `servicing_spread` + `exit_on_forward_noi`; API-edge Esplanade test.
3. **BL gates never fire in the chat-bot path** (they live in the populator). → A1.6 server-side gate
   harness before any HOTL.
4. **Migration bundled with new subsystems → an ops slip blocks all code.** → A0 (ops, with rollback)
   split from A1 (code).
5. **Wave C ported as a parallel Claude-Code-style fan-out → no server primitive exists.** → C-v1
   sequential / ACQ / HITL; parallel deferred to F.

---

## 9. Reuse manifest

**Reused as-is (do NOT rebuild — call them):** `acq_engine.py`, `lihtc_engine.py`, `populator.py`,
`underwrite-spec.schema.json`, the existing `/api/intake`, `/api/validate`, `MemoGenerator`, and the
`kimi_client`.

**New in Wave A:** `backend/store/deal_store.py` (DealStore + SQLite impl), `backend/engine_boundary.py`
(Decimal seam + orchestration-param carrier), `backend/adapters/spec_models.py` (bidirectional
adapter), `backend/qa_gates.py` (server-side gate harness), `backend/tests/` (Esplanade API-edge test,
adapter round-trip property test, no-LLM recalc test, gate-harness tests), `POST /api/recalc` +
routing layer in `main.py`, re-enabled `auth.py` dependency, pinned `numpy-financial`.

---

## 10. Verification (Wave A)

1. **Engine integrity:** `pytest` the vendored engine + fastpath suites — all green, engine unchanged.
2. **ACQ math through the API:** `POST /api/underwrite` (routing=ACQ, Esplanade inputs, passing
   `servicing_spread` / `exit_on_forward_noi`) → IRR ≤2% rel of 0.2251, EM ≤2% of 2.72, exit ≤0.5% of
   55,870,669, DSCR series ≤2%/yr.
3. **Adapter lossless:** round-trip property test green (full-spec byte-identity on pass-through;
   reverse direction on the view subset).
4. **No-LLM recalc:** Kimi-mocked-to-raise test passes for `/api/recalc` + `/api/underwrite`; recalc
   import graph excludes the LLM client; recalc P95 < 500ms.
5. **Gates fire server-side:** ACQ fee = 0.05 → `fee_bounds.ok=false`; unit count >2% off → blocked;
   mismatched ground-truth workbook → `IdentityMismatchError` — all surfaced in the API response.
6. **Ops smoke test on US VPS:** health + Esplanade underwrite + OAuth login pass; rollback verified.

---

## 11. Carry-forward from DreamVision_PRD_v3 (not discarded)

DreamVision framed DREAM.AI as a **4-domain super-app** (D1 Acquisitions, D2 IR/Capital, D3 Asset
Mgmt, D4 Construction/Dev) — which matches today's "DREAM = all Dev/RE/AM" definition, with the
underwriter as D1. The DreamVision **data-model entities** (Deal → Property/Documents/Analyses/Stage;
Analysis → ExtractedData/Scores/Recommendation/Reports/UserOverrides) and the **assumption-dashboard /
Excel-export** requirements are carried forward into Waves B/D and the multi-domain hooks in F.3. The
strategic-guidance doc's **Part 4 "Interactive Assumption Tweaking"** (Python recalc, LLM only for
async insight) is the spine of B.3 and the §6 cost-discipline rule.

---

## 12. Out of scope (this PRD)

- The **Hermes runtime** (Wave E is design-only — the intake seam only).
- The **Padawan cost-router** (Kimi-only is locked; router deferred indefinitely).
- **Postgres** (SQLite-first; Postgres is F.2, a config-only swap).
- **Parallel agent fan-out** (C-v1 is sequential; parallel is F.1).
- **D2/D3/D4 domain apps** (only the attachment *hooks* are in F.3).

---

## 13. Next step

Convert this PRD into a `/goal` and begin Wave A, starting with **A1.1** (clone repo + vendor engine)
and **A1.3** (the `engine_boundary` Decimal seam), since A1.4 / A1.5 / A1.6 all depend on the seam.
Waves B and C are fully specified above so they start the moment A is green.
