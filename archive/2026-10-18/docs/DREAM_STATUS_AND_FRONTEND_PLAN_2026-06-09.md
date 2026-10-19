# DREAM — Honest Status + Frontend Plan (2026-06-09)

Written because Evan reasonably asked: *"Haven't you been coding a frontend this whole time?
What did we even work on?"* This is the straight answer, plus a real plan so the next move is
deliberate, not piecemeal.

---

## 1. The honest answer: what today actually was

**Today was ~95% backend + a security review. There is no working frontend you can log into.**
That was never made clear to you in-session, and it should have been. Breakdown of the hours:

| Work | Visible to you? | Status |
|---|---|---|
| Wired the Kimi LLM into the job pipeline | No (server) | ✅ Done, live |
| Built username/password login system (backend) | No (server) | ✅ Done, live, tested |
| Built the assumption-dashboard page (`gemini_ui`) | **Only as repo code** | ⚠️ Committed, NEVER deployed, no login |
| Security review: found 10 bugs, fixed all, deployed | No (server) | ✅ Done, verified |
| Hardened the job pipeline (crash → ask-for-inputs) | No (server) | ✅ Done, live, tested |

So the one *frontend* thing built today (the dashboard) was committed to the repo but never
shipped and has no way to log in. Everything else was invisible server work. That's why you have
"no idea what UI is ready" — **because there isn't one.**

---

## 2. Why there's no working frontend (the root cause)

There are **THREE separate frontend codebases**, and none of them is a deployed, working,
auth-aware app:

1. **The LIVE site** (`dream.shieldstone.co`) — a compiled React bundle from **March 23**. Its
   source is NOT in our repo (only the built `.js` is on the server). It calls the OLD endpoints
   (`/api/intake`, `/api/underwrite`) and **never attaches a login token**. Since `/api/underwrite`
   now requires auth, this app's core function already returns 401. It was likely only ever used
   with auth turned off. **It is a dead end — a black box we can't cleanly edit.**

2. **`gemini_ui/`** (in the repo) — the newer app where I built today's assumption dashboard. It
   DOES have the token-attaching API client (`api.ts`) I wrote today. But it has **no login
   screen**, has **never been deployed**, and its production build is blocked by a stale
   Tailwind/PostCSS config (cosmetic, fixable).

3. **`src/`** (in the repo) — a THIRD frontend ("dream-vision-temp") with even more pages
   (Settings, DealDetail, etc.). Also never deployed, also no login.

**The core problem:** backend got built to production quality, but no single frontend was ever
(a) chosen as THE app, (b) given a login, and (c) deployed. Work spread across three half-apps.

---

## 3. What IS solid and working right now (the backend)

All verified live against `https://dream.shieldstone.co`:
- **Auth:** username/password login (`POST /api/auth/login` → token), Google-token support,
  allow-list, all the security fixes. Your account + Charles' account exist.
- **Deterministic engine:** `/api/recalc` + `/api/recalc/sensitivity` reproduce Esplanade exactly
  (IRR 0.2221 / EM 2.733). Auth-gated.
- **Chat-bot job pipeline:** `/api/jobs` runs live Kimi, pauses for missing inputs, stops at CP-1.
  Auth-gated.
- **All endpoints properly require a login.** No open holes.

The backend is genuinely production-ready. The *front door* is what's missing.

---

## 4. Accounts that exist (for whenever a login UI is ready)

| User | Login method | Notes |
|---|---|---|
| evan | password (+ Google once Test Users live) | password in earlier chat — move to password manager |
| charles | **password ONLY** | `gatewaymb.co` is NOT a Google domain (uses mxthunder mail), so Google sign-in will never work for Charles. Password: in chat — pass to him securely |
| fahd / alton / chuck | Google (once Test Users live) | no password accounts yet; can add if needed |

---

## 5. The plan — pick THE frontend, give it a login, ship it ONCE

Recommendation, in order of effort/payoff:

### Option A (recommended) — Ship `gemini_ui` as the real app
It already has today's dashboard + the token-aware API client. Work needed:
1. Fix the Tailwind/PostCSS build config (small).
2. Build **one** login screen (username/password form + optional Google button) that calls
   `/api/auth/login`, stores the token, and gates the app.
3. Make ALL the app's API calls go through the token-attaching client (api.ts pattern — already
   started).
4. Build it and deploy it to `/opt/dream-app/frontend` (replacing the March bundle), reload Caddy.
**Result:** a real app you log into and use (assumption dashboard + recalc + sensitivity). The
job/chat-bot pages would be follow-on work.
**Estimate:** one focused session.

### Option B — Standalone login + thin shell
Build just a login page + a minimal "it works" screen (shows your token authenticates, runs one
recalc). Proves the whole chain in a browser without committing to a full app. Half a session.
Good if you want to SEE auth work before investing in Option A.

### Option C — Decide product scope first
Before building, decide what the v1 app actually needs to DO for a user (just the chat-bot
underwrite? the assumption dashboard? the pipeline board?). The three half-frontends suggest the
product surface was never locked. A short scoping conversation prevents a 4th half-app.

---

## 6. What I recommend you do next session

1. **Pick Option A** (ship gemini_ui with a login) — it's the shortest path to a thing you can
   actually use, and it surfaces today's dashboard work.
2. Treat the March deployed app as retired (don't try to revive it — no source, token-blind).
3. Decide later whether the `src/` third frontend has anything worth salvaging, or delete it to
   end the confusion.

**One-line summary for you:** *The engine and the locks on the doors are done and tested. Nobody
has built the door itself yet. Next session = build one door (login + a real frontend) and hang
it.*
