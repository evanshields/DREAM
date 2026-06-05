# Dream Fast-Path — Wave 1 Agent Contracts

The five parallel analytical subagents dispatched concurrently in Wave 1. Each is a **pure
function**: deal-package paths + ONE scoped reference + a strict output slice → JSON only.
Agents write nothing to the workbook and share no state; the orchestrator (Wave 2) merges the
five slices and runs the calc engine.

Dispatch all five in a single message (`.skills/dispatching-parallel-agents/` pattern), or as
`parallel(...)` stage 1 of the Workflow definition. Each agent's output slice is validated
against `underwrite-spec.schema.json` before synthesis.

Routing (ACQ vs EFB) is decided in **Wave 0** before dispatch, so each agent knows which
template/fee/tax logic applies. If routing is ambiguous, Wave 0 asks once and stops — agents
never guess.

---

## agent-t12 — T-12 spread + forensic

- **Reads:** `references/11-data-extraction.md` §T-12 + §T-12 Forensic; `templates/field-mapping-<routing>.md` §Operating Expenses.
- **Source docs:** Seller T-12 (.xlsx). Aged receivables if present.
- **Returns slice:** `forensic{}` + the OpEx `cells[]` (S-column T-12 actuals) + `qa.t12_unmapped`.
- **Hard rules:**
  - Parse with openpyxl FIRST; verify 12 monthly columns (or set annual-only flag).
  - Build an EXPLICIT row-keyed mapping dict; NEVER fuzzy-match. `t12_unmapped` MUST be 0 to pass.
  - RUBS trap: Water/Electric/Trash/Pest reimbursements → Utility Reimbursements, NOT Other Income.
  - Deliver the forensic block unprompted: T-12/T-6/T-3 annualized NOI + delta row, vacancy trend, concessions %, loss-to-lease, bad debt %, expense anomalies (lines dropping to $0 mid-year), lease-up flag, 3–5 takeaways.
  - Verify col-O category rollups tie to source subtotals within $1.
- **Output schema:** `{ forensic: {...}, cells: [{cell,value,source,phase:1}], qa: {t12_unmapped:int} }`

## agent-rentroll — rent roll spread + unit mix

- **Reads:** `references/11-data-extraction.md` §Rent Roll.
- **Source docs:** Seller rent roll (.xlsx/PDF/CSV); CoStar Property Summary for SF backfill.
- **Returns slice:** unit-mix `cells[]` (R/S/T/U/W per bedroom×tier) + `qa.rr_vs_t12_gpr_gap_pct`.
- **Hard rules:**
  - Unit-detail rows only (skip charge-detail rows, storage/office/model units).
  - Status column for every unit (Vacant/Model/Notice/Down/Occupied) AND a use-type/segment per row.
  - **Unit count via `acq_engine.UnitCountReconciler` (BL-01/09):** classify by status AND use-type,
    reconcile vs a 2nd source (CoStar/ISG) AND the roll's own summary tab; honor explicit user
    exclusions ("just the EB5 multifamily part"). Emit `qa.unit_count`. BLOCK on >2% off the 2nd
    source / a detected non-residential segment / an exclusion violation. No raw pandas count.
  - Backfill missing SF from CoStar; cite the source. Never leave SF blank.
  - Renovation cohort split (SLV/GLD/RENO suffix, or rent-outlier detection).
  - Reconcile RR-implied GPR vs T-12 GPR within 5%; explain any gap (snapshot date / mix).
- **Output schema:** `{ unit_mix: [...], cells: [{cell,value,source,phase:2}], qa: {rr_vs_t12_gpr_gap_pct:number, unit_count:{counted,summary_tab,second_source,excluded_segments,blocked,single_source_warning,reasons}} }`

## agent-assumptions — pricing / closing / fees / debt / sale

- **Reads:** `templates/field-mapping-<routing>.md` §A-B; `references/13-manual-standards.md` §Fee Structure.
- **Source docs:** broker OM, lender term sheet.
- **Returns slice:** assumptions `cells[]` (cols A-B INPUT cells: B2-B5, B9-B10, B20-B36, B39-B42, B45-B48, B51/B53-B62, B65/B67/B69-B76, B79-B81).
- **Hard rules:**
  - NEVER write FORMULA cells (B6/B7/B8/B11/B14-B17/B52/B66/B68/B82 are formulas).
  - **ACQ acquisition fee B45 via `acq_engine.assert_fee_bounds` (BL-03):** 0.5% ($50M+) / 0.75%
    ($25–50M) / 1.0% (<$25M). FAIL on 0.05 (the EFB/Esplanade sentinel) or outside [0.005, 0.01] —
    not just a warning. Emit `qa.fee_bounds`; the populator refuses to write a failing fee without
    an override note. Read every fee/cost cell (B45 acq, dev fee, COI) by address.
  - Run the whisper-bid sanity check as soon as B10 is set (median PPU × units vs price).
  - **Read + report the 5 formula-audit cells (S40, B66, B67, rows 31-32, row 78) for
    `formula_integrity_check` (BL-07):** supply the actual formula strings (and a `row78_patch`
    repoint if the column layout is known) so the orchestrator emits a named verdict per cell.
