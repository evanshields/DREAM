"""
Returns Analysis Module — Shieldstone Underwriting Mini-App
IRR, equity multiple, cash-on-cash return, and sensitivity analysis.
Self-contained implementations using only numpy (no scipy or external solvers).
"""

from __future__ import annotations

from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# 1. IRR (Newton-Raphson)
# ---------------------------------------------------------------------------

def calculate_irr(
    cash_flows: list[float],
    max_iterations: int = 1000,
    tolerance: float = 1e-6,
) -> Optional[float]:
    """
    Solve for IRR using Newton-Raphson iteration.

    cash_flows[0] is the initial investment (typically negative).
    Subsequent values are annual net cash flows including any terminal
    proceeds in the final year.

    Parameters
    ----------
    cash_flows : list[float]
        Annual cash flow series.  Must contain at least one positive and
        one negative value to have a meaningful IRR.
    max_iterations : int
        Maximum Newton-Raphson iterations before giving up.
    tolerance : float
        Convergence tolerance on NPV.

    Returns
    -------
    float or None
        Annualized IRR as a decimal (e.g. 0.15 = 15%), or None if the
        solver fails to converge.
    """
    if len(cash_flows) < 2:
        return None

    cf = np.array(cash_flows, dtype=float)

    # Check for sign changes — needed for a real solution
    has_negative = np.any(cf < 0)
    has_positive = np.any(cf > 0)
    if not (has_negative and has_positive):
        return None

    # Initial guess: simple heuristic based on total return
    total = float(np.sum(cf))
    initial = (total / abs(float(cf[0]))) / len(cf) if cf[0] != 0 else 0.1
    rate = max(-0.9, min(initial, 10.0))  # clamp to reasonable range

    n = np.arange(len(cf), dtype=float)

    for _ in range(max_iterations):
        # Avoid (1+rate)^n blowing up for extreme rates
        if rate <= -1.0:
            rate = -0.9

        discounts = (1.0 + rate) ** n
        npv = float(np.sum(cf / discounts))

        if abs(npv) < tolerance:
            return rate

        # Derivative of NPV w.r.t. rate
        d_npv = float(np.sum(-n * cf / ((1.0 + rate) ** (n + 1))))
        if d_npv == 0.0:
            break

        rate = rate - npv / d_npv

    # Final check: accept if close enough
    discounts = (1.0 + rate) ** n
    final_npv = float(np.sum(cf / discounts))
    if abs(final_npv) < tolerance * 1_000:
        return rate

    return None


# ---------------------------------------------------------------------------
# 2. Equity Multiple
# ---------------------------------------------------------------------------

def calculate_equity_multiple(cash_flows: list[float]) -> float:
    """
    Calculate equity multiple (total distributions / total invested capital).

    Parameters
    ----------
    cash_flows : list[float]
        cash_flows[0] = initial equity invested (negative value).
        Subsequent values = annual distributions + terminal proceeds.

    Returns
    -------
    float
        Equity multiple (e.g. 1.8 means 1.8× return of invested capital).
        Returns 0.0 if no capital was invested.
    """
    if not cash_flows:
        return 0.0

    total_invested = abs(min(float(cash_flows[0]), 0.0))
    if total_invested == 0.0:
        return 0.0

    total_distributions = sum(max(float(cf), 0.0) for cf in cash_flows[1:])
    return total_distributions / total_invested


# ---------------------------------------------------------------------------
# 3. Cash-on-Cash Return
# ---------------------------------------------------------------------------

def calculate_coc_return(year1_ncf: float, equity_invested: float) -> float:
    """
    Calculate Year-1 cash-on-cash return.

    Parameters
    ----------
    year1_ncf : float
        Distributable cash flow in Year 1 (after all debt service).
    equity_invested : float
        Total equity invested at acquisition (positive value).

    Returns
    -------
    float
        CoC return as a decimal (e.g. 0.06 = 6%).
        Returns 0.0 if equity_invested is zero.
    """
    if equity_invested == 0.0:
        return 0.0
    return year1_ncf / equity_invested


