# 15: OpEx Agency Triangulation

## Purpose

Phase 8 of the master workflow triangulates every operating expense line item against the saved Fannie Mae, Freddie Mac, and HUD multifamily underwriting manuals to ensure the pro forma OpEx is defensible at the agency refinance. Agency-mandated minimums are extracted from the four PDFs in [shieldstone_acquisitions/agency-manuals/](../../../shieldstone_acquisitions/agency-manuals/) and triangulated with the Shieldstone manual benchmark and the T-12 actuals. The line-item tables below were extracted by direct read of those PDFs on 2026-05-13 and must be refreshed whenever any source PDF is updated. The agency-manuals folder [README.md](../../../shieldstone_acquisitions/agency-manuals/README.md) tracks publication dates.

---

## REST API fast path (preferred for Phase 8)

The line-item agency tables below are seeded into the Mission Driven AI REST API. Phase 8 can pull the binding floor + all underlying sources directly via one HTTPS call instead of re-reading this entire markdown each deal. See [references/00-api-reference.md](.skills/dream-underwrite/references/00-api-reference.md) for full auth and usage; the key endpoint is:

```bash
GET /api/v1/opex/triangulate?line_item=<item>&class=<A|B|C>&state=<state_overlay>&program=conventional
```

Returns `binding_floor` (agency + value + citation) plus `all_sources` (every rule row backing the triangulation). For standard ACQ deals, **always pass `program=conventional`** — without it, `binding_floor` returns the MAX across all programs (e.g., Fannie Seniors-with-Skilled-Nursing $450/u). Verify `binding_floor.citation` matches the deal context before quoting in the IC memo.

**The line-item tables below remain canonical** (single source of truth). The API is a faster read path, not a replacement source. When this markdown is updated, the API gets re-seeded — see the Refresh Note at the bottom.

---

## REQUIRED Gate (Phase 9 cannot proceed without this)

Phase 8 triangulation is a **required deliverable**, not a suggestion. Phase 9 (Property Tax) cannot begin until Phase 8 has produced:

1. The full per-line-item agency-min comparison table (PM, Payroll, G&A, R&M, Turnover, Contract Services, Utilities, Insurance, Replacement Reserves, Property Tax, Vacancy).
2. The binding source identified for each line (Fannie / Freddie / HUD / Shieldstone manual / T-12, whichever is highest).
3. Explicit flags for any line where Shieldstone pro forma is AT or BELOW an agency floor.
4. A Claude Log entry: `[timestamp] Phase 8: agency triangulation complete, N flags raised, [list line items flagged]`.

If any of the four is missing, do NOT advance to Phase 9. Output to chat: "Phase 8 triangulation incomplete: [what is missing]. Cannot proceed to Phase 9 (Property Tax). Resolve and re-run." The agency comparison protects the refinance sizing assumption that the entire IRR depends on; skipping it is not negotiable.

---

## Triangulation Formula

For each operating expense line item, the underwritten value is the MAXIMUM of five sources:

```
UW Expense = MAX(
    Fannie Mae multifamily minimum (per Selling and Servicing Guide),
    Freddie Mac multifamily minimum (per Seller/Servicer Guide),
    HUD MAP Guide minimum (per Handbook 4430.G + ML 2025-03 overlay),
    Shieldstone Multifamily Manual benchmark (per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md)),
    T-12 actual x 1.03 (T-12 plus standard 3 percent growth)
)
```

Taking the MAX ensures the pro forma is the most conservative (highest expense) of all benchmarks. This protects the refinance sizing, since the agencies will resize down if the underwritten OpEx is lower than the agency floor.

---

## Source Hierarchy

### Tier 1: Saved Agency Manuals

Located at [shieldstone_acquisitions/agency-manuals/](../../../shieldstone_acquisitions/agency-manuals/):

