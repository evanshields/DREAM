"""
EXAMPLE 1: Return Hurdles Calculation
======================================

This example demonstrates how to calculate risk-adjusted return hurdles
for different property profiles and market tiers.

"""

from shieldstone_v2_library import (
    MarketTier,
    RenovationScope,
    PropertyProfile,
    ReturnHurdleCalculator
)


def example_1_modern_property():
    """Example: Modern property in secondary market with light renovation."""
    print("=" * 70)
    print("EXAMPLE 1: 2018-Built Nashville Property (Secondary Market)")
    print("=" * 70)
    
    property = PropertyProfile(
        year_built=2018,
        unit_count=250,
        current_occupancy=0.92,
        renovation_scope=RenovationScope.LIGHT,
        renovation_cost_per_unit=8500,
        floating_rate_debt=False,
        market_distressed=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    result = calc.calculate_adjusted_hurdle()
    
    print(f"\nProperty Age: {result['property_age_years']} years")
    print(f"Property Vintage: {result['property_vintage']}")
    print(f"Market Tier: {result['market_tier'].upper()}")
    
    print(f"\nBASE HURDLE: {result['base_hurdle']:.1%}")
    print(f"\nRISK ADJUSTMENTS:")
    for factor, bps in result['adjustments_bps'].items():
        if bps > 0:
            print(f"  • {factor.replace('_', ' ').title()}: +{bps} bps")
    
    print(f"\nTOTAL ADJUSTMENT: +{result['total_adjustment_bps']} bps")
    print(f"ADJUSTED HURDLE: {result['adjusted_hurdle']:.1%}")
    print(f"FINAL IRR HURDLE: {result['final_hurdle']:.1%}")
    print(f"  (Binding Constraint: {result['binding_constraint']})")
    
    print(f"\nOTHER REQUIREMENTS:")
    print(f"  • Stabilized CoC Floor: {result['coc_floor_stabilized']:.1%}")
    print(f"  • Equity Multiple Min: {result['equity_multiple_minimum']:.2f}x")
    print(f"  • Net Investor IRR Min: {result['net_investor_irr_minimum']:.0%}")


def example_2_older_property():
    """Example: Older property with heavy renovation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: 1988-Built Tampa Property (Heavy Renovation)")
    print("=" * 70)
    
    property = PropertyProfile(
        year_built=1988,
        unit_count=180,
        current_occupancy=0.78,
        renovation_scope=RenovationScope.HEAVY,
        renovation_cost_per_unit=22000,
        floating_rate_debt=True,
        market_distressed=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    result = calc.calculate_adjusted_hurdle()
    
    print(f"\nProperty Age: {result['property_age_years']} years")
    print(f"Occupancy: {property.current_occupancy:.0%}")
    print(f"Renovation: {property.renovation_scope.value.upper()}")
    
    print(f"\nBASE HURDLE: {result['base_hurdle']:.1%}")
    print(f"\nRISK ADJUSTMENTS:")
    for factor, bps in result['adjustments_bps'].items():
        if bps > 0:
            print(f"  • {factor.replace('_', ' ').title()}: +{bps} bps")
    
    print(f"\nTOTAL ADJUSTMENT: +{result['total_adjustment_bps']} bps")
    print(f"FINAL IRR HURDLE: {result['final_hurdle']:.1%}")
    print(f"Stabilized CoC Floor: {result['coc_floor_stabilized']:.1%}")


def example_3_evaluate_deal():
    """Example: Evaluate whether a deal meets hurdles."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Deal Evaluation Against Hurdles")
    print("=" * 70)
    
    property = PropertyProfile(
        year_built=1995,
        unit_count=200,
        current_occupancy=0.85,
        renovation_scope=RenovationScope.MODERATE,
        renovation_cost_per_unit=15000,
        floating_rate_debt=False
    )
    
    calc = ReturnHurdleCalculator(MarketTier.SECONDARY, property)
    
    # Projected deal returns
    projected_irr = 0.185       # 18.5%
    projected_coc = 0.075       # 7.5%
    projected_em = 1.75         # 1.75x
    net_investor_irr = 0.16     # 16%
    
    evaluation = calc.evaluate_deal(
        projected_irr, projected_coc, projected_em, net_investor_irr
    )
    
    print(f"\nHURDLES:")
    print(f"  IRR: {evaluation['hurdles']['final_hurdle']:.1%}")
    print(f"  CoC: {evaluation['hurdles']['coc_floor_stabilized']:.1%}")
    print(f"  EM: {evaluation['hurdles']['equity_multiple_minimum']:.2f}x")
    print(f"  Net Investor IRR: {evaluation['hurdles']['net_investor_irr_minimum']:.0%}")
    
    print(f"\nPROJECTED RETURNS:")
    print(f"  IRR: {projected_irr:.1%} ({'✓ PASS' if evaluation['evaluation']['irr_pass'] else '✗ FAIL'})")
    print(f"    Margin: {evaluation['evaluation']['irr_margin']:+.1%}")
    print(f"  CoC: {projected_coc:.1%} ({'✓ PASS' if evaluation['evaluation']['coc_pass'] else '✗ FAIL'})")
    print(f"    Margin: {evaluation['evaluation']['coc_margin']:+.1%}")
    print(f"  EM: {projected_em:.2f}x ({'✓ PASS' if evaluation['evaluation']['em_pass'] else '✗ FAIL'})")
    print(f"    Margin: {evaluation['evaluation']['em_margin']:+.2f}x")
    print(f"  Net IRR: {net_investor_irr:.1%} ({'✓ PASS' if evaluation['evaluation']['net_irr_pass'] else '✗ FAIL'})")
    
    print(f"\n{'='*70}")
    print(f"RECOMMENDATION: {evaluation['recommendation']}")
    print(f"{'='*70}")
    
    if evaluation['failing_metrics']:
        print(f"\n⚠ Failing Metrics: {', '.join(evaluation['failing_metrics'])}")


if __name__ == "__main__":
    example_1_modern_property()
    example_2_older_property()
    example_3_evaluate_deal()

