# DREAM Frontend PRD — v1 (the real front door)

**Status:** Ready for execution · **Author:** Fable 5 (2026-06-09) · **Executor:** Opus (fresh session)
**Goal:** Build the ONE real, deployed, login-gated DREAM frontend that matches today's
production backend. Replaces the stale March bundle. This is the "door" — the backend (engine,
auth, job pipeline) is done and verified; nothing for a user to open exists yet.

---

## 0. Context the executor MUST read first

- Backend is LIVE + verified at `https://dream.shieldstone.co` (US VPS, Caddy: `/api/*` →
  `localhost:8001`; everything else → static files at `/opt/dream-app/frontend`).
- **The old deployed frontend's SOURCE is gone** — only the compiled `dist/` survives
  (`shieldstone_os/shieldstone_acquisitions/efb-mini-app/frontend/dist/`). We are NOT recovering
  it; we are building a fresh, cleaner clone of its look, properly wired to the backend.
- Do NOT touch the backend except the ONE new endpoint specified in §6 (deal-list). Do NOT touch
  the vendored `underwriting-engine/` or locked contracts.
- Prior partial frontends (`gemini_ui/`, `src/` in the DREAM repo; `dream-vision-temp` on H:) are
  REFERENCE ONLY — Evan does not want them as the base. Build fresh. You MAY lift small,
  self-contained pieces (e.g. the `gemini_ui/api.ts` token-attaching client, the
  `AssumptionDashboard.tsx` recalc logic) since they already match the backend — but the app
  shell, login, and styling are new.

---

## 1. What this app is (one sentence)

A login-gated single-page React app where an authorized Shieldstone user logs in, sees their deal
pipeline, runs an autonomous chat-bot underwrite to a CP-1 review, and tweaks assumptions with a
live sensitivity dashboard — all against the validated DREAM backend.

---

## 2. Tech stack (decided — don't re-litigate)

- **Vite + React 18/19 + TypeScript** (matches the existing repo frontends; fast static build).
- **Tailwind CSS** via the standard PostCSS pipeline (NOT the CDN hack the gemini_ui used — set up
  `tailwind.config.js` + `postcss.config.js` properly so `npm run build` works clean).
- **recharts** for the sensitivity chart (already proven in gemini_ui).
- **lucide-react** for icons.
- **No state-management lib** needed — React context for auth/token + local state per screen.
- **No router lib required** — a small hash or `react-router-dom` (v6) is fine; pick react-router
  for clean URLs (`/login`, `/pipeline`, `/deal/:id`, `/underwrite`).
- Token stored in `localStorage` (key `dream_token`), attached as `Authorization: Bearer <token>`
  on every API call. (The `gemini_ui/api.ts` pattern is the reference.)
- Build output → a `dist/` deployable to `/opt/dream-app/frontend` (Caddy already serves it +
  SPA-fallbacks to `index.html`).

---

## 3. Brand + visual design (EFB look + Shieldstone polish)

The live EFB app ALREADY uses the Shieldstone palette — so this is refinement, not redesign.
Pull tokens from the brand kit (`reference_shieldstone-bd-brand`) + the live CSS.

### Color tokens (define as Tailwind theme colors)
| Role | Name | HEX |
|---|---|---|
| Primary | Deep Teal | `#005253` |
| Primary text / dark | Dark Slate | `#3C4856` (live app also uses `#171C26` for near-black) |
| Teal tint (hover/accent) | — | `#5EC4C0` |
| Secondary accent | Taupe | `#D4C4B0` |
| Background | Off-White | `#FAFAF8` |
| Surface tints | — | `#EAF3F3`, `#E8ECEC` (light teal panels from the live app) |
| Callout / CTA | Electric Blue | `#2B52EF` (use SPARINGLY — callouts only) |
| Success | — | green `#16A34A` |
| Warning | — | amber `#D97706` / `#FBBF24` |
| Danger | — | red `#DC2626` / `#F87171` |

### Typography (all Google Fonts — load in index.html)
- **Headlines / big numbers:** Playfair Display (600/700)
- **Sub-headers / labels:** Josefin Sans (600/700)
- **Body / data:** Noto Sans (400/500/600)
- **Mono (cells, IDs, JSON):** JetBrains Mono
- **NEVER:** Inter, Roboto, Arial, Cormorant, Outfit.

### Feel
Institutional, calm, data-dense but uncluttered. White/off-white surfaces, Deep Teal as the
structural color (top bar, primary buttons, active states), generous whitespace, Playfair for the
hero numbers (IRR/EM), restrained use of Electric Blue. Light + dark mode optional (the live app
had a dark toggle; nice-to-have, not v1-blocking).

---

## 4. The four surfaces (v1 scope — ALL in)

