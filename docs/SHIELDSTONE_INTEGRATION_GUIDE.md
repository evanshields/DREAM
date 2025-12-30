# Shieldstone Integration Guide for DreamVision

**Purpose:** Step-by-step guide for integrating Shieldstone underwriting methodologies into the DREAM app.

---

## Overview

The Shieldstone Technical Underwriting Manual provides production-ready Python implementations that can be directly integrated into DreamVision. This guide shows how to use them in each phase of development.

---

## Phase 1: BOE Analysis Integration

### 1. Deal Screening (Hard Stops)

**Location:** `src/lib/shieldstone/deal_screening.py`

**Usage:**
```python
from src.lib.shieldstone import DealScreener

# In deal intake endpoint
property_details = {
    'unit_count': 180,
    'property_age': 27,
    'occupancy': 0.78,
    'declining_market': False,
    'high_crime_area': False,
    'structural_issues': False,
    'environmental_contamination': False,
    'severe_flood_risk': False
}

screener = DealScreener(property_details)
result = screener.screen()

if not result['passed']:
    return {
        'status': 'disqualified',
        'reason': result['reason'],
        'disqualifiers': result['disqualifiers']
    }
```

**Integration Points:**
- `POST /api/deals/{id}/analyze` - Run screening before full analysis
- Deal intake form - Show disqualifiers immediately
- Pipeline board - Auto-move disqualified deals to "Passed" stage

---

### 2. Return Hurdle Calculation

**Location:** `src/lib/shieldstone/return_hurdles.py`

**Usage:**
```python
from src.lib.shieldstone import ReturnHurdleCalculator

# Determine market tier from market research
market_tier = 'secondary'  # gateway, secondary, or tertiary

property_characteristics = {
    'heavy_renovation': True,
    'occupancy': 0.78,
    'property_age': 27,
    'market_downturn': False,
    'floating_rate_debt': True
}

calculator = ReturnHurdleCalculator(market_tier, property_characteristics)
hurdle_analysis = calculator.calculate_adjusted_hurdle()

# Use in scoring
required_irr = hurdle_analysis['final_hurdle']
```

**Integration Points:**
- Investment criteria engine - Set default hurdles by market tier
- Scoring framework - Compare projected IRR vs required hurdle
- BOE memo - Show hurdle analysis in risk section

---

### 3. Investment Criteria Defaults

**Location:** `src/lib/shieldstone/constants.py`

**Usage:**
```python
from src.lib.shieldstone.constants import (
    MIN_UNITS,
    MAX_PROPERTY_AGE,
    MIN_OCCUPANCY,
    MIN_IRR,
    MIN_COC_STABILIZED
)

# Set default investment criteria for new users
default_criteria = {
    'hard_stops': {
        'min_units': MIN_UNITS,
        'max_property_age': MAX_PROPERTY_AGE,
        'min_occupancy': MIN_OCCUPANCY,
    },
    'return_targets': {
        'min_irr': MIN_IRR,
        'min_coc_stabilized': MIN_COC_STABILIZED,
    }
}
```

**Integration Points:**
- Onboarding wizard - Pre-populate criteria with Shieldstone defaults
- Settings page - Show Shieldstone standards as reference
- Criteria editor - Allow users to override while showing defaults

---

## Phase 2: DCF Modeling Integration

### 1. Loan Sizing

**Location:** `src/lib/shieldstone/financing.py`

**Usage:**
```python
from src.lib.shieldstone import LoanSizer

# Calculate loan and equity requirements
sizer = LoanSizer(
    purchase_price=12_700_000,
    closing_cost_pct=0.03
)

result = sizer.calculate_loan_and_equity(
    total_capex=4_680_000,
    stabilized_noi=1_250_000,
    interest_rate=0.0575,  # 5yr Treasury + 150bps
    required_dscr=1.25
)

# Use in sources & uses
loan_amount = result['loan_amount']
total_equity = result['equity_breakdown']['total_equity']
```

