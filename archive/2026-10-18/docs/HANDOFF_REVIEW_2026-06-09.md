# DREAM — Review handoff for Opus (2026-06-09, end of Wave-1 + review-fix session)

You are reviewing a day's worth of changes to **github.com/evanshields/DREAM** (local clone
`c:\Users\evana\DREAM`, branch `wave-a-foundation`). Everything is committed + pushed; the **last
commit (4619c82) is NOT deployed to the live server**. Your job: independently review the changes
(especially the security-sensitive ones), then green-light or amend the deploy.

---

## 1. THE ONE URGENT FACT (read before anything else)

**The live server at https://dream.shieldstone.co is running the OLD code with `AUTH_JWT_SECRET`
set in its `.env`. In that combination, the deployed `auth_dep.py` swallows EVERY Google ID token
(they're 3-segment JWTs, the old shape-check routes them to HS256 verification, which fails → 401).
Adding Google Test Users in the consent screen will NOT make Google sign-in work until either:**
  (a) the fix commit `4619c82` is deployed (the right answer), **or**
  (b) `AUTH_JWT_SECRET` is removed from `/opt/dream-app/backend/.env` + `pm2 restart dream-api`
      (unbreaks Google, but kills the password login Evan is using to test).

Also currently true on the live server: **`/api/jobs`, `/api/recalc`, `/api/export-excel` are
fully unauthenticated** (verified live — recalc returned 200 with no token). Anyone can read deal
data and burn paid Kimi LLM calls. The fix is in 4619c82. This is the main reason to deploy soon.

---

## 2. What happened this session (3 commits on `wave-a-foundation`)

### Commit 3c3edb9 — "Wave-1 backend" + dashboard (deployed to server ✅)
Built per `docs/HANDOFF_NEXT_CHAT.md` tasks #1–#3 + an urgent password-login request:
- **Kimi switch** (`routers/jobs.py get_analysts()`): env-gated (`DREAM_USE_KIMI=1` + non-empty
  `KIMI_API_KEY` → KimiAnalysts, else StubAnalysts; fail-safe to Stub). +6 tests.
- **Minimal password login** (so Evan can test before Google Test Users propagate):
  `password.py` (bcrypt 5.0.0, sha256-prehash, cost 12), `app_jwt.py` (HS256, 12h, fail-closed
  secret), `store/user_store.py` (SQLite, hash-only), `routers/auth_login.py`
  (`POST /api/auth/login`), `create_user.py` (getpass CLI). `require_auth` accepts app-JWT OR
  Google token; ALLOWED_EMAILS on both. +17 tests. Pinned `bcrypt==5.0.0`, `PyJWT==2.13.0`.
- **React assumption dashboard** (`gemini_ui/`): `AssumptionDashboard.tsx` + `api.ts` (editable
  cards → debounced `/api/recalc`; sensitivity grid → `/api/recalc/sensitivity`; recharts;
  Esplanade seed). Wired into hash router + nav. NOTE: gemini_ui is NOT the deployed frontend
  (see §6).
- Wave F design docs (`backend/store/WAVE_F_POSTGRES_DESIGN.md`, `backend/WAVE_F_FULL_AUTH_DESIGN.md`)
  + psycopg 3.3.4 audit saved to `shieldstone_os/shieldstone_operations/third-party-audits/2026-06-09-psycopg.md`.

**Server ops done for this commit (live now):** files deployed, bcrypt+PyJWT installed in
`/opt/dream-app/backend/venv`, env appended (`KIMI_API_KEY`, `KIMI_BASE_URL`,
`KIMI_MODEL=KIMI_MODEL_FASTPATH=moonshot-v1-128k`, `DREAM_USE_KIMI=1`, `AUTH_JWT_SECRET`
[generated on-server, 64 chars]), `evan` user created (Evan has the password from chat — it is in
no file), dream-api restarted. **Verified live:** password login → 200 token → `/api/me` 200.
Backups: `/opt/dream-app/backend.bak-20260609-172925-wave1` + `.env.bak-20260609-172925`.

### Live Kimi test (task #2) — partial success, exposed the big bug
A real job (`POST /api/jobs`, sparse Esplanade intake) ran 18.9s of live Moonshot calls
(wiring confirmed) then **422'd at synthesis**: `ACQDealInputs.__init__() missing 6 required
positional arguments (bridge_loan, bridge_rate, bridge_io_years, refi_loan, refi_rate,
refi_io_years)`. Engine itself verified intact live (deterministic `/api/recalc` reproduces
Esplanade: IRR 0.2221 / EM 2.733 / exit 55,870,667).

### Commit 4619c82 — "Production-readiness review fixes" (NOT deployed ⚠️ — review this one)
Evan asked for a flaw review → 7-angle multi-agent review over the branch diff → 10 ranked
findings → all critical/high fixed. **14 files, +510/−48. Full suite: 311 passed, 1 skipped
(live-Kimi). tsc clean. 9 new regression tests in `backend/tests/test_review_fixes.py`.**

| # | Finding (severity order) | Fix |
|---|---|---|
| 1 | Google tokens 401'd whenever AUTH_JWT_SECRET set (shape-based routing) | `app_jwt.is_app_token()` routes by UNVERIFIED `iss` claim ("dream-app" → app verify, else → Google). Routing only — trust still comes from full verification |
| 2 | `/api/jobs` `/api/recalc` `/api/export-excel` mounted with NO auth | `main.py` mounts all three with `dependencies=[Depends(require_auth)]`; router files stay bare so their test harnesses run tokenless; `gemini_ui/api.ts` now attaches `Authorization` from localStorage (`setAuthToken`) |
| 3 | Readiness gate checks 3 fields; engine needs 9 → live 422 after LLM spend | `synthesis._coerce_acq_inputs` validates BEFORE constructing: missing debt terms / exit_cap≤0 / total_equity≤0 / short noi_series raise `MissingEngineInputsError`; runner maps it to AWAITING_INPUT with blocking questions (`meta.critical_inputs.*` namespace so the existing answer flow routes values back). Added `SYNTHESIZING→AWAITING_INPUT` to the transition table |
| 4 | Resume after answer dropped original intake + ALL deal_docs | submit persists `intake_payload {intake_summary, deal_docs}` on the deal's seed spec; `answer_job` rehydrates + overlays answers; runner now merges full `critical_inputs` dict (wave0 only extracts the BL-17 three and was dropping answered engine fields) |
| 5 | Blocking RED gate still landed at CP-1 as status='computed' | runner fails closed: spec persisted as `gate_failed`, job → FAILED naming the gates |
| 6 | Sync multi-minute submit; 5 sequential LLM slices; cancel can't interrupt | `KimiAnalysts.run_all` now runs the 5 independent slices CONCURRENTLY (ThreadPoolExecutor; client built once pre-fan-out) ≈5x latency cut. Full async-queue redesign deliberately deferred (see §5) |
| 7 | exit_cap=0 passed the gate → DivisionByZero after spend | covered by #3's validation + pydantic `gt=0` on `/api/recalc` + sweep guard on `/api/recalc/sensitivity` |
| 8 | NaN irr → 500 + permanently poisoned persisted spec | `engine_boundary.f()`: non-finite → None |
| 9 | Idempotent replay inserted an orphan deal row per retry | `job_store.find_by_idempotency()`; submit checks it BEFORE `ds.create` |
| 10 | Two uncoordinated SQLite connections, no WAL → 'database is locked' | `open_sqlite()` sets `journal_mode=WAL` + `busy_timeout=15000`; SQLiteDealStore now uses `open_sqlite` |

---

## 3. What to review hardest (the security-sensitive diff)

`git diff 3c3edb9..4619c82` — focus on:
1. **`backend/auth_dep.py` + `backend/app_jwt.py`** — the issuer-dispatch. Confirm: (a)
   `is_app_token` grants NO trust (unverified decode used only to choose the verifier); (b) an
   app-issuer token failing verification → 401 (no fallthrough to Google with our own expired
   tokens); (c) JWT-only server (no GOOGLE_CLIENT_ID) + non-app token → 401 not 500; (d) the
   local-dev stub is unreachable when either secret is set.
2. **`backend/main.py` router gating** — confirm auth_login stays PUBLIC (login must mint the
   token) and nothing else is left open. Note `/api/health` and `/` remain public by design.
3. **`backend/jobs/runner.py`** — the two new exits (AWAITING_INPUT on MissingEngineInputsError,
   FAILED on RED gate): check the transition calls are legal and the audit trail is honest.
4. **`backend/routers/jobs.py`** — `intake_payload` on the seed spec: deal_docs (possibly large)
   now persist in SQLite per deal; acceptable for v1, flag if you disagree. The resume overlay
   ordering (answers beat originals).
5. **`backend/jobs/analysts.py`** — thread-safety of the concurrent slices (client built once
   before fan-out; OpenAI SDK clients are thread-safe for requests).

Run everything yourself:
```
cd c:\Users\evana\DREAM
.venv/Scripts/python -m pytest underwriting-engine/engine/tests underwriting-engine/fastpath/tests backend/tests -q
# expect: 311 passed, 1 skipped (the live-Kimi test)
```

---

## 4. Deploy steps (once you approve) — exact commands

```bash
# 1. backup
ssh -p 2222 -i ~/.ssh/id_ed25519 root@72.61.5.208 \
  'cp -a /opt/dream-app/backend /opt/dream-app/backend.bak-$(date +%Y%m%d-%H%M%S)-reviewfix'

# 2. copy the 12 changed backend files (from c:\Users\evana\DREAM\backend)
scp -P 2222 -i ~/.ssh/id_ed25519 app_jwt.py auth_dep.py engine_boundary.py main.py \
    root@72.61.5.208:/opt/dream-app/backend/
scp -P 2222 -i ~/.ssh/id_ed25519 jobs/analysts.py jobs/contracts.py jobs/job_store.py \
    jobs/runner.py jobs/synthesis.py root@72.61.5.208:/opt/dream-app/backend/jobs/
scp -P 2222 -i ~/.ssh/id_ed25519 routers/jobs.py routers/recalc.py \
    root@72.61.5.208:/opt/dream-app/backend/routers/
scp -P 2222 -i ~/.ssh/id_ed25519 store/deal_store.py root@72.61.5.208:/opt/dream-app/backend/store/

# 3. restart + check
ssh -p 2222 -i ~/.ssh/id_ed25519 root@72.61.5.208 \
  'pm2 restart dream-api --update-env && sleep 4 && pm2 logs dream-api --lines 6 --nostream'
```

**Live verification checklist (in order):**
1. `curl -s -o /dev/null -w "%{http_code}" https://dream.shieldstone.co/api/health` → 200
2. `curl -s -o /dev/null -w "%{http_code}" -X POST https://dream.shieldstone.co/api/recalc -H "Content-Type: application/json" -d '{}'` → **401** (was 200/422 — proves the gate landed)
3. Password login still works: `POST /api/auth/login {"username":"evan","password":"<Evan has it>"}` → 200 token; token on `/api/me` → 200
4. Token on `/api/recalc` with the Esplanade body → 200, IRR ≈ 0.2221
5. Token on `POST /api/jobs` with the sparse intake (`{"intake_summary":{"routing":"ACQ","deal_name":"Esplanade","critical_inputs":{"purchase_price":55000000,"hold_years":7,"exit_cap":0.06}}}`) → **`status:"awaiting_input"` with bridge/refi blocking questions** (was a 422 crash). Note: still spends ~20s of Kimi calls first.
6. After Test Users propagate: real Google sign-in → 200 (the issuer-dispatch fix makes this work alongside the password login)

Rollbacks if anything goes wrong: `/opt/dream-app/backend.bak-20260609-172925-wave1` (pre-Wave-1)
and the `-reviewfix` backup from step 1.

---

## 5. Known remaining gaps (real, deliberately deferred — next sessions)

- **Async job queue** (review finding #6's full fix): submit still runs synchronously in the
  request thread; with live docs it's still 1–4 min (now ÷5 via parallel slices). Needs the
  enqueue/worker split the runner docstring anticipates. **This is the biggest remaining
  production risk** (proxy timeouts on big deals).
- **No login UI in any frontend.** Backend auth is done; no frontend has a sign-in form/Google
  button in the repo. Evan currently tests via curl/token. Needs a small login page + token wiring.
- **The DEPLOYED frontend is not in the repo** (live title "DREAM — EFB Underwriter"; both repo
  frontends are "DreamVision"). Its source lives only on the VPS at `/opt/dream-app`. Recover it
  into the repo or replace it with gemini_ui (which now has the assumption dashboard + api token
  support).
- `/api/underwrite` still runs the OLD unvalidated engine (`backend/calculations/`) while
  `/api/recalc` runs the validated one — drift risk; retire or rewire.
- `verify_google_token` re-fetches Google certs per request (add caching).
- ~17 `sys.path.insert` hacks + a silent `_Shim` fallback in wave0/synthesis (package the app).
- Dashboard hardcodes Esplanade; can't load a real deal from `GET /api/jobs/{id}`.
- `'hap'/'noah'` substring matching false-flags ACQ deals as EFB-ambiguous (wave0).
- Orphaned earlier 422-test artifacts: 1 FAILED job + a few draft deal rows in the live DB (harmless).

**Evan's standing actions:** add 5 Google Test Users (in progress); rotate the Kimi key + Google
Client Secret (both rode through chat); password for the `evan` login is in Evan's chat history
only — store it in a password manager.

---

## 6. Paste-prompt for the Opus review session

> Read `c:\Users\evana\DREAM\docs\HANDOFF_REVIEW_2026-06-09.md` fully. Then review
> commit 4619c82 on branch wave-a-foundation of `c:\Users\evana\DREAM` (diff vs 3c3edb9) with a
> security-reviewer's eye, prioritizing §3 of the handoff. Run the full pytest suite to confirm
> 311 pass. If you find a flaw, fix it locally with a test and re-run the suite. When satisfied,
> deploy per §4 (backup → scp → restart) and run the 6-step live verification checklist. Report
> pass/fail on each step. Do NOT touch the vendored underwriting-engine/ or the locked contracts
> (Decimal only in engine_boundary; spec canonical; HITL stops at CP-1; no sqlite3 outside
> backend/store).
