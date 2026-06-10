"""
backend/jobs/analysts.py — the five SEQUENTIAL Wave-1 analytical slices (chat-bot fast path).

The fast path's Wave 1 is five analytical agents (agent-contracts.md): t12 / rentroll / assumptions
/ comps / marketdata. Each is a pure function: deal package -> a JSON slice that the synthesis
runner merges into one underwrite-spec. This module gives the runner three things:

  (a) AnalystSlice — the PROTOCOL the runner depends on (so Stub and Kimi are interchangeable).
  (b) StubAnalysts — FIXED Esplanade-equivalent slices, NO LLM. Drives run_synthesis to the
      validated Esplanade ground truth (IRR ~0.2251, EM ~2.72) so the whole job pipeline is
      testable with zero network. The deal/engine inputs carry CITED sources (determinism rule);
      a couple of judgment cells are tagged 'llm-inferred' so the OpenQuestion ledger is exercised.
  (c) KimiAnalysts — the REAL implementation. Each slice builds a focused prompt from that slice's
      hard rules in agent-contracts.md, calls the Kimi client (LAZY import of backend/agent/
      kimi_client, model moonshot-v1-128k for long deal docs), parses the JSON reply, and VALIDATES
      it against underwrite-spec.schema.json (a self-contained validator — no jsonschema dependency)
      before returning. Deterministic values (engine inputs, counts) MUST carry a 'source' citation;
      judgment values are tagged 'llm-inferred'. Importing KimiAnalysts needs NO API key (the client
      is constructed lazily, only when a slice actually runs).

Each slice returns a plain dict whose keys are a subset of AnalyticalSlices' fields. The runner
deep-merges the five dicts (helper `merge_slices`) and hands the result to run_synthesis.
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from jobs.contracts import OpenQuestion, SOURCE_LLM_INFERRED, SOURCE_CITED  # noqa: E402

# The five slice phases, in sequential order (mirrors contracts.WAVE1_SLICE_PHASES).
SLICE_NAMES: tuple = ("t12", "rentroll", "assumptions", "comps", "marketdata")

# Long-deal-doc model (the .env.example moonshot-v1-32k default is STALE — see task brief).
KIMI_MODEL = os.environ.get("KIMI_MODEL_FASTPATH", "moonshot-v1-128k")

_SCHEMA_PATH = os.path.join(_ENGINE_FASTPATH := os.path.join(
    os.path.dirname(_BACKEND), "underwriting-engine", "fastpath"), "underwrite-spec.schema.json")


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class AnalystSlice(Protocol):
    """One Wave-1 analytical slice. `name` is one of SLICE_NAMES; `run` returns a dict that is a
    subset of AnalyticalSlices' fields (merged by the runner)."""

    name: str

    def run(self, deal_docs: Dict[str, Any], intake_summary: Dict[str, Any],
            critical_inputs: Dict[str, Any]) -> Dict[str, Any]: ...


class AnalystSet(Protocol):
    """The ordered set of five slices the runner iterates. `slices()` yields them in phase order."""

    def slices(self) -> List[AnalystSlice]: ...


# ---------------------------------------------------------------------------
# Merge helper
# ---------------------------------------------------------------------------

