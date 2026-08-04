"""
spec<->models adapter (Wave A1.4) — spec-canonical, routing-aware, view-pluggable.

The PRD's locked decision #3: the ``underwrite-spec.json`` is the MASTER record (it carries every
value's citation + the QA safety gates); the screen-facing model is a derived VIEW. This module is
the bidirectional translator.

DESIGN — losslessness by construction:
  - ``spec_to_view(spec)`` splits the spec into (a) a flat ``fields`` dict the screen edits, mapped
    from canonical ``cells[]`` addresses, and (b) a ``remainder`` = the ENTIRE spec minus the cells
    the view owns. The remainder is carried verbatim.
  - ``view_to_spec(view)`` reassembles: it writes the view fields back to their canonical cell
    addresses (preserving each cell's original ``source``/``type``/``phase`` metadata) and merges
    them into the untouched remainder.

Because the remainder is carried verbatim and the owned cells are written back to the same
addresses with their original metadata, ``spec -> view -> spec`` is byte-identical on every
pass-through field (qa, comps, forensic, narrative, memo_vars, headline_metrics, all non-view
cells, full meta). ``view -> spec -> view`` reconstructs the view subset exactly.

VIEW-PLUGGABLE (the Wave-B seam): the set of (cell -> field) mappings is a ROUTING-KEYED table
(``_FIELD_MAP``). Wave B adds the ACQ view by extending the ACQ entry — the adapter core does not
change. EFB is wired first here.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class UnknownRoutingError(ValueError):
    """Raised when a spec's meta.routing is neither ACQ nor EFB."""


# ---------------------------------------------------------------------------
# Field map — canonical cell address <-> view field name, keyed by routing.
# Wave B extends the ACQ list; the adapter core is untouched.
# Each entry: (cell_address, view_field_name, value_type)
# ---------------------------------------------------------------------------

_EFB_FIELDS: List[Tuple[str, str, str]] = [
    ("B2",  "property_name",  "text"),
    ("B3",  "address",        "text"),
    ("B4",  "city_state_zip", "text"),
    ("B5",  "year_built",     "year"),
    ("B6",  "total_units",    "integer"),     # note: B6 is a formula in the model; see view_to_spec
    ("B9",  "asking_price",   "currency"),
    ("B10", "purchase_price", "currency"),
    ("B39", "acquisition_fee_pct", "percent"),  # EFB fee cell (B45 on ACQ)
    ("B79", "exit_cap_rate",  "percent"),
    ("B80", "costs_of_sale",  "percent"),
    ("B81", "sale_year",      "integer"),
]

# ACQ shares the same headline cells except the acquisition-fee cell is B45 (BL-03 gate cell).
_ACQ_FIELDS: List[Tuple[str, str, str]] = [
    ("B2",  "property_name",  "text"),
    ("B3",  "address",        "text"),
    ("B4",  "city_state_zip", "text"),
    ("B5",  "year_built",     "year"),
    ("B6",  "total_units",    "integer"),
    ("B9",  "asking_price",   "currency"),
    ("B10", "purchase_price", "currency"),
    ("B45", "acquisition_fee_pct", "percent"),
    ("B79", "exit_cap_rate",  "percent"),
    ("B80", "costs_of_sale",  "percent"),
    ("B81", "sale_year",      "integer"),
    # Wave B extends here: vacancy curve, 3-method exit-cap inputs, market tier/hurdle, etc.
]

_FIELD_MAP: Dict[str, List[Tuple[str, str, str]]] = {
    "EFB": _EFB_FIELDS,
    "ACQ": _ACQ_FIELDS,
}


def _routing(spec: Dict[str, object]) -> str:
    meta = spec.get("meta", {}) if isinstance(spec, dict) else {}
    routing = str(meta.get("routing", "")).upper()
    if routing not in _FIELD_MAP:
        raise UnknownRoutingError(
            f"meta.routing must be ACQ or EFB, got {routing!r}"
        )
    return routing


def _norm_cell(addr: str) -> str:
    """'Pro Forma!B10' -> 'B10'; 'B10' -> 'B10'. The view keys on the bare cell on the default tab."""
    return addr.split("!", 1)[1].strip() if "!" in addr else addr.strip()


# ---------------------------------------------------------------------------
# The view
# ---------------------------------------------------------------------------

