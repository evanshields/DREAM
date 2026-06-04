# 11: Data Extraction Protocols

## Overview

This reference covers how to parse and normalize the four primary source documents used in multifamily underwriting: rent rolls, T-12 operating statements, rent comps, and sales comps. Each document type has unique formatting challenges, this guide helps Claude extract clean, structured data regardless of source format. Used at Phase 1 (T-12 spread), Phase 2 (rent roll), and Phase 11 (comps build).

## Rent Roll Extraction

### Common Formats
- **Yardi/RealPage exports:** Excel or PDF with GL codes (e.g., "4000 Rent Income", "4530 Utility Income")
- **Broker OM rent rolls:** Simplified PDF tables, often missing charge detail
- **AppFolio/Buildium:** CSV exports with tenant-level detail

### Fields to Extract

| Field | Where to Find It | Notes |
|---|---|---|
| Unit Number | Column A or first column | May include building prefix (e.g., "R14", "T46") |
| Tenant Name | Column B | "VACANT" indicates empty unit |
| Bed/Bath | Column E or unit type column | "2 Bed/1 Bath", "3 Bed/2 Bath", etc. |
| Lease Start | Column C | Date format varies |
| Lease End | Column D | "at-will" = month-to-month |
| Base Rent | Column H | Scheduled rent (may differ from total charges) |
| Total Charges | Column K | Rent + utility reimbursement + pet rent + other |
| Deposits Held | Column L | Security deposit amount |
| Rent Start Date | Column G | When current rent took effect |

### Key Processing Steps

1. **Identify unit rows vs. charge detail rows.** Yardi-style rent rolls alternate between unit header rows (with tenant name, dates) and charge detail rows (GL codes like "4000 Rent Income", "4530 Utility Income"). Only unit header rows count for the unit mix.

2. **Separate rent from utility reimbursements.** The "Total Charges" column often includes RUBS charges ($25/month typical). Base rent is the "4000 Rent Income" line. Don't use total charges as "rent."

3. **Identify renovation status.** Look for unit type suffixes: "SLV" (silver), "GLD" (gold), "RENO", "UPGRADED", "CLASSIC". If not labeled, compare rents, a $1,324 unit in a sea of $1,195 units was likely renovated.

4. **Flag vacant units.** Tenant = "VACANT" or blank. Also flag "PENDING LEASE" or "NOTICE" units.

5. **Backfill missing SF from CoStar unit mix.** Yardi exports often omit SF on the rent roll. If the SF column is blank for any unit type, map the unit-type code (e.g., "2x2", "A2", "B1") to SF from the CoStar Property Summary that was uploaded at the start of the deal. Document the backfill source in chat. Do NOT leave SF blank in the model, every PSF calc downstream depends on it.

6. **Calculate key metrics:**
   - Total units (count unit header rows, excluding storage/office)
   - Occupied units (exclude VACANT)
   - Physical occupancy = Occupied ÷ Total
   - Average rent by unit type (occupied units only)
   - Weighted average rent (all occupied units)

7. **Reconcile rent roll GPR to T-12 GPR within 5%.** Compute implied annual GPR from the rent roll (avg in-place rent × occupied units × 12 + asking rent × vacant units × 12). Compare to T-12 GPR for the same period. If the gap is greater than 5%, either the snapshot dates differ (rent roll vs. T-12 mid-period vs. period-end) or there is a unit-mix issue. Surface the gap in chat with the most likely cause. Example: Esplanade had $4.17M implied RR GPR vs. $4.27M T-12 GPR, a 2.4% gap, which flagged late-2025 vacancy creep the rent roll did not yet show.

### Output Format for Model
```
Unit Type | # Units | SF | In-Place Rent | Rent PSF
2BR/2BA Unreno | 21 | 1,066 | $1,195 | $1.12
2BR/2BA Reno | 100 | 1,066 | $1,324 | $1.24
3BR/2BA Unreno | 18 | 1,260 | $1,195 | $0.95
3BR/2BA Reno | 47 | 1,260 | $1,324 | $1.05
```

## T-12 Forensic Analysis: Automatic Deliverable

