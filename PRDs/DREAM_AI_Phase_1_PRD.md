# DREAM AI - Phase 1 Product Requirements Document

**Product Name:** DREAM AI  
**Company:** Shieldstone Acquisitions / DREAM.AI  
**Document Type:** Phase 1 PRD (Deal Intake & Document Processing)  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 1. Overview

This PRD covers Phase 1 of DREAM AI's acquisitions intelligence workflow:

- **Deal Intake:** Manual entry or document upload to create new deals
- **Document Processing:** AI-powered extraction of key data from OMs, T-12s, rent rolls
- **Data Validation:** User review and correction of extracted data

Phase 1 establishes the entry point for all deal flow and creates the foundation for downstream analysis.

---

## 2. Goals & Success Metrics

### Goals

1. Enable rapid deal intake with minimal friction
2. Extract structured data from unstructured documents with high accuracy
3. Minimize manual data entry through intelligent extraction
4. Create a clean, validated dataset for downstream analysis
5. Support multiple document formats (PDF, Excel, images)

### Success Metrics

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| Deal creation time (manual) | <2 minutes | <1 minute | Task completion |
| Deal creation time (document upload) | <3 minutes | <2 minutes | Task completion |
| Document extraction accuracy | >85% | >92% | User corrections tracked |
| User correction rate | <15% of fields | <8% of fields | Field edits post-extraction |
| Extraction processing time | <45 seconds | <30 seconds | API response time |
| Document upload success rate | >98% | >99% | Upload failures tracked |
| Mobile completion rate | >25% | >40% | Device analytics |

---

## 3. User Flows

### 3.1 High-Level Deal Intake Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEAL INTAKE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────────────┐   │
│  │  Manual Entry  │     │ Document Upload │     │  Email Forward         │   │
│  │  (Quick Add)   │     │ (OM, T-12, RR)  │     │  (Future Phase)        │   │
│  └───────┬────────┘     └───────┬────────┘     └────────────┬───────────┘   │
│          │                      │                           │               │
│          ▼                      ▼                           ▼               │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────────────┐   │
│  │  Basic Info    │     │  AI Extraction │     │  AI Extraction         │   │
│  │  Form          │     │  Processing    │     │  Processing            │   │
│  └───────┬────────┘     └───────┬────────┘     └────────────┬───────────┘   │
│          │                      │                           │               │
│          ▼                      ▼                           ▼               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      VALIDATION & REVIEW                                 ││
│  │                                                                          ││
│  │    ┌─────────────────┐          ┌─────────────────┐                     ││
│  │    │  Review/Edit    │          │  Confidence     │                     ││
│  │    │  Extracted Data │          │  Indicators     │                     ││
│  │    └────────┬────────┘          └────────┬────────┘                     ││
│  │             │                            │                              ││
│  │             ▼                            ▼                              ││
│  │    ┌─────────────────────────────────────────────────────┐              ││
│  │    │              DEAL CREATED                            │              ││
│  │    │                                                      │              ││
│  │    │  → Ready for Screening (Phase 2)                     │              ││
│  │    │  → Documents stored and linked                       │              ││
│  │    │  → Activity logged                                   │              ││
│  │    └─────────────────────────────────────────────────────┘              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Document Upload Flow (Primary Path)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT UPLOAD FLOW                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Step 1: Upload                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Drag & drop or file picker                                           │ │
│  │  • Accepts: PDF, XLSX, XLS, PNG, JPG, DOCX                              │ │
│  │  • Max file size: 50MB per file                                         │ │
│  │  • Multiple files allowed (OM + T-12 + Rent Roll)                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  Step 2: Document Classification (AI)                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  AI automatically identifies document type:                             │ │
│  │  • Offering Memorandum (OM)                                              │ │
│  │  • Trailing 12 Operating Statement (T-12)                               │ │
│  │  • Rent Roll                                                             │ │
│  │  • Property Photo                                                        │ │
│  │  • Other / Unknown                                                       │ │
│  │                                                                          │ │
│  │  User can override classification if needed                              │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  Step 3: Data Extraction (AI)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  Parallel extraction based on document type:                            │ │
│  │                                                                          │ │
│  │  OM → Property info, asking price, unit mix, photos, highlights         │ │
│  │  T-12 → Revenue, expenses, NOI, line items                              │ │
│  │  Rent Roll → Unit details, rents, occupancy, lease terms                │ │
│  │                                                                          │ │
│  │  Each field tagged with confidence score (0-100)                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  Step 4: Validation & Review                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Low-confidence fields highlighted (yellow <80%, red <60%)            │ │
│  │  • Side-by-side view: extracted data + source document                  │ │
│  │  • User edits tracked for ML improvement                                │ │
│  │  • "Looks Good" button to confirm                                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                        │
│                                      ▼                                        │
│  Step 5: Deal Created                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Deal record created in database                                      │ │
│  │  • Documents linked to deal                                             │ │
│  │  • Automatic trigger: Screening (Phase 2) begins                        │ │
│  │  • User redirected to Deal Detail page                                  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Deal Intake Methods

### 4.1 Method A: Manual Entry (Quick Add)

For users who want to quickly log a deal without documents, or for deals where documents aren't yet available.

**Use Cases:**
- Verbal deal from broker
- Deal from CoStar/LoopNet listing (no OM yet)
- Quick logging for tracking purposes
- Mobile entry on the go

### 4.2 Method B: Document Upload

Primary intake method for deals with existing materials.

**Use Cases:**
- Broker sends OM package
- T-12 and rent roll available
- Full underwriting package received

### 4.3 Method C: Email Forward (Phase 1.5 - High Priority)

**Priority:** High - Key Differentiator

Automatic deal creation from forwarded emails to dedicated DREAM AI inbox.

**Use Cases:**
- Broker email with attachments
- Deal alerts from listing services
- Automated ingestion
- Forward to: `intake@dream.ai` (or similar)

**Implementation:**
- Email forwarding to dedicated DREAM AI inbox
- Automatic attachment extraction
- AI-powered document classification
- Deal creation from email content and attachments
- Email parsing for deal context
- Reply-to functionality for follow-up questions

**Key Differentiator:** Makes deal intake frictionless - users simply forward emails they already receive.

### 4.4 Method D: WhatsApp Integration (Phase 1.5 - High Priority)

**Priority:** High - Key Differentiator

Deal intake via WhatsApp Business API, allowing users to send deals directly from their mobile device.

**Use Cases:**
- Quick deal submission from mobile
- Broker sends deal via WhatsApp
- Photo/document sharing via WhatsApp
- Voice message transcription for deal details
- International broker communication

**Implementation:**
- WhatsApp Business API integration
- Document/image extraction from messages
- Voice message transcription (optional)
- Two-way communication for follow-up questions
- Link to web dashboard for detailed entry
- WhatsApp bot: `+1-XXX-DREAM-AI` (or similar)

**Key Differentiator:** Enables deal intake from anywhere, especially valuable for mobile-first users and international brokers.

