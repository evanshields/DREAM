# 10: Comps Tab Build

## Purpose

The Comps tab is the analytical heart of the master skill's Phase 11. Sales comps validate basis (going-in $/unit, exit assumption). Rent comps validate every pro forma rent assumption from Phase 4. Per-bedroom breakout drives the Pro Forma's market-rate tier directly. This reference encodes the sandbox `shieldstone-comps-build.skill` logic with the 16-slot sales structure (recency-weighted), 10 submarket + 2 new + 3 vintage + 5 affordability rent structure, per-BR breakout, and the Q-block input grid that drives display formulas via INDEX/MATCH. Critical rule: NEVER auto-populate the comp set, always present a ranked candidate list and get explicit user confirmation before writing.

---

## Tab Structure (Canonical)

The Comps tab has three sections. Do NOT touch the structural formulas, only populate data and curated row contents.

### Sales Comps (Rows 5–30)

| Row range | Content |
|---|---|
| Row 7 | Column headers |
| Row 8 | Subject (formula-linked to Pro Forma) |
| Rows 10–25 | **16 sale comp slots** |
| Rows 26–30 | Weighted-avg + product-type breakout (Mid-Rise / High-Rise / Garden / Other), do NOT touch |

**Sales comp slot mechanics (rows 10–25):**
- B10 = 1, B11:B25 = `=B10+1` chain (do NOT touch)
- C10:C25 = recency-weighted (NOT equal weight)
- D-O cols: D name, E product type, F year built, G units, H sale date, I sale price, J `=I/G` PPU, K `=I/O` PPSF, L cap rate (often blank from CoStar), M vacancy at sale, N current ask PSF, O building SF
- **ORDER: descending by sale date, newest at row 10, oldest at row 25**

### Main Rent Comp Display (Rows 33–64)

| Row range | Content |
|---|---|
| Row 33 | Headers |
| Row 34 | Subject (Current Rents) |
| Row 35 | Subject (Stabilized Rents) |
| Rows 37–46 | **10 primary submarket comps** (B37=1, B38:B46 chain) |
| Rows 47–48 | 2 reserved for new CoStar additions (Perch, Brae, etc.) |
| Rows 49–51 | 3 vintage anchor slots (only populate if user opts in) |
| Rows 52–56 | **5 affordability benchmark rows** (LIHTC 60/80/100, FMR, SAFMR), **weight = 0** |
| Row 57 | Total/Median across live comps |
| Rows 58–61 | Categories (Mid-Rise / High-Rise / Garden / Other), fixed labels |

**Subject row formula links (rows 34–35):**
- I34 = `=Pro Forma!T22` (avg SF), J34 = `=Pro Forma!U22` (in-place rent), L34 = `=J34`, K34 = `=J34/I34`, M34 = `=L34/I34`
- I35 = `=Pro Forma!T22`, J35 = `=Pro Forma!W22` (stabilized rent), L35 = `=J35`, K35 = `=J35/I35`, M35 = `=L35/I35`

**D-N formulas at rows 37–56** use INDEX/MATCH against the Q-block at Q8:AD118.

### Q-Block Input Grid (Rows 8–118, Columns Q:AF)

This is the data grid that feeds the display table.

| Col | Field |
|---|---|
| Q | Comp # |
| R | Property name |
| S | Product type (Garden / Mid-Rise / High-Rise) |
| T | Year built |
| U | Year renovated |
| V | Beds |
| W | Baths |
| X | # units |
| Y | %mix |
| Z | Avail # |
| AA | Avail % |
| AB | Avg SF |
| AC | Asking rent |
| AD | Ask/SF |
| AE | Effective rent (`=AC-25` default for market comps; `=AC` for affordability rows) |
| AF | Eff/SF |

**Per-property allocation:** each property occupies one row per bedroom type. A property with 1BR/2BR/3BR uses 3 rows. Affordability benchmarks use 1 row each, with X = subject total units, AB = subject avg SF, AC = blended rent.

