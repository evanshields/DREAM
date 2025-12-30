# DREAM AI - Phase 3 Product Requirements Document

**Product Name:** DREAM AI  
**Company:** Shieldstone Acquisitions / DREAM.AI  
**Document Type:** Phase 3 PRD (Market Research - Lite)  
**Version:** 1.0  
**Last Updated:** December 2025

---

## 1. Overview

This PRD covers Phase 3 of DREAM AI's acquisitions intelligence workflow:

- **Market Research (Lite):** Essential market context for deal analysis
- **MSA Classification:** Automatic market tier identification
- **Submarket Fundamentals:** Key metrics for underwriting validation
- **Data Aggregation:** Pull from multiple sources into unified view
- **Memo Support:** Market data formatted for report generation

Phase 3 provides the market intelligence foundation needed for accurate underwriting and compelling investment memos. The "Lite" version focuses on the most critical data points for MVP, with full market research capabilities planned for future phases.

**Key Principle:** Automate the market research that analysts currently spend 1-2 hours gathering manually, delivering it in under 60 seconds.

---

## 2. Goals & Success Metrics

### Goals

1. Provide essential market context for every deal automatically
2. Reduce manual market research time from 1-2 hours to <1 minute
3. Support accurate rent growth and cap rate assumptions
4. Enable market-informed scoring and hurdle adjustments
5. Generate market sections for BOE, IC, and Full UW memos

### Success Metrics

| Metric | Target | Stretch Goal | Measurement |
|--------|--------|--------------|-------------|
| Market research completion time | <60 seconds | <30 seconds | Task completion |
| Data point coverage | >80% | >90% | Fields populated |
| LLM cost per market research | <$0.15 | <$0.10 | API cost tracking |
| Data accuracy (spot check) | >90% | >95% | Manual verification |
| User satisfaction with market data | >4.0/5 | >4.5/5 | Feedback |

---

## 3. MVP Scope (Lite Version)

### 3.1 What's Included in MVP

| Category | Data Points | Source |
|----------|-------------|--------|
| **MSA Overview** | Population, job growth, major employers | Census, BLS, Perplexity |
| **Market Tier** | Gateway/Secondary/Tertiary classification | Internal algorithm |
| **Submarket Basics** | Vacancy rate, rent growth, avg rents | Perplexity, public data |
| **Employment** | Top 5-10 employers, unemployment rate | BLS, Perplexity |
| **Demographics** | Median income, population growth | Census |
| **Walkability** | Walk Score, Transit Score | Walk Score API |
| **Regulatory** | Rent control status, landlord-friendly rating | Perplexity, internal DB |
| **Supply Pipeline** | Units under construction (MSA level) | Perplexity |

### 3.2 What's NOT in MVP (Future Phases)

| Feature | Phase | Notes |
|---------|-------|-------|
| Deep submarket analysis | Future | Detailed neighborhood data |
| Construction pipeline tracking | Future | Project-level tracking |
| Historical trend charts | Future | Multi-year visualizations |
| Comp set identification | Future | Automated comp finding |
| Custom market reports | Future | Exportable market reports |
| Market alerts | Future | Saved search notifications |
| Rent comp analysis | Future | Automated rent comp pulls |
| Sales comp analysis | Future | Recent transaction data |

---

## 4. Data Sources & Integration

### 4.1 Primary Data Sources

| Source | Data Provided | Integration Method | Cost |
|--------|---------------|-------------------|------|
| **Perplexity API** | Real-time market research, news, trends | API | ~$0.05-0.10/query |
| **Census Bureau** | Demographics, population, income | API (free) | $0 |
| **BLS** | Employment, unemployment, job growth | API (free) | $0 |
| **Walk Score** | Walk Score, Transit Score, Bike Score | API | ~$0.01/lookup |
| **Internal Database** | Cached market data, user contributions | PostgreSQL | $0 |

### 4.2 Data Refresh Strategy

