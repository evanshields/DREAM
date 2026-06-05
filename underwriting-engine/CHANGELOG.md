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

## 2026-06-05 — Wave 2: engine wiring + new build + pinned UW-Snapshot fix (Envy 3-way forensic)

Source: same backlog (`shieldstone_acquisitions/underwrites/envy-pompano/_compare/`). Wave 2 closes
the **analyst-divergence gap** — it makes the engine DO the tedious analytical work humans diverged
on (four-tier optimization, interest reserve, lease-up ramp), adds the two genuinely net-new builds
(FL tax range, reprice solver), and lands Evan's pinned UW-Snapshot scope fix. Produced via a hybrid
Opus/Sonnet **multi-agent workflow** (schema-first → 3 parallel independent items → Epic C synthesis
design + tests); the workflow DRAFTED code and the parent applied it carefully to the shared
`acq_engine.py` in-context (avoiding six agents racing one file).

**Two decisions locked with Evan 2026-06-05:** (1) BL-04 EFB auto-route = DETECT + RECOMMEND only,
the fast path STOPS at CP-1 (`stop_at_cp1` always true) — the engine never auto-builds the EFB model;
(2) BL-13 FL tax = assume `agent-marketdata` supplies the county method + assessed value, flat-ratio
kept as the documented default.

Backlog closed: **BL-04** (four-tier wired + NOAH detection + EFB route recommendation), **BL-10**
(exit-cap == HIGHEST gate), **BL-11** (interest-reserve-net DSCR), **BL-12** (data-derived lease-up
ramp), **BL-13** (FL property-tax range estimator), **BL-15** (LTV formula-integrity gate), **BL-16**
(RUBS contra-sign + recovery-jump gate), **BL-19** (reprice / goal-seek solver), **BL-08** (pinned
UW-Snapshot scope fix).

Files:
- `engine/acq_engine.py` (+~940) — ALL ADDITIVE, no edit to the validated SeniorDebtCalculator /
  ACQCashFlowProjector / ExitCapTriangulator math. New: `PropertyTaxRangeEstimator` (BL-13, low/point/
  high + county-method/flat-ratio + FL Save-Our-Homes); `RepriceSolver` (BL-19, bisection goal-seek on
  price, NaN/Inf-guarded, reuses the projector via a `price_to_inputs` callback — never reimplements
  cash-flow math); `detect_noah` + `build_efb_route_signal` + `EFBRouteSignal` (BL-04, stop_at_cp1
  always true); `reserve_adjusted_dscr` (BL-11, no-op when no shortfall years → Esplanade unchanged);
  `exit_cap_gate` (BL-10), `ltv_gate` (BL-15), `rubs_sign_gate` (BL-16). Module-level `import math` +
  `Callable` added. Fixed a BL-13 draft edge case: county-method high could collapse onto point when
  the assessed value == PP×hi_ratio; added a strict ±3% reassessment band for non-flat states (GA
  statutory flat preserved).
- `fastpath/underwrite-spec.schema.json` (+132) — 9 additive fields: `meta.efb_route_signal`;
  `qa.{exit_cap_gate,ltv_gate,rubs_sign}`; `headline_metrics.{tier_allocation,interest_reserve,
  lease_up_ramp,property_tax_range,reprice}`. Field names mirror the engine dataclasses 1:1. Inserted
  surgically (compact style preserved — no reformatting churn).
- `SKILL.md` (+55) — Phase 4 BL-04 NOAH/EFB hard-stop note; Phase 7 BL-16 RUBS gate; Phase 10
  BL-10/BL-15/BL-11 notes; **BL-08 Phase-11b scope fix** (Snapshot = revenue→OpEx→NOI→cap only; DSCR→
  Checks, returns/exit→Pro Forma; QA-gate + checkpoint rewritten).
- `fastpath/agent-contracts.md` (+29) — Wave-2 synthesis steps 1–7b rewired to CALL the built classes
  + emit the spec fields; step-10 reprice; CP-1 surfacing adds the new gates + the BL-04 halt.
- `references/12-uw-snapshot.md` (+28) — **BL-08**: removed Capital Stack/Debt Service/Returns/Bond/
  Exit/Sensitivity rows from the structure table; scope-boundary note; Financing/Returns/Exit sanity
  sections relabeled CHECKS-TAB / PRO-FORMA-TAB; Final Metrics Audit reframed as a chat summary.
- `references/06-property-tax.md` (+1), `templates/field-mapping-acq.md` — BL-13 estimator pointer;
  BL-08 Snapshot-scope note.
- Tests: NEW `test_property_tax_range.py`, `test_reprice_solver.py`, `test_wave2_epicc.py` (+83
  cases). **Full suite 144/144** (was 61; the Esplanade/Rayzor ground-truth tests + all Wave-1 gates
  unchanged — no regression).
- `fastpath/wave2-workflow.js` — the orchestration script that produced this wave (build artifact /
  reproducibility record, not a runtime path).

Acceptance: CANDIDATE — validated against the Envy forensic data + the Esplanade ground truth (engine
additions are no-ops on the stabilized regression deal: reserve sizes to $0, no NOAH signal, no
reprice trigger). Behavioral: a below-hurdle deal returns a clearing price; a lease-up Y1 DSCR clears
the reserve floor while a stabilized series is unchanged; a non-max B79 / positive S54 / literal B52
each fail their gate; the EFB recommendation halts at CP-1 without building the EFB model.

