# Proposed Changes — `shieldstone-master-uw` (post-Esplanade review, 2026-05-15)

## Briefing context

Esplanade Apartment Homes (186 units, Orlando FL, 2007 vintage, NOAH) completed an 11-phase ACQ underwrite on 2026-05-15. The Claude Log tab of the workbook captured 30 explicit skill-improvement items at turns 81-89. A briefing document instructed a separate session to turn those 30 items into precise diffs.

**Critical finding before drafting proposals:** 29 of the 30 structural changes were ALREADY shipped in this session's prior 4 commits (`6454bf7`, `b0dced7`, `b7171c5`, `14c9f1e`, pushed earlier today). The briefing was authored without knowledge of that work. The proposals below focus on what's genuinely needed:

- 1 structural gap (Item 7 audit lives in EFB field-map but not ACQ)
- 9 worked-example citations (anchor existing abstract rules to concrete Esplanade outcomes)
- 1 Phase 12 transcript-aware enhancement (Task B)
- 1 sub-skill scaffold (Task C, separate folder)

No proposals to re-do the structural work that's already in.

---

## Coverage matrix: 30 items vs. shipped commits

| # | Item | Commit | Status |
|---|---|---|---|
| 1 | Never write monthly from annual; openpyxl-first parsing | `b0dced7` | Shipped (references/11-data-extraction.md §Parsing Protocol) |
| 2 | Explicit mapping dict, unmapped count = 0 gate | `b0dced7` | Shipped |
| 3 | Col O rollup tie to source subtotals, $1 fail | `b0dced7` | Shipped |
| 4 | T-3 / T-6 / T-12 forensic standalone | `b0dced7` | Shipped (item 0 of forensic block) |
| 5 | Backfill RR SF from CoStar | `b0dced7` | Shipped (Step 5 of Rent Roll Extraction) |
| 6 | RR GPR vs T-12 GPR within 5% reconciliation | `b0dced7` | Shipped (Step 7) |
| 7 | Audit template formulas (S40 / B66 / B67 / rows 31-32 / row 78) | `b0dced7` (EFB only) | **PARTIAL** — Audit lives in `templates/field-mapping-efb.md`. ACQ field-map is a stub. **Proposal #1 below.** |
| 8 | Whisper bid sanity check | `b0dced7` | Shipped (SKILL.md Phase 3) |
| 9 | NOAH detection rule | `b7171c5` | Shipped (references/04-acq-revenue.md). **Proposal #2: add Esplanade worked example.** |
| 10 | HAP achievability ramp (50/75/90) | `b7171c5` | Shipped |
| 11 | Classic-market rent cap as DEFENSE | `b7171c5` | Shipped |
| 12 | Other Income FL Class A defaults ($85-90 PUM) | `b7171c5` | Shipped (references/03-efb-revenue.md) |
| 13 | S42 = ECONOMIC vacancy label rule | `b7171c5` | Shipped |
| 14 | Year 1 economic vacancy +HAP timing | `b7171c5` | Shipped |
| 15 | FL insurance floor post-Ian $900-1,200/u | `b7171c5` | Shipped. **Proposal #3: add Esplanade worked example ($723/u UW vs $904 T-12).** |
| 16 | Replacement reserves by vintage | `b7171c5` | Shipped ($250/$300/$350/$400 by age) |
| 17 | Agency triangulation REQUIRED gate (Phase 8) | `14c9f1e` | Shipped |
| 18 | FL reassessment specifics (Yr1, Yr2+, Save Our Homes, millage from CoStar) | `14c9f1e` | Shipped. **Proposal #4: add Esplanade worked example.** |
| 19 | Senior DSCR row adapts (bridge ↔ refi) | `14c9f1e` | Shipped |
| 20 | Per-period DSCR validation matrix | `14c9f1e` | Shipped |
| 21 | Refi sizing test as MAX(LTV, DY, DSCR) | `14c9f1e` | Shipped. **Proposal #5: add Esplanade worked example (refi DY-bound at 8.02%).** |
| 22 | Subject row dynamic linking VALIDATION | `14c9f1e` | Shipped. **Proposal #6: add Esplanade worked example (D8 was "Resia Rayzor Ranch" through Phase 11 first pass).** |
| 23 | Affordability anchors at bottom, weight=0 | Pre-existing in `references/10-comps-build.md` | Already covered |
| 24 | Vintage anchor 10-mile backfill | `14c9f1e` | Shipped |
| 25 | Plain-text methodology cell | `14c9f1e` | Shipped |
| 26 | Sales weighting 3 options + collapse flag | `14c9f1e` | Shipped. **Proposal #7: add Esplanade worked example (16 comps within 17mo, weights $0.058-$0.063).** |
| 27 | Never add new tabs/sections/rows | `6454bf7` (Universal Rule 9) | Shipped. **Proposal #8: add Esplanade worked example (DSCR section + QA Checks table redirect).** |
| 28 | Context discipline / snip after each phase | `6454bf7` (Universal Rule 10) | Shipped |
| 29 | Claude Log entry every turn | `6454bf7` (Universal Rule 11 + Claude Log Convention section) | Shipped |
| 30 | When user pushes back, ASSUME they're right | `6454bf7` (Universal Rule 12) | Shipped. **Proposal #9: add Esplanade worked example (msg[288] "Phase 11 Complete" with 7 listed issues).** |

