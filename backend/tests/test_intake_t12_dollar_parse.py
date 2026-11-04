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
