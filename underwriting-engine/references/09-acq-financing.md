# 09: ACQ Financing: Bridge, Agency, and HUD Multifamily

## Purpose

ACQ deals use conventional debt structures, typically bridge debt for the value-add or lease-up period followed by an agency or HUD refinance into permanent debt. This reference encodes the financing playbook from the Shieldstone Multifamily Manual v2 §6.5 (Refinancing Strategy) and the agency/HUD standards Shieldstone underwrites against. Bond financing is a separate framework, see [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md). The two paths are mutually exclusive on a single deal.

---

## Debt Stack Patterns

| Pattern | Typical Use | Hold |
|---|---|---|
| **Bridge-to-agency** | Value-add: bridge during reno, refi into Fannie/Freddie at stabilization | 3–7 years |
| **Bridge-to-HUD** | Affordable / workforce: bridge during lease-up, HUD 223(f) refi at stabilization | 3–10 years |
| **Agency direct** | Stabilized core / core-plus acquisition with no reno | 5–10 years |
| **Bridge cycle** | Multiple bridge refinances; rarely optimal | 7+ years |
| **Cash** | Small deals, opportunistic | Variable |

For near-stabilized core-plus deals: bridge-to-agency is the dominant path. Bridge during late lease-up (Months 0–24) into agency at Month 24–36.

---

## Bridge Debt

### Bridge Pricing (2024–2026 benchmarks)

| Spread | Typical |
|---|---|
| Rate | 7.25–7.75% (floating, indexed to SOFR + 350–450 bps) |
| Origination | 0.50–1.00% |
| Exit fee | 0.25–0.50% |
| Term | 24 months initial + 1–2 extensions at 6–12 months each |
| Extension fees | 0.25–0.50% per extension |
| Reserve requirements | Interest reserve, capex reserve, often replacement reserve |

### Bridge Sizing

Two methods, dependent on deal structure:

**Method 1, In-place DSCR test** (current operations):
```
Loan = (Current Stabilized NOI / 1.15) / (Bridge Rate + Constant)
```

Where "current stabilized NOI" is the trailing 6-month or trailing 12-month NOI annualized, not pro forma.

**Method 2, Forward-sized with earnout** (lease-up deals):
```
Initial Loan = (In-Place NOI / 1.15) / (Constant)
Earnout Loan = additional proceeds released upon hitting Year 1 UW NOI milestone
```

The earnout structure is common on near-stabilized core-plus deals, gives the lender comfort on Day 1 and gives the sponsor capital release as performance hits underwriting.

### Bridge DSCR Floor

1.15x DSCR on in-place NOI is the standard bridge floor. Some lenders accept 1.10x on premium-quality sponsors with strong track record.

---

## Agency Refinance (Fannie Mae / Freddie Mac)

### The 90/90 Rule

**Definition:** Property must achieve ≥90% economic occupancy for 90 consecutive days before agency lenders will close the refi.

**Economic occupancy vs. physical:**
- Physical occupancy = Occupied units / Total units
- Economic occupancy = Collected rent / Gross potential rent
- The 90/90 rule applies to ECONOMIC occupancy (collections), not physical
- Concessions, bad debt, and loss-to-lease all REDUCE economic occupancy below physical
- A property at 95% physical with 6% concessions may only be 89% economic, fails 90/90

### 90/90 as Refi Gate, NOT Closing Gate

For near-stabilized core-plus deals routed ACQ, the 90/90 rule does NOT gate the acquisition closing. The bridge period IS how you get to 90/90. Discuss path to 90/90 (Month 18–30 typical target) but do not pretend the deal needs 90/90 at close.

For traditional Shieldstone value-add (pre-2000 vintage, 80-89% in-place occupancy at acquisition), 90/90 still gates the refinance, just not the bridge close.

### Optimal Refinance Window

| Timing | Assessment |
|---|---|
| Month 18–23 | Too early, unlikely to have 90/90 |
| **Month 24–30** | **Optimal, reno complete, stabilized, bridge still current** |
| Month 31–36 | Acceptable, may require bridge extension |
| Month 37–48 | Suboptimal, extension fees erode returns |
| Month 49+ | Evaluate sale instead, capital deployed too long |