| Agency | Manual | Local PDF | Effective |
|---|---|---|---|
| Fannie Mae | Multifamily Selling and Servicing Guide (DUS) | [fannie-mae/multifamily-selling-servicing-guide-2026-04.pdf](../../../shieldstone_acquisitions/agency-manuals/fannie-mae/multifamily-selling-servicing-guide-2026-04.pdf) | 04/30/2026 |
| Freddie Mac | Multifamily Seller/Servicer Guide | [freddie-mac/multifamily-seller-servicer-guide-2026-04.pdf](../../../shieldstone_acquisitions/agency-manuals/freddie-mac/multifamily-seller-servicer-guide-2026-04.pdf) | April 2026 |
| HUD | Multifamily Accelerated Processing Guide (Handbook 4430.G) | [hud/map-guide-4430G-2021-03.pdf](../../../shieldstone_acquisitions/agency-manuals/hud/map-guide-4430G-2021-03.pdf) | 03/19/2021 |
| HUD | Mortgagee Letter 2025-03 (DSCR / LTV / LTC update) | [hud/mortgagee-letter-2025-03.pdf](../../../shieldstone_acquisitions/agency-manuals/hud/mortgagee-letter-2025-03.pdf) | 01/08/2025 |

The 2014 attachment to ML 14-02 (formerly used for 223(f) sizing) is preserved as [hud/223f-refinance-standards-2014-01-SUPERSEDED.pdf](../../../shieldstone_acquisitions/agency-manuals/hud/223f-refinance-standards-2014-01-SUPERSEDED.pdf) for historical reference only and is no longer authoritative. ML 2025-03 replaced the DSCR and LTV/LTC numbers from that attachment.

### Tier 2: Shieldstone Multifamily Manual

Distilled in [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md) and applied operationally in [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md). Key sections:

- §1.1 Investment Philosophy and Return Hurdles
- §4.2 Property Tax Analysis and Reassessment Risk
- §4.3 Insurance
- §4.4 Payroll and Management
- §4.5 R&M, G&A, Marketing, Turnover, Contracts, Utilities
- §4.6 Replacement Reserves

### Tier 3: T-12 Actuals

T-12 actual + 3 percent growth (5 percent in hardening markets per [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md)) is the baseline. Stabilized properties almost always show T-12 expenses at or above agency floors. Lease-up and distressed assets are the exception, and the agency floor will bind in those cases.

---

## Per-Line-Item Triangulation Tables

The Fannie Mae and Freddie Mac guides operate by listing line-item INCLUSIONS (what goes into each NCF expense category) rather than dollar floors. The HUD MAP Guide drives expense estimates through appraiser comparables (Section 7.8) rather than fixed $/unit minimums. Agency-mandated dollar floors exist only where noted. For all other line items, the binding source on most deals is the Shieldstone manual benchmark or T-12 actual + 3 percent growth, and the agencies will accept that pro forma at refinance provided it is supported by comparables and operating history.

### Property Management Fee

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Greatest of (a) 3 percent of EGI, (b) actual fee, or (c) appraiser's market fee. Minimum may be 2.5 percent of EGI if the underwritten fee is at least $500/unit AND actual fee is less than or equal to UW fee | S&S Guide Part II Ch. 2 §203.01 Item 17(a), p. 124 |
| Freddie Mac | Appropriateness reviewed at underwriting and at any property management company change. No fixed floor; market fee required | S/S Guide Ch. 8 §8.13, p. 193; Ch. 43 §43.19, p. 804 |
| HUD MAP Guide | Must equal or exceed a market rate fee that would be charged by a replacement third-party manager. No fixed floor | MAP Guide §10.7.4, p. 373 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | 3 percent of EGI for 100+ units; 4-5 percent for less than 50 units; Asset Management fee 0.5-1.0 percent of EGI separate | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Property Management |
| **Triangulated UW** | **3 percent of EGI (or 2.5 percent with $500/unit floor on small assets) per Fannie; market support per Freddie / HUD** | |

### Payroll and Benefits

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Defined category (401k, bonuses, contract labor, employee benefits, FICA, manager salaries, payroll taxes, security personnel, etc.). No fixed $/unit floor. Underwrite to actual / T-12 with adjustments | S&S Guide Part II Ch. 2 §203.01 Item 17(g), p. 129 |
| Freddie Mac | Underwrite to operating history; no fixed $/unit floor | S/S Guide Ch. 8 §8.5 (Property Fundamentals) |
| HUD MAP Guide | Three-year operating history plus T-12; no fixed $/unit floor. Strip lease-up bonuses for stabilized pro forma | MAP Guide §7.8.2, p. 218 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $1,500-2,500/unit Class B; $1,200-2,000 Class C. T-12 plus 3 percent; strip lease-up bonuses | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Payroll |
| **Triangulated UW** | **T-12 plus 3 percent OR Shieldstone Manual range, whichever is higher; agency floors do not bind** | |

