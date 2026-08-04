"""
Deal Memo Generator — generates institutional-quality EFB deal memos using Kimi.

Provides both a full 1-page investment memo and a 3-sentence executive summary
suitable for the results panel in the EFB Mini-App frontend.
"""

from .kimi_client import KimiClient
from .prompts import (
    MEMO_SYSTEM,
    EXECUTIVE_SUMMARY_SYSTEM,
    build_memo_user_message,
)


class MemoGenerator:
    """
    Generates investment memos and executive summaries for EFB deals.

    Uses the sync KimiClient — intended for on-demand generation where
    the user explicitly clicks "Generate Memo" rather than streaming output.
    For streaming memo generation, use AsyncKimiClient directly.
    """

    def __init__(self):
        self.client = KimiClient()

    def generate(self, inputs: dict, model_results: dict) -> str:
        """
        Generate a complete institutional-quality deal memo.

        The memo follows the fixed Shieldstone EFB memo template:
        property overview, deal thesis, capital stack table, key metrics table
        (with T-Manual hurdles and RAG status), risk factors, and recommendation.

        Args:
            inputs: Raw model inputs dict. Expected keys include:
                - property_name (str)
                - city / location (str)
                - year_built / vintage (int)
                - unit_count / units (int)
                - purchase_price (float)
                - market_tier (str): "Gateway" | "Secondary" | "Tertiary"
                - a_bond_amount (float), a_bond_rate (float)
                - b_bond_amount (float, optional)
                - lp_equity (float, optional)
            model_results: Computed outputs dict. Expected keys include:
                - levered_irr (float, e.g. 0.162 for 16.2%)
                - equity_multiple (float, e.g. 1.85)
                - net_investor_irr (float)
                - yr1_dscr (float)
                - going_in_cap_rate (float)
                - price_per_unit (float)
                - annual_tax_savings (float)
                - cash_flows (list of annual NCF figures)

        Returns:
            Markdown string containing the full 1-page investment memo.

        Raises:
            openai.APIError: On Moonshot API failure.
            ValueError: If Kimi API key is not configured.
        """
        messages = [
            {"role": "system", "content": MEMO_SYSTEM},
            {"role": "user", "content": build_memo_user_message(inputs, model_results)},
        ]
        return self.client.chat(messages, max_tokens=3000)

    def generate_executive_summary(self, inputs: dict, model_results: dict) -> str:
        """
        Generate a 3-sentence executive summary for the results panel.

        Format enforced by the prompt:
          Sentence 1 — What the deal is (name, location, units, price).
          Sentence 2 — Key financials (IRR, EM, DSCR) vs. T-Manual hurdle.
          Sentence 3 — Go/no-go signal and primary supporting reason or risk.

        Returns plain prose — no markdown, no bullets, no headers.

        Args:
            inputs: Same structure as `generate()` inputs.
            model_results: Same structure as `generate()` model_results.

        Returns:
            A 3-sentence plain-text string suitable for display in the
            results panel without any markdown rendering.

        Raises:
            openai.APIError: On Moonshot API failure.
            ValueError: If Kimi API key is not configured.
        """
        user_content = build_memo_user_message(inputs, model_results)
        messages = [
            {"role": "system", "content": EXECUTIVE_SUMMARY_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Write the 3-sentence executive summary for this deal.\n\n"
                    + user_content
                ),
            },
        ]
        return self.client.chat(messages, max_tokens=200)
