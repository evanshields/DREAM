# Shieldstone ACQ Mini Model: Field Mapping Guide

> **Status: VERIFIED 2026-06-03** against the Resia Rayzor Ranch ACQ Mini Model (5.04.26)
> exemplar. Every Pro Forma cell below was read directly from that workbook with openpyxl
> (formulas preserved). Blue-text inputs and black-text formulas are distinguished per cell.
> This is the populator contract for the Dream fast-path openpyxl writer — write only the
> cells marked **INPUT**; never touch cells marked **FORMULA**.

---

## Overview

The Shieldstone ACQ Mini Model (also called the Shieldstone Flex Model) is a 12-sheet Excel workbook used for conventional value-add and core-plus multifamily acquisitions. It shares structural DNA with the EFB Mini Model but differs in:

- Tax treatment (state-specific reassessment, not $0 exemption)
- Fee structure (0.5–1.0% acquisition vs. 5% EFB)
- Return metrics (IRR, EM, CoC populated vs. bond DSCR for EFB)
- Debt structure (bridge-to-agency or bridge-to-HUD vs. EFB bonds)

Blue-text cells are inputs; black-text cells are formulas, never overwrite formulas.

---

## Pre-Population Formula Audit (REQUIRED at Phase 3)

The ACQ Mini Model was forked from the same scaffold as the EFB Mini Model and inherits the same 5 known formula bugs. Per Universal Rule 8, the skill MUST audit these cells BEFORE populating any input that depends on them. Audit procedure and expected formulas are identical to the EFB version — see [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md) §Pre-Population Formula Audit. The same 5 bug-prone cells apply: **S40, B66, B67, rows 31-32, row 78**.

**BL-07 enforcement:** `acq_engine.formula_integrity_check` emits a **named PASS/PATCH verdict for all 5 cells EVERY run**. **S40 (`=U36`→`=U36*12`) and row 78 (bridge→refi DSCR pointer) AUTO-PATCH** (printed patch + one-line human confirm → populator applies via `applied=true`); B66/B67/rows 31-32 are flag-only. Only place the skill mutates black-text formula cells.

**Esplanade ACQ 2026-05-15:** All 5 bugs present in the Rayzor-derived ACQ template. S40 understated Other Income by ~$1.5M cumulative. Row 78 zeroed Senior DSCR from Year 3+ (bridge-pointer never switched to refi). Rows 31-32 mis-thresholded refi P+I (B70 treated as absolute year). All 5 patches applied with user confirmation pre-Phase-3.

Two additional bug candidates surfaced in Phase 10 that may belong in the catalog (pending 2nd-deal confirmation per the leanness 2-deal rule):
- Row 79 (Aggregate DSCR): missing refi principal in denominator
- Refi P+I formulas: use FULLY amortizing payment, not IO-period interest-only

---

## 12-Sheet Structure

The workbook contains the following sheets:

| # | Sheet Name | Purpose |
|---|---|---|
| 1 | **Claude Log** | Audit trail of all model edits made by Claude. Phase-by-phase notes. |
| 2 | **Rent Comps Analysis** | Curated rent comp analytics, feeds the per-BR market read |
| 3 | **Seller Ins Est** | Seller-provided insurance estimate; informs Year 1 pro forma insurance |
| 4 | **Seller RR** | Seller-provided rent roll (verbatim paste from broker package) |
| 5 | **Seller T-12** | Seller-provided T-12 (verbatim paste from broker package) |
| 6 | **T-12 Inputs** | Cleaned T-12 with model-category mapping (Phase 1 destination) |
| 7 | **RR Inputs** | Cleaned rent roll with Status column (Phase 2 destination) |
| 8 | **Pro Forma** | **The model itself.** Assumptions cols A–B, P&L cols D–P, unit mix cols R–Z, OpEx cols R–AC |
| 9 | **Comps** | Comps tab, 16 sales, 10+ rent comps, per-BR breakout (Phase 11a destination) |
| 10 | **UW Snapshot** | Phase 11b finalization, headline metrics, T-12/T-6/T-3 reconciliation, sanity check |
| 11 | **Checks** | Internal sanity check formulas (Sources = Uses, DSCR floors, ratio bounds) |
| 12 | **Loom Script** | Pre-formatted script for recording a Loom walkthrough of the model |

