"""
backend/create_user.py — tiny CLI to create a login user WITHOUT writing plaintext to disk.

Reads the password interactively (getpass — no echo, no shell history, never a file) or from the
DREAM_NEW_PASSWORD env var for non-interactive provisioning. Hashes with bcrypt and persists only
the hash via the store package.

Usage (interactive — prompts for the password, nothing is echoed or logged):
    python backend/create_user.py --username evan --email evan@shieldstone.co

Non-interactive (e.g. piped secret; the value never lands on disk or in shell history if you
read it from a secret manager):
    DREAM_NEW_PASSWORD='...' python backend/create_user.py --username evan \
        --email evan@shieldstone.co --from-env

The DB file is DREAM_DB_PATH (default ./dream_deals.db) — the SAME file the app uses, so set
DREAM_DB_PATH to the production path when provisioning.
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from datetime import datetime, timezone

_BACKEND = os.path.dirname(os.path.abspath(__file__))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from store.user_store import get_user_store, UserExists  # noqa: E402
from password import hash_password  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Create a DREAM login user (bcrypt; no plaintext on disk).")
    ap.add_argument("--username", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--from-env", action="store_true",
                    help="read the password from DREAM_NEW_PASSWORD instead of prompting")
    args = ap.parse_args(argv)

    if args.from_env:
        password = os.environ.get("DREAM_NEW_PASSWORD", "")
        if not password:
            print("DREAM_NEW_PASSWORD is empty; refusing to create a user with no password.",
                  file=sys.stderr)
            return 2
    else:
        password = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.", file=sys.stderr)
            return 2
        if not password:
            print("Empty password; aborting.", file=sys.stderr)
            return 2

    now = datetime.now(timezone.utc).isoformat()
    pw_hash = hash_password(password)
    # Drop the plaintext reference promptly; it is never written anywhere.
    del password

    store = get_user_store()
    try:
        rec = store.create_user(args.username, args.email, pw_hash, now_iso=now)
    except UserExists:
        print(f"User '{args.username}' already exists. Delete it first or pick another username.",
              file=sys.stderr)
        return 1

    print(f"Created user '{rec.username}' <{rec.email}> in {os.environ.get('DREAM_DB_PATH', 'dream_deals.db')}.")
    print("Only the bcrypt hash was stored; plaintext was never written to disk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
