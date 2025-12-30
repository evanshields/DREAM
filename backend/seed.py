"""
DREAM AI - Database Seeding Script
Realistic Multifamily Deal Sample Data
Version: 1.0

This script seeds the database with a complete, realistic multifamily deal
including all necessary data for demonstrating the full DREAM AI workflow.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any
import json

# Prisma client import (adjust based on your setup)
# from prisma import Prisma
# from prisma.enums import *

# For demonstration, we'll structure the data as dictionaries
# In production, you'll use actual Prisma client methods

# ============================================================================
# SAMPLE ORGANIZATION & USERS
# ============================================================================

SAMPLE_ORGANIZATION = {
    "name": "Shieldstone Acquisitions Demo",
    "subscription_tier": "PROFESSIONAL",
    "settings": {
        "default_hold_period": 60,  # months
        "default_market_tier": "SECONDARY",
        "timezone": "America/New_York"
    }
}

SAMPLE_USERS = [
    {
        "email": "john.analyst@shieldstone.com",
        "name": "John Analyst",
        "role": "ANALYST",
        "preferences": {
            "email_notifications": True,
            "default_view": "pipeline"
        }
    },
    {
        "email": "sarah.manager@shieldstone.com",
        "name": "Sarah Manager",
        "role": "ADMIN",
        "preferences": {
            "email_notifications": True,
            "default_view": "dashboard"
        }
    }
]

# ============================================================================
# INVESTMENT CRITERIA
# ============================================================================

SAMPLE_INVESTMENT_CRITERIA = {
    "name": "Shieldstone Value-Add Multifamily Criteria",
    "is_default": True,
    "criteria_config": {
        "property_types": ["MULTIFAMILY"],
        "market_tiers": ["GATEWAY", "SECONDARY"],
        "min_units": 50,
        "max_units": 300,
        "preferred_vintages": ["1980_1999", "POST_2000"],
        "target_metrics": {
            "irr": {
                "minimum": 0.14,
                "target": 0.18,
                "excellent": 0.22
            },
            "equity_multiple": {
                "minimum": 1.50,
                "target": 1.80,
                "excellent": 2.00
            },
            "stabilized_coc": {
                "minimum": 0.06,
                "target": 0.08,
                "excellent": 0.10
            }
        },
        "red_flags": {
            "violent_crime_threshold": 2.5,  # Times national average
            "population_decline_threshold": -0.01,  # -1% per year
            "single_employer_threshold": 0.40  # 40% of employment
        }
    }
}

# ============================================================================
# SAMPLE DEAL: Oak Creek Apartments (Austin, TX)
# ============================================================================

SAMPLE_DEAL = {
    "name": "Oak Creek Apartments - Austin, TX",
    "status": "SCREENING",
    "property_data": {
        "offering_memorandum_date": "2025-11-15",
        "broker": "CBRE Multifamily",
        "listing_type": "Off-Market"
    }
}

# ============================================================================
# PROPERTY DATA
# ============================================================================

SAMPLE_PROPERTY = {
    "address": "1234 Oak Creek Drive",
    "city": "Austin",
    "state": "TX",
    "zip": "78744",
    "latitude": Decimal("30.2118"),
    "longitude": Decimal("-97.7503"),
    "submarket": "South Austin",
    "msa_code": "12420",  # Austin-Round Rock MSA
    
    # Property Characteristics
    "units": 196,
    "buildings": 12,
    "year_built": 1985,
    "renovation_year": 2015,  # Partial renovation
    "net_rentable_sf": 176400,  # 196 units × 900 avg SF
    "avg_unit_size": 900,
    "property_class": "CLASS_B",
    
    # Financial Overview
    "asking_price": Decimal("34300000"),  # $175k per unit
    "price_per_unit": Decimal("175000"),
    "price_per_sf": Decimal("194.44"),
    "current_noi": Decimal("2058000"),  # T-12 NOI
    "pro_forma_noi": Decimal("2450000"),  # Stabilized NOI projection
    "going_in_cap_rate": Decimal("0.06"),  # 6.0%
    "occupancy_rate": Decimal("0.88")  # 88% occupied
}

# ============================================================================
# UNIT MIX
# ============================================================================

SAMPLE_UNIT_MIX = [
    {
        "unit_type": "1BR/1BA",
        "count": 78,
        "avg_sf": 650,
        "in_place_rent": Decimal("1150"),
        "market_rent": Decimal("1350")
    },
    {
        "unit_type": "2BR/2BA",
        "count": 98,
        "avg_sf": 1000,
        "in_place_rent": Decimal("1450"),
        "market_rent": Decimal("1750")
    },
    {
        "unit_type": "3BR/2BA",
        "count": 20,
        "avg_sf": 1250,
        "in_place_rent": Decimal("1850"),
        "market_rent": Decimal("2200")
    }
]

# ============================================================================
# RENT ROLL (Sample Units)
# ============================================================================

def generate_rent_roll():
    """Generate sample rent roll entries"""
    rent_roll = []
    unit_counter = 1
    
    for unit_type_data in SAMPLE_UNIT_MIX:
        unit_type = unit_type_data["unit_type"]
        count = unit_type_data["count"]
        avg_sf = unit_type_data["avg_sf"]
        in_place_rent = unit_type_data["in_place_rent"]
        market_rent = unit_type_data["market_rent"]
        
        # Generate entries for this unit type
        for i in range(count):
            # Determine if vacant (12% vacancy)
            is_vacant = (unit_counter % 8 == 0)  # Every 8th unit vacant
            
            # Vary rents slightly
            current_rent = in_place_rent if not is_vacant else Decimal("0")
            if not is_vacant and unit_counter % 3 == 0:
                # Some units at market rent (recent renewals)
                current_rent = market_rent
            
            # Lease dates
            if not is_vacant:
                lease_start = datetime.now() - timedelta(days=(unit_counter * 7) % 365)
                lease_end = lease_start + timedelta(days=365)
            else:
                lease_start = None
                lease_end = None
            
            rent_roll.append({
                "unit_number": f"{(unit_counter // 10) + 1}{unit_counter % 10}",
                "unit_type": unit_type,
                "sq_ft": avg_sf,
                "current_rent": current_rent,
                "market_rent": market_rent,
                "lease_start": lease_start,
                "lease_end": lease_end,
                "tenant_name": f"Tenant {unit_counter}" if not is_vacant else None,
                "is_vacant": is_vacant
            })
            
            unit_counter += 1
    
    return rent_roll

# ============================================================================
# T-12 OPERATING STATEMENT
# ============================================================================

SAMPLE_T12_OPERATING_STATEMENT = {
    "period": "T12",
    "line_items": [
        # Revenue
        {
            "category": "Revenue",
            "line_item": "Gross Potential Rent",
            "amount": Decimal("3234000"),
            "per_unit": Decimal("16500"),
            "notes": "Based on in-place rents"
        },
        {
            "category": "Revenue",
            "line_item": "Vacancy Loss",
            "amount": Decimal("-388080"),  # 12%
            "per_unit": Decimal("-1980"),
            "notes": "12% physical vacancy"
        },
        {
            "category": "Revenue",
            "line_item": "Concessions",
            "amount": Decimal("-64680"),  # 2%
            "per_unit": Decimal("-330"),
            "notes": "One month free on 12-month leases"
        },
        {
            "category": "Revenue",
            "line_item": "Other Income",
            "amount": Decimal("117600"),
            "per_unit": Decimal("600"),
            "notes": "Parking, pet fees, laundry, utilities"
        },
        {
            "category": "Revenue",
            "line_item": "Effective Gross Income",
            "amount": Decimal("2898840"),
            "per_unit": Decimal("14790"),
            "notes": "EGI"
        },
        
        # Operating Expenses
        {
            "category": "Operating Expenses",
            "line_item": "Management Fee",
            "amount": Decimal("86965"),  # 3% of EGI
            "per_unit": Decimal("444"),
            "notes": "3% of EGI"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Payroll & Personnel",
            "amount": Decimal("176400"),
            "per_unit": Decimal("900"),
            "notes": "On-site staff"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Repairs & Maintenance",
            "amount": Decimal("156800"),
            "per_unit": Decimal("800"),
            "notes": "R&M and turnover costs"
        },
        {
            "category": "Operating Expenses",
            "line_item": "General & Administrative",
            "amount": Decimal("78400"),
            "per_unit": Decimal("400"),
            "notes": "Legal, accounting, office"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Marketing",
            "amount": Decimal("39200"),
            "per_unit": Decimal("200"),
            "notes": "Leasing and advertising"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Utilities",
            "amount": Decimal("98000"),
            "per_unit": Decimal("500"),
            "notes": "Common area utilities"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Property Taxes",
            "amount": Decimal("245000"),
            "per_unit": Decimal("1250"),
            "notes": "Current assessment, 2.5% effective rate"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Insurance",
            "amount": Decimal("58800"),
            "per_unit": Decimal("300"),
            "notes": "Property and liability"
        },
        {
            "category": "Operating Expenses",
            "line_item": "Total Operating Expenses",
            "amount": Decimal("939565"),
            "per_unit": Decimal("4794"),
            "notes": "Total OpEx"
        },
        
        # NOI
        {
            "category": "NOI",
            "line_item": "Net Operating Income",
            "amount": Decimal("1959275"),
            "per_unit": Decimal("9996"),
            "notes": "T-12 NOI"
        }
    ]
}

# ============================================================================
# PRO FORMA ASSUMPTIONS
# ============================================================================

SAMPLE_PRO_FORMA_ASSUMPTIONS = {
    "acquisition": {
        "purchase_price": 34300000,
        "closing_costs_pct": 0.025,  # 2.5%
        "acquisition_fee_pct": 0.01,  # 1%
        "closing_costs": 857500,
        "acquisition_fee": 343000
    },
    
    "financing": {
        "senior_debt": {
            "ltv": 0.65,
            "interest_rate": 0.0625,  # 6.25%
            "amortization_years": 30,
            "term_months": 36,
            "io_period_months": 12
        },
        "refinance": {
            "enabled": True,
            "month": 30,
            "ltv": 0.75,
            "rate": 0.055,  # 5.5% agency
            "amortization": 30
        }
    },
    
    "revenue": {
        "unit_mix": SAMPLE_UNIT_MIX,
        "rent_growth": [0.04, 0.04, 0.035, 0.035, 0.03],  # Years 1-5
        "other_income_per_unit": 600,
        "other_income_growth": [0.03] * 5,
        "physical_vacancy": [0.12, 0.10, 0.08, 0.06, 0.06],
        "concessions": [0.02, 0.015, 0.01, 0.01, 0.01],
        "bad_debt": [0.005] * 5
    },
    
    "expenses": {
        "management_fee_pct": 0.03,
        "payroll_per_unit": 900,
        "repairs_per_unit": 800,
        "admin_per_unit": 400,
        "marketing_per_unit": 200,
        "utilities_per_unit": 500,
        "insurance_per_unit": 300,
        "property_tax": {
            "current_assessed": 9800000,
            "reassessment_ratio": 0.70,  # Texas 60-70%
            "millage_rate": 0.025,
            "appeal_scenario": False
        },
        "expense_growth_rate": [0.03, 0.03, 0.03, 0.03, 0.03]
    },
    
    "capex": {
        "renovation_budget": {
            "exterior": 980000,  # $5k per unit
            "interior": 1960000,  # $10k per unit
            "contingency": 294000  # 10%
        },
        "timeline": {
            "start_month": 1,
            "duration_months": 24
        },
        "reserves_per_unit": 300  # Annual
    },
    
    "exit": {
        "hold_period_months": 60,
        "exit_cap_rate": 0.055,  # 5.5%
        "selling_costs_pct": 0.02  # 2%
    },
    
    "waterfall": {
        "gp_equity_pct": 0.10,
        "lp_equity_pct": 0.90,
        "preferred_return": 0.08,  # 8%
        "hurdles": [
            {"irr_threshold": 0.15, "gp_split": 0.30, "lp_split": 0.70},
            {"irr_threshold": 0.20, "gp_split": 0.50, "lp_split": 0.50}
        ]
    }
}

# ============================================================================
# SAMPLE PRO FORMA RESULTS
# ============================================================================

SAMPLE_PRO_FORMA_RESULTS = {
    "sources_uses": {
        "sources": {
            "senior_debt": 22295000,
            "gp_equity": 1450050,
            "lp_equity": 13050450,
            "total_sources": 36795500
        },
        "uses": {
            "purchase_price": 34300000,
            "closing_costs": 857500,
            "acquisition_fee": 343000,
            "renovation_budget": 1960000,
            "contingency": 294000,
            "reserves": 41000,
            "total_uses": 37795500
        }
    },
    
    "returns": {
        "going_in_cap_rate": 0.0600,
        "stabilized_cap_rate": 0.0667,
        "exit_cap_rate": 0.0550,
        
        "project_irr": 0.1850,  # 18.5%
        "project_em": 1.92,
        
        "gp_irr": 0.2450,  # 24.5% (with promote)
        "gp_em": 2.85,
        "gp_profit": 2681500,
        
        "lp_irr": 0.1720,  # 17.2%
        "lp_em": 1.85,
        "lp_profit": 11092800,
        
        "stabilized_coc": 0.0785,  # 7.85%
        "avg_coc": 0.0650
    }
}

# ============================================================================
# MARKET RESEARCH DATA
# ============================================================================

SAMPLE_MARKET_RESEARCH = {
    "msa_data": {
        "msa_code": "12420",
        "msa_name": "Austin-Round Rock-Georgetown, TX",
        "primary_city": "Austin",
        "state": "TX",
        "market_tier": "SECONDARY",
        "tier_rationale": "Austin qualifies as a secondary market based on population of 2,300,000, 3.2% job growth, 2.1% population growth.",
        
        "population": 2300000,
        "population_growth_1yr": 0.021,
        "population_growth_5yr": 0.098,
        "median_household_income": 82500,
        
        "total_employment": 1250000,
        "unemployment_rate": 0.031,
        "job_growth_1yr": 0.032,
        
        "top_employers": [
            {"name": "University of Texas", "industry": "Education", "employee_count": 24000, "is_growing": True},
            {"name": "Dell Technologies", "industry": "Technology", "employee_count": 13000, "is_growing": True},
            {"name": "Ascension Seton", "industry": "Healthcare", "employee_count": 10000, "is_growing": True},
            {"name": "Apple", "industry": "Technology", "employee_count": 8000, "is_growing": True},
            {"name": "Amazon", "industry": "Technology", "employee_count": 7500, "is_growing": True}
        ],
        
        "multifamily_inventory": 575000,
        "vacancy_rate": 0.052,
        "avg_rent_1br": 1350,
        "avg_rent_2br": 1750,
        "rent_growth_1yr": 0.034,
        "avg_cap_rate": 0.055,
        
        "units_under_construction": 18500,
        "units_delivered_12mo": 12300,
        
        "rent_control_status": "PREEMPTED",
        "landlord_friendly_rating": 8,
        
        "market_outlook": "POSITIVE",
        "outlook_rationale": "Strong job growth driven by tech sector expansion, continued in-migration from California. Supply elevated but demand remains robust."
    },
    
    "submarket_data": {
        "submarket_name": "South Austin",
        "vacancy_rate": 0.048,
        "avg_rent": 1520,
        "rent_growth_1yr": 0.038,
        "strengths": [
            "Strong rental demand from tech employment",
            "Proximity to downtown (8 miles)",
            "Good school districts",
            "Transit-accessible"
        ],
        "weaknesses": [
            "Rising property taxes",
            "Gentrification concerns",
            "Traffic congestion"
        ]
    },
    
    "location_data": {
        "walk_score": 72,
        "transit_score": 45,
        "bike_score": 68,
        "nearby_employers": [
            {"name": "Dell Technologies HQ", "distance_miles": 3.2, "employees": 13000},
            {"name": "Apple Campus", "distance_miles": 4.1, "employees": 8000},
            {"name": "Samsung Fab", "distance_miles": 4.8, "employees": 3000}
        ],
        "nearby_amenities": {
            "grocery_stores": ["H-E-B", "Whole Foods", "Trader Joe's"],
            "restaurants": 45,
            "schools": 4,
            "parks": 2
        }
    },
    
    "data_as_of": datetime.now().isoformat(),
    "sources": ["Census Bureau", "BLS", "CoStar", "Walk Score", "Perplexity"],
    "llm_cost_cents": 12
}

# ============================================================================
# SAMPLE ANALYSIS RESULTS
# ============================================================================

SAMPLE_ANALYSIS_RESULTS = {
    "type": "FULL_UW",
    "version": 1,
    "status": "COMPLETED",
    "recommendation": "BUY",
    
    "scores": {
        "overall": 78,
        "financial": 82,
        "business_plan": 76,
        "market": 81,
        "property": 72,
        "risk": 75,
        
        "breakdown": {
            "financial": {
                "score": 82,
                "factors": {
                    "irr_vs_hurdle": "18.5% IRR exceeds 16% risk-adjusted hurdle",
                    "equity_multiple": "1.92x EM exceeds 1.50x minimum",
                    "coc": "7.85% stabilized CoC meets 6% floor"
                }
            },
            "business_plan": {
                "score": 76,
                "factors": {
                    "value_add_thesis": "Interior renovation to achieve $200-300/unit rent premiums",
                    "execution_feasibility": "24-month renovation timeline is achievable",
                    "sponsor_capability": "Experienced with similar 1980s value-add deals"
                }
            },
            "market": {
                "score": 81,
                "factors": {
                    "market_tier": "Secondary market (Austin) with strong growth",
                    "employment_growth": "3.2% job growth, tech-driven",
                    "supply_demand": "Supply elevated but absorption strong"
                }
            },
            "property": {
                "score": 72,
                "factors": {
                    "vintage": "1985 vintage requires moderate capex",
                    "occupancy": "88% occupied, turnaround opportunity",
                    "condition": "Partial 2015 renovation, solid bones"
                }
            },
            "risk": {
                "score": 75,
                "factors": {
                    "red_flags": "None identified",
                    "key_risks": "Property tax reassessment, renovation timeline",
                    "mitigations": "3-scenario tax modeling, phased renovation"
                }
            }
        }
    },
    
    "strengths": [
        "Strong IRR of 18.5% with 250 bps cushion above hurdle",
        "Austin secondary market with tech-driven employment growth",
        "Clear value-add path: $10k/unit interior upgrades → $200-300/unit rent premium",
        "Solid execution timeline: 24-month renovation, 36-month stabilization",
        "Attractive refinancing opportunity at Month 30 (90/90 rule compliance)"
    ],
    
    "concerns": [
        "Property tax reassessment likely post-acquisition (70% of purchase price)",
        "Supply pipeline elevated at 3.2% of inventory",
        "Renovation timeline risk: delays could push stabilization beyond refinance window",
        "Floating rate bridge debt: rate exposure during IO period"
    ],
    
    "recommendation_rationale": """
