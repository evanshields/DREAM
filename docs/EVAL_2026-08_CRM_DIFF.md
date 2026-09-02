# CRM Diff: DREAM App Rail vs Twenty (dreamcre.co) — 2026-08-31

Method: Playwright walkthrough of the live DREAM app as a logged-in user (screenshots in `eval_2026-08_screenshots/`), plus a version-pinned feature profile of the dreamcre.co Twenty instance (v2.32.0, confirmed via its public client-config) built from its release changelog and docs. Twenty's in-app UI was not screenshotted (no login provided); its claims are docs-based and tagged in the source research.

## Bottom line

These are not two CRMs. DREAM has a **deal-execution rail** (who's on this deal, what's due, what happened) welded to the underwriting engine. Twenty is a **full sales system of record** (companies, people, stage pipelines, email, permissions, API). They overlap on almost nothing except tasks and notes, which is why the "DREAM-on-Twenty" split (Twenty owns the sales book, DREAM owns deal execution + numbers) is architecturally natural rather than a compromise.

## Side-by-side

| Capability | DREAM app today (observed live) | Twenty v2.32.0 (docs/changelog) |
|---|---|---|
| People | Global directory, 8 seeded; name + optional email ONLY (no phone/title/tags) | Full People object, ~19 field types incl. phones/emails/address, custom fields |
| Companies | None in practice (API accepts `kind=company`, zero records, no UI; company = free text on a person) | First-class Companies object, domain-based auto-creation from email |
| Deal team | 7 fixed role slots per deal (broker/seller/lender/bond counsel/issuer/nonprofit sponsor/other), chip UI, typeahead re-links existing contacts | Generic relations; roles would be a select field or junction relation (flexible, not purpose-built) |
| Pipeline | Engine statuses only (DRAFT/IN PROGRESS/COMPUTED/GATE FAILED/ARCHIVED); board explicitly refuses stage drags ("Status is set by the engine...") — only archive/restore | Kanban on any select field, drag between stages, editable stages, saved views, multiple pipelines via views, calendar view, dashboards |
| Tasks | Per-deal, due date + overdue flag + done; NO assignee, reminder, or notification | Standard object with assignee + status + custom fields; but ALSO no reminders/notification center yet (promised 2026) — a shared gap |
| Notes | Per-deal, author + date | Standard object, attachable across records |
| Timeline | Best-in-class for deals: CRM items interleaved with engine events (PHASE, LLM CALL, GATE, SPEC WRITE) in one stream | Per-record timeline: field changes, emails, calendar events; nothing like the engine interleave |
| Email | A string on the contact; zero capture/send/sync | Sync + auto-association to People/Companies/Opportunities, reply composer, workflow send. THIS instance: IMAP/SMTP/CalDAV only until Google/Microsoft OAuth apps are provisioned |
| Multi-user | Single-owner everything; no roles, sharing, assignees, or admin UI | Invites w/ roles, custom roles with object- AND field-level permissions, 2FA, admin impersonation. Caveat: ROW-level permissions ("rep sees own deals only") are paywalled even self-hosted |
| Automation | None (engine jobs only) | Visual workflows: record/cron/webhook/manual triggers; create/update/search records, branches, loops, code steps, HTTP requests, send email |
| API for integration | The app's own FastAPI (we control it) | GraphQL + REST (core + metadata), role-scoped API keys, OAuth, outbound webhooks w/ HMAC signatures, built-in MCP server at dreamcre.co/mcp, 100 req/min + 60-record batches |
| Import/export | None observed | CSV/XLSX import w/ upsert + relation mapping (10K rows/file), per-view CSV export |

## What each does that the other never will

**DREAM app keeps (Twenty can't replicate):** the engine-interleaved deal timeline; deterministic metrics on pipeline cards (Bond Proceeds/DSCR/IRR/EM); the CP-1 underwriting flow; the 7-role deal-team card purpose-built for bond deals.

**Twenty brings (we should not rebuild):** companies + orgs, drag-stage sourcing pipelines, email capture, team permissions, workflows, import/export, and a serious integration surface (webhooks + MCP + GraphQL). Rebuilding this inside DREAM was Branch B's cost; this diff is the argument against it.

## If the decision is Branch A (DREAM-on-Twenty) — instance hardening BEFORE system-of-record status

1. **Pin the image tag.** Container runs `twentycrm/twenty:latest` (digest from 2026-08-18 = v2.32.0); the next `docker compose pull` silently jumps ~5 weekly releases, some with breaking changes. Pin `twentycrm/twenty:v2.32.0` (or chosen upgrade) per the house pinning policy.
2. **Provision Google OAuth** on the instance so Gmail/Calendar sync works (today only IMAP/SMTP/CalDAV is live); email auto-association is half of Twenty's value for the sales book.
3. **Nightly Postgres dump + off-box copy.** No full-workspace export exists in the UI; the DB dump IS the backup.
4. **Row-level permissions are paid.** Plan around object/field-level: everyone on the team sees the whole sales book (matches DREAM's everyone-sees-all today).
5. **Sync design notes:** outbound webhooks fire on all objects (HMAC-signed) but event filtering at 2.32 is uncertain — verify in the UI; rate limit 100 req/min is fine for incremental sync, use the import path for backfills; the built-in MCP server is a direct integration path for DREAM-the-agent (Hermes) to read/write the CRM natively.

## Open items

- No authenticated screenshots of dreamcre.co (need a login/invite from Evan or Chuck to eyeball the actual workspace config, existing data, and webhook filtering UI).
- Whether Chuck already configured objects/pipelines in dreamcre.co is unknown — check before designing the schema.
- Shared gap to plan around either way: neither system pings anyone about due dates today (Twenty's notification center is promised "2026"); a Hermes cron reading Twenty tasks could cover this cheaply.

Source research: agent outputs archived in session scratchpad (`crm-diff/dream-crm-inventory.md`, `crm-diff/twenty-feature-profile.md`); key facts reproduced here. Screenshots: `eval_2026-08_screenshots/01`–`08`.
