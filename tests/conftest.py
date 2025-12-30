"""
Pytest Configuration and Shared Fixtures
=========================================

Shared test configuration, fixtures, and utilities.
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Dict, Generator

# Add src to Python path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (component interaction)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full user workflows)"
    )
    config.addinivalue_line(
        "markers", "financial: Financial calculation tests"
    )
    config.addinivalue_line(
        "markers", "scenario: Scenario management tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take >5 seconds"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on location."""
    for item in items:
        # Auto-mark based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
        
        # Auto-mark based on test name
        if "financial" in item.name or "calc" in item.name:
            item.add_marker(pytest.mark.financial)
        if "scenario" in item.name:
            item.add_marker(pytest.mark.scenario)


# ============================================================================
# Shared Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture(scope="session")
def sample_deal_data() -> Dict:
    """Sample deal data for testing."""
    return {
        'id': 'test-deal-001',
        'name': 'Test Deal - 200 Units',
        'address': '123 Main Street',
        'city': 'Atlanta',
        'state': 'GA',
        'zip': '30303',
        'units': 200,
        'buildings': 8,
        'year_built': 2010,
        'purchase_price': 10_000_000,
        'price_per_unit': 50_000,
        'gross_potential_rent': 1_500_000,
        'current_occupancy': 0.90,
        'property_class': 'B',
        'submarket': 'Midtown'
    }


@pytest.fixture(scope="session")
def sample_financial_data() -> Dict:
    """Sample financial data for testing."""
    return {
        'gross_potential_rent': 1_500_000,
        'vacancy_rate': 0.05,
        'vacancy_loss': 75_000,
        'other_income': 80_000,
        'effective_gross_income': 1_505_000,
        'operating_expenses': 600_000,
        'noi': 905_000,
        'total_capex': 2_500_000,
        'interest_rate': 0.0575,
        'hold_period': 5
    }


@pytest.fixture(scope="session")
def sample_assumptions() -> Dict:
    """Sample assumptions for testing."""
    return {
        'acquisition': {
            'purchase_price': 10_000_000,
            'closing_costs': 0.03,
            'acquisition_fee': 0.01
        },
        'financing': {
            'ltv': 0.65,
            'interest_rate': 0.0575,
            'io_period_months': 30,
            'amortization_years': 30
        },
        'revenue': {
            'rent_growth': 0.03,
            'other_income_growth': 0.02,
            'vacancy_rate': 0.05,
            'concessions': 0.02
        },
        'expenses': {
            'growth_rate': 0.02,
            'management_fee': 0.03
        },
        'capex': {
            'total_budget': 2_500_000,
            'renovation_months': 18,
            'reserves_per_unit': 300
        },
        'exit': {
            'hold_period_years': 5,
            'exit_cap': 0.05,
            'selling_costs': 0.02
        }
    }


@pytest.fixture(scope="function")
def sample_cash_flows() -> Dict:
    """Sample cash flow data for IRR testing."""
    return {
        'total_equity': 4_000_000,
        'annual_cash_flows': [200_000, 250_000, 300_000, 350_000, 400_000],
        'exit_proceeds': 3_800_000
    }


@pytest.fixture(scope="function")
def base_scenario_assumptions() -> Dict:
    """Base case scenario assumptions."""
    return {
        'name': 'Base Case',
        'purchase_price': 10_000_000,
        'rent_growth': 0.03,
        'exit_cap': 0.05,
        'vacancy_rate': 0.05,
        'opex_growth': 0.02,
        'interest_rate': 0.0575
    }


@pytest.fixture(scope="function")
def upside_scenario_assumptions() -> Dict:
    """Upside case scenario assumptions."""
    return {
        'name': 'Upside Case',
        'purchase_price': 10_000_000,
        'rent_growth': 0.05,
        'exit_cap': 0.045,
        'vacancy_rate': 0.03,
        'opex_growth': 0.02,
        'interest_rate': 0.055
    }


