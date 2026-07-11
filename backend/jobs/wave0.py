"""
backend/jobs/wave0.py — Wave 0 routing + BL-17 critical-input capture (NO LLM).

Wave 0 runs BEFORE the five analytical slices. Two jobs, both deterministic (the runner never
dispatches an agent that would discover a gap mid-run — the Envy failure):

  1. Per-routing critical inputs — one blocking OpenQuestion per missing input:
       ACQ: purchase_price / hold_years / exit_cap (BL-17, state_ledger.CriticalInputs). These
            three diverged silently on Envy (7 vs 10 hold, 6.5 vs 6.25 exit); capturing them up
            front and surviving restarts is the whole point of the durable ledger.
       EFB: stabilized_noi (float, > 0 — the bond-sizing input). hold_years is optional (the
            engine defaults 10); bond_rate / target_dscr / amortization_years /
            annual_property_tax_exempted are optional scalar pass-throughs to the engine.

  2. Routing — default ACQ; explicit routing="EFB" is ACCEPTED (the EFB unlock) with basis
     "explicit:EFB". An AMBIGUOUS EFB signal (tokens in the notes without an explicit routing)
     still stops at AWAITING_INPUT with a blocking routing OpenQuestion — Wave 0 never guesses.
     When routing is ambiguous, critical-input capture is DEFERRED: the resume re-runs Wave 0
     with the answered routing and gates the correct per-route set then (asking the ACQ trio on
     a deal that may be EFB would demand the wrong inputs).

Return contract (a plain dict, JSON-native):
  ready    -> {"ready": True,  "critical_inputs": {...}, "routing": "ACQ"|"EFB",
               "routing_basis": "..."}
  not ready-> {"ready": False, "awaiting": [OpenQuestion, ...], "routing": "ACQ"|"EFB"|None,
               "critical_inputs": {...}}  (the OpenQuestions are BLOCKING)

critical_inputs values are ALWAYS scalars (float/int/None) — the slices' locked contract
(arrays fed to the LLM slices get echoed back as schema-invalid cells; a production bug).

No clock, no DB, no LLM — the runner persists the result and drives the transition.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from jobs.contracts import OpenQuestion, SOURCE_CITED  # noqa: E402

_ENGINE_FASTPATH = os.path.join(
    os.path.dirname(_BACKEND), "underwriting-engine", "fastpath",
)
if _ENGINE_FASTPATH not in sys.path:
    sys.path.insert(0, _ENGINE_FASTPATH)
try:
    from state_ledger import CriticalInputs, REQUIRED_CRITICAL_INPUTS  # noqa: E402
except Exception:  # pragma: no cover
    CriticalInputs = None  # type: ignore
    REQUIRED_CRITICAL_INPUTS = ("purchase_price", "hold_years", "exit_cap")

# Human-readable prompts per missing BL-17 input (CP-1 / AWAITING_INPUT surface). ACQ route.
_CRITICAL_PROMPTS = {
    "purchase_price": "What is the purchase price (B10)? Required before any spread begins (BL-17).",
    "hold_years": "What is the hold period in years (e.g. 7 or 10)? Required before any spread (BL-17).",
    "exit_cap": "What is the exit cap rate (e.g. 0.0625)? Required before any spread (BL-17).",
}

# EFB critical inputs: stabilized_noi is REQUIRED (bond sizing runs on it); everything else is an
# optional scalar pass-through with a validated engine default (engine_boundary.EFBDealInputs).
_EFB_REQUIRED_CRITICAL_INPUTS = ("stabilized_noi",)
_EFB_CRITICAL_PROMPTS = {
    "stabilized_noi": ("What is the stabilized (Year-1) NOI? Required to size the tax-exempt "
                       "bonds to the target DSCR (EFB critical input)."),
}

# Default routing is ACQ; these tokens in the intake (WITHOUT an explicit routing) force an
# explicit human routing decision — Wave 0 never guesses EFB from prose.
_EFB_SIGNAL_TOKENS = (
    "efb", "tax-exempt bond", "tax exempt bond", "4% bond", "lihtc",
    "workforce housing", "hap", "noah",
)


def _extract_critical_inputs(intake_summary: Dict[str, Any]):
    """Pull purchase_price/hold_years/exit_cap from the intake summary. Accepts either a flat
    payload or a nested 'critical_inputs' block. Returns a CriticalInputs (or a duck-typed shim)."""
    ci_src: Dict[str, Any] = {}
    nested = intake_summary.get("critical_inputs")
    if isinstance(nested, dict):
        ci_src.update(nested)
    # flat fallbacks / aliases
    for key, aliases in (
        ("purchase_price", ("purchase_price", "price", "B10")),
        ("hold_years", ("hold_years", "hold_period", "hold")),
        ("exit_cap", ("exit_cap", "exit_cap_rate")),
    ):
        if ci_src.get(key) in (None, ""):
            for a in aliases:
                if intake_summary.get(a) not in (None, ""):
                    ci_src[key] = intake_summary[a]
                    break

    pp = ci_src.get("purchase_price")
    hy = ci_src.get("hold_years")
    ec = ci_src.get("exit_cap")
    try:
        pp = float(pp) if pp not in (None, "") else None
    except (TypeError, ValueError):
        pp = None
    try:
        hy = int(hy) if hy not in (None, "") else None
    except (TypeError, ValueError):
        hy = None
    try:
        ec = float(ec) if ec not in (None, "") else None
    except (TypeError, ValueError):
        ec = None

    if CriticalInputs is not None:
        return CriticalInputs(purchase_price=pp, hold_years=hy, exit_cap=ec)

    class _Shim:  # pragma: no cover - only when the vendored ledger is absent
        def __init__(self, p, h, e):
            self.purchase_price, self.hold_years, self.exit_cap = p, h, e

        def missing(self):
            return [k for k in REQUIRED_CRITICAL_INPUTS if getattr(self, k) in (None, "")]

        @property
        def complete(self):
            return not self.missing()

    return _Shim(pp, hy, ec)


def _extract_efb_critical_inputs(intake_summary: Dict[str, Any]):
    """Pull the EFB critical inputs from the intake summary (nested 'critical_inputs' block or
    flat aliases). stabilized_noi (float, > 0) is REQUIRED; hold_years is optional (the engine
    defaults 10); bond_rate / target_dscr / amortization_years / annual_property_tax_exempted are
    optional pass-throughs included only when present. ALL values are scalars (the slices' locked
    contract). Returns (critical_inputs_dict, missing_field_names)."""
    ci_src: Dict[str, Any] = {}
    nested = intake_summary.get("critical_inputs")
    if isinstance(nested, dict):
        ci_src.update(nested)
    # flat fallbacks / aliases
    for key, aliases in (
        ("stabilized_noi", ("stabilized_noi", "noi", "year1_noi")),
        ("hold_years", ("hold_years", "hold_period", "hold")),
        ("bond_rate", ("bond_rate",)),
        ("target_dscr", ("target_dscr",)),
        ("amortization_years", ("amortization_years",)),
        ("annual_property_tax_exempted", ("annual_property_tax_exempted",)),
    ):
        if ci_src.get(key) in (None, ""):
            for a in aliases:
                if intake_summary.get(a) not in (None, ""):
                    ci_src[key] = intake_summary[a]
                    break

    def _flt(v):
        try:
            return float(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            return None

    def _int(v):
        try:
            return int(v) if v not in (None, "") else None
        except (TypeError, ValueError):
            return None

    noi = _flt(ci_src.get("stabilized_noi"))
    if noi is not None and noi <= 0:
        noi = None  # a non-positive NOI cannot size bonds — treat as missing (ask, don't crash)

    ci: Dict[str, Any] = {"stabilized_noi": noi, "hold_years": _int(ci_src.get("hold_years"))}
    for k in ("bond_rate", "target_dscr", "annual_property_tax_exempted"):
        v = _flt(ci_src.get(k))
        if v is not None:
            ci[k] = v
    v = _int(ci_src.get("amortization_years"))
    if v is not None:
        ci["amortization_years"] = v

    missing = [k for k in _EFB_REQUIRED_CRITICAL_INPUTS if ci.get(k) is None]
    return ci, missing


def _detect_routing(intake_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Decide routing. Explicit routing (ACQ or EFB) is accepted with its basis recorded. An
    ambiguous EFB signal in the prose (without an explicit routing) forces a human routing
    decision — Wave 0 never guesses EFB from tokens."""
    explicit = str(intake_summary.get("routing", "")).strip().upper()
    if explicit == "ACQ":
        return {"routing": "ACQ", "basis": "explicit:ACQ", "ambiguous": False}
    if explicit == "EFB":
        # The EFB unlock: an EXPLICIT routing=EFB is accepted (deterministic, human-supplied).
        return {"routing": "EFB", "basis": "explicit:EFB", "ambiguous": False}

    blob = " ".join(
        str(v) for v in (
            intake_summary.get("deal_name", ""),
            intake_summary.get("notes", ""),
            intake_summary.get("description", ""),
            intake_summary.get("summary", ""),
        )
    ).lower()
    hit = next((t for t in _EFB_SIGNAL_TOKENS if t in blob), None)
    if hit:
        return {"routing": None, "basis": f"ambiguous: EFB signal '{hit}' detected", "ambiguous": True}

    # default: ACQ (EFB routes only on an explicit routing=EFB or an answered routing question)
    return {"routing": "ACQ", "basis": "default:ACQ (no EFB signal; EFB requires explicit routing)",
            "ambiguous": False}


