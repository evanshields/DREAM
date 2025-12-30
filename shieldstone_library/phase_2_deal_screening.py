"""
PHASE 2: DEAL SCREENING & VALIDATION
====================================

From Shieldstone Technical Manual v2.0 - Section 2.1

Merit-based screening framework that checks for true deal-killers (red flags)
and calculates risk adjustments for non-disqualifying factors.

Philosophy:
- Red flags = unmitigable issues that kill deals
- Risk factors = adjustments to hurdles and contingencies
- Economics determine viability, not arbitrary cutoffs

Key Features:
- Red flag checking (structural, environmental, market, legal)
- Risk-based hurdle adjustments (age, occupancy, class, maintenance)
- No hard disqualifiers on age or occupancy
- Systematic recommendation logic

"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RedFlagCategory(Enum):
    """Categories of deal-killer red flags."""
    STRUCTURAL = "structural"
    ENVIRONMENTAL = "environmental"
    MARKET = "market"
    LEGAL = "legal"


class RiskLevel(Enum):
    """Risk severity classifications."""
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    SEVERE = "severe"


@dataclass
class ScreeningInput:
    """
    Input data for deal screening.
    
    Attributes:
        property_age_years: Age of property in years
        current_occupancy: Current occupancy rate (0.0 to 1.0)
        property_class: Property class ('A', 'B', 'C', 'D')
        deferred_maintenance_per_unit: Estimated deferred maintenance per unit
        unit_count: Total number of units
        
        Red flag checks (True = issue present):
        structural_issues: Known structural failure or condemnation
        environmental_contamination: Active soil/groundwater contamination
        severe_flood_zone: FEMA Zone A/V without mitigation
        code_violations_unresolved: Outstanding violations preventing occupancy
        high_crime_area: Violent crime >2.5x national average
        population_declining: Population decline >1%/year for 5+ years
        single_employer_risk: Single employer >40% of employment
        title_defects: Unresolvable title defects
        active_litigation: Active litigation affecting transfer
        zoning_nonconformance: Non-conforming use without grandfathering
        
        Market characteristics:
        submarket_type: 'primary', 'secondary', 'tertiary', 'emerging'
        supply_pipeline_pct: New supply as % of existing inventory
        population_growth_5yr: 5-year population growth rate
        employment_growth_5yr: 5-year employment growth rate
    """
    # Property basics
    property_age_years: int
    current_occupancy: float  # 0.0 to 1.0
    property_class: str  # 'A', 'B', 'C', 'D'
    deferred_maintenance_per_unit: float
    unit_count: int
    
    # Red flag checks (True = issue present)
    structural_issues: bool = False
    environmental_contamination: bool = False
    severe_flood_zone: bool = False  # FEMA A/V without mitigation
    code_violations_unresolved: bool = False
    high_crime_area: bool = False  # >2.5x national average
    population_declining: bool = False  # >1%/year for 5+ years
    single_employer_risk: bool = False  # >40% employment concentration
    title_defects: bool = False
    active_litigation: bool = False
    zoning_nonconformance: bool = False
    
    # Market characteristics
    submarket_type: str = 'primary'  # 'primary', 'secondary', 'tertiary', 'emerging'
    supply_pipeline_pct: float = 0.0  # New supply as % of existing inventory
    population_growth_5yr: float = 0.0
    employment_growth_5yr: float = 0.0


class DealScreener:
    """
    Screen deals using merit-based framework.
    
    Philosophy:
    - Red flags = true deal-killers that cannot be mitigated
    - Risk factors = adjustments to hurdles and contingencies
    - Economics determine viability, not arbitrary cutoffs
    
    Methods:
    - check_red_flags(): Identify unmitigable deal-killers
    - calculate_risk_adjustments(): Calculate hurdle and contingency adjustments
    - screen(): Execute complete screening process with recommendation
    """
    
    RED_FLAG_DEFINITIONS = {
        'structural_issues': {
            'category': RedFlagCategory.STRUCTURAL,
            'description': 'Known structural failure or condemnation',
            'exception': 'Engineer-approved remediation with guaranteed costs'
        },
        'environmental_contamination': {
            'category': RedFlagCategory.ENVIRONMENTAL,
            'description': 'Active soil/groundwater contamination',
            'exception': 'De minimis findings or NFA letter'
        },
        'severe_flood_zone': {
            'category': RedFlagCategory.STRUCTURAL,
            'description': 'FEMA Zone A/V without mitigation',
            'exception': 'Elevated structure or successful LOMA/LOMR'
        },
        'code_violations_unresolved': {
            'category': RedFlagCategory.STRUCTURAL,
            'description': 'Outstanding violations preventing occupancy',
            'exception': 'Documented remediation plan'
        },
        'high_crime_area': {
            'category': RedFlagCategory.MARKET,
            'description': 'Violent crime >2.5x national average',
            'exception': 'Improving trend with security plan'
        },
        'population_declining': {
            'category': RedFlagCategory.MARKET,
            'description': 'Population decline >1%/yr for 5+ years',
            'exception': 'Submarket with countervailing growth drivers'
        },
        'single_employer_risk': {
            'category': RedFlagCategory.MARKET,
            'description': 'Single employer >40% of employment',
            'exception': 'Government, healthcare, or university employer'
        },
        'title_defects': {
            'category': RedFlagCategory.LEGAL,
            'description': 'Unresolvable title defects',
            'exception': 'Title insurance with appropriate endorsements'
        },
        'active_litigation': {
            'category': RedFlagCategory.LEGAL,
            'description': 'Active litigation affecting transfer',
            'exception': 'Litigation escrowed or seller indemnification'
        },
        'zoning_nonconformance': {
            'category': RedFlagCategory.LEGAL,
            'description': 'Non-conforming use without grandfathering',
            'exception': 'Documented grandfathered status'
        }
    }
    
    def __init__(self, screening_input: ScreeningInput):
        """Initialize screener with property data."""
        self.input = screening_input
        
    def check_red_flags(self) -> Tuple[bool, List[Dict]]:
        """
        Check for true deal-killers.
        
        Returns:
            Tuple of (has_red_flags: bool, red_flag_details: List[Dict])
        """
        red_flags = []
        
        flag_attrs = [
            'structural_issues', 'environmental_contamination', 'severe_flood_zone',
            'code_violations_unresolved', 'high_crime_area', 'population_declining',
            'single_employer_risk', 'title_defects', 'active_litigation', 'zoning_nonconformance'
        ]
        
        for attr in flag_attrs:
            if getattr(self.input, attr, False):
                flag_info = self.RED_FLAG_DEFINITIONS[attr]
                red_flags.append({
                    'flag': attr,
                    'category': flag_info['category'].value,
                    'description': flag_info['description'],
                    'exception': flag_info['exception']
                })
        
        return (len(red_flags) > 0, red_flags)
    
    def calculate_risk_adjustments(self) -> Dict:
        """
        Calculate hurdle and contingency adjustments for risk factors.
        
        Returns:
            dict: Comprehensive risk analysis with hurdle/contingency adjustments
        """
        hurdle_adj = 0
        contingency_adj = 0
        factors = []
        
        # Property age adjustment
        age = self.input.property_age_years
        if age <= 20:
            age_hurdle, age_cont, age_level = 0, 0, RiskLevel.LOW
        elif age <= 30:
            age_hurdle, age_cont, age_level = 50, 2, RiskLevel.MODERATE
        elif age <= 40:
            age_hurdle, age_cont, age_level = 100, 3, RiskLevel.ELEVATED
        elif age <= 50:
            age_hurdle, age_cont, age_level = 150, 5, RiskLevel.HIGH
        else:
            age_hurdle, age_cont, age_level = 200, 7, RiskLevel.SEVERE
        
        hurdle_adj += age_hurdle
        contingency_adj += age_cont
        factors.append({
            'factor': 'property_age',
            'value': f'{age} years',
            'risk_level': age_level.value,
            'hurdle_adjustment_bps': age_hurdle,
            'contingency_adjustment_pct': age_cont,
            'note': 'NOT a disqualifier—requires appropriate renovation budget and returns'
        })
        
        # Occupancy adjustment
        occ = self.input.current_occupancy
        if occ >= 0.90:
            occ_hurdle, occ_level = 0, RiskLevel.LOW
        elif occ >= 0.85:
            occ_hurdle, occ_level = 50, RiskLevel.MODERATE
        elif occ >= 0.75:
            occ_hurdle, occ_level = 100, RiskLevel.ELEVATED
        elif occ >= 0.65:
            occ_hurdle, occ_level = 150, RiskLevel.HIGH
        else:
            occ_hurdle, occ_level = 200, RiskLevel.SEVERE
        
        hurdle_adj += occ_hurdle
        factors.append({
            'factor': 'occupancy',
            'value': f'{occ:.0%}',
            'risk_level': occ_level.value,
            'hurdle_adjustment_bps': occ_hurdle,
            'contingency_adjustment_pct': 0,
            'note': 'Low occupancy = distressed pricing opportunity if turnaround thesis valid'
        })
        
        # Property class adjustment
        prop_class = self.input.property_class.upper()
        class_adjustments = {
            'A': (0, RiskLevel.LOW),
            'B': (0, RiskLevel.LOW),
            'C': (50, RiskLevel.MODERATE),
            'D': (100, RiskLevel.ELEVATED)
        }
        class_hurdle, class_level = class_adjustments.get(prop_class, (50, RiskLevel.MODERATE))
        hurdle_adj += class_hurdle
        factors.append({
            'factor': 'property_class',
            'value': f'Class {prop_class}',
            'risk_level': class_level.value,
            'hurdle_adjustment_bps': class_hurdle,
            'contingency_adjustment_pct': 0,
            'note': 'Class C/D require realistic tenant profiles and expense assumptions'
        })
        
        # Deferred maintenance adjustment
        dm = self.input.deferred_maintenance_per_unit
        if dm < 2000:
            dm_cont, dm_hurdle, dm_level = 0, 0, RiskLevel.LOW
        elif dm < 5000:
            dm_cont, dm_hurdle, dm_level = 5, 0, RiskLevel.MODERATE
        elif dm < 10000:
            dm_cont, dm_hurdle, dm_level = 7, 50, RiskLevel.ELEVATED
        else:
            dm_cont, dm_hurdle, dm_level = 10, 100, RiskLevel.HIGH
        
        hurdle_adj += dm_hurdle
        contingency_adj += dm_cont
        factors.append({
            'factor': 'deferred_maintenance',
            'value': f'${dm:,.0f}/unit',
            'risk_level': dm_level.value,
            'hurdle_adjustment_bps': dm_hurdle,
            'contingency_adjustment_pct': dm_cont,
            'note': 'High deferred maintenance = value-add opportunity with proper budgeting'
        })
        
        # Submarket adjustment
        submarket = self.input.submarket_type.lower()
        submarket_adjustments = {
            'primary': (0, RiskLevel.LOW),
            'secondary': (50, RiskLevel.MODERATE),
            'tertiary': (100, RiskLevel.ELEVATED),
            'emerging': (75, RiskLevel.MODERATE)
        }
        sub_hurdle, sub_level = submarket_adjustments.get(submarket, (50, RiskLevel.MODERATE))
        hurdle_adj += sub_hurdle
        factors.append({
            'factor': 'submarket_type',
            'value': submarket.title(),
            'risk_level': sub_level.value,
            'hurdle_adjustment_bps': sub_hurdle,
            'contingency_adjustment_pct': 0,
            'note': 'Secondary/tertiary submarkets require conservative exit assumptions'
        })
        
        return {
            'total_hurdle_adjustment_bps': hurdle_adj,
            'total_contingency_adjustment_pct': contingency_adj,
            'risk_factors': factors,
            'overall_risk_level': self._calculate_overall_risk_level(hurdle_adj)
        }
    
    def _calculate_overall_risk_level(self, total_hurdle_adj: int) -> str:
        """Determine overall risk level based on total adjustments."""
        if total_hurdle_adj < 100:
            return RiskLevel.LOW.value
        elif total_hurdle_adj < 200:
            return RiskLevel.MODERATE.value
        elif total_hurdle_adj < 350:
            return RiskLevel.ELEVATED.value
        elif total_hurdle_adj < 500:
            return RiskLevel.HIGH.value
        else:
            return RiskLevel.SEVERE.value
    
    def screen(self) -> Dict:
        """
        Execute full screening process.
        
        Returns:
            dict: Comprehensive screening result with pass/fail and recommendation
        """
        # Check red flags first
        has_red_flags, red_flag_details = self.check_red_flags()
        
        if has_red_flags:
            return {
                'passed_screening': False,
                'recommendation': 'PASS',
                'reason': 'Red flag(s) identified that cannot be mitigated',
                'red_flags': red_flag_details,
                'risk_adjustments': None,
                'next_steps': [
                    'Review red flag exception criteria',
                    'If exception applies, document and proceed',
                    'If no exception, pass on deal'
                ]
            }
        
        # Calculate risk adjustments
        adjustments = self.calculate_risk_adjustments()
        
        # Determine recommendation based on aggregate risk
        total_adj = adjustments['total_hurdle_adjustment_bps']
        overall_risk = adjustments['overall_risk_level']
        
        if total_adj < 200:
            recommendation = 'PROCEED'
            next_steps = [
                'Proceed to full underwriting',
                f'Apply +{total_adj} bps to base hurdle',
                f"Add {adjustments['total_contingency_adjustment_pct']}% to capex contingency"
            ]
        elif total_adj < 400:
            recommendation = 'PROCEED_WITH_CAUTION'
            next_steps = [
                'Proceed to full underwriting with enhanced scrutiny',
                f'Apply +{total_adj} bps to base hurdle',
                f"Add {adjustments['total_contingency_adjustment_pct']}% to capex contingency",
                'Require detailed DD on elevated risk factors',
                'Stress test downside scenarios'
            ]
        elif total_adj < 600:
            recommendation = 'REQUEST_REPRICING'
            next_steps = [
                'Aggregate risk level may exceed acceptable threshold',
                f'Deal requires +{total_adj} bps hurdle adjustment',
                'Before full underwriting, discuss pricing expectations with broker',
                'Validate seller flexibility before investing in DD costs'
            ]
        else:
            recommendation = 'PASS'
            next_steps = [
                'Cumulative risk factors create excessive hurdle requirements',
                f'Deal would require +{total_adj} bps adjustment',
                'Unless seller accepts significant discount, pass',
                'Consider if specific risk factors can be contractually mitigated'
            ]
        
        return {
            'passed_screening': recommendation != 'PASS',
            'recommendation': recommendation,
            'reason': f"Overall risk level: {overall_risk}; Total hurdle adjustment: +{total_adj} bps",
            'red_flags': [],
            'risk_adjustments': adjustments,
            'next_steps': next_steps
        }

