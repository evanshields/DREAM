# Wave F.2 Design — `PostgresDealStore` (drop-in DealStore impl)

**Status:** design only (no code, no install, no deploy). Driver: `psycopg[binary]==3.3.4` + `psycopg-pool` (audited 2026-06-09, verdict green-with-hygiene — see `shieldstone_operations/third-party-audits/2026-06-09-psycopg.md`).

## 1. Goal & the contract it must mirror
`PostgresDealStore` is a **second implementation of the existing `DealStore` Protocol** in `backend/store/deal_store.py`. Nothing outside the store package changes. The swap is **config-only** through `get_deal_store()`.

The Protocol it must satisfy **exactly** (signatures already defined in `deal_store.py`):

```
create(spec, owner, now_iso, deal_id=None, status="draft") -> DealRecord
get(deal_id) -> DealRecord                       # raises DealNotFound
put(deal_id, spec, expected_version, now_iso,
    status=None, owner=None) -> DealRecord        # raises DealNotFound / VersionConflict
list(owner=None, routing=None, status=None) -> List[DealRecord]
delete(deal_id) -> None                           # raises DealNotFound
```

It **reuses the existing errors and dataclass unchanged**: `DealNotFound`, `VersionConflict(deal_id, expected, actual)`, `DealRecord`, and the existing `_index_from_spec(spec)` helper (derived index off the canonical spec — spec stays the single source of truth). No new public types. `create()` keeps generating `uuid.uuid4().hex` when `deal_id` is None.

**LOCKED-CONTRACT compliance:**
- Floats only — no `Decimal` crosses this boundary (Decimal lives only in `engine_boundary.py` + vendored engine). The spec blob is JSON; `json`/`jsonb` round-trips floats fine.
- `sqlite3` rule is unaffected — psycopg is a *new* driver, still confined to `backend/store/`. Add psycopg to the same architectural guard test so it (like sqlite3) cannot be imported outside the store package.
- Deterministic: still takes `now_iso` from the caller; **never calls a clock** and **never uses `DEFAULT now()` in SQL** for the index timestamps — they come from the argument, matching the sibling stores.

## 2. Schema (DDL)
One table, mirroring the SQLite `deals` table but using native Postgres types. `spec` becomes **`jsonb`** (queryable, validated, compact) instead of a TEXT blob — still treated as an *opaque document* by the app (we never author index fields independently; they are derived via `_index_from_spec`).

```sql
CREATE TABLE IF NOT EXISTS deals (
    deal_id     text PRIMARY KEY,
    spec        jsonb        NOT NULL,        -- canonical underwrite-spec.json (opaque document)
    version     integer      NOT NULL,
    slug        text,
    deal_name   text,
    routing     text,                          -- ACQ | EFB
    mode        text,                          -- HITL | HOTL
    status      text,                          -- draft|computed|populated|exported|archived
    owner       text,
    created_at  text,                          -- ISO-8601 string from caller (NOT a timestamptz default)
    updated_at  text
);
CREATE INDEX IF NOT EXISTS idx_deals_owner   ON deals(owner);
CREATE INDEX IF NOT EXISTS idx_deals_routing ON deals(routing);
CREATE INDEX IF NOT EXISTS idx_deals_status  ON deals(status);
```

Notes:
- `created_at`/`updated_at` stay **`text`** (ISO strings) to preserve byte-for-byte parity with the SQLite store's behavior and the deterministic `now_iso` contract — list ordering is lexicographic on ISO-8601, which is chronological. (A future migration could switch to `timestamptz` if richer querying is needed, but parity first.)
- `version` is the optimistic-concurrency counter (see §4). No DB trigger increments it — the store does, exactly like SQLite.
- `spec jsonb` enables future server-side filters (e.g. `spec->'meta'->>'routing'`) but the app keeps deriving the index in Python so both backends behave identically.

Schema is created idempotently on first store construction (mirroring `executescript(_SCHEMA)`), guarded so concurrent boot doesn't race (`CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS` are safe).

## 3. Connection pooling
Replace SQLite's "single shared connection + `threading.Lock`" with a **`psycopg_pool.ConnectionPool`** (sync pool — matches the sync store layer; no async rewrite).

- One module-level pool created in `__init__` from a DSN (`min_size` small, e.g. 1–2; `max_size` ~ FastAPI worker thread count, e.g. 8; `timeout` to fail fast).
- Each method borrows a connection via `with self._pool.connection() as conn:` and runs inside that connection's transaction (psycopg autocommits at the `with` block exit on success, rolls back on exception). **No global lock needed** — Postgres handles concurrency; the pool handles connection lifecycle. This removes the SQLite single-writer bottleneck.
- Pool is created once; `get_deal_store()` keeps returning a process-wide singleton so the pool is shared (do not open a pool per request).
- DSN from env (`DREAM_DATABASE_URL`, e.g. `postgresql://dream:***@host:5432/dream?sslmode=require`). Per the audit hygiene: TLS (`sslmode=require`), credentials in env only, never logged.
- `psycopg.rows.dict_row` row factory so rows behave like the SQLite `Row` mapping (`row["deal_id"]`), keeping `_row_to_record` near-identical.

