# DREAM morning decision brief for Evan

Sunday morning ET remains the beta target. A reviewed synthetic local sample is usable now; the integrated Mono/CRM/Hermes workbook-and-document beta is not accepted yet.

## 1. Choose the authoritative Esplanade scenario

**Question:** should acceptance retain the historical $34M purchase  / 6% exit  / 0.2251 IRR scenario, with its approved workbook and complete cash-flow/debt schedule identified, or should another named approved scenario be reconciled before any proposed rebaseline?

Retaining the existing gate pending authoritative source is recommended. The unchanged engine gives 0.22212539391032182; the existing tolerance test passes but the exact 0.2251 gate fails. The exact manifest May 15 workbook was found: 37.5M / 7.5%, cached IRR 0.18065955204168627, independently reproduced from cached annual flows. May 17 matches that scenario; May 13 is 72.941176M / 8% / 0.0587445281; May 18 is 39M / 7.25% / 0.1840259314. No workbook was recalculated or modified, and no expected number was tuned. Full paths/hashes: task9 `esplanade-source-candidate-receipt.json`.

## 2. Route the app contract handoff to its actual owner

The project plan assigns Claude Code the app identity, opportunity/deal-link and Hermes conversation contracts. The current MCP owner is active, but no sitting app architecture owner has acknowledged/adopted those contracts or supplied the backend fixture path. The fresh sessionless Claude Max review route cannot establish another session's receipt.

**Action needed:** identify the current app architecture owner/session or assign that role, and have that owner accept or amend `CODEX-ARCHITECTURE-ACCEPTANCE-REQUEST-V2.md` in the existing project handoff. This asks for ownership/adoption, not for Evan to design the interface. Live wiring stays gated. The app also uses global key-only replay; intended principal/payload scope and team-sharing policy need that owner's contract decision before any separately approved security/schema remedy.

## 3. Try the fixed local sample; respect the workload limits

Read [acceptance limits](../local_demo/ACCEPTANCE_LIMITS_2026-10-04.md), then run from this isolated documentation v2 checkout:

```powershell
& .\local_demo\Start-LocalSample.ps1
```

Open `http://127.0.0.1:8769/__demo__/`; stop with Ctrl+C. Use the fixed ACQ/EFB inputs on that page, leave documents empty, try questions/resume, identical-payload replay, CP-1 stop and the read-only bridge failure cases. No real CRM, providers, exports or approval actions. This checkout adds text clarifications to the same reviewed runtime; its original v1 remains immutable.

**Cancellation is limited:** the app's fixed in-process worker observed a cooperative flag between phases. It does not stop arbitrary blocking work or prove process-tree cleanup. A separate Windows MCP Dispatcher test failed because an owned grandchild stayed alive after cancellation and lock release; it was safely cleaned up. Current published MCPd1484de has 149 passing native Linux package/component tests, including a direct TERM-ignoring group helper test. Our two native full Dispatcher descendant cases remain unadopted/unrun and require exact-source owner execution; neither that package pass nor the app fixture establishes arbitrary-workload safety.

Existing owners can continue test integration, remaining CI repairs, Mono/manual acceptance alignment and contract fixtures without changing financial assumptions. Final formatting/Phase7 proof, Phase8 / 9 approvals, Phase10 general loader and actual human-reviewed output remain prerequisites. Full public OAuth, new credentials/profile changes, deployment/root steps, Windows worker startup and new paid calls retain their exact approvals.

No new action approval is needed for the completed documentation/local-fixture work. If native integration is requested, the concrete approval target is the reviewed two-file `c2-dispatcher-acceptance-tests-v3.patch` on the owner's exact feature source and an isolated existing Linux CI test job. Its risk is a buggy teardown hanging an isolated fixture/lock; use owned-process cleanup and a hard job timeout. That approval excludes remote production execution, WSL installation, credentials and deployment.
