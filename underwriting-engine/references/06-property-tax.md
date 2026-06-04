# 06: Property Tax Underwriting

## Purpose

Property tax handling is structurally different across EFB deals (100% exemption, $0 ad valorem), ACQ deals (state-specific reassessment ratios applied to purchase price), and Georgia bond-lease deals (PILOT schedule at 40–60% of fee-simple). This reference consolidates the firm's 6-file tax-exemption research at [shieldstone_acquisitions/tax-exemption-research/](shieldstone_acquisitions/tax-exemption-research/) into the operating handbook the skill needs at Phase 9. It covers EFB exemption flow, state-specific ACQ reassessment ratios (FL 65–80%, TX 60–70%, GA 40%, others), the GA bond-lease PILOT exception, TX non-ad-valorem MUD/PID flags, and the three-scenario stress test for ACQ deals. Source files (also useful for deeper context): [00-master-framework.md](shieldstone_acquisitions/tax-exemption-research/00-master-framework.md), [01-texas-deep-dive.md](shieldstone_acquisitions/tax-exemption-research/01-texas-deep-dive.md), [02-georgia-deep-dive.md](shieldstone_acquisitions/tax-exemption-research/02-georgia-deep-dive.md), [03-florida-deep-dive.md](shieldstone_acquisitions/tax-exemption-research/03-florida-deep-dive.md), [04-feasibility-matrix.md](shieldstone_acquisitions/tax-exemption-research/04-feasibility-matrix.md), [05-executive-synthesis.md](shieldstone_acquisitions/tax-exemption-research/05-executive-synthesis.md).

---

## EFB Tax Flow ($0 Ad Valorem)

For EFB deals routed in Phase 0, property taxes are $0 ad valorem. This is structural, not an assumption.

### How the exemption works (by state)

| State | Statute | Mechanism |
|---|---|---|
| Florida | §196.1978(1) | 501(c)(3) owns fee, tax-exempt bonds fund acquisition. 100% exemption for portions at ≤80% AMI; 75% for 81–120% AMI. Annual DR-504AFH filing by March 1. |
| Florida | §196.199 / §196.1978(3) | Governmental ownership (HFA, Housing Authority). Permanent 100% exemption by virtue of governmental title. |
| Texas | Tex. Tax Code §11.11 + Loc. Gov. Code Ch 303 (PFC) | PFC holds fee title. 100% exemption. Post-HB 2071 set-asides: 50% @ 80% AMI etc. |
| Texas | Tex. Tax Code §11.11 + Loc. Gov. Code Ch 394 (HFC) | HFC holds fee title. 100% exemption. Post-HB 21 (2025): traveling HFC deals dead, issuer must have jurisdiction over the asset. |
| Texas | Tex. Tax Code §11.11 + Loc. Gov. Code Ch 392 (HA) | Housing Authority holds fee. 100% exemption. Most stable post-reform. |
| Texas | Tex. Tax Code §11.1825 (CHDO) | CHDO owns or is GP. 100% exemption with 50% @ 60% AMI + 10% @ 30% AMI set-aside. Compliance audits required. |
| Georgia | O.C.G.A. §8-3-8 (HA fee) | Housing Authority fee ownership. 100% exemption ONLY with Private Enterprise Agreement covering substantially all units. Hard April 1 filing deadline. |

### Standing assumption

For EFB Phase 9 in any state EXCEPT GA bond-lease structures (see below), set:
- Tax exemption breaker = ON
- Percentage exempt = 100%
- Property tax expense flows through model as $0

### Texas mid-year transfer timing

The exemption is effective upon transfer to the exempt entity, but in some Texas counties may require a full tax year to take effect on the assessment roll. **Model Year 1 at full tax expense, Years 2+ at $0** unless counsel confirms mid-year exemption availability. If Year 1 tax expense creates a DSCR shortfall under 1.15x, size an interest reserve per [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md) §Interest Reserve.

### Tax exemption value quantification (always provide)

Calculate and surface in chat for every EFB deal:

```
Annual Tax Exemption Value = Current Annual Property Taxes (from T-12 or tax bill)
10-Year Value = Annual × 10
```

This is the headline EFB value-creation lever. Quote it in commentary, in the investment memo, and in issuer pitches.

---

## GA Bond-Lease PILOT Exception (Critical)

Georgia Development Authority (DA, DDA, URA) bond-lease structures do NOT produce a $0 exemption. They produce a **PILOT** (Payment in Lieu of Taxes) schedule.

### How it works

