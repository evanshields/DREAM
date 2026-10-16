# Explicit annual debt-service adapter repair

Base `de824ba1052bab509617b05f75b84515180b9937`, isolated `codex/beta-engine-input-proof`. The app accepts `ACQDealInputs.debt_service` and exposes it in `ACQRecalcRequest`, but the original boundary ignores it and always supplies derived payments to the vendored projector. A user can enter a payment schedule and receive computed-looking results for different payments.

The patch consumes a complete annual payment list at the existing Decimal seam, validates list shape, modeled-year count and finite nonnegative values, and replaces only `DebtServiceYear.debt_service`. It preserves the engine's year/phase/loan balance, refinance/sale timing and default path. It does not infer a new amortization/payoff from supplied payment totals, change the vendored calculator or tune financial numbers. Both typed `/api/recalc` and raw `/api/underwrite/v2` refuse malformed schedules with422.

Independent review caught raw-v2 strings/dictionaries being iterated as payments; list validation and three endpoint regressions were added. Read-only review otherwise accepted the replacement semantics. Review is not original Claude backend merge/deploy acceptance.

Verification:

- Original clean boundary, first 11 new tests: **10 failed,1 passed**; original first-year CFBT70,000 instead of requested50,000, bad schedules silently ignored. This is regression evidence, not the patched result.
- Patched targeted boundary/recalc/import-graph tests: **30 passed** before the three raw-shape tests.
- Final offline app/engine suite after review fixes: **415 passed,20 skipped,2 deselected**. The exclusions are the pre-existing invalid-Google-token tests requiring outbound certificate fetch;19 skips need absent Rayzor workbook,1 needs live Kimi. No installs or provider/network calls.
- Default Esplanade boundary output remains0.22212539391032182. Exact0.2251 acceptance remains **failed**. Original May15 financial-source reconciliation is a separate input/methodology gate. The precise manifest-referenced workbook was found and read safely via ZIP/XML: it has purchase37.5M/exit7.5%/cachedIRR0.18065955, different from the memo fixture34M/exit6%/claimed0.2251. The remaining input is the authoritative model/run/cash-flow export for the memo's oracle, or the financial owner's source-version ruling. Rayzor fixture and existing toleranced default tests remain unchanged.

Reproduce task-local `run-engine-input-tests.py` with the existing app `.venv/Scripts/python.exe`; `--baseline` preloads original app boundary and runs new regressions. The default mode runs the offline suite. Secrets/provider environment variables are removed from the child test process and outbound socket calls blocked except loopback.

Only `backend/engine_boundary.py`, new `backend/tests/test_explicit_debt_service.py` and this review note are scoped for review. Backend Python stays CRLF. No main write, business commit, push, PR, merge, auth/config change, production deploy or expected-number edit. Claude backend owner should review/apply this isolated patch independently of the active MCP fixwave.
