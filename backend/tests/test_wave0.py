"""Wave C — Wave 0 acceptance tests. Deterministic routing + per-route critical-input capture, NO
LLM. ACQ: ready when the BL-17 trio present; AWAITING_INPUT with one blocking OpenQuestion per
missing input. EFB (the unlock): explicit routing=EFB is ACCEPTED and gates on stabilized_noi;
an AMBIGUOUS EFB signal still forces a blocking routing decision (never guesses)."""
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
    assert out["routing_basis"].startswith("default:ACQ")


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


def test_ambiguous_routing_defers_critical_input_questions():
    """When routing is ambiguous, the ONLY blocking question is routing — per-route critical
    inputs are gated on the resume (asking the ACQ trio on a maybe-EFB deal is wrong)."""
    out = run_wave0(_job(), {"notes": "workforce housing play"})  # no routing, no inputs
    assert out["ready"] is False
    assert [q.field for q in out["awaiting"]] == ["meta.routing"]


# ---- the EFB unlock: explicit routing=EFB is accepted -------------------------------------

def test_explicit_efb_routing_accepted_with_stabilized_noi():
    out = run_wave0(_job(), {
        "routing": "EFB",
        "critical_inputs": {"stabilized_noi": 4448271.31},
    })
    assert out["ready"] is True
    assert out["routing"] == "EFB"
    assert out["routing_basis"] == "explicit:EFB"
    assert out["critical_inputs"]["stabilized_noi"] == 4448271.31
    assert out["critical_inputs"]["hold_years"] is None  # optional; engine defaults 10


def test_efb_missing_stabilized_noi_blocks_with_one_question():
    out = run_wave0(_job(), {"routing": "EFB"})
    assert out["ready"] is False
    assert [q.field for q in out["awaiting"]] == ["meta.critical_inputs.stabilized_noi"]
    assert all(q.blocking for q in out["awaiting"])


def test_efb_non_positive_noi_treated_as_missing():
    out = run_wave0(_job(), {"routing": "EFB", "critical_inputs": {"stabilized_noi": 0}})
    assert out["ready"] is False
    assert [q.field for q in out["awaiting"]] == ["meta.critical_inputs.stabilized_noi"]


# ---- false-positive / true-positive substring-vs-word-boundary regression (Phase 4c) ----------

def test_efb_signal_false_positive_perhaps_does_not_block():
    """'hap' must NOT match inside 'perhaps' — naked substring test misfired here."""
    out = run_wave0(_job(), {
        "notes": "we will perhaps renovate the property",
        "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
    })
    assert out["ready"] is True
    assert out["routing"] == "ACQ"
    assert "awaiting" not in out


def test_efb_signal_false_positive_shenandoah_does_not_block():
    """'noah' must NOT match inside 'Shenandoah' — naked substring test misfired here."""
    out = run_wave0(_job(), {
        "deal_name": "Shenandoah Apartments",
        "critical_inputs": {"purchase_price": 55000000, "hold_years": 7, "exit_cap": 0.06},
    })
    assert out["ready"] is True
    assert out["routing"] == "ACQ"


def test_efb_signal_true_positive_hap_still_blocks():
    """A standalone 'HAP' token still forces the blocking routing question."""
    out = run_wave0(_job(), {"notes": "HAP contract in place"})
    assert out["ready"] is False
    routing_q = [q for q in out["awaiting"] if q.field == "meta.routing"]
    assert len(routing_q) == 1
    assert routing_q[0].blocking is True
    assert out["routing"] is None


def test_efb_signal_true_positive_noah_still_blocks():
    """A standalone 'NOAH' token still forces the blocking routing question."""
    out = run_wave0(_job(), {"notes": "NOAH preservation deal"})
    assert out["ready"] is False
    routing_q = [q for q in out["awaiting"] if q.field == "meta.routing"]
    assert len(routing_q) == 1
    assert routing_q[0].blocking is True
    assert out["routing"] is None


def test_efb_signal_true_positive_plural_bonds_still_blocks():
    """PLURAL forms ('tax-exempt bondS') are the most common phrasing in deal prose — the
    word-boundary regex must not drop them (regression: a bare trailing \\b silently
    mis-routed plural-phrased EFB deals to ACQ)."""
    out = run_wave0(_job(), {"notes": "financed with tax-exempt bonds"})
    assert out["ready"] is False
    routing_q = [q for q in out["awaiting"] if q.field == "meta.routing"]
    assert len(routing_q) == 1
    assert routing_q[0].blocking is True
    assert out["routing"] is None


def test_efb_signal_true_positive_plural_4pct_bonds_still_blocks():
    """'4% bonds' (plural) still forces the blocking routing question."""
    out = run_wave0(_job(), {"notes": "structure uses 4% bonds with a HFA issuer"})
    assert out["ready"] is False
    assert [q for q in out["awaiting"] if q.field == "meta.routing"]


def test_efb_optional_scalars_ride_along():
    out = run_wave0(_job(), {
        "routing": "EFB",
        "critical_inputs": {
            "stabilized_noi": 4448271.31, "hold_years": 10, "bond_rate": 0.05,
            "target_dscr": 1.15, "amortization_years": 35,
            "annual_property_tax_exempted": 900000,
        },
    })
    assert out["ready"] is True
    ci = out["critical_inputs"]
    assert ci == {
        "stabilized_noi": 4448271.31, "hold_years": 10, "bond_rate": 0.05,
        "target_dscr": 1.15, "amortization_years": 35,
        "annual_property_tax_exempted": 900000.0,
    }
    # the slices' locked contract: every critical-input value is a scalar
    assert all(isinstance(v, (int, float)) for v in ci.values())