def merge_slices(slice_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deep-merge the five slice dicts into one merged dict for AnalyticalSlices.from_dict.
    List-valued cell fields concatenate; dict-valued fields update; scalars last-write-wins."""
    merged: Dict[str, Any] = {}
    list_keys = {"t12_cells", "rentroll_cells", "assumptions_cells", "unit_mix",
                 "classified_units", "user_exclusions"}
    for out in slice_outputs:
        for k, v in (out or {}).items():
            if k in list_keys and isinstance(v, list):
                merged.setdefault(k, [])
                merged[k].extend(v)
            elif isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k].update(v)
            else:
                merged[k] = v
    return merged


def make_open_questions(merged: Dict[str, Any]) -> List[OpenQuestion]:
    """Build OpenQuestions for every llm-inferred slice cell (mirrors synthesis.build_open_questions
    but operates on the pre-synthesis merged dict, for the runner's convenience)."""
    questions: List[OpenQuestion] = []
    for key in ("t12_cells", "rentroll_cells", "assumptions_cells"):
        for cell in merged.get(key, []) or []:
            if str(cell.get("source", "")).strip().lower() != SOURCE_LLM_INFERRED:
                continue
            addr = str(cell.get("cell", ""))
            questions.append(OpenQuestion(
                id=f"oq-{addr or len(questions)}",
                field=addr,
                question=(f"Confirm {addr}: value {cell.get('value')!r} was LLM-inferred "
                          f"(no citation). Provide the source or correct it."),
                current_value=cell.get("value"),
                source=SOURCE_LLM_INFERRED,
                blocking=False,
            ))
    return questions


# ---------------------------------------------------------------------------
# Esplanade ground-truth fixtures (the StubAnalysts payload) — CITED deal data.
# Values match backend/tests/test_engine_boundary_esplanade.py so run_synthesis reproduces
# IRR ~0.2251 / EM ~2.72 with NO LLM.
# ---------------------------------------------------------------------------

_ESPLANADE_NOI = [2387932, 2563041, 2742167, 2883487, 2983197,
                  3134540, 3241781, 3352240, 3466013, 3583198]

_ESPLANADE_ENGINE_INPUTS = {
    "bridge_loan": 23800000.0, "bridge_rate": 0.08, "bridge_io_years": 2,
    "refi_loan": 31944864.0, "refi_rate": 0.06, "refi_io_years": 3,
    "refi_amort_years": 30, "refi_year": 2,
    "total_equity": 13145673.0, "noi_series": [float(v) for v in _ESPLANADE_NOI],
    "exit_cap": 0.06, "sale_year": 7, "costs_of_sale": 0.02,
    "servicing_spread": 0.0116, "refi_cost_pct": 0.02, "exit_on_forward_noi": True,
}


class StubAnalysts:
    """FIXED Esplanade-equivalent slices. No LLM, no network. Used by the runner's default path and
    every test that needs an end-to-end run without a live model."""

    def __init__(self, *, units: int = 240):
        self._units = units

    # -- the five slices --
    def slice_t12(self) -> Dict[str, Any]:
        return {
            "forensic": {
                "lease_up_flag": False,
                "takeaways": ["Stabilized in-place operations; T-12/T-6/T-3 aligned within 2%."],
            },
            "t12_cells": [
                {"cell": "S40", "value": 0, "source": "T-12 actuals", "phase": 1},
            ],
            "t12_unmapped": 0,
        }

    def slice_rentroll(self) -> Dict[str, Any]:
        classified = [{"bedroom": "2BR", "status": "Occupied"} for _ in range(self._units)]
        return {
            "unit_mix": [{"bedroom": "2BR", "units": self._units}],
            "rentroll_cells": [
                {"cell": "S22", "value": self._units, "source": "Rent roll summary tab", "phase": 2},
            ],
            "classified_units": classified,
            "summary_tab_count": self._units,
            "second_source_count": self._units,
            "rr_vs_t12_gpr_gap_pct": 1.2,
        }

    def slice_assumptions(self) -> Dict[str, Any]:
        return {
            "assumptions_cells": [
                {"cell": "B10", "value": 55000000, "source": "OM p.3 / executed PSA", "phase": 3},
                {"cell": "B45", "value": 0.0075, "source": "Fee band 0.75% ($25-50M)", "phase": 3},
                # one judgment cell -> exercises the OpenQuestion ledger
                {"cell": "B31", "value": 0.03, "source": SOURCE_LLM_INFERRED, "phase": 3},
            ],
            "assumptions_engine_inputs": dict(_ESPLANADE_ENGINE_INPUTS),
            "fee_override": False,
            "template_formulas": {"S40": "=U36", "B66": "=B52/B10"},
        }

    def slice_comps(self) -> Dict[str, Any]:
        return {
            "comps": {
                "sales": [{"name": "Comp A", "price_per_unit": 229000, "sold": True}],
                "rent": [{"bedroom": "2BR", "p50": 1850, "p75": 1980}],
                "pipeline": [],
                "median_ppu": 229000,
            }
        }

    def slice_marketdata(self) -> Dict[str, Any]:
        return {
            "marketdata": {
                "fmr": {"2BR": 1820, "citation": "FMR Orange FL 2026"},
                "opex_triangulate": [],
            },
            "freshness": {"as_of": "2026-06-01", "source": "Mission Driven API"},
        }

    def run_all(self, deal_docs: Optional[Dict[str, Any]] = None,
                intake_summary: Optional[Dict[str, Any]] = None,
                critical_inputs: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Run the five slices in sequence and return their outputs (runner merges them)."""
        return [
            self.slice_t12(),
            self.slice_rentroll(),
            self.slice_assumptions(),
            self.slice_comps(),
            self.slice_marketdata(),
        ]


# ---------------------------------------------------------------------------
# Self-contained spec-slice validator (no jsonschema dependency)
# ---------------------------------------------------------------------------

class SchemaValidationError(ValueError):
    """A KimiAnalysts slice failed validation against underwrite-spec.schema.json (fail closed)."""


def _validate_cells(cells: Any) -> None:
    """Validate a `cells[]` slice fragment against the schema's cell item rules (required keys,
    value type, allowed `type`/`source`). Lightweight; covers what the slices actually emit."""
    if not isinstance(cells, list):
        raise SchemaValidationError("cells must be a list")
    allowed_types = {"currency", "percent", "decimal", "integer", "text", "year"}
    for c in cells:
        if not isinstance(c, dict):
            raise SchemaValidationError("each cell must be an object")
        for req in ("cell", "value", "source"):
            if req not in c:
                raise SchemaValidationError(f"cell missing required key {req!r}: {c!r}")
        if not isinstance(c["cell"], str) or not c["cell"]:
            raise SchemaValidationError(f"cell.cell must be a non-empty string: {c!r}")
        if not isinstance(c["value"], (int, float, str, bool)) and c["value"] is not None:
            raise SchemaValidationError(f"cell.value bad type: {c!r}")
        if not isinstance(c["source"], str):
            raise SchemaValidationError(f"cell.source must be a string: {c!r}")
        if "type" in c and c["type"] not in allowed_types:
            raise SchemaValidationError(f"cell.type {c['type']!r} not allowed")


def validate_slice(slice_out: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single slice's output. Raises SchemaValidationError on a violation, else returns
    the slice unchanged. Validates the cell-bearing fields against the schema's cell item rules and
    asserts qa scalar shapes the synthesis runner depends on."""
    if not isinstance(slice_out, dict):
        raise SchemaValidationError("slice output must be a dict")
    for key in ("t12_cells", "rentroll_cells", "assumptions_cells"):
        if key in slice_out:
            _validate_cells(slice_out[key])
    if "t12_unmapped" in slice_out and not isinstance(slice_out["t12_unmapped"], int):
        raise SchemaValidationError("qa.t12_unmapped must be an integer")
    if "assumptions_engine_inputs" in slice_out and not isinstance(
            slice_out["assumptions_engine_inputs"], dict):
        raise SchemaValidationError("assumptions_engine_inputs must be a dict (engine input floats)")
    return slice_out


# ---------------------------------------------------------------------------
# KimiAnalysts — the REAL (live-LLM) implementation. Lazy client; importable with no key.
# ---------------------------------------------------------------------------

# Focused per-slice system prompts distilled from agent-contracts.md hard rules. Each instructs the
# model to return JSON ONLY, with deterministic engine inputs/counts carrying a 'source' citation
# and judgment cells tagged 'llm-inferred'.
_SLICE_PROMPTS: Dict[str, str] = {
    "t12": (
        "You are agent-t12. Parse the seller T-12. Build an EXPLICIT row-keyed mapping (never "
        "fuzzy-match); t12_unmapped MUST be 0. RUBS trap: Water/Electric/Trash/Pest reimbursements "
        "are Utility Reimbursements, NOT Other Income. Deliver the forensic block (T12/T6/T3 NOI, "
        "vacancy trend, concessions, loss-to-lease, bad debt, anomalies, lease_up_flag, takeaways). "
        "Return JSON ONLY: {\"forensic\":{...}, \"t12_cells\":[{\"cell\",\"value\",\"source\","
        "\"phase\":1}], \"t12_unmapped\":0}. Every cell carries a 'source' citation."
    ),
    "rentroll": (
        "You are agent-rentroll. Unit-detail rows only. Classify each unit by status AND use-type. "
        "Use the unit-count reconciler inputs: emit classified_units, summary_tab_count, and a 2nd "
        "source count. Reconcile RR-implied GPR vs T-12 within 5%. Return JSON ONLY: {\"unit_mix\":"
        "[...], \"rentroll_cells\":[{\"cell\",\"value\",\"source\",\"phase\":2}], "
        "\"classified_units\":[...], \"summary_tab_count\":int, \"second_source_count\":int, "
        "\"rr_vs_t12_gpr_gap_pct\":number}. Counts carry a 'source' citation."
    ),
    "assumptions": (
        "You are agent-assumptions. Read pricing/closing/fees/debt/sale INPUT cells only (NEVER "
        "formula cells). ACQ acquisition fee B45 must be within 0.5-1.0%; never the 0.05 sentinel. "
        "Build the engine input floats (bridge/refi/equity/exit_cap/sale_year/noi_series) as "
        "assumptions_engine_inputs. Return JSON ONLY: {\"assumptions_cells\":[{\"cell\",\"value\","
        "\"source\",\"phase\":3}], \"assumptions_engine_inputs\":{...}, \"fee_override\":false, "
        "\"template_formulas\":{...}}. Deal/engine values carry a 'source'; pure judgment values "
        "use \"source\":\"llm-inferred\"."
    ),
    "comps": (
        "You are agent-comps. Sales: Sold + valid price/units/SF, recency-weighted ranked "
        "candidates. Rent comps by bedroom with P50/P75/Max (skip the subject). Construction "
        "pipeline state-filtered (no out-of-state carryover). Return JSON ONLY: {\"comps\":"
        "{\"sales\":[...], \"rent\":[...], \"pipeline\":[...], \"median_ppu\":number}}."
    ),
    "marketdata": (
        "You are agent-marketdata. Pull FMR/SAFMR/LIHTC/OpEx from the Mission Driven API; prefer "
        "SAFMR (ZIP) in SAFMR metros. OpEx program=conventional for ACQ. Every value carries its "
        "API citation as 'source'. Stamp freshness. Return JSON ONLY: {\"marketdata\":{...}, "
        "\"freshness\":{...}}."
    ),
}


class KimiAnalysts:
    """Live-LLM analytical slices via the Kimi (Moonshot) client. The client is built LAZILY on the
    first slice run, so importing/constructing KimiAnalysts needs NO API key — only running a slice
    against a deal does. Each slice's output is schema-validated before it is returned (fail closed)."""

    def __init__(self, client: Any = None, model: str = KIMI_MODEL, max_tokens: int = 4000):
        self._client = client
        self._model = model
        self._max_tokens = max_tokens

    # -- lazy client --
    def _get_client(self) -> Any:
        if self._client is None:
            # Lazy import so module import never requires the OpenAI SDK / API key.
            from agent.kimi_client import KimiClient  # noqa: WPS433 (intentional lazy import)
            self._client = KimiClient()
            # Pin the long-deal-doc model unless the client was pre-configured otherwise.
            try:
                self._client.model = self._model
            except Exception:  # pragma: no cover
                pass
        return self._client

    @staticmethod
    def _parse_json(reply: str) -> Dict[str, Any]:
        """Extract a JSON object from the model reply (tolerates ```json fences / leading prose)."""
        reply = (reply or "").strip()
        if reply.startswith("```"):
            reply = reply.split("```", 2)[1] if "```" in reply[3:] else reply[3:]
            if reply.lstrip().lower().startswith("json"):
                reply = reply.lstrip()[4:]
        start, end = reply.find("{"), reply.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise SchemaValidationError(f"no JSON object in model reply: {reply[:200]!r}")
        return json.loads(reply[start:end + 1])

    def _run_slice(self, name: str, deal_docs: Dict[str, Any],
                   intake_summary: Dict[str, Any],
                   critical_inputs: Dict[str, Any]) -> Dict[str, Any]:
        system = _SLICE_PROMPTS[name]
        user = (
            "Deal package summary:\n"
            f"{json.dumps(intake_summary, ensure_ascii=False)[:6000]}\n\n"
            "Critical inputs (BL-17, authoritative):\n"
            f"{json.dumps(critical_inputs, ensure_ascii=False)}\n\n"
            "Deal documents (excerpted):\n"
            f"{json.dumps(deal_docs, ensure_ascii=False)[:60000]}\n\n"
            "Return the JSON slice now."
        )
        client = self._get_client()
        reply = client.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=self._max_tokens,
        )
        return validate_slice(self._parse_json(reply))

    # the five slices (each schema-validated)
    def slice_t12(self, dd, isum, ci) -> Dict[str, Any]:
        return self._run_slice("t12", dd, isum, ci)

    def slice_rentroll(self, dd, isum, ci) -> Dict[str, Any]:
        return self._run_slice("rentroll", dd, isum, ci)

    def slice_assumptions(self, dd, isum, ci) -> Dict[str, Any]:
        return self._run_slice("assumptions", dd, isum, ci)

    def slice_comps(self, dd, isum, ci) -> Dict[str, Any]:
        return self._run_slice("comps", dd, isum, ci)

    def slice_marketdata(self, dd, isum, ci) -> Dict[str, Any]:
        return self._run_slice("marketdata", dd, isum, ci)

    def run_all(self, deal_docs: Optional[Dict[str, Any]] = None,
                intake_summary: Optional[Dict[str, Any]] = None,
                critical_inputs: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """The five slices are independent (each reads the same inputs; only merge_slices joins
        them), so run them CONCURRENTLY — five sequential Moonshot calls were the dominant
        latency on the live submit path (~5x wall clock). Order of results is preserved."""
        dd = dict(deal_docs or {})
        isum = dict(intake_summary or {})
        ci = dict(critical_inputs or {})
        self._get_client()  # build the lazy client ONCE before fan-out (init is not thread-safe)
        slices = (self.slice_t12, self.slice_rentroll, self.slice_assumptions,
                  self.slice_comps, self.slice_marketdata)
        with ThreadPoolExecutor(max_workers=len(slices)) as pool:
            futures = [pool.submit(s, dd, isum, ci) for s in slices]
            return [fut.result() for fut in futures]
