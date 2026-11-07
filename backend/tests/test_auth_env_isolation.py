"""Regression tests for the autouse auth isolation fixture in conftest.py."""
import auth


def test_auth_globals_start_empty():
    assert auth.GOOGLE_CLIENT_ID == ""
    assert auth.ALLOWED_EMAILS_RAW == ""
    assert auth.ALLOWED_EMAILS == set()


def test_in_test_mutation_does_not_leak_part_one():
    auth.ALLOWED_EMAILS.add("leak@example.com")
    auth.GOOGLE_CLIENT_ID = "leaked-client-id"
    auth.ALLOWED_EMAILS_RAW = "leak@example.com"


def test_in_test_mutation_does_not_leak_part_two():
    # Runs right after part one in file order; the fixture must have reset everything.
    assert auth.ALLOWED_EMAILS == set()
    assert auth.GOOGLE_CLIENT_ID == ""
    assert auth.ALLOWED_EMAILS_RAW == ""