# ---------------------------------------------------------------------------
# 4. Build investor cash flow series
# ---------------------------------------------------------------------------

def build_investor_cash_flows(
    pro_forma: list[dict],
    exit_proceeds: float,
    equity_invested: float,
    hold_period: Optional[int] = None,
) -> list[float]:
    """
    Assemble the full investor cash flow series for IRR and EM calculations.

    Parameters
    ----------
    pro_forma : list[dict]
        Annual pro forma rows (output of efb_engine.compute_pro_forma).
        Must include 'distributable_cf' key.
    exit_proceeds : float
        Net equity proceeds from sale (after bond payoff and transaction costs).
    equity_invested : float
        Total equity invested at acquisition (positive value).
    hold_period : int | None
        Number of years to include.  Defaults to len(pro_forma).

    Returns
    -------
    list[float]
        [year_0_investment, year_1_cf, ..., year_N_cf_plus_exit]
        Year 0 is negative (outflow). Final year includes exit proceeds.
    """
    if hold_period is None:
        hold_period = len(pro_forma)
    hold_period = min(hold_period, len(pro_forma))

    cash_flows: list[float] = [-abs(equity_invested)]

    for yr_idx in range(hold_period):
        row = pro_forma[yr_idx]
        dist_cf = float(row.get("distributable_cf", 0.0))

        if yr_idx == hold_period - 1:
            # Terminal year: distributions + sale proceeds
            cash_flows.append(dist_cf + exit_proceeds)
        else:
            cash_flows.append(dist_cf)

    return cash_flows


# ---------------------------------------------------------------------------
# 5. Sensitivity Table (5×5 grid: exit cap × bond rate)
# ---------------------------------------------------------------------------

def compute_sensitivity_table(
    base_irr: float,
    base_dscr: float,
    inputs: dict,
) -> dict:
    """
    Build a 5×5 IRR/DSCR sensitivity grid varying exit cap and A Bond rate.

    Exit cap varies ±50 bps in 25 bps steps (5 columns).
    A Bond rate varies ±100 bps in 25 bps steps (5 rows, center ±50bps).

    NOTE: This function is intentionally lightweight and does NOT re-run the
    full pro forma (to avoid circular imports).  It adjusts base_irr and
    base_dscr using first-order linear approximations suitable for quick
    sensitivity display.  For full recalculation, call efb_engine functions
    directly with modified inputs.

    Parameters
    ----------
    base_irr : float
        Baseline IRR as a decimal.
    base_dscr : float
        Baseline Year-1 DSCR.
    inputs : dict
        Original deal inputs (used to read base rates for labeling).

    Returns
    -------
    dict
        {
            'exit_cap_labels': list[str],   # column headers
            'bond_rate_labels': list[str],  # row headers
            'irr_values':  list[list[float]], # [row][col]
            'dscr_values': list[list[float]],
        }
    """
    base_exit_cap: float = float(inputs.get("exit_cap_rate", 0.055))
    base_bond_rate: float = float(inputs.get("a_bond_rate", 0.055))

    # 5 exit cap steps: -50, -25, 0, +25, +50 bps
    exit_cap_deltas = [-0.0050, -0.0025, 0.0, 0.0025, 0.0050]
    # 5 bond rate steps: -50, -25, 0, +25, +50 bps (symmetric ±50 for 5-column grid)
    bond_rate_deltas = [-0.0050, -0.0025, 0.0, 0.0025, 0.0050]

    exit_caps = [base_exit_cap + d for d in exit_cap_deltas]
    bond_rates = [base_bond_rate + d for d in bond_rate_deltas]

    exit_cap_labels = [f"{c * 100:.2f}%" for c in exit_caps]
    bond_rate_labels = [f"{r * 100:.2f}%" for r in bond_rates]

    # Sensitivity approximations:
    #   IRR: higher exit cap → lower sale price → lower IRR  (approx -3× cap delta)
    #        higher bond rate → higher DS → lower distributable CF → lower IRR  (approx -0.8× rate delta)
    #   DSCR: higher bond rate → higher DS → lower DSCR  (approx -0.15× rate delta per bp)
    #         exit cap does not directly affect DSCR (it's an exit metric)
    IRR_EXIT_SENSITIVITY = -3.0    # IRR change per 1 unit of cap change
    IRR_RATE_SENSITIVITY = -0.8    # IRR change per 1 unit of rate change
    DSCR_RATE_SENSITIVITY = -3.0   # DSCR change per 1 unit of rate change

    irr_values: list[list[float]] = []
    dscr_values: list[list[float]] = []

    for bond_rate in bond_rates:
        irr_row: list[float] = []
        dscr_row: list[float] = []
        rate_delta = bond_rate - base_bond_rate
        irr_rate_adj = IRR_RATE_SENSITIVITY * rate_delta
        dscr_rate_adj = DSCR_RATE_SENSITIVITY * rate_delta

        for exit_cap in exit_caps:
            cap_delta = exit_cap - base_exit_cap
            irr_cap_adj = IRR_EXIT_SENSITIVITY * cap_delta
            adjusted_irr = base_irr + irr_rate_adj + irr_cap_adj
            adjusted_dscr = base_dscr + dscr_rate_adj

            irr_row.append(round(max(adjusted_irr, -1.0), 4))
            dscr_row.append(round(max(adjusted_dscr, 0.0), 4))

        irr_values.append(irr_row)
        dscr_values.append(dscr_row)

    return {
        "exit_cap_labels": exit_cap_labels,
        "bond_rate_labels": bond_rate_labels,
        "irr_values": irr_values,
        "dscr_values": dscr_values,
    }


