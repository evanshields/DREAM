"""Gap tests for the intake percentage helper `_first_pct` in intake/intake_service.py.

Safe behavior asserted: ambiguous, negative or unsupported percent readings return None
(a blank), and clean readings return the plain fraction (5% -> 0.05). Fabricated numbers are
worse than blanks.

Tests that fail on current code are marked xfail(strict=True) so the suite stays green and
flips loudly once the helper is fixed. Test file only: no product code change.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intake.intake_service import _first_pct  # noqa: E402


# --- Passing controls: clean cases ---------------------------------------------------------

@pytest.mark.parametrize(
    "text,labels,expected",
    [
        ("Vacancy 5%", ("vacancy",), 0.05),
        ("Management Fee 3%", ("management fee",), 0.03),
    ],
)
def test_clean_single_digit_values_read_plainly(text, labels, expected):
    assert _first_pct(text, *labels) == pytest.approx(expected)


# The regex gap before the number is greedy, so it swallows leading digits of the value.
# These are the clean cases the task named (5.0 %, 95%) plus two more, and they read wrong today.
@pytest.mark.xfail(strict=True, reason="pct gap: greedy gap eats leading digits so 5.0 % reads as 0.0")
def test_clean_spaced_decimal_reads_plainly():
    assert _first_pct("Vacancy: 5.0 %", "vacancy") == pytest.approx(0.05)


@pytest.mark.xfail(strict=True, reason="pct gap: greedy gap eats leading digits so 95% reads as 5%")
def test_clean_occupancy_95_reads_plainly():
    assert _first_pct("Occupancy 95%", "occupancy") == pytest.approx(0.95)


@pytest.mark.xfail(strict=True, reason="pct gap: greedy gap eats leading digits so 95.0 % reads as 0.0")
def test_clean_occupancy_95_spaced_reads_plainly():
    assert _first_pct("Occupancy: 95.0 %", "occupancy") == pytest.approx(0.95)


@pytest.mark.xfail(strict=True, reason="pct gap: greedy gap eats leading digits so 7.25% reads as 5%")
def test_clean_two_decimal_reads_plainly():
    assert _first_pct("Vacancy 7.25%", "vacancy") == pytest.approx(0.0725)


@pytest.mark.xfail(strict=True, reason="pct gap: greedy gap eats leading digits so 12% reads as 2%")
def test_clean_two_digit_reads_plainly():
    assert _first_pct("Vacancy 12%", "vacancy") == pytest.approx(0.12)


def test_no_label_returns_none():
    assert _first_pct("Rent 5%", "vacancy") is None


def test_label_without_percent_returns_none():
    assert _first_pct("Vacancy 5 units", "vacancy") is None


def test_second_label_used_when_first_absent():
    assert _first_pct("Physical Vacancy 4%", "vacancy rate", "physical vacancy") == pytest.approx(0.04)


@pytest.mark.parametrize("cell", ["Vacancy (5.0)%", "Vacancy (5)%"])
def test_parenthesized_trailing_paren_form_is_blank(cell):
    # "(5.0)%" and "(5)%" do not match the plain pattern, so they are already blank. Control.
    assert _first_pct(cell, "vacancy") is None


# --- Negative or parenthesized percents ----------------------------------------------------

@pytest.mark.xfail(strict=True, reason="pct gap: leading minus sign is dropped so -5% reads as +5%")
def test_negative_percent_is_blank():
    assert _first_pct("Vacancy -5%", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: accounting parentheses (5%) read as positive 5%")
def test_parenthesized_percent_is_blank():
    assert _first_pct("Vacancy (5%)", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: parenthesized decimal (5.0 %) reads as positive")
def test_parenthesized_percent_with_space_is_blank():
    assert _first_pct("Vacancy (5.0 %)", "vacancy") is None


# --- Per-month or per-unit rates read as annual --------------------------------------------

@pytest.mark.xfail(strict=True, reason="pct gap: '% per month' rate read as an annual rate")
def test_per_month_rate_is_blank():
    assert _first_pct("Vacancy 0.5% per month", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: '% / mo' rate read as an annual rate")
def test_slash_mo_rate_is_blank():
    assert _first_pct("Management Fee 0.25% / mo", "management fee") is None


@pytest.mark.xfail(strict=True, reason="pct gap: '% per unit' value read as an annual rate")
def test_per_unit_rate_is_blank():
    assert _first_pct("Management Fee 2% per unit", "management fee") is None


# --- Percent-like numbers that are really a year or a count --------------------------------

@pytest.mark.xfail(strict=True, reason="pct gap: 2024% accepted as 20.24 instead of blank")
def test_year_like_value_is_blank():
    assert _first_pct("Vacancy 2024%", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: values above 100% (count-like 250%) accepted")
def test_over_100_percent_is_blank():
    assert _first_pct("Vacancy 250%", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: thousands separator truncated so 1,250% reads as 250%")
def test_comma_grouped_count_is_blank():
    assert _first_pct("Vacancy 1,250%", "vacancy") is None


# --- Unsupported first token with a later valid column -------------------------------------

@pytest.mark.xfail(strict=True, reason="pct gap: n/a first column skipped and a later column is used")
def test_na_first_column_does_not_borrow_later_column():
    assert _first_pct("Vacancy n/a   4.8%", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: dash placeholder first column skipped, later column used")
def test_dash_first_column_does_not_borrow_later_column():
    assert _first_pct("Vacancy --   Prior Year 6%", "vacancy") is None


@pytest.mark.xfail(strict=True, reason="pct gap: TBD first token skipped, later column used")
def test_tbd_first_token_does_not_borrow_later_column():
    assert _first_pct("Vacancy TBD   5%", "vacancy") is None
