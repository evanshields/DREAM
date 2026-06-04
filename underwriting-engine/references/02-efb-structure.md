# 02: EFB Deal Structure

## What Are Essential Function Bonds?

EFBs are tax-exempt governmental purpose revenue bonds issued by public entities (housing authorities, HFAs, joint powers authorities) to finance facilities performing an "essential governmental function", including affordable and workforce multifamily housing. Under Section 103 of the Internal Revenue Code, interest on EFBs is federally tax-exempt because the issuer owns the property for a public purpose.

EFBs are NOT subject to private-activity volume cap (unlike 142(d) LIHTC bonds), do NOT require TEFRA hearings, and have NO federal costs-of-issuance cap, making them the most flexible tax-exempt structure for workforce housing.

## EFB vs. Other Tax-Exempt Structures

| Feature | EFB (Governmental) | 501(c)(3) Bonds | 142(d) Exempt Facility |
|---|---|---|---|
| Volume cap required | No | No | Yes |
| For-profit ownership | No | No | Yes |
| LIHTC eligible | No | No | Yes |
| Private business use limit | 10% | 5% | N/A |
| TEFRA hearing | No | Yes | Yes |
| COI cap (2%) | No | Yes | Yes |
| Federal income set-asides | None (state law may impose) | Per charitable purpose | 20/50 or 40/60 AMI |

## Transaction Parties

