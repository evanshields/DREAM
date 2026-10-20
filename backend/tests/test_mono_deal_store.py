"""Storage proofs use disposable engineering records with no financial math."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from store.mono_deal_store import MonoConflict, MonoDealStore, MonoNotFound


def revision(number=1, marker="a"):
    return {"revision": number, "identity": {"deal_sha256": marker, "source_hashes": {}},
            "paths": {"bundle": "fixture-only"}, "unknown_future_field": [None, 0, ""]}


def decision(marker="one"):
    return {"decision_id": marker, "actor": {"subject": "disposable-test"}, "reason": "Engineering fixture"}


def job(job_id="j1", number=1, marker="a"):
    return {"job_id": job_id, "revision": number, "identity": revision(number, marker)["identity"],
            "state": "queued", "diagnostics": [], "result": None}


@pytest.fixture
def store(tmp_path):
    result = MonoDealStore(tmp_path / "mono.sqlite")
    result.register("fixture", revision())
    return result


def test_registration_reopen_and_opaque_history(store):
    assert store.register("fixture", revision())["revision"] == 1
    with pytest.raises(MonoConflict):
        store.register("fixture", revision(marker="different"))
    accepted = store.commit_revision("fixture", 1, revision(2, "b"), decision(), "key", "digest")
    reopened = MonoDealStore(store.path)
    assert reopened.current("fixture") == accepted
    assert reopened.current("fixture")["unknown_future_field"] == [None, 0, ""]
    assert reopened.decisions("fixture") == [decision()]
    assert [row["revision"] for row in reopened.revisions("fixture")] == [1, 2]
    assert reopened.register("fixture", revision()) == accepted
    # Returned JSON cannot mutate stored history.
    accepted["identity"]["deal_sha256"] = "tampered"
    assert reopened.current("fixture")["identity"]["deal_sha256"] == "b"


def test_independent_instances_compete_with_database_cas(store):
    barrier = Barrier(2)

    def compete(marker):
        independent = MonoDealStore(store.path)
        barrier.wait()
        try:
            return independent.commit_revision("fixture", 1, revision(2, marker), decision(marker), marker, marker)
        except MonoConflict as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(compete, ["first", "second"]))
    assert sum(isinstance(row, MonoConflict) for row in outcomes) == 1
    assert store.current("fixture")["revision"] == 2
    assert len(store.decisions("fixture")) == 1
    assert len(store.revisions("fixture")) == 2
    assert store.current("fixture")["identity"]["deal_sha256"] == store.decisions("fixture")[0]["decision_id"]


def test_idempotency_returns_original_after_later_edits(store):
    original = store.commit_revision("fixture", 1, revision(2, "b"), decision(), "key", "digest")
    store.commit_revision("fixture", 2, revision(3, "c"), decision("two"), "key2", "digest2")
    assert store.commit_revision("fixture", 1, revision(2, "b"), decision(), "key", "digest") == original
    with pytest.raises(MonoConflict):
        store.commit_revision("fixture", 3, revision(4), decision(), "key", "changed")
    assert len(store.decisions("fixture")) == 2


def test_failure_after_inserts_rolls_back_pointer_history_and_idempotency(store, monkeypatch):
    def fail(*args):
        raise RuntimeError("Injected before commit")

    with monkeypatch.context() as patch:
        patch.setattr(store, "_remember", fail)
        with pytest.raises(RuntimeError):
            store.commit_revision("fixture", 1, revision(2), decision(), "key", "digest")
    assert store.current("fixture")["revision"] == 1
    assert len(store.revisions("fixture")) == 1
    assert store.decisions("fixture") == []
    assert store.commit_revision("fixture", 1, revision(2), decision(), "key", "digest")["revision"] == 2


@pytest.mark.parametrize("bad", [revision(3), {**revision(2), "deal_id": "other"}])
def test_invalid_revision_scope_is_rejected_without_history(store, bad):
    with pytest.raises(MonoConflict):
        store.commit_revision("fixture", 1, bad, decision(), "key", "digest")
    assert len(store.revisions("fixture")) == 1


def test_job_scope_identity_and_receipt_immutability(store):
    store.register("other", revision())
    store.add_job("fixture", job())
    with pytest.raises(MonoNotFound):
        store.job("other", "j1")
    with pytest.raises(MonoNotFound):
        store.update_job("other", "j1", {"state": "running"})
    with pytest.raises(MonoNotFound):
        store.add_job("fixture", job("missing-revision", 2))
    with pytest.raises(MonoConflict):
        store.add_job("fixture", job("wrong-identity", marker="x"))
    with pytest.raises(MonoConflict):
        store.update_job("fixture", "j1", {"identity": {}})
    with pytest.raises(MonoConflict):
        store.add_job("other", job())
    result = {"result_id": "result", "identity": {"native_calculation_id": "native"}, "outputs": {"fixture": None}}
    store.update_job("fixture", "j1", {"state": "running"})
    receipt = store.update_job("fixture", "j1", {"state": "complete", "result": result})
    assert store.update_job("fixture", "j1", {"state": "complete"}) == receipt
    for changed in ({"state": "failed"}, {"result": {}}, {"warnings": ["altered"]}):
        with pytest.raises(MonoConflict):
            store.update_job("fixture", "j1", changed)
    assert MonoDealStore(store.path).job("fixture", "j1") == receipt


def complete(store, job_id="j1", number=1, marker="a"):
    store.add_job("fixture", job(job_id, number, marker))
    return store.update_job("fixture", job_id, {"state": "complete", "result": {"result_id": f"result-{job_id}", "outputs": {}}})


def test_result_promotion_and_edit_invalidation(store):
    complete(store)
    identity = revision()["identity"]
    assert not store.promote_result("fixture", "j1", 1, {"deal_sha256": "wrong"})
    assert store.promote_result("fixture", "j1", 1, identity)
    assert store.current_result("fixture")["job_id"] == "j1"
    event = {"gate": "comps", "decision": "confirm", "revision": 1, "actor": {"subject": "disposable-test"}}
    store.record_gate("fixture", 1, event, "comps", "digest")
    store.commit_revision("fixture", 1, revision(2, "b"), decision(), "edit", "digest-edit")
    assert store.current_result("fixture") is None
    assert store.gates("fixture") == {"comps": None, "go_no_go": None}
    assert store.gate_history("fixture") == [event]
    assert not store.promote_result("fixture", "j1", 1, identity)
    assert store.job("fixture", "j1")["result"]["result_id"] == "result-j1"
    complete(store, "j2", 2, "b")
    assert store.promote_result("fixture", "j2", 2, revision(2, "b")["identity"])


def test_old_running_job_completion_never_becomes_current(store):
    store.add_job("fixture", job())
    store.update_job("fixture", "j1", {"state": "running"})
    store.commit_revision("fixture", 1, revision(2, "b"), decision(), "edit", "digest")
    store.update_job("fixture", "j1", {"state": "complete", "result": {"result_id": "old"}})
    assert not store.promote_result("fixture", "j1", 1, revision()["identity"])
    assert store.current_result("fixture") is None


def test_promotion_racing_an_edit_never_leaves_an_old_current_result(store):
    complete(store)
    barrier = Barrier(2)

    def promote():
        independent = MonoDealStore(store.path)
        barrier.wait()
        return independent.promote_result("fixture", "j1", 1, revision()["identity"])

    def edit():
        independent = MonoDealStore(store.path)
        barrier.wait()
        return independent.commit_revision("fixture", 1, revision(2, "b"), decision(), "edit", "digest")

    with ThreadPoolExecutor(max_workers=2) as pool:
        promoted = pool.submit(promote)
        edited = pool.submit(edit)
        assert isinstance(promoted.result(), bool)
        assert edited.result()["revision"] == 2
    assert store.current_result("fixture") is None
    assert store.job("fixture", "j1")["result"] is not None


def test_failed_revision_transaction_preserves_current_gates_and_result(store, monkeypatch):
    complete(store)
    store.promote_result("fixture", "j1", 1, revision()["identity"])
    event = {"gate": "comps", "decision": "confirm", "revision": 1}
    store.record_gate("fixture", 1, event, "gate", "gate-digest")

    def fail(*args):
        raise RuntimeError("Injected after pointer update")

    monkeypatch.setattr(store, "_remember", fail)
    with pytest.raises(RuntimeError):
        store.commit_revision("fixture", 1, revision(2), decision(), "edit", "digest")
    assert store.current("fixture")["revision"] == 1
    assert store.gates("fixture")["comps"] == event
    assert store.current_result("fixture")["job_id"] == "j1"


def test_promote_requires_complete_receipt(store):
    store.add_job("fixture", job())
    assert not store.promote_result("fixture", "j1", 1, revision()["identity"])
    store.update_job("fixture", "j1", {"state": "complete", "result": {"outputs": {}}})
    assert not store.promote_result("fixture", "j1", 1, revision()["identity"])


def test_cancel_request_cannot_be_promoted_if_native_completion_wins_terminal_write(store):
    store.add_job('fixture', job())
    store.update_job('fixture', 'j1', {'cancel_requested': True})
    store.update_job('fixture', 'j1', {'state': 'complete', 'result': {'result_id': 'native-finished', 'outputs': {}}})
    assert not store.promote_result('fixture', 'j1', 1, revision()['identity'])
    assert store.current_result('fixture') is None
    assert store.job('fixture', 'j1')['result']['result_id'] == 'native-finished'


def test_gate_idempotency_history_and_scope(store):
    event = {"gate": "comps", "decision": "confirm", "revision": 1}
    assert store.record_gate("fixture", 1, event, "gate", "digest") == event
    assert store.record_gate("fixture", 1, event, "gate", "digest") == event
    with pytest.raises(MonoConflict):
        store.record_gate("fixture", 1, {**event, "decision": "go"}, "gate", "changed")
    with pytest.raises(MonoConflict):
        store.commit_revision("fixture", 1, revision(2), decision(), "gate", "digest")
    with pytest.raises(MonoConflict):
        store.record_gate("fixture", 1, {**event, "deal_id": "other"}, "other", "digest")
    store.commit_revision("fixture", 1, revision(2), decision(), "edit", "edit-digest")
    assert store.record_gate("fixture", 1, event, "gate", "digest") == event
    with pytest.raises(MonoConflict):
        store.record_gate("fixture", 1, event, "stale", "digest")
    assert store.gate_history("fixture") == [event]
    assert store.gates("fixture")["comps"] is None


def test_recovery_persists_without_resubmission_and_preserves_terminals(store):
    store.add_job("fixture", job("queued"))
    store.add_job("fixture", {**job("running"), "state": "running"})
    store.add_job("fixture", {**job("stale"), "state": "stale"})
    receipt = complete(store)
    reopened = MonoDealStore(store.path)
    assert set(reopened.recover_interrupted()) == {"queued", "running"}
    assert MonoDealStore(store.path).job("fixture", "running")["state"] == "interrupted"
    assert "No automatic resubmission" in reopened.job("fixture", "queued")["diagnostics"][-1]
    assert reopened.job("fixture", "j1") == receipt
    assert reopened.job("fixture", "stale")["state"] == "stale"
    assert reopened.recover_interrupted() == []


def test_missing_deal_is_not_empty_history(store):
    for method in (store.current, store.revisions, store.decisions, store.jobs, store.gates, store.gate_history, store.current_result):
        with pytest.raises(MonoNotFound):
            method("absent")