---

## Phase 1: T-12 Inputs Sheet

T-12 spread destination. Per the legacy skill source:

- T-12 Inputs sheet, columns A and B-M (12 monthly values)
- Column A: line item labels (must match model categories)
- Column N: reported total
- Column O: SUMIFS-extension formulas (filled in Phase 1)

Critical category labels in Column A:
- `Gross Potential Rent`, `Vacancy`, `Concessions`, `Loss to Lease`, `Bad Debt/Collections`, `Other Income`
- `Management Fee`, `Payroll & Personnel`, `General & Administrative`, `Marketing`, `Repairs & Maintenance`, `Turnover`, `Contract Services`, `Utilities`, `Utility Reimbursements`, `Property Taxes`, `Insurance`, `Replacement Reserves`
- Use `"x"` for subtotals / section headers / non-underwritten lines

Critical SUMIFS extension: after writing T-12, extend Model Inputs SUMIFS range on H43:H54 to cover the full written range (e.g., O5:O309).

---

## Phase 2: RR Inputs Sheet

Rent roll spread destination. Paste verbatim at A1 with the additional Status column added (Vacant / Model / Notice / Down / Occupied).

---

## Phase 3: Pro Forma Sheet (Columns A and B) — VERIFIED CELL MAP

The Pro Forma sheet's assumptions stack lives in columns A (labels) and B (values/formulas).
**INPUT** = blue, write it. **FORMULA** = black, never write.

### Property Info + Going-In (Rows 2–11)

| Cell | Label | Type | Formula / Source |
|---|---|---|---|
| B2 | Asset Name | INPUT | OM |
| B3 | Address | INPUT | OM |
| B4 | City, State & ZIP | INPUT | OM |
| B5 | Year Built | INPUT | OM / tax records |
| B6 | Number of Units | FORMULA | `=S22`. **BL-01 GATE:** guard the S3:S21 unit-mix inputs that feed S22, NOT B6 — populator refuses S-cells when `qa.unit_count.blocked` (244-defect). |
| B7 | Rentable SF | FORMULA | `=T22*S22` |
| B8 | Price Per Unit | FORMULA | `=B10/B6` |
| B9 | Whisper/Asking Price | INPUT | OM |
| B10 | Purchase Price | INPUT | Negotiated (triggers whisper sanity check) |
| B11 | Going-In Cap Rate (T-3) | FORMULA | `=IFERROR(F21/B10,"N/A")` |

### Project-Level Return Metrics (Rows 14–17) — ALL FORMULA (the reconciliation targets)

| Cell | Label | Formula |
|---|---|---|
| B14 | Stabilized Yield on Cost | `=IFERROR(G21/ABS(E71),0)` |
| B15 | **Internal Rate of Return (IRR)** | `=IRR(E77:P77)` |
| B16 | **Equity Multiple** | `=SUMIF(E77:P77,">0",E77:P77)/ABS(SUMIF(E77:P77,"<0",E77:P77))` |
| B17 | **Cash-on-Cash Return** | `=IFERROR(AVERAGEIFS(F81:P81,F1:P1,"<"&B81)," ")` |

These three cells are what the Python engine's IRR / EM / CoC reconcile against at CP-2.

### Closing Costs (Rows 20–36) — all INPUT

