"""
Deal Screening Criteria

Implements Section 1.2: Deal Screening Criteria
from the Shieldstone Technical Underwriting Manual.
"""

from typing import Dict, List
from .constants import (
    MIN_UNITS, MAX_PROPERTY_AGE, MIN_OCCUPANCY, MAX_CRIME_MULTIPLIER
)


class DealScreener:
    """
    Screen deals against hard disqualifiers before deep underwriting.
    
    Purpose: Avoid wasting time on fundamentally flawed opportunities.
    """
    
    def __init__(self, property_details: Dict):
        """
        Parameters:
        -----------
        property_details : dict
            - unit_count: int
            - property_age: int  
            - occupancy: float (0-1)
            - declining_market: bool
            - high_crime_area: bool
            - structural_issues: bool
            - environmental_contamination: bool
            - severe_flood_risk: bool (FEMA Zone A/V)
        """
        self.details = property_details
        self.disqualifiers: List[str] = []
        
    def screen(self) -> Dict:
        """
        Run all screening tests.
        
        Returns:
        --------
        dict : Pass/fail decision with reasons
        """
        checks = [
            self._check_unit_count(),
            self._check_property_age(),
            self._check_occupancy(),
            self._check_location(),
            self._check_structural_condition(),
            self._check_environmental()
        ]
        
        passed = all(checks)
        
        return {
            'passed': passed,
            'disqualifiers': self.disqualifiers,
            'recommendation': 'PROCEED TO UNDERWRITING' if passed else 'PASS - DISQUALIFIED',
            'reason': '; '.join(self.disqualifiers) if not passed else 'All checks passed'
        }
    
    def _check_unit_count(self) -> bool:
        """Minimum 50 units for operational efficiency."""
        units = self.details.get('unit_count', 0)
        if units < MIN_UNITS:
            self.disqualifiers.append(
                f"Unit count {units} below minimum {MIN_UNITS}"
            )
            return False
        return True
    
    def _check_property_age(self) -> bool:
        """Maximum 40 years (too much deferred maintenance risk beyond this)."""
        age = self.details.get('property_age', 0)
        if age > MAX_PROPERTY_AGE:
            self.disqualifiers.append(
                f"Property age {age} years exceeds maximum {MAX_PROPERTY_AGE}"
            )
            return False
        return True
    
    def _check_occupancy(self) -> bool:
        """Minimum 70% occupancy (lower indicates severe operational problems)."""
        occupancy = self.details.get('occupancy', 0)
        if occupancy < MIN_OCCUPANCY:
            self.disqualifiers.append(
                f"Occupancy {occupancy:.0%} below minimum {MIN_OCCUPANCY:.0%}"
            )
            return False
        return True
    
    def _check_location(self) -> bool:
        """No declining markets or high-crime areas."""
        if self.details.get('declining_market', False):
            self.disqualifiers.append(
                "Located in declining market (negative population/employment trends)"
            )
            return False
        
        if self.details.get('high_crime_area', False):
            self.disqualifiers.append(
                f"High-crime area (violent crime >{MAX_CRIME_MULTIPLIER}x national average)"
            )
            return False
        
        return True
    
    def _check_structural_condition(self) -> bool:
        """No major structural defects."""
        if self.details.get('structural_issues', False):
            self.disqualifiers.append(
                "Major structural issues identified"
            )
            return False
        return True
    
    def _check_environmental(self) -> bool:
        """No environmental contamination or severe flood risk."""
        if self.details.get('environmental_contamination', False):
            self.disqualifiers.append(
                "Known environmental contamination present"
            )
            return False
        
        if self.details.get('severe_flood_risk', False):
            self.disqualifiers.append(
                "FEMA flood zone A/V (severe flood risk)"
            )
            return False
        
        return True

