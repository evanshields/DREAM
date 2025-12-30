# DREAM AI - Phase 5 Product Requirements Document

**Product Name:** DREAM AI  
**Company:** Shieldstone Acquisitions / DREAM.AI  
**Document Type:** Phase 5 PRD (Excel Export & Assumption Mapping)  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 1. Overview

This PRD covers Phase 5 of DREAM AI's acquisitions intelligence workflow:

- **Excel Export:** Export complete pro formas with working formulas
- **House Model Integration:** Push assumptions to DREAM AI's institutional template
- **Custom Model Mapping:** Map assumptions to user's proprietary Excel models
- **Assumption Standardization:** Consistent assumption format across all outputs

Phase 5 bridges the gap between DREAM AI's in-app analysis and the Excel-based workflows that many institutional investors still require. While the in-app pro forma engine (Phase 4) is designed to be a complete Excel replacement, some users need Excel outputs for:
- Investor reporting requirements
- Lender underwriting packages
- Internal approval workflows
- Integration with existing tools

**Key Principle:** The in-app pro forma is the source of truth. Excel export is a convenience feature, not a requirement for deal analysis.

---

## 2. Goals & Success Metrics

### Goals

1. Enable seamless export of analysis to Excel with working formulas
2. Provide institutional-quality Excel templates
3. Support custom model mapping for enterprise users
4. Maintain assumption consistency between app and Excel
5. Reduce time spent manually transferring data to Excel

### Success Metrics

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| Excel export generation time | <10 seconds | <5 seconds | Task completion |
| Formula accuracy | 100% | 100% | Automated testing |
| User satisfaction with Excel output | >4.0/5 | >4.5/5 | Feedback |
| Custom mapping setup time | <30 minutes | <15 minutes | Onboarding tracking |
| Data transfer errors | 0% | 0% | Error tracking |

---

## 3. Export Tiers

### 3.1 Tier Overview

| Tier | Name | Included In | Description |
|------|------|-------------|-------------|
| **Tier 1** | Basic Excel Export | All Plans | Export pro forma with working formulas |
| **Tier 2** | House Model | Pro Plan | Push to DREAM AI's institutional template |
| **Tier 3** | Custom Mapping | Enterprise | Map to user's proprietary Excel model |

### 3.2 Tier 1: Basic Excel Export (Included)

**What's Included:**
- Complete pro forma with all assumptions
- Working Excel formulas (not just values)
- Professional formatting
- Multiple sheets (Summary, Pro Forma, Sensitivity, etc.)
- Named ranges for key inputs
- Print-ready layout

**Output Sheets:**
1. **Summary** - Key metrics, deal snapshot
2. **Assumptions** - All input assumptions in one place
3. **Pro Forma** - Annual cash flows (10-year)
4. **Monthly** - Monthly cash flows (optional)
5. **Unit Mix** - Unit-level rent analysis
6. **Debt** - Loan amortization schedule
7. **Waterfall** - GP/LP distribution calculations
8. **Sensitivity** - Sensitivity tables (IRR, EM)
9. **Sources & Uses** - Capital stack breakdown

### 3.3 Tier 2: House Model (Premium)

**What's Included:**
- Everything in Tier 1
- Institutional-quality template matching major investor formats
- Additional analysis sheets
- Presentation-ready charts
- Comparison to benchmarks
- Audit trail

**Additional Sheets:**
10. **Benchmarks** - Comparison to market averages
11. **Returns Analysis** - Detailed IRR/EM breakdown
12. **Risk Analysis** - Scenario comparison
13. **Charts** - Visual representations
14. **Cover Page** - Branded summary page

### 3.4 Tier 3: Custom Model Mapping (Enterprise)

**What's Included:**
- Everything in Tier 2
- One-time mapping to user's proprietary Excel template
- Automatic population of user's model
- Preserves all custom formulas and logic
- Support for complex model structures

**Setup Process:**
1. User uploads their Excel template
2. DREAM AI analyzes template structure
3. User maps DREAM AI fields to template cells
4. Mapping saved for future use
5. One-click population of their model

---

## 4. Assumption Field Mapping

### 4.1 Standard Assumption Categories

All assumptions are organized into standard categories for consistent mapping:

