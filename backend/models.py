"""
Pydantic models for EFB Underwriting Mini-App API.
All input/output schemas for FastAPI endpoints.
Updated to match Excel model assumptions (V2).
"""

from __future__ import annotations
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ============================================================================
# UNIT MIX
# ============================================================================

class UnitType(BaseModel):
    unit_type: str = Field(default="1BR/1BA", description="Unit type label")
    beds: int = Field(default=1, ge=0, le=5)
    baths: float = Field(default=1.0, ge=0.5, le=4.0)
    count: int = Field(default=1, ge=1)
    current_rent: float = Field(default=1200.0, ge=0)
    market_rent: float = Field(default=1300.0, ge=0)
    sqft: float = Field(default=750.0, ge=100)


# ============================================================================
# DEAL INPUTS
# ============================================================================

class PropertyInputs(BaseModel):
    property_name: str = Field(default="New Deal")
    address: str = Field(default="")
    city: str = Field(default="")
    state: str = Field(default="FL")
    total_units: int = Field(default=186, ge=1)
    rentable_sf: float = Field(default=210886.0, ge=0)
    year_built: int = Field(default=2008, ge=1900, le=2030)
    purchase_price: float = Field(default=36500000.0, ge=0)
    asking_price: float = Field(default=39000000.0, ge=0)
    unit_mix: List[UnitType] = Field(default_factory=list)
    # REMOVED: market_tier — not used in any calculation


class RevenueInputs(BaseModel):
    vacancy_yr1: float = Field(default=0.10, ge=0, le=1.0)
    vacancy_stable: float = Field(default=0.07, ge=0, le=1.0)
    other_income_per_unit_yr: float = Field(default=75.0, ge=0)
    revenue_growth: float = Field(default=0.030, ge=0, le=0.20, description="Single annual revenue growth rate")
    # REMOVED: loss_to_lease_pct, concessions_yr1, concessions_stable,
    #          bad_debt_monthly, revenue_growth_yr2, revenue_growth_stable, other_income_annual


class ExpenseInputs(BaseModel):
    payroll_per_unit: float = Field(default=1864.0, ge=0)
    general_admin_per_unit: float = Field(default=237.0, ge=0)
    marketing_per_unit: float = Field(default=219.0, ge=0)
    turnover_per_unit: float = Field(default=167.0, ge=0)
    rm_per_unit: float = Field(default=327.0, ge=0)
    contract_services_per_unit: float = Field(default=1456.0, ge=0)
    utilities_per_unit: float = Field(default=1135.0, ge=0)
    utility_reimbursements_per_unit: float = Field(
        default=851.0, ge=0,
        description="Stored positive; subtracted from expenses (or added to revenue) in calculation"
    )
    insurance_per_unit: float = Field(default=1084.0, ge=0)
    capital_expense_reserves_per_unit: float = Field(default=300.0, ge=0)
    mgmt_fee_pct: float = Field(default=0.03, ge=0, le=0.20)
    expense_growth: float = Field(default=0.030, ge=0, le=0.15)
    # REMOVED: admin_per_unit (renamed to general_admin_per_unit)
    # REMOVED: replacement_reserve_per_unit_yr (moved here as capital_expense_reserves_per_unit)


class GeneralPartnerInputs(BaseModel):
    acquisition_fee_pct: float = Field(
        default=0.10, ge=0, le=0.20,
        description="% of purchase price"
    )
    asset_mgmt_fee_pct: float = Field(
        default=0.005, ge=0, le=0.05,
        description="% of EGI annually — appears below NOI line"
    )
    disposition_fee_pct: float = Field(
        default=0.00, ge=0, le=0.10,
        description="% of sale price at exit"
    )
    construction_mgmt_pct: float = Field(
        default=0.00, ge=0, le=0.10,
        description="% of capital budget"
    )
    other_closing_costs_pct: float = Field(default=0.00, ge=0, le=1.0)


