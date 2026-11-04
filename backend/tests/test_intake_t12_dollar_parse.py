"""T-12 text extraction must read the whole dollar amount, not just the last digit.

Bug: _first_dollar used a greedy [^\\n]{0,80} before the number, so '$4,800,000'
was read as 0.0. Synthetic text only. No network, no secrets, no client data.
Unparseable or unsupported forms must come back blank (key absent), never a
made-up number.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intake.intake_service import _extract_t12_from_text  # noqa: E402


@pytest.mark.parametrize(
    "line, expected",
    [
        ("Gross Potential Rent  $4,800,000\n", 4800000.0),
        ("Gross Potential Rent  4,800,000\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000.55\n", 4800000.55),
        ("Gross Potential Rent  $4,800,000.00\n", 4800000.0),
        ("Gross Potential Rent: $ 4,800,000\n", 4800000.0),
        ("GPR 12\n", 12.0),
        ("Gross Potential Rent,$4,800,000,\n", 4800000.0),
    ],
)
def test_t12_reads_full_dollar_amount(line, expected):
    out = _extract_t12_from_text(line)
    assert out["gpr_annual"] == expected


def test_t12_line_with_two_amounts_reads_first_amount_whole():
    out = _extract_t12_from_text("Gross Potential Rent  $4,800,000  $5,950,000\n")
    assert out["gpr_annual"] == 4800000.0


def test_t12_multiple_fields_each_read_whole():
    text = (
        "Gross Potential Rent  $4,800,000\n"
        "Effective Gross Income  $4,512,345\n"
        "Insurance  $120,500\n"
    )
    out = _extract_t12_from_text(text)
    assert out["gpr_annual"] == 4800000.0
    assert out["egi_annual"] == 4512345.0
    assert out["insurance_annual"] == 120500.0


def test_t12_abbreviated_millions_is_blank_not_made_up():
    """The parser does not support '$4.8M'. It must not return 4.8 or 8.0."""
    out = _extract_t12_from_text("Gross Potential Rent  $4.8M\n")
    assert "gpr_annual" not in out


def test_t12_no_number_is_blank():
    out = _extract_t12_from_text("Gross Potential Rent  n/a\n")
    assert "gpr_annual" not in out


# ---------------------------------------------------------------------------
# Argon finding: refuse ambiguous or unsupported first-column values.
# The parser returns the first numeric token after the label only when it is an
# unambiguous supported amount. Otherwise blank. It never skips forward to a
# later column.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "Gross Potential Rent 2025 $4,800,000\n",
        "Gross Potential Rent FY2025 4,800,000\n",
        "Gross Potential Rent FY 2025 $4,800,000\n",
        "Gross Potential Rent 12/31/2025 $4,800,000\n",
        "Gross Potential Rent 2025-26 $4,800,000\n",
        "Gross Potential Rent Q3 $4,800,000\n",
        "Effective Gross Income 2025 $4,512,345\n",
    ],
)
def test_t12_intervening_numeric_metadata_is_blank(line):
    out = _extract_t12_from_text(line)
    assert "gpr_annual" not in out
    assert "egi_annual" not in out


@pytest.mark.parametrize(
    "line",
    [
        "Gross Potential Rent  $4.8MM\n",
        "Gross Potential Rent  $4.8 million\n",
        "Gross Potential Rent  4.8 Million\n",
        "Gross Potential Rent  $1.2B\n",
        "Gross Potential Rent  $1.2 billion\n",
        "Gross Potential Rent  $4.8mm\n",
        "Gross Potential Rent  $4.8 MM\n",
        "Gross Potential Rent  $4,800K\n",
        "Gross Potential Rent  $4,800 thousand\n",
    ],
)
def test_t12_multi_letter_or_spelled_magnitude_is_blank(line):
    out = _extract_t12_from_text(line)
    assert "gpr_annual" not in out


@pytest.mark.parametrize(
    "line",
    [
        "Gross Potential Rent  $4.8M  $5,950,000\n",
        "Gross Potential Rent  $4.8MM  $5,950,000\n",
        "Gross Potential Rent  4.8 Million  5,950,000\n",
        "Gross Potential Rent  $1.2B  $5,950,000\n",
        "Gross Potential Rent  12%  $5,950,000\n",
    ],
)
def test_t12_unsupported_first_column_never_falls_through_to_second(line):
    out = _extract_t12_from_text(line)
    assert "gpr_annual" not in out


def test_t12_valid_first_column_then_unsupported_second_uses_first():
    out = _extract_t12_from_text("Gross Potential Rent  $4,800,000  $5.9MM\n")
    assert out["gpr_annual"] == 4800000.0


def test_t12_unsupported_line_does_not_block_a_later_clean_line():
    text = "Gross Potential Rent  $4.8MM\nGross Potential Rent  $4,800,000\n"
    assert _extract_t12_from_text(text)["gpr_annual"] == 4800000.0


# ---------------------------------------------------------------------------
# Argon finding (a): a sign or parentheses must never be stripped so that a
# negative amount reads as a positive one. Negative where a negative is not
# valid comes back blank.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "Gross Potential Rent  -4,800,000\n",
        "Gross Potential Rent  -$4,800,000\n",
        "Gross Potential Rent  $-4,800,000\n",
        "Gross Potential Rent  - $4,800,000\n",
        "Gross Potential Rent - $4,800,000\n",
        "Gross Potential Rent  4,800,000-\n",
        "Gross Potential Rent  $4,800,000-\n",
        "Gross Potential Rent  $4,800,000 -\n",
        "Gross Potential Rent  (4,800,000)\n",
        "Gross Potential Rent  ($4,800,000)\n",
        "Gross Potential Rent  $(4,800,000)\n",
        "Gross Potential Rent  ( 4,800,000 )\n",
        "Gross Potential Rent  (4,800,000\n",
        "Gross Potential Rent  4,800,000)\n",
        "Gross Potential Rent  -4,800,000  $5,950,000\n",
        "Gross Potential Rent  (4,800,000)  $5,950,000\n",
    ],
)
def test_t12_negative_or_parenthesized_amount_is_blank(line):
    out = _extract_t12_from_text(line)
    assert "gpr_annual" not in out


def test_t12_negative_line_does_not_block_a_later_clean_line():
    text = "Gross Potential Rent  (4,800,000)\nGross Potential Rent  $4,800,000\n"
    assert _extract_t12_from_text(text)["gpr_annual"] == 4800000.0


# ---------------------------------------------------------------------------
# Argon finding (b): a figure with an unsupported unit or rate (per month, per
# unit, per sf) is not an annual dollar figure and must come back blank.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "Gross Potential Rent  $400,000 per month\n",
        "Gross Potential Rent  $400,000/month\n",
        "Gross Potential Rent  $400,000 / mo\n",
        "Gross Potential Rent  $400,000 monthly\n",
        "Gross Potential Rent  $400,000 PM\n",
        "Gross Potential Rent  $400,000 a month\n",
        "Gross Potential Rent  $1,200 per unit\n",
        "Gross Potential Rent  $1,200/unit\n",
        "Gross Potential Rent  $1,200 / unit\n",
        "Gross Potential Rent  $1,200 PUPM\n",
        "Gross Potential Rent  $1,200 per door\n",
        "Gross Potential Rent  $18.50 per sf\n",
        "Gross Potential Rent  $18.50/sf\n",
        "Gross Potential Rent  $18.50 / SF\n",
        "Gross Potential Rent  $18.50 psf\n",
        "Gross Potential Rent  $18.50 per square foot\n",
        "Gross Potential Rent  $18.50/sq ft\n",
        "Gross Potential Rent  $4,800,000 per quarter\n",
        "Gross Potential Rent  $4,800,000 per week\n",
        "Gross Potential Rent  $4,800,000 per day\n",
        "Gross Potential Rent  $4,800,000 per 1,000 sf\n",
        "Gross Potential Rent  $4,800,000 per acre\n",
        "Gross Potential Rent  $1,200 per bed\n",
        "Gross Potential Rent  $1,200 each\n",
        "Gross Potential Rent  $1,200 annualized\n",
    ],
)
def test_t12_unsupported_unit_or_rate_is_blank(line):
    out = _extract_t12_from_text(line)
    assert "gpr_annual" not in out


@pytest.mark.parametrize(
    "line",
    [
        "Gross Potential Rent  $400,000 per month  $4,800,000\n",
        "Gross Potential Rent  $1,200 per unit  $4,800,000\n",
        "Gross Potential Rent  $18.50 per sf  $4,800,000\n",
    ],
)
def test_t12_unit_first_column_never_falls_through_to_annual_column(line):
    out = _extract_t12_from_text(line)
    assert "gpr_annual" not in out


def test_t12_unit_label_before_the_number_is_blank():
    out = _extract_t12_from_text("Gross Potential Rent (per month) $400,000\n")
    assert "gpr_annual" not in out
    out = _extract_t12_from_text("Gross Potential Rent per unit $1,200\n")
    assert "gpr_annual" not in out


# ---------------------------------------------------------------------------
# Plain supported forms keep working, including an explicit annual unit and a
# clean annual amount followed by a separate clean column. A spaced hyphen before
# the number is ambiguous (separator or minus) so it is blank, tested above.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line, expected",
    [
        ("Gross Potential Rent  $4,800,000\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000 per year\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000 per annum\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000 /yr\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000 USD\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000 annual\n", 4800000.0),
        ("Gross Potential Rent: $4,800,000  (3.2%)\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000 (budget)\n", 4800000.0),
        ("Gross Potential Rent  $4,800,000  $4,700,000\n", 4800000.0),
    ],
)
def test_t12_clean_amounts_still_read(line, expected):
    assert _extract_t12_from_text(line)["gpr_annual"] == expected