**Friction signal: comps-build sub-skill.** The briefing flagged that the user had to inject `shieldstone-comps-build` mid-session. Recommendation: **ABSORB**, not elevate. Local check shows no `.skills/shieldstone-comps-build/` folder exists; the original is archived at `.skills/_archive/sandbox-2026-05-13/shieldstone-comps-build.skill`. The prescriptions were already absorbed into `references/10-comps-build.md` during the initial 2026-05-13 consolidation, plus extended in `14c9f1e` (subject linking validation, vintage backfill, methodology cell, weighting options + collapse flag). No further action needed.

---

## Proposal #1 — ACQ Field Map: add Pre-Population Formula Audit

**Priority:** High (only structural gap from the briefing)
**File:** `.skills/dream-underwrite/templates/field-mapping-acq.md`
**Action:** INSERT new section (mirror the one in `field-mapping-efb.md`)
**Source citation:** Claude Log Turn 84 + transcript bug discovery messages
**Rationale:** The 5 inherited Rayzor template bugs apply to both EFB and ACQ Mini Models (the ACQ model was forked from the same scaffold). The audit section lives in `field-mapping-efb.md` from commit `b0dced7`. The ACQ field-map is a stub and has no audit guidance. Phase 3 audit will not fire on ACQ deals without this addition.

**Proposed text** (insert after the existing "Overview" or "Model Layout" section in `field-mapping-acq.md`):

```markdown
---

## Pre-Population Formula Audit (REQUIRED at Phase 3)

The ACQ Mini Model was forked from the same scaffold as the EFB Mini Model and inherits the same 5 known formula bugs. Per Universal Rule 8, the skill must audit these cells BEFORE populating any input that depends on them. For each cell below, read the actual formula via openpyxl, compare to the expected formula, and if there is a mismatch, surface it in chat with the proposed patch.

(For the verbatim audit procedure, expected formulas, and bug catalog, see [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md) §Pre-Population Formula Audit. The same 5 bugs apply: S40, B66, B67, rows 31-32, row 78. The audit procedure is identical.)

**Esplanade ACQ worked example (2026-05-15):** All 5 bugs were present in the Rayzor-derived ACQ template. S40 understated Other Income revenue by ~$1.5M cumulatively (10-year). Row 78 (Senior DSCR) zeroed out from Year 3+ because the naive formula only pointed at bridge DS rows; was patched to `IF(year ≤ B57, bridge_DS, refi_PI)`. Rows 31-32 (refi P+I) forced amortization to start Year 3 instead of Year 6 (misrepresenting IO period benefit); patched to `IF(F$1 < B69+B70+1, ...)`. All 5 patches applied with user confirmation. Two additional bugs discovered in Phase 10 (Aggregate DSCR Row 79 missing refi principal) were caught later and should be added to the catalog if confirmed reproducible.
```

---

## Proposal #2 — NOAH detection: add Esplanade worked example

**Priority:** High
**File:** `.skills/dream-underwrite/references/04-acq-revenue.md`
**Action:** APPEND example inside the existing "NOAH Detection Rule" subsection
**Source citation:** Claude Log Turn 85 + transcript msg[132]
**Rationale:** The NOAH rule is the highest-leverage addition to the skill. An abstract rule is easier to skip; a worked example anchors it.

**Proposed text** (append to the end of "NOAH Detection Rule" subsection, before "If ANY unit type is NOAH"):

```markdown
**Esplanade ACQ worked example (2026-05-15):** Subject was a 2007-vintage Orlando garden property. In-place rents averaged $1,871 across 1BR units; LIHTC 80% AMI ceiling for Orange Co was $2,182. Ratio: 1,871 / 2,182 = 0.86 → **NOAH confirmed**. The assistant initially proposed an 80% AMI tier upside thesis; the user (msg[132]) rejected it because in-place rents already sat at ~70% AMI naturally. Phase 4 was fully rebuilt: 80% AMI tier eliminated, structure became MLA (capped at FMR) + HAP at FMR + Classic/Renovated market split. Returns were recalibrated from an inflated 41% IRR to a defensible 22.5% IRR. The NOAH gate would have caught this before allocation if run first.
```

---

## Proposal #3 — FL insurance floor: add Esplanade worked example

