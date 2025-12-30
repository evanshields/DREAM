"""
PHASE 5: GROUND LEASE FINANCING
================================

From Shieldstone Technical Manual v2.0 - Section 6.6

Capitalized ground lease sizing and returns analysis.

Core Principle: GL rent is an OPERATING EXPENSE (not debt service),
deducted before NOI calculation.

Key Features:
- GL proceeds sizing (3 constraints)
- GL rent schedule with escalation
- Returns comparison (with vs. without GL)

"""

from typing import Dict


class CapitalizedGroundLeaseSizer:
    """
    Size capitalized ground lease and calculate impact on returns.
    
    Workflow:
    1. Calculate maximum GL proceeds (3 constraints)
    2. Model GL rent schedule (10+ years with escalation)
    3. Integrate GL rent into cash flows as operating expense
    4. Calculate returns WITH and WITHOUT GL (comparison)
    5. Sensitivity analyze Treasury rate and GL amount changes
    """
    
    def __init__(self, property_cost: float, stabilized_noi: float, property_value: float):
        """
        Args:
            property_cost: Total project cost (land + construction + soft costs)
            stabilized_noi: Year 3+ stabilized NOI before GL rent deduction
            property_value: Appraised fee simple property value
        """
        self.property_cost = property_cost
        self.stabilized_noi = stabilized_noi
        self.property_value = property_value
    
    def size_gl_proceeds(self, min_coverage_ratio: float = 2.8, ltv_cap: float = 0.40) -> Dict:
        """
        Calculate maximum GL proceeds (3 constraints).
        
        Returns:
            dict: Sizing analysis with all constraints
        """
        # Constraint 1: Coverage ratio
        max_gl_rent = self.stabilized_noi / min_coverage_ratio
        
        # Assume GL yield 5.591% (Option A at current Treasury)
        gl_yield = 0.05591
        max_gl_proceeds_coverage = max_gl_rent / gl_yield
        
        # Constraint 2: 40% of project cost
        max_gl_proceeds_ltc = self.property_cost * ltv_cap
        
        # Constraint 3: 40% LTC on appraisal
        max_gl_proceeds_appraisal = self.property_value * ltv_cap
        
        # Use minimum (most conservative)
        gl_proceeds = min(
            max_gl_proceeds_coverage,
            max_gl_proceeds_ltc,
            max_gl_proceeds_appraisal
        )
        
        return {
            'constraint_coverage': max_gl_proceeds_coverage,
            'constraint_ltc_project': max_gl_proceeds_ltc,
            'constraint_ltc_appraisal': max_gl_proceeds_appraisal,
            'binding_constraint': self._find_binding_constraint(
                max_gl_proceeds_coverage,
                max_gl_proceeds_ltc,
                max_gl_proceeds_appraisal
            ),
            'gl_proceeds': gl_proceeds,
            'gl_proceeds_pct_cost': gl_proceeds / self.property_cost
        }
    
    def _find_binding_constraint(self, c1: float, c2: float, c3: float) -> str:
        """Identify which constraint is most restrictive."""
        values = {'coverage': c1, 'ltc_project': c2, 'ltc_appraisal': c3}
        return min(values, key=values.get)
    
    def calculate_gl_rent_schedule(self, gl_proceeds: float, initial_yield: float, 
                                    years: int = 10, annual_increase: float = 0.02) -> Dict:
        """
        Calculate annual GL rent schedule with escalation.
        
        Args:
            gl_proceeds: Ground lease proceeds (sizing from above)
            initial_yield: GL yield (e.g., 0.05591 for Option A)
            years: Number of years to model
            annual_increase: Annual rent increase (0.02 for 2%)
        
        Returns:
            dict: Year-by-year GL rent schedule
        """
        schedule = {}
        year1_rent = gl_proceeds * initial_yield
        
        for year in range(1, years + 1):
            if year == 1:
                annual_rent = year1_rent
            elif year % 10 == 1 and year > 1:
                # CPI adjustment year (every 10 years)
                cpi_growth = 0.025
                prior_rent = schedule[year - 1]
                annual_rent = prior_rent * max(1 + annual_increase, 1 + cpi_growth)
            else:
                prior_rent = schedule[year - 1]
                annual_rent = prior_rent * (1 + annual_increase)
            
            schedule[year] = annual_rent
        
        return schedule
    
    def compare_returns_with_without_gl(self, gl_proceeds: float, senior_debt: float, 
                                        equity: float, annual_btcf_no_gl: float, 
                                        gl_yield: float) -> Dict:
        """
        Compare returns: with GL vs. without GL.
        
        Args:
            gl_proceeds: GL Proceeds amount
            senior_debt: Senior debt amount
            equity: Equity investment
            annual_btcf_no_gl: Annual BTCF without GL rent (Year 1-5 avg)
            gl_yield: GL annual rent yield
        
        Returns:
            dict: Returns comparison
        """
        # Scenario 1: WITHOUT GL
        btcf_no_gl = annual_btcf_no_gl
        coc_no_gl = btcf_no_gl / equity
        
        # Scenario 2: WITH GL
        annual_gl_rent = gl_proceeds * gl_yield
        btcf_with_gl = annual_btcf_no_gl - annual_gl_rent
        coc_with_gl = btcf_with_gl / equity
        
        # Rough IRR estimate (simplified)
        irr_drag_bps = ((coc_no_gl - coc_with_gl) / coc_no_gl) * 10000 if coc_no_gl > 0 else 0
        
        return {
            'annual_gl_rent': annual_gl_rent,
            'btcf_no_gl': btcf_no_gl,
            'btcf_with_gl': btcf_with_gl,
            'coc_no_gl': coc_no_gl,
            'coc_with_gl': coc_with_gl,
            'coc_impact_bps': (coc_with_gl - coc_no_gl) / coc_no_gl * 10000 if coc_no_gl > 0 else 0,
            'estimated_irr_drag_bps': irr_drag_bps,
            'gl_rent_as_pct_noi': annual_gl_rent / (annual_btcf_no_gl + annual_gl_rent) if (annual_btcf_no_gl + annual_gl_rent) > 0 else 0
        }