### Agency Underwriting Standards

| Requirement | Threshold | Source |
|---|---|---|
| Economic occupancy | ≥90% for 90 consecutive days | Fannie / Freddie multifamily guides |
| DSCR | **≥1.25x** (1.20x on select programs) | Trailing 3-month NOI annualized |
| LTV | **≤75%** (up to 80% on select programs) | Appraisal at stabilized value |
| Amortization | 30 years (standard) | |
| Property condition | No deferred maintenance | Updated PCA if >12 months old |
| Borrower liquidity | 9–12 months debt service | Bank statements, net worth |
| Seasoning | 12 months ownership typical | Title, settlement statement |

### Agency Sizing Methodology

**Critical:** Agency sizing uses TRAILING actual NOI, not pro forma. Underwriting must accurately predict what NOI will be at refinance.

The refi loan amount is sized at the **MAXIMUM of THREE constraints** (not two). Most write-ups show only DSCR vs LTV; the debt-yield test is the third leg and frequently binds for value-add deals coming out of bridge.

```
T-3 NOI Annualized = (Trailing 3 months actual NOI) × 4
Debt Constant      = Rate + Amortization Factor (e.g., 5.75% rate / 30yr → 7.00% constant)

Max Loan (DSCR)        = (T-3 NOI Annualized / 1.25) / Debt Constant
Max Loan (LTV)         = Stabilized Appraised Value × 0.75
Max Loan (Debt Yield)  = T-3 NOI Annualized / 0.085    (8.5% DY for agency; 10%+ for HUD)

Refinance Loan = MIN(Max Loan DSCR, Max Loan LTV, Max Loan Debt Yield)
```

**Always document the binding constraint in chat.** It tells the IC where the deal is at risk:

> "Refi sized at $20.4M, DSCR-constrained. LTV would have supported $22.3M; debt yield would have supported $21.0M. The 25-bps NOI miss at refi would compress the DSCR cap to $19.2M (a $1.2M cash-out reduction)."

Binding constraint pattern:
- **DSCR-bound** = thin NOI relative to debt service. Sensitive to NOI shocks at refi. Stress test ±10% NOI.
- **LTV-bound** = strong NOI but weak appraisal. Sensitive to cap rate moves and appraiser comps. Stress test ±50 bps exit cap.
- **Debt-yield-bound** = adequate NOI and value but loan size triggers lender risk overlay (typically high-leverage value-add coming out of bridge). Sensitive to absolute NOI level.

### Refinance Sizing Example

```
STABILIZED PERFORMANCE (Month 30):
  GPR:                  $3,024,000
  Vacancy (5%):         ($151,200)
  Concessions:          ($30,000)
  Other Income:         $120,000
  EGI:                  $2,962,800
  OpEx:                 ($1,180,000)
  NOI:                  $1,782,800

AGENCY LOAN SIZING:
  Target DSCR:          1.25x
  Rate:                 5.75% (agency rate at refi)
  Amortization:         30 years
  Constant:             7.00%

  Max Annual DS:        $1,782,800 / 1.25 = $1,426,240
  Max Loan (DSCR):      $1,426,240 / 0.070 = $20,374,857

  Appraised Value:      $29,713,333 (6.0% cap)
  Max Loan (75% LTV):   $22,285,000

  Binding: DSCR
  Refi Loan: $20,375,000
```

---

## HUD 223(f) Refinance

HUD 223(f) is the Federal Housing Administration's multifamily refinance program. Used for both market-rate and affordable. More flexible than agency on certain dimensions, more stringent on others.

### HUD 223(f) LTV Caps (CRITICAL: Memorize)

| Property Type | Refinance | Acquisition |
|---|---|---|
| Affordable (LIHTC, set-aside, etc.) | **87% LTV** | **85% LTV** |
| Market-rate | **85% LTV** | **83.3% LTV** |

These caps drive the maximum loan when HUD is in the takeout path.

### HUD 223(f) Standards (key)