**Leanness audit:** net additive (engine is the bulk; ~+5KB doc). Explicit accept on the growth —
six of the items wire ALREADY-BUILT (Wave-1-verified) classes into the synthesis so the engine
finally does the four-tier/reserve/ramp work that drove the human divergence; the gates each prevent
a forensic-confirmed defect; BL-08 removes spec scope (net-negative intent on the Snapshot).

## 2026-06-05 — Wave 1: hard-gate layer (Envy 3-way forensic — the autonomy floor)

Source: `shieldstone_acquisitions/underwrites/envy-pompano/_compare/` (SKILL_IMPROVEMENT_PLAN.md +
skill-backlog.json, 19 items). The Envy three-way forensic proved the bug is **process discipline,
not analytical skill** — the same skill produced 214 vs 244 units, opposite OpEx signs, a 9.5pp IRR
spread; nearly every shipped defect was a skill-fixable hard-gate miss. Wave 1 lands the 6 gate
items (5 of them autonomy prerequisites): the DREAM app / Shieldstone Hermes cannot safely run
unattended without these.

**Two decisions locked with Evan 2026-06-05:** (1) BL-01 unit gate = pass-with-flag on summary-tab
match when no 2nd source (single-source WARNING at CP-1), hard-block only on segment/exclusion/
disagreement; (2) BL-07 auto-patch = S40 + row-78 ONLY (the rest verdict-only).

Backlog items closed: **BL-01/09** (rent-roll unit-count reconcile), **BL-02/14** (deal-identity
hard gate), **BL-03** (fee-bounds), **BL-05** (CP-2 identity gate + self-render), **BL-06**
(non-collapsible gates), **BL-07** (named formula audit + S40/row-78 auto-patch).

Files:
- `engine/acq_engine.py` (+316) — NEW stateless validators, no edit to the validated classes:
  `assert_fee_bounds`/`FeeBoundsResult` (BL-03: 0.05 sentinel + [0.005,0.01] bounds);
  `UnitCountReconciler`/`UnitCountResult` (BL-01/09: status+use classify, 2nd-source/summary-tab
  reconcile, segment + user-exclusion block); `formula_integrity_check`/`FormulaAuditResult` (BL-07:
  named PASS/PATCH verdict for S40/B66/B67/rows31-32/row78 every run; S40+row-78 auto-patch).
- `fastpath/populator.py` (+292) — extended `deal_identity_check` (foreign-tab via KNOWN prior-deal
  tokens, #REF!/#NUM! literal sweep skipping Claude Log prose, vintage-note check; `strict_residuals`
  for Phase-11 re-verify — calibrated to NOT false-positive on the Rayzor template's seller-doc tabs
  + blank-Checks #REF!); `populate()` guards (identity-block, fee-bounds refuse, unit-count refuse,
  patch_log) + new WriteReport fields; `reconcile()` identity gate (raises `IdentityMismatchError`,
  never a transcript fallback) + `reconcile_self_render()` (BL-05 HOTL floor).
- `fastpath/underwrite-spec.schema.json` (+40) — `meta.deal_identity`, `qa.fee_bounds`, `qa.unit_count`.
- `SKILL.md` (+57) — Phase 2 unit-count HARD GATE; Phase 3 fee-bounds gate + 5 named formula
  verdicts; Universal Rule 3 non-collapsible-gates rule (BL-06); Phase 11 identity re-verify + comps
  carryover promoted advisory→HARD block; Wave-0 identity-gated ground-truth + CP-2 self-render prose.
- `fastpath/agent-contracts.md` (+35) — agent-rentroll (classify+reconcile+exclusions), agent-
  assumptions (FAIL on 0.05), Wave-2 (formula verdicts, identity-gated CP-2, self-render, non-collapse).
- `templates/field-mapping-{acq,efb}.md` — BL-07 named-verdict + auto-patch note; B45/B6 gate notes.
- Tests: NEW `test_fee_bounds.py` (5), `test_unit_count_reconcile.py` (7), `test_formula_audit.py`
  (7), `test_deal_identity_sweep.py` (7), `test_self_render_reconcile.py` (4); extended
  `test_populator.py` (+6). **Full suite 61/61** (was 25; ground-truth Esplanade/Rayzor tests
  unchanged — no engine regression).

Acceptance: CANDIDATE — validated against Envy forensic data + the real Rayzor ACQ template (no
false-positive on its seller-doc tabs / blank-Checks #REF!). Behavioral: a marina-slip segment
BLOCKS (not 244); a 0.05 ACQ fee is refused; an Aviara/foreign-tab/#REF! workbook fails identity;
a no-external-ground-truth run self-renders, never transcript-compares.

**Leanness audit:** net additive (~+5KB doc, new gate code + tests). Explicit accept on the growth —
these are recurring per-deal HARD gates that each prevent a defect that actually shipped in the
forensic (244 count, 5% fee, Aviara contamination, collapsed single-pass), and three are the
prerequisites for any unattended HOTL run. Higher-leverage than any byte they cost.

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