```typescript
interface ExportableAssumptions {
  // Property Information
  property: {
    assetName: string;
    address: string;
    city: string;
    state: string;
    zipCode: string;
    yearBuilt: number;
    units: number;
    buildings: number;
    netRentableSF: number;
    avgUnitSize: number;
    propertyClass: string;
    propertyType: string;
  };
  
  // Acquisition
  acquisition: {
    purchasePrice: number;
    pricePerUnit: number;
    pricePerSF: number;
    closingCosts: number;
    closingCostsPct: number;
    acquisitionFee: number;
    acquisitionFeePct: number;
    goingInCapRate: number;
  };
  
  // Unit Mix
  unitMix: UnitType[];
  
  // Revenue Assumptions
  revenue: {
    inPlaceRent: number;
    marketRent: number;
    lossToLease: number;
    lossToLeasePct: number;
    year1RentGrowth: number;
    stabilizedRentGrowth: number;
    targetOccupancy: number;
    currentOccupancy: number;
    concessions: number;
    concessionsPct: number;
    badDebt: number;
    badDebtPct: number;
    otherIncomePerUnit: number;
  };
  
  // Expense Assumptions
  expenses: {
    totalOpEx: number;
    opExPerUnit: number;
    expenseRatio: number;
    propertyTaxes: number;
    propertyTaxGrowth: number;
    insurance: number;
    insuranceGrowth: number;
    utilities: number;
    utilitiesGrowth: number;
    repairsMaintenance: number;
    rmGrowth: number;
    payroll: number;
    payrollGrowth: number;
    managementFee: number;
    managementFeePct: number;
    administrative: number;
    marketing: number;
    contractServices: number;
    replacementReserves: number;
    reservesPerUnit: number;
    generalExpenseGrowth: number;
  };
  
  // Capital Expenditure
  capex: {
    totalRenovationBudget: number;
    interiorPerUnit: number;
    exteriorPerUnit: number;
    amenitiesPerUnit: number;
    contingency: number;
    contingencyPct: number;
    renovationTimeline: number;  // months
    unitsPerMonth: number;
  };
  
  // Financing - Senior Debt
  seniorDebt: {
    loanAmount: number;
    ltv: number;
    interestRate: number;
    amortization: number;
    term: number;
    interestOnlyPeriod: number;
    originationFee: number;
    originationFeePct: number;
    rateType: string;  // FIXED, FLOATING
  };
  
  // Financing - Mezzanine (if applicable)
  mezzDebt?: {
    loanAmount: number;
    interestRate: number;
    term: number;
  };
  
  // Exit Assumptions
  exit: {
    holdPeriodMonths: number;
    holdPeriodYears: number;
    exitCapRate: number;
    exitCapSpread: number;  // vs entry
    sellingCosts: number;
    sellingCostsPct: number;
    dispositionFee: number;
    dispositionFeePct: number;
  };
  
  // Partnership Structure
  partnership: {
    gpCoinvest: number;
    gpCoinvestPct: number;
    lpEquity: number;
    totalEquity: number;
    preferredReturn: number;
    waterfallStructure: WaterfallTier[];
    assetManagementFee: number;
    assetManagementFeePct: number;
  };
  
  // Calculated Outputs (for reference)
  outputs: {
    leveredIRR: number;
    unleveredIRR: number;
    equityMultiple: number;
    avgCashOnCash: number;
    peakEquity: number;
    exitValue: number;
    exitNOI: number;
    stabilizedNOI: number;
    stabilizedDSCR: number;
    lpIRR: number;
    gpIRR: number;
    gpPromote: number;
  };
}

interface UnitType {
  unitType: string;      // "1BR", "2BR", etc.
  unitCount: number;
  avgSF: number;
  inPlaceRent: number;
  marketRent: number;
  renovatedRent: number;
  rentPremium: number;
}

interface WaterfallTier {
  tierName: string;
  hurdleType: string;    // "PREF", "ROC", "IRR", "PROFIT"
  hurdleRate: number;
  lpSplit: number;
  gpSplit: number;
}
```

### 4.2 Field Mapping Table

Complete mapping of DREAM AI fields to Excel cells:

