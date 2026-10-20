# Mono deal screen implementation and proof

The opt-in Mono screen displays all 1,262 mapped assumptions, durable authenticated edits, historical calculator jobs and revision-bound human review. It calls the pinned local calculator through the existing engine boundary. Financial values come from Python and Excel. Browser code formats returned values only.

## Integration boundary

Enable only through a server-owned DREAM_MONO_CONFIG file. No deployment configuration is changed by this branch. An unconfigured installation retains existing behavior. Registered deals require verified app or Google identity and an explicit existing association. The local development identity cannot attest edits. Real deployment and identity grants need separate approval.

The companion calculator branch codex/phase-3-decision-provenance adds authenticated human evidence without representing other actors as Evan. It depends on Phase 2b PR 22. PR 22 remains unmerged and is not approved for merge by this change.

Immutable staged revisions and trusted ledger snapshots are published through one database transaction. Compare-and-swap prevents concurrent edits from overwriting each other. Idempotent retries return the original event and distinguish its applied revision from the current revision. Input, source, result or package changes invalidate current results and human approvals. Earlier results remain historical.

A private queued dispatcher launches the fixed native runtime. It serializes Excel access, requests cancellation through the native job store and waits for cleanup. It does not terminate unrelated Excel instances. Native workbooks are saved with new names through isolated invisible Excel.

## Verification

The final candidate passed 317 backend tests with one skipped live-provider test, TypeScript validation and the production build. The production build retains an advisory large-bundle warning. Calculator regression passed 2,392 tests with four documented skips. The portable calculator suite covers the new source vocabulary and authenticated ruling validation in its existing automated workflow.

Detailed receipts are in the [local proof folder](C:/Users/evana/dream-work/models/_phase3). [Browser proof](C:/Users/evana/dream-work/models/_phase3/browser-proof-001.json) exercised a real authenticated calculation, cancellation, conflicting edits and exact display of 20 returned metric values. That proof identifies a historical calculator hash before the final audit-wording correction. The renewed native API proof records the current calculator identity separately. Do not combine their identities.

No live judgment model, production service, real investment approval or publication was exercised. Synthetic engineering decisions are labeled fixtures. The selected Esplanade acceptance scenario is the latest $38.7 million underwriting. Available preserved human workbooks and the current Drive input specification contain $37 million. Exact parity with the selected scenario remains unproved. The [Esplanade amendment](C:/Users/evana/dream-work/mono/deals/_reviews/2026-10-18/headless-vision/PHASE-3-ESPLANADE-AMENDMENT.md) records that source gap.

## Reproduce portable checks

From the app worktree, run the full backend pytest suite with the existing app virtual environment, then run TypeScript no-emit and the frontend production build. Native tests need the separately configured Windows Excel runtime and private source registrations. The proof scripts are retained in the local proof folder and deliberately excluded from the runtime corpus.

Independent Claude review and findings disposition are required before claiming engineering completion. Merge, deployment and real-deal gates remain separate approvals.