**Integration Points:**
- Financing assumptions page - Auto-calculate loan size
- Sources & uses table - Populate automatically
- DCF model - Use for debt service calculations

---

### 2. IRR Calculation

**Location:** `src/lib/shieldstone/returns.py`

**Usage:**
```python
from src.lib.shieldstone import IRRCalculator

# Calculate levered IRR
calc = IRRCalculator(
    total_equity=8_926_000,
    hold_period_years=5
)

cash_flows = [150000, 280000, 520000, 680000, 720000]  # Years 1-5
exit_proceeds = 6_200_000

result = calc.calculate_levered_irr(cash_flows, exit_proceeds)

irr = result['levered_irr']
equity_multiple = result['equity_multiple']
```

**Integration Points:**
- Returns dashboard - Display IRR and equity multiple
- Sensitivity analysis - Recalculate IRR for each scenario
- IC memo - Include in returns summary

---

### 3. Renovation Budget & ROI

**Reference:** Section 5.1 (Python code in manual)

**Implementation Needed:**
```python
# Create src/lib/shieldstone/capex.py
from src.lib.shieldstone.constants import RENOVATION_SCOPES

class RenovationBudgetBuilder:
    def calculate_budget(self, scope: str, current_rent: float):
        # Implementation from manual Section 5.1
        pass
```

**Integration Points:**
- Capex planning page - Calculate renovation budgets
- ROI validation - Ensure 8% threshold met
- DCF model - Include capex in cash flow projections

---

## Phase 3: Risk Assessment Integration

### 1. Execution Risk Scoring

**Location:** `src/lib/shieldstone/risk.py`

**Usage:**
```python
from src.lib.shieldstone import ExecutionRiskAnalyzer

risk_analyzer = ExecutionRiskAnalyzer()
reno_risk = risk_analyzer.assess_renovation_risk(
    scope='heavy',
    property_age=27,
    contractor_experience='proven'
)

# Use in overall risk score (35% weight)
execution_risk_score = reno_risk['risk_rating']
```

**Integration Points:**
- Risk assessment component - Include execution risk
- Scoring framework - Apply 35% weight to execution risk
- BOE memo - Show risk breakdown

---

## Data Model Extensions

### Deal Model Additions

```python
# Add to Deal model
class Deal(BaseModel):
    # ... existing fields ...
    
    # Shieldstone-specific fields
    market_tier: Optional[str]  # gateway, secondary, tertiary
    property_characteristics: Optional[Dict]  # For hurdle calculation
    screening_result: Optional[Dict]  # DealScreener output
    hurdle_analysis: Optional[Dict]  # ReturnHurdleCalculator output
```

### Analysis Model Additions

```python
# Add to Analysis model
class Analysis(BaseModel):
    # ... existing fields ...
    
    # Shieldstone standards applied
    shieldstone_standards_applied: bool = True
    financing_assumptions: Optional[Dict]  # LoanSizer output
    returns_analysis: Optional[Dict]  # IRRCalculator output
    risk_assessment: Optional[Dict]  # ExecutionRiskAnalyzer output
```

---

## API Endpoints

### New Endpoints

```python
# GET /api/deals/{id}/screening
# Run deal screening checks
def screen_deal(deal_id: int):
    deal = get_deal(deal_id)
    screener = DealScreener(deal.property_details)
    return screener.screen()

# GET /api/deals/{id}/hurdles
# Calculate return hurdles
def calculate_hurdles(deal_id: int):
    deal = get_deal(deal_id)
    calculator = ReturnHurdleCalculator(
        deal.market_tier,
        deal.property_characteristics
    )
    return calculator.calculate_adjusted_hurdle()

# POST /api/deals/{id}/financing
# Calculate loan sizing
def calculate_financing(deal_id: int, capex: float, noi: float):
    deal = get_deal(deal_id)
    sizer = LoanSizer(deal.purchase_price)
    return sizer.calculate_loan_and_equity(capex, noi)
```

