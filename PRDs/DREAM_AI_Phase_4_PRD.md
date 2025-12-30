# DREAM AI - Phase 4 Product Requirements Document

**Product Name:** DREAM AI  
**Company:** Shieldstone Acquisitions / DREAM.AI  
**Document Type:** Phase 4 PRD (Pro Forma Engine)  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 1. Overview

This PRD covers Phase 4 of DREAM AI's acquisitions intelligence workflow:

- **Pro Forma Engine:** Full DCF modeling with 5-10 year projections
- **Sensitivity Analysis:** Multi-variable scenario modeling
- **Waterfall Calculations:** GP/LP promote structure modeling
- **Excel Replacement:** Complete in-app financial modeling capability

Phase 4 is the analytical core of DREAM AI, implementing the Shieldstone Technical Manual methodology in a user-friendly interface that can fully replace Excel-based underwriting.

**Critical Requirement:** The in-app pro forma engine must be powerful enough that users never need to touch Excel. Excel export and custom model mapping are premium features, not requirements.

---

## 2. Goals & Success Metrics

### Goals

1. Provide institutional-quality DCF modeling without Excel
2. Implement 100% of Shieldstone methodology calculations
3. Enable rapid scenario comparison and sensitivity analysis
4. Support complex waterfall/promote structures
5. Generate investor-ready outputs directly from the app

### Success Metrics

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| Full pro forma generation time | <30 seconds | <15 seconds | Task completion |
| Calculation accuracy vs Excel | 99.99% | 100% | Regression tests |
| User-reported Excel dependency | <20% | <10% | Survey |
| Sensitivity analysis time | <5 seconds | <2 seconds | Task completion |
| Waterfall accuracy | 100% | 100% | Test suite |
| User satisfaction (pro forma) | >4.5/5 | >4.8/5 | Feedback |

---

## 3. Core Calculation Engine

### 3.1 Architecture Overview

All calculations performed in Python (Shieldstone library) - zero LLM cost for math.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRO FORMA ENGINE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────┐    │
│  │  User Inputs    │     │  Market Data    │     │  Shieldstone        │    │
│  │  (Assumptions)  │────▶│  (Benchmarks)   │────▶│  Defaults           │    │
│  └─────────────────┘     └─────────────────┘     └─────────────────────┘    │
│           │                      │                        │                  │
│           └──────────────────────┼────────────────────────┘                  │
│                                  ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      SHIELDSTONE PYTHON LIBRARY                          ││
│  │                                                                          ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     ││
│  │  │  Revenue    │  │  Expenses   │  │  CapEx      │  │  Financing  │     ││
│  │  │  Module     │  │  Module     │  │  Module     │  │  Module     │     ││
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     ││
│  │         │                │                │                │             ││
│  │         └────────────────┼────────────────┼────────────────┘             ││
│  │                          ▼                ▼                              ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │                    RETURNS CALCULATOR                                │││
│  │  │                                                                      │││
│  │  │  • Annual Cash Flows    • IRR (Levered/Unlevered)                   │││
│  │  │  • Exit Proceeds        • Equity Multiple                           │││
│  │  │  • Waterfall/Promote    • Cash-on-Cash by Year                      │││
│  │  │  • Sensitivity Matrix   • Net Investor Returns                      │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                  │                                           │
│                                  ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         OUTPUT LAYER                                     ││
│  │                                                                          ││
│  │  • Interactive Dashboard    • Sensitivity Charts                        ││
│  │  • Pro Forma Tables         • Waterfall Visualization                   ││
│  │  • Comparison Views         • Export (Excel/PDF)                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Calculation Modules (Shieldstone Implementation)

#### Revenue Module

```python
class RevenueCalculator:
    """
    Calculate revenue projections per Shieldstone Manual Section 3.
    """
    
    def calculate_year(
        self,
        year: int,
        base_rent: Decimal,
        units: int,
        occupancy: Decimal,
        rent_growth: Decimal,
        loss_to_lease: Decimal,
        concessions: Decimal,
        bad_debt: Decimal,
        other_income_per_unit: Decimal,
    ) -> RevenueResult:
        """
        Calculate annual revenue for a given year.
        
        Returns:
            RevenueResult with GPR, EGI, and all components
        """
        # Gross Potential Rent
        gpr = base_rent * 12 * units * (1 + rent_growth) ** (year - 1)
        
        # Loss to Lease (decreases as rents mark to market)
        ltl_factor = max(0, loss_to_lease * (1 - 0.25 * year))
        ltl = gpr * ltl_factor
        
        # Vacancy & Credit Loss
        vacancy = gpr * (1 - occupancy)
        concession_loss = gpr * concessions
        bad_debt_loss = gpr * bad_debt
        
        # Net Rental Income
        nri = gpr - ltl - vacancy - concession_loss - bad_debt_loss
        
        # Other Income
        other_income = other_income_per_unit * 12 * units * occupancy
        
        # Effective Gross Income
        egi = nri + other_income
        
        return RevenueResult(
            gross_potential_rent=gpr,
            loss_to_lease=ltl,
            vacancy_loss=vacancy,
            concessions=concession_loss,
            bad_debt=bad_debt_loss,
            net_rental_income=nri,
            other_income=other_income,
            effective_gross_income=egi,
        )
```

