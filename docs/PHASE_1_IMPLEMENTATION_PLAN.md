# Phase 1 Implementation Plan

**PRD Version:** 1.2  
**Created:** December 20, 2025  
**Status:** Ready for Implementation

---

## Overview

This document breaks down Phase 1 PRD into actionable implementation tasks with detailed prompts for each component. Each task can be assigned to the appropriate agent (UX Engineer, UI Engineer, Framework Converter, or general development).

---

## Implementation Strategy

### Approach
1. **Incremental Development**: Build Phase 1a → 1b → 1c → 1d → 1.5 sequentially
2. **Agent-Based Development**: Use specialized agents for their domains
3. **Prompt-Driven Tasks**: Each task includes a detailed prompt for the agent
4. **Testing at Each Phase**: Validate before moving to next phase

### Agent Roles
- **UX Engineer**: Information architecture, user flows, HTML prototypes
- **UI Engineer**: Styling, Tailwind CSS, design system application
- **Framework Converter**: Convert prototypes to Next.js/React components
- **Backend Engineer**: API development, database, LLM integration
- **Full-Stack Developer**: Integration, testing, deployment

---

## Phase 1a: Manual Entry (Week 1)

### Task 1.1: Database Schema Setup
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 4-6 hours

**Prompt:**
```
Create the database schema for Phase 1 based on Section 10 of the Phase 1 PRD.

Requirements:
1. Create PostgreSQL schema with all tables from Section 10.1:
   - deals table
   - documents table
   - extraction_jobs table
   - extraction_corrections table
2. Create all enums from Section 10.2:
   - property_type_enum
   - property_class_enum
   - source_type_enum
   - how_received_enum
   - market_status_enum
   - deal_stage_enum
   - priority_enum
   - document_type_enum (with all 22 document types)
   - processing_status_enum
   - extraction_job_status_enum
   - storage_provider_enum
3. Create all indexes from Section 10.1
4. Use Prisma schema format (backend/schema.prisma)
5. Include proper relationships and constraints
6. Add created_at, updated_at, deleted_at timestamps where specified

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 10
```

**Deliverables:**
- Updated `backend/schema.prisma`
- Migration file `backend/migrations/002_phase1_schema.sql`
- Seed data for testing

---

### Task 1.2: Manual Entry Form UX Prototype
**Agent:** UX Engineer  
**Priority:** Critical  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Create a UX prototype HTML file for the Manual Entry form (Quick Add) based on Section 5.1 of the Phase 1 PRD.

Requirements:
1. Create semantic HTML layout for all 4 sections:
   - Section 1: Property Identification (9 fields)
   - Section 2: Financial Overview (6 fields)
   - Section 3: Deal Source (7 fields)
   - Section 4: Notes & Tags (3 fields)
2. Include all field types: Text, Dropdown, Currency, Percentage, Number, Email, Phone, Textarea, Multi-select
3. Show all states: Empty, Filled, Validation Error, Success
4. Include form validation indicators
5. Mobile-first design (44pt touch targets)
6. Follow mobile best practices
7. Include navigation structure as HTML comments
8. No CSS/styling - pure semantic HTML only

Output: `ux-prototypes/manual-entry-form.html`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 5.1
```

**Deliverables:**
- `ux-prototypes/manual-entry-form.html`

---

### Task 1.3: Manual Entry Form UI Styling
**Agent:** UI Engineer (Minimal Pro)  
**Priority:** Critical  
**Estimated Time:** 2-3 hours

**Prompt:**
```
Apply Minimal Pro styling to the manual entry form UX prototype.

Requirements:
1. Read `ux-prototypes/manual-entry-form.html`
2. Apply Tailwind CSS classes using design tokens from `design-language-dream.md`
3. Use Minimal Pro flavor: low-chroma colors, subtle borders, minimal shadows
4. Ensure proper spacing, typography, and visual hierarchy
5. Style all form states: empty, filled, error, success
6. Maintain all semantic structure and accessibility attributes
7. Use tabular-nums for numeric inputs
8. Ensure 44pt minimum touch targets

Output: `dream-ui-minimal.html` (or create component file)

Reference: 
- design-language-dream.md
- PRDs/DREAM_AI_Phase_1_PRD.md Section 8.1
```

**Deliverables:**
- Styled form component or HTML file

---

### Task 1.4: Manual Entry Form React Component
**Agent:** Framework Converter / Full-Stack Developer  
**Priority:** Critical  
**Estimated Time:** 4-6 hours

**Prompt:**
```
Convert the styled manual entry form to a React component with TypeScript.

