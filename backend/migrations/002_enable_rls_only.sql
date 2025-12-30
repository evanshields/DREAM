-- DREAM AI - Enable Row Level Security Only (No Policies)
-- This just enables RLS - policies will be added separately
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
-- NOTE: This only enables RLS. Since you're using service_role key for 
-- backend operations, RLS won't block anything yet. Policies can be added
-- later once we verify the exact column names in your database.
-- ============================================================================