| Cell | Label | | Cell | Label |
|---|---|---|---|---|
| B20 | Legal Fees | | B29 | Appraisal |
| B21 | Lender's Counsel | | B30 | Market Study |
| B22 | Loan Closing/Underwriting | | B31 | Reserves & Escrows (header, 0) |
| B23 | Transfer/Recordation Fees | | B32 | Capital Reserve |
| B24 | Title | | B33 | Insurance Escrow |
| B25 | Property Condition Report | | B34 | Soft Cost Cushion |
| B26 | File Inspection | | B35 | Working Capital Reserves |
| B27 | Environmental | | B36 | Replacement Reserves (Capitalized) |
| B28 | Survey | | | |

(No bond Cost-of-Issuance lines in the ACQ model — that block is EFB-only.)

### Capital / Construction Budget (Rows 39–42) — all INPUT

| Cell | Label |
|---|---|
| B39 | Capital Budget |
| B40 | Capital Budget Paid by Reserves? ("Yes"/"No") |
| B41 | Year Renovation Begins |
| B42 | Year Renovation Complete |

### GP Fees (Rows 45–48) — all INPUT

| Cell | Label | ACQ Default |
|---|---|---|
| B45 | Acquisition Fee (% of PP) | **0.005 ($50M+), 0.0075 ($25–50M), 0.01 (<$25M)** — NOT 0.05. **BL-03 GATE:** `assert_fee_bounds` FAILS on 0.05 (EFB/Esplanade sentinel) or outside [0.005, 0.01]; populator refuses the write w/o an override note. |
| B46 | Asset Management Fee (% of EGI) | 0.005 |
| B47 | Disposition Fee | per deal |
| B48 | Construction Mgmt (% of Budget) | 0 if no reno |

### Senior Debt (Rows 51–62) — INPUT except B52

| Cell | Label | Type | Notes |
|---|---|---|---|
| B51 | LTV | INPUT | bridge LTV (e.g., 0.85) |
| B52 | Loan Amount | FORMULA | `=B51*B10` |
| B53 | Interest-Only Period | INPUT | years |
| B54 | Loan Origination Fee | INPUT | e.g., 0.0125 |
| B55 | Financing Fee | INPUT | |
| B56 | Interest Rate | INPUT | bridge rate (e.g., 0.08) |
| B57 | Term | INPUT | bridge term (years) — drives the bridge→refi DSCR switch |
| B58 | Loan Exit Fee | INPUT | |
| B59 | Amortization | INPUT | 30 |
| B60 | Fixed or Floating? | INPUT | "Fixed"/"Floating" |
| B61 | Spread (Floating) | INPUT | |
| B62 | Floor (Floating) | INPUT | |

### Refi / Supplemental Debt (Rows 65–76) — INPUT except B66, B68

| Cell | Label | Type | Notes |
|---|---|---|---|
| B65 | Loan Type | INPUT | "Senior Refi" / "Supplemental" / "None" |
| B66 | Last Dollar LTV (Combined) | FORMULA | `=IFERROR(SUM(B52,B67)/B10,"N/A")` — **formula-audit cell** |
| B67 | Loan Amount | INPUT | agency refi takeout size |
| B68 | Refi Valuation (Sized off Cap) | FORMULA | `=IFERROR(IF(OR(B65="Senior Refi",B65="Supplemental"),INDEX($F$21:$P$21,MATCH(B69,$F$1:$P$1,0))/(B11+1%),0)," ")` |
| B69 | Origination Year | INPUT | refi year (e.g., 1–2) |
| B70 | Interest-Only Period | INPUT | refi IO years (drives the Year-of-P+I switch) |
| B71 | Origination Fee | INPUT | |
| B72 | Interest Rate (Current) | INPUT | refi rate (e.g., 0.055) |
| B73 | Interest Rate (Accrued) | INPUT | |
| B74 | Loan Maturity | INPUT | |
| B75 | Exit Fee | INPUT | |
| B76 | Amortization | INPUT | 30 |

### Sale Information (Rows 79–82) — INPUT except B82