| Requirement | Threshold |
|---|---|
| DSCR | 1.176x market-rate / 1.11x affordable (lower than agency) |
| Amortization | Up to 35 years |
| Term | Up to 35 years (matches amort, fully amortizing) |
| Loan term | Typically 35-year fixed |
| MIP | Mortgage Insurance Premium, ongoing fee, factored into all-in cost |
| Property condition | Stricter than agency, needs full Project Capital Needs Assessment (PCNA) |

### HUD MAP Guide

The HUD MAP Guide (Handbook 4430.G) is the bible for HUD multifamily underwriting standards. Operating expense minimums, payroll, insurance, replacement reserves all defined there. See [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md) for per-line-item HUD MAP citations once the manual PDF is saved.

### When HUD Beats Agency

HUD 223(f) typically beats agency when:
- The deal is **affordable** (87% vs 75% LTV is a huge difference)
- Long-term hold (35-year amort beats 30-year)
- Below-market in-place rents (HUD UW is sometimes more flexible than agency)
- Borrower has time and patience (HUD takes 6–9 months to close vs 60–90 days for agency)

### When Agency Beats HUD

Agency typically beats HUD when:
- The deal is market-rate (85% vs 75% LTV difference disappears for market-rate refi)
- The borrower needs speed (agency closes faster)
- The borrower wants 5- or 10-year fixed, not 35-year fixed
- The deal will be sold within 5–7 years (35-year amort doesn't help)

---

## Conventional Debt Sizing: Master Workflow

When sizing ACQ debt at Phase 10, follow this sequence:

```
STEP 1: Bridge sizing (acquisition)
  Inputs: In-place NOI (last 6-12 months annualized), bridge rate (7.25-7.75%), 1.15x DSCR
  Output: Initial bridge loan + earnout structure if lease-up

STEP 2: Forward project Year 1-3 NOI
  Use [references/04-acq-revenue.md] revenue framework + [references/05-expenses.md] expense framework

STEP 3: Agency takeout sizing
  Inputs: Projected T-3 NOI annualized at refinance, agency rate (current market), 1.25x DSCR, 75% LTV, 30-yr amort
  Output: Refi loan amount + cash-out delta

STEP 4: Compare to HUD 223(f)
  Inputs: Same NOI, HUD rate (typically lower than agency), 1.176x or 1.11x DSCR, LTV cap by property type, 35-yr amort
  Output: HUD loan amount + cash-out delta

STEP 5: Choose path
  Pick the structure that maximizes risk-adjusted IRR and matches the equity strategy (cash-out timing, hold length, return profile)

STEP 6: Stress test
  Show refi proceeds at NOI -10% (NOI shortfall), refi rate +100 bps (rate stress)
  Both stresses should still close the bridge payoff with reasonable cushion
```

---

## Refinance Risk Mitigation

### NOI Shortfall at Refinance

If actual NOI at refi is 10% below underwritten, the refi loan shrinks proportionally, and cash-out drops by ~$2M for every $200K of NOI shortfall (at 7% constant, 1.25x DSCR).

Mitigants:
- Conservative NOI underwriting, don't stretch rent premiums to UW limits
- Accurate property tax reassessment per [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md)
- Build 5–10% NOI cushion into refi projections
- Realistic operating expense assumptions

### Interest Rate Risk

For every 50 bps rate increase, refi proceeds drop ~6–8% at agency sizing. Mitigants:
- Rate-lock when available
- Forward starting interest rate hedges
- Maintain enough bridge cushion to absorb a delayed refi if rates spike

### Appraisal Shortfall

LTV-constrained deals can be capped by a low appraisal. Mitigants:
- Order an early appraisal in Month 18–24 to spot trouble before locking refi
- Cross-reference with recent sale comps in same submarket
- Document NOI growth narrative for the appraiser

### Delayed Stabilization

If the property does not hit 90/90 by Month 30, bridge extension fees compound. Mitigants:
- Phase renovation to maintain 80%+ occupancy throughout
- Lease aggressively at competitive rents in renovation period
- Build 60–90 day cushion into the 90/90 target month

---

## DSCR Row Must Adapt to Active Loan Period

The Senior DSCR row in the EFB Mini Model (row 78) and the equivalent row in the ACQ Mini Model must switch between bridge debt service and refi P+I based on the active loan period. The naive formula `=NOI / -SUM(F29:F30)` (which always pulls from the bridge DS rows) silently overstates DSCR after bridge payoff because the bridge rows go to zero or stale post-refi.

**Correct formula pattern:**

```excel
=NOI / -IF(F$1 <= B57, SUM(F29:F30), SUM(F31:F32))
```

Where:
- `F$1` is the year header (Year 1, Year 2, ... Year 10)
- `B57` is the bridge term cell (e.g., 3 years)
- Rows 29-30 are bridge debt service (interest + any principal during bridge)
- Rows 31-32 are refi P+I (interest + amortized principal post-refi close)

The IF wrapper ensures:
- Years 1 through B57 (bridge term): DSCR pulls bridge DS
- Years B57+1 onward (post-refi): DSCR pulls refi P+I

This is one of the 5 known formula bugs documented in [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md) §Pre-Population Formula Audit. Phase 3 audit catches it; this section documents the WHY for the patch.

---

## Per-Period DSCR Validation (REQUIRED in Phase 10)

At Phase 10 (Sizing / Resizing), validate the Senior DSCR for every year of the 10-year hold against the active loan's floor. Different periods have different floors because different loans are in place.

| Year | Active Loan | Loan Phase | DSCR Floor |
|---|---|---|---|
| Year 1 | Bridge | IO | ≥ 1.10x |
| Year 2 | Bridge | IO (last year of bridge typically) | ≥ 1.10x |
| Year 3 | Refi | IO (if refi has 3yr IO period) | ≥ 1.25x |
| Year 4 | Refi | IO continuing | ≥ 1.25x |
| Year 5 | Refi | IO continuing or first amort year | ≥ 1.25x |
| Year 6 | Refi | First amort year (or continuing) | ≥ 1.25x |
| Years 7-10 | Refi | Amortizing + exit | ≥ 1.25x |

Adjust the row above for the specific deal's bridge term and refi IO period. The pattern is: bridge years floor at 1.10x; refi years floor at 1.25x.

**At Phase 10, output a per-year DSCR table in chat:**

```
DSCR Validation (Senior):
  Year  Active Loan  Phase    DSCR   Floor  Pass
  1     Bridge       IO       1.12x  1.10x  OK
  2     Bridge       IO       1.18x  1.10x  OK
  3     Refi         IO       1.31x  1.25x  OK
  4     Refi         IO       1.37x  1.25x  OK
  5     Refi         IO       1.42x  1.25x  OK
  6     Refi         Amort    1.27x  1.25x  TIGHT (only 2 bps cushion)
  7     Refi         Amort    1.33x  1.25x  OK
  8     Refi         Amort    1.39x  1.25x  OK
  9     Refi         Amort    1.45x  1.25x  OK
  10    Refi         Exit     1.51x  1.25x  OK
```

Any year that fails the floor is a hard flag, do not advance to Phase 11 without resizing or flagging the gap.

---

## Near-Stabilized Core-Plus Notes

When sizing near-stabilized core-plus bridge debt:

1. **In-place DSCR test on current ~90% occ NOI** (not Year 1 UW). Bridge lenders care about actual operations at close.
2. **Forward-sized earnout** structures release additional proceeds at Year 1 UW NOI milestone. Common structure: $50–60M initial + $10–15M earnout.
3. **90/90 rule does NOT gate closing.** The bridge IS how you get to 90/90. Refi target Month 24–30.
4. **Stabilization timing**: 60–90 day cushion built into the 90/90 target.

---

## See Also

- [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md), revenue side of ACQ underwrite
- [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md), operating expense framework
- [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md), return hurdles by market tier, exit cap triangulation
- [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md), Fannie/Freddie/HUD agency-manual triangulation for OpEx
- [shieldstone_acquisitions/agency-manuals/](shieldstone_acquisitions/agency-manuals/), saved agency UW manuals (firm-wide resource)
- [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md), EFB bond sizing alternative structure
