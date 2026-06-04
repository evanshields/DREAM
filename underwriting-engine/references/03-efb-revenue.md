# 03: EFB Revenue Underwriting

> **Pulling FMR / SAFMR / LIHTC rent data:** see [references/00-api-reference.md](.skills/dream-underwrite/references/00-api-reference.md) for the REST API endpoints, auth, and usage patterns across Claude Code / Claude.ai / Claude for Excel. The API is the primary source path (per SKILL.md Phase 4 sourcing chain).

## Mixed-Income AMI Rent Allocation

### Default: 60% / 20% / 20% (Deal-Dependent)

| Tier | Default % | AMI Range | Rent Source | Data Source |
|---|---|---|---|---|
| Low-Income | ~60% | 60-80% AMI | HUD MTSP LIHTC rent limits | REST API `/lihtc` or `/lihtc-table` |
| Missing Middle | ~20% | 80-140% AMI | HUD MTSP LIHTC limits at the relevant AMI tier, or HAP/FMR for voucher units | REST API `/lihtc` or `/fmr` / `/safmr` |
| Full Market Rate | ~20% | 140%+ AMI | Rent comp analysis | CoStar, Apartments.com, broker survey |

Allocations are deal-dependent. The right mix depends on the local market, issuer affordability requirements, and what makes the bonds size. Some deals may be 82/18 (Westwood), others 60/20/20 (Esplanade), others entirely different. Within any tier, some units may carry HAP vouchers at HUD FMR, these are government-guaranteed and the most reliable income stream.

### Low-Income Tier (60-80% AMI)

**Source:** LIHTC rent limits come from HUD MTSP (Multifamily Tax Subsidy Projects) via the Mission Driven AI MCP connector. Same calc methodology Novogradac uses for current-year limits, sourced directly from HUD for FY data lineage.

#### MCP Fetch Pattern

**When Phase 4 needs LIHTC rents, call the MCP directly:**

```
get_lihtc_rent_table(state="TX", county="Denton", year=2026)
```

Returns the full AMI percent × bedroom matrix (50%, 60%, 80%, 100%, 120% AMI rows; Studio/0, 1BR, 2BR, 3BR, 4BR columns). For a single cell, use:

```
get_lihtc_rent(state="TX", county="Denton", year=2026, ami_pct=60, bedroom="2BR")
```

Apply the gross rent ceiling LESS utility allowance to get net rent to owner. If RUBS is in place, the utility allowance calculation changes — document this explicitly.

The MCP server is refreshed quarterly. Per-deal stale-check via `data_freshness()` if the FY rolled over recently.

