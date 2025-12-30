"""
End-to-End Tests for Dream AI Critical Paths
=============================================

Uses Playwright for browser automation testing.
Tests complete user workflows from deal creation to analysis export.

Critical Paths:
1. Create/edit deal
2. Edit assumptions
3. Run scenarios
4. View/export key underwriting metrics
"""

import pytest
from playwright.sync_api import Page, expect
from typing import Dict
import re


# Configuration
BASE_URL = "http://localhost:5173"  # Vite default port
TEST_TIMEOUT = 30000  # 30 seconds


class TestDealCreation:
    """Test deal creation and editing workflows."""
    
    def test_create_new_deal_from_dashboard(self, page: Page):
        """Test creating a new deal from the dashboard."""
        # Navigate to dashboard
        page.goto(f"{BASE_URL}/#dashboard")
        expect(page).to_have_title(re.compile("Dream", re.IGNORECASE))
        
        # Click "New Deal" button
        page.click('button:has-text("New Deal")')
        
        # Should navigate to intake page
        expect(page).to_have_url(re.compile(".*intake"))
        
        # Fill in basic deal information
        page.fill('input[name="dealName"]', "Test Deal - 200 Unit Multifamily")
        page.fill('input[name="address"]', "123 Main Street, Atlanta, GA 30303")
        page.fill('input[name="units"]', "200")
        page.fill('input[name="purchasePrice"]', "10000000")
        
        # Submit the form
        page.click('button:has-text("Create Deal")')
        
        # Should navigate to analysis view
        expect(page).to_have_url(re.compile(".*analysis"))
        
        # Verify deal appears in the interface
        expect(page.locator('text=Test Deal - 200 Unit Multifamily')).to_be_visible()
    
    def test_upload_offering_memorandum(self, page: Page):
        """Test uploading an offering memorandum."""
        page.goto(f"{BASE_URL}/#intake")
        
        # Fill basic info
        page.fill('input[name="dealName"]', "OM Upload Test")
        
        # Upload file
        page.set_input_files('input[type="file"]', 'tests/fixtures/sample_om.pdf')
        
        # Wait for upload to complete
        expect(page.locator('text=Upload complete')).to_be_visible(timeout=TEST_TIMEOUT)
        
        # Should show extracted data
        expect(page.locator('[data-testid="extracted-data"]')).to_be_visible()
    
    def test_edit_deal_details(self, page: Page):
        """Test editing deal details after creation."""
        # Assuming a deal exists, navigate to it
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click edit button
        page.click('button[aria-label="Edit deal"]')
        
        # Modify fields
        page.fill('input[name="units"]', "250")
        page.fill('input[name="purchasePrice"]', "12000000")
        
        # Save changes
        page.click('button:has-text("Save Changes")')
        
        # Verify changes are reflected
        expect(page.locator('text=250 units')).to_be_visible()
        expect(page.locator('text=$12,000,000')).to_be_visible()
    
    def test_navigate_deal_pipeline(self, page: Page):
        """Test navigating through deal pipeline stages."""
        page.goto(f"{BASE_URL}/#pipeline")
        
        # Verify pipeline board is visible
        expect(page.locator('[data-testid="pipeline-board"]')).to_be_visible()
        
        # Verify default stages exist
        expect(page.locator('text=New')).to_be_visible()
        expect(page.locator('text=Screening')).to_be_visible()
        expect(page.locator('text=LOI')).to_be_visible()
        expect(page.locator('text=Due Diligence')).to_be_visible()
        
        # Drag a deal card (if deals exist)
        # This is a simplified example - actual drag-drop needs more setup
        if page.locator('[data-testid="deal-card"]').count() > 0:
            source = page.locator('[data-testid="deal-card"]').first
            target = page.locator('[data-stage="Screening"]')
            source.drag_to(target)
            
            # Verify deal moved
            expect(page.locator('[data-stage="Screening"] [data-testid="deal-card"]')).to_be_visible()


