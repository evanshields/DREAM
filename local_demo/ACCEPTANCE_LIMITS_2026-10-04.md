# Local sample acceptance limits

The externally reviewed v1 sample remains a synthetic local app proof. This versioned note separates three different cancellation mechanisms.

| Mechanism | Observed result | Practical limit |
|---|---|---|
| App asynchronous thread plus fixed StubAnalysts | Cooperative cancel acknowledged, then actual `cancelled` after the fixed analyst returns and the worker checks the flag | No child process exists. The proof does not interrupt an arbitrary blocking analyst, kill a process tree, or certify arbitrary workload cancellation. |
| App paused input/CP-1 job | Flag can be acknowledged without an active worker transition | The sample UI disables cancellation while paused. Retain actual paused/CP-1 state; do not display fabricated completion. |
| MCP Dispatcher on Windows with an owned grandchild | Separate test failed: direct child dead, job cancelled and lock free, but the owned grandchild alive | The helper's documented Windows fallback handles direct processes. Do not treat the app fixture or direct-child MCP pass as Windows descendant safety. The test safely cleaned only its acquired owned process HANDLE. |
| MCP native Linux process group | Two real descendant tests authored; unrun here | Current published MCP d1484de has 149 passing Linux package/component tests, including direct TERM-ignoring process-group helper coverage. Our two full Dispatcher descendant cases need owner adoption and exact-source execution; the component pass does not establish that integration proof. |

Use the local sample for fixed ACQ/EFB submission, missing-input questions/resume, identical-payload replay, polling, CP-1 stop and read-only bridge fault cases. Leave documents empty. Provider extraction, real CRM/Hermes, exports and CP-1 approval are unavailable. The public fixture identity is not a production credential.

App replay currently uses a global key before owner derivation. A separate authenticated synthetic probe observed changed payloads and another synthetic principal returning the original job under that key. Team-sharing/permission policy remains an architecture decision; this is not a production authorization assessment or permission for a security/schema change.

The app and MCP have separate job IDs, state vocabularies and resume rules. C2 `done` does not imply app `awaiting_cp1`, financial approval, a Mono workbook or a human-reviewed document. Hermes text is a conversational claim, never numerical authority. The bridge fixture projects no metrics or narrative.

Known financial limit: unchanged engine Esplanade IRR 0.22212539391032182 differs from historical exact 0.2251. Existing tolerance-test passes do not clear that exact requirement. Full workbook delivery also waits on the approved Mono template/general loader and human review.

These notes change no worker logic, cancellation API, credentials, profiles or financial expectations. The original v1 patch remains immutable. The documentation v2 checkout carries the same runtime plus this text clarification.
