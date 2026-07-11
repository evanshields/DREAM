"""/api/intake auth gate — the upload triggers a paid Kimi extraction, so it must sit behind
require_auth exactly like /api/underwrite (previously it 422'd on a missing token instead of 401,
i.e. an unauthenticated upload could reach the paid extractor).

main.py itself is NOT importable in this test venv (its intake import graph needs
pandas/pymupdf/openai, which the suite deliberately does not carry — same constraint as
test_auth_gate.py). The proof is therefore two-part:

1. Functional — a minimal app mounting a POST /api/intake UploadFile route with the SAME
   `Depends(require_auth)` signature main.py now uses: 401 without a token when auth is enabled,
   local-dev stub pass-through when disabled.
2. Source-level — parse backend/main.py's AST (no import) and assert the real `intake` route
   function carries Depends(require_auth), so the functional proof cannot drift from the file
   actually deployed.
"""
import ast
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_MAIN_PY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")


def _app():
    """Minimal app mounting an UploadFile route gated the way main.py gates /api/intake."""
    pytest.importorskip("multipart")  # python-multipart — required by FastAPI for UploadFile
    from fastapi import Depends, FastAPI, File, UploadFile
    from auth_dep import require_auth

    app = FastAPI()

    @app.post("/api/intake")
    async def intake(file: UploadFile = File(...), user: dict = Depends(require_auth)):
        body = await file.read()
        return {"filename": file.filename, "size": len(body), "email": user.get("email")}

    return app


def _client(app):
    from starlette.testclient import TestClient
    return TestClient(app)


def _post_file(client, headers=None):
    return client.post(
        "/api/intake",
        files={"file": ("deal_t12.csv", b"gross potential rent, 1000000\n", "text/csv")},
        headers=headers or {},
    )


def test_intake_local_dev_passthrough(monkeypatch):
    """Auth disabled (no GOOGLE_CLIENT_ID / AUTH_JWT_SECRET) -> stub user, upload still works."""
    pytest.importorskip("starlette")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)
    r = _post_file(_client(_app()))
    assert r.status_code == 200
    assert r.json()["email"] == "evan@shieldstone.co"


def test_intake_401_without_token(monkeypatch):
    """Auth enabled -> an unauthenticated upload is 401 (not 422) and never reaches the handler."""
    pytest.importorskip("starlette")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    r = _post_file(_client(_app()))
    assert r.status_code == 401


def test_intake_401_with_invalid_token(monkeypatch):
    pytest.importorskip("starlette")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")
    r = _post_file(_client(_app()), headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401


def test_main_py_intake_route_carries_require_auth():
    """Source-level proof against the REAL main.py: the `intake` function's parameter defaults
    include a Depends(require_auth) call. AST parse only — no heavy imports."""
    with open(_MAIN_PY, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())

    intake_fn = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "intake":
            intake_fn = node
            break
    assert intake_fn is not None, "main.py no longer defines an `intake` route function"

    def _is_require_auth_depends(default: ast.expr) -> bool:
        return (
            isinstance(default, ast.Call)
            and isinstance(default.func, ast.Name)
            and default.func.id == "Depends"
            and len(default.args) == 1
            and isinstance(default.args[0], ast.Name)
            and default.args[0].id == "require_auth"
        )

    defaults = list(intake_fn.args.defaults) + [
        d for d in intake_fn.args.kw_defaults if d is not None
    ]
    assert any(_is_require_auth_depends(d) for d in defaults), (
        "/api/intake is not gated: no Depends(require_auth) in the intake() signature"
    )
