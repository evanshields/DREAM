"""
backend/jobs/wave0.py — Wave 0 routing + BL-17 critical-input capture (NO LLM).

Wave 0 runs BEFORE the five analytical slices. Two jobs, both deterministic (the runner never
dispatches an agent that would discover a gap mid-run — the Envy failure):

  1. BL-17 critical inputs — purchase_price / hold_years / exit_cap (state_ledger.CriticalInputs).
     Any missing => the run STOPS at AWAITING_INPUT and emits one BLOCKING OpenQuestion per missing
     input. These three diverged silently on Envy (7 vs 10 hold, 6.5 vs 6.25 exit); capturing them
     up front and surviving restarts is the whole point of the durable ledger.

  2. Routing — FORCED to ACQ in v1 (EFB is a later unlock), but the BASIS is recorded so a future
     EFB enablement is auditable. If the intake explicitly signals an EFB/ambiguous-future deal,
     Wave 0 does NOT guess: it stops at AWAITING_INPUT with a blocking routing OpenQuestion.

Return contract (a plain dict, JSON-native):
  ready    -> {"ready": True,  "critical_inputs": {...}, "routing": "ACQ", "routing_basis": "..."}
  not ready-> {"ready": False, "awaiting": [OpenQuestion, ...], "routing": "ACQ"|None,
               "critical_inputs": {...}}  (the OpenQuestions are BLOCKING)

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

# Human-readable prompts per missing BL-17 input (CP-1 / AWAITING_INPUT surface).
_CRITICAL_PROMPTS = {
    "purchase_price": "What is the purchase price (B10)? Required before any spread begins (BL-17).",
    "hold_years": "What is the hold period in years (e.g. 7 or 10)? Required before any spread (BL-17).",
    "exit_cap": "What is the exit cap rate (e.g. 0.0625)? Required before any spread (BL-17).",
}

# v1 routing is forced ACQ; these tokens in the intake force an explicit human routing decision.
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


def _detect_routing(intake_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Decide routing. v1 forces ACQ but records the basis. An explicit EFB/ambiguous signal in the
    intake (without an explicit routing='ACQ' confirmation) forces a human routing decision."""
    explicit = str(intake_summary.get("routing", "")).strip().upper()
    if explicit == "ACQ":
        return {"routing": "ACQ", "basis": "explicit:ACQ", "ambiguous": False}
    if explicit == "EFB":
        # EFB is a later unlock; do not auto-route. Stop and ask.
        return {"routing": None, "basis": "explicit:EFB (unsupported in v1)", "ambiguous": True}

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

    # default v1: ACQ
    return {"routing": "ACQ", "basis": "default:ACQ (v1 forces ACQ; EFB is a later unlock)",
            "ambiguous": False}


def run_wave0(job: Any, intake_summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute Wave 0 for a job. `job` is a JobRecord (used for its job_id when building question
    ids); `intake_summary` is the deal package's already-parsed summary (NOT raw docs — no LLM).

    Returns a JSON-native dict (see module docstring). The runner uses `ready` to choose between
    transition->ANALYZING (ready) and transition->AWAITING_INPUT (blocking questions present)."""
    intake_summary = dict(intake_summary or {})
    job_id = getattr(job, "job_id", "job")

    ci = _extract_critical_inputs(intake_summary)
    routing = _detect_routing(intake_summary)

    awaiting: List[OpenQuestion] = []

    # --- routing ambiguity is a BLOCKING question (never guess EFB) ---
    if routing["ambiguous"] or routing["routing"] is None:
        awaiting.append(OpenQuestion(
            id=f"oq-{job_id}-routing",
            field="meta.routing",
            question=(
                "Confirm deal routing. Wave C-v1 underwrites ACQ only; an EFB/ambiguous signal was "
                f"detected ({routing['basis']}). Choose ACQ to proceed, or hold for the EFB unlock."
            ),
            current_value=None,
            source=SOURCE_CITED,
            options=["ACQ", "EFB"],
            blocking=True,
        ))

    # --- BL-17 critical inputs: one blocking question per missing field ---
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
            "routing": routing["routing"],          # may be None when EFB/ambiguous
            "routing_basis": routing["basis"],
            "critical_inputs": critical_inputs,
        }

    return {
        "ready": True,
        "critical_inputs": critical_inputs,
        "routing": routing["routing"],              # "ACQ"
        "routing_basis": routing["basis"],
    }