| Cell | Label | Type | Notes |
|---|---|---|---|
| B79 | Exit Cap Rate | INPUT | 3-method triangulation, take HIGHEST per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md) |
| B80 | Costs of Sale | INPUT | 0.02 |
| B81 | Sale Year | INPUT | e.g., 7 or 10 |
| B82 | Projected Sale Value | FORMULA | `=INDEX($F$62:$P$62,MATCH(B81,$F$1:$P$1,0))` |

---

## Phase 3: Pro Forma Sheet (Columns D–P), P&L Projections

10-year cash flow projection. **All formulas, never edit.** These derive from the inputs in columns A–B, R–Z, and R–AC.

Standard layout:
- Column D = Year 0 (acquisition / sources & uses)
- Columns E–N = Years 1–10 (operating)
- Column O = Year 11 (sale/exit)
- Row 78: DSCR by year
- Row 71: Sources = Uses test at Year 0

---

## Phase 4: Pro Forma Sheet (Columns R–Z), Unit Mix — VERIFIED

One row per bedroom-type × tier, starting R3. The ACQ model ships with the **four-tier**
layout (the Z-column rent-assumption notes confirm: MLA @ FMR / HAP voucher / 80% AMI / Market).
Per BR type the model reserves 4 rows (e.g., 1BR = rows 3–6, 2BR = rows 7–10, 3BR = rows 11–14).

| Column | Field | Type |
|---|---|---|
| R | Unit Type (e.g., "2 BR / 2 BA (HAP)") | INPUT |
| S | # of Units | INPUT |
| T | SF | INPUT |
| U | In-Place Rent/Month | INPUT |
| V | In-Place Rent PSF | FORMULA `=U/T` |
| W | Pro Forma Rent/Month | INPUT |
| X | Pro Forma Rent PSF | FORMULA `=W/T` |
| Y | Rent Premium | FORMULA `=W-U` |
| Z | Pro Forma Rent Assumption note | INPUT (cite tier: "MLA @ FMR", "HAP voucher", "80% AMI – MTSP", "Market – under P75") |

**Row 22 totals (all FORMULA, never write):** S22 `=SUM(S3:S21)`, T22/U22/W22 SUMPRODUCT
weighted averages, V22 `=U22/T22`, X22 `=W22/T22`.

Pro forma market-rate rents: P75 PSF of stabilized submarket comps × subject SF, split
Classic/Renovated per [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md).

---

## Phase 5: Other Income (Columns R/U, rows 25–36) — VERIFIED

Per-unit/month line items, all **INPUT** in column U:

| Cell | Item | | Cell | Item |
|---|---|---|---|---|
| U26 | Application Fee | | U31 | Tenant Insurance Premiums |
| U27 | Pet Rent | | U32 | Late Fees |
| U28 | Cable/Internet Income | | U33 | Cleaning & Repairs Reimbursement |
| U29 | Storage Income | | U34 | Miscellaneous Income |
| U30 | Parking Income | | U35 | Administrative Fees |

U36 = `=SUM(U26:U35)` (FORMULA, Total Per Unit/Month). Apply the 3-tier classification
(recurring / turnover-driven / non-recurring) from [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md) §Other Income before entering.

---

## Phase 6: Revenue Assumptions (Columns S/T/U…, rows 39–42) — VERIFIED

| Cell | Label | Type | Notes |
|---|---|---|---|
| S40 | Other Income (Per Unit/Per Year) | FORMULA | `=U36` — **formula-audit cell** (should annualize: expect `=U36*12`) |
| S41 / U41 | Market Growth | INPUT | S41 = Year-1 (0), U41+ = stabilized (e.g., 0.03). Year-by-year across the row. |
| S42 / U42 | Physical Vacancy | INPUT | year-by-year vacancy curve (S42 = Y1, e.g., 0.10; U42+ stabilized 0.07) |

The growth/vacancy assumptions extend across the projection columns (S, U, and rightward),
one value per year — this is where the year-by-year vacancy curve lives.

