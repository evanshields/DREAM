"""
DREAM AI - LLM Router Service
Task 1.13: LLM Router Implementation
PRD Reference: Section 6.1

Intelligent router that selects optimal LLM model based on document complexity.
"""

import os
import logging
from typing import Optional, Dict, Literal, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model identifiers
MODEL_GEMINI_FLASH = "gemini-1.5-flash"
MODEL_CLAUDE_HAIKU = "claude-3-5-haiku-20241022"
MODEL_GEMINI_PRO = "gemini-1.5-pro"
MODEL_CLAUDE_SONNET = "claude-3-5-sonnet-20241022"

# Cost per 1M tokens (from PRD Section 6.1)
MODEL_COSTS = {
    MODEL_GEMINI_FLASH: {
        "input": 0.075,  # $0.075 per 1M input tokens
        "output": 0.30,  # $0.30 per 1M output tokens
    },
    MODEL_CLAUDE_HAIKU: {
        "input": 0.25,   # $0.25 per 1M input tokens
        "output": 1.25,  # $1.25 per 1M output tokens
    },
    MODEL_GEMINI_PRO: {
        "input": 1.25,   # $1.25 per 1M input tokens
        "output": 5.00,   # $5.00 per 1M output tokens
    },
    MODEL_CLAUDE_SONNET: {
        "input": 3.00,   # $3.00 per 1M input tokens
        "output": 15.00, # $15.00 per 1M output tokens
    },
}

# Router thresholds
PAGE_COUNT_THRESHOLD = 20  # <20 pages → Flash; >=20 pages → Haiku
CONFIDENCE_THRESHOLD = 70  # Low confidence (<70) → Upgrade to Haiku

# ============================================================================
# ENUMS AND TYPES
# ============================================================================

