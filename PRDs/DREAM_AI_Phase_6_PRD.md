# DREAM AI - Phase 6 Product Requirements Document

**Product Name:** DREAM AI  
**Company:** Shieldstone Acquisitions / DREAM.AI  
**Document Type:** Phase 6 PRD (Report Generation)  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 1. Overview

This PRD covers Phase 6 of DREAM AI's acquisitions intelligence workflow:

- **BOE Memo:** 1-2 page back-of-envelope summary for quick screening
- **IC Memo:** 4-6 page Investment Committee presentation
- **Full UW Memo:** 8-10 page comprehensive underwriting report
- **HTML-First Design:** Beautiful, design-forward templates converted to PDF
- **Institutional Standards:** Reports that answer real investor questions

Phase 6 transforms analysis into investor-ready deliverables that meet institutional standards and replace manual memo writing.

---

## 2. Goals & Success Metrics

### Goals

1. Generate institutional-quality memos in under 2 minutes
2. Answer all common investor questions proactively
3. Create visually stunning, design-forward reports
4. Eliminate manual memo writing for 90%+ of deals
5. Support seamless PDF export and sharing

### Success Metrics

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| BOE memo generation time | <30 seconds | <15 seconds | Task completion |
| IC memo generation time | <90 seconds | <60 seconds | Task completion |
| Full UW memo generation time | <3 minutes | <2 minutes | Task completion |
| User satisfaction with reports | >4.5/5 | >4.8/5 | Feedback |
| Report quality (institutional review) | >90% approval | >95% approval | Investor feedback |
| Manual editing required | <20% of reports | <10% of reports | Edit tracking |

---

## 3. Report Types

### 3.1 Report Tier Comparison

| Aspect | BOE Memo | IC Memo | Full UW Memo |
|--------|----------|---------|--------------|
| **Purpose** | Quick screening decision | Investment Committee presentation | Complete due diligence documentation |
| **Length** | 1-2 pages | 4-6 pages | 8-10 pages |
| **Audience** | Internal team, quick review | IC members, partners | Investors, lenders, full team |
| **Generation Time** | <30 seconds | <90 seconds | <3 minutes |
| **LLM Usage** | Minimal (Haiku) | Moderate (Sonnet) | Full (Sonnet + Opus polish) |
| **LLM Cost Target** | <$0.05 | <$0.30 | <$1.00 |
| **Detail Level** | High-level summary | Key analysis points | Comprehensive documentation |

### 3.2 BOE Memo (Back of Envelope)

**Purpose:** Quick screening decision for deal flow triage

**Sections:**
1. **Header** - Property name, address, photo
2. **Deal Snapshot** - Key metrics table (6-8 metrics)
3. **Quick Take** - 2-3 sentence recommendation
4. **Key Highlights** - 3-4 bullet points
5. **Key Risks** - 2-3 bullet points
6. **Recommendation** - PURSUE / PASS / NEEDS REVIEW

### 3.3 IC Memo (Investment Committee)

**Purpose:** Support investment decision at IC meeting

**Sections:**
1. **Executive Summary** - 1 paragraph + recommendation
2. **Property Overview** - Location, vintage, units, photos
3. **Investment Thesis** - Why this deal, value creation plan
4. **Market Analysis** - Submarket fundamentals, comps
5. **Financial Summary** - Key returns, sources & uses
6. **Risk Factors** - Top 3-5 risks with mitigations
7. **Recommendation** - Clear recommendation with conditions

**Institutional Investor Questions (Must Answer):**
- What is the investment thesis?
- What are the key value drivers?
- What are the major risks and how are they mitigated?
- How does this compare to recent similar deals?
- What is the exit strategy?
- What are the key assumptions and how conservative are they?

### 3.4 Full UW Memo (Underwriting)

**Purpose:** Complete documentation for investors, lenders, and records

