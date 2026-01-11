# DREAM AI - Phase 2 Product Requirements Document

**Product Name:** DREAM AI  
**Company:** Shieldstone Acquisitions / DREAM.AI  
**Document Type:** Phase 2 PRD (Screening & Investment Criteria)  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 1. Overview

This PRD covers Phase 2 of DREAM AI's acquisitions intelligence workflow:

- **Investment Criteria Engine:** User-configurable preferences and requirements
- **Merit-Based Screening:** Evaluate deals on economic viability, not arbitrary disqualifiers
- **Risk-Adjusted Hurdles:** Dynamic return thresholds based on deal characteristics
- **Red Flag Detection:** Automated identification of deal-breakers and concerns
- **Deal Scoring:** Weighted scoring across multiple categories including Business Plan Viability

Phase 2 implements the Shieldstone Technical Manual's screening methodology (Sections 1.1 and 2.1) to provide institutional-quality deal evaluation in seconds.

**Core Philosophy:** Merit-based screening evaluates deals on their economic merits with appropriate risk adjustments, rather than using arbitrary disqualifiers that might cause investors to miss good opportunities.

---

## 2. Goals & Success Metrics

### Goals

1. Enable rapid, consistent deal screening aligned with Shieldstone methodology
2. Provide transparent, explainable screening decisions
3. Calculate risk-adjusted return hurdles automatically
4. Identify red flags and concerns proactively
5. Support customizable investment criteria per organization

### Success Metrics

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| Screening completion time | <30 seconds | <15 seconds | Task completion |
| Shieldstone methodology compliance | 100% | 100% | Methodology audit |
| LLM cost per screening | <$0.05 | <$0.03 | API cost tracking |
| User override rate | <20% | <10% | Override tracking |
| False positive rate (passed bad deals) | <5% | <2% | Outcome tracking |
| False negative rate (rejected good deals) | <3% | <1% | Outcome tracking |

---

## 3. Investment Criteria Engine

### 3.1 Criteria Categories

#### Hard Stops (Deal Breakers)

These are non-negotiable requirements. If a deal fails any hard stop, it receives an automatic PASS recommendation.

| Criterion | Type | Default | Configurable | Notes |
|-----------|------|---------|--------------|-------|
| Minimum Units | Number | 50 | Yes | Below threshold = Pass |
| Maximum Units | Number | 500 | Yes | Above threshold = Pass |
| Minimum Price | Currency | $5,000,000 | Yes | Below threshold = Pass |
| Maximum Price | Currency | $100,000,000 | Yes | Above threshold = Pass |
| Target Markets | List | All US | Yes | Outside markets = Pass |
| Excluded Markets | List | None | Yes | In excluded = Pass |
| Property Types | List | Multifamily | Yes | Wrong type = Pass |
| Minimum Year Built | Year | 1960 | Yes | Older = Pass |
| Ground Lease | Boolean | Allowed | Yes | Can exclude entirely |
| Rent Control | Boolean | Case-by-case | Yes | Can exclude entirely |

#### Soft Preferences (Weighted Factors)

These influence scoring but don't automatically disqualify a deal.

| Criterion | Type | Ideal Range | Weight | Notes |
|-----------|------|-------------|--------|-------|
| Price Per Unit | Currency | $75K-$200K | Medium | Market-adjusted |
| In-Place Cap Rate | Percentage | 5.5%-8.5% | High | Risk-adjusted |
| Occupancy | Percentage | 88%-98% | Medium | Below 85% = concern |
| Property Class | Letter | B, C | Medium | A = lower returns, D = higher risk |
| Vintage | Year Range | 1975-2010 | Low | Sweet spot for value-add |
| Market Tier | Category | Secondary | Medium | Gateway, Secondary, Tertiary |
| Value-Add Potential | Category | Moderate | High | Light, Moderate, Heavy |
| Source Quality | Category | Direct | Low | Direct > Broker > Auction |

#### Target Returns (Hurdle Rates)

| Metric | Minimum | Target | Stretch | Notes |
|--------|---------|--------|---------|-------|
| Levered IRR | 14% | 18% | 22%+ | Risk-adjusted |
| Equity Multiple | 1.50x | 1.80x | 2.00x+ | 5-year hold |
| Cash-on-Cash (Avg) | 6% | 8% | 10%+ | Years 2-5 |
| DSCR | 1.20x | 1.30x | 1.40x+ | Stabilized |
| Net LP IRR | 12% | 15% | 18%+ | After promote |

