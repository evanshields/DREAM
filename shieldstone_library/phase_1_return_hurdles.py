"""
PHASE 1: INVESTMENT PHILOSOPHY & RETURN HURDLES
===============================================

From Shieldstone Technical Manual v2.0 - Section 1.1

This module implements risk-adjusted return hurdle calculation for
multifamily value-add acquisitions. It calculates appropriate IRR,
cash-on-cash, and equity multiple targets based on property characteristics,
market tier, and risk factors.

Key Features:
- Market-tier based hurdles (Gateway/Secondary/Tertiary)
- Vintage-tiered CoC floors (6-8% by property age)
- Risk premium adjustments for renovation scope, age, occupancy
- Absolute minimum constraints (14% IRR, 1.5x EM, 15% net investor IRR)

"""

from typing import Dict
from dataclasses import dataclass
from enum import Enum


class MarketTier(Enum):
    """Market tier classifications with corresponding return expectations."""
    GATEWAY = "gateway"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class RenovationScope(Enum):
    """Renovation intensity classifications."""
    LIGHT = "light"          # <$10K/unit, cosmetic
    MODERATE = "moderate"    # $10-15K/unit
    HEAVY = "heavy"          # >$15K/unit or full gut


@dataclass
class PropertyProfile:
    """
    Property characteristics for hurdle calculation.
    
    Attributes:
        year_built: Year property was constructed
        unit_count: Total number of units
        current_occupancy: Current occupancy rate (0.0 to 1.0)
        renovation_scope: Planned renovation intensity
        renovation_cost_per_unit: Total renovation budget per unit
        floating_rate_debt: Whether financing uses floating rate
        market_distressed: Whether market is in distressed condition
    """
    year_built: int
    unit_count: int
    current_occupancy: float  # 0.0 to 1.0
    renovation_scope: RenovationScope
    renovation_cost_per_unit: float
    floating_rate_debt: bool
    market_distressed: bool = False