- **Output schema:** `{ cells: [{cell,value,source,phase:3}], qa: {whisper_flag:{...}, fee_bounds:{value,ok,is_sentinel,override,reason}, formula_audit:[...]} }`

## agent-comps — sales / rent / construction pipeline

- **Reads:** `references/10-comps-build.md`; `references/11-data-extraction.md` §Comps.
- **Source docs:** CoStar Sales Comps, Rent Comps, Full UW Report (Construction section).
- **Returns slice:** `comps{ sales[], rent[], pipeline[], median_ppu }`.
- **Hard rules:**
  - Sales: Sold + valid price/units/SF; recency-weighted; present ranked candidates (curation is human at CP-1, not auto-write).
  - Rent comps by BR with P50/P75/Max; skip the subject's own CoStar row.
  - Construction pipeline: state-filtered; run the template-fork carryover check (no out-of-state leftovers — this bit Esplanade/Aviara).
  - Compute median PPU for the whisper check.
- **Output schema:** `{ comps: {sales:[...], rent:[...], pipeline:[...], median_ppu:number} }`

## agent-marketdata — FMR / SAFMR / LIHTC / OpEx triangulation

- **Reads:** `references/00-api-reference.md`.
- **Source docs:** none (county/state/zip from the package).
- **Returns slice:** `marketdata{ fmr, safmr, lihtc_table, opex_triangulate[], freshness }`.
- **Hard rules:**
  - Pull from the Mission Driven REST API (`https://rent-mcp.shieldstone.co/api/v1/*`, Bearer token from `.secrets-vps.local`). Works headlessly via curl/CLI.
  - SAFMR metros (DFW, Houston, etc.): prefer `/safmr` (ZIP) over `/fmr` (county).
  - OpEx: always pass `program=conventional` for ACQ; capture `binding_floor.citation` per line item.
  - Stamp `/freshness` into `meta.freshness`.
  - Every value carries its API `citation` field as the `source`.
- **Output schema:** `{ marketdata: {...}, meta: {freshness:{...}} }`

---

## Wave 0 durable state (orchestrator — BL-17)

Before dispatch, the orchestrator captures the three BLOCKING critical inputs (purchase price, hold,
exit cap) into `meta.critical_inputs` and a sibling `underwrite-state.json`
([fastpath/state_ledger.py](.skills/dream-underwrite/fastpath/state_ledger.py)): if any is missing,
STOP and ask — do not dispatch agents that will discover the gap mid-run. As each phase completes the
orchestrator calls `record_phase`; as each source is parsed it calls `record_source` (path +
fingerprint + extracted summary). On a restart, `load_state` + `source_is_fresh` skip re-parsing
unchanged sources and `next_phase()` resumes where the run left off — eliminating the container-restart
re-parse waste. The ledger is the resume file; it does not replace the spec or the Claude Log.

## Wave 2 synthesis (orchestrator, sequential — NOT an agent)

