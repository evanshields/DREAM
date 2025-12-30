"""
DREAM AI - Document Classification Service
Task 1.12: Document Classification Service
PRD Reference: Section 6.2

Uses Gemini 1.5 Flash API to classify documents into one of 22 document types.
"""

import os
import logging
import hashlib
import json
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Gemini model for classification (Flash for cost efficiency)
CLASSIFICATION_MODEL = "gemini-1.5-flash"

# Cost tracking (per PRD Section 6.1)
# Gemini 1.5 Flash: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens
GEMINI_FLASH_INPUT_COST_PER_1M = 0.075
GEMINI_FLASH_OUTPUT_COST_PER_1M = 0.30

# Cache TTL (24 hours)
CACHE_TTL_HOURS = 24

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# In-memory cache (in production, use Redis)
_classification_cache: Dict[str, Dict] = {}

# ============================================================================
# DOCUMENT TYPE DEFINITIONS (All 22 types from PRD)
# ============================================================================

# Document types matching schema.prisma enum (all 22 types)
DOCUMENT_TYPES = [
    "OFFERING_MEMORANDUM",
    "T12_STATEMENT",  # Note: PRD says T12_OPERATING_STATEMENT, but schema uses T12_STATEMENT
    "RENT_ROLL",
    "LEASING_REPORT",
    "CONCESSIONS_REPORT",
    "AGED_RECEIVABLES",
    "CAPITAL_EXPENDITURE_REPORT",
    "LOAN_DOCUMENTS",
    "PROPERTY_PHOTO",
    "SITE_PLAN",
    "FLOOR_PLAN",
    "INSPECTION_REPORT",
    "APPRAISAL",
    "PRIOR_APPRAISAL",
    "MARKET_STUDY",
    "ENVIRONMENTAL_REPORT",
    "TITLE_REPORT",
    "ORIGINAL_PLANS",
    "CONSTRUCTION_BUDGET",
    "PERMITS",
    "ENGINEERING_REPORT",
    "OTHER"
]

# Map PRD document type names to schema enum values
DOCUMENT_TYPE_MAPPING = {
    "T12_OPERATING_STATEMENT": "T12_STATEMENT",  # PRD uses this, schema uses T12_STATEMENT
}

# ============================================================================
# CLASSIFICATION PROMPT (From PRD Section 6.2)
# ============================================================================

CLASSIFICATION_PROMPT = """You are a document classifier for commercial real estate acquisitions.

Analyze the provided document and classify it as one of:
- OFFERING_MEMORANDUM: Marketing package with property details, financials, photos
- T12_STATEMENT: Trailing 12-month income/expense statement (also called T12_OPERATING_STATEMENT)
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

Respond with JSON only:
{{
  "document_type": "OFFERING_MEMORANDUM",
  "confidence": 95,
  "reasoning": "Document contains property marketing language, unit mix, and financial projections"
}}

Important:
- document_type must be one of the types listed above (exact match, uppercase)
- confidence must be 0-100
- reasoning should explain why this classification was chosen
- Return ONLY valid JSON, no other text
"""

# ============================================================================
# CLASSIFICATION SERVICE
# ============================================================================

