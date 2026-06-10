"""
backend/jobs/synthesis.py — Wave C-v1 SEQUENTIAL Wave-2 synthesis runner (ACQ-only, HITL).

This is the heart of the chat-bot fast path: it takes the merged output of the five Wave-1
analytical slices (a plain dict — STUBBED/mockable in this pass, no live Kimi), assembles the
canonical underwrite-spec, drives the VALIDATED engine through `backend.engine_boundary`
(NOT reimplementing any math), fires the server-side BL gate harness
(`backend.qa_gates.run_gates`), and builds the OPEN-QUESTIONS ledger (every `llm-inferred`,
non-cited cell becomes an `OpenQuestion` for the CP-1 glance).

The 10 documented Wave-2 steps (agent-contracts.md §"Wave 2 synthesis") are honored as follows
in v1 (see module-level WIRED / DEFERRED notes and integration_notes for the honest map):

  WIRED (deterministic, engine-backed):
    * Step 4  — lease-up ramp NOI is consumed as the `noi_series` the projector runs on
                (here the slice supplies the ramped series; LeaseUpRamp itself is upstream/deferred).
    * Step 6  — sizing + interest-reserve: headline returns via `run_acq_underwrite`; the interest
                reserve is "wired-if-present, else skipped" — a STABILIZED deal (no shortfall years,
                e.g. Esplanade) gets `reserve_sized=0` and an UNCHANGED DSCR series (ground truth
                protected). The reserve resizing of equity is NOT performed in v1 (deferred).
    * Step 9  — headline_metrics written from the engine (the CP-2 oracle): IRR/EM/CoC, NOI/DSCR.
    * Gates   — fee_bounds (BL-03), unit_count (BL-01/09), deal_identity (BL-02), formula_audit
                (BL-07) all fire via `qa_gates.run_gates` on the assembled spec, server-side.

  WIRED-IF-PRESENT (pass-through, no recompute in v1):
    * Steps 1/2/3/5/7/7b/8/10 — when the slices already carry tier_allocation / rubs_sign /
      opex flags / property_tax_range / exit_cap_gate / ltv_gate / formula strings / reprice,
      they are carried verbatim onto the spec (headline_metrics.* or qa.*). The runner does NOT
      re-run FourTierOptimizer / ExitCapTriangulator / RepriceSolver in v1 — those Decimal calls
      stay upstream (the analytical slices / a later wave) so synthesis.py holds NO Decimal.

  DEFERRED (NOT in v1, documented honestly):
    * NOAH/EFB route signal build (the engine never auto-builds EFB; ACQ-only here).
    * Reprice solve, interest-reserve equity resizing, exit-cap/LTV gate RECOMPUTE from raw inputs.

DETERMINISM RULE (locked): headline_metrics + qa.* NEVER come from an LLM. They come from the
engine (`run_acq_underwrite`) and the gate harness. Any slice value tagged `source == 'llm-inferred'`
is treated as judgment, surfaced as an OpenQuestion, and NEVER written into headline_metrics/qa.

JSON-NATIVE: floats not Decimal at this layer (Decimal stays inside engine_boundary). The spec this
module emits is a plain dict matching underwrite-spec.schema.json (meta/qa/cells/headline_metrics/
comps/forensic/narrative).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# --- backend modules (conftest / app put backend/ on sys.path) ---------------
_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from engine_boundary import ACQDealInputs, run_acq_underwrite  # noqa: E402
from qa_gates import run_gates, GateSummary                    # noqa: E402

from jobs.contracts import (  # noqa: E402
    OpenQuestion,
    SOURCE_LLM_INFERRED,
    SOURCE_CITED,
)

# state_ledger.CriticalInputs is the BL-17 critical-input carrier (purchase_price/hold_years/
# exit_cap). We accept either that dataclass OR a plain dict/object with those attributes.
_ENGINE_FASTPATH = os.path.join(
    os.path.dirname(_BACKEND), "underwriting-engine", "fastpath",
)
if _ENGINE_FASTPATH not in sys.path:
    sys.path.insert(0, _ENGINE_FASTPATH)
try:  # tolerate absence in minimal test envs
    from state_ledger import CriticalInputs  # noqa: E402
except Exception:  # pragma: no cover - state_ledger is part of the vendored engine
    CriticalInputs = None  # type: ignore


# ---------------------------------------------------------------------------
# AnalyticalSlices — the clean, STUBBABLE interface the 5 Wave-1 slices produce.
# In v1 a stub builds this directly (no live Kimi). Each field mirrors a slice's
# output schema in agent-contracts.md. Everything is JSON-native (floats, dicts).
# ---------------------------------------------------------------------------

@dataclass
class AnalyticalSlices:
    """The merged output of the five sequential Wave-1 analytical slices.

    A SLICE CELL is a dict {cell, value, source[, type, phase, input_only]} exactly matching
    underwrite-spec.schema.json `cells[]`. `source` carries provenance: a CITED string
    ('OM p.3', 'T-12 + 3%', 'FMR Orange FL 2026', ...) is deterministic-safe; the literal
    'llm-inferred' marks a judgment value that becomes an OpenQuestion at CP-1.

    `assumptions_engine_inputs` is the bridge from the assumptions/sizing slices to the engine:
    the float ACQ deal inputs (bridge/refi/equity/exit_cap/sale_year/...). The runner unpacks it
    into ACQDealInputs and runs the validated orchestration. It is provenance-cited deal data,
    NOT an LLM guess — the determinism rule.
    """
    # --- agent-t12 (phase 1) ---
    forensic: Dict[str, Any] = field(default_factory=dict)
    t12_cells: List[Dict[str, Any]] = field(default_factory=list)
    t12_unmapped: int = 0

    # --- agent-rentroll (phase 2) ---
    unit_mix: List[Dict[str, Any]] = field(default_factory=list)
    rentroll_cells: List[Dict[str, Any]] = field(default_factory=list)
    unit_count: Optional[Dict[str, Any]] = None          # qa.unit_count evidence (reconciler output)
    classified_units: Optional[List[Dict[str, Any]]] = None   # raw classification for the gate harness
    summary_tab_count: Optional[int] = None
    second_source_count: Optional[int] = None
    user_exclusions: Optional[List[str]] = None
    rr_vs_t12_gpr_gap_pct: Optional[float] = None

    # --- agent-assumptions (phase 3) ---
    assumptions_cells: List[Dict[str, Any]] = field(default_factory=list)
    assumptions_engine_inputs: Dict[str, Any] = field(default_factory=dict)  # -> ACQDealInputs
    fee_override: Optional[bool] = None
    template_formulas: Optional[Dict[str, str]] = None   # formula-audit (BL-07) evidence
    whisper_flag: Optional[Dict[str, Any]] = None

    # --- agent-comps (phase 4) ---
    comps: Dict[str, Any] = field(default_factory=dict)

    # --- agent-marketdata (phase 5) ---
    marketdata: Dict[str, Any] = field(default_factory=dict)
    freshness: Optional[Dict[str, Any]] = None

    # --- merged spec scaffolding the slices/orchestrator already decided (Wave 0) ---
    meta: Dict[str, Any] = field(default_factory=dict)    # deal_name/slug/routing/template/deal_identity/...
    narrative: Dict[str, Any] = field(default_factory=dict)

    # --- WIRED-IF-PRESENT pass-throughs (computed upstream; carried verbatim, no recompute) ---
    tier_allocation: Optional[Dict[str, Any]] = None      # step 1
    rubs_sign: Optional[Dict[str, Any]] = None            # step 2  -> qa.rubs_sign
    property_tax_range: Optional[Dict[str, Any]] = None   # step 5
    exit_cap_gate: Optional[Dict[str, Any]] = None        # step 7  -> qa.exit_cap_gate
    ltv_gate: Optional[Dict[str, Any]] = None             # step 7b -> qa.ltv_gate
    lease_up_ramp: Optional[Dict[str, Any]] = None        # step 4 color
    reprice: Optional[Dict[str, Any]] = None              # step 10 (advisory)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AnalyticalSlices":
        """Build from a plain merged dict (what a stub or a real merge emits). Unknown keys ignored."""
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in (d or {}).items() if k in known})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_slice_cells(slices: AnalyticalSlices) -> List[Dict[str, Any]]:
    """Concatenate every slice's cells[] in sequential (phase) order: t12 -> rentroll -> assumptions.
    comps/marketdata contribute structured blocks (comps/marketdata/headline), not raw input cells."""
    cells: List[Dict[str, Any]] = []
    cells.extend(slices.t12_cells or [])
    cells.extend(slices.rentroll_cells or [])
    cells.extend(slices.assumptions_cells or [])
    return cells


def _is_llm_inferred(cell: Dict[str, Any]) -> bool:
    """A cell is judgment (not deterministic) iff its source is the llm-inferred sentinel."""
    return str(cell.get("source", "")).strip().lower() == SOURCE_LLM_INFERRED


def _critical_inputs_dict(critical_inputs: Any) -> Dict[str, Any]:
    """Normalize CriticalInputs (dataclass | dict | obj) into a plain dict (JSON-native).
    A dict source keeps ALL its keys (not just the BL-17 three) — answered AWAITING_INPUT
    questions for engine fields (bridge_loan, refi_rate, ...) ride in through here and must
    survive to _coerce_acq_inputs."""
    if critical_inputs is None:
        return {"purchase_price": None, "hold_years": None, "exit_cap": None}
    if isinstance(critical_inputs, dict):
        out = {
            "purchase_price": critical_inputs.get("purchase_price"),
            "hold_years": critical_inputs.get("hold_years"),
            "exit_cap": critical_inputs.get("exit_cap"),
        }
        out.update({k: v for k, v in critical_inputs.items() if v is not None})
        return out
    getter = lambda k: getattr(critical_inputs, k, None)  # noqa: E731
    return {
        "purchase_price": getter("purchase_price"),
        "hold_years": getter("hold_years"),
        "exit_cap": getter("exit_cap"),
    }


class MissingEngineInputsError(ValueError):
    """The merged slices + critical inputs do not form a runnable ACQ engine payload.

    Raised BEFORE ACQDealInputs is constructed so the runner can stop at AWAITING_INPUT with one
    blocking OpenQuestion per missing/invalid field — the BL-17 'ask, don't crash' contract —
    instead of dying with a raw TypeError AFTER the Wave-1 LLM spend."""

    def __init__(self, missing: List[str]):
        super().__init__(
            "ACQ engine inputs missing or invalid: " + ", ".join(missing)
            + " (supply them via the deal package or answer the blocking questions)"
        )
        self.missing = list(missing)


def _coerce_acq_inputs(engine_inputs: Dict[str, Any], ci: Dict[str, Any]) -> ACQDealInputs:
    """Build ACQDealInputs from the slices' engine inputs, with critical inputs as the
    authoritative overlay: BL-17's locked fields PLUS any engine field answered by a human at
    AWAITING_INPUT (human answers always beat slice values). Unknown keys are ignored.

    Validates the payload is RUNNABLE before constructing — missing required debt terms, a
    non-positive exit_cap/total_equity, or an NOI series shorter than the hold raise
    MissingEngineInputsError (question-able) rather than TypeError/DivisionByZero (a crash)."""
    fields = ACQDealInputs.__dataclass_fields__
    payload = {k: v for k, v in (engine_inputs or {}).items()
               if k in fields and v is not None}
    # hold_years is BL-17's name for the engine's sale_year.
    if ci.get("hold_years") is not None:
        payload["sale_year"] = int(ci["hold_years"])
    # Every engine field present in ci (exit_cap from BL-17; bridge/refi/etc from answered
    # questions) overrides the slice value — the human is authoritative.
    for k, v in ci.items():
        if k in fields and v is not None:
            payload[k] = v

    problems: List[str] = []
    required = ("bridge_loan", "bridge_rate", "bridge_io_years",
                "refi_loan", "refi_rate", "refi_io_years")
    problems.extend(k for k in required if payload.get(k) is None)
    if payload.get("exit_cap", 0.06) <= 0:
        problems.append("exit_cap")
    if payload.get("total_equity") is None or payload.get("total_equity", 0.0) <= 0:
        problems.append("total_equity")
    sale_year = int(payload.get("sale_year", 7))
    noi = payload.get("noi_series") or []
    if len(noi) < max(sale_year, 1):
        problems.append("noi_series")
    if problems:
        raise MissingEngineInputsError(problems)
    return ACQDealInputs(**payload)


def build_open_questions(slices: AnalyticalSlices) -> List[OpenQuestion]:
    """The OPEN-QUESTIONS ledger: every spec cell whose source is 'llm-inferred' (not a cited
    doc/API) becomes an OpenQuestion so CP-1 surfaces it non-collapsibly. Deterministic engine
    outputs (headline_metrics, qa.*) never appear here — they are not LLM-inferred."""
    questions: List[OpenQuestion] = []
    for cell in _all_slice_cells(slices):
        if not _is_llm_inferred(cell):
            continue
        addr = str(cell.get("cell", ""))
        questions.append(OpenQuestion(
            id=f"oq-{addr or len(questions)}",
            field=addr,
            question=(f"Confirm {addr}: value {cell.get('value')!r} was LLM-inferred "
                      f"(no document citation). Provide the source or correct it."),
            current_value=cell.get("value"),
            source=SOURCE_LLM_INFERRED,
            blocking=False,   # judgment values surface for a glance; they do not block CP-1 in HITL
        ))
    return questions


# ---------------------------------------------------------------------------
# Spec assembly
# ---------------------------------------------------------------------------

def assemble_spec(
    slices: AnalyticalSlices,
    headline_metrics: Dict[str, Any],
    critical_inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge the slices + engine headline_metrics into one underwrite-spec dict
    (schema: meta/qa/cells/headline_metrics/comps/forensic/narrative).

    The spec is built BEFORE the gate harness runs (run_gates reads it and writes qa.*).
    headline_metrics is the engine output (deterministic); the WIRED-IF-PRESENT pass-through
    blocks (tier_allocation / lease_up_ramp / property_tax_range / reprice) are folded in here.
    """
    meta = dict(slices.meta or {})
    meta.setdefault("routing", "ACQ")
    # BL-17 critical inputs onto meta (mirrors the durable state ledger).
    meta["critical_inputs"] = dict(critical_inputs)

    hm = dict(headline_metrics)  # engine output (floats); the CP-2 oracle
    # Fold WIRED-IF-PRESENT headline color (computed upstream; carried verbatim, never recomputed here).
    for key in ("tier_allocation", "lease_up_ramp", "property_tax_range", "reprice"):
        val = getattr(slices, key, None)
        if val is not None:
            hm[key] = val

    spec: Dict[str, Any] = {
        "meta": meta,
        "qa": {},                                  # run_gates fills this; pass-through qa.* added below
        "cells": _all_slice_cells(slices),
        "headline_metrics": hm,
    }
    if slices.comps:
        spec["comps"] = dict(slices.comps)
    if slices.forensic:
        spec["forensic"] = dict(slices.forensic)
    if slices.narrative:
        spec["narrative"] = dict(slices.narrative)

    # Seed the qa block with provenance the slices already computed (the gate harness will add to /
    # overwrite the gates it owns: fee_bounds, unit_count, deal_identity, formula_audit).
    qa = spec["qa"]
    if slices.t12_unmapped is not None:
        qa["t12_unmapped"] = int(slices.t12_unmapped)
    if slices.rr_vs_t12_gpr_gap_pct is not None:
        qa["rr_vs_t12_gpr_gap_pct"] = float(slices.rr_vs_t12_gpr_gap_pct)
    if slices.whisper_flag is not None:
        qa["whisper_flag"] = dict(slices.whisper_flag)
    # WIRED-IF-PRESENT qa gates (computed upstream; carried verbatim — NOT recomputed in v1).
    if slices.rubs_sign is not None:
        qa["rubs_sign"] = dict(slices.rubs_sign)
    if slices.exit_cap_gate is not None:
        qa["exit_cap_gate"] = dict(slices.exit_cap_gate)
    if slices.ltv_gate is not None:
        qa["ltv_gate"] = dict(slices.ltv_gate)

    return spec