Requirements:
1. Create `src/components/forms/ManualEntryForm.tsx`
2. Use React Hook Form for form management
3. Implement all validation rules from Section 7.1 of PRD
4. Create TypeScript types for form data matching PRD Section 5.1
5. Add form state management (loading, error, success)
6. Connect to API endpoint POST /api/v1/deals
7. Show validation errors inline
8. Handle form submission and success states
9. Use existing UI components from `src/components/UIComponents.tsx`
10. Follow existing code patterns in `src/`

Output: `src/components/forms/ManualEntryForm.tsx`
Types: `src/types/deal.ts`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Sections 5.1, 7.1, 9.1
```

**Deliverables:**
- `src/components/forms/ManualEntryForm.tsx`
- `src/types/deal.ts` (updated)
- Form validation logic

---

### Task 1.5: Deal List View
**Agent:** Full-Stack Developer  
**Priority:** High  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Create a deal list view page showing all deals with filtering and sorting.

Requirements:
1. Create `src/pages/DealsList.tsx`
2. Fetch deals from GET /api/v1/deals
3. Display deal cards with:
   - Property name, address
   - Units, asking price
   - Stage, priority badges
   - Created date
4. Add filtering by: stage, priority, property type
5. Add sorting by: created date, asking price, property name
6. Add search functionality
7. Link to deal detail page
8. Use existing DealCard component or create new one
9. Show loading and empty states

Output: `src/pages/DealsList.tsx`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 8.1
```

**Deliverables:**
- `src/pages/DealsList.tsx`
- Updated `src/components/DealCard.tsx` if needed

---

### Task 1.6: Backend API - Create Deal Endpoint
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Create the POST /api/v1/deals endpoint for manual deal creation.

Requirements:
1. Create `backend/api/endpoints/deals.py`
2. Implement POST /api/v1/deals endpoint matching Section 9.1 of PRD
3. Validate request body against PRD schema
4. Apply validation rules from Section 7.1
5. Create deal record in database
6. Return 201 Created with deal data
7. Handle validation errors (400)
8. Add proper error messages
9. Use Prisma client for database operations
10. Add logging and error handling

Request Body Schema (from PRD Section 9.1):
- property_name, address (street, city, state, zip)
- property_type, property_class, year_built, units
- asking_price, occupancy, noi_in_place, noi_pro_forma
- source (type, name, company, email, phone)
- notes, tags, priority

Output: `backend/api/endpoints/deals.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Sections 7.1, 9.1, 10.1
```

**Deliverables:**
- `backend/api/endpoints/deals.py`
- API tests

---

## Phase 1b: Document Upload (Week 1-2)

### Task 1.7: Document Upload UX Prototype
**Agent:** UX Engineer  
**Priority:** Critical  
**Estimated Time:** 2-3 hours

**Prompt:**
```
Create UX prototype for document upload interface based on Section 8.2 of PRD.

Requirements:
1. Create drag-and-drop zone
2. File picker fallback
3. Show uploaded files list with:
   - Filename
   - Document type dropdown (with all 22 types)
   - Status indicator (uploading, uploaded, error)
   - Remove button
4. Show file size limits (50MB per file)
5. Show supported formats (PDF, XLSX, XLS, PNG, JPG, DOCX)
6. Include Cancel and Extract Data buttons
7. Show upload progress
8. Include all states: empty, uploading, uploaded, error
9. Mobile-first design

Output: `ux-prototypes/document-upload.html`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 8.2
```

**Deliverables:**
- `ux-prototypes/document-upload.html`

---

### Task 1.8: Document Upload UI Component
**Agent:** UI Engineer  
**Priority:** Critical  
**Estimated Time:** 2-3 hours

**Prompt:**
```
Style the document upload UX prototype with Minimal Pro theme.

Requirements:
1. Read `ux-prototypes/document-upload.html`
2. Apply Tailwind CSS classes
3. Style drag-and-drop zone with hover states
4. Style file list with proper spacing
5. Add visual feedback for upload states
6. Use design tokens from design-language-dream.md
7. Ensure accessibility (keyboard navigation, screen readers)

Output: Styled component or HTML file

Reference: design-language-dream.md
```