class ClassificationService:
    """
    Document classification service using Gemini 1.5 Flash.
    
    Classifies documents into one of 22 document types with confidence scores.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize classification service.
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini client
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(CLASSIFICATION_MODEL)
        
        logger.info(f"Initialized ClassificationService with model: {CLASSIFICATION_MODEL}")
    
    def _calculate_document_hash(self, file_content: bytes, filename: str) -> str:
        """
        Calculate hash for document caching.
        
        Args:
            file_content: Document content as bytes
            filename: Document filename
        
        Returns:
            SHA256 hash string
        """
        # Include filename in hash to handle same content with different names
        content_hash = hashlib.sha256(file_content).hexdigest()
        filename_hash = hashlib.sha256(filename.encode()).hexdigest()
        combined = f"{content_hash}:{filename_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _get_cached_result(self, document_hash: str) -> Optional[Dict]:
        """
        Get cached classification result if available.
        
        Args:
            document_hash: Document hash
        
        Returns:
            Cached result dict or None
        """
        if document_hash in _classification_cache:
            cached = _classification_cache[document_hash]
            # Check if cache is still valid
            cached_time = cached.get("cached_at")
            if cached_time:
                age = datetime.utcnow() - cached_time
                if age < timedelta(hours=CACHE_TTL_HOURS):
                    logger.info(f"Using cached classification result for hash: {document_hash[:8]}")
                    return cached.get("result")
                else:
                    # Cache expired, remove it
                    del _classification_cache[document_hash]
        return None
    
    def _cache_result(self, document_hash: str, result: Dict):
        """
        Cache classification result.
        
        Args:
            document_hash: Document hash
            result: Classification result dict
        """
        _classification_cache[document_hash] = {
            "result": result,
            "cached_at": datetime.utcnow()
        }
        logger.debug(f"Cached classification result for hash: {document_hash[:8]}")
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in cents for Gemini API call.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Cost in cents
        """
        input_cost = (input_tokens / 1_000_000) * GEMINI_FLASH_INPUT_COST_PER_1M * 100
        output_cost = (output_tokens / 1_000_000) * GEMINI_FLASH_OUTPUT_COST_PER_1M * 100
        total_cost_cents = input_cost + output_cost
        return round(total_cost_cents, 2)
    
    def _parse_classification_response(self, response_text: str) -> Dict:
        """
        Parse classification response from Gemini.
        
        Args:
            response_text: Raw response text from Gemini
        
        Returns:
            Parsed classification result dict
        """
        try:
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            # Validate and map document_type
            doc_type = result.get("document_type", "").upper()
            
            # Map PRD names to schema enum values
            if doc_type in DOCUMENT_TYPE_MAPPING:
                doc_type = DOCUMENT_TYPE_MAPPING[doc_type]
            
            if doc_type not in DOCUMENT_TYPES:
                logger.warning(f"Invalid document_type '{doc_type}', defaulting to OTHER")
                result["document_type"] = "OTHER"
            else:
                result["document_type"] = doc_type
            
            # Validate confidence
            confidence = result.get("confidence", 0)
            if not isinstance(confidence, int) or confidence < 0 or confidence > 100:
                logger.warning(f"Invalid confidence '{confidence}', defaulting to 0")
                result["confidence"] = 0
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classification response: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")
            # Return default classification
            return {
                "document_type": "OTHER",
                "confidence": 0,
                "reasoning": f"Failed to parse classification response: {str(e)}"
            }
    
    async def classify(
        self,
        file_content: bytes,
        filename: str,
        mime_type: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Classify a document into one of 22 document types.
        
        Args:
            file_content: Document content as bytes
            filename: Document filename
            mime_type: MIME type of the document (optional)
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            Dict with:
            - document_type: One of 22 document types
            - confidence: Confidence score (0-100)
            - reasoning: Explanation of classification
            - cost_cents: Cost in cents
            - cached: Whether result was from cache
        """
        # Calculate document hash for caching
        document_hash = self._calculate_document_hash(file_content, filename)
        
        # Check cache
        if use_cache:
            cached_result = self._get_cached_result(document_hash)
            if cached_result:
                return {
                    **cached_result,
                    "cached": True
                }
        
        # Prepare file for Gemini
        try:
            # Create file part for Gemini
            file_part = {
                "mime_type": mime_type or "application/pdf",
                "data": file_content
            }
            
            # Retry logic
            for attempt in range(MAX_RETRIES):
                try:
                    # Generate classification
                    response = self.model.generate_content(
                        [CLASSIFICATION_PROMPT, file_part],
                        safety_settings={
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        }
                    )
                    
                    # Parse response
                    response_text = response.text
                    classification_result = self._parse_classification_response(response_text)
                    
                    # Calculate cost
                    # Note: Gemini API doesn't always return token counts in response
                    # We'll estimate based on typical usage or track separately
                    # For now, estimate: ~1000 input tokens, ~50 output tokens
                    estimated_input_tokens = len(file_content) // 4  # Rough estimate
                    estimated_output_tokens = len(response_text) // 4
                    cost_cents = self._calculate_cost(estimated_input_tokens, estimated_output_tokens)
                    
                    # Add metadata
                    result = {
                        **classification_result,
                        "cost_cents": cost_cents,
                        "cached": False,
                        "model": CLASSIFICATION_MODEL,
                        "filename": filename
                    }
                    
                    # Cache result
                    if use_cache:
                        self._cache_result(document_hash, result)
                    
                    logger.info(
                        f"Classified document '{filename}' as '{classification_result['document_type']}' "
                        f"with {classification_result['confidence']}% confidence "
                        f"(cost: ${cost_cents/100:.4f})"
                    )
                    
                    return result
                    
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(f"Classification attempt {attempt + 1} failed: {str(e)}, retrying...")
                        import asyncio
                        await asyncio.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Failed to classify document '{filename}': {str(e)}", exc_info=True)
            # Return default classification on error
            return {
                "document_type": "OTHER",
                "confidence": 0,
                "reasoning": f"Classification failed: {str(e)}",
                "cost_cents": 0,
                "cached": False,
                "model": CLASSIFICATION_MODEL,
                "filename": filename,
                "error": str(e)
            }

# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_classification_service_instance: Optional[ClassificationService] = None

def get_classification_service() -> ClassificationService:
    """
    Get or create classification service instance (singleton pattern).
    
    Returns:
        ClassificationService instance
    """
    global _classification_service_instance
    
    if _classification_service_instance is None:
        _classification_service_instance = ClassificationService()
    
    return _classification_service_instance

