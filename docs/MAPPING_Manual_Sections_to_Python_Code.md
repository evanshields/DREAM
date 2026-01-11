# Shieldstone Manual Sections → Python Code Mapping

**Complete reference mapping between Shieldstone Technical Manual v2.0 sections and Python implementation files**

---

## Quick Reference Table

| Manual Section | Python File(s) | Main Classes/Functions | Status |
|---------------|----------------|------------------------|--------|
| **Section 1.1** - Return Hurdles | `phase_1_return_hurdles.py` | `ReturnHurdleCalculator`, `MarketTier`, `PropertyProfile` | ✅ Complete |
| **Section 2.1** - Deal Screening | `phase_2_deal_screening.py` | `DealScreener`, `ScreeningInput`, `RedFlagCategory` | ✅ Complete |
| **Section 3** - Revenue Underwriting | (Conceptual - integrated in workflow) | Revenue validation logic in `phase_8_master_workflow.py` | 🔄 Integrated |
| **Section 4.2** - Property Tax | `shieldstone_v2_library.py` (Phase 3) | `PropertyTaxCalculator`, `PropertyTaxInput` | ✅ Complete |
| **Section 5** - Capex Planning | (Conceptual - integrated in workflow) | Capex ROI logic in `phase_8_master_workflow.py` | 🔄 Integrated |
| **Section 6.5** - Refinancing Strategy | `phase_4_refinancing.py` | `NinetyNinetyAnalyzer`, `RefinanceSizer`, `RefinanceDecisionFramework` | ✅ Complete |
| **Section 6.6** - Ground Lease Financing | `phase_5_ground_lease.py` | `CapitalizedGroundLeaseSizer` | ✅ Complete |
| **Section 6.7** - Deal Fees & Promote | `phase_6_fees_promote.py` | `DealFeeCalculator`, `PromoteCalculator`, `NetReturnCalculator` | ✅ Complete |
| **Section 7.2** - Exit Cap Triangulation | `phase_7_exit_cap.py` | `ExitCapTriangulator`, `ExitCapInput` | ✅ Complete |
| **Section 13** - Master Workflow | `phase_8_master_workflow.py` | `CompleteUnderwritingWorkflow`, `DealInputData`, `determine_recommendation` | ✅ Complete |

---

## Detailed Section-by-Section Mapping

### PART I: Foundation (Sections 1-4)

---

#### **Section 1.1: Investment Philosophy & Return Hurdles**

**Python File:** `shieldstone_library/phase_1_return_hurdles.py`

**Main Classes:**
- `MarketTier` (Enum) - Gateway/Secondary/Tertiary classification
- `RenovationScope` (Enum) - Light/Moderate/Heavy renovation intensity
- `PropertyProfile` (dataclass) - Property characteristics (age, units, occupancy, renovation scope)
- `ReturnHurdleCalculator` (class) - Main calculation engine

**Key Methods:**
- `ReturnHurdleCalculator.calculate_adjusted_hurdle()` - Calculates risk-adjusted IRR hurdle
- `ReturnHurdleCalculator.evaluate_deal()` - Compares projected returns to hurdles

**What It Does:**
- Calculates base IRR hurdle from market tier (Gateway: 16%, Secondary: 17.5%, Tertiary: 19%)
- Applies risk adjustments for property age, occupancy, renovation scope, financing type
- Sets vintage-tiered Cash-on-Cash floors (6-8% by property age)
- Enforces absolute minimums (14% IRR, 6% CoC, 1.5x Equity Multiple)

**Related Files:**
- Tests: `tests/test_return_hurdles.py`
- Example: `examples/example_1_return_hurdles.py`

---

#### **Section 1.2: Deal Screening Criteria**

**Note:** The manual index references Section 1.2, but the implementation uses **Section 2.1** from the v2.0 manual.

**Python File:** `shieldstone_library/phase_2_deal_screening.py`