### 4.1 Login (`/login`) — the gate
- Centered card on the Off-White background, Shieldstone logo/wordmark at top.
- **Username + password fields** → `POST /api/auth/login` `{username, password}` →
  `{access_token, token_type, email}`. Store token, redirect to `/pipeline`.
- **"Sign in with Google" button** (Google Identity Services). On success, send the Google ID
  token as the bearer to `/api/me`; if 200, store that token + proceed. (Google works only for
  Google-account users; username/password is the universal path — Charles is password-only.)
  - Google Client ID: `954847212741-g00fssf9sa9mvglus6b61cc61pt3f7hj.apps.googleusercontent.com`
  - NOTE: Google sign-in needs the GSI script + the client ID; if Google setup isn't finished,
    the button can be present but the username/password path is the must-work one for v1.
- **Error states:** 401 → "Invalid username or password" inline; 403 → "Your account isn't
  authorized." Don't leak which.
- On app load, if a stored token still validates (`GET /api/me` → 200), skip login → `/pipeline`.
- On any API 401 anywhere in the app, clear the token + bounce to `/login`.

### 4.2 Pipeline / Deal list (`/pipeline`) — the home screen
- Top bar: DREAM wordmark, nav (Pipeline · New Underwrite), user email + logout.
- **A list/board of the user's deals** from the new `GET /api/deals` endpoint (§6). Each deal card
  shows: deal_name, routing (ACQ/EFB badge), status (draft/computed/gate_failed/...), updated_at,
  and headline IRR/EM if present in the spec.
- Clicking a deal → `/deal/:id` (the CP-1 review / detail view, §4.3's output).
- A prominent **"New Underwrite"** CTA → `/underwrite`.
- Empty state: "No deals yet — start your first underwrite."
- Group or filter by status (computed / awaiting input / gate_failed / draft) — simple tabs or
  pills. Match the live app's pipeline-board feel (it had a Pipeline page).

### 4.3 Chat-bot Underwrite (`/underwrite` → job lifecycle) — the core product
This drives the `/api/jobs` pipeline built + hardened today. The flow:
1. **Intake form:** deal_name, routing (default ACQ), and the critical inputs. At minimum capture
   the BL-17 three (purchase_price, hold_years, exit_cap). Optionally a free-text/notes + a
   `deal_docs` paste/upload area (the analysts read it). Keep it simple for v1.
2. **Submit** → `POST /api/jobs` `{intake_summary:{routing, deal_name, critical_inputs:{...}},
   deal_docs:{...}, owner, deal_name, routing}`. The call runs synchronously and can take
   **20s–4min** with live Kimi — show a clear "Underwriting… (this can take a few minutes)"
   progress state. (Do NOT add a short fetch timeout; allow several minutes. A spinner + phase
   text is enough for v1.)
3. **Handle the response status:**
   - `awaiting_input` → render the **blocking_questions** as a form (each has `id`, `field`,
     `question`, optional `options`). User answers → `POST /api/jobs/{job_id}/answer`
     `{question_id, answer}` per question; the LAST answer resumes the run (another wait). Loop
     until not `awaiting_input`. **This is the key UX the backend now supports** (missing engine
     inputs come back as questions instead of crashing).
   - `awaiting_cp1` → render the **CP-1 review** (§4.4).
   - `failed` → show the `error` (e.g. "blocking QA gates failed: [...]") cleanly.
4. A **Cancel** button → `POST /api/jobs/{job_id}/cancel` (best-effort).
5. Poll `GET /api/jobs/{job_id}` if you architect submit as fire-then-poll; v1 may rely on the
   synchronous response since the backend returns the final view. (Polling is the cleaner pattern
   if the executor wants it; either works.)

### 4.4 CP-1 Review + Assumption Dashboard (`/deal/:id`)
The payoff screen — combines the underwrite result with the live recalc dashboard.
- **Headline metrics** (from `headline_metrics`): IRR, Equity Multiple, CoC (stabilized), Exit
  Value — big Playfair numbers in Deep-Teal-bordered cards. (Esplanade truth: IRR 0.2221 /
  EM 2.733 / exit ~55.87M — use to sanity-check.)
- **Gate summary** (from `gate_summary` / spec.qa): show each gate's pass/fail (fee_bounds,
  unit_count, deal_identity, ...). RED gates prominent.
- **Open questions** (from `open_questions`): the LLM-inferred cells needing confirmation — a
  reviewable list (non-blocking at CP-1). Let the user see source = 'llm-inferred' vs 'cited'.