| Category | DREAM AI Field | Excel Cell (House Model) | Format |
|----------|----------------|-------------------------|--------|
| **Property** | | | |
| | assetName | Summary!B3 | Text |
| | address | Summary!B4 | Text |
| | city | Summary!B5 | Text |
| | state | Summary!B6 | Text |
| | yearBuilt | Summary!B8 | Number |
| | units | Summary!B9 | Number |
| | netRentableSF | Summary!B10 | Number |
| **Acquisition** | | | |
| | purchasePrice | Assumptions!C5 | Currency |
| | pricePerUnit | Assumptions!C6 | Currency |
| | closingCostsPct | Assumptions!C8 | Percentage |
| | acquisitionFeePct | Assumptions!C9 | Percentage |
| | goingInCapRate | Assumptions!C10 | Percentage |
| **Revenue** | | | |
| | year1RentGrowth | Assumptions!C15 | Percentage |
| | stabilizedRentGrowth | Assumptions!C16 | Percentage |
| | targetOccupancy | Assumptions!C17 | Percentage |
| | lossToLeasePct | Assumptions!C18 | Percentage |
| | concessionsPct | Assumptions!C19 | Percentage |
| | badDebtPct | Assumptions!C20 | Percentage |
| | otherIncomePerUnit | Assumptions!C21 | Currency |
| **Expenses** | | | |
| | propertyTaxes | Assumptions!C25 | Currency |
| | propertyTaxGrowth | Assumptions!C26 | Percentage |
| | insurance | Assumptions!C27 | Currency |
| | insuranceGrowth | Assumptions!C28 | Percentage |
| | managementFeePct | Assumptions!C33 | Percentage |
| | reservesPerUnit | Assumptions!C38 | Currency |
| | generalExpenseGrowth | Assumptions!C39 | Percentage |
| **CapEx** | | | |
| | totalRenovationBudget | Assumptions!C43 | Currency |
| | interiorPerUnit | Assumptions!C44 | Currency |
| | contingencyPct | Assumptions!C47 | Percentage |
| | renovationTimeline | Assumptions!C48 | Number |
| **Financing** | | | |
| | ltv | Assumptions!C52 | Percentage |
| | interestRate | Assumptions!C53 | Percentage |
| | amortization | Assumptions!C54 | Number |
| | term | Assumptions!C55 | Number |
| | interestOnlyPeriod | Assumptions!C56 | Number |
| | originationFeePct | Assumptions!C57 | Percentage |
| **Exit** | | | |
| | holdPeriodYears | Assumptions!C61 | Number |
| | exitCapRate | Assumptions!C62 | Percentage |
| | sellingCostsPct | Assumptions!C63 | Percentage |
| **Partnership** | | | |
| | gpCoinvestPct | Assumptions!C67 | Percentage |
| | preferredReturn | Assumptions!C68 | Percentage |
| | assetManagementFeePct | Assumptions!C69 | Percentage |

---

## 5. Excel Template Structure