**Sections:**
1. **Executive Summary** (1 page)
2. **Property Description** (1 page)
3. **Market Analysis** (1-2 pages)
4. **Financial Analysis** (2-3 pages)
5. **Business Plan & Value Creation** (1 page)
6. **Risk Analysis** (1 page)
7. **Appendices** - Pro forma, rent roll summary, comps

**Additional Institutional Questions (Full UW Only):**
- Walk through the underwriting assumptions in detail
- How were rent growth assumptions derived?
- What is the basis for expense projections?
- How does the renovation budget compare to recent projects?
- What are the financing assumptions and alternatives?
- What is the sensitivity to key variables?
- What due diligence has been completed?
- What are the key milestones and timeline?

---

## 4. Report Content Specifications

### 4.1 BOE Memo Content

#### Header Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [Property Photo]                                                            │
│                                                                              │
│  OAK CREEK APARTMENTS                                                        │
│  1234 Oak Creek Drive, Austin, TX 78701                                      │
│                                                                              │
│  96 Units | 1985 Vintage | Class B                                           │
│  Generated: December 20, 2025                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Deal Snapshot Table

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Asking Price | $12,500,000 | — | — |
| Price/Unit | $130,208 | $125K-$160K | ✓ |
| In-Place Cap | 7.0% | 6.5%-7.5% | ✓ |
| Pro Forma Cap | 8.2% | >7.5% | ✓ |
| Projected IRR | 18.5% | >14% | ✓ |
| Equity Multiple | 1.85x | >1.50x | ✓ |
| Occupancy | 94% | >90% | ✓ |
| DSCR | 1.35x | >1.25x | ✓ |

#### Quick Take (LLM-Generated)

```
This 96-unit value-add opportunity in Austin's growing East submarket offers 
attractive risk-adjusted returns with a clear path to stabilization. The 
property's 1985 vintage and current 94% occupancy provide a stable base for 
the planned $768K interior renovation program targeting $150/unit rent premiums.
```

#### Key Highlights (LLM-Generated)

- Strong submarket fundamentals with 3.2% annual rent growth and 95.5% market occupancy
- Below-market in-place rents ($1,050 avg) vs. renovated comps ($1,200-$1,250)
- Experienced local property manager with 3 similar renovations completed
- Assumable debt at 5.5% provides $180K annual interest savings vs. market rates

#### Key Risks (LLM-Generated)

- Property tax reassessment likely to increase taxes 25-30% post-acquisition
- Renovation timeline dependent on contractor availability in tight labor market
- Submarket has 450 units under construction delivering in next 18 months

#### Recommendation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│    ████████████████████████████████████████████████████████████████████     │
│    █                                                                    █    │
│    █                         PURSUE                                     █    │
│    █                                                                    █    │
│    █   Recommend proceeding to full underwriting and LOI submission     █    │
│    █                                                                    █    │
│    ████████████████████████████████████████████████████████████████████     │
│                                                                              │
│    Score: 78/100 | Confidence: High                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.2 IC Memo Content

#### Executive Summary (Page 1)

