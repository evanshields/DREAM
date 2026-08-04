# Wave F (auth) Design — Full Postgres-backed Password Auth (supersedes the Task C SQLite login)

**Status:** design only. Builds directly on the Task C primitives now in the repo:
`backend/store/user_store.py` (`SQLiteUserStore`, `UserRecord` with `failed_attempts` + `locked_until` fields), `backend/password.py` (bcrypt, sha256-prehash, cost 12), `backend/app_jwt.py` (HS256 app JWT, 12h TTL, fail-closed secret), `backend/routers/auth_login.py` (`/api/auth/login`), and `backend/auth.py` (`ALLOWED_EMAILS`, Google path). The Google-OAuth path is untouched — password auth remains a peer that independently satisfies `require_auth`.

Driver: `psycopg[binary]==3.3.4` (audited 2026-06-09, green-with-hygiene). Backend swap is the same `DREAM_DB_BACKEND` env from `backend/store/WAVE_F_POSTGRES_DESIGN.md`.

## 1. What changes vs Task C
Task C shipped the *stopgap*: bcrypt user store, generic 401, allowlist re-check, short JWT — but `record_failed_attempt`/`reset_failed_attempts` are best-effort and `locked_until` is unused. This wave makes it the **real** auth system:

| Capability | Task C (SQLite stopgap) | Wave F (Postgres full) |
|---|---|---|
| Storage | SQLite (shared deal DB file) | Postgres (`users` + new tables) via `PostgresUserStore` |
| Lockout | counter only, never enforced | **enforced** time-based lockout |
| Password reset | none | **token-based reset flow** |
| Session expiry | 12h JWT, no revocation | JWT **+ server-side session table** (revocable, idle + absolute expiry) |
| Allowlist | env `ALLOWED_EMAILS` only | env allowlist **+ DB allowlist for non-Google users** (invite/provision) |
| Non-Google users | manual `create_user.py` | **admin provisioning + invite/reset emails** |

## 2. `PostgresUserStore` (mirrors `SQLiteUserStore` exactly)
Same public API as Task C's store — `create_user`, `get_user`, `get_by_email`, `find_user`, `list_users`, `record_failed_attempt`, `reset_failed_attempts`, `delete_user` — plus the new lockout/reset/session methods below. Same `UserRecord` dataclass (the `failed_attempts`/`locked_until` fields finally get used). Same rules: parametrized SQL only, caller passes `now_iso` (no clock), no `Decimal`, psycopg confined to `backend/store/`. `get_user_store()` becomes a factory on `DREAM_DB_BACKEND` (sqlite|postgres), identical pattern to `get_deal_store()`.

### Schema
```sql
CREATE TABLE IF NOT EXISTS users (
    username        text PRIMARY KEY,
    email           text NOT NULL,
    password_hash   text,                       -- bcrypt; NULLable for Google-only / invited-not-yet-set
    created_at      text,
    failed_attempts integer NOT NULL DEFAULT 0,
    locked_until    text NOT NULL DEFAULT '',    -- ISO-8601; '' = not locked
    is_active       boolean NOT NULL DEFAULT true,
    source          text NOT NULL DEFAULT 'password'  -- 'password' | 'google' | 'invited'
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- DB allowlist for NON-Google users (supplements env ALLOWED_EMAILS, never weakens it)
CREATE TABLE IF NOT EXISTS allowlist (
    email      text PRIMARY KEY,                 -- stored lowercased
    note       text,
    added_by   text,
    created_at text
);

-- Password reset / invite tokens (single-use, expiring)
CREATE TABLE IF NOT EXISTS reset_tokens (
    token_hash text PRIMARY KEY,                 -- sha256 of the random token; raw token only emailed
    username   text NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    expires_at text NOT NULL,                    -- ISO-8601
    used_at    text NOT NULL DEFAULT '',
    purpose    text NOT NULL DEFAULT 'reset'     -- 'reset' | 'invite'
);
CREATE INDEX IF NOT EXISTS idx_reset_user ON reset_tokens(username);

-- Server-side sessions (revocable; complements the stateless JWT)
CREATE TABLE IF NOT EXISTS sessions (
    session_id   text PRIMARY KEY,               -- random; also embedded as 'sid' claim in the JWT
    username     text NOT NULL REFERENCES users(username) ON DELETE CASCADE,
    email        text NOT NULL,
    created_at   text NOT NULL,
    last_seen_at text NOT NULL,                  -- updated on use (idle-timeout basis)
    expires_at   text NOT NULL,                  -- absolute expiry
    revoked_at   text NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(username);
```