After a T-12 is uploaded, ALWAYS provide an unprompted forensic analysis before mapping
line items to the model. This analysis is a standard deliverable on every deal, do not
wait for the user to ask.

### Required Analysis (All Deals)

**0. T-3 / T-6 / T-12 Annualized Comparison (lead deliverable)**

This is the single most important view in the forensic analysis. Always present it FIRST, as a standalone block, before drilling into individual line items:

| Period | Annualized GPR | Annualized OpEx | Annualized NOI | Annualized Vacancy % |
|---|---|---|---|---|
| T-12 | $ | $ | $ | % |
| T-6 (Jul-Dec) | $ | $ | $ | % |
| T-3 (Oct-Dec) | $ | $ | $ | % |
| Delta T-12 → T-3 | +/- $ | +/- $ | +/- $ | +/- bps |

The delta row tells the story. A T-12 NOI that looks healthy but a T-3 that is sharply lower means the property is rolling down RIGHT NOW. The Aug-Dec 2025 vacancy ramp on Esplanade would have been invisible without this comparison, the T-12 still reflected the strong early-2025 period.

For lease-up properties, the T-3 is the best proxy for stabilized run-rate; the T-12 is artificially depressed.

**1. Monthly Vacancy Trend**
- Calculate trailing T-12, T-6, and T-3 annualized occupancy rates
- Note trajectory: improving, deteriorating, or flat
- Flag if T-12 average vacancy > 10% (potential lease-up or distress signal)

**2. Concession Trend**
- Separate move-in concessions from renewal concessions (if data allows)
- Calculate concessions as % of GPR (T-12, T-6, T-3)
- Flag if concessions > 5% of GPR (aggressive leasing, may not sustain)

**3. Loss-to-Lease Trajectory**
- Compare earliest-month vs. latest-month average in-place rent
- Calculate whether the gap between asking and in-place rent is widening or narrowing
- Widening loss-to-lease = management falling behind market; narrowing = catching up

**4. Bad Debt / Collections**
- Report bad debt as % of GPR (annualized)
- Flag if > 3% of GPR (chronic collections problem)
- Note any month-to-month spikes (may indicate eviction batch or policy change)

**5. Expense Anomalies**
- Flag any line item dropping to $0 mid-year (seller cut services to inflate NOI)
- Flag one-time items: bonuses, referral fee spikes, legal settlements, insurance proceeds
- Flag mid-year service additions or removals (new security contract, dropped landscaping)
- Normalize anomalies when recommending pro forma assumptions

**6. NOI Trajectory**
- Calculate T-12, T-6, and T-3 annualized NOI
- Show which direction NOI is trending and identify the primary driver(s)
- For lease-up properties: focus on the T-3 as the best indicator of stabilization

**7. Key Takeaways for Underwriting**
- Summarize 3–5 bullet points: what does this T-12 tell us about operating momentum?
- Explicitly state whether the T-12 is representative of stabilized operations
- If NOT representative (lease-up, distressed, seller manipulation), state that pro forma
  should be built from comp-validated assumptions rather than T-12 extrapolation

### Aged Receivables Analysis (If Uploaded)

If an aged receivables report is also provided, append:
- **Net position by unit:** charges vs. payments, number of units with balances
- **Delinquency concentration:** how many units drive the total outstanding balance?
- **Aging buckets:** current / 30-day / 60-day / 90+ day breakdown
- **Collections health assessment:** healthy (< $50/unit average, 80%+ current),
  moderate ($50–150/unit, 60–80% current), or distressed (> $150/unit or < 60% current)

### Lease-Up Property Flag

If any of these conditions are true, explicitly flag the property as a lease-up:
- T-12 average vacancy > 15%
- Concessions > 5% of GPR
- Property delivered within 24 months of the T-12 period
- NOI is negative for 3+ months in the T-12

For lease-up properties:
- Do NOT extrapolate T-12 expenses as pro forma baseline for variable costs
- DO use T-12 for fixed costs (insurance, taxes, contracts) as they are representative
- Build pro forma revenue from rent comps and AMI/FMR ceilings, not T-12 revenue
- Size an interest reserve if Year 1 DSCR < 1.15x (see [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md) §Interest Reserve)