### Per-BR Breakout (Rows 66–86)

| Row range | Content |
|---|---|
| Row 66 | Bedroom flags (E66=1, I66=2, M66=3) |
| Row 68 | Subject, links to Pro Forma per-BR cells |
| Rows 70–79 | **10 submarket comps** (NO vintage, keeps the new-build PSF read clean) |
| Rows 80–84 | **5 affordability rows** (LIHTC 60/80/100, FMR, SAFMR), weight = 0 |
| Row 86 | Total/Median |

**Subject row 68 (always linked, never hardcoded):**
- E68 = `=Pro Forma!T6`, F68 = `=Pro Forma!U6` (1BR market)
- I68 = `=Pro Forma!T10`, J68 = `=Pro Forma!U10` (2BR market)
- M68 = `=Pro Forma!T13`, N68 = `=Pro Forma!U13` (3BR market)
- G68 = `=F68/E68`, K68 = `=J68/I68`, O68 = `=N68/M68`

**Submarket comps (rows 70–79):** B70:B79 hardcoded comp #, C70:C79 = 0.10 each (equal weight)

**Total row 86 SUMIF CRITICAL CHECK:** verify J86/K86/N86/O86 use `$C$70:$C$84` as SUMIF criteria range (NOT the bedroom column). Old templates have a known bug where the criteria range references the bedroom column, producing absurd $0 or $44 outputs.

### Market Upcoming Construction Pipeline (Rows 88–101)

The fourth block on the Comps tab. Carries forward verbatim when a workbook is forked from a template — every forked deal inherits whatever pipeline data the template had. **Bit Esplanade AND Aviara in May 2026** (both shipped with Denton TX leftovers from a Rayzor Ranch template fork), so this block now has explicit Phase 11a coverage.

| Row range | Content |
|---|---|
| Row 88 | Section header (do not modify) |
| Row 89 | Column headers (do not modify) |
| Rows 90–99 | **10 data slots** for under-construction deliveries |
| Row 100 | Blank separator (leave blank) |
| Row 101 | **Total / Average formula row** (NEVER modify) |

**Cell map (rows 90–99):**

| Col | Content | Notes |
|---|---|---|
| B | Sequence # | B90 = literal `1`; B91:B99 = `=B(prev)+1`. **Do not modify.** |
| C | Empty separator | Leave blank, do not write |
| D | Project name + address | Plus annotations (see below) |
| E | Expected delivery date | Write as Python `datetime` or Excel-serial (column is date-typed). Do NOT write as a string. |
| F | Unit count | Integer |

**Source:** CoStar Full UW Report Construction section. Typically pp. 54–66 for the immediate submarket. If immediate submarket has < 5 deliveries, broader MSA pages (often pp. 100+) are the secondary source.

**Sort order:** ascending by Expected Delivery Date (E column).

**Submarket discipline:** if the immediate submarket has fewer than 10 deliveries, leave excess rows BLANK rather than padding with broader-MSA projects. Mixing submarkets undercuts the supply analysis. Only expand to broader MSA if the user explicitly opts in.

**Annotations (append to col D):**

- ` — Affordable` for income-restricted product
- ` — SAME SUBMARKET` for direct competitors in the immediate submarket
- ` — X.X mi from subject` for proximity bands (under 3 miles flagged as directly competitive)

The Phase 12 memo renderer reads these flags to identify directly competitive deliveries in the supply-risk narrative.

**Template-fork carryover check (REQUIRED before writing):**

Before overwriting, read D90:F99. If ALL 10 existing rows reference an MSA outside the subject's state (e.g., subject is in FL but rows list TX addresses), flag this loudly to the user as a likely template-fork carryover and proceed to overwrite once confirmed. **Esplanade and Aviara worked example:** both deals shipped with Denton TX rows (Northwest Village, Harvest House, Birchway Sanger, etc.) that were Rayzor Ranch template leftover. The defect survived two deal forks and fed false supply data into Phase 12 IC memos. Surgical fix applied 2026-05-17; Phase 11a now catches this category of error proactively.

