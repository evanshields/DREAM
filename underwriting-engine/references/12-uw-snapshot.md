# 12: UW Snapshot Finalization

## Purpose

The UW Snapshot tab is the deliverable artifact. It pulls every key output from the Pro Forma and Comps tabs into a single page summarizing the deal: revenue, expenses, NOI, debt, returns. Phase 11b runs the snapshot finalization for both EFB and ACQ models, with the critical distinction being **with-tax vs. without-tax pulls** for EFB deals (the snapshot displays both views). This reference encodes the reconciliation logic, sanity check list, and final metrics audit the skill must run before declaring the model "delivered."

---

## UW Snapshot Sheet Structure

The Snapshot tab typically contains:

| Section | Content |
|---|---|
| Deal Identity | Asset name, address, units, year built, $/unit, $/SF |
| Capital Stack | Purchase price, bond amount (EFB) or loan amount (ACQ), LTV, equity (ACQ only) |
| Revenue Summary | GPR (year 1, year 10), Vacancy, Other Income, RUBS, EGI |
| Expense Summary | Total OpEx, OpEx/unit, OpEx ratio (% of EGI) |
| NOI | Year 1, Year 3, Year 5, Year 10 |
| Debt Service | Annual DS, DSCR Y1/Y3/Y5/Y10 |
| Returns (ACQ) | Levered IRR, Equity Multiple, Cash-on-Cash Y1/Y5, net investor IRR |
| Bond Metrics (EFB) | Bond proceeds vs TPC, sources = uses test, ROFR exit value |
| Exit | Sale year, exit cap, exit price, $/unit at exit |
| Sensitivity | DSCR / IRR at rate ± 50 bps, exit cap ± 50 bps |

Exact cell map varies by model template. See [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md) and [templates/field-mapping-acq.md](.skills/dream-underwrite/templates/field-mapping-acq.md).

---

## T-12 / T-6 / T-3 Reconciliation

The Snapshot should display three views of NOI:

| View | What It Shows | When It's Bound |
|---|---|---|
| **T-12 annualized** | Full trailing 12-month performance | Stabilized properties, mature operations |
| **T-6 annualized** | Trailing 6 months × 2 | Mid-stabilization (lease-up properties) |
| **T-3 annualized** | Trailing 3 months × 4 | Late lease-up; **agency refi uses T-3 as sizing basis** |

For near-stabilized late lease-up deals, the T-3 is the best proxy for stabilized run-rate. T-12 is artificially depressed.

For traditional value-add deals, the T-12 is the baseline operating reality.

**Always cite all three in chat** when presenting the snapshot:

```
T-12 NOI Annualized: $X
T-6 NOI Annualized: $Y
T-3 NOI Annualized: $Z
Trajectory: improving / flat / deteriorating
UW Year 1 NOI: $W (compared to T-3 = $Z)
Delta: +/- N% (flag if >15% above T-3)
```

---

## With-Tax vs. Without-Tax Pulls (EFB Only)

For EFB deals, the Snapshot pulls Pro Forma NOI **two ways**:

1. **Full Pro Forma NOI (with property tax modeled per pre-exemption assumption):** shows what the property would generate if it were taxed normally. Used for:
   - Quantifying the exemption value (annual savings)
   - Benchmarking against taxable-product market cap rates
   - IC presentations ("if we owned this conventionally, NOI would be $X less")

2. **EFB Pro Forma NOI (with property tax = $0):** the actual UW number. Drives:
   - Bond sizing
   - DSCR calculation
   - All return metrics

### Cell Logic

| Driver | Behavior |
|---|---|
| Tax exemption breaker (S70 = 1) | Property tax expense flows as $0 to NOI |
| Tax exemption breaker (S70 = 0) | Full taxable expense flows to NOI (this is the "with-tax" view) |

To toggle in Excel for snapshot purposes, the model typically has either:
- A separate "Tax Scenario" row that runs both calculations in parallel
- A switch input that flips for one section vs another
- A shadow calculation block

Verify the snapshot correctly displays BOTH views for EFB deals.

### Documentation

Note in chat: "EFB pro forma displays full NOI ($X with-tax) and EFB-adjusted NOI ($Y without-tax). Annual tax savings = $X - $Y = $Z. 10-year exemption value = $Z × 10."

---

## Sanity Check List (Run at Phase 11 Delivery)

Before declaring the model delivered, work through this checklist. Surface any failure to the user in chat.

### Pro Forma Sanity

- [ ] **Sources = Uses at Year 0**: net to approximately $0. Anything more than $50K of mismatch indicates an input error.
- [ ] **Unit count ties**: Pro Forma B6 (formula =S22) = rent roll unit count = T-12 unit count.
- [ ] **In-place rent ties**: Pro Forma U22 weighted avg in-place rent matches rent roll occupied-unit average within $25/unit.
- [ ] **Pro forma rent within achievability**: each tier's pro forma rent <= 75th percentile of comp set per [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md) §Rent Achievability.
- [ ] **Vacancy curve is NOT flat**: at least three distinct values across Years 1–10.
- [ ] **Other Income three-tier breakdown documented**: at least one chat line citing the tier classification of each T-12 line.

### Expense Sanity

