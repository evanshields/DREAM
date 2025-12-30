"""
Shieldstone Underwriting Constants

Critical standards and thresholds from the Technical Underwriting Manual.
"""

# Financing Standards
LTV_STANDARD = 0.65  # 65% LTV on purchase price
IO_PERIOD_MONTHS = 30
AMORTIZATION_YEARS = 30
RATE_SPREAD_BPS = 150  # 5yr Treasury + 150bps
CLOSING_COST_PCT = 0.03  # 3% typical
DSCR_REQUIRED = 1.25  # Typical lender requirement

# Return Requirements - Absolute Minimums
MIN_IRR = 0.12  # 12%
MIN_COC_STABILIZED = 0.06  # 6%
MIN_EQUITY_MULTIPLE = 1.4  # 1.4x

# Market Tier Base Hurdles (midpoint of ranges)
MARKET_TIERS = {
    'gateway': {
        'irr_range': (0.14, 0.16),
        'coc_year1': (0.06, 0.08),
        'coc_stabilized': (0.08, 0.10),
        'equity_multiple_5yr': (1.6, 1.8),
    },
    'secondary': {
        'irr_range': (0.16, 0.19),
        'coc_year1': (0.07, 0.09),
        'coc_stabilized': (0.09, 0.12),
        'equity_multiple_5yr': (1.7, 2.0),
    },
    'tertiary': {
        'irr_range': (0.18, 0.22),
        'coc_year1': (0.09, 0.12),
        'coc_stabilized': (0.12, 0.15),
        'equity_multiple_5yr': (1.9, 2.2),
    },
}

# Risk Adjustments (bps)
RISK_ADJUSTMENTS = {
    'heavy_construction': 0.020,  # 200 bps
    'low_occupancy': 0.015,  # 150 bps
    'property_age_30plus': 0.010,  # 100 bps
    'market_downturn': 0.015,  # 150 bps
    'floating_rate_debt': 0.010,  # 100 bps
}

# Deal Screening - Hard Disqualifiers
MIN_UNITS = 50
MAX_PROPERTY_AGE = 40
MIN_OCCUPANCY = 0.70
MAX_CRIME_MULTIPLIER = 2.0  # 2x national average

# Property Tax (Florida)
FL_REASSESSMENT_RATIO = 0.70  # 70% (NOT 100%)
TAX_ANNUAL_GROWTH = 0.03  # 3% conservative

# Renovation Standards
RENOVATION_SCOPES = {
    'light': {
        'cost_per_unit': 5000,
        'expected_premium': 0.05,
    },
    'moderate': {
        'cost_per_unit': 12000,
        'expected_premium': 0.10,
    },
    'heavy': {
        'cost_per_unit': 20000,
        'expected_premium': 0.15,
    },
    'luxury': {
        'cost_per_unit': 30000,
        'expected_premium': 0.20,
    },
}

RENOVATION_ROI_THRESHOLD = 0.08  # 8% cash-on-cash minimum
EXTERIOR_COST_PCT = 0.175  # 17.5% of interior
CONTINGENCY_PCT_NEW = 0.10  # 10% for properties ≤20 years
CONTINGENCY_PCT_OLD = 0.15  # 15% for properties >20 years

# Age Factors for Renovation
AGE_FACTOR_20 = 1.00
AGE_FACTOR_30 = 1.10
AGE_FACTOR_30PLUS = 1.20

# Due Diligence Timeline
DD_PHASE1_DAYS = 10
DD_PHASE2_DAYS = 45
DD_TOTAL_DAYS = 45

# Exit Strategy
MIN_HOLD_MONTHS_LTCG = 12
OPTIMAL_HOLD_MONTHS = 48
STABILIZATION_MONTHS_AFTER_RENO = 18

# Variance Analysis Thresholds
VARIANCE_WALK_IRR = -0.20  # IRR declined >20%
VARIANCE_RETRADE_CAPEX = 0.20  # Capex increased >20%
VARIANCE_CAUTION_IRR = -0.10  # IRR declined 10-20%

# PCA Variance Thresholds
PCA_VARIANCE_CRITICAL = 0.30  # >30%
PCA_VARIANCE_HIGH = 0.15  # 15-30%
PCA_VARIANCE_MODERATE = 0.05  # 5-15%

# Underwriting Philosophy
UNCERTAINTY_HAIRCUT_MIN = 0.15  # 15% haircut
UNCERTAINTY_HAIRCUT_MAX = 0.20  # 20% haircut