### 3.2 Criteria Configuration UI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Investment Criteria                                    [Save] [Reset]       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ [Hard Stops] [Preferences] [Return Targets] [Advanced]                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  HARD STOPS                                                                  │
│  These criteria will automatically disqualify deals                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Property Size                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Minimum Units          Maximum Units                                    ││
│  │  ┌──────────────┐       ┌──────────────┐                                ││
│  │  │ 50      [-][+]│       │ 500     [-][+]│                                ││
│  │  └──────────────┘       └──────────────┘                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Price Range                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Minimum Price          Maximum Price                                    ││
│  │  ┌──────────────┐       ┌──────────────┐                                ││
│  │  │ $5,000,000   │       │ $100,000,000 │                                ││
│  │  └──────────────┘       └──────────────┘                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Target Markets                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  [✓] Austin    [✓] Dallas    [✓] Houston    [✓] San Antonio             ││
│  │  [✓] Phoenix   [✓] Denver    [✓] Atlanta    [✓] Nashville               ││
│  │  [✓] Charlotte [✓] Raleigh   [ ] Los Angeles [ ] San Francisco          ││
│  │  [+ Add Market]                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Exclusions                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  [ ] Exclude Ground Lease properties                                     ││
│  │  [ ] Exclude Rent Control markets                                        ││
│  │  [ ] Exclude Section 8 / Affordable                                      ││
│  │  [ ] Exclude properties older than: [1960 ▼]                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Criteria Templates

Pre-built templates for common investment strategies:

| Template | Focus | Typical Criteria |
|----------|-------|------------------|
| **Core Value-Add** | B/C properties, moderate renovation | 75-200 units, 1975-2005, 85%+ occupancy |
| **Heavy Value-Add** | Distressed turnaround | 50-150 units, any vintage, <85% occupancy OK |
| **Core Plus** | Stabilized with upside | 100-300 units, 1990+, 92%+ occupancy |
| **Opportunistic** | Deep value, higher risk | Any size, any vintage, any occupancy |
| **Gateway Markets** | Primary markets only | Top 10 MSAs, Class A/B, 150+ units |
| **Secondary Markets** | Growth markets | Non-gateway, population growth >1% |

---

## 4. Merit-Based Screening Framework

### 4.1 Screening Philosophy

**Traditional Screening (What We Avoid):**
- Arbitrary cutoffs ("No properties older than 1980")
- Binary pass/fail on soft criteria
- One-size-fits-all hurdles
- Missing good deals due to rigid rules

**Merit-Based Screening (Our Approach):**
- Every deal evaluated on economic merits
- Risk factors increase required returns (not disqualify)
- Transparent adjustments with clear rationale
- Captures opportunities others miss

### 4.2 Risk-Adjusted Hurdle Calculation

Per Shieldstone Technical Manual Section 1.1:

```
Base Hurdle (Market Tier)
    + Renovation Risk Premium
    + Occupancy Risk Premium
    + Age Risk Premium
    + Financing Risk Premium
    + Market Cycle Premium
    ─────────────────────────
    = Risk-Adjusted IRR Hurdle
```

#### Base Hurdles by Market Tier

| Market Tier | IRR Range | Midpoint | Equity Multiple | Year 1 CoC |
|-------------|-----------|----------|-----------------|------------|
| Gateway | 14-16% | 15% | 1.6-1.8x | 4-6% |
| Secondary | 16-19% | 17.5% | 1.7-2.0x | 5-7% |
| Tertiary | 18-22% | 20% | 1.9-2.2x | 7-10% |

#### Risk Premiums

**Renovation Risk Premium:**

| Renovation Type | Definition | IRR Premium |
|-----------------|------------|-------------|
| Stabilized | No renovation needed | +0% |
| Light | <$5K/unit, cosmetic only | +50-100 bps |
| Moderate | $5K-$15K/unit, full interior | +100-200 bps |
| Heavy | >$15K/unit, gut renovation | +200-400 bps |
| Ground-Up | New construction | +300-500 bps |

**Occupancy Risk Premium:**

| Occupancy | Premium | Rationale |
|-----------|---------|-----------|
| >95% | +0% | Stabilized |
| 90-95% | +25 bps | Minor lease-up risk |
| 85-90% | +75 bps | Moderate lease-up |
| 80-85% | +150 bps | Significant turnaround |
| <80% | +250 bps | Distressed, high risk |

**Age Risk Premium:**

| Property Age | Premium | Rationale |
|--------------|---------|-----------|
| <20 years | +0% | Modern systems |
| 20-30 years | +25 bps | Some deferred maintenance |
| 30-40 years | +50 bps | Aging systems |
| 40-50 years | +100 bps | Major systems replacement likely |
| >50 years | +150 bps | Significant capital risk |

