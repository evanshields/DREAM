"""Wave C-v1 — JobStore acceptance tests. SQLite job lifecycle: idempotent create, opaque
round-trip, state-machine-enforced transitions, cooperative cancel, append-only audit, open-question
answer, and the durable UnderwriteState resume ledger persisted THROUGH the store (no loose files)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs.job_store import SQLiteJobStore, JobNotFound  # noqa: E402
from jobs.contracts import JobStatus, JobPhase, OpenQuestion, InvalidTransition  # noqa: E402

NOW = "2026-06-09T12:00:00Z"
LATER = "2026-06-09T13:00:00Z"


def store():
    return SQLiteJobStore(":memory:")


def test_create_then_get_round_trips():
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan@shieldstone.co",
                       now_iso=NOW, idempotency_key="k1")
    got = s.get_job(job.job_id)
    assert got.deal_id == "d1"
    assert got.routing == "ACQ"
    assert got.status == JobStatus.SUBMITTED
    assert got.phase == JobPhase.WAVE0_ROUTING
    assert got.mode == "HITL"
    assert got.owner == "evan@shieldstone.co"
    assert got.created_at == NOW


def test_create_is_idempotent_on_key():
    s = store()
    a = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW, idempotency_key="dup")
    b = s.create_job(deal_id="d2", routing="ACQ", owner="evan", now_iso=LATER, idempotency_key="dup")
    # Same key -> same job (no duplicate); first deal_id wins.
    assert a.job_id == b.job_id
    assert b.deal_id == "d1"
    assert len(s.list_jobs()) == 1


def test_empty_key_creates_distinct_jobs():
    s = store()
    a = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    b = s.create_job(deal_id="d2", routing="ACQ", owner="evan", now_iso=NOW)
    assert a.job_id != b.job_id
    assert len(s.list_jobs()) == 2


def test_transition_enforces_state_machine():
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    # Legal: SUBMITTED -> ROUTING
    s.transition(job.job_id, JobStatus.ROUTING, NOW, phase=JobPhase.WAVE0_ROUTING)
    assert s.get_job(job.job_id).status == JobStatus.ROUTING
    # Illegal: ROUTING -> AWAITING_CP1 (not in ALLOWED_TRANSITIONS) -> fail closed
    with pytest.raises(InvalidTransition):
        s.transition(job.job_id, JobStatus.AWAITING_CP1, NOW)


def test_full_happy_path_transitions():
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    jid = job.job_id
    s.transition(jid, JobStatus.ROUTING, NOW)
    s.transition(jid, JobStatus.ANALYZING, NOW)
    s.transition(jid, JobStatus.SYNTHESIZING, NOW)
    s.transition(jid, JobStatus.AWAITING_CP1, NOW, phase=JobPhase.CP1)
    final = s.get_job(jid)
    assert final.status == JobStatus.AWAITING_CP1
    assert final.phase == JobPhase.CP1
    # HITL: there is NO legal transition to COMPLETED via the normal machine except an explicit one
    assert final.can_advance_to(JobStatus.COMPLETED)  # the only outbound edge


def test_request_cancel_sets_flag_and_is_noop_on_terminal():
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    jid = job.job_id
    s.transition(jid, JobStatus.ROUTING, NOW)
    s.request_cancel(jid, now_iso=LATER)
    assert s.get_job(jid).cancel_requested is True
    # Drive to terminal, then cancel is a no-op (does not flip a terminal job)
    s.transition(jid, JobStatus.CANCELLED, LATER)
    s.request_cancel(jid)  # no raise, no change
    assert s.get_job(jid).status == JobStatus.CANCELLED


def test_append_audit_is_monotonic_and_validated():
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    jid = job.job_id
    s.append_audit(jid, "phase", "first", ts=NOW)
    s.append_audit(jid, "gate", "second", detail={"ok": True}, ts=LATER)
    audit = s.get_job(jid).audit
    assert [e.seq for e in audit] == [0, 1]
    assert audit[1].kind == "gate" and audit[1].detail == {"ok": True}
    # bad kind rejected
    with pytest.raises(ValueError):
        s.append_audit(jid, "not_a_kind", "x", ts=NOW)


def test_open_question_add_and_answer():
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    jid = job.job_id
    q = OpenQuestion(id="oq-1", field="meta.critical_inputs.exit_cap",
                     question="exit cap?", blocking=True)
    s.add_open_question(jid, q, now_iso=NOW)
    assert s.get_job(jid).has_blocking_questions() is True
    s.answer_open_question(jid, "oq-1", 0.0625, now_iso=LATER)
    answered = s.get_job(jid).open_questions[0]
    assert answered.answered is True and answered.answer == 0.0625
    assert s.get_job(jid).has_blocking_questions() is False
    with pytest.raises(KeyError):
        s.answer_open_question(jid, "nope", 1, now_iso=LATER)


def test_underwrite_state_persists_through_store_no_loose_file():
    """The resume ledger (UnderwriteState) round-trips through the store as an opaque column."""
    from state_ledger import UnderwriteState, CriticalInputs
    s = store()
    job = s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    jid = job.job_id
    assert s.get_state(jid) is None
    st = UnderwriteState(slug="esplanade", routing="ACQ",
                         critical_inputs=CriticalInputs(purchase_price=55e6, hold_years=7, exit_cap=0.06))
    st.record_phase(0, "wave0", "complete", "captured critical inputs")
    s.save_state(jid, st)
    got = s.get_state(jid)
    assert got.slug == "esplanade"
    assert got.critical_inputs.hold_years == 7
    assert got.completed_phases() == [0]


def test_get_missing_raises():
    s = store()
    with pytest.raises(JobNotFound):
        s.get_job("nope")


def test_list_filters():
    s = store()
    s.create_job(deal_id="d1", routing="ACQ", owner="evan", now_iso=NOW)
    j2 = s.create_job(deal_id="d2", routing="ACQ", owner="chuck", now_iso=NOW)
    s.transition(j2.job_id, JobStatus.ROUTING, NOW)
    assert {j.deal_id for j in s.list_jobs(owner="evan")} == {"d1"}
    assert {j.deal_id for j in s.list_jobs(status=JobStatus.ROUTING.value)} == {"d2"}
    assert {j.deal_id for j in s.list_jobs(deal_id="d2")} == {"d2"}
