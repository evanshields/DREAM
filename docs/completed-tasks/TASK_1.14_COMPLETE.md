# Task 1.14 Complete: OM Extraction Service ✅

**Status:** ✅ Complete  
**Date:** December 2025  
**PRD Reference:** Sections 5.2, 6.1, 6.2  
**Agent:** Backend Engineer

---

## What Was Completed

### 1. **OM Extraction Service** (`backend/services/extraction/om_extraction.py`)

#### Core Implementation
- ✅ Created `backend/services/extraction/om_extraction.py` with `OMExtractionService` class
- ✅ Uses LLM router to select optimal model (Flash for simple, Haiku for complex)
- ✅ Implements extraction prompt from PRD Section 6.2
- ✅ Extracts all fields from PRD Section 5.2
- ✅ Returns structured JSON with confidence scores
- ✅ Handles extraction errors with retry logic
- ✅ Tracks extraction costs
- ✅ Logs extraction results

#### Features Implemented

**LLM Router Integration:**
- ✅ Uses router to select model based on document complexity
- ✅ Supports Gemini 1.5 Flash (simple/standard OMs)
- ✅ Supports Claude 3.5 Haiku (complex OMs)
- ✅ Automatic model selection based on page count, user tier, confidence

**Property Information Extraction (PRD Section 5.2):**
- ✅ Property name
- ✅ Street address
- ✅ City, State, ZIP
- ✅ Year built
- ✅ Number of units
- ✅ Total square footage
- ✅ Lot size (optional)
- ✅ Property class (optional)
- ✅ Parking spaces (optional)
- ✅ Amenities (optional)

**Unit Mix Extraction (PRD Section 5.2):**
- ✅ Unit type (Studio, 1BR, 2BR, etc.)
- ✅ Unit count per type
- ✅ Average square footage per unit type
- ✅ Market rent per unit type
- ✅ In-place rent per unit type (if available)

**Financial Data Extraction (PRD Section 5.2):**
- ✅ Asking price
- ✅ Price per unit
- ✅ In-place NOI
- ✅ Pro forma NOI
- ✅ In-place cap rate
- ✅ Pro forma cap rate
- ✅ Gross Potential Rent
- ✅ Effective Gross Income
- ✅ Operating Expenses

**Investment Highlights Extraction (PRD Section 5.2):**
- ✅ Investment highlights (top 5-10 selling points)
- ✅ Value-add opportunities (if mentioned)
- ✅ Location highlights (if mentioned)
- ✅ Market overview (if mentioned)

**Confidence Scoring:**
- ✅ Confidence score (0-100) for each field
- ✅ Source/page location for each field
- ✅ Overall confidence calculation
- ✅ Fields requiring review identification (confidence < 70%)

**Error Handling:**
- ✅ Retry logic (3 attempts with exponential backoff)
- ✅ Graceful error handling for API failures
- ✅ JSON parsing error handling
- ✅ Model fallback (unknown model → Claude Haiku)

**Cost Tracking:**
- ✅ Cost calculation based on model and token usage
- ✅ Cost in dollars returned in result
- ✅ Token estimation for cost calculation

**Logging:**
- ✅ Router decision logging
- ✅ Extraction completion logging
- ✅ Error logging with context

---

## File Structure

```
backend/services/extraction/
├── __init__.py          ✅ Complete
└── om_extraction.py     ✅ Complete
```

---

## Key Features

### Model Selection

The service uses the LLM router to automatically select the optimal model:

- **Simple OMs** (<20 pages) → Gemini 1.5 Flash (cost-effective)
- **Complex OMs** (>=20 pages) → Claude 3.5 Haiku (better context handling)
- **Premium users** → Default to Claude 3.5 Haiku
- **Low confidence retry** → Upgrade to Claude 3.5 Haiku

### Extraction Prompt

Uses the extraction prompt from PRD Section 6.2, which instructs the LLM to:
- Extract all required fields
- Provide confidence scores (0-100)
- Include source/page location
- Return structured JSON

### Response Format

Each extracted field follows this structure:
```json
{
  "property_name": {
    "value": "Oak Creek Apartments",
    "confidence": 95,
    "source": "Page 1"
  }
}
```

Arrays (like unit_mix) follow a similar structure:
```json
{
  "unit_mix": [
    {
      "unit_type": "1BR",
      "unit_count": 60,
      "avg_sf": 750,
      "market_rent": 1200,
      "in_place_rent": 1150
    }
  ]
}
```

### Confidence Scoring

- **High confidence (90-100)**: Green checkmark, optional review
- **Medium confidence (70-89)**: Yellow highlight, review recommended
- **Low confidence (<70)**: Orange highlight, review required

Fields with confidence < 70% are automatically flagged in `fields_requiring_review`.

---

## Usage Examples

### Basic Extraction
```python
from services.extraction.om_extraction import get_om_extraction_service
from services.llm_router import UserTier

service = get_om_extraction_service()

with open("oak_creek_om.pdf", "rb") as f:
    file_content = f.read()

result = await service.extract(
    file_content=file_content,
    filename="oak_creek_om.pdf",
    mime_type="application/pdf",
    page_count=25,
    user_tier=UserTier.STANDARD,
)

print(f"Extracted: {result['extracted_data']['property_name']['value']}")
print(f"Confidence: {result['overall_confidence']}%")
print(f"Cost: ${result['cost_dollars']:.4f}")
print(f"Model used: {result['model_used']}")
```

