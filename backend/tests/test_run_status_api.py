"""API tests for routers/run_status.py on a bare FastAPI app. No token, no live services."""
import os
import sys

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers.run_status import router  # noqa: E402

app = FastAPI()
app.include_router(router)
client = TestClient(app)

IDS = [
    "run-blocked-red-gate", "run-clean-awaiting-cp1", "run-failed",
    "run-in-progress", "run-missing-values", "run-stale-engine-commit",
]
PATHS = ["/api/run-status", "/api/run-status/run-failed"]


def test_list_returns_six_runs():
    r = client.get("/api/run-status")
    assert r.status_code == 200
    runs = r.json()["runs"]
    assert sorted(x["run_id"] for x in runs) == IDS
    assert all(x["synthetic"] is True for x in runs)
    assert all(x["display_state"] for x in runs)


@pytest.mark.parametrize("run_id", IDS)
def test_detail_ok(run_id):
    r = client.get(f"/api/run-status/{run_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] == run_id
    assert body["read_only"] is True
    assert body["synthetic"] is True


def test_detail_blocked_is_diagnostic():
    body = client.get("/api/run-status/run-blocked-red-gate").json()
    assert body["display_state"] == "blocked" and body["values_are_diagnostic"] is True


def test_unknown_id_404():
    assert client.get("/api/run-status/run-nope").status_code == 404


@pytest.mark.parametrize(
    "bad",
    ["..%2Fetc%2Fpasswd", "../etc/passwd", "..", "RUN-FAILED", "run_failed", "a" * 65, "run-failed.json", "run%00failed"],
)
def test_bad_ids_404(bad):
    assert client.get(f"/api/run-status/{bad}").status_code == 404


def test_max_length_id_is_just_unknown():
    assert client.get("/api/run-status/" + "a" * 64).status_code == 404


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_write_methods_405(path, method):
    assert getattr(client, method)(path).status_code == 405


def test_router_only_registers_get():
    routes = [r for r in router.routes if isinstance(r, APIRoute)]
    assert len(routes) == 2
    for route in routes:
        assert route.methods == {"GET"}


def _keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _keys(v)


def test_no_secret_like_keys():
    bodies = [client.get("/api/run-status").json()]
    bodies += [client.get(f"/api/run-status/{i}").json() for i in IDS]
    for body in bodies:
        for key in _keys(body):
            assert key.lower() not in ("secret", "token", "password")