Recommend PROCEED. Oak Creek Apartments presents a solid value-add opportunity in a 
strong secondary market. The 18.5% IRR provides adequate cushion above the 16% 
risk-adjusted hurdle for this profile (Secondary market + 1985 vintage + moderate 
renovation + floating debt). 

The renovation strategy is conservative and backed by strong rent comps. Austin's 
tech-driven employment growth supports rent assumptions. Key risks (property tax, 
renovation timeline) are manageable with proper planning.

Net investor IRR of 17.2% (LP) meets the 15% minimum threshold with margin for error.
    """,
    
    "next_steps": [
        "Request detailed property condition assessment",
        "Validate rent comps with broker for renovated units",
        "Obtain property tax appeal history from seller",
        "Review contractor bids for renovation scope",
        "Model downside scenarios (exit cap 6.0%, rent growth 2.5%)"
    ],
    
    "llm_cost_cents": 145
}

# ============================================================================
# SEED FUNCTION
# ============================================================================

async def seed_database():
    """
    Main seeding function to populate database with sample data.
    
    In production, this would use Prisma client to create records.
    For this skeleton, we're showing the data structure.
    """
    
    print("🌱 Starting database seeding...")
    
    # 1. Create Organization
    print("Creating organization...")
    # org = await prisma.organization.create(data=SAMPLE_ORGANIZATION)
    
    # 2. Create Users
    print("Creating users...")
    # users = []
    # for user_data in SAMPLE_USERS:
    #     user_data["organization_id"] = org.id
    #     user = await prisma.user.create(data=user_data)
    #     users.append(user)
    
    # 3. Create Investment Criteria
    print("Creating investment criteria...")
    # criteria_data = SAMPLE_INVESTMENT_CRITERIA.copy()
    # criteria_data["organization_id"] = org.id
    # criteria = await prisma.investmentCriteria.create(data=criteria_data)
    
    # 4. Create Deal
    print("Creating deal...")
    # deal_data = SAMPLE_DEAL.copy()
    # deal_data["organization_id"] = org.id
    # deal_data["created_by_id"] = users[0].id
    # deal = await prisma.deal.create(data=deal_data)
    
    # 5. Create Property
    print("Creating property...")
    # property_data = SAMPLE_PROPERTY.copy()
    # property_data["deal_id"] = deal.id
    # property = await prisma.property.create(data=property_data)
    
    # 6. Create Unit Mix
    print("Creating unit mix...")
    # for unit_mix_data in SAMPLE_UNIT_MIX:
    #     unit_mix_data["property_id"] = property.id
    #     await prisma.unitMix.create(data=unit_mix_data)
    
    # 7. Create Rent Roll
    print("Creating rent roll...")
    # rent_roll = generate_rent_roll()
    # for rent_roll_entry in rent_roll:
    #     rent_roll_entry["property_id"] = property.id
    #     await prisma.rentRollEntry.create(data=rent_roll_entry)
    
    # 8. Create Analysis
    print("Creating analysis...")
    # analysis_data = {
    #     "deal_id": deal.id,
    #     "type": "FULL_UW",
    #     "version": 1,
    #     "assumptions": SAMPLE_PRO_FORMA_ASSUMPTIONS,
    #     "results": SAMPLE_ANALYSIS_RESULTS,
    #     "scores": SAMPLE_ANALYSIS_RESULTS["scores"],
    #     "recommendation": "BUY",
    #     "status": "COMPLETED",
    #     "llm_cost_cents": 145
    # }
    # analysis = await prisma.analysis.create(data=analysis_data)
    
    # 9. Create Pro Forma
    print("Creating pro forma...")
    # proforma_data = {
    #     "analysis_id": analysis.id,
    #     "purchase_price": SAMPLE_PRO_FORMA_ASSUMPTIONS["acquisition"]["purchase_price"],
    #     "closing_costs": SAMPLE_PRO_FORMA_ASSUMPTIONS["acquisition"]["closing_costs"],
    #     "acquisition_fee": SAMPLE_PRO_FORMA_ASSUMPTIONS["acquisition"]["acquisition_fee"],
    #     "senior_debt_amount": SAMPLE_PRO_FORMA_RESULTS["sources_uses"]["sources"]["senior_debt"],
    #     "senior_debt_ltv": SAMPLE_PRO_FORMA_ASSUMPTIONS["financing"]["senior_debt"]["ltv"],
    #     "senior_debt_rate": SAMPLE_PRO_FORMA_ASSUMPTIONS["financing"]["senior_debt"]["interest_rate"],
    #     "project_irr": SAMPLE_PRO_FORMA_RESULTS["returns"]["project_irr"],
    #     "project_em": SAMPLE_PRO_FORMA_RESULTS["returns"]["project_em"],
    #     "gp_irr": SAMPLE_PRO_FORMA_RESULTS["returns"]["gp_irr"],
    #     "gp_em": SAMPLE_PRO_FORMA_RESULTS["returns"]["gp_em"],
    #     "lp_irr": SAMPLE_PRO_FORMA_RESULTS["returns"]["lp_irr"],
    #     "lp_em": SAMPLE_PRO_FORMA_RESULTS["returns"]["lp_em"],
    #     "stabilized_coc": SAMPLE_PRO_FORMA_RESULTS["returns"]["stabilized_coc"],
    #     "sources_uses": SAMPLE_PRO_FORMA_RESULTS["sources_uses"],
    #     "annual_cash_flows": {"years": []},  # Would contain full yearly projections
    # }
    # proforma = await prisma.proForma.create(data=proforma_data)
    
    # 10. Create Operating Statement Lines
    print("Creating operating statement lines...")
    # for line_item in SAMPLE_T12_OPERATING_STATEMENT["line_items"]:
    #     line_item["pro_forma_id"] = proforma.id
    #     line_item["period"] = "T12"
    #     await prisma.operatingStatementLine.create(data=line_item)
    
    # 11. Create Market Research
    print("Creating market research...")
    # market_research_data = {
    #     "deal_id": deal.id,
    #     **SAMPLE_MARKET_RESEARCH,
    #     "data_as_of": datetime.now()
    # }
    # await prisma.marketResearch.create(data=market_research_data)
    
    # 12. Create MSA Cache
    print("Creating MSA cache...")
    # msa_cache_data = {
    #     **SAMPLE_MARKET_RESEARCH["msa_data"],
    #     "data_as_of": datetime.now(),
    #     "expires_at": datetime.now() + timedelta(days=7),
    #     "sources": SAMPLE_MARKET_RESEARCH["sources"]
    # }
    # await prisma.msaCache.create(data=msa_cache_data)
    
    # 13. Create Sample Tasks
    print("Creating tasks...")
    # tasks = [
    #     {
    #         "deal_id": deal.id,
    #         "created_by_id": users[0].id,
    #         "assigned_to_id": users[1].id,
    #         "title": "Review property condition assessment",
    #         "description": "Obtain PCA and review deferred maintenance items",
    #         "due_date": datetime.now() + timedelta(days=7),
    #         "priority": "HIGH",
    #         "status": "TODO"
    #     },
    #     {
    #         "deal_id": deal.id,
    #         "created_by_id": users[0].id,
    #         "assigned_to_id": users[0].id,
    #         "title": "Validate rent comps",
    #         "description": "Confirm $200-300 rent premium achievable with renovations",
    #         "due_date": datetime.now() + timedelta(days=5),
    #         "priority": "HIGH",
    #         "status": "IN_PROGRESS"
    #     },
    #     {
    #         "deal_id": deal.id,
    #         "created_by_id": users[1].id,
    #         "assigned_to_id": users[0].id,
    #         "title": "Property tax appeal analysis",
    #         "description": "Research Travis County tax appeal success rates",
    #         "due_date": datetime.now() + timedelta(days=10),
    #         "priority": "MEDIUM",
    #         "status": "TODO"
    #     }
    # ]
    # for task_data in tasks:
    #     await prisma.task.create(data=task_data)
    
    print("✅ Database seeding completed!")
    print(f"""
    Created sample data:
    - Organization: {SAMPLE_ORGANIZATION['name']}
    - Users: {len(SAMPLE_USERS)}
    - Deal: {SAMPLE_DEAL['name']}
    - Property: {SAMPLE_PROPERTY['address']}
    - Units: {SAMPLE_PROPERTY['units']}
    - Analysis: FULL_UW with 78/100 score
    - Recommendation: BUY (18.5% IRR)
    """)

# ============================================================================
# EXPORT DATA FOR TESTING
# ============================================================================

def export_sample_data():
    """Export sample data as JSON for testing/documentation"""
    sample_data = {
        "organization": SAMPLE_ORGANIZATION,
        "users": SAMPLE_USERS,
        "investment_criteria": SAMPLE_INVESTMENT_CRITERIA,
        "deal": SAMPLE_DEAL,
        "property": SAMPLE_PROPERTY,
        "unit_mix": SAMPLE_UNIT_MIX,
        "t12_statement": SAMPLE_T12_OPERATING_STATEMENT,
        "pro_forma_assumptions": SAMPLE_PRO_FORMA_ASSUMPTIONS,
        "pro_forma_results": SAMPLE_PRO_FORMA_RESULTS,
        "market_research": SAMPLE_MARKET_RESEARCH,
        "analysis_results": SAMPLE_ANALYSIS_RESULTS
    }
    
    with open("backend/seed_data_export.json", "w") as f:
        json.dump(sample_data, f, indent=2, default=str)
    
    print("Exported sample data to seed_data_export.json")

# ============================================================================
# RUN SEEDING
# ============================================================================

if __name__ == "__main__":
    # For testing, export data structure
    export_sample_data()
    
    # In production with Prisma:
    # asyncio.run(seed_database())