**Fallback chain if the MCP is unavailable:**
- (b) `reference-data/<county>-<state>-<year>.csv` from [scripts/fetch-hud-fmr.py](.skills/dream-underwrite/scripts/fetch-hud-fmr.py).
- (c) Manual paste from [https://rent-income.novoco.com/](https://rent-income.novoco.com/) — last-resort only. Anti-bot protections kill every scrape attempt, so do not Playwright-fetch or screenshot novoco.com.

#### Other LIHTC Mechanics

**Key points:**
- These are CEILING rents, not targets, underwrite at the published limit unless the rent achievability stress test caps lower
- Rents update annually (typically effective each year)
- Different counties have different limits, always use the correct county
- Can also model 60% AMI or 50% AMI tiers if deal structure requires deeper affordability

### HAP Voucher Units (Within Any Tier)

**Source:** HUD Fair Market Rents (FMR) via the Mission Driven AI HUD & LIHTC MCP connector.

**How to look up (in priority order):**

1. **Mission Driven AI MCP connector.** Call `get_fmr(state="TX", county="Denton", year=2026, bedroom="2BR")` for county/metro FMR, or `get_safmr(zip_code="76201", year=2026, bedroom="2BR")` for SAFMR-designated metros (see SAFMR section below).
2. **Local CSV** at `shieldstone_acquisitions/reference-data/<county>-<state>-<year>.csv`, produced by running [scripts/fetch-hud-fmr.py](.skills/dream-underwrite/scripts/fetch-hud-fmr.py) in Claude Code before opening Claude for Excel.
3. **Manual lookup** at huduser.gov/portal/datasets/fmr.html, last-resort fallback.

**Key points:**
- HAP = Housing Assistance Payment (the Section 8 contract)
- Voucher rents are **government-guaranteed income:** lowest credit risk tier
- FMR may be above or below market rent depending on the MSA
- Strong voucher demand (long waiting lists) = reliable occupancy for this tier
- Underwrite at 100% FMR (or 110% FMR in markets with Small Area FMR or exception rents, confirm locally)

### SAFMR: When ZIP-Level FMR Applies

For HUD metros designated as Small Area FMR (SAFMR) zones, use the **ZIP-code level SAFMR**, NOT the county/metro-level FMR. Designated SAFMR metros include Dallas-Fort Worth, Houston, Atlanta, Charlotte, several others.

**Why this matters:** SAFMR can differ materially from county-level FMR. In DFW, suburban Denton ZIP 76201 SAFMR for 1BR is $1,720; the Denton County FMR might be $1,490. Using the wrong FMR mis-sizes the HAP tier by 10–15%.

**How to fetch:** call `get_safmr(zip_code="76201", year=2026, bedroom="2BR")` on the Mission Driven AI MCP connector. The response payload indicates SAFMR designation status, so no separate huduser.gov check is required. Fallback: huduser.gov/portal/datasets/fmr/smallarea/index.html.

### Full Market Rate Units (140%+ AMI)

**Source:** Rent comp analysis

**How to determine:**
1. Pull 3–5 rent comps in the same submarket (same zip code preferred)
2. Match by vintage (±10 years), unit count (±50%), amenity package
3. Calculate average and median rent by unit type
4. Subject property market-rate rents should fall within comp range
5. If property is being renovated, use post-renovation comp rents (renovated comps)

**Key points:**
- These units have NO income restriction, full market pricing
- Market-rate units provide upside if rents are currently below market
- Don't assume market-rate rents exceed AMI ceilings, in some markets, AMI limits ARE at or above market

### Allocation by Unit Type

When applying 60/20/20 across multiple unit types (2BR, 3BR):

```
For each bedroom type:
  Total units of this type × 60% → 80% AMI tier
  Total units of this type × 20% → HAP voucher tier
  Total units of this type × 20% → Market rate tier

Round to whole units. Verify total = 100% of units.
```

May further split tiers by renovation status (reno vs. unreno) if rent premiums differ.

### HAP Revenue Optimization by Bedroom Type

When allocating HAP voucher units across bedroom types, do NOT default to proportional
allocation (e.g., 20% of each bedroom type). Instead, optimize for revenue by
concentrating HAP units where the spread between FMR and the non-HAP rent for that
bedroom type is widest.

**Why this works:** HAP rents are government-guaranteed, there is no occupancy risk from
pricing above the market-rate or AMI tier. The Housing Authority pays the rent regardless
of local market conditions. Therefore, you should maximize the HAP premium by putting
HAP units where FMR most exceeds what you'd otherwise charge.

**Optimization Steps:**

1. For each bedroom type, calculate the HAP delta:
   ```
   HAP Delta = FMR (or SAFMR) - [Higher of: 80% AMI rent, Market-rate capped rent]
   ```

2. Rank bedroom types by HAP delta from largest to smallest.
3. Concentrate ALL HAP units into the bedroom type(s) with the largest positive delta,
   up to the total HAP allocation count.
4. If the largest-delta bedroom type doesn't have enough units to absorb the full HAP
   allocation, fill the remaining HAP units into the next-largest-delta bedroom type.
5. Verify the total HAP unit count stays within the target allocation (typically 15–20%
   of total units, confirm with issuer).

**Document the optimization:** Note in chat which bedroom type received the HAP
concentration and why: "All 49 HAP units concentrated in 1BR (SAFMR $1,720 vs.
market cap $1,370 = +$350/unit/month delta). 2BR delta was only +$187. This adds
~$110K/year vs. proportional allocation."

