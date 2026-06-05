"""BL-07 named formula-integrity sweep tests.

Both humans fixed the fragile cells reactively, never by name. formula_integrity_check emits a
named PASS/PATCH verdict for all 5 every run; S40 and row-78 are the auto-patch set (the only
black-text cells the skill mutates), the rest are flag-only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import acq_engine as ax


def test_s40_autopatch():
    res = ax.formula_integrity_check({"S40": "=U36"})
    s40 = [v for v in res.verdicts if v.cell == "S40"][0]
    assert s40.status == "bug"
    assert s40.patch == "=U36*12"
    assert s40.auto is True
    assert s40 in res.auto_patches


def test_s40_already_annualized_passes():
    res = ax.formula_integrity_check({"S40": "=U36*12"})
    s40 = [v for v in res.verdicts if v.cell == "S40"][0]
    assert s40.status == "ok"
    assert s40.patch == ""


def test_row78_bridge_pointer_flags():
    # The known defect forms: a comps-grid ref (=D48), a bridge reference, or a zeroed cell.
    res = ax.formula_integrity_check({"row78": "=D48"})
    r78 = [v for v in res.verdicts if v.cell == "row78"][0]
    assert r78.status == "bug"
    assert r78.auto is True  # row78 IS in the auto-patch set...
    # ...but with no orchestrator-supplied repoint it carries no patch string, so it is NOT
    # auto-applied — it surfaces as a flagged bug for the orchestrator to supply the repoint.
    assert r78.patch == ""
    assert r78 not in res.auto_patches


def test_row78_with_supplied_patch_autopatches():
    res = ax.formula_integrity_check({
        "row78": "=D48",
        "row78_patch": "=IF(year>refi_year, refi_NOI/refi_DS, bridge_NOI/bridge_DS)",
    })
    r78 = [v for v in res.verdicts if v.cell == "row78"][0]
    assert r78.status == "bug"
    assert r78.patch.startswith("=IF")
    assert r78 in res.auto_patches


def test_all_five_cells_get_a_named_verdict():
    res = ax.formula_integrity_check({})  # nothing read
    cells = {v.cell for v in res.verdicts}
    assert cells == {"S40", "row78", "B66", "B67", "row31", "row32"}
    assert len(res.patch_log) == len(res.verdicts)


def test_b66_is_flag_only_no_patch():
    # A wrong B66 is flagged but never auto-patched (not in the auto set).
    res = ax.formula_integrity_check({"B66": "=B52/B10"})  # missing the SUM(B52,B67)
    b66 = [v for v in res.verdicts if v.cell == "B66"][0]
    assert b66.status == "bug"
    assert b66.auto is False
    assert b66.patch == ""
    assert b66 not in res.auto_patches


def test_b66_correct_passes():
    res = ax.formula_integrity_check({"B66": '=IFERROR(SUM(B52,B67)/B10,"N/A")'})
    b66 = [v for v in res.verdicts if v.cell == "B66"][0]
    assert b66.status == "ok"
