# DreamVision PRD v3.0
## DREAM.AI Domain 1 | Unified Acquisitions Intelligence Platform

**Version:** 3.0  
**Last Updated:** November 2025  
**Status:** Ready for Development  
**Development Approach:** AI-assisted coding (Claude Code / Cursor)

---

## Brand Context

**DreamVision** is a sub-brand within the **DREAM.AI** platform ecosystem.

**DREAM.AI** (Development, Real Estate, Asset Management, and Analysis Innovation) is a comprehensive super app covering the entire real estate investment lifecycle. DreamVision is Domain 1 of 4 planned domains:

| Domain | Sub-Brand | Focus |
|--------|-----------|-------|
| **Domain 1** | **DreamVision** | Acquisitions Intelligence (this PRD) |
| Domain 2 | TBD | Investor Relations & Capital Raising |
| Domain 3 | TBD | Asset Management & Operations |
| Domain 4 | TBD | Construction & Development |

All domains share common infrastructure (auth, billing, data model) and will eventually integrate for cross-domain intelligence. DreamVision is the priority launch product.

---

## 1. Product Overview

### 1.1 What is DreamVision?

DreamVision is an AI-powered acquisitions intelligence platform that helps real estate investors discover, analyze, and pursue investment opportunities. It combines market intelligence, deal sourcing, pipeline management, and automated underwriting into a single workflow.

**Core Value Proposition:** Reduce deal analysis time from 4-8 hours to under 15 minutes while maintaining institutional-quality output.

### 1.2 Target Users

- Real estate investment firms evaluating 10-50+ deals per month
- Emerging sponsors seeking to scale without proportionally scaling headcount
- Family offices and institutional investors wanting AI-powered competitive advantage
- Brokers and advisors needing fast, consistent deal screening

### 1.3 What DreamVision Replaces

| Current Approach | Pain Point | DreamVision Solution |
|-----------------|------------|---------------------|
| Manual market research | Hours of aggregating data sources | AI-powered instant market intelligence |
| Spreadsheet deal tracking | No workflow, fragmented data | Purpose-built pipeline CRM |
| Manual underwriting | 4-8 hours, inconsistent methodology | Configurable AI underwriting in minutes |
| Argus / RedIQ | Expensive, steep learning curve | Intuitive AI-native DCF modeling |
| Separate sourcing tools | Reactive, no integration | Integrated sourcing + analysis |

---

## 2. Development Phases

### Phase 1: Core Platform & BOE Analysis (Weeks 1-2)

**Goal:** Ship a working MVP that can ingest deals and produce useful analysis.

**Features:**
- User authentication and basic multi-tenancy
- Document upload (PDF offering memorandums, Excel financial models)
- AI-powered data extraction (property details, financial metrics)
- Configurable investment criteria with pass/fail screening
- Automated market research for any US property address
- Investment scoring with weighted categories
- BOE memo generation (PDF export)
- Basic deal pipeline (kanban board with stages)
- Delivery integrations (email, Slack webhook, Google Drive)

**Technical Deliverables:**
- FastAPI backend with PostgreSQL
- React frontend with Tailwind CSS
- LLM integration (Claude for analysis, Gemini for routine extraction)
- Perplexity API for market research
- PDF generation (ReportLab or similar)

### Phase 2: Advanced Underwriting & DCF Modeling (Weeks 3-8)

**Goal:** Replace Argus/RedIQ with AI-native financial modeling.

**Features:**
- Full 10-year pro forma generation
- Rent roll import and lease-level modeling
- Assumption engine with AI-suggested defaults + manual override
- Sensitivity analysis (rent growth, vacancy, exit cap, interest rates)
- Scenario modeling (base, upside, downside cases)
- Waterfall modeling (GP/LP splits, promotes, preferred returns)
- Debt modeling (multiple tranches, refinancing scenarios)
- Interactive dashboard with real-time model updates
- Excel export with working formulas
- Investment Committee package generation

**Asset Class Expansion (within Phase 2):**
- **2a.** Conventional Multifamily (default)
- **2b.** Affordable Housing / LIHTC (add compliance tracking, rent restrictions)
- **2c.** Student Housing (bed-based underwriting, academic calendar)
- **2d.** Mobile Home Parks / Manufactured Housing (lot rent, home sales, utility billing)
- **2e.** Senior Housing (independent living, assisted living, memory care, acuity levels)

### Phase 3: Market Intelligence & Deal Sourcing (Weeks 9-16)

**Goal:** Transform from reactive analysis to proactive opportunity identification.

