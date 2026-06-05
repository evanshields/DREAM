# Shieldstone EFB Mini Model: Field Mapping Guide

## Overview

This guide maps every input cell in the Shieldstone EFB Mini Model to the data source it should be populated from. The model lives on the sheet named **"EFB Mini Model"**. Blue-text cells are inputs; black-text cells are formulas, never overwrite formulas.

---

## Pre-Population Formula Audit (REQUIRED at Phase 3)

The EFB Mini Model template has historically shipped with formula bugs that, if left in place, corrupt every downstream output (DSCR, IRR, refi sizing, exit metrics). Per Universal Rule 8, the skill must audit these cells BEFORE populating any input that depends on them. For each cell below, read the actual formula via openpyxl, compare to the expected formula, and if there is a mismatch, surface it in chat with the proposed patch:

**BL-07 enforcement:** run `acq_engine.formula_integrity_check({cell: actual_formula})` to emit a **named PASS/PATCH verdict for all 5 cells EVERY run** (not just when one breaks downstream — both humans fixed these reactively, never by name). **S40 (`=U36`→`=U36*12`) and row 78 (bridge→refi DSCR pointer) are the AUTO-PATCH set** — printed patch + one-line human confirm, then the populator applies them via the `applied=true` flag. B66/B67/rows 31-32 stay flag-only. This is the only place the skill mutates black-text formula cells.

```
Formula Audit (EFB Mini Model):
  S40 (Other Income annual): expected =U36*12, actual =U36  [BUG, will undercount by 12x]
  B66 (LTC):                  expected =B52/B10, actual =SUM(B52,B67)/B10  [BUG, double-counts refi]
  B67 (Refi loan amount):     expected =B68, actual hardcoded $62,000,000  [BUG, will not flex]
  Rows 31-32 (Refi P+I):      expected IF(F$1<B69+B70+1, ...), actual IF(F$1<B70, ...)  [BUG, B70 treated as absolute year]
  Row 78 (Senior DSCR):       expected conditional (bridge DS yrs 1 through B57, refi P+I after), actual unconditional bridge DS pointer  [BUG, breaks post-refi]

Propose 5 patches? (Y/N)
```

Wait for user confirmation before writing any patch. Never silently apply.

### Bug catalog (with expected formulas)

| Cell | Role | Expected formula | Bug pattern observed | Patch |
|---|---|---|---|---|
| **S40** | Other Income, annualized | `=U36*12` | `=U36` (monthly value placed in annual cell) | Multiply by 12 |
| **B67** | Refi loan amount | `=B68` (or = sized refi from sizing block) | Hardcoded $62,000,000 | Link to refi sizing output cell |
| **B66** | Loan-to-Cost (LTC) | `=B52/B10` (senior loan / purchase price) | `=SUM(B52,B67)/B10` (sums senior + refi, double-counts the same dollar) | Use senior loan only; refi is a future event, not an at-acquisition LTC component |
| **Rows 31-32** | Refi P+I in 10-year cash flow | `=IF(F$1<B69+B70+1, [interest-only], [full P+I])` | `=IF(F$1<B70, ...)` (B70 treated as absolute year not relative IO period after refi close at year B69) | Adjust the year-comparison to be `refi close year + IO period + 1`, not just IO period |
| **Row 78** | Senior DSCR by year | Conditional formula: in years 1 through B57 pull bridge debt service (rows 29-30); in years B57+1 onward pull refi P+I (rows 31-32). Example: `=NOI / -IF(F$1<=B57, SUM(F29:F30), SUM(F31:F32))` | Unconditional pointer at bridge DS only (`=NOI / -SUM(F29:F30)`), which goes to zero or stale after bridge payoff and silently overstates DSCR | Wrap in IF that switches based on year vs. bridge term cell (B57) |

### Audit procedure

