"""
EFB Calculation Engine — Shieldstone Underwriting Mini-App
Matches the Excel EFB Acquisition Sizing Tool assumptions (V2).
Bond sizing uses absolute dollar amounts; no turbo amortization; direct exit cap input.
"""

from __future__ import annotations

from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Default input values — Esplanade at Tradition actuals
# ---------------------------------------------------------------------------

DEFAULTS: dict[str, Any] = {
    "purchase_price": 36_500_000,
    "total_units": 186,
    "unit_count": 186,
    "rentable_sf": 210_886,
    # Bond / debt
    "loan_amount": 42_500_000,
    "b_note_amount": 0.0,
    "b_note_loan_type": "Junior Debt",
    "b_note_refi_valuation": 0.0,
    "b_note_origination_year": 2,
    "b_note_io_period_year": 3,
    "b_note_origination_fees_pct": 0.00,
    "b_note_interest_rate_current": 0.00,
    "b_note_interest_rate_accrued": 0.00,
    "b_note_loan_maturity_year": 5,
    "b_note_exit_fees_pct": 0.00,
    "b_note_amortization_years": 30,
    "a_bond_rate": 0.048,
    "io_period_years": 1.0,
    "io_period_months": 12,
    "loan_term_years": 10,
    "amortization_years": 30,
    "origination_pct": 0.0125,
    "financial_advisory_pct": 0.005,
    "exit_fee_pct": 0.0,
    # Property tax
    "efb_exempt": True,
    "property_tax_rate": 0.0161841,
    "current_assessed_value": 29_190_966,
    "assessment_ratio": 0.80,
    "non_ad_valorem_taxes": 0.0,
    "reassessed_upon_acquisition": True,
    "reassessed_upon_sale": False,
    "pct_taxes_exempt": 1.0,
    "pilot_annual": 0.0,
    "ad_valorem_tax_growth_rate": 0.03,
    "non_ad_valorem_growth_rate": 0.00,
    # Exit
    "hold_period": 10,
    "exit_cap_rate": 0.09,
    "sale_transaction_cost": 0.02,
    "exit_to_conventional_buyer": False,
    # Revenue
    "revenue_growth": 0.030,
    "vacancy_yr1": 0.10,
    "vacancy_stable": 0.07,
    "other_income_per_unit_yr": 75.0,
    # Expenses
    "expense_growth": 0.030,
    "mgmt_fee_pct": 0.03,
    # GP fees
    "acquisition_fee_pct": 0.10,
    "asset_mgmt_fee_pct": 0.005,
    "disposition_fee_pct": 0.00,
    "construction_mgmt_pct": 0.00,
    "other_closing_costs_pct": 0.00,
    # Capital
    "capital_budget": 1_257_000,
    "capital_reserve_amount": 750_000,
    "renovation_start_year": 1,
    "renovation_end_year": 2,
    # Per-unit expense defaults (Esplanade actuals)
    "payroll_per_unit": 1_864,
    "general_admin_per_unit": 237,
    "marketing_per_unit": 219,
    "turnover_per_unit": 167,
    "rm_per_unit": 327,
    "contract_services_per_unit": 1_456,
    "utilities_per_unit": 1_135,
    "utility_reimbursements_per_unit": 851,
    "insurance_per_unit": 1_084,
    "capital_expense_reserves_per_unit": 300,
    # Year-1 expense totals (computed from per-unit × units; override in flatten_inputs)
    "payroll_yr1": 346_704,
    "general_admin_yr1": 44_082,
    "marketing_yr1": 40_734,
    "turnover_yr1": 31_062,
    "rm_services_yr1": 60_822,
    "contract_services_yr1": 270_816,
    "utilities_yr1": 211_110,
    "utility_reimbursements_yr1": 158_286,
    "insurance_yr1": 201_624,
    # Closing cost direct dollar amounts
    "gp_bond_counsel": 165_000,
    "lenders_counsel": 0,
    "cost_of_issuance": 231_000,
    "transfer_recordation": 50_000,
    "title": 50_000,
    "property_condition_report": 3_000,
    "file_inspection": 5_120,
    "environmental": 2_500,
    "survey": 5_250,
    "appraisal": 5_500,
    "market_study": 4_900,
    "capital_reserve": 750_000,
    "insurance_escrow": 100_000,
    "soft_cost_cushion": 50_000,
    "working_capital": 60_000,
    "replacement_reserves_capitalized": 0,
    "enhancements_and_reserves": 0,
    "financial_advisor_issuance": 60_000,
    "bond_counsel_coi": 75_000,
    "underwriter_counsel": 75_000,
    "trustee": 8_500,
    "trustee_counsel": 7_500,
    "other_bond_closing_costs": 5_000,
    # Fallback GPR if no unit mix supplied
    "gpr_yr1": 3_000_000,
}