1. DA issues bonds, holds fee title, and leases the property to the project entity on a 50–99 year leasehold.
2. The project entity (LLC owned by GS Residential + partners) holds the leasehold.
3. The leasehold is the taxable interest. Counties assess leasehold value by inverting a discount rate against the lease payment stream, typically resulting in a leasehold value of ~50% of fee-simple market value.
4. The project entity pays a **PILOT** to the county, structured by the bond-lease documents and negotiated with the county assessor / tax commissioner.

### Typical PILOT magnitude

PILOTs run **40–60% of fee-simple ad valorem** over the 10-year hold. NOT $0.

**Underwrite the modeled PILOT, not zero.** If a deal would have $1.92M/year fee-simple tax, the underwritten PILOT might be $0.80–$1.15M/year. The exact PILOT comes from the bond-lease term sheet and is negotiated up-front with the county.

### When GA can produce $0

The only GA path that yields a clean $0 ad valorem is O.C.G.A. §8-3-8 Housing Authority fee ownership with a Private Enterprise Agreement (PEA) covering substantially all units. Constraints:

- Hard **April 1 filing deadline** for each tax year
- **PEA-by-December-31** prerequisite for the preceding year
- A GA deal closing after Q3 of any year will NOT pick up the HA exemption until the following tax year, model Year 1 at full fee-simple, Year 2+ at $0
- Atlanta Housing, DeKalb HA, and similar HA fee ownership structures qualify

### Routing GA deals

| GA structure | Tax treatment | Route |
|---|---|---|
| DA bond-lease (most common, DDA, URA, CDA) | PILOT 40–60% of fee-simple | EFB (with PILOT, not $0) |
| §8-3-8 HA fee ownership with PEA | $0 ad valorem (after April 1 filing) | EFB |
| 501(c)(3) charitable ownership §48-5-41(a)(4) | Narrow; state case law restrictive on multifamily | EFB if precedent confirms |
| For-profit ownership (no exemption) | Full ad valorem at GA 40% statutory ratio | ACQ |

**Document the chosen structure explicitly in chat at Phase 9** and note the resulting tax flow.

---

## TX Non-Ad-Valorem (MUD/PID): CRITICAL CHECK

Texas master-planned communities commonly have:
- **MUDs** (Municipal Utility Districts)
- **PIDs** (Public Improvement Districts)
- Special water/drainage/road districts

These assessments are NOT covered by the governmental-ownership property tax exemption. They continue regardless of ownership structure.

### Procedure

For every TX deal at Phase 9:

1. Check county records or PSA closing documents for MUD/PID status.
2. If the property is in a MUD, pull current annual MUD assessment.
3. If the property is in a PID, pull PID assessment and remaining payment term.
4. Model MUD/PID assessments separately from ad valorem taxes in the pro forma.
5. **Even on an EFB deal**: MUD/PID expense is non-zero, must be modeled.

### Magnitudes

MUD assessments typically run $300–$800/unit/year. PID assessments vary widely, some PIDs amortize over 20–30 years at $400–$1,500/unit/year.

Note in chat: "TX deal in [Name] MUD with $612/unit annual assessment. NOT covered by EFB exemption. Modeled as separate non-ad-valorem line in Year 1+ pro forma."

---

## ACQ Property Tax (State-Specific Reassessment)

For ACQ deals, property tax is reassessed upon purchase based on state-specific ratios. **Do NOT assume 100% reassessment:** that overstates ongoing tax expense by 20–35% in most states and breaks the deal.

### State Reassessment Ratios

| State | Reassessment Ratio | Notes |
|---|---|---|
| **Florida** | **65–80%** | County-dependent; multifamily typically 65–75%; Save Our Homes doesn't protect commercial |
| **Texas** | **60–70%** | Appraisal district dependent; DFW 65% default; check CAD for subject |
| **Georgia** | **40%** | Statutory 40% of FMV |
| Arizona | 10–18% | LPV (Limited Property Value) system |
| Tennessee | 25% | Commercial ratio |
| North Carolina | 80–100% | County-dependent reassessment cycles |
| South Carolina | 4–6% | Very low for commercial |
| Massachusetts | 100% | Full; quarterly cycle |
| Colorado | 100% | Full; every 2 years |
| Washington | 100% | Full; annual |
| California | 100% at sale → Prop 13 2%/yr cap | Full reassessment at sale, then capped annual growth |
| NY/NJ/PA | Irregular | Municipal cycle, may not reassess on sale |
| **Default (uncertain)** | **65–70%** | Conservative cross-market when state-specific data unavailable |

