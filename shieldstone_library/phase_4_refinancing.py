"""
PHASE 4: REFINANCING STRATEGY & FEASIBILITY
============================================

From Shieldstone Technical Manual v2.0 - Section 6.5

This module implements the 90/90 rule, refinancing timeline analysis,
agency loan sizing, and refinance vs. sale decision framework.

Core Principle: You cannot refinance to agency until you achieve 90/90
(90 consecutive days of 90%+ economic occupancy).

Key Features:
- 90/90 timeline calculation
- Refinance loan sizing (DSCR and LTV constraints)
- Interest rate sensitivity analysis
- Refinance vs. sale decision framework

"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class RenovationStrategy(Enum):
    """Renovation execution strategies."""
    PARTIAL_LIGHT = "partial_light"      # 1/3 of units
    PARTIAL_MODERATE = "partial_moderate"  # 2/3 of units
    FULL = "full"                        # 100% of units


@dataclass
class RefinancePropertyProfile:
    """Property characteristics for refinance analysis."""
    unit_count: int
    acquisition_occupancy: float  # 0.0 to 1.0
    average_rent_current: float
    average_rent_renovated: float
    renovation_cost_per_unit: float
    renovation_strategy: RenovationStrategy
    bridge_loan_amount: float
    bridge_loan_rate: float
    acquisition_date: datetime


@dataclass
class RefinanceAssumptions:
    """Assumptions for refinance modeling."""
    target_agency_rate: float = 0.0575  # 5.75%
    agency_amortization_years: int = 30
    target_dscr: float = 1.25
    target_ltv: float = 0.75
    closing_costs_pct: float = 0.015  # 1.5%
    exit_cap_rate: float = 0.055  # For valuation


class NinetyNinetyAnalyzer:
    """
    Analyze 90/90 achievement and refinance timing.
    
    90/90 = 90 consecutive days of 90%+ economic occupancy
    This is the universal agency lender requirement.
    """
    
    def __init__(self, property_profile: RefinancePropertyProfile):
        self.property = property_profile
        
    def calculate_stabilization_timeline(self, 
                                         renovation_months: int,
                                         lease_up_velocity: int = 10) -> Dict:
        """
        Calculate timeline to achieve 90/90.
        
        Args:
            renovation_months: Months to complete renovation scope
            lease_up_velocity: Units leased per month during stabilization (default 10)
            
        Returns:
            dict: Timeline analysis with key milestones
        """
        # Determine units to renovate based on strategy
        if self.property.renovation_strategy == RenovationStrategy.PARTIAL_LIGHT:
            units_to_renovate = int(self.property.unit_count * 0.33)
        elif self.property.renovation_strategy == RenovationStrategy.PARTIAL_MODERATE:
            units_to_renovate = int(self.property.unit_count * 0.67)
        else:
            units_to_renovate = self.property.unit_count
        
        # Current occupied units
        occupied_at_acquisition = int(self.property.unit_count * self.property.acquisition_occupancy)
        
        # Target 90% economic occupancy
        target_occupied = int(self.property.unit_count * 0.90)
        
        # First units available for lease-up at month 3-4
        first_units_available_month = 3
        
        # Simple model: lease-up begins Month 4
        units_to_add = target_occupied - occupied_at_acquisition + units_to_renovate * 0.3  # 30% turnover
        months_of_lease_up = int(units_to_add / lease_up_velocity) + 1
        
        stabilization_month = first_units_available_month + months_of_lease_up
        
        # 90/90 requires 90 days (3 months) of sustained 90%+
        ninety_ninety_start = stabilization_month
        ninety_ninety_achieved = ninety_ninety_start + 3
        
        # Earliest refinance month
        earliest_refinance = ninety_ninety_achieved + 1
        
        return {
            'renovation_strategy': self.property.renovation_strategy.value,
            'units_to_renovate': units_to_renovate,
            'units_to_renovate_pct': units_to_renovate / self.property.unit_count,
            'renovation_complete_month': renovation_months,
            'stabilization_month': stabilization_month,
            '90_90_start_month': ninety_ninety_start,
            '90_90_achieved_month': ninety_ninety_achieved,
            'earliest_refinance_month': earliest_refinance,
            'recommended_refinance_window': f"Month {earliest_refinance}-{earliest_refinance + 6}",
            'timeline_summary': {
                'acquisition': 'Month 0',
                'first_units_leased': f'Month {first_units_available_month}',
                'renovation_complete': f'Month {renovation_months}',
                'stabilization': f'Month {stabilization_month}',
                '90_90_achieved': f'Month {ninety_ninety_achieved}',
                'target_refinance': f'Month {earliest_refinance + 2}'
            }
        }


class RefinanceSizer:
    """
    Size agency refinance loan and calculate proceeds.
    
    Uses DSCR and LTV constraints to determine maximum loan amount.
    """
    
    def __init__(self, assumptions: RefinanceAssumptions):
        self.assumptions = assumptions
        
    def calculate_debt_constant(self) -> float:
        """Calculate annual debt service constant."""
        monthly_rate = self.assumptions.target_agency_rate / 12
        n_payments = self.assumptions.agency_amortization_years * 12
        
        # Monthly payment factor per dollar of loan
        monthly_factor = (monthly_rate * (1 + monthly_rate)**n_payments) / \
                        ((1 + monthly_rate)**n_payments - 1)
        
        return monthly_factor * 12
    
    def size_refinance_loan(self, 
                           stabilized_noi: float,
                           appraised_value: float,
                           bridge_loan_payoff: float) -> Dict:
        """
        Size refinance loan based on DSCR and LTV constraints.
        
        Args:
            stabilized_noi: Trailing 3-month NOI annualized
            appraised_value: Current appraised value at stabilization
            bridge_loan_payoff: Bridge loan balance + accrued fees to pay off
            
        Returns:
            dict: Refinance sizing with proceeds calculation
        """
        debt_constant = self.calculate_debt_constant()
        
        # DSCR-constrained loan
        max_debt_service = stabilized_noi / self.assumptions.target_dscr
        dscr_loan = max_debt_service / debt_constant
        
        # LTV-constrained loan
        ltv_loan = appraised_value * self.assumptions.target_ltv
        
        # Binding constraint
        loan_amount = min(dscr_loan, ltv_loan)
        binding_constraint = 'DSCR' if loan_amount == dscr_loan else 'LTV'
        
        # Calculate proceeds
        closing_costs = loan_amount * self.assumptions.closing_costs_pct
        net_proceeds = loan_amount - closing_costs
        cash_out = net_proceeds - bridge_loan_payoff
        
        # Actual metrics achieved
        actual_dscr = stabilized_noi / (loan_amount * debt_constant)
        actual_ltv = loan_amount / appraised_value
        
        return {
            'stabilized_noi': stabilized_noi,
            'appraised_value': appraised_value,
            'exit_cap_implied': stabilized_noi / appraised_value,
            'constraints': {
                'dscr_max_loan': dscr_loan,
                'ltv_max_loan': ltv_loan,
                'binding_constraint': binding_constraint
            },
            'loan_amount': loan_amount,
            'actual_dscr': actual_dscr,
            'actual_ltv': actual_ltv,
            'debt_constant': debt_constant,
            'annual_debt_service': loan_amount * debt_constant,
            'proceeds': {
                'gross_loan': loan_amount,
                'closing_costs': closing_costs,
                'net_proceeds': net_proceeds,
                'bridge_payoff': bridge_loan_payoff,
                'cash_out_to_equity': cash_out
            },
            'post_refi_metrics': {
                'cash_flow_after_ds': stabilized_noi - (loan_amount * debt_constant),
                'debt_yield': stabilized_noi / loan_amount
            }
        }
    
    def sensitivity_analysis(self, 
                            stabilized_noi: float,
                            appraised_value: float,
                            bridge_loan_payoff: float,
                            rate_scenarios: List[float] = None) -> List[Dict]:
        """
        Show refinance proceeds across interest rate scenarios.
        
        Args:
            rate_scenarios: Interest rate scenarios to model (default: base +/- 100bps)
        """
        if rate_scenarios is None:
            base_rate = self.assumptions.target_agency_rate
            rate_scenarios = [
                base_rate - 0.01,
                base_rate - 0.005,
                base_rate,
                base_rate + 0.005,
                base_rate + 0.01,
                base_rate + 0.015
            ]
        
        results = []
        for rate in rate_scenarios:
            # Create modified assumptions
            modified = RefinanceAssumptions(
                target_agency_rate=rate,
                agency_amortization_years=self.assumptions.agency_amortization_years,
                target_dscr=self.assumptions.target_dscr,
                target_ltv=self.assumptions.target_ltv,
                closing_costs_pct=self.assumptions.closing_costs_pct
            )
            
            temp_sizer = RefinanceSizer(modified)
            sizing = temp_sizer.size_refinance_loan(
                stabilized_noi, appraised_value, bridge_loan_payoff
            )
            
            results.append({
                'rate': rate,
                'loan_amount': sizing['loan_amount'],
                'cash_out': sizing['proceeds']['cash_out_to_equity'],
                'annual_debt_service': sizing['annual_debt_service'],
                'binding_constraint': sizing['constraints']['binding_constraint']
            })
        
        return results


class RefinanceDecisionFramework:
    """
    Framework for refinance vs. sale decision.
    """
    
    def evaluate_refinance_vs_sale(self,
                                   stabilized_noi: float,
                                   refinance_loan: float,
                                   sale_price: float,
                                   bridge_payoff: float,
                                   remaining_equity: float,
                                   post_refi_coc: float,
                                   hold_period_remaining: int = 36) -> Dict:
        """
        Compare refinance-and-hold vs. sell scenarios.
        
        Args:
            stabilized_noi: Current stabilized NOI
            refinance_loan: Refinance loan amount
            sale_price: Estimated sale price (NOI / exit cap)
            bridge_payoff: Bridge loan payoff amount
            remaining_equity: Unreturned equity after any prior distributions
            post_refi_coc: Projected cash-on-cash after refinance
            hold_period_remaining: Months to hold after refinance (if refinancing)
        """
        # Refinance scenario
        refi_cash_out = refinance_loan * 0.985 - bridge_payoff  # Net of closing
        refi_equity_returned_pct = refi_cash_out / remaining_equity
        annual_cf_post_refi = stabilized_noi * post_refi_coc  # Simplified
        
        # Sale scenario
        sale_costs = sale_price * 0.025  # 2.5% disposition costs
        sale_net_proceeds = sale_price - sale_costs - bridge_payoff
        sale_profit = sale_net_proceeds - remaining_equity
        
        return {
            'refinance_scenario': {
                'cash_out_at_refi': refi_cash_out,
                'equity_returned_pct': refi_equity_returned_pct,
                'remaining_equity_in_deal': remaining_equity - refi_cash_out,
                'projected_annual_cf': annual_cf_post_refi,
                'hold_period_months': hold_period_remaining,
                'strategy': 'Cash out via refi, continue to hold for appreciation'
            },
            'sale_scenario': {
                'gross_sale_price': sale_price,
                'disposition_costs': sale_costs,
                'bridge_payoff': bridge_payoff,
                'net_to_equity': sale_net_proceeds,
                'profit_over_equity': sale_profit,
                'strategy': 'Full exit, redeploy capital'
            },
            'recommendation': self._make_recommendation(
                refi_cash_out, sale_net_proceeds, post_refi_coc
            )
        }
    
    def _make_recommendation(self, refi_cash_out: float, 
                            sale_proceeds: float, 
                            post_refi_coc: float) -> str:
        """Generate recommendation based on comparison."""
        if post_refi_coc >= 0.08:  # 8%+ CoC post-refi
            return "REFINANCE AND HOLD - Strong cash flow supports continued hold"
        elif refi_cash_out < sale_proceeds * 0.5:
            return "CONSIDER SALE - Refi cash out is <50% of sale proceeds"
        else:
            return "EVALUATE FURTHER - Consider market cycle, opportunity cost, LP preferences"

