# Shieldstone Technical Underwriting Manual - Index & Integration Guide

**Purpose:** This document provides a navigable index of the Shieldstone Technical Underwriting Manual and maps its contents to DreamVision DREAM app features.

**Manual Location:** `docs/shieldstone_technical_UW_manual_v1.md`

---

## Quick Navigation

### By DREAM App Feature

| DREAM Feature | Relevant Manual Sections | Key Use Cases |
|--------------|------------------------|---------------|
| **BOE Analysis (Phase 1)** | Sections 1.1, 1.2, 3.1-3.5, 4.1-4.6 | Deal screening, return hurdles, revenue/expense underwriting |
| **Investment Criteria Engine** | Section 1.1, 1.2 | Return hurdles, deal disqualifiers, risk adjustments |
| **Market Research** | Section 1.3, 1.4 | Market tier classification, competitive supply analysis |
| **Scoring Framework** | Section 1.1, 8.1-8.5 | Risk-adjusted return calculations, execution risk scoring |
| **DCF Modeling (Phase 2)** | Sections 5-7 | Capex planning, financing structure, IRR calculations |
| **Risk Assessment** | Section 8 | Comprehensive risk aggregation and mitigation |
| **Due Diligence** | Section 9 | DD timeline, third-party report analysis |
| **Report Generation** | Section 11 | IC memo format, variance analysis |

---

## Manual Structure Overview

### PART I: Foundation (Sections 1-4)

**Section 1: Foundational Frameworks** (Pages 1-24)
- **1.1 Investment Philosophy & Return Hurdles** ⭐ **CRITICAL**
  - Market tier classification (Gateway/Secondary/Tertiary)
  - Risk-adjusted IRR hurdle calculator
  - Absolute minimums (12% IRR, 6% CoC)
  - **DREAM Integration:** Use for investment criteria defaults and scoring
  
- **1.2 Deal Screening Criteria** ⭐ **CRITICAL**
  - Hard disqualifiers (min units, max age, min occupancy)
  - Location checks (crime, declining markets)
  - Structural/environmental checks
  - **DREAM Integration:** Implement as hard-stop criteria in Phase 1

- **1.3 Market Selection Framework**
  - Market tier scoring
  - Demographic/employment analysis
  - **DREAM Integration:** Enhance market research scoring

- **1.4 Competitive Supply Analysis**
  - Pipeline analysis methodology
  - Absorption rate calculations
  - **DREAM Integration:** Add to market research output

- **1.5 Data Source Catalog**
  - Reference data sources
  - **DREAM Integration:** Guide market research API selection

**Section 2: Data Collection & Validation** (Pages 25-42)
- Document quality scoring
- Reconciliation checks
- **DREAM Integration:** Use for document processing quality metrics

**Section 3: Revenue Underwriting** (Pages 43-68)
- In-place rent analysis
- Market rent determination
- Renovation rent premium (5-20% by scope)
- Rent growth projections
- Other income analysis
- **DREAM Integration:** Core BOE revenue assumptions

**Section 4: Operating Expenses** (Pages 69-90)
- Expense benchmarking standards
- **Property Tax: 70% FL reassessment** ⚠️ **CRITICAL STANDARD**
- Insurance, payroll, maintenance
- Replacement reserves
- **DREAM Integration:** BOE expense assumptions with FL-specific tax logic

---

### PART II: Analysis & Risk (Sections 5-9)

**Section 5: Capital Expenditure Planning** (Pages 91-112)
- Renovation scope development (Light/Moderate/Heavy/Luxury)
- **ROI threshold: 8% cash-on-cash** ⚠️ **CRITICAL STANDARD**
- Budget validation
- **DREAM Integration:** Phase 2 DCF modeling, capex ROI validation

**Section 6: Financing Structure** (Pages 113-132)
- **65% LTV standard** ⚠️ **CRITICAL STANDARD**
- **30-month IO period** ⚠️ **CRITICAL STANDARD**
- **Rate: 5yr Treasury + 150bps** ⚠️ **CRITICAL STANDARD**
- Loan sizing (LTV vs DSCR constraints)
- **DREAM Integration:** Default financing assumptions, loan calculator

**Section 7: Returns Analysis** (Pages 133-160)
- Going-in cap rate
- Exit cap rate determination
- Cash-on-cash calculation
- IRR calculation (levered/unlevered)
- Equity multiple targets
- Sensitivity analysis
- **DREAM Integration:** Core Phase 2 DCF calculations

**Section 8: Risk Assessment** (Pages 161-186)
- Market risk evaluation
- Execution risk scoring (35% weight)
- Financial risk identification
- Risk aggregation framework
- **DREAM Integration:** Scoring framework risk component

**Section 9: Due Diligence Protocols** (Pages 187-210)
- **45-day timeline: Phase I (Days 1-10), Phase II (Days 11-45)** ⚠️ **CRITICAL STANDARD**
- Third-party report analysis (PCA, Phase I ESA)
- Contingency release decision framework
- **DREAM Integration:** DD workflow, milestone tracking

---

### PART III: Exit & Workflow (Sections 10-13)

**Section 10: Exit Strategy** (Pages 211-234)
- Exit timing optimization (48-month target, 12-month LTCG minimum)
- Pre-sale preparation checklist
- **DREAM Integration:** Exit strategy recommendations

**Section 11: Reporting & Monitoring** (Pages 235-252)
- IC memo format (12-15 pages)
- Monthly KPIs
- Variance analysis
- **DREAM Integration:** Report generation templates

