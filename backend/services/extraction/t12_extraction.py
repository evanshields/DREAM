"""
DREAM AI - T-12 (Trailing 12) Extraction Service
Task 1.15: T-12 Extraction Service
PRD Reference: Sections 5.3, 6.2

Extracts revenue line items, expense line items, and calculated metrics
from Trailing 12 operating statements using Gemini 1.5 Flash.
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Use Gemini Flash for T-12 (standard tabular data)
T12_MODEL = "gemini-1.5-flash"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# Cost tracking (per PRD Section 6.1)
GEMINI_FLASH_INPUT_COST_PER_1M = 0.075
GEMINI_FLASH_OUTPUT_COST_PER_1M = 0.30

# ============================================================================
# T-12 EXTRACTION PROMPT (From PRD Section 6.2)
# ============================================================================

T12_EXTRACTION_PROMPT = """
You are a financial data extraction specialist for commercial real estate.

Extract the Trailing 12 operating statement from this document. Identify:

REVENUE:
- Gross Potential Rent (GPR)
- Loss to Lease
- Vacancy Loss
- Concessions
- Bad Debt
- Net Rental Income (calculated: GPR - losses)
- Other Income (itemized if available)
- Utility Reimbursement
- Fee Income (app fees, late fees, etc.)
- Effective Gross Income (EGI)

EXPENSES:
- Property Taxes
- Insurance
- Utilities (itemized if possible: gas, electric, water, trash)
- Repairs & Maintenance
- Contract Services (landscaping, pest control, etc.)
- Payroll (on-site staff)
- Management Fee
- Administrative
- Marketing
- Professional Fees (legal, accounting)
- Turnover Costs
- Replacement Reserves (if included)
- Other Expenses (itemized if available)
- Total Operating Expenses

CALCULATED METRICS:
- Net Operating Income (NOI) = EGI - Total Operating Expenses
- Expense Ratio = Total Operating Expenses ÷ EGI
- Per Unit Revenue = EGI ÷ Number of Units (if units count available)
- Per Unit Expenses = Total Operating Expenses ÷ Number of Units
- Per Unit NOI = NOI ÷ Number of Units

For each line item, provide:
- Annual amount (required)
- Monthly amount (if shown in document)
- Per unit amount (if calculable and units count available)
- Confidence score (0-100)
- Source/page location where found

IMPORTANT:
- Handle both monthly and annual data (convert monthly × 12 if needed)
- If document shows monthly data, convert to annual
- If document shows annual data, use as-is
- For calculated fields, indicate calculation method
- If a field is not found, set value to null and confidence to 0