# ---------------------------------------------------------------------------
# Convenience: full returns summary from pro forma + exit
# ---------------------------------------------------------------------------

def compute_returns_summary(
    pro_forma: list[dict],
    exit_analysis: dict,
    equity_invested: float,
    hold_period: Optional[int] = None,
) -> dict:
    """
    Produce a complete returns summary dict from pro forma and exit analysis.

    Parameters
    ----------
    pro_forma : list[dict]
        Output of efb_engine.compute_pro_forma().
    exit_analysis : dict
        Output of efb_engine.compute_exit_analysis().
    equity_invested : float
        Total equity invested (positive).
    hold_period : int | None
        Hold period in years; defaults to exit_analysis['hold_period'].

    Returns
    -------
    dict
        {
            'irr', 'equity_multiple', 'coc_yr1',
            'total_distributions', 'exit_proceeds',
            'cash_flows': list[float]
        }
    """
    if hold_period is None:
        hold_period = int(exit_analysis.get("hold_period", len(pro_forma)))

    exit_proceeds = float(exit_analysis.get("net_proceeds_to_equity", 0.0))

    cash_flows = build_investor_cash_flows(
        pro_forma=pro_forma,
        exit_proceeds=exit_proceeds,
        equity_invested=equity_invested,
        hold_period=hold_period,
    )

    irr = calculate_irr(cash_flows)
    em = calculate_equity_multiple(cash_flows)

    yr1_dist = float(pro_forma[0].get("distributable_cf", 0.0)) if pro_forma else 0.0
    coc = calculate_coc_return(yr1_dist, equity_invested)

    total_distributions = sum(cf for cf in cash_flows[1:] if cf > 0)

    return {
        "irr": round(irr, 6) if irr is not None else None,
        "irr_pct": f"{irr * 100:.2f}%" if irr is not None else "N/A",
        "equity_multiple": round(em, 4),
        "coc_yr1": round(coc, 6),
        "coc_yr1_pct": f"{coc * 100:.2f}%",
        "total_distributions": round(total_distributions, 2),
        "exit_proceeds": round(exit_proceeds, 2),
        "equity_invested": round(equity_invested, 2),
        "cash_flows": [round(cf, 2) for cf in cash_flows],
    }
