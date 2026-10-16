**Draft contract for local fixtures only.** Authored by Claude in isolation. It is a proposal, not adopted by any running session, and orchestrator acceptance is unknown. The evidence below is as reported in the delegation brief. I did not re-read the repos.

**Codex v2 source correction:** primary supplied the wrong app-state list to the isolated author in v1. Checked directly against `backend/jobs/contracts.py:JobStatus`; corrected below and guarded by a source-enum parity test. Claude authorship applies to the original proposal; this correction still awaits architecture-owner acceptance.

Labels used: **IMPL** means reported as existing. **PROP** means proposed here. **UNK** means unverified. **OWN** means needs an owner decision.

# 1. Implemented evidence

| Ref | Reported fact | Label |
|---|---|---|
| [backend/main.py](backend/main.py) `/api/me` | Returns email, name, picture via the app's `require_auth` | IMPL |
| App auth | Accepts own app JWT, or Google token plus allowlist. It is not a Twenty session verifier or role translator | IMPL |
| CRM `/api/links` | Links local contact, task, note and deal kinds. No Twenty opportunity kind | IMPL |
| App `backend/jobs/contracts.py:JobStatus` | submitted, routing, awaiting_input, analyzing, synthesizing, awaiting_cp1, completed, failed, cancelled | IMPL, directly verified in v2 |
| Job cancel | Sets `cancel_requested`. A running job honors it between phases. A paused job does not complete | IMPL |
| `backend/agent/drivers` | No Hermes implementation present | IMPL (absence) |
| dream-crm pin `df21f4a4...` (AGPL, separate repo), `test/integration/graphql/utils/get-current-user.util.ts` | CurrentUser query returns id, email, isEmailVerified, disabled, deletedAt, currentWorkspace{id, activationStatus}, currentUserWorkspace{id, userId} | IMPL, read-only analysis |
| Same pin, user resolver | Uses UserAuthGuard. Refreshes currentWorkspace, which may be absent | IMPL |
| Same pin, WorkspaceMemberDTO | Exposes id, userEmail, roles, userWorkspaceId. `currentUserWorkspace.id` is not established to equal `workspaceMember.id` | IMPL, equality UNK |
| Twenty deployed version and transport | Not verified | UNK |
| C2 pin `cfd42b4` plus dirty fixwave | Server-only, principal-scoped MCP stage tools: `start_stage` (stages 1-7), `get_job`, `answer_handback`, `confirm_comps`, `cancel_job` | IMPL, in flux |
| C2 identifiers | `job_id`, `request_id` and `deal_revision` are not the app's `job_id`, `conversation_id` or version | IMPL |
| C2 `done` | Does not imply app `awaiting_cp1`, a stage 8 workbook, or human approval | IMPL |
| C2 worker lifecycle and provenance gates | Missing, owned by the fixwave. No live use | IMPL gap |
| Execution plan | Lists identity, link and conversation contracts as Claude-owned. Stage 3 is contract-blocked | IMPL (plan) |

# 2. Proposed contracts (data shapes and method semantics, no endpoints)

Common rules for all three:
- Every DTO carries `schema_version`.
- Any unknown enum value, missing required field or extra-typed field yields `malformed`. The client fails closed and never guesses.
- No DTO contains credentials. No message or status DTO contains engine numbers except the gated `metrics` block in 2.0.

## 2.0 Read-only status DTO (first slice)

```
DealStatus {
  app_deal_id, link_id, status_revision,
  job_state: submitted|routing|awaiting_input|analyzing|synthesizing|
             awaiting_cp1|completed|failed|cancelled,
  phase|null, round|null, cancel_requested: bool,
  fresh_as_of, stale: bool,
  gates: {state: green|amber|red|unknown, receipt_ref|null},
  metrics: null | {display_allowed: bool, items: [...]}   // see invariants
}
```

Invariants:
- The state vocabulary is exactly the 9 app states. C2 states are never mapped into it.
- `metrics` is null unless `stale=false` and gates are green with a receipt.
- Red, unknown or stale gates mean metrics are hidden.
- `awaiting_cp1` is displayed as "awaiting human review" with no action offered.
- `completed` is shown as reported; no new approval action or inference is introduced. C2 `done` is refused, not mapped.

## 2.1 Verified identity