| Data Type | Refresh Frequency | Cache Duration |
|-----------|-------------------|----------------|
| MSA demographics | Monthly | 30 days |
| Employment data | Monthly | 30 days |
| Rent/vacancy trends | Weekly | 7 days |
| Walk Score | On-demand | 90 days |
| Regulatory status | Quarterly | 90 days |
| News/trends | Real-time | No cache |

### 4.3 Perplexity API Integration

**Query Strategy:** Use structured prompts to extract specific data points efficiently.

**Market Overview Query:**

```
Provide current market data for {city}, {state} multifamily real estate:

1. MSA Population and 5-year growth rate
2. Current unemployment rate
3. Top 5 employers and approximate employee counts
4. Average multifamily vacancy rate
5. Average rent for 1BR and 2BR apartments
6. Year-over-year rent growth percentage
7. Number of multifamily units under construction
8. Any rent control or tenant protection laws
9. Key economic drivers and recent developments
10. Overall market outlook (positive/neutral/negative)

Respond in JSON format with sources cited.
```

**Submarket Query:**

```
Provide submarket data for {submarket_name} in {city}, {state}:

1. Submarket boundaries/definition
2. Average Class B multifamily rent
3. Submarket vacancy rate
4. Recent rent growth trends
5. Major employers within 5 miles
6. New construction in submarket
7. Submarket strengths and weaknesses
8. Comparable properties (if known)

Respond in JSON format with sources cited.
```

---

## 5. Market Data Model

### 5.1 MSA Data Structure

```typescript
interface MSAData {
  // Identification
  msaCode: string;           // CBSA code
  msaName: string;           // "Austin-Round Rock-Georgetown, TX"
  primaryCity: string;       // "Austin"
  state: string;             // "TX"
  
  // Classification
  marketTier: MarketTier;    // GATEWAY, SECONDARY, TERTIARY
  tierRationale: string;     // Why this classification
  
  // Demographics
  population: number;
  populationGrowth1Yr: number;   // Percentage
  populationGrowth5Yr: number;   // Percentage
  medianHouseholdIncome: number;
  medianAge: number;
  
  // Employment
  totalEmployment: number;
  unemploymentRate: number;
  jobGrowth1Yr: number;          // Percentage
  topEmployers: Employer[];      // Top 5-10
  keyIndustries: string[];
  
  // Multifamily Market
  multifamilyInventory: number;  // Total units
  vacancyRate: number;           // Percentage
  avgRent1BR: number;
  avgRent2BR: number;
  rentGrowth1Yr: number;         // Percentage
  rentGrowth5Yr: number;         // CAGR
  avgCapRate: number;            // Percentage
  
  // Supply
  unitsUnderConstruction: number;
  unitsDeliveredLast12Mo: number;
  supplyAsPercentOfInventory: number;
  
  // Regulatory
  rentControlStatus: RentControlStatus;
  landlordFriendlyRating: number;  // 1-10
  regulatoryNotes: string;
  
  // Outlook
  marketOutlook: MarketOutlook;    // POSITIVE, NEUTRAL, NEGATIVE
  outlookRationale: string;
  
  // Metadata
  dataAsOf: Date;
  sources: string[];
}

interface Employer {
  name: string;
  industry: string;
  employeeCount: number;
  isGrowing: boolean;
}

enum MarketTier {
  GATEWAY = 'GATEWAY',       // Top 6 markets
  SECONDARY = 'SECONDARY',   // Major metros
  TERTIARY = 'TERTIARY'      // Smaller markets
}

enum RentControlStatus {
  NONE = 'NONE',
  STATEWIDE = 'STATEWIDE',
  LOCAL = 'LOCAL',
  PREEMPTED = 'PREEMPTED'    // State preempts local rent control
}

enum MarketOutlook {
  POSITIVE = 'POSITIVE',
  NEUTRAL = 'NEUTRAL',
  NEGATIVE = 'NEGATIVE'
}
```