**Main Classes:**
- `RedFlagCategory` (Enum) - Categories of deal-killing red flags
- `RiskLevel` (Enum) - Risk level classifications
- `ScreeningInput` (dataclass) - Property and market data for screening
- `DealScreener` (class) - Screening engine

**Key Methods:**
- `DealScreener.check_red_flags()` - Identifies true deal-killers
- `DealScreener.calculate_risk_adjustments()` - Calculates hurdle adjustments for risk factors
- `DealScreener.screen()` - Main screening function

**What It Does:**
- Checks for red flags (fatal flaws): structural issues, environmental contamination, flood zones, crime, population decline, etc.
- Identifies risk factors (require adjustment, not rejection): property age, low occupancy, deferred maintenance, property class
- Calculates hurdle adjustments (basis points) and contingency adjustments (percentage) based on risk factors
- Makes recommendation: PROCEED, PROCEED_WITH_CAUTION, REQUEST_REPRICING, or PASS

**Related Files:**
- Tests: `tests/test_screening.py`
- Example: `examples/example_2_screening.py`

---

#### **Section 1.3: Market Selection Framework**

**Status:** Conceptual - Market scoring logic referenced but not separately implemented

**Where Used:** Integrated into `phase_8_master_workflow.py` Phase 2 (Market Analysis)

**Note:** Market analysis scoring is simplified in the master workflow implementation.

---

#### **Section 1.4: Competitive Supply Analysis**

**Status:** Conceptual - Not separately implemented

**Where Used:** Referenced in manual for market research, but not implemented as standalone Python code.

---

#### **Section 2: Data Collection & Validation**

**Status:** Conceptual - Document quality scoring and reconciliation checks not implemented as standalone Python code

**Where Used:** Referenced in manual for document processing quality metrics, but implementation would be in document processing layer (outside Shieldstone library scope).

---

#### **Section 3: Revenue Underwriting**

**Status:** Integrated into master workflow

**Where Used:** `phase_8_master_workflow.py` - Phase 3 (Revenue Underwriting)

**Implementation:**
- Revenue validation logic is integrated into `CompleteUnderwritingWorkflow._phase_3_revenue()` method
- Validates rent premium assumptions (current rent vs. target rent)
- Checks if rent premium exceeds reasonable caps based on property age

**Key Logic:**
- Calculates implied rent premium (target rent - current rent) / current rent
- Sets max premium caps based on property age (15% for >30 years, 20% for ≤30 years)
- Flags aggressive rent assumptions

**Note:** Full revenue underwriting methodology (in-place rent analysis, market rent determination, renovation rent premium, rent growth projections) is documented in manual but simplified in workflow implementation.

---

#### **Section 4.2: Property Tax Analysis**

**Python File:** `shieldstone_library/shieldstone_v2_library.py` (consolidated library, Phase 3 section)

**Main Classes:**
- `PropertyTaxInput` (dataclass) - Property tax input data
- `PropertyTaxCalculator` (class) - Property tax calculation engine

**Key Methods:**
- `PropertyTaxCalculator.calculate()` - Calculates property taxes for Year 1 and future years

**What It Does:**
- Calculates property tax reassessment based on state-specific ratios (NOT 100% in most states)
- State-specific ratios: Florida: 70%, Texas: 65%, Georgia: 40%, Arizona: 15%, etc.
- Projects future year taxes with 3% annual growth assumption
- Returns Year 1 taxes and multi-year projection

**Key Formula:**
```
New Assessed Value = Purchase Price × Reassessment Ratio
Year 1 Taxes = New Assessed Value × Millage Rate
Future Years = Year 1 × (1 + 3% annual growth)
```

**Related Files:**
- Tests: `tests/test_property_tax.py`

---

### PART II: Analysis & Risk (Sections 5-9)

---

#### **Section 5: Capital Expenditure Planning**

**Status:** Integrated into master workflow

