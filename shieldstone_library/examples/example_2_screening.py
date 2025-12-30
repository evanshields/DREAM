"""
EXAMPLE 2: Deal Screening
==========================

This example demonstrates the merit-based screening framework that
distinguishes between red flags (deal-killers) and risk factors
(requiring hurdle adjustments).

"""

from shieldstone_v2_library import ScreeningInput, DealScreener


def example_1_clean_deal():
    """Example: Clean deal with minimal risk factors."""
    print("=" * 70)
    print("EXAMPLE 1: Clean Deal (2018 build, 93% occupied, Class B)")
    print("=" * 70)
    
    screening = ScreeningInput(
        property_age_years=7,
        current_occupancy=0.93,
        property_class='B',
        deferred_maintenance_per_unit=1500,
        unit_count=200,
        submarket_type='primary'
    )
    
    screener = DealScreener(screening)
    result = screener.screen()
    
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Overall Risk: {result['risk_adjustments']['overall_risk_level'].upper()}")
    print(f"Hurdle Adjustment: +{result['risk_adjustments']['total_hurdle_adjustment_bps']} bps")
    print(f"Contingency Add: +{result['risk_adjustments']['total_contingency_adjustment_pct']}%")
    
    print(f"\nRISK FACTORS:")
    for factor in result['risk_adjustments']['risk_factors']:
        print(f"  • {factor['factor'].replace('_', ' ').title()}: {factor['value']}")
        print(f"    Risk Level: {factor['risk_level']}")
        print(f"    Hurdle Add: +{factor['hurdle_adjustment_bps']} bps")


def example_2_distressed_deal():
    """Example: Distressed property with multiple risk factors."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Distressed Deal (1975 build, 68% occupied, Class C)")
    print("=" * 70)
    
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
    
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Overall Risk: {result['risk_adjustments']['overall_risk_level'].upper()}")
    print(f"Hurdle Adjustment: +{result['risk_adjustments']['total_hurdle_adjustment_bps']} bps")
    print(f"Contingency Add: +{result['risk_adjustments']['total_contingency_adjustment_pct']}%")
    
    print(f"\nRISK FACTORS:")
    for factor in result['risk_adjustments']['risk_factors']:
        if factor['hurdle_adjustment_bps'] > 0 or factor.get('contingency_adjustment_pct', 0) > 0:
            print(f"  • {factor['factor'].replace('_', ' ').title()}: {factor['value']}")
            print(f"    Risk: {factor['risk_level'].upper()}")
            if factor['hurdle_adjustment_bps'] > 0:
                print(f"    Hurdle: +{factor['hurdle_adjustment_bps']} bps")
            if factor.get('contingency_adjustment_pct', 0) > 0:
                print(f"    Contingency: +{factor['contingency_adjustment_pct']}%")
    
    print(f"\nNEXT STEPS:")
    for step in result.get('next_steps', []):
        print(f"  • {step}")


def example_3_red_flag_deal():
    """Example: Deal with red flags (deal-killers)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Red Flag Deal (Environmental Contamination)")
    print("=" * 70)
    
    screening = ScreeningInput(
        property_age_years=35,
        current_occupancy=0.75,
        property_class='B',
        deferred_maintenance_per_unit=5000,
        unit_count=180,
        submarket_type='primary',
        # RED FLAG: Environmental contamination
        environmental_contamination=True
    )
    
    screener = DealScreener(screening)
    result = screener.screen()
    
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Passed Screening: {result['passed_screening']}")
    print(f"Reason: {result['reason']}")
    
    if result['red_flags']:
        print(f"\nRED FLAGS:")
        for flag in result['red_flags']:
            print(f"  • {flag['flag'].replace('_', ' ').title()}")
            print(f"    Category: {flag['category']}")
            print(f"    Issue: {flag['description']}")
            print(f"    Exception: {flag['exception']}")
    
    print(f"\nNEXT STEPS:")
    for step in result.get('next_steps', []):
        print(f"  • {step}")


def example_4_moderate_risk():
    """Example: Moderate risk deal requiring caution."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Moderate Risk (1988 build, 79% occupied, Class B)")
    print("=" * 70)
    
    screening = ScreeningInput(
        property_age_years=37,
        current_occupancy=0.79,
        property_class='B',
        deferred_maintenance_per_unit=4000,
        unit_count=180,
        submarket_type='secondary'
    )
    
    screener = DealScreener(screening)
    result = screener.screen()
    
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Overall Risk: {result['risk_adjustments']['overall_risk_level'].upper()}")
    print(f"Total Hurdle Adjustment: +{result['risk_adjustments']['total_hurdle_adjustment_bps']} bps")
    
    print(f"\nKEY RISKS:")
    risks = sorted(
        result['risk_adjustments']['risk_factors'],
        key=lambda x: x['hurdle_adjustment_bps'],
        reverse=True
    )
    for factor in risks[:3]:  # Top 3 risks
        print(f"  • {factor['factor'].replace('_', ' ').title()}: {factor['value']}")
        print(f"    Adjustment: +{factor['hurdle_adjustment_bps']} bps")


if __name__ == "__main__":
    example_1_clean_deal()
    example_2_distressed_deal()
    example_3_red_flag_deal()
    example_4_moderate_risk()

