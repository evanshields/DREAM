"""
Bond Sizing Module — Shieldstone Underwriting Mini-App
Sizes A Bond to hit a target DSCR or LTV, and builds full amortization schedules.
Used when the user wants auto-sizing rather than manually specifying a bond amount.
"""

from __future__ import annotations

import math


# ---------------------------------------------------------------------------
# 1. Size bond to target DSCR
# ---------------------------------------------------------------------------

def size_bond_to_dscr(
    noi_yr1: float,
    target_dscr: float,
    a_bond_rate: float,
) -> float:
    """
    Back-solve the A Bond amount that produces a target Year-1 DSCR.

    During the IO period the only debt service is interest, so:
        DSCR = NOI / (A Bond × rate)
        A Bond = NOI / (target_dscr × rate)

    Parameters
    ----------
    noi_yr1 : float
        Stabilized Year-1 NOI (after expenses, before debt service).
    target_dscr : float
        Target DSCR (e.g. 1.25).
    a_bond_rate : float
        Annual interest rate as a decimal (e.g. 0.055 for 5.5%).

    Returns
    -------
    float
        Maximum A Bond amount that meets the target DSCR.

    Raises
    ------
    ValueError
        If target_dscr or a_bond_rate is non-positive.
    """
    if target_dscr <= 0:
        raise ValueError(f"target_dscr must be positive, got {target_dscr}")
    if a_bond_rate <= 0:
        raise ValueError(f"a_bond_rate must be positive, got {a_bond_rate}")

    annual_ds_max = noi_yr1 / target_dscr
    bond_amount = annual_ds_max / a_bond_rate
    return bond_amount


# ---------------------------------------------------------------------------
# 2. Size bond to LTV
# ---------------------------------------------------------------------------

def size_bond_to_ltv(purchase_price: float, ltv: float) -> float:
    """
    Size the A Bond to a target loan-to-value ratio.

    Parameters
    ----------
    purchase_price : float
        Acquisition price.
    ltv : float
        Target LTV as a decimal (e.g. 0.90 for 90%).

    Returns
    -------
    float
        A Bond amount = purchase_price × ltv.

    Raises
    ------
    ValueError
        If ltv is outside (0, 1].
    """
    if not (0 < ltv <= 1.0):
        raise ValueError(f"ltv must be between 0 and 1 (exclusive/inclusive), got {ltv}")
    return purchase_price * ltv


# ---------------------------------------------------------------------------
# 3. Annual debt service
# ---------------------------------------------------------------------------

def calculate_annual_debt_service(
    bond_amount: float,
    rate: float,
    io: bool,
    amort_years: int = 30,
) -> float:
    """
    Calculate annual debt service for a bond.

    Parameters
    ----------
    bond_amount : float
        Outstanding principal.
    rate : float
        Annual interest rate as a decimal.
    io : bool
        True = interest-only; False = fully amortizing.
    amort_years : int
        Amortization term in years (used only when io=False).

    Returns
    -------
    float
        Annual debt service (interest + scheduled principal).

    Raises
    ------
    ValueError
        If bond_amount or rate is negative, or amort_years < 1.
    """
    if bond_amount < 0:
        raise ValueError(f"bond_amount must be non-negative, got {bond_amount}")
    if rate < 0:
        raise ValueError(f"rate must be non-negative, got {rate}")
    if amort_years < 1:
        raise ValueError(f"amort_years must be >= 1, got {amort_years}")

    if io:
        return bond_amount * rate

    # Fully amortizing: standard mortgage PMT × 12
    r_monthly = rate / 12.0
    n = amort_years * 12

    if r_monthly == 0.0:
        monthly_pmt = bond_amount / n
    else:
        monthly_pmt = bond_amount * r_monthly / (1.0 - (1.0 + r_monthly) ** (-n))

    return monthly_pmt * 12.0


# ---------------------------------------------------------------------------
# 4. Full amortization schedule (month-by-month)
# ---------------------------------------------------------------------------

