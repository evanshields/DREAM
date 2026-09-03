# Operations Record — app.dreamcre.co Cutover — 2026-09-02

## Status

`https://app.dreamcre.co` is live with valid TLS and remains Twenty's configured public URL. Evan authenticated successfully and reached the existing All Companies route at the new hostname. The original `https://dreamcre.co` endpoint now returns a temporary HTTP 302 redirect to `https://app.dreamcre.co`, preserving the deep-link path and query string. The CRM remains healthy at `app.dreamcre.co`; the pre-redirect nginx configuration is retained for rollback at `/etc/nginx/sites-available/dreamcre.pre-redirect-20260902T181641Z`.

The database schema, PostgreSQL container, Redis container, and Hermes environment were not changed.

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

- Twenty server/worker: `twentycrm/twenty@sha256:cb80b05bc2619a88a3a83293f45f2be495a55ac77a90946fa1f7d85f0b7fde24`
- PostgreSQL: `postgres@sha256:e17e86066e5ef83e0952a9347f5c792b7ece00972e2aa787a6986f471b3dd3d5`
- Redis: `redis@sha256:344e3945a0b431c8ff1eecd58c5573538126bd756f02fc7e218ddf1fc2546366`

The Twenty server and worker now run through `/opt/twenty-crm/docker-compose.pinned.yml` at the recorded Twenty digest. PostgreSQL and Redis were deliberately left running without recreation during the hostname cutover.

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

## Source/fork preparation

- Refreshed the Twenty audit at `shieldstone_operations/third-party-audits/2026-09-02-twenty-crm.md`.
- Twenty publishes no `v2.32.0` Git tag, and the Docker image has no source-revision label.
- Strongest source candidate: `2711d27e9276fff05ecc611c8cd43a35cd5c4dbd`, the last `main` commit before the image build timestamp. It contains the 2.32.0 upgrade commands and SDK references. This is an inference, not a byte-proven mapping.
- Prepared a clean local worktree at `C:/tmp/dream-crm` on branch `dream-v232-base` at that commit.
- No dependency install, build, or source execution has occurred.
- GitHub authentication is available; `evanshields/dream-crm` does not yet exist. Do not publish the source until repository visibility and licensing are deliberately selected.

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

## Remaining acceptance checks

1. Evan confirms that the expected companies and deals are present in the authenticated session.
2. Verify fields, views, settings, file handling, generated links, API, MCP, and webhook behavior under the new hostname.

## Automation incident note

The 18:37 heartbeat was rendered only as `suggested_create` after a `DTSTART` validation failure. It was not accepted or persisted, and therefore never ran. Prevention rule: every future schedule must be verified as active and persisted after creation; an unaccepted `suggested_create` is not a running schedule.

The replacement task-attached heartbeat, `continue-dream-crm-overnight`, is persisted and ACTIVE at 23:30, 00:30, 01:30, 02:30, 03:30, 04:30, and 05:30 Eastern every night. Its prompt resumes only the first incomplete step, avoids duplicate work when another run is active, and makes no changes when the plan is complete. Failure-only notifications are enabled so a capacity or execution failure is visible.

## Risks still open

- The application currently connects to PostgreSQL as the bootstrap superuser. Migrate to a dedicated non-superuser role in a separate maintenance window.
- The server is already using substantial swap. Do not add a source build or heavy CI workload to this host.
- The exact source-to-image mapping is not cryptographically provable from Twenty's published metadata.
- Google/Microsoft OAuth and email/calendar integration remain unconfigured.
- MCP and webhook behavior at the new hostname has not yet been authenticated and verified.
- Automated off-box backup transfer is not configured; one verified off-box copy exists. Choose a durable encrypted destination before real deal data accumulates.