### 5.1 Summary Sheet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DREAM AI | INVESTMENT SUMMARY                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PROPERTY INFORMATION                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Asset Name:           Oak Creek Apartments                                  │
│  Address:              1234 Oak Creek Dr, Austin, TX 78701                   │
│  Year Built:           1985                                                  │
│  Units:                96                                                    │
│  Net Rentable SF:      82,560                                               │
│  Property Class:       B                                                     │
│                                                                              │
│  TRANSACTION SUMMARY                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Purchase Price:       $12,500,000                                          │
│  Price Per Unit:       $130,208                                             │
│  Going-In Cap:         7.00%                                                │
│                                                                              │
│  SOURCES & USES                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  SOURCES                           USES                                      │
│  Senior Debt      $8,125,000       Purchase Price    $12,500,000            │
│  LP Equity        $4,631,250       Closing Costs        $312,500            │
│  GP Co-Invest       $243,750       Acquisition Fee      $125,000            │
│                                    Renovation           $768,000            │
│                                    Contingency           $76,800            │
│                                    Working Capital      $218,450            │
│  ───────────────────────────────────────────────────────────────────────    │
│  TOTAL           $13,000,000       TOTAL            $13,000,000             │
│                                                                              │
│  KEY RETURNS                                                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   18.5%     │ │    1.85x    │ │    8.2%     │ │    1.35x    │           │
│  │   IRR       │ │   Equity    │ │  Avg CoC    │ │   DSCR      │           │
│  │  (Levered)  │ │  Multiple   │ │  (Yr 2-5)   │ │ (Stabilized)│           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                                              │
│  Generated by DREAM AI | December 20, 2025                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Assumptions Sheet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ASSUMPTIONS                                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ACQUISITION                        │  VALUE           │  NOTES             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Purchase Price                     │  $12,500,000     │  Asking price      │
│  Price Per Unit                     │  $130,208        │  =B5/Units         │
│  Price Per SF                       │  $151.36         │  =B5/SF            │
│  Closing Costs                      │  2.5%            │  DD, legal, etc.   │
│  Acquisition Fee                    │  1.0%            │  GP fee            │
│  Going-In Cap Rate                  │  7.00%           │  In-place NOI/Price│
│                                                                              │
│  REVENUE                            │  VALUE           │  NOTES             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Year 1 Rent Growth                 │  3.0%            │  Above in-place    │
│  Stabilized Rent Growth             │  2.5%            │  Years 2+          │
│  Target Occupancy                   │  95.0%           │  Stabilized        │
│  Loss to Lease                      │  5.0%            │  Burns off 25%/yr  │
│  Concessions                        │  1.0%            │  Lease-up          │
│  Bad Debt                           │  1.0%            │  Collection loss   │
│  Other Income/Unit/Month            │  $75             │  Fees, parking     │
│                                                                              │
│  EXPENSES                           │  VALUE           │  NOTES             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Property Taxes                     │  $312,500        │  Post-reassessment │
│  Property Tax Growth                │  2.5%            │  Annual            │
│  Insurance                          │  $72,000         │  Current + buffer  │
│  Insurance Growth                   │  5.0%            │  Hardening market  │
│  Utilities                          │  $115,200        │  T-12 actual       │
│  Repairs & Maintenance              │  $86,400         │  T-12 actual       │
│  Payroll                            │  $134,400        │  1.4 FTE           │
│  Management Fee                     │  3.0%            │  % of EGI          │
│  Replacement Reserves               │  $300/unit       │  Per Shieldstone   │
│  General Expense Growth             │  3.0%            │  Annual            │
│                                                                              │
│  (continues with CapEx, Financing, Exit, Partnership...)                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Pro Forma Sheet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  10-YEAR PRO FORMA                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                    Year 1    Year 2    Year 3    Year 4    Year 5   ...     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  REVENUE                                                                     │
│  Gross Potential   $1,152,000 $1,186,560 $1,222,157 $1,258,821 $1,296,586   │
│  Loss to Lease       (57,600)   (35,598)   (18,332)    (9,441)    (4,860)   │
│  Vacancy             (57,600)   (59,328)   (61,108)   (62,941)   (64,829)   │
│  Concessions         (11,520)   (11,866)   (12,222)   (12,588)   (12,966)   │
│  Bad Debt            (11,520)   (11,866)   (12,222)   (12,588)   (12,966)   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Net Rental Inc   $1,013,760 $1,067,903 $1,118,274 $1,161,263 $1,200,965   │
│  Other Income        $86,400    $88,992    $91,662    $94,412    $97,244   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  EGI              $1,100,160 $1,156,895 $1,209,936 $1,255,675 $1,298,209   │
│                                                                              │
│  EXPENSES                                                                    │
│  Property Taxes     $312,500   $320,313   $328,320   $336,528   $344,941   │
│  Insurance           $72,000    $75,600    $79,380    $83,349    $87,516   │
│  Utilities          $115,200   $118,656   $122,216   $125,882   $129,659   │
│  Repairs & Maint     $86,400    $88,992    $91,662    $94,412    $97,244   │
│  Payroll            $134,400   $139,104   $143,973   $149,012   $154,227   │
│  Management          $33,005    $34,707    $36,298    $37,670    $38,946   │
│  Administrative      $19,200    $19,776    $20,369    $20,980    $21,610   │
│  Marketing            $9,600     $9,792     $9,988    $10,188    $10,391   │
│  Contract Services   $28,800    $29,664    $30,554    $31,471    $32,415   │
│  Reserves            $28,800    $29,664    $30,554    $31,471    $32,415   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Total OpEx         $839,905   $866,268   $893,314   $920,963   $949,365   │
│  Expense Ratio        76.3%      74.9%      73.8%      73.3%      73.1%    │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  NOI                $260,255   $290,627   $316,622   $334,712   $348,844   │
│                                                                              │
│  DEBT SERVICE                                                                │
│  Interest           $528,125   $528,125   $528,125   $512,500   $496,875   │
│  Principal               $0        $0        $0    $15,625    $31,250     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Total Debt Svc     $528,125   $528,125   $528,125   $528,125   $528,125   │
│  DSCR                  0.49x      0.55x      0.60x      0.63x      0.66x   │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Cash Flow Before   $(267,870) $(237,498) $(211,503) $(193,413) $(179,281) │
│  CapEx               (768,000)       $0        $0        $0        $0      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Cash Flow After  $(1,035,870) $(237,498) $(211,503) $(193,413) $(179,281) │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Waterfall Sheet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WATERFALL DISTRIBUTION                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PARTNERSHIP STRUCTURE                                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Total Equity Required:     $4,875,000                                       │
│  GP Co-Invest (5%):           $243,750                                       │
│  LP Equity (95%):           $4,631,250                                       │
│                                                                              │
│  WATERFALL TIERS                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Tier 1: 8% Preferred Return to LP                                           │
│  Tier 2: Return of Capital to LP                                             │
│  Tier 3: 70% LP / 30% GP to 12% IRR                                         │
│  Tier 4: 60% LP / 40% GP to 15% IRR                                         │
│  Tier 5: 50% LP / 50% GP thereafter                                         │
│                                                                              │
│  DISTRIBUTION CALCULATION                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Total Distributions:       $9,018,750                                       │
│                                                                              │
│  │ Tier          │ Distribution │   LP Share   │   GP Share   │            │
│  │───────────────┼──────────────┼──────────────┼──────────────│            │
│  │ 8% Pref       │    $370,500  │    $370,500  │         $0   │            │
│  │ Return of Cap │  $4,631,250  │  $4,631,250  │         $0   │            │
│  │ 70/30 Split   │  $2,517,000  │  $1,761,900  │    $755,100  │            │
│  │ 60/40 Split   │  $1,000,000  │    $600,000  │    $400,000  │            │
│  │ 50/50 Split   │    $500,000  │    $250,000  │    $250,000  │            │
│  │───────────────┼──────────────┼──────────────┼──────────────│            │
│  │ TOTAL         │  $9,018,750  │  $7,613,650  │  $1,405,100  │            │
│                                                                              │
│  RETURNS SUMMARY                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                           │      LP      │      GP      │                   │
│  │────────────────────────┼──────────────┼──────────────│                   │
│  │ Total Invested         │  $4,631,250  │    $243,750  │                   │
│  │ Total Distributions    │  $7,613,650  │  $1,405,100  │                   │
│  │ Net Profit             │  $2,982,400  │  $1,161,350  │                   │
│  │ Equity Multiple        │       1.64x  │       5.76x  │                   │
│  │ IRR                    │      15.2%   │      42.5%   │                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Custom Model Mapping

