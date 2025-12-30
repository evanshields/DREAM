"""
Returns Analysis & IRR Calculation

Implements Section 7.4: IRR Calculation & Analysis
from the Shieldstone Technical Underwriting Manual.
"""

from typing import List, Dict
import numpy as np
from scipy.optimize import newton


class IRRCalculator:
    """
    Calculate levered and unlevered IRR with complete cash flow analysis.
    """
    
    def __init__(self, total_equity: float, hold_period_years: int = 5):
        """
        Parameters:
        -----------
        total_equity : float
            Total equity invested (down payment + closing + capex)
        hold_period_years : int
            Hold period in years (default 5)
        """
        self.total_equity = total_equity
        self.hold_period = hold_period_years
        
    def calculate_levered_irr(
        self, 
        annual_cash_flows: List[float], 
        exit_proceeds: float
    ) -> Dict:
        """
        Calculate levered (equity) IRR.
        
        Parameters:
        -----------
        annual_cash_flows : list
            Annual before-tax cash flow for years 1-N
        exit_proceeds : float
            Net proceeds to equity at sale
        
        Returns:
        --------
        dict : IRR analysis results
        """
        # Build complete cash flow array
        cf_array = [-self.total_equity] + annual_cash_flows + [exit_proceeds]
        
        # Calculate IRR using numpy financial functions
        try:
            # Use numpy's IRR function if available
            irr = np.irr(cf_array)  # type: ignore
        except (AttributeError, ValueError):
            # Fallback to Newton's method
            def npv(rate):
                return sum(cf / (1 + rate)**i for i, cf in enumerate(cf_array))
            
            try:
                irr = newton(npv, 0.15)
            except:
                # If Newton fails, try a simple binary search
                irr = self._binary_search_irr(cf_array)
        
        # Calculate equity multiple
        total_distributions = sum(annual_cash_flows) + exit_proceeds
        equity_multiple = total_distributions / self.total_equity
        
        return {
            'levered_irr': irr,
            'equity_multiple': equity_multiple,
            'total_distributions': total_distributions,
            'cash_flow_array': cf_array,
            'average_annual_return': irr
        }
    
    def _binary_search_irr(self, cf_array: List[float], tolerance: float = 1e-6) -> float:
        """
        Binary search fallback for IRR calculation.
        
        Parameters:
        -----------
        cf_array : list
            Cash flow array
        tolerance : float
            Convergence tolerance
        
        Returns:
        --------
        float : IRR
        """
        def npv(rate):
            return sum(cf / (1 + rate)**i for i, cf in enumerate(cf_array))
        
        # Initial bounds
        low = -0.99  # Can't go below -100%
        high = 10.0  # 1000% upper bound
        
        # Ensure NPV changes sign
        npv_low = npv(low)
        npv_high = npv(high)
        
        if npv_low * npv_high > 0:
            # No sign change, return midpoint
            return (low + high) / 2
        
        # Binary search
        while high - low > tolerance:
            mid = (low + high) / 2
            npv_mid = npv(mid)
            
            if abs(npv_mid) < tolerance:
                return mid
            
            if npv_mid * npv_low < 0:
                high = mid
            else:
                low = mid
                npv_low = npv_mid
        
        return (low + high) / 2

