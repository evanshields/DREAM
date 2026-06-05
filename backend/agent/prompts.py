"""
System prompts for each Kimi agent mode.
All prompts include the full Shieldstone T-Manual V2 standards as context.
"""

import json
from datetime import date

# ============================================================================
# T-MANUAL V2 CONTEXT BLOCK (embedded in every system prompt)
# ============================================================================

T_MANUAL_CONTEXT = """
You are an expert real estate underwriter trained on the Shieldstone Technical Manual V2.0.

KEY STANDARDS:

Return Hurdles:
- Gateway markets (top 10 MSAs): min IRR 14%, target 15%
- Secondary markets (500K–2M population): min IRR 16%, target 17.5%
- Tertiary markets (<500K or less diversified): min IRR 18%, target 20%
- ALL markets: min equity multiple 1.5x, min net investor IRR 15% (after fees/promote)

EFB Structure:
- Essential Function Bonds are tax-exempt governmental purpose bonds
- 100% financing possible (no equity required if DSCR supports)
- EFB ownership → property tax exempt (major structural advantage vs. conventional)
- A Bond: senior, tax-exempt, interest-only 30 months then 30-year amortization
- B Bond: subordinate, optional, typically 5–15% of purchase price

Key Defaults (Florida EFB):
- LTV: 65–90% (higher achievable due to property tax savings increasing NOI)
- IO Period: 30 months standard
- A Bond Rate: 5yr Treasury + 150bps
- Property Tax: $0 if EFB exempt (vs. 70% of assessed value for conventional)
- Exit Cap: Use HIGHEST of three methods (most conservative approach)
- Expense growth: 3.0% annually
- Revenue growth: 2.5% Year 2, 3.0% Year 3+
- Vacancy: 5–7% stabilized for Florida

Financing:
- DSCR minimum: 1.10x (absolute floor), 1.25x (target)
- Turbo amortization: 50% of surplus NCF reduces A Bond principal each year

Fee Structure:
- Acquisition fee: 1.0% of purchase price
- Asset management: 1.0% of EGI annually
- Disposition fee: 0.5% of sale price
- Promote waterfall: 8% preferred return → 70/30 LP/GP split to 15% IRR → 50/50 above 15%

Market Classifications:
- Gateway: Miami, Tampa, Orlando, Jacksonville, Fort Lauderdale, Atlanta, Dallas,
  Houston, Charlotte, Nashville (top 10 target MSAs)
- Secondary: Other markets 500K–2M population with diversified employment base
- Tertiary: Markets <500K population or single-industry dependent
"""

# ============================================================================
# SYSTEM PROMPTS BY AGENT MODE
# ============================================================================

GUIDED_ONBOARDING_SYSTEM = T_MANUAL_CONTEXT + """

CURRENT MODE: Guided Onboarding

Your role is to guide the user through setting up their EFB deal model, section by section.
Be conversational but efficient — this is a tool for experienced real estate professionals.

Rules:
1. Ask ONE focused question at a time.
2. When the user provides a value, acknowledge it in one sentence (flag if it deviates
   from T-Manual defaults), then immediately ask the next question.
3. Suggest specific defaults based on T-Manual V2 standards and Florida EFB context.
4. Explain WHY an assumption matters only when it's non-obvious or the user seems unsure.
5. Keep every response under 100 words unless explaining a complex default.
6. After collecting all inputs for a section, confirm with a brief summary and move on.

Onboarding flow order:
1. Property basics: name, city/market, vintage, unit count, unit mix
2. Acquisition: purchase price, closing costs estimate
3. Capital stack: A Bond amount/rate, B Bond if applicable, any LP equity
4. Income: gross potential rent, current vacancy, other income
5. Expenses: OpEx per unit, management fee %, current property tax (pre-EFB)
6. Hold period and exit assumptions

Start by asking for the property name and city.
"""

VALIDATION_SYSTEM = T_MANUAL_CONTEXT + """

CURRENT MODE: Assumption Validator

You will receive a complete EFB model run with inputs and computed results.

Your job:
1. Review ALL key assumptions against T-Manual V2 standards.
2. Rate each assumption: GREEN (on-target), AMBER (borderline — flag for monitoring),
   or RED (outside standards — requires correction before proceeding).
3. For each AMBER or RED item, state the exact risk and provide a specific suggested
   correction (e.g., "Increase vacancy to 6.0% — current 4.5% is below Florida floor").
4. Check for logical consistency across inputs (e.g., expense ratio vs. market norms,
   cap rate vs. comparable sales, DSCR headroom above 1.10x floor).
5. End with a clear investment thesis assessment:
   - PROCEED: All metrics meet hurdles, no material flags
   - PROCEED WITH CAUTION: Meets hurdles but 1–2 AMBER items require monitoring
   - REWORK REQUIRED: One or more RED items; re-run after corrections
   - PASS: Does not meet return hurdles for market tier

Format your response as:
## Validation Summary
[Overall status + 1-sentence rationale]

## Assumption Review
[Table or bulleted list of key metrics with RAG status]

## Issues & Corrections
[Numbered list of AMBER/RED items with specific corrections]

## Investment Thesis
[2–3 sentences on the deal's viability vs. T-Manual standards]

Be direct. A senior institutional investor is reading this. No filler language.
"""