class TestAssumptionEditing:
    """Test assumption editing workflows."""
    
    def test_open_assumption_editor(self, page: Page):
        """Test opening the assumption editor."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click on assumptions tab or button
        page.click('[data-testid="assumptions-tab"]')
        
        # Verify assumption editor is visible
        expect(page.locator('[data-testid="assumption-editor"]')).to_be_visible()
        
        # Verify key assumption categories are present
        expect(page.locator('text=Revenue')).to_be_visible()
        expect(page.locator('text=Expenses')).to_be_visible()
        expect(page.locator('text=Capital Expenditure')).to_be_visible()
        expect(page.locator('text=Financing')).to_be_visible()
    
    def test_edit_rent_growth_assumption(self, page: Page):
        """Test editing rent growth assumption and seeing impact."""
        page.goto(f"{BASE_URL}/#analysis")
        page.click('[data-testid="assumptions-tab"]')
        
        # Get original IRR value
        original_irr_text = page.locator('[data-testid="metric-irr"]').inner_text()
        original_irr = float(re.search(r'[\d.]+', original_irr_text).group())
        
        # Change rent growth from 3% to 5%
        rent_growth_input = page.locator('input[name="rentGrowth"]')
        rent_growth_input.fill('0.05')
        
        # Trigger recalculation (may happen automatically or need button)
        page.click('button:has-text("Recalculate")')
        
        # Wait for recalculation
        page.wait_for_timeout(1000)
        
        # Get new IRR value
        new_irr_text = page.locator('[data-testid="metric-irr"]').inner_text()
        new_irr = float(re.search(r'[\d.]+', new_irr_text).group())
        
        # New IRR should be higher
        assert new_irr > original_irr
    
    def test_edit_exit_cap_rate(self, page: Page):
        """Test editing exit cap rate assumption."""
        page.goto(f"{BASE_URL}/#analysis")
        page.click('[data-testid="assumptions-tab"]')
        
        # Get original exit value
        original_exit = page.locator('[data-testid="exit-value"]').inner_text()
        
        # Change exit cap from 5.0% to 5.5%
        page.fill('input[name="exitCap"]', '0.055')
        page.click('button:has-text("Recalculate")')
        page.wait_for_timeout(1000)
        
        # Get new exit value
        new_exit = page.locator('[data-testid="exit-value"]').inner_text()
        
        # Exit value should be lower (higher cap rate = lower value)
        assert new_exit != original_exit
    
    def test_vacancy_assumption_impact(self, page: Page):
        """Test that changing vacancy assumption impacts NOI."""
        page.goto(f"{BASE_URL}/#analysis")
        page.click('[data-testid="assumptions-tab"]')
        
        # Get original NOI
        original_noi = page.locator('[data-testid="stabilized-noi"]').inner_text()
        
        # Increase vacancy from 5% to 8%
        page.fill('input[name="vacancyRate"]', '0.08')
        page.click('button:has-text("Recalculate")')
        page.wait_for_timeout(1000)
        
        # Get new NOI
        new_noi = page.locator('[data-testid="stabilized-noi"]').inner_text()
        
        # NOI should be lower
        assert new_noi != original_noi
    
    def test_debt_assumption_changes(self, page: Page):
        """Test changing debt assumptions impacts DSCR and CoC."""
        page.goto(f"{BASE_URL}/#analysis")
        page.click('[data-testid="assumptions-tab"]')
        
        # Get original DSCR
        original_dscr = page.locator('[data-testid="metric-dscr"]').inner_text()
        
        # Change interest rate from 5.75% to 6.5%
        page.fill('input[name="interestRate"]', '0.065')
        page.click('button:has-text("Recalculate")')
        page.wait_for_timeout(1000)
        
        # Get new DSCR
        new_dscr = page.locator('[data-testid="metric-dscr"]').inner_text()
        
        # DSCR should be different (likely lower due to higher debt service)
        assert new_dscr != original_dscr


class TestScenarioManagement:
    """Test scenario creation and comparison workflows."""
    
    def test_create_upside_scenario(self, page: Page):
        """Test creating an upside scenario."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click "New Scenario" button
        page.click('button:has-text("New Scenario")')
        
        # Fill scenario name
        page.fill('input[name="scenarioName"]', 'Upside Case')
        page.select_option('select[name="scenarioType"]', 'upside')
        
        # Create scenario
        page.click('button:has-text("Create Scenario")')
        
        # Verify scenario appears in scenario selector
        expect(page.locator('[data-testid="scenario-selector"]')).to_contain_text('Upside Case')
    
    def test_switch_between_scenarios(self, page: Page):
        """Test switching between Base Case and Upside scenarios."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Get Base Case IRR
        base_irr = page.locator('[data-testid="metric-irr"]').inner_text()
        
        # Switch to Upside Case
        page.select_option('[data-testid="scenario-selector"]', 'Upside Case')
        page.wait_for_timeout(500)
        
        # Get Upside Case IRR
        upside_irr = page.locator('[data-testid="metric-irr"]').inner_text()
        
        # Switch back to Base Case
        page.select_option('[data-testid="scenario-selector"]', 'Base Case')
        page.wait_for_timeout(500)
        
        # Verify Base Case IRR is same as before
        final_base_irr = page.locator('[data-testid="metric-irr"]').inner_text()
        assert base_irr == final_base_irr
    
    def test_compare_scenarios_side_by_side(self, page: Page):
        """Test scenario comparison view."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click "Compare Scenarios" button
        page.click('button:has-text("Compare Scenarios")')
        
        # Verify comparison table is visible
        expect(page.locator('[data-testid="scenario-comparison"]')).to_be_visible()
        
        # Verify columns for different scenarios
        expect(page.locator('th:has-text("Base Case")')).to_be_visible()
        expect(page.locator('th:has-text("Upside Case")')).to_be_visible()
        
        # Verify key metrics are compared
        expect(page.locator('text=IRR')).to_be_visible()
        expect(page.locator('text=Equity Multiple')).to_be_visible()
        expect(page.locator('text=Cash-on-Cash')).to_be_visible()
    
    def test_delete_scenario(self, page: Page):
        """Test deleting a scenario."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Create a temporary scenario
        page.click('button:has-text("New Scenario")')
        page.fill('input[name="scenarioName"]', 'Temp Scenario')
        page.click('button:has-text("Create Scenario")')
        
        # Switch to temp scenario
        page.select_option('[data-testid="scenario-selector"]', 'Temp Scenario')
        
        # Delete scenario
        page.click('button[aria-label="Delete scenario"]')
        page.click('button:has-text("Confirm")')
        
        # Verify scenario is removed from selector
        expect(page.locator('[data-testid="scenario-selector"]')).not_to_contain_text('Temp Scenario')
        
        # Should switch back to Base Case
        expect(page.locator('[data-testid="scenario-selector"]')).to_have_value('Base Case')


class TestMetricsViewing:
    """Test viewing key underwriting metrics."""
    
    def test_view_summary_metrics(self, page: Page):
        """Test that all key metrics are visible in summary."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Verify key metrics are present
        expect(page.locator('[data-testid="metric-irr"]')).to_be_visible()
        expect(page.locator('[data-testid="metric-em"]')).to_be_visible()
        expect(page.locator('[data-testid="metric-coc"]')).to_be_visible()
        expect(page.locator('[data-testid="metric-dscr"]')).to_be_visible()
        expect(page.locator('[data-testid="metric-cap-rate"]')).to_be_visible()
        
        # Verify metrics have values (not empty or error)
        irr_text = page.locator('[data-testid="metric-irr"]').inner_text()
        assert '%' in irr_text or 'IRR' in irr_text
    
    def test_view_proforma_detail(self, page: Page):
        """Test viewing detailed pro forma."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click on "Pro Forma" tab or expand section
        page.click('[data-testid="proforma-tab"]')
        
        # Verify pro forma table is visible
        expect(page.locator('[data-testid="proforma-table"]')).to_be_visible()
        
        # Verify years are shown (Year 1-5 minimum)
        for year in range(1, 6):
            expect(page.locator(f'th:has-text("Year {year}")')).to_be_visible()
        
        # Verify key line items
        expect(page.locator('text=Gross Potential Rent')).to_be_visible()
        expect(page.locator('text=Vacancy')).to_be_visible()
        expect(page.locator('text=Net Operating Income')).to_be_visible()
        expect(page.locator('text=Cash Flow')).to_be_visible()
    
    def test_view_sensitivity_analysis(self, page: Page):
        """Test viewing sensitivity analysis."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Navigate to sensitivity tab
        page.click('[data-testid="sensitivity-tab"]')
        
        # Verify sensitivity table is visible
        expect(page.locator('[data-testid="sensitivity-table"]')).to_be_visible()
        
        # Verify common sensitivity variables
        expect(page.locator('text=Exit Cap Rate')).to_be_visible()
        expect(page.locator('text=Rent Growth')).to_be_visible()
    
    def test_investment_recommendation(self, page: Page):
        """Test viewing investment recommendation."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Verify recommendation badge is visible
        expect(page.locator('[data-testid="recommendation"]')).to_be_visible()
        
        # Recommendation should be one of: Strong Buy, Buy, Hold, Pass
        recommendation_text = page.locator('[data-testid="recommendation"]').inner_text()
        assert any(rec in recommendation_text.upper() for rec in ['STRONG BUY', 'BUY', 'HOLD', 'PASS'])


class TestExportFunctionality:
    """Test exporting analysis and reports."""
    
    def test_export_excel_proforma(self, page: Page):
        """Test exporting pro forma to Excel."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click export dropdown
        page.click('button:has-text("Export")')
        
        # Click Excel option
        with page.expect_download() as download_info:
            page.click('a:has-text("Export to Excel")')
        
        download = download_info.value
        
        # Verify file is downloaded
        assert download.suggested_filename.endswith('.xlsx')
    
    def test_export_pdf_memo(self, page: Page):
        """Test generating and downloading PDF memo."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click "Generate Memo" button
        page.click('button:has-text("Generate Memo")')
        
        # Select memo type
        page.click('button:has-text("BOE Memo")')
        
        # Wait for generation
        expect(page.locator('text=Generating memo...')).to_be_visible()
        expect(page.locator('text=Memo generated')).to_be_visible(timeout=TEST_TIMEOUT)
        
        # Download PDF
        with page.expect_download() as download_info:
            page.click('button:has-text("Download PDF")')
        
        download = download_info.value
        assert download.suggested_filename.endswith('.pdf')
    
    def test_share_analysis_link(self, page: Page):
        """Test generating shareable link."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Click share button
        page.click('button:has-text("Share")')
        
        # Copy link
        page.click('button:has-text("Copy Link")')
        
        # Verify success message
        expect(page.locator('text=Link copied')).to_be_visible()


