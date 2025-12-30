# DREAM AI User Flows

> Comprehensive documentation of core user journeys through the platform

---

## Table of Contents

1. [New User Onboarding](#1-new-user-onboarding)
2. [Quick Deal Screening (BOE)](#2-quick-deal-screening-boe)
3. [Full Deal Underwriting](#3-full-deal-underwriting)
4. [Investment Committee Presentation](#4-investment-committee-presentation)
5. [Pipeline Management](#5-pipeline-management)
6. [Pro Forma Sensitivity Analysis](#6-pro-forma-sensitivity-analysis)
7. [Team Collaboration](#7-team-collaboration)
8. [Custom Investment Criteria Setup](#8-custom-investment-criteria-setup)

---

## 1. New User Onboarding

**Goal:** Get a new user from signup to their first completed analysis in under 10 minutes.

### Flow Overview

```
Sign Up → Organization Setup → Investment Criteria Wizard → 
Upload First Deal → Review Analysis → Customize Settings
```

### Detailed Steps

#### 1.1 Sign Up
- **Entry Point:** Landing page CTA
- **Input:** Email, password (or OAuth with Google/Microsoft)
- **Duration:** 30 seconds

**Screen Elements:**
- Email/password fields
- "Sign up with Google" button
- Terms of Service checkbox
- "Already have an account?" link

#### 1.2 Organization Setup
- **Input:** Company name, team size, industry role
- **Duration:** 30 seconds

**Questions:**
- "What's your company name?"
- "How large is your team?" (Solo, 2-10, 11-50, 51+)
- "What's your primary role?" (Investment Manager, Analyst, Sponsor, Broker)

#### 1.3 Investment Criteria Wizard
- **Goal:** Configure initial screening criteria
- **Approach:** Guided setup with explanations
- **Duration:** 3-4 minutes

**Step 1: Property Type & Size**
```
┌─────────────────────────────────────────────────────────────────┐
│  What type of properties do you evaluate?                       │
│                                                                  │
│  [✓] Conventional Multifamily                                   │
│  [ ] Student Housing (Coming Soon)                              │
│  [ ] Senior Housing (Coming Soon)                               │
│                                                                  │
│  What's your minimum property size?                             │
│  [50] units (recommended: 50+ for institutional liquidity)      │
│                                                                  │
│  [Continue →]                                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Step 2: Return Targets**
```
┌─────────────────────────────────────────────────────────────────┐
│  What are your target returns?                                  │
│                                                                  │
│  Levered IRR:                                                   │
│  ├─ Minimum:    [14.0]% (Shieldstone absolute floor)           │
│  ├─ Target:     [18.0]%                                         │
│  └─ Excellent:  [22.0]%                                         │
│                                                                  │
│  Equity Multiple (5-year):                                      │
│  ├─ Minimum:    [1.50]x                                         │
│  ├─ Target:     [1.80]x                                         │
│  └─ Excellent:  [2.00]x                                         │
│                                                                  │
│  💡 These are based on Shieldstone methodology. We'll          │
│     automatically adjust these based on property risk.          │
│                                                                  │
│  [← Back]  [Continue →]                                         │
└─────────────────────────────────────────────────────────────────┘
```

**Step 3: Market Preferences**
```
┌─────────────────────────────────────────────────────────────────┐
│  Which markets do you prefer?                                   │
│                                                                  │
│  [✓] Gateway (Top 6: NYC, LA, Chicago, SF, Boston, DC)        │
│  [✓] Secondary (Major metros: 500K-2M population)              │
│  [ ] Tertiary (Smaller markets: <500K population)              │
│                                                                  │
│  ⚠️  We don't automatically disqualify any market — we adjust  │
│     return hurdles based on liquidity risk instead.             │
│                                                                  │
│  [← Back]  [Continue →]                                         │
└─────────────────────────────────────────────────────────────────┘
```

**Step 4: Review & Confirm**
```
┌─────────────────────────────────────────────────────────────────┐
│  Review Your Investment Criteria                                │
│                                                                  │
│  Property Type:     Conventional Multifamily                    │
│  Minimum Size:      50 units                                    │
│  Target IRR:        18.0% (min 14.0%, excellent 22.0%)         │
│  Target EM:         1.80x (min 1.50x, excellent 2.00x)         │
│  Market Preference: Gateway, Secondary                          │
│                                                                  │
│  You can change these anytime in Settings.                      │
│                                                                  │
│  [← Back]  [Start Analyzing Deals →]                           │
└─────────────────────────────────────────────────────────────────┘
```

#### 1.4 Upload First Deal (Guided)
- **Goal:** Walk user through document upload
- **Duration:** 2-3 minutes

**Screen:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Let's Analyze Your First Deal                                  │
│                                                                  │
│  Step 1: Upload Documents                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │     📄  Drag & drop files here                              ││
│  │                                                              ││
│  │     or click to browse                                       ││
│  │                                                              ││
│  │     Recommended:                                             ││
│  │     • Offering Memorandum (PDF)                             ││
│  │     • T-12 Operating Statement (Excel/PDF)                  ││
│  │     • Rent Roll (Excel/PDF)                                 ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  [Skip for now]  [Analyze Sample Deal]                         │
└─────────────────────────────────────────────────────────────────┘
```

**Alternative: Sample Deal**
If user clicks "Analyze Sample Deal":
- Pre-loaded Nashville multifamily deal
- All documents already processed
- Instant analysis results
- Shows full platform capabilities

#### 1.5 Review Analysis
- **Goal:** Show user what DREAM AI produces
- **Duration:** 3-5 minutes

**Analysis Complete Screen:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Analysis Complete ✓                                            │
│                                                                  │
│  Oakwood Apartments                                             │
│  Nashville, TN • 168 Units • Class B • Built 1985              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Investment Score: 78/100                                 │  │
│  │  Recommendation: BUY                                       │  │
│  │  Confidence: High                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  KEY METRICS                                                     │
│  ├─ Levered IRR:         19.2% ✓ (exceeds 18.0% target)       │
│  ├─ Equity Multiple:     1.89x ✓ (exceeds 1.80x target)       │
│  ├─ Cash-on-Cash (Stab): 8.4%                                  │
│  └─ Going-In Cap:        5.8%                                   │
│                                                                  │
│  STRENGTHS (5)                                                   │
│  • Strong secondary market with 3.2% job growth                │
│  • Below-market rents offer $175/unit upside                   │
│  • Recent $8M exterior renovation complete                     │
│  • 95% occupancy with stable operating history                 │
│  • Clear value-add thesis with proven submarket comps          │
│                                                                  │
│  CONCERNS (3)                                                    │
│  • Property age (39 years) requires ongoing CapEx              │
│  • Rising property taxes (reassessment likely)                 │
│  • New supply: 2,500 units under construction in submarket     │
│                                                                  │
│  [View Full Report]  [Adjust Assumptions]  [Export to Excel]  │
└─────────────────────────────────────────────────────────────────┘
```

**Tooltip/Help Text:**
- Investment Score explanation
- What each metric means
- Why these strengths/concerns matter

#### 1.6 Customize Settings (Optional)
- **Goal:** Show where to adjust preferences
- **Duration:** 1-2 minutes

**Tour Points:**
- Investment criteria page
- Notification preferences
- Team management
- Integration setup (Slack, Google Drive)

### Success Metrics
- ✅ 70%+ users complete onboarding
- ✅ 80%+ users complete first analysis
- ✅ Average time to first analysis: <10 minutes

---

## 2. Quick Deal Screening (BOE)

**Use Case:** Broker sends a teaser, you need a quick pass/fail decision in 2 minutes.

### Flow Overview

```
Receive Teaser → Upload to DREAM → BOE Analysis (2 min) → 
Pass/Proceed Decision → Send Response
```

### Detailed Steps

#### 2.1 Entry Point
**Trigger:** Email from broker with teaser/OM attached

**Action:** Forward email to `analyze@dream.ai` or upload via web

#### 2.2 Document Upload
```
┌─────────────────────────────────────────────────────────────────┐
│  New Deal                                                        │
│                                                                  │
│  Deal Name: [Oakwood Apartments]                                │
│                                                                  │
│  Documents:                                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  📄  Oakwood_OM.pdf (4.2 MB)                        [✓]     ││
│  │  📄  T12_Operating_Statement.xlsx (128 KB)          [✓]     ││
│  │  📄  Rent_Roll_Current.xlsx (89 KB)                 [✓]     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Analysis Type:                                                  │
│  [•] BOE (Back of Envelope) - Quick screening                  │
│  [ ] Full UW - Complete underwriting                            │
│                                                                  │
│  [Cancel]  [Analyze Deal →]                                    │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.3 Processing (Background)
**Duration:** 1-2 minutes

**Progress Indicator:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Analyzing Oakwood Apartments...                                │
│                                                                  │
│  [████████████████████████──────────] 85%                       │
│                                                                  │
│  ✓ Documents uploaded                                           │
│  ✓ Data extracted (168 units, Nashville, TN)                   │
│  ✓ Market research completed                                    │
│  ⏳ Calculating returns...                                       │
│  ⏳ Generating memo...                                           │
│                                                                  │
│  Estimated completion: 30 seconds                               │
└─────────────────────────────────────────────────────────────────┘
```

**Behind the Scenes:**
1. **Document Extraction (Claude Haiku, 20s):** Extract property details, financials, rent roll
2. **Market Research (Perplexity, 30s):** MSA classification, submarket data, employment
3. **Screening (Python, 5s):** Risk-adjusted hurdles, red flag check, scoring
4. **Pro Forma (Python, 5s):** Basic DCF with AI assumptions
5. **Memo Generation (Claude Sonnet, 30s):** 1-2 page BOE summary

**Total Time:** ~90 seconds

#### 2.4 BOE Results
```
┌─────────────────────────────────────────────────────────────────┐
│  BOE Analysis Complete ✓                                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RECOMMENDATION: PROCEED                                  │  │
│  │  Score: 78/100 (BUY)                                      │  │
│  │  Confidence: High                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  QUICK METRICS                                                   │
│  ├─ Purchase Price:   $29.4M ($175K/unit)                      │
│  ├─ Going-In Cap:     5.8%                                      │
│  ├─ Stabilized Cap:   6.2%                                      │
│  ├─ IRR:              19.2% ✓                                   │
│  ├─ Equity Multiple:  1.89x ✓                                  │
│  └─ CoC (Stab):       8.4%                                      │
│                                                                  │
│  EXECUTIVE SUMMARY                                               │
│  Oakwood Apartments presents a strong value-add opportunity in  │
│  a growing Nashville submarket. The property is well-positioned  │
│  with recent exterior renovations and below-market rents. A     │
│  light interior renovation program ($8K/unit) can capture       │
│  $175/unit rent premiums. Returns exceed target hurdles with    │
│  moderate execution risk.                                        │
│                                                                  │
│  TOP 3 STRENGTHS                                                 │
│  ✓ Below-market rents: $175/unit upside                        │
│  ✓ Strong market: 3.2% job growth, 95% absorption              │
│  ✓ Manageable renovation: Exterior complete, interior light    │
│                                                                  │
│  TOP 3 CONCERNS                                                  │
│  ⚠ Age: 39 years, ongoing CapEx needs                         │
│  ⚠ Supply: 2,500 units under construction                      │
│  ⚠ Tax risk: Reassessment likely post-sale                     │
│                                                                  │
│  NEXT STEPS                                                      │
│  • Request updated T-12 and rent roll                           │
│  • Tour property and competitive set                            │
│  • Validate renovation budget with contractor                   │
│  • Confirm property tax reassessment ratio with county          │
│                                                                  │
│  [Download PDF]  [Full Underwriting]  [Pass on Deal]          │
└─────────────────────────────────────────────────────────────────┘
```

#### 2.5 Decision & Response
**User Actions:**
1. **Proceed:** Move to "LOI" stage, schedule tour
2. **Full Underwriting:** Trigger complete analysis
3. **Pass:** Archive deal with reason

**Email to Broker (Generated):**
```
Hi [Broker Name],

Thank you for sharing Oakwood Apartments. We've completed our initial 
review and would like to proceed. The deal aligns with our investment 
criteria, and we're interested in learning more.

Next steps:
1. Can you provide an updated T-12 and current rent roll?
2. We'd like to schedule a property tour next week.
3. Do you have preliminary renovation cost estimates?

Looking forward to discussing further.

Best,
[Your Name]
```

### Success Metrics
- ✅ BOE complete in <2 minutes
- ✅ 85%+ accuracy on extracted data
- ✅ <$0.15 LLM cost per BOE

---

## 3. Full Deal Underwriting

**Use Case:** Deal passed initial screening, now perform complete institutional underwriting for IC presentation.

### Flow Overview

```
BOE Pass → Request Full UW → Review/Edit Assumptions → 
Approve Pro Forma → Generate IC Memo → Present to Investment Committee
```

### Detailed Steps

#### 3.1 Trigger Full Underwriting
**Entry Point:** BOE results page or deal detail page

**Button:** "Full Underwriting"

#### 3.2 Comprehensive Data Extraction
**Duration:** 3-5 minutes

**Processing Steps:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Full Underwriting Analysis                                     │
│                                                                  │
│  [████████████████████──────────────] 75%                       │
│                                                                  │
│  ✓ Property data extraction (complete)                          │
│  ✓ Rent roll analysis (168 units processed)                    │
│  ✓ T-12 expense breakdown (12 line items)                      │
│  ✓ Market research (MSA + submarket)                           │
│  ✓ Comparable transactions (4 comps identified)                │
│  ⏳ Building pro forma model...                                 │
│  ⏳ Calculating sensitivities...                                 │
│  ⏳ Generating investment memo...                                │
│                                                                  │
│  Estimated completion: 2 minutes                                │
└─────────────────────────────────────────────────────────────────┘
```

**What's Happening:**
1. **Deep Data Extraction (Claude Sonnet, 60s):** Every rent roll unit, all expense line items, full T-12 detail
2. **Market Research (Perplexity, 45s):** Deep submarket analysis, comps, supply pipeline
3. **Assumption Generation (Claude Sonnet, 60s):** AI suggests all pro forma inputs with rationale
4. **Pro Forma Build (Python, 10s):** Complete 10-year DCF with monthly detail
5. **Sensitivity Analysis (Python, 10s):** Exit cap, rent growth, vacancy scenarios
6. **Memo Generation (Claude Sonnet, 90s):** 8-10 page Full UW Memo

**Total Time:** ~5-7 minutes

#### 3.3 Assumption Review
```
┌─────────────────────────────────────────────────────────────────┐
│  Pro Forma Assumptions                          [Auto-Save ✓]  │
│                                                                  │
│  📋 Tabs: [Revenue] [Expenses] [CapEx] [Financing] [Exit]     │
│                                                                  │
│  ── REVENUE ────────────────────────────────────────────────    │
│                                                                  │
│  Unit Mix                                      In-Place  Market │
│  ├─ 1BR (48 units, 750 SF)                    $1,150   $1,325  │
│  ├─ 2BR (96 units, 1,100 SF)                  $1,475   $1,650  │
│  └─ 3BR (24 units, 1,350 SF)                  $1,850   $2,025  │
│                                                                  │
│  Pro Forma Rents (Post-Renovation)                              │
│  ├─ 1BR: [$1,325] (market rate)               ✏️ Edit          │
│  ├─ 2BR: [$1,650] (market rate)               ✏️ Edit          │
│  └─ 3BR: [$2,025] (market rate)               ✏️ Edit          │
│                                                                  │
│  💡 AI Rationale: Recent comps show $1,300-1,350 for renovated │
│     1BRs. We're using $1,325 as conservative midpoint.         │
│                                                                  │
│  Rent Growth (Annual %)                                          │
│  Year 1: [4.0]%  Year 2: [3.5]%  Year 3: [3.0]%  Year 4-10: [2.5]%│
│                                                                  │
│  💡 Market Analysis: Nashville MSA has averaged 4.2% rent      │
│     growth over past 3 years. We're projecting 4% Year 1       │
│     (pent-up demand) stepping down to 2.5% long-term.          │
│                                                                  │
│  Other Income: [$425] per unit per year        ✏️ Edit         │
│  ├─ Pet fees: $180                                              │
│  ├─ Parking: $120                                               │
│  ├─ Laundry: $60                                                │
│  ├─ Utility reimbursement: $40                                  │
│  └─ Other: $25                                                  │
│                                                                  │
│  Physical Vacancy: [5.0]%                      ✏️ Edit         │
│  Credit Loss: [2.0]%                           ✏️ Edit         │
│                                                                  │
│  [← Back to Summary]  [Continue to Expenses →]                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **AI Rationale:** Explains why each assumption was chosen
- **Inline Editing:** Click any number to change
- **Real-Time Recalc:** Python instantly recalculates all downstream metrics (<100ms)
- **Confidence Scores:** Show how certain AI is about each assumption (High/Medium/Low)
- **Market Comparison:** Compare assumptions to benchmarks

**Expenses Tab:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Operating Expenses                             Per Unit   Total│
│                                                                  │
│  Management Fee (4% of EGI)                    $752    $126,300 │
│  Payroll & Personnel                           $1,240  $208,300 │
│  General & Administrative                      $485    $81,500  │
│  Marketing & Leasing                           $290    $48,700  │
│  Utilities                                     $720    $121,000 │
│  Repairs & Maintenance                         $980    $164,600 │
│  Property Taxes                                $1,485  $249,500 │
│  Insurance                                     $620    $104,200 │
│  Replacement Reserves                          $300    $50,400  │
│  ─────────────────────────────────────────────────────────────  │
│  TOTAL OPERATING EXPENSES                      $6,872  $1,154,500│
│                                                                  │
│  Expense Ratio: 58.2% (vs. 56% market avg)     ⚠️ Slightly high│
│                                                                  │
│  🔍 Property Tax Detail                                         │
│  Current Assessed Value:      $18,500,000                       │
│  Expected Reassessment:       $24,500,000 (70% of purchase)    │
│  Millage Rate:                1.02%                             │
│  Projected Tax (Year 2):      $249,500                          │
│                                                                  │
│  💡 Tennessee reassesses at ~65-70% of sale price. We're using │
│     70% (conservative). Consider filing appeal after purchase.  │
│                                                                  │
│  [Three-Scenario Modeling]  ✏️ Edit Any Line Item              │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.4 Approve Pro Forma
**After reviewing/editing all tabs:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Pro Forma Summary                                              │
│                                                                  │
│  SOURCES & USES                                                  │
│  Sources:                      Uses:                             │
│  Senior Debt     $20,580,000   Purchase Price  $29,400,000     │
│  GP Equity       $  890,000    Closing Costs   $   735,000     │
│  LP Equity       $ 8,000,000   Acq Fee         $   294,000     │
│  ─────────────────────────     Renovation      $ 1,344,000     │
│  Total Sources   $29,470,000   Reserves        $   147,000     │
│                                 Total Uses      $29,920,000     │
│                                                                  │
│  RETURNS (5-Year Hold)                                           │
│  Levered IRR:              19.2% ✓ (vs 18.0% target)           │
│  Equity Multiple:          1.89x ✓ (vs 1.80x target)           │
│  Average CoC:              7.8%                                  │
│  LP IRR:                   18.1% (after fees & promote)         │
│  GP IRR:                   45.2% (including promote)            │
│                                                                  │
│  SENSITIVITY ANALYSIS                                            │
│  Exit Cap Rate vs. Rent Growth:                                 │
│  ┌────────┬────────┬────────┬────────┬────────┐                │
│  │        │  2.0%  │  2.5%  │  3.0%  │  3.5%  │ Rent Growth    │
│  ├────────┼────────┼────────┼────────┼────────┤                │
│  │  5.75% │  22.1% │  23.4% │  24.6% │  25.9% │                │
│  │  6.00% │  19.2% │  20.3% │  21.5% │  22.6% │ ← Base         │
│  │  6.25% │  16.5% │  17.5% │  18.6% │  19.6% │                │
│  │  6.50% │  14.0% │  15.0% │  15.9% │  16.9% │                │
│  └────────┴────────┴────────┴────────┴────────┘                │
│                                                                  │
│  [Download Excel]  [Generate IC Memo]  [Run What-If Scenarios] │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.5 Generate IC Memo
**User clicks "Generate IC Memo"**

**Processing (60-90s):**
```
┌─────────────────────────────────────────────────────────────────┐
│  Generating Investment Committee Memo...                        │
│                                                                  │
│  [████████████████████████████████████] 100%                    │
│                                                                  │
│  ✓ Executive summary                                            │
│  ✓ Property overview & photos                                   │
│  ✓ Market analysis                                              │
│  ✓ Financial summary                                            │
│  ✓ Risk factors & mitigations                                   │
│  ✓ Investment recommendation                                    │
│                                                                  │
│  Memo ready! (4-6 pages)                                        │
│                                                                  │
│  [Download PDF]  [View in Browser]  [Email to Team]           │
└─────────────────────────────────────────────────────────────────┘
```

**IC Memo Contents (4-6 pages):**
1. **Executive Summary & Recommendation**
2. **Property Overview** (unit mix, photos, condition)
3. **Market Analysis** (MSA overview, submarket fundamentals, employment)
4. **Financial Summary** (sources & uses, returns, sensitivity)
5. **Risk Factors & Mitigations**
6. **Value Creation Thesis**

### Success Metrics
- ✅ Full UW complete in <7 minutes
- ✅ User edits <5 assumptions on average (AI got most right)
- ✅ <$2.00 LLM cost per Full UW

---

## 4. Investment Committee Presentation

**Use Case:** Present deal to IC using DREAM-generated memo and live pro forma.

### Flow Overview

```
IC Scheduled → Prepare Materials → Present → Answer Questions → 
Vote → Update Deal Status
```

### Detailed Steps

#### 4.1 Pre-Meeting Preparation
**1-2 days before IC:**

**Checklist:**
```
┌─────────────────────────────────────────────────────────────────┐
│  IC Meeting Checklist: Oakwood Apartments                      │
│                                                                  │
│  Meeting: Tuesday, Jan 15, 2025 @ 10:00 AM                     │
│                                                                  │
│  DOCUMENTS                                                       │
│  [✓] IC Memo (6 pages, generated Dec 20)                       │
│  [✓] Pro Forma Excel (emailed to committee)                    │
│  [✓] Property photos (attached to memo)                        │
│  [ ] Site visit photos (upload recommended)                    │
│  [ ] Contractor bids (if available)                            │
│                                                                  │
│  PREPARATION                                                     │
│  [✓] Memo emailed 48 hours in advance                          │
│  [✓] Presentation slides generated                             │
│  [ ] Rehearse pitch (recommended)                               │
│  [ ] Prepare Q&A talking points                                 │
│                                                                  │
│  ANTICIPATED QUESTIONS                                           │
│  (Based on IC history and this deal's risk factors)            │
│  • Why are we confident in $175/unit rent bumps?              │
│  • What if property taxes reassess at 80% instead of 70%?     │
│  • How does new supply (2,500 units) impact absorption?       │
│  • What's our exit strategy if cap rates expand?              │
│                                                                  │
│  [Add Question]  [Generate Talking Points]                     │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2 Presentation Mode
**During IC meeting:**

**Live Dashboard:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ▶️ OAKWOOD APARTMENTS - IC PRESENTATION                        │
│                                                                  │
│  [Slide 1 of 9]                            [Presenter View 📺] │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │            OAKWOOD APARTMENTS                            │  │
│  │            Nashville, TN                                 │  │
│  │                                                           │  │
│  │            [Property Aerial Photo]                       │  │
│  │                                                           │  │
│  │            168 Units • Class B • Built 1985             │  │
│  │            Investment Score: 78/100 (BUY)               │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Presenter Notes:                                               │
│  • Highlight location: 5 mi from downtown, near major employers│
│  • Mention recent $8M exterior renovation (complete)           │
│  • Emphasize value-add thesis: light interior, rent to market  │
│                                                                  │
│  [← Prev]  [Next →]  [Jump to Slide...]  [Exit Presentation]  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Slides:**
1. **Title Slide** (property name, location, photo)
2. **Executive Summary** (recommendation, score, key metrics)
3. **Investment Thesis** (3 key value drivers)
4. **Property Overview** (unit mix, photos, condition)
5. **Market Analysis** (MSA overview, submarket strengths)
6. **Financial Summary** (returns, sources & uses)
7. **Value Creation** (renovation plan, rent upside)
8. **Risks & Mitigations** (top 3-4 risks)
9. **Recommendation** (vote request)

#### 4.3 Live Q&A with Pro Forma Editing
**IC Member:** "What if rent growth is only 2% instead of 3%?"

**Presenter Action:** Switch to Pro Forma view, edit assumption live

```
┌─────────────────────────────────────────────────────────────────┐
│  Live Pro Forma Editing                                         │
│                                                                  │
│  Rent Growth Assumption:                                         │
│  Original: 3.0% annually                                         │
│  Scenario: [2.0%] annually                                       │
│                                                                  │
│  [Calculate →]                                                   │
│                                                                  │
│  ── RESULTS ────────────────────────────────────────────────    │
│                                                                  │
│               Original    Scenario    Change                     │
│  IRR:         19.2%       17.1%       -2.1% ⚠️                  │
│  EM:          1.89x       1.76x       -0.13x                    │
│  LP IRR:      18.1%       16.2%       -1.9%                     │
│                                                                  │
│  ✓ Still exceeds minimum hurdles (14% IRR, 1.50x EM)           │
│  ⚠️ Falls below target hurdles (18% IRR, 1.80x EM)             │
│                                                                  │
│  Recommendation: HOLD (consider repricing)                      │
│                                                                  │
│  [Revert]  [Save as Downside Scenario]  [Keep Presenting]     │
└─────────────────────────────────────────────────────────────────┘
```

**Real-time recalculation (<100ms) demonstrates:**
- Transparency of assumptions
- Margin of safety (or lack thereof)
- Professional preparedness

#### 4.4 IC Vote & Decision
**After discussion:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Investment Committee Vote                                      │
│                                                                  │
│  Deal: Oakwood Apartments                                       │
│  Presenter: [Your Name]                                         │
│  Date: January 15, 2025                                         │
│                                                                  │
│  VOTING                                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  John Smith (Managing Partner)     [✓] Approve              ││
│  │  Sarah Johnson (CIO)               [✓] Approve              ││
│  │  Michael Chen (CFO)                [✓] Approve with conditions││
│  │  Emily Davis (Asset Manager)       [✓] Approve              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Decision: APPROVED                                              │
│                                                                  │
│  Conditions:                                                     │
│  • Obtain updated property tax assessment from county           │
│  • Validate renovation budget with 2nd contractor bid           │
│  • Conduct environmental Phase I                                │
│                                                                  │
│  Next Steps:                                                     │
│  • Submit LOI by January 17                                     │
│  • Schedule property tour for full team                         │
│  • Begin due diligence immediately upon PSA execution           │
│                                                                  │
│  [Update Deal Status]  [Create DD Tasks]  [Export Meeting Notes]│
└─────────────────────────────────────────────────────────────────┘
```

#### 4.5 Post-Meeting Actions
**Automated by DREAM AI:**
- Deal status updated to "IC Approved"
- Tasks created for conditions (assigned to team)
- Meeting notes saved to deal record
- Notification sent to team
- Calendar events created for next steps

### Success Metrics
- ✅ Presentations run smoothly with zero technical issues
- ✅ IC members rate quality as 4.5/5 or higher
- ✅ Faster IC decision-making (30% reduction in meeting time)

---

## 5. Pipeline Management

**Use Case:** Track 50+ deals across multiple stages, assign tasks, collaborate with team.

### Flow Overview

```
View Pipeline → Filter/Sort → Update Stage → Assign Tasks → 
Review Activity → Generate Pipeline Report
```

### Detailed Steps

#### 5.1 Pipeline Kanban View
```
┌─────────────────────────────────────────────────────────────────┐
│  Pipeline                                   [+ New Deal]  [⚙️]  │
│                                                                  │
│  Filters: [All Deals ▼] [All Users ▼] [This Month ▼]          │
│  Sort: [Date Added ▼]                                           │
│                                                                  │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │ New      │Screening │   LOI    │ Due Dil. │Under Con.│      │
│  │  (12)    │  (18)    │   (8)    │   (5)    │   (3)    │      │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤      │
│  │┌────────┐│┌────────┐│┌────────┐│┌────────┐│┌────────┐│      │
│  ││Oakwood ││││SunRidge││││Maple  ││││Riverside││Central ││      │
│  ││Nashville││Phoenix │││Glen    │││Dallas   │││Austin  ││      │
│  ││168 units│││240 units││304 units│││192 units│││148 units│     │
│  ││Score: 78││Score: 82││Score: 75││Score: 88││Score: 91││      │
│  ││📄 3 docs││📄 5 docs││📄 7 docs││📄 12 docs││📄 15 docs│     │
│  │└────────┘││└────────┘││└────────┘││└────────┘││└────────┘│      │
│  ││ [View]  ││[View]   ││[View]   ││[View]   ││[View]   ││      │
│  │└────────┘│└────────┘│└────────┘│└────────┘│└────────┘│      │
│  │          │          │          │          │          │      │
│  │┌────────┐│┌────────┐│┌────────┐│          │          │      │
│  ││Parkside│││Harbor  │││Westgate│││          │          │      │
│  ││Tampa   │││Seattle │││Phoenix │││          │          │      │
│  ││...     │││...     │││...     │││          │          │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
│                                                                  │
│  [List View]  [Map View]  [Calendar View]                      │
└─────────────────────────────────────────────────────────────────┘
```

**Deal Card Details:**
- Property name & location
- Unit count
- Investment score
- Document count
- Key dates (LOI due, closing, etc.)
- Assigned team member

**Drag & Drop:**
- User can drag deal cards between stages
- Automatically updates deal status
- Triggers stage-specific workflows (e.g., create DD checklist when moved to "Due Diligence")

#### 5.2 List View (Alternative)
```
┌─────────────────────────────────────────────────────────────────┐
│  Pipeline - List View                                           │
│                                                                  │
│  [⬚ Select All]  [Export CSV]  [Bulk Actions ▼]               │
│                                                                  │
│  Name           Location    Units  Score Stage      Updated     │
│  ─────────────────────────────────────────────────────────────  │
│  [⬚] Oakwood    Nashville   168    78   Screening  2 days ago   │
│  [⬚] SunRidge   Phoenix     240    82   Screening  3 days ago   │
│  [⬚] Maple Glen Phoenix     304    75   LOI        5 days ago   │
│  [⬚] Riverside  Dallas      192    88   Due Dil.   1 week ago   │
│  [⬚] Central    Austin      148    91   Contract   2 weeks ago  │
│  [⬚] Parkside   Tampa       216    68   Screening  3 days ago   │
│  [⬚] Harbor     Seattle     180    73   Screening  1 week ago   │
│  [⬚] Westgate   Phoenix     156    79   LOI        4 days ago   │
│  ...                                                             │
│                                                                  │
│  Showing 1-25 of 46 deals                    [1] [2] [3] [Next]│
└─────────────────────────────────────────────────────────────────┘
```

**Bulk Actions:**
- Assign to team member
- Change stage
- Archive/delete
- Export selected

#### 5.3 Deal Detail with Tasks
```
┌─────────────────────────────────────────────────────────────────┐
│  Oakwood Apartments                                [⋯ More]     │
│  Nashville, TN • 168 Units • Built 1985                         │
│                                                                  │
│  📋 Tabs: [Overview] [Documents] [Analysis] [Tasks] [Activity] │
│                                                                  │
│  ── TASKS ──────────────────────────────────────────────────    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  [+] Add Task                                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ✅ Completed (4)                          [Show ▼]             │
│  ├─ [✓] Upload OM (You, 2 days ago)                            │
│  ├─ [✓] Run BOE analysis (You, 2 days ago)                     │
│  ├─ [✓] Request updated T-12 (Sarah, 1 day ago)                │
│  └─ [✓] Schedule property tour (Michael, 1 day ago)            │
│                                                                  │
│  🔄 In Progress (2)                                              │
│  ├─ [⏳] Validate renovation budget with contractor             │
│  │      Assigned: Sarah Johnson                                 │
│  │      Due: Jan 18, 2025                                       │
│  │      [View Details]                                          │
│  └─ [⏳] Confirm property tax reassessment with county          │
│        Assigned: Michael Chen                                   │
│        Due: Jan 20, 2025                                        │
│        [View Details]                                           │
│                                                                  │
│  📅 Upcoming (3)                                                 │
│  ├─ [ ] Property tour                                           │
│  │     Assigned: Team                                           │
│  │     Due: Jan 22, 2025                                        │
│  ├─ [ ] Environmental Phase I                                   │
│  │     Assigned: Sarah Johnson                                  │
│  │     Due: Jan 25, 2025                                        │
│  └─ [ ] Submit LOI                                              │
│        Assigned: You                                            │
│        Due: Jan 17, 2025 ⚠️ 2 days away                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.4 Activity Log
```
┌─────────────────────────────────────────────────────────────────┐
│  Activity Log                                                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  📝 You added a note                        2 hours ago     │ │
│  │  "Spoke with broker. Willing to negotiate on price..."     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  ✅ Sarah completed task: Request updated T-12   Yesterday │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  📄 Michael uploaded document: Updated_Rent_Roll.xlsx      │ │
│  │                                                  Yesterday  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  🎯 Deal moved from New → Screening        2 days ago      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  📊 BOE Analysis completed (Score: 78)     2 days ago      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Load More...]                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Success Metrics
- ✅ 90%+ deals have updated status within 48 hours
- ✅ 85%+ tasks completed by due date
- ✅ Average time in pipeline: <60 days

---

## 6. Pro Forma Sensitivity Analysis

**Use Case:** Test deal under different scenarios to understand risk and return distribution.

### Detailed Steps

#### 6.1 Base Case Review
```
┌─────────────────────────────────────────────────────────────────┐
│  Pro Forma: Oakwood Apartments                                  │
│                                                                  │
│  Current Scenario: [Base Case ▼]                               │
│  └─ Other Scenarios: Upside, Downside, Custom                  │
│                                                                  │
│  RETURNS (5-Year Hold)                                           │
│  Levered IRR:              19.2%                                │
│  Equity Multiple:          1.89x                                │
│  LP IRR:                   18.1%                                │
│                                                                  │
│  [Run What-If Analysis]  [Create New Scenario]                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.2 What-If Analysis
**User clicks "Run What-If Analysis":**

```
┌─────────────────────────────────────────────────────────────────┐
│  What-If Sensitivity Analysis                                   │
│                                                                  │
│  Select Variables to Test:                                      │
│  [✓] Exit Cap Rate         (±0.50%)                            │
│  [✓] Rent Growth            (±1.00%)                            │
│  [✓] Vacancy Rate          (±2.00%)                            │
│  [ ] Expense Growth        (±0.50%)                            │
│  [ ] Renovation Cost       (±15%)                               │
│                                                                  │
│  [Run Analysis →]                                               │
│                                                                  │
│  ── EXIT CAP VS. RENT GROWTH ──────────────────────────────    │
│                                                                  │
│  IRR (%) by Exit Cap Rate and Rent Growth:                     │
│                                                                  │
│  Exit Cap │  2.0%    2.5%    3.0%    3.5%    4.0%              │
│  ────────┼──────────────────────────────────────────            │
│    5.50% │  23.8%   25.2%   26.5%   27.9%   29.2%              │
│    5.75% │  21.0%   22.3%   23.5%   24.8%   26.0%              │
│    6.00% │  18.3%   19.5%   20.7%   21.9%   23.1% ← Base       │
│    6.25% │  15.8%   16.9%   18.0%   19.1%   20.2%              │
│    6.50% │  13.4%   14.4%   15.5%   16.5%   17.5%              │
│                                                                  │
│  💡 Insight: Deal achieves 14% minimum hurdle in 88% of        │
│     scenarios above. Only fails if BOTH exit cap expands        │
│     to 6.50%+ AND rent growth falls below 2.0%.                 │
│                                                                  │
│  [Download Full Sensitivity Report]  [Create Scenarios]        │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.3 Scenario Modeling
**User clicks "Create New Scenario":**

```
┌─────────────────────────────────────────────────────────────────┐
│  Create Scenario                                                │
│                                                                  │
│  Scenario Name: [Downside]                                      │
│                                                                  │
│  Starting Point: [Copy from Base Case ▼]                       │
│                                                                  │
│  Assumptions to Adjust:                                          │
│                                                                  │
│  Rent Growth:                                                    │
│  Base: 3.0% annually                                             │
│  Downside: [2.0%] annually                                       │
│                                                                  │
│  Exit Cap Rate:                                                  │
│  Base: 6.00%                                                     │
│  Downside: [6.50%]                                               │
│                                                                  │
│  Physical Vacancy:                                               │
│  Base: 5.0%                                                      │
│  Downside: [7.0%]                                                │
│                                                                  │
│  Property Tax Reassessment:                                      │
│  Base: 70% of purchase                                           │
│  Downside: [80%] of purchase                                     │
│                                                                  │
│  [+ Add More Adjustments]                                        │
│                                                                  │
│  [Cancel]  [Calculate Downside Returns →]                       │
└─────────────────────────────────────────────────────────────────┘
```

**Downside Results:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Scenario Comparison                                            │
│                                                                  │
│  Metric          Base Case   Upside    Downside   Worst Case   │
│  ──────────────────────────────────────────────────────────────  │
│  IRR:            19.2%       24.1%     14.8% ⚠️    10.2% 🛑    │
│  Equity Mult:    1.89x       2.18x     1.54x ⚠️    1.32x 🛑    │
│  LP IRR:         18.1%       22.8%     13.9% ⚠️     9.5% 🛑    │
│  Peak Equity:    $8.9M       $8.9M     $9.2M       $9.8M       │
│                                                                  │
│  ✓ Base Case: Exceeds all hurdles                              │
│  ✓ Upside: Strong outperformance                                │
│  ⚠️ Downside: Meets minimum hurdles but below target           │
│  🛑 Worst Case: Falls below minimum hurdles (FAIL)             │
│                                                                  │
│  Recommendation:                                                 │
│  Deal has acceptable downside protection but limited margin of  │
│  safety. Consider negotiating 5% price reduction ($1.5M) to     │
│  improve downside returns.                                       │
│                                                                  │
│  [Save Scenarios]  [Export to Excel]  [Present to IC]         │
└─────────────────────────────────────────────────────────────────┘
```

### Success Metrics
- ✅ 95%+ IC presentations include sensitivity analysis
- ✅ Downside scenarios catch 80%+ of deals that later underperform

---

## 7. Team Collaboration

**Use Case:** Multiple analysts working on same deal, need to coordinate and share insights.

### Detailed Steps

#### 7.1 Team Member Permissions
```
┌─────────────────────────────────────────────────────────────────┐
│  Team Settings                                                  │
│                                                                  │
│  Members (4)                                 [+ Invite Member]  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  👤 You (Owner)                          Admin              │ │
│  │     evan@shieldstone.com                                    │ │
│  │     [Edit Profile]                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  👤 Sarah Johnson                        Admin              │ │
│  │     sarah@shieldstone.com                                   │ │
│  │     Last active: 2 hours ago                                │ │
│  │     [Change Role ▼]  [Remove]                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  👤 Michael Chen                         Analyst            │ │
│  │     michael@shieldstone.com                                 │ │
│  │     Last active: Yesterday                                  │ │
│  │     [Change Role ▼]  [Remove]                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  👤 Emily Davis                          Viewer             │ │
│  │     emily@shieldstone.com                                   │ │
│  │     Last active: 3 days ago                                 │ │
│  │     [Change Role ▼]  [Remove]                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ROLES & PERMISSIONS                                             │
│  • Admin: Full access, can add/remove members                  │
│  • Analyst: Create/edit deals, run analyses, generate reports  │
│  • Viewer: View-only access, cannot edit                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 7.2 Real-Time Collaboration
**Multiple users working on same deal:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Oakwood Apartments                                             │
│                                                                  │
│  👤 Sarah is editing Pro Forma (Expenses tab)  [View Live]     │
│                                                                  │
│  Recent Changes:                                                 │
│  ├─ Sarah updated Property Taxes: $249,500 → $265,000          │
│  │  Rationale: "Spoke with county - reassessment will be 75%"  │
│  │  3 minutes ago                              [Accept] [Discuss]│
│  │                                                              │
│  ├─ Michael added note to Renovation Budget:                    │
│  │  "Contractor bid came in 10% higher than expected"          │
│  │  1 hour ago                                 [View Note]      │
│  │                                                              │
│  └─ Emily commented on Market Analysis:                         │
│     "Found 3 more comps showing $1,350+ for renovated 1BRs"    │
│     2 hours ago                                [View Comps]     │
│                                                                  │
│  [View All Activity]  [Resolve Notifications]                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 7.3 Comments & Discussions
```
┌─────────────────────────────────────────────────────────────────┐
│  Pro Forma: Revenue Assumptions                                 │
│                                                                  │
│  Rent Growth (Annual %):                                         │
│  Year 1: [4.0]%                                   💬 2 comments │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Comments on "Rent Growth - Year 1":                            │
│                                                                  │
│  👤 Sarah Johnson - 2 hours ago                                 │
│  "4% seems aggressive given new supply. I'd use 3% to be safe." │
│  [Reply] [Like 👍]                                              │
│                                                                  │
│    └─ 👤 You - 1 hour ago                                       │
│       "Good point. But broker confirmed 2,500 units are mostly  │
│        Class A, different renter profile. Our Class B comps     │
│        are still tight. I'm comfortable with 4% Year 1."        │
│       [Reply] [Like 👍]                                         │
│                                                                  │
│       └─ 👤 Sarah Johnson - 30 minutes ago                      │
│          "Fair. Let's split the difference: 3.5% Year 1?"      │
│          [Reply] [Like 👍] [Accept Change]                     │
│                                                                  │
│  [Add Comment]                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Success Metrics
- ✅ 50%+ deals have multiple team members contributing
- ✅ 90%+ comments resolved within 24 hours
- ✅ Zero data loss/conflicts from concurrent editing

---

## 8. Custom Investment Criteria Setup

**Use Case:** Experienced user wants to fine-tune screening criteria to match their specific investment thesis.

### Detailed Steps

#### 8.1 Criteria Configuration
```
┌─────────────────────────────────────────────────────────────────┐
│  Investment Criteria                                [Save]      │
│                                                                  │
│  📋 Tabs: [Hard Stops] [Target Ranges] [Soft Preferences]      │
│                                                                  │
│  ── HARD STOPS ─────────────────────────────────────────────    │
│  (Deals failing these are automatically disqualified)           │
│                                                                  │
│  Property Type:                                                  │
│  [✓] Conventional Multifamily                                   │
│  [ ] Student Housing                                             │
│  [ ] Senior Housing                                              │
│                                                                  │
│  Minimum Units: [50]                                            │
│  Maximum Units: [500] (or "No Limit")                           │
│                                                                  │
│  Geographic Restrictions:                                        │
│  [ ] Exclude markets: [Add markets...]                          │
│  [ ] Include only: [Add markets...]                             │
│                                                                  │
│  Red Flags (Auto-Disqualify):                                   │
│  [✓] Active environmental contamination                         │
│  [✓] Unresolvable title/legal issues                           │
│  [✓] Violent crime >2.5x national average                      │
│  [✓] Population decline >1%/year for 5+ years                  │
│  [✓] Single employer >40% of MSA employment                     │
│  [ ] Property age >50 years                                     │
│  [ ] Occupancy <75%                                             │
│                                                                  │
│  ⚠️  Note: Shieldstone methodology recommends minimal hard     │
│     stops. Consider using risk-adjusted hurdles instead.        │
│                                                                  │
│  [Next: Target Ranges →]                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Target Ranges Tab:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Target Ranges                                                  │
│  (Deals are scored based on how well they hit these targets)    │
│                                                                  │
│  RETURNS                                                         │
│                                                                  │
│  Levered IRR:                                                   │
│  ├─ Minimum:    [14.0]% (absolute floor)                       │
│  ├─ Target:     [18.0]% (goal)                                 │
│  └─ Excellent:  [22.0]% (stretch)                              │
│                                                                  │
│  Equity Multiple (5-year hold):                                 │
│  ├─ Minimum:    [1.50]x                                         │
│  ├─ Target:     [1.80]x                                         │
│  └─ Excellent:  [2.00]x                                         │
│                                                                  │
│  Cash-on-Cash (Stabilized):                                     │
│  ├─ Minimum:    [6.0]%                                          │
│  ├─ Target:     [8.0]%                                          │
│  └─ Excellent:  [10.0]%                                         │
│                                                                  │
│  LP IRR (Net after fees & promote):                             │
│  ├─ Minimum:    [15.0]%                                         │
│  ├─ Target:     [17.0]%                                         │
│  └─ Excellent:  [20.0]%                                         │
│                                                                  │
│  ACQUISITION                                                     │
│                                                                  │
│  Price per Unit:                                                 │
│  ├─ Target Range: [$100K] - [$200K] per unit                   │
│  └─ Depends on market, vintage, condition                       │
│                                                                  │
│  Going-In Cap Rate:                                              │
│  ├─ Target Range: [5.0%] - [7.5%]                              │
│  └─ Lower for Gateway, higher for Tertiary                      │
│                                                                  │
│  VALUE-ADD PARAMETERS                                            │
│                                                                  │
│  Renovation Budget:                                              │
│  ├─ Target Range: [$5,000] - [$25,000] per unit                │
│  └─ Light to moderate scope preferred                           │
│                                                                  │
│  Loss-to-Lease:                                                  │
│  ├─ Minimum: [10]% (ensures rent growth opportunity)            │
│  └─ Target: [15-20]%                                            │
│                                                                  │
│  💡 These ranges are used to score deals. Outside ranges don't │
│     automatically disqualify, but reduce the score.             │
│                                                                  │
│  [← Back]  [Next: Soft Preferences →]                          │
└─────────────────────────────────────────────────────────────────┘
```

**Soft Preferences Tab:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Soft Preferences                                               │
│  (Influence scoring but don't disqualify)                       │
│                                                                  │
│  MARKET PREFERENCES                                              │
│                                                                  │
│  Preferred Market Tiers:  (Weight: 15%)                         │
│  [✓] Gateway                        Score: 100                  │
│  [✓] Secondary                      Score: 90                   │
│  [ ] Tertiary                       Score: 70                   │
│                                                                  │
│  PROPERTY CHARACTERISTICS                                        │
│                                                                  │
│  Preferred Vintage:  (Weight: 10%)                              │
│  [✓] Built 2000+                    Score: 100                  │
│  [✓] Built 1980-1999                Score: 85                   │
│  [ ] Built 1960-1979                Score: 70                   │
│  [ ] Built pre-1960                 Score: 60                   │
│                                                                  │
│  Preferred Property Class:  (Weight: 10%)                       │
│  [ ] Class A                        Score: 90                   │
│  [✓] Class B                        Score: 100 (best fit)       │
│  [ ] Class C                        Score: 75                   │
│                                                                  │
│  DEAL SOURCING                                                   │
│                                                                  │
│  Deal Source:  (Weight: 5%)                                     │
│  [✓] Off-market (relationship)      Score: 100                  │
│  [✓] Lightly marketed               Score: 90                   │
│  [ ] Fully marketed                 Score: 80                   │
│                                                                  │
│  BUSINESS PLAN                                                   │
│                                                                  │
│  Preferred Strategy:  (Weight: 15%)                             │
│  [✓] Value-add (light renovation)   Score: 100                  │
│  [✓] Value-add (heavy renovation)   Score: 85                   │
│  [ ] Core+ (stabilized)             Score: 70                   │
│  [ ] Opportunistic (ground-up)      Score: 60                   │
│                                                                  │
│  ──────────────────────────────────────────────────────────────  │
│                                                                  │
│  CATEGORY WEIGHTS                                                │
│  (Adjust how each category influences overall score)            │
│                                                                  │
│  ├─ Financial Performance:    [30]%                             │
│  ├─ Market Quality:           [25]%                             │
│  ├─ Property Quality:         [20]%                             │
│  ├─ Business Plan Viability:  [20]%                             │
│  └─ Deal Sourcing:            [5]%                              │
│                                                                  │
│  Total: 100%                                                     │
│                                                                  │
│  [← Back]  [Save Investment Criteria]                          │
└─────────────────────────────────────────────────────────────────┘
```

#### 8.2 Testing Criteria Against Historical Deals
```
┌─────────────────────────────────────────────────────────────────┐
│  Test Your Criteria                                             │
│                                                                  │
│  See how your updated criteria would score past deals:          │
│                                                                  │
│  Deal             Old Score   New Score   Change                │
│  ─────────────────────────────────────────────────────────────  │
│  Oakwood (Nash)   78          82          +4 ↑                  │
│  SunRidge (PHX)   82          79          -3 ↓                  │
│  Maple Glen       75          75          0 →                   │
│  Riverside (DAL)  88          90          +2 ↑                  │
│                                                                  │
│  Average Change: +0.8 points                                     │
│                                                                  │
│  💡 Your updated criteria favor newer properties in secondary  │
│     markets, which aligns with recent successful deals.         │
│                                                                  │
│  [Apply New Criteria]  [Revert Changes]                        │
└─────────────────────────────────────────────────────────────────┘
```

### Success Metrics
- ✅ 40%+ users customize default criteria
- ✅ Custom criteria result in higher deal quality (measured by post-investment performance)

---

## Summary of Success Metrics Across All Flows

| Flow | Key Metric | Target |
|------|------------|--------|
| Onboarding | Time to first analysis | <10 minutes |
| BOE Screening | Analysis completion time | <2 minutes |
| Full Underwriting | Analysis completion time | <7 minutes |
| IC Presentation | IC satisfaction rating | >4.5/5 |
| Pipeline Management | Deal status update frequency | Within 48 hours |
| Sensitivity Analysis | IC presentations with sensitivity | >95% |
| Team Collaboration | Comment resolution time | <24 hours |
| Criteria Setup | Users customizing criteria | >40% |

---

**Document Version:** 1.0  
**Last Updated:** December 20, 2025  
**Maintained By:** DREAM AI Product Team