**Financing Risk Premium:**

| Financing Type | Premium | Rationale |
|----------------|---------|-----------|
| Fixed rate, full term | +0% | No refinance risk |
| Fixed rate, refi needed | +25 bps | Refinance execution risk |
| Floating rate, capped | +50 bps | Rate volatility |
| Floating rate, uncapped | +100 bps | Significant rate risk |
| Bridge loan | +75 bps | Shorter term, refi required |

**Market Cycle Premium:**

| Cycle Position | Premium | Rationale |
|----------------|---------|-----------|
| Early recovery | +0% | Maximum upside |
| Mid-cycle | +25 bps | Normal conditions |
| Late cycle | +75 bps | Limited upside, correction risk |
| Peak/Overheated | +150 bps | Elevated risk |

### 4.3 Hurdle Calculation Example

```
Deal: Oak Creek Apartments, Austin TX
─────────────────────────────────────

Base Hurdle (Secondary Market):     17.5%
+ Renovation Premium (Moderate):    +1.5%
+ Occupancy Premium (94%):          +0.25%
+ Age Premium (40 years):           +1.0%
+ Financing Premium (Fixed):        +0%
+ Market Cycle Premium (Mid):       +0.25%
─────────────────────────────────────────
Risk-Adjusted IRR Hurdle:           20.5%

Deal Projected IRR:                 18.5%
Gap to Hurdle:                      -2.0%

Recommendation: PROCEED WITH CAUTION
Rationale: Deal falls 200bps short of risk-adjusted hurdle. 
Consider repricing or enhanced value-add scope.
```

---

## 5. Red Flag Detection

### 5.1 Red Flag Categories

#### Critical Red Flags (Potential Deal Breakers)

| Red Flag | Detection Method | Threshold | Action |
|----------|------------------|-----------|--------|
| Declining Occupancy | T-12 trend analysis | >5% decline YoY | Flag for review |
| Negative NOI Trend | T-12 analysis | >10% decline | Flag for review |
| Deferred Maintenance | OM/inspection notes | Major systems | Flag for review |
| Environmental Issues | Document search | Any mention | Flag for review |
| Title/Legal Issues | Document search | Any mention | Flag for review |
| Seller Motivation | Context clues | Distressed sale | Note (may be opportunity) |
| Unrealistic Pro Forma | Compare to T-12 | >30% NOI growth Y1 | Flag aggressive assumptions |

#### Warning Flags (Concerns to Monitor)

| Warning | Detection Method | Threshold | Action |
|---------|------------------|-----------|--------|
| High Expense Ratio | T-12 analysis | >55% | Note in analysis |
| Below-Market Mgmt Fee | T-12 analysis | <2.5% | Adjust to market |
| Unusual Revenue Items | T-12 analysis | One-time income | Normalize |
| Concentrated Lease Expiry | Rent roll | >30% in any month | Note rollover risk |
| High Delinquency | Rent roll | >5% of tenants | Note collection risk |
| Short Remaining Lease Terms | Rent roll | Avg <6 months | Note turnover risk |
| Limited Comps Available | Market research | <3 comps | Note uncertainty |

#### Informational Flags (Context)

| Flag | Detection | Notes |
|------|-----------|-------|
| Ground Lease | Document search | Calculate leasehold value |
| Rent Control | Market lookup | Adjust growth assumptions |
| LIHTC/Affordable | Document search | Different underwriting |
| Assumable Debt | OM/loan docs | Potential advantage |
| 1031 Exchange | Context | Seller timeline pressure |

### 5.2 Red Flag Detection Prompts

**Document Analysis Prompt (Haiku):**

```
You are a real estate due diligence analyst reviewing deal documents for red flags.

Analyze the following document excerpts and identify any red flags or concerns:

Document Type: {document_type}
Content: {document_content}

Look for:
1. Environmental issues (contamination, flood zone, etc.)
2. Legal/title concerns
3. Deferred maintenance indicators
4. Seller distress signals
5. Unrealistic assumptions
6. Missing or incomplete information
7. Unusual terms or conditions

For each red flag found, provide:
- Category (Critical, Warning, Informational)
- Specific concern
- Location in document
- Recommended action

Respond in JSON format:
{
  "red_flags": [
    {
      "category": "Critical",
      "concern": "Phase I environmental report mentions...",
      "location": "Page 45, Environmental section",
      "action": "Request Phase II environmental assessment"
    }
  ]
}
```

**Financial Analysis Prompt (Python-based, no LLM):**

