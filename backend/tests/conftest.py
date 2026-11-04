"""Make backend modules importable from tests regardless of pytest's rootdir."""
import os
import sys

# Existing tests were written against the v1 synchronous jobs API — keep them synchronous.
os.environ.setdefault("DREAM_JOBS_SYNC", "1")

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)


import pytest

# Auth-related env vars the backend reads (auth.py, auth_dep.py, app_jwt.py, routers/deals.py).
# This list covers those four modules only. It does not claim coverage of any other auth module.
_AUTH_ENV_VARS = (
    "AUTH_JWT_SECRET",
    "AUTH_JWT_TTL_HOURS",
    "GOOGLE_CLIENT_ID",
    "ALLOWED_EMAILS",
    "DREAM_STRICT_OWNERSHIP",
)

# Import-time isolation: conftest.py is loaded before any test module is collected, so clearing the
# host values here happens before auth.py runs its module-level os.environ reads. Without this,
# auth.GOOGLE_CLIENT_ID and auth.ALLOWED_EMAILS would capture the host machine's values at collection.
for _name in _AUTH_ENV_VARS:
    os.environ.pop(_name, None)


@pytest.fixture(autouse=True)
def _isolate_auth_env(monkeypatch):
    """Start every test with no auth env so results do not depend on the host machine.

    Clears the live environment and resets the module globals auth.py captured at import time.
    Tests that need auth set it themselves with monkeypatch inside the test.
    """
    for name in _AUTH_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    auth_mod = sys.modules.get("auth")
    if auth_mod is not None:
        monkeypatch.setattr(auth_mod, "GOOGLE_CLIENT_ID", "", raising=False)
        monkeypatch.setattr(auth_mod, "ALLOWED_EMAILS_RAW", "", raising=False)
        # auth_dep.py and routers/auth_login.py bind the same set object with "from auth import",
        # so clear it in place and restore it afterwards instead of rebinding the name.
        saved = set(auth_mod.ALLOWED_EMAILS)
        auth_mod.ALLOWED_EMAILS.clear()
        try:
            yield
        finally:
            auth_mod.ALLOWED_EMAILS.clear()
            auth_mod.ALLOWED_EMAILS.update(saved)
    else:
        yield
