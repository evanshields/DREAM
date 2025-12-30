"""
Unit Tests for Phase 1: Return Hurdles
=======================================

Tests for ReturnHurdleCalculator and related components.
"""

import sys
sys.path.insert(0, '..')

from shieldstone_v2_library import (
    MarketTier,
    RenovationScope,
    PropertyProfile,
    ReturnHurdleCalculator
)


def test_absolute_minimums():
    """Test that absolute minimums are enforced."""
    # Very low-risk property that would normally have sub-14% hurdle
    property = PropertyProfile(
        year_built=2023,
        unit_count=300,
        current_occupancy=0.95,
        renovation_scope=RenovationScope.LIGHT,
        renovation_cost_per_unit=5000,
        floating_rate_debt=False,
        market_distressed=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.GATEWAY, property)
    result = calc.calculate_adjusted_hurdle()
    
    # Should be bound by absolute minimum of 14%
    assert result['final_hurdle'] >= 0.14
    assert result['equity_multiple_minimum'] == 1.50
    assert result['net_investor_irr_minimum'] == 0.15
    print("✓ Absolute minimums enforced correctly")


def test_renovation_premium():
    """Test heavy renovation premium calculation."""
    # Old property with heavy renovation
    property = PropertyProfile(
        year_built=1975,
        unit_count=150,
        current_occupancy=0.85,
        renovation_scope=RenovationScope.HEAVY,
        renovation_cost_per_unit=25000,
        floating_rate_debt=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    result = calc.calculate_adjusted_hurdle()
    
    # Should have significant renovation premium (250 bps for pre-1980)
    assert result['adjustments']['renovation_scope'] == 0.0250
    assert result['adjustments_bps']['renovation_scope'] == 250
    print("✓ Heavy renovation premium calculated correctly")


def test_occupancy_premium():
    """Test occupancy risk premium."""
    # Low occupancy property
    property_low_occ = PropertyProfile(
        year_built=2015,
        unit_count=200,
        current_occupancy=0.65,
        renovation_scope=RenovationScope.MODERATE,
        renovation_cost_per_unit=12000,
        floating_rate_debt=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property_low_occ)
    result = calc.calculate_adjusted_hurdle()
    
    # Should have 150 bps occupancy premium for <65% occupancy
    assert result['adjustments']['occupancy'] == 0.015
    print("✓ Occupancy premium calculated correctly")


def test_market_tiers():
    """Test that different market tiers have appropriate base hurdles."""
    property = PropertyProfile(
        year_built=2015,
        unit_count=200,
        current_occupancy=0.90,
        renovation_scope=RenovationScope.MODERATE,
        renovation_cost_per_unit=12000,
        floating_rate_debt=False
    )
    
    gateway_calc = ReturnHurdleCalculator(MarketTier.GATEWAY, property)
    secondary_calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    tertiary_calc = ReturnHurdleCalculator(MarketTier.TERTIARY, property)
    
    gateway_result = gateway_calc.calculate_adjusted_hurdle()
    secondary_result = secondary_calc.calculate_adjusted_hurdle()
    tertiary_result = tertiary_calc.calculate_adjusted_hurdle()
    
    # Gateway should have lowest base, tertiary highest
    assert gateway_result['base_hurdle'] < secondary_result['base_hurdle']
    assert secondary_result['base_hurdle'] < tertiary_result['base_hurdle']
    assert gateway_result['base_hurdle'] == 0.15
    assert secondary_result['base_hurdle'] == 0.175
    assert tertiary_result['base_hurdle'] == 0.20
    print("✓ Market tier hurdles correct")


def test_vintage_coc_floors():
    """Test vintage-tiered CoC floors."""
    # Post-2020 property
    property_new = PropertyProfile(
        year_built=2022,
        unit_count=200,
        current_occupancy=0.90,
        renovation_scope=RenovationScope.LIGHT,
        renovation_cost_per_unit=8000,
        floating_rate_debt=False
    )
    
    # Pre-1980 property
    property_old = PropertyProfile(
        year_built=1975,
        unit_count=200,
        current_occupancy=0.90,
        renovation_scope=RenovationScope.MODERATE,
        renovation_cost_per_unit=12000,
        floating_rate_debt=False
    )
    
    calc_new = ReturnHurdleCalculator(MarketTier.SECONDARY, property_new)
    calc_old = ReturnHurdleCalculator(MarketTier.SECONDARY, property_old)
    
    result_new = calc_new.calculate_adjusted_hurdle()
    result_old = calc_old.calculate_adjusted_hurdle()
    
    # New should have 6% floor, old should have 8% floor
    assert result_new['coc_floor_stabilized'] == 0.06
    assert result_old['coc_floor_stabilized'] == 0.08
    print("✓ Vintage-tiered CoC floors correct")


def test_deal_evaluation():
    """Test deal evaluation against hurdles."""
    property = PropertyProfile(
        year_built=2010,
        unit_count=200,
        current_occupancy=0.88,
        renovation_scope=RenovationScope.MODERATE,
        renovation_cost_per_unit=13000,
        floating_rate_debt=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    
    # Test passing deal
    evaluation_pass = calc.evaluate_deal(
        projected_irr=0.19,
        projected_coc=0.08,
        projected_em=1.75,
        net_investor_irr=0.16
    )
    
    assert evaluation_pass['recommendation'] == 'PROCEED'
    assert evaluation_pass['evaluation']['irr_pass'] == True
    assert evaluation_pass['evaluation']['coc_pass'] == True
    assert len(evaluation_pass['failing_metrics']) == 0
    
    # Test failing deal
    evaluation_fail = calc.evaluate_deal(
        projected_irr=0.13,  # Below 14% absolute minimum
        projected_coc=0.05,
        projected_em=1.35,
        net_investor_irr=0.11
    )
    
    assert evaluation_fail['recommendation'] == 'PASS OR REPRICE'
    assert evaluation_fail['evaluation']['irr_pass'] == False
    assert len(evaluation_fail['failing_metrics']) > 0
    print("✓ Deal evaluation logic correct")


def run_all_tests():
    """Run all tests."""
    print("Running Phase 1 Return Hurdles Tests...")
    print("=" * 70)
    
    test_absolute_minimums()
    test_renovation_premium()
    test_occupancy_premium()
    test_market_tiers()
    test_vintage_coc_floors()
    test_deal_evaluation()
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()

