"""PR 10 repair: one test group per review finding (Astra 1 to 4, Argon 5 to 7 plus the Likely item).

Every test builds a private copy of the synthetic complete run, so the shipped fixtures stay frozen.
The rule under test: a run that is incomplete, skipped, malformed, duplicated, unverifiable or changed
after the fact never shows as complete.
"""
import hashlib
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

ENGINE_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "run_status_engine"
ID = "synthetic-complete"

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Run:
    """A private copy of the complete synthetic run under tmp_path, sealed with matching output hashes."""

    def __init__(self, tmp_path, monkeypatch):
        self.root = tmp_path / "runs"
        self.dir = self.root / ID / "run"
        shutil.copytree(ENGINE_DIR / ID, self.root / ID)
        monkeypatch.setenv("DREAM_RUNS_DIR", str(self.root))
        monkeypatch.setenv("DREAM_CURRENT_ENGINE_COMMIT", "synthetic-commit-0001")
        monkeypatch.setenv("DREAM_CURRENT_INPUTS_HASH", "synthetic-hash-0001")
        self.record = json.loads((self.dir / "run.json").read_text(encoding="utf-8"))
        self.seal()

    def seal(self):
        self.record["output_sha256"] = {n: _sha(self.dir / n) for n in ("sources.json", "bote.json") if (self.dir / n).is_file()}
        self.save()

    def save(self):
        (self.dir / "run.json").write_text(json.dumps(self.record), encoding="utf-8")

    def view(self):
        r = client.get(f"/api/run-status/{ID}")
        assert r.status_code == 200, r.text
        return r.json()

    def listed(self):
        runs = {r["run_id"]: r for r in client.get("/api/run-status").json()["runs"]}
        return runs[ID]["display_state"] if ID in runs else None


@pytest.fixture
def run(tmp_path, monkeypatch):
    return Run(tmp_path, monkeypatch)


def not_complete(run):
    v = run.view()
    assert v["display_state"] != "complete", v
    assert v["status"] != "completed" or v["display_state"] != "complete"
    assert run.listed() != "complete"
    return v


def test_sealed_copy_is_complete(run):
    """Control: the private copy used below really is complete, so the cases that follow prove something."""
    v = run.view()
    assert v["display_state"] == "complete"
    assert all(e["state"] == "ok" for e in v["evidence"])


# ---- Astra 1: missing or malformed stages ----

@pytest.mark.parametrize("drop", [[6], [7], [6, 7, 8], [8], [1]])
def test_a1_absent_expected_stage_is_not_complete(run, drop):
    run.record["stages"] = [s for s in run.record["stages"] if s["stage"] not in drop]
    run.save()
    not_complete(run)


def test_a1_duplicate_stage_ids_are_not_complete_and_ids_unique(run):
    run.record["stages"].append(dict(run.record["stages"][2]))
    run.save()
    v = not_complete(run)
    ids = [g["id"] for g in v["gates"]]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("bad", [None, False, 0, "", {}, "none"])
@pytest.mark.parametrize("key", ["failed", "waiting"])
def test_a1_untyped_failed_or_waiting_is_not_complete(run, key, bad):
    run.record[key] = bad
    run.save()
    not_complete(run)


@pytest.mark.parametrize("stage_value", [None, True, "6", 6.0, 99])
def test_a1_invalid_stage_identity_is_not_complete(run, stage_value):
    run.record["stages"][5]["stage"] = stage_value
    run.save()
    v = not_complete(run)
    ids = [g["id"] for g in v["gates"]]
    assert len(ids) == len(set(ids))


# ---- Astra 2: rejected BOTE ----

@pytest.mark.parametrize("payload", [b"{not json", b"[1, 2, 3]", b'"text"', b"", b"null"])
def test_a2_rejected_bote_is_not_verified_or_complete(run, payload):
    (run.dir / "bote.json").write_bytes(payload)
    run.seal()  # even a sealed hash must not rescue a file the loader rejected
    v = not_complete(run)
    bote = next(e for e in v["evidence"] if e["name"] == "bote.json")
    assert bote["state"] != "ok"
    assert all("No bote.json" not in (h["blank_reason"] or "") for h in v["headline"])
    assert all("rejected" in (h["blank_reason"] or "").lower() for h in v["headline"])


def test_a2_oversized_bote_is_not_verified_or_complete(run, monkeypatch):
    bote = json.loads((run.dir / "bote.json").read_text(encoding="utf-8"))
    bote["padding"] = "x" * 2_100_000  # valid JSON, over the 2 MB limit
    (run.dir / "bote.json").write_text(json.dumps(bote), encoding="utf-8")
    run.seal()
    v = not_complete(run)
    bote = next(e for e in v["evidence"] if e["name"] == "bote.json")
    assert bote["state"] != "ok"


