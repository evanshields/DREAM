"""Engine run source: adapter mapping and the read-only DREAM_RUNS_DIR source. Synthetic fixtures only."""
import copy
import json
import os
import shutil
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers.run_status import router  # noqa: E402
from run_status.adapter import adapt_engine_run  # noqa: E402
from run_status.view import build_view  # noqa: E402

ENGINE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "run_status_engine"
STOPPED, COMPLETE = "synthetic-stopped-stage6", "synthetic-complete"
FIXTURE_IDS = [
    "run-blocked-red-gate", "run-clean-awaiting-cp1", "run-failed",
    "run-in-progress", "run-missing-values", "run-stale-engine-commit",
]

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def engine_env(monkeypatch):
    monkeypatch.setenv("DREAM_RUNS_DIR", str(ENGINE_DIR))
    monkeypatch.setenv("DREAM_CURRENT_ENGINE_COMMIT", "synthetic-commit-0001")
    monkeypatch.setenv("DREAM_CURRENT_INPUTS_HASH", "synthetic-hash-0001")


def _raw(deal, name="run.json"):
    return json.loads((ENGINE_DIR / deal / "run" / name).read_text(encoding="utf-8"))


def _view(deal):
    return client.get(f"/api/run-status/{deal}").json()


# ---- unset env var keeps today's behaviour ----

def test_unset_env_serves_fixtures_only(monkeypatch):
    monkeypatch.delenv("DREAM_RUNS_DIR", raising=False)
    ids = sorted(r["run_id"] for r in client.get("/api/run-status").json()["runs"])
    assert ids == FIXTURE_IDS
    assert client.get(f"/api/run-status/{COMPLETE}").status_code == 404


def test_blank_or_missing_dir_serves_fixtures_only(monkeypatch, tmp_path):
    for value in ("", "   ", str(tmp_path / "does-not-exist")):
        monkeypatch.setenv("DREAM_RUNS_DIR", value)
        ids = sorted(r["run_id"] for r in client.get("/api/run-status").json()["runs"])
        assert ids == FIXTURE_IDS


def test_set_env_adds_engine_runs(engine_env):
    ids = sorted(r["run_id"] for r in client.get("/api/run-status").json()["runs"])
    assert ids == sorted(FIXTURE_IDS + [COMPLETE, STOPPED])
    summaries = {r["run_id"]: r for r in client.get("/api/run-status").json()["runs"]}
    assert summaries[COMPLETE]["synthetic"] is True


# ---- stage mapping ----

def test_stage6_failure_shows_blocked_and_red(engine_env):
    v = _view(STOPPED)
    assert v["display_state"] == "blocked"
    assert v["values_are_diagnostic"] is True
    gates = {g["id"]: g for g in v["gates"]}
    assert gates["stage-6"]["status"] == "red"
    assert "did not tie out" in gates["stage-6"]["detail"]
    assert [gates[f"stage-{n}"]["status"] for n in range(1, 6)] == ["green"] * 5


def test_waiting_stage7_never_complete(engine_env):
    v = _view(STOPPED)
    gates = {g["id"]: g for g in v["gates"]}
    assert gates["stage-7"]["status"] == "not_run"
    assert gates["stage-8"]["status"] == "not_run"
    assert v["display_state"] != "complete"
    assert v["status"] != "completed"
    assert v["holds"] and v["holds"][0]["owner"] == "evan"


def test_waiting_alone_never_complete(engine_env):
    rec = _raw(STOPPED)
    rec["stages"][5] = {"stage": 6, "name": "unit mix optimiser", "status": "ok"}
    rec["failed"] = []
    rec["stages"][7] = {"stage": 8, "name": "workbook build and Drive save", "status": "blocked", "why": "stage 7 did not finish"}
    view = build_view(adapt_engine_run(rec, None, run_id=STOPPED, current_engine_commit="synthetic-commit-0001",
                                       current_inputs_hash="synthetic-hash-0001"))
    assert view["status"] == "awaiting_input"
    assert view["display_state"] != "complete"


def test_complete_run_with_bote(engine_env):
    v = _view(COMPLETE)
    assert v["display_state"] == "complete"
    assert v["synthetic"] is True
    assert all(g["status"] == "green" for g in v["gates"]) and len(v["gates"]) == 8
    assert v["engine_commit"] == "synthetic-commit-0001"
    assert v["inputs_hash"] == "synthetic-hash-0001"
    assert all(e["state"] == "ok" and len(e["sha256"]) == 64 for e in v["evidence"])