def _merge_defaults(inputs: dict) -> dict:
    """Return a copy of DEFAULTS updated with caller-supplied inputs."""
    merged = dict(DEFAULTS)
    merged.update(inputs)
    return merged


# ---------------------------------------------------------------------------
# 1. Sources and Uses
# ---------------------------------------------------------------------------

def compute_sources_and_uses(inputs: dict) -> dict:
    """
    Compute the full sources-and-uses table for an EFB acquisition.

    Uses absolute dollar amounts for loan_amount and all closing costs.
    Origination fee and financial advisory fee are derived from loan_amount.
    Equity fills the gap between total uses and bond proceeds.

    Returns
    -------
    dict with keys: loan_amount, b_note_amount, lp_equity, total_sources,
        closing_costs (dict), total_closing_costs, total_uses, ltv,
        sources_uses_gap
    """
    i = _merge_defaults(inputs)

    purchase_price: float = float(i["purchase_price"])
    loan_amount: float = float(i["loan_amount"])
    b_note_amount: float = float(i["b_note_amount"])

    # Fees derived from loan amount
    origination_fee: float = loan_amount * float(i["origination_pct"])
    financial_advisory_fee: float = loan_amount * float(i["financial_advisory_pct"])

    # Acquisition fee derived from purchase price
    acquisition_fee: float = purchase_price * float(i["acquisition_fee_pct"])

    # Direct dollar closing costs from inputs
    gp_bond_counsel: float = float(i["gp_bond_counsel"])
    lenders_counsel: float = float(i["lenders_counsel"])
    cost_of_issuance: float = float(i["cost_of_issuance"])
    transfer_recordation: float = float(i["transfer_recordation"])
    title: float = float(i["title"])
    property_condition_report: float = float(i["property_condition_report"])
    file_inspection: float = float(i["file_inspection"])
    environmental: float = float(i["environmental"])
    survey: float = float(i["survey"])
    appraisal: float = float(i["appraisal"])
    market_study: float = float(i["market_study"])
    capital_reserve: float = float(i["capital_reserve"])
    insurance_escrow: float = float(i["insurance_escrow"])
    soft_cost_cushion: float = float(i["soft_cost_cushion"])
    working_capital: float = float(i["working_capital"])
    replacement_reserves_capitalized: float = float(i["replacement_reserves_capitalized"])
    enhancements_and_reserves: float = float(i.get("enhancements_and_reserves", 0.0))

    # Capital Budget Reserves: if toggle is on, set aside full capital budget at closing
    use_capital_budget_reserves: bool = bool(i.get("use_capital_budget_reserves", False))
    capital_budget_reserves_account: float = float(i.get("capital_budget", 0.0)) if use_capital_budget_reserves else 0.0

    # Other closing costs from GP fee % of purchase price
    other_closing_costs_pct: float = float(i.get("other_closing_costs_pct", 0.0))
    other_closing_costs: float = purchase_price * other_closing_costs_pct

    # Cost of Issuance Assumptions (sub-fields)
    financial_advisor_issuance: float = float(i.get("financial_advisor_issuance", 60000.0))
    bond_counsel_coi: float = float(i.get("bond_counsel_coi", 75000.0))
    underwriter_counsel: float = float(i.get("underwriter_counsel", 75000.0))
    trustee: float = float(i.get("trustee", 8500.0))
    trustee_counsel: float = float(i.get("trustee_counsel", 7500.0))
    other_bond_closing_costs: float = float(i.get("other_bond_closing_costs", 5000.0))

    closing_costs = {
        "origination_fee": origination_fee,
        "financial_advisory_fee": financial_advisory_fee,
        "acquisition_fee": acquisition_fee,
        "gp_bond_counsel": gp_bond_counsel,
        "lenders_counsel": lenders_counsel,
        "cost_of_issuance": cost_of_issuance,
        "transfer_recordation": transfer_recordation,
        "title": title,
        "property_condition_report": property_condition_report,
        "file_inspection": file_inspection,
        "environmental": environmental,
        "survey": survey,
        "appraisal": appraisal,
        "market_study": market_study,
        "capital_reserve": capital_reserve,
        "insurance_escrow": insurance_escrow,
        "soft_cost_cushion": soft_cost_cushion,
        "working_capital": working_capital,
        "replacement_reserves_capitalized": replacement_reserves_capitalized,
        "enhancements_and_reserves": enhancements_and_reserves,
        "other_closing_costs": other_closing_costs,
        # Cost of Issuance sub-fields
        "financial_advisor_issuance": financial_advisor_issuance,
        "bond_counsel_coi": bond_counsel_coi,
        "underwriter_counsel": underwriter_counsel,
        "trustee": trustee,
        "trustee_counsel": trustee_counsel,
        "other_bond_closing_costs": other_bond_closing_costs,
        "capital_budget_reserves_account": capital_budget_reserves_account,
    }

    total_closing_costs = sum(closing_costs.values())
    total_uses = purchase_price + total_closing_costs

    # Sources: bonds first, equity fills the gap
    bond_proceeds = loan_amount + b_note_amount
    lp_equity = max(0.0, total_uses - bond_proceeds)
    total_sources = bond_proceeds + lp_equity

    ltv = bond_proceeds / purchase_price if purchase_price > 0 else 0.0

    return {
        "loan_amount": loan_amount,
        "b_note_amount": b_note_amount,
        "closing_costs": closing_costs,
        "total_closing_costs": total_closing_costs,
        "total_uses": total_uses,
        "bond_proceeds": bond_proceeds,
        "lp_equity": lp_equity,
        "total_sources": total_sources,
        "sources_uses_gap": total_sources - total_uses,
        "ltv": ltv,
    }


