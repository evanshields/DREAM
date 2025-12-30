# Shieldstone Technical Manual v2.0 - Python Library

**Version:** 2.0.0  
**Date:** December 2025  
**Status:** Production Ready

A comprehensive Python library for multifamily value-add underwriting based on Shieldstone Acquisitions' Technical Manual Version 2.0. This library implements market-agnostic methodologies for institutional-quality deal analysis from initial screening through final investment recommendation.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Library Organization](#library-organization)
- [Phase-by-Phase Guide](#phase-by-phase-guide)
- [Complete Examples](#complete-examples)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Version History](#version-history)

---

## Features

### Core Capabilities

- **Risk-Adjusted Return Hurdles** - Calculate appropriate IRR, CoC, and equity multiple targets based on property characteristics, market tier, and risk factors
- **Merit-Based Deal Screening** - Identify true red flags vs. risk factors requiring hurdle adjustments
- **Property Tax Analysis** - Market-agnostic tax calculation with state-specific reassessment ratios
- **Refinancing Strategy** - 90/90 rule implementation, agency sizing, and refinance vs. sale decision framework
- **Ground Lease Financing** - Capitalized GL sizing, returns comparison, and decision matrix
- **Deal Fees & Promote** - Complete waterfall modeling with fee burden analysis
- **Exit Cap Triangulation** - Three-method validation (Treasury spread, exit comps, entry + strategy spread)
- **Master Workflow Integration** - Complete underwriting workflow from screening to final recommendation

### Key Standards

| Standard | Value | Notes |
|----------|-------|-------|
| **Minimum IRR** | 14% | Absolute floor |
| **Minimum Equity Multiple** | 1.5x | 5-year hold |
| **Net Investor IRR** | 15% | After fees/promote |
| **Stabilized CoC Floor** | 6-8% | Vintage-tiered |
| **Standard LTV** | 65% | On purchase price |
| **IO Period** | 30 months | Bridge financing |

---

## Installation

### Requirements

- Python 3.10 or higher
- numpy >= 1.21.0
- pandas >= 1.3.0

### Install Dependencies

```bash
cd shieldstone_library
pip install -r requirements.txt
```

### Import the Library

```python
# Import entire library
from shieldstone_v2_library import *

# Or import specific components
from shieldstone_v2_library import (
    ReturnHurdleCalculator,
    DealScreener,
    PropertyTaxCalculator,
    calculate_irr
)
```

---

## Quick Start

### Example 1: Calculate Risk-Adjusted Hurdles

```python
from shieldstone_v2_library import (
    MarketTier,
    PropertyProfile,
    RenovationScope,
    ReturnHurdleCalculator
)

# Define property characteristics
property = PropertyProfile(
    year_built=2015,
    unit_count=200,
    current_occupancy=0.88,
    renovation_scope=RenovationScope.MODERATE,
    renovation_cost_per_unit=12000,
    floating_rate_debt=False,
    market_distressed=False
)

# Calculate hurdles
calculator = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
result = calculator.calculate_adjusted_hurdle()

# Display results
print(f"Market Tier: {result['market_tier']}")
print(f"Base IRR Hurdle: {result['base_hurdle']:.1%}")
print(f"Total Risk Adjustment: +{result['total_adjustment_bps']} bps")
print(f"Final IRR Hurdle: {result['final_hurdle']:.1%}")
print(f"Stabilized CoC Floor: {result['coc_floor_stabilized']:.1%}")
```

**Output:**
```
Market Tier: secondary
Base IRR Hurdle: 17.5%
Total Risk Adjustment: +0 bps
Final IRR Hurdle: 17.5%
Stabilized CoC Floor: 7.0%
```

### Example 2: Screen a Deal

```python
from shieldstone_v2_library import ScreeningInput, DealScreener

# Define screening parameters
screening_data = ScreeningInput(
    property_age_years=37,  # 1988-built property
    current_occupancy=0.78,
    property_class='B',
    deferred_maintenance_per_unit=3500,
    unit_count=180,
    submarket_type='primary',
    # All red flags = False (no deal-killers)
)

# Run screening
screener = DealScreener(screening_data)
result = screener.screen()

print(f"Recommendation: {result['recommendation']}")
print(f"Hurdle Adjustment: +{result['risk_adjustments']['total_hurdle_adjustment_bps']} bps")
print(f"Contingency Add: +{result['risk_adjustments']['total_contingency_adjustment_pct']}%")
```

**Output:**
```
Recommendation: PROCEED
Hurdle Adjustment: +150 bps
Contingency Add: +5%
```

### Example 3: Calculate Property Taxes

```python
from shieldstone_v2_library import PropertyTaxInput, PropertyTaxCalculator

# Florida property example
tax_input = PropertyTaxInput(
    purchase_price=12_700_000,
    current_assessed_value=9_500_000,
    current_annual_taxes=137_819,
    county='Seminole',
    state='FL',
    reassessment_ratio=0.70  # Florida default
)

# Calculate taxes
tax_calc = PropertyTaxCalculator(tax_input)
result = tax_calc.calculate()

print(f"Purchase Price: ${result['purchase_price']:,.0f}")
print(f"Reassessment Ratio: {result['reassessment_ratio']:.0%}")
print(f"New Assessed Value: ${result['new_assessed_value']:,.0f}")
print(f"Year 1 Taxes: ${result['year_1_taxes']:,.0f}")
print(f"Tax Increase: ${result['tax_increase_dollars']:,.0f} ({result['tax_increase_pct']:.1%})")
```

**Output:**
```
Purchase Price: $12,700,000
Reassessment Ratio: 70%
New Assessed Value: $8,890,000
Year 1 Taxes: $129,090
Tax Increase: -$8,729 (-6.3%)
```

---

## Library Organization

The library is organized by workflow phase, matching the Shieldstone Manual structure:

```
shieldstone_library/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── shieldstone_v2_library.py          # Main consolidated library
├── __init__.py                        # Package initialization
├── phase_1_return_hurdles.py          # Section 1.1 implementation
├── phase_2_deal_screening.py          # Section 2.1 implementation
├── examples/                          # Usage examples
│   ├── example_1_return_hurdles.py
│   ├── example_2_screening.py
│   └── example_complete_workflow.ipynb
├── tests/                             # Unit tests
│   ├── test_return_hurdles.py
│   ├── test_screening.py
│   └── test_property_tax.py
└── sample_data/                       # Test data
    ├── sample_deal_tampa.json
    ├── sample_deal_nashville.json
    └── sample_rent_roll.csv
```

---

## Phase-by-Phase Guide

### Phase 1: Return Hurdles (Section 1.1)

Calculate risk-adjusted return requirements based on market tier and property characteristics.

**Key Classes:**
- `MarketTier` - Gateway/Secondary/Tertiary classification
- `RenovationScope` - Light/Moderate/Heavy intensity
- `PropertyProfile` - Property characteristics dataclass
- `ReturnHurdleCalculator` - Main calculation engine

**Usage:**
```python
calculator = ReturnHurdleCalculator(market_tier, property_profile)
hurdles = calculator.calculate_adjusted_hurdle()
evaluation = calculator.evaluate_deal(projected_irr, projected_coc, projected_em, net_irr)
```

**Returns:**
- Base IRR hurdle from market tier
- Risk premium adjustments (renovation, age, occupancy, financing, market cycle)
- Final hurdle (max of adjusted and absolute minimum 14%)
- Vintage-tiered CoC floor (6-8%)
- Equity multiple minimum (1.5x)

---

### Phase 2: Deal Screening (Section 2.1)

Merit-based screening that distinguishes between red flags (deal-killers) and risk factors (requiring adjustment).

**Key Classes:**
- `ScreeningInput` - Property and market data
- `DealScreener` - Screening engine with red flag checking

**Red Flags (True Deal-Killers):**
- Structural issues without guaranteed remediation
- Environmental contamination (active)
- Severe flood zone (FEMA A/V) without mitigation
- Unresolved code violations
- High crime (>2.5x national average)
- Population decline (>1%/year for 5+ years)
- Single employer risk (>40% concentration)
- Title defects
- Active litigation affecting transfer
- Zoning non-conformance

**Risk Factors (Require Adjustment, Not Disqualification):**
- Property age (even 50+ years allowed with adjustments)
- Low occupancy (risk-adjust, don't auto-reject)
- Property class (C/D require realistic assumptions)
- Deferred maintenance (budget appropriately)
- Submarket type

**Usage:**
```python
screener = DealScreener(screening_input)
result = screener.screen()

if result['passed_screening']:
    # Apply hurdle adjustments from result['risk_adjustments']
    proceed_to_underwriting()
```

---

### Phase 3: Property Tax Analysis (Section 4.2)

Market-agnostic property tax calculation using state-specific reassessment ratios.

**Key Principle:** Property taxes DO NOT reassess at 100% of purchase price in most states.

**State-Specific Ratios:**
- Florida: 70%
- Texas: 65%
- Georgia: 40%
- Arizona: 15%
- California, Colorado, MA, WA: 100%
- Default (when uncertain): 70%

**Calculation Method:**
```
New Assessed Value = Purchase Price × Reassessment Ratio
Year 1 Taxes = New Assessed Value × Millage Rate
Future Years = Year 1 × (1 + 3% annual growth)
```

**Usage:**
```python
tax_calc = PropertyTaxCalculator(tax_input)
result = tax_calc.calculate(projection_years=5)
# Returns year-by-year projection with methodology documentation
```

---

## Complete Examples

### Example: Full Deal Evaluation

```python
from shieldstone_v2_library import *

# Step 1: Screen the deal
screening = ScreeningInput(
    property_age_years=35,
    current_occupancy=0.82,
    property_class='B',
    deferred_maintenance_per_unit=2500,
    unit_count=180,
    submarket_type='primary'
)

screener = DealScreener(screening)
screening_result = screener.screen()

if not screening_result['passed_screening']:
    print(f"FAIL: {screening_result['reason']}")
    exit()

print(f"✓ Screening PASSED: {screening_result['recommendation']}")
hurdle_adjustment = screening_result['risk_adjustments']['total_hurdle_adjustment_bps']

# Step 2: Calculate adjusted hurdles
property = PropertyProfile(
    year_built=1990,
    unit_count=180,
    current_occupancy=0.82,
    renovation_scope=RenovationScope.MODERATE,
    renovation_cost_per_unit=14000,
    floating_rate_debt=False
)

hurdle_calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
hurdles = hurdle_calc.calculate_adjusted_hurdle()

print(f"\nFinal IRR Hurdle: {hurdles['final_hurdle']:.1%}")
print(f"CoC Floor: {hurdles['coc_floor_stabilized']:.1%}")

# Step 3: Calculate property taxes
tax_input = PropertyTaxInput(
    purchase_price=12_000_000,
    current_assessed_value=9_000_000,
    current_annual_taxes=120_000,
    county='Hillsborough',
    state='FL',
    reassessment_ratio=0.70
)

tax_result = PropertyTaxCalculator(tax_input).calculate()
print(f"\nYear 1 Property Taxes: ${tax_result['year_1_taxes']:,.0f}")
print(f"Tax Increase: ${tax_result['tax_increase_dollars']:,.0f}")

# Step 4: Evaluate returns
# (Assume you've calculated these from your pro forma)
projected_irr = 0.185  # 18.5%
projected_coc = 0.075  # 7.5%
projected_em = 1.75    # 1.75x
net_investor_irr = 0.16  # 16% after fees/promote

evaluation = hurdle_calc.evaluate_deal(
    projected_irr, projected_coc, projected_em, net_investor_irr
)

print(f"\n{'='*60}")
print(f"FINAL RECOMMENDATION: {evaluation['recommendation']}")
print(f"{'='*60}")
print(f"\nIRR: {projected_irr:.1%} vs. {hurdles['final_hurdle']:.1%} hurdle")
print(f"  Margin: {evaluation['evaluation']['irr_margin']:.1%}")
print(f"  Status: {'✓ PASS' if evaluation['evaluation']['irr_pass'] else '✗ FAIL'}")

print(f"\nCoC: {projected_coc:.1%} vs. {hurdles['coc_floor_stabilized']:.1%} floor")
print(f"  Margin: {evaluation['evaluation']['coc_margin']:.1%}")
print(f"  Status: {'✓ PASS' if evaluation['evaluation']['coc_pass'] else '✗ FAIL'}")

if evaluation['failing_metrics']:
    print(f"\n⚠ Failing Metrics: {', '.join(evaluation['failing_metrics'])}")
```

---

## API Reference

### ReturnHurdleCalculator

```python
class ReturnHurdleCalculator:
    def __init__(self, market_tier: MarketTier, property_profile: PropertyProfile)
    
    def calculate_adjusted_hurdle(self) -> Dict:
        """
        Returns:
            dict with keys:
            - market_tier (str)
            - property_vintage (str)
            - property_age_years (int)
            - base_hurdle (float)
            - adjustments (dict)
            - adjustments_bps (dict)
            - total_adjustment (float)
            - total_adjustment_bps (int)
            - adjusted_hurdle (float)
            - absolute_minimum_irr (float)
            - final_hurdle (float)
            - binding_constraint (str)
            - coc_floor_stabilized (float)
            - equity_multiple_minimum (float)
            - net_investor_irr_minimum (float)
        """
    
    def evaluate_deal(self, projected_irr: float, projected_coc: float,
                      projected_em: float, net_investor_irr: float) -> Dict:
        """
        Returns:
            dict with keys:
            - hurdles (dict)
            - projected (dict)
            - evaluation (dict with pass/fail and margins)
            - recommendation (str)
            - failing_metrics (list)
        """
```

### DealScreener

```python
class DealScreener:
    def __init__(self, screening_input: ScreeningInput)
    
    def check_red_flags(self) -> Tuple[bool, List[Dict]]:
        """Returns (has_red_flags, red_flag_details)"""
    
    def calculate_risk_adjustments(self) -> Dict:
        """
        Returns:
            dict with keys:
            - total_hurdle_adjustment_bps (int)
            - total_contingency_adjustment_pct (float)
            - risk_factors (list of dicts)
            - overall_risk_level (str)
        """
    
    def screen(self) -> Dict:
        """
        Returns:
            dict with keys:
            - passed_screening (bool)
            - recommendation (str): PROCEED/PROCEED_WITH_CAUTION/REQUEST_REPRICING/PASS
            - reason (str)
            - red_flags (list)
            - risk_adjustments (dict or None)
            - next_steps (list)
        """
```

### PropertyTaxCalculator

```python
class PropertyTaxCalculator:
    def __init__(self, tax_input: PropertyTaxInput)
    
    def calculate(self, projection_years: int = 5) -> Dict:
        """
        Returns:
            dict with keys:
            - purchase_price (float)
            - reassessment_ratio (float)
            - new_assessed_value (float)
            - millage_rate (float)
            - current_annual_taxes (float)
            - year_1_taxes (float)
            - tax_increase_dollars (float)
            - tax_increase_pct (float)
            - projection (dict: year_N -> tax amount)
            - growth_rate_assumed (float)
        """
```

### Helper Functions

```python
def calculate_irr(cash_flows: List[float], guess: float = 0.10) -> float:
    """
    Calculate IRR using Newton-Raphson method.
    
    Args:
        cash_flows: List starting with Year 0 (negative = investment)
        guess: Initial IRR guess
    
    Returns:
        IRR as decimal (e.g., 0.175 for 17.5%)
    """
```

---

## Testing

### Run Unit Tests

```bash
cd shieldstone_library
pytest tests/
```

### Test Coverage

- `test_return_hurdles.py` - Hurdle calculation validation
- `test_screening.py` - Red flag and risk adjustment logic
- `test_property_tax.py` - Tax calculation accuracy
- `test_integration.py` - End-to-end workflow

### Sample Test

```python
def test_return_hurdle_secondary_market():
    property = PropertyProfile(
        year_built=2015,
        unit_count=200,
        current_occupancy=0.88,
        renovation_scope=RenovationScope.MODERATE,
        renovation_cost_per_unit=12000,
        floating_rate_debt=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    result = calc.calculate_adjusted_hurdle()
    
    assert result['final_hurdle'] >= 0.14  # Absolute minimum
    assert result['coc_floor_stabilized'] >= 0.06  # Minimum CoC
    assert result['equity_multiple_minimum'] == 1.50
```

---

## Version History

### Version 2.0.0 (December 2025)
- **Major Update:** Complete transformation to market-agnostic framework
- Raised minimum IRR from 12% to 14%
- Raised equity multiple from 1.4x to 1.5x
- Added 15% net investor IRR minimum (after fees/promote)
- Removed all hard disqualifiers (age caps, occupancy minimums)
- Implemented vintage-tiered CoC floors (6-8% by property age)
- Added state-specific property tax framework
- Implemented three-method exit cap triangulation
- Added bridge-to-agency refinancing strategy (90/90 rule)
- Added capitalized ground lease financing framework
- Added complete deal fees & promote structure
- Added 8-phase master workflow
- Added 150+ term comprehensive glossary
- Production-ready Python implementations

### Version 1.0 (Original)
- Florida-centric framework
- Hard disqualifiers on age and occupancy
- Single-method exit cap calculation
- Basic hurdle structure

---

## Support & Documentation

- **Full Manual:** See `SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md`
- **Integration Guide:** See `SHIELDSTONE_INTEGRATION_GUIDE.md` (if available)
- **Jupyter Examples:** See `examples/example_complete_workflow.ipynb`

---

## License

Proprietary - Shieldstone Acquisitions

---

## About Shieldstone Acquisitions

Shieldstone Acquisitions is a multifamily value-add investment firm focused on institutional-quality underwriting and execution across gateway, secondary, and tertiary markets nationwide.

**Philosophy:** Economics determine viability, not arbitrary rules. Every deal deserves merit-based evaluation with appropriate risk adjustments.

---

**Questions or Issues?** Contact the development team or refer to the complete technical manual for detailed methodology explanations.