### 4.5 Method E: Slack Integration (Phase 1.5 - High Priority)

**Priority:** High - Key Differentiator

Deal intake via Slack bot, enabling team collaboration and deal sharing within Slack workspace.

**Use Cases:**
- Team members share deals in Slack channels
- Broker sends deal via Slack DM
- Automated deal notifications to Slack
- Collaborative deal review in Slack threads
- Integration with existing team workflows

**Implementation:**
- Slack bot/app installation
- `/dream-add-deal` slash command
- File upload support (OM, T-12, Rent Roll, all document types)
- Channel notifications for new deals
- Thread-based deal discussions
- Integration with Slack workflows
- Direct message support for private deal submission

**Key Differentiator:** Seamless integration with team communication tools, enabling deal intake without leaving Slack.

### 4.6 Method F: File Storage Integrations (Phase 1.5)

**Priority:** High - Essential for Easy Document Access

Direct integration with major cloud storage providers for seamless document import.

**Supported Platforms:**
- Google Drive
- Microsoft OneDrive
- Dropbox
- Box
- Apple iCloud

**Use Cases:**
- Import documents already stored in cloud
- Bulk import from shared folders
- Automatic sync from broker-provided folders
- Access documents without manual download/upload

**Implementation:**
- OAuth authentication for each provider
- File browser interface (similar to native file picker)
- Folder selection and bulk import
- Automatic file type detection
- Progress tracking for large imports
- Available in both Dashboard and Chat modes

**User Experience:**
- "Connect Google Drive" button in upload interface
- Native file browser showing user's cloud storage
- Multi-select for bulk import
- Automatic document classification after import

### 4.7 Method G: Chat Mode Entry (Phase 1.5 - MVP Priority)

**Priority:** MVP - High Priority

Conversational deal intake through an LLM-powered chat interface. Users can interact naturally to input deal information, upload documents, or answer questions about a property.

**Use Cases:**
- Natural language deal entry ("I have a 96-unit property in Austin asking $12.5M")
- Guided data collection through conversation
- Document upload via chat ("Here's the OM for Oak Creek")
- Quick property evaluation questions
- Mobile-friendly entry method
- File storage integration within chat

**Chat Mode Features:**
- Conversational interface similar to ChatGPT/Claude
- Intelligent follow-up questions to gather required data
- Document attachment support within chat (drag & drop, file picker, cloud storage)
- Context-aware prompts based on deal type
- Seamless transition to dashboard view when complete
- File storage integrations (Google Drive, OneDrive, Dropbox, Box, iCloud)
- Real-time extraction feedback

**Note:** Chat mode serves as the primary manual entry method and alternative to traditional form-based entry, providing a more natural interaction pattern for users comfortable with LLM interfaces.

**MVP Scope (Phase 1.5):**
- Basic chat interface with text input
- File upload support (drag & drop, file picker)
- Mode toggle (Dashboard ↔ Chat)
- Simple AI responses with extracted data display
- "View in Dashboard" transition
- File storage integration (at least Google Drive + Dropbox)

---

## 5. Form Fields & Data Extraction

### 5.1 Manual Entry Form (Quick Add)

#### Section 1: Property Identification

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| Property Name | Text | Yes | 3-100 chars | — | User-friendly identifier |
| Street Address | Text | Yes | Min 5 chars | — | Full street address |
| City | Text | Yes | Min 2 chars | — | |
| State | Dropdown | Yes | US states | — | |
| ZIP Code | Text | Yes | 5 or 9 digits | — | |
| Property Type | Dropdown | Yes | See options | Multifamily | |
| Property Class | Dropdown | No | A, B, C, D | — | User estimate |
| Year Built | Number | No | 1800-current | — | |
| Number of Units | Number | Yes | 1-9999 | — | |

**Property Type Options:**
- Multifamily (default)
- Single Family
- Student Housing
- Senior Housing
- Mobile Home Park
- Mixed Use
- Other

#### Section 2: Financial Overview

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| Asking Price | Currency | No | $0-$999,999,999 | — | |
| Price Per Unit | Currency | No | Auto-calc | — | Asking ÷ Units |
| Current Occupancy | Percentage | No | 0-100% | — | |
| In-Place NOI | Currency | No | $0-$99,999,999 | — | |
| Pro Forma NOI | Currency | No | $0-$99,999,999 | — | Seller's projection |
| In-Place Cap Rate | Percentage | No | Auto-calc | — | NOI ÷ Price |

#### Section 3: Deal Source

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| Source Type | Dropdown | No | See options | Broker | |
| Source Name | Text | No | Max 100 chars | — | Broker/contact name |
| Source Company | Text | No | Max 100 chars | — | Brokerage firm |
| Source Email | Email | No | Valid email | — | |
| Source Phone | Phone | No | Valid phone | — | |
| How Received | Dropdown | No | See options | Email | |
| Market Status | Dropdown | No | See options | Listed | |

**Source Type Options:**
- Broker (default)
- Direct from Owner
- Auction
- Wholesaler
- Network/Referral
- LoopNet/CoStar
- Other

**How Received Options:**
- Email (default)
- Phone Call
- In Person
- Website/Portal
- Referral
- Other

**Market Status Options:**
- Listed (default)
- Off-Market
- Pre-Market
- Pocket Listing
- REO/Foreclosure

#### Section 4: Notes & Tags

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| Initial Notes | Textarea | No | Max 2000 chars | Free-form notes |
| Tags | Multi-select | No | User-defined | Custom tags |
| Priority | Dropdown | No | Low/Medium/High | Default: Medium |

---

### 5.2 Document Extraction: Offering Memorandum (OM)

#### Property Information Extraction

| Field | Extraction Target | Confidence Threshold | Fallback |
|-------|-------------------|---------------------|----------|
| Property Name | Title page, headers | 85% | User entry |
| Address | Property description | 90% | User entry |
| City/State/ZIP | Property description | 90% | User entry |
| Year Built | Property details table | 80% | User entry |
| Number of Units | Property details table | 90% | User entry |
| Total SF | Property details table | 80% | User entry |
| Lot Size | Property details table | 70% | Optional |
| Property Class | Description or explicit | 60% | User estimate |
| Parking Spaces | Property details | 70% | Optional |
| Amenities | Amenities section | 60% | Optional |

#### Unit Mix Extraction

| Field | Extraction Target | Confidence Threshold | Notes |
|-------|-------------------|---------------------|-------|
| Unit Type | Unit mix table | 85% | Studio, 1BR, 2BR, etc. |
| Unit Count | Unit mix table | 90% | Per unit type |
| Avg SF | Unit mix table | 80% | Per unit type |
| Market Rent | Unit mix table | 80% | Per unit type |
| In-Place Rent | Unit mix table | 80% | Per unit type |

#### Financial Extraction

