"""
Financing Structure & Loan Sizing

Implements Section 6.3: Loan Sizing & LTV
from the Shieldstone Technical Underwriting Manual.
"""

from typing import Dict
from .constants import (
    LTV_STANDARD, CLOSING_COST_PCT, DSCR_REQUIRED
)


class LoanSizer:
    """
    Size loans using 65% LTV standard on purchase price.
    
    CRITICAL: Loan is based on purchase price, NOT total project cost.
    Equity covers: 35% down + closing costs + 100% of capex.
    """
    
    def __init__(self, purchase_price: float, closing_cost_pct: float = None):
        """
        Parameters:
        -----------
        purchase_price : float
            Purchase price of the property
        closing_cost_pct : float, optional
            Closing cost percentage (defaults to 3%)
        """
        self.purchase_price = purchase_price
        self.closing_cost_pct = closing_cost_pct or CLOSING_COST_PCT
        
    def calculate_loan_and_equity(
        self, 
        total_capex: float, 
        stabilized_noi: float,
        interest_rate: float = 0.0575,
        required_dscr: float = None
    ) -> Dict:
        """
        Calculate loan amount and total equity required.
        
        Parameters:
        -----------
        total_capex : float
            Total capital expenditure budget
        stabilized_noi : float
            Stabilized annual NOI (Year 3+)
        interest_rate : float
            Annual interest rate (default 5.75%)
        required_dscr : float, optional
            Lender DSCR requirement (defaults to 1.25x)
        """
        required_dscr = required_dscr or DSCR_REQUIRED
        
        # LTV-based loan sizing
        ltv_loan_amount = self.purchase_price * LTV_STANDARD
        
        # DSCR-based loan sizing (check constraint)
        # Calculate monthly payment factor for 30yr amortization
        monthly_rate = interest_rate / 12
        n_payments = 360  # 30 years
        
        # Monthly payment per dollar of loan
        monthly_payment_factor = (
            (monthly_rate * (1 + monthly_rate)**n_payments) / 
            ((1 + monthly_rate)**n_payments - 1)
        )
        
        annual_payment_per_dollar = monthly_payment_factor * 12
        
        # Maximum loan based on DSCR
        dscr_loan_amount = stabilized_noi / (required_dscr * annual_payment_per_dollar)
        
        # Take lesser of LTV or DSCR loan
        loan_amount = min(ltv_loan_amount, dscr_loan_amount)
        binding_constraint = 'LTV' if loan_amount == ltv_loan_amount else 'DSCR'
        
        # Calculate equity requirement
        closing_costs = self.purchase_price * self.closing_cost_pct
        down_payment = self.purchase_price - loan_amount
        total_equity = down_payment + closing_costs + total_capex
        
        # Calculate sources and uses
        sources = {
            'loan': loan_amount,
            'equity': total_equity,
            'total': loan_amount + total_equity
        }
        
        uses = {
            'purchase_price': self.purchase_price,
            'closing_costs': closing_costs,
            'capex': total_capex,
            'total': self.purchase_price + closing_costs + total_capex
        }
        
        return {
            'ltv_loan_amount': ltv_loan_amount,
            'dscr_loan_amount': dscr_loan_amount,
            'binding_constraint': binding_constraint,
            'loan_amount': loan_amount,
            'actual_ltv': loan_amount / self.purchase_price,
            'stabilized_dscr': stabilized_noi / (loan_amount * annual_payment_per_dollar),
            'equity_breakdown': {
                'down_payment': down_payment,
                'down_payment_pct': down_payment / self.purchase_price,
                'closing_costs': closing_costs,
                'capex': total_capex,
                'total_equity': total_equity
            },
            'sources': sources,
            'uses': uses,
            'sources_uses_balanced': abs(sources['total'] - uses['total']) < 1
        }

