# Complete Testing Guide: Tasks 1.0 to 1.25

**Version:** 1.1  
**Date:** December 2025  
**Status:** Ready for Testing  
**Updated:** Added Tasks 1.23-1.25 (Chat Mode)

---

## Table of Contents

1. [Prerequisites & Setup](#prerequisites--setup)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [Task-by-Task Testing](#task-by-task-testing)
   - Tasks 1.1-1.22: [Core Features](#task-by-task-testing)
   - Tasks 1.23-1.25: [Chat Mode](#tasks-123-125-chat-mode)

---

## Prerequisites & Setup

### 1. Environment Setup

#### Backend Prerequisites
```bash
# Check Python version (3.9+ required)
python --version

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
# - DATABASE_URL (Supabase PostgreSQL)
# - GEMINI_API_KEY
# - ANTHROPIC_API_KEY
# - AWS_ACCESS_KEY_ID (or Supabase storage credentials)
# - AWS_SECRET_ACCESS_KEY
# - STORAGE_PROVIDER (SUPABASE, S3, etc.)
```

#### Frontend Prerequisites
```bash
# Check Node.js version (18+ required)
node --version

# Install dependencies
npm install

# Set up environment variables
# Create .env file with:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Start Services

#### Start Backend Server
```bash
cd backend
python main.py
# Server should start on http://localhost:8000
```

#### Start Frontend Dev Server
```bash
npm run dev
# Server should start on http://localhost:5173
```

#### Start HTML Prototype Servers (Optional)
```bash
# Terminal 1: UX Prototypes
cd ux-prototypes
python -m http.server 8080

# Terminal 2: Root HTML files
python -m http.server 8081
```

### 3. Database Setup

```bash
# Run Prisma migrations
cd backend
prisma migrate deploy

# Seed database (optional)
python seed_prisma.py
```

### 4. Verify Services Are Running

```powershell
# Check all ports
Get-NetTCPConnection -LocalPort 8000,5173,8080,8081 -ErrorAction SilentlyContinue
```

---

## Backend Testing

### API Endpoints Overview

| Endpoint | Method | Purpose | Task |
|----------|--------|---------|------|
| `/api/v1/deals` | POST | Create deal | 1.6 |
| `/api/v1/deals` | GET | List deals | 1.6 |
| `/api/v1/deals/{deal_id}/documents` | POST | Upload documents | 1.10 |
| `/api/v1/extraction-jobs/{job_id}` | GET | Get extraction status | 1.18 |
| `/api/v1/deals/{deal_id}/confirm-extraction` | POST | Confirm extraction | 1.22 |

### Testing Tools

- **Postman** or **Insomnia** for API testing
- **curl** for command-line testing
- **Browser DevTools** for frontend API calls

---

## Frontend Testing

### UI Components Overview

| Component | File | Task |
|-----------|------|------|
| Manual Entry Form | `src/components/forms/ManualEntryForm.tsx` | 1.4 |
| Deal List | `src/pages/DealsList.tsx` | 1.5 |
| Document Upload | `src/components/upload/DocumentUpload.tsx` | 1.9 |
| Extraction Review | `src/components/review/ExtractionReview.tsx` | 1.21 |

### HTML Prototypes

| Prototype | File | Task |
|-----------|------|------|
| Manual Entry Form | `dream-ui-minimal.html` | 1.3 |
| Document Upload | `ux-prototypes/document-upload.html` | 1.7, 1.8 |
| Extraction Review | `ux-prototypes/extraction-review.html` | 1.19, 1.20 |

---

## Task-by-Task Testing

### Task 1.1: Database Schema Setup ✅

**Status:** Complete  
**Files:** `backend/schema.prisma`, `backend/migrations/`

#### Test Steps:

1. **Verify Schema Deployment**
   ```bash
   cd backend
   prisma migrate status
   # Should show all migrations as applied
   ```

2. **Check Database Tables**
   ```sql
   -- Connect to Supabase SQL Editor
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public'
   ORDER BY table_name;
   
   -- Expected tables:
   -- - organizations
   -- - users
   -- - deals
   -- - documents
   -- - extraction_jobs
   -- - extraction_data_cache
   -- - extraction_corrections
   -- - tags
   -- - deal_tags
   ```

3. **Verify Enums**
   ```sql
   SELECT typname 
   FROM pg_type 
   WHERE typtype = 'e'
   ORDER BY typname;
   
   -- Should include:
   -- - PropertyType
   -- - PropertyClass
   -- - DocumentType (with 22 values)
   -- - ProcessingStatus
   -- - ExtractionJobStatus
   -- etc.
   ```

4. **Test Seed Data**
   ```bash
   python seed_prisma.py
   # Check Supabase dashboard for seeded data
   ```

**Expected Result:** All tables, enums, and indexes created successfully.

---

### Task 1.2: Manual Entry Form UX Prototype ✅

**Status:** Complete  
**File:** `ux-prototypes/manual-entry-form.html` (if exists) or `dream-ui-minimal.html`

#### Test Steps:

1. **Open Prototype**
   - Navigate to: http://localhost:8081/dream-ui-minimal.html
   - Or open file directly in browser

2. **Verify Form Structure**
   - [ ] Section 1: Property Identification (9 fields visible)
   - [ ] Section 2: Financial Overview (6 fields visible)
   - [ ] Section 3: Deal Source (7 fields visible)
   - [ ] Section 4: Notes & Tags (3 fields visible)

3. **Test Form Fields**
   - [ ] Text inputs accept text
   - [ ] Dropdowns show options
   - [ ] Currency fields format correctly
   - [ ] Percentage fields accept 0-100
   - [ ] Email field validates format
   - [ ] Phone field accepts numbers
   - [ ] Textarea allows multi-line input

4. **Test States**
   - [ ] Empty state displays correctly
   - [ ] Filled state shows values
   - [ ] Error state shows validation messages
   - [ ] Success state shows confirmation

**Expected Result:** Form displays all fields correctly with proper semantic HTML structure.

---

### Task 1.3: Manual Entry Form UI Styling ✅

**Status:** Complete  
**File:** `dream-ui-minimal.html`

#### Test Steps:

1. **Visual Inspection**
   - [ ] Minimal Pro theme applied (low-chroma colors)
   - [ ] Typography uses Libre Franklin (body) and Playfair Display (headings)
   - [ ] Spacing is consistent (using Tailwind scale)
   - [ ] Form fields have proper borders and padding
   - [ ] Buttons are styled correctly
   - [ ] Color palette matches design language

2. **Responsive Design**
   - [ ] Test on mobile viewport (375px width)
   - [ ] Test on tablet viewport (768px width)
   - [ ] Test on desktop viewport (1920px width)
   - [ ] Touch targets are at least 44pt

3. **Accessibility**
   - [ ] Form labels are properly associated
   - [ ] Error messages are accessible
   - [ ] Keyboard navigation works
   - [ ] Screen reader friendly

**Expected Result:** Form matches Minimal Pro design language with proper styling.

---

### Task 1.4: Manual Entry Form React Component ✅

**Status:** Complete  
**File:** `src/components/forms/ManualEntryForm.tsx`

#### Test Steps:

1. **Navigate to Form**
   - Open: http://localhost:5173/#intake
   - Or navigate to deal intake page

2. **Test Form Validation**
   - [ ] Submit empty form → Shows validation errors
   - [ ] Enter invalid email → Shows email error
   - [ ] Enter occupancy > 100% → Shows error
   - [ ] Enter negative numbers → Shows error
   - [ ] Enter valid data → No errors

3. **Test Form Submission**
   - [ ] Fill all required fields
   - [ ] Click "Create Deal"
   - [ ] Verify API call to POST /api/v1/deals
   - [ ] Check response handling
   - [ ] Verify success message/redirect

4. **Test Field Types**
   - [ ] Text inputs work
   - [ ] Select dropdowns work
   - [ ] Currency formatting works
   - [ ] Percentage conversion (0-100 to 0-1) works
   - [ ] Date pickers work (if implemented)

5. **Test Error Handling**
   - [ ] Network error → Shows error message
   - [ ] 422 validation error → Shows field-specific errors
   - [ ] 500 server error → Shows generic error

**Expected Result:** Form validates correctly and creates deals via API.

---

### Task 1.5: Deal List View ✅

**Status:** Complete  
**File:** `src/pages/DealsList.tsx`

#### Test Steps:

1. **Navigate to Deal List**
   - Open: http://localhost:5173/#dashboard
   - Or navigate to deals page

2. **Test Deal Display**
   - [ ] Deals are displayed in cards/list
   - [ ] Each deal shows: name, address, property type, units, price
   - [ ] Status badges display correctly
   - [ ] Priority indicators show
   - [ ] Tags display (if any)

3. **Test Filtering**
   - [ ] Filter by property type → Updates list
   - [ ] Filter by status → Updates list
   - [ ] Filter by priority → Updates list
   - [ ] Clear filters → Shows all deals

4. **Test Sorting**
   - [ ] Sort by name (A-Z, Z-A)
   - [ ] Sort by price (high-low, low-high)
   - [ ] Sort by date (newest, oldest)
   - [ ] Sort by score (if implemented)

5. **Test Search**
   - [ ] Search by property name → Filters results
   - [ ] Search by address → Filters results
   - [ ] Clear search → Shows all deals

6. **Test Pagination** (if implemented)
   - [ ] Navigate to next page
   - [ ] Navigate to previous page
   - [ ] Change items per page

7. **Test API Integration**
   - [ ] Verify GET /api/v1/deals call
   - [ ] Check query parameters (filters, sort, search)
   - [ ] Verify response handling
   - [ ] Check loading state
   - [ ] Check empty state

**Expected Result:** Deal list displays correctly with filtering, sorting, and search working.

---

### Task 1.6: Backend API - Create Deal Endpoint ✅

**Status:** Complete  
**File:** `backend/api/deals.py`

#### Test Steps:

1. **Test POST /api/v1/deals**

   **Request:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/deals \
     -H "Content-Type: application/json" \
     -d '{
       "property_name": "Test Apartments",
       "address": {
         "street": "123 Test St",
         "city": "Austin",
         "state": "TX",
         "zip": "78701"
       },
       "property_type": "MULTIFAMILY",
       "units": 120,
       "asking_price": 15000000,
       "occupancy": 0.92,
       "source": {
         "type": "BROKER",
         "name": "John Doe",
         "company": "Test Realty"
       }
     }'
   ```

   **Expected Response:**
   ```json
   {
     "id": "deal_xxx",
     "property_name": "Test Apartments",
     "status": "NEW",
     "created_at": "2025-12-25T..."
   }
   ```

2. **Test Validation**
   - [ ] Missing required field → 422 error
   - [ ] Invalid property_type → 422 error
   - [ ] Occupancy > 1.0 → 422 error
   - [ ] Invalid state code → 422 error
   - [ ] Negative units → 422 error

3. **Test Database Creation**
   ```sql
   -- Check Supabase dashboard
   SELECT * FROM deals 
   WHERE property_name = 'Test Apartments';
   ```

4. **Test GET /api/v1/deals**
   ```bash
   curl http://localhost:8000/api/v1/deals
   ```

   **Query Parameters:**
   - `?property_type=MULTIFAMILY`
   - `?status=NEW`
   - `?sort=created_at&order=desc`
   - `?search=Test`

**Expected Result:** Deal creation works with proper validation and database persistence.

---

### Task 1.7: Document Upload UX Prototype ✅

**Status:** Complete  
**File:** `ux-prototypes/document-upload.html`

#### Test Steps:

1. **Open Prototype**
   - Navigate to: http://localhost:8080/document-upload.html

2. **Verify UI Elements**
   - [ ] Drag-and-drop zone visible
   - [ ] File picker button visible
   - [ ] Supported formats listed
   - [ ] File size limit (50MB) shown
   - [ ] Cancel and Extract Data buttons visible

3. **Test Drag-and-Drop**
   - [ ] Drag file over zone → Visual feedback
   - [ ] Drop file → File appears in list
   - [ ] Multiple files → All appear in list

4. **Test File Picker**
   - [ ] Click "Browse" → File picker opens
   - [ ] Select file → File appears in list

5. **Test File List**
   - [ ] Each file shows: name, size, document type dropdown
   - [ ] Remove button works
   - [ ] Status indicators show (uploading, uploaded, error)

6. **Test States**
   - [ ] Empty state (no files)
   - [ ] Uploading state (progress bar)
   - [ ] Uploaded state (checkmark)
   - [ ] Error state (error message)

**Expected Result:** Prototype shows all UI elements and states correctly.

---

### Task 1.8: Document Upload UI Component ✅

**Status:** Complete  
**File:** `ux-prototypes/document-upload.html` (styled)

#### Test Steps:

1. **Visual Inspection**
   - [ ] Minimal Pro theme applied
   - [ ] Drag-and-drop zone styled correctly
   - [ ] File list styled with proper spacing
   - [ ] Buttons styled correctly
   - [ ] Status indicators use proper colors

2. **Test Hover States**
   - [ ] Hover over drag zone → Border color changes
   - [ ] Hover over buttons → Background changes
   - [ ] Hover over file items → Subtle highlight

3. **Test Responsive Design**
   - [ ] Mobile viewport → Layout adapts
   - [ ] Touch targets are 44pt minimum
   - [ ] Text is readable on mobile

**Expected Result:** Styled component matches Minimal Pro design language.

---

### Task 1.9: Document Upload React Component ✅

**Status:** Complete  
**File:** `src/components/upload/DocumentUpload.tsx`

#### Test Steps:

1. **Navigate to Upload**
   - Navigate to deal detail page
   - Click "Upload Documents" or similar

2. **Test Drag-and-Drop**
   - [ ] Drag file over zone → Visual feedback
   - [ ] Drop file → File added to list
   - [ ] Multiple files → All added

3. **Test File Validation**
   - [ ] Upload PDF → Accepted
   - [ ] Upload XLSX → Accepted
   - [ ] Upload PNG → Accepted
   - [ ] Upload .txt → Rejected with error
   - [ ] Upload 60MB file → Rejected (50MB limit)

4. **Test Document Type Selection**
   - [ ] Select document type from dropdown
   - [ ] All 22 document types available
   - [ ] Selection persists

5. **Test Upload Process**
   - [ ] Click "Extract Data" or "Upload"
   - [ ] Progress bar shows
   - [ ] API call to POST /api/v1/deals/{deal_id}/documents
   - [ ] Success state shows
   - [ ] Extraction job ID received

6. **Test Error Handling**
   - [ ] Network error → Error message
   - [ ] File too large → Error message
   - [ ] Invalid file type → Error message
   - [ ] Server error → Error message

**Expected Result:** Component uploads files and initiates extraction.

---

### Task 1.10: Backend API - Document Upload Endpoint ✅

**Status:** Complete  
**File:** `backend/api/documents.py`

#### Test Steps:

1. **Test POST /api/v1/deals/{deal_id}/documents**

   **Request:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/deals/{deal_id}/documents \
     -F "files=@test-document.pdf" \
     -F "files=@test-rent-roll.xlsx"
   ```

   **Expected Response:**
   ```json
   {
     "upload_id": "upload_xxx",
     "documents": [
       {
         "id": "doc_xxx",
         "filename": "test-document.pdf",
         "size_bytes": 1234567,
         "status": "PROCESSING",
         "document_type": null
       }
     ],
     "extraction_job_id": "job_xxx"
   }
   ```

2. **Test File Validation**
   - [ ] Upload PDF → Accepted
   - [ ] Upload XLSX → Accepted
   - [ ] Upload .txt → 400 error
   - [ ] Upload 60MB file → 400 error (50MB limit)

3. **Test Database Records**
   ```sql
   -- Check documents table
   SELECT * FROM documents 
   WHERE deal_id = '{deal_id}';
   
   -- Check extraction_jobs table
   SELECT * FROM extraction_jobs 
   WHERE deal_id = '{deal_id}';
   ```

4. **Test Storage Upload**
   - [ ] Verify file uploaded to Supabase Storage
   - [ ] Check storage path in database
   - [ ] Verify file can be downloaded

**Expected Result:** Documents upload successfully and extraction jobs are created.

---

### Task 1.11: File Storage Service ✅

**Status:** Complete  
**File:** `backend/services/storage.py`

#### Test Steps:

1. **Test Storage Configuration**
   ```python
   # In Python shell or test script
   from services.storage import StorageService
   
   service = StorageService()
   # Should initialize with correct provider
   ```

2. **Test Upload**
   ```python
   with open('test-file.pdf', 'rb') as f:
       file_content = f.read()
   
   path = service.upload(
       file_content=file_content,
       filename='test-file.pdf',
       folder='documents',
       metadata={'deal_id': 'test'}
   )
   # Should return storage path
   ```

3. **Test Download**
   ```python
   file_content = service.download(path)
   # Should return file bytes
   ```

4. **Test Pre-signed URL**
   ```python
   url = service.generate_presigned_url(path, expiry_seconds=900)
   # Should return URL valid for 15 minutes
   ```

5. **Test Delete**
   ```python
   service.delete(path)
   # Should remove file from storage
   ```

**Expected Result:** Storage service works with configured provider (Supabase/S3).

---

### Task 1.12: Document Classification Service ✅

**Status:** Complete  
**File:** `backend/services/classification.py`

#### Test Steps:

1. **Test Classification**
   ```python
   from services.classification import ClassificationService
   
   service = ClassificationService()
   
   with open('test-om.pdf', 'rb') as f:
       file_content = f.read()
   
   result = await service.classify(
       file_content=file_content,
       filename='test-om.pdf',
       mime_type='application/pdf'
   )
   
   # Expected:
   # {
   #   "document_type": "OFFERING_MEMORANDUM",
   #   "confidence": 95,
   #   "reasoning": "...",
   #   "cost_cents": 0.05
   # }
   ```

2. **Test All Document Types**
   - [ ] Test with OM → Returns OFFERING_MEMORANDUM
   - [ ] Test with T-12 → Returns T12_STATEMENT
   - [ ] Test with Rent Roll → Returns RENT_ROLL
   - [ ] Test with unknown → Returns OTHER

3. **Test Caching**
   - [ ] First classification → Not cached
   - [ ] Second classification (same file) → Cached
   - [ ] Cache hit → Lower cost

4. **Test Error Handling**
   - [ ] Invalid file → Error handled
   - [ ] API error → Retry logic works
   - [ ] Missing API key → Error message

**Expected Result:** Documents classified correctly with confidence scores.

---

### Task 1.13: LLM Router ✅

**Status:** Complete  
**File:** `backend/services/llm_router.py`

#### Test Steps:

1. **Test Router Decision**
   ```python
   from services.llm_router import get_router, DocumentComplexity
   
   router = get_router()
   
   decision = router.get_router_decision(
       document_type="OFFERING_MEMORANDUM",
       document_complexity=DocumentComplexity.STANDARD,
       page_count=25,
       user_tier=UserTier.STANDARD
   )
   
   # Expected: Model selection with reasoning
   ```

2. **Test Model Selection Logic**
   - [ ] Simple OM (<50 pages) → Gemini Flash
   - [ ] Complex OM (>50 pages) → Claude Haiku
   - [ ] Very complex (poor quality) → Claude Sonnet
   - [ ] Premium user → Higher tier models

3. **Test Cost Estimation**
   - [ ] Cost calculated correctly
   - [ ] Cost tracked in router stats
   - [ ] Cost logged

4. **Test Router Stats**
   ```python
   stats = router.router_stats
   # Should show total decisions, model counts, total cost
   ```

**Expected Result:** Router selects appropriate model based on document characteristics.

---

### Task 1.14: OM Extraction Service ✅

**Status:** Complete  
**File:** `backend/services/extraction/om_extraction.py`

#### Test Steps:

1. **Test OM Extraction**
   ```python
   from services.extraction.om_extraction import get_om_extraction_service
   
   service = get_om_extraction_service()
   
   with open('test-om.pdf', 'rb') as f:
       file_content = f.read()
   
   result = await service.extract(
       file_content=file_content,
       filename='test-om.pdf',
       mime_type='application/pdf',
       document_type='OFFERING_MEMORANDUM'
   )
   
   # Expected:
   # {
   #   "extracted_data": {
   #     "property_name": {...},
   #     "unit_mix": [...],
   #     "financial_data": {...},
   #     "investment_highlights": [...]
   #   },
   #   "overall_confidence": 87,
   #   "fields_requiring_review": ["year_built"],
   #   "cost_dollars": 0.15
   # }
   ```

2. **Test Extracted Fields**
   - [ ] Property information extracted
   - [ ] Unit mix extracted (type, count, SF, rent)
   - [ ] Financial data extracted (price, NOI, cap rate)
   - [ ] Investment highlights extracted

3. **Test Confidence Scores**
   - [ ] Each field has confidence score
   - [ ] Overall confidence calculated
   - [ ] Low confidence fields identified

4. **Test Error Handling**
   - [ ] Invalid document → Error handled
   - [ ] API failure → Retry logic works
   - [ ] Fallback to alternative model works

**Expected Result:** OM data extracted correctly with confidence scores.

---

### Task 1.15: T-12 Extraction Service ✅

**Status:** Complete  
**File:** `backend/services/extraction/t12_extraction.py`

#### Test Steps:

1. **Test T-12 Extraction**
   ```python
   from services.extraction.t12_extraction import get_t12_extraction_service
   
   service = get_t12_extraction_service()
   
   with open('test-t12.xlsx', 'rb') as f:
       file_content = f.read()
   
   result = await service.extract(
       file_content=file_content,
       filename='test-t12.xlsx',
       mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
       number_of_units=120
   )
   ```

2. **Test Revenue Line Items**
   - [ ] Gross Potential Rent extracted
   - [ ] Loss to Lease extracted
   - [ ] Vacancy Loss extracted
   - [ ] Concessions extracted
   - [ ] Bad Debt extracted
   - [ ] Other Income extracted
   - [ ] Effective Gross Income calculated

3. **Test Expense Line Items**
   - [ ] Property Taxes extracted
   - [ ] Insurance extracted
   - [ ] Utilities extracted (itemized if available)
   - [ ] Repairs & Maintenance extracted
   - [ ] Payroll extracted
   - [ ] Management Fee extracted
   - [ ] Total Operating Expenses calculated

4. **Test Calculated Metrics**
   - [ ] NOI calculated (EGI - Expenses)
   - [ ] Expense Ratio calculated
   - [ ] Per-unit metrics calculated (if units provided)

5. **Test Monthly vs Annual**
   - [ ] Monthly data converted to annual (×12)
   - [ ] Annual data used as-is

**Expected Result:** T-12 data extracted correctly with all line items.

---

### Task 1.16: Rent Roll Extraction Service ✅

**Status:** Complete  
**File:** `backend/services/extraction/rent_roll_extraction.py`

#### Test Steps:

1. **Test Rent Roll Extraction**
   ```python
   from services.extraction.rent_roll_extraction import get_rent_roll_extraction_service
   
   service = get_rent_roll_extraction_service()
   
   with open('test-rent-roll.xlsx', 'rb') as f:
       file_content = f.read()
   
   result = await service.extract(
       file_content=file_content,
       filename='test-rent-roll.xlsx',
       mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
   )
   ```

2. **Test Unit-Level Data**
   - [ ] Unit number extracted
   - [ ] Unit type extracted
   - [ ] Square footage extracted
   - [ ] Bedrooms/bathrooms extracted
   - [ ] Current rent extracted
   - [ ] Market rent extracted (if available)
   - [ ] Lease dates extracted
   - [ ] Tenant status extracted

3. **Test Aggregated Metrics**
   - [ ] Total units calculated
   - [ ] Occupied/vacant units calculated
   - [ ] Occupancy rate calculated
   - [ ] Average rent calculated
   - [ ] Rent per square foot calculated
   - [ ] Loss to lease calculated (if market rent available)
   - [ ] Delinquency rate calculated

4. **Test Data Quality**
   - [ ] All units processed
   - [ ] Confidence scores for each unit
   - [ ] Missing data handled gracefully

**Expected Result:** Rent roll data extracted with unit-level and aggregated metrics.

---

### Task 1.17: Extraction Job Processor ✅

**Status:** Complete  
**File:** `backend/services/extraction/extraction_processor.py`

#### Test Steps:

1. **Test Full Extraction Workflow**
   ```python
   from services.extraction.extraction_processor import get_extraction_processor
   
   processor = get_extraction_processor()
   
   result = await processor.process_extraction_job(
       job_id='job_xxx',
       deal_id='deal_xxx',
       document_ids=['doc_xxx']
   )
   ```

2. **Test Workflow Steps**
   - [ ] Job status updated to PROCESSING
   - [ ] Document downloaded from storage
   - [ ] Document classified
   - [ ] Appropriate extraction service called
   - [ ] Data extracted with confidence scores
   - [ ] Extraction data stored in cache
   - [ ] Document record updated
   - [ ] Job status updated to COMPLETED

3. **Test Multiple Documents**
   - [ ] Process multiple documents in one job
   - [ ] All documents processed
   - [ ] Overall confidence calculated
   - [ ] Fields requiring review aggregated

4. **Test Error Handling**
   - [ ] Document download failure → Job marked FAILED
   - [ ] Classification failure → Job marked FAILED
   - [ ] Extraction failure → Job marked FAILED
   - [ ] Partial failure → Some documents succeed

5. **Test Database Updates**
   ```sql
   -- Check extraction_job status
   SELECT status, overall_confidence, fields_requiring_review
   FROM extraction_jobs
   WHERE id = 'job_xxx';
   
   -- Check extraction_data_cache
   SELECT extracted_data, extraction_confidence
   FROM extraction_data_cache
   WHERE document_id = 'doc_xxx';
   ```

**Expected Result:** Full extraction workflow processes documents correctly.

---

### Task 1.18: Extraction Status API Endpoint ✅

**Status:** Complete  
**File:** `backend/api/extraction.py`

#### Test Steps:

1. **Test GET /api/v1/extraction-jobs/{job_id}**

   **Request:**
   ```bash
   curl http://localhost:8000/api/v1/extraction-jobs/{job_id}
   ```

   **Expected Response:**
   ```json
   {
     "job_id": "job_xxx",
     "status": "COMPLETED",
     "started_at": "2025-12-25T10:30:05Z",
     "completed_at": "2025-12-25T10:30:35Z",
     "documents": [
       {
         "id": "doc_xxx",
         "document_type": "OFFERING_MEMORANDUM",
         "classification_confidence": 98,
         "extraction_status": "COMPLETED"
       }
     ],
     "extracted_data": {...},
     "fields_requiring_review": ["year_built", "property_class"],
     "overall_confidence": 87,
     "cost_cents": 150
   }
   ```

2. **Test Different Job Statuses**
   - [ ] PENDING → Shows pending status
   - [ ] PROCESSING → Shows processing status
   - [ ] COMPLETED → Shows extracted data
   - [ ] FAILED → Shows error message

3. **Test Error Handling**
   - [ ] Invalid job_id → 404 error
   - [ ] Missing job → 404 error

4. **Test Frontend Integration**
   - [ ] Frontend polls this endpoint
   - [ ] Status updates in real-time
   - [ ] Extracted data displayed

**Expected Result:** Endpoint returns extraction job status with all details.

---

### Task 1.19: Extraction Review UX Prototype ✅

**Status:** Complete  
**File:** `ux-prototypes/extraction-review.html`

#### Test Steps:

1. **Open Prototype**
   - Navigate to: http://localhost:8080/extraction-review.html

2. **Verify Layout**
   - [ ] Split-view: document viewer (left) + form (right)
   - [ ] Document viewer shows PDF preview
   - [ ] Form shows extracted fields

3. **Test Confidence Indicators**
   - [ ] High confidence (90+) → Green checkmark
   - [ ] Medium confidence (70-89) → Yellow highlight
   - [ ] Low confidence (50-69) → Orange highlight
   - [ ] Very low (<50) → Red highlight

4. **Test Form Fields**
   - [ ] All extracted fields displayed
   - [ ] Fields are editable
   - [ ] Source/page location shown
   - [ ] Review notes shown for low-confidence fields

5. **Test States**
   - [ ] Loading state
   - [ ] Populated state
   - [ ] Error state

**Expected Result:** Prototype shows review interface with all elements.

---

### Task 1.20: Extraction Review UI Component ✅

**Status:** Complete  
**File:** `ux-prototypes/extraction-review.html` (styled)

#### Test Steps:

1. **Visual Inspection**
   - [ ] Minimal Pro theme applied
   - [ ] Split-view layout styled correctly
   - [ ] Confidence badges styled with proper colors
   - [ ] Form fields styled correctly
   - [ ] Buttons styled correctly

2. **Test Responsive Design**
   - [ ] Desktop: Side-by-side layout
   - [ ] Mobile: Stacked layout
   - [ ] Touch targets are 44pt minimum

**Expected Result:** Styled component matches Minimal Pro design language.

---

### Task 1.21: Extraction Review React Component ✅

**Status:** Complete  
**File:** `src/components/review/ExtractionReview.tsx`

#### Test Steps:

1. **Navigate to Review Page**
   - Navigate to deal detail page
   - Click "Review Extraction" or similar
   - Or navigate to: `/deals/{deal_id}/review/{job_id}`

2. **Test Data Loading**
   - [ ] Component fetches extraction job status
   - [ ] Loading state shows
   - [ ] Extracted data displays
   - [ ] Error state handles failures

3. **Test Field Display**
   - [ ] All extracted fields shown
   - [ ] Confidence indicators display correctly
   - [ ] Source locations shown
   - [ ] Fields requiring review highlighted

4. **Test Field Editing**
   - [ ] Edit property name → Value updates
   - [ ] Edit year built → Value updates
   - [ ] Edit financial data → Value updates
   - [ ] Corrections tracked

5. **Test Document Viewer**
   - [ ] PDF displays in iframe
   - [ ] Page navigation works
   - [ ] Page number input works

6. **Test Actions**
   - [ ] "Save Changes" → Saves corrections
   - [ ] "Looks Good ✓" → Confirms extraction
   - [ ] API call to POST /api/v1/deals/{deal_id}/confirm-extraction

**Expected Result:** Component displays extraction data and allows review/correction.

---

### Task 1.22: Confirm Extraction API Endpoint ✅

**Status:** Complete  
**File:** `backend/api/extraction.py`

#### Test Steps:

1. **Test POST /api/v1/deals/{deal_id}/confirm-extraction**

   **Request:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/deals/{deal_id}/confirm-extraction \
     -H "Content-Type: application/json" \
     -d '{
       "corrections": {
         "year_built.value": 1986,
         "property_class.value": "B"
       },
       "confirmed": true
     }'
   ```

   **Expected Response:**
   ```json
   {
     "deal_id": "deal_xxx",
     "status": "READY_FOR_SCREENING",
     "corrections_applied": 2,
     "next_step": "screening"
   }
   ```

2. **Test Corrections Application**
   - [ ] Corrections applied to deal record
   - [ ] Deal stage updated to READY_FOR_SCREENING
   - [ ] Corrections stored in extraction_corrections table

3. **Test Database Updates**
   ```sql
   -- Check deal updates
   SELECT year_built, property_class, stage
   FROM deals
   WHERE id = 'deal_xxx';
   
   -- Check corrections table
   SELECT field_path, original_value, corrected_value
   FROM extraction_corrections
   WHERE extraction_job_id = 'job_xxx';
   ```

4. **Test Error Handling**
   - [ ] Invalid deal_id → 404 error
   - [ ] No extraction job → 404 error
   - [ ] Job not completed → 400 error

**Expected Result:** Corrections applied and deal status updated.

---

## Integration Testing

### End-to-End Workflow: Manual Entry → Upload → Extract → Review

#### Test Scenario 1: Complete Deal Intake Flow

1. **Create Deal Manually**
   - Navigate to: http://localhost:5173/#intake
   - Fill out manual entry form
   - Submit form
   - Verify deal created in database

2. **Upload Documents**
   - Navigate to deal detail page
   - Click "Upload Documents"
   - Upload OM, T-12, and Rent Roll
   - Verify documents uploaded
   - Verify extraction job created

3. **Wait for Extraction** (or trigger manually)
   - Poll extraction status endpoint
   - Verify extraction completes
   - Verify extracted data in cache

4. **Review Extraction**
   - Navigate to extraction review page
   - Review all extracted fields
   - Make corrections if needed
   - Confirm extraction

5. **Verify Final State**
   - Deal stage = READY_FOR_SCREENING
   - All corrections applied
   - Deal data complete

#### Test Scenario 2: Document Upload → Classification → Extraction

1. **Upload Document**
   - Upload OM document
   - Verify document stored

2. **Trigger Classification**
   - Extraction processor classifies document
   - Verify classification result

3. **Trigger Extraction**
   - Extraction processor routes to OM extraction service
   - Verify extraction completes
   - Verify data extracted

4. **Verify Results**
   - Check extraction job status
   - Check extracted data
   - Check confidence scores

---

## Performance Testing

### Test Response Times

1. **API Endpoints**
   - [ ] POST /api/v1/deals < 500ms
   - [ ] GET /api/v1/deals < 200ms
   - [ ] POST /api/v1/deals/{id}/documents < 2s
   - [ ] GET /api/v1/extraction-jobs/{id} < 200ms

2. **Extraction Services**
   - [ ] Document classification < 10s
   - [ ] OM extraction < 60s
   - [ ] T-12 extraction < 30s
   - [ ] Rent Roll extraction < 30s

3. **Frontend**
   - [ ] Page load < 2s
   - [ ] Form submission < 1s
   - [ ] File upload progress updates smoothly

---

## Error Handling Testing

### Test Error Scenarios

1. **Network Errors**
   - [ ] Disconnect network → Error message shown
   - [ ] Slow network → Loading states work
   - [ ] Timeout → Error handled

2. **Validation Errors**
   - [ ] Invalid form data → Field-specific errors
   - [ ] Invalid file type → Clear error message
   - [ ] File too large → Clear error message

3. **Server Errors**
   - [ ] 500 error → Generic error message
   - [ ] 404 error → Not found message
   - [ ] 422 error → Validation errors displayed

---

## Browser Compatibility Testing

### Test in Multiple Browsers

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

### Test Responsive Design

- [ ] Mobile (375px)
- [ ] Tablet (768px)
- [ ] Desktop (1920px)

---

## Security Testing

### Test Security Measures

1. **File Upload Security**
   - [ ] Malicious file types rejected
   - [ ] File size limits enforced
   - [ ] Files stored securely

2. **API Security**
   - [ ] CORS configured correctly
   - [ ] Input validation on all endpoints
   - [ ] SQL injection prevention (Prisma)

3. **Data Privacy**
   - [ ] Sensitive data not logged
   - [ ] Tenant names handled appropriately

---

## Test Data

### Sample Files for Testing

Create test files in `tests/fixtures/`:

1. **OM Document**: `test-om.pdf` (sample offering memorandum)
2. **T-12 Statement**: `test-t12.xlsx` (sample trailing 12)
3. **Rent Roll**: `test-rent-roll.xlsx` (sample rent roll)

### Sample API Requests

See `tests/fixtures/` for example request/response JSON files.

---

## Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check Python version
   - Check dependencies installed
   - Check environment variables

2. **Frontend not loading**
   - Check Node.js version
   - Check dependencies installed
   - Check browser console for errors

3. **API calls failing**
   - Check backend is running
   - Check CORS configuration
   - Check API URL in frontend

4. **Extraction not working**
   - Check API keys (Gemini, Anthropic)
   - Check storage configuration
   - Check database connections

---

## Next Steps After Testing

1. **Fix any bugs found**
2. **Optimize performance issues**
3. **Improve error messages**
4. **Add missing features**
5. **Document any issues**

---

---

## Tasks 1.23-1.25: Chat Mode

### Task 1.23: Chat Mode UX Prototype ✅

**Status:** Complete  
**File:** `ux-prototypes/chat-mode.html`

#### Test Steps:

1. **Open Prototype**
   - Navigate to: http://localhost:8080/chat-mode.html
   - Or open file directly in browser

2. **Verify UI Elements**
   - [ ] Header with mode toggle (Dashboard ↔ Chat)
   - [ ] Extracted deal summary card (if deal exists)
   - [ ] Chat messages area (scrollable)
   - [ ] Input area with text input
   - [ ] File upload button
   - [ ] Send button

3. **Test Empty State**
   - [ ] Welcome message displays
   - [ ] Example prompts shown
   - [ ] File upload hint visible

4. **Test Chat Interface**
   - [ ] AI messages display on left
   - [ ] User messages display on right
   - [ ] Message bubbles styled correctly
   - [ ] Timestamps shown
   - [ ] Typing indicator works

5. **Test File Upload**
   - [ ] Drag and drop zone visible when dragging
   - [ ] File picker accessible
   - [ ] File attachments display in messages
   - [ ] Upload progress shown

6. **Test States**
   - [ ] Empty state (no messages)
   - [ ] Loading state (typing indicator)
   - [ ] Populated state (conversation)
   - [ ] Error state (error message)

**Expected Result:** Prototype shows all chat interface elements correctly.

---

### Task 1.24: Chat Mode UI Component ✅

**Status:** Complete  
**File:** `ux-prototypes/chat-mode.html` (styled)

#### Test Steps:

1. **Visual Inspection**
   - [ ] Minimal Pro theme applied
   - [ ] Chat bubbles styled correctly:
     - User: YinMn Blue background, white text
     - AI: Background tertiary, dark text
   - [ ] Mode toggle styled
   - [ ] Input area styled
   - [ ] Extracted summary card styled

2. **Test Responsive Design**
   - [ ] Mobile: Full-width chat
   - [ ] Tablet: 60% chat width
   - [ ] Desktop: 50% chat width
   - [ ] Touch targets are 44pt minimum

3. **Test Interactions**
   - [ ] Hover states on buttons
   - [ ] Focus states on input
   - [ ] Active states on mode toggle

**Expected Result:** Styled component matches Minimal Pro design language.

---

### Task 1.25: Chat Mode React Component ✅

**Status:** Complete  
**File:** `src/components/chat/ChatMode.tsx`

#### Test Steps:

1. **Navigate to Chat Mode**
   - Add route to App.tsx or navigate directly
   - Or integrate mode toggle in header

2. **Test Empty State**
   - [ ] Welcome message displays
   - [ ] Example prompts clickable
   - [ ] Clicking prompt fills input
   - [ ] Input focuses automatically

3. **Test Message Sending**
   - [ ] Type message in input
   - [ ] Press Enter or click Send
   - [ ] Message appears in chat
   - [ ] AI response appears (simulated)
   - [ ] Typing indicator shows while loading

4. **Test File Upload**
   - [ ] Click attach button
   - [ ] File menu appears
   - [ ] Select "Browse Files"
   - [ ] File picker opens
   - [ ] File uploads and appears in message
   - [ ] Upload progress shown

5. **Test Drag and Drop**
   - [ ] Drag file over chat area
   - [ ] Drop zone highlights
   - [ ] Drop file
   - [ ] File uploads automatically

6. **Test Extracted Deal Summary**
   - [ ] Summary card appears when dealId provided
   - [ ] Shows property name, address, units, price
   - [ ] "View Full Details" button works
   - [ ] "Edit" button works

7. **Test Chat History**
   - [ ] Messages persist in localStorage
   - [ ] Reload page → Messages still there
   - [ ] Different deals have separate histories

8. **Test Mode Toggle**
   - [ ] Click "Dashboard" → Switches to dashboard
   - [ ] Chat history preserved
   - [ ] Can switch back to Chat

9. **Test Error Handling**
   - [ ] Network error → Error message
   - [ ] File upload error → Error indicator
   - [ ] Invalid file type → Error message

10. **Test Mobile Experience**
    - [ ] Layout adapts to mobile
    - [ ] Touch targets are 44pt
    - [ ] Keyboard doesn't cover input
    - [ ] Scrolling works smoothly

**Expected Result:** Chat mode component works with message history, file upload, and mode switching.

---

## Updated Integration Testing

### End-to-End Workflow: Chat Mode → Deal Creation

#### Test Scenario 3: Chat Mode Deal Intake

1. **Start Chat Mode**
   - Navigate to chat mode
   - See empty state with example prompts

2. **Create Deal via Chat**
   - Type: "I have a 96-unit property in Austin asking $12.5M"
   - AI responds asking for property name
   - Provide property name
   - AI asks for more details

3. **Upload Documents via Chat**
   - Click attach button
   - Upload OM document
   - AI processes and extracts data
   - Extracted data shown in summary card

4. **Review and Confirm**
   - Review extracted data in summary card
   - Continue conversation or switch to dashboard
   - Deal created and saved

---

**Testing Guide Version:** 1.1  
**Last Updated:** December 2025  
**Tasks Covered:** 1.1-1.25

