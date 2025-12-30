# Shieldstone Underwriting Standards - Quick Reference

**Purpose:** Quick lookup for critical standards, formulas, and thresholds used in Shieldstone underwriting methodology.

**Full Manual:** See `docs/shieldstone_technical_UW_manual_v1.md`

---

## Financing Standards

### Loan Structure
```
LTV: 65% of purchase price (NOT total project cost)
IO Period: 30 months
Amortization: 30 years (after IO)
Rate: Current 5yr Treasury + 150bps
```

### Equity Requirements
```
Total Equity = Down Payment + Closing Costs + 100% of Capex
Down Payment = Purchase Price - Loan Amount
Closing Costs = 3% of Purchase Price (typical)
```

### Loan Sizing Constraints
```
Loan Amount = MIN(LTV Loan, DSCR Loan)
LTV Loan = Purchase Price × 65%
DSCR Loan = Stabilized NOI / (DSCR × Annual Payment Factor)
DSCR Requirement: 1.25x (typical)
```

---

## Return Requirements

### Absolute Minimums
```
IRR: 12%
Stabilized Cash-on-Cash: 6%
Equity Multiple (5yr): 1.4x
```

### Market Tier Base Hurdles

| Market Tier | IRR Range | CoC Year 1 | CoC Stabilized | EM 5yr |
|-------------|-----------|------------|----------------|--------|
| **Gateway** | 14-16% | 6-8% | 8-10% | 1.6-1.8x |
| **Secondary** | 16-19% | 7-9% | 9-12% | 1.7-2.0x |
| **Tertiary** | 18-22% | 9-12% | 12-15% | 1.9-2.2x |

### Risk Adjustments (bps added to base hurdle)

| Risk Factor | Adjustment |
|-------------|------------|
| Heavy construction | +200 bps |
| Low occupancy (<85%) | +150 bps |
| Property age >30 years | +100 bps |
| Market downturn | +150 bps |
| Floating rate debt | +100 bps |

**Calculation:**
```
Adjusted Hurdle = Base Hurdle + Sum of Risk Adjustments
Final Hurdle = MAX(Adjusted Hurdle, Absolute Minimum 12%)
```

---

## Deal Screening Criteria

### Hard Disqualifiers
```
Minimum Units: 50
Maximum Property Age: 40 years
Minimum Occupancy: 70%
Maximum Crime: 2x national average (violent crime)
```

### Location Checks
- ❌ Declining market (negative population/employment trends)
- ❌ High-crime area (>2x national violent crime)
- ❌ Major structural issues
- ❌ Environmental contamination
- ❌ Severe flood risk (FEMA Zone A/V)

---

## Property Tax (Florida)

### Reassessment Ratio
```
Reassessment Ratio: 70% (NOT 100%)
Annual Growth: 3% (conservative)
```

**⚠️ CRITICAL:** Always call county assessor to confirm reassessment ratio.

**Calculation:**
```
New Tax = Current Tax × (Purchase Price / Assessed Value) × 0.70
Annual Tax Growth = Previous Year Tax × 1.03
```

---

## Revenue Underwriting

### Renovation Rent Premiums

| Scope | Cost/Unit | Expected Premium | Items |
|-------|-----------|------------------|-------|
| Light | $5,000 | 5% | Paint, clean carpet, minor fixtures |
| Moderate | $12,000 | 10% | Flooring, appliances, countertops |
| Heavy | $20,000 | 15% | Full kitchen, full bath, HVAC |
| Luxury | $30,000 | 20% | Designer finishes, layout changes |

### Age Adjustments
```
Age Factor:
  ≤20 years: 1.00x
  21-30 years: 1.10x
  >30 years: 1.20x

Adjusted Cost/Unit = Base Cost × Age Factor
```

### Rent Growth Assumptions
```
Conservative: 2-3% annually
Market-based: Use 3-year historical + market projections
Stress Test: Apply 15-20% haircut if uncertain
```

---

## Operating Expenses

