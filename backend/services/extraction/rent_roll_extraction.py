"""
DREAM AI - Rent Roll Extraction Service
Task 1.16: Rent Roll Extraction Service
PRD Reference: Sections 5.4, 6.2

Extracts unit-level data and calculates aggregated metrics
from Rent Roll documents using Gemini 1.5 Flash.
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

# Use Gemini Flash for Rent Roll (standard tabular data)
RENT_ROLL_MODEL = "gemini-1.5-flash"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# Cost tracking (per PRD Section 6.1)
GEMINI_FLASH_INPUT_COST_PER_1M = 0.075
GEMINI_FLASH_OUTPUT_COST_PER_1M = 0.30

# ============================================================================
# RENT ROLL EXTRACTION PROMPT (From PRD Section 6.2)
# ============================================================================

RENT_ROLL_EXTRACTION_PROMPT = """
You are a data extraction specialist for commercial real estate rent rolls.

Extract unit-level data from this Rent Roll document. For each unit, extract:

UNIT-LEVEL DATA:
- Unit Number (unique identifier)
- Unit Type (Studio, 1BR, 2BR, 3BR, etc.)
- Square Footage
- Bedrooms (0-5)
- Bathrooms (1-4)
- Current Rent (in-place rent)
- Market Rent (if available)
- Lease Start Date
- Lease End Date
- Move-In Date (if available)
- Tenant Name (optional, for privacy)
- Status (Occupied, Vacant, etc.)
- Deposit Amount
- Balance Due (delinquency indicator)

AGGREGATED METRICS (Calculate from unit-level data):
- Total Units (count of all units)
- Occupied Units (count where status = Occupied)
- Vacant Units (count where status = Vacant)
- Occupancy Rate (Occupied ÷ Total, as percentage)
- Total In-Place Rent (sum of current rents, monthly)
- Average Rent (Total In-Place Rent ÷ Occupied Units)
- Average Square Footage (Total SF ÷ Total Units)
- Rent Per Square Foot (Average Rent ÷ Average SF)
- Total Market Rent (sum of market rents, if available)
- Loss to Lease (Total Market Rent - Total In-Place Rent, if market rent available)
- Loss to Lease Percentage (Loss to Lease ÷ Total Market Rent × 100)
- Average Lease Term Remaining (average months until lease expiration)
- Delinquency Rate (Units with balance due ÷ Occupied Units, as percentage)

For each unit-level field, provide:
- The extracted value
- Confidence score (0-100)
- Source/column where found

For aggregated metrics, provide:
- The calculated value
- Confidence score (based on underlying data quality)
- Calculation method

IMPORTANT:
- Return ONLY valid JSON, no markdown code blocks
- All numeric values should be numbers (not strings)
- All confidence scores should be integers 0-100
- Dates should be in ISO format (YYYY-MM-DD)
- If a field is not found, use null for value and 0 for confidence
- For privacy, tenant names can be anonymized or omitted
- Handle various rent roll formats (Excel, PDF, CSV)

