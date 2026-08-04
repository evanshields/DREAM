"""Legacy /api/underwrite retirement (Phase 4c, 2026-07-12) — the route used to run the OLD
unvalidated float engine in backend/calculations/. It is now a 410 tombstone; the successors are
/api/underwrite/v2 (ACQ) and /api/underwrite/efb (routers/recalc.py).

Uses TestClient(main.app) directly (NOT as a context manager) to avoid triggering FastAPI's
lifespan/startup — the lifespan now sweeps stale jobs via jobs.queue, which may not exist yet in
this working tree (another builder owns that file). Auth env is left unset so require_auth's
local-dev stub applies and the assertions aren't gated on a token.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    from starlette.testclient import TestClient
    import main
    # Deliberately NOT a context manager — entering it would run the lifespan startup sweep,
    # which imports jobs.queue (may not exist yet while another builder is creating it).
    return TestClient(main.app)


def test_legacy_underwrite_returns_410(client):
    r = client.post("/api/underwrite", json={})
    assert r.status_code == 410
    detail = r.json().get("detail", "")
    assert "Retired" in detail
    assert "/api/underwrite/v2" in detail
    assert "/api/underwrite/efb" in detail


def test_validate_still_works_with_minimal_body(client):
    """/api/validate is unaffected by the retirement — DealInputs' fields all have defaults, so
    an empty body is a valid minimal deal."""
    r = client.post("/api/validate", json={})
    assert r.status_code not in (410, 404)
    assert r.status_code == 200
    body = r.json()
    assert "flags" in body
    assert "pass_fail" in body


def test_compute_pro_forma_no_longer_referenced_in_main_source():
    """Source-level guard: the retired route's old engine call must not linger in main.py."""
    main_py_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"
    )
    with open(main_py_path, "r", encoding="utf-8") as fh:
        source = fh.read()
    assert "compute_pro_forma" not in source
