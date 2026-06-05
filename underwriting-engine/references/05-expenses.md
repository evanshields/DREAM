# 05: Operating Expense Underwriting

## EFB Override: Property Taxes = $0

For EFB deals, property taxes are **$0:** full exemption via non-profit ownership. This is structural, not an assumption. Skip the property tax analysis section in [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md) §State-Specific Reassessment for EFB deals. All other expense categories below apply as written.

For ACQ (conventional) deals, use the full property tax methodology in [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md).

For GA bond-lease deals, taxes flow as PILOT (40–60% of fee-simple), NOT $0. See [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md) §GA Bond-Lease.

---

## Agency Manual Triangulation (Phase 8)

This reference covers the Shieldstone-manual benchmarks below. **For the full Fannie / Freddie / HUD agency-manual triangulation** (line-by-line minimum extraction from saved PDFs in [shieldstone_acquisitions/agency-manuals/](shieldstone_acquisitions/agency-manuals/)), see [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md). Phase 7 uses this reference; Phase 8 layers on Reference 15.

---

## Expense Benchmarking Standards

### Per-Unit Expense Ranges (Annual)

| Category | Class B Range | Class C Range | Notes |
|---|---|---|---|
| Property Management | 3–5% of EGI | 3–5% of EGI | 3% standard for 100+ units |
| Payroll | $1,500–$2,500 | $1,200–$2,000 | Scale with unit count |
| G&A | $200–$400 | $150–$300 | Legal, software, office |
| Marketing | $100–$300 | $75–$200 | Lower for affordable/EFB |
| Turnover | $100–$250 | $100–$200 | Lower for affordable (tenants stay) |
| R&M | $300–$600 | $400–$800 | Higher for older properties |
| Contract Services | $500–$1,500 | $500–$1,200 | Security, trash, pest, landscaping |
| Utilities (gross) | $800–$1,500 | $800–$1,400 | Water/sewer is typically 60–80% |
| Utility Reimbursements | actual T-12 ratio → UW to 75% | actual T-12 ratio → UW to 75% | Measure actual RUBS recovery from T-12, underwrite to 75% target, document gap |
| Insurance | $600–$1,200 (non-FL) | $700–$1,400 (non-FL) | FL post-Ian floor $900–1,200/u; use actual quote |
| Replacement Reserves | vintage-tiered, see §Replacement Reserves below | vintage-tiered, see §Replacement Reserves below | $250 / $300 / $350 / $400 by age band |

### Total Operating Expense Benchmarks
| Property Type | $/Unit/Year |
|---|---|
| Class A (2020+) | $5,500–$7,500 |
| Class B (2000–2019) | $6,000–$8,500 |
| Class C (pre-2000) | $6,500–$9,500 |

## Property Management

### Property Management
- Standard: 3% of EGI for 100+ unit properties
- Smaller properties (<50 units): 4–5%
- Asset management fee (0.5–1.0% of EGI) is SEPARATE from PM fee, both are appropriate

## Payroll

- UW to T-12 unless staffing changes planned
- Adjust for minimum wage changes in target state
- Budget for 3% annual payroll growth
- Include benefits burden (typically 20–30% on top of base)
- **Lease-up bonuses and temp leasing staff** in T-12 should be STRIPPED out for stabilized pro forma. Near-stabilized properties in late lease-up routinely show $50–150K in lease-up bonuses that won't recur.

## Insurance

### Standard Approach
- Start with current insurance cost from T-12
- Add 15–25% buffer for acquisition (new policy, higher replacement cost)
- Coastal FL/TX: 20–30% premium over inland
- Post-2020 hardening: assume 5–10% annual increases

### Florida Post-Ian Floor (REQUIRED)

The Florida insurance market hardened materially after Hurricane Ian (2022). Carriers exited, retention layers ballooned, and per-unit premiums roughly doubled for many properties.

**Florida insurance floor: $900-1,200/unit/year.** This applies statewide, not just coastal. Underwriting Florida insurance below this floor (e.g., relying on a stale T-12 from 2021 that shows $650/unit) requires:

1. **Explicit user override in chat** ("User confirms FL insurance at $720/unit despite post-Ian $900 floor; basis: bound quote from broker dated [date]")
2. **Agency-risk flag** ("At refi, expect Fannie/Freddie/HUD to require the bona fide quote method per Fannie S&S Guide §203.01 Item 17(c). If the bound quote at refi is at the $900+ floor, the refi will be sized down.")

The skill should refuse to default to the T-12 actual on a FL deal if T-12 is below $900/unit. Either confirm a bound quote, accept the higher pro forma, or note the override.

### Replacement Cost Basis
Verify insurance covers full replacement cost, not just market value.

### Texas Hail Exposure
North Texas (DFW, Denton) has significant hail exposure, budget 10–15% above national benchmarks. South Texas coastal (Houston, Corpus Christi) carries hurricane/windstorm surcharges.

## Repairs, Maintenance & Utilities

### R&M
- T-12 × 1.03–1.05 as baseline
- Add 5–10% for properties >30 years old
- Strip out capex-quality items from T-12 R&M (resurfacing, roof, HVAC replacement → these go in capex)
- For 2020+ vintage core-plus properties, apply +15% buffer over T-12, T-12 R&M is artificially low during early operating years before systems start aging

### Contract Services Red Flags
- Any service dropping to $0 mid-year = seller cut costs to inflate NOI
- Reinstate at full-year run rate + 3% growth
- Common cuts: security patrol, trash removal, landscaping