**Where Used:** `phase_8_master_workflow.py` - Phase 5 (Capex Planning)

**Implementation:**
- Capex ROI calculation logic is integrated into `CompleteUnderwritingWorkflow._phase_5_capex()` method
- Validates renovation budget ROI against 8% minimum threshold

**Key Logic:**
- Calculates annual rent increase from renovations
- Calculates achievable NOI increase (rent increase × 75% efficiency)
- Calculates Capex ROI = Achievable NOI Increase / Renovation Cost Total
- Flags if ROI < 8% minimum

**Note:** Full capex planning methodology (renovation scope development, budget validation, ROI threshold of 8%) is documented in manual but simplified in workflow implementation.

---

#### **Section 6: Financing Structure**

**Note:** Section 6 has multiple subsections. Only 6.5, 6.6, and 6.7 have dedicated Python implementations.

**Subsections:**
- **6.3 - Loan Sizing:** Integrated into `phase_8_master_workflow.py` Phase 6 (Financing)
- **6.5 - Refinancing Strategy:** ✅ Separate implementation (see below)
- **6.6 - Ground Lease Financing:** ✅ Separate implementation (see below)
- **6.7 - Deal Fees & Promote:** ✅ Separate implementation (see below)

---

#### **Section 6.5: Refinancing Strategy & Feasibility**

**Python File:** `shieldstone_library/phase_4_refinancing.py`

**Main Classes:**
- `RenovationStrategy` (Enum) - Light/Moderate/Heavy renovation strategies
- `RefinancePropertyProfile` (dataclass) - Property characteristics for refinancing
- `RefinanceAssumptions` (dataclass) - Refinancing assumptions (rates, timelines)
- `NinetyNinetyAnalyzer` (class) - 90/90 rule timeline calculator
- `RefinanceSizer` (class) - Agency loan sizing calculator
- `RefinanceDecisionFramework` (class) - Refinance vs. sale decision logic

**Key Methods:**
- `NinetyNinetyAnalyzer.calculate_timeline()` - Calculates if 90/90 rule is achievable
- `RefinanceSizer.size_agency_loan()` - Sizes agency loan using DSCR and LTV constraints
- `RefinanceDecisionFramework.analyze()` - Compares refinance vs. sale scenarios

**What It Does:**
- **90/90 Rule:** Checks if property can stabilize (90% occupancy, 90% of target rent) within 90 days of renovation completion
- **Agency Loan Sizing:** Sizes Fannie/Freddie loans using DSCR and LTV constraints
- **Refinance vs. Sale:** Compares refinancing to sale scenarios, considering interest rates, exit caps, and equity returns

**Related Concepts:**
- Bridge loan to agency loan refinancing strategy
- 30-month IO period on bridge loans
- Agency loan qualification (DSCR ≥ 1.25x, LTV ≤ 75%)

---

#### **Section 6.6: Ground Lease Financing**

**Python File:** `shieldstone_library/phase_5_ground_lease.py`

**Main Classes:**
- `CapitalizedGroundLeaseSizer` (class) - Ground lease sizing calculator

**Key Methods:**
- `CapitalizedGroundLeaseSizer.size()` - Sizes ground lease using three constraints:
  1. DSCR constraint (NOI / GL rent ≥ coverage ratio)
  2. NOI coverage constraint (GL rent ≤ max NOI percentage)
  3. Cap rate constraint (GL rent / land value ≤ cap rate)

**What It Does:**
- Calculates maximum ground lease rent using three-method constraint approach
- Compares returns with vs. without ground lease financing
- Analyzes coverage ratios and rent escalation schedules

**Key Concepts:**
- Ground lease as alternative financing structure
- Capitalized ground lease sizing (rent vs. land value)
- Coverage ratio analysis

---

#### **Section 6.7: Deal Fees & Promote Structures**

**Python File:** `shieldstone_library/phase_6_fees_promote.py`

