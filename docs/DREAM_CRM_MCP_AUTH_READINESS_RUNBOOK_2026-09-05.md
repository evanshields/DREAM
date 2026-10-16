# DREAM CRM MCP/Auth Readiness Runbook

**Date:** 2026-09-05  
**Scope:** authenticated access to the Twenty-derived CRM at `app.dreamcre.co`, including MCP access for Claude Code and the DREAM agent.  
**Status:** production MCP transport and OAuth discovery verified 2026-09-05; role hardening, partner schema, SMTP, and Google sign-in configuration remain to be completed.

## 1. Safety boundary

The CRM is the sales book. Twenty owns Companies, People, Opportunities/Deals, sales stage, email, meetings, tasks, notes, workflows, and MCP. DREAM owns the canonical `underwrite-spec.json`, uploaded underwriting documents and hashes, job state, deterministic engine results, QA-gate receipts, and CP-1 review.

The CRM/MCP integration may read and write CRM records and safe references (for example, a stable DREAM deal ID or deep link). It must never author or overwrite:

- the canonical deal specification or assumptions;
- deterministic headline metrics;
- QA-gate verdicts or receipts;
- CP-1 decisions or reviewer audit events.

If identity, authorization, linking, DREAM, or Hermes is unavailable, stop and show an unavailable/blocked state. Do not guess, silently retry a write, or display stale underwriting values as current. No secret belongs in browser code, logs, markdown, shell history, or chat.

## 2. What is verified vs. still a gate

Verified in production and in the deployed Twenty source:

- Product hostname: `https://app.dreamcre.co`; `dreamcre.co` is a temporary redirect during the transition.
- MCP endpoint: `POST https://app.dreamcre.co/mcp`, using MCP JSON-RPC over Streamable HTTP with optional SSE responses.
- An unauthenticated MCP request returns `401` and OAuth discovery metadata. OAuth discovery is live at `/.well-known/oauth-protected-resource/mcp` and `/.well-known/oauth-authorization-server`.
- OAuth supports authorization code + PKCE, refresh tokens, and dynamic client registration. API keys are also supported, but individual OAuth sessions are safer for team members because they inherit each person's CRM role.
- Product hostname: `https://app.dreamcre.co`; `dreamcre.co` is a temporary redirect during the transition.
- Twenty deployment: UK VPS, `/opt/twenty-crm`; observed version v2.32.0 in the cutover handoff.
- The CRM credential must be role-scoped. Browsers must not receive long-lived Twenty, DREAM, Hermes, or Tailscale credentials.
- The first underwriting vertical slice remains contract-blocked until identity, opportunity-to-deal-link, and Hermes conversation contracts are written.

Not yet verified by this repository and therefore not to be invented here:

- the final role/field grants for each team persona and service account;
- the exact data model IDs and generated tool names after the partner schema is created;
- the exact Google OAuth client and SMTP provider credentials;
- the final mapping from a Twenty user to a DREAM user/role.

Do not invent an MCP tool name or a GraphQL payload. Use MCP's `learn_tools` discovery after the role and data model are configured.

## 3. Access and role model

### CRM roles before team MCP access

The DREAM auth design defines three roles:

| Role | Intended access | MCP posture |
|---|---|---|
| DREAM CRM Operator | Read/create/update Companies, People, Deals, Partner Engagements, Notes, and Tasks | No delete, settings, roles/users, workflows, applications, AI configuration, or API/MCP administration. Disable All Actions Access. |
| DREAM CRM Viewer | Read-only access to the same business objects | No create, update, delete, or administration. |
| DREAM MCP Importer | Future unattended upsert service only | Separate expiring API key, no delete/settings access, stored only in LastPass or a root-owned VPS secret file. |

Twenty's object/field permissions remain the enforcement layer for CRM records. Keep the native `LAYOUTS` permission off Operator and Importer roles: it enables dashboard creation but also destructive widget operations. The service credential used by MCP must be narrower than a human administrator and must be revocable, expiring, and attributable to one integration.

### Safe CRM object model

| Object | MCP treatment | Explicit exclusion |
|---|---|---|
| Companies | Every partner organization. Add `Organization Type` multi-select: Capital Partner, Impact Partner, Sponsor/Developer, Broker/Intermediary, Service Provider, Internal. Add only useful partner fields: status, geography, capital strategy, check-size range, and impact themes. | No underwriting authority or secret fields |
| People | Read/create/update approved identity/contact/role fields | No password, OAuth token, or private credential fields |
| Deals/Opportunities | Add a unique `DREAM Deal ID`. Read/update sales stage, partner metadata, stable DREAM link/deep link. | Never write spec, assumptions, metrics, gates, CP-1, or engine outputs as authority |
| Partner Engagements | Create a custom junction object connecting one Deal to one Company, optionally with a primary Person. Fields: partner role/type, engagement stage, proposed/committed amount, terms or impact summary, next step, owner, and unique import key. | Never treat activity as underwriting evidence without provenance. |

Use idempotency for link creation and webhook replay. A repeated request must resolve to one stable DREAM deal link, not create a duplicate deal or run. CRM stage changes may request/link work (for example, stage `Underwriting`), but cannot bypass DREAM's `AWAITING_CP1` hard stop.

## 4. Authentication setup

### A. Twenty and hostname preflight