def run_wave0(job: Any, intake_summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute Wave 0 for a job. `job` is a JobRecord (used for its job_id when building question
    ids); `intake_summary` is the deal package's already-parsed summary (NOT raw docs — no LLM).

    Returns a JSON-native dict (see module docstring). The runner uses `ready` to choose between
    transition->ANALYZING (ready) and transition->AWAITING_INPUT (blocking questions present)."""
    intake_summary = dict(intake_summary or {})
    job_id = getattr(job, "job_id", "job")

    routing = _detect_routing(intake_summary)

    awaiting: List[OpenQuestion] = []
    critical_inputs: Dict[str, Any] = {}

    if routing["ambiguous"] or routing["routing"] is None:
        # --- routing ambiguity is a BLOCKING question (never guess EFB) -----------------------
        # Critical-input capture is DEFERRED: the correct per-route set depends on the answer
        # (asking the ACQ trio on a deal that turns out EFB would demand the wrong inputs). The
        # resume re-runs Wave 0 with the answered routing and gates the right set then.
        awaiting.append(OpenQuestion(
            id=f"oq-{job_id}-routing",
            field="meta.routing",
            question=(
                "Confirm deal routing (ACQ levered returns or EFB tax-exempt bond sizing). An "
                f"ambiguous EFB signal was detected ({routing['basis']}); Wave 0 never guesses "
                "routing from prose."
            ),
            current_value=None,
            source=SOURCE_CITED,
            options=["ACQ", "EFB"],
            blocking=True,
        ))

    elif routing["routing"] == "EFB":
        # --- EFB critical inputs: stabilized_noi required; the rest optional pass-throughs ----
        critical_inputs, missing = _extract_efb_critical_inputs(intake_summary)
        for field in missing:
            awaiting.append(OpenQuestion(
                id=f"oq-{job_id}-{field}",
                field=f"meta.critical_inputs.{field}",
                question=_EFB_CRITICAL_PROMPTS.get(field, f"Provide {field} (EFB critical input)."),
                current_value=None,
                source=SOURCE_CITED,
                blocking=True,
            ))

    else:
        # --- ACQ: BL-17 critical inputs, one blocking question per missing field (unchanged) --
        ci = _extract_critical_inputs(intake_summary)
        for field in ci.missing():
            awaiting.append(OpenQuestion(
                id=f"oq-{job_id}-{field}",
                field=f"meta.critical_inputs.{field}",
                question=_CRITICAL_PROMPTS.get(field, f"Provide {field} (BL-17 critical input)."),
                current_value=None,
                source=SOURCE_CITED,
                blocking=True,
            ))
        critical_inputs = {
            "purchase_price": ci.purchase_price,
            "hold_years": ci.hold_years,
            "exit_cap": ci.exit_cap,
        }

    if awaiting:
        return {
            "ready": False,
            "awaiting": awaiting,
            "routing": routing["routing"],          # may be None when ambiguous
            "routing_basis": routing["basis"],
            "critical_inputs": critical_inputs,
        }

    return {
        "ready": True,
        "critical_inputs": critical_inputs,
        "routing": routing["routing"],              # "ACQ" | "EFB"
        "routing_basis": routing["basis"],
    }