class CapitalInputs(BaseModel):
    capital_budget: float = Field(default=1257000.0, ge=0, description="Total renovation/capital budget")
    capital_reserve_amount: float = Field(default=750000.0, ge=0)
    renovation_start_year: int = Field(default=1, ge=1, le=10)
    renovation_end_year: int = Field(default=2, ge=1, le=10)
    use_capital_budget_reserves: bool = Field(
        default=False,
        description="Fund construction from reserves (set aside at closing) instead of operating cash flow"
    )


class BondInputs(BaseModel):
    loan_amount: float = Field(
        default=42500000.0, ge=0,
        description="Absolute A Bond loan amount in $"
    )
    io_period_years: float = Field(default=1.0, ge=0, le=10, description="IO period in years")
    loan_term_years: int = Field(default=10, ge=1, le=40)
    amortization_years: int = Field(default=30, ge=1, le=40)
    a_bond_rate: float = Field(default=0.048, ge=0, le=0.20)
    origination_pct: float = Field(default=0.0125, ge=0, le=0.05)
    financial_advisory_pct: float = Field(default=0.005, ge=0, le=0.05)
    exit_fee_pct: float = Field(default=0.00, ge=0, le=0.10)
    b_note_amount: float = Field(default=0.0, ge=0, description="Absolute B Note dollar amount")
    b_note_loan_type: str = Field(default="Junior Debt")
    b_note_refi_valuation: float = Field(default=0.0, ge=0)
    b_note_origination_year: int = Field(default=2, ge=1, le=15)
    b_note_io_period_year: int = Field(default=3, ge=1, le=15)
    b_note_origination_fees_pct: float = Field(default=0.00, ge=0, le=1.0)
    b_note_interest_rate_current: float = Field(default=0.00, ge=0, le=1.0)
    b_note_interest_rate_accrued: float = Field(default=0.00, ge=0, le=1.0)
    b_note_loan_maturity_year: int = Field(default=5, ge=1, le=15)
    b_note_exit_fees_pct: float = Field(default=0.00, ge=0, le=1.0)
    b_note_amortization_years: int = Field(default=30, ge=1, le=40)
    # REMOVED: b_note_rate (replaced by b_note_interest_rate_current and b_note_interest_rate_accrued)
    # REMOVED: a_bond_pct, b_bond_pct, b_bond_yield, io_period_months, turbo_pct


class ClosingCostInputs(BaseModel):
    gp_bond_counsel: float = Field(default=165000.0, ge=0)
    lenders_counsel: float = Field(default=0.0, ge=0)
    cost_of_issuance: float = Field(default=231000.0, ge=0)
    # Cost of Issuance Assumptions (sub-fields)
    financial_advisor_issuance: float = Field(default=60000.0, ge=0)
    bond_counsel_coi: float = Field(default=75000.0, ge=0)
    underwriter_counsel: float = Field(default=75000.0, ge=0)
    trustee: float = Field(default=8500.0, ge=0)
    trustee_counsel: float = Field(default=7500.0, ge=0)
    other_bond_closing_costs: float = Field(default=5000.0, ge=0)
    transfer_recordation: float = Field(default=50000.0, ge=0)
    title: float = Field(default=50000.0, ge=0)
    property_condition_report: float = Field(default=3000.0, ge=0)
    file_inspection: float = Field(default=5120.0, ge=0)
    environmental: float = Field(default=2500.0, ge=0)
    survey: float = Field(default=5250.0, ge=0)
    appraisal: float = Field(default=5500.0, ge=0)
    market_study: float = Field(default=4900.0, ge=0)
    capital_reserve: float = Field(default=750000.0, ge=0)
    insurance_escrow: float = Field(default=100000.0, ge=0)
    soft_cost_cushion: float = Field(default=50000.0, ge=0)
    working_capital: float = Field(default=60000.0, ge=0)
    replacement_reserves_capitalized: float = Field(default=0.0, ge=0)
    enhancements_and_reserves: float = Field(default=0.0, ge=0)


