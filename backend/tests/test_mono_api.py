"""Router contract tests with explicitly disposable actors and a fake service."""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from routers.mono import create_router


class FakeService:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def call(*args):
            self.calls.append((name, args))
            if args[0] == "forbidden":
                raise HTTPException(403, "No configured association")
            return {"method": name, "deal_id": args[0]}
        return call


@pytest.fixture
def setup():
    service = FakeService()
    actor = {"subject": "disposable-fixture", "auth_method": "fixture"}
    app = FastAPI()
    app.include_router(create_router(service, lambda: actor), prefix="/api/deals")
    return TestClient(app), service, actor


REVISION = {"expected_revision": 1, "expected_deal_sha256": "fixture-digest"}
EDIT = {**REVISION, "field_id": "fixture", "entered_value": "0", "unit": "text", "reason": "Engineering fixture", "idempotency_key": "edit"}
GATE = {**REVISION, "gate": "comps", "decision": "confirm", "reason": "Engineering fixture", "idempotency_key": "gate", "comps_sha256": "comps"}


@pytest.mark.parametrize("method,suffix,body,service_method", [
    ("get", "", None, "view"),
    ("post", "/edits", EDIT, "edit"),
    ("post", "/calculations", REVISION, "calculate"),
    ("get", "/jobs/job", None, "job"),
    ("post", "/jobs/job/cancel", None, "cancel"),
    ("post", "/gates", GATE, "gate"),
])
def test_factory_routes_validated_values_and_server_actor(setup, method, suffix, body, service_method):
    client, service, actor = setup
    response = getattr(client, method)(f"/api/deals/fixture/mono{suffix}", **({"json": body} if body else {}))
    assert response.status_code == 200
    name, args = service.calls[0]
    assert name == service_method
    assert args[0] == "fixture"
    assert args[-1] is actor
    if body:
        assert args[1] == body


@pytest.mark.parametrize("suffix,body", [("/edits", EDIT), ("/calculations", REVISION), ("/gates", GATE), ("/jobs/job/cancel", {})])
@pytest.mark.parametrize("forged", [{"actor": {"subject": "evan"}}, {"path": "C:/arbitrary"}, {"authority": "owner"}, {"source": {"ledger_root": "caller"}}])
def test_mutation_extra_fields_rejected_before_service(setup, suffix, body, forged):
    client, service, _ = setup
    assert client.post(f"/api/deals/fixture/mono{suffix}", json={**body, **forged}).status_code == 422
    assert service.calls == []


@pytest.mark.parametrize("bad_revision", [True, "1", 0, -1, 1.5])
def test_revision_is_a_positive_strict_integer(setup, bad_revision):
    client, service, _ = setup
    assert client.post("/api/deals/fixture/mono/edits", json={**EDIT, "expected_revision": bad_revision}).status_code == 422
    assert service.calls == []


@pytest.mark.parametrize("value", [None, 0, "", False, "0", "12.5%"])
def test_values_retain_raw_meaning_without_browser_conversion(setup, value):
    client, service, _ = setup
    assert client.post("/api/deals/fixture/mono/edits", json={**EDIT, "entered_value": value}).status_code == 200
    supplied = service.calls[0][1][1]["entered_value"]
    assert supplied == value
    assert type(supplied) is type(value)


def test_actor_dependency_failure_prevents_any_service_call():
    service = FakeService()

    def reject():
        raise HTTPException(401, "Real authentication required")

    app = FastAPI()
    app.include_router(create_router(service, reject), prefix="/api/deals")
    with TestClient(app) as client:
        assert client.get("/api/deals/fixture/mono").status_code == 401
        assert client.post("/api/deals/fixture/mono/edits", json=EDIT).status_code == 401
    assert service.calls == []


@pytest.mark.parametrize("value", [["nested"], {"actor": "forged"}])
def test_entered_values_must_be_scalars(setup, value):
    client, service, _ = setup
    assert client.post("/api/deals/fixture/mono/edits", json={**EDIT, "entered_value": value}).status_code == 422
    assert service.calls == []


def test_service_authority_and_structured_conflict_preserved(setup):
    client, service, _ = setup
    assert client.get("/api/deals/forbidden/mono").status_code == 403

    def conflict(*args):
        raise HTTPException(409, {"code": "revision_conflict", "message": "Reread", "current_revision": 2})

    service.edit = conflict
    response = client.post("/api/deals/fixture/mono/edits", json=EDIT)
    assert response.status_code == 409
    assert response.json()["detail"]["current_revision"] == 2
