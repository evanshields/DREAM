"""
Return Hurdle Calculator

Implements Section 1.1: Investment Philosophy & Return Hurdles
from the Shieldstone Technical Underwriting Manual.
"""

from typing import Dict
from .constants import MARKET_TIERS, RISK_ADJUSTMENTS, MIN_IRR


class ReturnHurdleCalculator:
    """
    Calculate risk-adjusted return hurdles based on market tier and execution risk.
    
    Core Philosophy:
    - Market tier establishes base hurdle
    - Execution risk adds adjustments
    - Absolute minimums are never violated
    """
    
    def __init__(self, market_tier: str, property_characteristics: Dict):
        """
        Initialize calculator.
        
        Parameters:
        -----------
        market_tier : str
            'gateway', 'secondary', or 'tertiary'
        property_characteristics : dict
            - heavy_renovation: bool
            - occupancy: float (0-1)
            - property_age: int
            - market_downturn: bool
            - floating_rate_debt: bool
        """
        if market_tier.lower() not in MARKET_TIERS:
            raise ValueError(f"Invalid market tier: {market_tier}")
        
        self.tier = market_tier.lower()
        self.characteristics = property_characteristics
        
    def calculate_adjusted_hurdle(self) -> Dict:
        """
        Calculate risk-adjusted IRR hurdle with full breakdown.
        
        Returns:
        --------
        dict : Complete hurdle analysis with adjustments
        """
        # Start with base hurdle (midpoint of range)
        irr_range = MARKET_TIERS[self.tier]['irr_range']
        base_hurdle = sum(irr_range) / 2
        
        # Calculate risk adjustments
        adjustments = {}
        total_adjustment = 0
        
        # Heavy construction risk
        if self.characteristics.get('heavy_renovation', False):
            adj = RISK_ADJUSTMENTS['heavy_construction']
            adjustments['heavy_construction'] = adj
            total_adjustment += adj
        
        # Occupancy risk
        occupancy = self.characteristics.get('occupancy', 1.0)
        if occupancy < 0.85:
            adj = RISK_ADJUSTMENTS['low_occupancy']
            adjustments['low_occupancy'] = adj
            total_adjustment += adj
        
        # Property age risk
        age = self.characteristics.get('property_age', 0)
        if age > 30:
            adj = RISK_ADJUSTMENTS['property_age_30plus']
            adjustments['property_age_30plus'] = adj
            total_adjustment += adj
        
        # Market cycle risk
        if self.characteristics.get('market_downturn', False):
            adj = RISK_ADJUSTMENTS['market_downturn']
            adjustments['market_downturn'] = adj
            total_adjustment += adj
        
        # Financing risk
        if self.characteristics.get('floating_rate_debt', False):
            adj = RISK_ADJUSTMENTS['floating_rate_debt']
            adjustments['floating_rate_debt'] = adj
            total_adjustment += adj
        
        # Calculate adjusted hurdle
        adjusted_hurdle = base_hurdle + total_adjustment
        
        # Ensure we never go below absolute minimums
        final_hurdle = max(adjusted_hurdle, MIN_IRR)
        
        return {
            'market_tier': self.tier,
            'base_hurdle': base_hurdle,
            'risk_adjustments': adjustments,
            'total_adjustment': total_adjustment,
            'total_adjustment_bps': int(total_adjustment * 10000),
            'adjusted_hurdle': adjusted_hurdle,
            'final_hurdle': final_hurdle,
            'absolute_minimum': MIN_IRR,
            'hurdle_used': 'adjusted' if adjusted_hurdle >= MIN_IRR else 'absolute_minimum'
        }
    
    def get_all_hurdles(self) -> Dict:
        """Get all return hurdles for the market tier."""
        irr_hurdle = self.calculate_adjusted_hurdle()
        tier_hurdles = MARKET_TIERS[self.tier]
        
        return {
            'irr_hurdle': irr_hurdle['final_hurdle'],
            'irr_adjustment_bps': irr_hurdle['total_adjustment_bps'],
            'coc_year1_range': tier_hurdles['coc_year1'],
            'coc_stabilized_range': tier_hurdles['coc_stabilized'],
            'equity_multiple_5yr_range': tier_hurdles['equity_multiple_5yr'],
            'absolute_minimums': {
                'irr': MIN_IRR,
                'coc_stabilized': 0.06,
                'equity_multiple_5yr': 1.4
            }
        }

