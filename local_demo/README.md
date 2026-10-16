# Repeatable local partial-beta sample

Run from this isolated checkout in PowerShell:

```powershell
& .\local_demo\Start-LocalSample.ps1
```

Open `http://127.0.0.1:8769/__demo__/`. Stop with Ctrl+C. Port8769 must be free; the launcher does not stop an existing process. It reuses the existing `C:\Users\evana\DREAM\.venv` and frontend dependencies, with no install, provider calls, production data, credentials or deployment. Only static Vite building is used; no Vite development server is started.

The local instructions provide fixed ACQ/EFB inputs and a separate read-only bridge fixture. The actual app job runner supports missing-input questions, human answers/resume, CP1 stop, identical-payload replay and polling. Cancellation passed only for the fixed in-process analyst fixture; its cooperative flag is observed between phases. It does not interrupt arbitrary blocking work or establish child-process cleanup. Read [the cancellation acceptance limits](ACCEPTANCE_LIMITS_2026-10-04.md) before trying cancellation. CP1 approval, upload/extraction, exports, real CRM/Hermes and provider endpoints are unavailable. The visible fixture banner applies to every served app page. The test identity and `LOCAL_FIXTURE_ONLY` marker are public fixture data. In-memory data disappears when stopped.

Repeat acceptance without a browser after building:

```powershell
& C:\Users\evana\DREAM\.venv\Scripts\python.exe .\local_demo\verify.py
node --test .\frontend\tests\jobProgress.test.mjs .\frontend\tests\bridgeFixtureView.test.mjs
```

`verification.json` records the earlier v1 synthetic fixture results. [The versioned acceptance limits](ACCEPTANCE_LIMITS_2026-10-04.md) add the separate observed Windows MCP grandchild failure and unrun native Linux cases; the earlier fixture JSON is not arbitrary-workload cancellation proof. The broader composed backend suite passed415 tests, skipped20 and deselected2 tests requiring online Google certificate retrieval. The21 frontend helper/contract tests passed. Typecheck and static build passed; the inherited remote API-base test build stayed local. Real loopback HTTP smoke served instructions/app/bridge with200 and a synthetic identity; external Google script was removed and CSP restricts transport to same origin. These are source/API/build proofs, not browser interaction or layout proof.

The financial oracle remains unresolved: current unchanged Esplanade engine IRR0.22212539391032182 differs from exact historical0.2251. Annual debt-service override is now honored and malformed schedules fail closed, but that does not resolve oracle source authority. Paused cancellation remains a backend gap; the frontend disables cancellation while paused and preserves observed state. No fixture can substitute for the Mono→C2→CRM/Hermes→human-reviewed workbook/document acceptance path.

This composition includes corrected cancellationv2, bridgev2 and the explicit-debt adapter patch based on appde824ba. It is an isolated review package, not a main commit or adopted architecture contract.
