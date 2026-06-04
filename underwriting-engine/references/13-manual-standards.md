# 13: Shieldstone Multifamily Manual Standards

## Purpose

This reference distills the critical underwriting standards from the Shieldstone Multifamily Underwriting Manual v2 ([SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md](C:\Users\evana\Downloads\Shieldstone Underwriting Skill Sandbox\Underwriting Manuals\Shieldstone Multifamily Underwriting Manual\v2\SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md)). The Manual is 7,800+ lines covering investment philosophy, deal screening, property tax, refinancing, exit cap, and full technical workflows. The master skill needs the concentrated standards: return hurdles by market tier, vintage CoC floors, exit cap triangulation, deal screening framework, fees and promote. Apply these at Phase 11 (UW Snapshot sanity check) for ACQ deals. EFB deals use bond-driven sizing per [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md) instead.

For near-stabilized core-plus deals routed ACQ, treat these standards as **reference points, not hard cuts** per [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md) §Near-Stabilized Core-Plus Hurdle Relaxation.

---

## Investment Philosophy

- Market tier establishes base hurdle
- Property vintage drives secondary adjustments (newer = lower risk)
- Execution risk factors add incremental hurdle premiums
- Absolute minimums are never violated regardless of adjustments
- If economics don't meet hurdles, pass, don't force the deal

---

## Market Tier Definitions

| Tier | Definition | Examples | Base IRR Range |
|---|---|---|---|
| **Gateway** | Top 10 MSAs by population, highly diversified economies | NYC, LA, Chicago, Dallas, Houston, DC, Miami, Atlanta, Phoenix, Philadelphia | 14–16% |
| **Secondary** | MSA population 500K–2M, moderately diversified | Austin, Nashville, Raleigh, Tampa, Orlando, Denver, Charlotte, San Antonio | 16–19% |
| **Tertiary** | MSA population <500K or limited economic diversification | Smaller metros, single-employer markets, limited institutional activity | 18–22% |

Population tiers are a starting framework, evaluate each market's specific fundamentals (job growth, population trends, supply pipeline, rent growth trajectory) rather than relying solely on population-based classification.

---

## Return Hurdles by Market Tier

### Gateway Markets (Top 10 MSAs)

| Metric | Target Range | Absolute Minimum |
|---|---|---|
| Levered IRR | 14–16% | 14% |
| Year 1 Cash-on-Cash | 4–6% | N/A (renovation period) |
| Stabilized Cash-on-Cash | See vintage tiers | See vintage tiers |
| Equity Multiple (5yr) | 1.6–1.8x | 1.5x |

### Secondary Markets (500K–2M Population)

| Metric | Target Range | Absolute Minimum |
|---|---|---|
| Levered IRR | 16–19% | 14% |
| Year 1 Cash-on-Cash | 5–7% | N/A (renovation period) |
| Stabilized Cash-on-Cash | See vintage tiers | See vintage tiers |
| Equity Multiple (5yr) | 1.7–2.0x | 1.5x |

### Tertiary Markets (<500K Population)

| Metric | Target Range | Absolute Minimum |
|---|---|---|
| Levered IRR | 18–22% | 14% |
| Year 1 Cash-on-Cash | 7–10% | N/A (renovation period) |
| Stabilized Cash-on-Cash | See vintage tiers | See vintage tiers |
| Equity Multiple (5yr) | 1.9–2.2x | 1.5x |

---

## Vintage-Tiered Cash-on-Cash Floors

Rationale: older properties carry higher operational risk, deferred maintenance exposure, and functional obsolescence. Investors require higher stabilized cash yields to compensate.

| Property Vintage | Stabilized CoC Floor | Rationale |
|---|---|---|
| **2020 or newer** | **6.0%** | Modern systems, minimal deferred maintenance, competitive amenities |
| **2000–2019** | **7.0%** | Aging systems, potential functional updates needed, moderate maintenance |
| **Pre-2000** | **7.5–8.0%** | Significant system replacement risk, functional obsolescence, higher R&M |

**Application:** Use property's original construction year, not renovation date. A 1985 property with 2020 renovations remains "Pre-2000" for CoC floor purposes, the bones don't change.

---