| Field | Extraction Target | Confidence Threshold | Notes |
|-------|-------------------|---------------------|-------|
| Asking Price | Executive summary, pricing | 95% | Critical field |
| Price Per Unit | Calculated or explicit | 90% | |
| In-Place NOI | Financial summary | 85% | |
| Pro Forma NOI | Financial summary | 85% | |
| In-Place Cap Rate | Financial summary | 85% | |
| Pro Forma Cap Rate | Financial summary | 85% | |
| Gross Potential Rent | Financial summary | 80% | |
| Effective Gross Income | Financial summary | 80% | |
| Operating Expenses | Financial summary | 80% | |

#### Seller Highlights Extraction

| Field | Extraction Target | Notes |
|-------|-------------------|-------|
| Investment Highlights | Bullet points, executive summary | Top 5-10 selling points |
| Value-Add Opportunities | Dedicated section | Renovation potential |
| Location Highlights | Location section | Nearby amenities, employers |
| Market Overview | Market section | Key market stats |

---

### 5.3 Document Extraction: Trailing 12 (T-12)

#### Revenue Line Items

| Field | Extraction Target | Validation | Notes |
|-------|-------------------|------------|-------|
| Gross Potential Rent | Revenue section | > $0 | Monthly × 12 if monthly |
| Loss to Lease | Revenue section | ≥ $0 | |
| Vacancy Loss | Revenue section | ≥ $0 | |
| Concessions | Revenue section | ≥ $0 | |
| Bad Debt | Revenue section | ≥ $0 | |
| Net Rental Income | Calculated | | GPR - losses |
| Other Income | Revenue section | ≥ $0 | Itemized if available |
| Utility Reimbursement | Revenue section | ≥ $0 | |
| Fee Income | Revenue section | ≥ $0 | App fees, late fees, etc. |
| **Effective Gross Income** | Calculated or explicit | | Total revenue |

#### Expense Line Items

| Field | Extraction Target | Per Unit Benchmark | Notes |
|-------|-------------------|-------------------|-------|
| Property Taxes | Expense section | Varies by market | |
| Insurance | Expense section | $400-800/unit | |
| Utilities | Expense section | $600-1,500/unit | Gas, electric, water, trash |
| Repairs & Maintenance | Expense section | $500-1,000/unit | |
| Contract Services | Expense section | $200-500/unit | Landscaping, pest, etc. |
| Payroll | Expense section | $800-1,500/unit | On-site staff |
| Management Fee | Expense section | 3-5% of EGI | |
| Administrative | Expense section | $100-300/unit | |
| Marketing | Expense section | $50-200/unit | |
| Professional Fees | Expense section | $50-150/unit | Legal, accounting |
| Turnover Costs | Expense section | $200-500/unit | |
| Replacement Reserves | Expense section | $250-350/unit | If included |
| **Total Operating Expenses** | Calculated or explicit | | |

#### Calculated Metrics

| Field | Calculation | Notes |
|-------|-------------|-------|
| Net Operating Income | EGI - Total OpEx | Critical metric |
| Expense Ratio | Total OpEx ÷ EGI | Varies by deal type (see notes) |
| Per Unit Revenue | EGI ÷ Units | |
| Per Unit Expenses | OpEx ÷ Units | |
| Per Unit NOI | NOI ÷ Units | |

**Expense Ratio Benchmarks by Deal Type:**
- **Build-to-Rent (BTR)**: Typically 20-30% (newer properties, lower maintenance)
- **Value-Add**: Typically 40-50% (renovation needs, higher turnover)
- **Distressed**: Often 50%+ (deferred maintenance, high vacancy)
- **Stabilized Class A/B**: Typically 35-45% (market dependent)
- **Stabilized Class C/D**: Typically 45-55% (higher maintenance needs)

**Note:** System should not apply default expense ratio assumptions. Each deal should be evaluated based on its specific characteristics and deal type.

---

### 5.4 Document Extraction: Rent Roll

#### Unit-Level Data

| Field | Extraction Target | Validation | Notes |
|-------|-------------------|------------|-------|
| Unit Number | First column typically | Unique | |
| Unit Type | Type column | Valid type | Studio, 1BR, 2BR, etc. |
| Square Footage | SF column | 200-3000 | |
| Bedrooms | Derived or explicit | 0-5 | |
| Bathrooms | Derived or explicit | 1-4 | |
| Current Rent | Rent column | $0-$10,000 | |
| Market Rent | Market column | $0-$10,000 | If available |
| Lease Start | Date column | Valid date | |
| Lease End | Date column | Valid date | After start |
| Move-In Date | Date column | Valid date | |
| Tenant Name | Name column | — | Optional, privacy |
| Status | Status column | Occupied/Vacant | |
| Deposit | Deposit column | ≥ $0 | |
| Balance Due | Balance column | ≥ $0 | Delinquency indicator |

#### Aggregated Metrics (Calculated)

| Metric | Calculation | Notes |
|--------|-------------|-------|
| Total Units | Count of rows | |
| Occupied Units | Count where status = Occupied | |
| Vacant Units | Count where status = Vacant | |
| Occupancy Rate | Occupied ÷ Total | |
| Total In-Place Rent | Sum of current rents | Monthly |
| Average Rent | Total rent ÷ Occupied units | |
| Average SF | Total SF ÷ Total units | |
| Rent PSF | Average rent ÷ Average SF | |
| Total Market Rent | Sum of market rents | If available |
| Loss to Lease | Market rent - In-place rent | |
| Loss to Lease % | LTL ÷ Market rent | |
| Avg Lease Term Remaining | Avg months to expiration | |
| Delinquency Rate | Units with balance ÷ Occupied | |

---

### 5.5 Document Extraction: Third-Party Reports (Due Diligence)

During the due diligence process, users may upload additional third-party reports that provide critical insights for underwriting. These documents require sophisticated extraction and are priced accordingly.

#### Document Types & Extraction Targets

| Document Type | Key Extraction Targets | Complexity | Cost Tier |
|---------------|----------------------|------------|-----------|
| **Prior Appraisal** | Valuation, comparables, assumptions, date | Medium | Standard |
| **Engineering Report** | Structural issues, MEP systems, building condition, recommendations | High | Premium |
| **Original Plans/Specs** | Building specifications, unit layouts, construction details, materials | Very High | Premium |
| **Construction Budget** | Cost breakdown, line items, contingencies, timeline | Medium | Standard |
| **Permits** | Permit numbers, dates, scope of work, status | Low | Standard |
| **Environmental Report (Phase I/II)** | Environmental risks, remediation needs, compliance status | High | Premium |
| **Market Study** | Market trends, demographics, comparable properties, forecasts | Medium | Standard |

#### Extraction Workflow for Third-Party Reports

1. **Document Upload**: User uploads third-party report to existing deal (during due diligence)
2. **Classification**: AI identifies document type and complexity
3. **Router Decision**: System selects appropriate LLM model (Flash vs Haiku) based on complexity
4. **Extraction**: Key insights extracted with confidence scores
5. **Impact Analysis**: Extracted data automatically updates underwriting assumptions
6. **User Review**: User reviews extracted insights and confirms impact on deal analysis