def test_provenance_unset_means_stale_not_complete(monkeypatch):
    monkeypatch.setenv("DREAM_RUNS_DIR", str(ENGINE_DIR))
    monkeypatch.delenv("DREAM_CURRENT_ENGINE_COMMIT", raising=False)
    monkeypatch.delenv("DREAM_CURRENT_INPUTS_HASH", raising=False)
    assert _view(COMPLETE)["display_state"] == "stale"


def test_skipped_is_amber_with_reason():
    rec = _raw(COMPLETE)
    rec["stages"][1] = {"stage": 2, "name": "rent roll parse and flags", "status": "skipped",
                        "why": "its output is already on disk; pass --force to rebuild"}
    v = adapt_engine_run(rec, None, run_id=COMPLETE)
    g = v["gates"][1]
    assert g["status"] == "amber" and "already on disk" in g["detail"]


def test_engine_blocked_behind_failure_is_not_run():
    rec = _raw(STOPPED)
    rec["stages"][6] = {"stage": 7, "name": "back of the envelope", "status": "blocked", "why": "stage 6 did not finish"}
    v = adapt_engine_run(rec, None, run_id=STOPPED)
    assert v["gates"][6]["status"] == "not_run"
    assert build_view(v)["display_state"] == "blocked"


# ---- fail closed ----

@pytest.mark.parametrize("mutate", [
    lambda r: r["stages"][0].pop("status"),
    lambda r: r["stages"][0].update(status="mystery"),
    lambda r: r["stages"].__setitem__(0, "not a dict"),
    lambda r: r.pop("stages"),
    lambda r: r.update(stages="oops"),
])
def test_unknown_or_missing_stage_data_is_blocked_never_complete(mutate):
    rec = _raw(COMPLETE)
    mutate(rec)
    v = adapt_engine_run(rec, None, run_id=COMPLETE, current_engine_commit="synthetic-commit-0001",
                         current_inputs_hash="synthetic-hash-0001")
    assert build_view(v)["display_state"] == "blocked"
    assert v["status"] != "completed"


@pytest.mark.parametrize("key", ["failed", "waiting"])
def test_missing_failed_or_waiting_list_is_not_complete(key):
    rec = _raw(COMPLETE)
    rec.pop(key)
    v = adapt_engine_run(rec, None, run_id=COMPLETE, current_engine_commit="synthetic-commit-0001",
                         current_inputs_hash="synthetic-hash-0001")
    assert v["status"] != "completed" and build_view(v)["display_state"] != "complete"


def test_stop_after_run_is_not_complete():
    rec = _raw(COMPLETE)
    rec["stop_after"] = 5
    rec["stages"] = rec["stages"][:5]
    v = adapt_engine_run(rec, None, run_id=COMPLETE, current_engine_commit="synthetic-commit-0001",
                         current_inputs_hash="synthetic-hash-0001")
    assert build_view(v)["display_state"] != "complete"


def test_missing_evidence_file_is_blocked(tmp_path):
    rec = _raw(COMPLETE)
    v = adapt_engine_run(rec, None, run_id=COMPLETE, run_dir=tmp_path, current_engine_commit="synthetic-commit-0001",
                         current_inputs_hash="synthetic-hash-0001")
    assert {e["state"] for e in v["evidence"]} == {"missing"}
    assert build_view(v)["display_state"] == "blocked"


def test_non_object_record_is_none():
    assert adapt_engine_run([1, 2], None, run_id="x") is None
    assert adapt_engine_run(None, None, run_id="x") is None


# ---- values pass through exactly ----

def test_values_byte_identical_and_null_stays_null(engine_env):
    bote = _raw(COMPLETE, "bote.json")
    rows = {h["source_pointer"]: h for h in _view(COMPLETE)["headline"]}
    assert rows["/price"]["value"] == bote["price"] == 1111111.0
    assert rows["/projection/years/0/noi"]["value"] == 111111.0
    assert rows["/stack/coverage/bridge/dscr_exempt"]["value"] == 1.1111
    # verified zero stays zero, not blank
    zero = rows["/stack/coverage/takeout/dscr_exempt"]
    assert zero["value"] == 0 and zero["value"] is not None and zero["blank_reason"] is None
    # stored null stays null with a reason
    irr = rows["/stack/irr"]
    assert irr["value"] is None and irr["blank_reason"]
    # raw response text carries the number as stored, not reformatted
    text = client.get(f"/api/run-status/{COMPLETE}").text
    assert "1111111.0" in text and "111111.0" in text and "1.1111" in text