```
INVESTMENT RECOMMENDATION: PURSUE

Oak Creek Apartments represents a compelling value-add acquisition in Austin's 
high-growth East submarket. The 96-unit, 1985-vintage property offers 
institutional-quality returns (18.5% IRR, 1.85x EM) through a proven light 
renovation strategy targeting $150/unit rent premiums.

KEY INVESTMENT MERITS:
• Below-market rents with clear path to $1,200+ post-renovation
• Strong submarket fundamentals with limited new supply
• Assumable financing providing meaningful interest rate savings
• Experienced operator with local track record

TRANSACTION SUMMARY:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Purchase Price      $12,500,000    │  Equity Required     $4,875,000      │
│  Price/Unit          $130,208       │  Projected IRR       18.5%           │
│  In-Place Cap        7.0%           │  Equity Multiple     1.85x           │
│  Stabilized Cap      8.2%           │  Hold Period         5 years         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Property Overview (Page 2)

- Property description with photos
- Unit mix table
- Amenities and features
- Location map with points of interest
- Condition assessment summary

#### Investment Thesis (Page 2-3)

**Value Creation Strategy:**
1. Interior renovations: $8,000/unit targeting $150 rent premium
2. Operational improvements: Reduce expense ratio from 48% to 44%
3. Occupancy optimization: Increase from 94% to 96% through improved marketing

**Why This Deal:**
- Submarket rent growth outpacing MSA average by 80bps
- Limited Class B competition within 1-mile radius
- Seller motivation creates favorable pricing
- Renovation scope matches sponsor's core competency

#### Market Analysis (Page 3-4)

- MSA overview and employment drivers
- Submarket deep dive with demographic data
- Competitive set analysis (5-7 comps)
- Supply/demand dynamics
- Rent comp analysis with photos

#### Financial Summary (Page 4-5)

**Sources & Uses:**
```
SOURCES                              USES
Senior Debt (65% LTV)   $8,125,000   Purchase Price        $12,500,000
LP Equity               $4,631,250   Closing Costs            $312,500
GP Co-Invest (5%)         $243,750   Acquisition Fee          $125,000
                                     Renovation Budget        $768,000
                                     Renovation Contingency    $76,800
                                     Working Capital          $218,450
─────────────────────────────────────────────────────────────────────
TOTAL                  $13,000,000   TOTAL                 $13,000,000
```

**Returns Summary:**
| Metric | Base Case | Downside | Upside |
|--------|-----------|----------|--------|
| IRR | 18.5% | 12.3% | 24.1% |
| Equity Multiple | 1.85x | 1.52x | 2.15x |
| Avg Cash-on-Cash | 8.2% | 5.1% | 10.8% |
| Net LP IRR | 15.2% | 9.8% | 20.1% |

#### Risk Factors (Page 5-6)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Renovation cost overrun | Medium | Medium | 10% contingency, fixed-price contracts |
| Slower lease-up | Low | Medium | Conservative 18-month timeline |
| Interest rate increase | Medium | Low | Fixed-rate debt, rate cap in place |
| New supply pressure | Medium | Medium | Focus on Class B value positioning |
| Property tax increase | High | Low | Budgeted 30% increase in Year 1 |

#### Recommendation (Page 6)

```
RECOMMENDATION: PROCEED TO LOI

Based on our analysis, Oak Creek Apartments meets our investment criteria and 
offers attractive risk-adjusted returns. We recommend:

1. Submit LOI at $12,250,000 (2% below ask)
2. Target 60-day due diligence period
3. Negotiate renovation credit of $100,000
4. Pursue debt assumption with 1-year extension

NEXT STEPS:
□ Finalize LOI terms with legal
□ Schedule property tour for IC members
□ Request T-12 backup documentation
□ Engage third-party inspectors