**Main Classes:**
- `DealFeeAssumptions` (dataclass) - Deal fee assumptions (acquisition, asset management, etc.)
- `PromoteStructure` (dataclass) - Promote structure (preferred return, splits)
- `DealFeeCalculator` (class) - Calculates all deal fees
- `PromoteCalculator` (class) - Calculates promote waterfall
- `NetReturnCalculator` (class) - Calculates net investor returns (after fees/promote)

**Key Methods:**
- `DealFeeCalculator.calculate_all_fees()` - Calculates acquisition fees, asset management fees, disposition fees
- `PromoteCalculator.calculate_waterfall()` - Calculates promote waterfall (8% pref, 70/30 split, 50/50 split)
- `NetReturnCalculator.calculate_net_irr()` - Calculates net investor IRR after fees and promote

**What It Does:**
- Calculates all deal fees (acquisition, asset management, disposition, etc.)
- Models promote structure (preferred return, profit splits)
- Calculates net investor returns (after fees and promote)
- Compares gross returns vs. net returns

**Key Concepts:**
- Fee burden analysis
- Promote waterfall structure
- Net investor IRR (after fees/promote) must meet 15% minimum

---

#### **Section 7: Returns Analysis**

**Subsections:**
- **7.2 - Exit Cap Triangulation:** ✅ Separate implementation (see below)
- **7.4 - IRR Calculation:** Integrated into `phase_8_master_workflow.py` Phase 7 (Returns Analysis)

**Note:** IRR calculation logic is simplified in the master workflow. Full IRR calculator would be implemented separately.

---

#### **Section 7.2: Exit Cap Rate Triangulation**

**Python File:** `shieldstone_library/phase_7_exit_cap.py`

**Main Classes:**
- `InvestmentStrategy` (Enum) - Light/Moderate/Heavy value-add strategies
- `ExitCapInput` (dataclass) - Input data for exit cap calculation
- `ExitCapTriangulator` (class) - Three-method exit cap calculator

**Key Methods:**
- `ExitCapTriangulator.triangulate()` - Calculates exit cap using three methods and triangulates

**What It Does:**
- **Method 1: Treasury Spread** - Exit cap = Entry cap + Treasury spread + strategy spread
- **Method 2: Exit Comp Validation** - Exit cap from comparable sales
- **Method 3: Entry Cap + Strategy Spread** - Exit cap = Entry cap + strategy-specific spread
- **Triangulation:** Averages three methods (weights can be adjusted)
- Validates exit cap reasonableness across all three methods

**Key Concepts:**
- Exit cap rate determination (critical for IRR calculations)
- Three-method validation ensures defensible assumptions
- Strategy-specific spreads (Light: +50bps, Moderate: +75bps, Heavy: +100bps)

---

#### **Section 8: Risk Assessment**

**Status:** Conceptual - Risk assessment logic referenced but not separately implemented

**Where Used:** Integrated into `phase_8_master_workflow.py` Phase 8 (Risk Assessment & Final Recommendation)

**Implementation:**
- Risk assessment is integrated into `CompleteUnderwritingWorkflow._phase_8_final_recommendation()` method
- Counts warnings and phases passed
- Makes final recommendation based on risk factors

**Note:** Full risk assessment methodology (market risk evaluation, execution risk scoring, financial risk identification, risk aggregation framework) is documented in manual but simplified in workflow implementation.

---

#### **Section 9: Due Diligence Protocols**

**Status:** Conceptual - Not implemented as Python code

**Where Used:** Referenced in manual for DD workflow and milestone tracking, but implementation would be in workflow/CRM layer (outside Shieldstone library scope).

**Note:** Due diligence timeline (45-day: Phase I Days 1-10, Phase II Days 11-45) and third-party report analysis are documented but not implemented as Python classes.

---

### PART III: Exit & Workflow (Sections 10-13)

---

#### **Section 10: Exit Strategy**