def test_values_not_reformatted_for_awkward_floats():
    bote = {"price": 37000000.1, "projection": {"years": [{"noi": 0.1 + 0.2}]}, "stack": {"irr": "0.2251"}}
    rows = {h["source_pointer"]: h["value"] for h in adapt_engine_run(_raw(COMPLETE), bote, run_id="x")["headline"]}
    assert rows["/price"] == 37000000.1
    assert rows["/projection/years/0/noi"] == 0.1 + 0.2
    assert rows["/stack/irr"] == "0.2251"


def test_no_bote_gives_blank_values_with_reason(engine_env):
    v = _view(STOPPED)
    assert len(v["headline"]) == 5
    assert all(h["value"] is None and h["blank_reason"] for h in v["headline"])
    assert v["missing_value_count"] == 5


def test_adapter_does_not_mutate_inputs():
    rec, bote = _raw(COMPLETE), _raw(COMPLETE, "bote.json")
    before = (copy.deepcopy(rec), copy.deepcopy(bote))
    adapt_engine_run(rec, bote, run_id=COMPLETE)
    assert (rec, bote) == before


# ---- read-only and traversal ----

@pytest.mark.parametrize("bad", ["..", "%2e%2e", "..%2fetc", "a/b", "UPPER", "x" * 65, "a.b", "%2e%2e%2f%2e%2e%2fetc%2fpasswd"])
def test_traversal_and_bad_ids_404(engine_env, bad):
    assert client.get(f"/api/run-status/{bad}").status_code in (404, 422)


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
@pytest.mark.parametrize("path", ["/api/run-status", f"/api/run-status/{COMPLETE}"])
def test_non_get_rejected(engine_env, method, path):
    assert getattr(client, method)(path).status_code == 405


def test_record_for_other_deal_rejected(engine_env, monkeypatch, tmp_path):
    root = tmp_path / "runs"
    shutil.copytree(ENGINE_DIR / COMPLETE, root / "other-deal")  # slug inside still says synthetic-complete
    monkeypatch.setenv("DREAM_RUNS_DIR", str(root))
    assert client.get("/api/run-status/other-deal").status_code == 404
    assert client.get("/api/run-status").json()["runs"] != []  # fixtures still listed


def test_symlinked_deal_dir_rejected(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    root.mkdir()
    os.symlink(ENGINE_DIR / COMPLETE, root / COMPLETE)
    monkeypatch.setenv("DREAM_RUNS_DIR", str(root))
    assert client.get(f"/api/run-status/{COMPLETE}").status_code == 404


def test_symlinked_run_json_rejected(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    (root / COMPLETE / "run").mkdir(parents=True)
    os.symlink(ENGINE_DIR / COMPLETE / "run" / "run.json", root / COMPLETE / "run" / "run.json")
    monkeypatch.setenv("DREAM_RUNS_DIR", str(root))
    assert client.get(f"/api/run-status/{COMPLETE}").status_code == 404


def test_malformed_run_json_404_and_not_listed(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    (root / "bad-deal" / "run").mkdir(parents=True)
    (root / "bad-deal" / "run" / "run.json").write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("DREAM_RUNS_DIR", str(root))
    assert client.get("/api/run-status/bad-deal").status_code == 404
    assert "bad-deal" not in [r["run_id"] for r in client.get("/api/run-status").json()["runs"]]


def test_fixture_wins_over_deal_folder_with_same_id(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    (root / "run-failed" / "run").mkdir(parents=True)
    rec = _raw(COMPLETE)
    rec["slug"] = "run-failed"
    (root / "run-failed" / "run" / "run.json").write_text(json.dumps(rec), encoding="utf-8")
    monkeypatch.setenv("DREAM_RUNS_DIR", str(root))
    assert _view("run-failed")["display_state"] == "failed"
    ids = [r["run_id"] for r in client.get("/api/run-status").json()["runs"]]
    assert ids.count("run-failed") == 1


def test_only_get_routes_on_router():
    from fastapi.routing import APIRoute
    methods = {m for r in router.routes if isinstance(r, APIRoute) for m in r.methods}
    assert methods == {"GET"}