---

## Phase 7: Operating Expenses (Columns S/U, rows 46–57) — VERIFIED

T-12 actuals in **column S (INPUT)**, pro forma per-unit/year in **column U (INPUT, except U46)**:

| Row | Item | S (T-12 total) | U (Pro Forma /unit/yr) |
|---|---|---|---|
| 46 | Property Management Fees | INPUT | FORMULA `=V46/S22` (driven by 3% of EGI, S62) |
| 47 | Payroll & Personnel | INPUT | INPUT |
| 48 | General & Administrative | INPUT | INPUT |
| 49 | Marketing | INPUT | INPUT |
| 50 | Turnover | INPUT | INPUT |
| 51 | Repairs & Maintenance | INPUT | INPUT |
| 52 | Contract Services | INPUT | INPUT |
| 53 | Utilities | INPUT | INPUT |
| 54 | Utility Reimbursements | INPUT (negative) | INPUT (negative) |
| 55 | Real Estate Taxes | INPUT | FORMULA `=S81/S22` (from tax calc) |
| 56 | Insurance | INPUT | INPUT |
| 57 | Capital Expense Reserves | INPUT | INPUT |

S58/U58 = `=SUM(..46:..57)` (FORMULA). Growth assumptions: S62/U62 PM fee % (0.03),
S63/U63 Annual Expense Growth (0.03) — INPUT.

---

## Phase 9: Property Tax (Column S, rows 66–71) — VERIFIED (note: NOT S52/S54/S57/S70/S71)

The ACQ tax calculator lives at **S66–S71**, distinct from the EFB layout the old stub assumed.

| Cell | Label | Type | ACQ Treatment |
|---|---|---|---|
| S66 | Property Tax Rate (millage) | INPUT | from tax bill / assessor (e.g., 0.019171) |
| S67 | Non Ad-Valorem Taxes | INPUT | **TX MUD/PID critical check** per [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md); not exempt |
| S68 | Current Assessed Value | INPUT | tax bill |
| S69 | Reassessed Upon Acquisition? | INPUT | "Yes" for most ACQ |
| S70 | Reassessed Upon Sale? | INPUT | "Yes"/"No" per state rule |
| S71 | Percentage of Value Assessed | INPUT | **State ratio**: FL 65–80%, TX 60–70%, GA 40% per [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md) |

There is **no tax-exemption breaker** in the ACQ model (that is EFB-only). Taxes flow as a
real expense via the rows 73+ tax-expense block into S55/U55.

---

## Phase 11a: Comps Sheet

Per [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md):

- Sales comps: rows 5–30, 16 slots, recency-weighted formula in C10:C25
- Rent comps display: rows 33–64, 10 primary + 2 new + 3 vintage + 5 affordability
- Q-block input grid: rows 8–118, columns Q:AF
- Per-BR breakout: rows 66–86, linked to Pro Forma!T6/U6/T10/U10/T13/U13

Same structure across EFB Mini Model and ACQ Mini Model.

---

## Phase 11b: UW Snapshot Sheet

Per [references/12-uw-snapshot.md](.skills/dream-underwrite/references/12-uw-snapshot.md):

- T-12 / T-6 / T-3 reconciliation
- For EFB: with-tax vs. without-tax pulls (display both views)
- **Snapshot scope: Deal Identity + Revenue + Expense + NOI blocks only.** DSCR is verified on the Checks tab (sheet 11); returns (IRR/EM/CoC) and exit metrics are read from Pro Forma rows B14–B17 and B79–B82. Neither DSCR nor returns/exit rows belong on the Snapshot sheet.
- Sanity check list per Reference 12

---

## Data Population Workflow (ACQ)

When the user drops in source documents, follow this sequence:

