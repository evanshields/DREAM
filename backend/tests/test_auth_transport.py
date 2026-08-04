"""Transport-caching acceptance test for verify_google_token (Phase 4c).

Today (pre-fix) verify_google_token constructed a fresh google_requests.Request() on every call,
defeating google-auth's cert caching (each call re-fetches Google's public certs). The fix hoists
one module-level `_GOOGLE_TRANSPORT` and reuses it across calls. This test proves both properties:
the transport passed into id_token.verify_oauth2_token IS auth._GOOGLE_TRANSPORT, and it is the
SAME object across repeated calls (not rebuilt each time).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import auth  # noqa: E402


def test_verify_google_token_reuses_module_level_transport(monkeypatch):
    captured_transports = []

    def _fake_verify_oauth2_token(token, transport, client_id):
        captured_transports.append(transport)
        # Valid-shaped idinfo — verify_google_token just returns it as-is; no extra field checks
        # happen inside the function itself (email/iss validation is Google's library's job).
        return {
            "sub": "1234567890",
            "email": "evan@shieldstone.co",
            "email_verified": True,
            "name": "Evan Shields",
            "picture": "https://example.com/pic.jpg",
            "iss": "accounts.google.com",
        }

    monkeypatch.setattr(auth.id_token, "verify_oauth2_token", _fake_verify_oauth2_token)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "fake-client-id.apps.googleusercontent.com")

    auth.verify_google_token("fake-token-1")
    auth.verify_google_token("fake-token-2")

    assert len(captured_transports) == 2
    # Both calls used the SAME transport object — the module-level _GOOGLE_TRANSPORT — not a
    # freshly constructed google_requests.Request() per call.
    assert captured_transports[0] is auth._GOOGLE_TRANSPORT
    assert captured_transports[1] is auth._GOOGLE_TRANSPORT
    assert captured_transports[0] is captured_transports[1]