**Row 101 is off-limits.** It contains SUM / MAX / AVERAGE formulas that aggregate rows above. openpyxl writes values to D90:F99 only; row 101 recomputes automatically.

---

## Workflow

### Step 1: Read the Pro Forma Subject

Pull these values from the Pro Forma tab so you know the subject before talking to the user:
- B6 units, B7 SF, B10 purchase price
- T22/U22/W22 avg SF / in-place rent / stabilized PF rent
- T6/U6 (1BR market SF/rent), T10/U10 (2BR), T13/U13 (3BR market, verify which row holds market vs AMI tiers)
- S3:S14 unit-mix counts to compute %mix (1BR / 2BR / 3BR)

Also pull from `Rent Comps Analysis` tab if affordability benchmarks already live there:
- LIHTC 60/80/100 AMI by bedroom, FMR by bedroom, SAFMR by bedroom

**Done when:** you can state subject units, SF, $/unit, in-place rent, stabilized rent, and %mix in one chat line.

### Step 2: Read CoStar Files

Both files have a single sheet `Export[date]` with a header row. Use Python (Claude for Excel runtime) to load them:

```python
import pandas as pd
df = pd.read_excel(path, sheet_name="Export031326", header=None)
df.columns = df.iloc[0]
df = df.iloc[1:].reset_index(drop=True)
```

For sales: filter to `Sale Status == "Sold"` with valid `Sale Price`, `Number Of Units`, `Building SF`. Sort descending by `Sale Date`.

For rent: each row is one property with unit-mix breakdowns in wide format. Identify which properties are TRUE submarket comps vs broader 20-mile-radius (the submarket file has ~8, the wide file has 300+).

**Done when:** clean dataframe of sale candidates and rent candidates with all key fields non-null.

### Step 3: Curate: ALWAYS Ask User Before Populating

**Most important rule.** Do NOT auto-populate the comp set. Show the user a ranked candidate list and get explicit selection.

**Sales (16 slots):**
1. Present top 20–25 candidates ranked by recency
2. Show: name / city / submarket / year built / units / PPU / PPSF / sale date
3. Ask which to include and which to drop
4. Common filters: stabilized only (no value-add stories unless intentional), 200+ units, similar product type, last 24 months