```python
def detect_financial_red_flags(t12_data: T12Data, rent_roll: RentRoll) -> List[RedFlag]:
    """
    Detect financial red flags from T-12 and rent roll data.
    Pure Python - no LLM cost.
    """
    red_flags = []
    
    # Check occupancy trend
    if t12_data.occupancy_trend < -0.05:  # >5% decline
        red_flags.append(RedFlag(
            category="Critical",
            concern=f"Occupancy declined {abs(t12_data.occupancy_trend):.1%} over trailing 12 months",
            action="Investigate cause of occupancy decline"
        ))
    
    # Check NOI trend
    if t12_data.noi_trend < -0.10:  # >10% decline
        red_flags.append(RedFlag(
            category="Critical",
            concern=f"NOI declined {abs(t12_data.noi_trend):.1%} over trailing 12 months",
            action="Analyze revenue and expense drivers"
        ))
    
    # Check expense ratio
    if t12_data.expense_ratio > 0.55:
        red_flags.append(RedFlag(
            category="Warning",
            concern=f"Expense ratio of {t12_data.expense_ratio:.1%} exceeds typical range",
            action="Review expense line items for optimization opportunities"
        ))
    
    # Check management fee
    if t12_data.management_fee_pct < 0.025:
        red_flags.append(RedFlag(
            category="Warning",
            concern=f"Management fee of {t12_data.management_fee_pct:.1%} below market (2.5-3.5%)",
            action="Adjust pro forma to market management fee"
        ))
    
    # Check lease concentration
    monthly_expirations = rent_roll.get_expiration_concentration()
    max_concentration = max(monthly_expirations.values())
    if max_concentration > 0.30:
        red_flags.append(RedFlag(
            category="Warning",
            concern=f"{max_concentration:.0%} of leases expire in same month",
            action="Plan for concentrated turnover period"
        ))
    
    # Check delinquency
    if rent_roll.delinquency_rate > 0.05:
        red_flags.append(RedFlag(
            category="Warning",
            concern=f"Delinquency rate of {rent_roll.delinquency_rate:.1%} exceeds 5% threshold",
            action="Review collection procedures and tenant quality"
        ))
    
    return red_flags
```

---

## 6. Deal Scoring System

### 6.1 Scoring Categories

Per Master PRD Section 5.3, deals are scored across weighted categories:

| Category | Weight | Components |
|----------|--------|------------|
| Financial Performance | 25-30% | IRR, EM, CoC vs. hurdles |
| Business Plan Viability | 20-25% | Value-add thesis, execution feasibility |
| Market Quality | 20-25% | MSA tier, submarket fundamentals |
| Property Quality | 15-20% | Vintage, condition, class |
| Deal Sourcing | 5-10% | Off-market, relationship, timing |
| Risk Factors | 5-10% | Red flags, execution complexity |

### 6.2 Scoring Rubrics

#### Financial Performance (25-30%)

| Score | Criteria |
|-------|----------|
| 90-100 | Exceeds risk-adjusted hurdle by >300bps |
| 75-89 | Exceeds risk-adjusted hurdle by 100-300bps |
| 60-74 | Meets risk-adjusted hurdle (±100bps) |
| 40-59 | Below hurdle by 100-300bps |
| 0-39 | Below hurdle by >300bps |

#### Business Plan Viability (20-25%)

| Score | Criteria |
|-------|----------|
| 90-100 | Proven playbook, conservative assumptions, strong sponsor |
| 75-89 | Solid thesis, reasonable assumptions, relevant experience |
| 60-74 | Viable thesis, some aggressive assumptions |
| 40-59 | Questionable thesis, multiple aggressive assumptions |
| 0-39 | Unrealistic thesis, assumptions not supported by data |

#### Market Quality (20-25%)

| Score | Criteria |
|-------|----------|
| 90-100 | Top-tier submarket, strong fundamentals, limited supply |
| 75-89 | Good submarket, positive trends, manageable supply |
| 60-74 | Average submarket, stable fundamentals |
| 40-59 | Weak submarket, concerning trends |
| 0-39 | Distressed market, negative fundamentals |

#### Property Quality (15-20%)

| Score | Criteria |
|-------|----------|
| 90-100 | Excellent condition, desirable vintage, Class A/B+ |
| 75-89 | Good condition, standard vintage, Class B |
| 60-74 | Average condition, older vintage, Class B/C |
| 40-59 | Below average condition, significant deferred maintenance |
| 0-39 | Poor condition, major capital needs |

#### Deal Sourcing (5-10%)