Respond with JSON matching this schema:
{
  "units": [
    {
      "unit_number": "101",
      "unit_type": "1BR",
      "square_footage": 750,
      "bedrooms": 1,
      "bathrooms": 1,
      "current_rent": 1200,
      "market_rent": 1250,
      "lease_start": "2024-01-01",
      "lease_end": "2024-12-31",
      "move_in_date": "2024-01-15",
      "tenant_name": "John Doe",
      "status": "Occupied",
      "deposit": 1200,
      "balance_due": 0,
      "confidence": 95,
      "source": "Row 2, Columns A-M"
    }
  ],
  "aggregated_metrics": {
    "total_units": {
      "value": 120,
      "confidence": 95,
      "source": "Calculated",
      "calculation": "Count of all units"
    },
    "occupied_units": {
      "value": 108,
      "confidence": 95,
      "source": "Calculated",
      "calculation": "Count where status = Occupied"
    },
    "vacant_units": {
      "value": 12,
      "confidence": 95,
      "source": "Calculated",
      "calculation": "Count where status = Vacant"
    },
    "occupancy_rate": {
      "value": 90.0,
      "confidence": 95,
      "source": "Calculated",
      "calculation": "Occupied ÷ Total × 100"
    },
    "total_in_place_rent": {
      "value": 129600,
      "confidence": 95,
      "source": "Calculated",
      "calculation": "Sum of current rents (monthly)"
    },
    "average_rent": {
      "value": 1200,
      "confidence": 95,
      "source": "Calculated",
      "calculation": "Total In-Place Rent ÷ Occupied Units"
    },
    "average_square_footage": {
      "value": 950,
      "confidence": 90,
      "source": "Calculated",
      "calculation": "Total SF ÷ Total Units"
    },
    "rent_per_square_foot": {
      "value": 1.26,
      "confidence": 90,
      "source": "Calculated",
      "calculation": "Average Rent ÷ Average SF"
    },
    "total_market_rent": {
      "value": 135000,
      "confidence": 85,
      "source": "Calculated",
      "calculation": "Sum of market rents (monthly)"
    },
    "loss_to_lease": {
      "value": 5400,
      "confidence": 85,
      "source": "Calculated",
      "calculation": "Total Market Rent - Total In-Place Rent"
    },
    "loss_to_lease_percentage": {
      "value": 4.0,
      "confidence": 85,
      "source": "Calculated",
      "calculation": "Loss to Lease ÷ Total Market Rent × 100"
    },
    "average_lease_term_remaining": {
      "value": 8.5,
      "confidence": 80,
      "source": "Calculated",
      "calculation": "Average months until lease expiration"
    },
    "delinquency_rate": {
      "value": 2.8,
      "confidence": 85,
      "source": "Calculated",
      "calculation": "Units with balance due ÷ Occupied Units × 100"
    }
  },
  "metadata": {
    "extraction_date": "2024-12-20",
    "document_period": "Current as of December 2024",
    "total_rows_processed": 120,
    "data_format": "Excel"
  }
}
"""

# ============================================================================
# RENT ROLL EXTRACTION SERVICE
# ============================================================================

class RentRollExtractionService:
    """
    Rent Roll extraction service using Gemini 1.5 Flash.
    
    Extracts unit-level data and calculates aggregated metrics
    from Rent Roll documents.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize Rent Roll extraction service.
        
        Args:
            gemini_api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set - Rent Roll extraction will fail")
        else:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(RENT_ROLL_MODEL)
        
        logger.info(f"Initialized RentRollExtractionService with model: {RENT_ROLL_MODEL}")
    
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
                    [RENT_ROLL_EXTRACTION_PROMPT, file_part],
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
            
            # Validate units array exists
            if "units" not in result:
                logger.warning("No 'units' array found in response, adding empty array")
                result["units"] = []
            
            # Validate aggregated_metrics exists
            if "aggregated_metrics" not in result:
                logger.warning("No 'aggregated_metrics' found in response, adding empty object")
                result["aggregated_metrics"] = {}
            
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
    ) -> Dict[str, Any]:
        """
        Extract data from Rent Roll document.
        
        Args:
            file_content: Document content as bytes
            filename: Document filename
            mime_type: MIME type of the document (defaults based on filename)
        
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
            elif filename.lower().endswith('.xlsx'):
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif filename.lower().endswith('.xls'):
                mime_type = "application/vnd.ms-excel"
            else:
                mime_type = "application/pdf"
        
        # Extract data
        try:
            extracted_data = self._extract_with_gemini(file_content, mime_type, filename)
        except Exception as e:
            logger.error(f"Rent Roll extraction failed: {str(e)}")
            raise
        
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
        
        # Collect confidence scores from unit-level data
        if "units" in extracted_data:
            for unit in extracted_data["units"]:
                if isinstance(unit, dict) and "confidence" in unit:
                    confidence = unit["confidence"]
                    confidence_scores.append(confidence)
                    if confidence < 70:
                        unit_num = unit.get("unit_number", "unknown")
                        fields_requiring_review.append(f"unit.{unit_num}")
        
        # Collect confidence scores from aggregated metrics
        if "aggregated_metrics" in extracted_data:
            for metric_name, metric_data in extracted_data["aggregated_metrics"].items():
                if isinstance(metric_data, dict) and "confidence" in metric_data:
                    confidence = metric_data["confidence"]
                    confidence_scores.append(confidence)
                    if confidence < 70:
                        fields_requiring_review.append(f"metric.{metric_name}")
        
        overall_confidence = int(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0
        
        # Build result
        result = {
            "extracted_data": extracted_data,
            "model_used": RENT_ROLL_MODEL,
            "cost_dollars": round(cost_dollars, 4),
            "overall_confidence": overall_confidence,
            "fields_requiring_review": fields_requiring_review,
            "extraction_timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Rent Roll extraction completed: {overall_confidence}% confidence, ${cost_dollars:.4f} cost")
        
        return result


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_rent_roll_extraction_instance: Optional[RentRollExtractionService] = None


def get_rent_roll_extraction_service() -> RentRollExtractionService:
    """Get or create global Rent Roll extraction service instance"""
    global _rent_roll_extraction_instance
    if _rent_roll_extraction_instance is None:
        _rent_roll_extraction_instance = RentRollExtractionService()
    return _rent_roll_extraction_instance