1. At the START of Phase 3 (before any cell in cols A-B is written), open the workbook with openpyxl.
2. Read the `.value` of S40, B66, B67, row 31 (sample one cell from cols F-N), row 32 (same), row 78 (sample F78).
3. For each, compare to the expected pattern. The comparison is structural (does the formula start with `=IF`?  Does it reference B70 vs B69+B70+1?), not exact string match (cell ranges shift if the model is altered).
4. Flag each bug found. Patches are applied ONLY after user confirms.
5. After patching, re-read the cells to confirm the new formulas are in place.
6. Log to Claude Log: `[timestamp] Phase 3: audited 5 known formula cells, found N bugs, patched M with user approval`.

If the user declines to patch, document the declined patches in Claude Log and proceed with full visibility. Do NOT silently work around a buggy formula in downstream phases, the corruption will compound.

---

## Model Layout

The sheet is organized into four zones:

| Zone | Columns | Content |
|---|---|---|
| **Assumptions** | A–B (rows 1–82) | All deal assumptions: pricing, closing costs, loan terms, fees, sale info |
| **P&L / Cash Flows** | D–P (rows 1–82) | Year-by-year projections (Year 0 = acquisition, Years 1–11) |
| **Unit Mix** | R–Z (rows 1–22) | Unit types, counts, SF, in-place rents, pro forma rents, assumptions |
| **Operating Assumptions** | R–AC (rows 24–73) | Revenue assumptions, OpEx (T-12 and pro forma), property tax calculator |

---

## Zone 1: Acquisition Assumptions (Columns A–B)

### Property Info (Rows 2–11)
| Cell | Label | Source | Input Type |
|---|---|---|---|
| B2 | Asset Name | Broker OM / deal info | Text |
| B3 | Address | Broker OM | Text |
| B4 | City, State & ZIP | Broker OM | Text |
| B5 | Year Built | Broker OM / tax records | Number |
| B6 | Number of Units | **FORMULA** (=S22, sum of unit mix) | Do not edit |
| B7 | Rentable SF | **FORMULA** (=T22×S22) | Do not edit |
| B8 | Price Per Unit | **FORMULA** (=B10/B6) | Do not edit |
| B9 | Asking Price | Broker OM | Currency |
| B10 | Purchase Price | Negotiated price | Currency |
| B11 | Going-In Cap Rate | **FORMULA** (=T-3 NOI/B10) | Do not edit |

### Closing Costs (Rows 13–30)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B14 | GP Bond Counsel | Deal terms | Typically $150–200K |
| B15 | Lender's Counsel | Deal terms | Often $0 (lender absorbs) |
| B16 | Cost of Issuance | Bond deal terms | EFB-specific |
| B17 | Transfer/Recordation | State/county rates | $50K typical |
| B18 | Title | Title company quote | $50K typical |
| B19 | Property Condition Report | Vendor quote | $3–5K |
| B20 | File Inspection | Vendor quote | $5K typical |
| B21 | Environmental | Phase I/II quote | $2.5–5K |
| B22 | Survey | Surveyor quote | $5–7K |
| B23 | Appraisal | Appraiser quote | $5–6K |
| B24 | Market Study | Vendor quote | $4–5K |
| B25 | Enhancements and Reserves | As needed (interest reserve sized here) | Often $0; sized when Year 1 DSCR < 1.15x |
| B26 | Capital Reserve | Lender requirement | $500K–$1M typical |
| B27 | Insurance Escrow | Lender requirement | $50–100K |
| B28 | Soft Cost Cushion | Contingency | $50K typical |
| B29 | Working Capital Reserves | Operating cushion | $50–75K |
| B30 | Replacement Reserves (Capitalized) | If required by lender | Often $0 |

### Capital Budget (Rows 33–36)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B33 | Capital Budget | Capex analysis (ref: [references/07-capex.md](.skills/dream-underwrite/references/07-capex.md)) | Total renovation budget |
| B34 | Capital Budget Paid by Reserves? | Deal structure decision | "Yes" or "No" |
| B35 | Year Renovation Begins | Business plan | Typically 1 |
| B36 | Year Renovation Complete | Business plan | Typically 2 |

