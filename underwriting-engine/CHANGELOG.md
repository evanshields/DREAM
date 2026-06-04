# Changelog — dream-underwrite (formerly shieldstone-master-uw)

Tracks every skill change with size delta. Per the leanness discipline encoded in [shieldstone-skill-improve/SKILL.md](../shieldstone-skill-improve/SKILL.md), the goal is a net-negative byte trend over time.

## Format

```
## YYYY-MM-DD — [description]

Source: [transcript file or commit message]
Before: [bytes]    After: [bytes]    Delta: [+/-N bytes]
Files: [paths]
Acceptance: [CONFIRMED N transcripts | CANDIDATE 1 transcript]

[bullet summary of changes]
```

---

## 2026-06-03 — Phase-12 memo reconciliation to canonical GS Residential format

Source: Evan meta-prompt. The Phase-12 reference documented an older memo layout (Sections I–VII,
Chart.js charts, Opportunities/Risks/Value-Creation cards, bare prompt() gate) that GS Residential
no longer ships; the real memos (Esplanade, Aviara) use a leaner structure. Reconciled by reading
`build_esplanade_acq_exempt.py` (template of record) + `build_aviara_acq.py` first.
- `references/14-html-memo.md` — rewritten (597 → ~150 lines, net -447). New canonical spec: name+
  email+password access gate (POSTs to /nda), six sections (#summary #sponsor #snapshot #market
  #comps #appendix), the four-scenario UW Snapshot table (Seller T-12 / T-3 Annl / UW Full Tax /
  UW Tax-Exempt), three-tab cell map (Pro Forma + UW Snapshot + Comps, not just Pro Forma),
  tax-framing rule, build/deploy loop. Removed: Risks/Opportunities/Value-Creation/Chart.js and the
  old MEMO_THESIS/RISK_FLAGS transcript slots.
- `SKILL.md` — Phase 12 sub-steps + QA gate rewritten to match (gate fields, six section ids,
  four-scenario snapshot ties to UW Snapshot tab, no charts/risks, tax-framing note).
Acceptance: CONFIRMED against 2 production build scripts (Esplanade-exempt, Aviara).

## 2026-06-03 — Engine improvements from the Envy Pompano Beach timed run

Source: live timed run of the Dream fast path on Envy Pompano Beach (ACQ), ~9 min wall-clock.
Engine independently reproduced Evan's "market-rate ACQ PASS, this is an EFB deal" conclusion
and his hand-run four-tier GPR result. Four gaps the run surfaced, now closed:
- `engine/acq_engine.py` — `InterestReserveSizer` (lease-up / Year-1 DSCR shortfall x buffer,
  rounded up — was a documented-but-unimplemented EFB Step-4 rule); `LeaseUpRamp` (derive the
  Year-1..N NOI ramp from the forensic vacancy + concession-burn-off curves, not a flat manual
  assumption); `FourTierOptimizer` (tier x bedroom GPR-max allocation under a fixed share
  constraint — market takes highest-rent units, affordable takes smallest-give-up units;
  reproduces Envy's -6.9% vs pure-market, matching Evan's ~-5 to -8%).
- `fastpath/populator.py` — `deal_identity_check` (template-fork carryover gate: compares the
  workbook's Pro Forma B2 asset name + B6 units against the spec; the Envy run hit a file that
  read "Aviara East Pompano" 228u — an unsaved/wrong-deal fork — and this now blocks loudly).
- Tests: `engine/tests/test_acq_leaseup_tiers.py` (4), `fastpath/tests/test_populator.py` (+2).
  Full suite 25/25.
Acceptance: CANDIDATE — validated vs Envy data; full Evan-Excel-vs-Dream reconciliation pending
his completed Claude-for-Excel underwrite + transcript.

## 2026-06-03 — Dream fast path: parallel analytical fan-out + Python calc engine + openpyxl populator

