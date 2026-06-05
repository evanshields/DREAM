# DREAM backend — Wave A (foundation)

FastAPI backend for the DREAM underwriting app. This is the broadened "EFB Underwriter" app
(see `../DREAM_PRD.md` at the repo root, or `dream/DREAM_PRD.md` in shieldstone_os).

## Wave A modules (new)

| Module | Purpose | PRD epic |
|---|---|---|
| `engine_boundary.py` | The **Decimal seam** between FastAPI (float/JSON) and the vendored skill engine (Decimal). Carries the orchestration params (`servicing_spread`, `exit_on_forward_noi`) that reproduce Esplanade ground truth. Only this module + the engine touch `Decimal`. | A1.3 |
| `store/deal_store.py` | **DealStore** persistence (SQLite-first, Postgres-ready). Spec stored as an opaque document + thin relational index; optimistic-concurrency `version` field. Nothing outside this package imports `sqlite3`. | A1.2 |
| `adapters/spec_models.py` | **spec↔models adapter** — the `underwrite-spec.json` is canonical (master); the screen view is derived. Lossless, routing-aware (ACQ fee cell B45 vs EFB B39), view-pluggable. | A1.4 |
| `routers/recalc.py` | `/api/recalc` — instant, deterministic, **LLM-free** recalculation. Own router so its import graph excludes the Kimi client. | A1.5 |
| `qa_gates.py` | Server-side **QA-gate harness** — runs the BL gates (fee-bounds, unit-count, deal-identity, formula-integrity) at compute time and writes structured verdicts into `spec.qa.*`. Closes the hole where gates only lived in the populator's Excel-write path. | A1.6 |
| `auth_dep.py` | Configurable Google OAuth dependency. Enforced when `GOOGLE_CLIENT_ID` is set; transparent local-dev pass-through otherwise. | A0.2 |

The vendored skill engine lives at `../underwriting-engine/{engine,fastpath}/` (merged from PR #2)
and is reused **unmodified** — it is the validated source of all financial math.

## Python version note (IMPORTANT)

- **Production / VPS runs Python 3.13**, where `requirements.txt` (pinned numpy 2.1.2 / pandas 2.2.3
  / pymupdf 1.24.11) has prebuilt wheels. Install with `pip install -r requirements.txt`.
  (Verified clean on the US VPS 2026-06-05 after fixing two pins: `starlette==0.38.6` to satisfy
  `fastapi==0.115.0`, and adding `requests==2.32.3` which `auth.py` needs via `google.auth`.)
- **Local dev on Python 3.14**: those exact pins lack cp314 wheels (build-from-source hangs). For
  local testing, install the API layer at compatible versions instead — see the test setup below.
  Do NOT change the pinned `requirements.txt`; it targets the 3.13 production runtime.

## Running the tests

```bash
# from the repo root, in a venv with the engine reqs + the API layer:
.venv/Scripts/python -m pip install -r underwriting-engine/engine/requirements.txt pytest
.venv/Scripts/python -m pip install "fastapi>=0.115" "pydantic>=2.9" "starlette>=0.41" \
    "httpx>=0.27" "python-multipart" "python-dotenv" "google-auth" "requests" "openai"

.venv/Scripts/python -m pytest \
  underwriting-engine/engine/tests underwriting-engine/fastpath/tests backend/tests -q
# Wave A baseline: 106 passed (61 vendored engine/fastpath + 45 new backend).
```

## Endpoints (Wave A state)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET  | `/api/health` | public | health check |
| GET  | `/api/me` | protected | authenticated user (stub in local dev) |
| POST | `/api/recalc` | open | instant ACQ recalc, **no LLM** (A1.5) |
| POST | `/api/recalc/exit-cap` · `/api/recalc/agency-sizing` | open | dashboard helpers, no LLM |
| POST | `/api/underwrite` | protected | full model (EFB engine today; routing layer + acq_engine = Wave B) |
| POST | `/api/validate` | protected | T-Manual GREEN/AMBER/RED |
| POST | `/api/intake` · `/api/agent/chat` · `/api/agent/memo` | (existing) | reused as-is |

## Next: Waves B & C

Fully specified in `DREAM_PRD.md`. Wave B broadens `/api/underwrite` to general ACQ via a routing
layer + the assumption dashboard; Wave C ports the 3-wave chat-bot fast path as a backend service.