| Score | Criteria |
|-------|----------|
| 90-100 | Off-market, direct relationship, exclusive |
| 75-89 | Limited marketing, strong broker relationship |
| 60-74 | Marketed deal, competitive but manageable |
| 40-59 | Widely marketed, highly competitive |
| 0-39 | Auction, distressed sale, unclear process |

#### Risk Factors (5-10%)

| Score | Criteria |
|-------|----------|
| 90-100 | No red flags, straightforward execution |
| 75-89 | Minor concerns, manageable risks |
| 60-74 | Some yellow flags, requires attention |
| 40-59 | Multiple concerns, elevated risk |
| 0-39 | Critical red flags, significant risk |

### 6.3 Overall Score Calculation

```python
def calculate_deal_score(
    financial_score: int,
    business_plan_score: int,
    market_score: int,
    property_score: int,
    sourcing_score: int,
    risk_score: int,
    weights: Optional[Dict[str, float]] = None
) -> DealScore:
    """
    Calculate weighted overall deal score.
    """
    # Default weights (user-configurable)
    if weights is None:
        weights = {
            'financial': 0.275,
            'business_plan': 0.225,
            'market': 0.225,
            'property': 0.175,
            'sourcing': 0.05,
            'risk': 0.05
        }
    
    overall = (
        financial_score * weights['financial'] +
        business_plan_score * weights['business_plan'] +
        market_score * weights['market'] +
        property_score * weights['property'] +
        sourcing_score * weights['sourcing'] +
        risk_score * weights['risk']
    )
    
    # Determine recommendation
    if overall >= 75:
        recommendation = "PURSUE"
    elif overall >= 60:
        recommendation = "PROCEED WITH CAUTION"
    elif overall >= 45:
        recommendation = "REQUEST REPRICING"
    else:
        recommendation = "PASS"
    
    return DealScore(
        overall_score=round(overall),
        recommendation=recommendation,
        category_scores={
            'financial': financial_score,
            'business_plan': business_plan_score,
            'market': market_score,
            'property': property_score,
            'sourcing': sourcing_score,
            'risk': risk_score
        },
        weights=weights
    )
```

### 6.4 Scoring Output UI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Deal Score: Oak Creek Apartments                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │                              78                                          ││
│  │                           ─────────                                      ││
│  │                          │         │                                     ││
│  │                          │  SCORE  │                                     ││
│  │                          │         │                                     ││
│  │                           ─────────                                      ││
│  │                                                                          ││
│  │                    ████████████████████████                              ││
│  │                    █      PURSUE         █                               ││
│  │                    ████████████████████████                              ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Category Breakdown                                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Financial Performance (27.5%)                                               │
│  ┌────────────────────────────────────────────────────────────────┐ 82     │
│  │████████████████████████████████████████████████████████████████│        │
│  └────────────────────────────────────────────────────────────────┘        │
│  IRR: 18.5% vs 20.5% hurdle (-200bps)                                       │
│                                                                              │
│  Business Plan Viability (22.5%)                                             │
│  ┌────────────────────────────────────────────────────────────────┐ 85     │
│  │██████████████████████████████████████████████████████████████████│      │
│  └────────────────────────────────────────────────────────────────┘        │
│  Proven value-add playbook with experienced sponsor                         │
│                                                                              │
│  Market Quality (22.5%)                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ 80     │
│  │████████████████████████████████████████████████████████████████│        │
│  └────────────────────────────────────────────────────────────────┘        │
│  Strong Austin submarket with 3.2% rent growth                              │
│                                                                              │
│  Property Quality (17.5%)                                                    │
│  ┌────────────────────────────────────────────────────────────────┐ 68     │
│  │████████████████████████████████████████████████████████│              │
│  └────────────────────────────────────────────────────────────────┘        │
│  1985 vintage, Class B-, deferred maintenance noted                         │
│                                                                              │
│  Deal Sourcing (5%)                                                          │
│  ┌────────────────────────────────────────────────────────────────┐ 70     │
│  │██████████████████████████████████████████████████████████│            │
│  └────────────────────────────────────────────────────────────────┘        │
│  Marketed deal, moderate competition                                         │
│                                                                              │
│  Risk Factors (5%)                                                           │
│  ┌────────────────────────────────────────────────────────────────┐ 75     │
│  │████████████████████████████████████████████████████████████│          │
│  └────────────────────────────────────────────────────────────────┘        │
│  Property tax reassessment risk, renovation timeline                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Screening Workflow