**Section 12: Case Studies** (Pages 253-272)
- Success/failure analysis
- Lessons learned
- **DREAM Integration:** Reference for edge cases

**Section 13: Complete Workflow** (Pages 273-290)
- Integrated analysis process
- Python implementation library
- Final recommendation framework
- **DREAM Integration:** End-to-end workflow orchestration

---

## Critical Standards Summary

These standards should be implemented as defaults in DreamVision:

### Financing Standards
- **LTV:** 65% on purchase price only (NOT total project cost)
- **Amortization:** 30-month IO, then 30-year amortization
- **Rate:** Current 5yr Treasury + 150bps
- **Equity:** 35% down + closing costs + 100% capex

### Property Tax (Florida)
- **Reassessment Ratio:** 70% (NOT 100%)
- **Always confirm with county assessor**
- **Annual Growth:** 3% conservative assumption

### Return Requirements
- **Absolute Minimum:** 12% IRR, 6% stabilized CoC, 1.4x equity multiple
- **Secondary Markets:** 16-19% IRR base
- **Risk Adjustments:** +200bps for heavy construction

### Renovation Standards
- **ROI Threshold:** Must exceed 8% cash-on-cash return
- **Scopes:** Light ($5K), Moderate ($12K), Heavy ($20K), Luxury ($30K)
- **Age Adjustments:** +10% if >20 years, +20% if >30 years

### Due Diligence
- **Timeline:** 45 days total
- **Phase I:** Days 1-10 (soft DD, go/no-go decision)
- **Phase II:** Days 11-45 (hard DD, earnest money at risk)

### Exit Strategy
- **Optimal Hold:** 48 months (renovation + 18 months stabilized)
- **Minimum Hold:** 12 months (for long-term capital gains)

### Underwriting Philosophy
- Conservative bias on all assumptions
- Market comps trump broker projections
- Stress test every base case
- Apply 15-20% haircut when uncertain

---

## Python Implementation Reference

The manual includes production-ready Python classes for:

1. **`ReturnHurdleCalculator`** (Section 1.1)
   - Market tier classification
   - Risk-adjusted hurdle calculation
   - Use in: Investment criteria engine, scoring framework

2. **`DealScreener`** (Section 1.2)
   - Hard disqualifier checks
   - Use in: Deal intake, initial screening

3. **`RenovationBudgetBuilder`** (Section 5.1)
   - Capex budget calculation
   - ROI validation
   - Use in: Phase 2 DCF modeling

4. **`LoanSizer`** (Section 6.3)
   - LTV/DSCR loan sizing
   - Equity requirement calculation
   - Use in: Financing assumptions, sources & uses

5. **`IRRCalculator`** (Section 7.4)
   - Levered/unlevered IRR
   - Equity multiple calculation
   - Use in: Returns analysis, DCF modeling

6. **`ExecutionRiskAnalyzer`** (Section 8.2)
   - Renovation risk scoring
   - Use in: Risk assessment component

7. **`DueDiligenceTimeline`** (Section 9.1)
   - 45-day milestone schedule
   - Critical path tracking
   - Use in: Pipeline CRM, DD workflow

8. **`ThirdPartyReportAnalyzer`** (Section 9.3)
   - PCA variance analysis
   - Phase I ESA evaluation
   - Use in: DD report analysis

9. **`ContingencyDecisionFramework`** (Section 9.5)
   - Variance analysis
   - Go/no-go decision logic
   - Use in: DD decision support

10. **`CompleteUnderwritingWorkflow`** (Section 13.1)
    - End-to-end orchestration
    - Use in: Full analysis pipeline

---

## Integration Roadmap

### Phase 1 (BOE Analysis) - Immediate Use
- ✅ Implement `DealScreener` for hard-stop criteria
- ✅ Use `ReturnHurdleCalculator` for investment criteria defaults
- ✅ Apply revenue/expense standards from Sections 3-4
- ✅ Reference Section 11.1 for BOE memo format

### Phase 2 (DCF Modeling) - High Priority
- ✅ Implement `RenovationBudgetBuilder` for capex planning
- ✅ Implement `LoanSizer` for financing structure
- ✅ Implement `IRRCalculator` for returns analysis
- ✅ Use Section 7 for complete returns framework

### Phase 3 (Advanced Features) - Future
- ✅ Implement `DueDiligenceTimeline` for DD workflow
- ✅ Use `ThirdPartyReportAnalyzer` for report integration
- ✅ Implement `ExecutionRiskAnalyzer` for risk scoring
- ✅ Use Section 10 for exit strategy recommendations

---

## Key Formulas Reference

See `docs/SHIELDSTONE_STANDARDS_REFERENCE.md` for quick formula lookup.

---

## Notes for Developers

1. **Florida-Specific Logic:** The manual emphasizes Florida property tax reassessment at 70% (not 100%). This should be configurable by state.

2. **Conservative Bias:** All calculations should default to conservative assumptions. When uncertain, apply 15-20% haircut.

3. **Market Tier Classification:** The manual uses Gateway/Secondary/Tertiary classification. Map this to DREAM's market research output.

4. **Python Code Quality:** The manual includes production-ready Python classes. These can be adapted but should maintain the same calculation logic.

5. **Extensibility:** Design the investment criteria engine to allow users to override Shieldstone defaults while maintaining the framework.

---

**Last Updated:** 2025-01-XX  
**Manual Version:** v1 (290 pages, 13 sections)  
**Status:** Ready for integration into DreamVision Phase 1 & 2