1. **Phase 1**: Paste Seller T-12 verbatim to Seller T-12 sheet. Map to T-12 Inputs. Deliver forensic analysis.
2. **Phase 2**: Paste Seller Rent Roll verbatim to Seller RR sheet. Map to RR Inputs with Status column.
3. **Phase 3**: Populate Pro Forma cols A–B. **ACQ fee at 0.5–1.0%** (NOT 5%). Closing costs (no bond COI). Debt terms (bridge initial + agency refi takeout).
4. **Phase 4**: Pro Forma cols R–Z unit mix. P65 PSF base case (or 4-tier if mixed-income hybrid).
5. **Phase 5**: Pro Forma S26 Other Income.
6. **Phase 6**: Pro Forma rows 27–28 revenue growth + vacancy curve.
7. **Phase 7**: Pro Forma cols R–AC rows 30–49 OpEx.
8. **Phase 8**: Triangulate OpEx against agency manuals per [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md).
9. **Phase 9**: Pro Forma rows 51–73 property tax calculator with state-specific reassessment ratio. S70 = 0, S71 = 0.
10. **Phase 10**: Resize debt and purchase price. Bridge at 1.15x DSCR on in-place NOI. Agency refi at 1.25x DSCR on forward T-3.
11. **Phase 11**: Populate Comps sheet. Run UW Snapshot sanity check. Validate IRR vs Manual hurdles per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md).
12. **Phase 12**: HTML investment memo per [references/14-html-memo.md](.skills/dream-underwrite/references/14-html-memo.md). Use ACQ variant of metrics (IRR, EM, CoC, net investor IRR) instead of EFB DSCR-only display.

---

## Resolved 2026-06-03 (against Rayzor ACQ Mini Model 5.04.26)

Verified directly with openpyxl — the items the old stub deferred are now mapped above:
- ✅ Closing costs = rows 20–36; GP fees = rows 45–48; senior debt = rows 51–62; refi = rows 65–76; sale = rows 79–82.
- ✅ **Tax calculator is S66–S71** (NOT the EFB-style S52/S54/S57/S70/S71 the old stub guessed). No exemption breaker in the ACQ model.
- ✅ Return metrics B14–B17 are formulas (IRR `=IRR(E77:P77)`, EM, CoC) — the CP-2 reconciliation targets.
- ✅ Unit mix R3:Z21 (4-tier layout), totals row 22; Other Income U26–U36; revenue S39–S42; OpEx S46–U57.

## Pre-population formula-audit findings (verified in this template)

The two ACQ formula-audit cells confirmed in the Rayzor template:
- **S40** (Other Income annual): ships as `=U36` — monthly, should be `=U36*12`. Flag + patch with user approval per Universal Rule 8.
- **B66 / B68**: combined-LTV and refi-valuation formulas present and structurally correct in this template (not buggy here, but read them before writing B67).
- Row 78 (Senior DSCR) bridge→refi pointer and rows 31–32 refi P+I thresholds: re-audit per [field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md) §Pre-Population Formula Audit (the Esplanade fork carried these bugs; confirm per deal).

## Still to map (non-blocking for the populator — these are read-only / output sheets)

These do not gate the openpyxl input populator (which writes only Pro Forma INPUT cells):
1. Claude Log sheet (free-form text logging — append-only, no cell map needed).
2. Loom Script sheet (output-only narration).
3. Rent Comps Analysis sheet internal layout (Phase 11a writes the Comps sheet, mapped in [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md)).
4. Checks sheet sanity formulas (read-only validation; surfaced at CP-2).
5. UW Snapshot ACQ vs EFB view toggle (read-only; Phase 11b).

---

## See Also

- [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md), EFB Mini Model cell map (full detail; the ACQ map will mirror this structure)
- [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md), conventional revenue framework (P65 PSF)
- [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md), state-specific reassessment ratios
- [references/09-acq-financing.md](.skills/dream-underwrite/references/09-acq-financing.md), bridge / agency / HUD financing
- [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md), return hurdles and exit cap triangulation