**Rent comps (10 primary + 2 new + 3 vintage + 5 affordability):**
1. Show all CoStar rent candidates ranked by submarket distance + vintage proximity to subject
2. Flag any property in the rent file that IS the subject (skip, happens where the subject property's own CoStar row appears)
3. Skip pre-1980 properties unless filling a vintage slot
4. **Vintage slots:** ask user whether to include 3–5 vintage anchors. If yes, present 6–10 vintage candidates (1960–2010, 100+ units, downtown / submarket-adjacent) ranked by relevance.
5. **Affordability benchmarks** are populated from Phase 4 data (Novogradac LIHTC 60/80/100 AMI, FMR, SAFMR). Do NOT skip even if no user opt-in, affordability rows are mandatory for EFB deals.

**Done when:** user has explicitly confirmed which 16 sales comps and which 10+ rent comps to use. Save their picks before writing.

### Step 4: Write Sales Comps (Descending by Sale Date)

For each picked comp, write D-O across rows 10–25 in descending sale date order (newest at row 10).

**Recency-weighted formula for C10:C25:**

```
=IFERROR(IF(D10<>"",MAX(0.01,1-(TODAY()-H10)/365*0.05),0),0)
```

This gives roughly:
- Sales in last 6 months: 0.95–0.98 weight
- 12 months old: 0.95
- 24 months old: 0.90
- Tapers, never below 0.01

**Normalize so weights sum to 1:**

```
=IFERROR(IF(D10<>"",MAX(0.01,1-(TODAY()-H10)/365*0.05)/SUMPRODUCT(MAX(0.01,1-(TODAY()-$H$10:$H$25)/365*0.05)*($D$10:$D$25<>"")),0),0)
```

OR simpler: ask the user if they want to override with a custom curve.

**Default fallback:** if the user doesn't specify, use a flat decay where last 6 months = 0.10 each, 6–12 months = 0.06 each, 12–18 months = 0.03 each, >18 months = 0.01 each, normalized to sum to 1.

Ship the C-column updates in chunks (4–5 cells per `set_cell_range` call) so the user sees progress.

**Done when:** D-O across rows 10–25 are populated, dates descend, J/K formulas auto-recalculate, and `=SUM(C10:C25)` ≈ 1.

### Step 5: Write Rent Comps (Q-Block + Display Table)

Write into the Q-block first. The display table picks it up via INDEX/MATCH.

**For each comp, add 1 row per bedroom type (skip beds with 0 units). Q-block layout per property:**

| Col | Value |
|---|---|
| Q | Comp # |
| R | Property name (same on every row of the property) |
| S | Product type (Garden / Mid-Rise / High-Rise based on stories: <4, 4–6, 7+) |
| T | Year built |
| U | Year renovated (or "N/A") |
| V | Beds (1, 2, 3, 4) |
| W | Baths (1 if beds<=1, else 2, heuristic, ask user for exact if needed) |
| X | # units |
| Z | Vacant units |
| AB | Avg SF |
| AC | Asking rent |
| AE | `=AC-25` (CoStar concession proxy) for market comps; `=AC` for affordability rows |

Y, AA, AD, AF are formulas already in the column.

**Comp number assignment:**

| Comps # | Use |
|---|---|
| 1–10 | Existing primary submarket (already populated; may need refresh) |
| 11–12 | New CoStar additions |
| 13–17 | Affordability benchmarks (LIHTC 60/80/100, FMR, SAFMR), use single row each with X = subject units, AB = subject avg SF, AC = blended rent across subject %mix |
| 18–22 | Vintage anchors (only if user opted in) |

**Affordability blended rent calc:**
```
LIHTC 60% AMI blended = 1BR_60 × %1BR + 2BR_60 × %2BR + 3BR_60 × %3BR
```
Same for 80%, 100%, FMR, SAFMR. If a benchmark lacks 3BR data (SAFMR often does), renormalize the 1BR/2BR weights and document.

**Done when:** Q-block has all rows for the picked comps, display table rows 37–56 auto-populate, and N50 / N57 / N86 weighted averages calculate without `#REF!` or `#DIV/0!`.

### Step 6: Per-BR Breakout

1. Wire subject row 68 to Pro Forma!T6/U6/T10/U10/T13/U13 (always, never hardcode)
2. B70:B79 = comp # for the 10 PRIMARY submarket comps only (NOT vintage, NOT affordability)
3. C70:C79 = 0.10 each (equal weight for per-BR view)
4. D70:D79 = `=D{37+row-70}` to mirror the display-table comp name (don't use INDEX/MATCH here, direct link is cleaner)
5. B80:B84 = comp # for the 5 affordability rows; C80:C84 = 0
6. E-O formulas at rows 70–84 query the Q-block and bedroom flag in row 66
7. Verify Total row 86 (or current row depending on inserts), J/N/K/O SUMIF criteria range MUST be `$C$70:$C$84`, NOT the bedroom column

**Done when:** subject row reads market rents per BR from Pro Forma, comp totals show realistic PSF spreads, and affordability rows appear as comparison without distorting weighted averages.

### Step 7: Sanity Check

Before declaring done, read back:
- C27 (sales weight total), should be 1.00
- N50 (rent comp weighted avg vacancy), flag if >25% (means lease-up comps are distorting; ask user if those should be re-weighted)
- C57 (rent comp weight total), should be 1.00
- J86/K86/N86/O86, confirm not `#VALUE!` or absurd ($44, $0.04 means the SUMIF bug is back)
- Subject vs comp comparison: state the 1BR / 2BR / 3BR rent and PSF reads in chat so the user can sanity-check

**Done when:** chat response cites specific cell values, names the 3 most important takeaways (e.g. "subject 2BR PSF $1.92 vs comp $1.63 = +18% mark-to-market room"), and flags any data quality issues you noticed.

---

## Important Rules

- **Never auto-populate without user curation.** Always present a ranked list and confirm before writing.
- **Sales descending by sale date, newest at top.** Not chronological.
- **Affordability rows always weight = 0** in both main and per-BR tables.
- **Subject per-BR row always linked** to Pro Forma, not hardcoded.
- **Skip the subject from the CoStar rent file.** When the property's own CoStar row appears (Rayzor Ranch in a Rayzor Ranch deal), it's not a comp.
- **Write in chunks:** 5–10 cells per `set_cell_range` call so user sees incremental progress.
- **Don't touch B-column sequence formulas (`=B+1`)** or row 26–30 / row 57–61 / row 86 totals/categories formulas. Those are structural.

---

## Subject Row Dynamic Linking: VALIDATION RULE (not a suggestion)

Both subject row cells must be formula references to the Pro Forma tab. Never hardcoded values. The validation runs every time the Comps tab is populated:

- **D8** (sales subject row): must contain a formula like `=Pro Forma!B10` (or the equivalent for that workbook). Reading hardcoded values like `=$78,500,000` is a validation failure.
- **Row 35** (rent subject row, primary rent comp table): must contain a formula chain that resolves to Pro Forma per-BR market rents. Reading hardcoded values like `=$1,485` is a validation failure.
- **Row 68** (rent subject row, per-BR breakout): same rule.

**At Phase 11, before any comp data is written:**

1. Read D8, row 35, row 68 with openpyxl using `cell.value` (which returns the formula string for formula cells; for hardcoded cells it returns the number).
2. If any cell returns a number (not a string starting with `=`), the cell is hardcoded. Flag and patch:

> "Validation failure: D8 contains hardcoded value `78500000`, expected formula `=Pro Forma!B10`. Patching with the formula now. Hardcoded subject values create a disconnect between the comps tab and the underwriting; every comp output then drifts as the pro forma updates."

3. Apply the patch (write the formula). Re-read to confirm.
4. Log to Claude Log: `[timestamp] Phase 11: subject row validation, N cells were hardcoded, patched with Pro Forma references`.

Never let a hardcoded subject row through. The downstream comparisons (percentile rank, premium/discount, weighted average) all depend on the subject reading dynamically.

---

## Vintage Anchor Backfill: 10-Mile Radius When Submarket Lacks Modern Stock

When the submarket CoStar file has fewer than 3 modern-vintage comps (post-2015 build year), the rent achievability analysis is unreliable on a 2020+ vintage subject. Park Central was the canonical example: the submarket CoStar pull had only 2 modern comps; the broader 10-mile radius pull had 137.

**Procedure:**

1. After Step 3 (Curate), count modern-vintage comps (year built ≥ 2015) in the candidate list.
2. If count < 3, request a 10-mile radius CoStar rent comp pull from the user. Note: this is the broader CoStar export with property filter set to a 10-mile radius around the subject, vintage post-2015, occupancy ≥ 90%.
3. From the 10-mile pull, select 3-5 vintage anchors for context. These go in the vintage anchor slots (rows 49-51 in the main rent comp table; up to 2 additional slots if needed).
4. **Vintage anchors carry weight = 0** in both the main table and the per-BR breakout. They are visible context, not weighted comps.
5. Document in chat: "Submarket CoStar had only 2 modern comps; pulled 137 from a 10-mile radius, selected 5 modern vintage anchors at weight=0 for context. Primary rent comp average remains submarket-based."

---

## Plain-Text Methodology Cell

Add a methodology documentation cell to the Comps tab so the reader does not have to reverse-engineer the weighting formulas. The cell location is workbook-specific (TBD on first execution; recommend a merged-cell block in cols D-H at the bottom of the sales comp table or above the rent comp table, depending on the layout).

**Content template (write to the cell as text, not a formula):**

```
COMPS METHODOLOGY (read this first)

Sales comps:
  - 16 comp slots, descending by sale date
  - Weights: recency-decay formula, =IFERROR(IF(D10<>"",MAX(0.01,1-(TODAY()-H10)/365*0.05),0),0)
  - Normalized to sum = 1.00
  - Override available; see Sales Weighting Options block below

Rent comps:
  - 10 submarket comps + 2 new construction + 3 vintage anchors (10-mile if needed) + 5 affordability rows
  - Affordability rows (LIHTC 60/80/100 AMI, FMR, SAFMR) carry weight = 0 always
  - Per-BR breakout: 10 submarket comps with weighted average, affordability shown but weight = 0
  - Subject rows (D8 sales, row 35 / row 68 rent) link to Pro Forma; never hardcoded

[Underwriter notes, fill in per deal:]
  - Submarket filter applied: [ZIP or city]
  - Vintage filter applied: [year range]
  - Class filter applied: [4/5-star, 3-star, etc.]
  - Lease-up comps (vacancy > 30%): [included / excluded / weight-reduced]
  - Override notes: [any manual weight overrides applied]
```

Future deal sessions will read this cell first to understand the prior underwriter's logic. Without it, the weighting choices are opaque on re-review.

---

## Sales Weighting: Three Options + Collapse Flag

The default sales comp weighting is **recency-decay** (auto formula). Two other options exist for cases where recency-decay produces a flat result:

| Option | Description | Use when |
|---|---|---|
| **Recency-decay (default)** | `=IFERROR(IF(D10<>"",MAX(0.01,1-(TODAY()-H10)/365*0.05),0),0)`, normalized | Mixed-vintage comps with varied sale dates |
| **Bucketed tiers (manual)** | User assigns weight per comp (e.g., A-tier 0.15, B-tier 0.10, C-tier 0.05) | Specific comps clearly more or less representative than the date-decay implies |
| **Hybrid** | Recency-decay as base, manual override on N specific rows | Most comps are date-driven but 1-2 outliers need manual treatment |

**Collapse flag (REQUIRED):** if the recency-decay output produces weights that all sit within ±20% of each other across all 16 sales comps (i.e., the date spread is too narrow for decay to differentiate meaningfully), surface the alternative options to the user:

> "Recency-decay weights collapsed to a narrow band (range 0.058-0.067, all within ±9% of mean). The weighted-average comp is essentially the arithmetic mean. Consider switching to bucketed tiers (manual) or hybrid to differentiate the high-quality comps. Continue with recency-decay? (Y/N)"

Document the chosen option in the Plain-Text Methodology Cell above.

---

## Common Pitfalls

1. **Inserting rows mid-table breaks the Q-block MATCH ranges.** If you must insert, verify formulas extend to AD118.
2. **The Total/Median row J/K/N/O formulas** frequently have a bug where SUMIF criteria range references the bedroom column. Always check after edits.
3. **3BR data is often missing for SAFMR:** renormalize 1BR/2BR mix weights, don't leave a $0.
4. **CoStar concession field is unreliable.** Default to `AE = AC - 25` for market comps unless the user wants property-specific concessions.
5. **Lease-up comps (vacancy > 30%) distort weighted averages.** Either drop them, weight them down, or call out the distortion in chat.

---

## See Also

- [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md), rent achievability stress test runs against curated comps
- [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md), P65 PSF base case for conventional/ACQ pro forma rent
- [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md), CoStar comp extraction protocols
- [references/12-uw-snapshot.md](.skills/dream-underwrite/references/12-uw-snapshot.md), UW Snapshot pulls comp comparison
