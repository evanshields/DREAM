# Phase 1 PRD - Additional Updates (Round 2)

**Date:** December 20, 2025  
**PRD Version:** 1.1 → 1.2 (Updated)

---

## Additional Feedback Addressed

### ✅ 1. Third-Party Reports & Due Diligence Documents

**Added:** Section 5.5 - Document Extraction: Third-Party Reports (Due Diligence)

**New Document Types Added:**
- PRIOR_APPRAISAL: Historical appraisal reports
- ORIGINAL_PLANS: Original architectural/construction plans and specifications
- CONSTRUCTION_BUDGET: Construction cost breakdown, budget estimates
- PERMITS: Building permits, zoning permits, construction permits
- ENGINEERING_REPORT: Structural engineering, MEP reports, building systems analysis

**Key Features:**
- **Due Diligence Workflow**: Users can upload third-party reports during due diligence
- **Impact on Underwriting**: Extracted insights automatically update underwriting assumptions
- **Cost Tiers**: Different pricing for complex documents (engineering reports, plans, specs)
- **Automatic Updates**: Risk flags, cost adjustments, timeline impacts

**Location:** Section 5.5 in PRD

---

### ✅ 2. Cost Considerations for Complex Documents

**Added:** Cost tiers and pricing strategy in Section 5.5 and 6.1

**Cost Tiers:**
- **Standard Documents** (OM, T-12, Rent Roll): Included in base subscription
- **Third-Party Reports**: 
  - Prior Appraisal: Standard tier
  - Engineering Report: Premium tier ($0.030)
  - Original Plans/Specs: Premium tier ($0.050)
  - Construction Budget: Standard tier
  - Permits: Standard tier
  - Environmental Report: Premium tier ($0.025)

**Pricing Strategy Options:**
1. Per-document pricing ($5-20 per document based on complexity)
2. Included in premium subscription tiers
3. Credit-based system (10 credits/month, 1 credit = standard doc, 3 credits = complex report)

**Location:** 
- Section 5.5 (Due Diligence Documents)
- Section 6.1 (LLM Routing - Cost Tiers)

---

### ✅ 3. File Storage Integrations

**Added:** Section 4.6 - Method F: File Storage Integrations

**Supported Platforms:**
- Google Drive
- Microsoft OneDrive
- Dropbox
- Box
- Apple iCloud

**Features:**
- OAuth authentication for each provider
- File browser interface (similar to native file picker)
- Folder selection and bulk import
- Automatic file type detection
- Progress tracking for large imports
- Available in both Dashboard and Chat modes

**Priority:** Phase 1.5 - Google Drive + Dropbox first

**Location:** Section 4.6 in PRD

---

### ✅ 4. LLM Router Function Implementation

**Updated:** Section 6.1 - Intelligent Router Function

**Router Logic:**
- **Simple Tasks**: Gemini 1.5 Flash (70% cost savings)
- **Standard Documents**: Gemini 1.5 Flash (OM, T-12, Rent Roll)
- **Complex Documents**: Claude 3.5 Haiku (large OMs, engineering reports)
- **Very Complex**: Claude 3.5 Haiku (plans, specs, technical reports)

**Router Decision Factors:**
1. Document Type
2. Document Size (<20 pages → Flash; >20 pages → Haiku)
3. Image Quality
4. Extraction Confidence (low confidence → upgrade to Haiku)
5. User Tier (premium users → default to Haiku)

**Cost Impact:**
- Standard deals: ~$0.015-0.025 (40-50% cost reduction)
- Complex deals: ~$0.05-0.10 (includes third-party reports)

**Location:** Section 6.1 in PRD

---

### ✅ 5. Integration Priority Updates

**Moved from Phase 10 to Phase 1.5 (High Priority):**

- **Email Forward**: Forward to intake@dream.ai
- **WhatsApp Integration**: WhatsApp Business API bot
- **Slack Integration**: Slack bot with slash commands

**Rationale:** These integrations are key differentiators that make deal intake frictionless.

