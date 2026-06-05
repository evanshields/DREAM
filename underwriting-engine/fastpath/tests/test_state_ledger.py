"""BL-17 durable phase-state ledger tests.

The Envy run wasted work to ephemeral context: a mid-stream price interruption, silent hold/exit-cap
divergence, and full T-12 re-parses after container restarts. The ledger captures the three blocking
critical inputs and persists phase/parse state so a restart resumes instead of re-parsing.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import state_ledger as SL


def test_critical_inputs_block_until_complete():
    st = SL.UnderwriteState(slug="envy")
    assert st.critical_inputs_ok() is False
    assert "purchase_price" in st.block_reason()
    st.critical_inputs.purchase_price = 75000000
    st.critical_inputs.hold_years = 7
    assert st.critical_inputs_ok() is False  # exit_cap still missing
    st.critical_inputs.exit_cap = 0.065
    assert st.critical_inputs_ok() is True
    assert st.block_reason() == ""


def test_phase_ledger_resume_point():
    st = SL.UnderwriteState(slug="envy")
    assert st.next_phase() == 0
    for p, name in [(0, "routing"), (1, "t12"), (2, "rentroll")]:
        st.record_phase(p, name, "complete", f"{name} done")
    assert st.completed_phases() == [0, 1, 2]
    assert st.next_phase() == 3
    # a partial phase does not count as complete
    st.record_phase(3, "assumptions", "partial", "fee pending")
    assert st.next_phase() == 3


def test_source_cache_skips_unchanged_reparse():
    st = SL.UnderwriteState(slug="envy")
    st.record_source("/deal/t12.xlsx", "t12", "1234:5678", summary="NOI $3.88M")
    assert st.source_is_fresh("/deal/t12.xlsx", "1234:5678") is True
    # a changed fingerprint forces a re-parse
    assert st.source_is_fresh("/deal/t12.xlsx", "9999:0000") is False
    # an unseen path is not fresh
    assert st.source_is_fresh("/deal/rr.xlsx", "x") is False
    assert st.get_source_summary("/deal/t12.xlsx") == "NOI $3.88M"


def test_record_source_replaces_prior_for_same_path():
    st = SL.UnderwriteState(slug="envy")
    st.record_source("/deal/t12.xlsx", "t12", "v1", "old")
    st.record_source("/deal/t12.xlsx", "t12", "v2", "new")
    assert len([s for s in st.parsed_sources if s.path == "/deal/t12.xlsx"]) == 1
    assert st.get_source_summary("/deal/t12.xlsx") == "new"


def test_save_and_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        st = SL.UnderwriteState(slug="envy", deal_name="Envy Pompano Beach", routing="ACQ")
        st.critical_inputs.purchase_price = 75000000
        st.critical_inputs.hold_years = 7
        st.critical_inputs.exit_cap = 0.065
        st.record_phase(0, "routing", "complete", "ACQ")
        st.record_source("/deal/t12.xlsx", "t12", "abc", "NOI $3.88M")
        path = SL.save_state(tmp, st, updated="2026-06-05T12:00:00")
        assert os.path.basename(path) == SL.STATE_FILENAME

        loaded = SL.load_state(tmp)
        assert loaded.slug == "envy"
        assert loaded.deal_name == "Envy Pompano Beach"
        assert loaded.routing == "ACQ"
        assert loaded.critical_inputs_ok() is True
        assert loaded.completed_phases() == [0]
        assert loaded.source_is_fresh("/deal/t12.xlsx", "abc") is True
        assert loaded.updated == "2026-06-05T12:00:00"


def test_load_missing_returns_fresh():
    with tempfile.TemporaryDirectory() as tmp:
        st = SL.load_state(tmp, slug="newdeal")
        assert st.slug == "newdeal"
        assert st.critical_inputs_ok() is False
        assert st.completed_phases() == []


def test_fingerprint_file_changes_with_content():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "f.txt")
        with open(p, "w") as f:
            f.write("a")
        fp1 = SL.fingerprint_file(p)
        with open(p, "w") as f:
            f.write("aaaa longer content")
        fp2 = SL.fingerprint_file(p)
        assert fp1 != fp2
        assert SL.fingerprint_file(os.path.join(tmp, "nope.txt")) == "missing"
