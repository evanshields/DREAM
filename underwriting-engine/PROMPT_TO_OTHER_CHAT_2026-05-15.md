# Master UW Skill Improvement Briefing — Esplanade ACQ Underwrite (2026-05-15)

You are picking up a skill-improvement task from a separate Claude session. Read this whole brief, then propose diffs and scaffold one new sub-skill. **Do not auto-edit skill files** — propose, wait for approval, then apply.

---

## Mission

Improve the `shieldstone-master-uw` skill at [c:\Users\evana\shieldstone_os\.skills\shieldstone-master-uw\](c:/Users/evana/shieldstone_os/.skills/dream-underwrite/) based on a complete 11-phase Esplanade ACQ underwrite that ended 2026-05-15. The prior session logged 30 explicit skill improvement items to the workbook's Claude Log tab (turns 82–89). Your job: turn those 30 items into precise skill-file diffs, plus scaffold a new self-improving sub-skill that can repeat this exercise on future transcripts.

---

## Source artifacts

You have local-disk access to all of these.

| Artifact | Path |
|---|---|
| **Claude-for-Excel transcript** (JSON, 331 msgs, 330K chars) | `C:/Users/evana/Downloads/evan-2026-05-15T21-10-04-766Z.json` |
| **ACQ Mini Model workbook** (12 sheets; **Claude Log has 89 rows of audit trail**) | `H:/My Drive/_Acquisitions Shieldstone/3. ACTIVE Deals/3.10.26 - Esplanade Apartment Homes (Orlando, FL)/Esplanade Apartments - Shieldstone ACQ Mini Model (5.15.26).xlsx` |
| **Master UW skill** (the target of all edits) | `c:/Users/evana/shieldstone_os/.skills/dream-underwrite/` |
| **Reference files** inside the skill | `.skills/dream-underwrite/references/01-deal-routing.md` through `17-trigger-vocabulary.md` |
| **Template mapping files** | `.skills/dream-underwrite/templates/field-mapping-acq.md`, `field-mapping-efb.md` |
| **Coexisting EFB-only skill** | `c:/Users/evana/shieldstone_os/.skills/shieldstone-efb-uw/SKILL.md` (reference only; don't edit) |
| **Coexisting comps-build sub-skill** (called mid-session at transcript msg[266]) | The prior session injected this externally; check whether a local copy exists at `c:/Users/evana/shieldstone_os/.skills/shieldstone-comps-build/` or similar. If absent, the master skill's Phase 11 should absorb its prescriptions directly. |
| **Production Phase 12 build scripts** (for context on memo output) | `c:/Users/evana/shieldstone_os/shieldstone_acquisitions/deal-memos/build_*.py` and the newly built `2026-05-esplanade-orlando-acq.html` |

---

## Source-of-truth pointers (read these first; everything else is derived)

### From the workbook's Claude Log tab

`openpyxl.load_workbook(path, data_only=True)['Claude Log']` — 89 rows. **Read columns A (turn #), C (User Request), D (Action), E (Details), F (Outcome) for rows 81–89.** That's where the 30 improvements live, verbatim, with worked examples from the Esplanade underwrite.

| Workbook row | Turn # | Content |
|---|---|---|
| 81 | 81 | Final deal state summary (Esplanade reads, bugs caught) |
| 82 | 82 | Phase 1 (T-12 spread) — items 1–4 |
| 83 | 83 | Phase 2 (Rent roll spread) — items 5–6 |
| 84 | 84 | Phase 3 (Pro Forma assumptions) — items 7–8 + 5 template bug specs |
| 85 | 85 | Phase 4 (Unit mix + NOAH rule) — items 9–11 |
| 86 | 86 | Phases 5–7 (Other Income, Vacancy, OpEx) — items 12–16 |
| 87 | 87 | Phases 8–10 (Agency triangulation, Tax, Debt+DSCR) — items 17–21 |
| 88 | 88 | Phase 11 (Comps + UW Snapshot) — items 22–26 |
| 89 | 89 | Cross-cutting — items 27–30 (template discipline, context, logging, pushback) |

### From the transcript JSON

Read the full file, but these specific message indices are the high-leverage pushback / decision moments:

| msg[N] | Role | What's there |
|---|---|---|
| 132 | user | **NOAH override** — user rejected the 80% AMI-tier upside thesis because in-place rents already sit at ~70% AMI. Triggered total Phase 4 rebuild. |
| 188 | user | Insurance + property tax fixes — UW insurance at $723/u (20% below T-12 $904/u), tax breaker switched off, Yr2+ reassessment at 80% of PP. Returns went from inflated 41% IRR to clean 22.5%. |
| 252 | user | UW Snapshot T-3 column was broken (hardcoded Rayzor OpEx + broken SUMPRODUCT). Full rebuild required. |
| 264 | user | User corrected scope on Comps tab build (assistant overstated complexity). Triggered the `shieldstone-comps-build` sub-skill injection. |
| 266 | user | Sub-skill injected externally via container upload — `shieldstone-comps-build` prescriptions. |
| 288 | user | **7 Phase 11 failures listed in one message**: (a) C10:C25 / J10:J25 formatting goofy, (b) no sales-comp weighting methodology shown, (c) D8 subject still "Resia Razor Ranch", (d) Row 35 rent subject leftover Rayzor, (e) affordability anchors interspersed instead of bottom-anchored, (f) LIHTC rows weighted >0 (should be 0), (g) thin vintage coverage. |
| 308 | user | Vintage anchor gap request — backfill from 10-mi radius file because Park Central submarket had only 2 modern (2015+) comps. |

The Esplanade transcript **does not include Phase 12** (memo build). Phase 12 was done in a separate session on 2026-05-15 and produced [shieldstone_acquisitions/deal-memos/2026-05-esplanade-orlando-acq.html](shieldstone_acquisitions/deal-memos/2026-05-esplanade-orlando-acq.html). That memo was built from the .xlsx only, blind to the transcript narrative — which is one of the gaps you're being asked to close.

---

## The 30 improvements, pre-classified

Don't re-derive these. The prior session logged them; read turns 82–89 of the Claude Log for verbatim text + worked examples. This is the grouping a prior reviewer assigned them. Treat it as a starting point, not gospel — challenge any classification that doesn't hold up when you actually read the Log entry.

### Group A: Already in skill — reinforce, do not change (6 items)
Confirmed paid off in the Esplanade underwrite. Worth citing the Esplanade example in the existing rule text but no structural change needed.

- **Whisper-bid sanity check** (Phase 3) — caught Esplanade's +5% premium vs sales comp wtd avg. Cite in [references/05-pro-forma-assumptions.md] or wherever the rule lives.
- **Universal Rule 8 template-formula audit** — caught 5 inherited Rayzor template bugs (S40 monthly→annual, B66, B67, rows 31-32, row 78 DSCR). Add these 5 specific bug specs to the audit checklist in `templates/field-mapping-acq.md` §Pre-Population Formula Audit.
- **Universal Rule 10 context snipping** — needed twice in the Esplanade session (msg[154], msg[286]). Reinforce: it's not optional.
- **Universal Rule 11 Claude Log every turn** — paid for itself; the 30 improvements only exist because the Log was kept current.
- **Universal Rule 12 trust user pushback** — msg[288] is the canonical example. 7 issues listed in one message after assistant declared "Phase 11 Complete." Cite as the worked example in the rule text.

### Group B: In skill but under-specified — tighten (4 items)

| Item | Location | Tightening |
|---|---|---|
| Phase 1 "audit before write" gate | [references/11-data-extraction.md] | Mandate: `parse with openpyxl → verify monthly columns present → roll up to col O → compare to source subtotals within $1 → only then write`. Currently the skill says "spread the T-12" without the gate. |
| Phase 8 OpEx agency triangulation | [references/15-opex-agency-triangulation.md] | Move from "layered on top of Phase 7" to a required deliverable (per-line-item table with manual citations). It's being skipped. |
| Phase 11 affordability anchor placement | [references/10-comps-build.md] | Spec: anchors live at the **bottom** of the rent comp display, weight=0 via conditional `=IF(type='Affordability',0,equal_weight)`. Don't intersperse. |
| Phase 11 subject row dynamic linking | [references/10-comps-build.md] | D8 (sales subject) and Row 35 (rent subject) MUST be formula references to Pro Forma cells, never hardcoded. msg[288] shows D8 was still "Resia Razor Ranch" through end of Phase 11 because formulas weren't enforced. |

### Group C: Genuinely new — add (7 items)

| Rule | Where to put it | One-liner |
|---|---|---|
| **NOAH detection (Phase 4)** | [references/04-acq-revenue.md] §Four-Tier Mixed-Income Structure | Before allocating 80% AMI upside, compute `in-place rent / 80% AMI ceiling` per unit type. Ratio > 0.85 → flag as NOAH; 80% AMI is not upside; only MLA and HAP at FMR are. Highest-leverage addition. |
| **HAP achievability ramp** | [references/03-efb-revenue.md] §HAP Revenue Optimization (also applies to ACQ when HAP tier is used) | Default Yr1=50%, Yr2=75%, Yr3+=90% capture rate, OR absorb in Yr1 vacancy curve. Currently skill assumes stabilized HAP from day one. |
| **Senior DSCR bridge↔refi switching** | [templates/field-mapping-acq.md] §Pre-Population Formula Audit | Row 78 formula must be `IF(year ≤ bridge_term, bridge_DS, refi_DS)`. Naive `=NOI/-SUM(F29:F30)` zeros out post-bridge. Add as known-buggy cell. |
| **Sales comp weighting collapse detector** | [references/10-comps-build.md] §Sales Comps | When max/min weight ratio < 1.5x, auto-propose the bucket-tier manual override. Recency-only decay flattens when all comps are within 12-18 months. |
| **Vintage anchor 10-mi backfill** | [references/10-comps-build.md] §Rent Comps | When submarket file has <3 comps from target vintage, pull 3-5 Class A anchors from a 10-mi radius file at weight=0 for visible bracketing. |
| **FL insurance floor post-Ian** | [references/05-expenses.md] §Insurance | Floor is $900-1,200/unit for FL multifamily. Underwriting below T-12 requires explicit override + agency-risk flag. Esplanade UW'd $723/u vs T-12 $904 — should have been louder. |
| **Replacement reserve by vintage** | [references/05-expenses.md] §Replacement Reserves | <10yr $250, 10–15yr $300, 15–20yr $350, 20+yr $400. Current skill defaults $250 across the board, which is wrong for older stock. |

### Group D: Cross-cutting (already-in-skill enforcement items)
- Items 27–30 from Turn 89 (no new tabs/rows; snip every phase; log every turn; trust pushback) — these are already Universal Rules. Cite Esplanade examples in each rule.

### Friction signal worth investigating
User had to inject `shieldstone-comps-build` mid-session at msg[266]. Phase 11 has 17 mentions vs Phase 6's 4 (the highest of any phase). Two options to propose:

1. **Absorb** the comps-build sub-skill's prescriptions into [references/10-comps-build.md] verbatim, retire the sub-skill.
2. **Elevate** comps-build to a first-class skill and have master-uw Phase 11 explicitly delegate to it via cross-reference.

Check whether `c:/Users/evana/shieldstone_os/.skills/shieldstone-comps-build/` exists and read it before recommending. If it exists locally, lean toward absorb. If it was a one-off externally-uploaded skill, lean toward elevate-and-keep.

---

## Your three tasks (in priority order)

### Task A — Apply skill improvements (priority)

Produce a structured diff proposal:

```
## Proposal #1
- File: .skills/dream-underwrite/references/04-acq-revenue.md
- Anchor: §Four-Tier Mixed-Income Structure, after the existing bullet "MLA / corporate rental"
- Action: INSERT
- Source citation: Claude Log Turn 85 / msg[132] of transcript
- Rationale: NOAH detection rule prevents the highest-leverage error class (treating 80% AMI as upside when in-place is already there)
- Proposed text:
  ```markdown
  **NOAH detection gate (run before allocating tier mix).** Before assigning any 80% AMI upside tier, compute `in-place rent / 80% AMI ceiling` per unit type from rent roll vs. HUD MTSP. If the ratio > 0.85 for any bedroom type, the asset is naturally occurring affordable (NOAH) for that type — 80% AMI is not upside, only MLA (capped at FMR) and HAP (at FMR) are. Confirm with user before proceeding. Esplanade example: in-place $1,871 vs LIHTC 80% AMI $2,182 = ratio 0.86 → NOAH confirmed; 80% AMI tier eliminated; rebuilt with MLA + HAP + Classic/Renovated market.
  ```
```

Repeat for every Group B/C item (and the Group A items that need worked-example citations added). Order them by impact (NOAH first; FL insurance floor second; etc.). Save the full proposal to `c:/Users/evana/shieldstone_os/.skills/dream-underwrite/PROPOSED_CHANGES_2026-05-15.md`. **Do not edit the skill files directly until the user reviews the proposal.**

### Task B — Phase 12 memo transcript-ingestion enhancement

The Phase 12 memo built today ([shieldstone_acquisitions/deal-memos/2026-05-esplanade-orlando-acq.html](shieldstone_acquisitions/deal-memos/2026-05-esplanade-orlando-acq.html)) reads the .xlsx for numbers but is blind to the narrative reasoning captured in the Claude Log. Propose a small enhancement:

- **Reference doc:** add a section to [references/14-html-memo.md] titled "Transcript-Aware Memo Build" specifying that, when a transcript JSON is available alongside the .xlsx, Phase 12 reads Claude Log columns C-F (or the transcript's Phase 11 wrap-up summary) and injects:
  - `MEMO_THESIS` — the deal-level NOAH/value-add framing
  - `MEMO_OVERRIDES` — explicit user decisions (insurance UW, tax breaker, vacancy curve, IR sizing)
  - `MEMO_AUDIT_TRAIL` — list of template bugs caught and patched
  - `MEMO_RISK_FLAGS` — risks the assistant explicitly surfaced for the user (e.g., HAP achievability ramp, insurance below T-12)
- **Build script template:** show what the variable block should look like in a per-deal `build_<slug>.py` when these slots are filled. Don't rewrite Esplanade's; just give a worked example block for the next deal.

### Task C — Scaffold the self-improving sub-skill

Create `c:/Users/evana/shieldstone_os/.skills/shieldstone-skill-improve/SKILL.md` plus one Python extractor `scripts/improve-from-transcript.py`. Specs:

- **Input:** one or more transcript JSONs + optionally the matching .xlsx (for Claude Log reading)
- **Output:** a `PROPOSED_CHANGES_<date>.md` file with the same diff format as Task A
- **Extractor mechanics:**
  - Pulls Claude Log turns 81+ (or whatever the "skill improvements" marker is) verbatim
  - Greps transcript user messages for pushback signals (regex on `wrong|stop|fix|actually|not right|still wrong|broken|missed|skipped`)
  - Counts phase mentions to produce a friction heatmap
  - Identifies cells the user manually overrode (Claude Log col E "user manual change" or similar)
- **Guardrails (must be encoded in the SKILL.md):**
  1. Never auto-write skill files — always produce a proposal that the user approves
  2. A rule needs to appear in ≥2 transcripts before being promoted to permanent; single-deal observations get logged as "candidate" with source citation
  3. Every accepted change writes a row to `.skills/dream-underwrite/CHANGELOG.md` with: date, source transcript filename, rule summary, files touched
- **First validation case:** feed the Esplanade transcript + workbook back into the new sub-skill. It should independently surface the same 30 items the prior session manually logged. If it surfaces fewer than ~20, the extractor is too narrow. If it surfaces >50, it's too noisy.

---

## Output format expected

For Task A: a single markdown file `PROPOSED_CHANGES_2026-05-15.md` with one block per proposal, in the structure shown above. Include a summary table at the top with columns: # / Priority (High/Med/Low) / File / Action / One-line description.

For Task B: a follow-up section in the same file titled "Phase 12 Memo Enhancement Proposal" with the proposed reference-doc text and a worked example variable block.

For Task C: actual file creation (the new sub-skill is greenfield, not a modification). Confirm before creating with a one-paragraph design summary.

---

## Guardrails

- **No auto-edits to the master skill.** Propose, wait for user approval, then apply. The user wants to review every change.
- **Don't bloat.** The master skill is already 17 reference files. Prefer tightening existing text over adding new files. Only add a new reference file when the topic is genuinely orthogonal to existing references.
- **Cite sources.** Every proposed rule must cite either a Claude Log turn number or a transcript msg[N] index. No uncited rules.
- **Don't touch the EFB-only skill** at `.skills/shieldstone-efb-uw/SKILL.md`. It coexists intentionally.
- **Watch for hook noise.** This environment has a Git-commit-related hook that logs to its own output but doesn't block your work; ignore its "condition not met" messages.

---

## Quick start

```python
# Sanity check: confirm you can read both source artifacts
import openpyxl, json

# 1. Workbook
wb = openpyxl.load_workbook(
    r'H:/My Drive/_Acquisitions Shieldstone/3. ACTIVE Deals/3.10.26 - Esplanade Apartment Homes (Orlando, FL)/Esplanade Apartments - Shieldstone ACQ Mini Model (5.15.26).xlsx',
    data_only=True
)
log = wb['Claude Log']
print(f"Claude Log rows: {log.max_row}")  # should be 89
print(f"Turn 82 action preview: {str(log.cell(82, 4).value)[:80]}")

# 2. Transcript
with open(r'C:/Users/evana/Downloads/evan-2026-05-15T21-10-04-766Z.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f"Messages: {len(data['messages'])}")  # should be 331
```

If both lines run clean, you have everything you need. Start with Task A.