### 5.2 Submarket Data Structure

```typescript
interface SubmarketData {
  // Identification
  submarketId: string;
  submarketName: string;
  msaCode: string;
  zipCodes: string[];
  
  // Location
  boundaries: string;          // Description of area
  latitude: number;
  longitude: number;
  
  // Multifamily Metrics
  vacancyRate: number;
  avgRent: number;
  avgRentPSF: number;
  rentGrowth1Yr: number;
  classBreakdown: {
    classA: { avgRent: number; vacancy: number };
    classB: { avgRent: number; vacancy: number };
    classC: { avgRent: number; vacancy: number };
  };
  
  // Supply
  existingUnits: number;
  unitsUnderConstruction: number;
  plannedUnits: number;
  
  // Demand Drivers
  majorEmployersNearby: Employer[];
  transitAccess: string;
  amenities: string[];
  
  // Scores
  walkScore: number;
  transitScore: number;
  bikeScore: number;
  
  // Assessment
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  
  // Metadata
  dataAsOf: Date;
  sources: string[];
}
```

### 5.3 Property-Level Market Context

```typescript
interface PropertyMarketContext {
  propertyId: string;
  
  // Location scores
  walkScore: number;
  transitScore: number;
  bikeScore: number;
  
  // Nearby amenities (within 1 mile)
  groceryStores: number;
  restaurants: number;
  schools: number;
  parks: number;
  
  // Nearby employers (within 5 miles)
  majorEmployers: Employer[];
  
  // Competitive set (future)
  nearbyProperties: CompetitiveProperty[];
  
  // Risk factors
  floodZone: string;
  crimeIndex: number;        // Relative to MSA average
  
  // Metadata
  dataAsOf: Date;
}
```

---

## 6. Market Tier Classification

### 6.1 Classification Algorithm

```python
class MarketTierClassifier:
    """
    Classify MSAs into Gateway, Secondary, or Tertiary tiers.
    Based on Shieldstone Technical Manual criteria.
    """
    
    # Gateway markets (Top 6)
    GATEWAY_MARKETS = [
        'New York-Newark-Jersey City',
        'Los Angeles-Long Beach-Anaheim',
        'Chicago-Naperville-Elgin',
        'San Francisco-Oakland-Berkeley',
        'Boston-Cambridge-Newton',
        'Washington-Arlington-Alexandria'
    ]
    
    # Secondary market thresholds
    SECONDARY_THRESHOLDS = {
        'min_population': 500000,
        'min_job_growth': 0.01,        # 1% annual
        'min_population_growth': 0.005, # 0.5% annual
        'max_unemployment': 0.06        # 6%
    }
    
    def classify(self, msa_data: MSAData) -> MarketTier:
        """
        Classify an MSA into a market tier.
        """
        # Check if Gateway
        if any(gateway in msa_data.msaName for gateway in self.GATEWAY_MARKETS):
            return MarketTier.GATEWAY
        
        # Score for Secondary classification
        secondary_score = 0
        
        if msa_data.population >= self.SECONDARY_THRESHOLDS['min_population']:
            secondary_score += 1
        
        if msa_data.jobGrowth1Yr >= self.SECONDARY_THRESHOLDS['min_job_growth']:
            secondary_score += 1
        
        if msa_data.populationGrowth1Yr >= self.SECONDARY_THRESHOLDS['min_population_growth']:
            secondary_score += 1
        
        if msa_data.unemploymentRate <= self.SECONDARY_THRESHOLDS['max_unemployment']:
            secondary_score += 1
        
        # Need 3+ criteria for Secondary
        if secondary_score >= 3:
            return MarketTier.SECONDARY
        
        return MarketTier.TERTIARY
    
    def get_rationale(self, msa_data: MSAData, tier: MarketTier) -> str:
        """
        Generate explanation for tier classification.
        """
        if tier == MarketTier.GATEWAY:
            return f"{msa_data.primaryCity} is a top-6 gateway market with institutional liquidity and diverse economic base."
        
        elif tier == MarketTier.SECONDARY:
            factors = []
            if msa_data.population >= 500000:
                factors.append(f"population of {msa_data.population:,}")
            if msa_data.jobGrowth1Yr >= 0.01:
                factors.append(f"{msa_data.jobGrowth1Yr:.1%} job growth")
            if msa_data.populationGrowth1Yr >= 0.005:
                factors.append(f"{msa_data.populationGrowth1Yr:.1%} population growth")
            
            return f"{msa_data.primaryCity} qualifies as a secondary market based on {', '.join(factors)}."
        
        else:
            return f"{msa_data.primaryCity} is classified as a tertiary market. Higher returns required to compensate for liquidity risk."
```