#### Expense Module

```python
class ExpenseCalculator:
    """
    Calculate operating expenses per Shieldstone Manual Section 4.
    """
    
    # Shieldstone expense growth defaults
    GROWTH_RATES = {
        'property_taxes': 0.025,      # 2.5% per year
        'insurance': 0.05,            # 5% per year (hardening market)
        'utilities': 0.03,            # 3% per year
        'repairs_maintenance': 0.03,  # 3% per year
        'payroll': 0.035,             # 3.5% per year
        'management_fee': 0.00,       # % of EGI, grows with revenue
        'admin': 0.03,                # 3% per year
        'marketing': 0.02,            # 2% per year
        'contract_services': 0.03,    # 3% per year
        'turnover': 0.03,             # 3% per year
    }
    
    def calculate_property_tax_reassessment(
        self,
        current_assessed_value: Decimal,
        purchase_price: Decimal,
        current_tax_rate: Decimal,
        state: str,
        reassessment_cap: Optional[Decimal] = None,
    ) -> Decimal:
        """
        Calculate property tax after reassessment.
        
        Per Shieldstone Manual Section 4.2:
        - Most states reassess to purchase price
        - Some states have caps (CA Prop 13, etc.)
        - Add 5-10% buffer for appeals/adjustments
        """
        if state in ['CA'] and reassessment_cap:
            new_assessed = min(purchase_price, 
                              current_assessed_value * (1 + reassessment_cap))
        else:
            new_assessed = purchase_price
        
        # Apply tax rate with 7.5% buffer
        new_tax = new_assessed * current_tax_rate * Decimal('1.075')
        
        return new_tax
    
    def calculate_year(
        self,
        year: int,
        base_expenses: ExpenseBreakdown,
        egi: Decimal,
        management_fee_pct: Decimal = Decimal('0.03'),
    ) -> ExpenseResult:
        """
        Calculate annual expenses with appropriate growth rates.
        """
        expenses = {}
        
        for category, base_amount in base_expenses.items():
            if category == 'management_fee':
                # Management fee as % of EGI
                expenses[category] = egi * management_fee_pct
            else:
                # Apply category-specific growth
                growth_rate = self.GROWTH_RATES.get(category, 0.03)
                expenses[category] = base_amount * (1 + growth_rate) ** (year - 1)
        
        total = sum(expenses.values())
        
        return ExpenseResult(
            line_items=expenses,
            total_operating_expenses=total,
            expense_ratio=total / egi if egi > 0 else Decimal('0'),
        )
```

#### CapEx Module

```python
class CapExCalculator:
    """
    Calculate capital expenditures per Shieldstone Manual Section 5.
    """
    
    # Shieldstone renovation cost benchmarks (per unit)
    RENOVATION_COSTS = {
        'light': {
            'interior': (3000, 5000),     # Paint, fixtures, appliances
            'exterior': (1000, 2000),     # Minor repairs, signage
            'amenities': (500, 1500),     # Common area refresh
        },
        'moderate': {
            'interior': (8000, 15000),    # Full interior renovation
            'exterior': (2000, 5000),     # Facade, roofing, parking
            'amenities': (2000, 5000),    # Pool, gym, clubhouse
        },
        'heavy': {
            'interior': (15000, 25000),   # Gut renovation
            'exterior': (5000, 10000),    # Major systems
            'amenities': (5000, 15000),   # Full amenity package
        },
    }
    
    def calculate_renovation_budget(
        self,
        units: int,
        renovation_type: str,  # 'light', 'moderate', 'heavy'
        market_tier: str,      # 'gateway', 'secondary', 'tertiary'
        scope: Dict[str, bool],  # Which components to include
    ) -> CapExBudget:
        """
        Calculate total renovation budget with phasing.
        """
        costs = self.RENOVATION_COSTS[renovation_type]
        
        # Market adjustment factor
        market_factors = {'gateway': 1.2, 'secondary': 1.0, 'tertiary': 0.85}
        factor = market_factors.get(market_tier, 1.0)
        
        budget = {}
        for component, include in scope.items():
            if include and component in costs:
                low, high = costs[component]
                # Use midpoint with market adjustment
                budget[component] = ((low + high) / 2) * factor * units
        
        total = sum(budget.values())
        
        return CapExBudget(
            line_items=budget,
            total_budget=total,
            per_unit=total / units,
            contingency=total * Decimal('0.10'),  # 10% contingency
        )
    
    def calculate_replacement_reserves(
        self,
        units: int,
        property_age: int,
        property_class: str,
    ) -> Decimal:
        """
        Calculate annual replacement reserves per Shieldstone standards.
        
        Base: $250-350/unit/year
        Adjustments for age and class
        """
        base_reserve = Decimal('300')  # Per unit per year
        
        # Age adjustment
        if property_age > 40:
            base_reserve *= Decimal('1.25')
        elif property_age > 25:
            base_reserve *= Decimal('1.10')
        
        # Class adjustment
        class_factors = {'A': 0.9, 'B': 1.0, 'C': 1.1, 'D': 1.25}
        base_reserve *= Decimal(str(class_factors.get(property_class, 1.0)))
        
        return base_reserve * units
```