REQUIRED APPROVALS:
□ Investment Committee approval
□ LP co-investment confirmation
□ Lender pre-approval for assumption
```

---

### 4.3 Full UW Memo Content

#### Table of Contents

1. Executive Summary
2. Property Description
   - 2.1 Location & Accessibility
   - 2.2 Physical Description
   - 2.3 Unit Mix & Amenities
   - 2.4 Condition Assessment
3. Market Analysis
   - 3.1 MSA Overview
   - 3.2 Submarket Analysis
   - 3.3 Competitive Landscape
   - 3.4 Supply Pipeline
   - 3.5 Rent Comparable Analysis
4. Financial Analysis
   - 4.1 Historical Performance
   - 4.2 Underwriting Assumptions
   - 4.3 Revenue Projections
   - 4.4 Expense Projections
   - 4.5 Capital Expenditure Plan
   - 4.6 Financing Structure
   - 4.7 Returns Analysis
   - 4.8 Sensitivity Analysis
5. Business Plan
   - 5.1 Value Creation Strategy
   - 5.2 Renovation Program
   - 5.3 Operational Improvements
   - 5.4 Timeline & Milestones
6. Risk Analysis
   - 6.1 Key Risks & Mitigations
   - 6.2 Downside Scenarios
   - 6.3 Exit Strategy Alternatives
7. Appendices
   - A. Detailed Pro Forma
   - B. Rent Roll Summary
   - C. Rent Comparables
   - D. Photos
   - E. Site Plan

#### UW Analysis Section (Per Shieldstone Manual)

**4.2 Underwriting Assumptions**

This section addresses the key institutional investor questions about assumption derivation:

**Revenue Assumptions:**

| Assumption | Value | Basis |
|------------|-------|-------|
| Year 1 Rent Growth | 3.0% | Based on trailing 12-month submarket rent growth of 3.2% |
| Stabilized Rent Growth | 2.5% | Conservative estimate vs. 10-year historical average of 3.1% |
| Target Occupancy | 95% | Submarket average is 95.5%; conservative given renovation disruption |
| Loss to Lease Burn-off | 25%/year | Standard assumption for value-add with 12-month leases |
| Renovated Unit Premium | $150/unit | Based on 5 comparable renovations in submarket (range: $125-$175) |

*Rent Growth Derivation:*
- CoStar 12-month rent growth: 3.4%
- Yardi Matrix forecast: 2.8%
- Historical 5-year CAGR: 3.1%
- Blended estimate: 3.0% Year 1, 2.5% stabilized

**Expense Assumptions:**

| Line Item | Year 1 | Growth Rate | Basis |
|-----------|--------|-------------|-------|
| Property Taxes | $312,500 | 2.5% | Post-reassessment at purchase price × 2.5% rate |
| Insurance | $72,000 | 5.0% | Current policy + 15% for hardening market |
| Utilities | $115,200 | 3.0% | T-12 actual + RUBS implementation savings |
| R&M | $86,400 | 3.0% | T-12 actual, reduced post-renovation |
| Payroll | $134,400 | 3.5% | 1.4 FTE on-site staff at market rates |
| Management | 3.0% EGI | — | Third-party PM contract |
| Reserves | $28,800 | 3.0% | $300/unit per Shieldstone standard |

*Property Tax Calculation:*
- Current assessed value: $8,500,000
- Purchase price: $12,500,000
- Current tax rate: 2.5%
- Projected Year 1 taxes: $12,500,000 × 2.5% = $312,500
- Represents 47% increase from current $212,500

**Renovation Budget:**

| Component | $/Unit | Total | Comparable Basis |
|-----------|--------|-------|------------------|
| Interior Package | $6,500 | $624,000 | Average of 3 recent renovations in submarket |
| Exterior/Common | $1,500 | $144,000 | Deferred maintenance + signage |
| **Subtotal** | $8,000 | $768,000 | |
| Contingency (10%) | $800 | $76,800 | Standard value-add contingency |
| **Total** | $8,800 | $844,800 | |

*Interior Package Scope:*
- New flooring (LVP): $2,000
- Cabinet refacing + hardware: $1,500
- Countertops (quartz): $1,200
- Appliances (SS package): $1,200
- Fixtures + paint: $600

*Renovation Cost Validation:*
- Comp 1 (Riverside Flats, 2023): $7,200/unit → $140 premium
- Comp 2 (Eastside Commons, 2024): $8,500/unit → $165 premium
- Comp 3 (Mueller Place, 2023): $6,800/unit → $125 premium
- Our budget: $8,000/unit → $150 premium (conservative)

**Financing Assumptions:**

| Term | Assumption | Basis |
|------|------------|-------|
| LTV | 65% | Conservative vs. 70-75% available |
| Interest Rate | 6.5% | Current 5-year fixed rate + 25bps buffer |
| Amortization | 30 years | Standard |
| IO Period | 3 years | To support renovation period cash flow |
| Loan Term | 5 years | Match hold period |
| DSCR (Stabilized) | 1.35x | Exceeds 1.25x minimum |

*Financing Alternatives Considered:*
- Debt assumption: 5.5% rate, saves $180K/year, requires lender approval
- Agency (Fannie/Freddie): 5.8% rate, higher proceeds, longer timeline
- Bridge: 7.5% rate, higher LTV, more flexibility

---

## 5. HTML Template Architecture

### 5.1 Design Philosophy

**Core Principles:**
- **Design-forward:** Reports should look like they came from a top-tier design agency
- **Brand-consistent:** Unified visual language across all report types
- **Print-optimized:** Perfect PDF conversion with proper page breaks
- **Responsive:** Web viewing on any device
- **Accessible:** WCAG 2.1 AA compliant

### 5.2 Template Structure

```
reports/
├── templates/
│   ├── base/
│   │   ├── base.html              # Shared layout
│   │   ├── variables.css          # Design tokens
│   │   ├── typography.css         # Font system
│   │   ├── colors.css             # Color palette
│   │   └── print.css              # Print styles
│   ├── boe/
│   │   ├── boe-template.html
│   │   ├── boe-styles.css
│   │   └── components/
│   │       ├── header.html
│   │       ├── metrics-table.html
│   │       ├── quick-take.html
│   │       └── recommendation.html
│   ├── ic-memo/
│   │   ├── ic-template.html
│   │   ├── ic-styles.css
│   │   └── components/
│   │       ├── cover-page.html
│   │       ├── executive-summary.html
│   │       ├── property-overview.html
│   │       ├── market-analysis.html
│   │       ├── financial-summary.html
│   │       ├── risk-factors.html
│   │       └── recommendation.html
│   └── full-uw/
│       ├── full-uw-template.html
│       ├── full-uw-styles.css
│       └── components/
│           ├── toc.html
│           ├── executive-summary.html
│           ├── property-description.html
│           ├── market-analysis.html
│           ├── financial-analysis.html
│           ├── business-plan.html
│           ├── risk-analysis.html
│           └── appendices.html
├── shared/
│   ├── components/
│   │   ├── data-table.html
│   │   ├── chart-container.html
│   │   ├── metric-card.html
│   │   ├── photo-gallery.html
│   │   └── map-embed.html
│   ├── charts/
│   │   ├── bar-chart.js
│   │   ├── line-chart.js
│   │   ├── pie-chart.js
│   │   └── waterfall-chart.js
│   └── branding/
│       ├── logo.svg
│       ├── fonts/
│       └── icons/
└── converters/
    ├── html-to-pdf.py
    └── html-to-image.py
