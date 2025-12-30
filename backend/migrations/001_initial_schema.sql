-- DREAM AI - Initial Database Migration
-- PostgreSQL Migration Script
-- Version: 1.0
-- Date: December 2025

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE subscription_tier AS ENUM ('FREE', 'BASIC', 'PROFESSIONAL', 'ENTERPRISE');
CREATE TYPE user_role AS ENUM ('ADMIN', 'ANALYST', 'VIEWER');
CREATE TYPE integration_type AS ENUM ('SLACK', 'GOOGLE_DRIVE', 'EMAIL');
CREATE TYPE deal_status AS ENUM ('NEW', 'SCREENING', 'LOI', 'DUE_DILIGENCE', 'UNDER_CONTRACT', 'CLOSED', 'PASSED');
CREATE TYPE property_class AS ENUM ('CLASS_A', 'CLASS_B', 'CLASS_C', 'CLASS_D');
CREATE TYPE document_type AS ENUM ('OFFERING_MEMORANDUM', 'T12_STATEMENT', 'RENT_ROLL', 'FINANCIAL_MODEL', 'PHOTO', 'OTHER');
CREATE TYPE extraction_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
CREATE TYPE analysis_type AS ENUM ('BOE', 'FULL_UW', 'IC_MEMO', 'FULL_MEMO');
CREATE TYPE analysis_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');
CREATE TYPE analysis_recommendation AS ENUM ('STRONG_BUY', 'BUY', 'HOLD', 'PASS');
CREATE TYPE debt_type AS ENUM ('SENIOR_DEBT', 'MEZZANINE', 'PREFERRED_EQUITY', 'BRIDGE', 'AGENCY', 'CONSTRUCTION');
CREATE TYPE report_type AS ENUM ('BOE_MEMO', 'IC_MEMO', 'FULL_UW_MEMO');
CREATE TYPE report_format AS ENUM ('PDF', 'EXCEL', 'SLIDES', 'HTML');
CREATE TYPE market_tier AS ENUM ('GATEWAY', 'SECONDARY', 'TERTIARY');
CREATE TYPE rent_control_status AS ENUM ('NONE', 'STATEWIDE', 'LOCAL', 'PREEMPTED');
CREATE TYPE market_outlook AS ENUM ('POSITIVE', 'NEUTRAL', 'NEGATIVE');
CREATE TYPE task_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');
CREATE TYPE task_status AS ENUM ('TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED');

-- ============================================================================
-- ORGANIZATION & USER MANAGEMENT
-- ============================================================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subscription_tier subscription_tier DEFAULT 'FREE',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role user_role DEFAULT 'ANALYST',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE investment_criteria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    criteria_config JSONB NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    type integration_type NOT NULL,
    credentials TEXT NOT NULL, -- Encrypted
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- DEAL MANAGEMENT
-- ============================================================================

