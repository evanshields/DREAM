"""Fail-closed regression tests (Argon review of head 492866a6, findings 1 to 4)."""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_status import loader  # noqa: E402
from run_status.loader import load_run, list_run_ids  # noqa: E402
from run_status.view import build_view, display_state  # noqa: E402

FINISHED = ("complete",)


def _done():
    run = copy.deepcopy(load_run("run-clean-awaiting-cp1"))
    run["status"] = "completed"
    return run


# Finding 1: unknown, missing or absent gate results must not read as finished.
@pytest.mark.parametrize("bad", ["blocked", "error", "failed", None, "gren", ""])
def test_unknown_gate_status_is_blocked(bad):
    run = _done()
    run["gates"][0]["status"] = bad
    assert display_state(run) == "blocked"
    assert build_view(run)["values_are_diagnostic"] is True


def test_gate_without_status_key_is_blocked():
    run = _done()
    del run["gates"][1]["status"]
    assert display_state(run) == "blocked"


@pytest.mark.parametrize("status", ["completed", "awaiting_cp1"])
def test_empty_gates_on_terminal_run_is_blocked(status):
    run = _done()
    run["status"] = status
    run["gates"] = []
    assert display_state(run) == "blocked"


def test_missing_gates_key_is_blocked():
    run = _done()
    del run["gates"]
    assert display_state(run) == "blocked"


# Finding 2: no provenance means unverifiable, which is stale.
@pytest.mark.parametrize("val", [None, ""])
def test_missing_provenance_both_sides_is_stale(val):
    run = _done()
    run["engine_commit"] = run["current_engine_commit"] = val
    assert display_state(run) == "stale"
    run = _done()
    run["inputs_hash"] = run["current_inputs_hash"] = val
    assert display_state(run) == "stale"


def test_absent_provenance_keys_is_stale():
    run = _done()
    for k in ("engine_commit", "current_engine_commit", "inputs_hash", "current_inputs_hash"):
        del run[k]
    assert display_state(run) == "stale"
    assert build_view(run)["is_stale"] is True


# Finding 3: evidence problems and open holds must not read as finished.
@pytest.mark.parametrize("state", ["missing", "hash_mismatch", "weird", None])
@pytest.mark.parametrize("status", ["completed", "awaiting_cp1"])
def test_bad_evidence_is_blocked(state, status):
    run = _done()
    run["status"] = status
    run["evidence"][1]["state"] = state
    assert display_state(run) == "blocked"


def test_completed_without_evidence_is_blocked():
    run = _done()
    run["evidence"] = []
    assert display_state(run) == "blocked"


def test_open_hold_never_complete():
    run = _done()
    run["holds"] = [{"id": "h", "reason": "x", "owner": "y"}]
    assert display_state(run) not in FINISHED
    assert display_state(run) == "needs_human_check"


def test_missing_evidence_fixture_shows_blocked_and_missing():
    view = build_view(load_run("run-missing-values"))
    assert view["display_state"] == "blocked"
    assert any(e["state"] == "missing" for e in view["evidence"])


# Finding 4: loader only serves frozen synthetic fixtures whose id matches.
def _drop(tmp_path, monkeypatch, name, data):
    (tmp_path / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(loader, "FIXTURE_DIR", tmp_path)


def test_non_synthetic_file_rejected(tmp_path, monkeypatch):
    run = copy.deepcopy(load_run("run-failed"))
    run["run_id"] = "real-one"
    run["synthetic"] = False
    _drop(tmp_path, monkeypatch, "real-one", run)
    assert load_run("real-one") is None
    assert "real-one" not in list_run_ids() or loader.load_all() == []


def test_missing_synthetic_flag_rejected(tmp_path, monkeypatch):
    run = copy.deepcopy(load_run("run-failed"))
    run["run_id"] = "no-flag"
    del run["synthetic"]
    _drop(tmp_path, monkeypatch, "no-flag", run)
    assert load_run("no-flag") is None


def test_run_id_mismatch_rejected(tmp_path, monkeypatch):
    run = copy.deepcopy(load_run("run-failed"))
    run["run_id"] = "someone-else"
    _drop(tmp_path, monkeypatch, "wrong-id", run)
    assert load_run("wrong-id") is None


def test_missing_run_id_does_not_500(tmp_path, monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routers.run_status import router

    run = copy.deepcopy(load_run("run-failed"))
    del run["run_id"]
    _drop(tmp_path, monkeypatch, "no-id", run)
    app = FastAPI()
    app.include_router(router)
    c = TestClient(app)
    assert c.get("/api/run-status").status_code == 200
    assert c.get("/api/run-status/no-id").status_code == 404


def test_malformed_json_is_none(tmp_path, monkeypatch):
    (tmp_path / "bad.json").write_text("{nope", encoding="utf-8")
    monkeypatch.setattr(loader, "FIXTURE_DIR", tmp_path)
    assert load_run("bad") is None