def test_a2_absent_bote_is_not_complete(run):
    (run.dir / "bote.json").unlink()
    run.seal()
    v = not_complete(run)
    assert {e["name"]: e["state"] for e in v["evidence"]}["bote.json"] == "missing"


# ---- Astra 3: a fresh hash is not verification ----

def test_a3_changed_output_is_not_verified(run):
    bote = json.loads((run.dir / "bote.json").read_text(encoding="utf-8"))
    bote["price"] = 9999999.0
    (run.dir / "bote.json").write_text(json.dumps(bote), encoding="utf-8")  # record untouched
    v = not_complete(run)
    assert {e["name"]: e["state"] for e in v["evidence"]}["bote.json"] == "hash_mismatch"


def test_a3_no_recorded_hash_is_unverified_not_verified(run):
    run.record.pop("output_sha256")
    run.save()
    v = not_complete(run)
    assert all(e["state"] != "ok" for e in v["evidence"])
    assert {e["state"] for e in v["evidence"]} == {"unverified"}


@pytest.mark.parametrize("bad", [None, [], "abc", {"bote.json": 5}, {"bote.json": "zz"}])
def test_a3_malformed_hash_map_is_not_verified(run, bad):
    run.record["output_sha256"] = bad
    run.save()
    v = not_complete(run)
    assert all(e["state"] != "ok" for e in v["evidence"])


def test_a3_hash_for_one_file_does_not_verify_the_other(run):
    run.record["output_sha256"].pop("bote.json")
    run.save()
    v = not_complete(run)
    states = {e["name"]: e["state"] for e in v["evidence"]}
    assert states["sources.json"] == "ok" and states["bote.json"] == "unverified"


# ---- Astra 4: bounded evidence reads ----

def test_a4_over_limit_artifact_is_never_opened(run, monkeypatch):
    import run_status.adapter as adapter
    monkeypatch.setattr(adapter, "MAX_EVIDENCE_BYTES", 10)
    hashed, read = [], []
    monkeypatch.setattr(adapter, "_sha256_file", lambda p: hashed.append(p.name) or "0" * 64)
    real_read = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes", lambda self: read.append(self.name) or real_read(self))
    v = run.view()
    assert hashed == [] and read == []
    assert v["display_state"] != "complete"
    assert all(e["state"] == "unverified" for e in v["evidence"])


def test_a4_hashing_is_chunked_never_read_bytes(run, monkeypatch):
    def boom(self):
        raise AssertionError("read_bytes would load the whole file")
    monkeypatch.setattr(Path, "read_bytes", boom)
    assert run.view()["display_state"] == "complete"


def test_a4_list_request_hashes_each_file_once_and_never_rereads_bote(run, monkeypatch):
    """No digest cache (it was the Argon recheck defect), so work is bounded another way: each request hashes
    each non-BOTE evidence file once, and bote.json is read once by the loader, not again by the adapter."""
    import run_status.adapter as adapter
    run.view()
    calls = []
    real = adapter._sha256_file
    monkeypatch.setattr(adapter, "_sha256_file", lambda p: calls.append(p.name) or real(p))
    for _ in range(3):
        assert run.listed() == "complete"
    assert "bote.json" not in calls
    assert len(calls) == 3 * len(set(calls))  # one hash per file per request


def test_a4_evidence_item_count_is_bounded(run, monkeypatch):
    import run_status.adapter as adapter
    monkeypatch.setattr(adapter, "MAX_EVIDENCE_ITEMS", 1)
    not_complete(run)


# ---- Argon 5: skipped stages ----

@pytest.mark.parametrize("n", [2, 6, 7, 8])
def test_r5_skipped_stage_is_never_complete(run, n):
    run.record["stages"][n - 1] = {"stage": n, "name": "x", "status": "skipped", "why": "cached output reuse"}
    run.save()
    not_complete(run)


def test_r5_skipped_bote_stage_with_deleted_bote_is_not_complete(run):
    run.record["stages"][6] = {"stage": 7, "name": "back of the envelope", "status": "skipped", "why": "cached"}
    run.save()
    (run.dir / "bote.json").unlink()
    run.seal()
    not_complete(run)


def test_r5_all_stages_skipped_is_not_complete(run):
    run.record["stages"] = [{"stage": n, "name": "x", "status": "skipped", "why": "cached"} for n in range(1, 9)]
    run.save()
    not_complete(run)


# ---- Argon 6: stop_after (verify) and malformed containers ----

@pytest.mark.parametrize("value", [0, "", False, [], {}, 5, "6"])
def test_r6_any_non_null_stop_after_is_not_complete(run, value):
    """Reviewer's stop_after claim: the code uses 'is not None', so falsy non-null values already stop the run."""
    run.record["stop_after"] = value
    run.save()
    not_complete(run)


