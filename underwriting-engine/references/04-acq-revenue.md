# 04: ACQ (Conventional) Revenue Underwriting

## Purpose

The default revenue approach for ANY ACQ deal is the **four-tier mixed-income structure**: 51% affordable (HAP + 80% AMI) / 49% market-rate. The market-rate block is NOT all MLA: only ~10% of total units are MLA / corporate rental (capped), and the remaining ~39% are true market-rate units priced via 75th percentile CoStar comp analysis, split into Classic and Renovated cohorts. This default applies to both ACQ and EFB routing unless the user explicitly specifies "market-rate only" or "no affordability set-asides." When the user says market-rate only, apply the Market-Rate Override section below.

> **Pulling FMR / SAFMR / LIHTC rent data:** see [references/00-api-reference.md](.skills/dream-underwrite/references/00-api-reference.md) for the REST API endpoints, auth, and usage patterns across Claude Code / Claude.ai / Claude for Excel. The API is the primary source path (per SKILL.md Phase 4 sourcing chain).

---

## Four-Tier Mixed-Income Structure (Default)

This is the standard revenue framework for all deals. The economic tiers and their rent sources:

| Tier | Share of Total | Description | Rent Source |
|---|---|---|---|
| **MLA / Corporate rental** | **~10% (CAP)** | Locally-affordable market-rate or corporate-leased units; rent capped at FMR for the bedroom type | HUD FMR |
| **Market (Classic + Renovated)** | **~39%** | True market-rate units, split into Classic and Renovated cohorts | **P75 PSF of CoStar rent comps** (renovated comps for renovated units, classic comps for classic units) |
| **HAP** (Section 8 vouchers) | ~13-26% (= 25-50% of the affordable 51%) | Section 8 voucher units; concentrate on larger bedroom types where FMR spread over AMI is widest | HUD FMR or SAFMR |
| **80% AMI** | ~25-38% (= balance of affordable 51% after HAP) | LIHTC-aligned set-aside tier | Novogradac MTSP at 80% AMI |
| **Total** | **100%** | 51% affordable / 49% market (10% MLA + 39% true market) | |

### Critical Rule: Cap MLA at ~10% of total

**Do NOT assume the full 49% market block is MLA.** MLA / corporate-rental units are capped at FMR and produce significantly less GPR than true market-rate units priced at P75 of submarket comps. Over-allocating to MLA understates achievable revenue. The 10% cap reflects realistic corporate-rental demand and any locally-required affordable market-rate set-asides.

### Market-Rate Tier Pricing (P75 of CoStar comps, by reno cohort)

For the ~39% market-rate units, do NOT apply a flat assumption. Pull the CoStar rent comps that were uploaded at the start of the deal and run:

1. **Split CoStar comps by renovation status:** identify comps that are renovated (recent capex, premium amenities, post-2018 reno date) vs. classic (vintage interiors, no major recent capex).
2. **Compute P75 PSF for each cohort, per bedroom type:** `=PERCENTILE(comp_psf_range, 0.75)` separately for classic comps and renovated comps.
3. **Price subject units by cohort:**
   - Subject **Renovated** units: P75 PSF of RENOVATED CoStar comps × subject SF (per bedroom)
   - Subject **Classic** units: P75 PSF of CLASSIC CoStar comps × subject SF (per bedroom)
4. **Validate the spread:** the renovated-to-classic premium per bedroom should match the renovation premium ranges in §Renovation Premiums. If it does not, sanity-check both cohorts before proceeding.

P75 (vs. P65 used historically) reflects the higher-quality positioning Shieldstone targets post-stabilization with refreshed management, amenities, and lease execution.

### Classic-Market Rent Cap: DEFENSE, Not Extension

A subtle trap in soft submarkets and NOAH properties (see NOAH detection below): the P75 PSF calculation can produce a "market" rent that the subject already meets or exceeds. When that happens, the underwrite should treat the pro forma rent as **rate defense (preventing erosion)**, not **rate extension (revenue growth)**.

Rule:

- If subject's in-place classic rent is already at or above the submarket P75 PSF (i.e., the property is performing at the top of its segment), classic-market pro forma rent must be **less than or equal to in-place rent**. Do not underwrite above current achievement.
- Light reno premium ($75-100/unit) in NOAH or soft submarkets is rate DEFENSE: it prevents the new owner from losing rate as classic units roll, by keeping the unit competitive. It is NOT a revenue uplift.
- In normal submarkets where subject is below P75, the renovated cohort premium IS extension (revenue growth), as documented in §Renovation Premiums.

