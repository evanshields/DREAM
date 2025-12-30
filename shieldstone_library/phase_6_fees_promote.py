"""
PHASE 6: DEAL FEES & PROMOTE STRUCTURES
========================================

From Shieldstone Technical Manual v2.0 - Section 6.7

Complete fee and promote (carried interest) modeling for value-add deals.

Core Principle: All fees disclosed upfront. Asset management fee ≠
property management fee (both are appropriate).

Key Features:
- Deal fee calculation (acquisition, AM, construction, disposition, refi)
- Promote waterfall (8% pref, 70/30 to 15% IRR, 50/50 above)
- Net investor return calculation (after fees and promote)

"""

from typing import Dict, List
from dataclasses import dataclass
import numpy as np


@dataclass
class DealFeeAssumptions:
    """Standard fee assumptions for value-add deals."""
    # Acquisition
    acquisition_fee_pct_small: float = 0.01  # <$50MM
    acquisition_fee_pct_large: float = 0.005  # ≥$50MM
    acquisition_fee_threshold: float = 50_000_000
    
    # Asset Management
    asset_mgmt_fee_pct: float = 0.0075  # 0.75% of EGI
    
    # Construction
    construction_mgmt_fee_pct: float = 0.04  # 4% of hard costs
    
    # Disposition
    disposition_fee_pct: float = 0.0025  # 0.25%
    
    # Refinance
    refinance_fee_pct: float = 0.0025  # 0.25%


@dataclass
class PromoteStructure:
    """Waterfall promote structure."""
    preferred_return: float = 0.08  # 8% pref
    tier_1_lp_share: float = 0.70  # 70/30 split
    tier_1_irr_hurdle: float = 0.15  # Until 15% IRR
    tier_2_lp_share: float = 0.50  # 50/50 above hurdle
    gp_coinvest_pct: float = 0.10  # GP invests 10% of equity


class DealFeeCalculator:
    """
    Calculate all deal fees and their impact on returns.
    """
    
    def __init__(self, fee_assumptions: DealFeeAssumptions = None):
        self.fees = fee_assumptions or DealFeeAssumptions()
    
    def calculate_acquisition_fee(self, purchase_price: float) -> Dict:
        """Calculate acquisition fee based on deal size."""
        if purchase_price < self.fees.acquisition_fee_threshold:
            rate = self.fees.acquisition_fee_pct_small
            tier = "small_deal"
        else:
            rate = self.fees.acquisition_fee_pct_large
            tier = "large_deal"
        
        fee = purchase_price * rate
        
        return {
            'purchase_price': purchase_price,
            'fee_rate': rate,
            'tier': tier,
            'acquisition_fee': fee
        }
    
    def calculate_asset_management_fees(self, 
                                        egi_schedule: List[float],
                                        hold_years: int = 5) -> Dict:
        """
        Calculate asset management fees over hold period.
        
        Args:
            egi_schedule: Projected EGI for each year of hold
        """
        annual_fees = []
        for year, egi in enumerate(egi_schedule, 1):
            fee = egi * self.fees.asset_mgmt_fee_pct
            annual_fees.append({
                'year': year,
                'egi': egi,
                'asset_mgmt_fee': fee
            })
        
        total_fees = sum(f['asset_mgmt_fee'] for f in annual_fees)
        total_egi = sum(egi_schedule)
        
        return {
            'fee_rate': self.fees.asset_mgmt_fee_pct,
            'annual_fees': annual_fees,
            'total_fees': total_fees,
            'effective_rate': total_fees / total_egi if total_egi > 0 else 0
        }
    
    def calculate_construction_management_fee(self, hard_costs: float) -> Dict:
        """Calculate construction management fee."""
        fee = hard_costs * self.fees.construction_mgmt_fee_pct
        
        return {
            'hard_costs': hard_costs,
            'fee_rate': self.fees.construction_mgmt_fee_pct,
            'construction_mgmt_fee': fee
        }
    
    def calculate_disposition_fee(self, sale_price: float) -> Dict:
        """Calculate disposition fee."""
        fee = sale_price * self.fees.disposition_fee_pct
        
        return {
            'sale_price': sale_price,
            'fee_rate': self.fees.disposition_fee_pct,
            'disposition_fee': fee
        }
    
    def calculate_refinance_fee(self, loan_proceeds: float) -> Dict:
        """Calculate refinance fee."""
        fee = loan_proceeds * self.fees.refinance_fee_pct
        
        return {
            'loan_proceeds': loan_proceeds,
            'fee_rate': self.fees.refinance_fee_pct,
            'refinance_fee': fee
        }
    
    def calculate_total_fee_burden(self,
                                   purchase_price: float,
                                   hard_costs: float,
                                   egi_schedule: List[float],
                                   sale_price: float,
                                   total_equity: float) -> Dict:
        """
        Calculate complete fee burden over hold period.
        """
        acq_fee = self.calculate_acquisition_fee(purchase_price)
        const_fee = self.calculate_construction_management_fee(hard_costs)
        am_fees = self.calculate_asset_management_fees(egi_schedule)
        disp_fee = self.calculate_disposition_fee(sale_price)
        
        total_fees = (
            acq_fee['acquisition_fee'] +
            const_fee['construction_mgmt_fee'] +
            am_fees['total_fees'] +
            disp_fee['disposition_fee']
        )
        
        return {
            'acquisition_fee': acq_fee,
            'construction_mgmt_fee': const_fee,
            'asset_mgmt_fees': am_fees,
            'disposition_fee': disp_fee,
            'total_fees': total_fees,
            'fees_as_pct_of_equity': total_fees / total_equity if total_equity > 0 else 0,
            'summary': {
                'upfront_fees': acq_fee['acquisition_fee'] + const_fee['construction_mgmt_fee'],
                'annual_fees': am_fees['total_fees'],
                'exit_fees': disp_fee['disposition_fee'],
                'total': total_fees
            }
        }