**Example: Rayzor Ranch**

| Bedroom | SAFMR | Non-HAP Rent | HAP Delta | HAP Units |
|---|---|---|---|---|
| 1BR/1BA | $1,720 | $1,370 | +$350 | 49 (all HAP here) |
| 2BR/2BA | $1,820 | $1,633 | +$187 | 0 |
| 3BR/2BA | $2,240 | $1,900 | +$340 | 0 |

Note: 3BR had a large delta too, but 1BR had more units available and the highest
absolute delta, so all HAP was concentrated there.

### HAP Achievability Ramp (Year 1 to Year 3)

HAP voucher units do NOT lease at full FMR on day one. The Housing Authority qualification process (tenant screening, HAP contract execution, inspection, voucher transfer) typically takes 6-12 months from lease commencement. Underwriting HAP units at 100% of FMR in Year 1 overstates GPR meaningfully.

**Default achievability schedule:**

| Period | % of FMR achieved | Rationale |
|---|---|---|
| Year 1 | **50%** | New HAP units; voucher placement, qualification, contract execution lag |
| Year 2 | **75%** | Most Year 1 units stabilized; remaining new placements ramping |
| Year 3+ | **90%** | Fully stabilized HAP block; 10% reflects normal turnover/re-qualification friction |

**Two implementation options:**

1. **Bake the ramp into GPR cells** for Years 1-3 (preferred for transparency). E.g., if HAP target is $1,720 FMR × 49 units × 12 months = $1,011K stabilized, Year 1 GPR contribution from HAP = $1,011K × 0.50 = $506K.
2. **Add an explicit Year 1 vacancy buffer of +300-500 bps** to absorb the timing gap, while keeping HAP GPR cells at stabilized FMR. Use this when the model structure does not allow per-tier GPR overrides.

**Document the choice in chat:** "HAP units underwritten with achievability ramp: Year 1 50% / Year 2 75% / Year 3+ 90% of FMR. Implemented as per-tier GPR override in cells X. Alternative would have been Y1 vacancy +400 bps."

### Year 1 Economic Vacancy with HAP Timing Premium

If GPR uses stabilized HAP rents (no per-tier achievability ramp baked in), add **300-500 bps to Year 1 economic vacancy** to absorb the HAP qualification delay. Without this buffer, Year 1 NOI overstates because GPR assumes full HAP collection from month 1.

This is in addition to the standard Year 1 lease-up vacancy curve.

### Note on Economic vs. Physical Vacancy

The Pro Forma `S42` line (and equivalent on the ACQ Mini Model) is **ECONOMIC vacancy, not physical occupancy loss**. It bundles four things:

- Physical vacancy (units empty)
- Concessions (free months, move-in specials)
- Bad debt (uncollected rent)
- Loss-to-lease (gap between asking and in-place)

Underwrite Year 1 = actual T-12 economic loss (read from T-12 forensic block per [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md)). Glide to 7-9% stabilized economic vacancy by Year 4-5.

If the model label just says "Vacancy" without qualifier, treat it as economic vacancy by default. Rename the cell label in chat commentary so the reader does not confuse it with physical occupancy.

## Rent Achievability Stress Test (Required)

After determining AMI ceilings, FMR rates, and market-rate rents, ALWAYS validate
achievability against local rent comps before finalizing the unit mix. Do not skip this
step, it has materially changed underwriting on past deals.

### Step 1: Pull Stabilized Comps

Filter rent comps for:
- Stabilized properties (90%+ occupancy)
- Same vintage band (±10 years of subject)
- Same submarket (same city or ZIP preferred)
- Same or similar class (do not compare Class A to Class C)

### Step 2: Compare Pro Forma Rent to Comp Distribution

For EACH tier and bedroom type, compare the proposed pro forma rent to:

| Metric | Definition | What It Tells You |
|---|---|---|
| Comp Median | 50th percentile of stabilized comp rents | "Average" market positioning |
| Comp 75th Percentile | Rent where 75% of comps are at or below | "Upper market", only top 25% of comps exceed this |
| Comp Maximum | Highest asking rent among comps | Absolute ceiling the market has demonstrated |

**How to calculate the 75th percentile:** Sort all comp rents for a given bedroom type
from lowest to highest. The 75th percentile is the value at position (0.75 × count). If
you have 20 comps, it's the 15th-highest rent. In Excel: `=PERCENTILE(range, 0.75)`.

### Step 3: Flag and Act

| Situation | Action |
|---|---|
| Pro forma rent < Comp Median | Conservative, achievable with high confidence |
| Pro forma rent between Median and 75th pctl | Reasonable, upper-market positioning |
| Pro forma rent between 75th pctl and Max | Aggressive, document justification |
| Pro forma rent > Comp Maximum | NOT achievable, must reprice |

### When AMI Limits Exceed Market Rents

In some markets, particularly secondary and tertiary metros in Texas, the Midwest, and
the Southeast, Novogradac AMI ceilings or HUD FMR rates may exceed what the local
market can actually bear. This means the regulatory maximum is HIGHER than what tenants
are willing and able to pay, because the AMI calculation is based on metro-wide household
income rather than hyperlocal rent dynamics.

**When this occurs:**

1. **Do NOT underwrite to the AMI ceiling.** The ceiling is a regulatory maximum, not a
   market guarantee. Tenants at that AMI level have alternatives in the local market and
   will not pay above-market rent just because the AMI formula permits it.

2. **Cap the affected tier at the 75th percentile of stabilized comps** for that bedroom
   type and vintage. The 75th percentile means you are pricing above 75% of the
   comparable properties in the market, aggressive but defensible. Only the top 25% of
   comps exceed this price point.

3. **Quantify the GPR impact** of the cap versus the full AMI ceiling. Show both
   scenarios so the team can see what's being left on the table and why.

4. **Calculate the effective AMI equivalency** of the capped rent:
   ```
   Effective AMI% = (Capped Rent + Utility Allowance) / (100% AMI Limit) × 100
   ```
   This helps position the deal with issuers, e.g., "our market-rate tier is effectively
   at 85% AMI, deepening affordability without a regulatory requirement."

5. **Document the rationale** with specific comp citations. Name the comps, their rents,
   and explain why the cap is set where it is.

6. **Relabel the tier** in the model: if 100% AMI is capped below the AMI ceiling,
   consider labeling it "Market Rate (AMI-Capped)" rather than "100% AMI" to avoid
   confusion in IC presentations.

### Example: Rayzor Ranch (Denton, TX)

| Bedroom | 100% AMI MTSP | Comp 75th Pctl | Cap Applied | Delta |
|---|---|---|---|---|
| 1BR/1BA | $1,533 | $1,370 | $1,370 | -$163/unit/month |
| 2BR/2BA | $1,832 | $1,633 | $1,633 | -$199/unit/month |
| 3BR/2BA | $2,116 | $1,900 | $1,900 | -$216/unit/month |

Applying the cap reduced GPR by ~$711K annually but produced a defensible underwrite
where every pro forma rent was achievable based on demonstrated comp data.

## Revenue Calculation

```
GPR = Σ across all tiers: (# Units × Monthly Rent × 12)

Vacancy: Build a year-by-year curve (see Vacancy Curve Protocol below).
  Do NOT use a single flat vacancy rate for the entire hold period.

Other Income: Classify T-12 line items into three tiers (see Other Income section below).
  EFB properties generate less turnover-driven income than conventional.

Utility Reimbursements (RUBS):
  75% recovery of gross owner-paid utilities (60-80% range)
  Validate against T-12 actual recovery rate

EGI = GPR - Vacancy + Other Income + Utility Reimbursements
```

## Other Income: Three-Tier Classification

