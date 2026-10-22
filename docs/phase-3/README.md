# Mono deal screen implementation and proof

The opt-in Mono screen displays all 1,262 mapped assumptions, durable authenticated edits, historical calculator jobs and revision-bound human review. It calls the pinned local calculator through the existing engine boundary. Financial values come from Python and Excel. Browser code formats returned values only.

## Integration boundary

Enable only through a server-owned DREAM_MONO_CONFIG file. No deployment configuration is changed by this branch. An unconfigured installation retains existing behavior. Registered deals require verified app or Google identity and an explicit existing association. The local development identity cannot attest edits. Real deployment and identity grants need separate approval.

The companion calculator branch codex/phase-3-decision-provenance adds authenticated human evidence without representing other actors as Evan. It depends on Phase 2b PR 22. PR 22 remains unmerged and is not approved for merge by this change.

Immutable staged revisions and trusted ledger snapshots are published through one database transaction. Compare-and-swap prevents concurrent edits from overwriting each other. Idempotent retries return the original event and distinguish its applied revision from the current revision. Input, source, result or package changes invalidate current results and human approvals. Earlier results remain historical.

A private queued dispatcher launches the fixed native runtime. It serializes Excel access, requests cancellation through the native job store and waits for cleanup. It does not terminate unrelated Excel instances. Native workbooks are saved with new names through isolated invisible Excel.

The outer bridge requests cancellation after 22 minutes. A human cancellation or shutdown request starts the same 30-second cleanup grace immediately. If the bridge remains alive beyond that grace, the visible job fails and a durable dispatcher quarantine blocks new calculations. The dispatcher retains its lease while the bridge remains alive. It never terminates that parent while Excel cleanup is uncertain. Historical records remain readable after restart, but the quarantine is not cleared automatically. Before clearing it, an operator must verify the exact recorded bridge, native worker and owned Excel process have ended using their ownership receipts. A PID disappearing by itself is insufficient proof.

## Verification

The current local remediation passed 342 backend tests with one skipped live-provider test. The preceding committed candidate also passed the remote backend checks, TypeScript validation and production build. The production build retains an advisory large-bundle warning. Calculator regression passed 2,392 tests with four documented skips. The portable calculator suite covers the new source vocabulary and authenticated ruling validation in its existing automated workflow.

The [portable verification index](verification.json) binds the tested source identities, counts and private receipt names. Browser proof exercised a real authenticated calculation, cancellation, conflicting edits and exact display of 20 returned metric values. That proof identifies a historical calculator hash before the final audit-wording correction. The renewed native API proof records its own calculator identity separately. Astra independently recalculated four preserved cases and checked source hashes. These are Windows proofs, separate from portable automated tests.

Claude Opus 5.5 completed read-only review and identified four required corrections. Lead corrections protect new authenticated Evan rulings, require explicit percentage scale and safely insert absent mapped fields. Evan then approved explicit total-loss presentation for an acquisition with no positive investor receipts. Normal calculated returns, including genuine zero, remain numeric. Pure Bond investment returns remain not applicable. The [saved-workbook return evidence](return-policy.json) records exact Azalea parity, loss and zero guard tests, with final registered API/browser renewal and independent review still open.

No live judgment model, production service, real investment approval or publication was exercised. Synthetic engineering decisions are labeled fixtures. Evan selected the September $37 million Esplanade workbook as the answer key. Exact parity is open and its historical Checks contain 12 broken references.

## Reproduce portable checks

From the app worktree, run the full backend pytest suite with the existing app virtual environment, then run TypeScript no-emit and the frontend production build. Native tests need the separately configured Windows Excel runtime and private source registrations. The proof scripts are retained in the local proof folder and deliberately excluded from the runtime corpus.

Findings disposition and final corrected proofs are required before claiming engineering completion. Merge, deployment and real-deal gates remain separate approvals.


## Automatic checks

The [app workflow](../../.github/workflows/ci.yml) runs portable backend tests, TypeScript and the frontend build on pull requests. It uses the existing pinned application dependencies and pytest 9.0.2. Native Excel and private cross-repository integration proofs remain separate Windows evidence.

The three GitHub-owned Actions are pinned to verified commit identities. They follow GitHub's [Python workflow guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) and [Node workflow guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/nodejs). The workflow has read-only repository permission, persists no checkout credential and uses no production secret.