class TaskComplexity(str, Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class UserTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class RouterDecision:
    """Router decision result"""
    model: str
    reasoning: str
    estimated_cost: float
    complexity: TaskComplexity
    factors: Dict[str, any]


# ============================================================================
# DOCUMENT TYPE COMPLEXITY MAPPING
# ============================================================================

# Document types that are simple/standard (use Flash)
SIMPLE_DOCUMENT_TYPES = {
    "T12_STATEMENT",
    "RENT_ROLL",
    "LEASING_REPORT",
    "CONCESSIONS_REPORT",
    "AGED_RECEIVABLES",
    "PERMITS",
}

# Document types that are complex (use Haiku)
COMPLEX_DOCUMENT_TYPES = {
    "OFFERING_MEMORANDUM",  # Can be simple or complex based on size
    "ENGINEERING_REPORT",
    "ORIGINAL_PLANS",
    "ENVIRONMENTAL_REPORT",
    "MARKET_STUDY",
    "APPRAISAL",
    "PRIOR_APPRAISAL",
    "INSPECTION_REPORT",
    "TITLE_REPORT",
    "CONSTRUCTION_BUDGET",
    "CAPITAL_EXPENDITURE_REPORT",
    "LOAN_DOCUMENTS",
}

# Document types that are very complex (always use Haiku)
VERY_COMPLEX_DOCUMENT_TYPES = {
    "ENGINEERING_REPORT",
    "ORIGINAL_PLANS",
    "ENVIRONMENTAL_REPORT",
}

# ============================================================================
# LLM ROUTER SERVICE
# ============================================================================

class LLMRouter:
    """
    Intelligent router that selects optimal LLM model based on document complexity.
    
    Router Logic (from PRD Section 6.1):
    - Simple tasks → Gemini 1.5 Flash
    - Standard docs → Gemini 1.5 Flash
    - Complex docs → Claude 3.5 Haiku
    - Very complex → Claude 3.5 Haiku
    """
    
    def __init__(self):
        """Initialize the LLM router"""
        self.decision_history: list[RouterDecision] = []
    
    def select_model(
        self,
        document_type: Optional[str] = None,
        page_count: Optional[int] = None,
        image_quality: Optional[Literal["high", "medium", "low"]] = None,
        extraction_confidence: Optional[float] = None,
        user_tier: UserTier = UserTier.STANDARD,
        task_type: str = "extraction",
        force_model: Optional[str] = None,
    ) -> RouterDecision:
        """
        Select optimal LLM model based on document complexity.
        
        Args:
            document_type: Document type (e.g., "OFFERING_MEMORANDUM")
            page_count: Number of pages in document
            image_quality: Image quality ("high", "medium", "low")
            extraction_confidence: Previous extraction confidence (0-100)
            user_tier: User subscription tier
            task_type: Task type ("classification", "extraction", etc.)
            force_model: Force specific model (for premium users)
        
        Returns:
            RouterDecision with selected model and reasoning
        """
        # Premium users can force model selection
        if force_model and user_tier in [UserTier.PREMIUM, UserTier.ENTERPRISE]:
            return RouterDecision(
                model=force_model,
                reasoning=f"Premium user forced model: {force_model}",
                estimated_cost=self._estimate_cost(force_model, page_count or 10),
                complexity=TaskComplexity.STANDARD,
                factors={"forced": True, "user_tier": user_tier.value},
            )
        
        # Premium users default to Haiku for better quality
        if user_tier == UserTier.PREMIUM:
            return RouterDecision(
                model=MODEL_CLAUDE_HAIKU,
                reasoning="Premium tier: Default to Claude 3.5 Haiku for higher quality",
                estimated_cost=self._estimate_cost(MODEL_CLAUDE_HAIKU, page_count or 10),
                complexity=TaskComplexity.COMPLEX,
                factors={"user_tier": user_tier.value, "premium_default": True},
            )
        
        # Classification tasks always use Flash (simple pattern matching)
        if task_type == "classification":
            return RouterDecision(
                model=MODEL_GEMINI_FLASH,
                reasoning="Classification task: Simple pattern matching, use cost-effective Flash",
                estimated_cost=self._estimate_cost(MODEL_GEMINI_FLASH, page_count or 5),
                complexity=TaskComplexity.SIMPLE,
                factors={"task_type": task_type},
            )
        
        # Determine complexity based on document type
        complexity = self._determine_complexity(
            document_type=document_type,
            page_count=page_count,
            image_quality=image_quality,
            extraction_confidence=extraction_confidence,
        )
        
        # Select model based on complexity
        if complexity in [TaskComplexity.SIMPLE, TaskComplexity.STANDARD]:
            model = MODEL_GEMINI_FLASH
            reasoning = f"{complexity.value.capitalize()} document: Use cost-effective Gemini 1.5 Flash"
        elif complexity == TaskComplexity.COMPLEX:
            model = MODEL_CLAUDE_HAIKU
            reasoning = f"Complex document: Use Claude 3.5 Haiku for better context handling"
        else:  # VERY_COMPLEX
            model = MODEL_CLAUDE_HAIKU
            reasoning = f"Very complex document: Use Claude 3.5 Haiku for higher accuracy"
        
        # Upgrade to Haiku if previous extraction had low confidence
        if extraction_confidence is not None and extraction_confidence < CONFIDENCE_THRESHOLD:
            model = MODEL_CLAUDE_HAIKU
            reasoning += f" (Upgraded due to low confidence: {extraction_confidence}%)"
        
        # Build factors dict
        factors = {
            "document_type": document_type,
            "page_count": page_count,
            "image_quality": image_quality,
            "extraction_confidence": extraction_confidence,
            "user_tier": user_tier.value,
            "task_type": task_type,
            "complexity": complexity.value,
        }
        
        decision = RouterDecision(
            model=model,
            reasoning=reasoning,
            estimated_cost=self._estimate_cost(model, page_count or 10),
            complexity=complexity,
            factors=factors,
        )
        
        # Track decision for analytics
        self.decision_history.append(decision)
        logger.info(f"Router decision: {model} for {document_type} (complexity: {complexity.value})")
        
        return decision
    
    def _determine_complexity(
        self,
        document_type: Optional[str] = None,
        page_count: Optional[int] = None,
        image_quality: Optional[Literal["high", "medium", "low"]] = None,
        extraction_confidence: Optional[float] = None,
    ) -> TaskComplexity:
        """
        Determine task complexity based on document characteristics.
        
        Decision factors (from PRD Section 6.1):
        1. Document Type: Simple docs (T-12, Rent Roll) → Flash; Complex docs (OM, reports) → Haiku
        2. Document Size: <20 pages → Flash; >=20 pages → Haiku
        3. Image Quality: High quality → Flash; Low quality → Haiku
        4. Extraction Confidence: Low confidence on first pass → Upgrade to Haiku
        """
        # Very complex documents always use Haiku
        if document_type and document_type in VERY_COMPLEX_DOCUMENT_TYPES:
            return TaskComplexity.VERY_COMPLEX
        
        # Simple document types (tabular data)
        if document_type and document_type in SIMPLE_DOCUMENT_TYPES:
            return TaskComplexity.SIMPLE
        
        # Complex document types
        if document_type and document_type in COMPLEX_DOCUMENT_TYPES:
            # OM can be simple or complex based on size
            if document_type == "OFFERING_MEMORANDUM":
                if page_count and page_count < PAGE_COUNT_THRESHOLD:
                    return TaskComplexity.STANDARD
                else:
                    return TaskComplexity.COMPLEX
            return TaskComplexity.COMPLEX
        
        # Default complexity based on page count
        if page_count:
            if page_count < PAGE_COUNT_THRESHOLD:
                return TaskComplexity.STANDARD
            else:
                return TaskComplexity.COMPLEX
        
        # Low image quality → Complex
        if image_quality == "low":
            return TaskComplexity.COMPLEX
        
        # Low extraction confidence → Complex
        if extraction_confidence is not None and extraction_confidence < CONFIDENCE_THRESHOLD:
            return TaskComplexity.COMPLEX
        
        # Default to standard
        return TaskComplexity.STANDARD
    
    def _estimate_cost(self, model: str, page_count: int) -> float:
        """
        Estimate cost for processing document with given model.
        
        Args:
            model: Model identifier
            page_count: Number of pages
        
        Returns:
            Estimated cost in dollars
        """
        if model not in MODEL_COSTS:
            logger.warning(f"Unknown model: {model}, using Flash pricing")
            model = MODEL_GEMINI_FLASH
        
        # Rough estimation: 1 page ≈ 1000 tokens input, 500 tokens output
        # This is a rough estimate - actual token counts vary
        estimated_input_tokens = page_count * 1000
        estimated_output_tokens = page_count * 500
        
        costs = MODEL_COSTS[model]
        input_cost = (estimated_input_tokens / 1_000_000) * costs["input"]
        output_cost = (estimated_output_tokens / 1_000_000) * costs["output"]
        
        return input_cost + output_cost
    
    def get_decision_history(self, limit: int = 100) -> list[RouterDecision]:
        """Get recent router decisions for analytics"""
        return self.decision_history[-limit:]
    
    def get_model_stats(self) -> Dict[str, any]:
        """Get statistics on model selection for analytics"""
        if not self.decision_history:
            return {
                "total_decisions": 0,
                "model_counts": {},
                "complexity_counts": {},
                "average_cost": 0.0,
            }
        
        model_counts = {}
        complexity_counts = {}
        total_cost = 0.0
        
        for decision in self.decision_history:
            model_counts[decision.model] = model_counts.get(decision.model, 0) + 1
            complexity_counts[decision.complexity.value] = complexity_counts.get(decision.complexity.value, 0) + 1
            total_cost += decision.estimated_cost
        
        return {
            "total_decisions": len(self.decision_history),
            "model_counts": model_counts,
            "complexity_counts": complexity_counts,
            "average_cost": total_cost / len(self.decision_history),
        }


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Global router instance
_router_instance: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get or create global router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example usage
    router = get_router()
    
    # Example 1: Simple document (T-12 Statement)
    decision1 = router.select_model(
        document_type="T12_STATEMENT",
        page_count=5,
        task_type="extraction",
    )
    print(f"Decision 1: {decision1.model} - {decision1.reasoning}")
    print(f"  Estimated cost: ${decision1.estimated_cost:.4f}")
    
    # Example 2: Complex document (Large OM)
    decision2 = router.select_model(
        document_type="OFFERING_MEMORANDUM",
        page_count=50,
        task_type="extraction",
    )
    print(f"\nDecision 2: {decision2.model} - {decision2.reasoning}")
    print(f"  Estimated cost: ${decision2.estimated_cost:.4f}")
    
    # Example 3: Very complex document (Engineering Report)
    decision3 = router.select_model(
        document_type="ENGINEERING_REPORT",
        page_count=30,
        image_quality="low",
        task_type="extraction",
    )
    print(f"\nDecision 3: {decision3.model} - {decision3.reasoning}")
    print(f"  Estimated cost: ${decision3.estimated_cost:.4f}")
    
    # Example 4: Low confidence upgrade
    decision4 = router.select_model(
        document_type="OFFERING_MEMORANDUM",
        page_count=15,
        extraction_confidence=65,  # Low confidence
        task_type="extraction",
    )
    print(f"\nDecision 4: {decision4.model} - {decision4.reasoning}")
    print(f"  Estimated cost: ${decision4.estimated_cost:.4f}")
    
    # Example 5: Premium user
    decision5 = router.select_model(
        document_type="T12_STATEMENT",
        page_count=5,
        user_tier=UserTier.PREMIUM,
        task_type="extraction",
    )
    print(f"\nDecision 5: {decision5.model} - {decision5.reasoning}")
    print(f"  Estimated cost: ${decision5.estimated_cost:.4f}")
    
    # Print stats
    print(f"\nRouter Stats:")
    stats = router.get_model_stats()
    print(f"  Total decisions: {stats['total_decisions']}")
    print(f"  Model counts: {stats['model_counts']}")
    print(f"  Average cost: ${stats['average_cost']:.4f}")

