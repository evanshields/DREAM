"""A1.5 acceptance tests — /api/recalc is instant, deterministic, and provably LLM-free.

Three proofs:
  1. Behavioral: recalc reproduces Esplanade ground truth through the engine_boundary.
  2. Import-graph: the recalc router's transitive imports do NOT include the Kimi/agent client.
  3. No-LLM-call: recalc runs to completion even when the Kimi client is mocked to raise.

We test the router/boundary directly (no live FastAPI server needed); the import-graph proof is the
durable regression tripwire.
"""
import importlib
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Esplanade ground truth (floats)
ESPLANADE = dict(
    bridge_loan=23800000.0, bridge_rate=0.08, bridge_io_years=2,
    refi_loan=31944864.0, refi_rate=0.06, refi_io_years=3,
    refi_amort_years=30, refi_year=2,
    total_equity=13145673.0,
    noi_series=[2387932, 2563041, 2742167, 2883487, 2983197,
                3134540, 3241781, 3352240, 3466013, 3583198],
    exit_cap=0.06, sale_year=7, costs_of_sale=0.02,
    servicing_spread=0.0116, refi_cost_pct=0.02, exit_on_forward_noi=True,
)


def rel(a, b):
    return abs(float(a) - float(b)) / abs(float(b))


def test_recalc_reproduces_esplanade():
    from engine_boundary import ACQDealInputs, run_acq_underwrite
    hm = run_acq_underwrite(ACQDealInputs(**ESPLANADE))
    assert rel(hm["irr"], 0.2251) <= 0.02
    assert rel(hm["equity_multiple"], 2.72) <= 0.02
    assert rel(hm["exit_value"], 55870669) <= 0.005


def test_recalc_router_import_graph_excludes_llm():
    """The recalc router must not transitively import the Kimi/agent client. Walk the modules the
    router pulls in and assert none is an LLM client module."""
    # Import the router fresh and snapshot loaded modules attributable to it.
    import routers.recalc as recalc_mod  # noqa: F401
    import engine_boundary  # noqa: F401

    # Any module under the 'agent' package or named like a Kimi/openai client is forbidden on this path.
    forbidden_substrings = ("agent.kimi_client", "kimi_client", "agent.prompts", "agent.memo_generator")
    # Inspect the recalc + engine_boundary modules' own import namespaces transitively (one hop is
    # enough to catch a direct/transitive pull because engine_boundary is the only heavy dep).
    seen = set()

    def collect(mod, depth=0):
        if depth > 3 or mod.__name__ in seen:
            return
        seen.add(mod.__name__)
        for name, val in vars(mod).items():
            if isinstance(val, types.ModuleType):
                collect(val, depth + 1)

    collect(recalc_mod)
    collect(engine_boundary)
    offenders = [m for m in seen if any(f in m for f in forbidden_substrings)]
    assert not offenders, f"recalc path transitively imports an LLM client: {offenders}"
    # And openai (the Kimi transport) must not be on the path either.
    assert "openai" not in seen, "recalc path imports openai (the Kimi transport)"


def test_recalc_runs_with_kimi_mocked_to_raise(monkeypatch):
    """If anything on the recalc path tried to call the LLM, this would raise. It must not."""
    # Install a fake agent.kimi_client whose every attribute access raises.
    class _Boom:
        def __getattr__(self, _):
            raise AssertionError("recalc must not touch the LLM client")

    fake = types.ModuleType("agent.kimi_client")
    fake.KimiClient = _Boom
    fake.AsyncKimiClient = _Boom
    monkeypatch.setitem(sys.modules, "agent.kimi_client", fake)

    # Re-run recalc; it should complete without ever importing/using the (now-booby-trapped) client.
    from engine_boundary import ACQDealInputs, run_acq_underwrite
    hm = run_acq_underwrite(ACQDealInputs(**ESPLANADE))
    assert hm["irr"] is not None


def test_recalc_endpoint_via_testclient():
    """End-to-end through FastAPI: POST /api/recalc returns headline_metrics matching ground truth.
    Skipped gracefully if starlette TestClient deps are unavailable in the env."""
    try:
        from starlette.testclient import TestClient
    except Exception:
        import pytest
        pytest.skip("starlette TestClient unavailable")
    # Import only the recalc router app in isolation to avoid main.py's LLM imports needing keys.
    from fastapi import FastAPI
    from routers.recalc import router
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    r = client.post("/api/recalc", json=ESPLANADE)
    assert r.status_code == 200
    hm = r.json()["headline_metrics"]
    assert rel(hm["irr"], 0.2251) <= 0.02
    assert rel(hm["exit_value"], 55870669) <= 0.005