### 6.1 Mapping Configuration UI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Custom Model Mapping                                        [Save] [Test]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Your Template: Acme_Partners_UW_Model_v3.xlsx                [Change File] │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  Map DREAM AI fields to cells in your Excel template:                        │
│                                                                              │
│  PROPERTY INFORMATION                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  DREAM AI Field          │  Your Cell    │  Format    │  Status        ││
│  │──────────────────────────┼───────────────┼────────────┼────────────────││
│  │  Asset Name              │  Cover!B5     │  Text      │  ✓ Mapped      ││
│  │  Address                 │  Cover!B6     │  Text      │  ✓ Mapped      ││
│  │  Units                   │  Inputs!C8    │  Number    │  ✓ Mapped      ││
│  │  Year Built              │  Inputs!C9    │  Number    │  ✓ Mapped      ││
│  │  Net Rentable SF         │  Inputs!C10   │  Number    │  ✓ Mapped      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ACQUISITION                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  DREAM AI Field          │  Your Cell    │  Format    │  Status        ││
│  │──────────────────────────┼───────────────┼────────────┼────────────────││
│  │  Purchase Price          │  Inputs!C15   │  Currency  │  ✓ Mapped      ││
│  │  Closing Costs %         │  Inputs!C18   │  Percent   │  ✓ Mapped      ││
│  │  Acquisition Fee %       │  [Click to map]│           │  ⚠️ Unmapped   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [+ Show All Fields]                                                         │
│                                                                              │
│  Mapping Progress: 45/52 fields mapped (87%)                                │
│  ████████████████████████████████████████░░░░░░                             │
│                                                                              │
│  [Preview Export]  [Download Populated Model]                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Mapping Data Model

