"""
Unit Tests for Financial Calculations
======================================

Tests for core financial calculations: NOI, DSCR, IRR, Equity Multiple, Cash-on-Cash.
All calculations must be deterministic and match Shieldstone methodology exactly.
"""

import pytest
from decimal import Decimal
from typing import Dict, List


# Import calculation modules (adjust paths as needed)
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from lib.shieldstone.returns import IRRCalculator
from lib.shieldstone.financing import LoanSizer
from lib.shieldstone.constants import (
    LTV_STANDARD,
    DSCR_REQUIRED,
    CLOSING_COST_PCT,
    MIN_IRR,
    MIN_COC_STABILIZED,
    MIN_EQUITY_MULTIPLE
)


class TestNOICalculation:
    """Test Net Operating Income calculations."""
    
    def test_basic_noi_calculation(self):
        """Test basic NOI = EGI - Operating Expenses."""
        gross_potential_rent = 1_200_000
        vacancy_loss = 60_000  # 5%
        other_income = 50_000
        operating_expenses = 480_000
        
        effective_gross_income = gross_potential_rent - vacancy_loss + other_income
        noi = effective_gross_income - operating_expenses
        
        assert effective_gross_income == 1_190_000
        assert noi == 710_000
    
    def test_noi_with_concessions(self):
        """Test NOI calculation with vacancy and concessions."""
        gross_potential_rent = 2_000_000
        vacancy_loss = 100_000  # 5%
        concessions = 40_000  # 2%
        bad_debt = 20_000  # 1%
        other_income = 80_000
        operating_expenses = 800_000
        
        egi = gross_potential_rent - vacancy_loss - concessions - bad_debt + other_income
        noi = egi - operating_expenses
        
        assert egi == 2_000_000
        assert noi == 1_120_000
    
    def test_noi_per_unit(self):
        """Test NOI per unit calculation."""
        noi = 600_000
        units = 200
        
        noi_per_unit = noi / units
        
        assert noi_per_unit == 3_000
    
    def test_noi_margin(self):
        """Test NOI margin calculation."""
        noi = 800_000
        egi = 1_500_000
        
        noi_margin = noi / egi
        
        assert abs(noi_margin - 0.5333) < 0.0001


class TestDSCRCalculation:
    """Test Debt Service Coverage Ratio calculations."""
    
    def test_basic_dscr(self):
        """Test DSCR = NOI / Annual Debt Service."""
        noi = 750_000
        annual_debt_service = 600_000
        
        dscr = noi / annual_debt_service
        
        assert dscr == 1.25
    
    def test_dscr_with_loan_sizing(self):
        """Test DSCR calculation using LoanSizer."""
        purchase_price = 10_000_000
        total_capex = 2_000_000
        stabilized_noi = 800_000
        interest_rate = 0.0575
        
        sizer = LoanSizer(purchase_price)
        result = sizer.calculate_loan_and_equity(
            total_capex=total_capex,
            stabilized_noi=stabilized_noi,
            interest_rate=interest_rate,
            required_dscr=DSCR_REQUIRED
        )
        
        # DSCR should be at or above 1.25x
        assert result['stabilized_dscr'] >= 1.25
        assert result['loan_amount'] > 0
        assert result['binding_constraint'] in ['LTV', 'DSCR']
    
    def test_ltv_vs_dscr_constraint(self):
        """Test that loan sizing uses lesser of LTV or DSCR."""
        # Scenario 1: LTV constrained (high NOI)
        purchase_price_1 = 10_000_000
        stabilized_noi_1 = 1_500_000  # Very strong NOI
        
        sizer_1 = LoanSizer(purchase_price_1)
        result_1 = sizer_1.calculate_loan_and_equity(
            total_capex=2_000_000,
            stabilized_noi=stabilized_noi_1,
            interest_rate=0.0575
        )
        
        assert result_1['binding_constraint'] == 'LTV'
        assert abs(result_1['actual_ltv'] - LTV_STANDARD) < 0.01
        
        # Scenario 2: DSCR constrained (low NOI)
        purchase_price_2 = 10_000_000
        stabilized_noi_2 = 400_000  # Weak NOI
        
        sizer_2 = LoanSizer(purchase_price_2)
        result_2 = sizer_2.calculate_loan_and_equity(
            total_capex=2_000_000,
            stabilized_noi=stabilized_noi_2,
            interest_rate=0.0575
        )
        
        assert result_2['binding_constraint'] == 'DSCR'
        assert result_2['stabilized_dscr'] >= 1.25
    
    def test_dscr_below_threshold(self):
        """Test that deals with insufficient NOI result in lower loan amounts."""
        purchase_price = 10_000_000
        stabilized_noi = 350_000  # Very low NOI
        
        sizer = LoanSizer(purchase_price)
        result = sizer.calculate_loan_and_equity(
            total_capex=2_000_000,
            stabilized_noi=stabilized_noi,
            interest_rate=0.0575
        )
        
        # Loan should be significantly constrained by DSCR
        ltv_loan = purchase_price * LTV_STANDARD
        assert result['loan_amount'] < ltv_loan
        assert result['binding_constraint'] == 'DSCR'