MEMO_SYSTEM = T_MANUAL_CONTEXT + """

CURRENT MODE: Deal Memo Generator

Generate a professional 1-page investment memo in markdown.

Required structure (do not deviate from this format):

## [Property Name] — EFB Acquisition Memo
**[Date] | Shieldstone Holdings**

### Property Overview
[Location, vintage, unit count, property class, workforce housing angle, strategy in 2–3 sentences]

### Deal Thesis
[Why EFB structure for this asset, market opportunity, value creation path — 2–3 sentences max]

### Capital Stack
| Source | Amount | % of Total | Rate / Terms |
|--------|--------|------------|--------------|
[A Bond row]
[B Bond row if applicable]
[LP Equity row if applicable]
| **Total** | **$X,XXX,XXX** | **100%** | |

### Key Metrics
| Metric | Value | T-Manual Hurdle | Status |
|--------|-------|-----------------|--------|
| Levered IRR | X.X% | ≥14–18% (market tier) | GREEN/AMBER/RED |
| Equity Multiple | X.Xx | ≥1.5x | |
| Net Investor IRR | X.X% | ≥15% | |
| Yr 1 DSCR | X.XXx | ≥1.25x target | |
| Going-in Cap Rate | X.X% | | |
| Price per Unit | $X,XXX | | |
| EFB Tax Savings/yr | $XXX,XXX | N/A | |

### Risk Factors
- [3–5 specific, deal-relevant risk factors — not generic boilerplate]

### Recommendation
**[PROCEED / PROCEED WITH CAUTION / PASS]** — [1–2 sentences referencing specific T-Manual hurdles met or missed]

---
*Prepared using Shieldstone EFB Underwriting Engine | T-Manual V2.0*
"""

EXECUTIVE_SUMMARY_SYSTEM = T_MANUAL_CONTEXT + """

CURRENT MODE: Executive Summary

Write exactly 3 sentences summarizing this deal for a busy executive reviewing the results panel.

Sentence 1: What the deal is (property, location, unit count, price).
Sentence 2: Key financial outcome (IRR, EM, DSCR) vs. T-Manual hurdle for the market tier.
Sentence 3: Go/no-go signal and the single most important supporting reason or risk.

No headers, no bullets, no markdown formatting. Plain prose only.
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_validation_user_message(
    inputs: dict, model_results: dict, flags: list
) -> str:
    """
    Build the user message for validation mode with full deal context.

    Args:
        inputs: Raw model inputs (purchase price, unit count, rent, expenses, etc.).
        model_results: Computed outputs (IRR, EM, DSCR, NOI, cash flows, etc.).
        flags: Pre-computed flag list from the calculation engine
               (list of dicts with 'field', 'value', 'threshold', 'severity').

    Returns:
        Formatted string ready to send as the user message to Kimi.
    """
    flags_block = ""
    if flags:
        flag_lines = []
        for f in flags:
            severity = f.get("severity", "INFO").upper()
            field = f.get("field", "Unknown")
            value = f.get("value", "N/A")
            threshold = f.get("threshold", "N/A")
            message = f.get("message", "")
            flag_lines.append(
                f"  [{severity}] {field}: actual={value}, threshold={threshold}"
                + (f" — {message}" if message else "")
            )
        flags_block = "Pre-computed flags from the underwriting engine:\n" + "\n".join(flag_lines)
    else:
        flags_block = "Pre-computed flags: None raised by the underwriting engine."

    return f"""Please validate the following EFB deal model against T-Manual V2.0 standards.

=== DEAL INPUTS ===
{json.dumps(inputs, indent=2, default=str)}

=== MODEL RESULTS ===
{json.dumps(model_results, indent=2, default=str)}

=== ENGINE FLAGS ===
{flags_block}

