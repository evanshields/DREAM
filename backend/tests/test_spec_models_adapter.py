"""A1.4 acceptance tests — the spec<->models adapter is lossless.

The dangerous failure is a SILENT FIELD DROP. These tests assert spec -> view -> spec is
byte-identical on every pass-through field (qa gates, cells, meta.deal_identity, comps, forensic,
headline_metrics), the reverse view-subset round-trip, and that editing a view field changes only
that cell. Routing-aware (ACQ fee cell B45 vs EFB B39); unknown routing raises.
"""
import copy
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import spec_to_view, view_to_spec, UnknownRoutingError  # noqa: E402


def _acq_spec():
    return {
        "meta": {
            "deal_name": "Esplanade", "slug": "esplanade", "routing": "ACQ",
            "template": "ACQ Mini Model.xlsx", "mode": "HITL",
            "deal_identity": {"match": True, "reasons": [], "foreign_tabs": []},
        },
        "qa": {
            "t12_unmapped": 0,
            "fee_bounds": {"value": 0.0075, "ok": True, "is_sentinel": False},
            "unit_count": {"counted": 240, "blocked": False, "single_source_warning": False},
            "gates": {"phase3": [{"item": "fee in band", "pass": True}]},
        },
        "cells": [
            {"cell": "B2", "value": "Esplanade", "type": "text", "source": "OM p.1", "phase": 3},
            {"cell": "B10", "value": 34000000, "type": "currency", "source": "OM p.3", "phase": 3},
            {"cell": "S26", "value": 850, "type": "currency", "source": "T-12 + 3%", "phase": 5},
            {"cell": "B45", "value": 0.0075, "type": "percent", "source": "fee band $25-50M", "phase": 3},
            {"cell": "B79", "value": 0.06, "type": "percent", "source": "exit triangulation HIGHEST", "phase": 10},
            {"cell": "B81", "value": 7, "type": "integer", "source": "business plan", "phase": 3},
        ],
        "headline_metrics": {"irr": 0.2251, "equity_multiple": 2.72, "exit_value": 55870669},
        "comps": {"sales": [{"name": "Comp A"}], "median_ppu": 237500},
        "forensic": {"lease_up_flag": False, "takeaways": ["strong T-3"]},
        "narrative": {"in_place_lift": "12%"},
        "memo_vars": {"deal_name": "Esplanade"},
    }


def _efb_spec():
    s = _acq_spec()
    s["meta"]["routing"] = "EFB"
    s["meta"]["template"] = "EFB Mini Model.xlsx"
    # EFB fee cell is B39, not B45
    s["cells"] = [
        {"cell": "B2", "value": "Rayzor Ranch", "type": "text", "source": "OM", "phase": 3},
        {"cell": "B10", "value": 36500000, "type": "currency", "source": "OM", "phase": 3},
        {"cell": "B39", "value": 0.05, "type": "percent", "source": "EFB std 5%", "phase": 3},
        {"cell": "B79", "value": 0.09, "type": "percent", "source": "direct", "phase": 10},
    ]
    s["headline_metrics"] = {"bond_amount": 42500000, "tax_savings_10yr": 4700000}
    return s


@pytest.mark.parametrize("spec_fn", [_acq_spec, _efb_spec])
def test_round_trip_byte_identical(spec_fn):
    spec = spec_fn()
    original = copy.deepcopy(spec)
    rebuilt = view_to_spec(spec_to_view(spec))
    assert rebuilt == original, "spec -> view -> spec must be byte-identical (no silent drop/reorder)"


@pytest.mark.parametrize("spec_fn", [_acq_spec, _efb_spec])
def test_no_silent_drop_of_safety_fields(spec_fn):
    spec = spec_fn()
    rebuilt = view_to_spec(spec_to_view(spec))
    # The safety-critical fields must survive verbatim.
    assert rebuilt["qa"] == spec["qa"]
    assert rebuilt["meta"]["deal_identity"] == spec["meta"]["deal_identity"]
    assert rebuilt["headline_metrics"] == spec["headline_metrics"]
    assert rebuilt["comps"] == spec["comps"]
    assert rebuilt["forensic"] == spec["forensic"]
    # Every original cell is present with identical metadata.
    assert rebuilt["cells"] == spec["cells"]


def test_view_exposes_mapped_fields_acq():
    view = spec_to_view(_acq_spec())
    assert view.routing == "ACQ"
    assert view.fields["property_name"] == "Esplanade"
    assert view.fields["purchase_price"] == 34000000
    assert view.fields["acquisition_fee_pct"] == 0.0075   # from B45
    assert view.fields["exit_cap_rate"] == 0.06
    assert view.fields["sale_year"] == 7


def test_view_uses_efb_fee_cell_b39():
    view = spec_to_view(_efb_spec())
    assert view.routing == "EFB"
    assert view.fields["acquisition_fee_pct"] == 0.05     # from B39, not B45
    assert view.cell_addr["acquisition_fee_pct"] == "B39"


def test_editing_a_view_field_changes_only_that_cell():
    spec = _acq_spec()
    view = spec_to_view(spec)
    view.fields["purchase_price"] = 33000000              # negotiate down
    rebuilt = view_to_spec(view)
    by_cell = {c["cell"]: c for c in rebuilt["cells"]}
    assert by_cell["B10"]["value"] == 33000000
    # source/type/phase metadata on the edited cell is preserved
    assert by_cell["B10"]["source"] == "OM p.3" and by_cell["B10"]["phase"] == 3
    # all other cells untouched
    assert by_cell["S26"]["value"] == 850 and by_cell["B79"]["value"] == 0.06


def test_reverse_view_subset_round_trip():
    """view -> spec -> view reconstructs the view's field subset exactly."""
    view1 = spec_to_view(_acq_spec())
    spec = view_to_spec(view1)
    view2 = spec_to_view(spec)
    assert view2.fields == view1.fields
    assert view2.cell_addr == view1.cell_addr


def test_unknown_routing_raises():
    bad = _acq_spec()
    bad["meta"]["routing"] = "XYZ"
    with pytest.raises(UnknownRoutingError):
        spec_to_view(bad)


def test_cells_order_helper_not_leaked_into_spec():
    """The internal _cells_order bookkeeping key must never appear in the reconstructed spec."""
    rebuilt = view_to_spec(spec_to_view(_acq_spec()))
    assert "_cells_order" not in rebuilt
