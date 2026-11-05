# HANDOFF: app-test-gap-map (repair of PR 11)

- Output: `docs/research/2026-11-04-app-fail-closed-test-gap-map.md` (report only, no code, test or config changed).
- Repair on the same branch after the Argon red team. Five defect families fixed: CRM version coverage (contact paths now covered, item paths split out as B76 and B77), export claim (B46 is a missing assertion at `test_export_excel.py:153-164`), census (one boundary, all B and F rows in tables, recounted with Python: 85 backend, 29 frontend, 114 total, B40b now a table row), missing path (F29 main recalc error keeps old metrics), wrong IDs and sources (extra-high line now says B55, B55 cites `wave0.py:105-129` and the imported `CriticalInputs` contract, B54, B57, B64 and `runner.py:202` line numbers corrected).
- Backend suite ran earlier: 550 passed, 1 skipped (whole repo 693 passed, 20 skipped). Frontend has no test runner, only tsc and build ran (both exit 0). Not rerun for this text-only repair.
- Biggest finding unchanged: deals list and detail API return headline numbers for `gate_failed` deals (probed), and the live-calc hook keeps old numbers after an error.
- HOLD rows (snapshot panel, evidence viewer): F06-F08, F10, F21-F23, F27, B86, B91, B94. Do not write tests there yet.
- Not mapped: root `src/`, `archive/`, `underwriting-engine/`. B26 and B55 are unprobed.
- Probe scripts lived in scratchpad and are not committed.