Respond with JSON matching this schema:
{
  "revenue": {
    "gross_potential_rent": {
      "annual": 1728000,
      "monthly": 144000,
      "per_unit": 14400,
      "confidence": 95,
      "source": "Page 2, Revenue Section"
    },
    "loss_to_lease": {
      "annual": 86400,
      "monthly": 7200,
      "per_unit": 720,
      "confidence": 90,
      "source": "Page 2, Revenue Section"
    },
    "vacancy_loss": {
      "annual": 129600,
      "monthly": 10800,
      "per_unit": 1080,
      "confidence": 90,
      "source": "Page 2, Revenue Section"
    },
    "concessions": {
      "annual": 43200,
      "monthly": 3600,
      "per_unit": 360,
      "confidence": 85,
      "source": "Page 2, Revenue Section"
    },
    "bad_debt": {
      "annual": 21600,
      "monthly": 1800,
      "per_unit": 180,
      "confidence": 80,
      "source": "Page 2, Revenue Section"
    },
    "net_rental_income": {
      "annual": 1440000,
      "monthly": 120000,
      "per_unit": 12000,
      "confidence": 95,
      "source": "Page 2, Calculated"
    },
    "other_income": {
      "annual": 86400,
      "monthly": 7200,
      "per_unit": 720,
      "confidence": 85,
      "source": "Page 2, Revenue Section",
      "itemized": {
        "parking": 43200,
        "storage": 21600,
        "laundry": 21600
      }
    },
    "utility_reimbursement": {
      "annual": 43200,
      "monthly": 3600,
      "per_unit": 360,
      "confidence": 80,
      "source": "Page 2, Revenue Section"
    },
    "fee_income": {
      "annual": 21600,
      "monthly": 1800,
      "per_unit": 180,
      "confidence": 75,
      "source": "Page 2, Revenue Section"
    },
    "effective_gross_income": {
      "annual": 1572000,
      "monthly": 131000,
      "per_unit": 13100,
      "confidence": 95,
      "source": "Page 2, Calculated"
    }
  },
  "expenses": {
    "property_taxes": {
      "annual": 180000,
      "monthly": 15000,
      "per_unit": 1500,
      "confidence": 95,
      "source": "Page 3, Expense Section"
    },
    "insurance": {
      "annual": 48000,
      "monthly": 4000,
      "per_unit": 400,
      "confidence": 90,
      "source": "Page 3, Expense Section"
    },
    "utilities": {
      "annual": 120000,
      "monthly": 10000,
      "per_unit": 1000,
      "confidence": 85,
      "source": "Page 3, Expense Section",
      "itemized": {
        "gas": 36000,
        "electric": 60000,
        "water": 18000,
        "trash": 6000
      }
    },
    "repairs_maintenance": {
      "annual": 96000,
      "monthly": 8000,
      "per_unit": 800,
      "confidence": 90,
      "source": "Page 3, Expense Section"
    },
    "contract_services": {
      "annual": 48000,
      "monthly": 4000,
      "per_unit": 400,
      "confidence": 85,
      "source": "Page 3, Expense Section"
    },
    "payroll": {
      "annual": 144000,
      "monthly": 12000,
      "per_unit": 1200,
      "confidence": 90,
      "source": "Page 3, Expense Section"
    },
    "management_fee": {
      "annual": 47160,
      "monthly": 3930,
      "per_unit": 393,
      "confidence": 90,
      "source": "Page 3, Expense Section",
      "percentage": 3.0
    },
    "administrative": {
      "annual": 24000,
      "monthly": 2000,
      "per_unit": 200,
      "confidence": 85,
      "source": "Page 3, Expense Section"
    },
    "marketing": {
      "annual": 12000,
      "monthly": 1000,
      "per_unit": 100,
      "confidence": 80,
      "source": "Page 3, Expense Section"
    },
    "professional_fees": {
      "annual": 18000,
      "monthly": 1500,
      "per_unit": 150,
      "confidence": 85,
      "source": "Page 3, Expense Section"
    },
    "turnover_costs": {
      "annual": 36000,
      "monthly": 3000,
      "per_unit": 300,
      "confidence": 80,
      "source": "Page 3, Expense Section"
    },
    "replacement_reserves": {
      "annual": 30000,
      "monthly": 2500,
      "per_unit": 250,
      "confidence": 75,
      "source": "Page 3, Expense Section"
    },
    "other_expenses": {
      "annual": 12000,
      "monthly": 1000,
      "per_unit": 100,
      "confidence": 70,
      "source": "Page 3, Expense Section",
      "itemized": {
        "misc": 12000
      }
    },
    "total_operating_expenses": {
      "annual": 762000,
      "monthly": 63500,
      "per_unit": 6350,
      "confidence": 95,
      "source": "Page 3, Calculated"
    }
  },
  "calculated_metrics": {
    "net_operating_income": {
      "annual": 810000,
      "monthly": 67500,
      "per_unit": 6750,
      "confidence": 95,
      "source": "Page 3, Calculated",
      "calculation": "EGI - Total Operating Expenses"
    },
    "expense_ratio": {
      "value": 48.5,
      "confidence": 95,
      "source": "Page 3, Calculated",
      "calculation": "Total Operating Expenses ÷ EGI"
    },
    "per_unit_revenue": {
      "value": 13100,
      "confidence": 90,
      "source": "Calculated",
      "calculation": "EGI ÷ Units"
    },
    "per_unit_expenses": {
      "value": 6350,
      "confidence": 90,
      "source": "Calculated",
      "calculation": "Total Operating Expenses ÷ Units"
    },
    "per_unit_noi": {
      "value": 6750,
      "confidence": 90,
      "source": "Calculated",
      "calculation": "NOI ÷ Units"
    }
  },
  "metadata": {
    "period": "Trailing 12 Months",
    "period_start": "2024-01-01",
    "period_end": "2024-12-31",
    "units_count": 120,
    "data_frequency": "annual"
  }
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code blocks
- All numeric values should be numbers (not strings)
- All confidence scores should be integers 0-100
- If a field is not found, use null for value and 0 for confidence
- Handle monthly vs annual data conversion correctly
- Include itemized breakdowns when available
"""

# ============================================================================
# T-12 EXTRACTION SERVICE
# ============================================================================

class T12ExtractionService:
    """
    T-12 (Trailing 12) extraction service using Gemini 1.5 Flash.
    
    Extracts revenue line items, expense line items, and calculated metrics
    from Trailing 12 operating statements.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize T-12 extraction service.
        
        Args:
            gemini_api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set - T-12 extraction will fail")
        else:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(T12_MODEL)
        
        logger.info(f"Initialized T12ExtractionService with model: {T12_MODEL}")
    
    def _extract_with_gemini(
        self,
        file_content: bytes,
        mime_type: str,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Extract data using Gemini API.
        
        Args:
            file_content: Document content as bytes
            mime_type: MIME type of the document
            filename: Document filename
        
        Returns:
            Extracted data dict
        """
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Prepare file part
        file_part = {
            "mime_type": mime_type,
            "data": file_content
        }
        
        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = self.model.generate_content(
                    [T12_EXTRACTION_PROMPT, file_part],
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                response_text = response.text
                return self._parse_extraction_response(response_text)
                
            except Exception as e:
                logger.warning(f"Gemini extraction attempt {attempt + 1} failed: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                import time
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
    
    def _parse_extraction_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse extraction response from LLM.
        
        Args:
            response_text: Raw response text from LLM
        
        Returns:
            Parsed extraction result dict
        """
        try:
            # Clean response text
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            # Validate structure
            if not isinstance(result, dict):
                raise ValueError("Response is not a JSON object")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {str(e)}")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
    
    def _calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate extraction cost in dollars.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Cost in dollars
        """
        input_cost = (input_tokens / 1_000_000) * GEMINI_FLASH_INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * GEMINI_FLASH_OUTPUT_COST_PER_1M
        
        return input_cost + output_cost
    
    async def extract(
        self,
        file_content: bytes,
        filename: str,
        mime_type: Optional[str] = None,
        number_of_units: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Extract data from T-12 operating statement.
        
        Args:
            file_content: Document content as bytes
            filename: Document filename
            mime_type: MIME type of the document (defaults to PDF)
            number_of_units: Number of units (for per-unit calculations)
        
        Returns:
            Dict with:
            - extracted_data: Extracted fields with confidence scores
            - model_used: Model used for extraction
            - cost_dollars: Cost in dollars
            - overall_confidence: Overall confidence score (0-100)
            - fields_requiring_review: List of fields with low confidence
        """
        # Determine MIME type
        if not mime_type:
            if filename.lower().endswith('.pdf'):
                mime_type = "application/pdf"
            elif filename.lower().endswith(('.xlsx', '.xls')):
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                mime_type = "application/pdf"
        
        # Extract data
        try:
            extracted_data = self._extract_with_gemini(file_content, mime_type, filename)
        except Exception as e:
            logger.error(f"T-12 extraction failed: {str(e)}")
            raise
        
        # If units count provided, add to metadata for per-unit calculations
        if number_of_units and "metadata" in extracted_data:
            extracted_data["metadata"]["units_count"] = number_of_units
        
        # Calculate cost (estimate tokens)
        estimated_input_tokens = len(file_content) // 4  # Rough estimate
        estimated_output_tokens = len(json.dumps(extracted_data)) // 4
        cost_dollars = self._calculate_cost(
            estimated_input_tokens,
            estimated_output_tokens,
        )
        
        # Calculate overall confidence
        confidence_scores = []
        fields_requiring_review = []
        
        # Collect confidence scores from revenue items
        if "revenue" in extracted_data:
            for field_name, field_data in extracted_data["revenue"].items():
                if isinstance(field_data, dict) and "confidence" in field_data:
                    confidence = field_data["confidence"]
                    confidence_scores.append(confidence)
                    if confidence < 70 and field_data.get("annual") is not None:
                        fields_requiring_review.append(f"revenue.{field_name}")
        
        # Collect confidence scores from expense items
        if "expenses" in extracted_data:
            for field_name, field_data in extracted_data["expenses"].items():
                if isinstance(field_data, dict) and "confidence" in field_data:
                    confidence = field_data["confidence"]
                    confidence_scores.append(confidence)
                    if confidence < 70 and field_data.get("annual") is not None:
                        fields_requiring_review.append(f"expenses.{field_name}")
        
        # Collect confidence scores from calculated metrics
        if "calculated_metrics" in extracted_data:
            for field_name, field_data in extracted_data["calculated_metrics"].items():
                if isinstance(field_data, dict) and "confidence" in field_data:
                    confidence = field_data["confidence"]
                    confidence_scores.append(confidence)
                    if confidence < 70:
                        fields_requiring_review.append(f"calculated_metrics.{field_name}")
        
        overall_confidence = int(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0
        
        # Build result
        result = {
            "extracted_data": extracted_data,
            "model_used": T12_MODEL,
            "cost_dollars": round(cost_dollars, 4),
            "overall_confidence": overall_confidence,
            "fields_requiring_review": fields_requiring_review,
            "extraction_timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"T-12 extraction completed: {overall_confidence}% confidence, ${cost_dollars:.4f} cost")
        
        return result


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_t12_extraction_instance: Optional[T12ExtractionService] = None


def get_t12_extraction_service() -> T12ExtractionService:
    """Get or create global T-12 extraction service instance"""
    global _t12_extraction_instance
    if _t12_extraction_instance is None:
        _t12_extraction_instance = T12ExtractionService()
    return _t12_extraction_instance

