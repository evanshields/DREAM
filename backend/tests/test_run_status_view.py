"""Unit tests of run_status/view.py over the six frozen synthetic fixtures."""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_status.loader import list_run_ids, load_run  # noqa: E402
from run_status.view import build_summary, build_view, display_state  # noqa: E402

EXPECTED = {
    "run-clean-awaiting-cp1": "needs_human_check",
    "run-blocked-red-gate": "blocked",
    "run-stale-engine-commit": "stale",
    "run-missing-values": "needs_human_check",
    "run-in-progress": "in_progress",
    "run-failed": "failed",
}


def _clean():
    return copy.deepcopy(load_run("run-clean-awaiting-cp1"))


def test_six_fixtures_exist():
    assert sorted(EXPECTED) == list_run_ids()


@pytest.mark.parametrize("run_id,expected", sorted(EXPECTED.items()))
def test_display_state_per_fixture(run_id, expected):
    assert build_view(load_run(run_id))["display_state"] == expected


@pytest.mark.parametrize(
    "status,expected",
    [
        ("submitted", "in_progress"), ("routing", "in_progress"), ("analyzing", "in_progress"),
        ("synthesizing", "in_progress"), ("awaiting_input", "needs_input"),
        ("awaiting_cp1", "needs_human_check"), ("completed", "complete"),
        ("failed", "failed"), ("cancelled", "failed"), ("mystery", "failed"),
    ],
)
def test_status_mapping(status, expected):
    run = _clean()
    run["status"] = status
    assert display_state(run) == expected


def test_stale_with_red_gate_is_blocked():
    run = load_run("run-stale-engine-commit")
    run["gates"][0]["status"] = "red"
    assert display_state(run) == "blocked"


def test_failed_with_red_gate_is_failed():
    run = load_run("run-blocked-red-gate")
    run["status"] = "failed"
    assert display_state(run) == "failed"


def test_blocked_beats_in_progress():
    run = load_run("run-blocked-red-gate")
    run["status"] = "analyzing"
    assert display_state(run) == "blocked"


def test_stale_by_input_hash():
    run = _clean()
    run["current_inputs_hash"] = "fixture-hash-9999"
    assert display_state(run) == "stale"


def test_stale_beats_in_progress():
    run = load_run("run-in-progress")
    run["engine_commit"] = "other"
    assert display_state(run) == "stale"


def test_diagnostic_flag_only_for_blocked_and_stale():
    for run_id, expected in EXPECTED.items():
        view = build_view(load_run(run_id))
        assert view["values_are_diagnostic"] is (expected in ("blocked", "stale"))


def test_blocked_and_stale_still_show_values():
    for run_id in ("run-blocked-red-gate", "run-stale-engine-commit"):
        view = build_view(load_run(run_id))
        assert len(view["headline"]) > 0
        assert view["headline"][0]["value"] is not None


def test_null_stays_null():
    view = build_view(load_run("run-missing-values"))
    blanks = [h for h in view["headline"] if h["name"] != "Purchase price" and h["value"] is None]
    assert len(blanks) == 2
    for h in blanks:
        assert h["value"] is None
        assert h["value"] != 0 and h["value"] != ""
        assert h["blank_reason"]


def test_verified_zero_stays_zero():
    view = build_view(load_run("run-missing-values"))
    zero = [h for h in view["headline"] if h["name"] == "Reserve shortfall"][0]
    assert zero["value"] == 0 and zero["value"] is not None
    assert type(zero["value"]) is int
    assert zero["source_file"] and zero["source_pointer"]
    assert zero["blank_reason"] is None


def test_counts():
    assert build_view(load_run("run-missing-values"))["missing_value_count"] == 2
    assert build_view(load_run("run-clean-awaiting-cp1"))["missing_value_count"] == 0
    assert build_view(load_run("run-blocked-red-gate"))["red_gate_count"] == 1
    assert build_view(load_run("run-clean-awaiting-cp1"))["red_gate_count"] == 0
    assert build_view(load_run("run-in-progress"))["missing_value_count"] == 0


@pytest.mark.parametrize("run_id", sorted(EXPECTED))
def test_values_byte_identical(run_id):
    run = load_run(run_id)
    before = [json.dumps(h["value"]) for h in run["headline"]]
    view = build_view(copy.deepcopy(run))
    after = [json.dumps(h["value"]) for h in view["headline"]]
    assert before == after


def test_view_does_not_mutate_input():
    run = load_run("run-blocked-red-gate")
    snapshot = json.dumps(run, sort_keys=True)
    build_view(run)
    assert json.dumps(run, sort_keys=True) == snapshot


def test_awaiting_cp1_banner_has_no_advance_action():
    view = build_view(load_run("run-clean-awaiting-cp1"))
    assert "person must review" in view["state_sentence"]
    assert view["read_only"] is True


def test_summary_shape():
    s = build_summary(load_run("run-failed"))
    assert set(s) == {"run_id", "deal_label", "display_state", "synthetic"}
    assert s["display_state"] == "failed" and s["synthetic"] is True