- **Assumption Dashboard** (lift the proven logic from `gemini_ui/AssumptionDashboard.tsx`):
  editable cards for the ACQ assumptions (bridge_loan/rate/io, refi_loan/rate/io, total_equity,
  exit_cap, sale_year, costs_of_sale, servicing_spread, refi_cost_pct). On edit (debounced 450ms),
  `POST /api/recalc` with the full `ACQRecalcRequest` shape → update headline metrics live. NEVER
  an LLM call.
- **Sensitivity grid:** pick a field (one of: exit_cap, refi_rate, bridge_rate, servicing_spread,
  costs_of_sale, total_equity, refi_loan, bridge_loan) + a metric (irr, equity_multiple,
  coc_stabilized, exit_value), sweep a range → `POST /api/recalc/sensitivity`
  `{base:ACQRecalcRequest, field, values:number[], metric}` → plot with recharts. (Backend rejects
  exit_cap ≤ 0 — handle the 400 gracefully.)
- (Optional v1.1) **Export to Excel** button → `POST /api/deals/{deal_id}/export` (exists).

---

## 5. Exact API contract (verified against the live backend)

Base: same-origin `/api`. Every call (except `/api/auth/login`) sends `Authorization: Bearer
<token>`. All bodies/returns are JSON, floats not Decimal.

| Endpoint | Method | Request | Returns | Auth |
|---|---|---|---|---|
| `/api/auth/login` | POST | `{username, password}` | `{access_token, token_type:"bearer", email}` | PUBLIC |
| `/api/me` | GET | — | `{email, name, picture}` | Bearer |
| `/api/deals` | GET | — (query: `?owner=&routing=&status=` optional) | `[{deal_id, deal_name, slug, routing, mode, status, owner, version, created_at, updated_at, headline_metrics?}]` | Bearer · **NEW, see §6** |
| `/api/jobs` | POST | `{intake_summary:{routing, deal_name, critical_inputs:{purchase_price, hold_years, exit_cap, ...}}, deal_docs:{}, owner, deal_name, routing, idempotency_key?}` | job view (below) | Bearer |
| `/api/jobs/{job_id}` | GET | — | job view | Bearer |
| `/api/jobs/{job_id}/answer` | POST | `{question_id, answer}` | job view | Bearer |
| `/api/jobs/{job_id}/cancel` | POST | — | job view | Bearer |
| `/api/recalc` | POST | `ACQRecalcRequest` (below) | `{headline_metrics:{irr, equity_multiple, coc_stabilized, coc_year1, exit_value, net_sale_proceeds, total_equity, noi_series[], dscr_series[], cash_flows[]}}` | Bearer |
| `/api/recalc/sensitivity` | POST | `{base:ACQRecalcRequest, field, values:number[], metric}` | `{field, metric, grid:[{value, metric, result}]}` | Bearer |
| `/api/deals/{deal_id}/export` | POST | (Excel template body) | xlsx | Bearer |

**Job view shape** (the response from submit/get/answer/cancel):
```
{ job_id, deal_id, status, phase, routing, mode, cancel_requested, error,
  open_questions: [OpenQuestion], blocking_questions: [OpenQuestion],
  // present ONLY when status == "awaiting_cp1":
  spec, headline_metrics, gate_summary }
```
**OpenQuestion shape:** `{id, field, question, current_value, source, options?, answered, answer}`
- `source`: `"cited"` (has a doc/API citation) or `"llm-inferred"` (judgment — confirm at CP-1).
- `options`: discrete choices when present (e.g. `["ACQ","EFB"]`) — render as a select.

**JobStatus values:** `submitted, routing, awaiting_input, analyzing, synthesizing, awaiting_cp1,
completed, failed, cancelled`. **DealStore status values:** `draft, computed, populated, exported,
archived` + `gate_failed` (a RED-gate run).

**ACQRecalcRequest** (all the assumption fields the dashboard edits; defaults reproduce Esplanade):
```
bridge_loan, bridge_rate, bridge_io_years, refi_loan, refi_rate, refi_io_years   (required-ish)
refi_amort_years=30, refi_year=2, total_equity=0.0, noi_series=[], exit_cap=0.06 (>0),
sale_year=7 (>=1), costs_of_sale=0.02, servicing_spread=0.0116, refi_cost_pct=0.02,
exit_on_forward_noi=true, years=10  (+ optional gpr/egi/opex/vacancy/debt_service series)
```
Esplanade seed values (for the demo/default deal) are in
`backend/tests/test_engine_boundary_esplanade.py` and `gemini_ui/AssumptionDashboard.tsx`
(`ESPLANADE_DEFAULTS`).

---

## 6. The ONE required backend addition: `GET /api/deals`

The Pipeline screen needs a deal-list endpoint that does NOT exist yet. `DealStore.list(owner,
routing, status)` already returns the records — just expose it.

