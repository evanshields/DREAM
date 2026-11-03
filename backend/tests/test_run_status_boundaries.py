"""Static boundary checks: read the source text of the slice and its fixtures."""
import io
import json
import os
import tokenize

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLICE_DIR = os.path.join(BACKEND, "run_status")
ROUTER = os.path.join(BACKEND, "routers", "run_status.py")
FIXTURES = os.path.join(BACKEND, "fixtures", "run_status")

FORBIDDEN = [
    "sqlite3", "psycopg", "engine_boundary", "Decimal", "openai", "anthropic",
    "requests", "httpx", "subprocess", "os.environ",
]


def _slice_files():
    files = [os.path.join(SLICE_DIR, n) for n in sorted(os.listdir(SLICE_DIR)) if n.endswith(".py")]
    return files + [ROUTER]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _fixture_files():
    return [os.path.join(FIXTURES, n) for n in sorted(os.listdir(FIXTURES)) if n.endswith(".json")]


@pytest.mark.parametrize("path", _slice_files())
@pytest.mark.parametrize("word", FORBIDDEN)
def test_forbidden_words_absent(path, word):
    assert word not in _read(path), f"{word} found in {path}"


@pytest.mark.parametrize("path", _fixture_files())
def test_fixture_is_synthetic_and_clean(path):
    data = json.loads(_read(path))
    assert data["synthetic"] is True

    def keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield k
                yield from keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from keys(v)

    for k in keys(data):
        assert "rent_ami" not in k and "utility" not in k


def test_six_fixtures():
    assert len(_fixture_files()) == 6


def test_no_arithmetic_operators_in_slice_code():
    """Token scan: no + - * / operator tokens in code (strings and comments are ignored).
    Counting is done with len() and sum(1 for ...), which need none."""
    bad = []
    for path in _slice_files():
        with open(path, "rb") as fh:
            for tok in tokenize.tokenize(io.BytesIO(fh.read()).readline):
                if tok.type == tokenize.OP and tok.string in ("+", "-", "*", "/", "+=", "-=", "*=", "/=", "//", "**", "%"):
                    bad.append((os.path.basename(path), tok.start[0], tok.string))
    # Only allowed: the "/" path join on Path objects in loader.py (file paths, not values).
    assert all(name == "loader.py" and op == "/" for name, _, op in bad), bad
    assert len(bad) <= 3, bad
