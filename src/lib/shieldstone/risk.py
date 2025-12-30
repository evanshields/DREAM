"""
Execution Risk Scoring

Implements Section 8.2: Execution Risk Scoring
from the Shieldstone Technical Underwriting Manual.
"""

from typing import Dict


class ExecutionRiskAnalyzer:
    """
    Score execution risks across renovation, lease-up, financing, and operations.
    
    Execution risk receives 35% weight in overall risk assessment.
    """
    
    def assess_renovation_risk(
        self, 
        scope: str, 
        property_age: int, 
        contractor_experience: str
    ) -> Dict:
        """
        Assess renovation execution risk.
        
        Parameters:
        -----------
        scope : str
            'light', 'moderate', 'heavy', 'luxury'
        property_age : int
            Years since construction
        contractor_experience : str
            'proven', 'moderate', 'limited'
        
        Returns:
        --------
        dict : Risk assessment with rating
        """
        base_risk = {
            'light': 0,
            'moderate': 50,
            'heavy': 150,
            'luxury': 200
        }.get(scope.lower(), 0)
        
        # Age adjustment
        if property_age > 30:
            age_adjustment = 100
        elif property_age > 20:
            age_adjustment = 50
        else:
            age_adjustment = 0
        
        # Contractor adjustment
        contractor_adj = {
            'proven': 0,
            'moderate': 50,
            'limited': 150
        }.get(contractor_experience.lower(), 50)
        
        total_adjustment = base_risk + age_adjustment + contractor_adj
        
        if total_adjustment >= 300:
            rating = 'SEVERE'
        elif total_adjustment >= 200:
            rating = 'HIGH'
        elif total_adjustment >= 100:
            rating = 'MODERATE'
        else:
            rating = 'LOW'
        
        return {
            'renovation_scope': scope,
            'base_risk_bps': base_risk,
            'age_adjustment_bps': age_adjustment,
            'contractor_adjustment_bps': contractor_adj,
            'total_adjustment_bps': total_adjustment,
            'risk_rating': rating,
            'mitigation_required': total_adjustment >= 200
        }

