# DREAM beta acceptance and frontend ownership

**Cancellation v2, independent review correction:** old-phase acknowledgements previously lost `cancel_requested=true` during phase-regression suppression. V2 keeps the newer phase and ORs the cancellation bit for the same active run, with a regression covering earlier acknowledgement, false replay, foreign job and CP1 latch. Eleven helper tests pass. The original v1 patch remains immutable. This is helper/request-order evidence, not arbitrary server snapshot revision ordering or a reproduced browser race.

Checkpoint: 2026-10-04 approximately 03:56 UTC. Target is Sunday morning October 4 ET; readiness is measured by evidence, not promised by the target. App base de824ba1052bab509617b05f75b84515180b9937. Branch codex/beta-cancel-proof is isolated in the task-9 dream-beta-wt worktree. Existing Claude builders retain backend, CRM bridge, Lane A/B, MCP, shared pipeline, provider and deployment ownership.

## Owned change

The existing underwriting frontend used to discard cancellation failures and return to intake immediately. It now keeps the known run visible, renders cancellation acknowledgement separately from server-confirmed cancellation, polls only executing jobs, permits status refresh after connection loss, and preserves confirmed terminal outcomes against stale responses. Cancel is unavailable before the server returns a job ID. Paused input cancellation is explicitly unavailable because the current backend only sets a flag with no worker to honor it. CP-1 stays a visible human stop even with that flag. No new backend, CRM identity or Hermes transport is invented.

Named paths: frontend/src/pages/Underwrite.tsx, frontend/src/hooks/useJobPolling.ts, frontend/src/lib/jobProgress.ts, frontend/src/lib/api.ts (optional cancellation AbortSignal only), frontend/tests/jobProgress.test.mjs, this document. No vendored engine, backend or authenticated production service changed. A read junction uses the existing frontend node_modules; no installation ran.

Two independent peer reviews through the existing Claude Max route (Sonnet 5.5) had zero MCP servers/tools, disabled hooks and persistence, no API-key/paid fallback and no billing/quota warning. They identified paused-state, reconnect/race, hanging request and page-leave defects; those were corrected. Cancellation now has a 15-second abort deadline and unmount cleanup. Paused runs offer refresh and a Pipeline exit. This is source review, not browser sign-off; the final corrective edits were locally tested and not sent for a third review.

## Observed acceptance

| Gate | Result | Evidence and practical limit |
|---|---|---|
| Cancellation transition fixtures | Passed | 10 Node tests: acknowledgement versus completion, failed/lost request, terminal race, CP-1/input pause, late view/old-job suppression, abort/late-response suppression, phase ordering/resume, unknown status, failure and active polling. Pure lifecycle helpers; no browser interaction claim. |
| Frontend typecheck/build | Passed | TypeScript project build plus Vite 7.2.4 static build with native config loader. Existing large chunk warning. No dev/preview server. |
| Full existing local app/engine suite attempt | Environment-blocked | 401 passed, 20 skipped, 2 failed because invalid-token auth tests attempted Google certificate fetch and hit the deliberate outbound network guard. No auth code changes proposed. |
| Offline subset excluding the two Google-dependent checks | Passed | 401 passed, 20 skipped, 2 deselected. 19 skips require absent Rayzor ACQ workbook template; one requires live Kimi key, intentionally absent. This is not a complete suite green. |
| Existing app async worker cancellation | Passed | In-memory stores, real async queue and blocking StubAnalysts fixture: POST cancel returned analyzing/cancel_requested, worker then reached cancelled, metrics absent. Not MCP dispatcher cancellation. |
| App stub CP-1/replay | Passed | ACQ and EFB fixed first-party fixtures reach awaiting_cp1; duplicate submission returns same job/deal. Bare jobs router, not authenticated app/CRM. |
| Paused backend cancellation | Failed | Actual POST on awaiting_input returns awaiting_input plus cancel_requested=true; no worker honors it. Frontend now explains/gates this instead of claiming cancellation. |
| Locked exact Esplanade oracle | Failed | Current boundary fixture outputs 0.22212539391032182 (0.2221 at four decimals), versus locked 0.2251. Existing 2% relative test passes. No engine/backend changes; owner must reconcile before exact oracle acceptance. |
| Rayzor EFB dollar target | Passed with precision limit | Fixed fixture outputs 63868906.8825598, rounds to 63868907. This is a deterministic fixture check, not fresh underwriting/workbook proof. |
| Browser UX and authenticated analyst on another machine | Not run | Requires a safe browser/authorized identity route; no profile or credential changes made. |
| Integrated Mono -> C-2 -> CRM/Hermes -> reviewed output | Not run | Blocked below; local app stub proof is not this vertical slice. |

## Cross-repository contract review