```typescript
interface CustomModelMapping {
  id: string;
  organizationId: string;
  createdBy: string;
  
  // Template info
  templateName: string;
  templateFileId: string;  // Reference to stored template
  templateVersion: string;
  
  // Field mappings
  mappings: FieldMapping[];
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  lastUsedAt: Date;
}

interface FieldMapping {
  dreamAiField: string;      // e.g., "acquisition.purchasePrice"
  excelSheet: string;        // e.g., "Inputs"
  excelCell: string;         // e.g., "C15"
  format: CellFormat;
  transform?: TransformRule; // Optional transformation
}

enum CellFormat {
  TEXT = 'TEXT',
  NUMBER = 'NUMBER',
  CURRENCY = 'CURRENCY',
  PERCENTAGE = 'PERCENTAGE',
  DATE = 'DATE'
}

interface TransformRule {
  type: TransformType;
  params?: Record<string, any>;
}

enum TransformType {
  NONE = 'NONE',
  MULTIPLY = 'MULTIPLY',      // e.g., convert decimal to percentage
  DIVIDE = 'DIVIDE',
  ROUND = 'ROUND',
  DATE_FORMAT = 'DATE_FORMAT'
}
```

### 6.3 Mapping Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CUSTOM MODEL MAPPING WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: Upload Template                                                     │
│  ─────────────────────────                                                   │
│  • User uploads their proprietary Excel model                                │
│  • System analyzes structure (sheets, named ranges, input cells)             │
│  • Template stored securely for future use                                   │
│         │                                                                    │
│         ▼                                                                    │
│  STEP 2: Auto-Detection (AI-Assisted)                                        │
│  ─────────────────────────────────────                                       │
│  • AI analyzes cell labels and context                                       │
│  • Suggests mappings for common fields                                       │
│  • User reviews and confirms suggestions                                     │
│         │                                                                    │
│         ▼                                                                    │
│  STEP 3: Manual Mapping                                                      │
│  ───────────────────────                                                     │
│  • User maps remaining fields manually                                       │
│  • Click DREAM AI field → Click Excel cell                                   │
│  • System validates cell format compatibility                                │
│         │                                                                    │
│         ▼                                                                    │
│  STEP 4: Test & Validate                                                     │
│  ───────────────────────                                                     │
│  • Run test export with sample data                                          │
│  • Verify values populated correctly                                         │
│  • Check formula integrity preserved                                         │
│         │                                                                    │
│         ▼                                                                    │
│  STEP 5: Save & Use                                                          │
│  ─────────────────────                                                       │
│  • Save mapping configuration                                                │
│  • One-click export for future deals                                         │
│  • Update mapping if template changes                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. API Specifications

### 7.1 Export Endpoints

#### Export to Excel (Basic)

```
POST /api/v1/deals/{deal_id}/export/excel

Request Body:
{
  "format": "xlsx",
  "include_sheets": ["summary", "assumptions", "proforma", "waterfall", "sensitivity"],
  "include_monthly": false,
  "scenario": "base_case"
}

Response (200 OK):
{
  "export_id": "exp_abc123",
  "download_url": "https://storage.dreamai.com/exports/exp_abc123.xlsx",
  "expires_at": "2025-12-20T11:30:00Z",
  "file_size_bytes": 245678
}
```

#### Export to House Model

```
POST /api/v1/deals/{deal_id}/export/house-model

Request Body:
{
  "template_version": "v2.0",
  "include_charts": true,
  "include_benchmarks": true
}

Response (200 OK):
{
  "export_id": "exp_def456",
  "download_url": "https://storage.dreamai.com/exports/exp_def456.xlsx",
  "expires_at": "2025-12-20T11:30:00Z",
  "file_size_bytes": 456789
}
```

#### Export to Custom Model

```
POST /api/v1/deals/{deal_id}/export/custom-model

Request Body:
{
  "mapping_id": "map_xyz789"
}

Response (200 OK):
{
  "export_id": "exp_ghi012",
  "download_url": "https://storage.dreamai.com/exports/exp_ghi012.xlsx",
  "expires_at": "2025-12-20T11:30:00Z",
  "file_size_bytes": 567890,
  "fields_populated": 45,
  "fields_skipped": 7,
  "warnings": [
    {"field": "mezzDebt.loanAmount", "reason": "No mezzanine debt in this deal"}
  ]
}
```