Document the call in chat: "Subject in-place classic rent $1,485 PSF $1.41 is above submarket P75 PSF $1.38. Treating $50/unit light reno premium as rate defense, not extension. Pro forma classic rent held at $1,485 (no uplift). If user disagrees, reframe as extension and accept the downside DSCR risk if achievement slips."

### NOAH Detection Rule (Required Before Tier Allocation)

A NOAH (Naturally Occurring Affordable Housing) property is one where the in-place rents are already AT or NEAR the 80% AMI ceiling. On a NOAH, the 80% AMI tier produces NO uplift, the property is already there. Allocating units to the 80% AMI tier on a NOAH creates a false sense of "affordability set-aside" that the deal cannot monetize as upside.

**Detection (run at start of Phase 4, BEFORE tier allocation):**

For each unit type (1BR, 2BR, 3BR):

1. Pull the in-place average rent per unit type from the Rent Roll Inputs tab.
2. Pull the 80% AMI rent ceiling per unit type from the HUD/AMI MCP connector (or local CSV per Phase 4 sourcing priority).
3. Compute the ratio: `in-place rent / 80% AMI ceiling`.
4. If the ratio is greater than 0.85, flag the unit type as NOAH.

**If ANY unit type is NOAH:**

- Do NOT use the 80% AMI tier as an "upside" lever on that unit type. The 80% AMI tier rent equals (or is below) the in-place rent, so it adds zero pro forma GPR.
- The only legitimate uplift levers on NOAH properties are:
  - **MLA / corporate rental** (capped at FMR, may be above or below 80% AMI depending on county) — applies to ~10% of total
  - **HAP** (Section 8 vouchers at FMR) — applies to ~13-26% of total
- Confirm the NOAH classification with the user before proceeding to allocation: "1BR in-place rent $1,420 = 92% of 80% AMI ceiling ($1,544). Flagging as NOAH. 80% AMI tier adds no uplift on 1BR. Recommend allocating 1BR to HAP and Market cohorts only. Proceed? (Y/N)"

**Logging:** record the NOAH detection result for each unit type in Claude Log so the IC and the next session see why the 80% AMI tier was sized as it was.

### Tier Allocation for Maximum GPR

1. Compute the dollar premium of each tier (Market Renovated, Market Classic, MLA, 80% AMI, HAP) vs. baseline rent for each bedroom type.
2. Assign HAP to bedroom types where FMR spread vs. 80% AMI is largest (typically 2BR and 3BR).
3. Assign 80% AMI to the remaining affordable units.
4. Assign MLA (capped at 10%) where the corporate-rental demand exists or a local affordability requirement applies.
5. The balance is Market, split into Classic / Renovated per the business plan reno scope.

**Example tier allocation (329-unit property, target: 33 MLA / 128 Market / 66 HAP / 102 80% AMI):**

| Bedroom | Total | MLA | Market | HAP | 80% AMI | Rationale |
|---|---|---|---|---|---|---|
| 1BR | 86 | 0 | 86 | 0 | 0 | All Market (HAP absorbs into larger units first where FMR delta is widest) |
| 2BR | 228 | 33 | 42 | 66 | 87 | Largest bedroom type absorbs the affordability mix and MLA cap |
| 3BR | 15 | 0 | 0 | 0 | 15 | All 80% AMI (largest 80% AMI delta in 3BR) |
| **Total** | **329** | **33 (10%)** | **128 (39%)** | **66 (20%)** | **102 (31%)** | 51% affordable, 49% market |

The 128 Market units split into Classic / Renovated per the renovation business plan; each cohort priced at its respective P75 PSF.

Actual tier allocations are deal-dependent. Run the HAP optimization logic per [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md) HAP Revenue Optimization section.

### Routing Implications

- 4-tier with EFB structure: route EFB (use [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md))
- 4-tier with ACQ structure (full property tax, equity, bridge-to-agency): route ACQ and apply this section

---

## Market-Rate Override (when user specifies no affordability set-asides)

Use this framework only when the user explicitly says "market-rate only," "no affordability set-asides," or "pure market-rate." In that case, do NOT apply the four-tier structure. Underwrite revenue from a market-rate framework with no AMI tiers, no Novogradac lookups, and no HAP overlay. The drivers are in-place rents, market-rate rent growth, renovation premiums (when applicable), and a vacancy curve calibrated to submarket fundamentals.

### In-Place Rent Analysis

