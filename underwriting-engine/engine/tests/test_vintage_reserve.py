"""BL-18 vintage_reserve_floor tests.

Evan's Envy reserve line carried a stale '2007 vintage' rationale on a 2020 asset and a $250-vs-$300
inconsistency. The floor is set by the CONFIRMED year_built; a stated note value below the floor is
raised to it.
"""
import os
import sys
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import acq_engine as ax


def test_floor_by_vintage():
    assert ax.vintage_reserve_floor(2021).floor_per_unit == D("250")
    assert ax.vintage_reserve_floor(2020).floor_per_unit == D("250")
    assert ax.vintage_reserve_floor(2010).floor_per_unit == D("300")
    assert ax.vintage_reserve_floor(2000).floor_per_unit == D("300")
    assert ax.vintage_reserve_floor(1999).floor_per_unit == D("350")
    assert ax.vintage_reserve_floor(1975).floor_per_unit == D("350")


def test_pre2000_floor_override():
    r = ax.vintage_reserve_floor(1980, pre2000_floor=D("400"))
    assert r.floor_per_unit == D("400")


def test_note_below_floor_is_raised():
    # Evan's $250/u note on a 2010 asset -> floor is $300 -> raised.
    r = ax.vintage_reserve_floor(2010, note_value=D("250"))
    assert r.raised is True
    assert r.reconciled_value == D("300")
    assert "below" in r.reason


def test_note_at_or_above_floor_kept():
    r = ax.vintage_reserve_floor(2010, note_value=D("325"))
    assert r.raised is False
    assert r.reconciled_value == D("325")


def test_2020_asset_250_note_is_fine():
    # A $250/u note on a true 2020 asset is exactly the floor — not raised.
    r = ax.vintage_reserve_floor(2020, note_value=D("250"))
    assert r.raised is False
    assert r.reconciled_value == D("250")


def test_no_note_returns_floor():
    r = ax.vintage_reserve_floor(2005)
    assert r.note_value is None
    assert r.reconciled_value == D("300")
