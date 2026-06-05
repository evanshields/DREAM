"""A1.2 acceptance tests — DealStore persistence + optimistic concurrency + opaque-document
round trip + the 'no DB driver outside the store' architectural guard."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store import SQLiteDealStore, DealNotFound, VersionConflict  # noqa: E402

NOW = "2026-06-05T12:00:00Z"
LATER = "2026-06-05T13:00:00Z"


def _spec(slug="esplanade", routing="ACQ", units=240):
    return {
        "meta": {"deal_name": "Esplanade", "slug": slug, "routing": routing, "mode": "HITL"},
        "qa": {"unit_count": {"counted": units, "blocked": False}},
        "cells": [{"cell": "B10", "value": 34000000, "source": "OM p.3"}],
        "headline_metrics": {"irr": 0.2251, "equity_multiple": 2.72},
    }


def store():
    return SQLiteDealStore(":memory:")


def test_create_then_get_round_trips_opaque_spec():
    s = store()
    rec = s.create(_spec(), owner="evan@shieldstone.co", now_iso=NOW)
    got = s.get(rec.deal_id)
    # The full spec survives byte-for-byte (opaque document).
    assert got.spec == _spec()
    assert got.version == 1
    # Index fields are derived off the spec.
    assert got.slug == "esplanade" and got.routing == "ACQ" and got.deal_name == "Esplanade"
    assert got.owner == "evan@shieldstone.co" and got.status == "draft"
    assert got.created_at == NOW and got.updated_at == NOW


def test_put_increments_version_and_updates_index():
    s = store()
    rec = s.create(_spec(), owner="evan", now_iso=NOW)
    new_spec = _spec(slug="esplanade-v2")
    new_spec["headline_metrics"]["irr"] = 0.19
    updated = s.put(rec.deal_id, new_spec, expected_version=1, now_iso=LATER, status="computed")
    assert updated.version == 2
    assert updated.slug == "esplanade-v2"
    assert updated.status == "computed"
    assert updated.updated_at == LATER and updated.created_at == NOW  # created_at preserved
    assert s.get(rec.deal_id).spec["headline_metrics"]["irr"] == 0.19


def test_version_conflict_blocks_lost_update():
    s = store()
    rec = s.create(_spec(), owner="evan", now_iso=NOW)
    # Two readers both hold version 1. First write succeeds (now v2).
    s.put(rec.deal_id, _spec(slug="a"), expected_version=1, now_iso=LATER)
    # Second writer still thinks it's v1 -> conflict, no silent clobber.
    with pytest.raises(VersionConflict) as ei:
        s.put(rec.deal_id, _spec(slug="b"), expected_version=1, now_iso=LATER)
    assert ei.value.expected == 1 and ei.value.actual == 2
    # The slug from the first (winning) write is intact.
    assert s.get(rec.deal_id).slug == "a"


def test_get_missing_raises():
    s = store()
    with pytest.raises(DealNotFound):
        s.get("nope")


def test_put_missing_raises():
    s = store()
    with pytest.raises(DealNotFound):
        s.put("nope", _spec(), expected_version=1, now_iso=NOW)


def test_list_filters_by_owner_routing_status():
    s = store()
    s.create(_spec(slug="acq1", routing="ACQ"), owner="evan", now_iso=NOW, status="draft")
    s.create(_spec(slug="efb1", routing="EFB"), owner="evan", now_iso=NOW, status="computed")
    s.create(_spec(slug="acq2", routing="ACQ"), owner="chuck", now_iso=NOW, status="draft")
    assert {r.slug for r in s.list(owner="evan")} == {"acq1", "efb1"}
    assert {r.slug for r in s.list(routing="ACQ")} == {"acq1", "acq2"}
    assert {r.slug for r in s.list(owner="evan", status="draft")} == {"acq1"}


def test_delete():
    s = store()
    rec = s.create(_spec(), owner="evan", now_iso=NOW)
    s.delete(rec.deal_id)
    with pytest.raises(DealNotFound):
        s.get(rec.deal_id)
    with pytest.raises(DealNotFound):
        s.delete(rec.deal_id)


def test_explicit_deal_id_and_duplicate_guard():
    s = store()
    s.create(_spec(), owner="evan", now_iso=NOW, deal_id="fixed-id")
    assert s.get("fixed-id").deal_id == "fixed-id"
    with pytest.raises(ValueError):
        s.create(_spec(), owner="evan", now_iso=NOW, deal_id="fixed-id")


def test_no_sqlite_or_filepath_outside_store():
    """Architectural guard (PRD A1.2): no module outside backend/store imports sqlite3 or builds
    a per-deal file path. Scans backend/*.py and the new modules."""
    import re
    backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    offenders = []
    for root, dirs, files in os.walk(backend):
        # skip the store package itself, tests, caches, venvs, the vendored engine
        if (os.sep + "store") in root or (os.sep + "tests") in root:
            continue
        if "__pycache__" in root or ".venv" in root or "underwriting-engine" in root:
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(root, fn)
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                src = fh.read()
            if re.search(r"\bimport\s+sqlite3\b|\bfrom\s+sqlite3\b", src):
                offenders.append(f"{p}: imports sqlite3")
            if "underwrites/" in src and (".json" in src):
                offenders.append(f"{p}: builds a per-deal file path")
    assert not offenders, "persistence leaked outside DealStore:\n" + "\n".join(offenders)