### Calculation Methodology

```
Year 1 Assessed Value = Purchase Price × Reassessment Ratio
Year 1 Annual Taxes = Year 1 Assessed Value × Millage Rate
Forward growth: 2–3% annually (or per local trend)
```

**Example: Texas multifamily, $75M PP, Denton TX**

```
Reassessment ratio: 65% (DFW default)
Year 1 Assessed Value: $75,000,000 × 0.65 = $48,750,000
Millage rate: 2.45% (Denton ISD + county + city blended)
Year 1 Taxes: $48,750,000 × 0.0245 = $1,194,375
Year 2+: ×1.025 annually
```

**Example: Florida multifamily, $36M PP, Orange County**

```
Reassessment ratio: 70% (Orange Co multifamily typical)
Year 1 Assessed Value: $36,000,000 × 0.70 = $25,200,000
Millage rate: ~1.86%
Year 1 Taxes: $25,200,000 × 0.0186 = $468,720
Year 2+: ×1.02 annually
```

### Florida Reassessment Specifics (REQUIRED for FL ACQ deals)

The Florida calculation has nuances that, if missed, materially understate Year 2+ taxes and break the deal at refi. Use this exact methodology for any FL ACQ deal:

**Year 1 (acquisition year):**

```
Year 1 Assessed Value = current assessed value (from CoStar / tax bill / county records)
Year 1 Taxes         = Year 1 Assessed Value × current millage rate
```

In Florida, the reassessment from the sale does NOT take effect in the acquisition year. The Just Value used for Year 1 is the assessment carried over from the seller's last cycle. This is typically much lower than the new purchase price.

**Year 2 and beyond (post-reassessment):**

```
Year 2 Assessed Value = 80% × Purchase Price
Year 2 Taxes          = Year 2 Assessed Value × current millage rate
Year 3+:              ×2% annual (Florida statutory cap on commercial non-homestead is 10% but trend is 2-3% in stable markets)
```

The 80% multiplier reflects Florida county appraiser practice for commercial multifamily, which assesses at Just Value (market value) discounted by typical operating reserves, depreciation factors, and non-revenue allocations. Verify against the county-specific table for Orange / Hillsborough / Broward / Miami-Dade.

**Save Our Homes cap is REMOVED at sale.** Florida's Save Our Homes amendment (constitutional homestead cap that limits annual increases to 3% or CPI) applies ONLY to homestead-exempted residential property OWNED by the seller. It does NOT apply to commercial / multifamily. Even if you see the seller's bills show modest year-over-year increases, that is the assessor's discretionary trending, not a structural cap that protects the buyer.

The Save Our Homes cap resets at sale for any portfolio. Underwriting based on a continuation of the seller's low effective tax burden is a deal-breaking error in Florida.

**Millage rate: pull from CoStar, NEVER use a state default.**

Florida millage rates vary by 30-80% across counties and overlay districts (school, fire, water, special assessment). State-default millage will misprice Year 1 taxes by hundreds of basis points.

Pull millage from CoStar:

```
Current Millage = (Current Annual Tax / Current Assessed Value)
```

Both numbers are on the CoStar Property Summary that was uploaded at the start of the deal. If CoStar shows tax = $187,432 and assessed value = $9,856,000, then current millage = 1.901%. Use 1.901% for both Year 1 and Year 2+ forecasts (millage rolls are not reset at sale; only the assessed value is).

Document in chat: "FL Property Tax: Year 1 carries seller assessment ($9.86M × 1.901% = $187K). Year 2+ reassesses to 80% × PP ($36M × 0.80 × 1.901% = $548K). Millage pulled from CoStar (current tax $187K / current assessed $9.86M = 1.901%); county-default would have been 1.86%. Save Our Homes does NOT protect the buyer."

**Example: Georgia multifamily, $86.75M PP, DeKalb County (for-profit ownership, NOT bond-lease)**

```
Reassessment ratio: 40% (statutory)
Year 1 Assessed Value: $86,750,000 × 0.40 = $34,700,000
Millage rate: ~4.5% blended
Year 1 Taxes: $34,700,000 × 0.045 = $1,561,500
Year 2+: ×1.03 annually
```

### Three-Scenario Stress Test (ACQ)

| Scenario | Reassessment Assumption | Use |
|---|---|---|
| **Base case** | State-typical ratio per table above | Primary UW |
| **Downside** | 100% reassessment | Stress test |
| **Appeal success** | Base case - 10 to 15% | Optimistic scenario; presented if there is evidence of appeal precedent |