From the rent roll (parsed in Phase 2):
- **By bedroom type**: average in-place rent, average SF, rent PSF, count occupied
- **By renovation status** (if labeled SLV / GLD / RENO / CLASSIC): split by-bedroom rents into Classic vs Renovated cohorts
- **Loss-to-lease**: gap between in-place rent and current asking rent (from rent roll's "Market Rent" column if available, else from CoStar comps)

### Market Rent Sourcing: P65 PSF as Base Case

The market-rate override UW base case for pro forma market rent is the **65th percentile PSF** of stabilized rent comps in the same submarket, vintage band, and class.

**Procedure:**
1. Pull rent comps from CoStar. Filter to stabilized (90%+ occupancy), same submarket (ZIP or city), same vintage band (±10 years), same class.
2. Calculate PSF per bedroom type across all comps: PSF = Asking Rent / Avg SF.
3. Sort PSF lowest to highest. Pick the value at position (0.65 × count). In Excel: `=PERCENTILE(range, 0.65)`.
4. Apply P65 PSF to subject SF per bedroom: Pro Forma Rent = P65 PSF × Subject Avg SF.

**Why P65 and not median (P50):**
- P50 = middle of the market. Suitable for a do-nothing UW base case.
- P65 = upper-middle. Implies the operator captures slightly-above-market by virtue of value-add execution, fresh management, refreshed amenities, and competent leasing.
- P75 = aggressive. Reserved for full-scope reno with premium amenity adds, must be supported by 75th-pctl renovated comps.
- P90+ = not achievable without proof. Reprice the deal.

**Sanity checks:**
- Pro forma rent should sit between P50 and P75 of the stabilized comp set.
- If the in-place rent is already at or above P50, the loss-to-lease opportunity is small and the value-add thesis weakens, flag this in commentary.
- If subject is the highest PSF in its submarket without amenity superiority, the underwrite is aggressive.

### Renovation Premiums

When the deal includes a renovation program (light/moderate/heavy scope per [references/07-capex.md](.skills/dream-underwrite/references/07-capex.md)), the pro forma rent has two components:

```
Pro Forma Rent (Renovated) = In-Place Renovated Comp Rent
                              OR
                            P65 PSF of RENOVATED submarket comps × Subject SF
                              OR
                            In-Place Classic Rent + Renovation Premium

Pro Forma Rent (Classic, untouched units) = In-Place Classic Rent + Market Growth
```

**Renovation premium methodology:**

1. Pull comp set of renovated properties in the same submarket and vintage. These are properties with documented recent renovations (CoStar property notes or broker-confirmed).
2. Calculate the spread: Renovated Comp Rent - Classic Comp Rent (same bedroom type).
3. The renovation premium is the spread, NOT a target. Apply it conservatively.
4. Cross-check ROI: Annual Premium × 12 / Renovation Cost Per Unit >= 8% minimum CoC return on the reno spend per [references/07-capex.md](.skills/dream-underwrite/references/07-capex.md).

**Typical premium ranges by scope:**

| Scope | $/unit reno cost | Typical Rent Premium $/month | ROI |
|---|---|---|---|
| Light | $3-8K | $50-125 | 30-60% |
| Moderate | $8-20K | $125-250 | 15-35% |
| Heavy | $20-35K | $250-400 | 8-20% |
| Luxury | $35K+ | $400+ | 5-15% |

If a scope cannot achieve >= 8% ROI on the reno spend, it does not justify the capital outlay. Reprice the scope or cut the program.

### Tier Splits by Renovation Status

For value-add deals, split the unit mix into 2 cohorts per bedroom type:

| Cohort | Description | Rent |
|---|---|---|
| Classic / Untouched | Units NOT renovated in business plan | In-place rent + 2-3% market growth |
| Renovated | Units renovated during business plan | In-place classic + renovation premium |

**Phasing:** the unit mix shifts year by year as units are renovated. Renovate 8-15 units/month for properties 100+ units; full property in 12-24 months depending on scope. The Pro Forma model handles this through the renovation start/end year inputs (rows 38-42 in the EFB Mini Model template; equivalent rows in the ACQ Mini Model).

---

## Near-Stabilized Core-Plus Hurdle Relaxation

When a near-stabilized 2020+ vintage institutional-quality deal routes ACQ, the Shieldstone Multifamily Manual v2 absolute minimums (14% IRR, 1.5x EM, 15% net investor IRR) are **reference points, not hard cuts**. These are near-stabilized, institutional-quality core-plus assets that fall below traditional value-add hurdles but still warrant pursuit.

| Manual standard | Near-stabilized core-plus treatment |
|---|---|
| 14% absolute IRR floor | Reference, not hard cut. Flag but don't auto-pass. |
| 1.5x 5-year EM | Reference. Near-stabilized 7-10yr holds typically achieve 1.7-2.0x. |
| 15% net investor IRR | Reference. |
| Vintage CoC floor (2020+ = 6%) | KEEP. Directional floor. |
| 90/90 rule as CLOSING gate | THROW OUT. Late lease-up properties close before 90/90; bridge period is how you get there. Discuss path to 90/90 for the agency refi (Month 18-30) but do NOT gate closing. |
| 3-method exit cap triangulation | Apply but recognize EFB-influenced market comps typically run 50-100 bps tighter. |

Document the relaxation explicitly in chat: "Treating as near-stabilized core-plus, not traditional value-add. Manual hurdles are directional. Vintage CoC floor 6.0% (2022 build) is the binding constraint."

---

## Vacancy Curve for ACQ Deals

Same year-by-year protocol as [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md) Vacancy Curve section, with these ACQ-specific differences:

| Scenario | Year 1 | Stabilized |
|---|---|---|
| ACQ value-add, in-place 90%+ occ | 7-8% (transition disruption) | 5-6% |
| ACQ value-add, in-place 80-89% occ | 10-12% | 6-7% |
| ACQ value-add, in-place <80% occ | T-12 actual or higher | 7%+ |
| ACQ core-plus, near-stabilized | 7-8% Year 1, 5-6% stabilized | |
| Near-stabilized lease-up curve | 10/10/7/7/6/6/6/6/6/6 | |

EFB has a 100-200 bps structural advantage from below-market rent reducing turnover. ACQ does NOT get this benefit, pro forma vacancy should track submarket comp vacancy.

---

## Concessions for ACQ Deals

Near-stabilized lease-up curve: 5/3/2/1/1/1/1/1/1/1 % of GPR.

ACQ stabilized core-plus: 1-2% of GPR.

ACQ value-add during renovation: 2-4% of GPR during the renovation period (Year 1-2 typically), tapering to 1% stabilized.

Above 5% concessions = aggressive leasing. Either reprice the deal or flag explicitly.

---

## Bad Debt for ACQ Deals

Near-stabilized lease-up: 1.0/1.0/0.5/0.5/0.5/0.5/0.5/0.5/0.5/0.5 %.

ACQ stabilized: 0.5-1.0% of GPR.

T-12 bad debt above 3% of GPR = collections problem. Investigate root cause (tenant credit quality, lease structures, eviction backlog) before normalizing the pro forma.

---

## Other Income for ACQ Deals

Same three-tier classification as [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md) Other Income section, but without the EFB haircut on Tier 2 (turnover-driven).

| Tier | ACQ Range | EFB Range |
|---|---|---|
| Recurring/Contractual | $200-500/unit/yr | $200-500/unit/yr |
| Turnover-Driven | $200-500/unit/yr (full T-12 run rate) | $100-250/unit/yr (30-50% haircut) |
| Non-Recurring | $0 (always strip) | $0 (always strip) |
| **Total** | **$400-1,000/unit/yr** | **$300-750/unit/yr** |

**RUBS classification trap (still applies):** items in T-12 "Other Income" that are utility reimbursements (Water Revenue, Electric Submeter, Trash Fee, Pest Fee) MUST be classified as Utility Reimbursements, NOT Other Income. See [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md).

---

## RUBS Recovery for ACQ Deals

75% default recovery of gross owner-paid utilities. Validate against T-12 actual recovery rate. Same as EFB.

---

## Core-Plus Near-Stabilized ACQ Assumption Defaults

For near-stabilized 2020+ vintage institutional-quality deals routed ACQ, these defaults apply unless overridden:

| Parameter | Default |
|---|---|
| Market rent growth | 2.0%/yr |
| Other income growth | 2.0%/yr |
| Expense growth | 2.5-3.0%/yr |
| Vacancy curve | 10/10/7/7/6/6/6/6/6/6 |
| Concessions | 5/3/2/1/1/1/1/1/1/1 % of GPR |
| Bad debt | 1.0/1.0/0.5/0.5/0.5/0.5/0.5/0.5/0.5/0.5 % |
| Mgmt fee | 3.0% of EGI |
| Levy growth (prop tax) | 2-3%/yr (NOT applicable in EFB or where exemption is in place) |
| Acquisition fee | 0.5-1.0% (per deal size, NOT 5%) |

---

## See Also

- [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md), EFB three-tier revenue framework with AMI/FMR
- [references/07-capex.md](.skills/dream-underwrite/references/07-capex.md), capital expenditure planning and renovation ROI threshold
- [references/10-comps-build.md](.skills/dream-underwrite/references/10-comps-build.md), Comps tab population for P65 PSF rent comp curation
- [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md), Shieldstone Manual return hurdles by market tier