# ---------------------------------------------------------------------------
# The runner
# ---------------------------------------------------------------------------

@dataclass
class SynthesisResult:
    """Structured return of run_synthesis (the tuple's richer form, for the runner/presenter)."""
    spec: Dict[str, Any]
    headline_metrics: Dict[str, Any]
    gate_summary: GateSummary
    open_questions: List[OpenQuestion]


def run_synthesis(
    slices: Any,
    critical_inputs: Any,
    now_iso: str,
    *,
    return_result: bool = False,
):
    """Execute the Wave-2 SEQUENTIAL synthesis (ACQ-only, HITL) and return the spec + headline_metrics.

    Args:
      slices: the merged 5-slice output — an AnalyticalSlices, or a plain dict (a stub's output)
              coerced via AnalyticalSlices.from_dict (no live LLM needed).
      critical_inputs: state_ledger.CriticalInputs | dict | obj with purchase_price/hold_years/exit_cap
              (BL-17). The three locked fields win over slice-supplied values for exit_cap / sale_year.
      now_iso: caller-supplied ISO-8601 timestamp (this module keeps no clock — deterministic, like
              DealStore / the state ledger). Stamped into meta.generated.

    Returns:
      (spec: dict, headline_metrics: dict) by default — the documented signature.
      When return_result=True, a SynthesisResult carrying the GateSummary + open_questions too
      (the runner persists these on the JobRecord; the presenter renders them at CP-1).

    Determinism: headline_metrics comes ONLY from engine_boundary.run_acq_underwrite; qa.* gates
    come ONLY from qa_gates.run_gates. No LLM value enters either. The fail-closed contract: a
    blocking gate sets GateSummary.ok=False with the gate named in .blocking (the runner FAILs /
    surfaces it; it does not silently proceed).
    """
    if not isinstance(slices, AnalyticalSlices):
        slices = AnalyticalSlices.from_dict(dict(slices or {}))

    routing = str((slices.meta or {}).get("routing", "ACQ")).upper()
    if routing != "ACQ":
        # ACQ ROUTE ONLY in v1 (EFB is a later wave). Fail closed rather than guess.
        raise ValueError(
            f"Wave C-v1 synthesis is ACQ-only; got routing {routing!r}. EFB is a later unlock."
        )

    ci = _critical_inputs_dict(critical_inputs)

    # --- Steps 6 + 9: drive the VALIDATED engine for headline returns (deterministic) ----------
    # The lease-up-ramped NOI series (step 4) is supplied by the slices via assumptions_engine_inputs
    # (noi_series); the engine consumes it directly. Interest reserve (step 6) is wired-if-present:
    # a stabilized deal (no shortfall years) yields reserve_sized=0 and an UNCHANGED DSCR series,
    # so the Esplanade ground truth is protected (no equity resize is applied in v1).
    acq_inputs = _coerce_acq_inputs(slices.assumptions_engine_inputs, ci)
    headline_metrics = run_acq_underwrite(acq_inputs)  # floats; the CP-2 oracle

    # --- assemble the canonical spec (before gates; run_gates reads it) ------------------------
    spec = assemble_spec(slices, headline_metrics, ci)
    spec.setdefault("meta", {})["generated"] = now_iso
    if slices.freshness is not None:
        spec["meta"]["freshness"] = dict(slices.freshness)

    # --- Gates: fire the server-side BL harness on the assembled spec (BL-01/02/03/07) ---------
    # This is the load-bearing call: without it the chat-bot path would emit a spec the populator's
    # gates never saw. run_gates writes verdicts into spec.qa.* and returns the non-collapsible
    # summary. Evidence (unit classification, 2nd-source count, formula strings, fee override) comes
    # from the slices; absent evidence => that gate is skipped (not failed), per the harness contract.
    spec, gate_summary = run_gates(
        spec,
        fee_override=slices.fee_override,
        classified_units=slices.classified_units,
        summary_tab_count=slices.summary_tab_count,
        second_source_count=slices.second_source_count,
        user_exclusions=slices.user_exclusions,
        template_formulas=slices.template_formulas,
    )

    # --- OPEN-QUESTIONS ledger: every llm-inferred (non-cited) cell -> an OpenQuestion ----------
    open_questions = build_open_questions(slices)

    if return_result:
        return SynthesisResult(
            spec=spec,
            headline_metrics=headline_metrics,
            gate_summary=gate_summary,
            open_questions=open_questions,
        )
    return spec, headline_metrics