**Deliverables:**
- Styled upload component

---

### Task 1.9: Document Upload React Component
**Agent:** Full-Stack Developer  
**Priority:** Critical  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create React component for document upload with drag-and-drop functionality.

Requirements:
1. Create `src/components/upload/DocumentUpload.tsx`
2. Implement drag-and-drop using react-dropzone
3. Support file picker fallback
4. Validate file types and sizes (50MB limit)
5. Show upload progress
6. Display uploaded files list
7. Allow document type selection (all 22 types from PRD)
8. Connect to POST /api/v1/deals/{deal_id}/documents
9. Handle upload errors
10. Show success states

Output: `src/components/upload/DocumentUpload.tsx`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 8.2, 9.1
```

**Deliverables:**
- `src/components/upload/DocumentUpload.tsx`
- Upload utility functions

---

### Task 1.10: Backend API - Document Upload Endpoint
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create POST /api/v1/deals/{deal_id}/documents endpoint for document upload.

Requirements:
1. Create `backend/api/endpoints/documents.py`
2. Handle multipart/form-data file uploads
3. Validate file types and sizes (50MB max)
4. Store files in S3-compatible storage
5. Create document records in database
6. Return 202 Accepted with upload_id and document list
7. Set initial status to PROCESSING
8. Queue extraction job (async)
9. Handle storage errors gracefully

Request: multipart/form-data with files[] array
Response: 202 Accepted with upload_id, documents array, extraction_job_id

Output: `backend/api/endpoints/documents.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 9.1
```

**Deliverables:**
- `backend/api/endpoints/documents.py`
- Storage service integration
- File validation logic

---

### Task 1.11: File Storage Service
**Agent:** Backend Engineer  
**Priority:** High  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Create file storage service for S3-compatible storage.

Requirements:
1. Create `backend/services/storage.py`
2. Support S3-compatible storage (AWS S3, DigitalOcean Spaces, etc.)
3. Implement upload, download, delete methods
4. Generate pre-signed URLs for document access (15-minute expiry)
5. Handle encryption at rest (if needed)
6. Add error handling and retries
7. Support multiple storage providers (configurable)
8. Add logging for all operations

Output: `backend/services/storage.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 13.1
```

**Deliverables:**
- `backend/services/storage.py`
- Storage configuration

---

## Phase 1c: AI Extraction (Week 2)

### Task 1.12: Document Classification Service
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create document classification service using Gemini 1.5 Flash.

Requirements:
1. Create `backend/services/classification.py`
2. Use Gemini 1.5 Flash API for classification
3. Implement classification prompt from PRD Section 6.2
4. Support all 22 document types from PRD
5. Return document_type, confidence, reasoning
6. Handle API errors and retries
7. Add cost tracking
8. Cache results for same document hash
9. Log classification results

Classification Prompt: Use prompt from PRD Section 6.2
Document Types: All 22 types including PRIOR_APPRAISAL, ORIGINAL_PLANS, etc.

Output: `backend/services/classification.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 6.2
```

**Deliverables:**
- `backend/services/classification.py`
- Classification tests

---

### Task 1.13: LLM Router Implementation
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Create intelligent LLM router that selects optimal model based on document complexity.

Requirements:
1. Create `backend/services/llm_router.py`
2. Implement router logic from PRD Section 6.1:
   - Simple tasks → Gemini 1.5 Flash
   - Standard docs → Gemini 1.5 Flash
   - Complex docs → Claude 3.5 Haiku
   - Very complex → Claude 3.5 Haiku
3. Decision factors:
   - Document type
   - Document size (<20 pages → Flash, >20 pages → Haiku)
   - Image quality
   - Extraction confidence (low → upgrade to Haiku)
   - User tier
4. Return selected model and reasoning
5. Track router decisions for analytics

Output: `backend/services/llm_router.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 6.1
```

**Deliverables:**
- `backend/services/llm_router.py`
- Router tests

---

### Task 1.14: OM Extraction Service
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 5-6 hours

**Prompt:**
```
Create OM (Offering Memorandum) extraction service using LLM router.

Requirements:
1. Create `backend/services/extraction/om_extraction.py`
2. Use router to select model (Flash for simple, Haiku for complex)
3. Implement extraction prompt from PRD Section 6.2
4. Extract all fields from PRD Section 5.2:
   - Property information (name, address, units, etc.)
   - Unit mix (type, count, avg_sf, market_rent)
   - Financial data (asking price, NOI, cap rates)
   - Investment highlights
