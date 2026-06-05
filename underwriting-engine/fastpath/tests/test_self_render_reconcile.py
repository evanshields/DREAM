"""BL-05 CP-2: identity gate before reconcile + self-render fallback.

On the Envy run the parent handed Dream the Aviara fork as ground truth; CP-2 reconcile silently
degraded to a transcript comparison and the safety gate fired without teeth. Two fixes:
  1. reconcile() raises IdentityMismatchError when the ground truth fails deal_identity_check.
  2. reconcile_self_render() compares the engine against the openpyxl-populated draft it just
     wrote (always available) — never a transcript.
"""
import os
import sys
import tempfile

import openpyxl
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import populator as P


def _make_input_draft(path, b10=75000000, b6=214):
    """A draft whose B10/B6 are INPUT values (not formulas), so self-render can read them
    without an Excel recalc."""
    wb = openpyxl.Workbook()
    pf = wb.active
    pf.title = "Pro Forma"
    pf["B10"] = b10   # purchase price (input)
    pf["B6"] = b6     # units (input here, for the self-render check)
    wb.save(path)
    wb.close()


def test_identity_mismatch_raises_not_silent():
    with tempfile.TemporaryDirectory() as tmp:
        draft = os.path.join(tmp, "draft.xlsx")
        _make_input_draft(draft)
        bad_identity = {"match": False, "reasons": ["Pro Forma B2 'Aviara East Pompano' != Envy"]}
        with pytest.raises(P.IdentityMismatchError):
            P.reconcile(draft, {"purchase_price": 75000000},
                        metric_cells={"purchase_price": "B10"},
                        identity=bad_identity)


def test_identity_match_allows_reconcile():
    with tempfile.TemporaryDirectory() as tmp:
        draft = os.path.join(tmp, "draft.xlsx")
        _make_input_draft(draft)
        ok_identity = {"match": True, "reasons": []}
        rows = P.reconcile(draft, {"purchase_price": 75000000},
                           metric_cells={"purchase_price": "B10"},
                           identity=ok_identity)
        assert len(rows) == 1
        assert rows[0].excel == 75000000
        assert rows[0].flag is False


def test_self_render_reconciles_against_own_draft():
    # No external ground truth -> reconcile against the populated draft itself.
    with tempfile.TemporaryDirectory() as tmp:
        draft = os.path.join(tmp, "draft.xlsx")
        _make_input_draft(draft, b10=75000000, b6=214)
        rows = P.reconcile_self_render(
            draft,
            {"purchase_price": 75000000, "units": 214},
            metric_cells={"purchase_price": "B10", "units": "B6"},
        )
        flags = {r.metric: r.flag for r in rows}
        assert flags == {"purchase_price": False, "units": False}
        # Never None — the self-written draft is always available.
        assert all(r.excel is not None for r in rows)


def test_self_render_flags_a_populator_mismatch():
    # Self-render catches a POPULATOR bug: the engine says 214 but the draft holds 244.
    with tempfile.TemporaryDirectory() as tmp:
        draft = os.path.join(tmp, "draft.xlsx")
        _make_input_draft(draft, b6=244)
        rows = P.reconcile_self_render(
            draft, {"units": 214}, metric_cells={"units": "B6"})
        assert rows[0].flag is True   # 214 vs 244 -> outside tolerance
