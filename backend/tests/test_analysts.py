"""Wave C-v1 — analytical-slice acceptance tests. StubAnalysts is schema-valid and drives the
synthesis engine to Esplanade ground truth with NO LLM; KimiAnalysts imports + constructs LAZILY
(no API key needed to import); a live-Kimi smoke test is skipif-guarded."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs.analysts import (  # noqa: E402
    StubAnalysts,
    KimiAnalysts,
    merge_slices,
    make_open_questions,
    validate_slice,
    SchemaValidationError,
    SLICE_NAMES,
)
from jobs.synthesis import run_synthesis  # noqa: E402

CI = {"purchase_price": 55000000.0, "hold_years": 7, "exit_cap": 0.06}
TS = "2026-06-09T00:00:00Z"
HEADLINE_TOL = 0.02  # IRR sensitivity


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


def test_slice_names_are_the_five():
    assert SLICE_NAMES == ("t12", "rentroll", "assumptions", "comps", "marketdata")


def test_stub_outputs_all_schema_valid():
    for out in StubAnalysts().run_all(None, {}, CI):
        # validate_slice raises on a violation; returns the slice if clean
        assert validate_slice(out) is out


def test_stub_merged_reproduces_esplanade_ground_truth():
    merged = merge_slices(StubAnalysts().run_all(None, {}, CI))
    merged.setdefault("meta", {})["routing"] = "ACQ"
    res = run_synthesis(merged, CI, TS, return_result=True)
    hm = res.headline_metrics
    assert rel(hm["irr"], 0.2221) <= HEADLINE_TOL, hm["irr"]
    assert rel(hm["equity_multiple"], 2.72) <= HEADLINE_TOL, hm["equity_multiple"]
    assert rel(hm["exit_value"], 55870669) <= 0.005, hm["exit_value"]
    assert res.gate_summary.ok is True
    assert res.gate_summary.blocking == []
    # gates present (the chat-bot path's whole point)
    assert "fee_bounds" in res.spec["qa"]
    assert "unit_count" in res.spec["qa"]


def test_stub_has_one_llm_inferred_open_question():
    merged = merge_slices(StubAnalysts().run_all(None, {}, CI))
    qs = make_open_questions(merged)
    assert [q.field for q in qs] == ["B31"]
    assert qs[0].blocking is False


def test_validate_slice_rejects_bad_cell():
    with pytest.raises(SchemaValidationError):
        validate_slice({"assumptions_cells": [{"cell": "B10", "value": 1}]})  # missing 'source'
    with pytest.raises(SchemaValidationError):
        validate_slice({"t12_unmapped": "zero"})  # must be int


def test_kimi_analysts_imports_and_constructs_without_key(monkeypatch):
    """SKELETON: constructing KimiAnalysts must NOT touch the network or require a key."""
    monkeypatch.delenv("KIMI_API_KEY", raising=False)
    ka = KimiAnalysts()
    assert ka._client is None  # lazy — no client built at construction
    # The five slice methods exist (protocol shape).
    for m in ("slice_t12", "slice_rentroll", "slice_assumptions", "slice_comps",
              "slice_marketdata", "run_all"):
        assert callable(getattr(ka, m))


def test_kimi_json_parser_tolerates_fences():
    ka = KimiAnalysts()
    out = ka._parse_json('```json\n{"t12_unmapped": 0, "t12_cells": []}\n```')
    assert out["t12_unmapped"] == 0


def test_kimi_uses_injected_client_no_network(monkeypatch):
    """A fake client proves _run_slice wires prompt->reply->validate without a live model."""
    class FakeClient:
        model = "x"

        def chat(self, messages, max_tokens=4000):
            assert messages[0]["role"] == "system"
            return '{"t12_unmapped": 0, "t12_cells": [{"cell":"S40","value":0,"source":"T-12"}]}'

    ka = KimiAnalysts(client=FakeClient())
    out = ka.slice_t12({}, {}, CI)
    assert out["t12_unmapped"] == 0
    assert out["t12_cells"][0]["cell"] == "S40"


@pytest.mark.skipif(not os.environ.get("KIMI_API_KEY"), reason="live Kimi key not set")
def test_kimi_live_smoke():  # pragma: no cover - network
    ka = KimiAnalysts()
    out = ka.slice_marketdata(
        {"county": "Orange", "state": "FL"},
        {"deal_name": "Esplanade", "summary": "240-unit ACQ in Orlando FL"},
        CI,
    )
    assert "marketdata" in out