Source: Evan direction — "skill takes 90min-2hr, should take 30min; move toward Human-Out-of-the-Loop"
Files:
- `engine/lihtc_engine.py` — ADOPTED into git (was unversioned 1,684-line LIHTC/EFB engine in Downloads); + `engine/acq_engine.py` (NEW: ACQ levered cash flow, bridge→agency-refi per-period debt, exit-cap triangulation, IRR/EM/CoC, agency takeout sizing, state property tax, return hurdles); `engine/README.md`, `engine/requirements.txt`, `engine/tests/` (EFB Rayzor + ACQ Esplanade ground-truth validation, 13 tests)
- `fastpath/underwrite-spec.schema.json` — NEW the analysis→populate→memo contract
- `fastpath/agent-contracts.md` — NEW the 5 Wave-1 parallel subagent prompts + output slices
- `fastpath/populator.py` — NEW openpyxl populator (copy-not-original, blue-cells-only, refuses formula cells, structural diff, PENDING-RECALC guard) + tiered reconciliation gate; `fastpath/tests/` (6 safety-invariant tests on the real Rayzor template)
- `templates/field-mapping-acq.md` — stub → VERIFIED full cell map (read from Rayzor ACQ Mini Model; corrected tax-calc cells to S66–S71, return metrics B14–B17, etc.)
- `SKILL.md` — Environment table promotes Claude Code fast path to DEFAULT; new §Claude Code Fast Path (3 waves, CP-1/2/3 collapse, HITL/HOTL modes)
Acceptance: CANDIDATE — 19/19 tests pass; first live-deal timing vs 30-min target pending

- Engine ties to ground truth: ACQ IRR 22.21% vs 22.51%, EM 2.73 vs 2.72, exit value exact, DSCR series within 2%; EFB bond sizing + DSCR-on-interest reproduced. Decoded two ACQ conventions: exit on forward (sale+1) NOI; refi cash-out distributed to equity in refi year.

## 2026-05-15 — Phase QA gates + leanness discipline + Esplanade structural ports

