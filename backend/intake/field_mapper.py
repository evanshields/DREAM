"""
Field Mapper — maps raw extracted fields to frontend form field keys.

Handles three document types:
  - T-12 / Operating Statement  → per-unit annual expense fields + revenue fields
  - Rent Roll                   → unit_mix array + vacancy
  - Offering Memorandum         → property header fields

All per-unit values are computed by dividing annual totals by unit_count.
Percentages are passed through as-is (0–1 float).
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Field alias maps
# ---------------------------------------------------------------------------
# Each key is a frontend form field name.
# Each value is a list of raw extraction keys that might carry the data.
# The mapper tries each alias in order and uses the first non-None value.

T12_FIELD_MAP: dict[str, list[str]] = {
    "gross_potential_rent":    ["gpr_annual", "gross_potential_rent", "gpr", "total_potential_revenue"],
    "vacancy_rate":            ["vacancy_pct", "vacancy_rate", "physical_vacancy"],
    "concessions_pct":         ["concessions_pct", "concessions_rate"],
    "bad_debt_annual":         ["bad_debt_annual", "bad_debt", "credit_loss"],
    "other_income_annual":     ["other_income_annual", "other_income", "ancillary_income"],
    "payroll_per_unit":        ["payroll_annual", "payroll", "salaries", "staff"],
    "utilities_per_unit":      ["utilities_annual", "utilities", "utility"],
    "rm_per_unit":             ["rm_annual", "repairs_maintenance_annual", "repairs", "maintenance", "r&m"],
    "turnover_per_unit":       ["turnover_annual", "turnover", "make_ready"],
    "admin_per_unit":          ["admin_annual", "admin", "administrative", "marketing"],
    "insurance_per_unit":      ["insurance_annual", "insurance", "property_insurance"],
    "mgmt_fee_pct":            ["mgmt_fee_pct", "management_fee_pct", "mgmt_fee"],
    "mgmt_fee_annual":         ["mgmt_fee_annual", "management_fee_annual"],
    "property_tax_annual":     ["property_tax_annual", "real_estate_tax_annual", "taxes_annual"],
    "noi_annual":              ["noi_annual", "net_operating_income_annual", "NOI"],
    "total_opex_annual":       ["total_opex_annual", "total_operating_expenses_annual"],
    "egi_annual":              ["egi_annual", "effective_gross_income_annual", "EGI"],
}

RENT_ROLL_FIELD_MAP: dict[str, str] = {
    "unit_mix":    "unit_type_aggregates",   # list[dict]
    "total_units": "total_units",
    "vacancy_yr1": "vacancy_rate",
}

OM_FIELD_MAP: dict[str, list[str]] = {
    "property_name": ["property_name", "project_name"],
    "total_units":   ["total_units", "unit_count", "number_of_units", "units"],
    "year_built":    ["year_built", "year_constructed"],
    "asking_price":  ["asking_price", "list_price", "sale_price"],
    "purchase_price": ["purchase_price", "asking_price"],
    "address":       ["address"],
}


# ---------------------------------------------------------------------------
# Per-unit expense fields — these are stored as annual totals and need
# dividing by unit_count to produce the per-unit-per-year figure.
# ---------------------------------------------------------------------------

_PER_UNIT_FIELDS = {
    "payroll_per_unit",
    "utilities_per_unit",
    "rm_per_unit",
    "turnover_per_unit",
    "admin_per_unit",
    "insurance_per_unit",
}

# Fields that should be passed through as annual totals (no per-unit conversion).
_ANNUAL_TOTAL_FIELDS = {
    "gross_potential_rent",
    "other_income_annual",
    "bad_debt_annual",
    "mgmt_fee_annual",
    "property_tax_annual",
    "noi_annual",
    "total_opex_annual",
    "egi_annual",
}

# Percentage fields — passed through as 0–1 floats, no unit division.
_PERCENTAGE_FIELDS = {
    "vacancy_rate",
    "concessions_pct",
    "mgmt_fee_pct",
}


# ---------------------------------------------------------------------------
# Public mapping functions
# ---------------------------------------------------------------------------

def map_t12_to_form(extracted: dict, unit_count: int) -> dict:
    """
    Convert T-12 raw extracted values to form-ready fields.

    Per-unit expense fields are divided by unit_count when unit_count > 0.
    Percentage fields are passed through unchanged (0–1 floats).
    Annual totals (GPR, EGI, NOI, etc.) are passed through at the property level.

    Parameters
    ----------
    extracted:
        Raw output from the T-12 extractor (field names from T12_FIELD_MAP values).
    unit_count:
        Total residential units.  Required to compute per-unit figures.
        Pass 0 or None to skip per-unit conversion (values will be raw annual totals).

    Returns
    -------
    dict keyed by frontend form field names.
    """
    result: dict[str, Any] = {}

    safe_unit_count = unit_count if (unit_count and unit_count > 0) else None

    for form_key, aliases in T12_FIELD_MAP.items():
        raw_value = _first_match(extracted, aliases)
        if raw_value is None:
            continue

        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            result[form_key] = raw_value
            continue

        if form_key in _PERCENTAGE_FIELDS:
            # Sanity check: if someone stored 8.5 instead of 0.085, normalise.
            if value > 1.0:
                value = value / 100.0
            result[form_key] = round(value, 4)

        elif form_key in _PER_UNIT_FIELDS:
            if safe_unit_count:
                result[form_key] = round(value / safe_unit_count, 2)
            else:
                # Store as annual total with a note key
                result[form_key + "_annual_total"] = round(value, 2)
                result[form_key + "_note"] = "unit_count_unavailable_for_per_unit_conversion"

        elif form_key in _ANNUAL_TOTAL_FIELDS:
            result[form_key] = round(value, 2)

        else:
            # Default: pass through
            result[form_key] = round(value, 2)

    # Attach unit count if provided, so the form can display it
    if safe_unit_count:
        result["_source_unit_count"] = safe_unit_count

    return result


def map_rent_roll_to_form(extracted: dict) -> dict:
    """
    Convert rent roll aggregates to the unit_mix format expected by the form.

    Returns
    -------
    dict with keys:
      - ``unit_mix``: list[dict] — one entry per unit type with
        {type, beds, baths, count, avg_rent, avg_market_rent, avg_sqft}
      - ``total_units``: int
      - ``vacancy_yr1``: float (0–1) — current physical vacancy from rent roll
    """
    result: dict[str, Any] = {}

    # unit_mix / unit_type_aggregates
    agg_key = RENT_ROLL_FIELD_MAP["unit_mix"]
    aggregates = extracted.get(agg_key)
    if aggregates is not None:
        result["unit_mix"] = _normalise_unit_mix(aggregates)

    # total_units
    total_units_key = RENT_ROLL_FIELD_MAP["total_units"]
    total_units = extracted.get(total_units_key)
    if total_units is not None:
        try:
            result["total_units"] = int(total_units)
        except (TypeError, ValueError):
            pass

    # Derive total_units from unit_mix if not explicitly set
    if "total_units" not in result and "unit_mix" in result:
        result["total_units"] = sum(u.get("count", 0) for u in result["unit_mix"])

    # vacancy_yr1 from rent roll current status
    vac_key = RENT_ROLL_FIELD_MAP["vacancy_yr1"]
    vac = extracted.get(vac_key)
    if vac is not None:
        try:
            vac_float = float(vac)
            # Normalise if stored as e.g. 7.5 rather than 0.075
            if vac_float > 1.0:
                vac_float /= 100.0
            result["vacancy_yr1"] = round(vac_float, 4)
        except (TypeError, ValueError):
            pass

    # Pass through any warnings from the extractor
    if "warnings" in extracted:
        result["_extraction_warnings"] = extracted["warnings"]

    return result


def map_om_to_form(extracted: dict) -> dict:
    """
    Convert Offering Memorandum data to property header form fields.

    Returns
    -------
    dict with property-level keys expected by the form:
      - property_name, total_units, year_built, asking_price, purchase_price, address
    """
    result: dict[str, Any] = {}

    for form_key, aliases in OM_FIELD_MAP.items():
        raw_value = _first_match(extracted, aliases)
        if raw_value is None:
            continue

        # Numeric coercion for expected numeric fields
        if form_key in ("total_units", "year_built"):
            try:
                result[form_key] = int(float(raw_value))
            except (TypeError, ValueError):
                result[form_key] = raw_value

        elif form_key in ("asking_price", "purchase_price"):
            try:
                result[form_key] = round(float(str(raw_value).replace(",", "").replace("$", "")), 2)
            except (TypeError, ValueError):
                result[form_key] = raw_value

        else:
            result[form_key] = raw_value

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _first_match(d: dict, keys: list[str]) -> Any:
    """Return the value of the first key found in dict d, or None."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _normalise_unit_mix(raw: list[dict]) -> list[dict]:
    """
    Ensure every unit mix entry has a consistent schema.
    Coerces types and fills in None for missing fields.
    Filters out junk rows (row numbers, headers, totals, unknowns).
    """
    normalised: list[dict] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue

        raw_type = str(entry.get("type") or "").strip()

        # Skip empty types
        if not raw_type:
            continue

        # Skip pure numeric types (row numbers extracted as unit types)
        if raw_type.replace(".", "").isdigit():
            continue

        # Skip header/footer rows and summary labels
        _lower = raw_type.lower()
        skip_keywords = [
            "total", "count", "unit type", "unknown", "header", "summary",
            "subtotal", "grand", "average", "vacant", "model", "employee",
            "office", "commercial", "n/a", "none",
        ]
        if any(kw in _lower for kw in skip_keywords):
            continue

        count = _safe_int(entry.get("count")) or 0
        # Skip entries with 0 units (likely artifacts)
        if count <= 0:
            continue

        norm: dict[str, Any] = {
            "type":              raw_type,
            "beds":              _safe_int(entry.get("beds")),
            "baths":             _safe_float(entry.get("baths")),
            "count":             count,
            "avg_rent":          _safe_float(entry.get("avg_rent")),
            "avg_market_rent":   _safe_float(entry.get("avg_market_rent")),
            "avg_sqft":          _safe_float(entry.get("avg_sqft")),
        }
        normalised.append(norm)
    return normalised


def _safe_int(val: Any) -> int | None:
    if val is None:
        return None
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return None


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return round(float(val), 2)
    except (TypeError, ValueError):
        return None