class PropertyTaxInputs(BaseModel):
    efb_exempt: bool = Field(default=True)
    pilot_annual: float = Field(default=0.0, ge=0, description="PILOT payment if not fully exempt")
    property_tax_rate: float = Field(
        default=0.0161841, ge=0, le=0.10,
        description="Actual tax rate as decimal, e.g. 0.016"
    )
    current_assessed_value: float = Field(default=29190966.0, ge=0)
    assessment_ratio: float = Field(default=0.80, ge=0, le=1.0)
    non_ad_valorem_taxes: float = Field(default=0.0, ge=0)
    reassessed_upon_acquisition: bool = Field(default=True)
    pct_taxes_exempt: float = Field(
        default=1.00, ge=0, le=1.0,
        description="Fraction of taxes exempt under EFB (1.0 = fully exempt)"
    )
    reassessed_upon_sale: bool = Field(default=False)
    ad_valorem_tax_growth_rate: float = Field(default=0.03, ge=0, le=0.20)
    non_ad_valorem_growth_rate: float = Field(default=0.00, ge=0, le=0.20)
    # REMOVED: tax_assessment_ratio (renamed to assessment_ratio)
    # REMOVED: tax_mill_rate (replaced by property_tax_rate)
    # REMOVED: fire_rescue_annual (replaced by non_ad_valorem_taxes)


class ExitInputs(BaseModel):
    hold_period: int = Field(default=10, ge=1, le=30)
    exit_cap_rate: float = Field(default=0.09, ge=0, le=0.20, description="Direct exit cap rate input")
    sale_transaction_cost: float = Field(default=0.020, ge=0, le=0.10)
    exit_to_conventional_buyer: bool = Field(default=False)
    # REMOVED: five_yr_treasury, comp_price_per_unit, strategy_spread, override_exit_cap
    #          (no more three-method triangulation — just use exit_cap_rate directly)


class WaterfallInputs(BaseModel):
    lp_preferred_return: float = Field(default=0.08, ge=0, le=0.25)
    lp_equity_split_to_hurdle: float = Field(default=0.70, ge=0, le=1.0)
    irr_hurdle: float = Field(default=0.15, ge=0, le=0.50)
    lp_residual_split: float = Field(default=0.50, ge=0, le=1.0)


class DealInputs(BaseModel):
    property: PropertyInputs = Field(default_factory=PropertyInputs)
    revenue: RevenueInputs = Field(default_factory=RevenueInputs)
    expenses: ExpenseInputs = Field(default_factory=ExpenseInputs)
    general_partner: GeneralPartnerInputs = Field(default_factory=GeneralPartnerInputs)
    capital: CapitalInputs = Field(default_factory=CapitalInputs)
    closing_costs: ClosingCostInputs = Field(default_factory=ClosingCostInputs)
    bonds: BondInputs = Field(default_factory=BondInputs)
    property_tax: PropertyTaxInputs = Field(default_factory=PropertyTaxInputs)
    exit: ExitInputs = Field(default_factory=ExitInputs)
    waterfall: WaterfallInputs = Field(default_factory=WaterfallInputs)


# ============================================================================
# UNDERWRITE RESPONSE
# ============================================================================

class ProFormaYear(BaseModel):
    year: int
    gpr: float
    vacancy: float
    net_rental_revenue: float
    other_income: float
    utility_reimbursements: float = 0.0
    egi: float
    # Expense detail
    payroll: float
    general_admin: float = 0.0
    marketing: float = 0.0
    turnover: float
    rm_services: float
    contract_services: float = 0.0
    utilities: float
    insurance: float
    capital_expense_reserves: float = 0.0
    mgmt_fee: float
    re_taxes: float
    total_opex: float
    noi: float
    # Below NOI
    asset_mgmt_fee: float = 0.0
    capital_improvements: float = 0.0
    construction_mgmt_fee: float = Field(default=0.0)
    capital_budget_reserves_spent: float = 0.0
    cf_before_ds: float
    # Debt service
    a_bond_interest: float
    a_bond_principal_scheduled: float = 0.0
    b_bond_interest: float = 0.0
    net_cash_flow: float
    distributable_cf: float
    dscr: float
    a_bond_balance: float
    # Legacy fields kept as optional with defaults so old callers don't break
    loss_to_lease: float = 0.0
    concessions: float = 0.0
    bad_debt: float = 0.0
    admin: float = 0.0
    replacement_reserves: float = 0.0
    turbo_principal: float = 0.0