# ---------------------------------------------------------------------------
# 2. Property Tax Helper
# ---------------------------------------------------------------------------

def _property_tax(inputs: dict, year: int = 1) -> float:
    """
    Return annual property tax based on EFB exemption status.

    If efb_exempt: return pilot_annual (default $0).
    Else: compute from assessed value × property_tax_rate, apply pct_taxes_exempt reduction,
          then add non_ad_valorem_taxes. Assessed value grows by ad_valorem_tax_growth_rate
          year-over-year; non_ad_valorem grows by non_ad_valorem_growth_rate.
    """
    if inputs.get("efb_exempt", True):
        return float(inputs.get("pilot_annual", 0.0))

    purchase_price: float = float(inputs["purchase_price"])
    property_tax_rate: float = float(inputs.get("property_tax_rate", 0.0161841))
    assessment_ratio: float = float(inputs.get("assessment_ratio", 0.80))
    non_ad_valorem: float = float(inputs.get("non_ad_valorem_taxes", 0.0))
    pct_exempt: float = float(inputs.get("pct_taxes_exempt", 0.0))
    reassessed: bool = bool(inputs.get("reassessed_upon_acquisition", True))
    ad_valorem_growth: float = float(inputs.get("ad_valorem_tax_growth_rate", 0.03))
    non_ad_valorem_growth: float = float(inputs.get("non_ad_valorem_growth_rate", 0.00))

    if reassessed:
        assessed_value = purchase_price * assessment_ratio
    else:
        assessed_value = float(inputs.get("current_assessed_value", purchase_price)) * assessment_ratio

    # Apply year-over-year growth (year 1 = base, year 2 = base * (1+g), etc.)
    assessed_value = assessed_value * (1.0 + ad_valorem_growth) ** (year - 1)
    non_ad_valorem_yr = non_ad_valorem * (1.0 + non_ad_valorem_growth) ** (year - 1)

    ad_valorem_tax = assessed_value * property_tax_rate
    effective_tax = ad_valorem_tax * (1.0 - pct_exempt) + non_ad_valorem_yr

    return max(0.0, effective_tax)


