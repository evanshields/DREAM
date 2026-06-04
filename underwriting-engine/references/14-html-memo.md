# 14: Phase 12 HTML Investment Memo (GS Residential canonical format)

## Purpose

Phase 12 renders the completed underwrite as a single self-contained HTML investment memo in
the **canonical GS Residential format** — the structure the firm actually ships (Esplanade,
Aviara). This reference was reconciled to the real build scripts on 2026-06-03 because the prior
version documented an older layout (Sections I–VII, Chart.js charts, Opportunities/Risks/
Value-Creation cards, a bare `prompt()` gate) that GS Residential no longer uses. **Match the
build scripts below; do not invent a third variant.**

## Template of record (read these FIRST, in this order)

1. [build_esplanade_acq_exempt.py](shieldstone_acquisitions/deal-memos/build_esplanade_acq_exempt.py) — **THE canonical build.** This is what `redeploy.sh` ships to `gsresidential.co/esplanadeapartments.html`. The executable source of truth for structure, the access gate, the four-scenario UW snapshot, brand tokens, and the cell-pull pattern.
2. [build_aviara_acq.py](shieldstone_acquisitions/deal-memos/build_aviara_acq.py) — the Aviara clone of the same structure (second worked example: tax-exempt-led, no value-add tier).
3. [EDITING_WORKFLOW.md](shieldstone_acquisitions/deal-memos/EDITING_WORKFLOW.md) and [redeploy.sh](shieldstone_acquisitions/deal-memos/redeploy.sh) — the deploy + edit loop.

Use `build_esplanade_acq_exempt.py` as the scaffold for a new deal: copy it, swap the
deal-variable block + base64 images + the four scenario columns, keep the structure.

---

## Canonical structure (what Phase 12 MUST produce)

- **Single self-contained `.html`**, embedded base64 images, no external refs except Google Fonts.
- **Brand:** navy `#1B2A4A`, orange `#C86E3A`, warm `#F7F2EC`; Playfair Display (headings) /
  Josefin Sans (labels) / Noto Sans (body). GS Residential logo (base64) top-left in a sticky
  nav with `<Deal> | Investment Narrative` brand text and a progress bar.
- **`<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">`** (confidential).
- **House style:** no raw em-dash characters — use `&mdash;` entity or rephrase. Investor framing
  throughout (Shieldstone/GS as investor, not "operator").

### Access gate (name + email + password — NOT a bare prompt)

A full-screen navy gate at top of `<body>` with THREE fields (name, email, password):
- `id="pw-gate"`, form `id="access-form"` with `#access-name`, `#access-email`, `#pw-input`,
  submit `#access-submit`, error `#pw-err`.
- Gates on a per-deal password constant `MEMO_PASSWORD`; remembers via
  `sessionStorage.setItem('memo_auth','1')`.
- On success, POSTs `{name, email, address:''}` to `/nda` (fire-and-forget `fetch`, `.catch(()=>{})`).
- Exact snippet is in `build_esplanade_acq_exempt.py` lines ~495–537 — copy it verbatim, change
  only `MEMO_PASSWORD` and the deal name in the gate header.

### Sections, in this exact order, with these ids

| id | Label | Background | Content |
|---|---|---|---|
| `#summary` | I &middot; Executive Summary | default | Two-col: left = 3 "highlight-block" bullet groups (orange left-border); right = sticky "Key Investment Details" snapshot card + an income/rent-tier bar. Below: a 3-up photo strip; optional amenity/access map. |
| `#sponsor` | II &middot; Sponsor | `section-warm` | 5-person team grid (base64 headshots) + optional operating-partner card. Bios are reusable boilerplate. |
| `#snapshot` | III &middot; Underwriting Snapshot | `section-warm` | **The four-scenario UW Snapshot table** (`uw-snap-table`). See below. |
| `#market` | IV &middot; Market &amp; Submarket | `section-inverted` (navy) | `market-row`: left = 3 "bullet-block" groups with round orange icons; right = "&lt;Region&gt; at a Glance" stats card. Then a 5-stat snapshot row, then a 3-col grid (demand drivers / operating outperformance / transit &amp; access). |
| `#comps` | V &middot; Comparable Analysis | default | Sales comps (compact table, subject row highlighted), rent comps (subject in-place + UW-stabilized rows highlighted), affordability anchors (weight 0), per-bedroom UW rent schedule, market construction pipeline. From the model's **Comps** tab. |
| `#appendix` | VI &middot; Appendix | `section-inverted` | Sources &amp; Uses, Debt Structure, 10-Year Operating Projection table, Property Tax detail, Exit &amp; Return summary. |

**Footer:** GS Residential Holdings, LLC + Aventura address + disclaimer + confidentiality block.

**REMOVED (do NOT include):** standalone Risks section, Opportunities cards, Value-Creation
checklist, Chart.js DSCR/vacancy charts. The data that used to live in charts now lives in the
appendix's 10-Year Operating Projection table.

### The four-scenario UW Snapshot table (Section III — the distinctive piece)

A `uw-snap-table` with **four value columns**, pulled from the model's **UW Snapshot** tab:

| Column | Header | Source |
|---|---|---|
| 1 | Seller T-12 | UW Snapshot seller-T-12 column |
| 2 | Seller T-3 Annualized | UW Snapshot T-3 column |
| 3 | UW Stabilized (Full Taxes) | UW Snapshot full-tax column |
| 4 | UW Stabilized (Tax-Exempt) — `class="exempt"` (orange) | UW Snapshot tax-exempt column |