---

## Frontend Integration

### Investment Criteria Component

```typescript
// Use Shieldstone defaults in criteria editor
import { SHIELDSTONE_DEFAULTS } from '@/lib/shieldstone/constants';

const InvestmentCriteriaEditor = () => {
  const [criteria, setCriteria] = useState(SHIELDSTONE_DEFAULTS);
  
  return (
    <div>
      <h3>Investment Criteria</h3>
      <p>Based on Shieldstone Acquisitions standards</p>
      {/* Criteria editor UI */}
    </div>
  );
};
```

### Deal Screening Badge

```typescript
// Show screening status in deal card
const DealCard = ({ deal }) => {
  const screening = deal.screening_result;
  
  return (
    <div>
      {screening?.passed ? (
        <Badge color="green">Passed Screening</Badge>
      ) : (
        <Badge color="red">Disqualified</Badge>
      )}
    </div>
  );
};
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_shieldstone/test_deal_screening.py
def test_deal_screener_min_units():
    details = {'unit_count': 40}  # Below minimum
    screener = DealScreener(details)
    result = screener.screen()
    assert not result['passed']
    assert 'below minimum' in result['reason']

# tests/test_shieldstone/test_return_hurdles.py
def test_secondary_market_base_hurdle():
    calc = ReturnHurdleCalculator('secondary', {})
    hurdle = calc.calculate_adjusted_hurdle()
    assert 0.16 <= hurdle['base_hurdle'] <= 0.19
```

### Integration Tests

```python
# tests/integration/test_boe_analysis.py
def test_full_boe_analysis_with_shieldstone():
    # Create deal
    # Run screening
    # Calculate hurdles
    # Generate BOE memo
    # Verify Shieldstone standards applied
    pass
```

---

## Configuration

### Environment Variables

```bash
# .env
SHIELDSTONE_STANDARDS_ENABLED=true
SHIELDSTONE_DEFAULT_MARKET_TIER=secondary
SHIELDSTONE_FL_TAX_REASSESSMENT=0.70
```

### User Preferences

Allow users to:
- Enable/disable Shieldstone standards
- Override default market tier
- Adjust risk adjustment factors
- Customize hard-stop criteria

---

## Migration Path

### Phase 1 (Week 1-2)
1. ✅ Add Shieldstone Python modules to codebase
2. ✅ Integrate `DealScreener` into deal intake
3. ✅ Use `ReturnHurdleCalculator` for investment criteria defaults
4. ✅ Add Shieldstone standards to BOE memo generation

### Phase 2 (Week 3-8)
1. ✅ Integrate `LoanSizer` into financing assumptions
2. ✅ Integrate `IRRCalculator` into returns analysis
3. ✅ Add `RenovationBudgetBuilder` for capex planning
4. ✅ Include Shieldstone calculations in DCF model

### Phase 3 (Week 9+)
1. ✅ Integrate `ExecutionRiskAnalyzer` into risk scoring
2. ✅ Add `DueDiligenceTimeline` to pipeline CRM
3. ✅ Implement variance analysis frameworks
4. ✅ Add Shieldstone report templates

---

## Documentation

### User-Facing Docs

Create help articles:
- "Understanding Investment Criteria"
- "How We Calculate Return Hurdles"
- "Deal Screening Standards"
- "Shieldstone Methodology Overview"

### Developer Docs

- API documentation for Shieldstone modules
- Integration examples
- Testing guidelines
- Extension points for customization

---

## Next Steps

1. **Review Python modules** - Ensure compatibility with FastAPI/PostgreSQL stack
2. **Create database migrations** - Add Shieldstone-specific fields
3. **Build API endpoints** - Expose Shieldstone calculations
4. **Update frontend** - Integrate into UI components
5. **Write tests** - Ensure accuracy of calculations
6. **Documentation** - User and developer guides

---

**Last Updated:** 2025-01-XX  
**Status:** Ready for Phase 1 integration




