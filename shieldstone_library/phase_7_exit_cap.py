"""
PHASE 7: EXIT CAP TRIANGULATION
================================

From Shieldstone Technical Manual v2.0 - Section 7.2

Three-method exit cap validation framework.

Golden Rule: Exit cap rate is ALWAYS higher than going-in cap rate.
If your model shows exit cap ≤ going-in cap, you are assuming cap rate
compression—a speculative bet that must be explicitly justified.

Key Features:
- Method 1: Treasury Spread Method
- Method 2: Exit Comp Validation
- Method 3: Entry Cap + Strategy Spread
- Triangulation using most conservative (highest) result

"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class InvestmentStrategy(Enum):
    """Investment strategy classifications."""
    CORE = "core"
    CORE_PLUS = "core_plus"
    VALUE_ADD = "value_add"
    OPPORTUNISTIC = "opportunistic"


@dataclass
class ExitCapInput:
    """Input data for exit cap triangulation."""
    # Property basics
    unit_count: int
    going_in_cap: float
    stabilized_noi: float  # Year of exit
    total_project_cost: float
    
    # Market data
    forward_treasury_rate: float  # At target exit year
    agency_spread: float = 0.0150  # Default 150 bps
    
    # Strategy
    investment_strategy: InvestmentStrategy = InvestmentStrategy.VALUE_ADD
    
    # Comp data (list of $/unit values)
    comp_price_per_unit: List[float] = None


class ExitCapTriangulator:
    """
    Triangulate exit cap rate using three independent methods.
    
    Methods:
    1. Treasury Spread - Forward rate + agency spread + buffer
    2. Exit Comp Validation - Implied $/unit vs market
    3. Entry Cap + Strategy Spread - Going-in + risk premium
    
    Use HIGHEST (most conservative) of three methods.
    """
    
    STRATEGY_SPREADS = {
        InvestmentStrategy.CORE: 0.0035,        # +35 bps (midpoint 25-45)
        InvestmentStrategy.CORE_PLUS: 0.0062,   # +62 bps (midpoint 50-75)
        InvestmentStrategy.VALUE_ADD: 0.0100,   # +100 bps
        InvestmentStrategy.OPPORTUNISTIC: 0.0150  # +150 bps (midpoint 100-200)
    }
    
    NEGATIVE_LEVERAGE_BUFFER = 0.0075  # 75 bps default
    
    def __init__(self, inputs: ExitCapInput):
        self.inputs = inputs
        
    def method_1_treasury_spread(self) -> Dict:
        """
        Method 1: Forward Treasury + Agency Spread + Buffer
        """
        debt_rate = self.inputs.forward_treasury_rate + self.inputs.agency_spread
        exit_cap = debt_rate + self.NEGATIVE_LEVERAGE_BUFFER
        
        return {
            'method': 'Treasury Spread',
            'exit_cap': exit_cap,
            'components': {
                'forward_treasury': self.inputs.forward_treasury_rate,
                'agency_spread': self.inputs.agency_spread,
                'implied_debt_rate': debt_rate,
                'negative_leverage_buffer': self.NEGATIVE_LEVERAGE_BUFFER
            },
            'rationale': f"Forward debt rate of {debt_rate:.2%} + {self.NEGATIVE_LEVERAGE_BUFFER:.2%} buffer for positive leverage"
        }
    
    def method_2_exit_comp(self, test_cap: float = None) -> Dict:
        """
        Method 2: Exit Comp Validation
        
        If test_cap provided, validates that specific cap.
        Otherwise, calculates cap rate implied by average comp $/unit.
        """
        if test_cap is None:
            test_cap = self.inputs.going_in_cap + 0.0100  # Default: entry + 100bps
        
        # Calculate implied exit metrics
        exit_price = self.inputs.stabilized_noi / test_cap
        exit_per_unit = exit_price / self.inputs.unit_count
        
        # Compare to comps
        if self.inputs.comp_price_per_unit:
            avg_comp = sum(self.inputs.comp_price_per_unit) / len(self.inputs.comp_price_per_unit)
            max_comp = max(self.inputs.comp_price_per_unit)
            min_comp = min(self.inputs.comp_price_per_unit)
            premium_to_avg = (exit_per_unit - avg_comp) / avg_comp
            
            # Determine if cap rate is supportable
            if premium_to_avg <= 0.10:
                assessment = 'SUPPORTABLE'
                suggested_cap = test_cap
            elif premium_to_avg <= 0.20:
                assessment = 'AGGRESSIVE'
                # Suggest cap that equals max comp
                suggested_cap = self.inputs.stabilized_noi / (max_comp * self.inputs.unit_count)
            else:
                assessment = 'UNREALISTIC'
                # Suggest cap that equals average comp
                suggested_cap = self.inputs.stabilized_noi / (avg_comp * self.inputs.unit_count)
            
            comp_analysis = {
                'avg_comp_per_unit': avg_comp,
                'max_comp_per_unit': max_comp,
                'min_comp_per_unit': min_comp,
                'subject_per_unit': exit_per_unit,
                'premium_to_avg': premium_to_avg,
                'assessment': assessment
            }
        else:
            suggested_cap = test_cap
            comp_analysis = {'note': 'No comps provided for validation'}
        
        return {
            'method': 'Exit Comp Validation',
            'test_cap': test_cap,
            'exit_cap': suggested_cap,
            'implied_exit_price': exit_price,
            'implied_per_unit': exit_per_unit,
            'comp_analysis': comp_analysis,
            'rationale': f"Exit $/unit of ${exit_per_unit:,.0f} validated against market comps"
        }
    
    def method_3_entry_spread(self) -> Dict:
        """
        Method 3: Entry Cap + Strategy-Appropriate Spread
        """
        spread = self.STRATEGY_SPREADS[self.inputs.investment_strategy]
        exit_cap = self.inputs.going_in_cap + spread
        
        return {
            'method': 'Entry Cap + Strategy Spread',
            'exit_cap': exit_cap,
            'components': {
                'going_in_cap': self.inputs.going_in_cap,
                'strategy': self.inputs.investment_strategy.value,
                'strategy_spread': spread
            },
            'rationale': f"Going-in {self.inputs.going_in_cap:.2%} + {spread:.2%} {self.inputs.investment_strategy.value} spread"
        }
    
    def triangulate(self) -> Dict:
        """
        Execute full triangulation and return recommended exit cap.
        """
        m1 = self.method_1_treasury_spread()
        m2 = self.method_2_exit_comp()
        m3 = self.method_3_entry_spread()
        
        results = [m1, m2, m3]
        caps = [m1['exit_cap'], m2['exit_cap'], m3['exit_cap']]
        
        # Use most conservative (highest)
        recommended_cap = max(caps)
        spread = max(caps) - min(caps)
        
        if spread <= 0.0025:
            confidence = 'HIGH'
            confidence_note = 'All methods within 25 bps - strong consensus'
        elif spread <= 0.0050:
            confidence = 'MODERATE'
            confidence_note = 'Methods within 50 bps - reasonable consensus'
        else:
            confidence = 'LOW'
            confidence_note = f'Methods diverge by {spread:.0%} - investigate before proceeding'
        
        # Calculate YOC relationship
        yoc = self.inputs.stabilized_noi / self.inputs.total_project_cost
        yoc_spread = yoc - recommended_cap
        
        return {
            'method_results': {
                'treasury_spread': m1,
                'exit_comp': m2,
                'entry_spread': m3
            },
            'triangulation': {
                'method_1_cap': m1['exit_cap'],
                'method_2_cap': m2['exit_cap'],
                'method_3_cap': m3['exit_cap'],
                'spread': spread,
                'recommended_exit_cap': recommended_cap,
                'binding_method': 'Treasury Spread' if recommended_cap == m1['exit_cap'] 
                                  else ('Exit Comp' if recommended_cap == m2['exit_cap'] else 'Entry Spread'),
                'confidence': confidence,
                'confidence_note': confidence_note
            },
            'yoc_analysis': {
                'yield_on_cost': yoc,
                'exit_cap': recommended_cap,
                'yoc_spread': yoc_spread,
                'spread_adequate': yoc_spread >= 0.0050,
                'note': 'YOC should exceed exit cap by 50-100 bps for adequate value creation margin'
            }
        }
    
    def sensitivity_analysis(self, cap_range: Tuple[float, float] = None, 
                            step: float = 0.0025) -> List[Dict]:
        """
        Generate sensitivity table across exit cap range.
        """
        if cap_range is None:
            base = self.triangulate()['triangulation']['recommended_exit_cap']
            cap_range = (base - 0.0100, base + 0.0050)
        
        results = []
        current_cap = cap_range[0]
        
        while current_cap <= cap_range[1]:
            exit_price = self.inputs.stabilized_noi / current_cap
            exit_per_unit = exit_price / self.inputs.unit_count
            
            results.append({
                'exit_cap': current_cap,
                'exit_price': exit_price,
                'exit_per_unit': exit_per_unit
            })
            
            current_cap += step
        
        return results