### Expense Benchmarks (per unit per year)

| Expense Category | Typical Range | Notes |
|-----------------|---------------|-------|
| Property Tax | $800-$1,500 | Varies by state/county |
| Insurance | $300-$600 | Property + liability |
| Payroll | $400-$800 | On-site staff |
| Management Fee | 3-5% of revenue | Third-party |
| Repairs & Maintenance | $600-$1,200 | Age-dependent |
| Utilities | $200-$500 | Common area |
| Replacement Reserves | $300-$600 | CapEx reserve |

### Property Tax Calculation (Florida)
```
Year 1 Tax = Current Tax × (Purchase Price / Assessed Value) × 0.70
Year N Tax = Year N-1 Tax × 1.03
```

### Replacement Reserves
```
Typical: $300-$600 per unit per year
Age Adjustment:
  ≤20 years: $300/unit/year
  21-30 years: $450/unit/year
  >30 years: $600/unit/year
```

---

## Capital Expenditure Planning

### Renovation Budget Components
```
Total Capex = Interior + Exterior/Common + Contingency

Interior = Cost/Unit × Unit Count × Age Factor
Exterior/Common = Interior × 17.5%
Contingency = (Interior + Exterior) × Contingency %

Contingency %:
  ≤20 years: 10%
  >20 years: 15%
```

### ROI Validation
```
Rent Increase = Current Rent × Premium %
Annual NOI Increase = Rent Increase × 12 × Unit Count
Achievable NOI Increase = Annual NOI Increase × 0.75 (vacancy/concessions)
Cash-on-Cash ROI = Achievable NOI Increase / Total Capex

⚠️ REQUIRED: ROI must exceed 8% cash-on-cash
```

---

## Returns Calculations

### Cash-on-Cash Return
```
CoC = Annual Cash Flow / Total Equity Invested

Annual Cash Flow = NOI - Debt Service
Total Equity = Down Payment + Closing Costs + Capex
```

### IRR Calculation
```
IRR = Rate where NPV = 0

Cash Flow Array = [-Total Equity] + [Annual CF Years 1-N] + [Exit Proceeds]
```

### Equity Multiple
```
Equity Multiple = Total Distributions / Total Equity Invested

Total Distributions = Sum(Annual Cash Flows) + Exit Proceeds
```

### Exit Cap Rate
```
Exit Value = Stabilized NOI / Exit Cap Rate
Exit Cap Rate = Going-In Cap Rate ± Market Adjustment

Typical Range: 4.5% - 6.5% (market dependent)
Conservative: Use higher cap rate (lower value)
```

---

## Risk Assessment

### Execution Risk Scoring (35% weight in overall risk)

| Scope | Base Risk (bps) |
|-------|----------------|
| Light | 0 |
| Moderate | 50 |
| Heavy | 150 |
| Luxury | 200 |

### Age Adjustments
```
Property Age >30: +100 bps
Property Age 21-30: +50 bps
Property Age ≤20: 0 bps
```

### Contractor Experience
```
Proven: 0 bps
Moderate: +50 bps
Limited: +150 bps
```

### Risk Rating Thresholds
```
Total Adjustment:
  ≥300 bps: SEVERE
  200-299 bps: HIGH
  100-199 bps: MODERATE
  <100 bps: LOW
```

---

## Due Diligence Timeline

### Phase I: Days 1-10 (Soft DD)
```
Day 1: Data room access
Day 3: Document quality assessment
Day 5: Financial reconciliation
Day 7: Property tax research + initial site visit
Day 10: ⚠️ GO/NO-GO DECISION (full refund if walk)
```

### Phase II: Days 11-45 (Hard DD)
```
Day 11: Hard money wired ($300K non-refundable)
Day 14: 100% property inspection
Day 21: Lease audit complete
Day 25: PCA received
Day 28: Phase I ESA received
Day 30: Appraisal received
Day 35: Contractor bids received
Day 40: All findings resolved
Day 43: Investment Committee approval
Day 44: Final walkthrough
Day 45: ⚠️ CLOSING (earnest money at risk)
```