**Priority:** Medium-High
**File:** `.skills/dream-underwrite/references/05-expenses.md`
**Action:** APPEND example inside "Florida Post-Ian Floor (REQUIRED)" subsection
**Source citation:** Claude Log Turn 86 + transcript msg[188]
**Rationale:** Esplanade was the canonical "user overrode the floor" case. The override worked because it was explicit; the example reinforces that pattern.

**Proposed text** (append to the end of the "Florida Post-Ian Floor (REQUIRED)" subsection):

```markdown
**Esplanade ACQ worked example (2026-05-15):** T-12 actual insurance was $904/unit. User chose to underwrite at $723/unit (20% below T-12). Per this rule, the skill required: (a) explicit user override logged in chat ("User: confirms FL insurance at $723/u based on bound quote from broker dated [date]; T-12 of $904 reflected the seller's 2024 carrier and not the buyer's"), and (b) agency-risk flag ("At refi, Fannie/Freddie will require bona fide quote per S&S Guide §203.01 Item 17(c); if bound quote at refi is at or above $900 floor, refi will be sized down accordingly"). Both documented in Claude Log. Override accepted. The mistake to avoid is silently defaulting to T-12 actual on a FL deal — that's how the floor gets missed.
```

---

## Proposal #4 — FL reassessment: add Esplanade worked example

**Priority:** Medium
**File:** `.skills/dream-underwrite/references/06-property-tax.md`
**Action:** APPEND worked example inside "Florida Reassessment Specifics (REQUIRED for FL ACQ deals)" subsection
**Source citation:** Claude Log Turn 87
**Rationale:** Adds concrete numbers to the abstract Yr1 / Yr2+ formula.

**Proposed text** (append to the end of the "Florida Reassessment Specifics" subsection):

```markdown
**Esplanade ACQ worked example (2026-05-15):**

```
Year 1 (acquisition year, seller assessment carries):
  Current Assessed Value (CoStar): $29,190,000
  Current Millage (CoStar tax $472K / assessed $29.19M): 1.6183%
  Year 1 Taxes: $29,190,000 × 1.6183% = $472,397

Year 2+ (post-reassessment to commercial Just Value):
  Purchase Price: $34,000,000
  Year 2 Assessed Value: 0.80 × $34,000,000 = $27,200,000
  Year 2 Taxes: $27,200,000 × 1.6183% = $440,177
  Years 3+: ×2% annual trending
```

Notable: Year 2 taxes (~$440K) are LOWER than Year 1 (~$472K) in this case because the seller's prior assessment ($29.19M) was higher than 80% of the new PP ($27.2M). This is a Florida-specific quirk that catches underwriters off-guard. Millage was pulled from CoStar (1.6183%); Orange County state-default would have been ~1.86%, overstating taxes by 15%.
```

---

## Proposal #5 — Refi sizing as MAX-of-three: add Esplanade worked example

**Priority:** Medium
**File:** `.skills/dream-underwrite/references/09-acq-financing.md`
**Action:** APPEND example inside "Agency Sizing Methodology" subsection
**Source citation:** Claude Log Turn 87
**Rationale:** Anchors the abstract DSCR / LTV / debt-yield triangulation with a real deal where debt yield was the binding constraint.

**Proposed text** (append after the "Binding constraint pattern" bullets):

```markdown
**Esplanade ACQ worked example (2026-05-15):** Refi sized at $31.9M Year 2 against the agency takeout from bridge. Constraints:

```
T-3 NOI Annualized at refi: $2,560,000 (Year 2 stabilized)
Agency rate at refi:        6.25%
Agency constant:            7.39%

Max Loan (DSCR @ 1.25x):    $2,560,000 / 1.25 / 0.0739 = $27,710,000
Max Loan (LTV @ 75%):       $40,800,000 × 0.75       = $30,600,000
Max Loan (Debt Yield @ 8%): $2,560,000 / 0.08         = $32,000,000

Binding: DSCR at $27.7M.  WAIT — that's not what we sized.
```

Actually, in the Esplanade case the binding was debt yield at 8.02% per Claude Log Turn 87 ($2.56M / $31.9M = 8.02% DY). DSCR appeared looser because we sized off Year 2 IO P+I (interest-only refi period) rather than fully amortized. **Implication for the skill:** when sizing the refi, the DSCR test must use the FULLY AMORTIZING P+I, not the IO-period interest-only payment. Otherwise DSCR looks loose and debt yield silently binds. Add this gotcha to the cell map for the ACQ Mini Model refi assumptions block.
```

---

## Proposal #6 — Subject row dynamic linking: add Esplanade worked example

**Priority:** Medium
**File:** `.skills/dream-underwrite/references/10-comps-build.md`
**Action:** APPEND example inside "Subject Row Dynamic Linking: VALIDATION RULE" subsection
**Source citation:** Claude Log Turn 88 + transcript msg[288] item (c)
**Rationale:** msg[288] is one of the strongest "user pushback" moments; the canonical example for why hardcoded subject values are unacceptable.

