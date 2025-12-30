"""
Shieldstone Technical Manual v2.0 Python Library
================================================

A comprehensive library for multifamily value-add underwriting based on
Shieldstone Acquisitions' Technical Manual Version 2.0.

This library implements all Python code from the manual, organized by
workflow phases and providing a complete toolset for deal analysis from
screening through final investment recommendation.

Version: 2.0
Date: December 2025
Status: Production Ready

Main Components:
---------------
- Phase 1: Investment Philosophy & Return Hurdles (Section 1)
- Phase 2: Deal Screening & Validation (Section 2)
- Phase 3: Property Tax Analysis (Section 4)
- Phase 4: Refinancing Strategy (Section 6.5)
- Phase 5: Ground Lease Financing (Section 6.6)
- Phase 6: Deal Fees & Promote (Section 6.7)
- Phase 7: Exit Cap Triangulation (Section 7.2)
- Phase 8: Master Workflow Integration (Section 13)

Usage:
------
```python
from shieldstone_library import ReturnHurdleCalculator, DealScreener
from shieldstone_library import CompleteUnderwritingWorkflow

# Use individual components
hurdles = ReturnHurdleCalculator(market_tier, property_profile)
result = hurdles.calculate_adjusted_hurdle()

# Or run complete workflow
workflow = CompleteUnderwritingWorkflow(deal_data)
final_report = workflow.execute_complete_workflow()
```

"""

__version__ = "2.0.0"
__author__ = "Shieldstone Acquisitions"
__license__ = "Proprietary"

# Phase 1: Return Hurdles
from .phase_1_return_hurdles import (
    MarketTier,
    RenovationScope,
    PropertyProfile,
    ReturnHurdleCalculator
)

# Phase 2: Deal Screening
from .phase_2_deal_screening import (
    RedFlagCategory,
    RiskLevel,
    ScreeningInput,
    DealScreener
)

# Phase 3: Property Tax Analysis (from consolidated library)
try:
    from .shieldstone_v2_library import (
        PropertyTaxInput,
        PropertyTaxCalculator
    )
except ImportError:
    PropertyTaxInput = None
    PropertyTaxCalculator = None

# Phase 4: Refinancing Strategy
from .phase_4_refinancing import (
    RenovationStrategy,
    RefinancePropertyProfile,
    RefinanceAssumptions,
    NinetyNinetyAnalyzer,
    RefinanceSizer,
    RefinanceDecisionFramework
)

# Phase 5: Ground Lease Financing
from .phase_5_ground_lease import (
    CapitalizedGroundLeaseSizer
)

# Phase 6: Deal Fees & Promote
from .phase_6_fees_promote import (
    DealFeeAssumptions,
    PromoteStructure,
    DealFeeCalculator,
    PromoteCalculator,
    NetReturnCalculator
)

# Phase 7: Exit Cap Triangulation
from .phase_7_exit_cap import (
    InvestmentStrategy,
    ExitCapInput,
    ExitCapTriangulator
)

# Phase 8: Master Workflow
from .phase_8_master_workflow import (
    WorkflowPhase,
    RecommendationType,
    WorkflowStatus,
    DealInputData,
    CompleteUnderwritingWorkflow,
    determine_recommendation
)

__all__ = [
    # Phase 1: Return Hurdles
    'MarketTier',
    'RenovationScope',
    'PropertyProfile',
    'ReturnHurdleCalculator',
    
    # Phase 2: Deal Screening
    'RedFlagCategory',
    'RiskLevel',
    'ScreeningInput',
    'DealScreener',
    
    # Phase 3: Property Tax
    'PropertyTaxInput',
    'PropertyTaxCalculator',
    
    # Phase 4: Refinancing Strategy
    'RenovationStrategy',
    'RefinancePropertyProfile',
    'RefinanceAssumptions',
    'NinetyNinetyAnalyzer',
    'RefinanceSizer',
    'RefinanceDecisionFramework',
    
    # Phase 5: Ground Lease
    'CapitalizedGroundLeaseSizer',
    
    # Phase 6: Fees & Promote
    'DealFeeAssumptions',
    'PromoteStructure',
    'DealFeeCalculator',
    'PromoteCalculator',
    'NetReturnCalculator',
    
    # Phase 7: Exit Cap
    'InvestmentStrategy',
    'ExitCapInput',
    'ExitCapTriangulator',
    
    # Phase 8: Master Workflow
    'WorkflowPhase',
    'RecommendationType',
    'WorkflowStatus',
    'DealInputData',
    'CompleteUnderwritingWorkflow',
    'determine_recommendation',
]

