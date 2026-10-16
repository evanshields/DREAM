# Bridge contract proposal and local fixture acceptance

Base app `de824ba1052bab509617b05f75b84515180b9937`; separate CRM source pin `df21f4a40bd9bc74886f4551b4717c037ebb3fdc`. No Twenty source copied, existing app auth edited, service credential used or live route added.

`BETA_BRIDGE_CONTRACT_DRAFT_2026-10-04.md` is Claude-authored through Evan's authorized existing Max route: sonnet (`claude-sonnet-5-5`), no tools/MCP servers/hooks/connectors/session persistence or API fallback. First sandbox attempt timed out; the same bounded route succeeded with approved local execution outside the filesystem sandbox. Supporting task-local receipt is `claude-bridge-contract-draft-result.json`. This is reviewable architecture work, not acceptance by the existing orchestrator or verified deployed behavior.

## Reconciliation of the draft before adoption

- The first-slice execution plan excludes metrics. Local fixture projection therefore **always omits** metrics, narrative text and unknown credential-like fields, even on green/fresh status. Draft section2.0's future metrics block is out of this slice and must be removed or explicitly future-scoped by the backend owner.
- Link and message actor IDs and canonical payload hashes must be derived/validated by the verified server boundary, never accepted as authority from request JSON. Client workspace/opportunity IDs are lookup intent, not authorization. The draft lists data fields and method semantics; it does not implement that boundary.
- Status normalization must identify its authority explicitly. The local fixture wrapper requires `status.source='dream_app'`; `source='c2'` is refused even if its overlapping state is `done`. There is no C2-to-app state adapter.
- One `schema_version:1` fixture wrapper contains identity/link/status/conversation DTOs. This local packaging is not a deployed API, and `roles=['fixture-reader']` is only synthetic test data. Unknown/unmapped roles must be denied by the actual owner-defined server role map before it emits verified identity.
- Identity expiration is a display guard, not user-proof verification. The fixture consumer performs no signature/session/role check and cannot authorize a request.
- Archived links block this fixture's execution/conversation view. The proposed read-only archive-history behavior needs a separate approved response; no silent deal rebind, archive, repair or creation is implemented.
- Replay/concurrent reservation, retry hashing, cursor resumption, cancellation and timeouts remain backend acceptance obligations. The nine local projection tests do not establish those persistence/transport properties. Independent review found blank context IDs could match; nonempty context checks and a regression now refuse that case.

## Source evidence and proposed owner decisions

Actual `/api/me` is `backend/main.py` and returns only email/name/picture through current app auth; it cannot certify Twenty identity. `backend/routers/crm.py` and `backend/store/crm_store.py` have local links for deal/contact/task/note, no workspace/opportunity mapping. `backend/jobs/HERMES_INTAKE_SEAM.md` is explicitly design-only intake, not a conversation transport.

Separate CRM source: `packages/twenty-server/test/integration/graphql/utils/get-current-user.util.ts` demonstrates a user-authenticated CurrentUser query with user ID, verified email/disabled/deleted state, workspace and user-workspace IDs. `packages/twenty-server/src/engine/core-modules/user/user.resolver.ts` uses UserAuthGuard and refreshes workspace; `.../dtos/workspace-member.dto.ts` exposes roles and workspace-member identity. This does not verify deployed shape, session transport or identity joins. A service API key cannot stand in for proof of the browser user.

The Claude architecture draft supplies defaults instead of asking Evan to design the APIs: server-verifiable Twenty user proof to a short-lived principal assertion (security/config implementation separately gated), explicit deny-by-default role table, DREAM-owned link uniqueness and replay/repair audit, server-only app Hermes driver, explicit message/cursor/cancel contracts. Required architect action is record accept/amend and choose the supported existing user-proof transport, actual role/ID mapping and exact Hermes invocation/result contract. Deployed version and role-scoped Twenty access remain environment prerequisites; no production credential/auth path is inferred from local code.

## Local proof and partial beta path

The unmounted `DealWorkspaceFixture` component consumes only the safe projection in `bridgeFixtureView.ts`. Nine real consumer tests cover ready read-only projection; identity/dependency loss and expiry; context mismatch/repair/archive; unknown and C2 state rejection; CP1 human stop; stale/headline/claim/credential omission; Hermes downtime; malformed version/payload and blank context IDs. There is no fetch, route, run submission, upload, CP1 action or send operation. TypeScript project and static Vite build pass; DOM/browser/authenticated CRM proof is not run.

Reproduce from branch root: `node --test frontend/tests/bridgeFixtureView.test.mjs`; from frontend use the existing reviewed TypeScript project CLI and Vite `build --configLoader native`. No new dependency installation or dev server. The fixture component is compiled/typechecked but deliberately not mounted in the app bundle.

The useful beta fallback remains the existing DREAM underwriting app plus the independently tested cancellation patch and explicit debt-service adapter fix. It can show actual deterministic numbers, discrepancies and CP1 review without claiming the CRM/Hermes integration or exact historical oracle is complete. Live bridge wiring waits for the three contracts' recorded owner acceptance and existing approved environment access; publication/deployment still requires exact authorization.