### 6.2 Market Tier Impact on Analysis

| Tier | Base IRR Hurdle | Typical Cap Rates | Liquidity | Investor Base |
|------|-----------------|-------------------|-----------|---------------|
| Gateway | 14-16% | 4.0-5.5% | High | Institutional |
| Secondary | 16-19% | 5.0-7.0% | Moderate | Institutional + Private |
| Tertiary | 18-22% | 6.0-8.5% | Lower | Private + Local |

---

## 7. User Interface

### 7.1 Market Research Panel (Deal Detail Page)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Market Research: Austin, TX                                    [Refresh 🔄]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MSA Overview                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  SECONDARY      │  │  2.3M           │  │  3.2%           │              │
│  │  Market Tier    │  │  Population     │  │  Job Growth     │              │
│  │                 │  │  +2.1% YoY      │  │  (vs 1.8% US)   │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  3.1%           │  │  5.2%           │  │  $1,485         │              │
│  │  Unemployment   │  │  Vacancy Rate   │  │  Avg 2BR Rent   │              │
│  │  (vs 3.7% US)   │  │  (vs 5.8% US)   │  │  +3.4% YoY      │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│  Top Employers                                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  1. University of Texas          │ Education      │ 24,000 employees    ││
│  │  2. Dell Technologies            │ Technology     │ 13,000 employees    ││
│  │  3. Ascension Seton             │ Healthcare     │ 10,000 employees    ││
│  │  4. Apple                        │ Technology     │ 8,000 employees     ││
│  │  5. Amazon                       │ Technology     │ 7,500 employees     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Supply Pipeline                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Units Under Construction: 18,500 (3.2% of inventory)                   ││
│  │  Delivered Last 12 Months: 12,300                                        ││
│  │  Absorption Rate: 95% of deliveries absorbed                            ││
│  │                                                                          ││
│  │  ⚠️ Supply elevated but absorption remains strong                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Regulatory Environment                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Rent Control: None (Texas preempts local rent control)                 ││
│  │  Landlord-Friendly Rating: 8/10                                          ││
│  │  Property Tax Rate: 2.5% (high, but no state income tax)                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Market Outlook: POSITIVE                                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Strong job growth driven by tech sector expansion, continued in-migration  │
│  from California. Supply elevated but demand remains robust. Watch for      │
│  potential slowdown in tech hiring.                                         │
│                                                                              │
│  Data as of: December 2025 | Sources: Census, BLS, CoStar, Perplexity      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Property Location Panel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Property Location: 1234 Oak Creek Dr                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │                        [Interactive Map]                                 ││
│  │                                                                          ││
│  │                    🏢 Property Location                                  ││
│  │                    📍 Major Employers                                    ││
│  │                    🛒 Retail/Grocery                                     ││
│  │                    🚇 Transit Stops                                      ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Location Scores                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │      72         │  │      45         │  │      68         │              │
│  │   Walk Score    │  │  Transit Score  │  │   Bike Score    │              │
│  │   Very Walkable │  │  Some Transit   │  │    Bikeable     │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│  Nearby Amenities (1 mile)                                                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  🛒 Grocery: 3 (H-E-B, Whole Foods, Trader Joe's)                           │
│  🍽️ Restaurants: 45+                                                        │
│  🏫 Schools: 4 (2 elementary, 1 middle, 1 high)                             │
│  🌳 Parks: 2 (Roy G. Guerrero Park, Festival Beach)                         │
│                                                                              │
│  Major Employers (5 miles)                                                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  • Dell Technologies HQ (3.2 mi) - 13,000 employees                         │
│  • Apple Campus (4.1 mi) - 8,000 employees                                  │
│  • Samsung Fab (4.8 mi) - 3,000 employees                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Market Research Workflow

### 8.1 Automated Research Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MARKET RESEARCH WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Deal Created with Address                                                   │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 1: Geocode & Identify Market                                       ││
│  │  ─────────────────────────────────                                       ││
│  │  • Parse address → lat/long                                              ││
│  │  • Identify MSA from coordinates                                         ││
│  │  • Identify submarket (if defined)                                       ││
│  │  • Check cache for recent data                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 2: Fetch Cached Data                                               ││
│  │  ─────────────────────────                                               ││
│  │  • Check internal database for MSA data                                  ││
│  │  • If fresh (<7 days), use cached                                        ││
│  │  • If stale, queue refresh                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 3: Fetch External Data (Parallel)                                  ││
│  │  ─────────────────────────────────────                                   ││
│  │  • Census API → Demographics                                             ││
│  │  • BLS API → Employment data                                             ││
│  │  • Walk Score API → Location scores                                      ││
│  │  • Perplexity → Real-time market data                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 4: Classify & Analyze                                              ││
│  │  ───────────────────────────                                             ││
│  │  • Classify market tier                                                  ││
│  │  • Calculate supply/demand metrics                                       ││
│  │  • Identify regulatory factors                                           ││
│  │  • Generate market outlook                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  STEP 5: Store & Return                                                  ││
│  │  ─────────────────────────                                               ││
│  │  • Cache results in database                                             ││
│  │  • Update deal with market context                                       ││
│  │  • Return formatted data to UI                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│         │                                                                    │
│         ▼                                                                    │
│  Market Research Complete → Available for Screening, Analysis, Reports      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Cost Optimization

| Step | Method | Cost |
|------|--------|------|
| Geocoding | Google Maps or free alternative | ~$0.005 |
| Census data | Free API | $0 |
| BLS data | Free API | $0 |
| Walk Score | API | ~$0.01 |
| Perplexity | API (if cache miss) | ~$0.05-0.10 |
| **Total (cache miss)** | | **~$0.07-0.12** |
| **Total (cache hit)** | | **~$0.02** |

**Caching Strategy:**
- MSA-level data cached for 7 days
- Walk Score cached for 90 days
- Perplexity results cached by query hash for 24 hours
- Target: 70%+ cache hit rate to minimize costs

---

## 9. API Specifications

### 9.1 Market Research Endpoints

#### Get Market Data for Deal

```
GET /api/v1/deals/{deal_id}/market-research

Response (200 OK):
{
  "deal_id": "deal_xyz789",
  "msa": {
    "msaCode": "12420",
    "msaName": "Austin-Round Rock-Georgetown, TX",
    "primaryCity": "Austin",
    "state": "TX",
    "marketTier": "SECONDARY",
    "tierRationale": "Austin qualifies as a secondary market based on population of 2,300,000, 3.2% job growth, 2.1% population growth.",
    "population": 2300000,
    "populationGrowth1Yr": 0.021,
    "medianHouseholdIncome": 82500,
    "unemploymentRate": 0.031,
    "jobGrowth1Yr": 0.032,
    "topEmployers": [
      {"name": "University of Texas", "industry": "Education", "employeeCount": 24000},
      {"name": "Dell Technologies", "industry": "Technology", "employeeCount": 13000}
    ],
    "vacancyRate": 0.052,
    "avgRent2BR": 1485,
    "rentGrowth1Yr": 0.034,
    "unitsUnderConstruction": 18500,
    "rentControlStatus": "PREEMPTED",
    "landlordFriendlyRating": 8,
    "marketOutlook": "POSITIVE",
    "outlookRationale": "Strong job growth driven by tech sector..."
  },
  "submarket": {
    "submarketName": "East Austin",
    "vacancyRate": 0.048,
    "avgRent": 1520,
    "rentGrowth1Yr": 0.038,
    "strengths": ["Strong rental demand", "Tech employment nearby"],
    "weaknesses": ["Rising property taxes", "Gentrification concerns"]
  },
  "propertyLocation": {
    "walkScore": 72,
    "transitScore": 45,
    "bikeScore": 68,
    "nearbyEmployers": [...],
    "nearbyAmenities": {...}
  },
  "dataAsOf": "2025-12-20T10:30:00Z",
  "sources": ["Census Bureau", "BLS", "Walk Score", "Perplexity"],
  "llmCostCents": 8,
  "processingTimeMs": 45000
}
```

#### Refresh Market Data

```
POST /api/v1/deals/{deal_id}/market-research/refresh

Request Body:
{
  "force_refresh": true  // Bypass cache
}

Response (202 Accepted):
{
  "job_id": "mkt_job_123",
  "status": "PROCESSING",
  "estimated_time_seconds": 45
}
```

#### Get MSA Data (Standalone)

```
GET /api/v1/markets/msa/{msa_code}

Response (200 OK):
{
  "msaCode": "12420",
  "msaName": "Austin-Round Rock-Georgetown, TX",
  ...
}
```

#### Search Markets

```
GET /api/v1/markets/search?q=austin

Response (200 OK):
{
  "results": [
    {"msaCode": "12420", "msaName": "Austin-Round Rock-Georgetown, TX", "state": "TX"},
    {"msaCode": "12700", "msaName": "Austin, MN", "state": "MN"}
  ]
}
```

---

## 10. Database Schema

```sql
-- MSA data table
CREATE TABLE msa_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    msa_code VARCHAR(10) NOT NULL UNIQUE,
    msa_name VARCHAR(200) NOT NULL,
    primary_city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    
    -- Classification
    market_tier market_tier_enum NOT NULL,
    tier_rationale TEXT,
    
    -- Demographics
    population INTEGER,
    population_growth_1yr DECIMAL(5, 4),
    population_growth_5yr DECIMAL(5, 4),
    median_household_income INTEGER,
    median_age DECIMAL(4, 1),
    
    -- Employment
    total_employment INTEGER,
    unemployment_rate DECIMAL(5, 4),
    job_growth_1yr DECIMAL(5, 4),
    top_employers JSONB,
    key_industries TEXT[],
    
    -- Multifamily market
    multifamily_inventory INTEGER,
    vacancy_rate DECIMAL(5, 4),
    avg_rent_1br INTEGER,
    avg_rent_2br INTEGER,
    rent_growth_1yr DECIMAL(5, 4),
    rent_growth_5yr DECIMAL(5, 4),
    avg_cap_rate DECIMAL(5, 4),
    
    -- Supply
    units_under_construction INTEGER,
    units_delivered_12mo INTEGER,
    
    -- Regulatory
    rent_control_status rent_control_status_enum,
    landlord_friendly_rating INTEGER,
    regulatory_notes TEXT,
    
    -- Outlook
    market_outlook market_outlook_enum,
    outlook_rationale TEXT,
    
    -- Metadata
    data_as_of TIMESTAMPTZ NOT NULL,
    sources TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Submarket data table
CREATE TABLE submarket_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    msa_code VARCHAR(10) NOT NULL REFERENCES msa_data(msa_code),
    submarket_name VARCHAR(100) NOT NULL,
    
    -- Location
    boundaries TEXT,
    zip_codes TEXT[],
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Metrics
    vacancy_rate DECIMAL(5, 4),
    avg_rent INTEGER,
    avg_rent_psf DECIMAL(6, 2),
    rent_growth_1yr DECIMAL(5, 4),
    class_breakdown JSONB,
    
    -- Supply
    existing_units INTEGER,
    units_under_construction INTEGER,
    
    -- Assessment
    strengths TEXT[],
    weaknesses TEXT[],
    
    -- Metadata
    data_as_of TIMESTAMPTZ NOT NULL,
    sources TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_submarket UNIQUE (msa_code, submarket_name)
);

-- Property location data
CREATE TABLE property_location_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    -- Coordinates
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    
    -- Scores
    walk_score INTEGER,
    transit_score INTEGER,
    bike_score INTEGER,
    
    -- Nearby amenities
    nearby_amenities JSONB,
    nearby_employers JSONB,
    
    -- Risk factors
    flood_zone VARCHAR(10),
    crime_index DECIMAL(5, 2),
    
    -- Metadata
    data_as_of TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT one_location_per_deal UNIQUE (deal_id)
);

-- Market research jobs
CREATE TABLE market_research_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    
    status job_status_enum NOT NULL DEFAULT 'PENDING',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- Cost tracking
    llm_cost_cents INTEGER,
    api_calls JSONB,
    processing_time_ms INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_msa_code ON msa_data(msa_code);
CREATE INDEX idx_msa_state ON msa_data(state);
CREATE INDEX idx_msa_tier ON msa_data(market_tier);
CREATE INDEX idx_submarket_msa ON submarket_data(msa_code);
CREATE INDEX idx_property_location_deal ON property_location_data(deal_id);
```

---

## 11. Integration with Other Phases

### 11.1 Phase 2 (Screening) Integration

Market data informs:
- Market tier → Base IRR hurdle
- Vacancy trends → Occupancy risk assessment
- Rent growth → Revenue assumption validation
- Supply pipeline → Competition risk flag

### 11.2 Phase 4 (Pro Forma) Integration

Market data provides:
- Rent growth benchmarks for assumptions
- Expense benchmarks by market
- Cap rate ranges for exit assumptions
- Market-specific tax rates

### 11.3 Phase 6 (Reports) Integration

Market data populates:
- Market Analysis section of memos
- MSA overview with key metrics
- Submarket context
- Competitive positioning

---

## 12. Testing Requirements

### 12.1 Data Quality Tests

| Test | Description | Target |
|------|-------------|--------|
| Data completeness | All required fields populated | >80% |
| Data freshness | Data within acceptable age | 100% |
| Classification accuracy | Correct market tier | >95% |
| Source validation | Data matches sources | >90% |

### 12.2 Performance Tests

| Operation | Target | Method |
|-----------|--------|--------|
| Full market research | <60 seconds | Load test |
| Cache hit response | <2 seconds | Unit test |
| Walk Score lookup | <3 seconds | Integration test |
| Perplexity query | <30 seconds | Integration test |

### 12.3 Cost Tests

- Track actual costs per research
- Alert if costs exceed $0.20 per research
- Monthly cost report by data source

---

## 13. Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| Include crime data? | Deferred | Sensitive, consider carefully |
| School ratings? | Deferred | May not be relevant for multifamily |
| Historical charts? | Future | Requires data storage |
| Comp identification? | Future | Requires property database |

---

## 14. Rollout Plan

### Phase 3a: MSA Data (Week 3)
- Census integration
- BLS integration
- Market tier classification

### Phase 3b: Location Data (Week 3)
- Geocoding
- Walk Score integration
- Nearby amenities

### Phase 3c: Perplexity Integration (Week 3-4)
- Real-time market queries
- Caching layer
- Cost monitoring

### Phase 3d: UI & Integration (Week 4)
- Market research panel
- Integration with screening
- Integration with reports

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Author: DREAM AI Product Team*