#### Impact on Underwriting

When third-party reports are uploaded and processed:

- **Automatic Updates**: Key metrics and assumptions updated in underwriting model
- **Risk Flags**: System flags potential issues (e.g., structural problems, environmental concerns)
- **Cost Adjustments**: Construction budgets and CapEx needs automatically incorporated
- **Valuation Impact**: Prior appraisals inform valuation assumptions
- **Timeline Adjustments**: Permit and construction timelines affect deal timeline
- **Confidence Scoring**: Each extracted insight tagged with confidence level

**Example Flow:**
```
User uploads Engineering Report → 
System extracts: "Foundation issues identified, $250K remediation needed" →
Underwriting automatically updates:
  - CapEx reserve: +$250K
  - Risk score: Increased
  - Deal timeline: Extended by 3 months
  - User notified: "Engineering report findings may impact deal viability"
```

#### Cost Considerations

**Pricing Strategy:**
- **Standard Documents** (OM, T-12, Rent Roll): Included in base subscription
- **Third-Party Reports**: 
  - Option 1: Per-document pricing ($5-20 per document based on complexity)
  - Option 2: Included in premium subscription tiers
  - Option 3: Credit-based system (e.g., 10 credits per month, 1 credit = 1 standard doc, 3 credits = 1 complex report)

**Cost Recovery:**
- Premium extraction for complex documents requires higher-cost LLM models
- Engineering reports, plans, and specs require Claude Haiku (3-5x cost)
- System should clearly communicate costs before processing
- Users can choose to process now or upgrade subscription

---

## 6. AI Extraction Pipeline

### 6.1 LLM Routing for Extraction

**Intelligent Router Function:**

The system uses an intelligent router to select the optimal LLM model based on document complexity and task requirements.

**Router Logic:**

| Task Complexity | Document Type | Model Selection | Reasoning |
|----------------|---------------|-----------------|-----------|
| **Simple** | Classification, basic extraction | Gemini 1.5 Flash | 70% cost savings, sufficient quality |
| **Standard** | OM, T-12, Rent Roll (typical) | Gemini 1.5 Flash | Cost-effective for structured data |
| **Complex** | Large OMs (>50 pages), multi-doc | Claude 3.5 Haiku | Better context handling |
| **Very Complex** | Engineering reports, plans, specs | Claude 3.5 Haiku | Higher accuracy needed |
| **Edge Cases** | Poor quality scans, unusual formats | Claude 3.5 Haiku | Better error handling |

**Router Decision Factors:**
1. **Document Type**: Simple docs (T-12, Rent Roll) → Flash; Complex docs (OM, reports) → Haiku
2. **Document Size**: <20 pages → Flash; >20 pages → Haiku
3. **Image Quality**: High quality → Flash; Low quality → Haiku
4. **Extraction Confidence**: Low confidence on first pass → Upgrade to Haiku
5. **User Tier**: Premium users → Default to Haiku; Standard users → Router decides

**Primary Model Selection:**

| Task | Default Model | Fallback Model | Estimated Cost | Reasoning |
|------|---------------|----------------|----------------|-----------|
| Document Classification | Gemini 1.5 Flash | Claude 3.5 Haiku | $0.0005 | Simple pattern matching |
| OM Data Extraction (simple) | Gemini 1.5 Flash | Claude 3.5 Haiku | $0.005 | Standard OMs |
| OM Data Extraction (complex) | Claude 3.5 Haiku | Gemini 1.5 Pro | $0.015 | Large/complex OMs |
| T-12 Data Extraction | Gemini 1.5 Flash | Claude 3.5 Haiku | $0.003 | Tabular data |
| Rent Roll Extraction | Gemini 1.5 Flash | Claude 3.5 Haiku | $0.003 | Tabular data |
| Third-Party Reports | Claude 3.5 Haiku | Gemini 1.5 Pro | $0.020-0.050 | Complex extraction (see cost tiers) |
| Photo Extraction | Vision model | — | $0.005 | Image processing |
| Confidence Scoring | Python | — | $0.000 | Rule-based |
| **Total per Deal (Standard)** | | | **~$0.015-0.025** | 40-50% cost reduction |
| **Total per Deal (Complex)** | | | **~$0.05-0.10** | Includes third-party reports |

**Model Cost Comparison:**

| Model | Input Cost | Output Cost | Best For | Notes |
|-------|------------|-------------|----------|-------|
| **Gemini 1.5 Flash** (Primary) | $0.075/M tokens | $0.30/M tokens | Standard extraction | 70% cost reduction, good for structured data |
| **Claude 3.5 Haiku** (Complex) | $0.25/M tokens | $1.25/M tokens | Complex documents | Better context handling |
| **Gemini 1.5 Pro** (Fallback) | $1.25/M tokens | $5/M tokens | Very complex docs | Higher quality, 4x cost |
| **Claude 3.5 Sonnet** (Premium) | $3/M tokens | $15/M tokens | Edge cases | Premium option, 12x cost |

**Cost Tiers for Third-Party Reports:**

Third-party reports (engineering, plans, specs, etc.) require more sophisticated extraction and are priced accordingly:

| Document Type | Complexity | Model | Estimated Cost | Notes |
|---------------|------------|-------|----------------|-------|
| Prior Appraisal | Medium | Gemini Flash | $0.010 | Structured format |
| Engineering Report | High | Claude Haiku | $0.030 | Technical language |
| Original Plans/Specs | Very High | Claude Haiku | $0.050 | Image-heavy, technical |
| Construction Budget | Medium | Gemini Flash | $0.010 | Tabular data |
| Permits | Low | Gemini Flash | $0.005 | Simple extraction |
| Environmental Report | High | Claude Haiku | $0.025 | Technical content |

**Cost Recovery Strategy:**

- **Standard Documents** (OM, T-12, Rent Roll): Included in base subscription
- **Third-Party Reports**: Additional cost per document or included in premium tiers
- **Bulk Processing**: Volume discounts for multiple documents
- **Enterprise**: Unlimited processing included

**Recommendation:**
- **Default**: Gemini 1.5 Flash for standard documents (70% cost savings)
- **Router**: Automatically upgrade to Claude 3.5 Haiku for complex documents
- **Premium Users**: Option to force Haiku for all documents
- **A/B Testing**: Monitor extraction quality and adjust router thresholds

### 6.2 Extraction Prompt Templates

#### Document Classification Prompt