Rows: GPR (+ per-unit subline), Vacancy/Concessions/Bad Debt/LTL, Other Income, **EGI** (+ vacancy-%
subline + HAP/MLA-unit subline), each OpEx line (loop `UW_OPEX_LINES`), **Total OpEx**, **NOI**
(+ NOI-per-unit subline), then **implied cap rates at Ask and at Purchase Price** (the highlight row).

The four scenario columns are the variable block `SCEN_*` (e.g. `SCEN_T12_GPR`, `SCEN_UWE_NOI`,
`SCEN_PP_CAPS[0..3]`) — see `build_esplanade_acq_exempt.py` lines ~719–757.

---

## Phase 12 Cell Map (pull from the model — NOT just the Pro Forma tab)

The canonical memo pulls from **three** tabs. Detect model type (EFB vs ACQ) from sheet names.

### Deal identity + pricing (Pro Forma tab, A–B)

| Memo var | Cell | Notes |
|---|---|---|
| DEAL_NAME | B2 | |
| YEAR_BUILT | B5 | |
| UNITS | B6 | formula `=S22` |
| PURCHASE_PRICE | B10 | |
| PRICE_PER_UNIT | B8 | formula |
| GOING_IN_CAP_T3 | B11 | formula |
| IRR / EM / CoC (ACQ) | B15 / B16 / B17 | formulas |
| LOAN/LTV/RATE/TERM | B51–B57 | |
| EXIT_CAP / COSTS_OF_SALE / SALE_YEAR | B79 / B80 / B81 | |

### Four-scenario snapshot (UW Snapshot tab) — the `SCEN_*` block

Read the UW Snapshot tab's four scenario columns (Seller T-12, T-3 Annualized, UW Stabilized Full
Taxes, UW Stabilized Tax-Exempt) for each line: GPR, vacancy bundle, other income, EGI, every OpEx
line, total OpEx, NOI, and the implied cap rates at Ask and PP. These populate `SCEN_T12_*`,
`SCEN_T3_*`, `SCEN_UWT_*` (full tax), `SCEN_UWE_*` (exempt), `SCEN_ASK_CAPS`, `SCEN_PP_CAPS`,
`UW_OPEX_LINES`.

### Comps (Comps tab) — Section V

Sales comps (16-slot, subject highlighted), rent comps by bedroom (subject in-place +
UW-stabilized highlighted), affordability anchors (weight 0), per-bedroom UW rent schedule, and
the construction pipeline (rows 88–101). See [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md).

### Appendix series (Pro Forma D–P)

10-year GPR/EGI/OpEx/NOI/DSCR series for the appendix's 10-Year Operating Projection table.

---

## Tax framing (REQUIRED)

A memo may **lead** with the tax-exempt scenario (the orange column, the headline NOI uplift) —
but it must **always show the full-tax scenario alongside it** in the four-scenario snapshot. Do
not name a specific exemption statute in audience-facing copy unless the deal lead confirms it.
For a pure conventional ACQ with no exemption, the fourth column is omitted and the table is
three-scenario (T-12 / T-3 / UW Stabilized).

---

## Build + deploy workflow

1. Copy `build_esplanade_acq_exempt.py` → `build_<deal>.py`. Swap the deal-variable block, the
   `SCEN_*` four-scenario numbers (from the UW Snapshot tab), the comps (from the Comps tab), the
   base64 images (hero/aerial/kitchen/clubhouse + 5 headshots + logo), and `MEMO_PASSWORD`.
2. Run `python build_<deal>.py` → emits the single self-contained `.html`.
3. Deploy via `redeploy.sh` / the `ssh cat >` pipeline in [EDITING_WORKFLOW.md](shieldstone_acquisitions/deal-memos/EDITING_WORKFLOW.md) to `gsresidential.co/<deal>.html`.

When the fast path produced an `underwrite-spec.json`, the `memo_vars` block already holds the
deal-variable + `SCEN_*` values, so the build script reads them from the spec rather than
re-reading the .xlsx.

---

## Phase 12 QA gate (run BEFORE returning the HTML)

- [ ] Access gate present with **name + email + password** (three fields), POSTs to `/nda`, gates on `MEMO_PASSWORD`, `sessionStorage` remember
- [ ] GS Residential logo (base64) in a sticky nav; `<Deal> | Investment Narrative` brand text; progress bar; `robots noindex` meta
- [ ] Six sections in order with correct ids: `#summary #sponsor #snapshot #market #comps #appendix`
- [ ] Section III four-scenario UW Snapshot table ties to the model's **UW Snapshot** tab (T-12 / T-3 / UW Full Tax / UW Tax-Exempt); exempt column shown alongside full-tax (never exempt-only)
- [ ] Sponsor 5-person grid present
- [ ] **NO** Risks section, **NO** Opportunities cards, **NO** Value-Creation checklist, **NO** Chart.js
- [ ] No raw em-dash characters (`&mdash;` or rephrase)
- [ ] Single self-contained `.html` (base64 images inline, no external refs except Google Fonts)
- [ ] Brand tokens correct: navy `#1B2A4A` / orange `#C86E3A` / warm `#F7F2EC`; Playfair / Josefin / Noto
- [ ] Footer: GS Residential Holdings, LLC + Aventura address + disclaimer + confidentiality

## See also

- [references/12-uw-snapshot.md](.skills/dream-underwrite/references/12-uw-snapshot.md), the UW Snapshot tab the four-scenario table pulls from
- [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md), the Comps tab Section V pulls from
- [templates/field-mapping-acq.md](.skills/dream-underwrite/templates/field-mapping-acq.md) / [field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md), Pro Forma cell map
