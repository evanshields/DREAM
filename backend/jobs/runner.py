"""
backend/jobs/runner.py — Wave C-v1 SEQUENTIAL job runner (the chat-bot fast path engine).

run_job(job_id) drives one fast-path underwrite to the HITL stop, SEQUENTIALLY (v1):

    SUBMITTED
      -> ROUTING          run_wave0 (per-routing critical inputs + ACQ/EFB routing decision)
         |-- not ready -> AWAITING_INPUT  (blocking OpenQuestions persisted; STOP, return)
      -> ANALYZING        the five analytical slices, one after another (StubAnalysts default;
                          KimiAnalysts when wired). Each slice + the merge are audited.
      -> SYNTHESIZING     run_synthesis (validated engine -> headline_metrics; BL gate harness)
      -> AWAITING_CP1     persist the spec to DealStore; STOP. HITL: NEVER auto-completes.

Locked invariants honored here:
  * HITL ONLY — the terminal of a successful run is AWAITING_CP1. There is no transition to
    COMPLETED (contracts.ALLOWED_TRANSITIONS has none from SYNTHESIZING); only an explicit human
    action advances past CP-1.
  * Cooperative cancel — cancel_requested is checked BETWEEN phases (the runner re-reads the job
    at each checkpoint); an honored cancel transitions ANALYZING/etc -> CANCELLED and returns.
  * Determinism — headline_metrics + qa.* come ONLY from run_synthesis (engine + gate harness),
    never from the analysts. Any analyst llm-inferred cell becomes an OpenQuestion at CP-1.
  * Fail closed — any exception transitions the active job -> FAILED with the error recorded; it
    is re-raised so the caller (router) can surface it.

NOTE (async): v1 runs synchronously (the router awaits it). Where an async work queue plugs in
later, replace the direct run_job(...) call at the router with an enqueue; run_job itself is the
worker body and needs no change.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Optional

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store import get_deal_store, DealStore  # noqa: E402
from jobs.contracts import (  # noqa: E402
    JobStatus, JobPhase, WAVE1_SLICE_PHASES, OpenQuestion, SOURCE_CITED,
)
from jobs.job_store import get_job_store, SQLiteJobStore  # noqa: E402
from jobs.wave0 import run_wave0  # noqa: E402
from jobs.analysts import StubAnalysts, merge_slices  # noqa: E402
from jobs.synthesis import run_synthesis, MissingEngineInputsError  # noqa: E402

# Map slice index -> the WAVE1 phase for audit/phase tracking.
_SLICE_PHASE = list(WAVE1_SLICE_PHASES)


class JobCancelled(Exception):
    """Raised internally when a cooperative cancel is honored mid-run (caught by run_job)."""


def _now(now_iso: Optional[str]) -> str:
    """The runner keeps no clock (deterministic, like DealStore). Callers pass now_iso; tests pass a
    fixed string. If omitted, fall back to an ISO timestamp so production calls still stamp time."""
    if now_iso:
        return now_iso
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _check_cancel(job_store: SQLiteJobStore, job_id: str) -> None:
    if job_store.get_job(job_id).cancel_requested:
        raise JobCancelled()


def run_job(
    job_id: str,
    analysts: Any = None,
    *,
    now_iso: Optional[str] = None,
    intake_summary: Optional[dict] = None,
    deal_docs: Optional[dict] = None,
    job_store: Optional[SQLiteJobStore] = None,
    deal_store: Optional[DealStore] = None,
):
    """Run one fast-path underwrite to its HITL stop. Returns the final JobRecord.

    Args:
      job_id: an existing SUBMITTED job (created by the intake router; its deal_id points at a
              DealStore record the spec is written back to).
      analysts: an AnalystSet-like object with run_all(...) (default: StubAnalysts — no LLM).
                Wire KimiAnalysts here when running live.
      intake_summary: the parsed deal-package summary Wave 0 + the analysts consume.
      now_iso: caller-supplied ISO timestamp (deterministic; tests pin it).

    On AWAITING_INPUT (missing critical inputs / ambiguous routing) the run STOPS and returns; the
    blocking OpenQuestions are on the returned job. On success it STOPS at AWAITING_CP1 (HITL)."""
    js = job_store or get_job_store()
    ds = deal_store or get_deal_store()
    analysts = analysts or StubAnalysts()
    intake_summary = dict(intake_summary or {})
    ts = _now(now_iso)

    job = js.get_job(job_id)
    # Only a fresh (SUBMITTED) or a just-answered (back-to-ROUTING) job is runnable. A terminal
    # job, or one already paused at AWAITING_CP1 (HITL: a human advances it, not a re-run), is a
    # no-op — re-running must never reset progress or re-drive the engine.
    if job.status not in (JobStatus.SUBMITTED, JobStatus.ROUTING):
        return job

    try:
        # ---- Wave 0: routing + BL-17 critical inputs -------------------------------------------
        js.transition(job_id, JobStatus.ROUTING, ts, phase=JobPhase.WAVE0_ROUTING)
        js.append_audit(job_id, "phase", "Wave 0: routing + critical-input capture", ts=ts)
        _check_cancel(js, job_id)

        wave0 = run_wave0(js.get_job(job_id), intake_summary)

        if not wave0["ready"]:
            for q in wave0["awaiting"]:
                js.add_open_question(job_id, q, now_iso=ts)
            js.transition(job_id, JobStatus.AWAITING_INPUT, ts, phase=JobPhase.WAVE0_ROUTING)
            js.append_audit(
                job_id, "phase",
                f"Wave 0 STOP: awaiting {len(wave0['awaiting'])} blocking input(s)",
                detail={"basis": wave0.get("routing_basis")}, ts=ts,
            )
            return js.get_job(job_id)

        # Full critical-inputs dict: wave0's normalized BL-17 three win, but EXTRA engine fields
        # answered at AWAITING_INPUT (bridge_loan, refi_rate, ...) ride along to synthesis —
        # wave0 only extracts the locked three and would otherwise drop the answers.
        critical_inputs = {
            **(intake_summary.get("critical_inputs") or {}),
            **wave0["critical_inputs"],
        }

        # ---- Wave 1: the five analytical slices, SEQUENTIALLY ----------------------------------
        js.transition(job_id, JobStatus.ANALYZING, ts, phase=_SLICE_PHASE[0])
        slice_outputs = []
        runner = getattr(analysts, "run_all", None)
        if runner is not None:
            # run_all returns the five outputs in order; we still audit per phase + check cancel.
            # The SLICES get only wave0's normalized per-route critical inputs (their documented
            # contract, ALL scalars — the ACQ BL-17 trio, or the EFB stabilized_noi + optional
            # bond scalars). The full merged critical_inputs — which may carry answered ENGINE fields
            # including arrays like noi_series — goes to synthesis ONLY: feeding arrays to the LLM
            # as "authoritative critical inputs" makes it echo them back as (schema-invalid) cells.
            outputs = analysts.run_all(deal_docs, intake_summary, wave0["critical_inputs"])
            for i, out in enumerate(outputs):
                _check_cancel(js, job_id)
                phase = _SLICE_PHASE[min(i, len(_SLICE_PHASE) - 1)]
                js.transition(job_id, JobStatus.ANALYZING, ts, phase=phase)
                js.append_audit(job_id, "llm_call", f"Wave 1 slice {phase.value} complete", ts=ts)
                slice_outputs.append(out)
        else:  # pragma: no cover - protocol fallback
            raise TypeError("analysts must expose run_all(...)")

        merged = merge_slices(slice_outputs)
        # Ensure routing flows into the spec meta (synthesis dispatches on meta.routing).
        merged.setdefault("meta", {}).setdefault("routing", wave0["routing"])
        merged["meta"].setdefault("routing_basis", wave0.get("routing_basis", ""))
        # Deal identity must SURVIVE synthesis: the slices' meta rarely carries the app-level
        # deal_name/slug/template/mode, and the CP-1 ds.put re-derives the index from the NEW
        # spec — without this carry-forward, computed deals lose their names in the pipeline.
        seed_meta = ds.get(js.get_job(job_id).deal_id).spec.get("meta", {}) or {}
        for key in ("deal_name", "slug", "template", "mode"):
            if seed_meta.get(key):
                merged["meta"].setdefault(key, seed_meta[key])

        _check_cancel(js, job_id)

        # ---- Wave 2: synthesis (engine + gates) — deterministic, no LLM ------------------------
        js.transition(job_id, JobStatus.SYNTHESIZING, ts, phase=JobPhase.WAVE2_SYNTHESIS)
        try:
            result = run_synthesis(merged, critical_inputs, ts, return_result=True)
        except MissingEngineInputsError as e:
            # ASK, don't crash (the BL-17 spirit, applied to the full engine contract): the deal
            # package did not yield a runnable payload — one blocking question per missing field.
            # field uses the meta.critical_inputs.* namespace so the existing answer->resume
            # mapping (_summary_from_answers) routes the values back without new parsing.
            engine_route = getattr(e, "routing", "ACQ")
            for name in e.missing:
                js.add_open_question(job_id, OpenQuestion(
                    id=f"oq-{job_id}-engine-{name}",
                    field=f"meta.critical_inputs.{name}",
                    question=(f"Provide {name} for the {engine_route} engine — the deal package "
                              f"did not yield it (or the value was invalid)."),
                    current_value=None,
                    source=SOURCE_CITED,
                    blocking=True,
                ), now_iso=ts)
            js.append_audit(job_id, "error", f"synthesis paused for inputs: {e}", ts=ts)
            js.transition(job_id, JobStatus.AWAITING_INPUT, ts)
            return js.get_job(job_id)
        js.append_audit(
            job_id, "gate",
            f"Synthesis gates ok={result.gate_summary.ok} "
            f"blocking={result.gate_summary.blocking}",
            detail=result.gate_summary.as_dict(), ts=ts,
        )

        # ---- FAIL CLOSED on a blocking gate: a RED underwrite must never present as a clean CP-1
        if not result.gate_summary.ok:
            job = js.get_job(job_id)
            deal = ds.get(job.deal_id)
            ds.put(job.deal_id, result.spec, expected_version=deal.version,
                   now_iso=ts, status="gate_failed")  # spec kept for forensics, never 'computed'
            js.append_audit(job_id, "gate",
                            f"BLOCKING gate(s) failed: {result.gate_summary.blocking} — "
                            "failing closed (spec persisted as gate_failed)",
                            detail=result.gate_summary.as_dict(), ts=ts)
            js.transition(job_id, JobStatus.FAILED, ts,
                          error=f"blocking QA gates failed: {result.gate_summary.blocking}")
            return js.get_job(job_id)

        # Persist every llm-inferred cell as an OpenQuestion for the CP-1 glance.
        for q in result.open_questions:
            js.add_open_question(job_id, q, now_iso=ts)

        # ---- persist the spec to DealStore (the deal already exists; bump its version) ---------
        job = js.get_job(job_id)
        deal = ds.get(job.deal_id)
        ds.put(job.deal_id, result.spec, expected_version=deal.version,
               now_iso=ts, status="computed")
        js.append_audit(job_id, "spec_mutation", "spec persisted to DealStore (status=computed)",
                        detail={"irr": result.headline_metrics.get("irr")}, ts=ts)

        # ---- HITL STOP at CP-1 (NEVER auto-completes) ------------------------------------------
        js.transition(job_id, JobStatus.AWAITING_CP1, ts, phase=JobPhase.CP1)
        js.append_audit(job_id, "phase", "STOP at CP-1 (HITL): spec + headline + gates presented",
                        ts=ts)
        return js.get_job(job_id)

    except JobCancelled:
        js.transition(job_id, JobStatus.CANCELLED, _now(now_iso))
        js.append_audit(job_id, "phase", "run cancelled (cooperative cancel honored)",
                        ts=_now(now_iso))
        return js.get_job(job_id)
    except Exception as e:  # noqa: BLE001 — fail closed; record + re-raise
        try:
            js.transition(job_id, JobStatus.FAILED, _now(now_iso), error=str(e))
            js.append_audit(job_id, "error", f"run failed: {e}", ts=_now(now_iso))
        except Exception:  # pragma: no cover - never mask the original error
            pass
        raise