class SourcesUses(BaseModel):
    loan_amount: float
    b_note_amount: float
    lp_equity: float
    total_sources: float
    purchase_price: float
    acquisition_fee: float
    gp_bond_counsel: float
    lenders_counsel: float
    cost_of_issuance: float
    transfer_recordation: float
    title: float
    property_condition_report: float
    file_inspection: float
    environmental: float
    survey: float
    appraisal: float
    market_study: float
    capital_reserve: float
    insurance_escrow: float
    soft_cost_cushion: float
    working_capital: float
    replacement_reserves_capitalized: float
    enhancements_and_reserves: float = 0.0
    other_closing_costs: float = 0.0
    financial_advisor_issuance: float = 0.0
    bond_counsel_coi: float = 0.0
    underwriter_counsel: float = 0.0
    trustee: float = 0.0
    trustee_counsel: float = 0.0
    other_bond_closing_costs: float = 0.0
    capital_budget_reserves_account: float = 0.0
    total_closing_costs: float
    total_uses: float
    ltv: float


class ExitAnalysis(BaseModel):
    hold_year: int
    exit_noi: float
    method1_cap: float
    method2_cap: float
    method3_cap: float
    exit_cap_used: float
    exit_cap_method: str
    sale_price: float
    price_per_unit: float
    outstanding_bonds: float
    sale_costs: float
    net_proceeds: float
    going_in_cap: float


class ReturnsSummary(BaseModel):
    property_irr: Optional[float]
    equity_multiple: float
    coc_yr1: float
    net_proceeds: float
    equity_invested: float
    irr_formatted: str
    em_formatted: str
    coc_formatted: str
    hurdle_irr: float
    passes_irr: bool
    passes_em: bool


class EFBTaxAdvantage(BaseModel):
    efb_annual_tax: float
    conventional_annual_tax: float
    annual_savings: float
    cumulative_savings: float
    yr1_dscr_conventional: float
    yr1_dscr_efb: float


class SensitivityGrid(BaseModel):
    a_bond_rates: List[float]
    exit_caps: List[float]
    dscr_grid: List[List[float]]


class UnderwriteResponse(BaseModel):
    sources_uses: SourcesUses
    pro_forma: List[ProFormaYear]
    exit_analysis: ExitAnalysis
    returns: ReturnsSummary
    tax_advantage: EFBTaxAdvantage
    sensitivity: SensitivityGrid
    yr1_dscr: float
    yr1_noi: float
    going_in_cap: float
    price_per_unit: float


# ============================================================================
# VALIDATION RESPONSE
# ============================================================================

class ValidationFlag(BaseModel):
    field: str
    section: str
    status: str  # GREEN | AMBER | RED
    message: str
    manual_ref: str
    current_value: Any
    benchmark: str


class ValidationResponse(BaseModel):
    flags: List[ValidationFlag]
    total: int
    green_count: int
    amber_count: int
    red_count: int
    pass_fail: str  # PASS | REVIEW | FAIL


# ============================================================================
# INTAKE RESPONSE
# ============================================================================

class IntakeResponse(BaseModel):
    doc_type: str
    confidence: float
    detection_method: str
    prefill_map: dict
    warnings: List[str]
    fields_filled_count: int
    # Raw extracted document text (bounded upstream at ~50K chars) so the client can carry it
    # into the jobs pipeline as deal_docs. Additive with a default — existing consumers unaffected.
    extracted_text: str = ""


# ============================================================================
# AGENT REQUESTS
# ============================================================================

class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class AgentChatRequest(BaseModel):
    mode: str = Field(description="onboarding|validation|free")
    messages: List[ChatMessage]
    current_inputs: Optional[DealInputs] = None
    model_results: Optional[dict] = None
    validation_flags: Optional[List[ValidationFlag]] = None


class MemoRequest(BaseModel):
    inputs: DealInputs
    model_results: dict