## 4. Optimistic-version mapping (the crux)
The SQLite `put()` does: read current version under lock → compare to `expected_version` → `UPDATE ... WHERE deal_id=? AND version=expected`. Postgres does the **same compare-and-swap atomically in one statement**, no app-level lock:

```sql
UPDATE deals
   SET spec = %(spec)s::jsonb, version = version + 1,
       slug = %(slug)s, deal_name = %(deal_name)s, routing = %(routing)s,
       mode = %(mode)s, status = %(status)s, owner = %(owner)s, updated_at = %(now)s
 WHERE deal_id = %(deal_id)s AND version = %(expected)s
RETURNING deal_id, spec, version, slug, deal_name, routing, mode, status, owner, created_at, updated_at;
```

Resolution logic (mirrors SQLite semantics precisely):
- If `RETURNING` yields a row → success; build `DealRecord` from it (no second SELECT needed — `RETURNING` replaces the SQLite re-SELECT).
- If **no** row returned → disambiguate with one cheap `SELECT version FROM deals WHERE deal_id=%s`:
  - row missing → raise `DealNotFound(deal_id)`.
  - row present (version differs) → raise `VersionConflict(deal_id, expected_version, stored_version)`.
- `status`/`owner` "keep existing if None" logic: resolve the read+update in one `with self._pool.connection()` transaction (the row is locked for the txn duration, so the compare-and-swap stays correct even under the read).

`create()` maps `sqlite3.IntegrityError` → the existing `ValueError("deal_id '...' already exists")` by catching `psycopg.errors.UniqueViolation`. `delete()` checks `cur.rowcount == 0` → `DealNotFound`, exactly like SQLite.

JSONB adaptation: psycopg adapts a Python `dict` to `jsonb` via `psycopg.types.json.Jsonb(spec)` (or `%s::jsonb` with `json.dumps`). Reading back, `jsonb` comes out as a Python `dict` already — so `_row_to_record` drops the `json.loads(row["spec_json"])` and uses `row["spec"]` directly. Floats preserved (no Decimal introduced).

## 5. `_row_to_record` parity
Nearly identical to SQLite's; only difference is `spec` is already a dict (no `json.loads`) and `version` is a real `int`. Same `or ""` / `or 0` / `or "draft"` defensive defaults so absent columns behave identically.

## 6. Config-only swap in `get_deal_store()`
Introduce **`DREAM_DB_BACKEND`** (default `sqlite`). `get_deal_store()` becomes a small factory — the *only* call site that changes:

```
DREAM_DB_BACKEND = sqlite  (default)  -> SQLiteDealStore(default_db_path())   # unchanged today
DREAM_DB_BACKEND = postgres           -> PostgresDealStore(os.environ["DREAM_DATABASE_URL"])
```

No caller outside `get_deal_store()` references either class. Tests can still inject a store. The same env switch will be honored by the sibling `get_user_store()` and `get_job_store()` so the whole store package flips backends together. Keep the singleton + lazy-init pattern.

## 7. Tests (to add alongside the impl)
- Reuse the existing DealStore behavior suite against **both** backends (parametrize the fixture over SQLite + Postgres) so the contract is proven identical: create/get/put/list/delete, `VersionConflict`, `DealNotFound`, duplicate-id `ValueError`, list filters + `ORDER BY updated_at DESC`.
- Postgres tests gate on a `DREAM_TEST_DATABASE_URL` env (skip if absent) so CI without a PG instance still passes. Do **not** point tests at the live DB.
- Extend the architectural-guard test: assert `psycopg` (like `sqlite3`) is imported **only** inside `backend/store/`.
- Esplanade oracle is unaffected (engine untouched); a round-trip test (persist a computed Esplanade spec → reload → values byte-identical) is a cheap regression guard.

## 8. Migration path (SQLite -> Postgres)
One-time, offline, idempotent script: open the SQLite DB via `open_sqlite(default_db_path())`, `SELECT *`, and for each row `INSERT ... ON CONFLICT (deal_id) DO NOTHING` into Postgres preserving `deal_id`, `version`, all index fields, and timestamps verbatim (so optimistic-version continuity holds). Run jobs + users migrations together (same DB file today). Cut over by flipping `DREAM_DB_BACKEND=postgres`. Keep SQLite file as a rollback for one cycle.