**Proposed text** (append to the end of the subsection, after the existing patch procedure):

```markdown
**Esplanade ACQ worked example (2026-05-15):** At Phase 11 first pass, the assistant declared "Phase 11 Complete." User (msg[288]) responded with 7 issues, including: D8 sales subject was still "Resia Rayzor Ranch" (left over from the template fork); Row 35 rent subject had Rayzor values; affordability anchors were interspersed instead of bottom-anchored; LIHTC rows had weight > 0. All four were hardcode failures. The patch path: D8 was rewritten as `=Pro Forma!B10` (purchase price), Row 35 cells were rewritten as `=Pro Forma!T22/U22/W22` (per-BR market rents), affordability rows were moved to rows 52-56 with weight = 0 via the conditional, LIHTC rent rows were re-anchored to weight = 0. Lesson: every Phase 11 first-pass MUST run the subject-row validation BEFORE declaring complete.
```

---

## Proposal #7 — Sales weighting collapse flag: add Esplanade worked example

**Priority:** Medium
**File:** `.skills/dream-underwrite/references/10-comps-build.md`
**Action:** APPEND example inside "Sales Weighting: Three Options + Collapse Flag" subsection
**Source citation:** Claude Log Turn 88
**Rationale:** Concrete case where recency-decay produced a flat result.

**Proposed text** (append after the "Collapse flag (REQUIRED)" paragraph):

```markdown
**Esplanade ACQ worked example (2026-05-15):** 16 sales comps all within a 17-month window of the underwriting date. Recency-decay weights ranged from $0.058 to $0.063 (only ±4% spread across all 16 comps, well inside the ±20% collapse threshold). The weighted average was effectively the arithmetic mean. User redirected to manual bucket tiers: 4 A-tier comps at 0.15 each (60% total weight), 6 B-tier at 0.05 each (30%), 6 C-tier at 0.017 each (10%). This differentiated the 4 most relevant comps and tightened the weighted PPU benchmark from $169K (flat) to $173K (bucket). Whisper bid sensitivity changed from +5% to +3% premium — still defensible, but the precision matters for IC.
```

---

## Proposal #8 — Universal Rule 9 (never invent structure): add Esplanade worked example

**Priority:** Medium
**File:** `.skills/dream-underwrite/SKILL.md`
**Action:** APPEND example inside Universal Rule 9
**Source citation:** Claude Log Turn 89 col E
**Rationale:** Concrete case from this deal — the assistant twice proposed adding structure that already existed.

**Proposed text** (append to Universal Rule 9):

```markdown
**Esplanade worked example (2026-05-15):** Twice during the underwrite the assistant proposed new template structure that already existed: (a) a new "DSCR section" below the existing Pro Forma when rows 76-79 already had DSCR rows, and (b) a new "QA Checks table" when a Checks sheet already existed. User redirected both times. Each redirect cost ~5 minutes of context. The fix: BEFORE proposing any new structure, scan all 12 sheets for existing instances of the target concept (search labels in column A/B and sheet names). If the structure exists anywhere, populate it; do NOT add parallel structure.
```

---

## Proposal #9 — Universal Rule 12 (trust pushback): add Esplanade worked example

**Priority:** High (per briefing — msg[288] is the canonical example)
**File:** `.skills/dream-underwrite/SKILL.md`
**Action:** APPEND example inside Universal Rule 12
**Source citation:** Claude Log Turn 89 + transcript msg[288]
**Rationale:** The strongest "trust the user" moment in the Esplanade deal. Adds bite to an otherwise-abstract rule.

**Proposed text** (append to Universal Rule 12):

```markdown
**Esplanade worked example (2026-05-15):** At Phase 11 first pass, the assistant emitted a chat message "Phase 11 Complete ✅." The user immediately responded (msg[288]) with 7 specific issues in one message: (a) C10:C25 / J10:J25 column formatting was off, (b) sales weighting methodology not documented anywhere visible, (c) D8 subject still read "Resia Rayzor Ranch", (d) Row 35 rent subject still had leftover Rayzor values, (e) affordability anchors were interspersed mid-table instead of bottom-anchored, (f) LIHTC rows had weight > 0, (g) vintage coverage was thin. The assistant's correct response: read each cell quoted, confirm the user's observation, propose the patch, never re-emit "Complete" until ALL 7 are addressed. **The wrong response (and easy to fall into) is to defend prior work, hand-wave one or two items, and re-declare complete.** When the user lists multiple issues, address each one in order; do not skip or batch-acknowledge.
```

---

# Task B — Phase 12 Memo Transcript-Ingestion Enhancement

**Priority:** Medium
**File:** `.skills/dream-underwrite/references/14-html-memo.md`
**Action:** INSERT new section titled "Transcript-Aware Memo Build"

**Rationale:** The Phase 12 memo built today (`2026-05-esplanade-orlando-acq.html`) reads the .xlsx for numbers but is blind to the narrative reasoning captured in the Claude Log. The next deal memo should be richer when a transcript JSON is available alongside the .xlsx.

