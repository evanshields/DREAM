"""BL-03 fee-bounds gate tests.

Fahd's B45 stayed at 0.05 (the EFB/Esplanade default) across 183 messages — an unread 5%
acquisition fee that overstated basis by ~$3M on a $74M deal. assert_fee_bounds turns that
silent carryover into a hard failure on the ACQ route.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import acq_engine as ax


def test_sentinel_fails_on_acq():
    r = ax.assert_fee_bounds(0.05, routing="ACQ")
    assert r.ok is False
    assert r.is_sentinel is True
    assert "sentinel" in r.reason.lower() or "0.05" in r.reason


def test_in_bounds_passes():
    assert ax.assert_fee_bounds(0.0075, routing="ACQ").ok is True
    assert ax.assert_fee_bounds(0.005, routing="ACQ").ok is True
    assert ax.assert_fee_bounds(0.01, routing="ACQ").ok is True


def test_out_of_bounds_fails():
    r = ax.assert_fee_bounds(0.02, routing="ACQ")  # 2% — above the 1% ceiling, not the sentinel
    assert r.ok is False
    assert r.is_sentinel is False
    assert "bounds" in r.reason.lower()


def test_override_bypasses():
    r = ax.assert_fee_bounds(0.05, routing="ACQ", override=True)
    assert r.ok is True
    assert r.is_sentinel is True  # still flagged AS the sentinel, but allowed by override


def test_efb_route_allows_5pct():
    # 5% IS the EFB default — must not fail on the EFB route.
    assert ax.assert_fee_bounds(0.05, routing="EFB").ok is True
