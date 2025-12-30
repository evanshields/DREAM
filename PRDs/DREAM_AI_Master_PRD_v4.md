# DREAM AI Master PRD v4.0
## Domain 1 | Unified Acquisitions Intelligence Platform

**Product Name:** DREAM AI  
**Full Name:** Development, Real Estate and Asset Management Analysis Interface  
**Version:** 4.0  
**Last Updated:** December 2025  
**Status:** Ready for Development  
**Development Approach:** AI-assisted coding (Claude Code / Cursor)

---

## Brand Context

**DREAM AI** is Domain 1 within the **DREAM.AI** super app ecosystem.

**DREAM.AI** is a comprehensive platform covering the entire real estate investment lifecycle. DREAM AI (this product) is the first of four planned domains:

| Domain | Name | Focus | Status |
|--------|------|-------|--------|
| **Domain 1** | **DREAM AI** | Acquisitions Intelligence & Underwriting | **This PRD** |
| Domain 2 | TBD | Investor Relations & Capital Raising | Future |
| Domain 3 | TBD | Asset Management & Operations | Future |
| Domain 4 | TBD | Construction & Development | Future |

All domains share common infrastructure (auth, billing, data model) and will eventually integrate for cross-domain intelligence. DREAM AI is the priority launch product.

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Development Phases](#2-development-phases)
3. [Core Analytical Methodology (Shieldstone Integration)](#3-core-analytical-methodology)
4. [LLM Architecture & Cost Optimization](#4-llm-architecture--cost-optimization)
5. [Core Functional Requirements](#5-core-functional-requirements)
6. [Data Models](#6-data-models)
7. [Technical Architecture](#7-technical-architecture)
8. [User Experience Guidelines](#8-user-experience-guidelines)
9. [Report Generation Framework](#9-report-generation-framework)
10. [Data Strategy & Market Intelligence](#10-data-strategy--market-intelligence)
11. [Integration Architecture](#11-integration-architecture)
12. [Success Metrics](#12-success-metrics)
13. [Development Notes for AI Coding Assistant](#13-development-notes-for-ai-coding-assistant)
14. [Asset Class Reference](#14-asset-class-reference)
15. [Shieldstone Python Library](#15-shieldstone-python-library)
16. [Glossary](#16-glossary)

---

# 1. Product Overview

## 1.1 What is DREAM AI?

DREAM AI is an AI-powered acquisitions intelligence platform that helps real estate investors discover, analyze, and pursue investment opportunities. It combines market intelligence, deal screening, pipeline management, and automated underwriting into a single workflow—powered by the Shieldstone Technical Underwriting Manual methodology.

**Core Value Proposition:** Reduce deal analysis time from 4-8 hours to under 7 minutes while maintaining institutional-quality output at a fraction of traditional software costs.

## 1.2 Target Users

| User Type | Description | Monthly Deal Volume |
|-----------|-------------|---------------------|
| **Investment Firms** | Real estate PE firms evaluating deal flow | 20-100+ deals/month |
| **Emerging Sponsors** | Operators seeking to scale without scaling headcount | 10-50 deals/month |
| **Family Offices** | Institutional investors wanting AI-powered advantage | 5-30 deals/month |
| **Brokers & Advisors** | Professionals needing fast, consistent screening | 10-50 deals/month |

**Target Customer Profile:**
- Analyzes 30-50 deals per month on average
- Currently spends 4-8 hours per deal in manual analysis
- Pays $500-2,000/month for existing tools (Argus, CoStar, etc.)
- Wants institutional-quality output without institutional-level costs

## 1.3 What DREAM AI Replaces

| Current Approach | Pain Point | DREAM AI Solution |
|-----------------|------------|-------------------|
| Manual market research | Hours aggregating data sources | AI-powered instant market intelligence |
| Spreadsheet deal tracking | No workflow, fragmented data | Purpose-built pipeline CRM |
| Manual underwriting in Excel | 4-8 hours, inconsistent methodology | Shieldstone-powered AI underwriting in minutes |
| Argus / RedIQ | $15K-50K/year, steep learning curve | Intuitive AI-native DCF modeling |
| Separate sourcing tools | Reactive, no integration | Integrated sourcing + analysis (future) |

## 1.4 Competitive Positioning

| Competitor | Price Point | DREAM AI Advantage |
|------------|-------------|-------------------|
| Argus Enterprise | $15,000-50,000/year | 10x cheaper, AI-native, faster learning curve |
| RedIQ | $500-1,500/month | More comprehensive analysis, better UX |
| Reonomy | $500-2,000/month | Integrated underwriting (not just data) |
| CoStar | $500-1,500/month | Actionable analysis, not just data |
| Excel + Manual | "Free" (labor cost) | 90% time savings, institutional methodology |

---

# 2. Development Phases

## 2.1 Phase Overview

| Phase | Name | MVP? | Timeline | Description |
|-------|------|------|----------|-------------|
| **1** | Deal Intake & Document Processing | ✅ | Weeks 1-2 | Upload OMs, extract data, validate |
| **2** | Screening & Investment Criteria | ✅ | Weeks 2-3 | Configure criteria, merit-based screening, scoring |
| **3** | Market Research (Lite) | ✅ | Weeks 3-4 | Essential market data for memos/scoring |
| **4** | Pro Forma Engine | ✅ | Weeks 4-8 | Complete DCF modeling, no Excel required |
| **5** | Excel Export & Assumption Mapping | ⚠️ | Weeks 8-10 | House model + custom template mapping |
| **6** | Report Generation | ✅ | Weeks 6-8 | BOE, IC Memo, Full UW Memo |
| **7** | Pipeline CRM | ✅ | Weeks 8-10 | Kanban, tasks, deal tracking |
| **8** | Slack AI Agent | ❌ | Post-MVP | Real-time deal assistant via Slack |
| **9** | Sensitivity & Scenarios | ⚠️ | Post-MVP | Advanced modeling features |
| **10** | Deal Sourcing & Alerts | ❌ | Future | Proactive opportunity identification |
| **11** | Asset Class: SFR BPL | ⚠️ | Post-MVP | Fix & flip, DSCR rentals, ground-up |
| **12** | Asset Class Expansion | ❌ | Future | Student, MHC, Senior, Industrial, etc. |

**Legend:**
- ✅ MVP (Must have for launch)
- ⚠️ MVP+ (High priority post-launch)
- ❌ Post-MVP (Future enhancement)

## 2.2 Phase 1: Deal Intake & Document Processing

**Goal:** Enable users to upload deal documents and extract structured data automatically.

**Features:**
- Document upload (PDF, Excel, images)
- AI-powered data extraction (property details, financials, rent rolls)
- Data validation and confidence scoring
- Manual override and correction interface
- Document storage and organization

**Key Inputs:**
- Offering Memorandums (PDF)
- Trailing 12-Month Operating Statements (Excel/PDF)
- Rent Rolls (Excel/PDF)
- Financial Models (Excel)
- Property photos

**Key Outputs:**
- Structured property data record
- Extracted financial metrics
- Confidence scores per field
- Flagged items requiring review

**Success Criteria:**
- >85% extraction accuracy on standard OMs
- <3 minutes processing time per document
- <$0.10 LLM cost per document extraction

---

## 2.3 Phase 2: Screening & Investment Criteria

**Goal:** Enable users to configure investment criteria and automatically screen deals using the Shieldstone merit-based framework.

**Features:**
- Configurable investment criteria (hard stops, soft preferences, target ranges)
- Merit-based screening (no arbitrary disqualifiers)
- Risk-adjusted hurdle calculation
- Red flag identification
- Deal scoring with weighted categories
- Pass/Proceed/Proceed with Caution recommendations

**Shieldstone Integration:**
- Section 1.1: Return hurdle calculator
- Section 2.1: Merit-based deal screener
- Risk adjustment matrix (age, occupancy, class, submarket)

**Key Outputs:**
- Screening result (Pass/Proceed/Request Repricing)
- Adjusted IRR hurdle with breakdown
- Risk factor summary
- Red flag alerts (if any)

**Success Criteria:**
- Screening completed in <30 seconds
- 100% alignment with Shieldstone methodology
- <$0.05 LLM cost per screening

---

## 2.4 Phase 3: Market Research (Lite)

**Goal:** Provide essential market context for deal analysis and memo generation.

**MVP Scope (Lite):**
- MSA identification and tier classification
- Submarket vacancy and rent growth
- Top 5-10 employers
- Population and job growth trends
- Walk Score / Transit Score
- Basic regulatory flags (rent control, etc.)

**Future Scope (Full):**
- Deep submarket analysis
- Construction pipeline tracking
- Comp set identification
- Historical trend charts
- Custom market reports
- Saved market alerts

**Data Sources:**
- Perplexity API (real-time research)
- Census Bureau API
- BLS Employment Data
- Walk Score API
- Public records

**Success Criteria:**
- >80% of key market data points populated
- <60 seconds for market research
- <$0.15 LLM cost per market research

---

## 2.5 Phase 4: Pro Forma Engine

**Goal:** Build a complete, standalone DCF modeling engine that can replace Excel entirely for deal analysis.

**This is the core analytical engine of DREAM AI.** It must be powerful enough that users never need to touch Excel if they don't want to.

**Features:**
- Full 10-year pro forma generation
- Monthly and annual cash flow views
- Rent roll import and unit-level modeling
- AI-suggested assumptions with manual override
- Revenue underwriting (in-place, market, growth)
- Operating expense modeling (with state-specific taxes)
- Capital expenditure planning
- Debt modeling (bridge, agency, multiple tranches)
- Refinancing scenarios (90/90 rule)
- Waterfall modeling (GP/LP splits, promotes, preferred returns)
- Returns calculation (IRR, EM, CoC, DSCR)
- Real-time recalculation (<100ms)

**Shieldstone Integration:**
- Section 3: Revenue underwriting
- Section 4: Operating expenses (including 4.2 state-specific property tax)
- Section 5: Capital expenditure
- Section 6: Financing structures (including 6.5 refinancing, 6.6 ground lease, 6.7 fees/promote)
- Section 7: Returns analysis (including 7.2 exit cap triangulation)

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    PRO FORMA ENGINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AI LAYER (Assumption Generation)                               │
│  ─────────────────────────────────                              │
│  • LLM analyzes OM, T-12, rent roll, market data                │
│  • Generates initial assumptions per Shieldstone methodology    │
│  • Provides confidence scores and rationale                     │
│                                                                  │
│  PYTHON CALCULATION ENGINE (Deterministic)                      │
│  ─────────────────────────────────────────                      │
│  • ALL financial calculations in Python (not LLM)               │
│  • Instant recalculation (<100ms)                               │
│  • Auditable, testable, reliable                                │
│  • Implements Shieldstone formulas exactly                      │
│                                                                  │
│  INTERACTIVE UI                                                 │
│  ──────────────                                                 │
│  • Edit any assumption                                          │
│  • See real-time impact on returns                              │
│  • Compare scenarios side-by-side                               │
│  • Export to Excel with working formulas                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Critical Design Principle:** The LLM generates assumptions; Python calculates everything. This ensures:
- Instant recalculation (no API latency)
- Zero cost for assumption tweaking
- Deterministic, auditable results
- Exact implementation of Shieldstone methodology

**Success Criteria:**
- Complete pro forma in <5 minutes (including AI assumption generation)
- <$0.50 LLM cost for assumption generation
- 100ms recalculation time for manual tweaks
- Matches Excel model outputs within 0.01%

---

## 2.6 Phase 5: Excel Export & Assumption Mapping

**Goal:** Enable users to export analysis to Excel and map assumptions to their own models.

**Tier 1: DREAM AI Excel Export (Included)**
- Export complete pro forma to Excel
- Working formulas (not just values)
- Professional formatting
- All assumptions clearly labeled

**Tier 2: DREAM AI House Model (Premium)**
- Push assumptions to our standardized institutional template
- Matches format of major institutional investors
- Includes sensitivity tables, waterfall, etc.

**Tier 3: Custom Model Mapping (Enterprise)**
- User uploads their Excel template once
- DREAM AI maps assumption fields to their cell references
- Assumptions auto-populate their proprietary model
- Preserves all their custom formulas/logic

**Assumption Fields for Mapping:**
(Based on institutional pro forma structure)

```typescript
interface ProFormaAssumptions {
  // Property Information
  property: {
    assetName: string;
    yearBuilt: number;
    units: number;
    buildings: number;
    netRentableSF: number;
    avgUnitSize: number;
    address: string;
  };
  
  // Acquisition
  acquisition: {
    purchasePrice: number;
    pricePerUnit: number;
    pricePerSF: number;
    acquisitionFee: number;
    assetMgmtFee: number;
    closingCosts: number;
    goingInCapRate: number;
  };
  
  // Financing
  seniorDebt: {
    loanAmount: number;
    ltv: number;
    interestRate: number;
    amortization: number;
    term: number;
    interestOnlyPeriod: number;
  };
  
  // Exit
  exit: {
    holdPeriodMonths: number;
    exitCapRate: number;
    exitClosingCosts: number;
  };
  
  // Unit Mix & Rents
  unitMix: Array<{
    unitType: string;
    count: number;
    avgSF: number;
    inPlaceRent: number;
    marketRent: number;
    proFormaRent: number;
  }>;
  
  // Growth Assumptions
  growthAssumptions: {
    marketRentGrowth: number[];
    otherIncomeGrowth: number[];
    physicalVacancy: number[];
    concessions: number[];
    expenseGrowthRate: number[];
  };
  
  // Operating Expenses
  operatingExpenses: {
    managementFee: { amount: number; perUnit: number };
    payrollPersonnel: { amount: number; perUnit: number };
    generalAdmin: { amount: number; perUnit: number };
    marketing: { amount: number; perUnit: number };
    repairsMaintenance: { amount: number; perUnit: number };
    utilities: { amount: number; perUnit: number };
    propertyTaxes: { amount: number; perUnit: number };
    insurance: { amount: number; perUnit: number };
    replacementReserves: { amount: number; perUnit: number };
  };
  
  // Construction/Renovation
  constructionBudget: {
    exteriorBudget: number;
    interiorBudget: number;
    contingency: number;
    totalBudget: number;
  };
  
  // Waterfall
  waterfall: {
    gpEquityPercent: number;
    lpEquityPercent: number;
    preferredReturn: number;
    hurdles: Array<{
      returnThreshold: number;
      gpShare: number;
      lpShare: number;
    }>;
  };
}
```

---

## 2.7 Phase 6: Report Generation

**Goal:** Generate professional investment memos at three tiers of depth.

### Memo Tiers

| Tier | Name | Pages | Use Case | LLM Cost Target |
|------|------|-------|----------|-----------------|
| **Tier 1** | BOE Memo | 1-2 | Quick screening, broker response | $0.05-0.15 |
| **Tier 2** | IC Memo | 4-6 | Investment Committee presentation | $0.50-1.00 |
| **Tier 3** | Full UW Memo | 8-10 | Due diligence, investor packages | $2.00-4.00 |

### BOE Memo Structure (1-2 pages)

```
PAGE 1:
├── Header (Property name, address, date)
├── Property Photo + Location Map
├── Executive Summary (2-3 sentences)
├── Key Metrics Table
│   ├── Purchase Price / Price per Unit
│   ├── Going-In Cap Rate
│   ├── Stabilized Cap Rate
│   ├── IRR / Equity Multiple
│   └── Cash-on-Cash (Stabilized)
├── Investment Score (0-100) with breakdown
└── Recommendation (Strong Buy / Buy / Hold / Pass)

PAGE 2 (optional):
├── Market Snapshot (3-4 bullets)
├── Key Risks (3-4 bullets)
├── Value Creation Thesis (2-3 bullets)
└── Recommended Next Steps
```

### IC Memo Structure (4-6 pages)

```
PAGE 1: Executive Summary + Recommendation
├── Property overview
├── Investment thesis
├── Key metrics summary
├── Score and recommendation

PAGE 2: Property Overview + Photos
├── Property description
├── Unit mix table
├── Renovation scope summary
├── Photos (exterior, interior, amenities)

PAGE 3: Market Analysis
├── MSA overview
├── Submarket fundamentals
├── Employment drivers
├── Competitive supply
├── Rent growth outlook

PAGE 4: Financial Summary
├── Sources & Uses
├── Pro forma summary (5-year)
├── Key assumptions table
├── Returns summary

PAGE 5: Sensitivity Analysis
├── Exit cap sensitivity
├── Rent growth sensitivity
├── Vacancy sensitivity
├── Combined scenario matrix

PAGE 6: Risk Factors + Mitigations
├── Property risks
├── Market risks
├── Execution risks
├── Mitigations for each
```

### Full UW Memo Structure (8-10 pages)

```
PAGES 1-6: Everything from IC Memo

PAGE 7: Detailed Assumptions Walkthrough
├── Revenue assumptions with rationale
├── Expense assumptions with rationale
├── CapEx assumptions with rationale
├── Financing assumptions with rationale

PAGE 8: Full Pro Forma (10-Year)
├── Annual revenue detail
├── Annual expense detail
├── NOI progression
├── Cash flow summary

PAGE 9: Waterfall Analysis
├── Equity structure
├── Preferred return tracking
├── Promote calculations
├── GP/LP returns by year

PAGE 10: Appendix
├── Rent roll summary
├── Expense detail
├── Market data sources
├── Comparable transactions
```

### Institutional Investor Questions (IC/Full UW Memos)

The following questions must be addressed in IC and Full UW memos:

**Project Overview:**
1. Property Description – age, construction quality, condition
2. Value Creation – how will returns be achieved?
3. Location Overview – population and industry
4. Local Market Overview – asset positioning within market
5. Description of Tenancy – keep existing? delinquencies?
6. Description of Planned Improvements – how do improvements compare to market?
7. Description of Deferred Maintenance
8. Social impact or ESG considerations
9. Sponsor experience and core competency alignment

**Opportunities:**
1. What opportunity is the market/competition missing?
2. Why do you expect to win? Already tied up?
3. Who is the seller and why are they selling?
4. Where is the property within its comp set?

**Risks:**
1. Where does the project risk losing money?
2. Material physical concerns for DD?
3. Material economic concerns for DD?
4. Local government risks affecting cash flow?
5. Crime issues at property or area?

**Market Data Points:**
- Submarket/market vacancy
- Rent growth projections
- Population growth
- Job growth drivers
- Top 5-10 employers + job counts
- Avg household income (2-mi and 5-mi radius)
- School ratings
- Transit options
- Renter-occupied vs. owner-occupied ratio

**Value Creation Checklist:**
- Off-market transaction advantage
- DD period advantage
- Inside information advantage
- Superior submarket expertise
- Unique value-creation approach
- Renovation cost/time efficiencies
- Conviction in outsized growth
- Leasing advantages
- Lease restructuring opportunities
- Additional income through other uses
- Superior management
- Correcting mismanagement
- Reducing operating expenses
- Operating efficiencies (nearby ownership)
- Superior financing terms
- Financial subsidies

---

## 2.8 Phase 7: Pipeline CRM

**Goal:** Provide a purpose-built deal tracking system integrated with analysis.

**Features:**
- Deal records with all associated analyses
- Configurable pipeline stages
- Kanban board (drag-and-drop)
- List view with filtering/sorting
- Map view (deals by location)
- Calendar view (key dates)
- Task management with assignments
- Notes and activity logging
- Team collaboration
- Document attachments

**Default Pipeline Stages:**
```
New → Screening → LOI → Due Diligence → Under Contract → Closed / Passed
```

**Deal Record Structure:**
- Property information
- All associated analyses (BOE, Full UW)
- Documents and attachments
- Notes and activity log
- Tasks with assignments and due dates
- Status/stage tracking
- Team member access

---

## 2.9 Phase 8: Slack AI Agent (Post-MVP)

**Goal:** Enable users to interact with DREAM AI directly from Slack.

**Key Commands:**
```
@DREAMAI analyze [address]        → Quick BOE analysis
@DREAMAI status [deal name]       → Pipeline status update
@DREAMAI memo [deal name]         → Generate/retrieve memo
@DREAMAI compare [deal1] vs [deal2] → Side-by-side comparison
@DREAMAI market [city/submarket]  → Market snapshot
@DREAMAI help                     → List available commands
```

**Notification Types:**
- New deal added to pipeline
- Analysis complete
- Deal stage changed
- Task assigned/due
- Market alert triggered

**Integration Architecture:**
- Slack Bot API
- Webhook for real-time updates
- OAuth for workspace installation
- Channel and DM support

---

## 2.10 Phase 9: Sensitivity & Scenarios (Post-MVP)

**Goal:** Advanced modeling capabilities for sophisticated analysis.

**Features:**
- Multi-variable sensitivity tables
- Scenario modeling (Base, Upside, Downside)
- Monte Carlo simulation
- Stress testing against covenants
- Comparison across scenarios
- Probability-weighted returns

**Shieldstone Integration:**
- Section 7.6: Sensitivity analysis framework
- Section 12: Risk management & stress testing

---

## 2.11 Phase 10: Deal Sourcing & Alerts (Future)

**Goal:** Transform from reactive analysis to proactive opportunity identification.

**Features:**
- Market intelligence dashboard
- Off-market signal detection
  - Tax delinquency monitoring
  - Ownership pattern analysis
  - Loan maturity tracking
  - Permit activity alerts
- Owner identification and contact enrichment
- Saved searches with alerts
- Heat maps showing opportunity density

---

## 2.12 Phase 11: Asset Class - SFR Business Purpose Lending

**Goal:** Expand underwriting to single-family investment properties.

**Loan Types:**
- Fix & Flip
- Ground-Up Construction
- DSCR Rental (long-term hold)
- Bridge

**Key Differences from Multifamily:**
- Property-level (not portfolio) analysis
- Shorter hold periods (6-24 months for bridge)
- Different leverage calculations (LTV, LTC, LTARV)
- ARV-based underwriting
- Renovation budget line items
- Exit strategy focus (sell vs. refinance)

**Metrics:**
- Purchase Price / ARV
- LTV / LTC / LTARV
- Rehab Budget / Cost per SF
- Projected Profit
- ROI / Annualized Return
- DSCR (for rentals)

---

## 2.13 Phase 12: Asset Class Expansion (Future)

| Priority | Asset Class | Complexity | Key Differences |
|----------|-------------|------------|-----------------|
| 1 | Conventional Multifamily | Base | MVP (Shieldstone) |
| 2 | SFR BPL | Medium | Phase 11 |
| 3 | Student Housing | Medium | Bed-based, academic calendar |
| 4 | Mobile Home Parks | Medium | Lot rent, home sales |
| 5 | Affordable / LIHTC | High | Compliance, rent restrictions |
| 6 | Senior Housing | High | Acuity levels, care types |
| 7 | Industrial | Medium | NNN, warehouse metrics |
| 8 | Retail | Medium | NNN, tenant credit |
| 9 | Self-Storage | Medium | Unit mix, rate optimization |
| 10 | Office | Medium | Lease structures, TI |

---

# 3. Core Analytical Methodology

## 3.1 Shieldstone Technical Manual Integration

DREAM AI implements the **Shieldstone Technical Underwriting Manual V2.0** as its core analytical methodology. This ensures institutional-quality analysis with consistent, defensible outputs.

### Manual Structure

| Section | Topic | DREAM AI Phase |
|---------|-------|----------------|
| 1 | Foundational Frameworks & Return Hurdles | Phase 2 |
| 2 | Data Collection & Validation | Phase 1 |
| 3 | Revenue Underwriting | Phase 4 |
| 4 | Operating Expense Underwriting | Phase 4 |
| 5 | Capital Expenditure Planning | Phase 4 |
| 6 | Financing Structure & Debt Analysis | Phase 4 |
| 7 | Returns Analysis & Valuation | Phase 4 |
| 8 | Market Analysis Framework | Phase 3 |
| 9 | Due Diligence & Risk Mitigation | Phase 6 |
| 10 | Exit Strategy & Disposition | Phase 4 |
| 11 | Asset Management Integration | Future |
| 12 | Risk Management & Stress Testing | Phase 9 |
| 13 | Complete Underwriting Workflow | All Phases |
| 14 | Comprehensive Glossary | Reference |

### Key Methodologies Implemented

#### Return Hurdles (Section 1.1)

| Metric | Absolute Minimum | Notes |
|--------|------------------|-------|
| Levered IRR | 14.0% | Risk-adjusted by market tier |
| Equity Multiple (5yr) | 1.50x | |
| Net Investor IRR | 15.0% | After fees and promote |
| Stabilized CoC | 6-8% | Vintage-tiered |

**Market Tier Base Hurdles:**

| Tier | Definition | Base IRR Range |
|------|------------|----------------|
| Gateway | Top 10 MSAs | 14-16% |
| Secondary | 500K-2M population | 16-19% |
| Tertiary | <500K population | 18-22% |

**Risk Adjustments (cumulative):**

| Factor | Adjustment |
|--------|------------|
| Heavy renovation (pre-1980) | +250 bps |
| Heavy renovation (1980-1999) | +175 bps |
| Heavy renovation (2000+) | +150 bps |
| Occupancy 75-84% | +100 bps |
| Occupancy <75% | +150 bps |
| Property age 31-40 years | +100 bps |
| Property age 40+ years | +150 bps |
| Floating rate debt | +75-100 bps |
| Distressed market | +100-150 bps |

#### Merit-Based Screening (Section 2.1)

**Philosophy:** Economics determine viability, not arbitrary cutoffs.

**True Deal-Killers (Red Flags):**
- Known structural failure
- Active environmental contamination
- Severe flood zone (FEMA A/V) without mitigation
- Violent crime >2.5x national average
- Population decline >1%/year for 5+ years
- Single employer >40% of employment
- Unresolvable title/legal issues

**Risk Factors (Require Adjustment, Not Rejection):**
- Property age (any age acceptable with proper hurdle adjustment)
- Low occupancy (requires turnaround thesis and adjusted timeline)
- Property class C/D (requires appropriate expense assumptions)
- Deferred maintenance (requires proper capex budgeting)

#### Property Tax Analysis (Section 4.2)

**State-Specific Reassessment Ratios:**

| State | Reassessment Ratio | Notes |
|-------|-------------------|-------|
| Florida | 65-80% | County-specific; Live Local abatement available |
| Texas | 60-70% | Aggressive reassessment; protest common |
| Georgia | 40% | More favorable |
| Default | 65-70% | When state-specific data unavailable |

**Three-Scenario Modeling:**
1. Base Case: Expected reassessment ratio
2. Downside: 100% reassessment
3. Appeal Success: Reduced assessment

#### Exit Cap Triangulation (Section 7.2)

**Three-Method Approach:**

1. **Treasury Spread Method:** 10Y Treasury + historical spread
2. **Exit Comp Validation:** Recent sales in submarket
3. **Entry Cap + Strategy Spread:** Going-in cap + execution risk premium

**Rule:** Use HIGHEST (most conservative) of three methods. Never use exit cap lower than entry cap.

#### Refinancing Strategy (Section 6.5)

**90/90 Rule:** Agency refinancing requires 90 consecutive days at ≥90% economic occupancy.

**Target Refinance Window:** Months 24-36

**Agency Parameters:**
- 80% LTV maximum
- 1.25x DSCR minimum
- 30-year amortization

#### Deal Fees & Promote (Section 6.7)

**Standard Fee Structure:**

| Fee Type | Range | Basis |
|----------|-------|-------|
| Acquisition Fee | 0.5-1.0% | Purchase price |
| Asset Management Fee | 0.5-1.0% | EGI |
| Construction Management | 3-5% | Hard costs |
| Disposition Fee | 0.25-0.5% | Sale price |

**Standard Promote Structure:**
- 8% preferred return
- 70/30 (LP/GP) to 15% IRR
- 50/50 above 15% IRR

**Net Investor IRR = Gross IRR - Fee Drag - Promote Impact**

---

# 4. LLM Architecture & Cost Optimization

## 4.1 Cost Optimization Philosophy

DREAM AI must be profitable at accessible price points. Target pricing: **$99-199/month** for typical users (30-50 deals/month).

**Cost Constraint:** LLM API costs must be <$30-50/month per average user to maintain healthy margins.

**Cost Target by Analysis Type:**

| Analysis Type | Target Cost | Volume (50 deals) | Monthly Cost |
|---------------|-------------|-------------------|--------------|
| Document Extraction | $0.05-0.10 | 50 | $2.50-5.00 |
| Deal Screening | $0.02-0.05 | 50 | $1.00-2.50 |
| Market Research | $0.10-0.15 | 50 | $5.00-7.50 |
| BOE Analysis | $0.10-0.20 | 40 | $4.00-8.00 |
| Full UW Analysis | $0.75-1.50 | 8 | $6.00-12.00 |
| IC/Full Memo | $2.00-4.00 | 2 | $4.00-8.00 |
| **Total** | | | **$22.50-43.00** |

## 4.2 LLM Routing Strategy

### Current Baseline (Claude-Only)

| Task | Model | Cost/Task |
|------|-------|-----------|
| Document extraction | Claude Haiku | $0.05-0.10 |
| Data field extraction | Claude Haiku | $0.02-0.05 |
| Market research synthesis | Claude Sonnet | $0.10-0.15 |
| Investment analysis | Claude Sonnet | $0.30-0.50 |
| Report narrative | Claude Sonnet | $0.20-0.40 |
| Complex edge cases | Claude Opus | $1.00-2.00 |

### Future Optimization (Multi-Model)

Evaluate alternative models for cost reduction:

| Task | Candidate Models | Evaluation Criteria |
|------|------------------|---------------------|
| Document extraction | Gemini Flash, Llama 3.1, Qwen | Accuracy, speed, cost |
| Simple classification | Mixtral, Llama 3.1 | Accuracy, cost |
| Market research | Perplexity, Gemini | Web access, freshness |
| Structured data extraction | Gemini, Qwen | JSON reliability |
| Narrative generation | Claude Sonnet, GPT-4 | Quality, cost |

**Evaluation Framework:**

For each task, test candidate models against:
1. **Accuracy:** Does it produce correct outputs?
2. **Reliability:** Does it follow instructions consistently?
3. **Speed:** Latency acceptable for UX?
4. **Cost:** Cost per 1K tokens / per task?
5. **Shieldstone Compliance:** Does it follow methodology?

**Target Savings:** 40-60% reduction in LLM costs through optimal model routing.

## 4.3 Python-First Calculation Strategy

**Critical Architecture Decision:** ALL financial calculations are performed in Python, not by LLMs.

**Why:**
1. **Cost:** Python calculations are free; LLM calculations cost money
2. **Speed:** Python is instant (<100ms); LLM requires API call (1-5 seconds)
3. **Reliability:** Python is deterministic; LLM can hallucinate numbers
4. **Auditability:** Python code can be tested and verified

**LLM Role:** Generate assumptions and narratives only.

**Python Role:** All math, all formulas, all financial calculations.

```
USER CHANGES ASSUMPTION
        │
        ▼
┌─────────────────┐
│  Python Engine  │  ← Instant recalculation
│  (Shieldstone)  │  ← $0.00 cost
│                 │  ← Deterministic results
└─────────────────┘
        │
        ▼
   UPDATED RETURNS
   (IRR, EM, CoC, etc.)
```

## 4.4 Cost Monitoring & Optimization

**Per-User Tracking:**
- LLM costs by task type
- Total monthly cost per user
- Cost per deal analyzed
- Margin per subscription tier

**Alerts:**
- User exceeding expected cost profile
- Task type exceeding cost target
- Model performance degradation

**Optimization Triggers:**
- If task cost >150% of target, evaluate alternative models
- If user cost >$50/month, review usage patterns
- Quarterly model evaluation for all task types

---

# 5. Core Functional Requirements

## 5.1 Document Processing

### Inputs

| Document Type | Format | Extraction Goals |
|---------------|--------|------------------|
| Offering Memorandum | PDF | Property details, financials, photos |
| T-12 Operating Statement | Excel/PDF | Revenue, expenses by line item |
| Rent Roll | Excel/PDF | Unit mix, rents, lease terms, vacancy |
| Financial Model | Excel | Existing assumptions, projections |
| Property Photos | JPG/PNG | Visual documentation |

### Extraction Capabilities

**Property Details:**
- Address, city, state, zip
- Unit count, building count
- Year built, renovation history
- Net rentable SF, average unit size
- Property class, submarket

**Financial Metrics:**
- Asking price, price per unit, price per SF
- Current NOI, pro forma NOI
- Going-in cap rate
- Occupancy rate

**Rent Roll Data:**
- Unit mix (type, count, SF)
- Current rents by unit type
- Market rents
- Lease terms, expiration dates
- Vacancy detail

**Operating Statement:**
- Gross potential rent
- Vacancy and concessions
- Other income by category
- Operating expenses by line item
- NOI

### Quality Handling

- Confidence scores for each extracted field (0-100%)
- Flag uncertain values for user review
- Support for OCR on scanned documents
- Graceful handling of non-standard formats
- Manual override interface for corrections

## 5.2 Investment Criteria Engine

### Philosophy

Users configure their own investment criteria. DREAM AI doesn't impose a single thesis—it teaches users what metrics matter and evaluates deals against their specific requirements.

### Criteria Types

| Type | Behavior | Example |
|------|----------|---------|
| Hard Stop | Deal fails if not met | Minimum 50 units |
| Soft Preference | Affects scoring, doesn't disqualify | Prefer 2000+ vintage |
| Target Range | Ideal values with acceptable range | Target 18% IRR, minimum 14% |

### Default Criteria (User-Configurable)

```yaml
criteria:
  # Hard Stops
  property_type:
    type: hard_stop
    allowed: [multifamily]
  
  minimum_units:
    type: hard_stop
    value: 50
  
  # Target Ranges (from Shieldstone)
  target_irr:
    type: target_range
    minimum: 14.0  # Absolute floor
    target: 18.0
    excellent: 22.0
  
  equity_multiple:
    type: target_range
    minimum: 1.50
    target: 1.80
    excellent: 2.00
  
  stabilized_coc:
    type: target_range
    minimum: 6.0  # Vintage-adjusted
    target: 8.0
    excellent: 10.0
  
  # Soft Preferences
  market_tier:
    type: soft_preference
    preferred: [gateway, secondary]
    acceptable: [tertiary]
    weight: 0.15
  
  property_vintage:
    type: soft_preference
    preferred: [post_2000]
    acceptable: [1980_1999, pre_1980]
    weight: 0.10
```

### Learning Mode

For new users, DREAM AI suggests industry-standard criteria and explains the rationale for each metric. Users can accept defaults or customize.

## 5.3 Scoring Framework

### Default Categories (User-Adjustable Weights)

| Category | Suggested Weight | Components |
|----------|------------------|------------|
| Financial Performance | 25-30% | IRR, EM, CoC vs. hurdles |
| Business Plan Viability | 20-25% | Value-add thesis, execution feasibility |
| Market Quality | 20-25% | MSA tier, submarket fundamentals |
| Property Quality | 15-20% | Vintage, condition, class |
| Deal Sourcing | 5-10% | Off-market, relationship, timing |
| Risk Factors | 5-10% | Red flags, execution complexity |

### Business Plan Viability Assessment (NEW)

This critical category evaluates whether the proposed value-add strategy is realistic and achievable:

**Value-Add Thesis (40% of category)**
- Is the renovation scope appropriate for the property and market?
- Do projected rent premiums align with renovated comps in the submarket?
- Is the value creation strategy (interior upgrades, amenity additions, operational improvements) well-defined?

**Execution Feasibility (30% of category)**
- Is the renovation timeline realistic given scope and market conditions?
- Are construction costs in line with recent comparable projects?
- Is the stabilization timeline achievable based on market absorption?

**Sponsor Capability (20% of category)**
- Does the sponsor have experience with similar projects (vintage, size, market)?
- Has the sponsor successfully executed comparable renovations?
- Does the sponsor have relationships with contractors, property managers in the market?

**Risk-Adjusted Confidence (10% of category)**
- How many assumptions require "everything to go right"?
- What's the margin of safety if renovation costs overrun by 15-20%?
- What happens if stabilization takes 6 months longer than projected?

**Scoring Rubric:**

| Score | Business Plan Assessment |
|-------|-------------------------|
| 90-100 | Proven playbook in familiar market; conservative assumptions; strong sponsor track record |
| 75-89 | Solid thesis with reasonable assumptions; sponsor has relevant experience |
| 60-74 | Viable thesis but aggressive assumptions or limited sponsor experience |
| 40-59 | Questionable thesis; multiple aggressive assumptions; execution risk elevated |
| 0-39 | Unrealistic thesis; assumptions not supported by market data; high failure risk |

### Score Output

- Overall score (0-100)
- Category breakdown with individual scores
- Strengths (top 3-5 positive factors)
- Concerns (top 3-5 risk factors)
- Recommendation: **Strong Buy / Buy / Hold / Pass**
- Confidence level (based on data quality)

### Recommendation Logic

| Score Range | Recommendation | Action |
|-------------|----------------|--------|
| 80-100 | Strong Buy | Proceed aggressively |
| 65-79 | Buy | Proceed with standard DD |
| 50-64 | Hold | Request repricing or enhanced DD |
| 0-49 | Pass | Do not pursue |

---

# 6. Data Models

## 6.1 Core Entities

```
Organization
├── id: UUID
├── name: string
├── subscription_tier: enum
├── settings: JSON
├── created_at: timestamp
│
├── Users[]
│   ├── id: UUID
│   ├── email: string
│   ├── role: enum (admin, analyst, viewer)
│   └── preferences: JSON
│
├── InvestmentCriteria
│   ├── id: UUID
│   ├── criteria_config: JSON
│   └── is_default: boolean
│
├── Integrations[]
│   ├── type: enum (slack, drive, email)
│   ├── credentials: encrypted
│   └── settings: JSON
│
└── Subscription
    ├── tier: enum
    ├── status: enum
    └── billing_info: JSON
```

```
Deal
├── id: UUID
├── organization_id: FK
├── name: string
├── status: enum (new, screening, loi, dd, contract, closed, passed)
├── created_at: timestamp
├── updated_at: timestamp
│
├── Property
│   ├── address: string
│   ├── city, state, zip: string
│   ├── units: integer
│   ├── buildings: integer
│   ├── year_built: integer
│   ├── net_rentable_sf: integer
│   ├── property_class: enum
│   ├── submarket: string
│   └── coordinates: point
│
├── Documents[]
│   ├── id: UUID
│   ├── type: enum (om, t12, rent_roll, model, photo)
│   ├── file_url: string
│   ├── extracted_data: JSON
│   ├── confidence_scores: JSON
│   └── uploaded_at: timestamp
│
├── Analyses[]
│   ├── id: UUID
│   ├── type: enum (boe, full_uw, ic_memo, full_memo)
│   ├── assumptions: JSON
│   ├── results: JSON
│   ├── scores: JSON
│   ├── recommendation: enum
│   ├── generated_report_url: string
│   └── created_at: timestamp
│
├── Notes[]
│   ├── id: UUID
│   ├── user_id: FK
│   ├── content: text
│   └── created_at: timestamp
│
├── Tasks[]
│   ├── id: UUID
│   ├── title: string
│   ├── assigned_to: FK
│   ├── due_date: date
│   ├── status: enum
│   └── created_at: timestamp
│
└── ActivityLog[]
    ├── id: UUID
    ├── user_id: FK
    ├── action: string
    ├── details: JSON
    └── created_at: timestamp
```

```
Analysis
├── id: UUID
├── deal_id: FK
├── type: enum
├── version: integer
│
├── ExtractedData
│   ├── property_details: JSON
│   ├── financial_metrics: JSON
│   ├── rent_roll: JSON
│   ├── operating_statement: JSON
│   └── confidence_scores: JSON
│
├── MarketResearch
│   ├── msa_data: JSON
│   ├── submarket_data: JSON
│   ├── employment_data: JSON
│   ├── demographic_data: JSON
│   └── researched_at: timestamp
│
├── Assumptions
│   ├── acquisition: JSON
│   ├── financing: JSON
│   ├── revenue: JSON
│   ├── expenses: JSON
│   ├── capex: JSON
│   ├── exit: JSON
│   └── waterfall: JSON
│
├── ProForma
│   ├── annual_cashflows: JSON[]
│   ├── monthly_cashflows: JSON[]
│   ├── returns_summary: JSON
│   └── sensitivity_tables: JSON
│
├── Scores
│   ├── overall: float
│   ├── financial: float
│   ├── market: float
│   ├── property: float
│   ├── risk: float
│   └── breakdown: JSON
│
├── Recommendation
│   ├── rating: enum
│   ├── confidence: float
│   ├── strengths: string[]
│   ├── concerns: string[]
│   └── next_steps: string[]
│
├── GeneratedReports[]
│   ├── type: enum (boe, ic, full)
│   ├── format: enum (pdf, excel, slides)
│   ├── file_url: string
│   └── generated_at: timestamp
│
└── UserOverrides
    ├── field_path: string
    ├── original_value: any
    ├── override_value: any
    ├── reason: string
    └── overridden_at: timestamp
```

```
Market (Cached)
├── id: UUID
├── location_key: string (msa_submarket)
│
├── MSAData
│   ├── msa_name: string
│   ├── tier: enum
│   ├── population: integer
│   ├── population_growth: float
│   ├── employment: integer
│   ├── employment_growth: float
│   └── major_employers: JSON[]
│
├── SubmarketData
│   ├── name: string
│   ├── vacancy_rate: float
│   ├── rent_growth: float
│   ├── avg_rent: float
│   ├── construction_pipeline: integer
│   └── absorption: integer
│
├── ResearchResults
│   ├── raw_response: text
│   ├── structured_data: JSON
│   └── sources: string[]
│
└── Metadata
    ├── last_updated: timestamp
    ├── ttl_hours: integer
    └── refresh_count: integer
```

## 6.2 Pro Forma Data Structure

```typescript
interface ProFormaModel {
  // Metadata
  id: string;
  dealId: string;
  version: number;
  createdAt: Date;
  updatedAt: Date;
  
  // Assumptions (AI-generated, user-editable)
  assumptions: {
    // Property
    property: {
      units: number;
      avgUnitSF: number;
      yearBuilt: number;
    };
    
    // Acquisition
    acquisition: {
      purchasePrice: number;
      closingCosts: number;  // % of purchase
      acquisitionFee: number;  // % of purchase
    };
    
    // Financing
    financing: {
      senior: {
        loanAmount: number;
        ltv: number;
        interestRate: number;
        ioPeriodMonths: number;
        amortizationYears: number;
        termMonths: number;
      };
      refinance?: {
        enabled: boolean;
        month: number;
        ltv: number;
        rate: number;
        amortization: number;
      };
    };
    
    // Revenue
    revenue: {
      unitMix: Array<{
        type: string;
        count: number;
        sf: number;
        inPlaceRent: number;
        marketRent: number;
        proFormaRent: number;
      }>;
      otherIncome: {
        perUnit: number;
        items: Array<{ name: string; amount: number }>;
      };
      growth: {
        rentGrowth: number[];  // Year 1-10
        otherIncomeGrowth: number[];
      };
      vacancy: {
        physical: number[];
        concessions: number[];
        badDebt: number[];
      };
    };
    
    // Expenses
    expenses: {
      lineItems: Array<{
        category: string;
        year1Amount: number;
        perUnit: number;
        growthRate: number;
        notes: string;
      }>;
      managementFee: {
        type: 'percent' | 'perUnit';
        value: number;
      };
      propertyTax: {
        currentAssessed: number;
        reassessmentRatio: number;
        millageRate: number;
        appealScenario: boolean;
      };
    };
    
    // CapEx
    capex: {
      renovationBudget: {
        exterior: number;
        interior: number;
        contingency: number;
      };
      timeline: {
        startMonth: number;
        durationMonths: number;
      };
      reserves: number;  // per unit per year
    };
    
    // Exit
    exit: {
      holdPeriodMonths: number;
      exitCapRate: number;
      sellingCosts: number;  // % of sale
    };
    
    // Waterfall
    waterfall: {
      gpEquity: number;  // %
      lpEquity: number;  // %
      preferredReturn: number;  // %
      hurdles: Array<{
        irrThreshold: number;
        gpSplit: number;
        lpSplit: number;
      }>;
    };
  };
  
  // Calculated Results (Python-generated)
  results: {
    // Sources & Uses
    sourcesUses: {
      sources: {
        seniorDebt: number;
        gpEquity: number;
        lpEquity: number;
        totalSources: number;
      };
      uses: {
        purchasePrice: number;
        closingCosts: number;
        acquisitionFee: number;
        renovationBudget: number;
        reserves: number;
        totalUses: number;
      };
    };
    
    // Annual Cash Flows
    annualCashFlows: Array<{
      year: number;
      gpr: number;
      vacancyLoss: number;
      egi: number;
      otherIncome: number;
      totalRevenue: number;
      operatingExpenses: number;
      noi: number;
      debtService: number;
      cashFlowBeforeCapex: number;
      capex: number;
      cashFlowAfterCapex: number;
      dscr: number;
    }>;
    
    // Monthly Cash Flows (for detailed view)
    monthlyCashFlows: Array<{
      month: number;
      year: number;
      revenue: number;
      expenses: number;
      noi: number;
      debtService: number;
      netCashFlow: number;
    }>;
    
    // Returns Summary
    returns: {
      goingInCapRate: number;
      stabilizedCapRate: number;
      exitCapRate: number;
      
      // Project-Level
      projectIRR: number;
      projectEM: number;
      
      // GP Returns
      gpIRR: number;
      gpEM: number;
      gpProfit: number;
      
      // LP Returns
      lpIRR: number;
      lpEM: number;
      lpProfit: number;
      
      // Cash-on-Cash
      year1CoC: number;
      stabilizedCoC: number;
      avgCoC: number;
      
      // Other
      peakEquity: number;
      totalDistributions: number;
      salePrice: number;
      saleProceeds: number;
    };
    
    // Sensitivity Tables
    sensitivity: {
      exitCapVsRentGrowth: number[][];
      exitCapVsVacancy: number[][];
      rentGrowthVsExpenseGrowth: number[][];
    };
    
    // Waterfall Detail
    waterfallDetail: Array<{
      year: number;
      cashFlow: number;
      prefAccrual: number;
      prefPayment: number;
      returnOfCapital: number;
      promoteDistribution: number;
      gpDistribution: number;
      lpDistribution: number;
      cumulativeGP: number;
      cumulativeLP: number;
    }>;
  };
}
```

---

# 7. Technical Architecture

## 7.1 Stack Decisions

```
Frontend:
├── Framework: React + TypeScript
├── Styling: Tailwind CSS
├── Components: shadcn/ui
├── State: Zustand or React Query
├── Charts: Recharts or Tremor
└── Forms: React Hook Form + Zod

Backend:
├── Framework: Python + FastAPI
├── Database: PostgreSQL
├── ORM: SQLAlchemy or Prisma
├── Task Queue: Celery + Redis
├── Cache: Redis
└── File Storage: S3-compatible

AI/LLM:
├── Primary: Claude API (Haiku, Sonnet, Opus)
├── Research: Perplexity API
├── Evaluation: Gemini, Llama, Qwen, Kimi (for cost optimization)
└── Embeddings: OpenAI or local

Infrastructure:
├── Hosting: Vercel (frontend) + Railway/Render (backend)
├── Auth: Clerk or Auth0
├── Payments: Stripe
├── Email: SendGrid or Resend
├── Monitoring: Sentry + PostHog
└── CI/CD: GitHub Actions
```

## 7.2 API Design

### RESTful Endpoints

```
# Deals
POST   /api/deals                      Create deal
GET    /api/deals                      List deals (with filters)
GET    /api/deals/{id}                 Get deal details
PATCH  /api/deals/{id}                 Update deal
DELETE /api/deals/{id}                 Delete deal

# Documents
POST   /api/deals/{id}/documents       Upload document
GET    /api/deals/{id}/documents       List documents
POST   /api/documents/{id}/extract     Trigger extraction
GET    /api/documents/{id}/extraction  Get extraction results

# Analysis
POST   /api/deals/{id}/analyze         Trigger analysis
GET    /api/deals/{id}/analysis        Get latest analysis
GET    /api/deals/{id}/analyses        List all analyses
POST   /api/analyses/{id}/regenerate   Regenerate with new assumptions

# Pro Forma
GET    /api/deals/{id}/proforma        Get pro forma model
PATCH  /api/deals/{id}/proforma        Update assumptions
POST   /api/deals/{id}/proforma/calculate  Recalculate (Python)

# Reports
POST   /api/deals/{id}/reports         Generate report
GET    /api/deals/{id}/reports         List reports
GET    /api/reports/{id}/download      Download report

# Market Research
POST   /api/markets/research           Research a location
GET    /api/markets/{location}         Get cached market data

# Pipeline
GET    /api/pipeline                   Get pipeline view
PATCH  /api/deals/{id}/stage           Update deal stage

# Investment Criteria
GET    /api/criteria                   Get criteria config
PUT    /api/criteria                   Update criteria

# User & Org
GET    /api/me                         Get current user
PATCH  /api/me                         Update user settings
GET    /api/organization               Get org details
PATCH  /api/organization               Update org settings
```

### Async Processing

Long-running tasks use background jobs:

```python
# Task types
TASK_DOCUMENT_EXTRACTION = "document.extraction"
TASK_MARKET_RESEARCH = "market.research"
TASK_DEAL_ANALYSIS = "deal.analysis"
TASK_REPORT_GENERATION = "report.generation"

# Job status endpoint
GET /api/jobs/{job_id}  →  { status, progress, result }

# Webhook on completion
POST {callback_url}  →  { job_id, status, result }
```

## 7.3 Database Schema (PostgreSQL)

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'analyst',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Deals
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'new',
    property_data JSONB DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER,
    extracted_data JSONB,
    confidence_scores JSONB,
    extraction_status VARCHAR(50) DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Analyses
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    version INTEGER DEFAULT 1,
    assumptions JSONB NOT NULL,
    results JSONB,
    scores JSONB,
    recommendation VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    llm_cost_cents INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id),
    type VARCHAR(50) NOT NULL,
    format VARCHAR(50) NOT NULL,
    file_url TEXT,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Market Cache
CREATE TABLE market_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_key VARCHAR(255) UNIQUE NOT NULL,
    msa_data JSONB,
    submarket_data JSONB,
    research_data JSONB,
    last_updated TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Activity Log
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    deal_id UUID REFERENCES deals(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_deals_org ON deals(organization_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_documents_deal ON documents(deal_id);
CREATE INDEX idx_analyses_deal ON analyses(deal_id);
CREATE INDEX idx_market_cache_location ON market_cache(location_key);
CREATE INDEX idx_activity_log_org ON activity_log(organization_id);
```

---

# 8. User Experience Guidelines

## 8.1 Design Principles

1. **Speed First:** Optimize every interaction for analyst productivity
2. **Progressive Disclosure:** Simple by default, powerful when needed
3. **Teach as You Go:** Help users understand metrics and methodology
4. **Keyboard Friendly:** Power users can navigate without mouse
5. **Mobile Responsive:** Core functions work on tablet

## 8.2 Key Screens

### Dashboard
- Pipeline summary (deals by stage)
- Recent analyses
- Tasks due
- Quick actions (new deal, upload document)

### Deal Intake
- Drag-drop upload zone
- Processing status with progress
- Extracted data preview
- Validation alerts
- Manual correction interface

### Analysis View
- Full memo with collapsible sections
- Interactive charts
- Assumption editor
- Real-time recalculation
- Export options

### Pro Forma Editor
- Tabbed interface (Revenue, Expenses, CapEx, Financing, Returns)
- Inline editing with instant recalc
- Sensitivity sliders
- Scenario comparison
- Excel-like grid for detailed view

### Pipeline Board
- Kanban with drag-drop stages
- Quick filters (date, score, market)
- Bulk actions
- Deal cards with key metrics

### Deal Detail
- All information in one place
- Documents tab
- Analyses tab
- Notes and activity
- Tasks

### Settings
- Investment criteria configuration
- Integration setup (Slack, Drive)
- Team management
- Notification preferences

## 8.3 Onboarding Flow

1. **Create Account** - Email + password or OAuth
2. **Organization Setup** - Company name, team size
3. **Investment Criteria Wizard** - Guided setup with explanations
4. **Connect Integrations** - Slack, Google Drive (optional)
5. **Upload First Deal** - Guided walkthrough
6. **Review Analysis** - Explain scoring and methodology
7. **Customize** - Adjust criteria, preferences

---

# 9. Report Generation Framework

## 9.1 Report Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT                                                          │
│  ─────                                                          │
│  • Analysis results (assumptions, calculations)                 │
│  • Market research data                                         │
│  • Property photos                                              │
│  • User-selected report type (BOE, IC, Full)                   │
│                                                                  │
│  LLM PROCESSING                                                 │
│  ──────────────                                                 │
│  • Generate narrative sections                                  │
│  • Answer institutional investor questions                      │
│  • Identify strengths and concerns                             │
│  • Formulate recommendation                                     │
│                                                                  │
│  TEMPLATE ENGINE                                                │
│  ───────────────                                                │
│  • Populate structured sections                                 │
│  • Insert charts and tables                                     │
│  • Apply branding/styling                                       │
│  • Generate PDF/Excel/Slides                                    │
│                                                                  │
│  OUTPUT                                                         │
│  ──────                                                         │
│  • Professional PDF memo                                        │
│  • Excel workbook (optional)                                    │
│  • Google Slides deck (optional)                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 9.2 LLM Prompting Strategy

### BOE Memo Generation

```
System: You are an institutional real estate analyst generating a 
Back-of-Envelope investment memo. Be concise, data-driven, and 
direct. Follow the Shieldstone methodology.

Context:
- Property: {property_summary}
- Key Metrics: {metrics_table}
- Market Data: {market_summary}
- Scores: {score_breakdown}

Generate:
1. Executive Summary (2-3 sentences)
2. Key Strengths (3-4 bullets)
3. Key Concerns (3-4 bullets)
4. Recommendation with rationale (1 paragraph)

Format: Markdown with clear headers
Tone: Professional, analytical, objective
Length: ~500 words maximum
```

### IC Memo Generation

```
System: You are an institutional real estate analyst generating an 
Investment Committee memo. Address all standard IC questions 
comprehensively. Follow the Shieldstone methodology.

Context:
- Full Analysis: {analysis_json}
- Market Research: {market_research}
- Comparable Transactions: {comps}

Required Sections:
1. Executive Summary & Recommendation
2. Property Overview
3. Market Analysis
4. Financial Summary
5. Risk Factors & Mitigations
6. Value Creation Thesis

Address These Questions:
{institutional_questions_list}

Format: Markdown with clear headers and subheaders
Tone: Professional, thorough, balanced
Length: ~2,000-3,000 words
```

## 9.3 Export Formats

### HTML-First Report Generation (Primary)

**Design Philosophy:** Reports are generated as beautiful, responsive HTML first, then converted to other formats. This ensures:
- Consistent, design-forward presentation
- Easy iteration on templates
- Interactive elements in web view
- Clean PDF conversion

**HTML Template Architecture:**
```
reports/
├── templates/
│   ├── boe/
│   │   ├── boe-template.html
│   │   ├── boe-styles.css
│   │   └── components/
│   ├── ic-memo/
│   │   ├── ic-template.html
│   │   ├── ic-styles.css
│   │   └── components/
│   └── full-uw/
│       ├── full-uw-template.html
│       ├── full-uw-styles.css
│       └── components/
├── shared/
│   ├── charts/
│   ├── tables/
│   └── branding/
└── converters/
    ├── html-to-pdf.py
    └── html-to-image.py
```

**Design Requirements:**
- Modern, clean aesthetic (not generic "report" look)
- Consistent typography and color system
- Data visualizations that tell the story
- Mobile-responsive for web viewing
- Print-optimized CSS for PDF conversion

### PDF Generation (from HTML)
- Convert HTML templates using Playwright, Puppeteer, or WeasyPrint
- Preserve design fidelity
- Proper page breaks and headers/footers
- Embedded fonts for consistency

### Excel Export
- Working formulas (not just values)
- Multiple sheets (Summary, Pro Forma, Sensitivity, etc.)
- Named ranges for key inputs
- Conditional formatting
- Print-ready layout

### Presentation Deck Generation (AI-Powered)

**Approach:** Use AI to generate presentation decks from memo content.

**Candidate APIs/Tools:**
| Tool | Approach | Evaluation Status |
|------|----------|-------------------|
| **Gamma.ai** | AI-native presentation generation | Evaluate for API access |
| **Beautiful.ai** | Template-based with smart formatting | Evaluate for API |
| **Tome** | AI narrative + visual generation | Evaluate for API |
| **Custom Build** | React + reveal.js with AI content | Fallback option |

**Deck Structure (IC Presentation):**
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
```

**Implementation Priority:** Phase 6 MVP = HTML + PDF; Deck generation = Post-MVP enhancement

---

# 10. Data Strategy & Market Intelligence

## 10.1 Customer Data Aggregation Philosophy

**Strategic Vision:** As customers analyze deals through DREAM AI, we aggregate anonymized data to build proprietary market intelligence that benefits all users and becomes a competitive moat.

**Key Principle:** We are transparent with users about data usage. Their individual data remains private and secure (SOC2 compliant), but aggregated, anonymized insights are shared back with the community.

## 10.2 Anonymized Data Lake

### Data Collection (With User Consent)

| Data Type | What We Collect | How We Use It |
|-----------|-----------------|---------------|
| **Rent Comps** | In-place rents by unit type, vintage, submarket | Benchmark rent assumptions across markets |
| **Operating Expenses** | T-12 expense ratios, line-item breakdowns | Build expense benchmarks by market, vintage, class |
| **Cap Rate Observations** | Asking cap, actual transaction cap (if shared) | Track cap rate trends by market and property type |
| **Renovation Costs** | CapEx budgets, cost per unit, scope details | Benchmark renovation costs by market and scope |
| **Rent Premium Achieved** | Pre/post-renovation rents (if customers share) | Validate rent premium assumptions |
| **Time to Stabilization** | Actual vs. projected stabilization timelines | Improve timeline predictions |

### Anonymization Requirements

- All data stripped of property address, owner, and deal-specific identifiers
- Aggregated to submarket level minimum (never individual property)
- Minimum sample size of 5 properties before any benchmark is published
- No individual customer's data identifiable in any output
- Customers can opt-out of data sharing (but lose access to aggregated insights)

### Data Model

```prisma
model AnonymizedDealData {
  id                String   @id @default(cuid())
  submittedAt       DateTime @default(now())
  
  // Location (anonymized to submarket)
  msa               String
  submarket         String
  zipCodePrefix     String   // First 3 digits only
  
  // Property Characteristics
  propertyClass     PropertyClass
  vintage           Int      // Decade only (1970s, 1980s, etc.)
  unitCount         Int      // Rounded to nearest 25
  unitMix           Json     // Anonymized unit mix percentages
  
  // Financial Data (per unit)
  avgRentPerUnit    Decimal
  avgRentPSF        Decimal
  occupancy         Decimal
  
  // Operating Expenses (ratios only)
  expenseRatio      Decimal
  taxesPerUnit      Decimal
  insurancePerUnit  Decimal
  utilitiesPerUnit  Decimal
  payrollPerUnit    Decimal
  rmPerUnit         Decimal
  
  // Cap Rate Observation
  askingCap         Decimal?
  projectedCap      Decimal?
  
  // Renovation Data (if value-add)
  renovationType    RenovationType?
  budgetPerUnit     Decimal?
  projectedRentBump Decimal?  // Percentage
  
  // Source metadata
  sourceCustomerId  String   // Hashed, for duplicate detection only
  dataQualityScore  Int      // 1-100, based on completeness
}

model MarketBenchmark {
  id                String   @id @default(cuid())
  generatedAt       DateTime @default(now())
  validUntil        DateTime
  
  // Location
  msa               String
  submarket         String?  // Null = MSA-level benchmark
  
  // Benchmark Type
  benchmarkType     BenchmarkType  // RENT, EXPENSE, CAP_RATE, RENOVATION
  propertyClass     PropertyClass?
  vintage           String?        // "1970s", "1980s", etc.
  
  // Statistics
  sampleSize        Int
  median            Decimal
  percentile25      Decimal
  percentile75      Decimal
  mean              Decimal
  stdDev            Decimal
  
  // Trend
  yoyChange         Decimal?
  trend             Trend?   // UP, DOWN, STABLE
  
  @@unique([msa, submarket, benchmarkType, propertyClass, vintage])
}
```

## 10.3 Market Intelligence Features (Powered by Aggregated Data)

### For All Users

| Feature | Description |
|---------|-------------|
| **Rent Benchmarks** | "Class B 1980s units in [Submarket] typically rent for $X-Y/unit" |
| **Expense Benchmarks** | "Operating expenses for similar properties average $X/unit" |
| **Cap Rate Trends** | "Cap rates in [MSA] have moved from X% to Y% over past 12 months" |
| **Renovation Cost Benchmarks** | "Light renovations in [Market] typically cost $X-Y/unit" |

### Premium Features (Paid Tier)

| Feature | Description |
|---------|-------------|
| **Detailed Submarket Analysis** | Granular benchmarks at submarket level |
| **Trend Forecasting** | AI-powered predictions based on data trends |
| **Comp Set Builder** | Find similar properties in database for comparison |
| **Custom Benchmarks** | Build benchmarks for specific property profiles |

## 10.4 Privacy & Consent Framework

### User Consent Flow

1. **Onboarding:** Clear explanation of data sharing during signup
2. **Opt-In/Opt-Out:** Toggle in settings to control data sharing
3. **Transparency Dashboard:** Show users what data has been contributed
4. **Value Exchange:** Users who share data get enhanced market intelligence

### Legal Requirements

- Privacy policy clearly explains data aggregation
- Terms of service include data usage rights
- CCPA/GDPR compliant data handling
- SOC2 Type II certification for security

### Data Retention

| Data Type | Retention Period | Notes |
|-----------|------------------|-------|
| Raw deal data | 7 years | Customer's own data |
| Anonymized contributions | Indefinite | Aggregated insights |
| Benchmarks | Updated monthly | Rolling calculations |

---

# 11. Integration Architecture

## 11.1 Baked-In Integrations (Core App)

| Integration | Purpose | Implementation |
|-------------|---------|----------------|
| Document Upload | Ingest OMs, T-12s, rent rolls | Direct upload + Google Drive picker |
| LLM APIs | Analysis, extraction, generation | Claude, Perplexity, (future: others) |
| Market Data | Research and validation | Perplexity, Census, BLS, Walk Score |
| PDF Generation | Report output | HTML templates → Playwright/Puppeteer |
| Email | Notifications, report delivery | SendGrid/Resend |
| Slack | Notifications, AI agent | Slack Bot API |

## 11.2 External Automations (n8n Server - Near Zero Cost)

| Automation | Purpose | Tool | Cost |
|------------|---------|------|------|
| Market Monitoring | Daily market checks, alerts | n8n + Cron | ~$0/month |
| CRM Sync | Push deals to HubSpot/GHL | n8n + Webhooks | ~$0/month |
| Document Organization | Auto-file to Google Drive | n8n + Drive API | ~$0/month |
| Reporting | Weekly pipeline summaries | n8n + Email | ~$0/month |

**Note:** External automations run on dedicated n8n server, making them essentially free (server cost only, no per-automation fees).

## 11.3 Slack Integration (Phase 8)

### Bot Commands

```
@DREAMAI analyze [address]
→ Creates new deal, triggers BOE analysis
→ Returns summary in thread

@DREAMAI status [deal name]
→ Returns current stage, score, next steps

@DREAMAI memo [deal name] [type]
→ Generates and shares memo (BOE/IC/Full)

@DREAMAI market [location]
→ Returns market snapshot

@DREAMAI pipeline
→ Returns pipeline summary with counts by stage

@DREAMAI help
→ Lists available commands
```

### Notifications

| Event | Channel | Message |
|-------|---------|---------|
| Analysis Complete | Deal channel or DM | "Analysis complete for [Deal]. Score: 78/100 (Buy). [View Details]" |
| Stage Changed | Deal channel | "[User] moved [Deal] to Due Diligence" |
| Task Assigned | DM to assignee | "New task: [Task] for [Deal]. Due: [Date]" |
| Task Due | DM to assignee | "Reminder: [Task] for [Deal] is due today" |

---

# 12. Success Metrics

## 12.1 Product Metrics (Aggressive Targets)

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| Time to First Analysis | <5 minutes | <3 minutes | Onboarding funnel |
| BOE Analysis Time | <2 minutes | <1 minute | Task completion time |
| Full UW Analysis Time | <7 minutes | <5 minutes | Task completion time |
| Data Extraction Accuracy | >90% | >95% | User corrections tracked |
| Market Research Coverage | >85% | >90% | Field completion rate |
| User Activation | >70% | >80% | Onboarding completion |
| Weekly Active Users | >75% | >85% | WAU/MAU ratio |

**Note:** These aggressive targets require optimized LLM routing, parallel processing, and efficient Python calculations. Achieving stretch goals will require evaluation of faster/cheaper models (Gemini Flash, Llama, Qwen) for appropriate tasks.

## 12.2 Financial Metrics (Cost-Optimized)

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| LLM Cost per BOE | <$0.05 | <$0.03 | API cost tracking |
| LLM Cost per Full UW | <$0.50 | <$0.30 | API cost tracking |
| LLM Cost per IC/Full Memo | <$1.50 | <$1.00 | API cost tracking |
| LLM Cost per User/Month | <$15 | <$10 | Aggregate tracking (50 deals) |
| Gross Margin | >75% | >80% | Revenue - COGS |
| Customer Acquisition Cost | <$300 | <$200 | Marketing spend / new customers |
| Monthly Churn | <4% | <3% | Cancellations / active |
| Net Revenue Retention | >115% | >125% | Expansion - churn |

**Cost Optimization Strategy:**
1. **Python-first calculations:** All math in Python ($0.00)
2. **Model routing:** Use cheapest model that meets quality threshold per task
3. **Caching:** Cache market research, avoid redundant LLM calls
4. **Batch processing:** Combine related prompts where possible
5. **Evaluate alternatives:** Gemini Flash, Llama 3.1, Qwen, Mixtral for routine tasks

**Monthly Cost Breakdown Target (50 deals/user):**

| Task | Cost/Task | Volume | Monthly Cost |
|------|-----------|--------|--------------|
| Document Extraction | $0.03 | 50 | $1.50 |
| Deal Screening | $0.02 | 50 | $1.00 |
| Market Research | $0.05 | 50 | $2.50 |
| BOE Analysis | $0.05 | 40 | $2.00 |
| Full UW Analysis | $0.30 | 8 | $2.40 |
| IC/Full Memo | $1.00 | 2 | $2.00 |
| **Total** | | | **$11.40** |

## 12.3 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Shieldstone Compliance | 100% | Methodology audit |
| Calculation Accuracy | 99.99% | Test suite |
| Report Quality Score | >4.5/5 | User ratings |
| Support Ticket Volume | <3% of users/month | Ticket count |
| NPS | >60 | Quarterly survey |

---

# 13. Development Notes for AI Coding Assistant

## 13.1 Context for Claude Code / Cursor

This PRD describes DREAM AI, an AI-powered real estate underwriting platform. The analytical methodology is defined by the Shieldstone Technical Manual V2.0.

### Architecture Preferences

- Prefer simple, readable code over clever abstractions
- Use established patterns (don't reinvent auth, billing, etc.)
- Prioritize shipping over perfection
- Build for iteration (easy to change later)
- **All financial calculations in Python, not LLM**

### Phase 1-4 Priority Order (MVP)

1. Auth + basic user/org model
2. Deal CRUD + document upload
3. Document extraction (LLM)
4. Investment criteria engine
5. Deal screening (Shieldstone Section 2)
6. Market research integration
7. Pro forma engine (Shieldstone Sections 3-7)
8. Report generation (BOE first, then IC/Full)
9. Pipeline board UI
10. Basic integrations (email, export)

### Code Quality Standards

- Type hints throughout Python code
- TypeScript strict mode for frontend
- Tests for critical paths (calculations, extraction)
- Clear error handling and logging
- API documentation (OpenAPI)

## 13.2 Key Technical Decisions

### Already Decided

- PostgreSQL for database (not NoSQL)
- FastAPI for backend (not Django/Flask)
- React for frontend (not Vue/Svelte)
- Clerk/Auth0 for auth (not custom)
- S3-compatible storage (not local filesystem)
- Python for all financial calculations (not LLM)

### Open for Discussion

- Specific PDF generation library (WeasyPrint vs ReportLab)
- Task queue (Celery vs Dramatiq vs ARQ)
- Caching strategy (Redis vs in-memory)
- Hosting platform (Vercel + Railway vs alternatives)
- LLM model selection for cost optimization

## 13.3 Shieldstone Implementation Notes

The Shieldstone Technical Manual V2.0 contains Python implementations for key calculations. These should be used as reference:

- `ReturnHurdleCalculator` (Section 1.1)
- `DealScreener` (Section 2.1)
- Revenue underwriting formulas (Section 3)
- Property tax calculations (Section 4.2)
- Exit cap triangulation (Section 7.2)
- Master workflow orchestrator (Section 13)

**Important:** The manual's Python code is reference implementation. Adapt as needed for the production codebase while maintaining methodological accuracy.

## 13.4 File Organization

```
dream-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   └── styles/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── extraction/
│   │   │   ├── analysis/
│   │   │   ├── proforma/
│   │   │   ├── reports/
│   │   │   └── market/
│   │   ├── shieldstone/
│   │   │   ├── hurdles.py
│   │   │   ├── screening.py
│   │   │   ├── revenue.py
│   │   │   ├── expenses.py
│   │   │   ├── capex.py
│   │   │   ├── financing.py
│   │   │   ├── returns.py
│   │   │   └── workflow.py
│   │   └── utils/
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
│
├── docs/
│   ├── PRDs/
│   ├── shieldstone/
│   └── api/
│
└── infrastructure/
    ├── docker/
    └── terraform/
```

---

# 14. Asset Class Reference

## 14.1 Conventional Multifamily (MVP)

**Status:** ✅ MVP Launch Asset Class

**Key Metrics:**
- Units, unit mix, avg SF
- Rent per unit, rent per SF
- Occupancy, vacancy loss
- NOI, cap rate, price per unit
- IRR, equity multiple, cash-on-cash
- DSCR, LTV

**Shieldstone Sections:** All (1-14)

## 14.2 SFR Business Purpose Lending (Phase 11 - Priority #1 Expansion)

**Status:** 🔜 First expansion after MVP

**Loan Types:**
- Fix & Flip
- Ground-Up Construction
- DSCR Rental
- Bridge

**Key Metrics:**
- Purchase Price, ARV
- LTV, LTC, LTARV
- Rehab Budget, Cost per SF
- Projected Profit, ROI
- Annualized Return
- DSCR (rentals)

**Key Differences:**
- Property-level analysis
- Shorter hold periods
- ARV-based underwriting
- Exit strategy focus

## 14.3 Affordable Housing / LIHTC (Priority #2 Expansion)

**Status:** 🔜 Second expansion (400+ page manual already developed)

**Key Metrics:**
- AMI levels (30%, 50%, 60%, 80%)
- Rent restrictions by unit
- Compliance period remaining
- Tax credit value (4% vs 9%)
- Year 15 exit considerations
- Qualified Contract process
- Regulatory agreement terms

**Key Differences:**
- Rent restrictions by AMI tier
- LIHTC compliance requirements
- Tax credit valuation and syndication
- Extended hold periods (15+ years)
- Regulatory overlay complexity
- Qualified Allocation Plan (QAP) considerations

**Implementation Advantage:** Existing 400+ page LIHTC underwriting manual provides comprehensive methodology for rapid implementation.

## 14.4 Student Housing (Future)

**Key Metrics:**
- Beds (not units)
- Rent per bed
- Pre-leasing velocity
- Distance to campus
- University enrollment

**Key Differences:**
- Bed-based underwriting
- Academic calendar lease-up
- University dependency

## 14.5 Mobile Home Parks (Future)

**Key Metrics:**
- Lot count (pad sites)
- Lot rent
- Park-owned vs tenant-owned homes
- Utility billing (RUBS, sub-metering)
- Home sales income
- Infill potential

**Key Differences:**
- Lot rent focus
- Home sales as separate income
- Utility pass-through complexity

## 14.6 Senior Housing (Future)

**Key Metrics:**
- Unit/bed count by care level
- IL, AL, MC mix
- Monthly service fees + care charges
- Acuity levels and staffing ratios
- Occupancy by care type
- Length of stay

**Key Differences:**
- Care level segmentation
- Operating complexity
- Regulatory requirements
- Specialized staffing

## 14.7 Asset Class Expansion Roadmap

| Priority | Asset Class | Timeline | Manual Status | Complexity |
|----------|-------------|----------|---------------|------------|
| MVP | Conventional Multifamily | Launch | Shieldstone v2 Complete | High |
| #1 | SFR BPL | Phase 11 | Needs Development | Medium |
| #2 | Affordable/LIHTC | Post-Phase 11 | 400+ Page Manual Ready | Very High |
| #3 | Student Housing | Future | Needs Development | Medium |
| #4 | Mobile Home Parks | Future | Needs Development | Medium |
| #5 | Senior Housing | Future | Needs Development | Very High |

---

# 15. Shieldstone Python Library

## 15.1 Library Overview

A standalone Python package implementing all Shieldstone Technical Manual calculations. This library provides:

- **Deterministic calculations** (no LLM costs, 100% accurate)
- **Independently testable** with comprehensive test coverage
- **Reusable** across the app and potentially as a separate product
- **Version-controlled** methodology updates

## 15.2 Package Structure

```
shieldstone/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── models.py              # Pydantic models for all data structures
│   ├── enums.py               # MarketTier, PropertyClass, etc.
│   └── exceptions.py          # Custom exceptions
├── screening/
│   ├── __init__.py
│   ├── hurdles.py             # ReturnHurdleCalculator
│   ├── red_flags.py           # RedFlagChecker
│   └── deal_screener.py       # DealScreener orchestration
├── revenue/
│   ├── __init__.py
│   ├── rent_analysis.py       # Rent comp analysis, loss-to-lease
│   ├── growth_projections.py  # Rent growth, occupancy projections
│   └── other_income.py        # Fee income, ancillary revenue
├── expenses/
│   ├── __init__.py
│   ├── opex_calculator.py     # Operating expense modeling
│   ├── property_tax.py        # Tax reassessment calculations
│   └── insurance.py           # Insurance cost modeling
├── capex/
│   ├── __init__.py
│   ├── renovation_budget.py   # Interior/exterior CapEx
│   ├── reserves.py            # Replacement reserves
│   └── timing.py              # Renovation phasing
├── financing/
│   ├── __init__.py
│   ├── debt_modeling.py       # Loan sizing, debt service
│   ├── refinance.py           # Refi analysis
│   └── ground_lease.py        # Ground lease calculations
├── returns/
│   ├── __init__.py
│   ├── irr_calculator.py      # IRR, XIRR calculations
│   ├── waterfall.py           # Promote/waterfall engine
│   ├── exit_cap.py            # Exit cap triangulation
│   └── sensitivity.py         # Sensitivity analysis
├── workflow/
│   ├── __init__.py
│   ├── boe_analyzer.py        # BOE-level analysis
│   ├── full_uw_analyzer.py    # Full underwriting workflow
│   └── orchestrator.py        # Master workflow orchestration
└── tests/
    ├── __init__.py
    ├── test_hurdles.py
    ├── test_screening.py
    ├── test_revenue.py
    ├── test_expenses.py
    ├── test_capex.py
    ├── test_financing.py
    ├── test_returns.py
    ├── test_workflow.py
    └── fixtures/
        ├── sample_deals.json
        └── expected_outputs.json
```

## 15.3 Key Classes

### ReturnHurdleCalculator

```python
from shieldstone.screening import ReturnHurdleCalculator
from shieldstone.core.enums import MarketTier, RenovationType

calculator = ReturnHurdleCalculator()

hurdle = calculator.calculate(
    market_tier=MarketTier.SECONDARY,
    renovation_type=RenovationType.VALUE_ADD_MODERATE,
    current_occupancy=0.85,
    property_age=45,
    is_floating_rate=True,
    market_cycle_position="late"
)

print(hurdle.required_irr)           # 0.195 (19.5%)
print(hurdle.required_equity_multiple)  # 1.75
print(hurdle.breakdown)              # Full breakdown of premiums
```

### DealScreener

```python
from shieldstone.screening import DealScreener

screener = DealScreener()

result = screener.screen(
    property_data=property,
    market_data=market,
    financial_data=financials,
    sponsor_criteria=criteria
)

print(result.recommendation)  # "PURSUE", "PASS", "NEEDS_REVIEW"
print(result.score)           # 78
print(result.red_flags)       # List of identified issues
print(result.key_metrics)     # IRR, EM, CoC, etc.
```

### ProFormaEngine

```python
from shieldstone.returns import ProFormaEngine

engine = ProFormaEngine()

proforma = engine.build(
    property=property,
    assumptions=assumptions,
    financing=financing,
    hold_period=5
)

print(proforma.annual_cash_flows)
print(proforma.irr)
print(proforma.equity_multiple)
print(proforma.exit_proceeds)
```

## 15.4 Integration with DREAM AI App

```python
# In the main app
from shieldstone import DealScreener, ProFormaEngine, ReturnHurdleCalculator

class AnalysisService:
    def __init__(self):
        self.screener = DealScreener()
        self.proforma_engine = ProFormaEngine()
        self.hurdle_calculator = ReturnHurdleCalculator()
    
    async def analyze_deal(self, deal: Deal) -> AnalysisResult:
        # Step 1: Calculate hurdles (Python - $0)
        hurdles = self.hurdle_calculator.calculate(
            market_tier=deal.market_tier,
            # ... other params
        )
        
        # Step 2: Screen deal (Python - $0)
        screening = self.screener.screen(deal)
        
        # Step 3: Build pro forma (Python - $0)
        proforma = self.proforma_engine.build(deal, hurdles)
        
        # Step 4: LLM for narrative only (Sonnet - ~$0.10)
        narrative = await self.llm.generate_narrative(
            screening=screening,
            proforma=proforma
        )
        
        return AnalysisResult(
            screening=screening,
            proforma=proforma,
            narrative=narrative
        )
```

## 15.5 Testing Requirements

- **100% test coverage** on all calculation functions
- **Property-based testing** for edge cases (Hypothesis)
- **Regression tests** against known-good Excel outputs
- **Integration tests** with sample deals from Shieldstone Manual
- **Performance benchmarks** (all calculations <100ms)

## 15.6 Development Priority

| Priority | Module | Reason |
|----------|--------|--------|
| 1 | `screening/hurdles.py` | Core to deal scoring |
| 2 | `returns/irr_calculator.py` | Most-used calculation |
| 3 | `returns/waterfall.py` | Complex, high-value |
| 4 | `revenue/*` | Revenue underwriting |
| 5 | `expenses/*` | Expense underwriting |
| 6 | `capex/*` | CapEx modeling |
| 7 | `financing/*` | Debt modeling |
| 8 | `workflow/*` | Orchestration |

---

# 16. Glossary

**AMI:** Area Median Income - benchmark for affordable housing rent limits

**ARV:** After Repair Value - estimated property value post-renovation

**BOE:** Back of Envelope - quick preliminary analysis

**BPS:** Basis Points - 1/100th of a percent (100 bps = 1%)

**CapEx:** Capital Expenditure - major property improvements

**CoC:** Cash-on-Cash Return - annual cash flow / equity invested

**DCF:** Discounted Cash Flow - present value modeling methodology

**DSCR:** Debt Service Coverage Ratio - NOI / debt service

**EGI:** Effective Gross Income - GPR - vacancy + other income

**EM:** Equity Multiple - total distributions / equity invested

**GPR:** Gross Potential Rent - 100% occupied at market rents

**IO:** Interest Only - loan period with no principal payments

**IRR:** Internal Rate of Return - annualized return accounting for timing

**LIHTC:** Low Income Housing Tax Credit - affordable housing program

**LTC:** Loan-to-Cost - loan amount / total project cost

**LTARV:** Loan-to-After-Repair-Value - loan amount / ARV

**LTV:** Loan-to-Value - loan amount / property value

**MSA:** Metropolitan Statistical Area - geographic market definition

**NOI:** Net Operating Income - revenue - operating expenses

**OM:** Offering Memorandum - marketing document for property sale

**PFS:** Personal Financial Statement - borrower's financial summary

**Pro Forma:** Projected financial performance model

**RUBS:** Ratio Utility Billing System - utility cost allocation method

**T-12:** Trailing 12 Months - historical operating statement

**UW:** Underwriting - financial analysis and risk assessment

**Value-Add:** Investment strategy involving property improvements

**Waterfall:** Distribution structure defining investor payment priority

**YOC:** Yield on Cost - stabilized NOI / total cost basis

---

# Appendix A: Open Questions

1. **Pricing Model:** Per-seat, per-deal, or hybrid?
2. **Free Tier:** Offer limited free access to drive adoption?
3. **Data Partnerships:** Worth pursuing CoStar/Yardi integrations early?
4. **LLM Cost Optimization:** Which alternative models to evaluate first?
5. **White-Label:** Offer white-label version for brokerages?

# Appendix B: Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Shieldstone Manual V2.0 | ✅ Complete | 7,800+ lines, production ready |
| LLM API Access | ✅ Available | Claude, Perplexity |
| Alternative LLM Evaluation | ⏳ Pending | Gemini, Llama, Qwen, Kimi |
| Excel Template (House Model) | ⏳ Pending | Based on institutional format |
| Report Templates | ⏳ Pending | BOE, IC, Full UW designs |

---

# Appendix C: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | Nov 2025 | Original DreamVision PRD |
| 4.0 | Dec 2025 | Renamed to DREAM AI; integrated Shieldstone methodology; added LLM cost optimization; expanded phases; added institutional investor questions; added SFR BPL; replaced outreach with Slack agent; comprehensive data models |

---

*End of DREAM AI Master PRD v4.0*