### GP Fees (Rows 39–43)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B39 | Acquisition Fee (% of PP) | Deal terms | 0.5–10% (EFB default 5%) |
| B40 | Administrator Advisory Fee (% of PP) | Deal terms | EFB-specific |
| B41 | Asset Management Fee (% of EGI) | Deal terms | 0.5–1.0% |
| B42 | Disposition Fee | Deal terms | 0.25–0.5% |
| B43 | Construction Mgmt (% of Budget) | Deal terms | 0–5% |

### A Note (Rows 46–54)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B46 | Loan Amount | Lender term sheet | Size at LTV or lender max |
| B47 | LTV | **FORMULA** (=B46/B10) | Do not edit |
| B48 | Interest-Only Period | Lender terms | Years (e.g., 1, 2, 3) |
| B49 | Loan Origination Fees | Lender terms | 1–2% typical |
| B50 | Financial Advisory Fee | Advisor terms | 0.5% typical |
| B51 | Loan Interest Rate | Lender terms | Decimal (e.g., 0.048) |
| B52 | Term | Lender terms | Years (e.g., 10) |
| B53 | Loan Exit Fees | Lender terms | Often 0 |
| B54 | Amortization | Lender terms | 30 years standard |

### Cost of Issuance (Rows 57–62)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B57 | Financial Advisor Issuance | Advisor terms | EFB-specific |
| B58 | Bond Counsel | Legal quote | EFB-specific |
| B59 | Underwriter Counsel | Legal quote | EFB-specific |
| B60 | Trustee | Trustee quote | EFB-specific |
| B61 | Trustee Counsel | Legal quote | EFB-specific |
| B62 | Other Bond Closing Costs | Miscellaneous | EFB-specific |

### B Note (Rows 65–76)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B65 | B Note Loan Type | Deal structure | "Junior Debt", "Supplemental", "Senior Refi", "N/A" |
| B67 | B Note Amount | Lender terms | $0 if not used |
| B69 | B Note Origination | When B note funds | Year number |
| B70 | B Note IO Period | Lender terms | Years |
| B71 | B Note Origination Fees | Lender terms | % |
| B72 | B Note Interest Rate (Current) | Lender terms | Decimal |
| B73 | B Note Interest Rate (Accrued) | Lender terms | Decimal |
| B74 | B Note Loan Maturity | Lender terms | Years |
| B75 | B Note Exit Fees | Lender terms | % |
| B76 | B Note Amortization | Lender terms | Years |

### Sale Info (Rows 79–81)
| Cell | Label | Source | Notes |
|---|---|---|---|
| B79 | Exit Cap Rate | Exit cap triangulation (ref: [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md)) | Decimal (e.g., 0.085) |
| B80 | Costs of Sale | Market standard | 2% typical |
| B81 | Sale Year | Business plan | 5, 7, or 10 typical |

---

## Zone 2: Unit Mix (Columns R–Z, Rows 2–22)

### Blue-Text Input Cells (per unit type row, starting R3)
| Column | Field | Source | Notes |
|---|---|---|---|
| R | Unit Type | Rent roll analysis | e.g., "2 BR / 2 BA (80% AMI)" |
| S | # of Units | Rent roll count | Integer |
| T | SF | Floor plans / listing / web search | Per-unit square footage |
| U | In-Place Rent/Month | Rent roll (avg of occupied units in this type) | Currency |
| W | Pro Forma Rent/Month | Market analysis / AMI limits / comp analysis | Currency |
| Z | Pro Forma Rent Assumptions | Analyst notes | Text describing basis |

### Formula Cells (Do NOT Edit)
| Column | Field | Formula |
|---|---|---|
| V | In-Place Rent PSF | =U/T |
| X | Pro Forma Rent PSF | =W/T |
| Y | Rent Premium | =W-U |

