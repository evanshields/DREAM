"""
PHASE 8: MASTER WORKFLOW INTEGRATION
=====================================

From Shieldstone Technical Manual v2.0 - Section 13

Complete underwriting workflow orchestrating all 8 phases from initial
screening through final investment recommendation.

Critical Philosophy:
- Economics determine viability - not arbitrary rules
- Risk factors require adjustment, not rejection
- Conservative bias protects capital
- If assumptions don't hold under scrutiny, pass or reprice

Workflow Phases:
1. Deal Screening (Red flags & risk adjustments)
2. Market Analysis (Market fundamentals scoring)
3. Revenue Underwriting (Rent validation)
4. Operating Expenses (Tax, insurance, etc.)
5. Capex Planning (Renovation budget & ROI)
6. Financing Structure (Debt sizing & DSCR)
7. Returns Analysis (IRR, CoC, EM vs. hurdles)
8. Risk Assessment & Final Recommendation

"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class WorkflowPhase(Enum):
    """Workflow execution phases."""
    SCREENING = "screening"
    MARKET = "market_analysis"
    REVENUE = "revenue_underwriting"
    EXPENSES = "expense_underwriting"
    CAPEX = "capex_planning"
    FINANCING = "financing_structure"
    RETURNS = "returns_analysis"
    RISK = "risk_assessment"
    FINAL = "final_recommendation"


class RecommendationType(Enum):
    """Final recommendation types."""
    PROCEED = "PROCEED"
    PROCEED_WITH_CAUTION = "PROCEED_WITH_CAUTION"
    REQUEST_REPRICING = "REQUEST_REPRICING"
    PASS = "PASS"


@dataclass
class WorkflowStatus:
    """Track workflow progress and findings."""
    phase: WorkflowPhase
    passed: bool
    findings: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DealInputData:
    """
    Complete deal input data for workflow.
    Designed to be populated from user interface.
    """
    # Property Basics
    property_name: str
    address: str
    city: str
    state: str
    zip_code: str
    year_built: int
    unit_count: int
    property_class: str  # 'A', 'B', 'C', 'D'
    
    # Financial Data
    purchase_price: float
    current_noi: float
    current_occupancy: float
    current_avg_rent: float
    
    # Market Data
    market_tier: str  # 'gateway', 'secondary', 'tertiary'
    submarket_type: str  # 'primary', 'secondary', 'tertiary', 'emerging'
    
    # Business Plan
    renovation_scope: str  # 'light', 'moderate', 'heavy'
    renovation_cost_total: float
    target_stabilized_noi: float
    target_stabilized_occupancy: float
    target_avg_rent: float
    
    # Financing Assumptions
    ltv: float = 0.65
    interest_rate: Optional[float] = None  # If None, calculate from Treasury
    io_period_months: int = 30
    loan_term_years: int = 5
    
    # Additional Data
    property_tax_current: Optional[float] = None
    property_tax_reassessment_ratio: Optional[float] = None


class CompleteUnderwritingWorkflow:
    """
    Master workflow orchestrator integrating all 8 phases.
    
    Executes complete deal analysis from screening through final recommendation.
    Each phase uses corresponding section's Python implementations.
    
    Design: Market-agnostic, suitable for any operator.
    """
    
    def __init__(self, deal_data: DealInputData):
        self.deal = deal_data
        self.workflow_history: List[WorkflowStatus] = []
        self.current_phase = WorkflowPhase.SCREENING
        self.findings_aggregate: List[str] = []
        self.warnings_aggregate: List[str] = []
        self.final_recommendation: Optional[RecommendationType] = None
        
    def execute_complete_workflow(self) -> Dict:
        """
        Execute all 8 phases of underwriting workflow.
        
        Returns comprehensive analysis with go/no-go recommendation.
        """
        try:
            # Phase 1: Screening
            screening_result = self._phase_1_screening()
            if not screening_result['passed']:
                return self._generate_final_report(early_exit=True)
            
            # Phase 2: Market Analysis
            market_result = self._phase_2_market_analysis()
            
            # Phase 3: Revenue Underwriting
            revenue_result = self._phase_3_revenue()
            
            # Phase 4: Operating Expenses
            expense_result = self._phase_4_expenses()
            
            # Phase 5: Capex Planning
            capex_result = self._phase_5_capex()
            
            # Phase 6: Financing
            financing_result = self._phase_6_financing()
            
            # Phase 7: Returns Analysis
            returns_result = self._phase_7_returns()
            
            # Phase 8: Risk Assessment & Final Recommendation
            final_result = self._phase_8_final_recommendation()
            
            return self._generate_final_report()
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Workflow execution error: {str(e)}",
                'phase_reached': self.current_phase.value
            }
    
    def _phase_1_screening(self) -> Dict:
        """
        Phase 1: Deal Screening
        
        Uses DealScreener from phase_2_deal_screening module.
        """
        self.current_phase = WorkflowPhase.SCREENING
        
        # Simplified screening for workflow integration
        # In production, would use full DealScreener
        screening_passed = True
        hurdle_adjustment_bps = 0
        
        # Basic age adjustment
        property_age = 2025 - self.deal.year_built
        if property_age > 40:
            hurdle_adjustment_bps += 150
        elif property_age > 30:
            hurdle_adjustment_bps += 100
        
        # Occupancy adjustment
        if self.deal.current_occupancy < 0.75:
            hurdle_adjustment_bps += 150
        elif self.deal.current_occupancy < 0.85:
            hurdle_adjustment_bps += 100
        
        status = WorkflowStatus(
            phase=WorkflowPhase.SCREENING,
            passed=screening_passed,
            findings=[f"Total hurdle adjustment: +{hurdle_adjustment_bps} bps"],
            data={'hurdle_adjustment_bps': hurdle_adjustment_bps}
        )
        self.workflow_history.append(status)
        
        return {'passed': screening_passed, 'hurdle_adjustment': hurdle_adjustment_bps}
    
    def _phase_2_market_analysis(self) -> Dict:
        """Phase 2: Market Analysis"""
        self.current_phase = WorkflowPhase.MARKET
        
        # Placeholder for market scoring
        market_score = 75  # Would come from actual analysis
        
        status = WorkflowStatus(
            phase=WorkflowPhase.MARKET,
            passed=market_score >= 50,
            data={'market_score': market_score}
        )
        self.workflow_history.append(status)
        
        return {'market_score': market_score}
    
    def _phase_3_revenue(self) -> Dict:
        """Phase 3: Revenue Underwriting"""
        self.current_phase = WorkflowPhase.REVENUE
        
        # Validate rent premium
        implied_premium = (self.deal.target_avg_rent - self.deal.current_avg_rent) / self.deal.current_avg_rent
        
        property_age = 2025 - self.deal.year_built
        max_premium = 0.15 if property_age > 30 else 0.20
        
        findings = []
        if implied_premium > max_premium:
            findings.append(f"Rent premium {implied_premium:.1%} exceeds cap {max_premium:.1%}")
            self.warnings_aggregate.append("Aggressive rent assumptions")
        
        status = WorkflowStatus(
            phase=WorkflowPhase.REVENUE,
            passed=implied_premium <= max_premium * 1.1,
            findings=findings,
            data={'implied_premium': implied_premium, 'max_premium': max_premium}
        )
        self.workflow_history.append(status)
        
        return status.data
    
    def _phase_4_expenses(self) -> Dict:
        """Phase 4: Operating Expense Underwriting"""
        self.current_phase = WorkflowPhase.EXPENSES
        
        # Property tax calculation would use PropertyTaxCalculator
        status = WorkflowStatus(
            phase=WorkflowPhase.EXPENSES,
            passed=True,
            data={}
        )
        self.workflow_history.append(status)
        
        return status.data
    
    def _phase_5_capex(self) -> Dict:
        """Phase 5: Capital Expenditure Planning"""
        self.current_phase = WorkflowPhase.CAPEX
        
        # Calculate capex ROI
        annual_rent_increase = (
            (self.deal.target_avg_rent - self.deal.current_avg_rent) * 
            12 * self.deal.unit_count
        )
        achievable_noi_increase = annual_rent_increase * 0.75
        capex_roi = achievable_noi_increase / self.deal.renovation_cost_total if self.deal.renovation_cost_total > 0 else 0
        
        findings = []
        if capex_roi < 0.08:
            findings.append(f"Capex ROI {capex_roi:.1%} below 8% minimum")
            self.warnings_aggregate.append("Inadequate renovation ROI")
        
        status = WorkflowStatus(
            phase=WorkflowPhase.CAPEX,
            passed=capex_roi >= 0.06,
            findings=findings,
            data={'capex_roi': capex_roi}
        )
        self.workflow_history.append(status)
        
        return status.data
    
    def _phase_6_financing(self) -> Dict:
        """Phase 6: Financing Structure"""
        self.current_phase = WorkflowPhase.FINANCING
        
        # Calculate loan and equity
        loan_amount = self.deal.purchase_price * self.deal.ltv
        interest_rate = self.deal.interest_rate or 0.0575
        closing_costs = self.deal.purchase_price * 0.03
        total_equity = (
            (self.deal.purchase_price - loan_amount) + 
            closing_costs + 
            self.deal.renovation_cost_total
        )
        
        annual_debt_service = loan_amount * interest_rate
        dscr = self.deal.target_stabilized_noi / annual_debt_service if annual_debt_service > 0 else 0
        
        findings = []
        if dscr < 1.25:
            findings.append(f"Stabilized DSCR {dscr:.2f}x below 1.25x minimum")
            self.warnings_aggregate.append("Insufficient debt service coverage")
        
        status = WorkflowStatus(
            phase=WorkflowPhase.FINANCING,
            passed=dscr >= 1.20,
            findings=findings,
            data={
                'loan_amount': loan_amount,
                'total_equity': total_equity,
                'annual_debt_service': annual_debt_service,
                'stabilized_dscr': dscr
            }
        )
        self.workflow_history.append(status)
        
        return status.data
    
    def _phase_7_returns(self) -> Dict:
        """Phase 7: Returns Analysis"""
        self.current_phase = WorkflowPhase.RETURNS
        
        # Get financing data
        financing_data = self.workflow_history[-1].data
        
        # Simplified IRR estimate (placeholder)
        estimated_irr = 0.175  # Would use actual IRR calculator
        
        # Get hurdle from screening
        screening_data = self.workflow_history[0].data
        base_hurdle = 0.175  # Secondary market base
        adjusted_hurdle = base_hurdle + (screening_data.get('hurdle_adjustment_bps', 0) / 10000)
        final_hurdle = max(adjusted_hurdle, 0.14)  # Absolute minimum
        
        stabilized_coc = 0.075  # Placeholder
        coc_floor = 0.07
        
        findings = []
        if estimated_irr < final_hurdle:
            findings.append(f"Estimated IRR {estimated_irr:.1%} below hurdle {final_hurdle:.1%}")
            self.warnings_aggregate.append("Returns below adjusted hurdles")
        
        status = WorkflowStatus(
            phase=WorkflowPhase.RETURNS,
            passed=estimated_irr >= 0.14,
            findings=findings,
            data={
                'estimated_irr': estimated_irr,
                'hurdle_irr': final_hurdle,
                'stabilized_coc': stabilized_coc,
                'coc_floor': coc_floor,
                'meets_hurdles': estimated_irr >= final_hurdle
            }
        )
        self.workflow_history.append(status)
        
        return status.data
    
    def _phase_8_final_recommendation(self) -> Dict:
        """Phase 8: Risk Assessment & Final Recommendation"""
        self.current_phase = WorkflowPhase.FINAL
        
        # Count phase passes
        phases_passed = sum(1 for s in self.workflow_history if s.passed)
        total_phases = len(self.workflow_history)
        
        # Get returns data
        returns_data = self.workflow_history[-1].data
        
        # Make recommendation
        if returns_data.get('estimated_irr', 0) < 0.14:
            recommendation = RecommendationType.PASS
            reasoning = "IRR below 14% absolute minimum"
        elif len(self.warnings_aggregate) == 0 and phases_passed == total_phases:
            recommendation = RecommendationType.PROCEED
            reasoning = "All phases passed with no material warnings"
        elif len(self.warnings_aggregate) <= 2:
            recommendation = RecommendationType.PROCEED_WITH_CAUTION
            reasoning = "Deal workable but requires attention to flagged items"
        else:
            recommendation = RecommendationType.REQUEST_REPRICING
            reasoning = "Multiple concerns - repricing required to justify risk"
        
        self.final_recommendation = recommendation
        
        status = WorkflowStatus(
            phase=WorkflowPhase.FINAL,
            passed=recommendation in [RecommendationType.PROCEED, RecommendationType.PROCEED_WITH_CAUTION],
            findings=[reasoning],
            data={
                'recommendation': recommendation.value,
                'reasoning': reasoning,
                'phases_passed': phases_passed,
                'total_phases': total_phases
            }
        )
        self.workflow_history.append(status)
        
        return status.data
    
    def _generate_final_report(self, early_exit: bool = False) -> Dict:
        """Generate comprehensive final report."""
        return {
            'property_name': self.deal.property_name,
            'recommendation': self.final_recommendation.value if self.final_recommendation else 'INCOMPLETE',
            'workflow_complete': not early_exit,
            'phases_executed': [s.phase.value for s in self.workflow_history],
            'phases_passed': sum(1 for s in self.workflow_history if s.passed),
            'total_phases': len(self.workflow_history),
            'findings': self.findings_aggregate,
            'warnings': self.warnings_aggregate,
            'phase_details': [
                {
                    'phase': s.phase.value,
                    'passed': s.passed,
                    'findings': s.findings,
                    'key_metrics': s.data
                }
                for s in self.workflow_history
            ],
            'timestamp': datetime.now().isoformat()
        }


def determine_recommendation(
    irr: float,
    coc_stabilized: float,
    hurdle_irr: float,
    hurdle_coc: float,
    warnings_count: int,
    red_flags_present: bool
) -> RecommendationType:
    """
    Systematic recommendation logic.
    
    Args:
        irr: Projected IRR
        coc_stabilized: Projected stabilized CoC
        hurdle_irr: Required IRR hurdle
        hurdle_coc: Required CoC floor
        warnings_count: Number of warnings flagged
        red_flags_present: Whether any red flags exist
    
    Returns:
        RecommendationType: Final recommendation
    """
    # Absolute disqualifiers
    if red_flags_present:
        return RecommendationType.PASS
    
    if irr < 0.14:  # Absolute minimum
        return RecommendationType.PASS
    
    # Check hurdle clearance
    irr_margin = irr - hurdle_irr
    coc_margin = coc_stabilized - hurdle_coc
    
    # Strong deal
    if irr_margin >= 0.01 and coc_margin >= 0.005 and warnings_count == 0:
        return RecommendationType.PROCEED
    
    # Acceptable deal with cautions
    if irr_margin >= 0.005 and coc_margin >= 0.0 and warnings_count <= 2:
        return RecommendationType.PROCEED_WITH_CAUTION
    
    # Marginal - needs repricing
    if irr_margin >= -0.01 and warnings_count <= 3:
        return RecommendationType.REQUEST_REPRICING
    
    # Doesn't work
    return RecommendationType.PASS