Source: Esplanade transcript review + user direction to add per-phase QA gates
Files:
- `SKILL.md` — Universal Rule 3 rewritten (QA gate requirement); Phase 1-12 each got a "QA gate" block before its Checkpoint
- `templates/field-mapping-acq.md` — Pre-Population Formula Audit section ported from EFB version (Proposal #1)
- `references/14-html-memo.md` — Transcript-Aware Memo Build section added (Task B)
- `references/case-studies/README.md` — created (new folder pattern)
- `../shieldstone-skill-improve/SKILL.md` — leanness discipline rules 6-10 added
- `CHANGELOG.md` — created (this file)

Acceptance: CONFIRMED 1 transcript (Esplanade ACQ 2026-05-15). Items dependent on a 2nd transcript before permanent promotion are flagged in field-mapping-acq.md as CANDIDATE.

Change summary:
- **Structural:** 12 phase QA gates added (one per phase). Each gate is a 5-7 item checklist the skill must run BEFORE pausing for user confirmation. Output format: `✅`/`❌` per item.
- **Universal Rule 3 rewritten:** explicit QA gate requirement, no silent skip
- **ACQ formula audit ported:** same 5 bug-prone cells (S40, B66, B67, rows 31-32, row 78) now documented in ACQ field-map
- **Transcript-Aware Memo Build:** 4 named slots (MEMO_THESIS, MEMO_OVERRIDES, MEMO_AUDIT_TRAIL, MEMO_RISK_FLAGS) populate when transcript JSON is uploaded alongside .xlsx at Phase 12
- **Case studies folder pattern:** `references/case-studies/` created for extended worked examples that should NOT live in runtime context
- **Leanness discipline encoded:** sub-skill now mandates net-negative byte budget, ≤2 examples per rule, table-over-prose, prune-on-add

What was NOT done (explicitly deferred):
- 8 worked-example citations (Proposals #2-9 from PROPOSED_CHANGES_2026-05-15.md). Replaced by QA gates which are higher-leverage and recurring rather than read-once.

Size at this commit: **410.8 KB unzipped** master skill folder. This commit is **net additive** (~6-8 KB added by 12 QA gates + 1 audit port + transcript-aware memo section + CHANGELOG/case-studies scaffolding). Explicit user accept on the growth because QA gates are higher-leverage than the 8 worked-example proposals they replaced (gates run every deal; examples read once).

**Baseline for net-negative tracking starts here.** Going forward, every commit must show a delta ≤ 0 OR explicit user accept on the growth.

---

## 2026-05-17 — Phase 11a construction pipeline coverage (template-fork bug fix)

Source: surgical fix surfaced from Esplanade (Orlando) + Aviara East Pompano (Pompano Beach) — both ACQ workbooks shipped with Denton TX pipeline rows on Comps tab (rows 88–101), carryover from a Rayzor Ranch template fork that survived two deal forks. Per the leanness 2-deal rule: **CONFIRMED 2 transcripts** (same defect observed on two distinct deals).
Before: 434.2 KB     After: 441.4 KB     Delta: **+7.2 KB**
Acceptance: CONFIRMED 2 transcripts; explicit user accept on the surgical addition.
Files touched:
- `SKILL.md` Phase 11a — added 4th sub-step (was 3) for Market Upcoming Construction Pipeline (rows 88–101)
- `SKILL.md` Phase 11 QA gate — added 3 checkboxes (pipeline refreshed; no out-of-state rows; row 101 formulas intact)
- `references/10-comps-build.md` Tab Structure section — added Market Upcoming Construction Pipeline (Rows 88–101) subsection with cell map, sourcing rule, sort order, annotations, template-fork carryover check, row 101 off-limits rule
- `CHANGELOG.md` — this entry

Change summary:
- Phase 11a now enumerates FOUR Comps-tab sections instead of three. The fourth (construction pipeline, rows 88–101) was previously unmanaged — the skill was silent on it, so a workbook forked from a template would inherit whatever pipeline data the template had with no audit.
- New Phase 11a step mandates: read D90:F99 first, run template-fork carryover check (subject MSA vs. existing rows), overwrite with CoStar Full UW Report Construction data, write D/E/F only (B/C/row 101 are formulas, off-limits).
- Submarket discipline: if immediate submarket has < 10 deliveries, leave excess rows BLANK rather than padding with broader MSA. Only expand if user opts in.
- Annotations: ` — Affordable`, ` — SAME SUBMARKET`, ` — X.X mi from subject` for memo renderer to flag direct competitors.
- 3 new QA gate items make this verifiable per deal.

This is the second deal-level finding to qualify for CONFIRMED status under the 2-deal rule from `shieldstone-skill-improve/SKILL.md`. The Esplanade memo at `2026-05-esplanade-orlando-acq-exempt.html` happened to render correct Orlando pipeline because the renderer caught the mismatch and bypassed the model — but that was lucky. Both prior memos had wrong supply data in the model itself.

**Leanness audit:** net +7.2 KB. Justified — this is a recurring per-deal QA gate item (3 checkboxes run every deal) plus a structural addition to a phase that had a known silent gap. Earns its keep on the next forked workbook.

---

## 2026-05-16 — Round 2 applied: REST API + OpEx integration

Source: Round 2 proposals NEW-1 through NEW-5 from PROPOSED_CHANGES_2026-05-15.md
Before: 410.8 KB     After: 434.2 KB     Delta: **+23.4 KB**
Acceptance: CONFIRMED 1 session (verified live API 2026-05-16) + explicit user accept on the growth
Files touched:
- `SKILL.md` — Phase 4 source chain rewritten (REST API #1, MCP deferred); "When to Read" table updated
- `references/00-api-reference.md` — **NEW FILE** (consolidated canonical API doc)
- `references/03-efb-revenue.md` — 1-line cross-reference + Data Source column endpoints updated
- `references/04-acq-revenue.md` — 1-line cross-reference at top
- `references/14-html-memo.md` — API-driven data freshness block added
- `references/15-opex-agency-triangulation.md` — REST API fast path block added at top
- `CHANGELOG.md` — this entry

Change summary:
- **NEW-1 (correctness):** SKILL.md Phase 4 no longer points underwriters at the broken MCP-first chain. New chain: REST API → MCP (deferred, Windows OAuth bug `ofld_63e310c0724bb7ca`) → local CSV → manual paste.
- **NEW-2 + NEW-4 consolidated:** instead of duplicating ~30 lines of API usage prose across 03-efb-revenue and 04-acq-revenue, created a canonical `00-api-reference.md`. Two reference files get 1-line cross-references. Net: ~+6 KB for the new file vs ~+6 KB across two files if duplicated. **Same byte cost, but creates a single source of truth.** Future API doc updates touch one file, not three.
- **NEW-3:** Phase 8 OpEx triangulation gets a REST API fast-path callout at the top of 15-opex-agency-triangulation.md. The markdown stays canonical (single source of truth); the API is a read-path that serves the same data.
- **NEW-5:** Phase 12 memo build now documents the API call pattern for live data freshness in memo footnotes.

Out of scope (kept untouched):
- shieldstone-efb-uw skill (coexists, not modified)
- 00-api-reference.md content reflects API as deployed 2026-05-16; will need refresh if endpoints / auth change

Bundle size delta to be measured by repackage-skill.py.

**Leanness audit:** this commit is net additive but creates the structural foundation (00-api-reference.md as single source) that enables future commits to be net-negative. The next API doc revision should not grow the skill at all — it'll edit the one canonical file.

---

---