```

### 5.3 Design System

#### Color Palette

```css
:root {
  /* Primary */
  --color-primary: #1E3A5F;        /* Deep navy */
  --color-primary-light: #2E5A8F;
  --color-primary-dark: #0E2A4F;
  
  /* Accent */
  --color-accent: #C9A227;         /* Gold */
  --color-accent-light: #E5C547;
  
  /* Semantic */
  --color-success: #059669;        /* Green */
  --color-warning: #D97706;        /* Amber */
  --color-danger: #DC2626;         /* Red */
  
  /* Neutrals */
  --color-text: #1F2937;
  --color-text-muted: #6B7280;
  --color-border: #E5E7EB;
  --color-background: #FFFFFF;
  --color-background-alt: #F9FAFB;
  
  /* Gradients */
  --gradient-header: linear-gradient(135deg, #1E3A5F 0%, #2E5A8F 100%);
}
```

#### Typography

```css
:root {
  /* Font Families */
  --font-display: 'Playfair Display', Georgia, serif;
  --font-body: 'Source Sans Pro', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 2rem;      /* 32px */
  --text-4xl: 2.5rem;    /* 40px */
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}

/* Heading Styles */
h1 {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.02em;
}

h2 {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.5rem;
}
```

#### Component Examples

**Metric Card:**

```html
<div class="metric-card">
  <div class="metric-value">18.5%</div>
  <div class="metric-label">Projected IRR</div>
  <div class="metric-status metric-status--pass">
    <svg class="icon"><!-- checkmark --></svg>
    Above 14% hurdle
  </div>
</div>

<style>
.metric-card {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metric-value {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--color-primary);
}

.metric-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.25rem;
}

