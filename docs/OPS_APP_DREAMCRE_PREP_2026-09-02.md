# Operations Record — app.dreamcre.co Cutover — 2026-09-02

## Status

`https://app.dreamcre.co` is live with valid TLS and is the CRM's configured public URL. The server and worker now run the private DREAM-branded image built from `evanshields/dream-crm`. An authenticated browser session shows the DREAM title, favicon, workspace mark, Companies page, Deals page, and workflow navigation. The original `https://dreamcre.co` endpoint returns a temporary HTTP 302 redirect to `https://app.dreamcre.co`, preserving the deep-link path and query string. The pre-redirect nginx configuration is retained for rollback at `/etc/nginx/sites-available/dreamcre.pre-redirect-20260902T181641Z`.

The PostgreSQL container, Redis container, and Hermes environment were not changed during the branded-image deployment. Only the CRM server and worker were recreated.

## Confirmed live state

- Host: `srv1476276` through the `shieldstone-uk` SSH alias on port 2222.
- Twenty directory: `/opt/twenty-crm`.
- Public proxy: nginx, not Caddy.
- Twenty ingress: `127.0.0.1:3010` behind nginx.
- Twenty application: v2.32.0.
- Authentication: password only; Google, Microsoft, magic-link, and SSO are disabled.
- Analytics: disabled.
- AI models: none configured.
- Multi-workspace mode: disabled.
- Storage: local.
- Disk: approximately 45GB available at preflight.
- Memory: approximately 3.9GB available at preflight.
- Swap: 4GB configured; approximately 2.4GB was in use. Treat sustained swap pressure as a resize signal.

## Image identity

The live Compose file used floating tags. Immutable identities recorded from the running artifacts:

- DREAM server/worker: `ghcr.io/evanshields/dream-crm@sha256:6d06ccd23cce5a76bac89b49c53fda22d0d0ac9d57e93d8e8c0f315fef1b0794`
- Rollback server/worker: `twentycrm/twenty@sha256:cb80b05bc2619a88a3a83293f45f2be495a55ac77a90946fa1f7d85f0b7fde24`
- PostgreSQL: `postgres@sha256:e17e86066e5ef83e0952a9347f5c792b7ece00972e2aa787a6986f471b3dd3d5`
- Redis: `redis@sha256:344e3945a0b431c8ff1eecd58c5573538126bd756f02fc7e218ddf1fc2546366`

The DREAM server and worker run through `/opt/twenty-crm/docker-compose.pinned.yml` at the recorded DREAM digest. PostgreSQL and Redis were deliberately left running without recreation. At live verification, the server was healthy, the worker was running, and both had zero restarts on the new image.

## Backups and hardening completed

- Created a root-only pre-cutover backup directory on the UK VPS.
- Generated a PostgreSQL custom-format dump.
- Verified the dump with `pg_restore --list`.
- Database dump SHA-256: `842bae4fcdcbce56b9eacfee1d7f795e240f9e57f45bc34b9f79c418c6e81ac1`.
- Copied the dump off the VPS and confirmed the same checksum.
- Backed up the live Compose, nginx, and environment configuration on the VPS.
- Corrected `/opt/twenty-crm/.env` from mode 0644 to root-owned 0600.
- Installed and enabled `twenty-crm-backup.timer` for a verified nightly custom-format dump at 03:15 local time with a small randomized delay.
- The backup service validates every dump with `pg_restore --list`, writes a SHA-256 receipt, and retains 14 days on-box.
- Ran the backup service once successfully; its checksum check passed.
- Ran a fresh pre-deployment database backup: `/var/backups/twenty-crm/twenty-20260903T040353Z.dump` (1,002,226 bytes).
- Fresh database dump SHA-256: `1fd6c0ff4a5d7e7e0737f00a6c44389f77078ff1e1fed04a0efb153e7612d0ec`.
- Copied that dump to `C:/Users/evana/DREAM-backups/twenty-crm/20260903T040353Z/twenty-20260903T040353Z.dump` and confirmed the same checksum off-box.
- Saved fresh root-only configuration copies under `/root/twenty-crm-predeploy/20260903T040414Z` and an immediately pre-image-change Compose copy at `/root/twenty-crm-predeploy/20260903T043000Z-docker-compose.pinned.yml`.

## Source/fork preparation

- Refreshed the Twenty audit at `shieldstone_operations/third-party-audits/2026-09-02-twenty-crm.md`.
- Twenty publishes no `v2.32.0` Git tag, and the Docker image has no source-revision label.
- Strongest source candidate: `2711d27e9276fff05ecc611c8cd43a35cd5c4dbd`, the last `main` commit before the image build timestamp. It contains the 2.32.0 upgrade commands and SDK references. This is an inference, not a byte-proven mapping.
- Created the private repository `https://github.com/evanshields/dream-crm` and retained `twentyhq/twenty` as a fetch-only upstream; upstream push is disabled locally.
- Prepared the clean local worktree at `C:/tmp/dream-crm`. The DREAM branding commit is `ca2969e350`, and the pinned image-workflow commit is `b81cfc9a33`.
- The DREAM repository retains Twenty's AGPL-3.0 license and upstream history. It is intentionally separate from `evanshields/DREAM`; no Twenty source is copied into the DREAM application repository.
- The pinned GitHub Actions build passed: `https://github.com/evanshields/dream-crm/actions/runs/33712738756`.
- The workflow publishes an amd64 image with SBOM and provenance and records the immutable digest used for deployment.
- The private GHCR package is `ghcr.io/evanshields/dream-crm`. The VPS package credential is stored only in root's Docker configuration, with directory mode 0700 and file mode 0600.
- All 46 inherited and DREAM-specific GitHub Actions workflows are active; none are disabled.