**Features:**
- Market intelligence dashboard with live scoring
- Submarket deep dives (demographics, employment, crime, schools)
- Heat maps showing opportunity density
- Off-market signal detection:
  - Tax delinquency monitoring
  - Ownership pattern analysis (long-hold owners)
  - Loan maturity tracking
  - Permit activity alerts
  - Litigation monitoring
- Owner identification and contact enrichment
- Portfolio mapping (identify multi-property owners)
- Saved searches with alerts

### Phase 4: Outreach Automation & CRM Enhancement (Weeks 17-24)

**Goal:** Complete the acquisitions workflow with automated outreach.

**Features:**
- **Option A - GoHighLevel Integration:**
  - Contact sync to GHL
  - Campaign triggers based on signals
  - Response tracking back to DreamVision
  - Appointment scheduling
  
- **Option B - Native Implementation:**
  - Email sequence builder
  - Template library with personalization
  - A/B testing
  - Deliverability monitoring
  - CAN-SPAM compliance

- Campaign management and analytics
- Lead scoring based on engagement + fit
- Enhanced CRM (full activity tracking, tasks, team collaboration)

### Future Phases: Asset Class Expansion

**Phase 5+:** Expand underwriting capabilities beyond multifamily:
- **5a.** Retail (NNN, strip centers, anchored)
- **5b.** Industrial (warehouse, flex, last-mile)
- **5c.** Industrial Outdoor Storage (IOS)
- **5d.** Office (traditional, medical, flex)
- **5e.** Hospitality (hotels, extended stay)
- **5f.** Self-Storage
- **5g.** Mixed-Use / Development
- **5h.** Data Centers
- **5i.** Parking (surface lots, structured)
- **5j.** Solar & Renewable Energy Infrastructure

Each asset class requires specific:
- Underwriting metrics and KPIs
- Market research parameters
- Comparable analysis frameworks
- Risk factors and scoring adjustments

---

## 3. Core Functional Requirements

### 3.1 Document Processing

**Inputs:**
- PDF: Offering memorandums, broker packages, rent rolls
- Excel: Financial models, rent rolls, operating statements
- Google Sheets: Import capability
- Manual entry: For deals without documents

**Extraction Capabilities:**
- Property details: Address, units/SF, vintage, asking price
- Financial metrics: NOI, cap rate, price per unit/SF
- Deal terms: Financing assumptions, hold period
- Rent roll data: Unit mix, current rents, lease terms, vacancy

**Quality Handling:**
- Confidence scores for extracted data
- Flag uncertain values for user review
- Support for OCR on scanned documents
- Graceful handling of non-standard formats

### 3.2 Investment Criteria Engine

**Philosophy:** Users should be able to configure their own investment criteria, not be locked into any predefined thesis. The system teaches users what metrics matter and why.