```
You are a document classifier for commercial real estate acquisitions.

Analyze the provided document and classify it as one of:
- OFFERING_MEMORANDUM: Marketing package with property details, financials, photos
- T12_OPERATING_STATEMENT: Trailing 12-month income/expense statement
- RENT_ROLL: Unit-by-unit listing of tenants, rents, lease terms
- LEASING_REPORT: Leasing activity, lease expirations, renewal rates
- CONCESSIONS_REPORT: Concession details, move-in specials, rent discounts
- AGED_RECEIVABLES: Outstanding tenant balances, delinquency report
- CAPITAL_EXPENDITURE_REPORT: CapEx history, planned improvements, reserve analysis
- LOAN_DOCUMENTS: Loan terms, mortgage statements, debt service details
- PROPERTY_PHOTO: Image of the property
- SITE_PLAN: Property layout, building footprint, parking
- FLOOR_PLAN: Unit layouts, building floor plans
- INSPECTION_REPORT: Property condition assessment, inspection findings
- APPRAISAL: Third-party property valuation
- PRIOR_APPRAISAL: Historical appraisal reports from previous transactions
- MARKET_STUDY: Market analysis, comparable properties, demographics
- ENVIRONMENTAL_REPORT: Phase I/II environmental assessments
- TITLE_REPORT: Title insurance, encumbrances, easements
- ORIGINAL_PLANS: Original architectural/construction plans and specifications
- CONSTRUCTION_BUDGET: Construction cost breakdown, budget estimates
- PERMITS: Building permits, zoning permits, construction permits
- ENGINEERING_REPORT: Structural engineering, MEP reports, building systems analysis
- OTHER: Any other document type

Respond with JSON:
{
  "document_type": "OFFERING_MEMORANDUM",
  "confidence": 95,
  "reasoning": "Document contains property marketing language, unit mix, and financial projections"
}
```

#### OM Extraction Prompt

```
You are a data extraction specialist for commercial real estate underwriting.

Extract the following information from this Offering Memorandum. For each field, provide:
- The extracted value
- A confidence score (0-100)
- The page/location where you found it

If a field is not found, set value to null and confidence to 0.

Required fields:
1. Property Name
2. Street Address
3. City, State, ZIP
4. Year Built
5. Number of Units
6. Asking Price
7. In-Place NOI
8. Pro Forma NOI
9. Unit Mix (array of: type, count, avg_sf, market_rent)
10. Investment Highlights (array of bullet points)

Respond with JSON matching this schema:
{
  "property_name": {"value": "...", "confidence": 95, "source": "Page 1"},
  "address": {"value": "...", "confidence": 90, "source": "Page 2"},
  ...
}
```

#### T-12 Extraction Prompt

```
You are a financial data extraction specialist for commercial real estate.

Extract the Trailing 12 operating statement from this document. Identify:

REVENUE:
- Gross Potential Rent
- Loss to Lease
- Vacancy Loss
- Concessions
- Bad Debt
- Other Income (itemized)
- Effective Gross Income

EXPENSES:
- Property Taxes
- Insurance
- Utilities (itemized if possible)
- Repairs & Maintenance
- Contract Services
- Payroll
- Management Fee
- Administrative
- Marketing
- Professional Fees
- Other Expenses (itemized)
- Total Operating Expenses

CALCULATED:
- Net Operating Income

For each line item, provide:
- Annual amount
- Monthly amount (if shown)
- Per unit amount (if calculable)
- Confidence score

Respond with structured JSON.
```

### 6.3 Confidence Scoring Rules

| Confidence Level | Score Range | UI Treatment | User Action |
|------------------|-------------|--------------|-------------|
| High | 90-100 | Green checkmark | Optional review |
| Medium | 70-89 | Yellow highlight | Review recommended |
| Low | 50-69 | Orange highlight | Review required |
| Very Low | 0-49 | Red highlight | Manual entry required |

**Confidence Calculation Factors:**
- LLM-reported confidence (50% weight)
- Cross-document validation (20% weight)
- Benchmark reasonableness (15% weight)
- Field completeness (15% weight)

---

## 7. Data Validation Rules

### 7.1 Field-Level Validation

| Field | Validation Rule | Error Message |
|-------|-----------------|---------------|
| Units | Must be > 0 | "Number of units is required" |
| Year Built | 1800 ≤ year ≤ current year | "Year built must be valid" |
| Asking Price | Must be > 0 if provided | "Invalid asking price" |
| Occupancy | 0% ≤ value ≤ 100% | "Occupancy must be 0-100%" |
| Cap Rate | 0% < value < 20% | "Cap rate seems unusual, please verify" |
| NOI | NOI < Asking Price | "NOI exceeds asking price" |
| Expense Ratio | No default validation | "Expense ratio varies by deal type (BTR: 20-30%, Value-Add: 40-50%, Distressed: 50%+)" |

### 7.2 Cross-Field Validation

| Validation | Rule | Warning Level |
|------------|------|---------------|
| NOI Consistency | T-12 NOI ≈ OM NOI (±10%) | Warning |
| Unit Count Match | Rent roll units = OM units | Error |
| Rent Consistency | Rent roll total ≈ T-12 GPR (±5%) | Warning |
| Occupancy Match | Rent roll occupancy ≈ OM occupancy (±5%) | Warning |
| Price Per Unit | $50K < PPU < $500K (market-dependent) | Warning |

### 7.3 Reasonableness Checks (Shieldstone-Based)

| Metric | Reasonable Range | Red Flag Threshold |
|--------|------------------|-------------------|
| Price Per Unit | $50K - $400K | < $30K or > $500K |
| Rent Per Unit | $500 - $3,000 | < $400 or > $4,000 |
| Expense Ratio | Varies by deal type | See deal-type benchmarks in Section 5.3 |
| Cap Rate | 4% - 10% | < 3% or > 12% |
| Occupancy | 85% - 98% | < 80% |
| Property Tax/Unit | $500 - $3,000 | < $300 or > $5,000 |
| Insurance/Unit | $300 - $800 | < $200 or > $1,200 |

---

## 8. User Interface Specifications

### 8.0 Dual-Mode Login Interface

**Overview:** Upon login, users can choose between two interface modes based on their workflow preference. Both modes support all document upload methods including file storage integrations.

#### 8.0.1 Dashboard Mode (Default)

The traditional dashboard view showing:
- Pipeline overview
- Recent deals
- Key metrics and KPIs
- Quick actions (Upload Deal, Market Watch, etc.)
- Navigation to all features
- **File Storage Integrations**: Connect Google Drive, OneDrive, Dropbox, Box, iCloud for easy document import

**Use Cases:**
- Users who prefer visual overview
- Power users managing multiple deals
- Team leads monitoring pipeline
- Users who want quick access to all features

**Document Upload Options:**
- Drag & drop files
- File picker
- **Cloud storage integrations** (Google Drive, OneDrive, Dropbox, Box, iCloud)
- Email forward (intake@dream.ai)
- WhatsApp bot
- Slack bot

#### 8.0.2 Chat Mode (Phase 1.5 MVP - High Priority)

A conversational interface similar to ChatGPT/Claude, allowing:
- Natural language deal entry
- Document upload via chat
- Guided data collection through conversation
- Property evaluation questions
- Seamless transition to structured views when needed
- **File storage integrations** within chat interface

**Chat Mode Features:**
- Clean, minimal chat interface (message bubbles)
- File attachment support:
  - Drag & drop files
  - File picker
  - **Cloud storage integrations** (Google Drive, OneDrive, Dropbox, Box, iCloud)
  - Paste images