### Row 22: Totals (All Formulas)
- S22: =SUM(S3:S21) → Total units
- T22: Weighted avg SF
- U22: Weighted avg in-place rent
- W22: Weighted avg pro forma rent

---

## Zone 3: Revenue Assumptions (Columns R–AC, Rows 24–28)

| Cell(s) | Label | Source | Notes |
|---|---|---|---|
| S26 | Other Income ($/unit/year) | T-12 analysis (ref: [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md)) | $50–150 typical |
| S27:AC27 | Market Growth | Market analysis | Decimal (e.g., 0.02 = 2%) |
| S28:AC28 | Physical Vacancy | Business plan | Year 1 higher during reno (0.10), stabilized 0.07 |

---

## Zone 4: Operating Expenses (Columns R–AC, Rows 30–73)

### T-12 Actuals (Column S, Rows 32–43)
Populate from T-12 operating statement. These are raw annual totals, no adjustments.

| Cell | Category | T-12 Source |
|---|---|---|
| S32 | Property Management | GL 6050 |
| S33 | Payroll | GL 7011 + benefits |
| S34 | G&A | GL 6040 + legal + bank + software |
| S35 | Marketing | Advertising + leasing commissions |
| S36 | Turnover | Make-ready + cleaning + painting |
| S37 | R&M | GL 6015 (exclude capex items) |
| S38 | Contract Services | GL 5004 + 5015 + pest + security + pool |
| S39 | Utilities (Gross) | GL 6020 (electric + gas + water/sewer) |
| S40 | Utility Reimbursements | GL 4530 (NEGATIVE number, it's a credit) |
| S41 | Real Estate Taxes | GL 6010 |
| S42 | Insurance | GL 6030 |
| S43 | Capital Reserves | $0 from T-12 (or actual if expensed) |

### Pro Forma Per-Unit/Year (Column U, Rows 33–43)
These are the blue-text underwriting assumptions.

| Cell | Category | How to Set | Reference |
|---|---|---|---|
| U32 | PM | **FORMULA** (=V32/S22), driven by S48 % | Auto-calculated |
| U33 | Payroll | T-12 ÷ units, adjusted ±10% | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Payroll |
| U34 | G&A | T-12/unit + 3% growth | $200–400/unit |
| U35 | Marketing | T-12/unit or haircut for affordable | Lower for EFB |
| U36 | Turnover | T-12/unit × 1.0–1.1 | Lower for affordable/EFB |
| U37 | R&M | T-12/unit × 1.03–1.05 | Vintage-adjusted |
| U38 | Contracts | NORMALIZE: reinstate cut services + 3% | Red flag check |
| U39 | Utilities | T-12/unit + 3% inflation | |
| U40 | Util Reimb | **FORMULA** (=-0.75×U39) | 75% RUBS recovery |
| U41 | RE Taxes | **FORMULA** (=S67/S22), from tax calculator | $0 for EFB |
| U42 | Insurance | **FORMULA** (=T42×1.2), 20% buffer | |
| U43 | CapEx Reserves | $250–$350/unit by vintage | |

### Expense Growth (Row 49)
| Cell(s) | Label | Default |
|---|---|---|
| S49:AC49 | Annual Expense Growth | 0.03 (3%) |

### Property Management % (Row 48)
| Cell(s) | Label | Default |
|---|---|---|
| S48:AC48 | PM Fee as % of EGI | 0.03 (3%) |

### Property Tax Calculator (Rows 51–73)
| Cell | Label | Source |
|---|---|---|
| S52 | Property Tax Rate (millage) | County assessor / tax bill |
| S53 | Non-Ad Valorem Taxes | Tax bill (TX MUD/PID check critical) |
| S54 | Current Assessed Value | Tax bill / assessor records |
| S55 | Reassessed Upon Acquisition? | "Yes" or "No" |
| S56 | Reassessed Upon Sale? | "Yes" or "No" |
| S57 | Percentage of Value Assessed | State ratio (ref: [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md)) |
| S70 | Tax Exemption Breaker | 1 = exemption ON (EFB), 0 = OFF (ACQ) |
| S71 | Percentage Exempt | 0 to 1 (1 = 100% exempt for EFB) |

---

## Waterfall Structure (Rows 93–97)

| Cell | Label | Source |
|---|---|---|
| F94 | GP Equity % | Deal terms (e.g., 0.05 = 5%) |
| F95 | LP Equity % | **FORMULA** (=1-F94) |
| F96 | Preferred Return | Deal terms (e.g., 0.09 = 9%) |
| F97 | Promote Over Pref | Deal terms (e.g., 0.30 = 30% GP) |

---

## Data Population Workflow (EFB)

When the user drops in source documents, follow this sequence:

### Step 1: Rent Roll → Unit Mix (R3:Z10)
1. Read [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md) for parsing instructions
2. Extract unit types, counts, SF, in-place rents
3. Populate R, S, T, U columns (blue-text only)
4. Apply 60/20/20 AMI allocation:
   - W column for 80% AMI units: Look up Novogradac rent limits for the county (pause-and-paste pattern per [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md))
   - W column for HAP units: Look up HUD FMR/SAFMR for the MSA
   - W column for market rate units: Use comp analysis
5. Add assumption notes in Z (cite "FHFC 80% AMI", "HAP @ 100% FMR", "Market Rate", etc.)

### Step 2: T-12 → Operating Expenses (S32:S43)
1. Map T-12 GL codes to model categories (RUBS classification trap per [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md))
2. Populate S32:S43 with raw annual totals
3. Populate U33:U43 with pro forma assumptions per Shieldstone manual
4. **Critical: S41 (RE Taxes) populates from T-12, but pro forma = $0 (EFB tax exemption)**
5. Set property tax calculator: S70 (Tax Exemption Breaker) = 1, S71 (% Exempt) = 1
6. Add notes in W column explaining each assumption

### Step 3: Property Info → Acquisition Assumptions (B2:B10)
1. Pull from OM: name, address, city/state, year built
2. Set purchase price (B10) and asking price (B9)
3. Unit count auto-calculates from unit mix (B6=S22)

### Step 4: EFB Financing → Loan Terms (B46:B54)
1. Bond amount: Target 120% of purchase price (B46)
2. Rate: Current AAA muni yield (B51), search to verify
3. IO Period: Set to match term, **full-term I/O** (B48 = B52)
4. Term: 10 years (B52)
5. Amortization: 30 (B54), model has it but IO period overrides

### Step 5: EFB Fees (B39:B43)
1. Developer fee: B39 + B40 should total 10% of project cost
   - Standard: B39 = 0.05, B40 = 0.05 (split as Acquisition Fee + Admin Advisory Fee)
   - Or: B39 = 0.10, B40 = 0 (all in one line)
2. Asset management: B41 = 0.005 (0.5% of EGI)
3. Disposition: B42 = 0.005 (0.5%)
4. Construction mgmt: B43 = per deal (0–5%)

### Step 6: Exit (B79:B81)
1. Sale year: B81 = 10 (matches bond maturity)
2. Exit cap: B79 = per ROFR terms or conservative assumption (8–10% for restricted assets)
3. Costs of sale: B80 = 0.02

### Step 7: Bond Sizing Validation
- Calculate: Bond Amount (B46) ÷ Purchase Price (B10), should = 1.20 (120% LTV)
- Check DSCR in row 78: should be >=1.15x in all years
- Check Sources = Uses (row 71 Year 0 ≈ $0)
- If DSCR < 1.15x: reduce purchase price or size interest reserve (B25) per [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md) §Interest Reserve Sizing
- Provide commentary on sizing margin and sensitivity to bond rate changes
