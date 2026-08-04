"""A1.6 acceptance tests — the BL safety gates fire server-side (compute path), not just in the
populator (Excel path). Proves fee-bounds (BL-03), unit-count (BL-01), deal-identity (BL-02), and
formula-integrity (BL-07) produce structured, non-collapsible verdicts in spec.qa.* and that RED
gates set summary.ok=False with the gate named in summary.blocking (HOTL hard-stop signal)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_gates import run_gates  # noqa: E402


def _spec(routing="ACQ", fee_cell="B45", fee=0.0075, identity_match=True):
    return {
        "meta": {
            "deal_name": "Esplanade", "slug": "esplanade", "routing": routing, "mode": "HOTL",
            "deal_identity": {"match": identity_match, "reasons": [] if identity_match else ["B2 mismatch"]},
        },
        "qa": {},
        "cells": [
            {"cell": "B10", "value": 34000000, "source": "OM"},
            {"cell": fee_cell, "value": fee, "source": "fee band"},
        ],
    }


def test_acq_fee_sentinel_blocks():
    spec, summary = run_gates(_spec(routing="ACQ", fee=0.05))
    assert summary.ok is False
    assert "fee_bounds" in summary.blocking
    assert spec["qa"]["fee_bounds"]["ok"] is False
    assert spec["qa"]["fee_bounds"]["is_sentinel"] is True


def test_acq_fee_in_bounds_passes():
    spec, summary = run_gates(_spec(routing="ACQ", fee=0.0075))
    assert spec["qa"]["fee_bounds"]["ok"] is True
    assert "fee_bounds" not in summary.blocking


def test_acq_fee_override_passes_even_at_sentinel():
    spec, summary = run_gates(_spec(routing="ACQ", fee=0.05), fee_override=True)
    assert spec["qa"]["fee_bounds"]["ok"] is True
    assert spec["qa"]["fee_bounds"]["override"] is True
    assert "fee_bounds" not in summary.blocking


def test_efb_fee_5pct_passes_on_b39():
    # On the EFB route 5% IS the default; fee cell is B39.
    spec, summary = run_gates(_spec(routing="EFB", fee_cell="B39", fee=0.05))
    assert spec["qa"]["fee_bounds"]["ok"] is True
    assert "fee_bounds" not in summary.blocking


def test_deal_identity_mismatch_blocks():
    spec, summary = run_gates(_spec(identity_match=False))
    assert summary.ok is False
    assert "deal_identity" in summary.blocking


def test_unit_count_off_second_source_blocks():
    spec, summary = run_gates(
        _spec(),
        classified_units=[{"bedroom": "1BR", "status": "Occupied"} for _ in range(244)],
        second_source_count=214,  # 244 vs 214 = ~14% off
    )
    assert summary.ok is False
    assert "unit_count" in summary.blocking
    assert spec["qa"]["unit_count"]["blocked"] is True


def test_unit_count_summary_tab_only_warns_not_blocks():
    spec, summary = run_gates(
        _spec(),
        classified_units=[{"bedroom": "1BR", "status": "Occupied"} for _ in range(214)],
        summary_tab_count=214,  # single source, within tol
    )
    assert "unit_count" not in summary.blocking
    assert "unit_count:single_source" in summary.warnings
    assert spec["qa"]["unit_count"]["single_source_warning"] is True


def test_unit_count_non_residential_segment_blocks():
    spec, summary = run_gates(
        _spec(),
        classified_units=(
            [{"bedroom": "1BR", "status": "Occupied"} for _ in range(214)]
            + [{"segment": "marina-slip", "status": "Occupied"}]
        ),
        summary_tab_count=214,
    )
    assert summary.ok is False
    assert "unit_count" in summary.blocking
    assert any("marina" in s for s in spec["qa"]["unit_count"]["excluded_segments"])


def test_formula_bug_warns_and_records_audit():
    spec, summary = run_gates(
        _spec(),
        template_formulas={"S40": "=U36", "B66": "=B52/B10", "row78": "=NOI/-SUM(F29:F30)"},  # S40 + row78 buggy
    )
    assert "formula_audit" in spec["qa"]
    assert any(v["cell"] == "S40" for v in spec["qa"]["formula_audit"])
    assert "formula_audit:bug_detected" in summary.warnings
    # compute-time formula bug is a warning, not a hard block
    assert "formula_audit" not in summary.blocking


def test_summary_as_dict_is_json_safe():
    _, summary = run_gates(_spec(routing="ACQ", fee=0.05))
    d = summary.as_dict()
    assert set(d.keys()) == {"ok", "blocking", "warnings", "details"}
    assert d["ok"] is False


def test_clean_acq_deal_all_green():
    spec, summary = run_gates(
        _spec(routing="ACQ", fee=0.0075),
        classified_units=[{"bedroom": "1BR", "status": "Occupied"} for _ in range(214)],
        second_source_count=214,
    )
    assert summary.ok is True
    assert summary.blocking == []
