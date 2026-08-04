"""
backend/routers/memo.py — deal-memo generation (PRD C.4: "a completed run yields a tweakable
deal instance + memo").

ONE endpoint:

  POST /api/deals/{deal_id}/memo   generate the 1-page institutional memo for a COMPUTED deal,
                                   persist it at spec.narrative.memo (optimistic version bump,
                                   status unchanged), and return {memo_markdown, generated_at}.
                                   404 unknown deal; 409 when the deal has no computed spec
                                   (draft / empty headline_metrics) or on a concurrent write.

This lives in its OWN router — NOT routers/deals.py — because deals must stay LLM-free in its
import graph (the pipeline list/detail views never pull in Kimi). This module imports the
Kimi-backed MemoGenerator (agent/memo_generator.py) and is mounted auth-gated in main.py exactly
like the other Wave A-D routers (the router file itself stays dependency-free so the standalone
test harness needs no token).

DETERMINISM RULE (locked, PRD): the memo is LLM-written PROSE over deterministic inputs. It reads
headline_metrics + qa.* off the persisted spec; it NEVER writes them. The only spec mutation here
is spec.narrative.memo. Every generated memo is prefixed with an explicit GENERATED-DRAFT marker
so the markdown itself carries its provenance.

Adapter note: MemoGenerator.generate(inputs, model_results) predates the deal-spec era (it was
built for the legacy /api/agent/memo flat-inputs route). Rather than rewrite it, _memo_payload()
is a thin adapter that projects the canonical spec into the (inputs, model_results) pair it
expects — routing-aware: ACQ deals map the levered-returns headline (irr -> levered_irr, ...),
EFB deals map the bond-sizing headline (bond_amount / year1_dscr -> yr1_dscr / tax savings).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from fastapi import APIRouter, HTTPException

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store import (  # noqa: E402
    get_deal_store, DealStore, DealRecord, DealNotFound, VersionConflict,
)
from agent import MemoGenerator  # noqa: E402  (the ONE LLM import — kept out of routers/deals.py)

router = APIRouter(prefix="/api/deals", tags=["memo"])

# The marker every generated memo carries in its markdown header (PRD: the memo is a DRAFT the
# human reviews at CP-1 — it must never present as authored analysis).
GENERATED_DRAFT_MARKER = (
    "> **GENERATED DRAFT — AI-written memo.** The narrative below was LLM-generated from the "
    "deal's deterministic engine outputs (headline metrics + QA gates). Numbers are only "
    "authoritative in the deal spec itself; review before distribution."
)

# Singleton generator (lazy: constructing MemoGenerator builds the Kimi client, which needs a
# key — tests monkeypatch get_memo_generator and never touch it).
_memo_generator: MemoGenerator | None = None


def get_memo_generator() -> MemoGenerator:
    global _memo_generator
    if _memo_generator is None:
        _memo_generator = MemoGenerator()
    return _memo_generator


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# The spec -> MemoGenerator adapter
# ---------------------------------------------------------------------------

# How many raw spec cells ride into the "key assumptions" block. The memo needs the load-bearing
# assumptions, not the whole workbook — and the prompt already carries the full headline + gates.
_MAX_ASSUMPTION_CELLS = 40


def _memo_payload(rec: DealRecord) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Project the canonical spec into the (inputs, model_results) pair MemoGenerator expects.

    inputs  — deal identity + key assumptions: meta (name/location/routing/tier), the BL-17 /
              EFB critical inputs, and a trimmed {cell: value (source)} assumptions map.
    model_results — the DETERMINISTIC outputs, routing-aware:
              ACQ: irr -> levered_irr (+ equity_multiple, CoC, exit value, equity);
              EFB: bond_amount / year1_dscr -> yr1_dscr / year1_noi / tax savings.
              qa.* gate verdicts ride along under 'qa_gates' so the memo's RAG statuses and
              risk factors reflect the gates that actually fired.
    """
    spec = rec.spec if isinstance(rec.spec, dict) else {}
    meta = spec.get("meta") or {}
    hm = spec.get("headline_metrics") or {}
    qa = spec.get("qa") or {}
    routing = (rec.routing or str(meta.get("routing", ""))).upper() or "ACQ"
    critical = meta.get("critical_inputs") or {}

    # ---- inputs: deal identity + key assumptions ------------------------------------------
    inputs: Dict[str, Any] = {
        "property_name": rec.deal_name or meta.get("deal_name") or rec.slug or rec.deal_id,
        "deal_id": rec.deal_id,
        "slug": rec.slug,
        "routing": routing,
        "mode": rec.mode or meta.get("mode", ""),
        "status": rec.status,
    }
    # Location / identity color when the slices captured it (never required).
    for key in ("city", "location", "market", "market_tier", "year_built", "vintage",
                "unit_count", "units", "deal_identity", "template"):
        if meta.get(key) is not None:
            inputs[key] = meta[key]
    # Critical inputs are the human-authoritative deal terms (BL-17 trio for ACQ;
    # stabilized_noi + bond scalars for EFB) — fold every non-None one in.
    for key, val in critical.items():
        if val is not None:
            inputs.setdefault(key, val)
    # Key assumptions: a trimmed {cell: "value (source)"} view of the spec's input cells,
    # provenance included so the memo can distinguish cited values from judgment calls.
    cells = spec.get("cells") or []
    assumptions: Dict[str, Any] = {}
    for cell in cells[:_MAX_ASSUMPTION_CELLS]:
        if not isinstance(cell, dict):
            continue
        addr = str(cell.get("cell", "")).strip()
        if addr:
            src = cell.get("source")
            assumptions[addr] = (f"{cell.get('value')} ({src})" if src else cell.get("value"))
    if assumptions:
        inputs["key_assumptions"] = assumptions

    # ---- model_results: the deterministic engine headline, routing-aware ------------------
    model_results: Dict[str, Any] = dict(hm)  # full headline block rides along verbatim
    if routing == "EFB":
        # Bond-sizing shape (engine_boundary.run_efb_underwrite): map to the memo template's names.
        if hm.get("year1_dscr") is not None:
            model_results["yr1_dscr"] = hm["year1_dscr"]
        if critical.get("annual_property_tax_exempted") is not None:
            model_results.setdefault("annual_tax_savings",
                                     critical["annual_property_tax_exempted"])
    else:
        # ACQ levered-returns shape (engine_boundary.run_acq_underwrite).
        if hm.get("irr") is not None:
            model_results["levered_irr"] = hm["irr"]
    # Gate verdicts (deterministic, from qa_gates.run_gates) inform RAG statuses + risk factors.
    if qa:
        model_results["qa_gates"] = qa

    return inputs, model_results


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/{deal_id}/memo")
def generate_deal_memo(deal_id: str) -> Dict[str, Any]:
    """Generate (or REgenerate — overwrites) the deal memo from the persisted spec.

    404 unknown deal. 409 when the deal has no computed spec to write a memo about (a draft:
    empty/missing headline_metrics — the memo is prose OVER engine outputs, so there must be
    engine outputs) or when a concurrent writer moved the deal version under us (re-read, retry).
    """
    ds: DealStore = get_deal_store()
    try:
        rec = ds.get(deal_id)
    except DealNotFound:
        raise HTTPException(status_code=404, detail=f"deal '{deal_id}' not found")

    spec = rec.spec if isinstance(rec.spec, dict) else {}
    hm = spec.get("headline_metrics")
    if not isinstance(hm, dict) or not hm:
        raise HTTPException(
            status_code=409,
            detail=(f"deal '{deal_id}' has no computed spec (status '{rec.status}', "
                    "no headline_metrics) — run the underwrite before generating a memo"),
        )

    inputs, model_results = _memo_payload(rec)
    generated_at = _now_iso()
    try:
        body = get_memo_generator().generate(inputs, model_results)
    except Exception as e:  # noqa: BLE001 — upstream LLM failure is a gateway error, not a 500
        raise HTTPException(status_code=502, detail=f"memo generation failed: {e}")

    memo_markdown = f"{GENERATED_DRAFT_MARKER}\n>\n> _Generated {generated_at}._\n\n{body}"

    # Persist at spec.narrative.memo — the ONLY mutation (headline_metrics/qa are never written
    # here; determinism rule). Optimistic version from the record we read; status unchanged.
    new_spec = dict(spec)
    narrative = dict(new_spec.get("narrative") or {})
    narrative["memo"] = {"markdown": memo_markdown, "generated_at": generated_at}
    new_spec["narrative"] = narrative
    try:
        ds.put(deal_id, new_spec, expected_version=rec.version, now_iso=generated_at)
    except VersionConflict as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {"memo_markdown": memo_markdown, "generated_at": generated_at}
