# 08: EFB Financing: Bond Sizing, Turbo Amortization & Capital Stack

## Bond Structure

| Parameter | Typical |
|---|---|
| Bond type | Tax-exempt essential function bonds |
| Rating | Often unrated (high-yield muni); some rated via issuer credit (e.g., JHA A+) |
| Rate range | **5.0-5.5% default assumption** for underwriting. Verify current market. Can be lower with strong issuer credit (Westwood achieved 4.65% with JHA A+ rating). |
| Structure | Turbo amortization (principal from available cash only, no default on missed principal) |
| Maturity | 10-30 years |
| Target | 100% of total project cost (no equity contribution) |
| DSCR floor | 1.15x Year 1 |
| Growth assumption | 3% annual rent AND expense growth (accepted by muni bond fund buyers in high-growth markets) |

### Rate Benchmarks (Indicative, Verify Current)

| Rating | 30-Yr Tax-Exempt | 30-Yr Taxable Equivalent |
|---|---|---|
| AAA | 3.7% | 5.4% |
| AA | 4.1% | 5.4% |
| A | 4.5% | 5.5% |
| BBB | 5.5% | 6.5% |
| Unrated (typical EFB) | 6.5% | 7.75% |

Source: Bloomberg, December 2023. Always verify current rates before sizing.