Do not lump all other income into a single $/unit assumption. Classify each T-12 line
item into one of three tiers, then underwrite each tier with the appropriate methodology.

### Tier 1: Recurring / Contractual Income
**Examples:** Laundry room lease, storage unit rentals, parking premiums, cable/internet
bulk agreements, pet rent, commercial lease income (if any)

**UW Treatment:** Underwrite at T-12 run rate + 3% annual growth. These income streams
are contractual and reliable, they persist regardless of tenant turnover.

### Tier 2: Turnover-Driven Income
**Examples:** Application fees, administrative fees, early lease termination penalties,
cleaning charges, redecorating fees, returned check fees, month-to-month premiums

**UW Treatment:** Reduce 30–50% below T-12 for EFB deals. Below-market rents
structurally reduce tenant turnover, which means fewer applications, fewer early
terminations, and fewer make-ready charges. If the T-12 shows $400/unit/year in
turnover-driven income, underwrite $200–280/unit/year for EFB.

### Tier 3: Non-Recurring / One-Time Items
**Examples:** Insurance proceeds, legal settlements, prior-year adjustments, one-time
vendor credits or rebates, construction-period income, referral bonuses from vendors

**UW Treatment:** Strip entirely from pro forma. These are not repeatable income streams
and will not recur under new ownership.

### Typical EFB Other Income Ranges

| Tier | Conventional Range | EFB Range | Notes |
|---|---|---|---|
| Recurring | $200–500/unit/yr | $200–500/unit/yr | Same, not turnover-dependent |
| Turnover-Driven | $200–500/unit/yr | $100–250/unit/yr | 30–50% haircut for EFB |
| Non-Recurring | Varies | $0 | Always strip |
| **Total** | **$400–1,000/unit/yr** | **$300–750/unit/yr** | EFB total is lower |

### Documentation
When writing Other Income to the model, note in chat which line items fell into each
tier and why. This transparency builds confidence in the assumption during IC review.

### Florida Class A Standard Defaults (PUM)

For Florida Class A near-stabilized properties, use these per-unit-per-month defaults unless the T-12 supports something materially different. Total approximates $85-90 PUM, which is a reasonable benchmark for Class A stabilized in Florida.

| Line item | $/unit/month | Notes |
|---|---|---|
| Application fees | $3 | Standard at $50-75 per app, amortized across all units |
| Pet fees | $3 | Pet rent + pet deposits, amortized |
| Cable / Internet | $20 | Only if bulk contract is feasible; otherwise $0 |
| Tenant insurance | $5 | Assumes full RLL (renters legal liability) enrollment |
| Late fees | $25-30 | Tighter collection = higher per-unit |
| Misc / valet trash | $25 | Valet trash $20 + storage/misc $5 |
| Admin fees | $1 | Small but recurring |
| **Total** | **~$85-90 PUM** | Class A FL benchmark |

These are FLORIDA-specific. Other states adjust: Texas typically runs lower (no valet trash standard), Georgia varies by submarket. Use these as the FL benchmark when the T-12 is unavailable or unrepresentative (lease-up, distressed).

When applying, note in chat: "Other Income built from FL Class A defaults: $87 PUM total. T-12 actual was $52 PUM (under-billed). Pro forma underwrites improvement to professional benchmark."

## Vacancy Curve: Year-by-Year Protocol

Do NOT use a flat vacancy assumption across the 10-year hold. Build a custom year-by-year
vacancy curve for each deal, informed by multiple data sources.

### Data Sources (Use in Priority Order)

1. **CoStar submarket vacancy forecast:** filter to the relevant quality tier
   (4/5-star for Class A, 3-star for Class B/C). This provides a market-level baseline.
2. **T-12 trailing occupancy:** calculate T-12, T-6, and T-3 annualized vacancy from
   the property's actual operating data.
3. **Box Score data** (if available), shows month-by-month actual occupancy, often more
   granular than the T-12 summary.
