"""Wave C-v1 — Wave 0 acceptance tests. Deterministic routing + BL-17 critical-input capture, NO
LLM: ready when all three inputs present + ACQ; AWAITING_INPUT with one blocking OpenQuestion per
missing input; ambiguous/EFB routing forces a blocking routing decision (never guesses)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs.wave0 import run_wave0  # noqa: E402
from jobs.contracts import JobRecord  # noqa: E402


def _job():
    return JobRecord(job_id="J1", deal_id="d1", routing="ACQ")


def test_ready_when_all_inputs_present_and_acq():
    out = run_wave0(_job(), {
        "routing": "ACQ",
        "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
    })
    assert out["ready"] is True
    assert out["routing"] == "ACQ"
    assert out["critical_inputs"] == {"purchase_price": 55000000.0, "hold_years": 7, "exit_cap": 0.06}


def test_flat_aliases_are_accepted():
    out = run_wave0(_job(), {"price": 55000000, "hold_period": 10, "exit_cap_rate": 0.0625})
    assert out["ready"] is True
    assert out["critical_inputs"]["hold_years"] == 10
    assert out["critical_inputs"]["exit_cap"] == 0.0625


def test_missing_input_blocks_with_open_question_per_missing():
    out = run_wave0(_job(), {"routing": "ACQ", "critical_inputs": {"purchase_price": 55000000}})
    assert out["ready"] is False
    fields = {q.field for q in out["awaiting"]}
    assert "meta.critical_inputs.hold_years" in fields
    assert "meta.critical_inputs.exit_cap" in fields
    assert all(q.blocking for q in out["awaiting"])


def test_no_inputs_blocks_all_three():
    out = run_wave0(_job(), {"routing": "ACQ"})
    assert out["ready"] is False
    missing = {q.field for q in out["awaiting"]}
    assert missing == {
        "meta.critical_inputs.purchase_price",
        "meta.critical_inputs.hold_years",
        "meta.critical_inputs.exit_cap",
    }


def test_routing_defaults_to_acq_with_basis():
    out = run_wave0(_job(), {
        "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
    })
    assert out["ready"] is True
    assert out["routing"] == "ACQ"
    assert "v1 forces ACQ" in out["routing_basis"]


def test_efb_signal_forces_blocking_routing_question():
    out = run_wave0(_job(), {
        "notes": "This is a tax-exempt bond workforce housing deal (EFB).",
        "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
    })
    assert out["ready"] is False
    routing_q = [q for q in out["awaiting"] if q.field == "meta.routing"]
    assert len(routing_q) == 1
    assert routing_q[0].blocking is True
    assert routing_q[0].options == ["ACQ", "EFB"]
    assert out["routing"] is None


def test_explicit_efb_routing_not_auto_supported():
    out = run_wave0(_job(), {
        "routing": "EFB",
        "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
    })
    assert out["ready"] is False
    assert any(q.field == "meta.routing" for q in out["awaiting"])
