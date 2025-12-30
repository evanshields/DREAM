# Commercial Real Estate Underwriting Concepts

> A practical guide to understanding multifamily investment metrics for analysts, investors, and principals

**Last Updated:** December 20, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Property Fundamentals](#property-fundamentals)
3. [Financial Metrics](#financial-metrics)
4. [Return Calculations](#return-calculations)
5. [Risk Assessment](#risk-assessment)
6. [Market Analysis](#market-analysis)
7. [Valuation Methods](#valuation-methods)
8. [Financing Structures](#financing-structures)
9. [Value-Add Strategies](#value-add-strategies)
10. [Exit Strategies](#exit-strategies)
11. [Due Diligence](#due-diligence)
12. [Common Pitfalls](#common-pitfalls)

---

## Introduction

Commercial real estate underwriting is the process of analyzing an investment opportunity to determine whether it meets your investment criteria and generates acceptable risk-adjusted returns. This guide explains key concepts using DREAM AI's Shieldstone methodology.

### What Makes Good Underwriting?

**Institutional-quality underwriting has three characteristics:**

1. **Transparent**: Every assumption is documented with rationale
2. **Defensible**: Inputs are supported by market data and comparable transactions
3. **Conservative**: Assumptions err on the side of caution, not optimism

DREAM AI enforces these principles automatically while accelerating the process from hours to minutes.

---

## Property Fundamentals

### Property Classification

**Class A**
- Built within last 15 years or extensively renovated
- High-end finishes and amenities
- Premium location
- Attracts high-income renters
- Lower cap rates, lower yields

**Class B** (DREAM AI sweet spot)
- Built 15-30 years ago
- Solid but not luxury finishes
- Good location, may not be premium
- Middle-income renters
- Moderate cap rates, value-add potential

**Class C**
- Built 30+ years ago
- Basic finishes
- Secondary locations
- Lower-income renters
- Higher cap rates, higher operational risk

**Why Class B?** Most institutional value-add strategies target Class B properties because they:
- Have proven demand and stable operations
- Offer rent growth potential through light renovations
- Maintain lower risk than Class C
- Provide better returns than Class A

### Unit Mix

The distribution of unit types in a property:

```
Example: Oakwood Apartments (168 units)
├─ 1BR (48 units, 750 SF) = 28.6% of units
├─ 2BR (96 units, 1,100 SF) = 57.1% of units
└─ 3BR (24 units, 1,350 SF) = 14.3% of units
```

**Why It Matters:**
- 2BR units typically have best demand/rent trade-off
- Unit mix should match submarket demographics
- Renovation returns vary by unit type

### Occupancy Metrics

**Physical Occupancy:** Percentage of units with paying tenants

```
Formula: Occupied Units / Total Units
Example: 160 occupied / 168 total = 95.2% occupancy
```

**Economic Occupancy:** Accounts for concessions and unpaid rent

```
Formula: (GPR - Vacancy Loss - Concessions - Bad Debt) / GPR
```

**Target Ranges:**
- **Excellent:** 95%+ physical, 93%+ economic
- **Good:** 90-95% physical, 88-93% economic
- **Concerning:** <90% physical, <88% economic

---

## Financial Metrics

### Revenue

**Gross Potential Rent (GPR)**
- Total rent if 100% occupied at current rates
- `Formula: Sum of (Units × Rent) across all unit types`

**Effective Gross Income (EGI)**
- Actual collectible income after vacancy, concessions, bad debt
- `Formula: GPR - Vacancy Loss + Other Income`

**Other Income**
- Pet fees, parking, laundry, utility reimbursements, etc.
- Typically $300-600 per unit per year
- Often overlooked but improves returns

**Example:**
```
GPR:                     $2,950,000
Vacancy Loss (5%):       ($147,500)
Other Income:            $71,400
─────────────────────────────────
EGI:                     $2,873,900
```

### Operating Expenses

**Typical Operating Expenses (per unit per year):**

| Category | Range | Notes |
|----------|-------|-------|
| **Management Fee** | $500-900 | Usually 3-5% of EGI |
| **Payroll & Personnel** | $800-1,500 | On-site staff, leasing |
| **General & Admin** | $300-600 | Office, legal, accounting |
| **Marketing** | $200-400 | Advertising, leasing costs |
| **Utilities** | $400-1,000 | Depends on who pays what |
| **Repairs & Maintenance** | $800-1,500 | Day-to-day repairs |
| **Property Taxes** | $800-2,000 | Varies significantly by state |
| **Insurance** | $400-800 | Property & liability |
| **Replacement Reserves** | $250-400 | CapEx savings |
| **Total** | **$5,000-8,000** | Higher in expensive markets |

**Expense Ratio:** Operating Expenses / EGI

- **Excellent:** 45-50% (efficient operations)
- **Good:** 50-55% (typical)
- **Concerning:** >60% (investigate inefficiencies)

**Property Tax Warning**
Most states reassess property taxes upon sale. A property showing $1,200/unit in taxes today may jump to $1,800/unit post-closing. **DREAM AI automatically models this using state-specific reassessment ratios.**

### Net Operating Income (NOI)

The Holy Grail metric of real estate. NOI measures property-level profit before debt service and capital expenditures.

```
Formula: EGI - Operating Expenses

Example:
EGI:                     $2,873,900
Operating Expenses:      $1,642,200 (57.1% expense ratio)
─────────────────────────────────
NOI:                     $1,231,700
```

**Why NOI Matters:**
- Used to calculate cap rates and property value
- Independent of financing structure
- Comparable across properties
- Focus of all value-add strategies

---

## Return Calculations

### Cap Rate (Capitalization Rate)

The unlevered return on a property, expressed as NOI / Value.

**Going-In Cap Rate:** Current NOI / Purchase Price

```
Example:
NOI: $1,231,700
Purchase Price: $29,400,000
──────────────────────────────
Going-In Cap: 4.19%
```

**Stabilized Cap Rate:** Pro Forma NOI / Purchase Price (including renovations)

```
Example:
Stabilized NOI: $1,852,000 (after rent growth)
Total Cost: $30,744,000 (purchase + renovations)
──────────────────────────────
Stabilized Cap: 6.02%
```

**Exit Cap Rate:** Projected NOI at sale / Expected Sale Price

**Cap Rate Interpretation:**
- **Lower Cap Rates:** Lower risk, lower returns, better locations
- **Higher Cap Rates:** Higher risk, higher returns, secondary locations
- **Typical Ranges:** Gateway 4-5.5%, Secondary 5-7%, Tertiary 7-9%

**Cap Rate Compression/Expansion:**
- **Compression:** Cap rates decline (property values rise)
- **Expansion:** Cap rates increase (property values fall)
- Exit cap rate assumptions are critical to returns

### Internal Rate of Return (IRR)

The annualized return accounting for timing of cash flows. **The gold standard for comparing investments.**

**Formula:** The discount rate at which Net Present Value (NPV) = 0

```
NPV = Σ (Cash Flow_t / (1 + IRR)^t) = 0
```

Don't worry—DREAM AI calculates this for you using the XIRR function.

**Example Cash Flows:**
```
Year 0: -$8,890,000 (equity investment)
Year 1: $245,000 (annual cash flow)
Year 2: $312,000
Year 3: $385,000
Year 4: $462,000
Year 5: $11,240,000 (sale proceeds + final year CF)
───────────────────
IRR: 19.2%
```

**IRR Targets (Shieldstone Methodology):**

| Market Tier | Minimum IRR | Target IRR |
|-------------|-------------|------------|
| Gateway | 14-16% | 18-20% |
| Secondary | 16-19% | 20-22% |
| Tertiary | 18-22% | 22-25% |

**Risk Adjustments:** Add to base hurdle for:
- Property age 40+ years: +150 bps
- Heavy renovation: +150-250 bps
- Low occupancy (<85%): +100-150 bps
- Floating rate debt: +75-100 bps

### Equity Multiple (EM)

Total distributions / equity invested. **How many times you get your money back.**

```
Formula: (Total Cash Flows + Sale Proceeds) / Initial Equity

Example:
Total Distributions: $1,404,000 (Years 1-5)
Sale Proceeds: $15,399,000
Initial Equity: $8,890,000
───────────────────
EM: 1.89x
```

**Targets:**
- **Minimum:** 1.50x (5-year hold)
- **Target:** 1.80x
- **Excellent:** 2.00x+

**EM vs. IRR:**
- EM ignores timing; IRR accounts for it
- A 2.0x EM in 3 years (40% IRR) beats 2.0x in 7 years (15% IRR)
- Both matter: EM shows absolute return, IRR shows efficiency

### Cash-on-Cash (CoC) Return

Annual cash flow / equity invested. **Simple yield metric.**

```
Formula: Annual Cash Flow / Equity Invested

Example (Year 3):
Cash Flow: $385,000
Equity: $8,890,000
───────────────────
CoC: 4.3%
```

**Stabilized CoC** (most important):
- After renovations complete and property stabilizes
- Typical target: 6-8%
- Lower for value-add (since equity is tied up in renovations)
- Higher for stabilized/core assets

### Debt Service Coverage Ratio (DSCR)

How comfortably NOI covers debt payments. **Lenders care deeply about this.**

```
Formula: NOI / Annual Debt Service

Example:
NOI: $1,231,700
Annual Debt Service: $1,143,000
───────────────────
DSCR: 1.08x
```

**Lender Requirements:**
- **Agency (Fannie/Freddie):** 1.25x minimum
- **Bridge/Bank:** 1.15-1.20x minimum
- **Mezzanine:** May accept <1.10x

**DSCR <1.0 = Property doesn't generate enough NOI to cover debt. Red flag.**

### Net Investor IRR

The LP (Limited Partner) investor's actual return after fees and promote.

```
Gross IRR:               19.2%
Less: Acquisition Fee    -0.3%
Less: Asset Mgmt Fees    -0.8%
Less: Promote Drag       -1.1%
─────────────────────────────
Net Investor IRR:        17.0%
```

**Target:** 15%+ net to LPs (after all fees)

Investors care about **net returns**, not gross. DREAM AI calculates both automatically.

---

## Risk Assessment

### Risk-Adjusted Return Hurdles

Not all 18% IRRs are created equal. A Gateway market Class A property requires lower returns than a Tertiary market Class C property due to lower risk.

**Shieldstone Risk Adjustment Framework:**

1. **Start with Base Hurdle** (by market tier)
2. **Add Risk Premiums** (cumulative)
3. **Compare Projected Returns** to Adjusted Hurdle

**Example:**
```
Secondary Market Base Hurdle:      16.0%
+ Heavy Renovation (+175 bps):     +1.75%
+ Property Age 40+ (+150 bps):     +1.50%
+ Occupancy <85% (+100 bps):       +1.00%
───────────────────────────────────────
Risk-Adjusted Hurdle:              20.25%

Projected IRR:                     19.2%
───────────────────────────────────────
Decision: PASS (returns insufficient for risk)
```

### Red Flags vs. Risk Factors

**Red Flags (Consider Passing):**
- Active environmental contamination
- Severe flood zone (FEMA A/V) without mitigation
- Violent crime >2.5x national average
- Population decline >1%/year for 5+ years
- Single employer >40% of MSA employment
- Unresolvable title/legal issues

**Risk Factors (Manageable with Adjustments):**
- Property age (increase CapEx reserves)
- Low occupancy (extend stabilization timeline)
- Deferred maintenance (budget properly for renovations)
- Rising interest rates (lock long-term financing)

**Shieldstone Principle:** Economics determine viability, not arbitrary cutoffs. Adjust hurdles rather than automatically disqualify.

### Sensitivity Analysis

Test how returns change under different scenarios.

**Key Variables to Test:**
1. **Exit Cap Rate:** ±0.25-0.50%
2. **Rent Growth:** ±1.0%
3. **Vacancy:** ±2.0%
4. **Renovation Costs:** ±15%
5. **Expense Growth:** ±0.50%

**Example Sensitivity Table:**

| Exit Cap | Rent Growth 2.0% | Rent Growth 3.0% | Rent Growth 4.0% |
|----------|------------------|------------------|------------------|
| 5.75% | 20.3% | 21.5% | 22.7% |
| 6.00% | 17.5% | 18.7% | 19.9% ← Base |
| 6.25% | 15.0% | 16.1% | 17.2% |
| 6.50% | 12.7% | 13.7% | 14.8% |

**Insight:** Deal achieves 14% minimum hurdle in 75% of tested scenarios. Acceptable downside protection.

---

## Market Analysis

### Market Tier Classification

**Gateway Markets (Top 6):**
- New York, Los Angeles, Chicago, San Francisco, Boston, DC
- Characteristics: Deep liquidity, institutional capital, diverse economies
- Pros: Lower risk, easier exit
- Cons: Lower returns, intense competition
- Base Hurdle: 14-16% IRR

**Secondary Markets:**
- Major metros: 500K-2M population
- Examples: Austin, Nashville, Denver, Charlotte, Phoenix
- Characteristics: Strong job growth, growing populations
- Pros: Better returns than Gateway, still institutional liquidity
- Cons: More cyclical, less diverse economies
- Base Hurdle: 16-19% IRR

**Tertiary Markets:**
- Smaller markets: <500K population
- Examples: Smaller regional cities
- Characteristics: Limited liquidity, more dependent on local economy
- Pros: Higher returns, less competition
- Cons: Exit risk, limited buyer pool
- Base Hurdle: 18-22% IRR

### Key Market Metrics

**Employment:**
- **Job Growth:** Target 1.5-3.0%+ annually
- **Unemployment:** Target <5% (vs. national average ~3.5-4.0%)
- **Top Employers:** Diversification critical (no single employer >20%)
- **Industries:** Tech, healthcare, education preferred (stable/growing)

**Demographics:**
- **Population Growth:** Target 0.5-2.0%+ annually
- **Median Income:** Should support target rents
- **Age Distribution:** 25-44 age cohort = prime renters
- **Education:** Higher education levels correlate with income/rent growth

**Multifamily Market:**
- **Vacancy Rate:** Target <6% (tighter = better)
- **Rent Growth:** Historical 3-5 year trend
- **Supply Pipeline:** Units under construction / existing inventory
- **Absorption:** How quickly new units lease up

**Regulatory Environment:**
- **Rent Control:** Avoid markets with strict rent control (SF, NYC, etc.)
- **Landlord-Friendly:** Texas, Florida, Georgia > California, Oregon
- **Property Taxes:** Texas (high), California (low due to Prop 13), varies widely

---

## Valuation Methods

### Income Approach (Primary for Multifamily)

**Formula:** Value = NOI / Cap Rate

```
Example:
Stabilized NOI: $1,852,000
Market Cap Rate: 5.75%
───────────────────
Value: $32,200,000
```

**Why This Matters:**
- Every $10,000 increase in NOI = $173,000+ in value (at 5.75% cap)
- Small operational improvements have outsized value impact
- This is how value-add creates returns

### Sales Comparison Approach

Compare to recent transactions of similar properties.

**Key Metrics for Comps:**
- Price per unit
- Price per SF
- Cap rate
- Vintage, class, location
- Transaction date

**Example:**
```
Your Property: $29,400,000 / 168 units = $175,000/unit

Recent Comps:
├─ Comp 1: $172,000/unit (similar vintage, same submarket)
├─ Comp 2: $168,000/unit (older, same submarket)
└─ Comp 3: $180,000/unit (newer, adjacent submarket)

Conclusion: Pricing in line with market, potentially good value.
```

### Cost Approach (Rarely Used for Multifamily)

Land value + replacement cost - depreciation

Used primarily for insurance purposes or very unique properties.

---

## Financing Structures

### Senior Debt

**Agency Debt (Fannie Mae / Freddie Mac):**
- **LTV:** 70-80%
- **Rate:** SOFR + spread (or fixed)
- **Term:** 5, 7, 10 years (with extensions)
- **Amortization:** 30 years
- **DSCR:** 1.25x minimum
- **Prepayment:** Yield maintenance or defeasance (expensive)
- **Best For:** Stabilized or near-stabilized properties

**Bridge Debt:**
- **LTV:** 65-75%
- **Rate:** SOFR + 3.5-5.5% (floating)
- **Term:** 2-3 years (with extensions)
- **Amortization:** Interest-only
- **DSCR:** 1.10-1.15x minimum
- **Prepayment:** Often allowed without penalty
- **Best For:** Value-add requiring 18-36 months to stabilize

**Bank Debt:**
- **LTV:** 65-75%
- **Rate:** Prime or SOFR + spread
- **Term:** 3-5 years
- **Amortization:** 20-30 years
- **DSCR:** 1.20-1.25x
- **Prepayment:** Varies
- **Best For:** Smaller deals (<$10M), relationship-driven

### Refinancing (90/90 Rule)

**Fannie/Freddie Requirement:** 90 consecutive days at ≥90% economic occupancy

**Typical Refinancing Strategy:**
```
Initial Bridge Loan (Months 0-24):
├─ LTV: 70%
├─ Rate: SOFR + 4.5%
└─ Interest-only

Refinance to Agency (Month 24-36):
├─ LTV: 75-80%
├─ Rate: Fixed (lower than bridge)
├─ Cash-out: $2-4M (return capital to investors)
└─ 30-year amortization (positive cash flow)
```

**Why Refinance Matters:**
- Return equity to investors early (boosts IRR)
- Lock in long-term fixed-rate financing
- Reduce interest expense (bridge → agency)
- Extend hold period if needed

### Mezzanine Debt & Preferred Equity

**Used when LTV needs to be higher than senior debt allows:**

```
Senior Debt:        70% LTV ($20.6M)
Mezzanine:          10% LTV ($2.9M)
Common Equity:      20% LTV ($5.9M)
─────────────────────────────────
Total Sources:      100% ($29.4M)
```

**Mezzanine Terms:**
- **Rate:** 10-14% (higher than senior, lower than equity return)
- **Term:** Matches senior debt
- **Structure:** Second lien on property or pledge of ownership interests
- **Return:** Current pay (no upside participation)

---

## Value-Add Strategies

### Revenue Enhancement

**1. Rent to Market (Loss-to-Lease Capture)**
- Current in-place rents below market
- Capture gap through turnover or lease renewals
- **Example:** $1,150 → $1,325 (+$175/unit)

**2. Interior Renovations**
- Light: Paint, fixtures, appliances ($3-8K/unit, $50-100/month premium)
- Moderate: Above + counters, flooring ($8-15K/unit, $100-150/month premium)
- Heavy: Above + bathrooms, layout ($15-25K/unit, $150-200/month premium)

**3. Amenity Upgrades**
- Fitness center, pool renovation, clubhouse, dog park
- Typically $500K-2M for full property
- Attracts higher-quality tenants, supports rent premiums

**4. Other Income**
- Pet fees ($25-50/month), parking ($50-100/month), storage, package lockers
- Utility billing (RUBS or sub-metering)
- Target: $50-100/unit/year increase

### Expense Reduction

**1. Operational Efficiencies**
- Replace inefficient property management
- Renegotiate vendor contracts
- Implement preventative maintenance (reduces R&M)
- Target: 100-200 bps expense ratio reduction

**2. Utility Savings**
- LED lighting, low-flow fixtures, smart thermostats
- Sub-metering (pass through to residents)
- Recapture: $30-80/unit/month

**3. Property Tax Appeals**
- Challenge reassessments post-purchase
- Typical success: 10-20% reduction from initial reassessment
- Hire specialists (pay on contingency)

### Business Plan Example: Classic Value-Add

```
Acquisition:
├─ Purchase Price: $29.4M ($175K/unit)
├─ In-Place Rents: $1,150 (1BR), $1,475 (2BR)
├─ Market Rents: $1,325 (1BR), $1,650 (2BR)
├─ Occupancy: 95%
└─ Going-In Cap: 5.8%

Renovation Strategy (Months 1-18):
├─ Budget: $8K/unit × 168 units = $1.34M
├─ Scope: Light interior renovation
│   └─ Paint, vinyl plank flooring, stainless appliances, fixtures
├─ Timing: 10 units/month upon turnover
└─ Rent Premium: $175/unit/month

Stabilization (Month 24):
├─ Pro Forma Rents: $1,325 (1BR), $1,650 (2BR)
├─ Occupancy: 95% (maintained)
├─ NOI: $1,852,000 (+50% from acquisition)
└─ Stabilized Cap: 6.0%

Exit (Year 5):
├─ Sale Price: $30.7M (6.0% exit cap)
└─ Profit: $15.4M (after debt payoff)

Returns:
├─ IRR: 19.2%
├─ Equity Multiple: 1.89x
└─ LP IRR: 17.0% (net)
```

---

## Exit Strategies

### Exit Cap Rate Triangulation (Shieldstone Method)

Never rely on a single exit cap assumption. **Use three methods and take the highest (most conservative):**

**Method 1: Treasury Spread Method**
```
10-Year Treasury Yield (projected Year 5):  4.5%
Historical Spread (Class B Secondary):      +200 bps
───────────────────────────────────────────────────
Implied Exit Cap:                           6.5%
```

**Method 2: Comp Validation Method**
```
Recent Sales in Submarket:      5.5-6.5% cap rates
Adjust for Property Quality:    +0.25% (your property slightly older)
───────────────────────────────────────────────────
Implied Exit Cap:                           6.0%
```

**Method 3: Entry Cap + Strategy Spread**
```
Going-In Cap Rate:                          5.8%
Value-Add Execution Risk Premium:           +0.50%
───────────────────────────────────────────────────
Implied Exit Cap:                           6.3%
```

**Decision Rule:** Use **highest** of three methods = 6.5%

**Why This Matters:**
- Exit cap is THE most important assumption
- Every 25 bps = $700K-1M+ in sale price
- Optimistic exit caps are #1 source of underperformance

### Hold Period Considerations

**Typical Hold Periods:**
- **Value-Add:** 4-6 years (time to execute and demonstrate stabilization)
- **Core+:** 7-10 years (harvest cash flow, less urgency to exit)
- **Opportunistic:** 3-5 years (higher risk, want liquidity)

**Why 5 Years is Common:**
- Enough time to execute business plan and stabilize
- Investors expect liquidity within 5-7 years
- Tax benefits (depreciation recapture strategies)
- Matches typical debt terms

---

## Due Diligence

### Financial Due Diligence

**Documents to Verify:**
- T-12 Operating Statement (trailing 12 months)
- Rent Roll (current as of <30 days ago)
- 3-year historical financials
- Lease agreements (review top 10% by revenue)
- Aging report (accounts receivable)
- Property tax assessments
- Insurance policies and claims history
- Utility bills (12 months)
- Service contracts (landscaping, HVAC, elevator, etc.)

**Red Flags:**
- Occupancy declining trend
- Rising expenses faster than rents
- Deferred maintenance not disclosed
- High resident turnover (>50% annually)
- Unusual other income (not sustainable)

### Physical Due Diligence

**Property Condition Assessment (PCA):**
- Hire third-party engineering firm
- Inspect all systems: roof, HVAC, plumbing, electrical, structure
- Estimate deferred maintenance and near-term CapEx (1-3 years)
- Budget 10-20% more than PCA suggests (they're often optimistic)

**Key Systems:**
- **Roofs:** $6-10/SF to replace (expensive)
- **HVAC:** $4-8K per unit to replace
- **Plumbing:** Old galvanized pipes = major expense
- **Electrical:** Panel upgrades, code compliance
- **Parking/Paving:** Resurfacing $2-5/SF

### Environmental Due Diligence

**Phase I Environmental Site Assessment (ESA):**
- Desktop review + site visit
- Identifies Recognized Environmental Conditions (RECs)
- Cost: $3-5K
- Required by all lenders

**Phase II ESA** (if Phase I identifies concerns):
- Soil/groundwater testing
- Cost: $10-50K+
- May kill deal or require remediation

**Common Issues:**
- Asbestos (pre-1980 properties)
- Lead paint (pre-1978 properties)
- Underground storage tanks (former gas stations)
- Mold

### Legal Due Diligence

**Title Review:**
- Ensure clear title
- Review easements, encumbrances, liens
- Purchase title insurance

**Zoning & Compliance:**
- Confirm property is legal conforming use
- Verify unit count matches records
- Check for code violations

**Litigation:**
- Search for pending lawsuits
- Review HOA disputes (if applicable)

---

## Common Pitfalls

### 1. Overly Aggressive Rent Growth Assumptions

**Mistake:** Assuming 5%+ annual rent growth when market supports 3%.

**Impact:** Every 1% rent growth assumption error = 2-3% IRR overstatement.

**Solution:** Anchor to market fundamentals. Use trailing 3-5 year rent growth, not last 12 months.

### 2. Ignoring Property Tax Reassessment

**Mistake:** Using current property tax without modeling reassessment.

**Impact:** $600/unit tax increase on 168-unit property = $100K NOI hit = $1.7M value destruction (at 6% cap).

**Solution:** DREAM AI automatically models state-specific reassessment ratios. Always budget 3 scenarios.

### 3. Underestimating Renovation Costs

**Mistake:** Budgeting $6K/unit when market cost is $8K/unit.

**Impact:** $2K/unit × 168 units = $336K budget overrun = 3-5% IRR decline.

**Solution:** Get contractor bids during due diligence. Add 10-15% contingency.

### 4. Optimistic Exit Cap Assumptions

**Mistake:** Using entry cap (5.8%) as exit cap when market cycle likely to turn.

**Impact:** Every 25 bps cap expansion = $700K-1M sale price decline.

**Solution:** Use Shieldstone three-method triangulation. **Never assume exit cap lower than entry cap.**

### 5. Ignoring Supply Pipeline

**Mistake:** Underwriting 4% rent growth while 5,000 units are under construction in submarket.

**Impact:** New supply floods market, vacancy rises, rent growth stalls.

**Solution:** DREAM AI flags elevated supply risk. Model 12-18 month lease-up delay if supply >3% of inventory.

### 6. Overestimating Refinancing Proceeds

**Mistake:** Assuming 80% LTV refinance when actual appraisal supports only 75%.

**Impact:** $1-2M less cash-out = delayed investor distributions = lower IRR.

**Solution:** Be conservative on refinance assumptions. Test scenarios with 70%, 75%, 80% LTV.

### 7. Neglecting DSCR Covenants

**Mistake:** Pro forma shows 1.18x DSCR when loan requires 1.25x.

**Impact:** Loan default risk, forced capital injection, or sale.

**Solution:** Model monthly DSCR during renovation period. Ensure minimum maintained at all times.

### 8. Failing to Account for Lease-Up Time

**Mistake:** Assuming renovated units lease immediately at pro forma rent.

**Impact:** Extended vacancy during renovation = negative cash flow, delayed stabilization.

**Solution:** Budget 30-60 days to lease renovated units. Model renovation phasing realistically (10-15 units/month, not 30).

### 9. Overlooking Market Cycle Timing

**Mistake:** Buying at peak pricing (4.5% cap) assuming market will improve further.

**Impact:** Cap rate expansion at exit kills returns.

**Solution:** Understand where market is in cycle. Late-cycle deals require higher entry returns and conservative exit caps.

### 10. Insufficient Due Diligence on Deferred Maintenance

**Mistake:** Accepting seller's disclosure without independent verification.

**Impact:** $500K-2M surprise CapEx (roof, HVAC, plumbing) wipes out returns.

**Solution:** Hire reputable PCA firm. Budget 15-20% above their recommendations. Walk every unit during due diligence.

---

## Using DREAM AI for Institutional-Quality Underwriting

DREAM AI implements all concepts in this guide automatically:

### Transparent Assumptions
- Every assumption has AI-generated rationale
- Market data sources cited
- Confidence scores on all inputs

### Defensible Analysis
- Shieldstone methodology enforced
- Risk-adjusted return hurdles calculated automatically
- Three-method exit cap triangulation

### Conservative Modeling
- State-specific property tax reassessment
- Realistic renovation timelines and costs
- Sensitivity analysis on every deal
- Downside scenario modeling

### Speed Without Compromise
- 2 minutes for BOE screening
- 7 minutes for complete underwriting
- Instant recalculation when assumptions change
- All financial calculations deterministic (Python, not LLM)

**The Result:** Institutional-quality analysis in a fraction of the time, allowing you to evaluate more deals and make better investment decisions.

---

## Conclusion

Real estate underwriting is both art and science. The **science**—financial modeling, return calculations, market analysis—can be systematized and accelerated through technology like DREAM AI. The **art**—judging market timing, assessing sponsor capabilities, evaluating business plan feasibility—requires human judgment.

**Best Practices:**
1. **Start Conservative:** It's easier to get pleasantly surprised than explain underperformance
2. **Triangulate Everything:** Multiple data sources beat single assumptions
3. **Test Downside:** If downside returns are unacceptable, pass
4. **Document Assumptions:** Future you (or IC) will want to know why you assumed X
5. **Learn from Mistakes:** Track actual vs. projected and refine process

DREAM AI handles the systematic analysis so you can focus on the judgment calls that truly matter.

---

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Author:** DREAM AI Team with Shieldstone Methodology