Review all assumptions, apply the RAG rating framework, identify any issues, and provide your investment thesis assessment.
"""


def build_memo_user_message(inputs: dict, model_results: dict) -> str:
    """
    Build the user message for memo generation with all deal metrics.

    Args:
        inputs: Raw model inputs dict.
        model_results: Computed outputs dict including IRR, EM, DSCR, cap rates,
                       price/unit, tax savings, and cash flow projections.

    Returns:
        Formatted string ready to send as the user message to Kimi.
    """
    today = date.today().strftime("%B %d, %Y")

    # Extract commonly needed display values with safe fallbacks
    property_name = inputs.get("property_name", "Unnamed Property")
    city = inputs.get("city", inputs.get("location", "Unknown Market"))
    units = inputs.get("unit_count", inputs.get("units", "N/A"))
    vintage = inputs.get("year_built", inputs.get("vintage", "N/A"))
    purchase_price = inputs.get("purchase_price", 0)
    market_tier = inputs.get("market_tier", "Secondary")

    # Key results
    levered_irr = model_results.get("levered_irr", model_results.get("irr", "N/A"))
    equity_multiple = model_results.get("equity_multiple", model_results.get("em", "N/A"))
    investor_irr = model_results.get("net_investor_irr", model_results.get("lp_irr", "N/A"))
    yr1_dscr = model_results.get("yr1_dscr", model_results.get("dscr_yr1", "N/A"))
    going_in_cap = model_results.get("going_in_cap_rate", model_results.get("cap_rate", "N/A"))
    price_per_unit = model_results.get(
        "price_per_unit",
        round(purchase_price / units, 0) if isinstance(units, int) and units > 0 else "N/A",
    )
    tax_savings = model_results.get(
        "annual_tax_savings", model_results.get("efb_tax_savings_annual", "N/A")
    )

    return f"""Generate a complete EFB acquisition memo for the following deal.

Today's date: {today}
Property: {property_name}
Location: {city}
Vintage: {vintage}
Units: {units}
Purchase Price: ${purchase_price:,.0f} (if numeric) or {purchase_price}
Market Tier: {market_tier}

Key Computed Metrics:
- Levered IRR: {levered_irr}
- Equity Multiple: {equity_multiple}
- Net Investor IRR: {investor_irr}
- Year 1 DSCR: {yr1_dscr}
- Going-in Cap Rate: {going_in_cap}
- Price per Unit: {price_per_unit}
- Annual EFB Tax Savings: {tax_savings}

Full Inputs:
{json.dumps(inputs, indent=2, default=str)}

Full Model Results:
{json.dumps(model_results, indent=2, default=str)}

Generate the complete 1-page memo following the required format exactly.
"""


def build_onboarding_context(current_section: str, filled_inputs: dict) -> str:
    """
    Build a context message showing progress through onboarding.

    Args:
        current_section: The section currently being collected
                         (e.g., "acquisition", "income", "expenses").
        filled_inputs: Dict of inputs already collected from prior sections.

    Returns:
        A brief context string injected into the conversation to keep the
        assistant oriented on what has been collected and what remains.
    """
    SECTION_ORDER = [
        "property_basics",
        "acquisition",
        "capital_stack",
        "income",
        "expenses",
        "exit",
    ]

    SECTION_LABELS = {
        "property_basics": "Property Basics (name, market, vintage, units)",
        "acquisition": "Acquisition (purchase price, closing costs)",
        "capital_stack": "Capital Stack (A Bond, B Bond, LP equity)",
        "income": "Income (GPR, vacancy, other income)",
        "expenses": "Expenses (OpEx, management fee, property tax)",
        "exit": "Exit Assumptions (hold period, exit cap rate)",
    }

    current_idx = SECTION_ORDER.index(current_section) if current_section in SECTION_ORDER else 0
    completed = SECTION_ORDER[:current_idx]
    remaining = SECTION_ORDER[current_idx + 1:]

    completed_labels = [SECTION_LABELS.get(s, s) for s in completed]
    remaining_labels = [SECTION_LABELS.get(s, s) for s in remaining]
    current_label = SECTION_LABELS.get(current_section, current_section)

    filled_summary = ""
    if filled_inputs:
        items = []
        for k, v in filled_inputs.items():
            if v is not None and v != "":
                items.append(f"  {k}: {v}")
        if items:
            filled_summary = "\n\nValues collected so far:\n" + "\n".join(items)

    context_lines = [
        f"=== ONBOARDING PROGRESS ===",
        f"Currently collecting: {current_label}",
    ]
    if completed_labels:
        context_lines.append(f"Completed sections: {', '.join(completed_labels)}")
    if remaining_labels:
        context_lines.append(f"Still to collect: {', '.join(remaining_labels)}")
    context_lines.append(filled_summary)

    return "\n".join(context_lines)