@dataclass
class SpecView:
    """The screen-facing view of a deal. ``fields`` are editable; ``remainder`` + ``cell_meta`` +
    ``cell_addr`` carry everything needed to losslessly reconstruct the canonical spec."""
    routing: str
    fields: Dict[str, object]                                   # field_name -> value
    remainder: Dict[str, object] = field(default_factory=dict)  # the spec minus view-owned cells
    cell_addr: Dict[str, str] = field(default_factory=dict)     # field_name -> original cell address
    cell_meta: Dict[str, Dict[str, object]] = field(default_factory=dict)  # field_name -> {source,type,phase,...}


# ---------------------------------------------------------------------------
# spec -> view
# ---------------------------------------------------------------------------

def spec_to_view(spec: Dict[str, object]) -> SpecView:
    routing = _routing(spec)
    spec = copy.deepcopy(spec)
    field_for_cell = {cell: (fname, vtype) for (cell, fname, vtype) in _FIELD_MAP[routing]}

    fields: Dict[str, object] = {}
    cell_addr: Dict[str, str] = {}
    cell_meta: Dict[str, Dict[str, object]] = {}

    remainder = copy.deepcopy(spec)
    other_cells: List[Dict[str, object]] = []
    cells_order: List[str] = []  # original cells[] order, by normalized address

    for c in spec.get("cells", []):
        bare = _norm_cell(str(c.get("cell", "")))
        cells_order.append(bare)
        if bare in field_for_cell:
            fname, _vtype = field_for_cell[bare]
            fields[fname] = c.get("value")
            cell_addr[fname] = c.get("cell")  # preserve the ORIGINAL address (may carry a sheet)
            # preserve every non-value attribute so write-back is byte-identical
            cell_meta[fname] = {k: v for k, v in c.items() if k not in ("value",)}
        else:
            other_cells.append(c)

    # remainder holds the spec with ONLY the non-view cells; view-owned cells are reconstructed.
    # Record the original cells[] ordering so view_to_spec can reinterleave byte-identically.
    remainder["cells"] = other_cells
    remainder["_cells_order"] = cells_order

    return SpecView(
        routing=routing,
        fields=fields,
        remainder=remainder,
        cell_addr=cell_addr,
        cell_meta=cell_meta,
    )


# ---------------------------------------------------------------------------
# view -> spec
# ---------------------------------------------------------------------------

def view_to_spec(view: SpecView) -> Dict[str, object]:
    spec = copy.deepcopy(view.remainder)
    other_cells = list(spec.get("cells", []))
    cells_order = spec.pop("_cells_order", None)  # internal bookkeeping — not part of the spec

    # Rebuild the view-owned cells at their original addresses, preserving original metadata and
    # the field-map declared order (deterministic output).
    rebuilt: List[Dict[str, object]] = []
    for (cell, fname, vtype) in _FIELD_MAP[view.routing]:
        if fname not in view.fields:
            continue
        meta = dict(view.cell_meta.get(fname, {}))
        addr = view.cell_addr.get(fname, cell)
        entry: Dict[str, object] = {"cell": addr, "value": view.fields[fname]}
        # restore source/type/phase/input_only etc. in their original key order if present
        for k, v in meta.items():
            if k != "cell":
                entry[k] = v
        entry.setdefault("cell", addr)
        rebuilt.append(entry)

    # Restore the original cells[] interleaving so spec -> view -> spec is byte-identical.
    spec["cells"] = _reinterleave(cells_order, rebuilt, other_cells)
    return spec


def _reinterleave(
    cells_order: Optional[List[str]],
    rebuilt: List[Dict[str, object]],
    other_cells: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    """Restore the original cells[] order recorded by spec_to_view. Each position in cells_order is
    either a view-owned cell (rebuilt at its original address) or one of the other cells (consumed
    in their preserved relative order)."""
    rebuilt_by_addr = {_norm_cell(str(c["cell"])): c for c in rebuilt}
    if isinstance(cells_order, list):
        out: List[Dict[str, object]] = []
        others_iter = iter(other_cells)
        for bare in cells_order:
            if bare in rebuilt_by_addr:
                out.append(rebuilt_by_addr[bare])
            else:
                out.append(next(others_iter))
        return out
    # Fallback (no recorded order, e.g. a view built by hand): owned cells first, then the rest.
    return rebuilt + other_cells
