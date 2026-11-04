"""Make backend modules importable from tests regardless of pytest's rootdir."""
import os
import sys

# Existing tests were written against the v1 synchronous jobs API — keep them synchronous.
os.environ.setdefault("DREAM_JOBS_SYNC", "1")

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)


import pytest

# Every auth-related env var the backend reads (auth.py, auth_dep.py, app_jwt.py, routers/deals.py).
_AUTH_ENV_VARS = (
    "AUTH_JWT_SECRET",
    "AUTH_JWT_TTL_HOURS",
    "GOOGLE_CLIENT_ID",
    "ALLOWED_EMAILS",
    "DREAM_STRICT_OWNERSHIP",
)


@pytest.fixture(autouse=True)
def _isolate_auth_env(monkeypatch):
    """Start every test with no auth env so results do not depend on the host machine.

    Tests that need auth set it themselves with monkeypatch.setenv inside the test.
    """
    for name in _AUTH_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