### General and Administrative (G&A)

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Defined category (admin fees, alarm system, bank charges, broker commissions, business license, cable, cell/pager, eviction expense, model apartment, office supplies, permits, etc.). No fixed $/unit floor | S&S Guide Part II Ch. 2 §203.01 Items 17(j) and continuation, p. 131-132 |
| Freddie Mac | Underwrite to operating history; no fixed $/unit floor | S/S Guide Ch. 8 (Property Fundamentals) |
| HUD MAP Guide | Three-year operating history plus comparables; no fixed $/unit floor | MAP Guide §7.8.4, p. 220 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $200-400/unit Class B; $150-300/unit Class C | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Expense Benchmarking |
| **Triangulated UW** | **T-12 plus 3 percent OR Shieldstone Manual range, whichever is higher; agency floors do not bind** | |

### Advertising and Marketing

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Included in NCF as separate expense line; no fixed $/unit floor | S&S Guide Part II Ch. 2 §203.01 (Underwritten NCF list), p. 218 |
| Freddie Mac | Underwrite to operating history; no fixed $/unit floor | S/S Guide Ch. 8 (Property Fundamentals) |
| HUD MAP Guide | Three-year history plus comparables; no fixed $/unit floor | MAP Guide §7.8.2, p. 218 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $100-300/unit Class B; $75-200/unit Class C. Lower for affordable/EFB | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Expense Benchmarking |
| **Triangulated UW** | **T-12 plus 3 percent OR Shieldstone Manual range; agency floors do not bind** | |

### Repairs and Maintenance (R&M)

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Defined category (appliances, building, carpet, cleaning, common area maintenance, decorating, electrical, elevator, exterminating, HVAC, janitorial, landscaping, lock/keys, mechanical, painting, pest control, plumbing, snow removal, supplies, turnover, etc.). No fixed $/unit floor | S&S Guide Part II Ch. 2 §203.01 Item 17(f), p. 128 |
| Freddie Mac | Underwrite to operating history; no fixed $/unit floor | S/S Guide Ch. 8 (Property Fundamentals) |
| HUD MAP Guide | Three-year history plus comparables. Strip capex-quality items (resurfacing, roof, HVAC replacement) to capex/reserves | MAP Guide §7.8.4, p. 220 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $300-600/unit Class B; $400-800/unit Class C. T-12 x 1.03-1.05; add 5-10 percent for properties greater than 30 years old; +15 percent buffer for 2020+ vintage in early operating years | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §R&M |
| **Triangulated UW** | **T-12 x 1.03-1.05 OR Shieldstone Manual range, whichever is higher** | |

### Turnover / Make-Ready

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Included in R&M category (make-ready, turnover, vacancy preparation) per S&S Guide Part II Ch. 2 §203.01 Item 17(f). No separate fixed floor | S&S Guide p. 128 |
| Freddie Mac | Cooperative properties: total unit turnover must not exceed 20 percent. No fixed $/unit floor for non-coop | S/S Guide (Cooperative Property exception, p. 310 of Fannie cross-reference) |
| HUD MAP Guide | Three-year history plus comparables; no fixed $/unit floor | MAP Guide §7.8.4, p. 220 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $100-250/unit Class B; $100-200/unit Class C. Lower for affordable (tenants stay longer) | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Expense Benchmarking |
| **Triangulated UW** | **T-12 plus 3 percent OR Shieldstone Manual range; agency floors do not bind** | |

### Contract Services

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Categorized within Payroll/Benefits (contract labor, contract work) and R&M (extermination, janitorial, landscaping, pest control, scavenger, snow removal). No fixed $/unit floor | S&S Guide Part II Ch. 2 §203.01 Items 17(f), 17(g), p. 128-129 |
| Freddie Mac | Underwrite to operating history; no fixed $/unit floor | S/S Guide Ch. 8 (Property Fundamentals) |
| HUD MAP Guide | Three-year history; no fixed $/unit floor | MAP Guide §7.8.4, p. 220 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $500-1,500/unit Class B; $500-1,200 Class C. Reinstate any service dropped to $0 mid-year (seller cost cuts to inflate NOI). Common cuts: security patrol, trash, landscaping | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Contract Services |
| **Triangulated UW** | **Reinstate seller cuts to full-year run rate plus 3 percent; agency floors do not bind** | |