**Status:** Conceptual - Not implemented as Python code

**Where Used:** Referenced in manual for exit strategy recommendations, but not implemented as standalone Python code.

---

#### **Section 11: Reporting & Monitoring**

**Status:** Conceptual - Not implemented as Python code

**Where Used:** Referenced in manual for report generation templates (IC memo format, monthly KPIs, variance analysis), but implementation would be in reporting layer (outside Shieldstone library scope).

---

#### **Section 12: Case Studies**

**Status:** Conceptual - Not implemented as Python code

**Where Used:** Referenced in manual for lessons learned and edge cases, but not implemented as Python code.

---

#### **Section 13: Complete Underwriting Workflow**

**Python File:** `shieldstone_library/phase_8_master_workflow.py`

**Main Classes:**
- `WorkflowPhase` (Enum) - Workflow execution phases
- `RecommendationType` (Enum) - Final recommendation types (PROCEED, PROCEED_WITH_CAUTION, REQUEST_REPRICING, PASS)
- `WorkflowStatus` (dataclass) - Tracks workflow progress and findings
- `DealInputData` (dataclass) - Complete deal input data structure
- `CompleteUnderwritingWorkflow` (class) - Master workflow orchestrator

**Key Methods:**
- `CompleteUnderwritingWorkflow.execute_complete_workflow()` - Executes all 8 phases
- `CompleteUnderwritingWorkflow._phase_1_screening()` - Phase 1: Deal Screening
- `CompleteUnderwritingWorkflow._phase_2_market_analysis()` - Phase 2: Market Analysis
- `CompleteUnderwritingWorkflow._phase_3_revenue()` - Phase 3: Revenue Underwriting
- `CompleteUnderwritingWorkflow._phase_4_expenses()` - Phase 4: Operating Expenses
- `CompleteUnderwritingWorkflow._phase_5_capex()` - Phase 5: Capital Expenditure Planning
- `CompleteUnderwritingWorkflow._phase_6_financing()` - Phase 6: Financing Structure
- `CompleteUnderwritingWorkflow._phase_7_returns()` - Phase 7: Returns Analysis
- `CompleteUnderwritingWorkflow._phase_8_final_recommendation()` - Phase 8: Risk Assessment & Final Recommendation
- `determine_recommendation()` - Standalone recommendation logic function

**What It Does:**
- Orchestrates complete underwriting workflow from screening through final recommendation
- Executes all 8 phases sequentially
- Stops early if Phase 1 (Screening) finds red flags
- Aggregates findings and warnings across all phases
- Makes final recommendation: PROCEED, PROCEED_WITH_CAUTION, REQUEST_REPRICING, or PASS
- Generates comprehensive final report with phase-by-phase details

**Key Features:**
- Complete workflow orchestration
- Phase-by-phase execution with status tracking
- Early exit on red flags
- Aggregated findings and warnings
- Systematic recommendation logic

**Related Concepts:**
- Integrates logic from Phases 1-7
- Uses simplified versions of revenue, expense, capex, and returns analysis
- Can be extended to use full implementations from individual phase modules

---

## Consolidated Library File

**File:** `shieldstone_library/shieldstone_v2_library.py`

**Purpose:** Consolidated library containing Phase 3 (Property Tax) and potentially other phases in a single file.

**Note:** Some phases are in standalone files (`phase_1_return_hurdles.py`, `phase_2_deal_screening.py`, etc.), while Phase 3 (Property Tax) is in the consolidated library file.

---

## Implementation Status Summary

| Status | Meaning |
|--------|---------|
| ✅ Complete | Fully implemented as standalone Python module(s) |
| 🔄 Integrated | Logic integrated into master workflow, but simplified |
| 📝 Conceptual | Documented in manual, but not implemented as Python code |