## T-12 Extraction

### Common Formats
- **Monthly columns:** 12 months of actual data side by side (most common)
- **Annual summary:** Single column with annual totals
- **Yardi GL export:** Detailed GL codes, often 80+ line items

### Parsing Protocol (REQUIRED before any cell is written)

Phase 1 of the master workflow cannot write a single cell into the T-12 Inputs tab until this protocol completes. The Esplanade deal exposed two failure modes that this protocol prevents: (a) fabricating monthly distributions from an annualized source, and (b) silent fuzzy-mapping of GL labels to categories.

**Step 1: Parse source with openpyxl FIRST.** Read the source T-12 .xlsx with `openpyxl` (do not just look at it in chat). Inspect column headers programmatically. Verify that all 12 monthly columns are present and labeled (typically Jan-Dec or Mo1-Mo12). If headers are ambiguous, read row 1-3 of the source to identify them, do not guess.

**Step 2: If only annuals are available, write column O only.** If the source provides annual totals only (no monthly columns), write to column O and leave C through N blank. Add an explicit chat note:

> "Source provided annual values only. Monthly cells C-N left blank per universal rule. Do NOT infer monthly distribution from annualized values, downstream T-3/T-6 forensics will be unavailable for this deal."

Never fabricate monthly distributions from an annual figure (e.g., dividing by 12 and writing the same value to every month). This corrupts the forensic deliverable.

**Step 3: Build an explicit row-keyed mapping dict.** For every line item in the source T-12, map it to the model category by exact match against a hard-coded dictionary. Example:

```python
MAPPING = {
    "Apartment Rental Income": "GPR",
    "Trash Fee": "Utility Reimbursements",
    "Pest Control Fee": "Utility Reimbursements",
    "Insurance Premiums": "Insurance",
    "Management Fee - 3%": "Property Management",
    # ... etc per the full T-12 line item list
}
```

NEVER fuzzy-match. Never use string similarity, contains-substring, or LLM intuition to bridge a label gap. Either the label is in the dictionary or it is not.

**Step 4: Print unmapped count before writing.** Iterate every line item in the source. Count those NOT in the dictionary. Print to chat:

> "T-12 mapping audit: 47 line items in source, 47 mapped, 0 unmapped. Ready to write."

If any line item is unmapped, STOP. Show the unmapped labels in chat. Ask the user to either (a) confirm the label maps to a category (and add to the dict for the session), or (b) confirm the line item is excluded. Do not proceed with non-zero unmapped count.

**Step 5: Verify col O rollups tie to source subtotals.** After writing to columns C through O, read column O back. Roll up by category (sum all rows mapped to "GPR", all rows mapped to "Insurance", etc.). Print each category total alongside the expected source subtotal:

```
Category Rollup Audit (col O vs. source subtotals):
  GPR:                   $4,267,431  vs.  $4,267,431  [OK]
  Utility Reimbursements:$  187,442  vs.  $  187,442  [OK]
  Insurance:             $  108,914  vs.  $  108,914  [OK]
  Property Management:   $  113,189  vs.  $  113,189  [OK]
  ...
```

**Mismatches greater than $1 fail the phase.** Stop. Do not advance to Phase 2. Investigate the discrepancy: (a) was a line item double-counted, (b) was a sign flipped (negative income written as positive), (c) was a row missed?

### Mapping T-12 Line Items to Model Categories

| Model Category | Typical T-12 GL Codes |
|---|---|
| **Property Management** | Management Fees (6050, 6055) |
| **Payroll** | Payroll & Taxes (7011), Employee Benefits, Workers Comp |
| **G&A** | Office (6040), Legal, Bank Charges, Software, Collections |
| **Marketing** | Advertising, Leasing Commissions, Signage |
| **Turnover** | Make-Ready, Cleaning, Painting (unit-turn related) |
| **R&M** | Repairs & Maintenance (6015), excluding capex-quality items |
| **Contract Services** | Landscaping (5015), Garbage (5004), Pest Control, Security/Patrol, Pool, Elevator |
| **Utilities (Gross)** | Electric, Gas, Water/Sewer, Trash (owner-paid portions) |
| **Utility Reimbursements** | Utility Income (4530), RUBS recovery |
| **Real Estate Taxes** | Real Estate Taxes (6010), Non-Ad Valorem |
| **Insurance** | Insurance (6030), Liability, Property |
| **Capital Reserves** | Replacement Reserves (if expensed, not capex) |

