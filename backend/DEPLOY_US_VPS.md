# Wave A0 — US VPS migration + nginx + OAuth (ops runbook + rollback)

Migrate the DREAM API from the **UK VPS** (`/opt/dream-app`, where it ran as PM2 `dream-api` and was
found stopped) to the **US VPS** (`72.61.5.208`, co-resident with OpenBrain + the future Shieldstone
Hermes). The UK instance stays intact and re-startable until the US smoke test passes.

> This file is the runbook + rollback plan (an A0 acceptance criterion). The live migration runs on
> the VPS hosts and needs Evan's SSH session / sign-off — do not run it unattended.

## Pre-flight (collision check — the named A0.1 risk)
On the US VPS, confirm no collision with OpenBrain before touching anything:
- PM2 name: `pm2 list` — there must be no existing `dream-api`. (Pick `dream-api` only if free.)
- Port: `ss -ltnp | grep 8001` — port **8001** must be free. If taken, pick a free port and update
  `ecosystem.config.js` + the nginx proxy block together.
- Env: the US box's OpenBrain env must not export a conflicting `FRONTEND_URL` / `PORT`.

## Migrate
1. **Ship the code** (the repo is the source of truth now — backend lives in `evanshields/DREAM`):
   on the US VPS, `git clone` / pull the `wave-a-foundation` branch into `/opt/dream-app`.
2. **Python 3.13 venv** (matches the pinned `requirements.txt` — has wheels):
   `python3.13 -m venv venv && venv/bin/pip install -r backend/requirements.txt`
3. **Env**: create `backend/.env` from `.env.example`. For production set `GOOGLE_CLIENT_ID`
   (this flips `auth_dep` to enforce OAuth — A0.2) and `ALLOWED_EMAILS=evan@shieldstone.co,...`.
   Set `KIMI_API_KEY` for the chat endpoints. Set `DREAM_DB_PATH` to a persistent path for the
   DealStore SQLite file.
4. **PM2**: `pm2 start ecosystem.config.js` (cwd `/opt/dream-app/backend`, uvicorn `:8001`). Confirm
   `pm2 logs dream-api` is clean. `pm2 save`.
5. **Build + ship the frontend**: build `gemini_ui` (`npm ci && npm run build`) and place `dist/`
   where nginx serves it (e.g. `/var/www/dream`). (The UK box had only a compiled build and **no
   public nginx route** — this is the first-ever public routing of the SPA.)
6. **nginx** (net-new server/location, not a copy): proxy `/api/` to `127.0.0.1:8001` and serve the
   SPA with SPA fallback:
   ```nginx
   location /api/ { proxy_pass http://127.0.0.1:8001; proxy_set_header Host $host;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_read_timeout 120s; }
   location /dream { alias /var/www/dream; try_files $uri $uri/ /dream/index.html; }
   ```
   `nginx -t && systemctl reload nginx`. Add the TLS cert (certbot) for the chosen hostname.

## Smoke test (the A0.1 / A0.2 acceptance gate)
On the US instance, all must pass before cutting over:
1. `curl -s http://127.0.0.1:8001/api/health` → `{"status":"ok"}`.
2. **Esplanade underwrite** through the API: `POST /api/recalc` with the Esplanade payload →
   IRR ≈ 0.2251 (±2%), exit ≈ 55,870,669 (±0.5%). (Same payload as
   `backend/tests/test_recalc_no_llm.py`.)
3. **OAuth**: with `GOOGLE_CLIENT_ID` set, `GET /api/me` with no token → **401**; with a valid
   allow-listed Google token → 200.
4. Frontend loads behind nginx over HTTPS and reaches `/api/health`.

## Rollback (one command, documented AC)
The UK instance is untouched and re-startable; nothing is deleted there until the US smoke test
passes. To roll back:
1. **US**: `pm2 stop dream-api` (and revert the nginx `/api` + `/dream` blocks: restore from
   `/etc/nginx/backups/…` then `nginx -t && systemctl reload nginx`).
2. **UK**: `ssh shieldstone-uk "pm2 start dream-api"` — back to the prior known-good state.
3. DNS (if a hostname was cut over): repoint to the UK box.

Keep the UK `/opt/dream-app` for one release cycle after a clean US cutover, then archive.