5. Return structured JSON with confidence scores
6. Handle extraction errors
7. Track extraction costs
8. Log extraction results

Extraction Prompt: Use prompt from PRD Section 6.2
Output Format: JSON matching PRD Section 6.2 schema

Output: `backend/services/extraction/om_extraction.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Sections 5.2, 6.1, 6.2
```

**Deliverables:**
- `backend/services/extraction/om_extraction.py`
- Extraction tests

---

### Task 1.15: T-12 Extraction Service
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create T-12 (Trailing 12) extraction service.

Requirements:
1. Create `backend/services/extraction/t12_extraction.py`
2. Use Gemini 1.5 Flash (standard tabular data)
3. Implement extraction prompt from PRD Section 6.2
4. Extract all fields from PRD Section 5.3:
   - Revenue line items (GPR, loss to lease, vacancy, etc.)
   - Expense line items (taxes, insurance, utilities, etc.)
   - Calculated metrics (NOI, expense ratio, per unit metrics)
5. Handle monthly vs annual data
6. Return structured JSON with confidence scores
7. Track extraction costs

Extraction Prompt: Use prompt from PRD Section 6.2
Output Format: JSON matching PRD Section 6.2 schema

Output: `backend/services/extraction/t12_extraction.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Sections 5.3, 6.2
```

**Deliverables:**
- `backend/services/extraction/t12_extraction.py`
- Extraction tests

---

### Task 1.16: Rent Roll Extraction Service
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create Rent Roll extraction service.

Requirements:
1. Create `backend/services/extraction/rent_roll_extraction.py`
2. Use Gemini 1.5 Flash (standard tabular data)
3. Implement extraction prompt from PRD Section 6.2
4. Extract unit-level data from PRD Section 5.4:
   - Unit number, type, square footage
   - Bedrooms, bathrooms
   - Current rent, market rent
   - Lease dates, tenant info, status
5. Calculate aggregated metrics:
   - Occupancy rate, average rent, rent PSF
   - Loss to lease, delinquency rate
6. Return structured JSON with confidence scores
7. Track extraction costs

Extraction Prompt: Use prompt from PRD Section 6.2
Output Format: JSON matching PRD Section 6.2 schema

Output: `backend/services/extraction/rent_roll_extraction.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Sections 5.4, 6.2
```

**Deliverables:**
- `backend/services/extraction/rent_roll_extraction.py`
- Extraction tests

---

### Task 1.17: Extraction Job Processor
**Agent:** Backend Engineer  
**Priority:** Critical  
**Estimated Time:** 5-6 hours

**Prompt:**
```
Create async extraction job processor that handles document extraction workflow.

Requirements:
1. Create `backend/services/extraction/extraction_processor.py`
2. Process extraction jobs asynchronously (Celery or similar)
3. Workflow:
   - Classify document type
   - Route to appropriate extraction service
   - Extract data with confidence scores
   - Calculate overall confidence
   - Identify fields requiring review
   - Update extraction_job status
4. Handle errors and retries
5. Track processing time and costs
6. Update document records with extraction data
7. Send notifications on completion

Output: `backend/services/extraction/extraction_processor.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 6
```

**Deliverables:**
- `backend/services/extraction/extraction_processor.py`
- Celery task configuration
- Job queue setup

---

### Task 1.18: Extraction Status API Endpoint
**Agent:** Backend Engineer  
**Priority:** High  
**Estimated Time:** 2-3 hours

**Prompt:**
```
Create GET /api/v1/extraction-jobs/{job_id} endpoint for checking extraction status.

Requirements:
1. Create endpoint in `backend/api/endpoints/extraction.py`
2. Return extraction job status matching PRD Section 9.1
3. Include:
   - Job status (PENDING, PROCESSING, COMPLETED, FAILED)
   - Processing timestamps
   - Extracted data
   - Fields requiring review
   - Overall confidence score
   - Cost information
4. Handle job not found errors
5. Return appropriate status codes

Response Format: Match PRD Section 9.1 response schema

Output: `backend/api/endpoints/extraction.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 9.1
```

**Deliverables:**
- `backend/api/endpoints/extraction.py`
- API tests

---

## Phase 1d: Review & Polish (Week 2)