class PromoteCalculator:
    """
    Calculate promote/carried interest distribution.
    """
    
    def __init__(self, promote_structure: PromoteStructure = None):
        self.promote = promote_structure or PromoteStructure()
    
    def calculate_waterfall(self,
                           total_equity: float,
                           total_distributions: float,
                           hold_years: int,
                           gp_coinvest_amount: float = None) -> Dict:
        """
        Calculate waterfall distribution between LP and GP.
        
        Args:
            total_equity: Total equity invested
            total_distributions: Total distributions at exit (including return of capital)
            hold_years: Investment hold period
            gp_coinvest_amount: GP co-investment (if None, calculated from structure)
        """
        # Calculate LP/GP split of invested equity
        if gp_coinvest_amount is None:
            gp_equity = total_equity * self.promote.gp_coinvest_pct
            lp_equity = total_equity - gp_equity
        else:
            gp_equity = gp_coinvest_amount
            lp_equity = total_equity - gp_equity
        
        # Calculate profit
        profit = total_distributions - total_equity
        
        # Simple IRR approximation for hurdle testing
        simple_irr = (total_distributions / total_equity) ** (1/hold_years) - 1 if total_equity > 0 and hold_years > 0 else 0
        
        # Initialize distributions
        lp_distributions = 0.0
        gp_distributions = 0.0
        
        # Step 1: Return of Capital
        lp_distributions += lp_equity
        gp_distributions += gp_equity
        remaining = profit
        
        # Step 2: Preferred Return to LPs
        accrued_pref = lp_equity * self.promote.preferred_return * hold_years
        pref_paid = min(remaining, accrued_pref)
        lp_distributions += pref_paid
        remaining -= pref_paid
        
        if remaining <= 0:
            return self._format_results(
                lp_equity, gp_equity, lp_distributions, gp_distributions,
                total_distributions, simple_irr
            )
        
        # Step 3: First Promote Tier (until hurdle IRR)
        tier_1_profit = remaining * 0.6  # Assume 60% of remaining in tier 1
        tier_1_to_lp = tier_1_profit * self.promote.tier_1_lp_share
        tier_1_to_gp = tier_1_profit * (1 - self.promote.tier_1_lp_share)
        lp_distributions += tier_1_to_lp
        gp_distributions += tier_1_to_gp
        remaining -= tier_1_profit
        
        # Step 4: Second Promote Tier (above hurdle)
        tier_2_to_lp = remaining * self.promote.tier_2_lp_share
        tier_2_to_gp = remaining * (1 - self.promote.tier_2_lp_share)
        lp_distributions += tier_2_to_lp
        gp_distributions += tier_2_to_gp
        
        return self._format_results(
            lp_equity, gp_equity, lp_distributions, gp_distributions,
            total_distributions, simple_irr
        )
    
    def _format_results(self, lp_equity: float, gp_equity: float, lp_dist: float, 
                       gp_dist: float, total_dist: float, irr: float) -> Dict:
        """Format waterfall results."""
        return {
            'equity_split': {
                'lp_equity': lp_equity,
                'gp_equity': gp_equity,
                'total_equity': lp_equity + gp_equity
            },
            'distributions': {
                'to_lp': lp_dist,
                'to_gp': gp_dist,
                'total': total_dist,
                'verify_total': lp_dist + gp_dist
            },
            'multiples': {
                'lp_multiple': lp_dist / lp_equity if lp_equity > 0 else 0,
                'gp_multiple': gp_dist / gp_equity if gp_equity > 0 else 0,
                'blended_multiple': total_dist / (lp_equity + gp_equity) if (lp_equity + gp_equity) > 0 else 0
            },
            'irr_estimate': irr,
            'promote_structure': {
                'pref_return': self.promote.preferred_return,
                'tier_1_split': f"{int(self.promote.tier_1_lp_share*100)}/{int((1-self.promote.tier_1_lp_share)*100)}",
                'tier_1_hurdle': self.promote.tier_1_irr_hurdle,
                'tier_2_split': f"{int(self.promote.tier_2_lp_share*100)}/{int((1-self.promote.tier_2_lp_share)*100)}"
            }
        }