**Proposed text** (insert as a new section after the existing "Phase 12 Workflow" section in `references/14-html-memo.md`):

```markdown
---

## Transcript-Aware Memo Build (when transcript JSON is available)

When a Claude-for-Excel transcript JSON is uploaded alongside the .xlsx, Phase 12 reads BOTH and enriches the memo with the narrative reasoning that's only in the transcript. The .xlsx tells you what; the transcript tells you why.

### Sources

| Source | What you pull |
|---|---|
| **Claude Log tab** (workbook, Sheet 1) | Per-turn `Action Taken` (col D), `Details` (col E), `Outcome` (col F). Each is one phase or one sub-decision. |
| **Transcript JSON** | User pushback moments, override decisions, thesis statements |

### Memo variable slots (NEW, in addition to the numeric variables from the Cell Map)

```python
# Append to the build script variables block per deal
MEMO_THESIS = """
NOAH workforce housing in Orlando submarket. In-place rents naturally affordable
(~70% AMI), so 80% AMI tier is not upside; HAP capture is the only structural lever.
Bridge-to-agency structure with light value-add ($7K/unit) defending classic-cohort
rents rather than extending them. Whisper $34M vs. asking $38M reflects the
NOAH-driven thesis correction.
"""

MEMO_OVERRIDES = [
    {"field": "Insurance", "uw": 723, "t12": 904, "rationale": "Bound quote from broker; 20% below T-12 reflects seller carrier shift"},
    {"field": "Property Tax", "yr1": 472, "yr2": 440, "rationale": "FL §193.011 reassessment at 80% PP, current millage 1.6183% from CoStar"},
    {"field": "Vacancy Curve", "y1": 9.0, "stabilized": 6.5, "rationale": "Year 1 includes +300 bps HAP qualification timing"},
    {"field": "Interest Reserve", "amount": 0, "rationale": "Year 1 DSCR 1.23x cleared bridge floor; no IR sized"},
]

MEMO_AUDIT_TRAIL = [
    "S40 (Other Income annual): patched from =U36 to =U36*12",
    "B66 (LTC): patched from =SUM(B52,B67)/B10 to =B52/B10",
    "B67 (Refi loan amount): patched from hardcoded $62M to =B68",
    "Rows 31-32 (Refi P+I): patched IO threshold to =IF(F$1<B69+B70+1,...)",
    "Row 78 (Senior DSCR): patched to IF(year<=B57, bridge_DS, refi_PI)",
    "Row 79 (Aggregate DSCR): added missing refi principal",
]

MEMO_RISK_FLAGS = [
    "HAP achievability ramp (Y1 50% / Y2 75% / Y3+ 90%) — if Y2 fails to ramp, $93K Y1 GPR shortfall",
    "Insurance UW at $723/u vs T-12 $904/u — at refi expect Fannie quote method to size up",
    "Refi sized debt-yield-bound at 8.02% — sensitive to NOI absolute level, not LTV",
    "Year 1 DSCR 1.23x (bridge floor) — zero NOI cushion",
]
```

### How the build script consumes these

In the `build_<dealslug>.py`, render these slots as named sections in the HTML:

- **MEMO_THESIS** → Section I "Project Overview" lead paragraph (replaces the generic boilerplate)
- **MEMO_OVERRIDES** → Section III "Risks" table (each override becomes a numbered risk row with rationale)
- **MEMO_AUDIT_TRAIL** → Appendix sub-section "Template Audit" (shows the IC that the model was sanity-checked, not just populated)
- **MEMO_RISK_FLAGS** → Section III "Risks" headline cards (Smart Brevity format)

### Why this matters

Without these slots, the memo reads as a numerical summary. With them, it reads as a defensible thesis. The IC sees not just "Year 1 DSCR is 1.23x" but "Year 1 DSCR 1.23x cleared bridge floor; bridge structure was chosen specifically to absorb HAP qualification timing." The transcript carries the reasoning; surface it.
```

**Worked example variable block for next deal:** See the Python block above. The next deal's `build_<slug>.py` should include these 4 named variables in addition to the numeric variables from the Phase 12 Cell Map.

---

# Task C — Self-Improving Sub-Skill Design Summary

**Folder to create:** `.skills/shieldstone-skill-improve/`

**Files in the sub-skill:**
- `SKILL.md` — the skill spec (frontmatter, when-to-invoke, guardrails)
- `scripts/improve-from-transcript.py` — the extractor

**Inputs:**
- One or more transcript JSON files (Claude-for-Excel format, `messages` array)
- Optional matching `.xlsx` workbook (for Claude Log reading)

**Output:**
- `PROPOSED_CHANGES_<YYYY-MM-DD>.md` in the master skill folder, same diff format as Task A