- [ ] **Property Management = 3% of EGI** (or 4–5% for <50 units).
- [ ] **Property taxes = $0 for EFB** (with-tax view exists separately) OR per state ratio for ACQ.
- [ ] **No expense line at $0 unless intentional** (caught by Phase 1 T-12 forensic; reinstate seller-cut contracts).
- [ ] **Insurance has 15–25% buffer** over T-12 (or 20–30% coastal FL/TX).
- [ ] **Total expense ratio 40–55% of EGI** for Class B; flag if outside.
- [ ] **Phase 8 agency triangulation cited** per category per [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md).

### Financing Sanity

#### EFB
- [ ] **Year 1 DSCR >= 1.15x** (or interest reserve sized + verified per [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md))
- [ ] **DSCR trajectory grows year over year** (with 3% rent growth and fixed interest)
- [ ] **Bond proceeds cover Total Project Cost** (sources = uses with no equity gap)
- [ ] **Bond rate sensitivity ± 50 bps** documented in commentary
- [ ] **Year 10 DSCR target 1.40x+** for healthy ROFR exercise

#### ACQ
- [ ] **In-place DSCR on bridge >= 1.15x** (current operations support the bridge close)
- [ ] **Forward T-3 NOI annualized supports agency refi at 1.25x DSCR**
- [ ] **75% LTV not breached** at agency refi appraisal
- [ ] **HUD 223(f) alternative sized** (per [references/09-acq-financing.md](.skills/dream-underwrite/references/09-acq-financing.md))
- [ ] **Refi proceeds at NOI -10% stress** still close out bridge with cushion

### Returns Sanity (ACQ)

- [ ] **Levered IRR vs. hurdle**: per market tier per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md) (Gateway 14–16%, Secondary 16–19%, Tertiary 18–22%) PLUS adjustments
- [ ] **Stabilized CoC vs. vintage floor**: 6.0% (2020+) / 7.0% (2000–2019) / 7.5–8.0% (pre-2000)
- [ ] **Equity Multiple >= 1.5x** (5-year hold)
- [ ] **Net investor IRR >= 15%** (after promote and fees)
- [ ] **Going-in cap rate within ±15% of submarket sales comp median**
- [ ] **Exit cap >= entry cap** (never embed compression)

### Exit Sanity

- [ ] **Exit cap from three-method triangulation** per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md): take HIGHEST of (Treasury spread, comp $/unit validation, entry + 100 bps)
- [ ] **Costs of sale: 2%**
- [ ] **Sale year matches business plan** (5 / 7 / 10)
- [ ] **EFB**: exit = ROFR exercise, no market cap exit needed (separate post-ROFR analysis)

### Comp Sanity (already validated at Phase 11a)

- [ ] **Sales comp weight total = 1.00**
- [ ] **Rent comp weight total = 1.00**
- [ ] **Affordability rows weight = 0**
- [ ] **Per-BR SUMIF criteria range = `$C$70:$C$84`** (NOT bedroom column)
- [ ] **No `#REF!` or `#DIV/0!` in summary rows**

---

## Final Metrics Audit (Headline Numbers to Present)

When delivering the model, present these headline numbers in chat in this order:

```
DEAL: [Property Name], [EFB or ACQ]
  Units: X | Year Built: Y | Class: Z | $/unit: $W

REVENUE:
  GPR Year 1: $X
  Vacancy Year 1: X% ($Y)
  Other Income: $Z/unit/yr
  EGI Year 1: $X
  Pro Forma Lift vs In-Place: +X% blended

EXPENSES:
  Total OpEx Year 1: $X ($Y/unit)
  OpEx Ratio: X% of EGI
  Property Tax: $0 (EFB) OR $X (ACQ)

NOI:
  Year 1: $X
  Year 5: $Y
  Year 10: $Z
  Growth: X% CAGR

CAPITAL STACK:
  Bond Amount (EFB) or Loan + Equity (ACQ): $X
  Bond Rate (EFB) or Bridge/Agency Rate (ACQ): X%
  Total Project Cost: $X
  Sources = Uses: pass / fail

DSCR (EFB):
  Year 1: X.XXx
  Year 5: X.XXx
  Year 10: X.XXx
  Interest Reserve: $X (if sized)

RETURNS (ACQ):
  Levered IRR: X%
  Equity Multiple: X.XXx
  Year 1 CoC: X%
  Stabilized CoC: X%
  Net Investor IRR: X%

EXIT:
  Exit Year: X
  Exit Cap: X%
  Exit Price: $X ($Y/unit)
  Exit IRR margin vs entry: +/- X bps

VALUE CREATION:
  EFB: Tax exemption $X/yr × 10 = $Y; AMI upside $Z/unit/mo lift
  ACQ: Rent gain $X/unit/mo lift; CapEx $Y; NOI growth $Z CAGR

KEY FLAGS:
  [list any sanity check failures]
  [list any aggressive assumptions]
  [list any data gaps]
```

This is the document the user copies into the investment memo.

---

## See Also

- [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md), return hurdle stack and exit cap triangulation
- [references/14-html-memo.md](.skills/dream-underwrite/references/14-html-memo.md), Phase 12 HTML investment memo (takes Snapshot as input)
- [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md), EFB Mini Model cell map
- [templates/field-mapping-acq.md](.skills/dream-underwrite/templates/field-mapping-acq.md), ACQ Mini Model cell map