```
VerifiedIdentity {
  principal_id,                 // DREAM-minted, stable, opaque
  twenty_user_id, twenty_workspace_id,
  twenty_user_workspace_id|null, workspace_member_id|null,
  email, email_verified: true,
  roles: DreamRole[],           // after translation, never raw Twenty roles
  proof_kind, proof_id, issued_at, expires_at
}
IdentityResult = verified{VerifiedIdentity}
  | denied{reason: unauthenticated|expired|revoked|disabled|deleted|
           unverified_email|no_workspace|not_allowlisted|no_role}
  | unavailable{dependency, retryable}
  | malformed
```

Method: `verify_principal(proof) -> IdentityResult`.

Invariants:
- Never treat `currentUserWorkspace.id` as `workspaceMember.id`. Join only by an explicitly verified key, otherwise leave `workspace_member_id` null.
- An absent `currentWorkspace` yields `denied(no_workspace)`.
- Disabled, deleted or `email_verified=false` yields denied.
- An unmapped or unknown role yields `no_role`. There is no default role.
- Expired proof yields denied. Revocation is checked at least at each link and conversation start.
- `principal_id` and `twenty_workspace_id` scope every downstream record.
- Existing `/api/me` and app JWT are not accepted as Twenty proof.

## 2.2 Opportunity-to-deal link

```
LinkRequest { twenty_workspace_id, twenty_opportunity_id,
              idempotency_key, payload_hash, principal_id }
LinkRecord  { link_id, app_deal_id, twenty_workspace_id, twenty_opportunity_id,
              state: active|repair_required|archived,
              created_by, link_revision, payload_hash, audit_ref }
LinkResult  = created|replayed{LinkRecord} | existing{LinkRecord}
  | payload_mismatch | forbidden | opportunity_gone | unavailable | malformed
```

Methods: `resolve_or_create_link(LinkRequest)`, `get_link(workspace, opportunity)`, `repair_link(link_id, expected_revision, action, reason)`, `archive_link(link_id, expected_revision, reason)`.

Invariants:
- The idempotency scope is (workspace, opportunity, key).
- Same key and same hash returns `replayed` with the identical record and no new write.
- Same key and different hash returns `payload_mismatch` with no mutation.
- A new key for an opportunity that has an active link returns `existing`. At most one active link per opportunity and one per deal.
- Archive happens when Twenty reports the opportunity gone, or on an explicit action. It retains the deal and its history and never auto-deletes.
- `archived` links resolve read-only. Reactivation goes only through `repair_link`.
- Repair needs `expected_revision` and a reason. It writes an audit event and never silently rebinds an opportunity to a different deal.
- A conflicting or ambiguous state yields `repair_required`, and status is blocked until repaired.
- The link store is DREAM-owned. Twenty holds only a safe reference.
- Existing `/api/links` kinds do not cover this. A new link kind or store is PROP.

## 2.3 Conversation and messages

```
Conversation { conversation_id, link_id, app_deal_id, principal_id,
               state: open|closed|unavailable }
Message { message_id, conversation_id, seq, role: user|assistant,
          client_message_id, retry_hash, content,
          claims: [{text, class:"unverified_claim", deal_ref|null}],
          state: accepted|streaming|complete|cancelled|timed_out|failed }
Event { cursor, conversation_id, message_id,
        type: accepted|delta|complete|failed|cancel_requested|cancelled|
              timeout|unavailable, at }
AuditEvent { audit_id, principal_id, conversation_id, message_id|null,
             action, outcome, at }   // no content bodies, no secrets
```

Methods: `send_message`, `read_events(conversation_id, after_cursor)`, `cancel_message`, `get_conversation`.

Invariants:
- `retry_hash` is a hash over a canonical form of conversation, `client_message_id`, content and allowed context ref. Same id and same hash replays the same message. Same id and different hash is `payload_mismatch`.
- Cursors are opaque, monotonic and per conversation. Resume with `after_cursor` yields no duplicates and no gaps. An expired cursor yields `reset_required` and the client refetches the full state.
- Cancel is two-step. `cancel_requested` is an acknowledgement and `cancelled` is the final state. The UI shows "cancelling" until the final event.
- Timeout is terminal. A partial answer is labeled incomplete and never promoted to complete.
- `unavailable` is a distinct, retryable state. It never corrupts CRM data.
- Context is limited to the linked `app_deal_id` and the principal's access.
- Every claim is `unverified_claim`. Messages never carry authoritative metrics. Numbers shown come only from `DealStatus.metrics`.
- Audit is recorded for send, cancel, timeout, unavailable and denial.
- App conversation IDs are not C2 `request_id` or `job_id`. Any future mapping is a separate, explicit record.