class NetReturnCalculator:
    """
    Calculate net investor returns after all fees and promote.
    """
    
    def __init__(self):
        self.fee_calc = DealFeeCalculator()
        self.promote_calc = PromoteCalculator()
    
    def calculate_gross_to_net(self,
                               gross_irr: float,
                               purchase_price: float,
                               hard_costs: float,
                               egi_schedule: List[float],
                               sale_price: float,
                               total_equity: float,
                               total_distributions: float,
                               hold_years: int) -> Dict:
        """
        Calculate net investor returns from gross returns.
        
        Args:
            gross_irr: Gross asset-level or equity-level IRR
            (other params as defined above)
        """
        # Calculate fee burden
        fees = self.fee_calc.calculate_total_fee_burden(
            purchase_price, hard_costs, egi_schedule, sale_price, total_equity
        )
        
        # Calculate promote impact
        waterfall = self.promote_calc.calculate_waterfall(
            total_equity, total_distributions, hold_years
        )
        
        # Calculate LP net return
        lp_equity = waterfall['equity_split']['lp_equity']
        lp_distributions = waterfall['distributions']['to_lp']
        lp_multiple = waterfall['multiples']['lp_multiple']
        
        # Simplified LP IRR (proper calculation requires cash flow timing)
        lp_irr_estimate = (lp_multiple ** (1/hold_years)) - 1 if hold_years > 0 else 0
        
        # Fee drag calculation
        fee_drag = fees['total_fees'] / total_distributions if total_distributions > 0 else 0
        
        return {
            'gross_irr': gross_irr,
            'fee_burden': fees['summary'],
            'fee_drag_pct': fee_drag,
            'waterfall': waterfall,
            'net_investor_metrics': {
                'lp_equity': lp_equity,
                'lp_distributions': lp_distributions,
                'lp_multiple': lp_multiple,
                'lp_irr_estimate': lp_irr_estimate,
                'meets_15pct_threshold': lp_irr_estimate >= 0.15
            }
        }