## Absolute Minimums (Non-Negotiable)

| Metric | Absolute Minimum | Rationale |
|---|---|---|
| **Levered IRR** | **14.0%** | Below this, risk-adjusted returns don't compensate for execution complexity |
| **Stabilized Cash-on-Cash** | Per vintage tier (6–8%) | Must generate meaningful current yield at stabilization |
| **Equity Multiple (5yr)** | **1.50x** | Must return 50% profit on equity over hold period |
| **Net Investor IRR** | **15.0%** | After promote and fees, investors must clear 15% or deal isn't worth sponsor effort |

**The 15% Net Investor IRR Rule:** ultimate go/no-go threshold. If the deal doesn't deliver 15% net to LPs after promote and fees, it's not worth pursuing.

---

## Risk Adjustments to Base Hurdles

Start with market tier base hurdle, then add adjustments for risk factors:

### Renovation Scope Risk (Vintage-Tiered)

| Property Vintage | Heavy Renovation Premium | Rationale |
|---|---|---|
| 2000+ vintage | +150 bps | Modern infrastructure, predictable scope |
| 1980–1999 vintage | +175–200 bps | Aging systems, potential hidden conditions |
| Pre-1980 vintage | +250 bps | High likelihood of unforeseen conditions, asbestos/lead risk, outdated infrastructure |

Light/Moderate Renovation: **No premium** for cosmetic updates (<$10K/unit).

### Occupancy Risk

| Current Occupancy | Premium |
|---|---|
| 85%+ | +0 bps |
| 75–84% | +100 bps |
| Below 75% | +150 bps |

### Property Age Risk (Independent of Renovation)

| Property Age | Premium |
|---|---|
| 0–20 years | +0 bps |
| 21–30 years | +50 bps |
| 31–40 years | +100 bps |
| 40+ years | +150 bps |

40+ year properties are NOT automatic disqualifiers. The premium compensates for risk; the deal still proceeds if economics work.

### Financing Risk

| Financing Structure | Premium |
|---|---|
| Fixed-rate permanent debt | +0 bps |
| Fixed-rate bridge (rate locked) | +0 bps |
| Floating-rate bridge | +75–100 bps |

### Market Cycle Risk

| Market Condition | Premium |
|---|---|
| Expanding/stable | +0 bps |
| Late cycle / elevated supply | +50–100 bps |
| Recessionary / distressed | +100–150 bps |

---

## Worked Hurdle Examples

### Example: 1988-Built in Tampa (Secondary Market)
- 180 units, occupancy 78%, heavy renovation $22K/unit, floating-rate bridge

| Component | Adjustment |
|---|---|
| Base (Secondary) | 17.5% (midpoint) |
| Renovation Premium (1980–1999, heavy) | +175 bps |
| Occupancy Premium (78%) | +100 bps |
| Property Age Premium (37 years) | +100 bps |
| Financing Premium (floating bridge) | +100 bps |
| **Adjusted IRR Hurdle** | **22.25%** |

CoC Floor: 7.5–8.0% (Pre-2000 vintage).

### Example: 1972-Built in Atlanta (Gateway Market)
- 250 units, occupancy 82%, full gut $35K/unit, floating-rate bridge

| Component | Adjustment |
|---|---|
| Base (Gateway) | 15.0% (midpoint) |
| Renovation Premium (Pre-1980, heavy) | +250 bps |
| Occupancy Premium (82%) | +100 bps |
| Property Age Premium (53 years) | +150 bps |
| Financing Premium (floating bridge) | +100 bps |
| **Adjusted IRR Hurdle** | **21.0%** |

CoC Floor: 7.5–8.0%. This deal requires 21% IRR to compensate for execution risk.

---

## Exit Cap Rate Triangulation (Three-Method Framework)

**Golden Rule:** Exit cap rate is ALWAYS higher than going-in cap rate. If your model shows exit cap <= going-in cap, you are assuming cap rate compression, a speculative bet that must be explicitly justified, not accidentally embedded.

### Method 1: Treasury Spread

```
Exit Cap = Forward Treasury (at exit year) + Agency Spread (~150 bps) + Negative Leverage Buffer (50–75 bps)
```

