"""
Integration Tests for Scenario Switching
==========================================

Tests for scenario creation, management, and switching functionality.
Ensures that assumption changes correctly propagate through all calculations.
"""

import pytest
from typing import Dict, List
from copy import deepcopy


# Mock scenario manager for testing
class ScenarioManager:
    """Manages multiple scenarios for a deal."""
    
    def __init__(self, base_assumptions: Dict):
        self.base_assumptions = base_assumptions
        self.scenarios = {
            'Base Case': deepcopy(base_assumptions)
        }
        self.active_scenario = 'Base Case'
    
    def create_scenario(self, name: str, assumptions: Dict = None):
        """Create a new scenario."""
        if assumptions is None:
            # Clone base case
            assumptions = deepcopy(self.base_assumptions)
        
        self.scenarios[name] = assumptions
        return name
    
    def switch_scenario(self, name: str):
        """Switch to a different scenario."""
        if name not in self.scenarios:
            raise ValueError(f"Scenario '{name}' does not exist")
        
        self.active_scenario = name
        return self.scenarios[name]
    
    def get_active_scenario(self) -> Dict:
        """Get the currently active scenario."""
        return self.scenarios[self.active_scenario]
    
    def update_assumption(self, path: str, value):
        """Update an assumption in the active scenario."""
        keys = path.split('.')
        scenario = self.scenarios[self.active_scenario]
        
        # Navigate to the nested key
        current = scenario
        for key in keys[:-1]:
            current = current[key]
        
        # Update the final key
        current[keys[-1]] = value
    
    def list_scenarios(self) -> List[str]:
        """List all scenario names."""
        return list(self.scenarios.keys())
    
    def delete_scenario(self, name: str):
        """Delete a scenario."""
        if name == 'Base Case':
            raise ValueError("Cannot delete Base Case scenario")
        
        if name not in self.scenarios:
            raise ValueError(f"Scenario '{name}' does not exist")
        
        del self.scenarios[name]
        
        # Switch to Base Case if deleted scenario was active
        if self.active_scenario == name:
            self.active_scenario = 'Base Case'


class TestScenarioCreation:
    """Test scenario creation and management."""
    
    def test_create_base_scenario(self):
        """Test that base scenario is created automatically."""
        base_assumptions = {
            'purchase_price': 10_000_000,
            'rent_growth': 0.03,
            'exit_cap': 0.05
        }
        
        manager = ScenarioManager(base_assumptions)
        
        assert 'Base Case' in manager.list_scenarios()
        assert manager.active_scenario == 'Base Case'
        assert manager.get_active_scenario() == base_assumptions
    
    def test_create_new_scenario(self):
        """Test creating a new scenario."""
        base_assumptions = {
            'purchase_price': 10_000_000,
            'rent_growth': 0.03,
            'exit_cap': 0.05
        }
        
        manager = ScenarioManager(base_assumptions)
        
        # Create upside scenario
        upside_name = manager.create_scenario('Upside Case')
        
        assert upside_name == 'Upside Case'
        assert 'Upside Case' in manager.list_scenarios()
        assert len(manager.list_scenarios()) == 2
    
    def test_create_scenario_with_custom_assumptions(self):
        """Test creating scenario with custom assumptions."""
        base_assumptions = {
            'purchase_price': 10_000_000,
            'rent_growth': 0.03,
            'exit_cap': 0.05
        }
        
        manager = ScenarioManager(base_assumptions)
        
        # Create downside scenario with different assumptions
        downside_assumptions = {
            'purchase_price': 10_000_000,
            'rent_growth': 0.01,  # Lower growth
            'exit_cap': 0.06      # Higher cap rate
        }
        
        manager.create_scenario('Downside Case', downside_assumptions)
        manager.switch_scenario('Downside Case')
        
        active = manager.get_active_scenario()
        assert active['rent_growth'] == 0.01
        assert active['exit_cap'] == 0.06
    
    def test_scenarios_are_independent(self):
        """Test that modifying one scenario doesn't affect others."""
        base_assumptions = {
            'purchase_price': 10_000_000,
            'rent_growth': 0.03
        }
        
        manager = ScenarioManager(base_assumptions)
        manager.create_scenario('Upside Case')
        
        # Modify upside scenario
        manager.switch_scenario('Upside Case')
        manager.update_assumption('rent_growth', 0.05)
        
        # Check that base case is unchanged
        manager.switch_scenario('Base Case')
        assert manager.get_active_scenario()['rent_growth'] == 0.03
        
        # Check that upside case has new value
        manager.switch_scenario('Upside Case')
        assert manager.get_active_scenario()['rent_growth'] == 0.05