### 7.1 Automated Screening Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCREENING WORKFLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Deal Created (Phase 1)                                                      │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 1: Hard Stop Check                                                 ││
│  │  ─────────────────────────                                               ││
│  │  • Check against user's hard stop criteria                               ││
│  │  • If ANY hard stop triggered → Auto-PASS                                ││
│  │  • Otherwise → Continue                                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 2: Risk-Adjusted Hurdle Calculation                                ││
│  │  ─────────────────────────────────────────                               ││
│  │  • Determine market tier                                                 ││
│  │  • Calculate all risk premiums                                           ││
│  │  • Sum to get risk-adjusted IRR hurdle                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 3: Red Flag Detection                                              ││
│  │  ─────────────────────────                                               ││
│  │  • Analyze documents for critical issues                                 ││
│  │  • Check financial metrics for warnings                                  ││
│  │  • Compile red flag summary                                              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 4: Category Scoring                                                ││
│  │  ─────────────────────────                                               ││
│  │  • Score each category (0-100)                                           ││
│  │  • Apply user-defined weights                                            ││
│  │  • Calculate overall score                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 5: Generate Recommendation                                         ││
│  │  ─────────────────────────────                                           ││
│  │  • PURSUE (75+): Proceed to full underwriting                           ││
│  │  • PROCEED WITH CAUTION (60-74): Review concerns, then proceed          ││
│  │  • REQUEST REPRICING (45-59): Good deal at different price              ││
│  │  • PASS (<45): Does not meet investment criteria                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  Screening Complete → Update Deal Status → Notify User                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Screening Results Page

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Screening Results: Oak Creek Apartments                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │   RECOMMENDATION                                                         ││
│  │   ┌────────────────────────────────────────────────────────────────────┐││
│  │   │                                                                    │││
│  │   │   ████████████████████████████████████████████████████████████    │││
│  │   │   █                    PURSUE                                █    │││
│  │   │   ████████████████████████████████████████████████████████████    │││
│  │   │                                                                    │││
│  │   │   Score: 78/100 | Confidence: High                                │││
│  │   │                                                                    │││
│  │   └────────────────────────────────────────────────────────────────────┘││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Risk-Adjusted Hurdle Analysis                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Base Hurdle (Secondary Market)                          17.50%         ││
│  │  + Renovation Premium (Moderate, $8K/unit)               +1.50%         ││
│  │  + Occupancy Premium (94%)                               +0.25%         ││
│  │  + Age Premium (40 years)                                +1.00%         ││
│  │  + Financing Premium (Fixed rate)                        +0.00%         ││
│  │  + Market Cycle Premium (Mid-cycle)                      +0.25%         ││
│  │  ─────────────────────────────────────────────────────────────────────  ││
│  │  Risk-Adjusted IRR Hurdle                                20.50%         ││
│  │                                                                          ││
│  │  Deal Projected IRR                                      18.50%         ││
│  │  Gap to Hurdle                                           -2.00%         ││
│  │                                                                          ││
│  │  ⚠️ Deal falls 200bps short of risk-adjusted hurdle                     ││
│  │  Consider: Repricing, enhanced value-add, or risk mitigation            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Red Flags & Concerns                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ⚠️ WARNINGS (2)                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  • Property tax reassessment will increase taxes ~47% post-acquisition  ││
│  │    Action: Already factored into pro forma                              ││
│  │                                                                          ││
│  │  • 28% of leases expire in March 2026                                   ││
│  │    Action: Plan renovation schedule around lease expirations            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ℹ️ INFORMATIONAL (1)                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  • Assumable debt at 5.5% available                                     ││
│  │    Note: Potential $180K annual interest savings vs. market rates       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [View Full Score Breakdown]  [Proceed to Analysis]  [Request Repricing]    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. API Specifications

### 8.1 Investment Criteria Endpoints

#### Get Organization Criteria

```
GET /api/v1/organizations/{org_id}/investment-criteria

Response (200 OK):
{
  "id": "crit_abc123",
  "organization_id": "org_xyz789",
  "name": "Core Value-Add Strategy",
  "hard_stops": {
    "min_units": 50,
    "max_units": 500,
    "min_price": 5000000,
    "max_price": 100000000,
    "target_markets": ["Austin", "Dallas", "Houston", "Phoenix"],
    "excluded_markets": [],
    "property_types": ["MULTIFAMILY"],
    "min_year_built": 1960,
    "exclude_ground_lease": false,
    "exclude_rent_control": false
  },
  "preferences": {
    "price_per_unit": {"min": 75000, "max": 200000, "weight": 0.5},
    "cap_rate": {"min": 0.055, "max": 0.085, "weight": 0.8},
    "occupancy": {"min": 0.88, "max": 0.98, "weight": 0.6},
    "property_class": {"preferred": ["B", "C"], "weight": 0.5},
    "vintage": {"min": 1975, "max": 2010, "weight": 0.3}
  },
  "return_targets": {
    "irr_minimum": 0.14,
    "irr_target": 0.18,
    "equity_multiple_minimum": 1.50,
    "equity_multiple_target": 1.80,
    "coc_minimum": 0.06,
    "dscr_minimum": 1.20
  },
  "scoring_weights": {
    "financial": 0.275,
    "business_plan": 0.225,
    "market": 0.225,
    "property": 0.175,
    "sourcing": 0.05,
    "risk": 0.05
  },
  "updated_at": "2025-12-20T10:30:00Z"
}
```