**Configurable Criteria Types:**
- Hard stops (deal fails if not met)
- Soft preferences (affects scoring but doesn't disqualify)
- Target ranges (ideal values)

**Example Criteria (user-configurable):**
```yaml
criteria:
  property_type:
    type: hard_stop
    allowed: [multifamily, student_housing, mobile_home_park]
  
  minimum_units:
    type: hard_stop
    value: 50
    
  target_irr:
    type: target_range
    minimum: 15
    target: 18
    excellent: 22
    
  market_tier:
    type: soft_preference
    preferred: [top_30_msa]
    acceptable: [top_100_msa]
    weight: 0.15
```

**Learning Mode:** For new users, the system can suggest industry-standard criteria and explain the rationale for each metric.

### 3.3 Market Research

**Automated Research for Any US Address:**
- MSA identification and tier classification
- Submarket boundaries and characteristics
- Demographic trends (population, households, income)
- Employment data (major employers, job growth, diversity)
- Multifamily fundamentals (vacancy, rent growth, absorption)
- Construction pipeline (deliveries, under construction, planned)
- Crime statistics and safety metrics
- School ratings (where applicable)
- Regulatory environment (rent control, eviction laws)

**Data Freshness:**
- Real-time research via Perplexity API
- Caching for recently researched markets (configurable TTL)
- User can force refresh

### 3.4 Scoring Framework

**Default Categories (user can adjust weights):**
- Financial Performance (suggested: 30-40%)
- Market Quality (suggested: 25-35%)
- Property Quality (suggested: 15-25%)
- Deal Sourcing Quality (suggested: 5-10%)
- Regulatory/Risk Factors (suggested: 5-15%)

**Score Output:**
- Overall score (0-100)
- Category breakdown with individual scores
- Strengths and concerns (AI-generated insights)
- Recommendation (Strong Buy / Buy / Hold / Pass)
- Confidence level

### 3.5 Report Generation

**BOE Memo (Phase 1):**
- Executive summary with recommendation
- Property overview
- Financial highlights
- Market summary
- Key risks and mitigations
- Next steps

**Full Underwriting Package (Phase 2):**
- Everything in BOE plus:
- Detailed pro forma (annual + monthly views)
- Sensitivity tables
- Scenario comparison
- Waterfall returns by investor class
- Comparable deals analysis

**Export Formats:**
- PDF (styled, professional)
- Excel (with working formulas)
- Google Slides (IC presentation)

### 3.6 Pipeline CRM

**Deal Record:**
- Property information
- All associated analyses
- Documents and attachments
- Notes and activity log
- Tasks with assignments and due dates
- Status/stage tracking
- Team member access

**Pipeline Stages (configurable):**
Default: New → Screening → LOI → Due Diligence → Under Contract → Closed / Passed

**Views:**
- Kanban board (drag-and-drop stages)
- List view with filtering/sorting
- Map view (deals by location)
- Calendar view (key dates)

---

## 4. Technical Architecture

### 4.1 Stack Decisions

```
Frontend:        React + TypeScript + Tailwind CSS
Backend:         Python + FastAPI
Database:        PostgreSQL with row-level security
Auth:            Clerk or Auth0 (don't build custom)
File Storage:    S3-compatible (or Google Cloud Storage)
AI - Complex:    Claude API (Sonnet for most, Opus for critical)
AI - Routine:    Gemini Flash (cost optimization)
AI - Research:   Perplexity API
PDF Generation:  ReportLab or WeasyPrint
Deployment:      Containerized (Docker), cloud-agnostic
```

### 4.2 AI/LLM Routing Strategy

Route tasks to appropriate models based on complexity and cost:

| Task | Model | Rationale |
|------|-------|-----------|
| Document text extraction | Gemini Flash | High volume, routine |
| Data field extraction | Gemini Flash | Structured output, routine |
| Market research synthesis | Perplexity | Real-time web access |
| Investment analysis | Claude Sonnet | Complex reasoning |
| Report narrative | Claude Sonnet | Writing quality |
| Complex edge cases | Claude Opus | Highest capability |

**Cost Target:** <$0.50 per complete BOE analysis

### 4.3 Data Model (Core Entities)

```
Organization
├── Users (with roles)
├── Investment Criteria (configurable)
├── Integrations (API keys, webhooks)
└── Subscription

Deal
├── Property (address, details, type)
├── Documents (uploads)
├── Analyses (BOE, full underwriting)
├── Pipeline Stage
├── Notes
├── Tasks
└── Activity Log

Analysis
├── Extracted Data
├── Market Research
├── Scores (by category)
├── Recommendation
├── Generated Reports
└── User Overrides

Market (cached)
├── MSA Classification
├── Submarket Data
├── Research Results
├── Last Updated
```

### 4.4 API Design Principles

- RESTful endpoints for CRUD operations
- Async processing for long-running tasks (analysis, research)
- Webhook support for integrations
- Rate limiting per organization
- Comprehensive error responses

**Key Endpoints:**
```
POST   /api/deals                    Create deal
POST   /api/deals/{id}/documents     Upload document
POST   /api/deals/{id}/analyze       Trigger analysis
GET    /api/deals/{id}/analysis      Get analysis results
PATCH  /api/deals/{id}               Update deal
GET    /api/pipeline                 Get pipeline view
POST   /api/markets/{location}/research   Research market
GET    /api/criteria                 Get investment criteria
PUT    /api/criteria                 Update criteria
```

---

## 5. User Experience Guidelines

### 5.1 Design Principles

- **Speed first:** Optimize every interaction for analyst productivity
- **Progressive disclosure:** Simple by default, powerful when needed
- **Teach as you go:** Help users understand metrics and best practices
- **Keyboard friendly:** Power users can navigate without mouse
- **Mobile responsive:** Core functions work on tablet

### 5.2 Key Screens

1. **Dashboard:** Pipeline summary, recent analyses, tasks due
2. **Deal Intake:** Drag-drop upload, processing status, extracted data preview
3. **Analysis View:** Full memo with collapsible sections, charts, export
4. **Pipeline Board:** Kanban with drag-drop, filters, quick actions
5. **Deal Detail:** All information, documents, history in one place
6. **Market Explorer:** Search markets, view scores, compare (Phase 3)
7. **Settings:** Criteria config, integrations, team management

### 5.3 Onboarding Flow

1. Create account / org
2. Configure investment criteria (wizard with explanations)
3. Connect integrations (Drive, Slack)
4. Upload first deal
5. Review analysis, understand scoring
6. Customize as needed

---

## 6. Success Metrics

| Metric | Target |
|--------|--------|
| Time to first analysis | < 10 minutes from signup |
| BOE analysis time | < 5 minutes (after upload) |
| Data extraction accuracy | > 90% (user validates) |
| Market research coverage | > 85% of key data points |
| AI cost per analysis | < $0.50 |
| User activation | > 60% complete first analysis |
| Weekly active users | > 70% of subscribers |

---

## 7. Development Notes for AI Coding Assistant

### 7.1 Context for Claude Code / Cursor

This PRD describes DreamVision, an AI-powered real estate underwriting platform. When helping build this:

**Architecture Preferences:**
- Prefer simple, readable code over clever abstractions
- Use established patterns (don't reinvent auth, billing, etc.)
- Prioritize shipping over perfection
- Build for iteration (easy to change later)

**Phase 1 Priority Order:**
1. Auth + basic user/org model
2. Deal CRUD + document upload
3. LLM integration for extraction
4. Market research integration
5. Scoring engine
6. Report generation
7. Pipeline board UI
8. Delivery integrations

**Code Quality:**
- Type hints throughout Python code
- TypeScript strict mode for frontend
- Tests for critical paths (scoring, extraction)
- Clear error handling and logging

### 7.2 Key Technical Decisions

**Already Decided:**
- PostgreSQL for database (not NoSQL)
- FastAPI for backend (not Django/Flask)
- React for frontend (not Vue/Svelte)
- Clerk/Auth0 for auth (not custom)
- S3-compatible storage (not local filesystem)

**Open for Discussion:**
- Specific PDF generation library
- Task queue (Celery vs. alternatives)
- Caching strategy (Redis vs. in-memory)
- Hosting platform (Vercel, Railway, Render, etc.)

### 7.3 Asset Class Considerations

When building the underwriting engine, design for extensibility:

```python
class AssetClassConfig:
    """Each asset class defines its own metrics, scoring, and research needs"""
    
    asset_type: str  # multifamily, student_housing, mobile_home_park, etc.
    key_metrics: List[MetricDefinition]
    scoring_weights: Dict[str, float]
    research_requirements: List[str]
    report_template: str
```

This allows adding new asset classes without rewriting core logic.

---

## 8. Out of Scope (for now)

- Native mobile apps (responsive web is sufficient)
- On-premise deployment
- White-labeling
- International markets (US only initially)
- Construction/development underwriting (separate domain)
- Asset management post-acquisition (separate domain)
- Investor relations / LP portal (separate domain)

---

## 9. Open Questions

1. **Pricing model:** Per-seat, per-deal, or hybrid?
2. **Free tier:** Offer limited free access to drive adoption?
3. **Data partnerships:** Worth pursuing CoStar/Yardi integrations early?
4. **Competitive moat:** What's the "10x better" feature we lead with?

---

## Appendix A: Asset Class Metric Reference

### Conventional Multifamily
- Units, unit mix, avg SF
- Rent per unit, rent per SF
- Occupancy, vacancy loss
- NOI, cap rate, price per unit
- IRR, equity multiple, cash-on-cash
- DSCR, LTV

### Affordable Housing / LIHTC
- All multifamily metrics plus:
- AMI levels (30%, 50%, 60%, 80%)
- Rent restrictions by unit
- Compliance period remaining
- Tax credit value
- Year 15 exit considerations

### Student Housing
- Beds (not units)
- Rent per bed
- Lease-up timing (academic calendar)
- Distance to campus
- University enrollment trends
- Pre-leasing velocity

### Mobile Home Parks / MHC
- Lot count (pad sites)
- Lot rent
- Park-owned homes vs. tenant-owned
- Utility billing (RUBS, sub-metering)
- Home sales income
- Infill potential

### Senior Housing
- Unit/bed count by care level
- Independent Living (IL), Assisted Living (AL), Memory Care (MC) mix
- Monthly service fees + care charges
- Acuity levels and staffing ratios
- Occupancy by care type
- Length of stay assumptions
- Entrance fee structures (if applicable)
- State licensing and regulatory requirements

---

## Appendix B: Glossary

**BOE:** Back of Envelope - quick preliminary analysis  
**DCF:** Discounted Cash Flow - present value modeling  
**DSCR:** Debt Service Coverage Ratio - NOI / debt service  
**IRR:** Internal Rate of Return - annualized return  
**LTV:** Loan-to-Value - leverage ratio  
**MSA:** Metropolitan Statistical Area  
**NOI:** Net Operating Income  
**OM:** Offering Memorandum  

---

*End of PRD*