4. **Supply pipeline:** check CoStar for new deliveries in the submarket over the next
   2–3 years. Heavy supply = keep vacancy elevated longer.
5. **Rent comp occupancy:** stabilized comps at 95%+ occupancy suggest the submarket
   can support 5% or lower stabilized vacancy.

### Standard Curve Shapes

**Lease-Up Deals** (T-12 occupancy < 90% or property < 24 months old):
- Year 1: Start at or near T-12 actual vacancy (e.g., 15–25%)
- Year 2: Step down materially (e.g., 8–12%), first full year of EFB pricing
- Year 3: Approach stabilized (e.g., 6–8%)
- Years 4–10: Stabilized (5–6%)

Example curve (Rayzor Ranch, 2022 vintage, T-12 vacancy 28.9%):
15% → 10% → 7% → 6% → 5% → 5% → 5% → 5% → 5% → 5%

**Stabilized Acquisitions** (T-12 occupancy > 90%):
- Year 1: 7–8% (acquisition disruption, tenant turnover during ownership transition)
- Year 2: 6–7%
- Years 3–10: 5–6% stabilized

**EFB Structural Advantage:**
Below-market rents reduce voluntary turnover. EFB stabilized vacancy should be 100–200
basis points below market-rate comps in the same submarket. If comps are at 6–7%
vacancy, EFB stabilized vacancy of 5% is defensible.

### Writing to the Model

Populate the vacancy curve in the model's vacancy row (Row 28 in EFB Mini Model) as
individual year values. Do not use a single flat rate across all years.

Document in chat which data sources informed each segment of the curve:
- "Years 1–3 based on CoStar Denton 4/5-star forecast (9.8% → 7.2% → 6.1%) with
  adjustments for lease-up status"
- "Years 4–10 stabilized at 5% based on comp occupancy (95%+ at Perch Denton,
  Village at Rayzor Ranch) and EFB structural advantage"

## In-Place Rent Analysis

When analyzing the rent roll, calculate:

1. **Average in-place rent by unit type** (occupied units only)
2. **Gap to AMI ceiling:** How far are current rents below HUD MTSP LIHTC limits?
   - Large gap = significant upside without market risk (regulatory ceiling, not demand-dependent)
3. **Gap to FMR:** Are current rents above or below HUD FMR?
   - Below FMR = voucher rents bring immediate income lift
   - Above FMR = can't achieve FMR on those units
4. **Gap to market:** How do current rents compare to comps?
   - Quantifies the market-rate tier opportunity

## Revenue Commentary to Provide

When underwriting EFB revenue, always note:

- **AMI upside quantification:** "In-place rents average $1,723/month for 2BR. The 80% AMI ceiling is $1,898, that's $175/unit/month of regulatory-protected upside with zero market risk."
- **HAP reliability:** "HUD FMR for 2BR in this MSA is $1,958. With a 20% HAP allocation (37 units), that's $869,832/year in government-backed income."
- **Market rate context:** "Comp analysis shows average 2BR rents at $2,106 in the 32839 submarket. Our market-rate tier at $2,050 is priced at a slight discount to the best comp, defensible."
- **Blended rent lift:** "Blended pro forma rent of $2,212 vs. in-place $1,808 = +22.3% revenue lift. Critically, 80% of this lift is driven by AMI ceilings and HUD FMR, not speculative market assumptions."

This color is directly useful for investor presentations and marketing materials.

## Rent Growth

| Tier | Annual Growth Assumption |
|---|---|
| AMI-restricted | 2% (conservative, AMI limits typically increase 2-3% annually) |
| HAP/FMR | 2% (FMR updates annually, generally tracks inflation) |
| Market rate | 2-3% (per submarket trend) |

Use 2% blended as default. Adjust based on local market data.

## See Also

- [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md), conventional/ACQ revenue framework (no AMI, P65 PSF, renovation premiums)
- [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md), Comps tab population (where the rent achievability stress test runs against curated comps)
- [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md), rent roll parsing and T-12 forensic
