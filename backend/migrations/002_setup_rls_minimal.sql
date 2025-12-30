-- DREAM AI - Row Level Security (RLS) Setup - MINIMAL VERSION
-- Enables RLS on all tables (policies can be added later)
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
-- BASIC RLS POLICIES (Simple organization-based access)
-- ============================================================================

-- Organizations: Users can only see their own organization
CREATE POLICY "Users can view their organization"
ON organizations FOR SELECT
USING (id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Users: Users can only see users in their organization
CREATE POLICY "Users can view organization users"
ON users FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Deals: Users can only see deals from their organization
CREATE POLICY "Users can view organization deals"
ON deals FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- Documents: Through deals
CREATE POLICY "Users can view organization documents"
ON documents FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Properties, Rent Roll, Unit Mix: Through deals
CREATE POLICY "Users can view organization properties"
ON properties FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

CREATE POLICY "Users can view organization rent roll"
ON rent_roll FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

CREATE POLICY "Users can view organization unit mix"
ON unit_mix FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Notes, Tasks, Market Research: Through deals
CREATE POLICY "Users can view organization notes"
ON notes FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

CREATE POLICY "Users can view organization tasks"
ON tasks FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

CREATE POLICY "Users can view organization market research"
ON market_research FOR SELECT
USING (deal_id IN (
  SELECT id FROM deals WHERE organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  )
));

-- Investment Criteria, Integrations, Activity Log: Direct organization_id
CREATE POLICY "Users can view organization investment criteria"
ON investment_criteria FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

CREATE POLICY "Users can view organization integrations"
ON integrations FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

CREATE POLICY "Users can view organization activity log"
ON activity_log FOR SELECT
USING (organization_id IN (
  SELECT organization_id FROM users WHERE id = auth.uid()
));

-- MSA Cache: Public read
CREATE POLICY "Users can view MSA cache"
ON msa_cache FOR SELECT
USING (true);

-- ============================================================================
-- NOTE: Complex policies for analyses, reports, scenarios, pro_formas, etc.
-- will be added later once we verify the exact schema structure.
-- For now, backend operations use service_role key which bypasses RLS.
-- ============================================================================