**Extractor mechanics:**
1. Pull Claude Log rows where col D contains "SKILL IMPROVEMENTS" (or rows ≥ Turn 81 if marker varies)
2. Grep transcript user messages for pushback regex: `wrong|stop|fix|actually|not right|still wrong|broken|missed|skipped|hardcoded|leftover|stale`
3. Count phase-name mentions per phase to produce a friction heatmap
4. Identify user manual overrides logged to Claude Log col E

**Guardrails (encoded in SKILL.md):**
1. **Never auto-write skill files.** Always produce a proposal that the user reviews.
2. **2-deal rule for promotion.** A rule needs to appear in ≥2 transcripts before being promoted to permanent text. Single-deal observations are logged as "candidate" with source citation.
3. **CHANGELOG row per accepted change.** Every approved change writes a row to `.skills/dream-underwrite/CHANGELOG.md` with: date / source transcript filename / rule summary / files touched.

**Validation case (built into the sub-skill design):**
Feed the Esplanade transcript + workbook into the new sub-skill. It should independently surface the same 30 items. Acceptance range: 20-50 items. <20 = extractor too narrow; >50 = noisy.

**Status:** Will scaffold immediately (greenfield folder, no master-skill edit). First validation run will follow scaffold.

---

## Summary (Round 1, drafted 2026-05-15)

- 9 worked-example citations to add to existing rules (small, additive)
- 1 structural addition (`field-mapping-acq.md` audit section)
- 1 reference doc enhancement (`14-html-memo.md` transcript-aware build)
- 1 new sub-skill (`shieldstone-skill-improve`)
- 0 changes to the EFB-only skill at `.skills/shieldstone-efb-uw/`

**Round 1 outcome (applied 2026-05-15, commits `e4575e0` + `bf5ef82`):**
- ✅ Sub-skill scaffolded with full leanness discipline (rules 6-10)
- ✅ Proposal #1 (ACQ formula audit port) applied
- ✅ Task B (transcript-aware memo) applied
- ❌ Proposals #2-9 (worked-example citations) deferred indefinitely. Replaced by **12 phase QA gates** added to SKILL.md (higher-leverage; recurring vs. read-once)

---

# Round 2 Proposals — Mission Driven AI REST API + OpEx (queued 2026-05-16)

## Round 2 context

A separate Claude session shipped a REST API + CLI on top of the `shieldstone-rent-mcp` server, then added agency OpEx benchmarks as a second dataset. Live at `https://rent-mcp.shieldstone.co`, Bearer-auth (token in `c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local`).