@pytest.fixture(scope="function")
def downside_scenario_assumptions() -> Dict:
    """Downside case scenario assumptions."""
    return {
        'name': 'Downside Case',
        'purchase_price': 10_000_000,
        'rent_growth': 0.01,
        'exit_cap': 0.06,
        'vacancy_rate': 0.08,
        'opex_growth': 0.03,
        'interest_rate': 0.065
    }


# ============================================================================
# Helper Functions
# ============================================================================

def assert_almost_equal(actual: float, expected: float, tolerance: float = 0.01):
    """Assert that two floats are approximately equal within tolerance."""
    assert abs(actual - expected) <= tolerance, \
        f"Expected {expected}, got {actual} (tolerance: {tolerance})"


def assert_percentage_difference(actual: float, expected: float, max_diff_pct: float = 1.0):
    """Assert that actual is within a percentage of expected."""
    diff_pct = abs((actual - expected) / expected) * 100
    assert diff_pct <= max_diff_pct, \
        f"Expected {expected}, got {actual} ({diff_pct:.2f}% difference, max: {max_diff_pct}%)"


# ============================================================================
# Playwright Configuration (for E2E tests)
# ============================================================================

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: Dict, tmpdir_factory):
    """Configure browser context for E2E tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Dream-AI-Test-Suite",
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "record_video_dir": str(tmpdir_factory.mktemp("videos")),
        "record_video_size": {"width": 1920, "height": 1080}
    }


@pytest.fixture(scope="function", autouse=True)
def slow_down_playwright(page):
    """Slow down Playwright actions for better observability in headed mode."""
    # Only slow down if running in headed mode
    if os.getenv("HEADED", "").lower() in ("1", "true", "yes"):
        page.set_default_timeout(10000)
        page.context.set_default_navigation_timeout(10000)
    else:
        page.set_default_timeout(30000)


# ============================================================================
# Performance Benchmarking
# ============================================================================

@pytest.fixture
def performance_tracker():
    """Track performance metrics for benchmarking."""
    import time
    
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.duration_ms = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            self.duration_ms = (self.end_time - self.start_time) * 1000
            return self.duration_ms
        
        def assert_faster_than(self, threshold_ms: float):
            assert self.duration_ms < threshold_ms, \
                f"Operation took {self.duration_ms:.2f}ms, expected <{threshold_ms}ms"
    
    return PerformanceTracker()


# ============================================================================
# Cleanup Hooks
# ============================================================================

@pytest.fixture(autouse=True)
def reset_state():
    """Reset application state between tests."""
    # Placeholder for any state reset logic
    yield
    # Cleanup after test


# ============================================================================
# Custom Assertions
# ============================================================================

class CustomAssertions:
    """Custom assertion helpers for financial tests."""
    
    @staticmethod
    def assert_valid_irr(irr: float):
        """Assert IRR is valid and reasonable."""
        assert -1.0 <= irr <= 5.0, f"IRR {irr:.2%} is outside reasonable range (-100% to 500%)"
    
    @staticmethod
    def assert_valid_dscr(dscr: float):
        """Assert DSCR is valid."""
        assert dscr > 0, f"DSCR must be positive, got {dscr}"
        assert dscr < 10, f"DSCR {dscr:.2f} is unreasonably high"
    
    @staticmethod
    def assert_valid_equity_multiple(em: float):
        """Assert Equity Multiple is valid."""
        assert em > 0, f"Equity Multiple must be positive, got {em}"
        assert em < 10, f"Equity Multiple {em:.2f}x is unreasonably high"
    
    @staticmethod
    def assert_sources_equal_uses(sources: float, uses: float, tolerance: float = 1.0):
        """Assert sources and uses balance."""
        assert abs(sources - uses) < tolerance, \
            f"Sources ({sources:,.2f}) do not equal Uses ({uses:,.2f})"


@pytest.fixture
def custom_assertions():
    """Provide custom assertions fixture."""
    return CustomAssertions()