#### Financing Module

```python
class FinancingCalculator:
    """
    Calculate debt service and refinancing per Shieldstone Manual Section 6.
    """
    
    def calculate_acquisition_loan(
        self,
        purchase_price: Decimal,
        ltv: Decimal,
        interest_rate: Decimal,
        amortization_years: int,
        io_period_years: int,
        term_years: int,
    ) -> LoanSchedule:
        """
        Calculate acquisition loan with IO period and amortization.
        """
        loan_amount = purchase_price * ltv
        monthly_rate = interest_rate / 12
        
        schedule = []
        balance = loan_amount
        
        for year in range(1, term_years + 1):
            if year <= io_period_years:
                # Interest-only period
                annual_interest = balance * interest_rate
                annual_principal = Decimal('0')
                annual_payment = annual_interest
            else:
                # Amortizing period
                remaining_months = (amortization_years - (year - io_period_years - 1)) * 12
                if remaining_months > 0:
                    monthly_payment = self._pmt(monthly_rate, remaining_months, balance)
                    annual_payment = monthly_payment * 12
                    annual_interest = balance * interest_rate  # Simplified
                    annual_principal = annual_payment - annual_interest
                else:
                    annual_payment = balance
                    annual_interest = Decimal('0')
                    annual_principal = balance
            
            balance -= annual_principal
            
            schedule.append(LoanYear(
                year=year,
                beginning_balance=balance + annual_principal,
                interest=annual_interest,
                principal=annual_principal,
                ending_balance=balance,
                payment=annual_payment,
            ))
        
        return LoanSchedule(
            loan_amount=loan_amount,
            years=schedule,
            total_interest=sum(y.interest for y in schedule),
        )
    
    def calculate_dscr(
        self,
        noi: Decimal,
        annual_debt_service: Decimal,
    ) -> Decimal:
        """Calculate Debt Service Coverage Ratio."""
        if annual_debt_service == 0:
            return Decimal('999')  # All-cash
        return noi / annual_debt_service
    
    def calculate_refinance(
        self,
        noi_at_refi: Decimal,
        exit_cap: Decimal,
        new_ltv: Decimal,
        new_rate: Decimal,
        existing_balance: Decimal,
    ) -> RefinanceResult:
        """
        Calculate refinance proceeds and new debt service.
        
        Per Shieldstone Manual Section 6.3:
        - Typically at Year 3 after stabilization
        - 75% LTV on stabilized value
        - Cash-out to return equity
        """
        stabilized_value = noi_at_refi / exit_cap
        max_loan = stabilized_value * new_ltv
        
        # DSCR constraint (1.25x minimum)
        max_loan_dscr = (noi_at_refi / Decimal('1.25')) / (new_rate + Decimal('0.02'))
        
        new_loan = min(max_loan, max_loan_dscr)
        cash_out = new_loan - existing_balance
        
        return RefinanceResult(
            stabilized_value=stabilized_value,
            new_loan_amount=new_loan,
            existing_balance_payoff=existing_balance,
            cash_out_proceeds=cash_out,
            new_annual_debt_service=new_loan * (new_rate + Decimal('0.02')),
        )
```

#### Returns Module

```python
class ReturnsCalculator:
    """
    Calculate investment returns per Shieldstone Manual Section 7.
    """
    
    def calculate_exit_value(
        self,
        exit_noi: Decimal,
        exit_cap: Decimal,
        selling_costs_pct: Decimal = Decimal('0.02'),
    ) -> ExitResult:
        """
        Calculate exit proceeds.
        
        Per Shieldstone Manual Section 7.2:
        - Exit cap = Entry cap + 10-25 bps (conservative)
        - Selling costs typically 2%
        """
        gross_value = exit_noi / exit_cap
        selling_costs = gross_value * selling_costs_pct
        net_proceeds = gross_value - selling_costs
        
        return ExitResult(
            exit_noi=exit_noi,
            exit_cap=exit_cap,
            gross_value=gross_value,
            selling_costs=selling_costs,
            net_proceeds=net_proceeds,
        )
    
    def calculate_irr(
        self,
        cash_flows: List[Decimal],
        dates: Optional[List[date]] = None,
    ) -> Decimal:
        """
        Calculate IRR or XIRR.
        
        Uses Newton-Raphson method for accuracy.
        """
        if dates:
            return self._xirr(cash_flows, dates)
        else:
            return self._irr(cash_flows)
    
    def calculate_equity_multiple(
        self,
        total_distributions: Decimal,
        total_equity_invested: Decimal,
    ) -> Decimal:
        """Calculate equity multiple (total return / invested)."""
        if total_equity_invested == 0:
            return Decimal('0')
        return total_distributions / total_equity_invested
    
    def calculate_cash_on_cash(
        self,
        annual_cash_flow: Decimal,
        equity_invested: Decimal,
    ) -> Decimal:
        """Calculate annual cash-on-cash return."""
        if equity_invested == 0:
            return Decimal('0')
        return annual_cash_flow / equity_invested
```