### Issuer / Borrower / Owner
- Housing authority, HFA, city, county, or similar public instrumentality
- Owns the property fee-simple (or via ground lease to affiliated entity)
- Tax-exempt status provides property tax exemption
- Issues revenue bonds secured by project revenues and assets (non-recourse to issuer)
- May use its credit rating to improve bond pricing (e.g., JHA's A+ rating on Westwood)

### Project Administrator (Shieldstone)
- Sources deals, negotiates PSA, coordinates DD, structures financing
- Does NOT own any interest in the property (no de minimis ownership unlike LIHTC)
- Compensated via fees from bond proceeds + ongoing admin fees + sponsor bonds
- Bears front-end cost risk (deposits, legal, advisory fees lost if deal doesn't close)
- Structures ROFR to acquire property at bond maturity

### Bond Trustee
- Independent fiduciary managing bond proceeds
- Collects project revenues (often weekly), distributes per waterfall priority
- Enforces bond covenants (DSCR, occupancy, compliance)

## Property Tax Exemption

### How It Works
Projects owned by housing authorities or other exempt governmental entities are fully exempt from local property taxation under Florida law (Chapter 421, housing authority exemption). Authorities may make voluntary payments in lieu of taxes (PILOTs).

Florida-specific exemptions also available under Section 196.1978:
- 100% exemption for units serving households at or below 80% AMI
- 75% exemption for units serving 81-120% AMI
- Properties must have 71+ units for certain benefits
- Requires recorded Land Use Restriction Agreement (LURA)

### Standing Assumption
For EFB underwriting, property taxes = $0. Do not model property tax expense. Do not question whether the exemption will be obtained.

### Value Quantification
Always calculate and highlight:
```
Annual Tax Exemption Value = Current Property Taxes from T-12 or tax bill
10-Year Value = Annual Exemption x 10
```
This is a key selling point for issuer pitches and investor presentations.

## Developer / Project Administrator Compensation

### Compensation Components (per Norris George & Ostrow)

1. **Up-front cash fee:** 1-5% of purchase price at closing, funded from bond proceeds
2. **Subordinate sponsor bonds:** 5-6% of purchase price, yielding 7-10%, paid from deeply subordinated project cash flow (after opex, senior DS, and all reserves). Tax-exempt interest. Payment depends on project performance, aligns sponsor incentives.
3. **Ongoing admin fee:** 10-12 bps of bond amount annually for oversight, compliance, reporting

### Shieldstone Standard
Developer fee target: 10% of total project cost. May be structured as:
- 100% cash at closing, OR
- 5% cash + 5% capitalized as subordinate B-piece/sponsor bonds through maturity

### Critical Compliance
- Fees must qualify under IRS QMC (Qualified Management Contract) safe harbors (Rev. Proc. 2017-13)
- Compensation must be reasonable, cannot be based on net profits
- Fixed fees, capitated fees, per-unit fees are standard
- Sponsor bonds must be "true debt", not recharacterizable as equity (no uncapped upside, no full guarantees)
- Total sponsor compensation cannot exceed value of services rendered
- Contract term cannot exceed 30 years or 80% of property's economic useful life

## Turbo Amortization

Unlike conventional scheduled amortization, turbo amortization requires principal repayment only from cash available after payment of operating expenses and interest. If there is no cash for principal in any period, it is simply deferred, there is no default. This substantially lowers default risk, and is a key reason municipal bond fund investors accept the structure.

## Cash Flow Waterfall (Standard 10-Tier)

```
1. Operating Fund, property opex (insurance, utilities, PM, maintenance)
2. Administrative Expense Fund, trustee fee, issuer fees
3. Capital Expense Fund, replacement reserves
4. Administrator/Operator Fee Fund, project admin compensation
5. Rebate Fund, IRS arbitrage rebate
6. Senior Debt Service Fund, interest + turbo principal on senior bonds
7. Operating Reserve Fund, backstop for operating shortfalls
8. Coverage and Senior DS Reserve Funds
9. Subordinate Debt Service Fund, sponsor bond interest/principal
10. Surplus/Excess Revenue Fund, remainder to public owner
```

Each tier must be filled completely before funds flow to the next.

**Note:** The EFB Mini Model Excel file does not explicitly model all 10 waterfall tiers. The model captures the key flows (revenue → opex → NOI → debt service → cash flow). The full waterfall is a bond structuring document, not a pro forma modeling exercise. Understand the waterfall conceptually but don't try to force all 10 tiers into the spreadsheet.

## ROFR (Right of First Refusal)

Structured into JV or indenture documents at closing. At bond maturity (Year 10), Shieldstone exercises ROFR to acquire property outright. Post-ROFR: hold as conventional owner, refinance, or sell at market.

## Market Track Record

Per Harvard Joint Center for Housing Studies (2003): **zero default rate** across 275 EFB issues reviewed. California JPAs issued over $8 billion in EFBs between 2019-2022, creating ~14,000 units of publicly owned workforce housing in 45+ financings. The model is now expanding to Florida and Texas.

## Florida Legal Framework

### Eligible Issuers
- Local housing authorities (Chapter 421, Florida Statutes)
- County housing finance authorities (Part IV of Chapter 159)
- Florida Housing Finance Corporation (FHFC), statewide
- Cities and counties directly

### Key Statutes
- Chapter 421: Housing authority powers, bond issuance, tax exemption
- Chapter 159, Part IV: HFA powers, revenue bonds, property ownership
- Section 196.1978: Affordable/workforce housing property tax exemptions
- Section 103 IRC: Federal tax-exempt bond status

### Florida Property Tax Advantage
Florida's apartment-homestead classification ratios are among the highest nationally (Jacksonville: 3.44x, third highest in the nation). This means property tax elimination through public ownership creates disproportionately large cash flow savings in Florida metros. Combined with Save Our Homes assessment resets upon sale, the exemption is especially valuable for acquisitions.

## Texas EFB Framework

### Eligible Issuers
- Local housing authorities (Chapter 392, Texas Local Government Code)
- Housing finance corporations (Chapter 394, Texas Local Government Code)
- Public facility corporations (PFCs) under Chapter 303, most common vehicle for EFB
- Economic development corporations (Type A and Type B, Chapter 504/505)
- Nonprofit corporations created by housing authorities or cities

### Property Tax Exemption: Texas

**How it works:** Properties owned by a housing authority, PFC, or other exempt
governmental entity are exempt from local property taxation under Sections 11.11 and
11.18 of the Texas Tax Code (governmental ownership exemption). The entity must be
the fee-simple owner or hold the property through an eligible structure.

**Key differences from Florida:**
- No assessment increase cap on commercial property (Florida has Save Our Homes for
  residential; Texas has no equivalent for multifamily commercial property)
- Assessment ratio varies by county appraisal district (CAD): typically 60–80% of market
  value, check the specific CAD for the subject property
- Exemption effective upon transfer to exempt entity; may require a full tax year to take
  effect. **Model Year 1 at full tax expense, Years 2+ at $0** unless counsel confirms
  mid-year exemption availability.
- No voluntary PILOT tradition in Texas (unlike some Florida housing authorities)

**Non-Ad Valorem, CRITICAL CHECK:**
Texas master-planned communities commonly have MUDs (Municipal Utility Districts), PIDs
(Public Improvement Districts), and special assessments. These are NOT covered by the
governmental ownership property tax exemption. Always check:
1. Is the property in a MUD? (Check county records or closing documents)
2. Is there a PID assessment? (These fund infrastructure and are NOT tax-exempt)
3. Are there other special assessments (water district, drainage, etc.)?

If MUD/PID assessments exist, model them separately from ad valorem taxes, they
continue regardless of ownership structure.

### HAP/FMR Lookup: SAFMR Requirement

**CRITICAL:** Texas HUD metros designated for Small Area Fair Market Rents (SAFMR)
require a ZIP-code-level FMR lookup, NOT the county-level FMR.

**How to fetch (Mission Driven AI HUD & LIHTC MCP connector):**
1. Call `get_safmr(zip_code="76201", year=2026, bedroom="2BR")` for the subject ZIP.
2. If the metro is not SAFMR-designated, the connector returns the standard county/metro
   FMR via `get_fmr(state="TX", county="Denton", year=2026, bedroom="2BR")`.
3. SAFMR designation status is included in the MCP response payload; no separate
   huduser.gov check required.

Fallback if the MCP is unavailable: huduser.gov/portal/datasets/fmr/smallarea/index.html
for SAFMR designation, then the matching FMR table — last-resort only.

**Why this matters:** SAFMR can differ significantly from county-level FMR. In the
Dallas-Fort Worth metro, SAFMR for a suburban Denton ZIP code ($1,720 for 1BR) may be
meaningfully different from the county FMR or the metro-wide FMR. Using the wrong FMR
will missize the HAP revenue tier.

### Texas-Specific Expense Considerations
- **Insurance:** Texas coastal (Houston, Corpus Christi) carries hurricane/windstorm
  surcharges. North Texas (DFW, Denton) has hail exposure, budget 10–15% above
  national benchmarks.
- **Property tax (pre-exemption):** Texas has among the highest effective property tax
  rates nationally (1.5–2.5% of assessed value). The exemption savings are therefore
  proportionally larger, always quantify.
- **Utilities:** ERCOT grid deregulation means electricity costs can be volatile. Use
  T-12 actuals and add 5% buffer rather than 3%.

## See Also

- [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md), full state-by-state property tax framework including GA bond-lease PILOT exception
- [references/08-efb-financing.md](.skills/dream-underwrite/references/08-efb-financing.md), bond sizing mechanics
- [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md), three-tier and four-tier rent allocation