.metric-status {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: var(--text-xs);
  margin-top: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.metric-status--pass {
  background: #D1FAE5;
  color: var(--color-success);
}

.metric-status--fail {
  background: #FEE2E2;
  color: var(--color-danger);
}
</style>
```

**Data Table:**

```html
<table class="data-table">
  <thead>
    <tr>
      <th>Metric</th>
      <th class="text-right">Value</th>
      <th class="text-right">Benchmark</th>
      <th class="text-center">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Projected IRR</td>
      <td class="text-right font-mono">18.5%</td>
      <td class="text-right text-muted">>14%</td>
      <td class="text-center"><span class="badge badge--success">✓</span></td>
    </tr>
  </tbody>
</table>

<style>
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.data-table th {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  padding: 0.75rem 1rem;
  text-align: left;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
}

.data-table tr:nth-child(even) {
  background: var(--color-background-alt);
}

.data-table tr:hover {
  background: #F3F4F6;
}
</style>
```

---

## 6. LLM Prompting Strategy

### 6.1 BOE Memo Prompts

**Quick Take Generation (Haiku):**

```
You are a real estate investment analyst writing a brief summary for a back-of-envelope memo.

Property: {property_name}
Location: {city}, {state}
Units: {units}
Vintage: {year_built}
Asking Price: ${asking_price:,.0f}
In-Place Cap: {cap_rate_in_place:.1%}
Projected IRR: {projected_irr:.1%}
Occupancy: {occupancy:.0%}
Investment Strategy: {strategy}

Write a 2-3 sentence "Quick Take" that:
1. Summarizes the opportunity in plain language
2. Highlights the key value driver
3. Notes any standout positive or concern

Be concise and direct. Avoid jargon. Write for a busy investment professional.
```

**Highlights/Risks Generation (Haiku):**

```
Based on the following deal data, generate:
1. 3-4 Key Highlights (positive aspects)
2. 2-3 Key Risks (concerns or challenges)

Each bullet should be one sentence, specific, and actionable.

Deal Data:
{deal_summary_json}

Format as JSON:
{
  "highlights": ["...", "...", "..."],
  "risks": ["...", "..."]
}
```

### 6.2 IC Memo Prompts

**Executive Summary (Sonnet):**

```
You are a senior investment analyst preparing an Investment Committee memo for a multifamily acquisition.

Write a compelling Executive Summary (2-3 paragraphs) that:
1. Opens with a clear recommendation (PURSUE/PASS)
2. Summarizes the investment thesis in 2-3 sentences
3. Lists 3-4 key investment merits as bullet points
4. Acknowledges primary risks briefly
5. Concludes with conviction level

Property Data:
{property_data_json}

Financial Summary:
{financial_data_json}

Market Data:
{market_data_json}

Tone: Professional, confident, balanced. Write as if presenting to sophisticated institutional investors.
```

**Risk Analysis (Sonnet):**

```
Analyze the following deal and identify the top 5 risks. For each risk:
1. Name the risk clearly
2. Assess probability (Low/Medium/High)
3. Assess impact (Low/Medium/High)
4. Provide a specific mitigation strategy

Consider:
- Market risks (supply, demand, rent growth)
- Property risks (condition, age, deferred maintenance)
- Execution risks (renovation, lease-up, timeline)
- Financial risks (interest rates, refinancing, exit cap)
- Operational risks (management, staffing, expenses)

Deal Data:
{complete_deal_json}

Format as a structured table.
```

### 6.3 Full UW Memo Prompts

**Assumption Narrative (Sonnet):**

```
You are documenting underwriting assumptions for an institutional investor audience.

For each assumption category below, write 2-3 sentences explaining:
1. What assumption was made
2. The basis/source for the assumption
3. How conservative or aggressive it is relative to market

Categories:
1. Revenue assumptions (rent growth, occupancy, loss to lease)
2. Expense assumptions (property taxes, insurance, operating costs)
3. Renovation budget (scope, cost per unit, timeline)
4. Financing terms (LTV, rate, structure)
5. Exit assumptions (cap rate, hold period)

Data:
{assumptions_json}

Market Benchmarks:
{benchmarks_json}

Comparable Transactions:
{comps_json}

Write in third person, professional tone. Be specific with numbers and sources.
```

**Final Polish (Opus):**

```
You are a senior editor reviewing an Investment Committee memo before it goes to institutional investors.

Review the following memo for:
1. Clarity and flow
2. Professional tone
3. Logical consistency
4. Completeness of analysis
5. Persuasiveness of recommendation

Make targeted improvements while preserving the analytical content. Focus on:
- Tightening language
- Improving transitions
- Strengthening key points
- Ensuring consistent formatting

Current Memo:
{draft_memo}

Return the polished version with track changes noted.
```

---

## 7. API Specifications

### 7.1 Report Generation Endpoints

#### Generate BOE Memo

```
POST /api/v1/deals/{deal_id}/reports/boe

Request Body:
{
  "format": "html",  // "html" or "pdf"
  "include_photo": true,
  "custom_notes": "Focus on the assumable debt opportunity"
}

Response (202 Accepted):
{
  "job_id": "rpt_abc123",
  "status": "PROCESSING",
  "estimated_time_seconds": 15
}
```

#### Generate IC Memo

```
POST /api/v1/deals/{deal_id}/reports/ic-memo

Request Body:
{
  "format": "html",
  "include_sections": ["executive_summary", "property_overview", "market_analysis", 
                       "financial_summary", "risk_factors", "recommendation"],
  "include_appendices": false,
  "custom_emphasis": ["assumable_debt", "renovation_upside"]
}

Response (202 Accepted):
{
  "job_id": "rpt_def456",
  "status": "PROCESSING",
  "estimated_time_seconds": 60
}
```

#### Generate Full UW Memo

```
POST /api/v1/deals/{deal_id}/reports/full-uw

Request Body:
{
  "format": "html",
  "include_appendices": true,
  "proforma_version": 3,
  "scenario": "base_case"
}

Response (202 Accepted):
{
  "job_id": "rpt_ghi789",
  "status": "PROCESSING",
  "estimated_time_seconds": 120
}
```

#### Get Report Status

```
GET /api/v1/reports/{job_id}

Response (200 OK):
{
  "job_id": "rpt_abc123",
  "status": "COMPLETED",
  "report_type": "BOE",
  "format": "html",
  "created_at": "2025-12-20T10:30:00Z",
  "completed_at": "2025-12-20T10:30:12Z",
  "html_url": "https://app.dreamai.com/reports/rpt_abc123.html",
  "pdf_url": "https://app.dreamai.com/reports/rpt_abc123.pdf",
  "llm_cost_cents": 5,
  "generation_time_ms": 12000
}
```

#### Convert to PDF

```
POST /api/v1/reports/{job_id}/pdf

Request Body:
{
  "paper_size": "letter",  // "letter" or "a4"
  "orientation": "portrait",
  "include_cover": true
}

Response (200 OK):
{
  "pdf_url": "https://storage.dreamai.com/reports/rpt_abc123.pdf",
  "file_size_bytes": 2456789,
  "page_count": 6
}
```

---

## 8. Database Schema

```sql
-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Report details
    report_type report_type_enum NOT NULL,  -- BOE, IC_MEMO, FULL_UW
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Generation status
    status report_status_enum NOT NULL DEFAULT 'PENDING',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- Content
    html_content TEXT,
    html_url VARCHAR(500),
    pdf_url VARCHAR(500),
    
    -- Source data snapshot
    deal_snapshot JSONB,
    proforma_snapshot JSONB,
    market_data_snapshot JSONB,
    
    -- LLM tracking
    llm_prompts JSONB,
    llm_responses JSONB,
    llm_cost_cents INTEGER,
    llm_tokens_used INTEGER,
    
    -- Performance
    generation_time_ms INTEGER,
    pdf_conversion_time_ms INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Report templates (customizable)
CREATE TABLE report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    
    name VARCHAR(100) NOT NULL,
    report_type report_type_enum NOT NULL,
    
    -- Template content
    html_template TEXT NOT NULL,
    css_styles TEXT,
    
    -- Customization
    color_primary VARCHAR(7),
    color_accent VARCHAR(7),
    logo_url VARCHAR(500),
    font_family VARCHAR(100),
    
    is_default BOOLEAN NOT NULL DEFAULT false,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Report shares
CREATE TABLE report_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    
    -- Share details
    share_token VARCHAR(64) NOT NULL UNIQUE,
    recipient_email VARCHAR(255),
    recipient_name VARCHAR(100),
    
    -- Access control
    expires_at TIMESTAMPTZ,
    password_hash VARCHAR(255),
    max_views INTEGER,
    current_views INTEGER DEFAULT 0,
    
    -- Tracking
    first_viewed_at TIMESTAMPTZ,
    last_viewed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_reports_deal ON reports(deal_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_templates_org ON report_templates(organization_id);
CREATE INDEX idx_shares_token ON report_shares(share_token);
```

---

## 9. Presentation Deck Generation (Future)

### 9.1 Deck API Evaluation

| Tool | API Available | Pricing | Quality | Integration Effort |
|------|---------------|---------|---------|-------------------|
| Gamma.ai | Private beta | TBD | High | Medium |
| Beautiful.ai | Yes | $12/user/mo | High | Low |
| Tome | Limited | $16/user/mo | Medium | Medium |
| Custom (reveal.js) | N/A | Dev time | Variable | High |

### 9.2 Recommended Approach

**Phase 1 (MVP):** Focus on HTML + PDF reports only

**Phase 2 (Post-MVP):** Evaluate deck generation options:
1. Partner with Gamma.ai for API access
2. Build custom solution using reveal.js + AI content
3. Export to PowerPoint/Google Slides format

### 9.3 IC Presentation Structure

```
Slide 1: Title + Property Photo
Slide 2: Executive Summary + Recommendation
Slide 3: Investment Thesis (3 key points)
Slide 4: Property Overview + Unit Mix
Slide 5: Market Analysis (key charts)
Slide 6: Financial Summary (returns table)
Slide 7: Value Creation Plan
Slide 8: Risk Factors + Mitigations
Slide 9: Recommendation + Next Steps
Slide 10: Appendix (optional)
```

---

## 10. Testing Requirements

### 10.1 Content Quality Tests

| Test | Method | Target |
|------|--------|--------|
| Factual accuracy | Compare to source data | 100% |
| Calculation accuracy | Verify all numbers | 100% |
| Narrative coherence | Human review | >4.5/5 |
| Institutional appropriateness | Expert review | >90% approval |

### 10.2 Performance Tests

| Operation | Target | Method |
|-----------|--------|--------|
| BOE generation | <30 seconds | Load test |
| IC memo generation | <90 seconds | Load test |
| Full UW generation | <180 seconds | Load test |
| PDF conversion | <10 seconds | Load test |

### 10.3 Visual Tests

- Screenshot comparison across browsers
- Print preview validation
- Mobile responsiveness
- Accessibility audit (WCAG 2.1 AA)

---

## 11. Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| Custom branding per organization? | Yes | Logo, colors in template |
| Report versioning/history? | Yes | Track all versions |
| Collaborative editing? | Future | Post-MVP |
| Multi-language support? | Future | English only for MVP |
| White-label option? | Future | Consider for enterprise |

---

## 12. Rollout Plan

### Phase 6a: BOE Memo (Week 5)
- HTML template design
- LLM prompt development
- PDF conversion pipeline

### Phase 6b: IC Memo (Week 5-6)
- Extended template
- Multi-section generation
- Chart integration

### Phase 6c: Full UW Memo (Week 6)
- Complete template
- Appendix generation
- Polish pass with Opus

### Phase 6d: Sharing & Export (Week 6)
- Share links
- Email delivery
- Download options

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Author: DREAM AI Product Team*