### 7.2 Mapping Endpoints

#### Upload Template

```
POST /api/v1/custom-models/templates

Content-Type: multipart/form-data

Request:
- file: (binary) Excel file
- name: "Acme Partners UW Model"

Response (201 Created):
{
  "template_id": "tpl_abc123",
  "name": "Acme Partners UW Model",
  "sheets": ["Cover", "Inputs", "ProForma", "Returns", "Waterfall"],
  "detected_input_cells": 156,
  "suggested_mappings": [
    {"dreamAiField": "property.assetName", "excelCell": "Cover!B5", "confidence": 0.95},
    {"dreamAiField": "acquisition.purchasePrice", "excelCell": "Inputs!C15", "confidence": 0.92}
  ]
}
```

#### Create/Update Mapping

```
PUT /api/v1/custom-models/mappings/{mapping_id}

Request Body:
{
  "template_id": "tpl_abc123",
  "mappings": [
    {"dreamAiField": "property.assetName", "excelSheet": "Cover", "excelCell": "B5", "format": "TEXT"},
    {"dreamAiField": "acquisition.purchasePrice", "excelSheet": "Inputs", "excelCell": "C15", "format": "CURRENCY"}
  ]
}

Response (200 OK):
{
  "mapping_id": "map_xyz789",
  "template_id": "tpl_abc123",
  "total_mappings": 45,
  "unmapped_fields": ["mezzDebt.loanAmount", "mezzDebt.interestRate"]
}
```

#### Test Mapping

```
POST /api/v1/custom-models/mappings/{mapping_id}/test

Request Body:
{
  "deal_id": "deal_xyz789"  // Use this deal's data for test
}

Response (200 OK):
{
  "success": true,
  "preview_url": "https://storage.dreamai.com/previews/test_123.xlsx",
  "validation_results": [
    {"field": "acquisition.purchasePrice", "status": "OK", "value": 12500000},
    {"field": "revenue.year1RentGrowth", "status": "WARNING", "message": "Cell formatted as number, not percentage"}
  ]
}
```

---

## 8. Database Schema

```sql
-- Export jobs table
CREATE TABLE export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id),
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Export type
    export_type export_type_enum NOT NULL,  -- BASIC, HOUSE_MODEL, CUSTOM
    mapping_id UUID REFERENCES custom_model_mappings(id),
    
    -- Configuration
    config JSONB NOT NULL,
    
    -- Output
    status job_status_enum NOT NULL DEFAULT 'PENDING',
    file_url VARCHAR(500),
    file_size_bytes INTEGER,
    expires_at TIMESTAMPTZ,
    
    -- Tracking
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Custom model templates
CREATE TABLE custom_model_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    created_by UUID NOT NULL REFERENCES users(id),
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- File storage
    file_url VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,  -- For change detection
    
    -- Analysis results
    sheets TEXT[],
    detected_cells JSONB,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Custom model mappings
CREATE TABLE custom_model_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    template_id UUID NOT NULL REFERENCES custom_model_templates(id),
    created_by UUID NOT NULL REFERENCES users(id),
    
    name VARCHAR(100) NOT NULL,
    
    -- Mapping configuration
    mappings JSONB NOT NULL,
    
    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    use_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_mapping_name UNIQUE (organization_id, name)
);

-- Enums
CREATE TYPE export_type_enum AS ENUM ('BASIC', 'HOUSE_MODEL', 'CUSTOM');

-- Indexes
CREATE INDEX idx_exports_deal ON export_jobs(deal_id);
CREATE INDEX idx_exports_status ON export_jobs(status);
CREATE INDEX idx_templates_org ON custom_model_templates(organization_id);
CREATE INDEX idx_mappings_org ON custom_model_mappings(organization_id);
CREATE INDEX idx_mappings_template ON custom_model_mappings(template_id);
```

---

## 9. Excel Generation Implementation

### 9.1 Technology Stack

| Component | Library | Notes |
|-----------|---------|-------|
| Excel generation | openpyxl | Python library for .xlsx |
| Formula handling | openpyxl formulas | Preserve working formulas |
| Styling | openpyxl styles | Professional formatting |
| Charts | openpyxl charts | Native Excel charts |
| Template handling | Jinja2 + openpyxl | Template-based generation |