CREATE TABLE deals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    status deal_status DEFAULT 'NEW',
    property_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID UNIQUE NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    -- Location
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip VARCHAR(10) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    submarket VARCHAR(255),
    msa_code VARCHAR(10),
    
    -- Property Characteristics
    units INTEGER NOT NULL,
    buildings INTEGER,
    year_built INTEGER,
    renovation_year INTEGER,
    net_rentable_sf INTEGER,
    avg_unit_size INTEGER,
    property_class property_class,
    
    -- Financial Overview
    asking_price DECIMAL(15, 2),
    price_per_unit DECIMAL(10, 2),
    price_per_sf DECIMAL(10, 2),
    current_noi DECIMAL(15, 2),
    pro_forma_noi DECIMAL(15, 2),
    going_in_cap_rate DECIMAL(5, 4),
    occupancy_rate DECIMAL(5, 4),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE unit_mix (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    
    unit_type VARCHAR(50) NOT NULL,
    count INTEGER NOT NULL,
    avg_sf INTEGER,
    in_place_rent DECIMAL(10, 2) NOT NULL,
    market_rent DECIMAL(10, 2) NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE rent_roll (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    
    unit_number VARCHAR(20) NOT NULL,
    unit_type VARCHAR(50) NOT NULL,
    sq_ft INTEGER,
    current_rent DECIMAL(10, 2) NOT NULL,
    market_rent DECIMAL(10, 2),
    lease_start TIMESTAMPTZ,
    lease_end TIMESTAMPTZ,
    tenant_name VARCHAR(255),
    is_vacant BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- DOCUMENTS
-- ============================================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    type document_type NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER,
    extracted_data JSONB,
    confidence_scores JSONB,
    extraction_status extraction_status DEFAULT 'PENDING',
    
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- ANALYSIS & UNDERWRITING
-- ============================================================================

CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    type analysis_type NOT NULL,
    version INTEGER DEFAULT 1,
    assumptions JSONB NOT NULL,
    results JSONB,
    scores JSONB,
    recommendation analysis_recommendation,
    status analysis_status DEFAULT 'PENDING',
    llm_cost_cents INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pro_formas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID UNIQUE NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    
    -- Acquisition
    purchase_price DECIMAL(15, 2) NOT NULL,
    closing_costs DECIMAL(15, 2) NOT NULL,
    acquisition_fee DECIMAL(15, 2) NOT NULL,
    
    -- Financing
    senior_debt_amount DECIMAL(15, 2) NOT NULL,
    senior_debt_ltv DECIMAL(5, 4) NOT NULL,
    senior_debt_rate DECIMAL(6, 5) NOT NULL,
    
    -- Returns
    project_irr DECIMAL(6, 5),
    project_em DECIMAL(6, 4),
    gp_irr DECIMAL(6, 5),
    gp_em DECIMAL(6, 4),
    lp_irr DECIMAL(6, 5),
    lp_em DECIMAL(6, 4),
    stabilized_coc DECIMAL(6, 5),
    
    -- Full pro forma data
    sources_uses JSONB NOT NULL,
    annual_cash_flows JSONB NOT NULL,
    monthly_cash_flows JSONB,
    sensitivity JSONB,
    waterfall_detail JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE operating_statement_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pro_forma_id UUID NOT NULL REFERENCES pro_formas(id) ON DELETE CASCADE,
    
    period VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    line_item VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    per_unit DECIMAL(10, 2),
    per_sf DECIMAL(8, 4),
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE debt_facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pro_forma_id UUID NOT NULL REFERENCES pro_formas(id) ON DELETE CASCADE,
    
    facility_type debt_type NOT NULL,
    lender VARCHAR(255),
    loan_amount DECIMAL(15, 2) NOT NULL,
    interest_rate DECIMAL(6, 5) NOT NULL,
    amortization INTEGER NOT NULL,
    term_months INTEGER NOT NULL,
    io_period INTEGER,
    ltv DECIMAL(5, 4),
    dscr DECIMAL(5, 4),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tranches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    debt_facility_id UUID NOT NULL REFERENCES debt_facilities(id) ON DELETE CASCADE,
    
    tranche_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    rate DECIMAL(6, 5) NOT NULL,
    priority INTEGER NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    description TEXT,
    assumption_set JSONB NOT NULL,
    results JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MARKET RESEARCH
-- ============================================================================

CREATE TABLE market_research (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID UNIQUE NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    msa_data JSONB NOT NULL,
    submarket_data JSONB,
    location_data JSONB,
    
    data_as_of TIMESTAMPTZ NOT NULL,
    sources TEXT[],
    llm_cost_cents INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE msa_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    msa_code VARCHAR(10) UNIQUE NOT NULL,
    msa_name VARCHAR(200) NOT NULL,
    primary_city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    
    -- Classification
    market_tier market_tier NOT NULL,
    tier_rationale TEXT,
    
    -- Demographics
    population INTEGER,
    population_growth_1yr DECIMAL(5, 4),
    population_growth_5yr DECIMAL(5, 4),
    median_household_income INTEGER,
    
    -- Employment
    total_employment INTEGER,
    unemployment_rate DECIMAL(5, 4),
    job_growth_1yr DECIMAL(5, 4),
    top_employers JSONB,
    
    -- Multifamily Market
    multifamily_inventory INTEGER,
    vacancy_rate DECIMAL(5, 4),
    avg_rent_1br INTEGER,
    avg_rent_2br INTEGER,
    rent_growth_1yr DECIMAL(5, 4),
    avg_cap_rate DECIMAL(5, 4),
    
    -- Supply
    units_under_construction INTEGER,
    units_delivered_12mo INTEGER,
    
    -- Regulatory
    rent_control_status rent_control_status,
    landlord_friendly_rating INTEGER,
    
    -- Outlook
    market_outlook market_outlook,
    outlook_rationale TEXT,
    
    data_as_of TIMESTAMPTZ NOT NULL,
    sources TEXT[],
    expires_at TIMESTAMPTZ NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- REPORTS
-- ============================================================================

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    
    type report_type NOT NULL,
    format report_format NOT NULL,
    file_url TEXT,
    content JSONB,
    
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- COLLABORATION & WORKFLOW
-- ============================================================================

CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    created_by_id UUID NOT NULL REFERENCES users(id),
    assigned_to_id UUID REFERENCES users(id),
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMPTZ,
    priority task_priority DEFAULT 'MEDIUM',
    status task_status DEFAULT 'TODO',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    
    action VARCHAR(100) NOT NULL,
    details JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- User indexes
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- Deal indexes
CREATE INDEX idx_deals_organization_id ON deals(organization_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_created_by_id ON deals(created_by_id);
CREATE INDEX idx_deals_created_at ON deals(created_at DESC);

-- Property indexes
CREATE INDEX idx_properties_deal_id ON properties(deal_id);
CREATE INDEX idx_properties_msa_code ON properties(msa_code);
CREATE INDEX idx_properties_city_state ON properties(city, state);

-- Unit mix indexes
CREATE INDEX idx_unit_mix_property_id ON unit_mix(property_id);

-- Rent roll indexes
CREATE INDEX idx_rent_roll_property_id ON rent_roll(property_id);
CREATE INDEX idx_rent_roll_is_vacant ON rent_roll(is_vacant);

-- Document indexes
CREATE INDEX idx_documents_deal_id ON documents(deal_id);
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_extraction_status ON documents(extraction_status);

-- Analysis indexes
CREATE INDEX idx_analyses_deal_id ON analyses(deal_id);
CREATE INDEX idx_analyses_type ON analyses(type);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);

-- Pro forma indexes
CREATE INDEX idx_pro_formas_analysis_id ON pro_formas(analysis_id);

-- Operating statement indexes
CREATE INDEX idx_operating_statement_lines_pro_forma_id ON operating_statement_lines(pro_forma_id);
CREATE INDEX idx_operating_statement_lines_period ON operating_statement_lines(period);

-- Debt facility indexes
CREATE INDEX idx_debt_facilities_pro_forma_id ON debt_facilities(pro_forma_id);

-- Tranche indexes
CREATE INDEX idx_tranches_debt_facility_id ON tranches(debt_facility_id);

-- Scenario indexes
CREATE INDEX idx_scenarios_analysis_id ON scenarios(analysis_id);

-- Market research indexes
CREATE INDEX idx_market_research_deal_id ON market_research(deal_id);

-- MSA cache indexes
CREATE INDEX idx_msa_cache_msa_code ON msa_cache(msa_code);
CREATE INDEX idx_msa_cache_state ON msa_cache(state);
CREATE INDEX idx_msa_cache_market_tier ON msa_cache(market_tier);
CREATE INDEX idx_msa_cache_expires_at ON msa_cache(expires_at);

-- Report indexes
CREATE INDEX idx_reports_analysis_id ON reports(analysis_id);
CREATE INDEX idx_reports_type ON reports(type);

-- Note indexes
CREATE INDEX idx_notes_deal_id ON notes(deal_id);
CREATE INDEX idx_notes_user_id ON notes(user_id);

-- Task indexes
CREATE INDEX idx_tasks_deal_id ON tasks(deal_id);
CREATE INDEX idx_tasks_assigned_to_id ON tasks(assigned_to_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Activity log indexes
CREATE INDEX idx_activity_log_organization_id ON activity_log(organization_id);
CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX idx_activity_log_deal_id ON activity_log(deal_id);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at DESC);

-- Investment criteria indexes
CREATE INDEX idx_investment_criteria_organization_id ON investment_criteria(organization_id);

-- Integration indexes
CREATE INDEX idx_integrations_organization_id ON integrations(organization_id);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_investment_criteria_updated_at BEFORE UPDATE ON investment_criteria FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_unit_mix_updated_at BEFORE UPDATE ON unit_mix FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rent_roll_updated_at BEFORE UPDATE ON rent_roll FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analyses_updated_at BEFORE UPDATE ON analyses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pro_formas_updated_at BEFORE UPDATE ON pro_formas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_operating_statement_lines_updated_at BEFORE UPDATE ON operating_statement_lines FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_debt_facilities_updated_at BEFORE UPDATE ON debt_facilities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tranches_updated_at BEFORE UPDATE ON tranches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_scenarios_updated_at BEFORE UPDATE ON scenarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_market_research_updated_at BEFORE UPDATE ON market_research FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_msa_cache_updated_at BEFORE UPDATE ON msa_cache FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE organizations IS 'Organizations/companies using the platform';
COMMENT ON TABLE users IS 'Individual users within organizations';
COMMENT ON TABLE deals IS 'Real estate investment opportunities being analyzed';
COMMENT ON TABLE properties IS 'Physical property details for each deal';
COMMENT ON TABLE unit_mix IS 'Unit type breakdown for multifamily properties';
COMMENT ON TABLE rent_roll IS 'Individual unit rent rolls for detailed analysis';
COMMENT ON TABLE analyses IS 'Underwriting analyses (BOE, Full UW, Memos)';
COMMENT ON TABLE pro_formas IS 'Financial pro forma models with DCF calculations';
COMMENT ON TABLE debt_facilities IS 'Debt financing structures for deals';
COMMENT ON TABLE scenarios IS 'Alternative scenario analyses (Base, Upside, Downside)';
COMMENT ON TABLE market_research IS 'Market intelligence data for deals';
COMMENT ON TABLE msa_cache IS 'Cached MSA-level market data';
COMMENT ON TABLE reports IS 'Generated investment memos and reports';

