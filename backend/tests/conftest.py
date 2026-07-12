"""Make backend modules importable from tests regardless of pytest's rootdir."""
import os
import sys

# Existing tests were written against the v1 synchronous jobs API — keep them synchronous.
os.environ.setdefault("DREAM_JOBS_SYNC", "1")

_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)