class TestScenarioSwitching:
    """Test switching between scenarios."""
    
    def test_switch_to_existing_scenario(self):
        """Test switching to an existing scenario."""
        base_assumptions = {'rent_growth': 0.03}
        manager = ScenarioManager(base_assumptions)
        
        manager.create_scenario('Upside Case')
        manager.switch_scenario('Upside Case')
        manager.update_assumption('rent_growth', 0.05)
        
        # Switch back to base
        manager.switch_scenario('Base Case')
        assert manager.get_active_scenario()['rent_growth'] == 0.03
        
        # Switch to upside
        manager.switch_scenario('Upside Case')
        assert manager.get_active_scenario()['rent_growth'] == 0.05
    
    def test_switch_to_nonexistent_scenario(self):
        """Test that switching to nonexistent scenario raises error."""
        manager = ScenarioManager({'rent_growth': 0.03})
        
        with pytest.raises(ValueError, match="does not exist"):
            manager.switch_scenario('Nonexistent Scenario')
    
    def test_active_scenario_tracking(self):
        """Test that active scenario is tracked correctly."""
        manager = ScenarioManager({'rent_growth': 0.03})
        manager.create_scenario('Upside Case')
        manager.create_scenario('Downside Case')
        
        assert manager.active_scenario == 'Base Case'
        
        manager.switch_scenario('Upside Case')
        assert manager.active_scenario == 'Upside Case'
        
        manager.switch_scenario('Downside Case')
        assert manager.active_scenario == 'Downside Case'


class TestAssumptionPropagation:
    """Test that assumption changes propagate through calculations."""
    
    def test_rent_growth_changes_propagate(self):
        """Test that changing rent growth updates all downstream calculations."""
        # Simplified calculation pipeline
        def calculate_returns(assumptions: Dict) -> Dict:
            """Mock calculation function."""
            year_1_noi = 800_000
            rent_growth = assumptions['rent_growth']
            
            # Project NOI over 5 years
            noi_projection = []
            for year in range(5):
                noi = year_1_noi * (1 + rent_growth)**year
                noi_projection.append(noi)
            
            # Simple exit value calculation
            exit_cap = assumptions['exit_cap']
            exit_value = noi_projection[-1] / exit_cap
            
            return {
                'noi_projection': noi_projection,
                'exit_value': exit_value,
                'year_5_noi': noi_projection[-1]
            }
        
        # Base case
        base = {'rent_growth': 0.03, 'exit_cap': 0.05}
        base_results = calculate_returns(base)
        
        # Upside case with higher rent growth
        upside = {'rent_growth': 0.05, 'exit_cap': 0.05}
        upside_results = calculate_returns(upside)
        
        # Upside should have higher Year 5 NOI
        assert upside_results['year_5_noi'] > base_results['year_5_noi']
        
        # Upside should have higher exit value
        assert upside_results['exit_value'] > base_results['exit_value']
    
    def test_exit_cap_changes_propagate(self):
        """Test that changing exit cap rate updates exit value."""
        def calculate_exit_value(stabilized_noi: float, exit_cap: float) -> float:
            return stabilized_noi / exit_cap
        
        stabilized_noi = 1_000_000
        
        # Lower cap rate = higher value
        base_exit = calculate_exit_value(stabilized_noi, 0.05)
        upside_exit = calculate_exit_value(stabilized_noi, 0.045)
        downside_exit = calculate_exit_value(stabilized_noi, 0.055)
        
        assert upside_exit > base_exit > downside_exit
        assert base_exit == 20_000_000
        assert upside_exit == pytest.approx(22_222_222, rel=0.01)
        assert downside_exit == pytest.approx(18_181_818, rel=0.01)
    
    def test_vacancy_changes_propagate(self):
        """Test that changing vacancy assumption updates NOI."""
        def calculate_noi(gross_rent: float, vacancy_rate: float, opex: float) -> float:
            egi = gross_rent * (1 - vacancy_rate)
            return egi - opex
        
        gross_rent = 1_500_000
        opex = 600_000
        
        # Different vacancy scenarios
        base_noi = calculate_noi(gross_rent, 0.05, opex)
        upside_noi = calculate_noi(gross_rent, 0.03, opex)
        downside_noi = calculate_noi(gross_rent, 0.08, opex)
        
        assert upside_noi > base_noi > downside_noi
        assert base_noi == 825_000
        assert upside_noi == 855_000
        assert downside_noi == 780_000