#### Waterfall Module

```python
class WaterfallCalculator:
    """
    Calculate GP/LP waterfall distributions per Shieldstone Manual Section 7.4.
    """
    
    def calculate_waterfall(
        self,
        total_distributions: Decimal,
        equity_invested: Decimal,
        structure: WaterfallStructure,
    ) -> WaterfallResult:
        """
        Calculate waterfall with multiple hurdles.
        
        Standard Shieldstone structure:
        - Tier 1: 8% pref to LP
        - Tier 2: Return of capital to LP
        - Tier 3: 70/30 LP/GP to 12% IRR
        - Tier 4: 60/40 LP/GP to 15% IRR  
        - Tier 5: 50/50 LP/GP above 15% IRR
        """
        remaining = total_distributions
        lp_total = Decimal('0')
        gp_total = Decimal('0')
        tier_details = []
        
        for tier in structure.tiers:
            if remaining <= 0:
                break
            
            if tier.type == 'preferred_return':
                # Calculate preferred return amount
                pref_amount = equity_invested * tier.hurdle_rate
                tier_distribution = min(remaining, pref_amount)
                lp_share = tier_distribution * tier.lp_split
                gp_share = tier_distribution * tier.gp_split
                
            elif tier.type == 'return_of_capital':
                tier_distribution = min(remaining, equity_invested)
                lp_share = tier_distribution * tier.lp_split
                gp_share = tier_distribution * tier.gp_split
                
            elif tier.type == 'profit_split':
                # Profit above previous hurdles
                tier_distribution = remaining  # All remaining goes through split
                lp_share = tier_distribution * tier.lp_split
                gp_share = tier_distribution * tier.gp_split
            
            remaining -= tier_distribution
            lp_total += lp_share
            gp_total += gp_share
            
            tier_details.append(TierResult(
                tier_name=tier.name,
                distribution=tier_distribution,
                lp_share=lp_share,
                gp_share=gp_share,
            ))
        
        return WaterfallResult(
            total_distributions=total_distributions,
            lp_total=lp_total,
            gp_total=gp_total,
            lp_irr=self._calculate_lp_irr(lp_total, equity_invested),
            gp_promote=gp_total,
            tier_details=tier_details,
        )
```

---

## 4. Assumption Categories

### 4.1 Acquisition Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| Purchase Price | Currency | From deal | $1M-$500M | User input or extracted |
| Closing Costs | % of Price | 2.5% | 1-4% | Due diligence, legal, etc. |
| Acquisition Fee | % of Price | 1.0% | 0-2% | GP acquisition fee |
| Earnest Money | % of Price | 1.0% | 0.5-3% | Hard/soft deposits |

### 4.2 Revenue Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| Year 1 Rent Growth | % | 3.0% | 0-10% | Above in-place |
| Stabilized Rent Growth | % | 2.5% | 2-4% | Years 2+ |
| Target Occupancy | % | 95% | 90-98% | Stabilized |
| Loss to Lease | % of GPR | Extracted | 0-15% | Burns off over time |
| Concessions | % of GPR | 1.0% | 0-5% | Lease-up incentives |
| Bad Debt | % of GPR | 1.0% | 0.5-3% | Collection loss |
| Other Income/Unit | $/unit/mo | $75 | $25-200 | Fees, parking, etc. |

### 4.3 Expense Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| Property Tax Growth | % | 2.5% | 1-5% | Annual increase |
| Insurance Growth | % | 5.0% | 3-8% | Hardening market |
| Expense Growth (Other) | % | 3.0% | 2-4% | General inflation |
| Management Fee | % of EGI | 3.0% | 2.5-5% | Third-party PM |
| Replacement Reserves | $/unit/yr | $300 | $250-500 | Per Shieldstone |

