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
  - Status column for every unit (Vacant/Model/Notice/Down/Occupied).
  - Backfill missing SF from CoStar; cite the source. Never leave SF blank.
  - Renovation cohort split (SLV/GLD/RENO suffix, or rent-outlier detection).
  - Reconcile RR-implied GPR vs T-12 GPR within 5%; explain any gap (snapshot date / mix).
- **Output schema:** `{ unit_mix: [...], cells: [{cell,value,source,phase:2}], qa: {rr_vs_t12_gpr_gap_pct:number} }`

## agent-assumptions — pricing / closing / fees / debt / sale

- **Reads:** `templates/field-mapping-<routing>.md` §A-B; `references/13-manual-standards.md` §Fee Structure.
- **Source docs:** broker OM, lender term sheet.
- **Returns slice:** assumptions `cells[]` (cols A-B INPUT cells: B2-B5, B9-B10, B20-B36, B39-B42, B45-B48, B51/B53-B62, B65/B67/B69-B76, B79-B81).
- **Hard rules:**
  - NEVER write FORMULA cells (B6/B7/B8/B11/B14-B17/B52/B66/B68/B82 are formulas).
  - ACQ acquisition fee (B45): 0.5% ($50M+) / 0.75% ($25–50M) / 1.0% (<$25M) — NOT 5% (that's EFB).
  - Run the whisper-bid sanity check as soon as B10 is set (median PPU × units vs price).
  - Flag the formula-audit cells (S40, B66, rows 31-32, row 78) for the orchestrator.
- **Output schema:** `{ cells: [{cell,value,source,phase:3}], qa: {whisper_flag:{...}, formula_audit:[...]} }`

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

## Wave 2 synthesis (orchestrator, sequential — NOT an agent)

Merge the five slices into one `underwrite-spec.json`, then run the calc engine:
1. **Rent tiers (P4):** NOAH detection, HAP-delta optimization, P75 caps → unit-mix W-column cells.
2. **Other income (P5) / OpEx (P7):** from `forensic`/`t12` → U-column cells.
3. **OpEx triangulation (P8):** `marketdata.opex_triangulate` vs UW → flags.
4. **Vacancy curve (P6):** from forensic + comp occupancy → S42/U42… cells.
5. **Property tax (P9):** EFB $0 / ACQ state reassessment → S66–S71 cells (ACQ).
6. **Sizing (P10):** `acq_engine` (ACQ: bridge→refi, agency takeout MIN constraint) or
   `lihtc_engine.BondSizingCalculator` (EFB) → debt cells + `headline_metrics`.
7. **Exit cap (ACQ):** `ExitCapTriangulator` 3-method, take HIGHEST.
8. Write `headline_metrics` (NOI/DSCR series, IRR/EM/CoC or bond/coverage) — the CP-2 oracle.

→ **CP-1**: present the full spec + `headline_metrics` + every QA gate ✅/❌ for the one analytical glance.