### Utilities
- T-12 + 3% inflation baseline (5% for Texas ERCOT-deregulated markets due to volatility)
- Model gross utilities AND RUBS recovery separately (not net)
- Water/sewer typically 60–80% of total utility spend

### RUBS Recovery Analysis (REQUIRED — do not skip)

Do NOT assume a flat -75% reimbursement default. Instead, calculate the actual current RUBS recovery ratio from the T-12 and underwrite explicitly toward a target.

**Procedure:**

1. **Calculate current ratio from T-12:**
   ```
   Current RUBS Ratio = (T-12 RUBS revenue + utility reimbursements) / T-12 gross owner-paid utility expense
   ```
   Sources for RUBS revenue: water/sewer reimbursement, electric submeter, trash fee, pest fee, utility admin fee. Confirm these are categorized under Utility Reimbursements (not Other Income, per the RUBS classification trap in [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md)).

2. **Compare current ratio to UW target:**
   - **Default UW target: 75% recovery.** This represents stabilized professional operation with full RUBS billing implementation.
   - If current ratio is already >= 75%: UW at the actual ratio, do not assume improvement is automatic.
   - If current ratio is 60-74%: UW at 75%, document the improvement assumption explicitly.
   - If current ratio is <60%: UW at 75%, flag as aggressive improvement assumption requiring operational lever (RUBS rollout, new utility billing vendor, etc.). Validate via the business plan.

3. **Document in chat commentary** (mandatory, even when current matches UW):
   ```
   RUBS Recovery Analysis:
     T-12 RUBS revenue:         $XXX,XXX
     T-12 gross utilities:      $XXX,XXX
     Current recovery ratio:    XX% (T-12 actual)
     Pro forma recovery ratio:  75% (UW target)
     Improvement assumption:    +XX percentage points
     Operational lever:         [RUBS rollout / submeter install / billing vendor change / N/A]
   ```

This documentation pattern is required so the IC and the agency at refi can see exactly where reimbursement income is coming from and why the assumption is defensible. A 75% UW without supporting analysis is a finding at refi.

## Replacement Reserves

Vintage-tiered by **age at the underwriting date** (not absolute year). The schedule ages naturally as time passes; no need to update the cutoff years annually.

| Age at UW date | $/Unit/Year |
|---|---|
| New build (0-10 years old) | **$250** |
| 11-15 years old | **$300** |
| 16-20 years old | **$350** |
| 20+ years old | **$400** |

At a 2026 UW date, "new build" covers 2016+ vintage; "11-15 years" is 2011-2015; "16-20 years" is 2006-2010; "20+ years" is pre-2006. Roll the cutoffs forward each year as the UW date advances.

**Note on agency floor:** The Fannie Mae S&S Guide §105.01 and HUD MAP Guide Appendix 5 §A.5.7 both publish a $250/unit/year minimum for conventional. The Shieldstone schedule above MEETS the floor at the new-build tier and EXCEEDS it at every older vintage tier, so no agency-resize sensitivity is required at refi for any vintage band. This is a meaningful change from the prior schedule, which set new builds below the agency floor.

For pre-1980 properties (covered by the 20+ years tier at $400), this still understates true capital needs over a 10-year hold for assets with major system replacement risk. Material renovation dollars belong in the capex budget (separate line), not the reserve line.

Treatment: Operating expense (deducted from NOI). Separate from capex budget.

## Expense Growth Assumptions

Standard: 3% annually for most categories. Exceptions:
- Property taxes: Per reassessment analysis ([references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md))
- Insurance: 5–10% in hardening markets
- Utilities: 3–5% (trending higher)
- Payroll: 3–4% (wage inflation)

## OpEx Underwriting Checklist
- [ ] T-12 mapped to standard categories
- [ ] RUBS items pulled OUT of Other Income, INTO Utility Reimbursements
- [ ] Per-unit costs compared to benchmarks
- [ ] Property taxes modeled per Phase 9 (EFB = $0, ACQ = state-specific reassessment, GA = PILOT)
- [ ] Insurance buffered for acquisition (15–25%)
- [ ] Contract services normalized (no mid-year cuts left at $0)
- [ ] Utilities split gross vs. RUBS recovery (not net)
- [ ] Replacement reserves vintage-tiered by age at UW date: $250 (0-10yr) / $300 (11-15yr) / $350 (16-20yr) / $400 (20+yr). New schedule meets or exceeds the $250 agency floor at every tier, no separate refi sensitivity required.
- [ ] FL insurance floor: $900-1,200/u post-Ian; if T-12 below $900/u, explicit user override + agency-risk flag
- [ ] RUBS recovery: actual T-12 ratio measured, gap to 75% UW target documented, operational lever named
- [ ] Lease-up payroll/marketing/turnover stripped for stabilized pro forma
- [ ] All expenses grown at appropriate rates
- [ ] Total expense ratio reasonable (typically 40–55% of EGI)
- [ ] Phase 8 triangulation against Fannie/Freddie/HUD agency manuals run per [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md)

## See Also

- [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md), full property tax framework (EFB exemption, state ratios, GA PILOT, TX non-ad-valorem)
- [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md), Phase 8 agency manual triangulation with line-by-line citations
- [references/11-data-extraction.md](.skills/dream-underwrite/references/11-data-extraction.md), T-12 forensic analysis and red flag detection
- [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md), Shieldstone Multifamily Manual v2 expense standards