## Cutover completed

- Added the Spaceship A record `app.dreamcre.co` to `187.124.113.118` and verified it against the authoritative nameserver and the public resolver.
- Enabled the prepared nginx site and passed `nginx -t` before reload.
- Issued and installed a Let's Encrypt certificate for `app.dreamcre.co`; automatic renewal is configured. The initial certificate expires on 2026-12-01.
- Verified `https://app.dreamcre.co/` returns HTTP 200.
- Changed Twenty's `SERVER_URL` to `https://app.dreamcre.co`.
- Recreated only the Twenty server and worker on the pinned Twenty image digest.
- Before enabling the root redirect, verified the server was healthy, the worker was running, and both hostnames returned HTTP 200.
- Verified the new hostname renders the password-login screen in Chrome and the Codex in-app browser.
- Confirmed a real authenticated browser session reaches the All Companies route at `app.dreamcre.co` with no browser-console errors.
- Changed `dreamcre.co` to return a temporary HTTP 302 redirect to `app.dreamcre.co`, preserving the requested deep-link path and query string.
- Confirmed the CRM remains healthy at `app.dreamcre.co` after the redirect change.
- Retained the rollback configuration at `/etc/nginx/sites-available/dreamcre.pre-redirect-20260902T181641Z`.

## DREAM image deployment completed — 2026-09-03

- Pulled the exact private image digest before changing the live Compose file.
- Backed up the live Compose file immediately before replacing the server/worker image reference.
- Recreated only `server`, waited for a healthy `/healthz`, and then recreated only `worker`.
- Confirmed the original PostgreSQL container ID `aa07de8a5378` and Redis container ID `09181b601ead` remained running and healthy.
- Confirmed the new server and worker use digest `sha256:6d06ccd23cce5a76bac89b49c53fda22d0d0ac9d57e93d8e8c0f315fef1b0794` with zero restarts.
- Confirmed public `/healthz`, `/.well-known/api-catalog`, and `/.well-known/mcp/server-card.json` return HTTP 200.
- Confirmed an unauthenticated MCP initialization request returns HTTP 401, preserving the fail-closed boundary.
- Confirmed `dreamcre.co` still returns HTTP 302 to `https://app.dreamcre.co/`.
- Confirmed the live favicon SHA-256 is `336973e59075d718d4cadaf0473588e2b020930587605a39a00391f6221ba576`, byte-identical to the reviewed DREAM asset.
- Confirmed the authenticated Companies and Deals routes render with DREAM branding and no browser-console errors. Workflow navigation renders both existing CRM workflows as Active.
- Re-ran the DREAM application gates after documenting the deployment: 403 tests passed and 20 skipped; frontend TypeScript checking and the production build passed. The existing large-chunk advisory remains non-blocking.

### Image rollback

If the branded image must be rolled back, do not recreate PostgreSQL or Redis:

```bash
cd /opt/twenty-crm
cp /root/twenty-crm-predeploy/20260903T043000Z-docker-compose.pinned.yml docker-compose.pinned.yml
docker compose --env-file .env -f docker-compose.pinned.yml up -d --no-deps --force-recreate server
curl --fail http://127.0.0.1:3010/healthz
docker compose --env-file .env -f docker-compose.pinned.yml up -d --no-deps --force-recreate worker
```

The restored Compose file pins the prior Twenty image digest recorded above. Verify the public health endpoint and authenticated CRM after rollback.

## Remaining acceptance checks

1. Evan confirms that the intentionally empty Companies and Deals views match the current expected CRM data.
2. Exercise a reversible test record and sample file upload before real deal intake begins.
3. Verify an authenticated API call, authenticated MCP call, and webhook delivery when their production credentials and target workflow are defined.

## Automation incident note

The 18:37 heartbeat was rendered only as `suggested_create` after a `DTSTART` validation failure. It was not accepted or persisted, and therefore never ran. Prevention rule: every future schedule must be verified as active and persisted after creation; an unaccepted `suggested_create` is not a running schedule.

The replacement task-attached heartbeat, `continue-dream-crm-overnight`, is persisted and ACTIVE at 23:30, 00:30, 01:30, 02:30, 03:30, 04:30, and 05:30 Eastern every night. Its prompt resumes only the first incomplete step, avoids duplicate work when another run is active, and makes no changes when the plan is complete. Failure-only notifications are enabled so a capacity or execution failure is visible.

## Risks still open

- The application currently connects to PostgreSQL as the bootstrap superuser. Migrate to a dedicated non-superuser role in a separate maintenance window.
- The server is already using substantial swap. Do not add a source build or heavy CI workload to this host.
- The exact mapping from Twenty's earlier public image to upstream source remains an inference. The deployed DREAM image is reproducibly tied to DREAM CRM commit `b81cfc9a33` by the pinned build workflow and image provenance.
- Google/Microsoft OAuth and email/calendar integration remain unconfigured.
- Public API/MCP discovery and fail-closed MCP authentication are verified. Authenticated MCP execution and webhook delivery still need a defined production credential and test target.
- Automated off-box backup transfer is not configured; one verified off-box copy exists. Choose a durable encrypted destination before real deal data accumulates.
