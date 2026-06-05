"""BL-01 + BL-09 unit-count reconcile gate tests.

Fahd's pandas read (header=5, all SQFT>0) counted 244 — including the condo + marina-slip rows
the user explicitly said to exclude. UnitCountReconciler classifies by use-type first, then
reconciles to a second source (or the roll's own summary tab with a single-source warning).
"""
import os
import sys
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import acq_engine as ax


def _residential(n):
    return [{"bedroom": "1BR", "status": "Occupied", "use_type": "residential"} for _ in range(n)]


def test_marina_segment_blocks():
    # 214 residential + 30 marina-slip rows = Fahd's 244. The marina segment must BLOCK.
    units = _residential(214) + [
        {"bedroom": "Slip", "status": "Occupied", "use_type": "marina slip"} for _ in range(30)
    ]
    res = ax.UnitCountReconciler().reconcile(units, second_source_count=214)
    assert res.blocked is True
    assert res.counted == 214  # the residential rows still count correctly
    assert any("marina" in s for s in res.excluded_segments)


def test_reconciles_to_second_source():
    res = ax.UnitCountReconciler().reconcile(
        _residential(214), summary_tab_count=214, second_source_count=214)
    assert res.blocked is False
    assert res.reconciled is True
    assert res.single_source_warning is False
    assert res.counted == 214


def test_summary_tab_only_passes_with_warning():
    # No independent 2nd source -> pass on the roll's own summary tab, but FLAG single-source.
    res = ax.UnitCountReconciler().reconcile(_residential(214), summary_tab_count=214)
    assert res.blocked is False
    assert res.single_source_warning is True
    assert any("single-source" in r.lower() for r in res.reasons)


def test_summary_tab_disagreement_blocks():
    # Counted 244 but the roll's own summary tab says 214 -> > 2% -> BLOCK.
    res = ax.UnitCountReconciler().reconcile(_residential(244), summary_tab_count=214)
    assert res.blocked is True


def test_second_source_disagreement_blocks():
    res = ax.UnitCountReconciler().reconcile(_residential(244), second_source_count=214)
    assert res.blocked is True


def test_user_exclusion_violation_blocks():
    # User said "exclude the EB5 condo block"; a condo segment present must block.
    units = _residential(214) + [
        {"bedroom": "Condo", "status": "Occupied", "use_type": "eb5 condo"} for _ in range(10)
    ]
    res = ax.UnitCountReconciler().reconcile(
        units, second_source_count=214, user_exclusions=["condo"])
    assert res.blocked is True
    assert any("condo" in s for s in res.excluded_segments)


def test_no_source_blocks():
    # Cannot validate without any reconciliation source -> block & escalate.
    res = ax.UnitCountReconciler().reconcile(_residential(214))
    assert res.blocked is True
    assert any("no reconciliation source" in r.lower() for r in res.reasons)
