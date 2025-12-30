-- DREAM AI - Row Level Security (RLS) Setup
-- Enables RLS and creates policies for all tables
-- Version: 1.0
-- Date: December 2025

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ============================================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE rent_roll ENABLE ROW LEVEL SECURITY;
ALTER TABLE unit_mix ENABLE ROW LEVEL SECURITY;
ALTER TABLE operating_statement_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE pro_formas ENABLE ROW LEVEL SECURITY;
ALTER TABLE debt_facilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE tranches ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE msa_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE investment_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES: ORGANIZATIONS
-- ============================================================================

-- Users can only see their own organization
CREATE POLICY "Users can view their organization"
ON organizations FOR SELECT
USING (id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Users can update their own organization (admins only - we'll refine this later)
CREATE POLICY "Users can update their organization"
ON organizations FOR UPDATE
USING (id IN (
  SELECT organization_id FROM users WHERE id = auth.uid() AND role = 'ADMIN'
));

-- ============================================================================
-- RLS POLICIES: USERS
-- ============================================================================

-- Users can only see users in their organization
CREATE POLICY "Users can view organization users"
ON users FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
ON users FOR UPDATE
USING (id = auth.uid());

-- ============================================================================
-- RLS POLICIES: DEALS
-- ============================================================================

-- Users can only see deals from their organization
CREATE POLICY "Users can view organization deals"
ON deals FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Users can create deals in their organization
CREATE POLICY "Users can create organization deals"
ON deals FOR INSERT
WITH CHECK (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Users can update deals in their organization
CREATE POLICY "Users can update organization deals"
ON deals FOR UPDATE
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- ============================================================================
-- RLS POLICIES: DOCUMENTS
-- ============================================================================

-- Users can only see documents from their organization's deals
CREATE POLICY "Users can view organization documents"
ON documents FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Users can create documents for their organization's deals
CREATE POLICY "Users can create organization documents"
ON documents FOR INSERT
WITH CHECK (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- ============================================================================
-- RLS POLICIES: PROPERTIES, RENT_ROLL, UNIT_MIX, etc.
-- (All related to deals, so same organization-based access)
-- ============================================================================

-- Properties: Users can only see properties from their organization's deals
CREATE POLICY "Users can view organization properties"
ON properties FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Rent Roll: Users can only see rent roll from their organization's deals
CREATE POLICY "Users can view organization rent roll"
ON rent_roll FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Unit Mix: Users can only see unit mix from their organization's deals
CREATE POLICY "Users can view organization unit mix"
ON unit_mix FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Scenarios: Users can only see scenarios from their organization's deals (through analyses)
CREATE POLICY "Users can view organization scenarios"
ON scenarios FOR SELECT
USING (EXISTS (
  SELECT 1 FROM analyses a
  JOIN deals d ON a.deal_id = d.id
  JOIN users u ON d.organization_id = u.organization_id
  WHERE a.id = scenarios.analysis_id
    AND u.id = auth.uid()
));

-- Analyses: Users can only see analyses from their organization's deals
CREATE POLICY "Users can view organization analyses"
ON analyses FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Notes: Users can only see notes from their organization's deals
CREATE POLICY "Users can view organization notes"
ON notes FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Tasks: Users can only see tasks from their organization's deals
CREATE POLICY "Users can view organization tasks"
ON tasks FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Market Research: Users can only see market research from their organization's deals
CREATE POLICY "Users can view organization market research"
ON market_research FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals 
  WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Investment Criteria: Users can only see investment criteria from their organization
CREATE POLICY "Users can view organization investment criteria"
ON investment_criteria FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Integrations: Users can only see integrations from their organization
CREATE POLICY "Users can view organization integrations"
ON integrations FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Activity Log: Users can only see activity logs from their organization
CREATE POLICY "Users can view organization activity log"
ON activity_log FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- MSA Cache: Public read (market data), but organization-scoped for writes
CREATE POLICY "Users can view MSA cache"
ON msa_cache FOR SELECT
USING (true); -- Market data is public, but we can restrict writes later

-- Operating Statement Lines: Through pro_formas -> analyses -> deals
CREATE POLICY "Users can view organization operating statement lines"
ON operating_statement_lines FOR SELECT
USING (EXISTS (
  SELECT 1 FROM pro_formas pf
  JOIN analyses a ON pf.analysis_id = a.id
  JOIN deals d ON a.deal_id = d.id
  JOIN users u ON d.organization_id = u.organization_id
  WHERE pf.id = operating_statement_lines.pro_forma_id
    AND u.id = auth.uid()
));

-- Pro Formas: Through analyses -> deals
CREATE POLICY "Users can view organization pro formas"
ON pro_formas FOR SELECT
USING (EXISTS (
  SELECT 1 FROM analyses a
  JOIN deals d ON a.deal_id = d.id
  JOIN users u ON d.organization_id = u.organization_id
  WHERE a.id = pro_formas.analysis_id
    AND u.id = auth.uid()
));

-- Debt Facilities: Through pro_formas -> analyses -> deals
CREATE POLICY "Users can view organization debt facilities"
ON debt_facilities FOR SELECT
USING (EXISTS (
  SELECT 1 FROM pro_formas pf
  JOIN analyses a ON pf.analysis_id = a.id
  JOIN deals d ON a.deal_id = d.id
  JOIN users u ON d.organization_id = u.organization_id
  WHERE pf.id = debt_facilities.pro_forma_id
    AND u.id = auth.uid()
));

-- Tranches: Through debt_facilities -> pro_formas -> analyses -> deals
CREATE POLICY "Users can view organization tranches"
ON tranches FOR SELECT
USING (EXISTS (
  SELECT 1 FROM debt_facilities df
  JOIN pro_formas pf ON df.pro_forma_id = pf.id
  JOIN analyses a ON pf.analysis_id = a.id
  JOIN deals d ON a.deal_id = d.id
  JOIN users u ON d.organization_id = u.organization_id
  WHERE df.id = tranches.debt_facility_id
    AND u.id = auth.uid()
));

-- Reports: Through analyses -> deals
CREATE POLICY "Users can view organization reports"
ON reports FOR SELECT
USING (EXISTS (
  SELECT 1 FROM analyses a
  JOIN deals d ON a.deal_id = d.id
  JOIN users u ON d.organization_id = u.organization_id
  WHERE a.id = reports.analysis_id
    AND u.id = auth.uid()
));

-- ============================================================================
-- NOTE: INSERT/UPDATE/DELETE policies will be added as needed
-- For now, we're using service_role key for backend operations which bypasses RLS
-- ============================================================================