### Utilities

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Two line items: 17(d) Utilities (electricity, fuel oil, gas, heat, septic, trash, vacant unit utilities) and 17(e) Water and Sewer. Solar PV requires trailing 12-month utility expense support; reimbursement income capped to T-12 | S&S Guide Part II Ch. 2 §203.01 Items 17(d) and 17(e), p. 127; Section 111.04, p. 95 |
| Freddie Mac | Underwrite to operating history; no fixed $/unit floor | S/S Guide Ch. 8 (Property Fundamentals) |
| HUD MAP Guide | Three-year history; separate Owner-paid utility methodology in Section 6.9 (new projects) | MAP Guide §6.9, p. 187; §7.7.10, p. 212 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $800-1,500/unit gross Class B; RUBS recovery 60-80 percent. T-12 plus 3 percent (5 percent for Texas ERCOT-deregulated). Water/sewer is 60-80 percent of total utility spend. Model gross AND RUBS recovery separately | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Utilities |
| **Triangulated UW** | **T-12 plus 3-5 percent (state-specific) OR Shieldstone Manual range, whichever is higher** | |

### Insurance

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Insurance equal to: bona fide written quote from a reputable broker for a new 12-month policy; OR 110 percent of current expense (policy with less than 6 months remaining); OR 105 percent of current expense (6-12 months remaining). For acquisitions, only underwrite premiums from the purchaser's carrier; disregard the seller's | S&S Guide Part II Ch. 2 §203.01 Item 17(c), p. 126 |
| Freddie Mac | Insurance Reserves required per Section 39.2. Underwrite to current premium plus market support | S/S Guide §39.2, p. 647; Ch. 31 (insurance requirements) |
| HUD MAP Guide | Three-year history. Casualty insurance face amount: lower of 80 percent of insurable improvements OR balance of insured mortgage | MAP Guide §3.9, p. 92-94; §3.2.2, p. 73 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | $600-1,200/unit Class B; $700-1,400/unit Class C. T-12 x 1.15-1.25 buffer for acquisition. Coastal FL/TX: 20-30 percent premium. Texas hail: 10-15 percent above national. Hardening market: 5-10 percent annual escalation | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Insurance |
| **Triangulated UW** | **MAX of: Fannie quote-based minimum, T-12 x 1.15-1.25 buffer, Shieldstone Manual range with state overlay** | |

### Replacement Reserves (CRITICAL line item)

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | $250/unit/year minimum for conventional. Higher for property-type subprograms: Student Housing $250 (per Section 105.01, p. 219); Seniors Housing $300 no Skilled Nursing / $450 with Skilled Nursing (Section 505, p. 245); Cooperative $250 (Section 804.03, p. 310) | S&S Guide Part II Ch. 4 §406, p. 167; Part III Ch. 1 §105, p. 219; Part III Ch. 5 §505, p. 245 |
| Freddie Mac | PCA-driven amount, reviewed by Freddie Mac. Seniors Housing ranges: Age Restricted Excellent $150-250 / Average $250-350 / Major $350-450; Independent Living $200-300; Assisted Living $250-350; Skilled Nursing $300-400 (Chapter 21 §21.16, p. 402). Manufactured Housing Community: $50/Home Site/year plus $250/Manufactured Home/year (Chapter 22 §22.2(i), p. 414) | S/S Guide §39.3, p. 647-654; §62.6(f), p. 1086, 1102; Ch. 21 §21.16(e), p. 401-402; Ch. 22 §22.2(i), p. 414 |
| HUD MAP Guide | $250/unit/year MINIMUM ("In no event may this figure be less than $250 for any property"). Actual amount set by CNA e-Tool review. Rate of change capped at inflation. Minimum balance maintained per CNA financial plan | MAP Guide Appendix 5 §A.5.7 Capital Needs Assessments, p. 778 (Year 1 Annual Deposit Per Unit); §3.1.28, p. 70 |
| HUD ML 2025-03 | Not addressed (DSCR and LTV/LTC only) | n/a |
| Shieldstone Manual | **Vintage-tiered by age at UW date:** 0-10yr = $250/unit; 11-15yr = $300/unit; 16-20yr = $350/unit; 20+yr = $400/unit. Meets or exceeds the $250 agency floor at every tier. | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Replacement Reserves |
| **Triangulated UW** | **Use Shieldstone vintage-tiered values directly** for both EFB and ACQ. Agency $250 floor only binds at the new-build tier and Shieldstone matches it. No separate agency-resize sensitivity required. For 20+yr properties, $400 may still understate true capital needs over a 10-year hold; material renovation belongs in the capex budget (separate line). | |

