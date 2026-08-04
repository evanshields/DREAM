"""Wave B.2 tests — the ACQ deal validator (GREEN/AMBER/RED vs V2.0 acquisitions standards)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acq_validator import validate_acq, summarize  # noqa: E402


def _by_field(flags):
    return {f.field: f for f in flags}


def test_strong_deal_all_green():
    hm = {"irr": 0.2251, "equity_multiple": 2.72, "dscr_series": [1.23, 1.33, 1.41, 1.49, 1.54, 1.35, 1.39]}
    flags = validate_acq(hm, market_tier="SECONDARY", going_in_cap=0.0702, exit_cap=0.06,
                         acquisition_fee_pct=0.0075)
    # exit cap 0.06 < entry 0.0702 -> that one is RED (compression); the rest GREEN.
    bf = _by_field(flags)
    assert bf["irr"].status == "GREEN"
    assert bf["equity_multiple"].status == "GREEN"
    assert bf["acquisition_fee_pct"].status == "GREEN"
    assert bf["dscr"].status == "GREEN"


def test_irr_below_tier_hurdle_is_red():
    flags = validate_acq({"irr": 0.12, "equity_multiple": 1.6}, market_tier="SECONDARY")
    assert _by_field(flags)["irr"].status == "RED"  # 12% < 16% Secondary hurdle


def test_irr_within_2pts_is_amber():
    flags = validate_acq({"irr": 0.15}, market_tier="SECONDARY")  # 15% vs 16% hurdle
    assert _by_field(flags)["irr"].status == "AMBER"


def test_gateway_tier_lower_hurdle():
    # 14.5% clears Gateway (14%) but not Secondary (16%)
    assert _by_field(validate_acq({"irr": 0.145}, market_tier="GATEWAY"))["irr"].status == "GREEN"
    assert _by_field(validate_acq({"irr": 0.145}, market_tier="SECONDARY"))["irr"].status in ("AMBER", "RED")


def test_exit_below_entry_is_red():
    flags = validate_acq({"irr": 0.2}, going_in_cap=0.06, exit_cap=0.055)
    assert _by_field(flags)["exit_cap"].status == "RED"


def test_exit_ge_entry_is_green():
    flags = validate_acq({"irr": 0.2}, going_in_cap=0.06, exit_cap=0.065)
    assert _by_field(flags)["exit_cap"].status == "GREEN"


def test_dscr_below_floor_flags_red_per_year():
    # Year 3 (refi phase, floor 1.25) at 1.10 -> RED
    hm = {"dscr_series": [1.20, 1.30, 1.10, 1.40]}
    flags = validate_acq(hm, bridge_io_years=2)
    bf = _by_field(flags)
    assert "dscr_year3" in bf and bf["dscr_year3"].status == "RED"
    # bridge-phase year 1 at 1.20 is above the 1.10 bridge floor -> not flagged
    assert "dscr_year1" not in bf


def test_acq_fee_sentinel_is_red():
    flags = validate_acq({"irr": 0.2}, acquisition_fee_pct=0.05)  # EFB sentinel on ACQ
    assert _by_field(flags)["acquisition_fee_pct"].status == "RED"


def test_summary_pass_fail():
    assert summarize(validate_acq({"irr": 0.2251, "equity_multiple": 2.72}))["pass_fail"] == "PASS"
    assert summarize(validate_acq({"irr": 0.10}, market_tier="SECONDARY"))["pass_fail"] == "FAIL"
    assert summarize(validate_acq({"irr": 0.15}, market_tier="SECONDARY"))["pass_fail"] == "REVIEW"


def test_flag_as_dict_shape():
    flags = validate_acq({"irr": 0.2251})
    d = flags[0].as_dict()
    assert set(d.keys()) >= {"field", "status", "message", "benchmark", "current_value", "section"}