### With Retry on Low Confidence
```python
result = await service.extract(
    file_content=file_content,
    filename="oak_creek_om.pdf",
    user_tier=UserTier.STANDARD,
)

# If confidence is low, retry with explicit low confidence flag
if result['overall_confidence'] < 70:
    result = await service.extract(
        file_content=file_content,
        filename="oak_creek_om.pdf",
        previous_confidence=result['overall_confidence'],
        user_tier=UserTier.STANDARD,
    )
```

### Premium User (Always Haiku)
```python
result = await service.extract(
    file_content=file_content,
    filename="oak_creek_om.pdf",
    user_tier=UserTier.PREMIUM,  # Will default to Haiku
)
```

---

## API Integration

### With Extraction Processor (Task 1.17)

The extraction processor will use this service:

```python
from services.extraction.om_extraction import get_om_extraction_service

om_service = get_om_extraction_service()

# For each OM document
if document.document_type == "OFFERING_MEMORANDUM":
    extraction_result = await om_service.extract(
        file_content=document.content,
        filename=document.filename,
        mime_type=document.mime_type,
        page_count=document.page_count,
        user_tier=UserTier(document.user.tier),
    )
    
    # Store extraction result
    await store_extraction_result(document.id, extraction_result)
```

---

## Response Structure

```python
{
    "extracted_data": {
        "property_name": {"value": "...", "confidence": 95, "source": "Page 1"},
        "street_address": {"value": "...", "confidence": 90, "source": "Page 2"},
        "city": {"value": "...", "confidence": 90, "source": "Page 2"},
        "state": {"value": "TX", "confidence": 90, "source": "Page 2"},
        "zip_code": {"value": "78701", "confidence": 90, "source": "Page 2"},
        "year_built": {"value": 1985, "confidence": 80, "source": "Page 3"},
        "number_of_units": {"value": 120, "confidence": 90, "source": "Page 3"},
        "total_sf": {"value": 120000, "confidence": 80, "source": "Page 3"},
        "unit_mix": [
            {
                "unit_type": "1BR",
                "unit_count": 60,
                "avg_sf": 750,
                "market_rent": 1200,
                "in_place_rent": 1150
            }
        ],
        "asking_price": {"value": 15000000, "confidence": 95, "source": "Page 1"},
        "in_place_noi": {"value": 900000, "confidence": 85, "source": "Page 6"},
        "pro_forma_noi": {"value": 1100000, "confidence": 85, "source": "Page 6"},
        "investment_highlights": {
            "value": ["Prime location", "Value-add opportunity"],
            "confidence": 75,
            "source": "Page 1"
        },
        # ... more fields
    },
    "model_used": "gemini-1.5-flash",
    "router_reasoning": "Standard document: Use cost-effective Gemini 1.5 Flash",
    "cost_dollars": 0.005,
    "overall_confidence": 87,
    "fields_requiring_review": ["property_class", "lot_size"],
    "extraction_timestamp": "2025-12-20T10:30:35Z"
}
```

---

## PRD Compliance

✅ **Section 5.2 Requirements Met:**
- Property information extraction ✅
- Unit mix extraction ✅
- Financial data extraction ✅
- Investment highlights extraction ✅
- All fields with confidence thresholds ✅

✅ **Section 6.1 Requirements Met:**
- Uses LLM router for model selection ✅
- Supports Flash for simple OMs ✅
- Supports Haiku for complex OMs ✅
- Cost tracking ✅

✅ **Section 6.2 Requirements Met:**
- Uses extraction prompt from PRD ✅
- Returns structured JSON with confidence scores ✅
- Includes source/page location ✅
- Handles missing fields gracefully ✅

---

## Configuration

### Environment Variables Required

```bash
# Gemini API (for Flash model)
GEMINI_API_KEY="your-gemini-api-key"

# Claude API (for Haiku model)
ANTHROPIC_API_KEY="sk-ant-your-key"
```

### Dependencies

```bash
pip install google-generativeai anthropic
```

---

## Error Handling

The service handles various error scenarios:

1. **API Failures**: Retries up to 3 times with exponential backoff
2. **JSON Parsing Errors**: Logs error and raises ValueError
3. **Missing API Keys**: Logs warning and raises ValueError on use
4. **Unknown Models**: Falls back to Claude Haiku
5. **Invalid File Types**: Handles gracefully with default MIME type

---

## Cost Estimation

Based on PRD Section 6.1:
- **Simple OM** (<20 pages, Flash): ~$0.005
- **Complex OM** (>=20 pages, Haiku): ~$0.015
- **Very Complex OM** (50+ pages, Haiku): ~$0.025

---

## Next Steps

1. **Integration with Extraction Processor:**
   - Update extraction processor (Task 1.17) to use this service
   - Handle extraction job workflow

2. **Testing:**
   - Create unit tests for extraction service
   - Test with sample OM documents
   - Validate extraction accuracy

3. **Optimization:**
   - Fine-tune extraction prompt based on results
   - Adjust confidence thresholds
   - Optimize cost/quality tradeoff

---

**Task 1.14 Status: ✅ COMPLETE**

The OM Extraction Service is ready for integration with the extraction processor!