class TestScenarioComparison:
    """Test comparing multiple scenarios side-by-side."""
    
    def test_compare_two_scenarios(self):
        """Test comparing Base Case vs Upside Case."""
        base_assumptions = {
            'rent_growth': 0.03,
            'exit_cap': 0.05,
            'vacancy_rate': 0.05
        }
        
        manager = ScenarioManager(base_assumptions)
        
        # Create upside scenario
        upside_assumptions = {
            'rent_growth': 0.05,
            'exit_cap': 0.045,
            'vacancy_rate': 0.03
        }
        manager.create_scenario('Upside Case', upside_assumptions)
        
        # Compare key metrics
        base = manager.scenarios['Base Case']
        upside = manager.scenarios['Upside Case']
        
        comparison = {
            'rent_growth': {
                'base': base['rent_growth'],
                'upside': upside['rent_growth'],
                'delta': upside['rent_growth'] - base['rent_growth']
            },
            'exit_cap': {
                'base': base['exit_cap'],
                'upside': upside['exit_cap'],
                'delta': upside['exit_cap'] - base['exit_cap']
            },
            'vacancy_rate': {
                'base': base['vacancy_rate'],
                'upside': upside['vacancy_rate'],
                'delta': upside['vacancy_rate'] - base['vacancy_rate']
            }
        }
        
        # Verify deltas
        assert comparison['rent_growth']['delta'] == 0.02
        assert comparison['exit_cap']['delta'] == -0.005
        assert comparison['vacancy_rate']['delta'] == -0.02
    
    def test_three_scenario_comparison(self):
        """Test comparing Base, Upside, and Downside scenarios."""
        base_assumptions = {
            'purchase_price': 10_000_000,
            'rent_growth': 0.03,
            'exit_cap': 0.05
        }
        
        manager = ScenarioManager(base_assumptions)
        
        # Create upside and downside
        upside = {'purchase_price': 10_000_000, 'rent_growth': 0.05, 'exit_cap': 0.045}
        downside = {'purchase_price': 10_000_000, 'rent_growth': 0.01, 'exit_cap': 0.06}
        
        manager.create_scenario('Upside Case', upside)
        manager.create_scenario('Downside Case', downside)
        
        # Verify all scenarios exist
        scenarios = manager.list_scenarios()
        assert len(scenarios) == 3
        assert 'Base Case' in scenarios
        assert 'Upside Case' in scenarios
        assert 'Downside Case' in scenarios