**Location:** Sections 4.3, 4.4, 4.5 in PRD

---

### ✅ 6. Chat Mode Priority Update

**Updated:** Chat Mode is now Phase 1.5 MVP (High Priority)

**MVP Scope:**
- Basic chat interface with text input
- File upload support (drag & drop, file picker)
- Mode toggle (Dashboard ↔ Chat)
- Simple AI responses with extracted data display
- "View in Dashboard" transition
- File storage integration (at least Google Drive + Dropbox)

**Location:** Section 8.0.2 and Section 16 (Rollout Plan)

---

### ✅ 7. Expense Ratio Validation Decision

**Decision:** NO deal type detection for expense ratio validation

**Implementation:**
- Removed automatic deal type detection
- Expense ratio benchmarks remain as reference only
- No automatic validation based on deal type
- Users manually specify deal characteristics

**Location:** Section 7.1 (Validation Rules) - No changes needed, decision documented

---

## Updated Document Classification

**New Document Types in Classification Prompt:**
- PRIOR_APPRAISAL
- ORIGINAL_PLANS
- CONSTRUCTION_BUDGET
- PERMITS
- ENGINEERING_REPORT

**Total Document Types Supported:** 22 types (up from 17)

**Location:** 
- Section 6.2 (Document Classification Prompt)
- Section 10.2 (Database Enum)

---

## Updated Rollout Plan

**Phase 1.5 Added (Weeks 3-4):**

**Priority Order:**
1. Chat Mode MVP (Week 3)
2. File Storage Integrations (Week 3-4) - Google Drive + Dropbox first
3. Email Forward (Week 4)
4. WhatsApp + Slack (Week 4-5)

**Key Differentiators:**
- Chat Mode MVP
- Email/WhatsApp/Slack integrations
- File storage integrations
- Third-party report support
- Due diligence workflow

**Location:** Section 16 (Rollout Plan)

---

## Cost Recovery Strategy

**Standard Documents:**
- OM, T-12, Rent Roll: Included in base subscription

**Third-Party Reports:**
- Option 1: Per-document pricing ($5-20 based on complexity)
- Option 2: Included in premium subscription tiers
- Option 3: Credit-based system

**Cost Communication:**
- System clearly communicates costs before processing
- Users can choose to process now or upgrade subscription
- Premium users get unlimited processing

**Location:** Section 5.5 and Section 6.1

---

## Files Modified

1. **PRDs/DREAM_AI_Phase_1_PRD.md**
   - Added Section 5.5 (Third-Party Reports & Due Diligence)
   - Updated Section 6.1 (LLM Router Function)
   - Updated Section 6.2 (Document Classification - added 5 new types)
   - Updated Section 8.0 (Dual-Mode Interface - file storage integrations)
   - Updated Section 10.2 (Database Enum - added new document types)
   - Updated Section 16 (Rollout Plan - Phase 1.5)
   - Updated Sections 4.3-4.6 (Integration methods - moved to Phase 1.5)

2. **docs/PRD_updates_round2.md** (This file)
   - Summary of all additional updates

---

## Key Decisions Made

1. **Chat Mode**: Phase 1.5 MVP - High Priority ✅
2. **Expense Ratio**: NO deal type detection ✅
3. **LLM Model**: Proceed with Gemini Flash + Router function ✅
4. **Integrations**: Move Email/WhatsApp/Slack to Phase 1.5 ✅
5. **File Storage**: Phase 1.5 - Google Drive + Dropbox first ✅
6. **Third-Party Reports**: Support with cost tiers ✅

---

## Next Steps

1. **Review Updated PRD**: All changes incorporated
2. **Prioritize Phase 1.5 Features**: Chat Mode MVP is top priority
3. **Cost Model Design**: Finalize pricing strategy for third-party reports
4. **Integration Planning**: Begin technical design for Email/WhatsApp/Slack
5. **File Storage APIs**: Research OAuth integration for Google Drive/Dropbox

---

*Summary compiled: December 20, 2025*