# 3. Readiness barriers

None of these can be cleared by fixtures. Fixtures must simulate each as a typed result.

| Barrier | Status | Blocks | Clears when |
|---|---|---|---|
| B1 User-proof transport (Twenty to DREAM) | UNK | Any live identity use | Owner selects a transport, and the deployed Twenty version supports it |
| B2 Current role map | UNK | Role claims in `VerifiedIdentity` | Owner supplies an actual role table. Until then fixtures use opaque test roles |
| B3 Hermes invoke | No implementation | Any live conversation | A driver contract exists and is reviewed |
| B4 Deployed Twenty version vs pinned analysis | UNK | Trusting the CurrentUser shape | Version verified against the pin |
| B5 C2 worker lifecycle and provenance gates | Missing, in fixwave | Any C2 use | Fixwave owner signs off. Not used in the first slice |
| B6 Orchestrator acceptance of this draft | UNK | Treating this as adopted | Recorded acceptance |

No source was copied from the AGPL repo. No metric or model result is claimed here.

# 4. Local fixture acceptance cases

Scope is read-only status plus conversational claims. There are no upload, run or CP1 write paths. Every fixture is local JSON with no network.

| ID | Fixture input | Expected UI and contract result |
|---|---|---|
| F-01 | Valid identity, active link, status `analyzing` | Shows state, phase and round. Metrics hidden |
| F-02 | Same link request replayed | Same `link_id`, `replayed`, no duplicate |
| F-03 | Same key, different hash | `payload_mismatch` shown, no change |
| F-04 | Second key for the same opportunity | `existing`, one link only |
| F-05 | Link `repair_required` | Status blocked with an explanation |
| F-06 | Link `archived` | Read-only, no conversation send |
| F-07 | Identity `denied` (each reason) | Fail closed, specific safe message |
| F-08 | `currentWorkspace` absent | `no_workspace` denial |
| F-09 | Member id differs from user-workspace id | No join. `workspace_member_id` null |
| F-10 | Unknown role | `no_role` denial |
| F-11 | Unknown `job_state` or enum value | `unknown_state`, blocked, no guess |
| F-12 | Malformed DTO (missing field, wrong type, extra enum) | `malformed`, fail closed |
| F-13 | DREAM API unavailable | Honest unavailable state, retry offered |
| F-14 | Hermes unavailable | Conversation `unavailable`, status still shows |
| F-15 | Identity service unavailable | Fail closed, no cached privilege |
| F-16 | Proof expired mid-session | Re-verify required, no further sends |
| F-17 | Stale status with metrics present | Metrics hidden, stale banner |
| F-18 | Red or unknown gate with metrics | Metrics hidden, gate state shown |
| F-19 | Status `awaiting_cp1` | "Awaiting human review", no action control |
| F-20 | App status `completed` | Shown as reported, no new approval inference; C2 `done` refused |
| F-21 | C2-shaped job state in the fixture | Rejected as `malformed`, never mapped |
| F-22 | Message replay, same retry hash | Same message, no duplicate |
| F-23 | Stream resumed from cursor | No duplicates or gaps |
| F-24 | Expired cursor | `reset_required`, full refetch |
| F-25 | Cancel: `cancel_requested` then `cancelled` | UI shows "cancelling", then final |
| F-26 | Timeout with partial text | Terminal, labeled incomplete |
| F-27 | Assistant message containing a number | Rendered as an unverified claim, not a metric |
| F-28 | Fixture containing a secret-like field | Test fails if it appears in any rendered output or log |

# 5. Owner decisions

Each has a proposed default. The owner confirms or overrides.

1. **Identity proof transport (B1).** Default: the server-side bridge verifies the Twenty session and mints a short-lived, DREAM-signed principal assertion. The browser never holds long-lived credentials.
2. **Role table (B2).** Default: a small explicit table, deny by default, supplied by the owner.
3. **Link creation in the first slice.** Default: allowed, as the only write, because the plan lists linking in the slice. Confirm this is outside "no upload/run/CP1 writes".
4. **Hermes invoke shape (B3).** Default: an app-side driver behind a single `send_message` method. C2 stays out of the first slice.
5. **Orchestrator acceptance (B6).** Record accept, amend or reject.

**Bottom line:** Codex can build against sections 2 and 4 now. Nothing here unblocks live wiring until B1 to B3 clear.