### 4.4 CapEx Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| Interior Renovation | $/unit | $0 | $0-25,000 | Per unit budget |
| Exterior Renovation | $/unit | $0 | $0-10,000 | Common areas |
| Renovation Contingency | % | 10% | 5-20% | Cost overrun buffer |
| Renovation Timeline | Months | 18 | 6-36 | Full completion |
| Units/Month Renovated | # | 5 | 2-15 | Renovation velocity |

### 4.5 Financing Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| LTV | % | 65% | 55-75% | Loan-to-value |
| Interest Rate | % | 6.5% | 5-9% | Current market |
| Amortization | Years | 30 | 25-30 | Loan amortization |
| IO Period | Years | 3 | 0-5 | Interest-only |
| Loan Term | Years | 5 | 3-10 | Maturity |
| Rate Type | Select | Fixed | Fixed/Floating | |
| Origination Fee | % | 1.0% | 0.5-2% | Points |

### 4.6 Exit Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| Hold Period | Years | 5 | 3-10 | Investment horizon |
| Exit Cap Rate | % | Entry + 15bps | 4-10% | Conservative |
| Selling Costs | % | 2.0% | 1.5-3% | Broker, legal |
| Exit Year NOI | Calc | Year N NOI | — | Auto-calculated |

### 4.7 Partnership Assumptions

| Assumption | Type | Default | Range | Notes |
|------------|------|---------|-------|-------|
| GP Co-Invest | % | 5% | 0-20% | GP equity |
| Preferred Return | % | 8% | 6-10% | LP pref |
| Promote Structure | Select | Standard | Custom | Waterfall tiers |
| Asset Mgmt Fee | % of EGI | 1.0% | 0.5-2% | Annual fee |
| Disposition Fee | % | 1.0% | 0-2% | On sale |

---

## 5. User Interface

### 5.1 Assumptions Editor

**Layout:** Tabbed interface with real-time updates

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Pro Forma: Oak Creek Apartments                    [Save] [Reset] [Export] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ [Acquisition] [Revenue] [Expenses] [CapEx] [Financing] [Exit] [Partner] ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Revenue Assumptions                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │ Year 1 Rent Growth          │  │ Current: 3.0%                       │   │
│  │ ───────────────────────     │  │ ┌─────────────────────────────────┐ │   │
│  │ [====|===============] 3.0% │  │ │ Market benchmark: 2.5% - 4.0%   │ │   │
│  │                             │  │ │ Your assumption is within range │ │   │
│  │ Min: 0%        Max: 10%     │  │ └─────────────────────────────────┘ │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │ Stabilized Rent Growth      │  │ Current: 2.5%                       │   │
│  │ ───────────────────────     │  │ ┌─────────────────────────────────┐ │   │
│  │ [===|================] 2.5% │  │ │ Shieldstone default: 2.5%       │ │   │
│  │                             │  │ │ ✓ Matches methodology           │ │   │
│  │ Min: 1%        Max: 5%      │  │ └─────────────────────────────────┘ │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │ Target Occupancy            │  │ Current: 95%                        │   │
│  │ ───────────────────────     │  │ ┌─────────────────────────────────┐ │   │
│  │ [=======|===========] 95%   │  │ │ Property in-place: 92%          │ │   │
│  │                             │  │ │ Market average: 94%             │ │   │
│  │ Min: 85%       Max: 98%     │  │ └─────────────────────────────────┘ │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                                              │
│  [+ Show Advanced Assumptions]                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Pro Forma Output Display