1. Confirm the running host, container/image digest, source commit/tag, application version, and `/opt/twenty-crm` deployment without printing environment values.
2. Confirm `app.dreamcre.co` TLS, redirect behavior, trusted origins, secure-cookie scope, and generated-link base.
3. Confirm the production endpoint remains healthy: `POST https://app.dreamcre.co/mcp` must fail closed when unauthenticated and publish its OAuth discovery metadata.
4. Create a disposable, reversible CRM test target. Never test a mutation against a live partner or deal.

### B. Google OAuth

Twenty already contains the Google sign-in implementation. Create a Google Cloud **Web application** OAuth client, use `https://app.dreamcre.co/auth/google/redirect` as the exact redirect URI, and use `https://app.dreamcre.co` as the authorized origin if Google requests one. Use Internal consent only if every user is in the managed Workspace; otherwise use External and add test users during rollout.

An authorized VPS operator must store the client ID and secret in LastPass/root-owned `0600` configuration and set `AUTH_GOOGLE_ENABLED=true`, `AUTH_GOOGLE_CLIENT_ID`, `AUTH_GOOGLE_CLIENT_SECRET`, and `AUTH_GOOGLE_CALLBACK_URL=https://app.dreamcre.co/auth/google/redirect`. Keep Gmail/calendar integration disabled for now; it is separate from sign-in.

### C. SMTP for invites and reset

Email/password and forgot-password flows already exist, but production currently uses `EMAIL_DRIVER=LOGGER`. That means reset links are written to server logs instead of delivered. Do not invite a team or test password reset until real SMTP is configured.

Configure `EMAIL_DRIVER=SMTP`, `EMAIL_FROM_ADDRESS`, `EMAIL_FROM_NAME`, `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, `EMAIL_SMTP_USER`, `EMAIL_SMTP_PASSWORD`, `EMAIL_SMTP_NO_TLS`, and `IS_EMAIL_VERIFICATION_REQUIRED=true` only in a root-owned `0600` secret file or approved vault injection. Validate:

- invite and reset mail are sent from the approved domain;
- links use `https://app.dreamcre.co` and expire; tokens are single-use;
- reset/invite requests return the same generic response for known and unknown emails;
- successful reset revokes existing sessions;
- SMTP credentials never appear in process listings, logs, browser responses, or this repository.

## 5. Claude Code connection (dry run first)

Run these after roles are hardened. OAuth is the preferred team path; do not put an API key in a project `.mcp.json` or shared dotfile.

```powershell
claude mcp add --transport http --scope user dream-crm https://app.dreamcre.co/mcp
claude mcp login dream-crm
claude mcp list
```

Then use `learn_tools` to discover the role-scoped tools and run one disposable read-only lookup. Remove the local client entry and revoke a disposable credential after testing.

## 6. Permissions validation

Record a redacted receipt containing timestamp, client identity, server URL, credential ID suffix, role, and result—never the token.

1. Unauthenticated request: rejected (`401` or the documented equivalent).
2. Expired/revoked credential: rejected; no CRM mutation occurs.
3. Viewer: can read approved CRM objects; create/update/delete and admin tools are rejected.
4. Analyst: can perform one disposable Company/Person/Deal/Partner Engagement operation within the approved scope; cannot touch spec, metrics, gates, or CP-1.
5. Admin: administrative actions work only if explicitly granted; ordinary MCP access remains least-privilege.
6. Cross-user/strict-ownership behavior matches the configured v1 policy; never infer ownership from a display name.
7. Repeated opportunity-to-deal-link request is idempotent.
8. Webhook replay is rejected or idempotently ignored.
9. DREAM/Hermes outage returns an honest blocked/unavailable result and leaves the CRM record unchanged.
10. Browser inspection and server logs show no service credential.

Any failed check is a hard stop. Revoke the test credential, preserve the redacted evidence, and fix the contract/configuration before retrying.

## 7. Phased rollout and rollback

**Phase 0 — observe:** pin the CRM image/digest, verify backups/restore, inspect live MCP/auth configuration, and write the missing identity/link/conversation contracts.

**Phase 1 — read-only:** connect one role-scoped credential; test identity, Companies, People, Deals, and Partner Engagement reads against disposable/non-sensitive data. No production writes.

**Phase 2 — narrow writes:** enable only approved CRM fields and one idempotent link/deep-link mutation. Keep underwriting status, metrics, gates, and CP-1 read-only mirrors.

**Phase 3 — server-side bridge:** add the identity-aware DREAM↔Twenty bridge and Hermes conversation only after conversation IDs, allowed deal context, timeout/cancellation, audit, and unavailable states are specified.

**Phase 4 — production pilot:** one analyst, one real week of partner activity, continuous audit/backup monitoring, and a tested credential-revocation path. Expand only after the acceptance gates in the CRM execution plan pass.

Rollback is: revoke the MCP credential; disable the MCP/bridge integration; restore the prior canonical URL/nginx configuration if hostname behavior is involved; restart the pinned prior deployment; verify login and record access. A hostname rollback normally does not require database restoration. Restore data only if the database itself changed or was corrupted.

## References

- `docs/DREAM_PRD_V4.md` — authority boundaries, topology, phases, and locked invariants.
- `docs/DREAM_CRM_PRODUCT_EXECUTION_PLAN_2026-09-02.md` — CRM data authority, contract gates, and rollout acceptance criteria.
- `docs/HANDOFF_APP_DREAMCRE_CO_2026-09-02.md` — hostname cutover, planned MCP URL, backup/rollback checks.
- `backend/WAVE_F_FULL_AUTH_DESIGN.md` — DREAM role, allowlist, invite/reset, lockout, and revocable-session design.
