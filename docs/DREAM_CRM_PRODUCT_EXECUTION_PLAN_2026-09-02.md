# DREAM CRM Product Execution Plan — 2026-09-02

## Outcome

DREAM becomes one product:

- `dreamcre.co` — public landing page later.
- `app.dreamcre.co` — authenticated CRM, deal workspace, conversational underwriting, deterministic results, and CP-1 review.
- `dream.shieldstone.co` — existing underwriting app retained during transition and as a controlled rollback surface.

Twenty supplies the working CRM foundation. DREAM supplies the underwriting system and agentic experience. No team is rebuilding companies, people, pipelines, email, tasks, workflows, or MCP functionality that Twenty already provides.

## Repository boundaries

| Repository | Owns | Must not own |
|---|---|---|
| `evanshields/DREAM` | DREAM API, authentication, canonical deal/spec, jobs, deterministic engines, gates, CP-1, artifacts, first-party integration contracts | Twenty source |
| `evanshields/dream-underwrite` | Hermes underwriting payload, orchestration doctrine, gate payloads | CRM UI or canonical app persistence |
| planned `evanshields/dream-crm` | Version-pinned Twenty foundation, DREAM CRM application package, minimal upstream-compatible UI/branding patches | Canonical deal spec or deterministic underwriting math |

The Twenty-derived repository is separate because it has its own license, dependency graph, release cadence, and security-update path. The preferred implementation is a thin fork: DREAM features live in a clearly bounded application/package; core patches are used only where supported extension points are insufficient.

## Product topology

```text
User browser
    |
    v
app.dreamcre.co — DREAM CRM
    |  CRM records, pipeline, email, tasks, workflows, MCP
    |  DREAM deal pages, chat, documents, assumptions, results
    |
    +--> server-side identity-aware bridge
             |
             +--> DREAM API on US VPS
             |       +--> canonical deal/spec
             |       +--> deterministic engines and gates
             |       +--> jobs, artifacts, CP-1
             |
             +--> Hermes on UK VPS through Tailscale

All automated runs terminate at AWAITING_CP1.
```

Tailscale is server-to-server infrastructure. Browsers receive neither tailnet access nor long-lived DREAM, Hermes, or Twenty administrative credentials.

## Data authority

| Data | Authority | Mirror/consumer |
|---|---|---|
| Companies, people, Opportunity, sales stage | Twenty | DREAM links by stable IDs |
| Email, meetings, CRM tasks, notes | Twenty | DREAM may display linked summaries |
| Opportunity-to-deal mapping | DREAM | Twenty stores a safe reference/deep link |
| Uploaded underwriting copy and hash | DREAM | Twenty may show metadata |
| `underwrite-spec.json` and assumptions | DREAM | Never written by CRM |
| Job state, retries, phase, round | DREAM | Twenty displays read-only status |
| Headline metrics and QA gates | Deterministic DREAM engine | Twenty displays verified read-only mirrors |
| CP-1 reviewer action and audit | DREAM | Twenty sales-stage changes cannot bypass it |
| Hermes conversation | DREAM/Hermes boundary | May reference CRM context; never becomes metric authority |

## First vertical slice

Build one narrow proof before broad customization:

1. Open a real Twenty Opportunity as a full-page Deal workspace.
2. Show the Opportunity identity and current user.
3. Create or resolve one stable DREAM deal link idempotently.
4. Display the current DREAM underwriting status read-only.
5. Render a DREAM conversation panel that can reach the server-side Hermes bridge.
6. Fail closed and explain the state when identity, linking, DREAM, or Hermes is unavailable.

This slice deliberately excludes uploads, assumption editing, run submission, metrics, and CP-1 actions until their contracts exist.

## Required backend contracts before production frontend wiring

Claude Code owns these contracts. Codex does not invent them.

### Identity

- How Twenty proves the current user to DREAM.
- Stable user ID, verified email, role mapping, token lifetime, revocation, and failure behavior.

### Opportunity-to-deal link

- Create/find semantics, idempotency key, duplicate handling, archive/delete behavior, and link repair.

### Hermes conversation

- Conversation and message IDs, allowed deal context, streaming/polling behavior, cancellation, timeout, audit, and unavailable states.
- Explicit separation between conversational claims and deterministic metrics.

### Upload

- Accepted formats and size, short-lived authorization, immutable version, hash receipt, validation, quarantine, and deletion rules.

### Run status

- Exact job-state vocabulary, phase/round, retry/fallback, idempotent start, real cancellation, and terminal failure behavior.

### Results and CP-1

- Engine metrics, gate receipts, stale/blocked behavior, discrepancies, reviewer permissions, correction/re-run actions, and audit event.

## Delivery lanes

### Claude Code — architecture, backend, VPS, deploys

- Harden and back up Twenty.
- Move the product hostname to `app.dreamcre.co` using the companion nginx handoff.
- Define the contracts above.
- Build the Twenty adapter, webhook verification, deal-link store, service authentication, and Hermes driver boundary.
- Own production deploys and live verification.

### Codex — CRM and frontend

- Maintain the authenticated live CRM inventory.
- Write the Deal-workspace UX and acceptance criteria.
- Build the first vertical-slice UI against contract fixtures.
- Integrate only after the corresponding API contract is written.
- Verify accessibility, responsive behavior, honest loading/error/blocked states, and DREAM-dominant branding.

### Parallel-agent operating rule