- Context-aware follow-up questions
- Real-time validation and suggestions
- Ability to switch to dashboard view at any time
- Mobile-optimized for on-the-go entry
- Due diligence document uploads (third-party reports)

**Example Chat Flow:**
```
User: "I have a 96-unit property in Austin asking $12.5M"
AI: "Great! Let me help you evaluate this deal. What's the property name?"
User: "Oak Creek Apartments"
AI: "Thanks. Can you share the address?"
User: [uploads OM.pdf from Google Drive]
AI: "I've extracted the key information from the OM. Here's what I found:
     - Address: 1234 Oak Creek Dr, Austin, TX 78701
     - Units: 96
     - Asking Price: $12,500,000
     - Year Built: 1985
     
     Would you like me to pull the T-12 and rent roll, or do you have those documents?"
User: [connects Dropbox and selects T-12.xlsx]
AI: "Perfect! I've extracted the T-12 data. Now let's review the key metrics..."
```

**Implementation Notes:**
- Mode preference stored in user settings
- Users can switch modes at any time via header toggle
- Chat mode serves as the primary manual entry method (Phase 1.5 MVP)
- Dashboard mode remains the default for existing users
- Both modes access the same underlying data and features
- **File storage integrations available in both modes** for maximum convenience

### 8.1 Deal Intake Page

**URL:** `/deals/new`

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DREAM AI                                              [User Menu] [Logout] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  New Deal                                                                ││
│  │                                                                          ││
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐       ││
│  │  │                             │  │                             │       ││
│  │  │   📄 Upload Documents       │  │   ✏️ Quick Add              │       ││
│  │  │                             │  │                             │       ││
│  │  │   Drop OM, T-12, Rent Roll  │  │   Enter basic info manually │       ││
│  │  │   for automatic extraction  │  │   for quick tracking        │       ││
│  │  │                             │  │                             │       ││
│  │  └─────────────────────────────┘  └─────────────────────────────┘       ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Document Upload Interface

**Component:** Drag-and-drop zone with file picker fallback

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │                        ┌─────────────────┐                               ││
│  │                        │   📁            │                               ││
│  │                        │                 │                               ││
│  │                        └─────────────────┘                               ││
│  │                                                                          ││
│  │              Drag and drop files here, or click to browse                ││
│  │                                                                          ││
│  │              Supported: PDF, XLSX, XLS, PNG, JPG, DOCX                   ││
│  │              Max file size: 50MB                                         ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Uploaded Files:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📄 Oak_Creek_OM.pdf          │ Offering Memorandum ▼ │  ✓  │  🗑️      ││
│  │  📊 Oak_Creek_T12.xlsx        │ T-12 Statement ▼      │  ✓  │  🗑️      ││
│  │  📊 Oak_Creek_RentRoll.xlsx   │ Rent Roll ▼           │  ✓  │  🗑️      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│                                      [Cancel]  [Extract Data →]             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Extraction Review Interface

**Layout:** Split view with source document on left, extracted data on right

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Review Extracted Data                                    [Back] [Confirm]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │                             │  │                                     │   │
│  │  [PDF Viewer]               │  │  Property Information               │   │
│  │                             │  │  ─────────────────────              │   │
│  │  Oak_Creek_OM.pdf           │  │                                     │   │
│  │                             │  │  Property Name                      │   │
│  │  Page 1 of 24               │  │  ┌─────────────────────────────┐   │   │
│  │                             │  │  │ Oak Creek Apartments    ✓   │   │   │
│  │  ┌───────────────────────┐  │  │  └─────────────────────────────┘   │   │
│  │  │                       │  │  │                                     │   │
│  │  │   [Document Preview]  │  │  │  Address                            │   │
│  │  │                       │  │  │  ┌─────────────────────────────┐   │   │
│  │  │                       │  │  │  │ 1234 Oak Creek Dr       ✓   │   │   │
│  │  │                       │  │  │  └─────────────────────────────┘   │   │
│  │  │                       │  │  │                                     │   │
│  │  │                       │  │  │  Asking Price                       │   │
│  │  │                       │  │  │  ┌─────────────────────────────┐   │   │
│  │  │                       │  │  │  │ $12,500,000             ✓   │   │   │
│  │  │                       │  │  │  └─────────────────────────────┘   │   │
│  │  │                       │  │  │                                     │   │
│  │  │                       │  │  │  Units        Year Built            │   │
│  │  │                       │  │  │  ┌─────────┐  ┌─────────────────┐  │   │
│  │  │                       │  │  │  │ 96  ✓   │  │ 1985        ⚠️  │  │   │
│  │  │                       │  │  │  └─────────┘  └─────────────────┘  │   │
│  │  └───────────────────────┘  │  │  (Low confidence - please verify)  │   │
│  │                             │  │                                     │   │
│  │  [◀ Prev] [Next ▶]          │  │  [Show All Fields ▼]               │   │
│  │                             │  │                                     │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                              │
│  Extraction Summary: 24 fields extracted, 2 need review                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Confidence Indicators

**Visual Design:**