Frozen C-2 reference is tools/dream_mcp/DESIGN.md sections16-29, v2 8ac1ab4 initially reviewed at b4edb7b; final source reconciliation pinned MCP cfd42b4f, comps 7a9149da and routing 0db7eba5. Lane C reports Windows integration green, Linux CI dispatched and Opus review running; these are owner receipts, not this task's independently run tests. The current comps-wt Lane C relay is newer authority than stale main/MCP Kaizen copies. Independent findings and ownership were published as CODEX-BETA-C2-ACCEPTANCE-REVIEW-2026-10-04.md and CODEX-BETA-OWNERSHIP-2026-10-04.md in its phase13-plan folder, with an append-only Lane C relay. Receipt by a live Claude session is unverified.

| Boundary | Written evidence | Missing acceptance |
|---|---|---|
| C-2 stage lifecycle | start_stage stages1-7; required tree revision; principal/slug key namespace; get_job polling; explicit answer then new start; cancel acknowledgement versus actual child death | Worker lock lifetime, replay in all states, cancellation/tree reap, canonical screen proof, old-wait resumed linkage and waiting_since, shared ledger hardening, real dispatcher integration tests. Current dirty/source review only; builders own fixes. |
| C-2 -> app | C-2 state vocabulary and deal tree hash are distinct from app JobView.status/spec persistence | No adapter contract that turns C-2 done into deterministic verified awaiting_cp1. C-2 done is not human approval, nor stage8/workbook completion. |
| CRM identity | Execution plan assigns Claude verified current-user proof, stable ID/email/role/revocation | No located written first-slice Twenty identity contract; frontend integration remains blocked. Existing app bearer /api/me is not Twenty identity translation. |
| Opportunity -> deal | DREAM owns mapping; stable IDs/deep links; CRM never owns spec | No located idempotent link/create/repair/archive contract or adapter. No CRM browser token or invented schema. |
| Hermes conversation | Claude owns conversation/message IDs, deal context, streaming/polling/cancel/timeout/audit | No located server bridge contract. C-2 handback IDs are not CRM conversation IDs. Narrative claims never become headline metrics. |

C-2 source review is concurrent and must be refreshed before relying on line numbers. Refresh accepted removal of local answer fallback and canonical screen-hash function, while worker provenance and core lifecycle gaps remain. Do not publish the original snapshot as if later fixes were absent.

## Methodology and workflow sequence

Lane A latest relay reports v8f cosmetic proof, pass4 committed 81ec708, 2,446 tests; Evan hand-formatting v8g. Remaining: prove v8g against v8f, apply pass4, phaseC, final recheck, close Phase7. These are reported lane receipts; this task did not read private workbook outputs or rerun them.

Lane B waits for final Phase7 template and recorded transaction decisions. Phase9 approved blank/example publication and Phase10 general Mono loader follow the deal/template sequence. C-5 waits for Phase10 and finished formatting. The app Mini export/stub fixture does not substitute for Mono loader or methodology validation. Existing manuals/process remain owned in canonical dream-underwrite; no underwriting judgment, assumptions or investor document was produced here.

Repeatable throwaway integrated acceptance after owners finish: import the approved esplanade-c2 fixture at exact Lane A release SHA; capture input/template hashes; start stage5; observe precise generation/request/prompt SHA; answer with principal/model claim; explicitly resume using new key and returned tree revision; confirm the unchanged canonical comp screen; repeat the market handback/resume; prove original waits close with response SHA/claim/consumer job; force replay/stale revision/cancel/RED failures; reach engine-verified app awaiting_cp1; only then have a human review the workbook/document. Stage8/Mono is unavailable in C-2; do not imply it ran.

## Exact decisions and remaining gates

No prior Phase7/template rulings need to be asked again. Existing C-2 orchestrator must settle its replay/spec contradictions and builders must close lifecycle defects. Backend owner must address paused cancellation and reconcile exact Esplanade oracle drift without changing vendored engine casually. Claude must supply the three app bridge contracts before Codex wires the CRM workspace.

Separately gated actions still require exact Evan approval: production/root deployment, public C-3 OAuth/hostname, new credentials/Twenty key, provider/profile/security changes, paid fallback, and eventual C-5 Windows worker. No merge/push/draft PR/deploy was attempted. Full browser/auth/CI/fixture/live/restore/real-week proofs remain open; the current state is not an integrated beta-ready claim.

## Reproduction

From this branch's root: `node --test frontend/tests/jobProgress.test.mjs`. Use the existing reviewed TypeScript CLI for no-emit/project build and Vite CLI `build --configLoader native` from frontend; do not install new packages or expose the vulnerable pinned dev server. The task-9 run-local-tests.py and app-sample-acceptance.py scripts preserve provider/network restrictions and emit the local fixture receipt. Those task-local harnesses are supporting evidence outside this business branch, not production payload.