### Task 1.19: Extraction Review UX Prototype
**Agent:** UX Engineer  
**Priority:** Critical  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create UX prototype for extraction review interface based on PRD Section 8.3.

Requirements:
1. Create split-view layout:
   - Left: PDF/document viewer
   - Right: Extracted data form
2. Show extracted fields with confidence indicators:
   - High (90+): Green checkmark
   - Medium (70-89): Yellow highlight
   - Low (50-69): Orange highlight
   - Very Low (<50): Red highlight
3. Allow inline editing of extracted fields
4. Show source page/location for each field
5. Highlight low-confidence fields
6. Include "Looks Good" confirmation button
7. Show extraction summary (X fields extracted, Y need review)
8. Include all states: loading, populated, error

Output: `ux-prototypes/extraction-review.html`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 8.3, 8.4
```

**Deliverables:**
- `ux-prototypes/extraction-review.html`

---

### Task 1.20: Extraction Review UI Component
**Agent:** UI Engineer  
**Priority:** Critical  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Style the extraction review UX prototype with Minimal Pro theme.

Requirements:
1. Read `ux-prototypes/extraction-review.html`
2. Apply Tailwind CSS classes
3. Style confidence indicators (green/yellow/orange/red)
4. Style split-view layout
5. Style extracted data form
6. Add hover states and interactions
7. Ensure proper visual hierarchy
8. Use design tokens from design-language-dream.md

Output: Styled component

Reference: design-language-dream.md, PRDs/DREAM_AI_Phase_1_PRD.md Section 8.4
```

**Deliverables:**
- Styled review component

---

### Task 1.21: Extraction Review React Component
**Agent:** Full-Stack Developer  
**Priority:** Critical  
**Estimated Time:** 5-6 hours

**Prompt:**
```
Create React component for extraction review with inline editing.

Requirements:
1. Create `src/components/review/ExtractionReview.tsx`
2. Fetch extraction job data from API
3. Display split-view: document viewer + extracted data
4. Show confidence indicators for each field
5. Allow inline editing of extracted fields
6. Track user corrections
7. Show extraction summary
8. Implement "Looks Good" confirmation
9. Connect to POST /api/v1/deals/{deal_id}/confirm-extraction
10. Handle loading and error states

Output: `src/components/review/ExtractionReview.tsx`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Sections 8.3, 9.1
```

**Deliverables:**
- `src/components/review/ExtractionReview.tsx`
- Document viewer integration

---

### Task 1.22: Confirm Extraction API Endpoint
**Agent:** Backend Engineer  
**Priority:** High  
**Estimated Time:** 2-3 hours

**Prompt:**
```
Create POST /api/v1/deals/{deal_id}/confirm-extraction endpoint.

Requirements:
1. Create endpoint in `backend/api/endpoints/extraction.py`
2. Accept corrections object with user edits
3. Update deal record with confirmed data
4. Track corrections in extraction_corrections table
5. Update deal status to READY_FOR_SCREENING
6. Return confirmation response
7. Handle validation errors

Request Body: { corrections: {...}, confirmed: true }
Response: { deal_id, status, corrections_applied, next_step }

Output: Updated `backend/api/endpoints/extraction.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 9.1
```

**Deliverables:**
- Updated extraction endpoint
- Correction tracking logic

---

## Phase 1.5: Enhanced Intake (Weeks 3-4)

### Task 1.23: Chat Mode UX Prototype
**Agent:** UX Engineer  
**Priority:** High (MVP)  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create UX prototype for Chat Mode interface based on PRD Section 8.0.2 and UX feedback.

Requirements:
1. Create chat interface with message bubbles
2. Show extracted deal summary card above chat
3. Include file upload in chat (drag & drop, file picker, cloud storage)
4. Show typing indicator for AI responses
5. Include mode toggle (Dashboard ↔ Chat)
6. Show all states: empty, loading, populated, error
7. Mobile-first design
8. Include example chat flow from PRD

Output: `ux-prototypes/chat-mode.html`

Reference: 
- PRDs/DREAM_AI_Phase_1_PRD.md Section 8.0.2
- docs/chat-mode-ux-ui-feedback.md
```

**Deliverables:**
- `ux-prototypes/chat-mode.html`

---

### Task 1.24: Chat Mode UI Component
**Agent:** UI Engineer  
**Priority:** High (MVP)  
**Estimated Time:** 3-4 hours