### Research Protocol

1. **Identify county assessor.** Get the assessor's contact info from county website.
2. **Call and ask:**
   - What percentage of purchase price do you assess multifamily upon sale?
   - Is there a lag between sale and reassessment?
   - Current millage rate for this tax district?
   - Any pending millage increases?
3. **Cross-check with recent comps.** Pull 2–3 recent multifamily sales in the same county. Look up post-sale assessed values. Calculate observed ratio: Post-Sale Assessed / Sale Price. Compare to the state-default ratio.
4. **Document source** in the model commentary or chat: "Reassessment ratio 65% per Denton CAD; cross-checked against 3 comps (Comp A 64%, Comp B 67%, Comp C 65%). Using 65% in base case."

### Common Errors

- Assuming 100% reassessment in TX, FL, or GA, overstates taxes 25–60%
- Ignoring reassessment lag (some counties take 12–18 months, model Year 1 at old assessment, Year 2+ at new)
- Forgetting non-ad-valorem MUD/PID/special-district assessments
- Modeling taxes as flat (always grow at 2–3% annually)
- Using residential homestead ratios for multifamily (commercial has different rules in most states)
- Forgetting the GA bond-lease PILOT exception, modeling $0 when reality is 40–60% PILOT

---

## Florida Live Local Act (§196.1979): UPSIDE LAYER ONLY

The Florida Live Local Act (SB 102, SB 328 amendments) creates a property tax exemption for **for-profit ownership** with 40% of units at 80% or 120% AMI set-asides. Critical caveats:

| Feature | Mechanism |
|---|---|
| Ownership | For-profit (standard GP/LP) |
| Set-aside | 40% of units at ≤80% AMI (100% exemption tier) OR ≤120% AMI (75% exemption tier) |
| LURA | Required, recorded with FHFC |
| Recertification | **Annual**, re-application required every tax year |
| Lender-underwritability | **NO, annual recert means lenders will not credit it to NOI** |
| Use in master skill | **Upside layer only**. Never primary path. Document as potential upside that could improve returns if executed, but underwrite without it in the base case. |

If a deal is on the Live Local path but the user wants the base UW to be conservative (lender-underwritable), route the deal as ACQ with full state-specific reassessment and note Live Local as an upside scenario in commentary.

---

## Property Tax Calculator Cell Map (EFB Mini Model)

For populating the property tax inputs at Phase 9:

| Cell | Label | Source | EFB | ACQ |
|---|---|---|---|---|
| S52 | Property Tax Rate (millage) | County assessor / tax bill | Populate (display only) | Populate (drives calc) |
| S53 | Non-Ad Valorem Taxes | Tax bill | Per TX MUD/PID check | Per tax bill |
| S54 | Current Assessed Value | Tax bill / assessor records | Populate (display only) | Populate (Year 1 baseline) |
| S55 | Reassessed Upon Acquisition? | Decision | "No" (exemption) | "Yes" |
| S56 | Reassessed Upon Sale? | Decision | "No" | "Yes" (or "No" per state rule) |
| S57 | Percentage of Value Assessed | State ratio table above | n/a (exempt) | 0.65 (TX), 0.70 (FL), 0.40 (GA), etc. |
| S70 | Tax Exemption Breaker | Switch | 1 (ON) | 0 (OFF) |
| S71 | Percentage Exempt | 0 to 1 | 1 (100%) | 0 |

For the ACQ Mini Model / Flex Model equivalent cells, see [templates/field-mapping-acq.md](.skills/dream-underwrite/templates/field-mapping-acq.md).

---

## See Also

- [shieldstone_acquisitions/tax-exemption-research/00-master-framework.md](shieldstone_acquisitions/tax-exemption-research/00-master-framework.md), full state-by-state exemption framework with archetypes and ranking rubric
- [shieldstone_acquisitions/tax-exemption-research/04-feasibility-matrix.md](shieldstone_acquisitions/tax-exemption-research/04-feasibility-matrix.md), 7-deal × N-path scoring matrix with 90-day execution checks
- [references/02-efb-structure.md](.skills/dream-underwrite/references/02-efb-structure.md), EFB legal frameworks and standing assumptions
- [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md), operating expense framework where property tax sits
- [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md), EFB cell map
- [templates/field-mapping-acq.md](.skills/dream-underwrite/templates/field-mapping-acq.md), ACQ cell map