### RUBS Classification Trap (CRITICAL)

Items in the T-12 "Other Income" section that MUST be categorized as `Utility Reimbursements`, NOT as Other Income:
- Water Revenue, Water Income, Water Submeter
- Electric Reimbursable, Electric Submeter
- Utility Administration Fee
- Trash Service Fee
- Pest Fees

If these end up in Other Income, the pro forma double-counts utility recovery (once via RUBS recovery assumption, once via Other Income) and overstates EGI by 5–10%.

### Red Flags to Identify in T-12
- **Line items dropping to $0 mid-year:** Seller cut services to inflate NOI
- **Spike in concessions:** Aggressive leasing ahead of sale
- **Bad debt >3% of GPR:** Chronic collections problems
- **Late charges >$500/unit/year:** Tenant financial stress signal
- **Inconsistent management fee %:** May indicate related-party pricing
- **Abnormally low payroll:** May be understaffed
- **Near-stabilized lease-up bonuses ($50–150K):** Strip from stabilized pro forma

### Output Format
```
Category | T-12 Total | T-12 $/Unit | Pro Forma $/Unit | Pro Forma Total | Notes
PM | $113,189 | $609 | $703 | $130,808 | 3% of EGI
Payroll | $346,669 | $1,864 | $1,864 | $346,704 | UW to T-12
...
```

## Rent Comp Extraction

### Fields to Extract
| Field | Notes |
|---|---|
| Property name | Comp property |
| Address/submarket | Distance from subject |
| Year built | Vintage comparison |
| Unit count | Scale comparison |
| Unit type | 1BR, 2BR, 3BR |
| Asking rent | Current advertised rent |
| Rent PSF | Rent ÷ SF |
| Concessions | Free months, move-in specials |
| Renovation status | Classic vs. renovated |
| Amenities | Pool, fitness, W/D in-unit, etc. |
| Data source | CoStar, Apartments.com, manual survey |

### Comp Selection Criteria
- Same submarket (ideally same zip code)
- Similar vintage (±10 years)
- Similar unit count (±50%)
- Similar class/amenity package
- Leased within last 6 months

### Analysis Output
```
Percentile ranking of subject vs. comps
Premium/discount to submarket average
Rent achievability assessment by tier
```

## Sales Comp Extraction

### Fields to Extract
| Field | Notes |
|---|---|
| Property name | Comp property |
| Sale date | Within 24 months preferred |
| Sale price | Total and $/unit |
| Cap rate | If available |
| Year built | Vintage |
| Unit count | Size comparison |
| Condition at sale | Value-add, stabilized, etc. |
| Buyer type | Institutional, private, REIT |

### Usage in Underwriting
- Validates exit $/unit assumption
- Feeds Method 2 of exit cap triangulation per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md)
- Provides market context for IC presentation

## General Extraction Tips

1. **Always verify unit count.** Rent rolls may include non-residential units (office, storage, model). Exclude from unit count.
2. **Reconcile T-12 to rent roll.** T-12 revenue should approximately equal (avg rent × occupied units × 12). Large discrepancies signal data quality issues.
3. **Normalize for annualization.** If T-12 covers 14 months (common with Yardi exports), normalize to 12.
4. **Strip out one-time items.** Insurance settlements, legal recoveries, capital reimbursements, these inflate T-12 income artificially.
5. **Document data sources.** For every assumption, note whether it came from the rent roll, T-12, broker OM, or external research.

## See Also

- [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md), Other Income three-tier classification
- [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md), pro forma expense assumptions per category
- [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md), comp curation and Comps tab population
- [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md), exact cells for T-12 Inputs and OpEx population