# ---------------------------------------------------------------------------
# 3. Amortization Helper
# ---------------------------------------------------------------------------

def _monthly_payment(principal: float, annual_rate: float, amort_years: int) -> float:
    """Standard level-payment mortgage monthly payment."""
    r = annual_rate / 12.0
    n = amort_years * 12
    if r == 0.0:
        return principal / n if n > 0 else 0.0
    return principal * r / (1.0 - (1.0 + r) ** (-n))


# ---------------------------------------------------------------------------
# 4. Pro Forma (20-year)
# ---------------------------------------------------------------------------

def compute_pro_forma(inputs: dict) -> list[dict]:
    """
    Compute 20-year annual pro forma matching the Excel model structure.

    Revenue: GPR → Vacancy → Net Rental Revenue → + Other Income
             → + Utility Reimbursements → EGI
    Expenses: per-unit categories × units + mgmt fee % EGI + RE taxes
    NOI = EGI - Total OpEx
    Below NOI: Asset Mgmt Fee + Capital Improvements → CF Before Debt Service
    Debt Service: IO period then standard amortization (no turbo)
    DSCR = NOI / (interest + scheduled principal)

    Returns
    -------
    list[dict] — one dict per year (years 1–20)
    """
    i = _merge_defaults(inputs)

    # ---- Capital structure ----
    sou = compute_sources_and_uses(i)
    a_bond_balance: float = sou["loan_amount"]
    a_bond_rate: float = float(i["a_bond_rate"])
    io_months: int = int(round(float(i.get("io_period_months", float(i.get("io_period_years", 1.0)) * 12))))
    loan_term_years: int = int(i["loan_term_years"])
    amortization_years: int = int(i["amortization_years"])

    b_note_balance: float = sou["b_note_amount"]
    b_note_rate: float = float(i.get("b_note_interest_rate_current", i.get("b_note_rate", 0.0)))

    # ---- Unit count ----
    unit_count: int = int(i.get("unit_count", i.get("total_units", 1)))

    # ---- GP fees ----
    asset_mgmt_fee_pct: float = float(i.get("asset_mgmt_fee_pct", 0.005))
    construction_mgmt_pct: float = float(i.get("construction_mgmt_pct", 0.00))

    # ---- Capital improvements: spread across renovation_start_year to renovation_end_year ----
    capital_budget: float = float(i.get("capital_budget", 0.0))
    renovation_start_year: int = int(i.get("renovation_start_year", 1))
    renovation_end_year: int = int(i.get("renovation_end_year", 2))
    renovation_span = max(1, renovation_end_year - renovation_start_year + 1)
    use_capital_budget_reserves: bool = bool(i.get("use_capital_budget_reserves", False))
    capex_per_reno_year = capital_budget / renovation_span

    # ---- Revenue base ----
    gpr_yr1: float = float(i.get("gpr_yr1", 0.0))
    other_income_per_unit_yr: float = float(i.get("other_income_per_unit_yr", 75.0))
    utility_reimbursements_per_unit: float = float(i.get("utility_reimbursements_per_unit", 0.0))

    # ---- Vacancy rates ----
    vacancy_yr1: float = float(i["vacancy_yr1"])
    vacancy_stable: float = float(i["vacancy_stable"])

    # ---- Growth rates ----
    rev_growth: float = float(i.get("revenue_growth", 0.030))
    exp_growth: float = float(i["expense_growth"])
    mgmt_fee_pct: float = float(i["mgmt_fee_pct"])

    # ---- Year-1 expense totals ----
    payroll_yr1: float = float(i.get("payroll_yr1", float(i.get("payroll_per_unit", 1864)) * unit_count))
    general_admin_yr1: float = float(i.get("general_admin_yr1", float(i.get("general_admin_per_unit", 237)) * unit_count))
    marketing_yr1: float = float(i.get("marketing_yr1", float(i.get("marketing_per_unit", 219)) * unit_count))
    turnover_yr1: float = float(i.get("turnover_yr1", float(i.get("turnover_per_unit", 167)) * unit_count))
    rm_services_yr1: float = float(i.get("rm_services_yr1", float(i.get("rm_per_unit", 327)) * unit_count))
    contract_services_yr1: float = float(i.get("contract_services_yr1", float(i.get("contract_services_per_unit", 1456)) * unit_count))
    utilities_yr1: float = float(i.get("utilities_yr1", float(i.get("utilities_per_unit", 1135)) * unit_count))
    insurance_yr1: float = float(i.get("insurance_yr1", float(i.get("insurance_per_unit", 1084)) * unit_count))
    capital_expense_reserves_yr1: float = float(i.get("capital_expense_reserves_per_unit", 300)) * unit_count

    # Utility reimbursements grow at expense_growth (offsets gross utility expense)
    utility_reimbursements_yr1: float = float(i.get(
        "utility_reimbursements_yr1",
        utility_reimbursements_per_unit * unit_count
    ))

    rows: list[dict] = []

    for yr in range(1, 21):
        # ---- Revenue ----
        if yr == 1:
            gpr = gpr_yr1
            vacancy_rate = vacancy_yr1
            other_income = other_income_per_unit_yr * unit_count
            utility_reimbursements = utility_reimbursements_yr1
        else:
            prev = rows[-1]
            gpr = prev["gpr"] * (1.0 + rev_growth)
            vacancy_rate = vacancy_stable
            other_income = prev["other_income"] * (1.0 + rev_growth)
            utility_reimbursements = prev["utility_reimbursements"] * (1.0 + exp_growth)

        vacancy = gpr * vacancy_rate
        net_rental_revenue = gpr - vacancy

        # EGI includes net rental revenue + other income + utility reimbursements
        egi = net_rental_revenue + other_income + utility_reimbursements

        # ---- Expenses ----
        if yr == 1:
            payroll = payroll_yr1
            general_admin = general_admin_yr1
            marketing = marketing_yr1
            turnover = turnover_yr1
            rm_services = rm_services_yr1
            contract_services = contract_services_yr1
            utilities = utilities_yr1
            insurance = insurance_yr1
            capital_expense_reserves = capital_expense_reserves_yr1
        else:
            prev = rows[-1]
            growth = 1.0 + exp_growth
            payroll = prev["payroll"] * growth
            general_admin = prev["general_admin"] * growth
            marketing = prev["marketing"] * growth
            turnover = prev["turnover"] * growth
            rm_services = prev["rm_services"] * growth
            contract_services = prev["contract_services"] * growth
            utilities = prev["utilities"] * growth
            insurance = prev["insurance"] * growth
            capital_expense_reserves = prev["capital_expense_reserves"] * growth

        mgmt_fee = egi * mgmt_fee_pct

        # ---- Property tax (with year-over-year growth) ----
        re_taxes = _property_tax(i, year=yr)

        total_opex = (
            payroll
            + general_admin
            + marketing
            + turnover
            + rm_services
            + contract_services
            + utilities
            + insurance
            + capital_expense_reserves
            + mgmt_fee
            + re_taxes
        )

        noi = egi - total_opex

        # ---- Below NOI ----
        asset_mgmt_fee = egi * asset_mgmt_fee_pct

        if renovation_start_year <= yr <= renovation_end_year:
            capital_improvements = capex_per_reno_year
        else:
            capital_improvements = 0.0

        construction_mgmt_fee = capital_improvements * construction_mgmt_pct

        # Contra: if reserves fund construction, offset capex from cash flow
        capital_budget_reserves_spent = capital_improvements if use_capital_budget_reserves else 0.0

        cf_before_ds = noi - asset_mgmt_fee - capital_improvements - construction_mgmt_fee + capital_budget_reserves_spent

        # ---- Debt service ----
        months_elapsed_start = (yr - 1) * 12
        months_elapsed_end = yr * 12

        if months_elapsed_end <= io_months:
            # Full year is IO
            a_bond_interest = a_bond_balance * a_bond_rate
            a_bond_principal_scheduled = 0.0
        elif months_elapsed_start >= io_months:
            # Full year is amortizing
            # Recalculate remaining amortization months from original amortization schedule
            remaining_amort_months = amortization_years * 12 - (months_elapsed_start - io_months)
            remaining_amort_years = max(1, remaining_amort_months // 12)
            monthly_pmt = _monthly_payment(a_bond_balance, a_bond_rate, remaining_amort_years)
            a_bond_interest = a_bond_balance * a_bond_rate
            a_bond_principal_scheduled = max(0.0, min(monthly_pmt * 12.0 - a_bond_interest, a_bond_balance))
        else:
            # Straddle year: IO transitions to amortizing mid-year
            io_months_this_year = io_months - months_elapsed_start
            amort_months_this_year = 12 - io_months_this_year

            io_interest = a_bond_balance * a_bond_rate * (io_months_this_year / 12.0)

            remaining_amort_months = amortization_years * 12
            remaining_amort_years = max(1, remaining_amort_months // 12)
            monthly_pmt = _monthly_payment(a_bond_balance, a_bond_rate, remaining_amort_years)
            amort_interest = a_bond_balance * a_bond_rate * (amort_months_this_year / 12.0)
            amort_principal = max(0.0, monthly_pmt * amort_months_this_year - amort_interest)

            a_bond_interest = io_interest + amort_interest
            a_bond_principal_scheduled = amort_principal

        # B Note: interest only (no amortization modeled)
        b_bond_interest = b_note_balance * b_note_rate

        # Net cash flow after all interest
        net_cash_flow = cf_before_ds - a_bond_interest - b_bond_interest - a_bond_principal_scheduled

        # Distributable cash flow = same as net_cash_flow (no turbo in Excel model)
        distributable_cf = net_cash_flow

        # DSCR = NOI / total annual debt service (interest + scheduled principal)
        total_ds = a_bond_interest + a_bond_principal_scheduled + b_bond_interest
        dscr = noi / total_ds if total_ds > 0 else float("inf")

        # Update A Bond balance
        a_bond_balance = max(0.0, a_bond_balance - a_bond_principal_scheduled)

        rows.append({
            "year": yr,
            "gpr": gpr,
            "vacancy": vacancy,
            "net_rental_revenue": net_rental_revenue,
            "other_income": other_income,
            "utility_reimbursements": utility_reimbursements,
            "egi": egi,
            # Expenses
            "payroll": payroll,
            "general_admin": general_admin,
            "marketing": marketing,
            "turnover": turnover,
            "rm_services": rm_services,
            "contract_services": contract_services,
            "utilities": utilities,
            "insurance": insurance,
            "capital_expense_reserves": capital_expense_reserves,
            "mgmt_fee": mgmt_fee,
            "re_taxes": re_taxes,
            "total_opex": total_opex,
            "noi": noi,
            # Below NOI
            "asset_mgmt_fee": asset_mgmt_fee,
            "capital_improvements": capital_improvements,
            "construction_mgmt_fee": construction_mgmt_fee,
            "capital_budget_reserves_spent": capital_budget_reserves_spent,
            "cf_before_ds": cf_before_ds,
            # Debt service
            "a_bond_interest": a_bond_interest,
            "a_bond_principal_scheduled": a_bond_principal_scheduled,
            "b_bond_interest": b_bond_interest,
            "net_cash_flow": net_cash_flow,
            "distributable_cf": distributable_cf,
            "dscr": dscr,
            "a_bond_balance": a_bond_balance,
            # Legacy fields with zeroed defaults for backward compatibility
            "loss_to_lease": 0.0,
            "concessions": 0.0,
            "bad_debt": 0.0,
            "admin": general_admin,  # alias
            "replacement_reserves": capital_expense_reserves,  # alias
            "turbo_principal": 0.0,
        })

    return rows


# ---------------------------------------------------------------------------
# 5. Exit Analysis
# ---------------------------------------------------------------------------

def compute_exit_analysis(inputs: dict, pro_forma: list[dict]) -> dict:
    """
    Compute exit analysis using direct exit cap rate input.

    No three-method triangulation — caller provides exit_cap_rate directly.
    If exit_to_conventional_buyer, deduct property taxes from exit NOI before
    applying cap rate (buyer prices in taxes they will now pay).

    Returns
    -------
    dict with sale price, net proceeds, outstanding bonds, and cap detail.
    """
    i = _merge_defaults(inputs)

    hold_period: int = int(i["hold_period"])
    hold_period = min(hold_period, len(pro_forma))

    exit_year_row = pro_forma[hold_period - 1]
    exit_noi: float = exit_year_row["noi"]

    # If selling to a conventional (taxable) buyer, they will owe property taxes
    # that EFB structure eliminated — buyer prices in those taxes
    if i.get("exit_to_conventional_buyer", False):
        purchase_price = float(i["purchase_price"])
        assessment_ratio = float(i.get("assessment_ratio", 0.80))
        property_tax_rate = float(i.get("property_tax_rate", 0.0161841))
        conv_tax = purchase_price * assessment_ratio * property_tax_rate
        exit_noi_for_cap = exit_noi - conv_tax
    else:
        exit_noi_for_cap = exit_noi

    # Direct exit cap rate — no triangulation
    exit_cap: float = float(i["exit_cap_rate"])

    sale_price = exit_noi_for_cap / exit_cap if exit_cap > 0 else 0.0
    sale_transaction_cost: float = float(i["sale_transaction_cost"])
    net_sale_proceeds = sale_price * (1.0 - sale_transaction_cost)

    outstanding_a_bond = exit_year_row["a_bond_balance"]
    outstanding_b_note = float(i["b_note_amount"])
    total_outstanding_bonds = outstanding_a_bond + outstanding_b_note

    net_proceeds_to_equity = net_sale_proceeds - total_outstanding_bonds

    return {
        "hold_period": hold_period,
        "exit_noi": exit_noi,
        "exit_noi_for_cap": exit_noi_for_cap,
        "exit_to_conventional_buyer": bool(i.get("exit_to_conventional_buyer", False)),
        # Stub method caps for backward compatibility with ExitAnalysis model
        "method1_cap": exit_cap,
        "method2_cap": exit_cap,
        "method3_cap": exit_cap,
        "exit_cap_rate": exit_cap,
        "exit_cap": exit_cap,
        "sale_price": sale_price,
        "sale_transaction_cost": sale_transaction_cost,
        "net_sale_proceeds": net_sale_proceeds,
        "outstanding_a_bond": outstanding_a_bond,
        "outstanding_b_bond": outstanding_b_note,
        "total_outstanding_bonds": total_outstanding_bonds,
        "net_proceeds_to_equity": net_proceeds_to_equity,
    }


# ---------------------------------------------------------------------------
# 6. Sensitivity Grid
# ---------------------------------------------------------------------------

def compute_sensitivity_grid(inputs: dict) -> dict:
    """
    Compute a DSCR sensitivity grid across A Bond rate and exit cap rate.

    A Bond rate varies ±100 bps in 25 bps increments (9 values).
    Exit cap rate varies ±50 bps in 25 bps increments (5 values).

    Returns
    -------
    dict with 'a_bond_rates', 'exit_caps', 'dscr_grid', 'noi_grid'
    """
    i = _merge_defaults(inputs)

    base_a_rate: float = float(i["a_bond_rate"])
    base_exit_cap: float = float(i["exit_cap_rate"])

    a_bond_rates = [round(base_a_rate + delta * 0.0025, 6) for delta in range(-4, 5)]
    exit_caps = [round(base_exit_cap + delta * 0.0025, 6) for delta in range(-2, 3)]

    dscr_grid: list[list[float]] = []
    noi_grid: list[list[float]] = []

    for _exit_cap in exit_caps:
        dscr_row: list[float] = []
        noi_row: list[float] = []
        for a_rate in a_bond_rates:
            scenario = dict(i)
            scenario["a_bond_rate"] = a_rate
            scenario["exit_cap_rate"] = _exit_cap
            pf = compute_pro_forma(scenario)
            yr1_dscr = pf[0]["dscr"] if pf else 0.0
            yr1_noi = pf[0]["noi"] if pf else 0.0
            dscr_row.append(round(yr1_dscr, 4))
            noi_row.append(round(yr1_noi, 2))
        dscr_grid.append(dscr_row)
        noi_grid.append(noi_row)

    return {
        "a_bond_rates": a_bond_rates,
        "exit_caps": exit_caps,
        "dscr_grid": dscr_grid,
        "noi_grid": noi_grid,
    }


# ---------------------------------------------------------------------------
# 7. EFB Tax Advantage
# ---------------------------------------------------------------------------

def compute_efb_tax_advantage(inputs: dict, pro_forma: list[dict]) -> dict:
    """
    Quantify the EFB tax exemption advantage versus a conventional acquisition.

    Conventional tax = purchase_price × assessment_ratio × property_tax_rate.
    EFB tax = 0 if efb_exempt, else same formula (partial exemption).

    Returns
    -------
    dict with efb_annual_tax, conventional_annual_tax, annual_savings,
        cumulative_savings, pv_savings, yearly_breakdown
    """
    i = _merge_defaults(inputs)

    purchase_price: float = float(i["purchase_price"])
    assessment_ratio: float = float(i.get("assessment_ratio", 0.80))
    property_tax_rate: float = float(i.get("property_tax_rate", 0.0161841))
    hold_period: int = int(i["hold_period"])
    a_bond_rate: float = float(i["a_bond_rate"])

    # EFB: use the model's actual tax calculation
    efb_annual_tax: float = _property_tax(i)

    # Conventional: purchase price × assessment ratio × property tax rate (fully taxable)
    conventional_annual_tax: float = purchase_price * assessment_ratio * property_tax_rate

    annual_savings: float = conventional_annual_tax - efb_annual_tax
    cumulative_savings: float = annual_savings * hold_period

    # PV of savings stream at A Bond rate
    if a_bond_rate > 0 and hold_period > 0:
        pv_savings = annual_savings * (1.0 - (1.0 + a_bond_rate) ** (-hold_period)) / a_bond_rate
    else:
        pv_savings = cumulative_savings

    yearly_breakdown = []
    for yr in range(1, hold_period + 1):
        pf_row = pro_forma[yr - 1] if yr <= len(pro_forma) else {}
        yearly_breakdown.append({
            "year": yr,
            "efb_re_taxes": pf_row.get("re_taxes", efb_annual_tax),
            "conventional_re_taxes": conventional_annual_tax,
            "annual_savings": conventional_annual_tax - pf_row.get("re_taxes", efb_annual_tax),
        })

    return {
        "efb_annual_tax": efb_annual_tax,
        "conventional_annual_tax": conventional_annual_tax,
        "annual_savings": annual_savings,
        "cumulative_savings": cumulative_savings,
        "pv_savings": round(pv_savings, 2),
        "yearly_breakdown": yearly_breakdown,
    }
