"""
T-Manual V2 Validation Engine — validates deal inputs against Shieldstone standards.
Returns structured flag report with GREEN/AMBER/RED status per field.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationFlag:
    field: str
    section: str        # "Revenue", "Expenses", "Bond Structure", "Returns", "Property"
    status: str         # "GREEN", "AMBER", "RED"
    message: str
    manual_ref: str     # e.g. "T-Manual V2, Section 1.1"
    current_value: Any
    benchmark: str


# ---------------------------------------------------------------------------
# Market-tier return hurdles (T-Manual V2, Section 1.1)
# ---------------------------------------------------------------------------

MARKET_HURDLES: dict[str, dict[str, float]] = {
    "gateway": {
        "min_irr": 0.14,
        "mid_irr": 0.15,
        "min_em":  1.5,
        "min_net_investor_irr": 0.15,
    },
    "secondary": {
        "min_irr": 0.16,
        "mid_irr": 0.175,
        "min_em":  1.5,
        "min_net_investor_irr": 0.15,
    },
    "tertiary": {
        "min_irr": 0.18,
        "mid_irr": 0.20,
        "min_em":  1.5,
        "min_net_investor_irr": 0.15,
    },
}

VINTAGE_HURDLE_ADD = 0.015   # +150 bps for pre-1985 vintage


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class DealValidator:
    """
    Validates EFB deal inputs (and optionally pro-forma model results) against
    Shieldstone T-Manual V2 standards.

    Usage
    -----
    validator = DealValidator()

    # Pre-flight check (no model yet)
    flags = validator.validate_inputs_only(inputs)

    # Full check (with model output)
    flags = validator.validate(inputs, model_results)

    summary = validator.get_summary(flags)
    """

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def validate(
        self,
        inputs: dict,
        model_results: dict | None = None,
    ) -> list[ValidationFlag]:
        """
        Run all validation rules.

        Parameters
        ----------
        inputs:
            Raw deal inputs dict from the frontend form.
        model_results:
            Output of compute_pro_forma + exit analysis.  When supplied the
            full returns-tier check is executed; when None those checks are
            skipped.
        """
        flags: list[ValidationFlag] = []

        flags.extend(self._validate_property(inputs))
        flags.extend(self._validate_revenue(inputs))
        flags.extend(self._validate_expenses(inputs))
        flags.extend(self._validate_financing(inputs))
        flags.extend(self._validate_capital(inputs))
        flags.extend(self._validate_exit(inputs))

        if model_results is not None:
            flags.extend(self._validate_returns(inputs, model_results))

        return flags

    def validate_inputs_only(self, inputs: dict) -> list[ValidationFlag]:
        """
        Validate inputs before running the full model (pre-flight check).
        Skips return-hurdle checks that require model_results.
        """
        return self.validate(inputs, model_results=None)

    def get_summary(self, flags: list[ValidationFlag]) -> dict:
        """Return {total, green_count, amber_count, red_count, pass_fail}."""
        green  = sum(1 for f in flags if f.status == "GREEN")
        amber  = sum(1 for f in flags if f.status == "AMBER")
        red    = sum(1 for f in flags if f.status == "RED")
        return {
            "total":       len(flags),
            "green_count": green,
            "amber_count": amber,
            "red_count":   red,
            "pass_fail":   "FAIL" if red > 0 else ("REVIEW" if amber > 0 else "PASS"),
        }

    # ------------------------------------------------------------------ #
    # Property / vintage                                                  #
    # ------------------------------------------------------------------ #

    def _validate_property(self, inputs: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        year_built: int | None = inputs.get("year_built")
        if year_built is not None:
            if year_built < 1985:
                flags.append(ValidationFlag(
                    field="year_built",
                    section="Property",
                    status="AMBER",
                    message=(
                        f"Property built in {year_built} (pre-1985). "
                        "Apply +150 bps to required IRR hurdle per vintage adjustment rule."
                    ),
                    manual_ref="T-Manual V2, Section 1.4 — Vintage Adjustment",
                    current_value=year_built,
                    benchmark="1985 or newer — no vintage adjustment required",
                ))
            else:
                flags.append(ValidationFlag(
                    field="year_built",
                    section="Property",
                    status="GREEN",
                    message=f"Property vintage {year_built}: no vintage IRR adjustment required.",
                    manual_ref="T-Manual V2, Section 1.4 — Vintage Adjustment",
                    current_value=year_built,
                    benchmark="1985 or newer",
                ))

        return flags

    # ------------------------------------------------------------------ #
    # Revenue assumptions                                                 #
    # ------------------------------------------------------------------ #

    def _validate_revenue(self, inputs: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        # --- Vacancy (Year 1) ---
        vacancy_yr1: float | None = inputs.get("vacancy_yr1")
        if vacancy_yr1 is not None:
            if vacancy_yr1 < 0.03:
                flags.append(ValidationFlag(
                    field="vacancy_yr1",
                    section="Revenue",
                    status="RED",
                    message=(
                        f"Year-1 vacancy of {vacancy_yr1:.1%} is critically optimistic (<3%). "
                        "Model likely overstates revenue."
                    ),
                    manual_ref="T-Manual V2, Section 2.1 — Vacancy Assumptions",
                    current_value=f"{vacancy_yr1:.1%}",
                    benchmark="Minimum 3%; standard range 5–10%",
                ))
            elif vacancy_yr1 < 0.05:
                flags.append(ValidationFlag(
                    field="vacancy_yr1",
                    section="Revenue",
                    status="AMBER",
                    message=(
                        f"Year-1 vacancy of {vacancy_yr1:.1%} is optimistic (<5%). "
                        "Stress-test at 7–8% vacancy."
                    ),
                    manual_ref="T-Manual V2, Section 2.1 — Vacancy Assumptions",
                    current_value=f"{vacancy_yr1:.1%}",
                    benchmark="Standard range 5–10%",
                ))
            elif vacancy_yr1 > 0.15:
                flags.append(ValidationFlag(
                    field="vacancy_yr1",
                    section="Revenue",
                    status="AMBER",
                    message=(
                        f"Year-1 vacancy of {vacancy_yr1:.1%} may be overly conservative (>15%). "
                        "Verify market conditions support this assumption."
                    ),
                    manual_ref="T-Manual V2, Section 2.1 — Vacancy Assumptions",
                    current_value=f"{vacancy_yr1:.1%}",
                    benchmark="Standard range 5–10%; >15% requires market justification",
                ))
            else:
                flags.append(ValidationFlag(
                    field="vacancy_yr1",
                    section="Revenue",
                    status="GREEN",
                    message=f"Year-1 vacancy of {vacancy_yr1:.1%} is within standard range.",
                    manual_ref="T-Manual V2, Section 2.1 — Vacancy Assumptions",
                    current_value=f"{vacancy_yr1:.1%}",
                    benchmark="5–15%",
                ))

        # --- Revenue growth rate ---
        revenue_growth: float | None = inputs.get("revenue_growth_pct")
        if revenue_growth is not None:
            if revenue_growth > 0.04:
                flags.append(ValidationFlag(
                    field="revenue_growth_pct",
                    section="Revenue",
                    status="AMBER",
                    message=(
                        f"Revenue growth rate of {revenue_growth:.1%} is aggressive (>4%). "
                        "Acceptable range is 2–3.5%."
                    ),
                    manual_ref="T-Manual V2, Section 2.2 — Revenue Growth",
                    current_value=f"{revenue_growth:.1%}",
                    benchmark="2.0–3.5%",
                ))
            elif revenue_growth < 0.02:
                flags.append(ValidationFlag(
                    field="revenue_growth_pct",
                    section="Revenue",
                    status="AMBER",
                    message=(
                        f"Revenue growth rate of {revenue_growth:.1%} is below standard range (<2%). "
                        "Confirm market conditions support below-inflation rent growth."
                    ),
                    manual_ref="T-Manual V2, Section 2.2 — Revenue Growth",
                    current_value=f"{revenue_growth:.1%}",
                    benchmark="2.0–3.5%",
                ))
            else:
                flags.append(ValidationFlag(
                    field="revenue_growth_pct",
                    section="Revenue",
                    status="GREEN",
                    message=f"Revenue growth rate of {revenue_growth:.1%} is within acceptable range.",
                    manual_ref="T-Manual V2, Section 2.2 — Revenue Growth",
                    current_value=f"{revenue_growth:.1%}",
                    benchmark="2.0–3.5%",
                ))

        return flags

    # ------------------------------------------------------------------ #
    # Expense assumptions                                                 #
    # ------------------------------------------------------------------ #

    def _validate_expenses(self, inputs: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        # --- Expense growth ---
        expense_growth: float | None = inputs.get("expense_growth_pct")
        if expense_growth is not None:
            if expense_growth < 0.02:
                flags.append(ValidationFlag(
                    field="expense_growth_pct",
                    section="Expenses",
                    status="RED",
                    message=(
                        f"Expense growth of {expense_growth:.1%} is too aggressive (<2%). "
                        "Operating expenses grow at or above CPI; this assumption understates costs."
                    ),
                    manual_ref="T-Manual V2, Section 3.1 — Expense Growth",
                    current_value=f"{expense_growth:.1%}",
                    benchmark="Minimum 2.5%; standard 3–3.5%",
                ))
            elif expense_growth < 0.025:
                flags.append(ValidationFlag(
                    field="expense_growth_pct",
                    section="Expenses",
                    status="AMBER",
                    message=(
                        f"Expense growth of {expense_growth:.1%} is below standard threshold (<2.5%). "
                        "Recommend stress-testing at 3%."
                    ),
                    manual_ref="T-Manual V2, Section 3.1 — Expense Growth",
                    current_value=f"{expense_growth:.1%}",
                    benchmark="2.5–3.5%",
                ))
            else:
                flags.append(ValidationFlag(
                    field="expense_growth_pct",
                    section="Expenses",
                    status="GREEN",
                    message=f"Expense growth of {expense_growth:.1%} is within acceptable range.",
                    manual_ref="T-Manual V2, Section 3.1 — Expense Growth",
                    current_value=f"{expense_growth:.1%}",
                    benchmark="2.5–3.5%",
                ))

        # --- Management fee ---
        mgmt_fee_pct: float | None = inputs.get("mgmt_fee_pct")
        if mgmt_fee_pct is not None:
            if mgmt_fee_pct < 0.03 or mgmt_fee_pct > 0.10:
                flags.append(ValidationFlag(
                    field="mgmt_fee_pct",
                    section="Expenses",
                    status="RED",
                    message=(
                        f"Management fee of {mgmt_fee_pct:.1%} of EGI is outside acceptable bounds (3–10%). "
                        + ("Fee is unrealistically low — understates operating costs."
                           if mgmt_fee_pct < 0.03
                           else "Fee exceeds market norms — verify with property manager.")
                    ),
                    manual_ref="T-Manual V2, Section 3.3 — Management Fee",
                    current_value=f"{mgmt_fee_pct:.1%}",
                    benchmark="3–10% of EGI; typical multifamily 4–8%",
                ))
            else:
                flags.append(ValidationFlag(
                    field="mgmt_fee_pct",
                    section="Expenses",
                    status="GREEN",
                    message=f"Management fee of {mgmt_fee_pct:.1%} of EGI is within acceptable range.",
                    manual_ref="T-Manual V2, Section 3.3 — Management Fee",
                    current_value=f"{mgmt_fee_pct:.1%}",
                    benchmark="3–10% of EGI",
                ))

        # --- Replacement reserves ---
        reserves_per_unit: float | None = inputs.get("replacement_reserves_per_unit")
        if reserves_per_unit is not None:
            if reserves_per_unit < 200:
                flags.append(ValidationFlag(
                    field="replacement_reserves_per_unit",
                    section="Expenses",
                    status="RED",
                    message=(
                        f"Replacement reserves of ${reserves_per_unit:,.0f}/unit/yr are critically low (<$200). "
                        "Lenders will require a minimum of $250–300; model understates future capex needs."
                    ),
                    manual_ref="T-Manual V2, Section 3.4 — Replacement Reserves",
                    current_value=f"${reserves_per_unit:,.0f}/unit/yr",
                    benchmark="Minimum $200; standard $300–500/unit/yr",
                ))
            elif reserves_per_unit < 300:
                flags.append(ValidationFlag(
                    field="replacement_reserves_per_unit",
                    section="Expenses",
                    status="AMBER",
                    message=(
                        f"Replacement reserves of ${reserves_per_unit:,.0f}/unit/yr are below standard (<$300). "
                        "Consider increasing to $300–400 for a conservative base case."
                    ),
                    manual_ref="T-Manual V2, Section 3.4 — Replacement Reserves",
                    current_value=f"${reserves_per_unit:,.0f}/unit/yr",
                    benchmark="Standard $300–500/unit/yr",
                ))
            else:
                flags.append(ValidationFlag(
                    field="replacement_reserves_per_unit",
                    section="Expenses",
                    status="GREEN",
                    message=f"Replacement reserves of ${reserves_per_unit:,.0f}/unit/yr meet minimum standard.",
                    manual_ref="T-Manual V2, Section 3.4 — Replacement Reserves",
                    current_value=f"${reserves_per_unit:,.0f}/unit/yr",
                    benchmark="$300+/unit/yr",
                ))

        # --- Property tax / EFB exemption ---
        efb_exempt: bool | None = inputs.get("efb_exempt")
        property_tax_in_model: float | None = inputs.get("property_tax_annual")

        if efb_exempt is True and property_tax_in_model is not None:
            if property_tax_in_model > 0:
                flags.append(ValidationFlag(
                    field="property_tax_annual",
                    section="Bond Structure",
                    status="RED",
                    message=(
                        f"EFB exemption is marked TRUE but model includes ${property_tax_in_model:,.0f} in "
                        "property taxes. EFB-exempt properties carry $0 property tax. Remove tax line or "
                        "disable exemption flag."
                    ),
                    manual_ref="T-Manual V2, Section 4.2 — EFB Property Tax Exemption",
                    current_value=f"EFB Exempt=True, Tax=${property_tax_in_model:,.0f}",
                    benchmark="EFB Exempt=True → Property Tax = $0",
                ))
            else:
                flags.append(ValidationFlag(
                    field="property_tax_annual",
                    section="Bond Structure",
                    status="GREEN",
                    message="EFB exemption is TRUE and property tax is correctly set to $0.",
                    manual_ref="T-Manual V2, Section 4.2 — EFB Property Tax Exemption",
                    current_value="EFB Exempt=True, Tax=$0",
                    benchmark="EFB Exempt=True → Property Tax = $0",
                ))
        elif efb_exempt is False and property_tax_in_model is not None:
            flags.append(ValidationFlag(
                field="property_tax_annual",
                section="Bond Structure",
                status="GREEN",
                message=(
                    f"No EFB exemption; property tax of ${property_tax_in_model:,.0f} is present in model."
                ),
                manual_ref="T-Manual V2, Section 4.2 — EFB Property Tax Exemption",
                current_value=f"EFB Exempt=False, Tax=${property_tax_in_model:,.0f}",
                benchmark="Non-exempt property — tax line required",
            ))

        return flags

    # ------------------------------------------------------------------ #
    # Financing                                                           #
    # ------------------------------------------------------------------ #

    def _validate_financing(self, inputs: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        # --- LTV ---
        ltv: float | None = inputs.get("ltv")
        if ltv is not None:
            if ltv > 0.75:
                flags.append(ValidationFlag(
                    field="ltv",
                    section="Bond Structure",
                    status="RED",
                    message=(
                        f"LTV of {ltv:.1%} exceeds hard maximum of 75%. "
                        "Significantly increases default risk and lender rejection probability."
                    ),
                    manual_ref="T-Manual V2, Section 5.1 — Financing Standards",
                    current_value=f"{ltv:.1%}",
                    benchmark="Maximum 75%; standard ≤65%",
                ))
            elif ltv > 0.65:
                flags.append(ValidationFlag(
                    field="ltv",
                    section="Bond Structure",
                    status="AMBER",
                    message=(
                        f"LTV of {ltv:.1%} exceeds standard 65% guideline. "
                        "Acceptable with strong debt service coverage but review with lender."
                    ),
                    manual_ref="T-Manual V2, Section 5.1 — Financing Standards",
                    current_value=f"{ltv:.1%}",
                    benchmark="Standard ≤65%",
                ))
            else:
                flags.append(ValidationFlag(
                    field="ltv",
                    section="Bond Structure",
                    status="GREEN",
                    message=f"LTV of {ltv:.1%} is within standard guidelines.",
                    manual_ref="T-Manual V2, Section 5.1 — Financing Standards",
                    current_value=f"{ltv:.1%}",
                    benchmark="≤65%",
                ))

        # --- DSCR ---
        dscr: float | None = inputs.get("dscr") or (
            # Allow model_results or a pre-computed value
            inputs.get("debt_service_coverage_ratio")
        )
        if dscr is not None:
            if dscr < 1.10:
                flags.append(ValidationFlag(
                    field="dscr",
                    section="Bond Structure",
                    status="RED",
                    message=(
                        f"DSCR of {dscr:.2f}x is below the hard floor of 1.10x. "
                        "Deal cannot support debt service; renegotiate price or terms."
                    ),
                    manual_ref="T-Manual V2, Section 5.2 — DSCR",
                    current_value=f"{dscr:.2f}x",
                    benchmark="Minimum 1.10x; standard ≥1.25x",
                ))
            elif dscr < 1.25:
                flags.append(ValidationFlag(
                    field="dscr",
                    section="Bond Structure",
                    status="AMBER",
                    message=(
                        f"DSCR of {dscr:.2f}x is below preferred 1.25x threshold. "
                        "Stress-test at 10% revenue decline."
                    ),
                    manual_ref="T-Manual V2, Section 5.2 — DSCR",
                    current_value=f"{dscr:.2f}x",
                    benchmark="Preferred ≥1.25x",
                ))
            else:
                flags.append(ValidationFlag(
                    field="dscr",
                    section="Bond Structure",
                    status="GREEN",
                    message=f"DSCR of {dscr:.2f}x meets preferred coverage standard.",
                    manual_ref="T-Manual V2, Section 5.2 — DSCR",
                    current_value=f"{dscr:.2f}x",
                    benchmark="≥1.25x",
                ))

        # --- IO period ---
        io_months: int | None = inputs.get("io_months")
        if io_months is not None:
            if io_months != 30:
                status = "AMBER"
                msg = (
                    f"IO period of {io_months} months deviates from standard 30-month term. "
                    + ("Shorter IO reduces cash-on-cash in early years."
                       if io_months < 30
                       else "Extended IO increases balloon risk at maturity.")
                )
            else:
                status = "GREEN"
                msg = "IO period of 30 months matches standard term."
            flags.append(ValidationFlag(
                field="io_months",
                section="Bond Structure",
                status=status,
                message=msg,
                manual_ref="T-Manual V2, Section 5.3 — IO Period",
                current_value=f"{io_months} months",
                benchmark="30 months",
            ))

        return flags

    # ------------------------------------------------------------------ #
    # Capital expenditure                                                 #
    # ------------------------------------------------------------------ #

    def _validate_capital(self, inputs: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        deal_type: str = str(inputs.get("deal_type", "")).lower()
        is_value_add = "value" in deal_type or "value-add" in deal_type or "rehab" in deal_type

        if not is_value_add:
            # Only enforce capex minimum for value-add deals
            return flags

        total_units: int | None = inputs.get("total_units")
        immediate_capex: float | None = inputs.get("immediate_capex_total")

        if total_units and immediate_capex is not None:
            capex_per_unit = immediate_capex / total_units
            if capex_per_unit < 500:
                flags.append(ValidationFlag(
                    field="immediate_capex_total",
                    section="Expenses",
                    status="AMBER",
                    message=(
                        f"Immediate capex of ${capex_per_unit:,.0f}/unit is low for a value-add deal (<$500/unit). "
                        "Confirm scope of work; under-budgeting capex is a leading cause of deal failure."
                    ),
                    manual_ref="T-Manual V2, Section 6.1 — Capital Budget",
                    current_value=f"${capex_per_unit:,.0f}/unit",
                    benchmark="≥$500/unit for value-add; typical light rehab $2,000–5,000/unit",
                ))
            else:
                flags.append(ValidationFlag(
                    field="immediate_capex_total",
                    section="Expenses",
                    status="GREEN",
                    message=f"Immediate capex of ${capex_per_unit:,.0f}/unit meets minimum threshold for value-add.",
                    manual_ref="T-Manual V2, Section 6.1 — Capital Budget",
                    current_value=f"${capex_per_unit:,.0f}/unit",
                    benchmark="≥$500/unit",
                ))

        return flags

    # ------------------------------------------------------------------ #
    # Exit assumptions                                                    #
    # ------------------------------------------------------------------ #

    def _validate_exit(self, inputs: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        going_in_cap: float | None = inputs.get("going_in_cap_rate")
        exit_cap: float | None = inputs.get("exit_cap_rate")
        hold_period_years: float | None = inputs.get("hold_period_years")

        # --- Exit cap vs going-in cap ---
        if going_in_cap is not None and exit_cap is not None:
            if exit_cap < going_in_cap:
                flags.append(ValidationFlag(
                    field="exit_cap_rate",
                    section="Returns",
                    status="AMBER",
                    message=(
                        f"Exit cap of {exit_cap:.2%} is below going-in cap of {going_in_cap:.2%}. "
                        "This assumes cap rate compression at exit — an optimistic scenario. "
                        "Stress-test with exit cap equal to or above going-in cap."
                    ),
                    manual_ref="T-Manual V2, Section 7.1 — Exit Cap Rate",
                    current_value=f"Exit {exit_cap:.2%} vs Going-In {going_in_cap:.2%}",
                    benchmark="Exit cap ≥ going-in cap (conservative); allow max -25 bps compression",
                ))
            elif exit_cap > going_in_cap + 0.0100:
                flags.append(ValidationFlag(
                    field="exit_cap_rate",
                    section="Returns",
                    status="AMBER",
                    message=(
                        f"Exit cap of {exit_cap:.2%} is more than 100 bps above going-in cap of {going_in_cap:.2%}. "
                        "Conservative assumption — verify this doesn't make an otherwise viable deal appear failed."
                    ),
                    manual_ref="T-Manual V2, Section 7.1 — Exit Cap Rate",
                    current_value=f"Exit {exit_cap:.2%} vs Going-In {going_in_cap:.2%}",
                    benchmark="Typical expansion: +25–75 bps over hold period",
                ))
            else:
                flags.append(ValidationFlag(
                    field="exit_cap_rate",
                    section="Returns",
                    status="GREEN",
                    message=(
                        f"Exit cap of {exit_cap:.2%} vs going-in cap of {going_in_cap:.2%} — "
                        "reasonable assumption."
                    ),
                    manual_ref="T-Manual V2, Section 7.1 — Exit Cap Rate",
                    current_value=f"Exit {exit_cap:.2%} vs Going-In {going_in_cap:.2%}",
                    benchmark="Exit cap within +25–75 bps of going-in cap",
                ))

        # --- Hold period ---
        if hold_period_years is not None:
            if hold_period_years < 3:
                flags.append(ValidationFlag(
                    field="hold_period_years",
                    section="Returns",
                    status="AMBER",
                    message=(
                        f"Hold period of {hold_period_years:.1f} years is short (<3 years). "
                        "Execution risk is elevated; value-add business plans need time to stabilize. "
                        "Verify exit strategy is realistic at this timeline."
                    ),
                    manual_ref="T-Manual V2, Section 7.2 — Hold Period",
                    current_value=f"{hold_period_years:.1f} years",
                    benchmark="Minimum 3 years; standard 5–7 years",
                ))
            else:
                flags.append(ValidationFlag(
                    field="hold_period_years",
                    section="Returns",
                    status="GREEN",
                    message=f"Hold period of {hold_period_years:.1f} years meets minimum execution runway.",
                    manual_ref="T-Manual V2, Section 7.2 — Hold Period",
                    current_value=f"{hold_period_years:.1f} years",
                    benchmark="≥3 years",
                ))

        return flags

    # ------------------------------------------------------------------ #
    # Return hurdles (requires model_results)                            #
    # ------------------------------------------------------------------ #

    def _validate_returns(self, inputs: dict, model_results: dict) -> list[ValidationFlag]:
        flags: list[ValidationFlag] = []

        market_tier: str = str(inputs.get("market_tier", "gateway")).lower()
        hurdles = MARKET_HURDLES.get(market_tier, MARKET_HURDLES["gateway"])

        year_built: int | None = inputs.get("year_built")
        vintage_add = VINTAGE_HURDLE_ADD if (year_built is not None and year_built < 1985) else 0.0
        effective_min_irr = hurdles["min_irr"] + vintage_add

        projected_irr: float | None = model_results.get("levered_irr") or model_results.get("irr")
        projected_em: float | None = model_results.get("equity_multiple") or model_results.get("em")
        net_investor_irr: float | None = (
            model_results.get("net_investor_irr")
            or model_results.get("investor_irr")
        )

        # --- Levered IRR ---
        if projected_irr is not None:
            tier_label = market_tier.capitalize()
            vintage_note = f" (+{vintage_add:.0%} vintage adjustment applied)" if vintage_add else ""
            if projected_irr < effective_min_irr:
                flags.append(ValidationFlag(
                    field="projected_irr",
                    section="Returns",
                    status="RED",
                    message=(
                        f"Projected levered IRR of {projected_irr:.1%} is BELOW the {tier_label} market "
                        f"minimum of {effective_min_irr:.1%}{vintage_note}. Deal does not meet Shieldstone "
                        "return standards."
                    ),
                    manual_ref="T-Manual V2, Section 1.1 — Return Hurdles",
                    current_value=f"{projected_irr:.1%}",
                    benchmark=f"{tier_label} minimum: {effective_min_irr:.1%}",
                ))
            elif projected_irr < effective_min_irr + 0.01:
                flags.append(ValidationFlag(
                    field="projected_irr",
                    section="Returns",
                    status="AMBER",
                    message=(
                        f"Projected levered IRR of {projected_irr:.1%} is within 100 bps of the "
                        f"{tier_label} minimum of {effective_min_irr:.1%}{vintage_note}. "
                        "Limited cushion — any assumption slippage will miss the hurdle."
                    ),
                    manual_ref="T-Manual V2, Section 1.1 — Return Hurdles",
                    current_value=f"{projected_irr:.1%}",
                    benchmark=f"{tier_label} minimum: {effective_min_irr:.1%}; preferred midpoint: {hurdles['mid_irr']:.1%}",
                ))
            else:
                flags.append(ValidationFlag(
                    field="projected_irr",
                    section="Returns",
                    status="GREEN",
                    message=(
                        f"Projected levered IRR of {projected_irr:.1%} exceeds {tier_label} minimum "
                        f"of {effective_min_irr:.1%} by {(projected_irr - effective_min_irr) * 100:.0f} bps{vintage_note}."
                    ),
                    manual_ref="T-Manual V2, Section 1.1 — Return Hurdles",
                    current_value=f"{projected_irr:.1%}",
                    benchmark=f"{tier_label} minimum: {effective_min_irr:.1%}",
                ))

        # --- Equity Multiple ---
        if projected_em is not None:
            min_em = hurdles["min_em"]
            if projected_em < min_em:
                flags.append(ValidationFlag(
                    field="equity_multiple",
                    section="Returns",
                    status="RED",
                    message=(
                        f"Projected equity multiple of {projected_em:.2f}x is below the minimum "
                        f"of {min_em:.1f}x required for all markets."
                    ),
                    manual_ref="T-Manual V2, Section 1.1 — Return Hurdles",
                    current_value=f"{projected_em:.2f}x",
                    benchmark=f"Minimum {min_em:.1f}x all markets",
                ))
            elif projected_em < min_em + 0.1:
                flags.append(ValidationFlag(
                    field="equity_multiple",
                    section="Returns",
                    status="AMBER",
                    message=(
                        f"Projected equity multiple of {projected_em:.2f}x barely clears the "
                        f"{min_em:.1f}x floor. Low margin of safety."
                    ),
                    manual_ref="T-Manual V2, Section 1.1 — Return Hurdles",
                    current_value=f"{projected_em:.2f}x",
                    benchmark=f"Minimum {min_em:.1f}x; preferred 1.7x+",
                ))
            else:
                flags.append(ValidationFlag(
                    field="equity_multiple",
                    section="Returns",
                    status="GREEN",
                    message=f"Projected equity multiple of {projected_em:.2f}x meets return standard.",
                    manual_ref="T-Manual V2, Section 1.1 — Return Hurdles",
                    current_value=f"{projected_em:.2f}x",
                    benchmark=f"Minimum {min_em:.1f}x",
                ))

        # --- Net investor IRR ---
        if net_investor_irr is not None:
            min_net = hurdles["min_net_investor_irr"]
            if net_investor_irr < min_net:
                flags.append(ValidationFlag(
                    field="net_investor_irr",
                    section="Returns",
                    status="RED",
                    message=(
                        f"Net investor IRR (after fees/promote) of {net_investor_irr:.1%} is below "
                        f"the {min_net:.1%} minimum required across all market tiers."
                    ),
                    manual_ref="T-Manual V2, Section 1.2 — Net Investor Returns",
                    current_value=f"{net_investor_irr:.1%}",
                    benchmark=f"Minimum {min_net:.1%} net to investor",
                ))
            else:
                flags.append(ValidationFlag(
                    field="net_investor_irr",
                    section="Returns",
                    status="GREEN",
                    message=(
                        f"Net investor IRR of {net_investor_irr:.1%} meets the {min_net:.1%} minimum."
                    ),
                    manual_ref="T-Manual V2, Section 1.2 — Net Investor Returns",
                    current_value=f"{net_investor_irr:.1%}",
                    benchmark=f"Minimum {min_net:.1%}",
                ))

        return flags
