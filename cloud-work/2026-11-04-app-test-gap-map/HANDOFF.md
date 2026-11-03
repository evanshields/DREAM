# HANDOFF: app-test-gap-map

- Output: `docs/research/2026-11-04-app-fail-closed-test-gap-map.md` (report only, no code, test or config changed).
- Backend suite ran: 550 passed, 1 skipped (whole repo 693 passed, 20 skipped). Frontend has no test runner; only tsc and build ran (both exit 0).
- Biggest finding: deals list and detail API return headline numbers for `gate_failed` deals (probed), and the live-calc hook keeps old numbers after an error.
- HOLD rows (snapshot panel, evidence viewer): F06-F08, F10, F21-F23, F27, B86, B91, B94. Do not write tests there yet.
- Not mapped: root `src/`, `archive/`, `underwriting-engine/`. B26 and B55 are unprobed.
- Probe scripts lived in scratchpad and are not committed.