def build_amortization_schedule(
    principal: float,
    rate: float,
    io_months: int,
    total_months: int,
    turbo_payments: dict[int, float] | None = None,
) -> list[dict]:
    """
    Build a month-by-month amortization schedule with optional turbo principal.

    IO months have zero scheduled principal reduction.  Amortizing months use
    the standard level-payment formula re-cast on the remaining balance after
    any turbo principal applied during IO.  Turbo payments reduce the balance
    in the month they are applied, lowering subsequent interest and principal.

    Parameters
    ----------
    principal : float
        Original loan amount.
    rate : float
        Annual interest rate as a decimal.
    io_months : int
        Number of interest-only months from origination.
    total_months : int
        Total loan term in months.
    turbo_payments : dict[int, float] | None
        Optional {month_number: turbo_amount} extra principal payments applied
        during or after the IO period.  Month numbers are 1-indexed.

    Returns
    -------
    list[dict]
        One dict per month with keys:
        {month, beginning_balance, interest, scheduled_principal,
         turbo_principal, total_principal, ending_balance, cumulative_principal}

    Raises
    ------
    ValueError
        If io_months >= total_months or principal is non-positive.
    """
    if principal <= 0:
        raise ValueError(f"principal must be positive, got {principal}")
    if io_months < 0:
        raise ValueError(f"io_months must be non-negative, got {io_months}")
    if total_months < 1:
        raise ValueError(f"total_months must be >= 1, got {total_months}")
    if io_months >= total_months:
        raise ValueError(
            f"io_months ({io_months}) must be less than total_months ({total_months})"
        )

    turbo_map: dict[int, float] = turbo_payments or {}
    r_monthly = rate / 12.0
    schedule: list[dict] = []
    balance = principal
    cumulative_principal = 0.0

    # Pre-compute amortizing payment based on balance at start of amortization.
    # We'll recast each month to handle balance changes from turbo payments.
    amort_months_remaining = total_months - io_months

    for month in range(1, total_months + 1):
        beg_balance = balance
        interest = beg_balance * r_monthly

        # Scheduled principal
        if month <= io_months:
            scheduled_principal = 0.0
        else:
            # Recast: solve for level payment on remaining balance over remaining months
            remaining_amort = total_months - month + 1
            if r_monthly == 0.0:
                monthly_pmt = beg_balance / remaining_amort if remaining_amort > 0 else beg_balance
            else:
                if remaining_amort > 0:
                    monthly_pmt = beg_balance * r_monthly / (1.0 - (1.0 + r_monthly) ** (-remaining_amort))
                else:
                    monthly_pmt = beg_balance + interest
            scheduled_principal = max(0.0, monthly_pmt - interest)
            scheduled_principal = min(scheduled_principal, beg_balance)  # cap at balance

        turbo_principal = turbo_map.get(month, 0.0)
        turbo_principal = min(turbo_principal, max(0.0, beg_balance - scheduled_principal))

        total_principal = scheduled_principal + turbo_principal
        end_balance = max(0.0, beg_balance - total_principal)
        cumulative_principal += total_principal
        balance = end_balance

        schedule.append({
            "month": month,
            "beginning_balance": round(beg_balance, 2),
            "interest": round(interest, 2),
            "scheduled_principal": round(scheduled_principal, 2),
            "turbo_principal": round(turbo_principal, 2),
            "total_principal": round(total_principal, 2),
            "ending_balance": round(end_balance, 2),
            "cumulative_principal": round(cumulative_principal, 2),
        })

        # Loan fully repaid
        if end_balance == 0.0:
            break

    return schedule


# ---------------------------------------------------------------------------
# Convenience: annual summary of monthly schedule
# ---------------------------------------------------------------------------

def summarize_schedule_by_year(schedule: list[dict]) -> list[dict]:
    """
    Aggregate a monthly amortization schedule into annual rows.

    Parameters
    ----------
    schedule : list[dict]
        Output of build_amortization_schedule().

    Returns
    -------
    list[dict]
        One dict per year with totals and year-end balance.
    """
    annual: dict[int, dict] = {}
    for row in schedule:
        yr = math.ceil(row["month"] / 12)
        if yr not in annual:
            annual[yr] = {
                "year": yr,
                "total_interest": 0.0,
                "total_scheduled_principal": 0.0,
                "total_turbo_principal": 0.0,
                "total_principal": 0.0,
                "ending_balance": 0.0,
            }
        annual[yr]["total_interest"] += row["interest"]
        annual[yr]["total_scheduled_principal"] += row["scheduled_principal"]
        annual[yr]["total_turbo_principal"] += row["turbo_principal"]
        annual[yr]["total_principal"] += row["total_principal"]
        annual[yr]["ending_balance"] = row["ending_balance"]  # last month of year

    # Round all floats
    result = []
    for yr_num in sorted(annual.keys()):
        d = annual[yr_num]
        result.append({k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items()})

    return result