class ReturnHurdleCalculator:
    """
    Calculate risk-adjusted return hurdles for multifamily acquisitions.
    
    Framework:
    1. Start with market tier base hurdle
    2. Add vintage-tiered renovation premium
    3. Add occupancy, age, financing, and market cycle premiums
    4. Compare to absolute minimums
    5. Return final hurdle with full breakdown
    
    Absolute Minimums (non-negotiable):
    - 14% IRR
    - 1.5x equity multiple (5-year hold)
    - 15% net investor IRR (after fees and promote)
    """
    
    # Market tier base IRR ranges (midpoint used for calculation)
    MARKET_TIERS = {
        MarketTier.GATEWAY: {
            'irr_range': (0.14, 0.16),
            'irr_midpoint': 0.15,
            'coc_year1_range': (0.04, 0.06),
            'equity_multiple_range': (1.6, 1.8)
        },
        MarketTier.SECONDARY: {
            'irr_range': (0.16, 0.19),
            'irr_midpoint': 0.175,
            'coc_year1_range': (0.05, 0.07),
            'equity_multiple_range': (1.7, 2.0)
        },
        MarketTier.TERTIARY: {
            'irr_range': (0.18, 0.22),
            'irr_midpoint': 0.20,
            'coc_year1_range': (0.07, 0.10),
            'equity_multiple_range': (1.9, 2.2)
        }
    }
    
    # Absolute minimums - non-negotiable
    ABSOLUTE_MINIMUMS = {
        'irr': 0.14,
        'equity_multiple_5yr': 1.50,
        'net_investor_irr': 0.15
    }
    
    # Vintage-tiered stabilized CoC floors
    COC_FLOORS_BY_VINTAGE = {
        'post_2020': 0.06,      # 2020 or newer
        '2000_2019': 0.07,      # 2000-2019
        'pre_2000': 0.075       # Pre-2000 (use 0.08 for pre-1980)
    }
    
    # Vintage-tiered heavy renovation premiums
    HEAVY_RENO_PREMIUMS = {
        'post_2000': 0.0150,    # +150 bps
        '1980_1999': 0.0175,    # +175-200 bps (using 175)
        'pre_1980': 0.0250      # +250 bps
    }
    
    def __init__(self, market_tier: MarketTier, property_profile: PropertyProfile):
        """
        Initialize calculator with market and property data.
        
        Args:
            market_tier: Gateway, Secondary, or Tertiary market classification
            property_profile: PropertyProfile dataclass with deal characteristics
        """
        self.market_tier = market_tier
        self.property = property_profile
        self.current_year = 2025
        
    def _get_property_age(self) -> int:
        """Calculate property age in years."""
        return self.current_year - self.property.year_built
    
    def _get_vintage_category(self) -> str:
        """Categorize property by vintage for CoC and renovation premiums."""
        if self.property.year_built >= 2020:
            return 'post_2020'
        elif self.property.year_built >= 2000:
            return '2000_2019'
        elif self.property.year_built >= 1980:
            return '1980_1999'
        else:
            return 'pre_1980'
    
    def _get_coc_floor(self) -> float:
        """Get stabilized CoC floor based on vintage."""
        vintage = self._get_vintage_category()
        if vintage == 'post_2020':
            return self.COC_FLOORS_BY_VINTAGE['post_2020']
        elif vintage == '2000_2019':
            return self.COC_FLOORS_BY_VINTAGE['2000_2019']
        else:  # pre_2000 or pre_1980
            # Use 8% for pre-1980, 7.5% for 1980-1999
            return 0.08 if vintage == 'pre_1980' else self.COC_FLOORS_BY_VINTAGE['pre_2000']
    
    def _calculate_renovation_premium(self) -> float:
        """Calculate renovation risk premium based on scope and vintage."""
        if self.property.renovation_scope != RenovationScope.HEAVY:
            return 0.0
        
        vintage = self._get_vintage_category()
        if vintage in ['post_2020', '2000_2019']:
            return self.HEAVY_RENO_PREMIUMS['post_2000']
        elif vintage == '1980_1999':
            return self.HEAVY_RENO_PREMIUMS['1980_1999']
        else:
            return self.HEAVY_RENO_PREMIUMS['pre_1980']
    
    def _calculate_occupancy_premium(self) -> float:
        """Calculate occupancy risk premium."""
        occ = self.property.current_occupancy
        if occ >= 0.85:
            return 0.0
        elif occ >= 0.75:
            return 0.01  # +100 bps
        else:
            return 0.015  # +150 bps
    
    def _calculate_age_premium(self) -> float:
        """Calculate property age risk premium."""
        age = self._get_property_age()
        if age <= 20:
            return 0.0
        elif age <= 30:
            return 0.005  # +50 bps
        elif age <= 40:
            return 0.01   # +100 bps
        else:
            return 0.015  # +150 bps
    
    def _calculate_financing_premium(self) -> float:
        """Calculate financing structure risk premium."""
        if self.property.floating_rate_debt:
            return 0.01  # +100 bps for floating rate exposure
        return 0.0
    
    def _calculate_market_cycle_premium(self) -> float:
        """Calculate market cycle risk premium."""
        if self.property.market_distressed:
            return 0.0125  # +125 bps average for distressed markets
        return 0.0
    
    def calculate_adjusted_hurdle(self) -> Dict:
        """
        Calculate full risk-adjusted IRR hurdle with breakdown.
        
        Returns:
            dict: Comprehensive hurdle analysis containing:
                - base_hurdle: Market tier starting point
                - adjustments: Dict of each premium applied
                - adjusted_hurdle: Sum of base + adjustments
                - final_hurdle: Max of adjusted and absolute minimum
                - coc_floor: Vintage-appropriate stabilized CoC minimum
                - equity_multiple_minimum: 1.5x absolute floor
                - complete breakdown with basis points
        """
        base = self.MARKET_TIERS[self.market_tier]['irr_midpoint']
        
        adjustments = {
            'renovation_scope': self._calculate_renovation_premium(),
            'occupancy': self._calculate_occupancy_premium(),
            'property_age': self._calculate_age_premium(),
            'financing_structure': self._calculate_financing_premium(),
            'market_cycle': self._calculate_market_cycle_premium()
        }
        
        total_adjustment = sum(adjustments.values())
        adjusted_hurdle = base + total_adjustment
        final_hurdle = max(adjusted_hurdle, self.ABSOLUTE_MINIMUMS['irr'])
        
        return {
            'market_tier': self.market_tier.value,
            'property_vintage': self._get_vintage_category(),
            'property_age_years': self._get_property_age(),
            'base_hurdle': base,
            'adjustments': adjustments,
            'adjustments_bps': {k: int(v * 10000) for k, v in adjustments.items()},
            'total_adjustment': total_adjustment,
            'total_adjustment_bps': int(total_adjustment * 10000),
            'adjusted_hurdle': adjusted_hurdle,
            'absolute_minimum_irr': self.ABSOLUTE_MINIMUMS['irr'],
            'final_hurdle': final_hurdle,
            'binding_constraint': 'adjusted' if adjusted_hurdle >= self.ABSOLUTE_MINIMUMS['irr'] else 'absolute_minimum',
            'coc_floor_stabilized': self._get_coc_floor(),
            'equity_multiple_minimum': self.ABSOLUTE_MINIMUMS['equity_multiple_5yr'],
            'net_investor_irr_minimum': self.ABSOLUTE_MINIMUMS['net_investor_irr']
        }
    
    def evaluate_deal(self, projected_irr: float, projected_coc: float, 
                      projected_em: float, net_investor_irr: float) -> Dict:
        """
        Evaluate whether deal meets hurdles.
        
        Args:
            projected_irr: Deal's projected levered IRR
            projected_coc: Deal's projected stabilized cash-on-cash return
            projected_em: Deal's projected equity multiple
            net_investor_irr: Net IRR to investors after fees/promote
        
        Returns:
            dict: Pass/fail on each metric plus overall recommendation
        """
        hurdles = self.calculate_adjusted_hurdle()
        
        irr_pass = projected_irr >= hurdles['final_hurdle']
        coc_pass = projected_coc >= hurdles['coc_floor_stabilized']
        em_pass = projected_em >= hurdles['equity_multiple_minimum']
        net_irr_pass = net_investor_irr >= hurdles['net_investor_irr_minimum']
        
        all_pass = irr_pass and coc_pass and em_pass and net_irr_pass
        
        return {
            'hurdles': hurdles,
            'projected': {
                'irr': projected_irr,
                'coc_stabilized': projected_coc,
                'equity_multiple': projected_em,
                'net_investor_irr': net_investor_irr
            },
            'evaluation': {
                'irr_pass': irr_pass,
                'irr_margin': projected_irr - hurdles['final_hurdle'],
                'coc_pass': coc_pass,
                'coc_margin': projected_coc - hurdles['coc_floor_stabilized'],
                'em_pass': em_pass,
                'em_margin': projected_em - hurdles['equity_multiple_minimum'],
                'net_irr_pass': net_irr_pass,
                'net_irr_margin': net_investor_irr - hurdles['net_investor_irr_minimum']
            },
            'recommendation': 'PROCEED' if all_pass else 'PASS OR REPRICE',
            'failing_metrics': [
                m for m, p in [
                    ('IRR', irr_pass), 
                    ('CoC', coc_pass), 
                    ('EM', em_pass),
                    ('Net Investor IRR', net_irr_pass)
                ] if not p
            ]
        }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_market_tier_description(tier: MarketTier) -> str:
    """Get human-readable description of market tier."""
    descriptions = {
        MarketTier.GATEWAY: "Top-tier markets (NYC, LA, SF, DC, Boston, Seattle)",
        MarketTier.SECONDARY: "Strong growth markets (Nashville, Austin, Tampa, Charlotte)",
        MarketTier.TERTIARY: "Smaller markets with higher risk/return profiles"
    }
    return descriptions.get(tier, "Unknown market tier")


def get_renovation_scope_description(scope: RenovationScope) -> str:
    """Get human-readable description of renovation scope."""
    descriptions = {
        RenovationScope.LIGHT: "Cosmetic updates (<$10K/unit): Paint, flooring, fixtures",
        RenovationScope.MODERATE: "Moderate renovation ($10-15K/unit): Kitchens, baths, appliances",
        RenovationScope.HEAVY: "Heavy renovation (>$15K/unit): Full gut, structural, major systems"
    }
    return descriptions.get(scope, "Unknown renovation scope")