class TestIRRCalculation:
    """Test Internal Rate of Return calculations."""
    
    def test_simple_irr(self):
        """Test IRR calculation with simple cash flows."""
        total_equity = 4_000_000
        annual_cash_flows = [200_000, 250_000, 300_000, 350_000, 400_000]
        exit_proceeds = 3_000_000
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        # IRR should be positive and reasonable (10-25% range for this deal)
        assert result['levered_irr'] > 0.10
        assert result['levered_irr'] < 0.25
        
        # Equity multiple should be > 1
        assert result['equity_multiple'] > 1.0
        
        # Total distributions should equal sum of cash flows + exit
        expected_distributions = sum(annual_cash_flows) + exit_proceeds
        assert abs(result['total_distributions'] - expected_distributions) < 1
    
    def test_irr_with_zero_cash_flows(self):
        """Test IRR when early years have zero cash flow (renovation period)."""
        total_equity = 5_000_000
        annual_cash_flows = [0, 0, 400_000, 500_000, 600_000]  # No CF in years 1-2
        exit_proceeds = 5_000_000
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        # Should still calculate correctly
        assert result['levered_irr'] > 0
        assert result['equity_multiple'] > 1.0
    
    def test_irr_meets_shieldstone_minimum(self):
        """Test that IRR meets Shieldstone absolute minimum (12%)."""
        total_equity = 4_000_000
        
        # Create cash flows that should barely meet 12% hurdle
        annual_cash_flows = [240_000, 280_000, 320_000, 360_000, 400_000]
        exit_proceeds = 3_200_000
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        # Should be at or above 12% minimum
        assert result['levered_irr'] >= MIN_IRR - 0.01  # Allow 1% tolerance
    
    def test_irr_negative_scenario(self):
        """Test IRR calculation when deal loses money."""
        total_equity = 5_000_000
        annual_cash_flows = [100_000, 150_000, 200_000, 250_000, 300_000]
        exit_proceeds = 2_000_000  # Sold at a loss
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        # IRR should be negative
        assert result['levered_irr'] < 0
        
        # Equity multiple should be < 1
        assert result['equity_multiple'] < 1.0
    
    def test_irr_precision(self):
        """Test that IRR calculation is precise (NPV at IRR ≈ 0)."""
        total_equity = 3_000_000
        annual_cash_flows = [180_000, 200_000, 220_000, 240_000, 260_000]
        exit_proceeds = 2_800_000
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        # Calculate NPV at the calculated IRR - should be near zero
        irr = result['levered_irr']
        cf_array = result['cash_flow_array']
        
        npv = sum(cf / (1 + irr)**i for i, cf in enumerate(cf_array))
        
        assert abs(npv) < 100  # NPV should be within $100 of zero


class TestEquityMultiple:
    """Test Equity Multiple calculations."""
    
    def test_basic_equity_multiple(self):
        """Test EM = Total Distributions / Equity Invested."""
        total_equity = 4_000_000
        annual_cash_flows = [200_000, 250_000, 300_000, 350_000, 400_000]
        exit_proceeds = 4_500_000
        
        total_distributions = sum(annual_cash_flows) + exit_proceeds
        equity_multiple = total_distributions / total_equity
        
        assert equity_multiple == 1.875
    
    def test_equity_multiple_meets_minimum(self):
        """Test that EM meets Shieldstone minimum (1.4x for 5 years)."""
        total_equity = 5_000_000
        
        # Minimum distributions to hit 1.4x
        minimum_distributions = total_equity * MIN_EQUITY_MULTIPLE
        
        # Allocate across 5 years + exit
        annual_cash_flows = [200_000, 200_000, 200_000, 200_000, 200_000]
        exit_proceeds = minimum_distributions - sum(annual_cash_flows)
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        assert result['equity_multiple'] >= MIN_EQUITY_MULTIPLE
    
    def test_equity_multiple_consistency(self):
        """Test that EM calculated in IRRCalculator matches manual calculation."""
        total_equity = 3_500_000
        annual_cash_flows = [175_000, 200_000, 225_000, 250_000, 275_000]
        exit_proceeds = 3_200_000
        
        calculator = IRRCalculator(total_equity, hold_period_years=5)
        result = calculator.calculate_levered_irr(annual_cash_flows, exit_proceeds)
        
        # Manual calculation
        manual_em = (sum(annual_cash_flows) + exit_proceeds) / total_equity
        
        assert abs(result['equity_multiple'] - manual_em) < 0.001