## 3. Lockout (enforced)
Policy: **N failed attempts (default 5) locks the account for L minutes (default 15)**, fixed window to start.
- `record_failed_attempt(username, now_iso)`: `failed_attempts += 1`; if the new count `>= MAX_FAILED` set `locked_until = now + LOCK_MINUTES` (ISO string computed by the router from `now_iso` — store stays clock-free). No-op on missing user (anti-enumeration).
- `reset_failed_attempts(username)`: zero the counter and clear `locked_until` (after a successful login or reset).
- **Enforcement in `auth_login.login`**: before verifying the password, if `user.locked_until` is non-empty and `locked_until > now_iso` → return the **same generic 401** as a bad password (do not reveal "locked" to anonymous callers to avoid enumeration).
- Config: `AUTH_MAX_FAILED`, `AUTH_LOCK_MINUTES` envs.

## 4. Password reset (token-based)
Two new endpoints on the existing `/api/auth` router (still **no LLM imports** — preserves the recalc import-graph guard):
- `POST /api/auth/reset/request {email}` → always returns generic success (no user-enumeration). If the email maps to a user: generate a 32-byte URL-safe random token, store **sha256(token)** in `reset_tokens` with `expires_at = now + RESET_TTL_MIN` (default 30 min), and email the **raw** token link. (Email transport = a thin mailer seam; design only here.)
- `POST /api/auth/reset/confirm {token, new_password}` → sha256 the token, look up an unused, unexpired row; on hit: `hash_password(new_password)` (reuse `backend/password.py` unchanged), update `users.password_hash`, set `used_at`, `reset_failed_attempts`, and **revoke all existing sessions** for that user. Generic failure on any miss/expiry/reuse.
- **Invites for non-Google users** reuse the same machinery with `purpose='invite'` and a longer TTL: admin creates a user row with `password_hash=NULL`, emails an invite token; confirm sets the first password.

## 5. Session expiry (JWT + revocable server session)
Keep the stateless **app JWT** (`app_jwt.py`) but bind it to a server-side session so logout/lockout/reset can revoke before the JWT's natural expiry:
- On login success: create a `sessions` row (`session_id`, `created_at=now`, `last_seen_at=now`, `expires_at=now+ABSOLUTE_TTL`), then `mint_token` with an added **`sid`** claim. `app_jwt` gains an optional `sid` in the payload — minimal, backward-compatible.
- `require_auth` (app-JWT path): after `decode_token`, look up `sid` in `sessions`; reject (401) if **missing, revoked, past `expires_at` (absolute), or idle beyond `IDLE_TTL`**. On accept, update `last_seen_at=now`. The JWT short-circuits invalid tokens before the DB hit.
- `POST /api/auth/logout` → set `revoked_at=now` for the caller's `sid`. Reset/lockout revoke **all** of a user's sessions.
- Config: `AUTH_SESSION_TTL_HOURS` (absolute, default 12), `AUTH_SESSION_IDLE_MIN` (idle, default 60). The Google-OAuth path is unchanged.

## 6. Allowlist + non-Google users
- **Env `ALLOWED_EMAILS` stays the hard gate** for both Google and password paths. Never weakened.
- **DB `allowlist` table supplements it** so non-Google users can be provisioned without a redeploy: effective allowlist = `ALLOWED_EMAILS` (env) ∪ `allowlist` (DB). Admin endpoints (gated to an admin subset) manage the DB allowlist + provisioning + invites.

## 7. Migration path (Task C SQLite -> Wave F Postgres)
1. Ship `PostgresUserStore` + new tables behind `DREAM_DB_BACKEND` (default still `sqlite` → zero behavior change until flipped).
2. One-time migration script (sibling to the DealStore migration): copy every `users` row SQLite → Postgres (preserve all fields; default `is_active=true`, `source='password'`). New tables start empty; seed `allowlist` from `ALLOWED_EMAILS` for parity.
3. Existing bcrypt hashes are **portable as-is** — same `backend/password.py`, no re-hash.
4. Flip `DREAM_DB_BACKEND=postgres` (deals + jobs + users move together). Existing Task C JWTs (no `sid`) remain valid until expiry — accept `sid`-less tokens during a one-cycle grace, then require `sid`. Keep SQLite as rollback for one cycle.
5. Tests: parametrize the user-store contract over both backends; add lockout-enforced, reset-flow, session-revocation, allowlist-union tests; extend the architectural guard so psycopg is store-package-only.

## 8. Locked-contract / guardrail compliance
- No LLM imports in the auth router or store (recalc import-graph guard stays green).
- psycopg confined to `backend/store/` (same guard that protects sqlite3).
- No `Decimal` anywhere in auth.
- HITL job semantics untouched — this is auth only.
- Caller-supplied `now_iso`, parametrized SQL, fail-closed secrets all preserved from Task C.