**Why this matters:** the Claude.ai MCP connector OAuth flow is broken on Windows (Anthropic bug `ofld_63e310c0724bb7ca` — desktop can't handle the `claude://` callback URL scheme). The current `shieldstone-master-uw` Phase 4 source chain lists the MCP connector as priority (a), which is **actively misleading**: it tells underwriters to try a broken path first. The REST API bypasses the OAuth issue entirely (any HTTPS client works).

**Verified live 2026-05-16:**
- Endpoint: `https://rent-mcp.shieldstone.co/api/v1/freshness` → returns 401 unauthenticated, 200 with token. ✅
- Regression baseline 1: Denton TX 2BR FMR = $1,931 ✅
- Regression baseline 2: FL_coastal Class B insurance floor = $900/unit (Shieldstone post-Ian binding) ✅
- Coverage: 56 states, 4,764 counties, 33,773 SAFMR ZIPs, 47,640 LIHTC rows, 70+ agency OpEx rows

**Source citations:**
- Live commits in `c:/Users/evana/mission-driven-hud-lihtc-mcp/` (`121881b` OpEx, `021f90b` CLI fix, `8b79593` REST API + CLI)
- Bug ref: `ofld_63e310c0724bb7ca` (Anthropic Windows OAuth)
- OpEx data extracted from `references/15-opex-agency-triangulation.md` on 2026-05-13

---

## Round 2 Summary Table

| # | Priority | File | Action | One-line |
|---|---|---|---|---|
| NEW-1 | **High (correctness)** | `SKILL.md` Phase 4 | REPLACE source chain | Demote broken MCP connector, put REST API at #1 |
| NEW-2 | Med | `references/04-acq-revenue.md` | INSERT | API usage pattern for ACQ Phase 4 rent lookup |
| NEW-3 | High | `references/15-opex-agency-triangulation.md` | INSERT top | API fast-path for Phase 8 OpEx triangulation |
| NEW-4 | Med | `references/03-efb-revenue.md` | INSERT | Mirror of NEW-2 for EFB workflow |
| NEW-5 | Med | `references/14-html-memo.md` | APPEND | Phase 12 memo build pulls from API |
| NEW-6 | Low (memory) | `memory/reference_mission-driven-hud-lihtc-mcp.md` | UPDATE | Memory file: add REST API + OpEx endpoints |

## Round 2 leanness flag

NEW-2 and NEW-4 are near-duplicates (same API usage pattern, different reference file). The **leanness-respecting alternative** is:

- Create ONE canonical `references/00-api-reference.md` (a new reference file, low position so it sorts first)
- Point NEW-2 and NEW-4 at it with `→ see [references/00-api-reference.md](.skills/dream-underwrite/references/00-api-reference.md)` instead of inline duplication
- Net result: 1 file with the canonical API doc, 2-line cross-references in 03 and 04, instead of ~80 lines of duplicated prose

This is **strongly recommended** before applying NEW-2 / NEW-4. Cuts ~60 lines vs. naive application.

---

## Proposal NEW-1 — Phase 4 source chain (CORRECTNESS issue, not just additive)

**Priority:** HIGH. The current SKILL.md Phase 4 actively points at a broken path.
**File:** `.skills/dream-underwrite/SKILL.md` Phase 4 sub-step 3
**Action:** REPLACE existing 3-tier chain with the new 4-tier (REST API → MCP deferred → CSV → manual)
**Source citation:** Live API verification 2026-05-16; Anthropic bug `ofld_63e310c0724bb7ca`

**Current text (broken):**

```
3. **HUD FMR / SAFMR / LIHTC data sourcing priority** (Mission Driven AI HUD & LIHTC connector):
   - (a) Mission Driven AI HUD & LIHTC MCP connector if registered in session. Tool calls: ...
   - (b) [reference-data/](shieldstone_acquisitions/reference-data/) CSV from [scripts/fetch-hud-fmr.py](.skills/dream-underwrite/scripts/fetch-hud-fmr.py)
   - (c) Manual paste from huduser.gov FMR table (last-resort fallback).
```

**Proposed replacement:**

```
3. **HUD FMR / SAFMR / LIHTC data sourcing priority:**
   - (a) **Mission Driven AI REST API** at `https://rent-mcp.shieldstone.co/api/v1/*` (Bearer auth, token in `c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local`). Works in Claude Code (Bash + curl), Claude.ai (analysis tool urllib), Claude for Excel (Power Query), anywhere HTTPS reaches. CLI helper: `python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py fmr TX Denton --bedroom 2BR --value`. Full pattern in [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md) §Pulling rent data via REST API.
   - (b) MCP connector (DEFERRED — blocked by Claude.ai Windows OAuth bug `ofld_63e310c0724bb7ca`; re-enable when Anthropic ships the fix).
   - (c) Local CSV from [scripts/fetch-hud-fmr.py](.skills/dream-underwrite/scripts/fetch-hud-fmr.py) (per-county, offline fallback).
   - (d) Manual paste from huduser.gov (last resort, when API and CSV both unavailable).
```

**Leanness:** trades ~7 lines of broken MCP tool-call examples for ~7 lines of working API guidance. Approximately net-zero. **Apply with explicit user accept on correctness grounds** even though leanness budget is neutral.

---

## Proposal NEW-2 — ACQ revenue: REST API pull pattern

**Priority:** Medium (depends on NEW-1 landing). **Leanness alternative below.**
**File:** `.skills/dream-underwrite/references/04-acq-revenue.md`
**Action:** INSERT new subsection
**Source citation:** Verified live 2026-05-16

**Recommendation:** Apply via the consolidated `00-api-reference.md` file instead. See "Round 2 leanness flag" above. If you accept the consolidated approach, NEW-2 collapses to a single `→ see [references/00-api-reference.md](...)` pointer (~1 line) in `04-acq-revenue.md` at the rent-sourcing anchor.

If applied as written in the briefing (~30 lines inline), the prose would duplicate verbatim in NEW-4 (EFB revenue). The duplication grows the runtime skill twice without earning value twice.

---

## Proposal NEW-3 — OpEx triangulation: REST API fast path (Phase 8)

**Priority:** High
**File:** `.skills/dream-underwrite/references/15-opex-agency-triangulation.md`
**Action:** INSERT at top after Purpose section
**Source citation:** Verified live 2026-05-16

**Proposed text:**

```markdown
---

## REST API fast path (Phase 8 triangulation)

The line-item agency tables documented below are seeded into the Mission Driven AI REST API at `https://rent-mcp.shieldstone.co`. Phase 8 can pull the binding floor and all underlying sources directly via one HTTPS call instead of re-reading this markdown each deal.

**Triangulation call (returns binding floor + UW recommendation + every source row):**

```bash
TOKEN=$(grep MCP_AUTH_TOKEN c:/Users/evana/mission-driven-hud-lihtc-mcp/.secrets-vps.local | cut -d= -f2)
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://rent-mcp.shieldstone.co/api/v1/opex/triangulate?line_item=insurance&class=B&state=FL_coastal&program=conventional"
# → {"binding_floor": {"agency": "shieldstone", "value": 900.0, ...}, "all_sources": [...]}
```

Or via CLI helper:

```powershell
python c:/Users/evana/mission-driven-hud-lihtc-mcp/cli/rent.py opex-triangulate insurance --class B --state FL_coastal --program conventional
```

**Caveat (don't skip):** when `program` filter is omitted, `binding_floor` returns the MAX across ALL programs (e.g., Fannie Seniors Housing with Skilled Nursing $450/unit). For standard ACQ deals, always pass `--program conventional`. Verify the returned `binding_floor.citation` matches the deal context before quoting in the IC memo.

**The line-item tables below remain canonical** — the API is a faster read path, not a replacement source of truth. When this markdown is updated (per the Refresh Note at the bottom), the API gets re-seeded.

---
```

**Leanness:** Net +25 lines. Earns it back if Phase 8 actually uses the API (one API call vs. reading the full markdown). Apply with user accept.

---

## Proposal NEW-4 — EFB revenue: REST API pull pattern

**Priority:** Medium. **Same leanness alternative as NEW-2** — consolidate into `00-api-reference.md`, point at it from `03-efb-revenue.md`.

If applied as written, would duplicate ~30 lines of NEW-2 prose. Recommend skip in favor of the cross-reference approach.

---

## Proposal NEW-5 — Phase 12 memo build: API-driven data freshness

**Priority:** Medium
**File:** `.skills/dream-underwrite/references/14-html-memo.md`
**Action:** APPEND inside the "Transcript-Aware Memo Build" section (added in Round 1) or as a new subsection
**Source citation:** Verified live 2026-05-16

**Proposed text:**

```markdown
### API-driven data freshness (Phase 12)

The memo build script (per-deal `build_<slug>.py` or the Claude.ai-native inline path) should call the REST API for current FMR / SAFMR / LIHTC values AND for the binding agency OpEx floors used in the triangulation section of the memo, rather than re-extracting from the .xlsx alone:

```python
import os, json, urllib.request

token = os.environ.get('MCP_AUTH_TOKEN')  # or read from .secrets-vps.local
def api(path, **params):
    qs = '&'.join(f'{k}={v}' for k, v in params.items())
    req = urllib.request.Request(
        f"https://rent-mcp.shieldstone.co{path}?{qs}",
        headers={'Authorization': f'Bearer {token}'})
    return json.loads(urllib.request.urlopen(req).read())

lihtc = api('/api/v1/lihtc-table', state='FL', county='Orange', year=2026)
insurance = api('/api/v1/opex/triangulate',
                line_item='insurance', state='FL_coastal',
                program='conventional', **{'class':'B'})
# Use insurance['binding_floor']['citation'] for memo data-source footnote
```

Use each response's `citation` field for the memo's data-source footnote (auditable for IC).
```

**Leanness:** Net +20 lines. Apply if the API is going to be the canonical Phase 12 data source. Otherwise defer.

---

## Proposal NEW-6 — Memory file (outside skill bundle)

**Priority:** Low (memory is private, not part of runtime skill)
**File:** `c:/Users/evana/.claude/projects/c--Users-evana-shieldstone-os/memory/reference_mission-driven-hud-lihtc-mcp.md`
**Action:** UPDATE to add REST API + OpEx endpoints
**Source citation:** Verified live 2026-05-16

**Note:** memory files are personal context, not part of the skill bundle. Updating this does NOT affect the skill's behavior in Claude.ai, only the assistant's awareness in Claude Code sessions. **Safe to apply immediately** (no leanness implications for the skill).

---

## Round 2 recommended apply order

1. **NEW-6** (memory file) — apply immediately, no skill impact, fixes my future-session awareness
2. **NEW-1** (Phase 4 source chain) — apply with user accept; this is a CORRECTNESS fix (existing chain is broken on Windows)
3. **NEW-3** (Phase 8 OpEx fast path) — apply with user accept; high-leverage if Phase 8 actually adopts the API
4. Defer NEW-2 / NEW-4 in favor of consolidating into a new `references/00-api-reference.md`, then patching cross-references in 03 and 04 to point at it. Final delta: ~+50 lines for 00-api-reference, ~+2 lines each in 03/04. Vs. ~+60 lines if applied as written. Saves ~10 lines + creates clean single-source-of-truth.
5. **NEW-5** (Phase 12 API call pattern) — apply only after NEW-3 (consistent with API-as-canonical-data-source pattern)

**Net byte budget for Round 2 if all applied with consolidation:**
- NEW-1: ~net zero (replacement)
- NEW-3: ~+25 lines
- NEW-2 + NEW-4 consolidated as `00-api-reference.md`: ~+50 lines minus duplication that didn't happen
- NEW-5: ~+20 lines
- **Total: ~+95 lines (~3-4 KB)**. Net additive. Earned if API adoption happens; pure cost if it doesn't.


User approval requested before applying Proposals #1-9 and Task B to the master skill. Task C (scaffolding the new sub-skill) proceeds in parallel since it's greenfield.