**Prompt:**
```
Style the Chat Mode UX prototype with Minimal Pro theme.

Requirements:
1. Read `ux-prototypes/chat-mode.html`
2. Apply Tailwind CSS classes
3. Style chat bubbles (user vs AI)
4. Style extracted summary card
5. Style input area
6. Add hover states and interactions
7. Ensure mobile responsiveness
8. Use design tokens from design-language-dream.md

Output: Styled component

Reference: 
- design-language-dream.md
- docs/chat-mode-ux-ui-feedback.md
```

**Deliverables:**
- Styled chat component

---

### Task 1.25: Chat Mode React Component
**Agent:** Full-Stack Developer  
**Priority:** High (MVP)  
**Estimated Time:** 6-8 hours

**Prompt:**
```
Create Chat Mode React component with conversational interface.

Requirements:
1. Create `src/components/chat/ChatMode.tsx`
2. Implement chat interface with message history
3. Handle user input and AI responses
4. Integrate file upload in chat
5. Show extracted deal summary card
6. Connect to chat API endpoint
7. Handle streaming responses (if implemented)
8. Include mode toggle
9. Persist chat history
10. Mobile-optimized

Output: `src/components/chat/ChatMode.tsx`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 8.0.2
```

**Deliverables:**
- `src/components/chat/ChatMode.tsx`
- Chat API integration

---

### Task 1.26: File Storage Integration - Google Drive
**Agent:** Backend Engineer  
**Priority:** High  
**Estimated Time:** 5-6 hours

**Prompt:**
```
Create Google Drive integration for file import.

Requirements:
1. Create `backend/services/integrations/google_drive.py`
2. Implement OAuth 2.0 authentication
3. Create file browser API endpoint
4. Support folder selection and file listing
5. Download files from Google Drive
6. Upload to DREAM storage
7. Handle OAuth token refresh
8. Store user credentials securely

Output: `backend/services/integrations/google_drive.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 4.6
```

**Deliverables:**
- `backend/services/integrations/google_drive.py`
- OAuth flow implementation

---

### Task 1.27: File Storage Integration - Dropbox
**Agent:** Backend Engineer  
**Priority:** High  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create Dropbox integration for file import.

Requirements:
1. Create `backend/services/integrations/dropbox.py`
2. Implement OAuth 2.0 authentication
3. Create file browser API endpoint
4. Support folder selection and file listing
5. Download files from Dropbox
6. Upload to DREAM storage
7. Handle OAuth token refresh

Output: `backend/services/integrations/dropbox.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 4.6
```

**Deliverables:**
- `backend/services/integrations/dropbox.py`
- OAuth flow implementation

---

### Task 1.28: File Storage UI Component
**Agent:** Full-Stack Developer  
**Priority:** High  
**Estimated Time:** 4-5 hours

**Prompt:**
```
Create React component for file storage integration (Google Drive, Dropbox).

Requirements:
1. Create `src/components/upload/CloudStoragePicker.tsx`
2. Show "Connect Google Drive" / "Connect Dropbox" buttons
3. Handle OAuth flow
4. Display file browser interface
5. Allow file/folder selection
6. Show selected files
7. Handle import from cloud storage
8. Show progress during import

Output: `src/components/upload/CloudStoragePicker.tsx`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 4.6
```

**Deliverables:**
- `src/components/upload/CloudStoragePicker.tsx`
- OAuth flow UI

---

### Task 1.29: Email Forward Integration
**Agent:** Backend Engineer  
**Priority:** Medium  
**Estimated Time:** 6-8 hours

**Prompt:**
```
Create email forwarding integration for deal intake.

Requirements:
1. Set up email inbox (intake@dream.ai)
2. Create `backend/services/integrations/email.py`
3. Parse incoming emails and attachments
4. Extract deal context from email body
5. Classify attachments as documents
6. Create deal from email
7. Trigger extraction pipeline
8. Send confirmation email
9. Handle email parsing errors

Output: `backend/services/integrations/email.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 4.3
```

**Deliverables:**
- `backend/services/integrations/email.py`
- Email service configuration

---

### Task 1.30: WhatsApp Integration
**Agent:** Backend Engineer  
**Priority:** Medium  
**Estimated Time:** 6-8 hours