### Capital Reserves (additional, separate from Replacement Reserves)

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Not generally required separate from Replacement Reserve. Completion / Repairs funding required if applicable (Section 405) | S&S Guide §405, p. 166 |
| Freddie Mac | Repair Reserve, Special Purpose Reserve, Rental Achievement Reserve required only when specified in Letter of Commitment | S/S Guide §39.3(a), p. 654 |
| HUD MAP Guide | Critical Repairs Escrow and Non-Critical Repairs Escrow per CNA. Lump-sum initial deposit may be required at endorsement | MAP Guide §5.10.7, p. 156; Appendix 5 §A.5.7.2, p. 119 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | Treat capex as separate budget; do not commingle with Replacement Reserves (which are an operating expense deduction from NOI) | [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) §Replacement Reserves |
| **Triangulated UW** | **PCA-determined critical repairs escrow at closing; not an ongoing operating expense** | |

### Property Tax (Reassessment)

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | For California Properties: Acquisitions trend at 2 percent; for refinances, no trending until actual tax bill surpasses underwritten taxes. Non-California: 3 percent for Structured Transactions and Mortgage Loans secured by multiple Properties; for all other Mortgage Loans, growth rates published in DUS Gateway | S&S Guide Part II Ch. 2 §204.01 Base Assumptions, Real Estate Taxes table, p. 136 |
| Freddie Mac | Reserve required per §39.2. Tax amount underwritten to actual / assessor projection | S/S Guide §39.2, p. 647 |
| HUD MAP Guide | Adjustments to real estate taxes may be permissible if anticipated tax reduction based on reassessment or reclassification. Three-year operating history baseline | MAP Guide §7.8.9, p. 223 |
| HUD ML 2025-03 | Not addressed | n/a |
| Shieldstone Manual | EFB: $0 (non-profit exemption). ACQ: state-specific reassessment ratio (FL 70 percent, TX 65 percent, GA 40 percent of new assessed value vs. purchase price). GA bond-lease: PILOT 40-60 percent of fee-simple | [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md) |
| **Triangulated UW** | **Use Shieldstone state-specific reassessment methodology; agencies accept the higher of actual / reassessment projection** | |

### Vacancy and Collection Loss (for context, supports NCF)

| Source | Minimum / Required | Citation |
|---|---|---|
| Fannie Mae | Use the underwritten economic vacancy rate. Cooperative Property: greater of 5 percent or highest level experienced during last 3 years | S&S Guide Part II Ch. 2 §204.01 Economic Vacancy, p. 136; Part III Ch. 8 §808.04 Cooperative exceptions, p. 310 |
| Freddie Mac | Per minimum levels specified in Letter of Commitment | S/S Guide Ch. 8 (Property Fundamentals) |
| HUD MAP Guide | Per Appendix 3 §A.3.1 minimums. Minimum 85 percent average physical occupancy; max 93 percent economic occupancy for market rate | MAP Guide §3.1.33, p. 72; §7.8.9, p. 222 |
| HUD ML 2025-03 | Vacancy Factor by program: 3 percent (90+ percent rental assistance), 5 percent (Affordable LIHTC), 7 percent (Market Rate / LIHTC w/o Rent Advantage) | ML 2025-03 Section III Table, p. 2 |
| Shieldstone Manual | Stabilized 5-7 percent in primary markets; higher in tertiary | [references/04-revenue.md](.skills/dream-underwrite/references/04-revenue.md) |
| **Triangulated UW** | **MAX of: HUD ML 2025-03 program-specific minimum (3-7 percent), Shieldstone benchmark, T-12 actual** | |

---

## Citation Convention for Phase 8 Output

When triangulating in the chat output or UW memo, cite the specific source per line. Example:

```
Replacement Reserves UW (2022-built deal, ~4 years old at 2026 UW = 0-10yr tier): $250/unit/year
  Fannie Mae S&S Guide Part III Ch. 1 §105.01 minimum: $250/unit (conventional floor)
  HUD MAP Guide Appendix 5 §A.5.7 minimum: $250/unit ("In no event may this figure be less than $250 for any property", p. 778)
  Freddie Mac S/S Guide §62.6(f): PCA-determined (no fixed floor for conventional)
  Shieldstone Manual (0-10yr tier): $250/unit
  T-12 actual: $190/unit x 1.03 = $196/unit

  Binding: Agency floor and Shieldstone Manual aligned at $250/unit. No agency resize required at refi.

Replacement Reserves UW (1998-built deal, 28 years old at 2026 UW = 20+yr tier): $400/unit/year
  Fannie / HUD floor: $250/unit (well below Shieldstone for this vintage)
  Shieldstone Manual (20+yr tier): $400/unit
  T-12 actual: $310/unit x 1.03 = $319/unit

  Binding: Shieldstone Manual $400. Agency floor is not constraining.
  Note: material 20+yr capital needs (system replacements) belong in capex budget, not reserves.
```

Insurance example:

```
Insurance UW: $1,180/unit/year
  Fannie S&S Guide Part II Ch. 2 §203.01 Item 17(c) (page 126): bona fide quote required; for acquisition use purchaser's carrier; 105-110 percent escalation on existing policies
  HUD MAP Guide §3.9 (page 92-94): 80 percent of insurable improvements or insured mortgage balance, whichever is lower
  Shieldstone Manual §4.3 Class B coastal FL: $700-1,200/unit plus 15-25 percent acquisition buffer plus 20-30 percent coastal FL premium
  T-12 actual: $1,025/unit x 1.15 (hardening buffer) = $1,179/unit

  Binding: T-12 plus hardening buffer ($1,179). Pro forma $1,180 sits at floor, supported by current broker quote.
```

This citation chain becomes the audit trail in the underwriting memo and the IC package.

---

## Flag Threshold

Flag any line item where the agency minimums and Shieldstone Manual disagree by more than 15 percent. Examples:

- "Insurance: Fannie minimum $950/unit (bona fide quote method) vs. Shieldstone $700-1,200, 35 percent gap on low end. Shieldstone benchmark too low for Class B coastal FL; defer to Fannie floor."
- "R&M: HUD MAP Guide three-year average for comparable property $400/unit vs. Shieldstone T-12 x 1.05 = $315/unit for this 2022 build, 27 percent gap. HUD/comparable binds; pro forma at $400/unit."
- "Replacement Reserves (2022 vintage, 0-10yr tier): Shieldstone Manual $250/unit matches Fannie/HUD floor. No gap, no flag. Confirm vintage tier in chat."
- "Replacement Reserves (1998 vintage, 20+yr tier): Shieldstone Manual $400/unit vs. Fannie/HUD $250/unit floor = +60% premium. Shieldstone binds. Material 20+yr system replacement risk noted; consider whether incremental capex is needed beyond reserve line."

When disagreement greater than 15 percent occurs, note the binding source explicitly and explain the rationale.

---

## Where the Agencies Are Silent

Important caveat: Fannie Mae, Freddie Mac, and the HUD MAP Guide do NOT publish $/unit minimums for most OpEx line items (payroll, G&A, marketing, R&M, turnover, contract services, utilities). They instead:

1. Define what GOES IN each NCF expense category (Fannie's 17(d)-17(j) line-item taxonomy)
2. Require comparable property analysis and three-year operating history (HUD MAP §7.8)
3. Defer to appraiser conclusions and PCA reports for property-specific support

For these line items, the binding source on most deals is the Shieldstone manual benchmark OR T-12 actual + 3 percent growth. The agency floor only binds where it is explicitly published, which is currently:

- Property management fee: 3 percent of EGI (Fannie) or 2.5 percent floor with $500/unit minimum
- Replacement Reserves: $250/unit/year (Fannie conventional, HUD MAP)
- Replacement Reserves Seniors Housing: $300-450/unit (Fannie), $200-450/unit by condition (Freddie)
- Replacement Reserves MHC: $50/site + $250/home (Freddie)
- Insurance: bona fide broker quote method (Fannie)
- Vacancy: 3-7 percent by program type (HUD ML 2025-03)
- DSCR / LTV / LTC: per HUD ML 2025-03 sizing table (for HUD-insured loans only)

For every other line item, the underwriter must defend the pro forma using Shieldstone manual + T-12 actuals + comparables, knowing the agency will scrutinize at refinance but will not pre-publish a floor.

---

## Why This Phase Matters

Phase 7 (per [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md)) gets the operating expense pro forma to a Shieldstone-standard baseline. Phase 8 stress-tests that baseline against the agencies that will refinance the deal. If the Phase 7 pro forma is below agency minimums, the agency will refuse to size the refi at the underwritten loan amount, an NOI shortfall happens at the worst possible time, and the IRR collapses.

The triangulation is not just defensive, it is also a forward-looking discipline. By forcing the UW to clear agency floors at acquisition, the model assumes the refinance will actually happen at the projected proceeds, which feeds the entire IRR calculation.

---

## Failure Modes to Avoid

1. **Skipping Phase 8:** running Phase 7 only and assuming Shieldstone benchmarks match agency floors. They usually do, but the 5-10 percent of cases where they don't break the deal.
2. **Citing generic "agency standards" without section refs:** undermines the audit trail and gives counsel/IC no way to verify. Always cite by chapter, section, and page number.
3. **Using stale manual versions:** agency manuals update at least annually. Refresh quarterly per [agency-manuals/README.md](../../../shieldstone_acquisitions/agency-manuals/README.md). HUD's MAP Guide March 2021 version is the most recent consolidated PDF; check the HUD Multifamily Policy Drafting Table for in-progress chapter revisions before quoting a number that has not been confirmed by a recent Mortgagee Letter.
4. **Forgetting state-specific overlays:** Texas hail, Florida hurricane, and coastal exposure add to insurance floors beyond what the federal manuals capture. Apply [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md) state-specific overlays on top of agency floors.
5. **Misreading the 2014 attachment as current:** the 2014 attachment to ML 14-02 is SUPERSEDED for DSCR and LTV/LTC by ML 2025-03. Do not cite figures from [hud/223f-refinance-standards-2014-01-SUPERSEDED.pdf](../../../shieldstone_acquisitions/agency-manuals/hud/223f-refinance-standards-2014-01-SUPERSEDED.pdf).

---

## Refresh Note

Re-extract these tables when any of the four underlying PDFs is updated:

- [fannie-mae/multifamily-selling-servicing-guide-2026-04.pdf](../../../shieldstone_acquisitions/agency-manuals/fannie-mae/multifamily-selling-servicing-guide-2026-04.pdf) (Fannie publishes effective dates with each release)
- [freddie-mac/multifamily-seller-servicer-guide-2026-04.pdf](../../../shieldstone_acquisitions/agency-manuals/freddie-mac/multifamily-seller-servicer-guide-2026-04.pdf) (Freddie publishes via AllRegs)
- [hud/map-guide-4430G-2021-03.pdf](../../../shieldstone_acquisitions/agency-manuals/hud/map-guide-4430G-2021-03.pdf) (no full revision since March 2021; chapter-level drafts on HUD Multifamily Policy Drafting Table)
- [hud/mortgagee-letter-2025-03.pdf](../../../shieldstone_acquisitions/agency-manuals/hud/mortgagee-letter-2025-03.pdf) (current 223(f) DSCR / LTV / LTC overlay; check HUDClips for newer ML)

The [agency-manuals/README.md](../../../shieldstone_acquisitions/agency-manuals/README.md) tracks publication dates and lists known stale references.

Last extracted: 2026-05-13 from the four PDFs above.

---

## See Also

- [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md), Phase 7 operating expense framework (Shieldstone-manual benchmarks)
- [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md), distilled Shieldstone Manual standards
- [shieldstone_acquisitions/agency-manuals/](../../../shieldstone_acquisitions/agency-manuals/), saved agency UW manuals (firm-wide resource)
- [references/09-acq-financing.md](.skills/dream-underwrite/references/09-acq-financing.md), agency refinance underwriting (consumes Phase 8 triangulation output)
- [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md), T-12 mapping (Tier 3 input to triangulation)