class TestScenarioCalculationIntegrity:
    """Test that calculations remain consistent across scenario switches."""
    
    def test_calculation_consistency(self):
        """Test that switching scenarios and back yields same results."""
        base_assumptions = {
            'noi': 800_000,
            'exit_cap': 0.05
        }
        
        manager = ScenarioManager(base_assumptions)
        
        # Calculate base case
        def calc_exit_value(assumptions):
            return assumptions['noi'] / assumptions['exit_cap']
        
        base_exit_1 = calc_exit_value(manager.get_active_scenario())
        
        # Create and switch to upside
        upside = {'noi': 900_000, 'exit_cap': 0.045}
        manager.create_scenario('Upside Case', upside)
        manager.switch_scenario('Upside Case')
        
        upside_exit = calc_exit_value(manager.get_active_scenario())
        
        # Switch back to base
        manager.switch_scenario('Base Case')
        base_exit_2 = calc_exit_value(manager.get_active_scenario())
        
        # Base case should be identical both times
        assert base_exit_1 == base_exit_2 == 16_000_000
        assert upside_exit == 20_000_000
    
    def test_assumption_modification_isolation(self):
        """Test that modifying assumptions in one scenario doesn't affect calculations in another."""
        manager = ScenarioManager({'value': 100})
        manager.create_scenario('Scenario A')
        manager.create_scenario('Scenario B')
        
        # Modify Scenario A
        manager.switch_scenario('Scenario A')
        manager.update_assumption('value', 200)
        
        # Modify Scenario B
        manager.switch_scenario('Scenario B')
        manager.update_assumption('value', 300)
        
        # Verify isolation
        assert manager.scenarios['Base Case']['value'] == 100
        assert manager.scenarios['Scenario A']['value'] == 200
        assert manager.scenarios['Scenario B']['value'] == 300


class TestScenarioDeletion:
    """Test scenario deletion functionality."""
    
    def test_delete_scenario(self):
        """Test deleting a scenario."""
        manager = ScenarioManager({'value': 100})
        manager.create_scenario('Test Scenario')
        
        assert 'Test Scenario' in manager.list_scenarios()
        
        manager.delete_scenario('Test Scenario')
        
        assert 'Test Scenario' not in manager.list_scenarios()
    
    def test_cannot_delete_base_case(self):
        """Test that Base Case cannot be deleted."""
        manager = ScenarioManager({'value': 100})
        
        with pytest.raises(ValueError, match="Cannot delete Base Case"):
            manager.delete_scenario('Base Case')
    
    def test_delete_active_scenario_switches_to_base(self):
        """Test that deleting active scenario switches to Base Case."""
        manager = ScenarioManager({'value': 100})
        manager.create_scenario('Test Scenario')
        manager.switch_scenario('Test Scenario')
        
        assert manager.active_scenario == 'Test Scenario'
        
        manager.delete_scenario('Test Scenario')
        
        assert manager.active_scenario == 'Base Case'


class TestNestedAssumptions:
    """Test handling of nested assumption structures."""
    
    def test_update_nested_assumption(self):
        """Test updating deeply nested assumptions."""
        base_assumptions = {
            'revenue': {
                'rent_growth': 0.03,
                'vacancy': 0.05
            },
            'expenses': {
                'growth_rate': 0.02
            }
        }
        
        manager = ScenarioManager(base_assumptions)
        
        # Update nested value
        manager.update_assumption('revenue.rent_growth', 0.05)
        
        assert manager.get_active_scenario()['revenue']['rent_growth'] == 0.05
        
        # Verify other values unchanged
        assert manager.get_active_scenario()['revenue']['vacancy'] == 0.05
        assert manager.get_active_scenario()['expenses']['growth_rate'] == 0.02


# Pytest fixtures
@pytest.fixture
def sample_manager():
    """Create a sample scenario manager for testing."""
    base = {
        'purchase_price': 10_000_000,
        'rent_growth': 0.03,
        'exit_cap': 0.05,
        'vacancy_rate': 0.05,
        'opex_growth': 0.02
    }
    return ScenarioManager(base)


@pytest.fixture
def three_scenario_manager(sample_manager):
    """Create a manager with three scenarios."""
    upside = {
        'purchase_price': 10_000_000,
        'rent_growth': 0.05,
        'exit_cap': 0.045,
        'vacancy_rate': 0.03,
        'opex_growth': 0.02
    }
    
    downside = {
        'purchase_price': 10_000_000,
        'rent_growth': 0.01,
        'exit_cap': 0.06,
        'vacancy_rate': 0.08,
        'opex_growth': 0.03
    }
    
    sample_manager.create_scenario('Upside Case', upside)
    sample_manager.create_scenario('Downside Case', downside)
    
    return sample_manager


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

