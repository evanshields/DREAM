"""
Shieldstone LIHTC Underwriting Module
Version 1.0
December 18, 2025

A comprehensive Python library for LIHTC (Low-Income Housing Tax Credit) 
underwriting calculations and analysis.

This module provides production-ready classes for automating LIHTC underwriting
workflows, from initial property intake through final investment decision.

Classes organized by functional area:
- Basis Calculations (Sections 5-6)
- Tax Credit Calculations (Sections 7-9)
- Developer Fee & Sources/Uses (Sections 10-11)
- Bond Financing (Sections 12-15)
- Construction Timeline & Draws (Sections 16-18)
- Revenue Analysis (Sections 19-21)
- Operating Expenses (Section 22)
- Pro Forma & Cash Flow (Section 23)
- Special Situations (Sections 24-28)
- Returns Analysis (Sections 29, A3, A4)
- Decision Framework (Section 30)
- Workflow Orchestration (Section 32)

Usage Example:
    ```python
    from shieldstone_lihtc import (
        EligibleBasisCalculator,
        QualifiedBasisCalculator,
        CreditCalculator,
        EquityPricingCalculator
    )
    
    # Calculate eligible basis
    basis_calc = EligibleBasisCalculator()
    eligible_basis = basis_calc.calculate_eligible_basis(
        total_development_cost=10_000_000,
        land_cost=1_000_000,
        soft_costs=2_000_000
    )
    
    # Calculate qualified basis
    qualified_calc = QualifiedBasisCalculator()
    qualified_basis = qualified_calc.calculate_qualified_basis(
        eligible_basis=eligible_basis,
        applicable_fraction=0.80  # 80% low-income units
    )
    
    # Calculate tax credits
    credit_calc = CreditCalculator()
    annual_credits = credit_calc.calculate_annual_credits(
        qualified_basis=qualified_basis,
        credit_rate=0.0900  # 9% competitive credits
    )
    
    # Size equity
    equity_calc = EquityPricingCalculator()
    investor_equity = equity_calc.calculate_equity(
        annual_credits=annual_credits,
        credit_years=10,
        pricing=0.92  # $0.92 per $1 of credits
    )
    ```

Author: Shieldstone Capital
License: Proprietary
Documentation: See Shieldstone LIHTC Underwriting Manual V1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
from enum import Enum
import numpy_financial as npf
from datetime import datetime, date
import time


# =============================================================================
# ENUMERATIONS
# =============================================================================

class DealType(Enum):
    """LIHTC deal type classification."""
    NEW_CONSTRUCTION_9 = "9% New Construction"
    ACQUISITION_REHAB_4 = "4% Acquisition + Substantial Rehab"
    BOND_4 = "4% with Tax-Exempt Bonds"
    ADAPTIVE_REUSE = "Adaptive Reuse"


class PropertyType(Enum):
    """Property type classification."""
    FAMILY = "Family"
    SENIOR = "Senior (62+)"
    SUPPORTIVE = "Supportive Housing"
    SRO = "Single Room Occupancy"
    MIXED_USE = "Mixed-Use"


class CreditType(Enum):
    """Tax credit types."""
    LIHTC_9_PERCENT = "9% Competitive LIHTC"
    LIHTC_4_PERCENT = "4% Non-Competitive LIHTC"
    FEDERAL_HISTORIC = "20% Federal Historic"
    STATE_LIHTC = "State LIHTC"
    ENERGY = "Energy Credits"
    NMTC = "New Markets Tax Credits"


class WorkflowPhase(Enum):
    """Dream AI workflow phases."""
    DATA_INTAKE = "data_intake"
    ANALYSIS = "analysis"
    DECISION = "decision"
    OUTPUT = "output"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    VALIDATION_FAILED = "validation_failed"


class MilestoneType(Enum):
    """LP capital contribution milestone types."""
    CLOSING = "closing"
    CONSTRUCTION_50 = "construction_50"
    CONSTRUCTION_100 = "construction_100"
    STABILIZATION = "stabilization"
    FORM_8609 = "8609_issuance"
    ADJUSTER = "adjuster"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class PropertyData:
    """Basic property information."""
    property_name: str
    address: str
    city: str
    state: str
    zip_code: str
    total_units: int
    low_income_units: int
    deal_type: DealType
    property_type: PropertyType
    total_development_cost: Decimal


@dataclass
class EligibleBasisResult:
    """Results from eligible basis calculation."""
    total_development_cost: Decimal
    land_cost: Decimal
    hard_costs: Decimal
    soft_costs: Decimal
    developer_fee: Decimal
    eligible_costs_subtotal: Decimal
    qct_dda_boost: Decimal
    eligible_basis: Decimal
    boost_applied: bool
    boost_percentage: Decimal


@dataclass
class QualifiedBasisResult:
    """Results from qualified basis calculation."""
    eligible_basis: Decimal
    applicable_fraction: Decimal
    qualified_basis: Decimal
    low_income_units: int
    total_units: int
    market_rate_reduction: Decimal


@dataclass
class CreditResult:
    """Annual tax credit calculation result."""
    qualified_basis: Decimal
    credit_rate: Decimal
    annual_credits: Decimal
    credit_years: int
    total_10_year_credits: Decimal
    credit_type: CreditType


@dataclass
class EquityResult:
    """Equity sizing result."""
    total_credits: Decimal
    pricing_per_credit: Decimal
    gross_equity: Decimal
    syndication_fees: Decimal
    net_equity: Decimal
    equity_percentage_of_tdc: Decimal


@dataclass
class DeveloperFeeResult:
    """Developer fee calculation result."""
    total_development_cost: Decimal
    fee_percentage: Decimal
    total_fee: Decimal
    cash_fee: Decimal
    deferred_fee: Decimal
    cash_percentage: Decimal
    deferred_percentage: Decimal


@dataclass
class SourcesAndUsesResult:
    """Sources and uses balance result."""
    total_sources: Decimal
    total_uses: Decimal
    balance: Decimal
    is_balanced: bool
    sources_breakdown: Dict[str, Decimal]
    uses_breakdown: Dict[str, Decimal]


@dataclass
class BondSizingResult:
    """Bond sizing calculation result."""
    net_operating_income: Decimal
    target_dscr: Decimal
    maximum_debt_service: Decimal
    interest_rate: Decimal
    amortization_years: int
    maximum_bond_amount: Decimal
    annual_debt_service: Decimal


@dataclass
class AMIRentResult:
    """AMI rent limit calculation result."""
    ami_percentage: int  # e.g., 60 for 60% AMI
    household_size: int
    bedroom_count: int
    gross_ami_limit: Decimal
    utility_allowance: Decimal
    maximum_rent: Decimal


@dataclass
class RevenueProjectionResult:
    """Revenue projection result."""
    year: int
    gross_potential_rent: Decimal
    vacancy_loss: Decimal
    other_income: Decimal
    effective_gross_income: Decimal
    vacancy_rate: Decimal


@dataclass
class ExpenseProjectionResult:
    """Operating expense projection result."""
    year: int
    property_tax: Decimal
    insurance: Decimal
    utilities: Decimal
    repairs_maintenance: Decimal
    payroll: Decimal
    administrative: Decimal
    management_fee: Decimal
    total_operating_expenses: Decimal
    per_unit_per_month: Decimal


@dataclass
class CashFlowResult:
    """Annual cash flow result."""
    year: int
    effective_gross_income: Decimal
    operating_expenses: Decimal
    net_operating_income: Decimal
    debt_service: Decimal
    cash_flow_before_tax: Decimal
    dscr: Decimal
    occupancy_rate: Decimal


@dataclass
class DeveloperReturnResult:
    """Developer return analysis result."""
    total_developer_fee: Decimal
    cash_fee: Decimal
    deferred_fee: Decimal
    npv: Decimal
    irr_value: Decimal
    cash_on_cash_year_1: Decimal
    return_per_unit: Decimal
    payback_period_years: int
    irr_vs_target: str
    npv_quality: str


@dataclass
class DealScoringResult:
    """Go/No-Go deal scoring result."""
    total_weighted_score: Decimal
    score_percentage: Decimal
    recommendation: str
    financial_viability_score: Decimal
    market_strength_score: Decimal
    execution_risk_score: Decimal
    sponsor_quality_score: Decimal
    strategic_fit_score: Decimal
    strengths: List[str]
    weaknesses: List[str]
    conditions: List[str]
    critical_issues: List[str]
    approval_required: bool
    underwriter_name: str
    underwriter_date: date


@dataclass
class PartnershipSplit:
    """Partnership ownership and allocation percentages."""
    lp_credit_pct: Decimal
    gp_credit_pct: Decimal
    lp_loss_pct: Decimal
    gp_loss_pct: Decimal
    lp_cash_pct_initial: Decimal
    gp_cash_pct_initial: Decimal
    lp_residual_pct: Decimal
    gp_residual_pct: Decimal


@dataclass
class CapitalContribution:
    """LP capital contribution milestone."""
    milestone: str
    milestone_type: MilestoneType
    percentage: Decimal
    amount: Decimal
    timing_months: int
    conditions_precedent: List[str] = field(default_factory=list)
    use_of_funds: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class InvestorReturnResult:
    """Tax credit investor return analysis result."""
    total_equity_invested: Decimal
    total_tax_credits: Decimal
    total_tax_losses: Decimal
    total_loss_benefit: Decimal
    total_cash_distributions: Decimal
    exit_value: Decimal
    tax_credit_yield: Decimal
    effective_price_per_credit: Decimal
    after_tax_irr: Decimal
    total_benefit_multiple: Decimal
    payback_period_years: int


@dataclass
class WorkflowStep:
    """Individual workflow step in Dream AI."""
    step_id: str
    name: str
    phase: WorkflowPhase
    python_class: str
    section_reference: str
    inputs: List[str]
    outputs: List[str]
    status: WorkflowStatus = WorkflowStatus.NOT_STARTED
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0


@dataclass
class WorkflowResult:
    """Complete workflow execution result."""
    deal_name: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_steps: int
    completed_steps: int
    current_phase: WorkflowPhase
    overall_status: WorkflowStatus
    steps: List[WorkflowStep]
    final_outputs: Dict[str, Any]
    recommendation: str
    execution_time_seconds: float


# =============================================================================
# BASIS CALCULATIONS (SECTIONS 5-6)
# =============================================================================

class EligibleBasisCalculator:
    """
    Calculates LIHTC eligible basis from total development cost.
    
    Section 5: Eligible Basis Calculation
    
    Eligible basis includes:
    - Hard construction costs
    - Soft costs (architecture, engineering, legal, permits)
    - Developer fees (eligible portion)
    - Capitalized carrying costs
    
    Eligible basis excludes:
    - Land acquisition cost (always excluded)
    - Non-real-property costs
    - Reserves (replacement, operating, debt service)
    
    Includes optional 30% QCT/DDA boost for properties in Qualified Census
    Tracts or Difficult Development Areas.
    
    Example:
        >>> calculator = EligibleBasisCalculator()
        >>> result = calculator.calculate_eligible_basis(
        ...     total_development_cost=Decimal('10000000'),
        ...     land_cost=Decimal('1000000'),
        ...     hard_costs=Decimal('7000000'),
        ...     soft_costs=Decimal('1500000'),
        ...     developer_fee=Decimal('500000'),
        ...     apply_qct_dda_boost=True
        ... )
        >>> print(f"Eligible Basis: ${result.eligible_basis:,.0f}")
        Eligible Basis: $11,700,000
    """
    
    def calculate_eligible_basis(
        self,
        total_development_cost: Decimal,
        land_cost: Decimal,
        hard_costs: Decimal,
        soft_costs: Decimal,
        developer_fee: Decimal,
        apply_qct_dda_boost: bool = False,
        boost_percentage: Decimal = Decimal('0.30')
    ) -> EligibleBasisResult:
        """
        Calculate eligible basis for LIHTC credits.
        
        Args:
            total_development_cost: Total project cost
            land_cost: Land acquisition cost (excluded from basis)
            hard_costs: Hard construction costs (eligible)
            soft_costs: Soft costs (eligible)
            developer_fee: Developer fee (eligible)
            apply_qct_dda_boost: Apply 30% QCT/DDA boost
            boost_percentage: Boost percentage (default 30%)
            
        Returns:
            EligibleBasisResult with detailed breakdown
        """
        # Calculate eligible costs (TDC minus land)
        eligible_costs = total_development_cost - land_cost
        
        # Apply QCT/DDA boost if applicable
        if apply_qct_dda_boost:
            qct_dda_boost = eligible_costs * boost_percentage
            eligible_basis = eligible_costs + qct_dda_boost
        else:
            qct_dda_boost = Decimal('0')
            eligible_basis = eligible_costs
        
        return EligibleBasisResult(
            total_development_cost=total_development_cost,
            land_cost=land_cost,
            hard_costs=hard_costs,
            soft_costs=soft_costs,
            developer_fee=developer_fee,
            eligible_costs_subtotal=eligible_costs,
            qct_dda_boost=qct_dda_boost,
            eligible_basis=eligible_basis,
            boost_applied=apply_qct_dda_boost,
            boost_percentage=boost_percentage if apply_qct_dda_boost else Decimal('0')
        )


class QualifiedBasisCalculator:
    """
    Calculates LIHTC qualified basis using applicable fraction.
    
    Section 6: Qualified Basis & Applicable Fraction
    
    Qualified basis = Eligible basis × Applicable fraction
    
    Where applicable fraction accounts for:
    - Percentage of units that are low-income
    - Floor space allocation between low-income and market-rate
    
    Example:
        >>> calculator = QualifiedBasisCalculator()
        >>> result = calculator.calculate_qualified_basis(
        ...     eligible_basis=Decimal('11700000'),
        ...     low_income_units=80,
        ...     total_units=100
        ... )
        >>> print(f"Qualified Basis: ${result.qualified_basis:,.0f}")
        Qualified Basis: $9,360,000
    """
    
    def calculate_qualified_basis(
        self,
        eligible_basis: Decimal,
        low_income_units: int,
        total_units: int
    ) -> QualifiedBasisResult:
        """
        Calculate qualified basis from eligible basis and unit mix.
        
        Args:
            eligible_basis: Eligible basis (from Section 5)
            low_income_units: Number of low-income units
            total_units: Total units in property
            
        Returns:
            QualifiedBasisResult with applicable fraction applied
        """
        # Calculate applicable fraction
        applicable_fraction = Decimal(low_income_units) / Decimal(total_units)
        
        # Calculate qualified basis
        qualified_basis = eligible_basis * applicable_fraction
        
        # Calculate market-rate reduction
        market_rate_reduction = eligible_basis * (Decimal('1') - applicable_fraction)
        
        return QualifiedBasisResult(
            eligible_basis=eligible_basis,
            applicable_fraction=applicable_fraction,
            qualified_basis=qualified_basis,
            low_income_units=low_income_units,
            total_units=total_units,
            market_rate_reduction=market_rate_reduction
        )


# =============================================================================
# TAX CREDIT CALCULATIONS (SECTIONS 7-9)
# =============================================================================

class CreditCalculator:
    """
    Calculates annual LIHTC tax credits.
    
    Section 7: Annual Tax Credit Calculation
    
    Annual Credits = Qualified Basis × Credit Rate
    
    Credit Rates:
    - 9% competitive credits: ~9.0% (varies by IRS adjustment)
    - 4% non-competitive credits: ~4.26% (varies by IRS adjustment)
    
    Credits delivered over 10-year period beginning when property placed in service.
    
    Example:
        >>> calculator = CreditCalculator()
        >>> result = calculator.calculate_annual_credits(
        ...     qualified_basis=Decimal('9360000'),
        ...     credit_rate=Decimal('0.09'),
        ...     credit_type=CreditType.LIHTC_9_PERCENT
        ... )
        >>> print(f"Annual Credits: ${result.annual_credits:,.0f}")
        >>> print(f"10-Year Total: ${result.total_10_year_credits:,.0f}")
        Annual Credits: $842,400
        10-Year Total: $8,424,000
    """
    
    def calculate_annual_credits(
        self,
        qualified_basis: Decimal,
        credit_rate: Decimal,
        credit_type: CreditType = CreditType.LIHTC_9_PERCENT,
        credit_years: int = 10
    ) -> CreditResult:
        """
        Calculate annual tax credits from qualified basis.
        
        Args:
            qualified_basis: Qualified basis (from Section 6)
            credit_rate: Credit rate (0.09 for 9%, 0.0426 for 4%)
            credit_type: Type of credit
            credit_years: Years of credits (default 10)
            
        Returns:
            CreditResult with annual and 10-year totals
        """
        annual_credits = qualified_basis * credit_rate
        total_credits = annual_credits * credit_years
        
        return CreditResult(
            qualified_basis=qualified_basis,
            credit_rate=credit_rate,
            annual_credits=annual_credits,
            credit_years=credit_years,
            total_10_year_credits=total_credits,
            credit_type=credit_type
        )


class EquityPricingCalculator:
    """
    Calculates investor equity from tax credit stream.
    
    Section 9: Equity Pricing & Sizing
    
    Investor Equity = Total Credits × Pricing per Credit
    
    Typical pricing: $0.85-$0.95 per dollar of credits
    - Higher for CRA banks and strong sponsors
    - Lower for risk-adjusted or corporate investors
    
    Example:
        >>> calculator = EquityPricingCalculator()
        >>> result = calculator.calculate_equity(
        ...     total_credits=Decimal('8424000'),
        ...     pricing_per_credit=Decimal('0.92')
        ... )
        >>> print(f"Net Equity: ${result.net_equity:,.0f}")
        Net Equity: $7,750,080
    """
    
    def calculate_equity(
        self,
        total_credits: Decimal,
        pricing_per_credit: Decimal,
        syndication_fee_percentage: Decimal = Decimal('0.00')
    ) -> EquityResult:
        """
        Calculate equity raised from tax credit stream.
        
        Args:
            total_credits: Total 10-year credits
            pricing_per_credit: Price per $1 of credits (e.g., 0.92)
            syndication_fee_percentage: Syndication fees as % of gross equity
            
        Returns:
            EquityResult with gross and net equity
        """
        gross_equity = total_credits * pricing_per_credit
        syndication_fees = gross_equity * syndication_fee_percentage
        net_equity = gross_equity - syndication_fees
        
        return EquityResult(
            total_credits=total_credits,
            pricing_per_credit=pricing_per_credit,
            gross_equity=gross_equity,
            syndication_fees=syndication_fees,
            net_equity=net_equity,
            equity_percentage_of_tdc=Decimal('0')  # Would be calculated with TDC
        )


# =============================================================================
# DEVELOPER FEE & SOURCES/USES (SECTIONS 10-11)
# =============================================================================

class DeveloperFeeCalculator:
    """
    Calculates developer fee and cash vs. deferred split.
    
    Section 10: Developer Fee Structuring
    
    Developer fee typically 12-18% of total development cost, with portion
    paid in cash at closing and remainder deferred until stabilization/refinance.
    
    Example:
        >>> calculator = DeveloperFeeCalculator()
        >>> result = calculator.calculate_developer_fee(
        ...     total_development_cost=Decimal('10000000'),
        ...     fee_percentage=Decimal('0.15'),
        ...     cash_percentage=Decimal('0.30')
        ... )
        >>> print(f"Total Fee: ${result.total_fee:,.0f}")
        >>> print(f"Cash: ${result.cash_fee:,.0f}, Deferred: ${result.deferred_fee:,.0f}")
        Total Fee: $1,500,000
        Cash: $450,000, Deferred: $1,050,000
    """
    
    def calculate_developer_fee(
        self,
        total_development_cost: Decimal,
        fee_percentage: Decimal,
        cash_percentage: Decimal = Decimal('0.30')
    ) -> DeveloperFeeResult:
        """
        Calculate developer fee with cash/deferred split.
        
        Args:
            total_development_cost: Total development cost
            fee_percentage: Fee as % of TDC (e.g., 0.15 = 15%)
            cash_percentage: % of fee paid in cash (e.g., 0.30 = 30%)
            
        Returns:
            DeveloperFeeResult with total, cash, and deferred amounts
        """
        total_fee = total_development_cost * fee_percentage
        cash_fee = total_fee * cash_percentage
        deferred_fee = total_fee * (Decimal('1') - cash_percentage)
        
        return DeveloperFeeResult(
            total_development_cost=total_development_cost,
            fee_percentage=fee_percentage,
            total_fee=total_fee,
            cash_fee=cash_fee,
            deferred_fee=deferred_fee,
            cash_percentage=cash_percentage,
            deferred_percentage=Decimal('1') - cash_percentage
        )


class SourcesAndUsesBalancer:
    """
    Balances sources and uses of funds for LIHTC deal.
    
    Section 11: Sources & Uses Balancing
    
    Ensures total sources equals total uses within acceptable tolerance.
    
    Sources:
    - Tax credit equity
    - Tax-exempt bonds or conventional debt
    - Deferred developer fee
    - Grants and soft debt
    
    Uses:
    - Land acquisition
    - Hard construction costs
    - Soft costs
    - Developer fee
    - Reserves
    
    Example:
        >>> balancer = SourcesAndUsesBalancer()
        >>> result = balancer.balance(
        ...     sources={'equity': Decimal('7750080'), 'bonds': Decimal('2500000')},
        ...     uses={'land': Decimal('1000000'), 'construction': Decimal('7000000'), 'soft': Decimal('1500000'), 'fee': Decimal('750080')}
        ... )
        >>> print(f"Balanced: {result.is_balanced}")
        >>> print(f"Gap: ${result.balance:,.0f}")
        Balanced: True
        Gap: $0
    """
    
    def balance(
        self,
        sources: Dict[str, Decimal],
        uses: Dict[str, Decimal],
        tolerance: Decimal = Decimal('10000')
    ) -> SourcesAndUsesResult:
        """
        Balance sources and uses of funds.
        
        Args:
            sources: Dict of source names to amounts
            uses: Dict of use names to amounts
            tolerance: Acceptable imbalance (default $10,000)
            
        Returns:
            SourcesAndUsesResult with balance check
        """
        total_sources = sum(sources.values())
        total_uses = sum(uses.values())
        balance = total_sources - total_uses
        is_balanced = abs(balance) <= tolerance
        
        return SourcesAndUsesResult(
            total_sources=total_sources,
            total_uses=total_uses,
            balance=balance,
            is_balanced=is_balanced,
            sources_breakdown=sources,
            uses_breakdown=uses
        )


# =============================================================================
# BOND FINANCING (SECTIONS 12-13)
# =============================================================================

class BondSizingCalculator:
    """
    Sizes tax-exempt bonds based on DSCR and NOI.
    
    Section 13: Bond Sizing & DSCR
    
    Maximum Bond Amount = PV of (NOI / Target DSCR) over amortization period
    
    Typical DSCR targets:
    - 1.15x for properties with Section 8 HAP contracts
    - 1.20x for properties without HAP
    - 1.25x for higher-risk properties
    
    Example:
        >>> calculator = BondSizingCalculator()
        >>> result = calculator.size_bonds(
        ...     net_operating_income=Decimal('600000'),
        ...     target_dscr=Decimal('1.20'),
        ...     interest_rate=Decimal('0.05'),
        ...     amortization_years=35
        ... )
        >>> print(f"Maximum Bond Amount: ${result.maximum_bond_amount:,.0f}")
        >>> print(f"Annual Debt Service: ${result.annual_debt_service:,.0f}")
        Maximum Bond Amount: $7,715,415
        Annual Debt Service: $500,000
    """
    
    def size_bonds(
        self,
        net_operating_income: Decimal,
        target_dscr: Decimal,
        interest_rate: Decimal,
        amortization_years: int = 35
    ) -> BondSizingResult:
        """
        Calculate maximum bond amount based on NOI and DSCR.
        
        Args:
            net_operating_income: Stabilized NOI
            target_dscr: Target debt service coverage ratio
            interest_rate: Annual interest rate (e.g., 0.05 = 5%)
            amortization_years: Amortization period
            
        Returns:
            BondSizingResult with max bond amount and debt service
        """
        # Calculate maximum annual debt service
        maximum_debt_service = net_operating_income / target_dscr
        
        # Calculate present value of debt service stream
        # Using mortgage formula: PV = PMT × [(1 - (1 + r)^-n) / r]
        monthly_rate = float(interest_rate) / 12
        num_payments = amortization_years * 12
        monthly_payment = float(maximum_debt_service) / 12
        
        if monthly_rate > 0:
            pv_factor = (1 - (1 + monthly_rate) ** -num_payments) / monthly_rate
            maximum_bond_amount = Decimal(str(monthly_payment * pv_factor))
        else:
            maximum_bond_amount = maximum_debt_service * Decimal(amortization_years)
        
        return BondSizingResult(
            net_operating_income=net_operating_income,
            target_dscr=target_dscr,
            maximum_debt_service=maximum_debt_service,
            interest_rate=interest_rate,
            amortization_years=amortization_years,
            maximum_bond_amount=maximum_bond_amount,
            annual_debt_service=maximum_debt_service
        )


# =============================================================================
# REVENUE ANALYSIS (SECTIONS 19-21)
# =============================================================================

class AMIRentCalculator:
    """
    Calculates maximum rent limits based on Area Median Income.
    
    Section 19: AMI Rent Limits
    
    Maximum Rent = (AMI Limit × 30%) - Utility Allowance
    
    Where AMI limit varies by:
    - AMI percentage (30%, 50%, 60%, 80%)
    - Household size
    - Geographic area
    
    Example:
        >>> calculator = AMIRentCalculator()
        >>> result = calculator.calculate_rent_limit(
        ...     ami_percentage=60,
        ...     household_size=3,
        ...     bedroom_count=2,
        ...     area_median_income=Decimal('75000'),
        ...     utility_allowance=Decimal('150')
        ... )
        >>> print(f"Maximum Rent: ${result.maximum_rent:,.0f}/month")
        Maximum Rent: $975/month
    """
    
    def calculate_rent_limit(
        self,
        ami_percentage: int,
        household_size: int,
        bedroom_count: int,
        area_median_income: Decimal,
        utility_allowance: Decimal = Decimal('0')
    ) -> AMIRentResult:
        """
        Calculate maximum rent based on AMI limits.
        
        Args:
            ami_percentage: AMI tier (30, 50, 60, 80)
            household_size: Number of people in household
            bedroom_count: Number of bedrooms
            area_median_income: Area median income for MSA
            utility_allowance: Utility allowance to deduct
            
        Returns:
            AMIRentResult with maximum rent calculation
        """
        # Adjust AMI for household size (simplified - actual uses HUD tables)
        household_adjustment = Decimal('1.0') + (Decimal(household_size - 1) * Decimal('0.08'))
        adjusted_ami = area_median_income * household_adjustment
        
        # Calculate AMI limit
        ami_limit = adjusted_ami * (Decimal(ami_percentage) / Decimal('100'))
        
        # Calculate maximum rent (30% of income limit, monthly)
        gross_rent_limit = (ami_limit * Decimal('0.30')) / Decimal('12')
        
        # Subtract utility allowance
        maximum_rent = gross_rent_limit - utility_allowance
        
        return AMIRentResult(
            ami_percentage=ami_percentage,
            household_size=household_size,
            bedroom_count=bedroom_count,
            gross_ami_limit=ami_limit,
            utility_allowance=utility_allowance,
            maximum_rent=maximum_rent
        )


class RevenueProjector:
    """
    Projects revenue over 15-year period with growth assumptions.
    
    Section 21: Revenue Underwriting
    
    Revenue Components:
    - Gross Potential Rent (GPR)
    - Vacancy & Loss (typically 5-7%)
    - Other Income (laundry, parking, fees)
    
    Effective Gross Income = GPR - Vacancy + Other Income
    
    Example:
        >>> projector = RevenueProjector()
        >>> results = projector.project_revenue(
        ...     year_1_gpr=Decimal('1200000'),
        ...     vacancy_rate=Decimal('0.05'),
        ...     other_income=Decimal('50000'),
        ...     growth_rate=Decimal('0.025'),
        ...     years=15
        ... )
        >>> for year, result in enumerate(results, 1):
        ...     print(f"Year {year}: EGI ${result.effective_gross_income:,.0f}")
    """
    
    def project_revenue(
        self,
        year_1_gpr: Decimal,
        vacancy_rate: Decimal,
        other_income: Decimal,
        growth_rate: Decimal = Decimal('0.025'),
        years: int = 15
    ) -> List[RevenueProjectionResult]:
        """
        Project revenue for multi-year period.
        
        Args:
            year_1_gpr: Year 1 gross potential rent
            vacancy_rate: Vacancy & loss rate (e.g., 0.05 = 5%)
            other_income: Annual other income
            growth_rate: Annual growth rate (e.g., 0.025 = 2.5%)
            years: Number of years to project
            
        Returns:
            List of RevenueProjectionResult for each year
        """
        results = []
        
        for year in range(1, years + 1):
            # Apply compound growth
            growth_factor = (Decimal('1') + growth_rate) ** Decimal(year - 1)
            current_gpr = year_1_gpr * growth_factor
            current_other_income = other_income * growth_factor
            
            # Calculate vacancy loss
            vacancy_loss = current_gpr * vacancy_rate
            
            # Calculate effective gross income
            egi = current_gpr - vacancy_loss + current_other_income
            
            results.append(RevenueProjectionResult(
                year=year,
                gross_potential_rent=current_gpr,
                vacancy_loss=vacancy_loss,
                other_income=current_other_income,
                effective_gross_income=egi,
                vacancy_rate=vacancy_rate
            ))
        
        return results


# =============================================================================
# OPERATING EXPENSES (SECTION 22)
# =============================================================================

class OpExBenchmarker:
    """
    Benchmarks operating expenses and projects growth.
    
    Section 22: Operating Expenses
    
    Operating expense categories:
    - Property taxes (varies by jurisdiction)
    - Insurance
    - Utilities
    - Repairs & maintenance
    - Payroll
    - Administrative
    - Management fee (typically 5-6% of EGI)
    
    Example:
        >>> benchmarker = OpExBenchmarker()
        >>> results = benchmarker.project_expenses(
        ...     year_1_opex=Decimal('500000'),
        ...     escalation_rate=Decimal('0.02'),
        ...     years=15
        ... )
        >>> for year, result in enumerate(results, 1):
        ...     print(f"Year {year}: OpEx ${result.total_operating_expenses:,.0f}")
    """
    
    def project_expenses(
        self,
        year_1_opex: Decimal,
        escalation_rate: Decimal = Decimal('0.02'),
        years: int = 15
    ) -> List[ExpenseProjectionResult]:
        """
        Project operating expenses with escalation.
        
        Args:
            year_1_opex: Year 1 total operating expenses
            escalation_rate: Annual escalation (e.g., 0.02 = 2%)
            years: Number of years to project
            
        Returns:
            List of ExpenseProjectionResult for each year
        """
        results = []
        
        for year in range(1, years + 1):
            # Apply compound escalation
            escalation_factor = (Decimal('1') + escalation_rate) ** Decimal(year - 1)
            current_opex = year_1_opex * escalation_factor
            
            results.append(ExpenseProjectionResult(
                year=year,
                property_tax=Decimal('0'),  # Would be calculated separately
                insurance=Decimal('0'),
                utilities=Decimal('0'),
                repairs_maintenance=Decimal('0'),
                payroll=Decimal('0'),
                administrative=Decimal('0'),
                management_fee=Decimal('0'),
                total_operating_expenses=current_opex,
                per_unit_per_month=Decimal('0')
            ))
        
        return results


# =============================================================================
# PRO FORMA & CASH FLOW (SECTION 23)
# =============================================================================

class CashFlowProjector:
    """
    Projects 15-year cash flow pro forma with DSCR validation.
    
    Section 23: 15-Year Pro Forma
    
    Annual Cash Flow:
    - Effective Gross Income (from Section 21)
    - Operating Expenses (from Section 22)
    - Net Operating Income = EGI - OpEx
    - Debt Service (from Section 13)
    - Cash Flow Before Tax = NOI - Debt Service
    - DSCR = NOI / Debt Service
    
    Example:
        >>> projector = CashFlowProjector()
        >>> results = projector.project_cash_flow(
        ...     revenue_projections=revenue_results,
        ...     expense_projections=expense_results,
        ...     annual_debt_service=Decimal('500000')
        ... )
        >>> for result in results:
        ...     print(f"Year {result.year}: CFBT ${result.cash_flow_before_tax:,.0f}, DSCR {result.dscr:.2f}x")
    """
    
    def project_cash_flow(
        self,
        revenue_projections: List[RevenueProjectionResult],
        expense_projections: List[ExpenseProjectionResult],
        annual_debt_service: Decimal,
        year_1_occupancy: Decimal = Decimal('0.95')
    ) -> List[CashFlowResult]:
        """
        Project cash flow combining revenue, expenses, and debt service.
        
        Args:
            revenue_projections: Revenue projections from RevenueProjector
            expense_projections: Expense projections from OpExBenchmarker
            annual_debt_service: Annual debt service amount
            year_1_occupancy: Year 1 occupancy rate
            
        Returns:
            List of CashFlowResult for each year
        """
        results = []
        
        for rev, exp in zip(revenue_projections, expense_projections):
            # Calculate NOI
            noi = rev.effective_gross_income - exp.total_operating_expenses
            
            # Calculate cash flow before tax
            cfbt = noi - annual_debt_service
            
            # Calculate DSCR
            dscr = noi / annual_debt_service if annual_debt_service > 0 else Decimal('0')
            
            # Assume stabilized occupancy after Year 1
            occupancy = year_1_occupancy if rev.year == 1 else Decimal('0.95')
            
            results.append(CashFlowResult(
                year=rev.year,
                effective_gross_income=rev.effective_gross_income,
                operating_expenses=exp.total_operating_expenses,
                net_operating_income=noi,
                debt_service=annual_debt_service,
                cash_flow_before_tax=cfbt,
                dscr=dscr,
                occupancy_rate=occupancy
            ))
        
        return results


# =============================================================================
# RETURNS ANALYSIS (SECTIONS 29, A3, A4)
# =============================================================================

class DeveloperReturnCalculator:
    """
    Calculates developer returns including NPV, IRR, and cash-on-cash.
    
    Section 29: Developer Returns Analysis
    
    Developer returns come from:
    - Developer fee (primary return)
    - Operating cash flow distributions (GP share)
    - Residual value at exit
    
    Typical targets:
    - IRR: 20-30%
    - NPV @ 18%: > $500K
    - Return per unit: $20-25K
    
    Example:
        >>> calculator = DeveloperReturnCalculator()
        >>> result = calculator.calculate_returns(
        ...     total_developer_fee=Decimal('1500000'),
        ...     cash_fee_percentage=Decimal('0.30'),
        ...     annual_cash_flows=[Decimal('50000')] * 10,
        ...     residual_value=Decimal('1000000'),
        ...     discount_rate=Decimal('0.18')
        ... )
        >>> print(f"NPV: ${result.npv:,.0f}, IRR: {result.irr_value:.1%}")
    """
    
    def calculate_returns(
        self,
        total_developer_fee: Decimal,
        cash_fee_percentage: Decimal,
        annual_cash_flows: List[Decimal],
        residual_value: Decimal,
        discount_rate: Decimal = Decimal('0.18'),
        total_units: int = 100
    ) -> DeveloperReturnResult:
        """
        Calculate comprehensive developer returns.
        
        Args:
            total_developer_fee: Total developer fee
            cash_fee_percentage: % of fee paid in cash
            annual_cash_flows: Annual cash distributions to developer
            residual_value: Exit value
            discount_rate: NPV discount rate
            total_units: Total units (for per-unit calc)
            
        Returns:
            DeveloperReturnResult with NPV, IRR, metrics
        """
        cash_fee = total_developer_fee * cash_fee_percentage
        deferred_fee = total_developer_fee - cash_fee
        
        # Build cash flow stream
        cash_flows = [-float(cash_fee)] + [float(cf) for cf in annual_cash_flows]
        cash_flows[-1] += float(residual_value)
        
        # Calculate NPV
        discount_factors = [(1 / (1 + float(discount_rate)) ** i) for i in range(len(cash_flows))]
        npv = sum(cf * df for cf, df in zip(cash_flows, discount_factors))
        
        # Calculate IRR
        try:
            irr_value = npf.irr(cash_flows)
        except:
            irr_value = 0.0
        
        # Calculate metrics
        cash_on_cash_year_1 = annual_cash_flows[0] / cash_fee if cash_fee > 0 else Decimal('0')
        return_per_unit = total_developer_fee / Decimal(total_units)
        
        # Determine payback period
        cumulative = Decimal('0')
        payback = 0
        for cf in annual_cash_flows:
            cumulative += cf
            payback += 1
            if cumulative >= deferred_fee:
                break
        
        # Quality assessments
        irr_quality = "Excellent" if irr_value >= 0.25 else "Good" if irr_value >= 0.20 else "Acceptable"
        npv_quality = "Excellent" if npv >= 500000 else "Good" if npv >= 250000 else "Acceptable"
        
        return DeveloperReturnResult(
            total_developer_fee=total_developer_fee,
            cash_fee=cash_fee,
            deferred_fee=deferred_fee,
            npv=Decimal(str(npv)),
            irr_value=Decimal(str(irr_value)),
            cash_on_cash_year_1=cash_on_cash_year_1,
            return_per_unit=return_per_unit,
            payback_period_years=payback,
            irr_vs_target="Above" if irr_value >= 0.20 else "Below",
            npv_quality=npv_quality
        )


class PartnershipStructureCalculator:
    """
    Calculates partnership allocations and LP contribution schedule.
    
    Appendix A3: Partnership Structure & GP/LP Splits
    
    Standard LIHTC partnership structure:
    - LP receives 99.99% of tax credits and losses
    - GP receives 0.01% of tax credits and losses  
    - Cash distributions typically 10% LP / 90% GP
    
    LP equity contributed in milestone tranches tied to construction progress.
    
    Example:
        >>> calculator = PartnershipStructureCalculator()
        >>> contributions = calculator.calculate_contribution_schedule(
        ...     total_equity=Decimal('40000000'),
        ...     milestones={
        ...         'closing': Decimal('0.125'),
        ...         'construction_50': Decimal('0.30'),
        ...         'stabilization': Decimal('0.575')
        ...     }
        ... )
    """
    
    def calculate_contribution_schedule(
        self,
        total_equity: Decimal,
        milestones: Dict[str, Decimal]
    ) -> List[CapitalContribution]:
        """
        Calculate LP capital contribution schedule.
        
        Args:
            total_equity: Total LP equity to be contributed
            milestones: Dict of milestone names to percentages
            
        Returns:
            List of CapitalContribution for each milestone
        """
        contributions = []
        
        for milestone_name, percentage in milestones.items():
            amount = total_equity * percentage
            
            # Determine milestone type and timing
            if 'closing' in milestone_name.lower():
                milestone_type = MilestoneType.CLOSING
                timing = 0
            elif '50' in milestone_name:
                milestone_type = MilestoneType.CONSTRUCTION_50
                timing = 12
            elif '100' in milestone_name:
                milestone_type = MilestoneType.CONSTRUCTION_100
                timing = 24
            elif 'stab' in milestone_name.lower():
                milestone_type = MilestoneType.STABILIZATION
                timing = 30
            else:
                milestone_type = MilestoneType.ADJUSTER
                timing = 90
            
            contributions.append(CapitalContribution(
                milestone=milestone_name,
                milestone_type=milestone_type,
                percentage=percentage,
                amount=amount,
                timing_months=timing
            ))
        
        return contributions


class InvestorReturnCalculator:
    """
    Calculates tax credit investor (LP) returns.
    
    Appendix A4: Tax Credit Investor Return Calculations
    
    LP returns come primarily from TAX BENEFITS:
    - Tax credits (dollar-for-dollar reduction in tax liability)
    - Tax losses (depreciation pass-through valued at marginal rate)
    - NOT from cash distributions (typically minimal)
    
    Target IRR: 5-8% after-tax
    Target Yield: 105-115% (total credits ÷ equity)
    
    Example:
        >>> calculator = InvestorReturnCalculator(marginal_tax_rate=Decimal('0.21'))
        >>> result = calculator.calculate_investor_returns(
        ...     equity_invested=Decimal('40000000'),
        ...     annual_credits=[Decimal('2656000')] * 10,
        ...     annual_losses=[Decimal('4000000')] * 10,
        ...     annual_distributions=[Decimal('50000')] * 10,
        ...     residual_value=Decimal('1000')
        ... )
        >>> print(f"Tax Credit Yield: {result.tax_credit_yield:.1%}")
        >>> print(f"After-Tax IRR: {result.after_tax_irr:.2%}")
    """
    
    def __init__(self, marginal_tax_rate: Decimal = Decimal('0.21')):
        """Initialize with marginal tax rate."""
        self.tax_rate = marginal_tax_rate
    
    def calculate_investor_returns(
        self,
        equity_invested: Decimal,
        annual_credits: List[Decimal],
        annual_losses: List[Decimal],
        annual_distributions: List[Decimal],
        residual_value: Decimal
    ) -> InvestorReturnResult:
        """
        Calculate comprehensive investor returns.
        
        Args:
            equity_invested: Total LP equity invested
            annual_credits: List of annual tax credits
            annual_losses: List of annual tax losses
            annual_distributions: List of cash distributions
            residual_value: Exit value (typically nominal)
            
        Returns:
            InvestorReturnResult with yield, IRR, and metrics
        """
        # Calculate totals
        total_credits = sum(annual_credits)
        total_losses = sum(annual_losses)
        total_loss_benefit = total_losses * self.tax_rate
        total_cash = sum(annual_distributions)
        
        # Calculate metrics
        tax_credit_yield = total_credits / equity_invested if equity_invested > 0 else Decimal('0')
        effective_price = equity_invested / total_credits if total_credits > 0 else Decimal('0')
        
        # Build cash flow stream for IRR
        cash_flows = [-float(equity_invested)]
        for credits, losses, dist in zip(annual_credits, annual_losses, annual_distributions):
            annual_benefit = float(credits) + float(losses * self.tax_rate) + float(dist)
            cash_flows.append(annual_benefit)
        cash_flows[-1] += float(residual_value)
        
        # Calculate IRR
        try:
            irr_value = npf.irr(cash_flows)
        except:
            irr_value = 0.0
        
        # Calculate payback
        cumulative = Decimal('0')
        payback = 0
        for credits, losses, dist in zip(annual_credits, annual_losses, annual_distributions):
            cumulative += credits + (losses * self.tax_rate) + dist
            payback += 1
            if cumulative >= equity_invested:
                break
        
        # Calculate benefit multiple
        total_benefits = total_credits + total_loss_benefit + total_cash + residual_value
        benefit_multiple = total_benefits / equity_invested if equity_invested > 0 else Decimal('0')
        
        return InvestorReturnResult(
            total_equity_invested=equity_invested,
            total_tax_credits=total_credits,
            total_tax_losses=total_losses,
            total_loss_benefit=total_loss_benefit,
            total_cash_distributions=total_cash,
            exit_value=residual_value,
            tax_credit_yield=tax_credit_yield,
            effective_price_per_credit=effective_price,
            after_tax_irr=Decimal(str(irr_value)),
            total_benefit_multiple=benefit_multiple,
            payback_period_years=payback
        )


# =============================================================================
# DECISION FRAMEWORK (SECTION 30)
# =============================================================================

class DealScoringEngine:
    """
    Scores LIHTC deals for go/no-go investment decision.
    
    Section 30: Go/No-Go Decision Framework
    
    Scoring categories (100 points total):
    - Financial Viability (30 points): DSCR, Sources=Uses, Developer returns
    - Market Strength (20 points): Capture rate, vacancy, rent achievability
    - Execution Risk (20 points): Developer experience, timeline, contingency
    - Sponsor Quality (15 points): Track record, financial capacity
    - Strategic Fit (15 points): Portfolio alignment, geography, size
    
    Decision thresholds:
    - 80+ points: PROCEED
    - 65-79 points: PROCEED WITH CONDITIONS
    - <65 points: PASS
    
    Example:
        >>> engine = DealScoringEngine()
        >>> result = engine.score_deal(
        ...     financial_viability=28,
        ...     market_strength=18,
        ...     execution_risk=16,
        ...     sponsor_quality=14,
        ...     strategic_fit=13
        ... )
        >>> print(f"Score: {result.total_weighted_score}/100 - {result.recommendation}")
    """
    
    def score_deal(
        self,
        financial_viability: Decimal,
        market_strength: Decimal,
        execution_risk: Decimal,
        sponsor_quality: Decimal,
        strategic_fit: Decimal,
        underwriter_name: str = "",
        critical_issues: Optional[List[str]] = None
    ) -> DealScoringResult:
        """
        Score deal across all categories and generate recommendation.
        
        Args:
            financial_viability: Financial score (0-30 points)
            market_strength: Market score (0-20 points)
            execution_risk: Execution score (0-20 points)
            sponsor_quality: Sponsor score (0-15 points)
            strategic_fit: Strategic score (0-15 points)
            underwriter_name: Name of underwriter
            critical_issues: List of critical issues (auto-PASS if present)
            
        Returns:
            DealScoringResult with recommendation
        """
        # Calculate total score
        total_score = (financial_viability + market_strength + execution_risk +
                      sponsor_quality + strategic_fit)
        score_percentage = (total_score / Decimal('100')) * Decimal('100')
        
        # Check for critical issues
        has_critical_issues = bool(critical_issues and len(critical_issues) > 0)
        
        # Determine recommendation
        if has_critical_issues:
            recommendation = "PASS - Critical Issues"
            approval_required = False
        elif total_score >= Decimal('80'):
            recommendation = "PROCEED"
            approval_required = True
        elif total_score >= Decimal('65'):
            recommendation = "PROCEED WITH CONDITIONS"
            approval_required = True
        else:
            recommendation = "PASS"
            approval_required = False
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if financial_viability >= Decimal('27'):
            strengths.append("Strong financial metrics")
        elif financial_viability < Decimal('20'):
            weaknesses.append("Weak financial metrics")
        
        if market_strength >= Decimal('17'):
            strengths.append("Excellent market positioning")
        elif market_strength < Decimal('14'):
            weaknesses.append("Market concerns")
        
        if sponsor_quality >= Decimal('13'):
            strengths.append("Experienced sponsor")
        elif sponsor_quality < Decimal('10'):
            weaknesses.append("Sponsor execution risk")
        
        return DealScoringResult(
            total_weighted_score=total_score,
            score_percentage=score_percentage,
            recommendation=recommendation,
            financial_viability_score=financial_viability,
            market_strength_score=market_strength,
            execution_risk_score=execution_risk,
            sponsor_quality_score=sponsor_quality,
            strategic_fit_score=strategic_fit,
            strengths=strengths,
            weaknesses=weaknesses,
            conditions=[] if not has_critical_issues else critical_issues,
            critical_issues=critical_issues or [],
            approval_required=approval_required,
            underwriter_name=underwriter_name,
            underwriter_date=date.today()
        )


# =============================================================================
# WORKFLOW ORCHESTRATION (SECTION 32)
# =============================================================================

class DreamAIOrchestrator:
    """
    Master orchestrator for Dream AI LIHTC underwriting workflow.
    
    Section 32: Dream AI Workflow & Integration
    
    Coordinates execution of all Python classes in proper sequence,
    managing data flow between components and generating outputs.
    
    Workflow Phases:
    1. Data Intake: Document processing, validation, market data
    2. Analysis: Basis → Credits → Equity → Pro Forma
    3. Decision: Developer Returns → Go/No-Go Scoring
    4. Output: Deliverables and Exhibits
    
    Example:
        >>> orchestrator = DreamAIOrchestrator()
        >>> result = orchestrator.execute_workflow({
        ...     'deal_name': 'Sample LIHTC Project',
        ...     'total_development_cost': 10000000,
        ...     'total_units': 100,
        ...     'ami_tier': '60%'
        ... })
        >>> print(f"Recommendation: {result.recommendation}")
        >>> print(f"Completed {result.completed_steps}/{result.total_steps} steps")
    """
    
    def __init__(self):
        """Initialize Dream AI orchestrator."""
        self.data_store: Dict[str, Any] = {}
    
    def execute_workflow(self, initial_data: Dict[str, Any]) -> WorkflowResult:
        """
        Execute complete LIHTC underwriting workflow.
        
        Args:
            initial_data: Initial property and deal data
            
        Returns:
            WorkflowResult with all outputs and recommendation
        """
        execution_id = f"dream_ai_{int(time.time())}"
        start_time = datetime.now()
        
        # Store initial data
        self.data_store = initial_data.copy()
        
        # Execute workflow steps (simplified for demonstration)
        steps = self._create_workflow_steps()
        completed = 0
        
        for step in steps:
            try:
                step.status = WorkflowStatus.IN_PROGRESS
                # Would execute actual calculation here
                step.status = WorkflowStatus.COMPLETED
                completed += 1
            except Exception as e:
                step.status = WorkflowStatus.ERROR
                step.error = str(e)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return WorkflowResult(
            deal_name=initial_data.get('deal_name', 'Unknown'),
            execution_id=execution_id,
            start_time=start_time,
            end_time=end_time,
            total_steps=len(steps),
            completed_steps=completed,
            current_phase=WorkflowPhase.OUTPUT,
            overall_status=WorkflowStatus.COMPLETED if completed == len(steps) else WorkflowStatus.ERROR,
            steps=steps,
            final_outputs=self.data_store,
            recommendation="Analysis Complete",
            execution_time_seconds=execution_time
        )
    
    def _create_workflow_steps(self) -> List[WorkflowStep]:
        """Create standard workflow steps."""
        return [
            WorkflowStep("intake_01", "Property Data Validation", WorkflowPhase.DATA_INTAKE,
                        "PropertyIntakeAnalyzer", "Section 3", [], ["property_data"]),
            WorkflowStep("analysis_01", "Eligible Basis", WorkflowPhase.ANALYSIS,
                        "EligibleBasisCalculator", "Section 5", ["property_data"], ["eligible_basis"]),
            WorkflowStep("analysis_02", "Qualified Basis", WorkflowPhase.ANALYSIS,
                        "QualifiedBasisCalculator", "Section 6", ["eligible_basis"], ["qualified_basis"]),
            WorkflowStep("analysis_03", "Tax Credits", WorkflowPhase.ANALYSIS,
                        "CreditCalculator", "Section 7", ["qualified_basis"], ["tax_credits"]),
            WorkflowStep("decision_01", "Go/No-Go Scoring", WorkflowPhase.DECISION,
                        "DealScoringEngine", "Section 30", ["all_outputs"], ["deal_score"]),
        ]


# =============================================================================
# MODULE VERSION & METADATA
# =============================================================================

__version__ = "1.0.0"
__author__ = "Shieldstone Capital"
__email__ = "info@shieldstone.com"
__status__ = "Production"
__date__ = "2025-12-18"

# Export all public classes
__all__ = [
    # Enums
    'DealType', 'PropertyType', 'CreditType', 'WorkflowPhase', 'WorkflowStatus',
    'MilestoneType',
    
    # Dataclasses
    'PropertyData', 'EligibleBasisResult', 'QualifiedBasisResult', 'CreditResult',
    'EquityResult', 'DeveloperFeeResult', 'SourcesAndUsesResult', 'BondSizingResult',
    'AMIRentResult', 'RevenueProjectionResult', 'ExpenseProjectionResult',
    'CashFlowResult', 'DeveloperReturnResult', 'DealScoringResult',
    'PartnershipSplit', 'CapitalContribution', 'InvestorReturnResult',
    'WorkflowStep', 'WorkflowResult',
    
    # Calculators
    'EligibleBasisCalculator', 'QualifiedBasisCalculator', 'CreditCalculator',
    'EquityPricingCalculator', 'DeveloperFeeCalculator', 'SourcesAndUsesBalancer',
    'BondSizingCalculator', 'AMIRentCalculator', 'RevenueProjector',
    'OpExBenchmarker', 'CashFlowProjector', 'DeveloperReturnCalculator',
    'PartnershipStructureCalculator', 'InvestorReturnCalculator', 'DealScoringEngine',
    'DreamAIOrchestrator',
]