**Prompt:**
```
Create WhatsApp Business API integration for deal intake.

Requirements:
1. Create `backend/services/integrations/whatsapp.py`
2. Set up WhatsApp Business API webhook
3. Handle incoming messages and media
4. Extract deal information from messages
5. Support document/image uploads
6. Implement two-way communication
7. Create deal from WhatsApp message
8. Send follow-up questions via WhatsApp

Output: `backend/services/integrations/whatsapp.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 4.4
```

**Deliverables:**
- `backend/services/integrations/whatsapp.py`
- WhatsApp webhook setup

---

### Task 1.31: Slack Integration
**Agent:** Backend Engineer  
**Priority:** Medium  
**Estimated Time:** 6-8 hours

**Prompt:**
```
Create Slack bot integration for deal intake.

Requirements:
1. Create `backend/services/integrations/slack.py`
2. Set up Slack app and bot
3. Implement `/dream-add-deal` slash command
4. Handle file uploads in Slack
5. Support DM and channel interactions
6. Create deal from Slack message
7. Send deal notifications to channels
8. Support thread-based discussions

Output: `backend/services/integrations/slack.py`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 4.5
```

**Deliverables:**
- `backend/services/integrations/slack.py`
- Slack app configuration

---

## Testing & Quality Assurance

### Task 1.32: End-to-End Testing
**Agent:** QA Engineer / Full-Stack Developer  
**Priority:** High  
**Estimated Time:** 8-10 hours

**Prompt:**
```
Create comprehensive E2E tests for Phase 1 workflows.

Requirements:
1. Test manual entry flow (create deal → view in list)
2. Test document upload flow (upload → extract → review → confirm)
3. Test extraction accuracy with sample documents
4. Test error handling (invalid files, API errors)
5. Test validation rules
6. Test confidence scoring
7. Use Playwright or Cypress
8. Create test fixtures with sample documents

Test Scenarios:
- Happy path: Upload OM → Extract → Review → Confirm → Deal created
- Happy path: Manual entry → Deal created
- Error recovery: Upload fails → Retry → Success
- Correction flow: Low confidence → User corrects → Confirm

Output: `tests/e2e/test_phase1_workflows.py` or similar

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 12.3
```

**Deliverables:**
- E2E test suite
- Test fixtures

---

## Deployment & Infrastructure

### Task 1.33: Deployment Configuration
**Agent:** DevOps / Backend Engineer  
**Priority:** High  
**Estimated Time:** 4-6 hours

**Prompt:**
```
Set up deployment configuration for Phase 1.

Requirements:
1. Create Dockerfiles for backend and frontend
2. Set up docker-compose for local development
3. Configure environment variables
4. Set up database migrations
5. Configure file storage (S3-compatible)
6. Set up task queue (Celery/Redis)
7. Configure logging and monitoring
8. Create deployment documentation

Output: 
- `Dockerfile` (backend)
- `Dockerfile` (frontend)
- `docker-compose.yml`
- `.env.example`
- `DEPLOYMENT.md`

Reference: PRDs/DREAM_AI_Phase_1_PRD.md Section 13
```

**Deliverables:**
- Docker configuration
- Deployment documentation
- Environment setup

---

## Summary

### Task Count by Phase
- **Phase 1a**: 6 tasks (Manual Entry)
- **Phase 1b**: 5 tasks (Document Upload)
- **Phase 1c**: 7 tasks (AI Extraction)
- **Phase 1d**: 4 tasks (Review & Polish)
- **Phase 1.5**: 9 tasks (Enhanced Intake)
- **Testing**: 1 task
- **Deployment**: 1 task

**Total: 33 tasks**

### Estimated Timeline
- **Phase 1a**: Week 1 (6 tasks)
- **Phase 1b**: Week 1-2 (5 tasks)
- **Phase 1c**: Week 2 (7 tasks)
- **Phase 1d**: Week 2 (4 tasks)
- **Phase 1.5**: Weeks 3-4 (9 tasks)
- **Testing**: Week 4 (1 task)
- **Deployment**: Week 4 (1 task)

**Total: 4 weeks**

### Next Steps
1. Review this implementation plan
2. Prioritize tasks based on dependencies
3. Assign tasks to appropriate agents
4. Start with Phase 1a, Task 1.1 (Database Schema)
5. Use prompts provided for each task
6. Test incrementally as you complete each phase

---

*Implementation Plan Version: 1.0*  
*Created: December 20, 2025*



