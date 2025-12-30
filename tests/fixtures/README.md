# Test Fixtures

This directory contains test data and mock files for the Dream AI test suite.

## Files

### `mock_deals.json`
Sample deal data with various property types, vintages, and classes:
- **Base Case Deal**: 200-unit Class B property in Atlanta (standard scenario)
- **Small Deal**: 75-unit property in Nashville
- **Large Deal**: 350-unit Class A tower in Charlotte  
- **Value-Add Deal**: 180-unit Class C property requiring heavy renovation

### Sample Documents (To Be Added)
- `sample_om.pdf` - Sample offering memorandum
- `sample_rent_roll.xlsx` - Sample rent roll
- `sample_t12.pdf` - Sample T-12 operating statement

## Usage in Tests

```python
import json
from pathlib import Path

# Load mock deals
fixtures_path = Path(__file__).parent / 'fixtures'
with open(fixtures_path / 'mock_deals.json') as f:
    deals = json.load(f)

# Use in test
base_case = deals['base_case_deal']
assert base_case['units'] == 200
```

## Adding New Fixtures

When adding new test fixtures:

1. **Use realistic data** - Base on actual market data
2. **Document source** - Note where data came from if applicable
3. **Provide context** - Explain what scenario the fixture represents
4. **Keep consistent** - Use same structure as existing fixtures
5. **Anonymize** - Remove any identifying information

## Fixture Guidelines

### Property Data
- Use realistic prices per unit for the market/class
- Ensure occupancy rates are reasonable (70-98%)
- Match rent levels to vintage and class

### Financial Data
- NOI should align with cap rate and purchase price
- Operating expenses should be 35-50% of EGI
- Rent growth assumptions should match market tier

### Scenarios
- **Base Case**: Most likely scenario
- **Upside**: Optimistic but achievable assumptions
- **Downside**: Conservative/pessimistic assumptions

