"""
Shieldstone EFB Underwriting — Calculations Package

Exports:
    efb_engine   — Core EFB financial model (sources/uses, pro forma, exit, sensitivity, tax advantage)
    bond_sizing  — Bond auto-sizing and amortization schedule builder
    returns      — IRR, equity multiple, CoC, and sensitivity table
"""

from .efb_engine import (
    DEFAULTS,
    compute_sources_and_uses,
    compute_pro_forma,
    compute_exit_analysis,
    compute_sensitivity_grid,
    compute_efb_tax_advantage,
)

from .bond_sizing import (
    size_bond_to_dscr,
    size_bond_to_ltv,
    calculate_annual_debt_service,
    build_amortization_schedule,
    summarize_schedule_by_year,
)

from .returns import (
    calculate_irr,
    calculate_equity_multiple,
    calculate_coc_return,
    build_investor_cash_flows,
    compute_sensitivity_table,
    compute_returns_summary,
)

__all__ = [
    # efb_engine
    "DEFAULTS",
    "compute_sources_and_uses",
    "compute_pro_forma",
    "compute_exit_analysis",
    "compute_sensitivity_grid",
    "compute_efb_tax_advantage",
    # bond_sizing
    "size_bond_to_dscr",
    "size_bond_to_ltv",
    "calculate_annual_debt_service",
    "build_amortization_schedule",
    "summarize_schedule_by_year",
    # returns
    "calculate_irr",
    "calculate_equity_multiple",
    "calculate_coc_return",
    "build_investor_cash_flows",
    "compute_sensitivity_table",
    "compute_returns_summary",
]