#### Update Criteria

```
PUT /api/v1/organizations/{org_id}/investment-criteria

Request Body:
{
  "hard_stops": {...},
  "preferences": {...},
  "return_targets": {...},
  "scoring_weights": {...}
}

Response (200 OK):
{
  "id": "crit_abc123",
  "updated_at": "2025-12-20T11:00:00Z",
  ...
}
```

### 8.2 Screening Endpoints

#### Run Screening

```
POST /api/v1/deals/{deal_id}/screen

Request Body:
{
  "criteria_id": "crit_abc123",  // Optional, uses org default if omitted
  "include_market_data": true
}

Response (202 Accepted):
{
  "job_id": "screen_job_123",
  "status": "PROCESSING",
  "estimated_time_seconds": 15
}
```

#### Get Screening Results

```
GET /api/v1/deals/{deal_id}/screening

Response (200 OK):
{
  "screening_id": "screen_abc123",
  "deal_id": "deal_xyz789",
  "completed_at": "2025-12-20T10:30:15Z",
  
  "recommendation": "PURSUE",
  "overall_score": 78,
  "confidence": "HIGH",
  
  "hard_stop_check": {
    "passed": true,
    "checks": [
      {"criterion": "min_units", "value": 96, "threshold": 50, "passed": true},
      {"criterion": "max_price", "value": 12500000, "threshold": 100000000, "passed": true}
    ]
  },
  
  "hurdle_analysis": {
    "base_hurdle": 0.175,
    "premiums": {
      "renovation": {"value": 0.015, "reason": "Moderate renovation ($8K/unit)"},
      "occupancy": {"value": 0.0025, "reason": "94% occupancy"},
      "age": {"value": 0.01, "reason": "40-year-old property"},
      "financing": {"value": 0, "reason": "Fixed rate financing"},
      "market_cycle": {"value": 0.0025, "reason": "Mid-cycle market"}
    },
    "risk_adjusted_hurdle": 0.205,
    "deal_projected_irr": 0.185,
    "gap_to_hurdle": -0.02
  },
  
  "category_scores": {
    "financial": {"score": 82, "weight": 0.275, "notes": "IRR 200bps below hurdle"},
    "business_plan": {"score": 85, "weight": 0.225, "notes": "Proven value-add playbook"},
    "market": {"score": 80, "weight": 0.225, "notes": "Strong Austin submarket"},
    "property": {"score": 68, "weight": 0.175, "notes": "1985 vintage, Class B-"},
    "sourcing": {"score": 70, "weight": 0.05, "notes": "Marketed deal"},
    "risk": {"score": 75, "weight": 0.05, "notes": "Tax reassessment, timeline risk"}
  },
  
  "red_flags": {
    "critical": [],
    "warnings": [
      {
        "category": "Financial",
        "concern": "Property tax reassessment will increase taxes ~47%",
        "action": "Already factored into pro forma"
      },
      {
        "category": "Operational",
        "concern": "28% of leases expire in March 2026",
        "action": "Plan renovation schedule around lease expirations"
      }
    ],
    "informational": [
      {
        "category": "Financing",
        "concern": "Assumable debt at 5.5% available",
        "action": "Potential $180K annual interest savings"
      }
    ]
  },
  
  "llm_cost_cents": 4,
  "processing_time_ms": 12500
}
```

#### Override Screening

```
POST /api/v1/deals/{deal_id}/screening/override

Request Body:
{
  "new_recommendation": "PROCEED WITH CAUTION",
  "reason": "Sponsor has exceptional track record in this submarket",
  "override_by": "user_123"
}

Response (200 OK):
{
  "screening_id": "screen_abc123",
  "original_recommendation": "PURSUE",
  "new_recommendation": "PROCEED WITH CAUTION",
  "override_reason": "Sponsor has exceptional track record in this submarket",
  "override_by": "user_123",
  "override_at": "2025-12-20T11:00:00Z"
}
```