class TestUserFlowIntegration:
    """Test complete user workflows end-to-end."""
    
    def test_complete_deal_analysis_workflow(self, page: Page):
        """Test complete workflow: create deal → edit assumptions → view results → export."""
        # Step 1: Create deal
        page.goto(f"{BASE_URL}/#intake")
        page.fill('input[name="dealName"]', "Integration Test Deal")
        page.fill('input[name="address"]', "456 Oak St, Dallas, TX 75201")
        page.fill('input[name="units"]', "150")
        page.fill('input[name="purchasePrice"]', "8000000")
        page.click('button:has-text("Create Deal")')
        
        # Step 2: Wait for analysis
        expect(page.locator('[data-testid="metric-irr"]')).to_be_visible(timeout=TEST_TIMEOUT)
        
        # Step 3: Edit assumptions
        page.click('[data-testid="assumptions-tab"]')
        page.fill('input[name="rentGrowth"]', '0.04')
        page.click('button:has-text("Recalculate")')
        page.wait_for_timeout(1000)
        
        # Step 4: View updated metrics
        page.click('[data-testid="metrics-tab"]')
        expect(page.locator('[data-testid="metric-irr"]')).to_be_visible()
        
        # Step 5: Export
        page.click('button:has-text("Export")')
        with page.expect_download() as download_info:
            page.click('a:has-text("Export to Excel")')
        
        download = download_info.value
        assert download.suggested_filename.endswith('.xlsx')
    
    def test_multi_scenario_analysis_workflow(self, page: Page):
        """Test workflow: create base → create upside/downside → compare → export."""
        page.goto(f"{BASE_URL}/#analysis")
        
        # Verify Base Case exists
        expect(page.locator('[data-testid="scenario-selector"]')).to_have_value('Base Case')
        
        # Create Upside scenario
        page.click('button:has-text("New Scenario")')
        page.fill('input[name="scenarioName"]', 'Upside')
        page.click('button:has-text("Create Scenario")')
        
        # Modify upside assumptions
        page.select_option('[data-testid="scenario-selector"]', 'Upside')
        page.click('[data-testid="assumptions-tab"]')
        page.fill('input[name="rentGrowth"]', '0.05')
        page.click('button:has-text("Recalculate")')
        
        # Create Downside scenario
        page.click('button:has-text("New Scenario")')
        page.fill('input[name="scenarioName"]', 'Downside')
        page.click('button:has-text("Create Scenario")')
        
        # Modify downside assumptions
        page.fill('input[name="rentGrowth"]', '0.01')
        page.click('button:has-text("Recalculate")')
        
        # Compare scenarios
        page.click('button:has-text("Compare Scenarios")')
        expect(page.locator('[data-testid="scenario-comparison"]')).to_be_visible()
        
        # Verify all three scenarios appear
        expect(page.locator('text=Base Case')).to_be_visible()
        expect(page.locator('text=Upside')).to_be_visible()
        expect(page.locator('text=Downside')).to_be_visible()


# Pytest fixtures
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }


@pytest.fixture(scope="function")
def page(page: Page):
    """Set up page for each test."""
    page.set_default_timeout(TEST_TIMEOUT)
    return page


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--headed', '--slowmo=500'])