### 9.2 Generation Process

```python
class ExcelExporter:
    """
    Generate Excel exports from DREAM AI pro forma data.
    """
    
    def export_basic(self, deal: Deal, proforma: ProForma, config: ExportConfig) -> bytes:
        """
        Generate basic Excel export with working formulas.
        """
        wb = Workbook()
        
        # Create sheets
        self._create_summary_sheet(wb, deal, proforma)
        self._create_assumptions_sheet(wb, proforma.assumptions)
        self._create_proforma_sheet(wb, proforma)
        self._create_waterfall_sheet(wb, proforma.waterfall)
        self._create_sensitivity_sheet(wb, proforma)
        
        # Apply styling
        self._apply_professional_styling(wb)
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
    
    def _create_proforma_sheet(self, wb: Workbook, proforma: ProForma):
        """
        Create pro forma sheet with working formulas.
        """
        ws = wb.create_sheet("Pro Forma")
        
        # Headers
        headers = ["", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Revenue section with formulas
        ws.cell(row=3, column=1, value="REVENUE")
        ws.cell(row=4, column=1, value="Gross Potential Rent")
        
        # Year 1 GPR (direct value)
        ws.cell(row=4, column=2, value=proforma.year1_gpr)
        
        # Year 2+ GPR (formula referencing growth rate)
        for year in range(2, 6):
            col = year + 1
            growth_cell = "Assumptions!$C$16"  # Stabilized rent growth
            prev_cell = ws.cell(row=4, column=col-1).coordinate
            ws.cell(row=4, column=col, value=f"={prev_cell}*(1+{growth_cell})")
        
        # Continue with other line items...
    
    def export_to_custom_model(
        self, 
        deal: Deal, 
        proforma: ProForma, 
        mapping: CustomModelMapping
    ) -> bytes:
        """
        Populate user's custom Excel model with DREAM AI data.
        """
        # Load user's template
        template_bytes = self._fetch_template(mapping.template_id)
        wb = load_workbook(BytesIO(template_bytes))
        
        # Get assumption values
        assumptions = self._flatten_assumptions(proforma.assumptions)
        
        # Apply mappings
        for field_mapping in mapping.mappings:
            field_value = assumptions.get(field_mapping.dream_ai_field)
            
            if field_value is not None:
                ws = wb[field_mapping.excel_sheet]
                cell = ws[field_mapping.excel_cell]
                
                # Apply format transformation
                formatted_value = self._format_value(
                    field_value, 
                    field_mapping.format,
                    field_mapping.transform
                )
                
                cell.value = formatted_value
        
        # Save
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
```

---

## 10. Testing Requirements

### 10.1 Formula Accuracy Tests

| Test | Description | Target |
|------|-------------|--------|
| IRR formula | Excel XIRR matches Python | ±0.01% |
| Sum formulas | All sums calculate correctly | 100% |
| Growth formulas | Year-over-year growth correct | 100% |
| Waterfall formulas | Distribution calculations match | 100% |

### 10.2 Format Tests

| Test | Description | Target |
|------|-------------|--------|
| Currency formatting | Proper $ and commas | 100% |
| Percentage formatting | Proper % display | 100% |
| Date formatting | Consistent date format | 100% |
| Print layout | Proper page breaks | 100% |

### 10.3 Compatibility Tests

| Test | Description | Target |
|------|-------------|--------|
| Excel 2016+ | Opens without errors | 100% |
| Excel Online | Full functionality | 95% |
| Google Sheets | Import works | 90% |
| LibreOffice | Basic functionality | 85% |

---

## 11. Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| Support Google Sheets export? | Future | Different API |
| Allow formula customization? | Future | Complex feature |
| Version control for templates? | Future | Track template changes |
| Collaborative editing? | Future | Real-time sync |

---

## 12. Rollout Plan

### Phase 5a: Basic Export (Week 4)
- Excel generation engine
- Standard template
- Download functionality

### Phase 5b: House Model (Week 4-5)
- Institutional template
- Additional analysis sheets
- Chart generation

### Phase 5c: Custom Mapping (Week 5)
- Template upload
- Mapping UI
- Auto-detection

### Phase 5d: Polish & Testing (Week 5)
- Formula validation
- Compatibility testing
- Performance optimization

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Author: DREAM AI Product Team*









