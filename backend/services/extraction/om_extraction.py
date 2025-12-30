"""
DREAM AI - OM (Offering Memorandum) Extraction Service
Task 1.14: OM Extraction Service
PRD Reference: Sections 5.2, 6.1, 6.2

Extracts property information, unit mix, financial data, and investment highlights
from Offering Memorandum documents using LLM router to select optimal model.
"""

import os
import json
import logging
import base64
from typing import Optional, Dict, List, Any
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from anthropic import Anthropic

# Import router (adjust path based on project structure)
try:
    from services.llm_router import get_router, RouterDecision, UserTier, MODEL_GEMINI_FLASH, MODEL_CLAUDE_HAIKU
except ImportError:
    # Fallback for different import paths
    import sys
    from pathlib import Path
    backend_path = Path(__file__).parent.parent.parent
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    from services.llm_router import get_router, RouterDecision, UserTier, MODEL_GEMINI_FLASH, MODEL_CLAUDE_HAIKU

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# ============================================================================
# OM EXTRACTION PROMPT (From PRD Section 6.2)
# ============================================================================

OM_EXTRACTION_PROMPT = """
You are a data extraction specialist for commercial real estate underwriting.

Extract the following information from this Offering Memorandum. For each field, provide:
- The extracted value
- A confidence score (0-100)
- The page/location where you found it

If a field is not found, set value to null and confidence to 0.

Required fields:

1. Property Information:
   - property_name: Property name or title
   - street_address: Full street address
   - city: City name
   - state: State abbreviation (2 letters)
   - zip_code: ZIP code (5 or 9 digits)
   - year_built: Year the property was built
   - number_of_units: Total number of units
   - total_sf: Total square footage
   - lot_size: Lot size (optional)
   - property_class: Property class (A, B, C, D) if mentioned
   - parking_spaces: Number of parking spaces (optional)
   - amenities: List of amenities (optional)

2. Unit Mix (array of objects):
   - unit_type: Type (Studio, 1BR, 2BR, 3BR, etc.)
   - unit_count: Number of units of this type
   - avg_sf: Average square footage per unit
   - market_rent: Market rent per unit
   - in_place_rent: Current in-place rent per unit (if available)

3. Financial Data:
   - asking_price: Asking price
   - price_per_unit: Price per unit (if explicit)
   - in_place_noi: In-place Net Operating Income
   - pro_forma_noi: Pro forma Net Operating Income
   - in_place_cap_rate: In-place cap rate
   - pro_forma_cap_rate: Pro forma cap rate
   - gross_potential_rent: Gross Potential Rent
   - effective_gross_income: Effective Gross Income
   - operating_expenses: Total operating expenses

4. Investment Highlights:
   - investment_highlights: Array of top 5-10 selling points
   - value_add_opportunities: Array of value-add opportunities (if mentioned)
   - location_highlights: Array of location highlights (if mentioned)
   - market_overview: Key market statistics (if mentioned)

Respond with JSON matching this schema:
{
  "property_name": {"value": "...", "confidence": 95, "source": "Page 1"},
  "street_address": {"value": "...", "confidence": 90, "source": "Page 2"},
  "city": {"value": "...", "confidence": 90, "source": "Page 2"},
  "state": {"value": "TX", "confidence": 90, "source": "Page 2"},
  "zip_code": {"value": "78701", "confidence": 90, "source": "Page 2"},
  "year_built": {"value": 1985, "confidence": 80, "source": "Page 3"},
  "number_of_units": {"value": 120, "confidence": 90, "source": "Page 3"},
  "total_sf": {"value": 120000, "confidence": 80, "source": "Page 3"},
  "lot_size": {"value": "2.5 acres", "confidence": 70, "source": "Page 3"},
  "property_class": {"value": "B", "confidence": 60, "source": "Page 4"},
  "parking_spaces": {"value": 150, "confidence": 70, "source": "Page 3"},
  "amenities": {"value": ["Pool", "Fitness Center", "Clubhouse"], "confidence": 60, "source": "Page 5"},
  "unit_mix": [
    {
      "unit_type": "1BR",
      "unit_count": 60,
      "avg_sf": 750,
      "market_rent": 1200,
      "in_place_rent": 1150
    },
    {
      "unit_type": "2BR",
      "unit_count": 60,
      "avg_sf": 1100,
      "market_rent": 1600,
      "in_place_rent": 1550
    }
  ],
  "asking_price": {"value": 15000000, "confidence": 95, "source": "Page 1"},
  "price_per_unit": {"value": 125000, "confidence": 90, "source": "Page 1"},
  "in_place_noi": {"value": 900000, "confidence": 85, "source": "Page 6"},
  "pro_forma_noi": {"value": 1100000, "confidence": 85, "source": "Page 6"},
  "in_place_cap_rate": {"value": 6.0, "confidence": 85, "source": "Page 6"},
  "pro_forma_cap_rate": {"value": 7.3, "confidence": 85, "source": "Page 6"},
  "gross_potential_rent": {"value": 1728000, "confidence": 80, "source": "Page 6"},
  "effective_gross_income": {"value": 1650000, "confidence": 80, "source": "Page 6"},
  "operating_expenses": {"value": 750000, "confidence": 80, "source": "Page 6"},
  "investment_highlights": {
    "value": [
      "Prime location in growing Austin market",
      "Value-add opportunity with unit renovations",
      "Strong rental demand"
    ],
    "confidence": 75,
    "source": "Page 1"
  },
  "value_add_opportunities": {
    "value": [
      "Unit renovations to increase rents",
      "Amenity upgrades"
    ],
    "confidence": 70,
    "source": "Page 7"
  },
  "location_highlights": {
    "value": [
      "Near major employers",
      "Close to shopping and dining"
    ],
    "confidence": 70,
    "source": "Page 8"
  },
  "market_overview": {
    "value": {
      "population_growth": "5% annually",
      "job_growth": "Strong"
    },
    "confidence": 60,
    "source": "Page 9"
  }
}

IMPORTANT:
- Return ONLY valid JSON, no markdown code blocks
- All numeric values should be numbers (not strings)
- All confidence scores should be integers 0-100
- If a field is not found, use null for value and 0 for confidence
- For arrays (unit_mix, investment_highlights), include the full array structure
"""

