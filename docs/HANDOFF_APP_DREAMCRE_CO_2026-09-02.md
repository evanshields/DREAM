# Claude Code Handoff — Move DREAM CRM to app.dreamcre.co

## Objective

Move the existing self-hosted Twenty CRM from `dreamcre.co` to `app.dreamcre.co` without data loss, while keeping `dreamcre.co` as a temporary redirect until the public landing page is built.

This is a VPS/DNS/deployment task owned by Claude Code. Do not change the DREAM underwriting API or Hermes profile as part of this cutover.

## Known state

- DNS provider: Spaceship (`launch1.spaceship.net`, `launch2.spaceship.net`).
- Current Twenty deployment: UK VPS, `/opt/twenty-crm`.
- Current observed application version: v2.32.0.
- Current product URL: `https://dreamcre.co`.
- Target product URL: `https://app.dreamcre.co`.
- Future root behavior: public landing page. Interim root behavior: redirect to the app.
- Planned MCP URL after cutover: `https://app.dreamcre.co/mcp`.

Treat the server configuration and exact environment-variable names as live facts to inspect, not values to infer from this document.

## Guardrails

- Take timestamped backups before every mutation.
- Pin exact versions/digests; never deploy `latest`.
- Secrets stay in root-owned `0600` files and never enter the repo, command output, or chat.
- Do not touch Mission Driven's Twenty deployment on the US VPS.
- Do not modify the existing `avery` Hermes profile.
- Do not expose Tailscale or service credentials to browser code.
- Preserve a tested rollback to the existing hostname.
- Do not combine this hostname cutover with a Twenty version upgrade.

## Preflight

- Confirm the exact UK host and `/opt/twenty-crm` deployment.
- Record the running container images, immutable digests, application version, Compose configuration, nginx configuration, health, disk, memory, and database size.
- Identify every configured public/base/server URL variable from the live deployment and the version-pinned Twenty documentation.
- Inventory callback and integration URLs:
  - Login and invite/reset links.
  - Google/Microsoft OAuth, if configured.
  - Email/calendar synchronization.
  - Webhooks.
  - MCP.
  - Any API clients or allowed origins.
- Confirm `app.dreamcre.co` is unused.
- Lower DNS TTL in advance if the current provider permits it.

## Backups

- Create a timestamped Postgres dump and verify that it is non-empty and readable.
- Copy the dump off the UK VPS.
- Back up Compose, nginx, and environment configuration without printing secrets.
- Record the exact rollback commands and prior DNS values.
- If restore has not been proven, prove it in an isolated database before cutover.

## Cutover sequence

1. Add the `app` DNS record in Spaceship pointing to the current CRM ingress.
2. Verify public DNS resolution from more than one resolver.
3. Add `app.dreamcre.co` to nginx and obtain a valid TLS certificate.
4. Update Twenty's canonical/public URL configuration using the exact variables supported by the deployed version.
5. Update trusted origins, secure-cookie scope, redirect URLs, callback URLs, webhook destinations, MCP URL, and generated-link bases as applicable.
6. Restart only the Twenty stack using the normal deployment method.
7. Keep the original root hostname serving the app during initial verification if the version cannot safely support both names; otherwise make it a temporary redirect only after the target passes.
8. Once verified, configure `dreamcre.co` as a temporary redirect to `https://app.dreamcre.co` while preserving path and query string where safe.

## Verification

- TLS is valid for `app.dreamcre.co`.
- Login, logout, invite, password reset, and session refresh work.
- Existing workspace, users, objects, fields, views, workflows, and records are unchanged.
- Companies, People, Deals, Tasks, Notes, Dashboards, and Settings load.
- Creating and editing a disposable test record works; remove it only with explicit confirmation and after verification.
- Email/calendar integration works or remains honestly marked unconfigured.
- REST/GraphQL clients use the new base URL.
- MCP connects at the new endpoint using a role-scoped credential.
- Webhook signing and delivery work at the new endpoint; replay is rejected or idempotent.
- Browser cookies and CORS do not depend on the old hostname.
- `dreamcre.co` redirects to the app without a loop.
- Logs contain no secrets or repeated errors.
- Memory and disk remain healthy.

## Rollback

Rollback immediately if authentication, data access, MCP, webhooks, or generated links fail and cannot be corrected within the maintenance window:

1. Restore the prior canonical URL configuration.
2. Restore the prior nginx configuration.
3. Restore the prior DNS behavior.
4. Restart the pinned prior deployment.
5. Verify login and record access on `dreamcre.co`.
6. Restore the database only if the database itself changed or became corrupted; a hostname rollback should not normally require data restoration.

## Evidence to return

- Backup identifiers and off-box-copy confirmation, without secret paths or values.
- Exact image tag and digest.
- Exact source commit/tag corresponding to the running image.
- DNS and TLS verification.
- Authentication and primary-screen smoke results.
- MCP and webhook verification.
- Final nginx/Twenty configuration diff with secrets redacted.
- Rollback status and any remaining operational risks.