---

## Exit Strategy

### Optimal Exit Timing
```
Minimum Hold: 12 months (for long-term capital gains)
Renovation Complete: Acquisition + Renovation Timeline
Stabilization: Renovation Complete + 18 months
Optimal Exit: Acquisition + 48 months
```

### Tax Impact
```
Long-Term Capital Gains (≥12 months):
  Federal Rate: 20% + 3.8% NIIT = 23.8% effective

Short-Term Capital Gains (<12 months):
  Federal Rate: 37% + 3.8% NIIT = 40.8% effective

Tax Savings (LTCG vs STCG): ~17% of capital gain
```

---

## Variance Analysis Thresholds

### Contingency Release Decision

| Variance | Decision |
|----------|----------|
| IRR < 12% absolute minimum | WALK |
| IRR declined >20% | RE-TRADE |
| Capex increased >20% | RE-TRADE |
| IRR declined 10-20% | PROCEED WITH CAUTION |
| All within tolerance | PROCEED |

### PCA Variance Analysis

| Variance % | Severity | Action |
|-------------|----------|--------|
| >30% | CRITICAL | Re-trade or walk |
| 15-30% | HIGH | Request seller credit |
| 5-15% | MODERATE | Increase contingency |
| <5% | LOW | Budget validated |

---

## Underwriting Philosophy

### Conservative Bias Principles
1. **Market comps trump broker projections**
2. **Stress test every base case**
3. **Apply 15-20% haircut when uncertain**
4. **Never violate absolute minimums**
5. **Always confirm critical assumptions** (e.g., property tax with county)

### Data Quality Standards
```
Document Quality Score: >70 required
Rent Roll vs T-12 Variance: <5% acceptable
PCA vs Underwritten Capex: <15% variance acceptable
```

---

## Market Tier Classification

### Gateway Markets
```
Top 10 MSAs: NYC, LA, SF, CHI, DC, BOS, SEA, MIA, DAL, HOU
Population: >2M MSA
Diversification: High (multiple industries)
```

### Secondary Markets
```
MSA Population: 500K - 2M
Examples: Austin, Nashville, Raleigh, Phoenix, Tampa
Diversification: Moderate to high
```

### Tertiary Markets
```
MSA Population: <500K
Diversification: Lower (single industry risk)
```

---

## Quick Calculation Examples

### Example 1: Risk-Adjusted Hurdle
```
Market: Secondary (base 17.5%)
Heavy renovation: +200 bps
Low occupancy (78%): +150 bps
Floating rate debt: +100 bps

Adjusted Hurdle = 17.5% + 2.0% + 1.5% + 1.0% = 22.0%
Final Hurdle = MAX(22.0%, 12.0%) = 22.0%
```

### Example 2: Renovation Budget
```
Property: 180 units, 27 years old, Heavy scope
Base Cost: $20,000/unit
Age Factor: 1.10 (27 years)

Cost/Unit = $20,000 × 1.10 = $22,000
Interior = $22,000 × 180 = $3,960,000
Exterior = $3,960,000 × 17.5% = $693,000
Contingency = ($3,960,000 + $693,000) × 15% = $697,950
Total Capex = $5,350,950
```

### Example 3: Loan Sizing
```
Purchase Price: $12,700,000
LTV Loan: $12,700,000 × 65% = $8,255,000
Stabilized NOI: $1,250,000
DSCR Required: 1.25x
Rate: 5.75%, 30yr amort

Annual Payment Factor: ~0.068
DSCR Loan: $1,250,000 / (1.25 × 0.068) = $14,705,882

Loan Amount = MIN($8,255,000, $14,705,882) = $8,255,000
Binding Constraint: LTV
```

---

**Last Updated:** 2025-01-XX  
**Version:** Quick Reference v1.0  
**For detailed explanations, see:** `docs/shieldstone_technical_UW_manual_v1.md`