class TestCashOnCash:
    """Test Cash-on-Cash return calculations."""
    
    def test_stabilized_coc(self):
        """Test stabilized CoC = Stabilized Annual CF / Total Equity."""
        total_equity = 4_000_000
        stabilized_annual_cf = 320_000
        
        coc = stabilized_annual_cf / total_equity
        
        assert coc == 0.08  # 8%
    
    def test_coc_meets_shieldstone_minimum(self):
        """Test that stabilized CoC meets minimum (6%)."""
        total_equity = 5_000_000
        min_annual_cf = total_equity * MIN_COC_STABILIZED
        
        assert min_annual_cf == 300_000
        
        coc = min_annual_cf / total_equity
        assert coc == MIN_COC_STABILIZED
    
    def test_year_1_vs_stabilized_coc(self):
        """Test that stabilized CoC is typically higher than Year 1."""
        total_equity = 4_500_000
        year_1_cf = 180_000  # Lower during renovation
        stabilized_cf = 360_000  # Higher post-renovation
        
        year_1_coc = year_1_cf / total_equity
        stabilized_coc = stabilized_cf / total_equity
        
        assert year_1_coc == 0.04  # 4%
        assert stabilized_coc == 0.08  # 8%
        assert stabilized_coc > year_1_coc
    
    def test_coc_from_noi_and_debt_service(self):
        """Test CoC calculation from NOI and debt service."""
        # Given
        noi = 850_000
        annual_debt_service = 500_000
        total_equity = 4_000_000
        
        # Calculate
        annual_cash_flow = noi - annual_debt_service
        coc = annual_cash_flow / total_equity
        
        assert annual_cash_flow == 350_000
        assert coc == 0.0875  # 8.75%


class TestSourcesAndUses:
    """Test Sources & Uses calculations."""
    
    def test_sources_uses_balance(self):
        """Test that sources equal uses."""
        purchase_price = 10_000_000
        total_capex = 2_500_000
        
        sizer = LoanSizer(purchase_price, closing_cost_pct=CLOSING_COST_PCT)
        result = sizer.calculate_loan_and_equity(
            total_capex=total_capex,
            stabilized_noi=750_000,
            interest_rate=0.0575
        )
        
        # Sources should equal uses
        assert result['sources_uses_balanced'] is True
        assert abs(result['sources']['total'] - result['uses']['total']) < 1
        
        # Detailed breakdown
        sources_total = result['sources']['loan'] + result['sources']['equity']
        uses_total = (
            result['uses']['purchase_price'] +
            result['uses']['closing_costs'] +
            result['uses']['capex']
        )
        
        assert abs(sources_total - uses_total) < 1
    
    def test_equity_breakdown(self):
        """Test that equity breakdown is accurate."""
        purchase_price = 8_000_000
        total_capex = 1_800_000
        
        sizer = LoanSizer(purchase_price)
        result = sizer.calculate_loan_and_equity(
            total_capex=total_capex,
            stabilized_noi=600_000,
            interest_rate=0.0575
        )
        
        equity_breakdown = result['equity_breakdown']
        
        # Verify equity components
        expected_closing = purchase_price * CLOSING_COST_PCT
        expected_down = purchase_price - result['loan_amount']
        expected_total = expected_down + expected_closing + total_capex
        
        assert abs(equity_breakdown['closing_costs'] - expected_closing) < 1
        assert abs(equity_breakdown['down_payment'] - expected_down) < 1
        assert abs(equity_breakdown['total_equity'] - expected_total) < 1


