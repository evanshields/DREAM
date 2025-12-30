"""
Unit Tests for Phase 2: Deal Screening
=======================================

Tests for DealScreener and related components.
"""

import sys
sys.path.insert(0, '..')

from shieldstone_v2_library import (
    ScreeningInput,
    DealScreener,
    RedFlagCategory,
    RiskLevel
)


def test_clean_deal_screening():
    """Test screening of clean deal with minimal risk."""
    screening = ScreeningInput(
        property_age_years=10,
        current_occupancy=0.93,
        property_class='B',
        deferred_maintenance_per_unit=1500,
        unit_count=200,
        submarket_type='primary'
    )
    
    screener = DealScreener(screening)
    result = screener.screen()
    
    assert result['passed_screening'] == True
    assert result['recommendation'] == 'PROCEED'
    assert result['risk_adjustments']['total_hurdle_adjustment_bps'] < 100
    print("✓ Clean deal screening correct")


def test_distressed_deal_screening():
    """Test screening of distressed deal with multiple risk factors."""
    screening = ScreeningInput(
        property_age_years=50,
        current_occupancy=0.68,
        property_class='C',
        deferred_maintenance_per_unit=8500,
        unit_count=150,
        submarket_type='tertiary'
    )
    
    screener = DealScreener(screening)
    result = screener.screen()
    
    # Should pass screening but with significant adjustments
    assert result['passed_screening'] == True
    assert result['risk_adjustments']['total_hurdle_adjustment_bps'] > 300
    assert result['risk_adjustments']['overall_risk_level'] in ['elevated', 'high', 'severe']
    print("✓ Distressed deal risk adjustments correct")


def test_red_flag_screening():
    """Test that red flags fail screening."""
    screening = ScreeningInput(
        property_age_years=30,
        current_occupancy=0.85,
        property_class='B',
        deferred_maintenance_per_unit=5000,
        unit_count=180,
        submarket_type='primary',
        environmental_contamination=True  # RED FLAG
    )
    
    screener = DealScreener(screening)
    result = screener.screen()
    
    assert result['passed_screening'] == False
    assert result['recommendation'] == 'PASS'
    assert len(result['red_flags']) > 0
    print("✓ Red flag screening correct")


def test_age_adjustment_tiers():
    """Test that property age adjustments are correctly tiered."""
    # Test each age tier
    age_tests = [
        (15, 0, RiskLevel.LOW),
        (25, 50, RiskLevel.MODERATE),
        (35, 100, RiskLevel.ELEVATED),
        (45, 150, RiskLevel.HIGH),
        (55, 200, RiskLevel.SEVERE)
    ]
    
    for age, expected_bps, expected_level in age_tests:
        screening = ScreeningInput(
            property_age_years=age,
            current_occupancy=0.90,
            property_class='B',
            deferred_maintenance_per_unit=1000,
            unit_count=200,
            submarket_type='primary'
        )
        
        screener = DealScreener(screening)
        result = screener.screen()
        
        age_factor = next(
            f for f in result['risk_adjustments']['risk_factors']
            if f['factor'] == 'property_age'
        )
        
        assert age_factor['hurdle_adjustment_bps'] == expected_bps
        assert age_factor['risk_level'] == expected_level.value
    
    print("✓ Age adjustment tiers correct")


def test_occupancy_adjustment_tiers():
    """Test occupancy risk adjustments."""
    occ_tests = [
        (0.95, 0, RiskLevel.LOW),
        (0.87, 50, RiskLevel.MODERATE),
        (0.78, 100, RiskLevel.ELEVATED),
        (0.68, 150, RiskLevel.HIGH),
        (0.58, 200, RiskLevel.SEVERE)
    ]
    
    for occ, expected_bps, expected_level in occ_tests:
        screening = ScreeningInput(
            property_age_years=15,
            current_occupancy=occ,
            property_class='B',
            deferred_maintenance_per_unit=1000,
            unit_count=200,
            submarket_type='primary'
        )
        
        screener = DealScreener(screening)
        result = screener.screen()
        
        occ_factor = next(
            f for f in result['risk_adjustments']['risk_factors']
            if f['factor'] == 'occupancy'
        )
        
        assert occ_factor['hurdle_adjustment_bps'] == expected_bps
        assert occ_factor['risk_level'] == expected_level.value
    
    print("✓ Occupancy adjustment tiers correct")


def test_property_class_adjustments():
    """Test property class adjustments."""
    class_tests = [
        ('A', 0, RiskLevel.LOW),
        ('B', 0, RiskLevel.LOW),
        ('C', 50, RiskLevel.MODERATE),
        ('D', 100, RiskLevel.ELEVATED)
    ]
    
    for prop_class, expected_bps, expected_level in class_tests:
        screening = ScreeningInput(
            property_age_years=15,
            current_occupancy=0.90,
            property_class=prop_class,
            deferred_maintenance_per_unit=1000,
            unit_count=200,
            submarket_type='primary'
        )
        
        screener = DealScreener(screening)
        result = screener.screen()
        
        class_factor = next(
            f for f in result['risk_adjustments']['risk_factors']
            if f['factor'] == 'property_class'
        )
        
        assert class_factor['hurdle_adjustment_bps'] == expected_bps
        assert class_factor['risk_level'] == expected_level.value
    
    print("✓ Property class adjustments correct")


def test_recommendation_logic():
    """Test recommendation thresholds."""
    # PROCEED: <200 bps
    screening_proceed = ScreeningInput(
        property_age_years=15,
        current_occupancy=0.90,
        property_class='B',
        deferred_maintenance_per_unit=1500,
        unit_count=200,
        submarket_type='primary'
    )
    
    screener = DealScreener(screening_proceed)
    result = screener.screen()
    assert result['recommendation'] == 'PROCEED'
    
    # PROCEED_WITH_CAUTION: 200-400 bps
    screening_caution = ScreeningInput(
        property_age_years=35,
        current_occupancy=0.80,
        property_class='C',
        deferred_maintenance_per_unit=3000,
        unit_count=200,
        submarket_type='secondary'
    )
    
    screener = DealScreener(screening_caution)
    result = screener.screen()
    assert result['recommendation'] == 'PROCEED_WITH_CAUTION'
    
    print("✓ Recommendation logic correct")


def run_all_tests():
    """Run all tests."""
    print("Running Phase 2 Deal Screening Tests...")
    print("=" * 70)
    
    test_clean_deal_screening()
    test_distressed_deal_screening()
    test_red_flag_screening()
    test_age_adjustment_tiers()
    test_occupancy_adjustment_tiers()
    test_property_class_adjustments()
    test_recommendation_logic()
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()

