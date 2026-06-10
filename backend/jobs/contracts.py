"""
backend/jobs/contracts.py — Wave C-v1 shared job contracts (DREAM fast-path service).

The single source of truth for the names every Wave C module depends on (intake router,
synthesis runner, store adapter, CP-1 presenter). Contracts ONLY: no I/O, no engine import,
no LLM dependency, so this module is trivially importable and unit-testable WITHOUT live LLM
calls (a stubbed analytical slice just emits OpenQuestion / AuditEvent records).

LOCKED Wave C-v1 invariants encoded here:
  * SEQUENTIAL synthesis: the 5 Wave-1 slices run one-after-another; phases reflect that order.
  * ACQ ROUTE ONLY: routing is carried but the runner proves the ACQ (Esplanade) path.
  * HITL ONLY: a run ALWAYS stops at AWAITING_CP1 and NEVER auto-completes. There is no
    transition AWAITING_CP1 -> COMPLETED in ALLOWED_TRANSITIONS; only an explicit human action
    (a later, separately-gated unlock) advances it. mode is pinned to 'HITL'.
  * Deterministic values NEVER come from an LLM: headline_metrics + qa.* come from the engine.
    The LLM (Kimi) is reserved for judgment slices, and each LLM-inferred (non-cited) value
    becomes an OpenQuestion so CP-1 can surface it.

JSON-NATIVE / STDLIB ONLY: floats not Decimal (Decimal stays inside backend/engine_boundary.py),
plain dict/list/str/int/float/bool/None. Every dataclass round-trips through to_dict/from_dict so
the whole JobRecord persists as an OPAQUE document through DealStore alongside the spec.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums (stored as their string .value in the persisted document)
# ---------------------------------------------------------------------------

class JobStatus(str, enum.Enum):
    """Lifecycle of a single fast-path underwrite run."""
    SUBMITTED = "submitted"            # intake accepted, deal record created, nothing run yet
    ROUTING = "routing"               # Wave 0: ACQ/EFB decision + BL-17 critical-input capture
    AWAITING_INPUT = "awaiting_input"  # PAUSED: routing ambiguous OR missing critical inputs; needs a human answer
    ANALYZING = "analyzing"           # Wave 1: the 5 analytical slices run sequentially
    SYNTHESIZING = "synthesizing"     # Wave 2: merge slices -> engine -> headline_metrics + gates
    AWAITING_CP1 = "awaiting_cp1"     # HITL STOP: spec + headline_metrics + every gate presented for the human glance
    COMPLETED = "completed"           # human advanced past CP-1 (explicit; NOT auto-reached in v1)
    FAILED = "failed"                 # unrecoverable error (gate harness raised, engine error, bad input)
    CANCELLED = "cancelled"           # cancel_requested honored from an active state

    def __str__(self) -> str:  # so f-strings / logs read the value, not "JobStatus.X"
        return self.value


class JobPhase(str, enum.Enum):
    """Where the run currently is, mirroring the fast-path waves (sequential in v1)."""
    WAVE0_ROUTING = "wave0_routing"
    WAVE1_T12 = "wave1_t12"
    WAVE1_RENTROLL = "wave1_rentroll"
    WAVE1_ASSUMPTIONS = "wave1_assumptions"
    WAVE1_COMPS = "wave1_comps"
    WAVE1_MARKETDATA = "wave1_marketdata"
    WAVE2_SYNTHESIS = "wave2_synthesis"
    CP1 = "cp1"

    def __str__(self) -> str:
        return self.value


# Ordered Wave-1 slice phases — the runner iterates this list IN ORDER (sequential, not parallel).
WAVE1_SLICE_PHASES: tuple = (
    JobPhase.WAVE1_T12,
    JobPhase.WAVE1_RENTROLL,
    JobPhase.WAVE1_ASSUMPTIONS,
    JobPhase.WAVE1_COMPS,
    JobPhase.WAVE1_MARKETDATA,
)

# Statuses from which a cancel may be honored (any non-terminal state).
ACTIVE_STATUSES: frozenset = frozenset({
    JobStatus.SUBMITTED,
    JobStatus.ROUTING,
    JobStatus.AWAITING_INPUT,
    JobStatus.ANALYZING,
    JobStatus.SYNTHESIZING,
    JobStatus.AWAITING_CP1,
})

# Terminal statuses — no outbound transitions.
TERMINAL_STATUSES: frozenset = frozenset({
    JobStatus.COMPLETED,
    JobStatus.FAILED,
    JobStatus.CANCELLED,
})

# Provenance tags for any value surfaced to the human at CP-1.
SOURCE_LLM_INFERRED = "llm-inferred"   # judgment-slice output with no document citation -> becomes an OpenQuestion
SOURCE_CITED = "cited"                 # carries a doc/API citation (OM p.3, T-12+3%, FMR ...); deterministic-safe

# AuditEvent.kind vocabulary (closed set; validated by new_audit()).
AUDIT_KINDS: frozenset = frozenset({"llm_call", "gate", "spec_mutation", "phase", "error"})


# ---------------------------------------------------------------------------
# State machine (the ONE authoritative transition table)
# ---------------------------------------------------------------------------

# Allowed forward/normal transitions. cancel + fail are added uniformly below.
_BASE_TRANSITIONS: Dict[JobStatus, set] = {
    JobStatus.SUBMITTED:      {JobStatus.ROUTING},
    JobStatus.ROUTING:        {JobStatus.AWAITING_INPUT, JobStatus.ANALYZING},
    JobStatus.AWAITING_INPUT: {JobStatus.ROUTING, JobStatus.ANALYZING},  # resume after a human answer
    JobStatus.ANALYZING:      {JobStatus.SYNTHESIZING, JobStatus.AWAITING_INPUT},
    JobStatus.SYNTHESIZING:   {JobStatus.AWAITING_CP1,                   # HITL: synthesis terminates at CP-1
                               JobStatus.AWAITING_INPUT},                # ...or asks for missing engine inputs
    JobStatus.AWAITING_CP1:   {JobStatus.COMPLETED},                     # ONLY an explicit human action; never auto
    JobStatus.COMPLETED:      set(),
    JobStatus.FAILED:         set(),
    JobStatus.CANCELLED:      set(),
}


def _build_transition_table() -> Dict[JobStatus, frozenset]:
    table: Dict[JobStatus, frozenset] = {}
    for state, nxt in _BASE_TRANSITIONS.items():
        allowed = set(nxt)
        if state in ACTIVE_STATUSES:
            allowed.add(JobStatus.CANCELLED)  # cancel from any active state
            allowed.add(JobStatus.FAILED)     # any active state may error out
        table[state] = frozenset(allowed)
    return table


ALLOWED_TRANSITIONS: Dict[JobStatus, frozenset] = _build_transition_table()


def can_transition(src: JobStatus, dst: JobStatus) -> bool:
    """True iff dst is a legal next status from src. A no-op (src == dst) is allowed (idempotent set)."""
    if src == dst:
        return True
    return dst in ALLOWED_TRANSITIONS.get(src, frozenset())


class InvalidTransition(ValueError):
    """Raised by the runner when an illegal status change is attempted (fail closed)."""


def assert_transition(src: JobStatus, dst: JobStatus) -> None:
    if not can_transition(src, dst):
        raise InvalidTransition(f"illegal job transition {src.value} -> {dst.value}")


# ---------------------------------------------------------------------------
# OpenQuestion — every LLM-inferred (non-cited) value the human must confirm at CP-1
# ---------------------------------------------------------------------------

@dataclass
class OpenQuestion:
    """One thing CP-1 needs a human to confirm/answer.

    Created for: (a) a routing ambiguity / missing BL-17 critical input (AWAITING_INPUT), and
    (b) every LLM-inferred value — any judgment-slice cell/metric whose `source == 'llm-inferred'`
    (no document citation) becomes an OpenQuestion so it is non-collapsibly surfaced at CP-1.
    Deterministic engine outputs (headline_metrics, qa.*) never spawn one — they are not LLM-inferred.
    """
    id: str
    field: str                                   # the spec field/cell address in question (e.g. 'B79', 'meta.routing')
    question: str
    current_value: Any = None                    # the value the run is proceeding with absent an answer
    source: str = SOURCE_LLM_INFERRED            # SOURCE_LLM_INFERRED | SOURCE_CITED
    options: Optional[List[Any]] = None          # discrete choices when applicable (e.g. ['ACQ','EFB'])
    answered: bool = False
    answer: Any = None
    blocking: bool = False                        # True for missing critical inputs / routing ambiguity (gates progress)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OpenQuestion":
        return cls(**{k: d.get(k) for k in (
            "id", "field", "question", "current_value", "source",
            "options", "answered", "answer", "blocking") if k in d})


# ---------------------------------------------------------------------------
# AuditEvent — append-only trail (LLM call / gate / spec mutation / phase / error)
# ---------------------------------------------------------------------------

@dataclass
class AuditEvent:
    """One append-only entry in the run's audit trail. Mirrors the in-workbook Claude Log:
    never mutated, only appended; `seq` is monotonic per job."""
    seq: int
    kind: str                                    # one of AUDIT_KINDS
    summary: str                                 # one-line human-readable result
    detail: Dict[str, Any] = field(default_factory=dict)
    ts: str = ""                                 # ISO-8601, supplied by the caller (no clock in contracts)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AuditEvent":
        return cls(
            seq=int(d["seq"]),
            kind=d["kind"],
            summary=d.get("summary", ""),
            detail=dict(d.get("detail") or {}),
            ts=d.get("ts", ""),
        )


# ---------------------------------------------------------------------------
# JobRecord — the durable job object (persisted OPAQUELY via DealStore)
# ---------------------------------------------------------------------------

@dataclass
class JobRecord:
    """One fast-path underwrite run. Persisted as an opaque document; `deal_id` ties it to the
    DealStore DealRecord that holds the spec + state ledger. `idempotency_key` makes a retried
    intake reuse this job/deal instead of creating a duplicate."""
    job_id: str
    deal_id: str
    routing: str                                 # 'ACQ' (v1) | 'EFB' (later) — carried, not LLM-derived for determinism
    status: JobStatus = JobStatus.SUBMITTED
    phase: JobPhase = JobPhase.WAVE0_ROUTING
    mode: str = "HITL"                           # LOCKED to HITL in Wave C-v1 (HOTL is a separate later unlock)
    created_at: str = ""                         # ISO, caller-supplied
    updated_at: str = ""                         # ISO, caller-supplied
    owner: str = ""
    idempotency_key: str = ""                    # intake-supplied; unique per logical submission
    cancel_requested: bool = False               # cooperative cancel flag; honored at the next runner checkpoint
    error: Optional[str] = None                  # set when status == FAILED
    open_questions: List[OpenQuestion] = field(default_factory=list)
    audit: List[AuditEvent] = field(default_factory=list)

    # ---- status helpers ----
    def is_active(self) -> bool:
        return self.status in ACTIVE_STATUSES

    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES

    def can_advance_to(self, dst: JobStatus) -> bool:
        return can_transition(self.status, dst)

    # ---- open-question helpers ----
    def blocking_questions(self) -> List[OpenQuestion]:
        return [q for q in self.open_questions if q.blocking and not q.answered]

    def has_blocking_questions(self) -> bool:
        return bool(self.blocking_questions())

    def add_open_question(self, q: OpenQuestion) -> OpenQuestion:
        self.open_questions.append(q)
        return q

    # ---- audit helpers (monotonic seq; ts supplied by caller) ----
    def next_seq(self) -> int:
        return (max((e.seq for e in self.audit), default=-1)) + 1

    def add_audit(self, kind: str, summary: str,
                  detail: Optional[Dict[str, Any]] = None, ts: str = "") -> AuditEvent:
        if kind not in AUDIT_KINDS:
            raise ValueError(f"unknown audit kind {kind!r}; expected one of {sorted(AUDIT_KINDS)}")
        ev = AuditEvent(seq=self.next_seq(), kind=kind, summary=summary,
                        detail=dict(detail or {}), ts=ts)
        self.audit.append(ev)
        return ev

    # ---- (de)serialization: opaque JSON document for DealStore ----
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "deal_id": self.deal_id,
            "routing": self.routing,
            "status": self.status.value,
            "phase": self.phase.value,
            "mode": self.mode,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "owner": self.owner,
            "idempotency_key": self.idempotency_key,
            "cancel_requested": self.cancel_requested,
            "error": self.error,
            "open_questions": [q.to_dict() for q in self.open_questions],
            "audit": [e.to_dict() for e in self.audit],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "JobRecord":
        return cls(
            job_id=d["job_id"],
            deal_id=d["deal_id"],
            routing=d.get("routing", "ACQ"),
            status=JobStatus(d.get("status", JobStatus.SUBMITTED.value)),
            phase=JobPhase(d.get("phase", JobPhase.WAVE0_ROUTING.value)),
            mode=d.get("mode", "HITL"),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            owner=d.get("owner", ""),
            idempotency_key=d.get("idempotency_key", ""),
            cancel_requested=bool(d.get("cancel_requested", False)),
            error=d.get("error"),
            open_questions=[OpenQuestion.from_dict(q) for q in d.get("open_questions", [])],
            audit=[AuditEvent.from_dict(e) for e in d.get("audit", [])],
        )


# Convenience: phase ordering for a sequential ACQ run (Wave 0 -> 5 slices -> synthesis -> CP-1).
JOB_PHASE_ORDER: tuple = (
    (JobPhase.WAVE0_ROUTING,)
    + WAVE1_SLICE_PHASES
    + (JobPhase.WAVE2_SYNTHESIS, JobPhase.CP1)
)