---

## 9. Database Schema

```sql
-- Investment criteria table
CREATE TABLE investment_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    created_by UUID NOT NULL REFERENCES users(id),
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN NOT NULL DEFAULT false,
    
    -- Criteria configuration (JSONB for flexibility)
    hard_stops JSONB NOT NULL,
    preferences JSONB NOT NULL,
    return_targets JSONB NOT NULL,
    scoring_weights JSONB NOT NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT one_default_per_org UNIQUE (organization_id, is_default) 
        WHERE is_default = true
);

-- Screening results table
CREATE TABLE screening_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    criteria_id UUID NOT NULL REFERENCES investment_criteria(id),
    
    -- Results
    recommendation screening_recommendation_enum NOT NULL,
    overall_score INTEGER NOT NULL,
    confidence confidence_level_enum NOT NULL,
    
    -- Detailed analysis (JSONB)
    hard_stop_check JSONB NOT NULL,
    hurdle_analysis JSONB NOT NULL,
    category_scores JSONB NOT NULL,
    red_flags JSONB NOT NULL,
    
    -- Override tracking
    is_overridden BOOLEAN NOT NULL DEFAULT false,
    original_recommendation screening_recommendation_enum,
    override_reason TEXT,
    override_by UUID REFERENCES users(id),
    override_at TIMESTAMPTZ,
    
    -- Performance tracking
    llm_cost_cents INTEGER,
    processing_time_ms INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Only one active screening per deal
    CONSTRAINT one_screening_per_deal UNIQUE (deal_id)
);

-- Red flags table (for tracking patterns)
CREATE TABLE red_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    screening_id UUID NOT NULL REFERENCES screening_results(id) ON DELETE CASCADE,
    
    category red_flag_category_enum NOT NULL,  -- CRITICAL, WARNING, INFORMATIONAL
    flag_type VARCHAR(100) NOT NULL,
    concern TEXT NOT NULL,
    action TEXT,
    source VARCHAR(100),  -- Document, calculation, market data
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enums
CREATE TYPE screening_recommendation_enum AS ENUM (
    'PURSUE', 'PROCEED_WITH_CAUTION', 'REQUEST_REPRICING', 'PASS'
);

CREATE TYPE confidence_level_enum AS ENUM ('HIGH', 'MEDIUM', 'LOW');

CREATE TYPE red_flag_category_enum AS ENUM ('CRITICAL', 'WARNING', 'INFORMATIONAL');

-- Indexes
CREATE INDEX idx_criteria_org ON investment_criteria(organization_id);
CREATE INDEX idx_screening_deal ON screening_results(deal_id);
CREATE INDEX idx_screening_recommendation ON screening_results(recommendation);
CREATE INDEX idx_red_flags_screening ON red_flags(screening_id);
CREATE INDEX idx_red_flags_category ON red_flags(category);
```

---

## 10. Testing Requirements

### 10.1 Methodology Compliance Tests

| Test | Description | Target |
|------|-------------|--------|
| Hurdle calculation | All premium combinations | 100% match to manual |
| Scoring rubrics | Score boundaries | Correct categorization |
| Hard stop logic | All criteria combinations | Correct pass/fail |
| Red flag detection | Known red flag scenarios | >95% detection |

### 10.2 Performance Tests

| Operation | Target | Method |
|-----------|--------|--------|
| Full screening | <30 seconds | Load test |
| Hard stop check | <100ms | Unit test |
| Hurdle calculation | <50ms | Unit test |
| Score calculation | <100ms | Unit test |

### 10.3 Accuracy Tests

- Compare screening results against 100+ historical deals
- Track false positive/negative rates
- A/B test against manual screening

---

## 11. Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| Allow negative criteria (things to avoid)? | Yes | Implemented as exclusions |
| Criteria versioning? | Future | Track changes over time |
| Shared criteria templates? | Future | Marketplace for templates |
| Machine learning on outcomes? | Future | Learn from deal outcomes |

---

## 12. Rollout Plan

### Phase 2a: Criteria Engine (Week 2)
- Criteria configuration UI
- Hard stops implementation
- Template system

### Phase 2b: Hurdle Calculator (Week 2)
- Risk premium calculations
- Market tier classification
- Hurdle breakdown display

### Phase 2c: Red Flag Detection (Week 2-3)
- Document analysis prompts
- Financial red flag detection
- Red flag UI

### Phase 2d: Scoring System (Week 3)
- Category scoring
- Weight configuration
- Results dashboard

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Author: DREAM AI Product Team*