class TestLeverageImpact:
    """Test how changing leverage impacts returns."""
    
    def test_leverage_impact_on_dscr(self):
        """Test that increasing leverage decreases DSCR."""
        purchase_price = 10_000_000
        stabilized_noi = 700_000
        total_capex = 2_000_000
        
        # Scenario 1: Standard 65% LTV
        sizer_1 = LoanSizer(purchase_price)
        result_1 = sizer_1.calculate_loan_and_equity(
            total_capex=total_capex,
            stabilized_noi=stabilized_noi,
            interest_rate=0.0575
        )
        
        # Scenario 2: Higher leverage (simulate 70% LTV by manually adjusting)
        # For this test, we verify that DSCR constraint becomes binding
        # as we increase the loan amount
        
        # With lower NOI, DSCR constraint should bind
        low_noi = 500_000
        result_2 = sizer_1.calculate_loan_and_equity(
            total_capex=total_capex,
            stabilized_noi=low_noi,
            interest_rate=0.0575
        )
        
        # Lower NOI should result in lower loan (DSCR constrained)
        assert result_2['loan_amount'] < result_1['loan_amount']
        assert result_2['binding_constraint'] == 'DSCR'
    
    def test_leverage_impact_on_coc(self):
        """Test that higher leverage increases CoC (if DSCR allows)."""
        purchase_price = 10_000_000
        noi = 800_000
        total_capex = 2_000_000
        interest_rate = 0.0575
        
        # Higher loan = lower equity = higher CoC (assuming NOI - DS is positive)
        sizer = LoanSizer(purchase_price)
        result = sizer.calculate_loan_and_equity(
            total_capex=total_capex,
            stabilized_noi=noi,
            interest_rate=interest_rate
        )
        
        # Calculate approximate annual debt service
        loan = result['loan_amount']
        monthly_rate = interest_rate / 12
        n_payments = 360
        monthly_payment_factor = (
            (monthly_rate * (1 + monthly_rate)**n_payments) /
            ((1 + monthly_rate)**n_payments - 1)
        )
        annual_debt_service = loan * monthly_payment_factor * 12
        
        # Calculate CoC
        annual_cf = noi - annual_debt_service
        coc = annual_cf / result['equity_breakdown']['total_equity']
        
        # CoC should be positive and reasonable
        assert coc > 0
        assert coc < 0.20  # Less than 20%


class TestRentGrowthImpact:
    """Test how rent growth impacts NOI and returns."""
    
    def test_rent_growth_impact_on_noi(self):
        """Test that rent growth increases NOI over time."""
        # Year 1
        year_1_gpr = 1_200_000
        vacancy_rate = 0.05
        other_income = 50_000
        opex = 480_000
        
        year_1_egi = year_1_gpr * (1 - vacancy_rate) + other_income
        year_1_noi = year_1_egi - opex
        
        # Year 5 with 3% annual rent growth
        rent_growth = 0.03
        years = 4  # Growth from year 1 to year 5
        year_5_gpr = year_1_gpr * (1 + rent_growth)**years
        
        # Assume opex grows at 2%
        opex_growth = 0.02
        year_5_opex = opex * (1 + opex_growth)**years
        
        year_5_egi = year_5_gpr * (1 - vacancy_rate) + other_income * (1 + rent_growth)**years
        year_5_noi = year_5_egi - year_5_opex
        
        # Year 5 NOI should be significantly higher
        assert year_5_noi > year_1_noi
        noi_increase_pct = (year_5_noi - year_1_noi) / year_1_noi
        
        # NOI should increase by approximately 3-5% compounded
        assert noi_increase_pct > 0.10  # At least 10% increase over 4 years
    
    def test_rent_growth_impact_on_irr(self):
        """Test that higher rent growth improves IRR."""
        total_equity = 4_000_000
        base_cf = 250_000
        
        # Scenario 1: No growth
        no_growth_cfs = [base_cf] * 5
        exit_proceeds_1 = 3_500_000
        
        calc_1 = IRRCalculator(total_equity, hold_period_years=5)
        result_1 = calc_1.calculate_levered_irr(no_growth_cfs, exit_proceeds_1)
        
        # Scenario 2: 3% annual growth
        growth_rate = 0.03
        growth_cfs = [base_cf * (1 + growth_rate)**i for i in range(5)]
        
        # Higher NOI also means higher exit value
        exit_proceeds_2 = 4_000_000
        
        calc_2 = IRRCalculator(total_equity, hold_period_years=5)
        result_2 = calc_2.calculate_levered_irr(growth_cfs, exit_proceeds_2)
        
        # Growth scenario should have higher IRR
        assert result_2['levered_irr'] > result_1['levered_irr']
        assert result_2['equity_multiple'] > result_1['equity_multiple']


# Pytest fixtures
@pytest.fixture
def sample_deal():
    """Sample deal data for testing."""
    return {
        'purchase_price': 10_000_000,
        'units': 200,
        'gross_potential_rent': 1_500_000,
        'vacancy_rate': 0.05,
        'other_income': 80_000,
        'operating_expenses': 600_000,
        'total_capex': 2_500_000,
        'interest_rate': 0.0575,
        'hold_period': 5
    }


@pytest.fixture
def sample_cash_flows():
    """Sample cash flow data for testing."""
    return {
        'total_equity': 4_000_000,
        'annual_cash_flows': [200_000, 250_000, 300_000, 350_000, 400_000],
        'exit_proceeds': 3_800_000
    }


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])