Merge the five slices into one `underwrite-spec.json`, then run the calc engine:
1. **Rent tiers + NOAH/EFB route (P4 — BL-04):** CALL `acq_engine.FourTierOptimizer.allocate(units, tier_shares, tier_ceilings)` to build the market-max GPR mix → unit-mix W-column cells; emit `headline_metrics.tier_allocation` (allocations[], gpr, pure_market_gpr, gpr_delta, gpr_delta_pct, tier_targets — field names mirror the return dict). Then CALL `acq_engine.detect_noah(inplace_by_bedroom, ami80_ceiling_by_bedroom)` (in-place vs 85% of the 80%-AMI ceiling, per bedroom) and `acq_engine.build_efb_route_signal(noah, hurdle, levered_irr, exemption_annual_tax)`; emit `meta.efb_route_signal`. **When the conventional case FAILS hurdles AND NOAH+exemption fire, `efb_recommended=true` and `stop_at_cp1=true` — STOP at CP-1 for a human glance; do NOT build the EFB model (locked Evan 2026-06-05).**
2. **Other income (P5) / OpEx (P7):** from `forensic`/`t12` → U-column cells. **RUBS / Utility Reimbursements (S54) gate (BL-16):** CALL `acq_engine.rubs_sign_gate(reimbursement_value, uw_utility_expense, t12_reimbursement, t12_utility_expense)`; emit `qa.rubs_sign`. ok==false (positive S54, or recovery jump > 15pp vs T-12 with no justification) → populator refuses S54.
3. **OpEx triangulation (P8):** `marketdata.opex_triangulate` vs UW → flags.
4. **Vacancy curve + lease-up ramp (P6 — BL-12):** feed the forensic vacancy + concession curves (from `agent-t12`) into `acq_engine.LeaseUpRamp.noi_series(stabilized_noi, stabilized_egi, vacancy_curve, concession_curve, ...)` instead of a flat 0.62/0.85/1.0 assumption; the returned series is the NOI fed to the projector. Emit `headline_metrics.lease_up_ramp` (noi_series + the vacancy_curve/concession_curve it consumed + stabilizes_year + basis) so the memo can show WHY Year-1 NOI is below stabilized. → S42/U42… cells.
5. **Property tax (P9):** EFB $0 / ACQ state reassessment → S66–S71 cells (ACQ). With `agent-marketdata` county method + market-derived assessed value, basis='county-method'; else the flat `PropertyTaxCalculator.STATE_RATIO` default (basis='flat-ratio'). Emit `headline_metrics.property_tax_range` (low/high/point, ratio_used, assessed_value, exemption_delta when efb_route_signal previews EFB).
6. **Sizing + interest reserve (P10 — BL-11):** `acq_engine` (ACQ: bridge→refi, agency takeout MIN constraint) or `lihtc_engine.BondSizingCalculator` (EFB) → debt cells + `headline_metrics`. CALL `acq_engine.InterestReserveSizer.size(noi_series, debt_service, dscr_floor, buffer)`; **fund the sized reserve from sources (adds to equity/TPC)** and pass the result to `acq_engine.reserve_adjusted_dscr(raw_dscr, reserve)` so ramp-year DSCR is NET of reserve draws (realistic Y1, not 0.41–0.77x). Emit `headline_metrics.interest_reserve`. **GATE: a stabilized deal with no shortfall years (Esplanade) gets reserve_sized=0 and an UNCHANGED DSCR series — the ground-truth result is unaffected.**
7. **Exit cap (ACQ) + gate (BL-10):** `ExitCapTriangulator` 3-method, take HIGHEST; then CALL `acq_engine.exit_cap_gate(result, b79_value)` to assert the value staged for B79 == the highest method and ≥2 methods are documented. Emit `qa.exit_cap_gate`; ok==false blocks B79.
7b. **LTV gate (BL-15):** CALL `acq_engine.ltv_gate(target_ltv, purchase_price, senior_loan, b52_formula, b66_formula)` — assert computed senior LTV ties to target and B52/B66 read as formulas (=B51*B10 not overwritten by a literal). Emit `qa.ltv_gate`; ok==false blocks B51/B67.
8. **Formula audit (BL-07):** run `acq_engine.formula_integrity_check` over the read formula strings;
   emit a named PASS/PATCH verdict per cell into `qa.formula_audit`. S40 + row-78 auto-patch entries
   carry `applied=false` until the printed patch is human-confirmed (then `applied=true`).
9. Write `headline_metrics` (NOI/DSCR series, IRR/EM/CoC or bond/coverage) — the CP-2 oracle.
10. **Reprice signal (P-end — BL-19, ACQ):** after `HurdleCalculator.compute` and the FINAL realistic
    returns are in (i.e. AFTER step-6 interest-reserve wiring — reserve-covered ramp years must already
    be reflected in noi_series/equity, or the solve clears the wrong price), run
    `acq_engine.RepriceSolver().solve(...)` when `HurdleResult.recommendation` is REQUEST REPRICING/PASS
    (or levered IRR < adjusted_hurdle). Pass a `price_to_inputs(price)` closure that re-sizes equity +
    bridge/refi from a trial B10 and returns `ACQCashFlowProjector.project` kwargs. Stage the result
    into `headline_metrics.reprice`. ADVISORY ONLY — never auto-writes B10; surfaces at CP-3 as the
    "request repricing" ask (Envy: clears ~$56–57M vs the $74–75M ask).

**CP-2 (Wave 3) reconcile is identity-gated (BL-05):** run `deal_identity_check` on the ground-truth
workbook FIRST; if it fails, `reconcile()` raises and the parent escalates the fork — never a
transcript comparison. With no valid external ground truth, use `reconcile_self_render()` against the
populator's own openpyxl render (HOTL floor; catches populator not engine-logic bugs).

→ **CP-1**: present the full spec + `headline_metrics` + every QA gate ✅/❌ (incl. `unit_count`,
`fee_bounds`, the 5 named formula verdicts, `deal_identity`, `exit_cap_gate`, `ltv_gate`,
`rubs_sign`, and `meta.efb_route_signal` when `efb_recommended=true`) for the one analytical glance —
gates are non-collapsible (BL-06): each surfaces here, no bulk-write that hides them. **BL-04: an
`efb_recommended=true` signal HALTS the fast path at CP-1 (stop_at_cp1 is always true) — the engine
never auto-builds the EFB four-tier; a human flips routing here or the run finishes as ACQ.**