**Layout:** Multi-panel dashboard with key metrics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Pro Forma Results                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Key Metrics                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │   18.5%     │ │    1.85x    │ │    8.2%     │ │    1.35x    │            │
│  │   IRR       │ │   Equity    │ │  Avg CoC    │ │   DSCR      │            │
│  │   ✓ Pass    │ │  Multiple   │ │             │ │   ✓ Pass    │            │
│  │             │ │   ✓ Pass    │ │             │ │             │            │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘            │
│                                                                              │
│  Annual Cash Flows                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  │ $500K ─────────────────────────────────────────────────────────────────  │
│  │                                                              ████████    │
│  │                                                    ████████  ████████    │
│  │                                          ████████  ████████  ████████    │
│  │                                ████████  ████████  ████████  ████████    │
│  │                      ████████  ████████  ████████  ████████  ████████    │
│  │            ████████  ████████  ████████  ████████  ████████  ████████    │
│  │  ████████  ████████  ████████  ████████  ████████  ████████  ████████    │
│  │  ████████  ████████  ████████  ████████  ████████  ████████  ████████    │
│  └────────────────────────────────────────────────────────────────────────  │
│      Year 1    Year 2    Year 3    Year 4    Year 5    Year 6    Exit       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                          DETAILED PRO FORMA                              ││
│  │                                                                          ││
│  │  [Revenue ▼]                                                             ││
│  │  ─────────────────────────────────────────────────────────────────────  ││
│  │                    Year 1      Year 2      Year 3      Year 4    Year 5 ││
│  │  Gross Potential  $1,152,000  $1,186,560  $1,222,157  $1,258,821 $1,296  ││
│  │  Loss to Lease      (57,600)    (35,598)    (18,332)     (9,441)   (4,8  ││
│  │  Vacancy            (57,600)    (59,328)    (61,108)    (62,941)  (64,8  ││
│  │  Concessions        (11,520)    (11,866)    (12,222)    (12,588)  (12,9  ││
│  │  Bad Debt           (11,520)    (11,866)    (12,222)    (12,588)  (12,9  ││
│  │  Net Rental Inc   $1,013,760  $1,067,903  $1,118,274  $1,161,263 $1,200  ││
│  │  Other Income        $86,400     $88,992     $91,662     $94,412   $97,2 ││
│  │  ─────────────────────────────────────────────────────────────────────  ││
│  │  EGI              $1,100,160  $1,156,895  $1,209,936  $1,255,675 $1,297  ││
│  │                                                                          ││
│  │  [Expenses ▼]                                                            ││
│  │  [NOI ▼]                                                                 ││
│  │  [Debt Service ▼]                                                        ││
│  │  [Cash Flow ▼]                                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Sensitivity Analysis Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Sensitivity Analysis                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Variable Selection                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Row Variable: [Exit Cap Rate ▼]     Column Variable: [Rent Growth ▼]    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  IRR Sensitivity Matrix                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │              │   1.5%   │   2.0%   │   2.5%   │   3.0%   │   3.5%   │   ││
│  │              │ Rent Grw │ Rent Grw │ Rent Grw │ Rent Grw │ Rent Grw │   ││
│  │──────────────┼──────────┼──────────┼──────────┼──────────┼──────────│   ││
│  │ 5.00% Exit   │  22.1%   │  23.4%   │  24.8%   │  26.1%   │  27.5%   │   ││
│  │ 5.25% Exit   │  19.8%   │  21.1%   │  22.4%   │  23.7%   │  25.0%   │   ││
│  │ 5.50% Exit   │  17.6%   │  18.9%   │ [20.2%]  │  21.5%   │  22.8%   │   ││
│  │ 5.75% Exit   │  15.5%   │  16.8%   │  18.1%   │  19.4%   │  20.7%   │   ││
│  │ 6.00% Exit   │  13.5%   │  14.8%   │  16.1%   │  17.4%   │  18.7%   │   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Legend: [Base Case]  ■ Above Hurdle (14%)  ■ Below Hurdle                  │
│                                                                              │
│  Additional Sensitivities                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ [+ Add Purchase Price]  [+ Add LTV]  [+ Add Interest Rate]              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Waterfall Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Waterfall Distribution                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Total Distributions: $5,250,000                                             │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │  ████████████████████████████████████████████████████████████████████   ││
│  │  │                                                                   │   ││
│  │  │ 8% Pref      │ Return of    │  70/30 Split │ 50/50 Split │        │   ││
│  │  │ $280K        │ Capital      │  $1,470K     │ $500K       │        │   ││
│  │  │              │ $3,000K      │              │             │        │   ││
│  │  │──────────────│──────────────│──────────────│─────────────│        │   ││
│  │  │ LP: $280K    │ LP: $3,000K  │ LP: $1,029K  │ LP: $250K   │        │   ││
│  │  │ GP: $0       │ GP: $0       │ GP: $441K    │ GP: $250K   │        │   ││
│  │  │              │              │              │             │        │   ││
│  │  └──────────────────────────────────────────────────────────────────────┘││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Summary                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                    LP                          GP                        ││
│  │  Total           $4,559,000 (86.8%)           $691,000 (13.2%)          ││
│  │  Equity          $2,850,000                   $150,000                   ││
│  │  Multiple        1.60x                        4.61x                      ││
│  │  IRR             16.2%                        42.5%                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  [Edit Waterfall Structure]  [Compare Structures]                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Scenario Management

### 6.1 Scenario Types

| Scenario | Purpose | Key Adjustments |
|----------|---------|-----------------|
| **Base Case** | Primary underwriting | User's best estimates |
| **Downside** | Stress test | -10% rents, +50bps exit cap, 6mo delay |
| **Upside** | Best case | +5% rents, -25bps exit cap |
| **Sponsor Case** | Compare to seller | Match seller's assumptions |
| **Custom** | User-defined | Any combination |

### 6.2 Scenario Comparison View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Scenario Comparison                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                 │   Base Case   │   Downside   │   Upside   │  Sponsor  ││
│  │─────────────────┼───────────────┼──────────────┼────────────┼───────────││
│  │ IRR             │     18.5%     │    12.3%     │   24.1%    │   22.0%   ││
│  │ Equity Multiple │     1.85x     │    1.52x     │   2.15x    │   2.05x   ││
│  │ Avg CoC         │     8.2%      │    5.1%      │   10.8%    │   9.5%    ││
│  │ Exit Value      │   $16.2M      │   $14.1M     │  $18.5M    │  $17.8M   ││
│  │ Exit NOI        │   $890K       │   $801K      │   $935K    │   $925K   ││
│  │─────────────────┼───────────────┼──────────────┼────────────┼───────────││
│  │ Key Differences │               │              │            │           ││
│  │ Rent Growth     │     2.5%      │    1.5%      │   3.5%     │   4.0%    ││
│  │ Exit Cap        │     5.50%     │    6.00%     │   5.25%    │   5.00%   ││
│  │ Occupancy       │     95%       │    92%       │   96%      │   97%     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Probability-Weighted Return                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Scenario Weights: Base 50% │ Downside 30% │ Upside 20%                  ││
│  │ Weighted IRR: 16.8%                                                      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. API Specifications

### 7.1 Pro Forma Endpoints

#### Create/Update Pro Forma

```
POST /api/v1/deals/{deal_id}/proforma

Request Body:
{
  "assumptions": {
    "acquisition": {
      "purchase_price": 12500000,
      "closing_costs_pct": 0.025,
      "acquisition_fee_pct": 0.01
    },
    "revenue": {
      "year1_rent_growth": 0.03,
      "stabilized_rent_growth": 0.025,
      "target_occupancy": 0.95,
      "loss_to_lease": 0.05,
      "concessions": 0.01,
      "bad_debt": 0.01,
      "other_income_per_unit": 75
    },
    "expenses": {
      "property_tax_growth": 0.025,
      "insurance_growth": 0.05,
      "expense_growth": 0.03,
      "management_fee_pct": 0.03,
      "replacement_reserves_per_unit": 300
    },
    "capex": {
      "interior_per_unit": 8000,
      "exterior_per_unit": 2000,
      "contingency_pct": 0.10,
      "timeline_months": 18,
      "units_per_month": 5
    },
    "financing": {
      "ltv": 0.65,
      "interest_rate": 0.065,
      "amortization_years": 30,
      "io_period_years": 3,
      "loan_term_years": 5,
      "rate_type": "FIXED",
      "origination_fee_pct": 0.01
    },
    "exit": {
      "hold_period_years": 5,
      "exit_cap_rate": 0.055,
      "selling_costs_pct": 0.02
    },
    "partnership": {
      "gp_coinvest_pct": 0.05,
      "preferred_return": 0.08,
      "waterfall_structure": "STANDARD",
      "asset_mgmt_fee_pct": 0.01,
      "disposition_fee_pct": 0.01
    }
  }
}

Response (200 OK):
{
  "proforma_id": "pf_abc123",
  "deal_id": "deal_xyz789",
  "version": 3,
  "calculated_at": "2025-12-20T10:30:00Z",
  "results": {
    "summary": {
      "irr": 0.185,
      "equity_multiple": 1.85,
      "avg_cash_on_cash": 0.082,
      "total_equity_required": 4875000,
      "total_distributions": 9018750,
      "exit_value": 16200000
    },
    "annual_cashflows": [...],
    "waterfall": {...},
    "sensitivities": {...}
  }
}
```

#### Get Pro Forma

```
GET /api/v1/deals/{deal_id}/proforma

Response (200 OK):
{
  "proforma_id": "pf_abc123",
  "deal_id": "deal_xyz789",
  "version": 3,
  "assumptions": {...},
  "results": {...},
  "scenarios": [
    {"name": "Base Case", "is_active": true, ...},
    {"name": "Downside", "is_active": false, ...}
  ]
}
```

#### Run Sensitivity Analysis

```
POST /api/v1/deals/{deal_id}/proforma/sensitivity

Request Body:
{
  "row_variable": "exit_cap_rate",
  "row_range": [0.05, 0.055, 0.06, 0.065, 0.07],
  "column_variable": "rent_growth",
  "column_range": [0.015, 0.02, 0.025, 0.03, 0.035],
  "output_metric": "irr"
}

Response (200 OK):
{
  "matrix": [
    [0.221, 0.234, 0.248, 0.261, 0.275],
    [0.198, 0.211, 0.224, 0.237, 0.250],
    [0.176, 0.189, 0.202, 0.215, 0.228],
    [0.155, 0.168, 0.181, 0.194, 0.207],
    [0.135, 0.148, 0.161, 0.174, 0.187]
  ],
  "base_case_position": [2, 2],
  "hurdle_rate": 0.14
}
```

#### Calculate Waterfall

```
POST /api/v1/deals/{deal_id}/proforma/waterfall

Request Body:
{
  "total_distributions": 5250000,
  "equity_invested": 3000000,
  "structure": {
    "tiers": [
      {"name": "8% Pref", "type": "preferred_return", "hurdle_rate": 0.08, "lp_split": 1.0, "gp_split": 0.0},
      {"name": "Return of Capital", "type": "return_of_capital", "lp_split": 1.0, "gp_split": 0.0},
      {"name": "70/30 to 12%", "type": "profit_split", "hurdle_irr": 0.12, "lp_split": 0.7, "gp_split": 0.3},
      {"name": "50/50 Above", "type": "profit_split", "lp_split": 0.5, "gp_split": 0.5}
    ]
  }
}

Response (200 OK):
{
  "total_distributions": 5250000,
  "lp_total": 4559000,
  "gp_total": 691000,
  "lp_irr": 0.162,
  "gp_irr": 0.425,
  "tier_details": [...]
}
```

---

## 8. Database Schema

```sql
-- Pro forma table
CREATE TABLE proformas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    parent_version_id UUID REFERENCES proformas(id),
    
    -- Assumptions (JSONB for flexibility)
    assumptions JSONB NOT NULL,
    
    -- Calculated results (cached)
    results JSONB,
    calculated_at TIMESTAMPTZ,
    calculation_time_ms INTEGER,
    
    -- Metadata
    name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_active_version UNIQUE (deal_id, version)
);

-- Scenarios table
CREATE TABLE proforma_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proforma_id UUID NOT NULL REFERENCES proformas(id) ON DELETE CASCADE,
    
    -- Scenario details
    name VARCHAR(100) NOT NULL,
    scenario_type scenario_type_enum NOT NULL,
    is_base_case BOOLEAN NOT NULL DEFAULT false,
    
    -- Assumption overrides
    assumption_overrides JSONB,
    
    -- Calculated results
    results JSONB,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sensitivity analyses
CREATE TABLE sensitivity_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proforma_id UUID NOT NULL REFERENCES proformas(id) ON DELETE CASCADE,
    
    -- Configuration
    row_variable VARCHAR(50) NOT NULL,
    row_range DECIMAL[] NOT NULL,
    column_variable VARCHAR(50) NOT NULL,
    column_range DECIMAL[] NOT NULL,
    output_metric VARCHAR(50) NOT NULL,
    
    -- Results
    matrix JSONB NOT NULL,
    base_case_position INTEGER[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Assumption templates (reusable)
CREATE TABLE assumption_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    created_by UUID NOT NULL REFERENCES users(id),
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    assumptions JSONB NOT NULL,
    
    -- Applicability
    property_type property_type_enum,
    market_tier market_tier_enum,
    
    is_default BOOLEAN NOT NULL DEFAULT false,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_proformas_deal ON proformas(deal_id);
CREATE INDEX idx_proformas_active ON proformas(deal_id) WHERE is_active = true;
CREATE INDEX idx_scenarios_proforma ON proforma_scenarios(proforma_id);
CREATE INDEX idx_templates_org ON assumption_templates(organization_id);
```

---

## 9. Testing Requirements

### 9.1 Calculation Accuracy Tests

| Test Suite | Description | Target |
|------------|-------------|--------|
| IRR Calculations | Compare to Excel XIRR | ±0.01% |
| Waterfall Distributions | Test all tier combinations | 100% match |
| Debt Service | Amortization schedules | ±$1 |
| Property Tax Reassessment | State-specific rules | 100% compliance |
| Expense Growth | Multi-year projections | ±$1 |

### 9.2 Regression Tests

- Compare outputs against 50+ historical deals modeled in Excel
- Automated nightly runs
- Alert on any deviation >0.1%

### 9.3 Performance Tests

| Operation | Target | Method |
|-----------|--------|--------|
| Full pro forma calculation | <500ms | Load test |
| Sensitivity matrix (5x5) | <200ms | Load test |
| Waterfall calculation | <100ms | Load test |
| Scenario comparison (4) | <1s | Load test |

---

## 10. Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| Support for ground lease deals? | Yes | Per Shieldstone Manual Section 6.4 |
| Multi-property portfolio modeling? | Future | Post-MVP |
| Integration with Argus exports? | Future | Evaluate demand |
| Custom waterfall builder UI? | Phase 4.1 | Start with presets |
| Monte Carlo simulation? | Future | Nice to have |

---

## 11. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Shieldstone Python Library | Internal | Build in parallel |
| numpy-financial | External | Available |
| decimal (Python) | Built-in | Available |
| Chart.js or Recharts | Frontend | Available |

---

## 12. Rollout Plan

### Phase 4a: Core Engine (Week 3)
- Revenue calculations
- Expense calculations
- NOI projections

### Phase 4b: Financing & Returns (Week 3-4)
- Debt service calculations
- IRR/EM calculations
- Exit value calculations

### Phase 4c: Waterfall & Sensitivity (Week 4)
- Waterfall engine
- Sensitivity analysis
- Scenario management

### Phase 4d: UI & Polish (Week 4)
- Assumptions editor
- Results dashboard
- Charts and visualizations

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Author: DREAM AI Product Team*