When an issuer pledges its own credit (like JHA's A+ rating), bond pricing improves materially. The Westwood deal achieved 4.65% with JHA's backing.

## Bond Sizing: Step by Step

### The Core Question
Can tax-exempt bond proceeds cover **100% of total project cost** while maintaining 1.15x DSCR?

### Step 1: Calculate Stabilized NOI
```
GPR (per [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md))
- Vacancy (7-10% Year 1, 5-7% stabilized)
+ Other Income ($50-100/unit/mo, three-tier classified)
+ RUBS (75% recovery of gross utilities)
= EGI
- Total OpEx (property taxes = $0 for EFB; all else per [references/05-expenses.md](.skills/dream-underwrite/references/05-expenses.md))
= NOI
```

### Step 2: Calculate Total Project Cost
```
Purchase Price                    $XX,XXX,XXX
+ Immediate Capital Budget        $X,XXX,XXX
+ Capital Reserve                 $XXX,XXX
+ Insurance Escrow                $XXX,XXX
+ Transaction/Soft Costs          $X,XXX,XXX
  (Bond counsel, trustee, COI, legal, DD, closing costs)
+ Developer/Acquisition Fees      $X,XXX,XXX
= TOTAL PROJECT COST (= Required Bond Proceeds)
```

### Step 3: Check DSCR
```
Annual Interest = Bond Proceeds × Bond Rate
Year 1 DSCR = Stabilized NOI / Annual Interest

DSCR >= 1.15x → Deal sizes. Proceed.
DSCR < 1.15x → Price must come down, OR size an interest reserve. See Step 4.
```

### Step 4: Interest Reserve Sizing (When Year 1 DSCR < 1.15x)

Year 1 DSCR shortfalls are common when:
- The deal is a lease-up acquisition (Year 1 vacancy elevated)
- The state requires Year 1 at full tax expense before exemption kicks in (Texas)
- The bond rate is at the high end of the 5.0–5.5% band

Procedure:
1. Calculate shortfall: Annual Debt Service - Year 1 NOI = Shortfall
2. Apply buffer: Interest Reserve = Shortfall × 1.25 to 1.35 (25-35% cushion)
3. Round up to nearest $50K or $100K
4. Write to B25 (Enhancements and Reserves) in the EFB Mini Model
5. Verify total bond proceeds still cover Total Project Cost including reserve
6. Note in chat: "Interest Reserve of $X sized to cover Year 1 shortfall of $Y (DSCR X.XXx) plus XX% buffer"

Flag this EARLY, as soon as Year 1 NOI and debt service are known.

### Step 5: Max Supportable Purchase Price
```
Max Annual DS = NOI / 1.15
Max Bond Amount = Max Annual DS / Bond Rate
Max PP = Max Bond Amount - (Capex + Reserves + Transaction Costs + Dev Fee)
```

### Step 6: DSCR Trajectory
With 3% rent growth and 3% expense growth (and fixed debt service on I/O equivalent from turbo structure), DSCR improves each year because NOI grows while interest is fixed on the outstanding balance.

```
Year 1 DSCR:  1.15x (floor)
Year 5 DSCR:  ~1.25-1.35x (growing)
Year 10 DSCR: ~1.40-1.50x (strong)
Year 20 DSCR: ~1.90-2.00x (very strong)
```

The Westwood deal showed 1.15x Year 1 → 1.44x Year 10 → 1.99x Year 20.

## Turbo Amortization

### How It Works
Unlike conventional amortization (fixed P&I payments), turbo amortization requires:
1. Pay operating expenses first
2. Pay interest on bonds
3. Fill all reserve funds
4. THEN, only if cash remains, pay principal

If there's no cash for principal in any period, it's simply deferred, **no default triggers.**

### Why It Matters
- Substantially reduces default risk (no missed payment = no default)
- Allows more aggressive leverage (100% financing feasible)
- Muni bond fund investors accept the structure because downside is protected
- Combined with 3% growth assumption, raises achievable bond proceeds by 35-60%

### Underwriting Implication
For the EFB Mini Model, underwrite debt service as interest-only for cash flow projection purposes. The turbo principal payments are variable and cash-flow dependent, they don't appear as scheduled payments in the pro forma.

## Westwood Jacksonville: Reference Transaction

| Item | Amount | Per Unit |
|---|---|---|
| Purchase price | $35,850,000 | $140,039 |
| Immediate capital budget | $3,400,000 | $13,281 |
| Capital reserve | $750,000 | $2,930 |
| Transaction/soft costs (incl. fees) | $9,300,000 | $36,328 |
| Insurance escrow | $108,667 | $424 |
| **Total bond proceeds** | **$45,150,000** | **$176,367** |

| Metric | Value |
|---|---|
| Bond rate | 4.65% (JHA A+ credit backing) |
| Annual debt service | $2,099,475 |
| Year 1 NOI (post tax exemption) | ~$2,484,336 |
| Year 1 DSCR | ~1.15x |
| Year 10 DSCR | ~1.44x |
| Property tax eliminated (Year 1) | ~$396,600 |
| Bond proceeds as % of PP | 126% |

### Westwood Fee Structure
| Component | Amount |
|---|---|
| Acquisition fee | $1,648,000 (~4.6% of PP) |
| Finder's fee | $2,000,000 |
| Loan origination fee | $536,156 (1.25%) |
| Financial advisory fee (JHA) | $225,750 |
| Bond costs of issuance | $231,000 |

## Capital Stack Design

### Standard EFB Stack (No Equity)
```
SOURCES:
  Senior tax-exempt EFBs          100% of TPC
  (Optional: subordinate soft loans for deeper affordability)

USES:
  Purchase Price
  Capital Budget
  Reserves (capital, insurance, operating)
  Transaction Costs
  Developer/Admin Fees
  Bond Issuance Costs
```

No private equity. All residual value accrues to governmental owner during bond term. Shieldstone captures value post-ROFR.

## Bond Rate Sensitivity

Always show how bond rate changes affect sizing:

```
For a deal with $3.0M stabilized NOI:

Rate    Max Bonds (1.15x DSCR)    Available for PP (after $5M costs/fees)
4.50%   $57,971K                  $52,971K
4.75%   $54,917K                  $49,917K
5.00%   $52,174K                  $47,174K  ← low end of default range
5.25%   $49,689K                  $44,689K
5.50%   $47,431K                  $42,431K  ← high end of default range
5.75%   $45,369K                  $40,369K
6.00%   $43,478K                  $38,478K
```

A 25 bps move changes max PP by ~$2-3M. This is why verifying current bond rates is critical before quoting a supportable price to a seller.

## Florida-Specific Considerations

### Property Tax Advantage
Florida's apartment tax classification ratios are among the nation's highest:
- Jacksonville: 3.44x (3rd highest nationally)
- Assessment resets upon sale (Save Our Homes doesn't protect commercial)
- Effective rates ~1.5% for commercial/apartment

This means property tax elimination through EFB/public ownership creates outsized cash flow savings compared to other states.

### Insurance Risk
Florida faces hurricane, flood, and climate-related insurance cost escalation. Budget conservatively for insurance, 15-25% above current T-12 levels, with 5-10% annual growth assumed.

### Target Asset Profile
Per national EFB practice and Florida economics:
- Built after 2000, Class A or B, stabilized
- 150-200+ units (fixed bond issuance costs need scale)
- Suburban/infill near employment centers
- Existing rents at or slightly above 80-120% AMI levels
- Manageable capital needs for 10-year hold

## See Also

- [references/02-efb-structure.md](.skills/dream-underwrite/references/02-efb-structure.md), EFB legal frameworks, transaction parties, standing assumptions
- [references/03-efb-revenue.md](.skills/dream-underwrite/references/03-efb-revenue.md), revenue build for bond sizing input
- [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md), tax exemption flow (drives NOI for sizing)
- [references/09-acq-financing.md](.skills/dream-underwrite/references/09-acq-financing.md), ACQ debt sizing (bridge-to-agency, HUD 223(f))
- [templates/field-mapping-efb.md](.skills/dream-underwrite/templates/field-mapping-efb.md), EFB Mini Model cell map for B25 (interest reserve) and B46–B62 (debt cells)