# ============================================================================
# OM EXTRACTION SERVICE
# ============================================================================

class OMExtractionService:
    """
    OM (Offering Memorandum) extraction service using LLM router.
    
    Uses router to select optimal model (Flash for simple, Haiku for complex)
    and extracts all fields from PRD Section 5.2.
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
    ):
        """
        Initialize OM extraction service.
        
        Args:
            gemini_api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
            claude_api_key: Anthropic Claude API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.claude_api_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set - Gemini extraction will fail")
        else:
            genai.configure(api_key=self.gemini_api_key)
        
        if not self.claude_api_key:
            logger.warning("ANTHROPIC_API_KEY not set - Claude extraction will fail")
        else:
            self.claude_client = Anthropic(api_key=self.claude_api_key)
        
        self.router = get_router()
        logger.info("Initialized OMExtractionService")
    
    def _estimate_page_count(self, file_content: bytes, mime_type: str) -> int:
        """
        Estimate page count from file content.
        
        This is a rough estimate - in production, use a PDF parser.
        """
        # Rough estimate: PDF ~50KB per page, images ~200KB per page
        if mime_type == "application/pdf":
            return max(1, len(file_content) // 50000)
        elif mime_type.startswith("image/"):
            return max(1, len(file_content) // 200000)
        else:
            return 10  # Default estimate
    
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
        
        model = genai.GenerativeModel(MODEL_GEMINI_FLASH)
        
        # Prepare file part
        file_part = {
            "mime_type": mime_type,
            "data": file_content
        }
        
        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = model.generate_content(
                    [OM_EXTRACTION_PROMPT, file_part],
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
    
    def _extract_with_claude(
        self,
        file_content: bytes,
        mime_type: str,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Extract data using Claude API.
        
        Args:
            file_content: Document content as bytes
            mime_type: MIME type of the document
            filename: Document filename
        
        Returns:
            Extracted data dict
        """
        if not self.claude_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        # Convert file to base64 for Claude
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Determine media type for Claude
        media_type_map = {
            "application/pdf": "application/pdf",
            "image/png": "image/png",
            "image/jpeg": "image/jpeg",
            "image/jpg": "image/jpeg",
        }
        media_type = media_type_map.get(mime_type, "application/pdf")
        
        # Retry logic
        for attempt in range(MAX_RETRIES):
            try:
                response = self.claude_client.messages.create(
                    model=MODEL_CLAUDE_HAIKU,
                    max_tokens=4096,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": OM_EXTRACTION_PROMPT
                                },
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": file_base64
                                    }
                                }
                            ]
                        }
                    ]
                )
                
                response_text = response.content[0].text
                return self._parse_extraction_response(response_text)
                
            except Exception as e:
                logger.warning(f"Claude extraction attempt {attempt + 1} failed: {str(e)}")
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
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate extraction cost in dollars.
        
        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Cost in dollars
        """
        from services.llm_router import MODEL_COSTS
        
        if model not in MODEL_COSTS:
            logger.warning(f"Unknown model: {model}, using Flash pricing")
            model = MODEL_GEMINI_FLASH
        
        costs = MODEL_COSTS[model]
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        
        return input_cost + output_cost
    
    async def extract(
        self,
        file_content: bytes,
        filename: str,
        mime_type: Optional[str] = None,
        page_count: Optional[int] = None,
        user_tier: UserTier = UserTier.STANDARD,
        previous_confidence: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Extract data from Offering Memorandum.
        
        Args:
            file_content: Document content as bytes
            filename: Document filename
            mime_type: MIME type of the document (defaults to PDF)
            page_count: Number of pages (estimated if not provided)
            user_tier: User subscription tier
            previous_confidence: Previous extraction confidence (for retry logic)
        
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
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                mime_type = "image/png"
            else:
                mime_type = "application/pdf"
        
        # Estimate page count if not provided
        if not page_count:
            page_count = self._estimate_page_count(file_content, mime_type)
        
        # Use router to select model
        router_decision = self.router.select_model(
            document_type="OFFERING_MEMORANDUM",
            page_count=page_count,
            extraction_confidence=previous_confidence,
            user_tier=user_tier,
            task_type="extraction",
        )
        
        logger.info(f"Router selected {router_decision.model} for OM extraction (reasoning: {router_decision.reasoning})")
        
        # Extract based on selected model
        try:
            if router_decision.model == MODEL_GEMINI_FLASH:
                extracted_data = self._extract_with_gemini(file_content, mime_type, filename)
            elif router_decision.model == MODEL_CLAUDE_HAIKU:
                extracted_data = self._extract_with_claude(file_content, mime_type, filename)
            else:
                # Fallback to Claude Haiku
                logger.warning(f"Unknown model {router_decision.model}, using Claude Haiku")
                extracted_data = self._extract_with_claude(file_content, mime_type, filename)
                router_decision.model = MODEL_CLAUDE_HAIKU
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
        
        # Calculate cost (estimate tokens)
        estimated_input_tokens = len(file_content) // 4  # Rough estimate
        estimated_output_tokens = len(json.dumps(extracted_data)) // 4
        cost_dollars = self._calculate_cost(
            router_decision.model,
            estimated_input_tokens,
            estimated_output_tokens,
        )
        
        # Calculate overall confidence
        confidence_scores = []
        fields_requiring_review = []
        
        for field_name, field_data in extracted_data.items():
            if isinstance(field_data, dict) and "confidence" in field_data:
                confidence = field_data["confidence"]
                confidence_scores.append(confidence)
                
                # Fields with confidence < 70 require review
                if confidence < 70 and field_data.get("value") is not None:
                    fields_requiring_review.append(field_name)
        
        overall_confidence = int(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0
        
        # Build result
        result = {
            "extracted_data": extracted_data,
            "model_used": router_decision.model,
            "router_reasoning": router_decision.reasoning,
            "cost_dollars": round(cost_dollars, 4),
            "overall_confidence": overall_confidence,
            "fields_requiring_review": fields_requiring_review,
            "extraction_timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"OM extraction completed: {overall_confidence}% confidence, ${cost_dollars:.4f} cost")
        
        return result


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_om_extraction_instance: Optional[OMExtractionService] = None


def get_om_extraction_service() -> OMExtractionService:
    """Get or create global OM extraction service instance"""
    global _om_extraction_instance
    if _om_extraction_instance is None:
        _om_extraction_instance = OMExtractionService()
    return _om_extraction_instance