Example: Forward 5yr Treasury 4.50% + 150 bps agency + 75 bps buffer = 6.75% exit cap.

### Method 2: Exit Comp Validation

```
Exit Price = Stabilized NOI (Exit Year) / Exit Cap
Exit $/Unit = Exit Price / Unit Count
```

Validate against 1–3 submarket sales in last 24 months (similar vintage, unit count, class).

- Within ±10% of comp $/unit: reasonable
- More than +15% above comps: aggressive
- More than +20% above comps: unrealistic

### Method 3: Entry Cap + Strategy Spread

| Strategy | Spread to Entry Cap |
|---|---|
| Core | +25–45 bps |
| Core Plus | +50–75 bps |
| Value-Add | +100 bps |
| Opportunistic | +100–200 bps |

```
Exit Cap = Going-In Cap + Strategy Spread
```

### Triangulation Rule

**Final Exit Cap = HIGHEST of the three methods** (most conservative).

If methods diverge by >50 bps, investigate why before proceeding.

---

## Deal Screening Framework (Merit-Based)

Per the Manual, there are NO hard age caps or occupancy minimums. Red flags only:
- Structural failure
- Active contamination
- Declining MSA population
- Unresolvable legal title issues

Everything else = pricing discussion with risk-adjusted hurdles applied.

### Recommendation Thresholds by Total Hurdle Adjustment

| Total Hurdle Adjustment | Recommendation |
|---|---|
| <200 bps | **PROCEED** |
| 200–399 bps | **PROCEED WITH CAUTION** |
| 400–599 bps | **REQUEST REPRICING** |
| 600+ bps | **PASS** |

---

## Fee Structure (ACQ Deals)

| Fee | Rate |
|---|---|
| **Acquisition** | **0.5–1.0% of PP**, 0.5% for $50M+, 0.75% for $25–50M, 1.0% for <$25M (NOT 5%, that's reserved for EFB executions where the sponsor acts as bond issuer/administrator) |
| Asset Management | 0.5–1.0% of EGI annually (near-stabilized default: 0.5%) |
| Construction Management | 3–5% of hard costs (typically zero for near-stabilized core-plus) |
| Disposition | 0.25–0.5% of sale price |

---

## Promote Structure

Standard Shieldstone promote:

```
Tier 1: 8% preferred return to LP
Tier 2: 70/30 split to LP and GP up to 15% IRR
Tier 3: 50/50 split above 15% IRR
```

All fees modeled in base case. Asset management and acquisition fees are charged on TOP of the promote (sponsor revenue, not LP cost-of-capital).

---

## 90/90 Rule for Agency Refi

| Requirement | Threshold |
|---|---|
| Economic Occupancy | >= 90% for 90 consecutive days |
| DSCR (Fannie/Freddie) | >= 1.25x (1.20x select programs) on T-3 NOI annualized |
| LTV | <= 75% (up to 80% select programs) |
| Property Condition | No deferred maintenance, updated PCA if >12 months old |
| Borrower Liquidity | 9–12 months debt service |
| Seasoning | Typically 12 months ownership |

For near-stabilized core-plus deals: 90/90 does NOT gate closing. Bridge period IS how you get to 90/90. See [references/09-acq-financing.md](.skills/dream-underwrite/references/09-acq-financing.md) §90/90 as Refi Gate.

---

## HUD 223(f) LTV Caps (Memorize)

| Property Type | Refinance | Acquisition |
|---|---|---|
| Affordable | 87% | 85% |
| Market-rate | 85% | 83.3% |

---

## See Also

- Source manual: [SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md](C:\Users\evana\Downloads\Shieldstone Underwriting Skill Sandbox\Underwriting Manuals\Shieldstone Multifamily Underwriting Manual\v2\SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md) (full 7,800-line technical manual)
- [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md), near-stabilized core-plus hurdle relaxation
- [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md), state-specific reassessment ratios
- [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md), EFB sizing alternative (bond-driven, not return-driven)
- [references/09-acq-financing.md](.skills/dream-underwrite/references/09-acq-financing.md), bridge / agency / HUD financing
- [references/12-uw-snapshot.md](.skills/dream-underwrite/references/12-uw-snapshot.md), Phase 11 sanity checks where these standards apply
