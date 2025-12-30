"""
Unit Tests for Phase 3: Property Tax
=====================================

Tests for PropertyTaxCalculator and related components.
"""

import sys
sys.path.insert(0, '..')

from shieldstone_v2_library import PropertyTaxInput, PropertyTaxCalculator


def test_florida_property_tax():
    """Test Florida property with 70% reassessment ratio."""
    tax_input = PropertyTaxInput(
        purchase_price=12_700_000,
        current_assessed_value=9_500_000,
        current_annual_taxes=137_819,
        county='Seminole',
        state='FL',
        reassessment_ratio=0.70
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate()
    
    # Verify calculation
    expected_new_assessed = 12_700_000 * 0.70
    assert abs(result['new_assessed_value'] - expected_new_assessed) < 1
    assert result['reassessment_ratio'] == 0.70
    assert 'year_1' in result['projection']
    print("✓ Florida property tax calculation correct")


def test_texas_property_tax():
    """Test Texas property with 65% default ratio."""
    tax_input = PropertyTaxInput(
        purchase_price=15_000_000,
        current_assessed_value=11_000_000,
        current_annual_taxes=168_000,
        county='Travis',
        state='TX'
        # No ratio provided - should use TX default of 65%
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate()
    
    # Should use TX default
    assert result['reassessment_ratio'] == 0.65
    expected_new_assessed = 15_000_000 * 0.65
    assert abs(result['new_assessed_value'] - expected_new_assessed) < 1
    print("✓ Texas property tax with default ratio correct")


def test_california_full_reassessment():
    """Test California with 100% reassessment."""
    tax_input = PropertyTaxInput(
        purchase_price=50_000_000,
        current_assessed_value=35_000_000,
        current_annual_taxes=350_000,
        county='Los Angeles',
        state='CA'
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate()
    
    # California should reassess at 100%
    assert result['reassessment_ratio'] == 1.00
    expected_new_assessed = 50_000_000 * 1.00
    assert abs(result['new_assessed_value'] - expected_new_assessed) < 1
    print("✓ California 100% reassessment correct")


def test_georgia_low_reassessment():
    """Test Georgia with 40% reassessment ratio."""
    tax_input = PropertyTaxInput(
        purchase_price=10_000_000,
        current_assessed_value=7_000_000,
        current_annual_taxes=100_000,
        county='Fulton',
        state='GA'
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate()
    
    # Georgia should use 40% ratio
    assert result['reassessment_ratio'] == 0.40
    expected_new_assessed = 10_000_000 * 0.40
    assert abs(result['new_assessed_value'] - expected_new_assessed) < 1
    print("✓ Georgia 40% reassessment correct")


def test_unknown_state_default():
    """Test unknown state defaults to 70%."""
    tax_input = PropertyTaxInput(
        purchase_price=20_000_000,
        current_assessed_value=15_000_000,
        current_annual_taxes=200_000,
        county='Unknown',
        state='ZZ'  # Fake state code
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate()
    
    # Should default to 70%
    assert result['reassessment_ratio'] == 0.70
    print("✓ Unknown state defaults to 70%")


def test_tax_projection():
    """Test multi-year tax projection with growth."""
    tax_input = PropertyTaxInput(
        purchase_price=12_000_000,
        current_assessed_value=9_000_000,
        current_annual_taxes=120_000,
        county='Hillsborough',
        state='FL',
        reassessment_ratio=0.70
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate(projection_years=5)
    
    # Should have 5 years of projections
    assert 'year_1' in result['projection']
    assert 'year_5' in result['projection']
    
    # Each year should grow by 3%
    year_1 = result['projection']['year_1']
    year_2 = result['projection']['year_2']
    growth_rate = (year_2 - year_1) / year_1
    assert abs(growth_rate - 0.03) < 0.001  # Should be ~3%
    print("✓ Multi-year tax projection with growth correct")


def test_custom_reassessment_ratio():
    """Test custom reassessment ratio overrides state default."""
    # Florida normally uses 70%, but override with custom 80%
    tax_input = PropertyTaxInput(
        purchase_price=10_000_000,
        current_assessed_value=8_000_000,
        current_annual_taxes=100_000,
        county='Miami-Dade',
        state='FL',
        reassessment_ratio=0.80  # Custom override
    )
    
    calc = PropertyTaxCalculator(tax_input)
    result = calc.calculate()
    
    # Should use custom 80% not FL default 70%
    assert result['reassessment_ratio'] == 0.80
    expected_new_assessed = 10_000_000 * 0.80
    assert abs(result['new_assessed_value'] - expected_new_assessed) < 1
    print("✓ Custom reassessment ratio override correct")


def run_all_tests():
    """Run all tests."""
    print("Running Phase 3 Property Tax Tests...")
    print("=" * 70)
    
    test_florida_property_tax()
    test_texas_property_tax()
    test_california_full_reassessment()
    test_georgia_low_reassessment()
    test_unknown_state_default()
    test_tax_projection()
    test_custom_reassessment_ratio()
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()

