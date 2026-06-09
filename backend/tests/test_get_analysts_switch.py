"""Wave C — get_analysts() ENV-gated Kimi/Stub switch.

Asserts the three selection cases without ever calling the live LLM:
  (1) default (no flag)                  => StubAnalysts
  (2) DREAM_USE_KIMI=1 + KIMI_API_KEY    => KimiAnalysts
  (3) DREAM_USE_KIMI=1 + NO key          => StubAnalysts (fail-safe)

KimiAnalysts builds its Moonshot client LAZILY (only when a slice actually runs),
so merely selecting/constructing it here touches no network and needs no real key.
This test never calls .run_all / .slice_*, so no LLM is invoked.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import routers.jobs as jobs_router  # noqa: E402
from jobs.analysts import StubAnalysts, KimiAnalysts  # noqa: E402


def _clear_env(monkeypatch):
    monkeypatch.delenv("DREAM_USE_KIMI", raising=False)
    monkeypatch.delenv("KIMI_API_KEY", raising=False)


def test_default_is_stub(monkeypatch):
    _clear_env(monkeypatch)
    analysts = jobs_router.get_analysts()
    assert isinstance(analysts, StubAnalysts)
    assert not isinstance(analysts, KimiAnalysts)


def test_flag_off_explicit_is_stub(monkeypatch):
    # An explicit falsey flag (even with a key present) stays on Stub.
    _clear_env(monkeypatch)
    monkeypatch.setenv("DREAM_USE_KIMI", "0")
    monkeypatch.setenv("KIMI_API_KEY", "sk-should-be-ignored")
    assert isinstance(jobs_router.get_analysts(), StubAnalysts)


def test_flag_on_with_key_is_kimi(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("DREAM_USE_KIMI", "1")
    monkeypatch.setenv("KIMI_API_KEY", "sk-test-key-not-used-no-network")
    analysts = jobs_router.get_analysts()
    assert isinstance(analysts, KimiAnalysts)


def test_flag_on_truthy_words_with_key_is_kimi(monkeypatch):
    for val in ("true", "YES", "On"):
        _clear_env(monkeypatch)
        monkeypatch.setenv("DREAM_USE_KIMI", val)
        monkeypatch.setenv("KIMI_API_KEY", "sk-test-key")
        assert isinstance(jobs_router.get_analysts(), KimiAnalysts), val


def test_flag_on_no_key_falls_back_to_stub(monkeypatch):
    # Fail-safe: flag set, key missing -> Stub, never an exception / 500.
    _clear_env(monkeypatch)
    monkeypatch.setenv("DREAM_USE_KIMI", "1")
    analysts = jobs_router.get_analysts()
    assert isinstance(analysts, StubAnalysts)


def test_flag_on_empty_key_falls_back_to_stub(monkeypatch):
    # An empty/whitespace key is treated as absent (fail-safe).
    _clear_env(monkeypatch)
    monkeypatch.setenv("DREAM_USE_KIMI", "1")
    monkeypatch.setenv("KIMI_API_KEY", "   ")
    assert isinstance(jobs_router.get_analysts(), StubAnalysts)
