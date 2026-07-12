# DREAM — Handoff to next chat (2026-06-09)

Paste this into a fresh Claude Code chat to continue DREAM v3.0. It picks up after Waves A–E shipped
and the US VPS migration completed. Goal: knock out tasks #1–#5 below using sub-agent swarms, max
parallelism where dependencies allow.

---

## STATE (verified, do not redo)

- **Repo:** `github.com/evanshields/DREAM`, local clone `c:\Users\evana\DREAM`, branch
  **`wave-a-foundation`** (PR #3 open vs main), latest commit **571d6d8**.
- **All PRD code waves built:** A (foundation), B-backend (EFB→ACQ broaden, routing, /api/underwrite/v2,
  sensitivity, acq_validator), C-v1 (chat-bot fast-path job service: jobs/{job_store,wave0,analysts,
  runner} + routers/jobs.py), D (Excel push: routers/export_excel.py), E (Hermes intake seam — design
  doc only, `backend/jobs/HERMES_INTAKE_SEAM.md`). **279 tests pass, 1 skipped (live-Kimi).**
- **LIVE:** `https://dream.shieldstone.co` on the US VPS (`ssh -p 2222 -i ~/.ssh/id_ed25519
  root@72.61.5.208`), PM2 `dream-api` on 127.0.0.1:8001, served by **Caddy** (NOT nginx; Caddyfile at
  `/etc/caddy/Caddyfile`, auto-TLS). Google OAuth ENFORCED (AUTH_ENABLED true; /api/me → 401 without
  token). UK VPS dream-api STOPPED (retired). Rollback: `/opt/dream-app.bak-ce2310b` +
  `/etc/caddy/Caddyfile.bak-20260609-oauth`.
- **Engine:** validated skill engine vendored at `underwriting-engine/` (re-synced to canonical, 162
  engine/fastpath tests). Reused unmodified. Esplanade ground truth: IRR 0.2251 / EM 2.72 / exit
  55,870,669 (2% IRR tol, 0.5% headline). Decimal lives ONLY in `backend/engine_boundary.py` + the engine.
- **Local Python is 3.14** (no wheels for the pinned numpy/pandas/pymupdf — install the API layer at
  compatible versions for local tests; the SERVER is py3.13 where `backend/requirements.txt` installs
  clean). Local test venv: `c:\Users\evana\DREAM\.venv`. Run:
  `.venv/Scripts/python -m pytest underwriting-engine/engine/tests underwriting-engine/fastpath/tests backend/tests -q`
- **Kimi key:** in the LOCAL gitignored `backend/.env` (base_url `https://api.moonshot.ai/v1`, use model
  `moonshot-v1-128k`). NOT on the server yet. The key value is in that local file — read it from there;
  do not ask the user to re-paste. (User should rotate it eventually — rode through chat.)
- **OAuth:** Client ID `954847212741-g00fssf9sa9mvglus6b61cc61pt3f7hj.apps.googleusercontent.com`.
  ALLOWED_EMAILS on the server: evan@shieldstone.co, fahd@shieldstone.co, alton@shieldstone.co,
  chuck@shieldstone.co, charles@gatewaymb.co. **External OAuth app** — those 5 must also be added as
  **Test Users** in the Google consent screen or login 403s (USER action, may already be done).
- **Persistence:** `backend/store/deal_store.py` SQLite, exposes `open_sqlite`/`default_db_path` so
  `jobs/job_store.py` persists through the store package (architectural guard: no sqlite3 import outside
  `backend/store/`). Jobs + deals share one DB. Postgres swap = Wave F.2.
- **CONTRACTS to honor:** Decimal only in engine_boundary; spec (`underwrite-spec.schema.json`) is the
  canonical object, `models.py` is a view via `backend/adapters/spec_models.py`; BL safety gates fire
  server-side via `backend/qa_gates.py`; HITL = jobs stop at AWAITING_CP1, never auto-complete.
- **Known noise:** a stale `PostToolUse` CHANGELOG hook in `shieldstone_os/.claude/settings.json` fires
  on every bash command (benign, ignore; or remove the `hooks` block).
- Full background: `docs/DREAM_PRD.md`, memory `project_dream-v3-prd.md`.

---

## THE FIVE TASKS + dependency map

| # | Task | Depends on | Parallel group |
|---|------|-----------|----------------|
| 1 | **Verify OAuth login end-to-end** — confirm a token from an allow-listed Google account → /api/me 200; non-listed → 403; no token → 401. Document the exact login flow the frontend uses. | Google test users added (user) | A (indep) |
| 2 | **Wire Kimi on the server → live chat-bot.** Add KIMI_API_KEY + KIMI_BASE_URL + KIMI_MODEL=moonshot-v1-128k to the SERVER `/opt/dream-app/backend/.env` (value from local `backend/.env`), restart dream-api, run a real end-to-end job via `/api/jobs` with KimiAnalysts (one real deal) → confirm it reaches CP-1 with live LLM slices. | key (in local .env) | A (indep) |
| 3 | **Wave B.3 — React assumption dashboard.** In `gemini_ui/` (the Vite/React app): assumptions as editable cards (value/type/range/benchmark/source), edits call `/api/recalc` (no LLM), a sensitivity grid calling `/api/recalc/sensitivity`. Build + verify against the LIVE API. | live API (#done) | B (indep code; can run alongside A) |
| 4 | **Wave F infra: Postgres DealStore + username/password auth mini-wave.** Stand up Postgres on the US VPS (audit the driver per the third-party rule), add a `PostgresDealStore` impl behind the existing `DealStore` interface (config-only swap), and build a Postgres-backed username/password login (bcrypt/passlib, sessions, lockout, reset) ALONGSIDE the existing Google OAuth — both gate access; allowlist same 5 + room for non-Google users. Vetted libs only, hashed-never-plaintext, its own tested suite. | touches DealStore + auth | C (SEQUENCE AFTER #2 lands or isolate; conflicts with #2 on .env/restart) |
| 5 | **Merge PR #3 → main.** Branch `wave-a-foundation` → main once #1/#2 verified. Housekeeping. | #1, #2 green | last |

**Recommended swarm shape (3 waves):**
- **Wave 1 (parallel):** #1 (login verify, ops) + #3 (dashboard, frontend) + #2 (Kimi server, ops). These touch different surfaces (Caddy/Google vs gemini_ui vs server .env+jobs) — safe concurrent.
- **Wave 2:** #4 (Postgres + password auth) — its own track; run after #2 so the server .env/restart dance doesn't collide; audit the Postgres driver first.
- **Wave 3:** #5 merge PR after #1+#2 verified green.

---

## METAPROMPT (paste to start)

```
You are continuing DREAM v3.0 (github.com/evanshields/DREAM, local c:\Users\evana\DREAM, branch
wave-a-foundation @ 571d6d8). Read docs/HANDOFF_NEXT_CHAT.md and memory project_dream-v3-prd.md
FIRST — the full verified state is there; do not redo shipped work. The app is LIVE at
https://dream.shieldstone.co (US VPS, Caddy, Google OAuth on, UK retired); 279 tests green.

Knock out tasks #1–#5 from the handoff using sub-agent swarms, maximizing parallelism per the
dependency map. Use Workflow for multi-agent orchestration. Honor every locked contract (Decimal only
in engine_boundary; spec is canonical; BL gates server-side; HITL stops at CP-1; no sqlite3 outside
backend/store; reuse the vendored engine unmodified; Esplanade is the oracle). Agents DRAFT code you
review + test before applying to shared files; run the full pytest suite after each apply; commit per
task with clear messages (Co-Authored-By: Claude Opus 4.8). The Kimi key is in the LOCAL backend/.env
— read it, don't ask. Run the third-party audit before adding the Postgres driver (per the global
audit rule; save to shieldstone_operations/third-party-audits/).

Sequence: Wave 1 parallel {#1 verify OAuth login, #2 wire Kimi on server + one live end-to-end job,
#3 React assumption dashboard}; then #4 (Postgres DealStore + username/password auth mini-wave, its
own track, after #2); then #5 (merge PR #3 → main once #1/#2 green). Confirm the budget/scope with
Evan before spinning a large swarm if token cost will be high.

USER ACTIONS that may gate tasks (check, don't assume): (a) 5 emails added as Google consent Test
Users for #1; (b) Client Secret + Kimi key rotation (security hygiene, not blocking). Surface these.
```