- Use sub-agents when the work naturally splits into independent lanes.
- Match the model to the work: Sol for architecture, high-risk review, and final reconciliation; Terra for implementation; Luna for focused audits, inventories, and fast verification; GPT-5.5 only for bounded checks where it is clearly sufficient.
- Keep the primary agent accountable for reconciling results, enforcing DREAM guardrails, and deciding what actually ships.
- Do not split tightly coupled edits just to create motion.

## Phased execution

### Execution snapshot — 2026-09-03

- **Stage 0 — substantially complete:** the CRM image is digest-pinned; a verified nightly database backup and one checksum-matched off-box copy exist; configuration backups and a 4GB swapfile are in place. A full database restore drill and durable automated off-box transfer remain open.
- **Stage 1 — complete:** `app.dreamcre.co` is live with valid TLS, and `dreamcre.co` temporarily redirects to it with rollback configuration retained.
- **Stage 2 — in progress:** the private `evanshields/dream-crm` fork, fetch-only Twenty upstream, reproducible image workflow, and dedicated `C:/tmp/dream-crm` worktree exist. An earlier baseline DREAM-branded image (`sha256:6d06ccd23cce5a76bac89b49c53fda22d0d0ac9d57e93d8e8c0f315fef1b0794`) is live and verified. The newer Nocturne Iris light/dark system, approved DREAM mark, self-hosted typography, localization-aware shell copy, and conservative static-cache policy are implemented but not yet deployed on `codex/dream-branding-shell`. Focused review, the full 6,362-test frontend suite, shared-UI tests, and a production frontend build pass; the newer branch's combined commit, fork CI, deployment, and authenticated live verification remain.
- **Stage 3 — contract-blocked:** no Deal-workspace or Hermes UI implementation starts until the identity, deal-link, and conversation API contracts are written.
- **Stages 4–5 — not started.** Their gates and ownership boundaries below remain unchanged.

### Stage 0 — Protect what exists

- Complete database and configuration backups.
- Pin the deployed Twenty image/tag/digest and identify its exact source commit.
- Add UK swap and establish a resize threshold.
- Prove restore before real partner data enters the CRM.
- Refresh the third-party audit for the exact fork point before installing or running the fork locally.

### Stage 1 — Domain cutover

- Execute `HANDOFF_APP_DREAMCRE_CO_2026-09-02.md`.
- Keep `dreamcre.co` as a temporary redirect to the app.
- Preserve the current hostname as a documented rollback during the transition.

### Stage 2 — Versioned CRM foundation

- Create the separately licensed `dream-crm` repository at the exact deployed Twenty commit.
- Add `twentyhq/twenty` as the read-only `upstream` remote.
- Establish protected main/release branches and a DREAM development worktree.
- Document upstream merge, security-patch, test, and rollback procedures.
- Keep Twenty core modifications minimal and separately reviewable.

### Stage 3 — First vertical slice

- Implement the Opportunity Deal workspace shell.
- Prove identity, stable deal linking, read-only status, and Hermes conversation.
- Keep the existing DREAM frontend available as fallback.

### Stage 4 — Deal execution

- Add file intake and validation.
- Add assumption review and optimistic locking.
- Add idempotent run start, real progress states, retry/fallback, and cancellation.
- Add deterministic results, gates, discrepancy display, and CP-1.
- Add versioned outputs.

### Stage 5 — Productization

- Add tenant isolation before inviting outside customers.
- Isolate customer data, credentials, document storage, Hermes profiles, cost governors, and underwriting deployments.
- Add audit/retention/deletion controls, billing, monitoring, and support tooling.
- Resolve AGPL source-offer obligations or obtain reviewed commercial rights before production commercialization of a derivative.

## Acceptance gates

The first vertical slice passes only when:

- A non-Evan analyst signs in from a non-Z13 machine.
- One Opportunity links to exactly one DREAM deal despite repeated requests.
- Refreshing preserves state.
- Unauthorized users fail closed.
- DREAM or Hermes downtime shows an honest unavailable state and does not corrupt CRM work.
- No service secret reaches browser code or logs.

The integrated product passes only when:

- A real document package reaches an immutable, hash-verified DREAM intake version.
- A full run lands at `AWAITING_CP1` and cannot advance automatically.
- A forced RED gate blocks publication and hides stale headline values.
- Esplanade remains ACQ IRR `0.2251`.
- Rayzor remains EFB bond proceeds `$63,868,907`.
- A webhook replay creates no duplicate link, deal, or run.
- Backup restore and deployment rollback both succeed.
- One real week of sales and underwriting work is completed through `app.dreamcre.co`.

## Immediate next actions

1. Complete the combined branch review; then commit, run fork CI, deploy by immutable digest, and verify authenticated light/dark routes without changing CRM data or workflows.
2. Deploy the tested CRM static-cache policy with the branded image, and separately enable nginx compression on the UK VPS after `nginx -t`; verify live HTML, hashed-JavaScript cache, and compression headers with rollback available.
3. Complete a full database restore drill and configure durable encrypted off-box backup transfer before real deal data accumulates.
4. Configure and test authenticated CRM API/MCP access and one webhook only after role-scoped credentials and a reversible test target are defined.
5. Claude Code writes the identity, opportunity-to-deal-link, and Hermes conversation contracts.
6. Codex builds the first vertical-slice Deal-workspace UI against those written contracts and fail-closed fixtures.
7. Evan chooses the fork's production license path before external commercialization: AGPL-compliant source availability or reviewed commercial rights.