- Add to a router (e.g. extend `routers/jobs.py` or a small new `routers/deals.py`; mount it
  auth-gated in `main.py` like the others): `GET /api/deals` →
  `[{deal_id, deal_name, slug, routing, mode, status, owner, version, created_at, updated_at,
  headline_metrics}]` where `headline_metrics` is pulled from each record's `spec.headline_metrics`
  (may be `{}` for un-computed drafts). Optional query filters `owner/routing/status` pass straight
  to `DealStore.list`.
- Add a test mirroring `test_jobs_api.py` (in-memory store, assert the list shape + filters).
- Keep it tiny + read-only. This is the only backend change in this PRD.

---

## 7. Cross-cutting requirements

- **Auth context:** one React context provides `{token, email, login(), logout()}`; a
  `<RequireAuth>` wrapper redirects to `/login` when no/invalid token. A single `apiFetch()` helper
  attaches the bearer + handles 401 globally (clear token → `/login`).
- **Loading + error states everywhere** — especially the multi-minute job submit (clear, honest
  "this can take a few minutes" copy, NOT a frozen spinner).
- **No secrets in the bundle.** Google Client ID is public (fine); no API keys, no JWT secret.
- **Accessibility basics:** labels on inputs, focus states, keyboard-submittable forms.
- **Responsive:** works on a laptop primarily; don't break on tablet. Mobile is not v1-critical.

---

## 8. Build + deploy (the executor runs this at the end)

1. `npm install && npm run build` → produces `dist/`. Confirm it builds CLEAN (the Tailwind
   PostCSS pipeline must be set up correctly — the gemini_ui's CDN-tailwind + leaky root
   postcss.config was the prior failure; do it properly).
2. Deploy: `scp -r dist/* root@72.61.5.208:/opt/dream-app/frontend/` (port 2222, key
   `~/.ssh/id_ed25519`). **Back up the current `/opt/dream-app/frontend` first**
   (`cp -a frontend frontend.bak-<stamp>`). Caddy already SPA-fallbacks to `index.html` — no Caddy
   change needed.
3. **Verify in a browser** (the whole point): open `https://dream.shieldstone.co` →
   - redirected to `/login`
   - log in as `evan` (password from chat) AND as `charles` / `<password redacted - credential with Evan/Charles>` → both reach
     the pipeline
   - run a New Underwrite with the sparse Esplanade intake (purchase_price 55000000, hold 7, exit
     0.06) → it should reach `awaiting_input` with bridge/refi questions → answer them → reach
     CP-1 with headline metrics
   - on the CP-1 dashboard, edit exit_cap → headline IRR updates live; run a sensitivity sweep →
     chart renders
4. Report what works + any gaps.

---

## 9. Out of scope for v1 (note, don't build)

- Async job queue (submit stays synchronous — backend gap, separate work).
- Password reset / lockout / sessions (the full Postgres auth mini-wave — designed, deferred).
- Excel export UI polish (endpoint exists; a simple button is enough).
- Multi-tenant / per-user data isolation beyond the existing allow-list + owner field.
- Recovering or reusing the old March bundle.

---

## 10. Acceptance criteria (the executor is done when)

1. `npm run build` produces a clean `dist/`, deployed to the VPS, served at the domain.
2. Login works for BOTH `evan` (password) and `charles` (password); Google button present.
3. An unauthenticated visitor is bounced to `/login`; a 401 anywhere bounces to `/login`.
4. The pipeline lists deals from `GET /api/deals` (new endpoint shipped + tested).
5. A full underwrite runs end-to-end in the browser: intake → awaiting_input questions → answer →
   CP-1 with headline metrics + gates + open questions.
6. The assumption dashboard recalcs live and the sensitivity grid plots.
7. The Shieldstone brand (Deep Teal / Off-White / Playfair-Josefin-Noto) is applied throughout.
8. Full backend test suite still green (the one new `/api/deals` test added).

---

### Appendix — paste-prompt to start the Opus execution session

> Read `c:\Users\evana\DREAM\docs\DREAM_FRONTEND_PRD_v1.md` fully, then build it. This is
> a fresh Vite+React+TS+Tailwind frontend for the DREAM app (local repo `c:\Users\evana\DREAM`),
> the real login-gated front door for the production backend at https://dream.shieldstone.co. Honor
> the exact API contract in §5, add the one `GET /api/deals` endpoint in §6 (with a test), apply the
> Shieldstone brand in §3, and build all four surfaces in §4. Do NOT touch the vendored
> underwriting-engine/ or the locked backend contracts. When built, deploy per §8 (back up the
> current frontend first) and run the browser verification. Report against the §10 acceptance
> criteria. Test accounts: evan (password in Evan's keeping) and charles / <password redacted - credential with Evan/Charles>.