| Confidence | Icon | Color | Border |
|------------|------|-------|--------|
| High (90+) | ✓ | Green (#22C55E) | None |
| Medium (70-89) | ⚠️ | Yellow (#EAB308) | Yellow dashed |
| Low (50-69) | ⚠️ | Orange (#F97316) | Orange solid |
| Very Low (<50) | ❌ | Red (#EF4444) | Red solid |

---

## 9. API Specifications

### 9.1 Deal Endpoints

#### Create Deal (Manual Entry)

```
POST /api/v1/deals

Request Body:
{
  "property_name": "Oak Creek Apartments",
  "address": {
    "street": "1234 Oak Creek Dr",
    "city": "Austin",
    "state": "TX",
    "zip": "78701"
  },
  "property_type": "MULTIFAMILY",
  "units": 96,
  "year_built": 1985,
  "asking_price": 12500000,
  "occupancy": 0.94,
  "noi_in_place": 875000,
  "source": {
    "type": "BROKER",
    "name": "John Smith",
    "company": "CBRE",
    "email": "jsmith@cbre.com"
  },
  "notes": "Value-add opportunity, interiors need updating",
  "tags": ["value-add", "austin"],
  "priority": "HIGH"
}

Response (201 Created):
{
  "id": "deal_abc123",
  "created_at": "2025-12-20T10:30:00Z",
  "status": "NEW",
  "property_name": "Oak Creek Apartments",
  ...
}
```

#### Upload Documents

```
POST /api/v1/deals/{deal_id}/documents

Content-Type: multipart/form-data

Request:
- files[]: (binary) - One or more files
- document_types[]: (optional) - Pre-specified types

Response (202 Accepted):
{
  "upload_id": "upload_xyz789",
  "documents": [
    {
      "id": "doc_001",
      "filename": "Oak_Creek_OM.pdf",
      "size_bytes": 15234567,
      "status": "PROCESSING",
      "document_type": null  // Will be classified
    }
  ],
  "extraction_job_id": "job_ext123"
}
```

#### Get Extraction Status

```
GET /api/v1/extraction-jobs/{job_id}

Response (200 OK):
{
  "job_id": "job_ext123",
  "status": "COMPLETED",  // PENDING, PROCESSING, COMPLETED, FAILED
  "started_at": "2025-12-20T10:30:05Z",
  "completed_at": "2025-12-20T10:30:35Z",
  "documents": [
    {
      "id": "doc_001",
      "document_type": "OFFERING_MEMORANDUM",
      "classification_confidence": 98,
      "extraction_status": "COMPLETED"
    }
  ],
  "extracted_data": {
    "property_name": {"value": "Oak Creek Apartments", "confidence": 95},
    "address": {"value": "1234 Oak Creek Dr, Austin, TX 78701", "confidence": 92},
    ...
  },
  "fields_requiring_review": ["year_built", "property_class"],
  "overall_confidence": 87
}
```

#### Confirm Extraction

```
POST /api/v1/deals/{deal_id}/confirm-extraction

Request Body:
{
  "corrections": {
    "year_built": 1986,  // User corrected from 1985
    "property_class": "B"  // User added
  },
  "confirmed": true
}

Response (200 OK):
{
  "deal_id": "deal_abc123",
  "status": "READY_FOR_SCREENING",
  "corrections_applied": 2,
  "next_step": "screening"
}
```

### 9.2 Document Endpoints

#### Get Document

```
GET /api/v1/documents/{document_id}

Response (200 OK):
{
  "id": "doc_001",
  "deal_id": "deal_abc123",
  "filename": "Oak_Creek_OM.pdf",
  "document_type": "OFFERING_MEMORANDUM",
  "size_bytes": 15234567,
  "mime_type": "application/pdf",
  "upload_date": "2025-12-20T10:30:00Z",
  "storage_url": "https://storage.dreamai.com/...",
  "extraction_data": {...},
  "pages": 24
}
```

#### Get Document Preview

```
GET /api/v1/documents/{document_id}/preview?page=1

Response (200 OK):
{
  "page": 1,
  "total_pages": 24,
  "image_url": "https://storage.dreamai.com/previews/...",
  "text_content": "Oak Creek Apartments - Investment Offering..."
}
```

---

## 10. Database Schema

### 10.1 Core Tables

```sql
-- Deals table
CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Property identification
    property_name VARCHAR(200) NOT NULL,
    address_street VARCHAR(200),
    address_city VARCHAR(100),
    address_state CHAR(2),
    address_zip VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Property characteristics
    property_type property_type_enum DEFAULT 'MULTIFAMILY',
    property_class property_class_enum,
    year_built INTEGER,
    units INTEGER,
    total_sf INTEGER,
    lot_size_acres DECIMAL(10, 2),
    parking_spaces INTEGER,
    
    -- Financial overview
    asking_price DECIMAL(15, 2),
    price_per_unit DECIMAL(12, 2) GENERATED ALWAYS AS (
        CASE WHEN units > 0 THEN asking_price / units END
    ) STORED,
    occupancy DECIMAL(5, 4),
    noi_in_place DECIMAL(15, 2),
    noi_pro_forma DECIMAL(15, 2),
    cap_rate_in_place DECIMAL(5, 4) GENERATED ALWAYS AS (
        CASE WHEN asking_price > 0 THEN noi_in_place / asking_price END
    ) STORED,
    
    -- Source information
    source_type source_type_enum DEFAULT 'BROKER',
    source_name VARCHAR(200),
    source_company VARCHAR(200),
    source_email VARCHAR(200),
    source_phone VARCHAR(20),
    how_received how_received_enum DEFAULT 'EMAIL',
    market_status market_status_enum DEFAULT 'LISTED',
    
    -- Workflow
    stage deal_stage_enum DEFAULT 'NEW',
    priority priority_enum DEFAULT 'MEDIUM',
    assigned_to UUID REFERENCES users(id),
    
    -- Metadata
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT valid_units CHECK (units IS NULL OR units > 0),
    CONSTRAINT valid_year CHECK (year_built IS NULL OR (year_built >= 1800 AND year_built <= EXTRACT(YEAR FROM NOW()))),
    CONSTRAINT valid_occupancy CHECK (occupancy IS NULL OR (occupancy >= 0 AND occupancy <= 1))
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id),
    
    -- File info
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    storage_provider storage_provider_enum DEFAULT 'S3',
    
    -- Classification
    document_type document_type_enum,
    classification_confidence INTEGER,
    classification_model VARCHAR(50),
    
    -- Processing status
    processing_status processing_status_enum DEFAULT 'PENDING',
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processing_error TEXT,
    
    -- Extraction
    extraction_data JSONB,
    extraction_confidence INTEGER,
    page_count INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_size CHECK (size_bytes > 0 AND size_bytes <= 52428800)  -- 50MB
);

-- Extraction jobs table
CREATE TABLE extraction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    -- Status
    status extraction_job_status_enum DEFAULT 'PENDING',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- Results
    extracted_data JSONB,
    fields_requiring_review TEXT[],
    overall_confidence INTEGER,
    
    -- Cost tracking
    llm_tokens_used INTEGER,
    llm_cost_cents INTEGER,
    llm_model VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User corrections tracking (for ML improvement)
CREATE TABLE extraction_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_job_id UUID NOT NULL REFERENCES extraction_jobs(id),
    document_id UUID NOT NULL REFERENCES documents(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Correction details
    field_name VARCHAR(100) NOT NULL,
    original_value TEXT,
    corrected_value TEXT NOT NULL,
    original_confidence INTEGER,
    
    -- Context for ML training
    document_type document_type_enum,
    page_number INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_deals_org ON deals(organization_id);
CREATE INDEX idx_deals_stage ON deals(stage);
CREATE INDEX idx_deals_created ON deals(created_at DESC);
CREATE INDEX idx_deals_address ON deals(address_city, address_state);
CREATE INDEX idx_documents_deal ON documents(deal_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_extraction_jobs_deal ON extraction_jobs(deal_id);
CREATE INDEX idx_extraction_jobs_status ON extraction_jobs(status);
```

### 10.2 Enums

```sql
CREATE TYPE property_type_enum AS ENUM (
    'MULTIFAMILY', 'SINGLE_FAMILY', 'STUDENT_HOUSING', 
    'SENIOR_HOUSING', 'MOBILE_HOME_PARK', 'MIXED_USE', 'OTHER'
);

CREATE TYPE property_class_enum AS ENUM ('A', 'B', 'C', 'D');

CREATE TYPE source_type_enum AS ENUM (
    'BROKER', 'DIRECT_OWNER', 'AUCTION', 'WHOLESALER', 
    'NETWORK', 'LOOPNET_COSTAR', 'OTHER'
);

CREATE TYPE how_received_enum AS ENUM (
    'EMAIL', 'PHONE', 'IN_PERSON', 'WEBSITE', 'REFERRAL', 'OTHER'
);

CREATE TYPE market_status_enum AS ENUM (
    'LISTED', 'OFF_MARKET', 'PRE_MARKET', 'POCKET_LISTING', 'REO'
);

CREATE TYPE deal_stage_enum AS ENUM (
    'NEW', 'SCREENING', 'BOE_ANALYSIS', 'FULL_UW', 
    'LOI', 'DUE_DILIGENCE', 'CLOSING', 'CLOSED', 'PASSED', 'DEAD'
);

CREATE TYPE priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');

CREATE TYPE document_type_enum AS ENUM (
    'OFFERING_MEMORANDUM', 'T12_STATEMENT', 'RENT_ROLL', 
    'LEASING_REPORT', 'CONCESSIONS_REPORT', 'AGED_RECEIVABLES',
    'CAPITAL_EXPENDITURE_REPORT', 'LOAN_DOCUMENTS',
    'PROPERTY_PHOTO', 'SITE_PLAN', 'FLOOR_PLAN', 
    'INSPECTION_REPORT', 'APPRAISAL', 'PRIOR_APPRAISAL',
    'MARKET_STUDY', 'ENVIRONMENTAL_REPORT', 'TITLE_REPORT',
    'ORIGINAL_PLANS', 'CONSTRUCTION_BUDGET', 'PERMITS',
    'ENGINEERING_REPORT', 'OTHER'
);

CREATE TYPE processing_status_enum AS ENUM (
    'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'
);

CREATE TYPE extraction_job_status_enum AS ENUM (
    'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED'
);

CREATE TYPE storage_provider_enum AS ENUM ('S3', 'GCS', 'LOCAL');
```

---

## 11. Error Handling

### 11.1 User-Facing Errors

| Error Code | Message | User Action |
|------------|---------|-------------|
| UPLOAD_TOO_LARGE | "File exceeds 50MB limit" | Reduce file size |
| UPLOAD_INVALID_TYPE | "Unsupported file type" | Use PDF, XLSX, etc. |
| UPLOAD_FAILED | "Upload failed, please try again" | Retry upload |
| EXTRACTION_FAILED | "Unable to extract data from document" | Try different doc or manual entry |
| EXTRACTION_TIMEOUT | "Processing taking longer than expected" | Wait or retry |
| VALIDATION_FAILED | "Please correct highlighted fields" | Fix validation errors |

### 11.2 System Errors

| Error | Handling | Monitoring |
|-------|----------|------------|
| LLM API failure | Retry 3x with backoff, then fail gracefully | Alert on 3+ failures |
| Storage failure | Retry, fallback to secondary provider | Alert immediately |
| Database timeout | Retry with exponential backoff | Alert on pattern |
| Memory overflow (large PDF) | Chunk processing, limit page count | Log and alert |

---

## 12. Testing Requirements

### 12.1 Unit Tests

| Component | Test Cases |
|-----------|------------|
| Document classifier | Correctly identifies OM, T-12, Rent Roll, Photos |
| Extraction parser | Handles various OM formats, messy data |
| Validation rules | All field validations, cross-field checks |
| Confidence scoring | Accurate scoring based on factors |

### 12.2 Integration Tests

| Flow | Test Cases |
|------|------------|
| Manual entry | Create deal with all fields, partial fields, validation errors |
| Document upload | Single file, multiple files, large files, invalid files |
| Extraction pipeline | End-to-end extraction, correction flow |
| API endpoints | All CRUD operations, error responses |

### 12.3 E2E Tests

| Scenario | Steps |
|----------|-------|
| Happy path - Upload | Upload OM → Extract → Review → Confirm → Deal created |
| Happy path - Manual | Fill form → Submit → Deal created |
| Error recovery | Upload fails → Retry → Success |
| Correction flow | Low confidence → User corrects → Confirm |

### 12.4 Performance Tests

| Metric | Target |
|--------|--------|
| Upload (50MB file) | < 10 seconds |
| Extraction (24-page OM) | < 45 seconds |
| Page load (deal list) | < 2 seconds |
| API response (create deal) | < 500ms |

---

## 13. Security Considerations

### 13.1 Document Security

- All documents encrypted at rest (AES-256)
- Documents encrypted in transit (TLS 1.3)
- Pre-signed URLs for document access (15-minute expiry)
- Access logging for all document views
- Automatic PII detection and redaction (future)

### 13.2 Data Access

- Organization-level data isolation
- Role-based access control (RBAC)
- Audit trail for all deal modifications
- Soft delete with 30-day retention

### 13.3 API Security

- Rate limiting: 100 requests/minute per user
- File upload limits: 50MB per file, 200MB per request
- Input sanitization on all text fields
- CSRF protection on all mutations

---

## 14. Open Questions

| Question | Status | Decision |
|----------|--------|----------|
| Should we support Google Drive / Dropbox import? | Open | Consider for v1.1 |
| How to handle password-protected PDFs? | Open | Prompt user for password or reject |
| Should we extract photos from OMs? | Open | Yes, for property gallery |
| Max pages to process per document? | Open | Suggest 100 pages |
| How long to retain processing logs? | Open | 90 days suggested |

---

## 15. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Claude API (Haiku) | External | Available |
| S3-compatible storage | External | TBD provider |
| PDF processing library | Internal | pdf2image, PyMuPDF |
| Excel processing | Internal | openpyxl, pandas |
| Image processing | Internal | Pillow |

---

## 16. Rollout Plan

### Phase 1a: Manual Entry (Week 1)
- Basic deal creation form
- Field validation
- Deal list view

### Phase 1b: Document Upload (Week 1-2)
- File upload infrastructure
- Document storage
- Basic classification
- Drag & drop interface

### Phase 1c: AI Extraction (Week 2)
- OM extraction (Gemini Flash)
- T-12 extraction (Gemini Flash)
- Rent roll extraction (Gemini Flash)
- Intelligent router implementation
- Cost tracking

### Phase 1d: Review & Polish (Week 2)
- Extraction review UI
- Confidence indicators
- Correction tracking

### Phase 1.5: Enhanced Intake (High Priority - Weeks 3-4)
**Key Differentiators:**
- **Chat Mode MVP**: Conversational deal entry interface
- **Email Integration**: Forward to intake@dream.ai
- **WhatsApp Integration**: WhatsApp Business API bot
- **Slack Integration**: Slack bot with slash commands
- **File Storage Integrations**: Google Drive, OneDrive, Dropbox, Box, iCloud
- **Third-Party Report Support**: Engineering reports, plans, specs, permits, etc.
- **Due Diligence Workflow**: Upload additional docs during DD, impact on underwriting

**Priority Order:**
1. Chat Mode MVP (Week 3)
2. File Storage Integrations (Week 3-4) - Google Drive + Dropbox first
3. Email Forward (Week 4)
4. WhatsApp + Slack (Week 4-5)

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Author: DREAM AI Product Team*