@pytest.mark.parametrize("value", [0, "", [], {}, "yes", None])
def test_r6_malformed_force_is_not_complete(run, value):
    run.record["force"] = value
    run.save()
    not_complete(run)


@pytest.mark.parametrize("wrote", ["bad", 7, {"a": 1}, [], [5], [""], None])
def test_r6_malformed_wrote_on_bote_stage_is_not_complete(run, wrote):
    run.record["stages"][6]["wrote"] = wrote
    run.save()
    not_complete(run)


def test_r6_malformed_wrote_on_any_ok_stage_is_not_complete(run):
    run.record["stages"][3]["wrote"] = "not-a-list"
    run.save()
    not_complete(run)


# ---- Argon 7: duplicate stage numbers, evidence names, JSON keys ----

def test_r7_duplicate_evidence_names_are_not_complete_and_paths_unique(run):
    run.record["stages"][0]["wrote"] = ["C:\\a\\sources.json", "D:\\b\\sources.json"]
    run.save()
    v = not_complete(run)
    paths = [e["path"] for e in v["evidence"]]
    assert len(paths) == len(set(paths))


def test_r7_duplicate_hold_ids_unique(run):
    for n in (6, 7):
        run.record["stages"][n - 1] = {"stage": 7, "name": "x", "status": "waiting", "waiting_on": "evan", "what_to_do": "look"}
    run.save()
    v = not_complete(run)
    ids = [h["id"] for h in v["holds"]]
    assert len(ids) == len(set(ids))


def test_r7_duplicate_key_in_run_json_is_error_not_merged(run):
    text = (run.dir / "run.json").read_text(encoding="utf-8")
    assert text.rstrip().endswith("}")
    text = text.rstrip()[:-1] + ', "failed": [6]}'  # a second "failed" key after the empty one
    (run.dir / "run.json").write_text(text, encoding="utf-8")
    v = not_complete(run)
    assert v["display_state"] == "blocked"


def test_r7_duplicate_key_in_run_json_hiding_nothing_still_error(run):
    text = (run.dir / "run.json").read_text(encoding="utf-8").rstrip()[:-1] + ', "failed": []}'  # same value twice
    (run.dir / "run.json").write_text(text, encoding="utf-8")
    assert not_complete(run)["display_state"] == "blocked"


def test_r7_duplicate_key_in_bote_json_rejects_it(run):
    text = (run.dir / "bote.json").read_text(encoding="utf-8").rstrip()[:-1] + ', "price": 1.0}'
    (run.dir / "bote.json").write_text(text, encoding="utf-8")
    run.seal()
    v = not_complete(run)
    assert {e["name"]: e["state"] for e in v["evidence"]}["bote.json"] != "ok"
    assert all(h["value"] is None for h in v["headline"])


# ---- Likely 1: non-scalar headline values ----

@pytest.mark.parametrize("value", [{"a": 1}, [1], True])
def test_l1_non_scalar_headline_value_is_blank_with_reason(run, value):
    bote = json.loads((run.dir / "bote.json").read_text(encoding="utf-8"))
    bote["price"] = value
    (run.dir / "bote.json").write_text(json.dumps(bote), encoding="utf-8")
    run.seal()
    rows = {h["source_pointer"]: h for h in run.view()["headline"]}
    assert rows["/price"]["value"] is None and rows["/price"]["blank_reason"]
    assert rows["/projection/years/0/noi"]["value"] == 111111.0


# ---- Argon recheck: the hash cache must never validate bytes other than the ones shown ----

def test_r8_same_size_same_mtime_changed_bytes_is_not_verified(run):
    """Warm any digest cache with the sealed bytes, then swap in different bytes of the same size with the
    original modified time. The old metadata-only cache key still matched and kept the Verified badge."""
    bote = run.dir / "bote.json"
    assert run.view()["display_state"] == "complete"  # warm: digest of the sealed bytes is now remembered
    st = bote.stat()
    original = bote.read_bytes()
    changed = original.replace(b'"price": 1111111.0', b'"price": 9999999.0')
    assert changed != original and len(changed) == len(original)
    bote.write_bytes(changed)
    os.utime(bote, ns=(st.st_atime_ns, st.st_mtime_ns))
    after = bote.stat()
    assert (after.st_size, after.st_mtime_ns) == (st.st_size, st.st_mtime_ns)
    v = not_complete(run)
    assert {e["name"]: e["state"] for e in v["evidence"]}["bote.json"] == "hash_mismatch"


def test_r8_displayed_hash_is_the_hash_of_the_bytes_parsed(run):
    """The headline value and the evidence digest come from one read of bote.json."""
    v = run.view()
    ev = {e["name"]: e for e in v["evidence"]}["bote.json"]
    assert ev["sha256"] == _sha(run.dir / "bote.json")