**Fully Implemented (✅):**
- Section 1.1 - Return Hurdles
- Section 2.1 - Deal Screening
- Section 4.2 - Property Tax
- Section 6.5 - Refinancing Strategy
- Section 6.6 - Ground Lease Financing
- Section 6.7 - Deal Fees & Promote
- Section 7.2 - Exit Cap Triangulation
- Section 13 - Master Workflow

**Integrated (🔄):**
- Section 3 - Revenue Underwriting (simplified in workflow)
- Section 5 - Capex Planning (simplified in workflow)
- Section 6.3 - Loan Sizing (simplified in workflow)
- Section 7.4 - IRR Calculation (simplified in workflow)
- Section 8 - Risk Assessment (simplified in workflow)

**Conceptual (📝):**
- Section 1.3 - Market Selection Framework
- Section 1.4 - Competitive Supply Analysis
- Section 2 - Data Collection & Validation
- Section 9 - Due Diligence Protocols
- Section 10 - Exit Strategy
- Section 11 - Reporting & Monitoring
- Section 12 - Case Studies

---

## Import Guide

### Import Individual Phases

```python
# Phase 1: Return Hurdles
from shieldstone_library.phase_1_return_hurdles import (
    ReturnHurdleCalculator,
    MarketTier,
    PropertyProfile
)

# Phase 2: Deal Screening
from shieldstone_library.phase_2_deal_screening import (
    DealScreener,
    ScreeningInput
)

# Phase 3: Property Tax
from shieldstone_library.shieldstone_v2_library import (
    PropertyTaxCalculator,
    PropertyTaxInput
)

# Phase 4: Refinancing
from shieldstone_library.phase_4_refinancing import (
    NinetyNinetyAnalyzer,
    RefinanceSizer,
    RefinanceDecisionFramework
)

# Phase 5: Ground Lease
from shieldstone_library.phase_5_ground_lease import (
    CapitalizedGroundLeaseSizer
)

# Phase 6: Fees & Promote
from shieldstone_library.phase_6_fees_promote import (
    DealFeeCalculator,
    PromoteCalculator,
    NetReturnCalculator
)

# Phase 7: Exit Cap
from shieldstone_library.phase_7_exit_cap import (
    ExitCapTriangulator
)

# Phase 8: Master Workflow
from shieldstone_library.phase_8_master_workflow import (
    CompleteUnderwritingWorkflow,
    DealInputData
)
```

### Import Everything

```python
from shieldstone_library import (
    # Phase 1
    ReturnHurdleCalculator,
    MarketTier,
    PropertyProfile,
    
    # Phase 2
    DealScreener,
    ScreeningInput,
    
    # Phase 3
    PropertyTaxCalculator,
    PropertyTaxInput,
    
    # Phase 4
    NinetyNinetyAnalyzer,
    RefinanceSizer,
    RefinanceDecisionFramework,
    
    # Phase 5
    CapitalizedGroundLeaseSizer,
    
    # Phase 6
    DealFeeCalculator,
    PromoteCalculator,
    NetReturnCalculator,
    
    # Phase 7
    ExitCapTriangulator,
    
    # Phase 8
    CompleteUnderwritingWorkflow,
    DealInputData
)
```

---

## File Structure Reference

```
shieldstone_library/
├── phase_1_return_hurdles.py      # Section 1.1
├── phase_2_deal_screening.py      # Section 2.1
├── phase_4_refinancing.py         # Section 6.5
├── phase_5_ground_lease.py        # Section 6.6
├── phase_6_fees_promote.py        # Section 6.7
├── phase_7_exit_cap.py            # Section 7.2
├── phase_8_master_workflow.py     # Section 13
├── shieldstone_v2_library.py      # Section 4.2 (consolidated)
├── __init__.py                    # Package exports
├── tests/                         # Unit tests
├── examples/                      # Usage examples
└── README.md                      # Library documentation
```

---

**Last Updated:** December 2025  
**Manual Version:** v2.0  
**Library Version:** 2.0.0

