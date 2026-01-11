# DREAM Multi-Agent System Architecture
**Complete Technical Specification for Building a 100+ Agent Real Estate Analysis Platform**

---

## Executive Summary

### The Vision
Transform Dream from a manual-dependent underwriting tool into an intelligent multi-agent system that orchestrates 100+ specialized agents to analyze multifamily real estate deals across all phases:

1. **Initial Screening** - Back-of-the-envelope analysis
2. **Full Underwriting** - Comprehensive deal evaluation
3. **Investment Memo** - IC package preparation
4. **Due Diligence Execution** - Post-LOI/PSA diligence tracking and risk mitigation

### The Core Problem
The Shieldstone Manual v2 provides:
- ✅ Excellent natural language methodology for humans
- ✅ Python code for key calculations
- ❌ **But raw LLM + manual + code is NOT enough for production-grade underwriting**

### The Solution
Build a **master agent/subagent architecture** where:
- Users interact with ONE conversational interface
- Behind the scenes, 100+ specialized agents execute based on Shieldstone's 8 phases
- Super agents manage the registry and orchestrate workflows
- Each deal phase triggers appropriate agent teams
- Agents learn from your underwriting criteria and adapt

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Technology Stack](#technology-stack)
4. [Infrastructure & Hosting](#infrastructure--hosting)
5. [Multi-Agent Orchestration](#multi-agent-orchestration)
6. [Agent Design Patterns](#agent-design-patterns)
7. [Shieldstone Integration](#shieldstone-integration)
8. [Development Workflow](#development-workflow)
9. [Cost Analysis](#cost-analysis)
10. [Implementation Roadmap](#implementation-roadmap)

---

## System Overview

### What DREAM.AI Does

DREAM.AI appears to users as a single intelligent assistant but orchestrates 100+ specialized agents behind the scenes.

**User Experience:**
```
User: "Should I buy this property?"
      [uploads rent roll, OM, T12]

DREAM.AI: "Based on my comprehensive analysis of Pine Grove Apartments,
I recommend passing on this opportunity. The rent roll shows 77% occupancy
well below the 94% submarket average, market research indicates 847 new
competing units added recently, and the pro forma assumes unrealistic 15%
rent growth when comparables show flat to declining rents..."
```

**What Actually Happens:**
1. Orchestrator agent receives request
2. Plans execution using Claude (determines which of 100 agents to call)
3. Executes 8-15 agents in parallel stages
4. Synthesizes all results into one conversational response
5. **User never knows multiple agents were involved**

### Core Value Proposition

**For Users:**
- ✅ Single conversational interface (like ChatGPT)
- ✅ Upload files (rent rolls, OMs, financials, third-party reports)
- ✅ Ask natural language questions
- ✅ Get comprehensive, professional analysis
- ✅ No knowledge of underlying complexity

**For You (Platform Owner):**
- ✅ Modular agent architecture (easy to add/update agents)
- ✅ Multi-tenant (one server serves 50-500 customers)
- ✅ Customer-specific configurations (each customer's own underwriting criteria)
- ✅ Scalable infrastructure
- ✅ Usage-based billing capability
- ✅ Shieldstone methodology embedded in every agent

---

## Architecture Principles

### 1. Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│              (Chat interface - web/mobile)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ Natural language + files
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR LAYER                              │
│  - Receives user request                                    │
│  - Plans which agents to use (via Claude)                   │
│  - Manages execution flow                                   │
│  - Synthesizes final response                               │
└────────────────────┬────────────────────────────────────────┘
                     │ Executes plan
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION LAYER (LangGraph)                     │
│  - Runs agents in parallel/sequential stages                │
│  - Manages state between agents                             │
│  - Handles dependencies                                     │
└────────────────────┬────────────────────────────────────────┘
                     │ Calls individual agents
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENT LAYER (100+ Agents)                       │
│  - Specialized agents mapped to Shieldstone phases          │
│  - Each agent is independent                                │
│  - Agents read from shared state, write results back        │
└────────────────────┬────────────────────────────────────────┘
                     │ Uses AI APIs + Shieldstone Python
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AI SERVICES + COMPUTATION LAYER                 │
│  - Claude API (primary - Sonnet 4.5)                        │
│  - Gemini API (batch processing, cheaper tasks)             │
│  - Perplexity API (real-time market data)                   │
│  - Shieldstone Python modules (calculations)                │
└─────────────────────────────────────────────────────────────┘
```

### 2. Multi-Tenancy Design

**One server, many customers, same codebase:**

```python
# Same agent code for all customers
class RentRollAgent:
    def __init__(self, customer_config):
        self.config = customer_config  # Different per customer!
        self.shieldstone_rules = load_shieldstone_manual()

    def analyze(self, rent_roll_data):
        # Use customer-specific criteria overlaid on Shieldstone methodology
        min_occupancy = self.config['min_occupancy']  # Customer A: 0.95, Customer B: 0.90
        target_irr = self.config['target_irr']        # Customer A: 0.15, Customer B: 0.12

        # Apply Shieldstone Phase 1 analysis principles
        analysis = self.shieldstone_rules.phase1.analyze_rent_roll(
            rent_roll_data,
            min_occupancy,
            target_irr
        )

        return analysis

# Database stores customer-specific configs
Customer A (USDV Capital):
  config: {
    "min_occupancy": 0.95,
    "target_irr": 0.15,
    "markets": ["Atlanta"],
    "shieldstone_overrides": {...}
  }

Customer B (ABC Fund):
  config: {
    "min_occupancy": 0.90,
    "target_irr": 0.12,
    "markets": ["Phoenix"],
    "shieldstone_overrides": {...}
  }
```

### 3. State Management

All agents share a common state object (managed by LangGraph):

```python
class AgentState(TypedDict):
    # User context
    user_message: str
    customer_id: str
    customer_config: Dict[str, Any]
    uploaded_files: Dict[str, bytes]
    deal_phase: str  # 'screening', 'underwriting', 'memo', 'diligence'

    # Agent execution
    agents_completed: List[str]
    current_stage: int

    # Shieldstone Phase Results (mapped to 8 phases)
    phase1_property_fundamentals: Optional[Dict]
    phase2_market_analysis: Optional[Dict]
    phase3_financial_modeling: Optional[Dict]
    phase4_risk_assessment: Optional[Dict]
    phase5_value_add_strategy: Optional[Dict]
    phase6_financing_structure: Optional[Dict]
    phase7_investment_returns: Optional[Dict]
    phase8_exit_strategy: Optional[Dict]

    # Agent-specific results (100+ result fields)
    rent_roll_analysis: Optional[Dict]
    om_analysis: Optional[Dict]
    market_research: Optional[Dict]
    pro_forma: Optional[Dict]
    third_party_reports: Optional[Dict]
    diligence_tracker: Optional[Dict]
    # ... 100+ result fields

    # Final output
    final_response: str

    # Metadata
    total_tokens_used: int
    total_cost: float
    shieldstone_compliance_score: float
```

**Flow:**
1. Orchestrator creates initial state
2. Agent A reads state, writes results to state
3. Agent B reads state (including Agent A's results), writes results
4. Continue through all agents
5. Synthesizer reads entire state, creates final response

---

## Technology Stack

### Core Technologies

**Backend Framework:**
- **FastAPI** (Python web framework)
- Handles API endpoints, authentication, routing

**Agent Orchestration:**
- **LangGraph** (built by LangChain team)
- Manages multi-agent workflows
- Handles parallel execution, dependencies, state

**AI APIs:**
- **Anthropic Claude SDK** (primary - Sonnet 4.5)
- **Google Gemini API** (secondary - cheaper for simple tasks)
- **Perplexity API** (real-time web search)

**Database:**
- **PostgreSQL** (customer data, configs, usage logs, deal history)
- **Redis** (caching agent results)

**Infrastructure:**
- **Docker** (containerization)
- **Railway/DigitalOcean/Hetzner** (hosting)

### Key Dependencies

```txt
# requirements.txt

# FastAPI & Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Caching
redis==5.0.1

# AI SDKs
anthropic==0.18.1
google-generativeai==0.3.2
openai==1.12.0

# Agent Orchestration
langgraph==0.2.0
langchain-anthropic==0.1.0
langchain-core==0.2.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1

# Utilities
pydantic==2.5.3
pandas==2.2.0
openpyxl==3.1.2
PyPDF2==3.0.1
numpy==1.26.4
scipy==1.12.0

# Shieldstone Integration
# (Your existing Python modules)
```

---

## Infrastructure & Hosting

### Hosting Options Ranked

#### Option 1: Railway (Recommended for MVP)
**Cost:** $5-20/month
**Setup Time:** 10 minutes
**Difficulty:** Easiest

**Pros:**
- ✅ Connect GitHub, auto-deploys on git push
- ✅ Automatic HTTPS, domains, environment variables
- ✅ Zero DevOps knowledge needed
- ✅ Built-in PostgreSQL and Redis

**Cons:**
- ❌ Slightly more expensive than raw VPS

**Setup:**
```bash
1. Push code to GitHub
2. Go to railway.app
3. "New Project" → "Deploy from GitHub"
4. Select repo
5. Add environment variables (API keys)
6. Deploy
# Done - your API is live at https://your-app.up.railway.app
```

#### Option 2: Hetzner VPS (Cheapest)
**Cost:** €4.49/month (~$5)
**Setup Time:** 1-2 hours
**Difficulty:** Moderate

**Pros:**
- ✅ Cheapest option
- ✅ Full control
- ✅ Good performance

**Cons:**
- ❌ Manual setup
- ❌ Europe-based (higher latency from US)
- ❌ You manage everything

#### Option 3: DigitalOcean (Industry Standard)
**Cost:** $6-24/month
**Setup Time:** 1-2 hours
**Difficulty:** Moderate

**Pros:**
- ✅ Industry standard, reliable
- ✅ Great documentation
- ✅ Managed databases available

**Cons:**
- ❌ Manual setup
- ❌ More expensive than Hetzner

### Single Server Architecture

**You do NOT need multiple servers for 50-500 customers.**

```
┌─────────────────────────────────────────────────────────────┐
│         ONE SERVER ($5-24/month)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  FastAPI Application (Port 8000)                   │    │
│  │  - All 100+ agents                                 │    │
│  │  - Orchestrator                                    │    │
│  │  - API endpoints                                   │    │
│  │  - Shieldstone Python modules                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PostgreSQL Database                               │    │
│  │  - Customer accounts                               │    │
│  │  - Customer configs                                │    │
│  │  - Usage logs                                      │    │
│  │  - Deal history                                    │    │
│  │  - Diligence tracking                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Redis Cache                                       │    │
│  │  - Agent result caching                            │    │
│  │  - Customer config caching                         │    │
│  │  - Shieldstone manual caching                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Capacity:**
- Single $24/month server handles 10,000-50,000 API calls/month
- 50 customers × 40 calls/month = 2,000 calls (well under capacity)
- Most time is spent waiting for Claude API (not CPU/RAM)

### Docker Deployment

```yaml
# docker-compose.yml

version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
      - DATABASE_URL=postgresql://dreamai:password@db:5432/dreamai
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./shieldstone:/app/shieldstone
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=dreamai
      - POSTGRES_USER=dreamai
      - POSTGRES_PASSWORD=password
    restart: unless-stopped

  redis:
    image: redis:7
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

**Deploy:**
```bash
# On your server
git clone https://github.com/yourusername/dream-agents.git
cd dream-agents
docker-compose up -d

# Your API is now running at http://server-ip:8000
```

---

## Multi-Agent Orchestration

### Core Orchestration Pattern

```
User Request
    ↓
Orchestrator Agent (Claude-powered + Shieldstone-aware)
    ↓
Analyzes deal phase & creates execution plan
    ↓
LangGraph Executes Plan
    ↓
    ├─ Stage 1 (Parallel): Phase 1 Agents (Property Fundamentals)
    ├─ Stage 2 (Parallel): Phase 2 Agents (Market Analysis)
    ├─ Stage 3 (Parallel): Phase 3 Agents (Financial Modeling)
    ├─ Stage 4 (Sequential): Phase 4-8 Agents (Risk, Strategy, Returns)
    └─ Stage 5: Synthesizer Agent (Shieldstone-compliant response)
    ↓
Conversational Response
```

### Orchestrator Agent Responsibilities

#### 1. Intent Understanding + Phase Detection

```python
User: "Should I buy this property?"

Orchestrator analyzes:
- User wants investment recommendation
- Deal phase: Initial screening (not full underwriting yet)
- Has uploaded: rent_roll.xlsx, om.pdf, t12.pdf
- Shieldstone phases needed: 1, 2, 3, 7 (fundamentals, market, financials, returns)
- Skip phases 4-6 for now (deep risk, value-add strategy - only if user wants full underwriting)
```

#### 2. Agent Selection (Shieldstone-Mapped)

```python
# Orchestrator uses Claude to pick agents based on Shieldstone phases
planning_prompt = """
User request: "Should I buy this property?"
Uploaded files: rent_roll.xlsx, om.pdf, t12.pdf
Deal phase: SCREENING

Available agents mapped to Shieldstone Manual v2:

PHASE 1 - Property Fundamentals:
- rent_roll_analyzer
- om_analyzer
- t12_analyzer
- property_condition_assessor

PHASE 2 - Market Analysis:
- market_research_agent
- demographic_analyzer
- supply_demand_analyzer
- comparable_sales_agent

PHASE 3 - Financial Modeling:
- pro_forma_builder
- revenue_optimizer
- expense_analyzer

PHASE 7 - Investment Returns:
- irr_calculator
- cash_flow_analyzer
- equity_multiple_calculator

Which agents should we use? In what order? This is a SCREENING request.
"""

# Claude responds with execution plan
plan = {
    "deal_phase": "screening",
    "shieldstone_phases": [1, 2, 3, 7],
    "stages": [
        {
            "name": "Phase 1: Property Fundamentals",
            "agents": ["rent_roll_analyzer", "om_analyzer", "t12_analyzer"],
            "parallel": true
        },
        {
            "name": "Phase 2: Market Analysis",
            "agents": ["market_research_agent", "comparable_sales_agent"],
            "parallel": true
        },
        {
            "name": "Phase 3 & 7: Financial Returns",
            "agents": ["pro_forma_builder", "irr_calculator"],
            "parallel": false,
            "depends_on": ["rent_roll_analyzer", "market_research_agent"]
        },
        {
            "name": "Synthesis",
            "agents": ["shieldstone_synthesizer"],
            "parallel": false
        }
    ]
}
```

#### 3. Execution Management

LangGraph executes the plan:
- Parallel agents run simultaneously (faster)
- Sequential agents wait for dependencies
- State passed between all agents
- Errors handled gracefully
- **Shieldstone compliance checked at each phase**

#### 4. Response Synthesis (Shieldstone-Compliant)

```python
# After all agents complete, synthesizer creates response using Shieldstone framework
synthesizer_prompt = """
User asked: "Should I buy this property?"

Shieldstone Phase Results:

PHASE 1 - Property Fundamentals:
- Rent roll: 77% occupancy, $1,450 avg rent, 15 vacant units >90 days
- OM analysis: 192 units, built 1985, $12M asking price ($62.5K/unit)
- T12: NOI $890K, OpEx $4,650/unit

PHASE 2 - Market Analysis:
- Market research: 847 new competing units added in submarket, rents flat YoY
- Comps: Recent sales $55-60K/unit at 92%+ occupancy

PHASE 3 - Financial Modeling:
- Pro forma: Projects 14.2% IRR assuming 95% occupancy and 4% rent growth

PHASE 7 - Investment Returns:
- IRR: 14.2% (leveraged), 9.8% (unleveraged)
- Cash-on-cash: Year 1: 6.2%, stabilized: 9.1%
- Equity multiple: 2.1x over 5 years

Synthesize into conversational response following Shieldstone methodology.
Be direct and actionable. Structure: Overview → Key Findings → Recommendation.
"""

# Claude creates final response
final_response = """
Based on my comprehensive Shieldstone analysis of Pine Grove Apartments,
I recommend passing on this opportunity. Here's why:

**Property Fundamentals (Phase 1):**
The rent roll reveals concerning fundamentals. At 77% occupancy vs. 94% submarket
average, this property is significantly underperforming. More troubling, 15 units
have been vacant for >90 days, suggesting deeper issues than normal turnover.

**Market Conditions (Phase 2):**
The submarket has absorbed 847 new competing units in the past 18 months, and
comparable properties are trading at $55-60K/unit with 92%+ occupancy. At $62.5K/unit,
this asset is priced at a premium despite inferior performance.

**Financial Analysis (Phase 3 & 7):**
The pro forma assumes stabilization to 95% occupancy and 4% annual rent growth,
projecting a 14.2% IRR. However, this is unrealistic given flat market rents and
significant new supply. A realistic scenario (85% stabilized occupancy, 2% growth)
yields an 8.9% IRR—below your 15% target.

**Recommendation:**
Pass. The deal only works with aggressive, unsupported assumptions. The risk-adjusted
return does not justify the execution risk in a oversupplied, flat-rent environment.
"""
```

### LangGraph Workflow Patterns

#### Pattern 1: Simple Sequential (Basic Deal Flow)

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Add agents as nodes (following Shieldstone phases)
workflow.add_node("phase1_rent_roll", rent_roll_node)
workflow.add_node("phase1_om", om_analyzer_node)
workflow.add_node("phase3_proforma", pro_forma_node)
workflow.add_node("phase7_returns", returns_calculator_node)
workflow.add_node("synthesizer", shieldstone_synthesizer_node)

# Define flow
workflow.set_entry_point("phase1_rent_roll")
workflow.add_edge("phase1_rent_roll", "phase1_om")
workflow.add_edge("phase1_om", "phase3_proforma")
workflow.add_edge("phase3_proforma", "phase7_returns")
workflow.add_edge("phase7_returns", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile and run
app = workflow.compile()
result = app.invoke(initial_state)
```

**Visualization:**
```
START → Phase1_RentRoll → Phase1_OM → Phase3_ProForma → Phase7_Returns → Synthesizer → END
```

#### Pattern 2: Parallel Execution (Full Underwriting)

```python
workflow = StateGraph(AgentState)

# Stage 1: Parallel Phase 1 agents (Property Fundamentals)
workflow.add_node("rent_roll", rent_roll_node)
workflow.add_node("om_analyzer", om_analyzer_node)
workflow.add_node("t12_analyzer", t12_analyzer_node)
workflow.add_node("property_condition", property_condition_node)

# Stage 2: Parallel Phase 2 agents (Market Analysis)
workflow.add_node("market_research", market_research_node)
workflow.add_node("demographics", demographic_node)
workflow.add_node("comps", comparable_sales_node)

# Stage 3: Phase 3 (depends on Phase 1 & 2)
workflow.add_node("pro_forma", pro_forma_node)

# Stage 4: Synthesis
workflow.add_node("synthesizer", shieldstone_synthesizer_node)

# Flow: All Phase 1 agents run in parallel, then all Phase 2, etc.
workflow.set_entry_point("rent_roll")

# Phase 1 → Phase 2
for phase1_agent in ["rent_roll", "om_analyzer", "t12_analyzer", "property_condition"]:
    for phase2_agent in ["market_research", "demographics", "comps"]:
        workflow.add_edge(phase1_agent, phase2_agent)

# Phase 2 → Phase 3
for phase2_agent in ["market_research", "demographics", "comps"]:
    workflow.add_edge(phase2_agent, "pro_forma")

workflow.add_edge("pro_forma", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()
```

**Visualization:**
```
                    START
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
    rent_roll    om_analyzer   t12_analyzer
        │             │             │
        └─────────────┼─────────────┘
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   market_research demographics   comps
        │             │             │
        └─────────────┼─────────────┘
                      ↓
                  pro_forma
                      ↓
                 synthesizer
                      ↓
                     END
```

**Runtime:** ~20 seconds (vs 60+ seconds sequential)

#### Pattern 3: Conditional Routing (Smart Screening)

```python
def should_continue_analysis(state: AgentState) -> str:
    """Decide next step based on Shieldstone Phase 1 screening"""
    rent_roll = state.get('phase1_property_fundamentals', {}).get('rent_roll', {})

    # Shieldstone Phase 1 kill criteria
    occupancy = rent_roll.get('occupancy', 1.0)
    revenue_per_unit = rent_roll.get('revenue_per_unit_annual', 999999)

    customer_minimums = state['customer_config']

    if occupancy < customer_minimums.get('min_occupancy', 0.80):
        return "reject"  # Skip detailed analysis - fundamentals failed
    elif revenue_per_unit < customer_minimums.get('min_revenue_per_unit', 8000):
        return "reject"  # Revenue too low
    else:
        return "continue"  # Proceed to full Shieldstone analysis

workflow = StateGraph(AgentState)

workflow.add_node("phase1_screening", phase1_screening_node)
workflow.add_node("full_underwriting", full_underwriting_branch)
workflow.add_node("quick_reject", quick_reject_node)
workflow.add_node("synthesizer", shieldstone_synthesizer_node)

workflow.set_entry_point("phase1_screening")

# Conditional routing based on Phase 1 results
workflow.add_conditional_edges(
    "phase1_screening",
    should_continue_analysis,
    {
        "continue": "full_underwriting",
        "reject": "quick_reject"
    }
)

workflow.add_edge("full_underwriting", "synthesizer")
workflow.add_edge("quick_reject", "synthesizer")
workflow.add_edge("synthesizer", END)
```

**Visualization:**
```
           START
             ↓
      phase1_screening
             ↓
        [DECISION]
         /       \
        ↓         ↓
    full_UW    quick_reject
        ↓         ↓
         \       /
       synthesizer
             ↓
            END
```

#### Pattern 4: Dynamic Workflow Builder (Shieldstone-Aware)

The most powerful pattern - let Claude build workflows on the fly based on deal phase and Shieldstone methodology:

```python
class ShieldstoneDynamicWorkflowBuilder:
    """Claude decides which Shieldstone phases and agents to use for each request"""

    def __init__(self, shieldstone_manual):
        self.manual = shieldstone_manual
        self.agent_registry = AGENT_REGISTRY

    def build_workflow(self, user_message: str, context: dict):
        # Ask Claude to create execution plan based on Shieldstone methodology
        plan = self.plan_workflow(user_message, context)

        # Convert plan to LangGraph workflow
        workflow = self.create_langgraph_from_plan(plan)

        return workflow

    def plan_workflow(self, user_message: str, context: dict):
        planning_prompt = f"""
        User request: "{user_message}"
        Available data: {context}
        Deal phase: {context.get('deal_phase', 'unknown')}

        Shieldstone Manual v2 has 8 phases:
        {self.get_shieldstone_phase_summary()}

        Available agents mapped to phases:
        {self.list_agents_by_phase()}

        Create optimal execution plan following Shieldstone methodology:
        - Use only necessary phases for the user's request
        - For screening: Phases 1, 2, 3, 7
        - For full underwriting: All 8 phases
        - For due diligence: Phases 4, 6, 8 + diligence-specific agents
        - Maximize parallelization within each phase
        - Minimize cost and runtime

        Return JSON execution plan.
        """

        response = claude.messages.create(...)
        return json.loads(response.content[0].text)

    def get_shieldstone_phase_summary(self):
        return """
        Phase 1: Property Fundamentals (rent roll, unit mix, physical condition)
        Phase 2: Market Analysis (supply/demand, demographics, trends)
        Phase 3: Financial Modeling (pro forma, revenue optimization)
        Phase 4: Risk Assessment (market risk, execution risk, structural risk)
        Phase 5: Value-Add Strategy (renovation, repositioning, operational improvements)
        Phase 6: Financing Structure (debt, equity, returns optimization)
        Phase 7: Investment Returns (IRR, cash-on-cash, equity multiple)
        Phase 8: Exit Strategy (hold period, disposition, market timing)
        """
```

**Example:**

```
User: "Quick check - is this rent roll clean?"

Claude plans:
- deal_phase: "screening"
- shieldstone_phases: [1]
- agents: ["rent_roll_analyzer"]
- stages: 1
- estimated_cost: $0.01
- estimated_runtime: 5 seconds

vs.

User: "Full investment committee package for Pine Grove"

Claude plans:
- deal_phase: "full_underwriting"
- shieldstone_phases: [1, 2, 3, 4, 5, 6, 7, 8]
- agents: [30+ agents across all phases]
- estimated_cost: $0.60
- estimated_runtime: 75 seconds

vs.

User: "We're under contract - help me track due diligence"

Claude plans:
- deal_phase: "diligence"
- shieldstone_phases: [4, 6, 8]  # Risk, financing, exit
- agents: ["diligence_tracker", "third_party_report_analyzer", "risk_mitigation_agent", ...]
- estimated_cost: $0.20
- estimated_runtime: 30 seconds
```

---

## Agent Design Patterns

### Base Agent Class

Every agent inherits from this and integrates Shieldstone methodology:

```python
from anthropic import Anthropic
from typing import Dict, Any, Optional
import json

class BaseAgent:
    """Base class for all DREAM.AI agents"""

    def __init__(self, customer_config: Optional[Dict[str, Any]] = None):
        self.config = customer_config or {}
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"
        self.shieldstone_manual = load_shieldstone_manual()

    def get_system_prompt(self) -> str:
        """Override in subclasses - should include Shieldstone context"""
        return "You are a helpful AI assistant."

    def get_shieldstone_phase(self) -> Optional[int]:
        """Override to map agent to Shieldstone phase (1-8)"""
        return None

    def should_cache_prompt(self) -> bool:
        """Whether to use prompt caching (90% savings)"""
        return True

    def run(self, user_message: str, max_tokens: int = 4000) -> Dict[str, Any]:
        """Execute agent"""
        system_prompt = self.get_system_prompt()

        # Use prompt caching for large system prompts (Shieldstone manual is large!)
        if self.should_cache_prompt() and len(system_prompt) > 1000:
            system = [{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}  # 90% cost reduction!
            }]
        else:
            system = system_prompt

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}]
        )

        return {
            "result": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cache_read_tokens": getattr(response.usage, "cache_read_input_tokens", 0)
            }
        }
```

### Example Specialized Agents (Shieldstone-Mapped)

#### Rent Roll Analyzer Agent (Phase 1: Property Fundamentals)

```python
class RentRollAgent(BaseAgent):
    """Analyzes rent rolls with customer-specific criteria + Shieldstone Phase 1 methodology"""

    def get_shieldstone_phase(self) -> int:
        return 1  # Property Fundamentals

    def get_system_prompt(self) -> str:
        # Customer-specific underwriting rules from config
        rules = self.config.get('underwriting_rules', {})

        # Load Shieldstone Phase 1 guidance
        phase1_guidance = self.shieldstone_manual.get_phase(1)

        return f"""You are a multifamily real estate underwriting specialist following the Shieldstone Manual v2 methodology.

# SHIELDSTONE PHASE 1: PROPERTY FUNDAMENTALS

{phase1_guidance}

# CUSTOMER'S INVESTMENT CRITERIA

{json.dumps(rules, indent=2)}

# YOUR TASK

Analyze rent rolls following Shieldstone Phase 1 principles and provide:

1. **Unit Mix Summary**
   - Total units by type (studio, 1BR, 2BR, 3BR)
   - Average rent by unit type
   - Occupied vs vacant units
   - Average lease term and expiration clustering

2. **Revenue Analysis**
   - Gross potential rent (GPR)
   - Effective gross income (EGI)
   - Loss-to-lease analysis (market rent vs in-place rent)
   - Other income (parking, pet fees, utilities, etc.)

3. **Red Flags** (per Shieldstone criteria)
   - Occupancy below market (< {rules.get('min_occupancy', 0.90) * 100}%)
   - Units vacant > 90 days
   - Rent significantly below market comps
   - Lease expiration clustering (>25% in single quarter)
   - Concessions or rent specials indicating weak demand

4. **Investment Metrics**
   - Revenue per unit (annual)
   - Revenue per square foot
   - Average rent as % of market rent
   - Potential revenue upside

5. **Recommendations**
   - Pricing opportunities (undermarket units)
   - Value-add potential (renovation, amenities)
   - Operational concerns

Return analysis as JSON with these exact keys:
unit_mix, revenue_analysis, red_flags, metrics, recommendations, shieldstone_compliance_notes
"""

    def analyze(self, rent_roll_data: str) -> Dict[str, Any]:
        """Analyze rent roll using Shieldstone Phase 1 methodology"""
        prompt = f"""Analyze this rent roll following Shieldstone Phase 1 methodology:

{rent_roll_data}

Return your analysis as JSON."""

        result = self.run(prompt)

        # Parse JSON response
        try:
            result['parsed_analysis'] = json.loads(result['result'])
        except:
            result['parsed_analysis'] = None

        return result
```

#### Market Research Agent (Phase 2: Market Analysis)

```python
class MarketResearchAgent(BaseAgent):
    """Researches market conditions using Perplexity for real-time data + Shieldstone Phase 2"""

    def get_shieldstone_phase(self) -> int:
        return 2  # Market Analysis

    def __init__(self, customer_config):
        super().__init__(customer_config)
        self.perplexity_key = settings.perplexity_api_key

    def research(self, location: str, property_type: str, submarket: str = None) -> Dict[str, Any]:
        """Research market using Perplexity + Claude synthesis + Shieldstone Phase 2"""

        # Load Shieldstone Phase 2 guidance
        phase2_guidance = self.shieldstone_manual.get_phase(2)

        # Use Perplexity for real-time web search
        perplexity_result = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {self.perplexity_key}"},
            json={
                "model": "sonar-pro",
                "messages": [{
                    "role": "user",
                    "content": f"""Research current market conditions for {property_type} in {location}
                    {f'(specifically {submarket} submarket)' if submarket else ''}.

                    Find:
                    - Current average rent trends (last 12 months)
                    - New supply (units delivered, under construction, planned)
                    - Vacancy rates (current and trend)
                    - Recent comparable sales (cap rates, price per unit)
                    - Economic and demographic trends
                    - Major employers and job growth
                    """
                }]
            }
        )

        market_data = perplexity_result.json()['choices'][0]['message']['content']

        # Use Claude to structure the data per Shieldstone Phase 2
        structure_prompt = f"""
        # SHIELDSTONE PHASE 2: MARKET ANALYSIS

        {phase2_guidance}

        # RAW MARKET RESEARCH DATA

        {market_data}

        Structure this market research data following Shieldstone Phase 2 framework.

        Return JSON with:
        - market_overview: Summary of market conditions
        - supply_demand: Current supply, demand drivers, absorption rates, pipeline
        - rent_trends: Historical trends, current rates, projections
        - demographic_analysis: Population, income, employment, growth
        - comparable_sales: Recent transactions with cap rates and pricing
        - risk_factors: Market risks per Shieldstone criteria
        - market_strength_score: 1-10 scale based on Shieldstone methodology
        """

        result = self.run(structure_prompt)
        result['raw_research'] = market_data

        return result
```

#### Pro Forma Builder Agent (Phase 3: Financial Modeling)

```python
class ProFormaAgent(BaseAgent):
    """Builds 10-year financial projections using Shieldstone Phase 3 + Python calculations"""

    def get_shieldstone_phase(self) -> int:
        return 3  # Financial Modeling

    def get_system_prompt(self) -> str:
        assumptions = self.config.get('proforma_assumptions', {})
        phase3_guidance = self.shieldstone_manual.get_phase(3)

        return f"""You are a real estate financial modeling expert following Shieldstone Phase 3 methodology.

# SHIELDSTONE PHASE 3: FINANCIAL MODELING

{phase3_guidance}

# CUSTOMER'S PRO FORMA ASSUMPTIONS

{json.dumps(assumptions, indent=2)}

# YOUR TASK

Build comprehensive 10-year pro forma with:

1. **Revenue Projections**
   - Base rent (with annual growth rates per Shieldstone)
   - Other income (parking, pet fees, utilities, laundry, etc.)
   - Vacancy & credit loss (per market standards)
   - Effective Gross Income (EGI)

2. **Operating Expenses** (by category with Shieldstone benchmarks)
   - Property management (% of EGI)
   - Payroll & benefits
   - Repairs & maintenance (per unit or % of EGI)
   - Utilities
   - Marketing & leasing
   - Property taxes (with annual growth)
   - Insurance
   - Other expenses
   - Total OpEx with annual growth rates

3. **Net Operating Income (NOI)**
   - EGI - OpEx
   - NOI margin analysis

4. **Cash Flow Analysis**
   - NOI - debt service (if leveraged)
   - Capital reserves
   - Cash available for distribution

5. **Investment Returns** (Shieldstone Phase 7 preview)
   - Cash-on-cash return (annual)
   - Unlevered IRR
   - Levered IRR
   - Equity multiple
   - Exit assumptions (cap rate, year)

Use the Shieldstone Python calculation modules where applicable.

Return complete year-by-year projections as JSON.
"""

    def build(self, property_data: dict, acquisition_details: dict) -> dict:
        """Build pro forma from property and acquisition data using Shieldstone calculations"""

        # First, use Claude to structure the data
        prompt = f"""
        Build 10-year pro forma for this property following Shieldstone Phase 3:

        Property Data: {json.dumps(property_data, indent=2)}
        Acquisition: {json.dumps(acquisition_details, indent=2)}

        Return detailed JSON pro forma.
        """

        result = self.run(prompt, max_tokens=8000)

        # Parse Claude's response
        try:
            parsed = json.loads(result['result'])
        except:
            parsed = None

        # THEN, validate and augment with Shieldstone Python calculations
        if parsed:
            # Import Shieldstone calculation modules
            from shieldstone.calculations import (
                calculate_noi,
                calculate_irr,
                calculate_cash_on_cash,
                calculate_equity_multiple
            )

            # Run Python calculations to validate Claude's math
            validated_proforma = self.validate_with_shieldstone_python(parsed)
            result['parsed_proforma'] = validated_proforma
        else:
            result['parsed_proforma'] = None

        return result

    def validate_with_shieldstone_python(self, claude_proforma: dict) -> dict:
        """Use Shieldstone Python modules to validate Claude's calculations"""
        # This is where you integrate your existing Shieldstone Python code
        # to ensure calculations are precise and consistent

        # Example:
        # validated_noi = calculate_noi(
        #     gross_income=claude_proforma['year_1']['gross_income'],
        #     vacancy_rate=claude_proforma['assumptions']['vacancy_rate'],
        #     operating_expenses=claude_proforma['year_1']['opex']
        # )

        # if abs(validated_noi - claude_proforma['year_1']['noi']) > 100:
        #     # Significant discrepancy - use Python calculation
        #     claude_proforma['year_1']['noi'] = validated_noi
        #     claude_proforma['validation_notes'] = "NOI recalculated using Shieldstone Python"

        return claude_proforma
```

#### Diligence Tracker Agent (Post-LOI/PSA Phase)

```python
class DiligenceTrackerAgent(BaseAgent):
    """Tracks due diligence progress and compares third-party reports to original underwriting"""

    def get_shieldstone_phase(self) -> int:
        return 4  # Risk Assessment (during diligence)

    def get_system_prompt(self) -> str:
        return """You are a due diligence management specialist following Shieldstone risk assessment methodology.

# YOUR ROLE

Once a property is under contract (LOI/PSA signed), you help track and analyze:

1. **Due Diligence Checklist**
   - Physical inspection (property condition assessment - PCA)
   - Environmental (Phase I ESA, Phase II if needed)
   - Survey and title review
   - Rent roll verification
   - Financial audit (T12, T3, bank statements)
   - Lease audits
   - Vendor contracts review
   - Litigation/permits/violations check

2. **Third-Party Report Analysis**
   - Compare findings to original underwriting assumptions
   - Identify material discrepancies
   - Quantify financial impact of new information

3. **Risk Assessment & Mitigation**
   - Categorize risks (deal-breaker, negotiable, acceptable)
   - Recommend price adjustments or credit requests
   - Suggest risk mitigation strategies

4. **Go/No-Go Recommendation**
   - Based on Shieldstone risk framework
   - Support decision to proceed, renegotiate, or terminate

Return analysis as JSON with: diligence_status, report_findings, risk_matrix,
financial_impact, recommendations
"""

    def track_diligence(self,
                       original_underwriting: dict,
                       third_party_reports: dict,
                       diligence_checklist: dict) -> dict:
        """Compare third-party reports to original underwriting"""

        prompt = f"""
        Analyze due diligence findings vs. original underwriting:

        **Original Underwriting:**
        {json.dumps(original_underwriting, indent=2)}

        **Third-Party Reports:**
        {json.dumps(third_party_reports, indent=2)}

        **Diligence Checklist Status:**
        {json.dumps(diligence_checklist, indent=2)}

        Identify discrepancies, assess risk impact, and provide recommendations.
        """

        result = self.run(prompt, max_tokens=6000)

        try:
            result['parsed_analysis'] = json.loads(result['result'])
        except:
            result['parsed_analysis'] = None

        return result
```

#### Shieldstone Synthesizer Agent (Cross-Phase Integration)

```python
class ShieldstoneSynthesizerAgent(BaseAgent):
    """Synthesizes all agent results into cohesive Shieldstone-compliant response"""

    def get_system_prompt(self) -> str:
        return """You are an expert real estate investment analyst synthesizing multi-agent analysis.

# YOUR ROLE

You receive results from 10-30 specialized agents that have analyzed a property following
the Shieldstone Manual v2 methodology (Phases 1-8).

Your job is to:

1. **Synthesize findings** across all Shieldstone phases into a cohesive narrative
2. **Identify key insights** and critical decision factors
3. **Make clear recommendation** (Buy, Pass, or Conditional)
4. **Structure response** for the user's deal phase:
   - **Screening:** Quick summary + clear buy/pass recommendation
   - **Full Underwriting:** Detailed analysis across all 8 phases + investment thesis
   - **Investment Memo:** IC-ready package with executive summary, full analysis, risks, returns
   - **Diligence:** Status update + risk mitigation + go/no-go recommendation

5. **Use conversational tone** while maintaining professional rigor

# OUTPUT STRUCTURE

For SCREENING requests:
- Executive summary (2-3 sentences)
- Key findings (3-5 bullets)
- Recommendation (clear buy/pass with rationale)

For FULL UNDERWRITING:
- Executive summary
- Phase-by-phase analysis (8 phases)
- Investment highlights & risks
- Financial projections summary
- Recommendation with conditions

For INVESTMENT MEMO:
- Executive summary (1 page equivalent)
- Investment thesis
- All 8 Shieldstone phases in detail
- Pro forma summary
- Risk analysis
- Recommendation and next steps

For DILIGENCE:
- Diligence status summary
- Findings vs. original underwriting
- Material discrepancies and financial impact
- Risk mitigation recommendations
- Go/no-go recommendation

Return response as conversational text (not JSON).
"""

    def synthesize(self, agent_state: dict, user_message: str) -> str:
        """Synthesize all agent results into final response"""

        deal_phase = agent_state.get('deal_phase', 'screening')

        # Build comprehensive context from all agents
        synthesis_prompt = f"""
        User's original request: "{user_message}"
        Deal phase: {deal_phase}

        AGENT RESULTS:

        Phase 1 - Property Fundamentals:
        {json.dumps(agent_state.get('phase1_property_fundamentals', {}), indent=2)}

        Phase 2 - Market Analysis:
        {json.dumps(agent_state.get('phase2_market_analysis', {}), indent=2)}

        Phase 3 - Financial Modeling:
        {json.dumps(agent_state.get('phase3_financial_modeling', {}), indent=2)}

        Phase 4 - Risk Assessment:
        {json.dumps(agent_state.get('phase4_risk_assessment', {}), indent=2)}

        Phase 5 - Value-Add Strategy:
        {json.dumps(agent_state.get('phase5_value_add_strategy', {}), indent=2)}

        Phase 6 - Financing Structure:
        {json.dumps(agent_state.get('phase6_financing_structure', {}), indent=2)}

        Phase 7 - Investment Returns:
        {json.dumps(agent_state.get('phase7_investment_returns', {}), indent=2)}

        Phase 8 - Exit Strategy:
        {json.dumps(agent_state.get('phase8_exit_strategy', {}), indent=2)}

        Synthesize this analysis following Shieldstone methodology into a clear, actionable response
        appropriate for a {deal_phase} request.
        """

        result = self.run(synthesis_prompt, max_tokens=8000)

        return result['result']
```

---

## Shieldstone Integration

### Mapping Shieldstone Manual v2 to Agent Architecture

The Shieldstone Manual v2 has **8 phases**. Each phase maps to a group of specialized agents:

| Shieldstone Phase | Description | Agent Examples | Deal Stage |
|-------------------|-------------|----------------|------------|
| **Phase 1: Property Fundamentals** | Unit mix, rent roll, physical condition, property details | `rent_roll_analyzer`<br>`om_analyzer`<br>`t12_analyzer`<br>`property_condition_assessor`<br>`unit_mix_analyzer` | Screening, Underwriting, Diligence |
| **Phase 2: Market Analysis** | Supply/demand, demographics, comps, trends | `market_research_agent`<br>`demographic_analyzer`<br>`supply_demand_analyzer`<br>`comparable_sales_agent`<br>`submarket_analyzer` | Screening, Underwriting |
| **Phase 3: Financial Modeling** | Pro forma, revenue optimization, expense analysis | `pro_forma_builder`<br>`revenue_optimizer`<br>`expense_analyzer`<br>`rent_growth_modeler`<br>`other_income_analyzer` | Screening, Underwriting, Memo |
| **Phase 4: Risk Assessment** | Market risk, execution risk, structural risk | `market_risk_analyzer`<br>`execution_risk_assessor`<br>`environmental_risk_agent`<br>`legal_risk_agent`<br>`operational_risk_agent` | Underwriting, Memo, Diligence |
| **Phase 5: Value-Add Strategy** | Renovations, repositioning, operational improvements | `renovation_planner`<br>`repositioning_strategist`<br>`amenity_optimizer`<br>`operational_improvement_agent` | Underwriting, Memo |
| **Phase 6: Financing Structure** | Debt, equity, capital stack, return optimization | `debt_optimizer`<br>`equity_structure_agent`<br>`capital_stack_modeler`<br>`lender_requirements_agent` | Underwriting, Memo |
| **Phase 7: Investment Returns** | IRR, cash-on-cash, equity multiple, sensitivity analysis | `irr_calculator`<br>`cash_flow_analyzer`<br>`equity_multiple_calculator`<br>`sensitivity_analyzer`<br>`return_attribution_agent` | Screening, Underwriting, Memo |
| **Phase 8: Exit Strategy** | Hold period, disposition strategy, market timing | `exit_strategist`<br>`hold_period_optimizer`<br>`disposition_planner`<br>`market_timing_agent` | Underwriting, Memo |

### Agent Count by Phase

**Estimated agent distribution across Shieldstone phases:**

- **Phase 1 agents:** ~15 (property fundamentals are data-intensive)
- **Phase 2 agents:** ~12 (market research has many facets)
- **Phase 3 agents:** ~10 (financial modeling sub-tasks)
- **Phase 4 agents:** ~15 (many risk categories)
- **Phase 5 agents:** ~8 (value-add strategies)
- **Phase 6 agents:** ~8 (financing structures)
- **Phase 7 agents:** ~10 (return calculations and sensitivity)
- **Phase 8 agents:** ~6 (exit planning)
- **Cross-phase agents:** ~10 (synthesizers, diligence trackers, report generators)
- **Utility agents:** ~6 (file parsers, data extractors, formatters)

**Total: ~100 agents**

### Shieldstone Manual as Cached System Prompt

**Key optimization:** Load the entire Shieldstone Manual v2 into each agent's system prompt and use **prompt caching** to reduce costs by 90%.

```python
def load_shieldstone_manual():
    """Load Shieldstone Manual v2 markdown content"""
    with open('shieldstone/manual_v2.md', 'r') as f:
        manual_content = f.read()

    return manual_content

class BaseAgent:
    def __init__(self, customer_config):
        # ...
        self.shieldstone_manual_full = load_shieldstone_manual()
        self.shieldstone_manual_phase = self.extract_phase_content(
            self.get_shieldstone_phase()
        )

    def extract_phase_content(self, phase_num: Optional[int]) -> str:
        """Extract specific phase content from manual"""
        if not phase_num:
            return ""

        # Parse markdown to extract phase section
        # This is where you'd parse the Shieldstone manual structure
        # and return only the relevant phase content

        phase_marker = f"## Phase {phase_num}:"
        # ... parsing logic ...

        return phase_content

    def get_system_prompt(self) -> str:
        """Include Shieldstone phase guidance in system prompt"""
        base_prompt = self.get_agent_specific_prompt()

        return f"""
{base_prompt}

# SHIELDSTONE METHODOLOGY (Phase {self.get_shieldstone_phase()})

{self.shieldstone_manual_phase}

Follow this methodology precisely in your analysis.
"""
```

**Cost savings:**
- Shieldstone manual: ~50,000 tokens
- Without caching: $0.15 per request (manual loaded each time)
- With caching: $0.015 per request after first call (90% reduction)
- **Over 100 requests/day: Saves $13.50/day = $405/month**

### Integrating Shieldstone Python Calculations

Your Shieldstone manual includes Python code for calculations. Integrate this directly:

```python
# shieldstone/calculations.py

def calculate_noi(gross_potential_rent: float,
                  other_income: float,
                  vacancy_rate: float,
                  operating_expenses: float) -> float:
    """Calculate Net Operating Income per Shieldstone methodology"""
    egi = (gross_potential_rent + other_income) * (1 - vacancy_rate)
    noi = egi - operating_expenses
    return noi

def calculate_irr(initial_investment: float,
                  annual_cash_flows: List[float],
                  exit_proceeds: float) -> float:
    """Calculate IRR per Shieldstone methodology"""
    import numpy as np

    cash_flows = [-initial_investment] + annual_cash_flows + [exit_proceeds]
    irr = np.irr(cash_flows)
    return irr

def calculate_debt_service_coverage_ratio(noi: float,
                                           annual_debt_service: float) -> float:
    """Calculate DSCR per Shieldstone methodology"""
    return noi / annual_debt_service if annual_debt_service > 0 else float('inf')

# ... more Shieldstone calculations ...
```

**Use in agents:**

```python
class ProFormaAgent(BaseAgent):
    def build(self, property_data: dict, acquisition_details: dict) -> dict:
        # Claude generates pro forma structure
        claude_result = self.run(...)

        # Validate with Shieldstone Python
        from shieldstone.calculations import calculate_noi, calculate_irr

        validated_noi = calculate_noi(
            gross_potential_rent=property_data['gpr'],
            other_income=property_data['other_income'],
            vacancy_rate=0.05,
            operating_expenses=property_data['opex']
        )

        # Use Python calculation as source of truth
        claude_result['year_1']['noi'] = validated_noi

        return claude_result
```

**Hybrid approach benefits:**
- ✅ Claude handles unstructured data, context, narrative
- ✅ Python handles precise numerical calculations
- ✅ Best of both worlds: AI reasoning + deterministic math

---

## Development Workflow

### Local Development Setup

```bash
# 1. Clone repo
git clone https://github.com/yourusername/dream-agents.git
cd dream-agents

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# ANTHROPIC_API_KEY=sk-ant-...
# GEMINI_API_KEY=...
# PERPLEXITY_API_KEY=...

# 5. Copy Shieldstone manual and Python modules
cp -r /path/to/shieldstone ./shieldstone

# 6. Run database migrations
alembic upgrade head

# 7. Run locally
python main.py

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Adding a New Agent (Step-by-Step)

#### 1. Create Agent Class

```python
# agents/new_agent.py

from agents.base_agent import BaseAgent
import json

class NewAgent(BaseAgent):
    """Description of what this agent does"""

    def get_shieldstone_phase(self) -> int:
        return 3  # Which Shieldstone phase (1-8)

    def get_system_prompt(self) -> str:
        phase_guidance = self.shieldstone_manual_phase

        return f"""You are a specialist in [specific task].

# SHIELDSTONE METHODOLOGY

{phase_guidance}

# YOUR TASK

[Detailed instructions for this agent]

Return results as JSON with keys: [key1, key2, key3]
"""

    def execute(self, input_data: dict) -> dict:
        """Main execution method"""
        prompt = f"Analyze: {json.dumps(input_data, indent=2)}"
        result = self.run(prompt)

        try:
            parsed = json.loads(result['result'])
            result['parsed_result'] = parsed
        except:
            result['parsed_result'] = None

        return result
```

#### 2. Register Agent

```python
# agents/registry.py

from agents.new_agent import NewAgent

AGENT_REGISTRY = {
    # ... existing agents ...

    "new_agent": {
        "class": NewAgent,
        "description": "What this agent does (1 sentence)",
        "shieldstone_phase": 3,
        "inputs": ["what it needs"],
        "outputs": ["what it produces"],
        "typical_runtime": "X seconds",
        "cost_per_run": "$X.XX",
        "state_key": "new_agent_result"
    },
}
```

#### 3. Create LangGraph Node Wrapper

```python
# orchestration/agent_nodes.py

from agents.registry import AGENT_REGISTRY

def create_agent_node(agent_class, state_key: str):
    """Create a LangGraph node from an agent class"""
    def node_function(state: AgentState) -> AgentState:
        # Instantiate agent with customer config
        agent = agent_class(state['customer_config'])

        # Execute agent (customize based on what data it needs from state)
        result = agent.execute(state)

        # Write result to state
        state[state_key] = result
        state['agents_completed'].append(state_key)

        return state

    return node_function

# Create node for new agent
new_agent_node = create_agent_node(
    AGENT_REGISTRY['new_agent']['class'],
    AGENT_REGISTRY['new_agent']['state_key']
)
```

#### 4. Test Agent Standalone

```python
# tests/test_new_agent.py

from agents.new_agent import NewAgent

def test_new_agent():
    """Test new agent with sample data"""
    agent = NewAgent(customer_config={})

    test_input = {
        "test_field_1": "test value",
        "test_field_2": 12345
    }

    result = agent.execute(test_input)

    print("Result:", result)
    assert result['parsed_result'] is not None
    assert 'key1' in result['parsed_result']

if __name__ == "__main__":
    test_new_agent()
```

#### 5. Deploy

```bash
# Test locally first
python tests/test_new_agent.py

# Commit and push
git add agents/new_agent.py agents/registry.py orchestration/agent_nodes.py tests/test_new_agent.py
git commit -m "Add new agent for [specific task]"
git push origin main

# Auto-deploys (Railway) or manual restart (VPS)
# On VPS:
ssh root@your-server
cd /app/dream-agents
git pull
docker-compose restart
```

**That's it!** The orchestrator will now automatically consider this agent when planning workflows.

### Development with Claude Code

You can develop from anywhere with Claude Code:

```bash
# On your laptop (traveling, home, office - anywhere)
cd ~/projects/dream-agents

# Use Claude Code to build agents
claude "Build a demographic analysis agent for Shieldstone Phase 2 that analyzes
population growth, median income, employment trends, and education levels for a
given market. Use census data APIs where possible."

# Claude Code creates: agents/demographic_analyzer.py

# Test locally
python tests/test_demographic_analyzer.py

# Works? Commit and push
git add agents/demographic_analyzer.py
git commit -m "Add demographic analysis agent (Phase 2)"
git push origin main

# Auto-deploys to production (if using Railway)
```

---

## Cost Analysis

### Infrastructure Costs (Monthly)

**Minimal Setup (1-50 customers):**
- Server: Railway Hobby **$5/month**
- **Total: $5/month**

**Production Setup (50-500 customers):**
- Server: DigitalOcean 4GB **$24/month**
- **Total: $24/month**

**Scale Setup (500-5000 customers):**
- Servers: 2× DigitalOcean 8GB **$96/month**
- Managed Database: **$60/month**
- Redis Cache: **$15/month**
- **Total: $171/month**

### AI API Costs

**Claude API (Sonnet 4.5):**
- Input: **$3 per million tokens**
- Output: **$15 per million tokens**

**With Prompt Caching (90% savings on cached portions):**
- First request: Full cost
- Subsequent requests: 10% cost on cached content (Shieldstone manual)

**Example Agent Call (Rent Roll Analyzer):**

```
System prompt: 50,000 tokens (Shieldstone manual - CACHED after first call)
User input: 3,000 tokens (rent roll data)
Output: 2,000 tokens (analysis)

WITHOUT CACHING:
Input: 53,000 tokens × $0.000003 = $0.159
Output: 2,000 tokens × $0.000015 = $0.030
Total: $0.189

WITH CACHING (after first call):
Input: 5,000 tokens × $0.000003 = $0.015 (only non-cached portion)
Cache read: 50,000 tokens × $0.0000003 = $0.015 (90% cheaper)
Output: 2,000 tokens × $0.000015 = $0.030
Total: $0.060 (68% savings)
```

### Cost Per Request Analysis

**Simple Request** ("Analyze this rent roll"):
- Agents used: 2 (rent_roll_analyzer, synthesizer)
- Tokens: ~60,000 total
- Cost: **$0.03-0.06** (with caching)

**Medium Request** ("Should I buy this property?" - Screening):
- Agents used: 8 (Phases 1, 2, 3, 7 agents + synthesizer)
- Tokens: ~120,000 total
- Cost: **$0.15-0.25** (with caching)

**Complex Request** ("Full investment committee package"):
- Agents used: 30+ (all 8 Shieldstone phases)
- Tokens: ~250,000 total
- Cost: **$0.50-0.80** (with caching)

**Due Diligence Request** ("Compare PCA report to original underwriting"):
- Agents used: 5-8 (diligence-specific agents)
- Tokens: ~100,000 total
- Cost: **$0.20-0.35** (with caching)

**Average across all request types: ~$0.20 per request** (with caching)

### Revenue Model Example

**Example SaaS Pricing:**
- **Basic Plan:** $99/month (100 analyses)
- **Pro Plan:** $299/month (500 analyses)
- **Enterprise:** $999/month (unlimited analyses + dedicated support)

**50 Customers Scenario (mixed plans):**
- 30 customers @ $99/month = $2,970
- 15 customers @ $299/month = $4,485
- 5 customers @ $999/month = $4,995
- **Total Revenue: $12,450/month**

**Costs:**
- Infrastructure: $24/month
- AI API (avg 150 requests/customer, 7,500 total): ~$1,500/month
- **Total Costs: $1,524/month**

**Profit: $10,926/month (88% margin)**

**Key insight:** Infrastructure is cheap. AI API costs scale with usage. Margins stay high.

---

## Implementation Roadmap

### Phase 1: MVP (Weeks 1-2)
**Goal:** Single working agent with FastAPI endpoint

**Tasks:**
1. ✅ Set up FastAPI project structure
2. ✅ Create BaseAgent class with Shieldstone manual loading
3. ✅ Build one agent: RentRollAgent (Phase 1)
4. ✅ Create simple endpoint: `POST /api/analyze-rent-roll`
5. ✅ Deploy to Railway
6. ✅ Test end-to-end with sample rent roll

**Deliverable:** Working API that analyzes rent rolls using Shieldstone Phase 1 methodology

---

### Phase 2: Multi-Agent Foundation (Weeks 3-4)
**Goal:** 5 core agents with basic orchestration

**Tasks:**
1. ✅ Build 4 more agents:
   - OMAnalyzerAgent (Phase 1)
   - MarketResearchAgent (Phase 2)
   - ProFormaBuilderAgent (Phase 3)
   - ShieldstoneSynthesizerAgent (cross-phase)
2. ✅ Set up LangGraph basic workflow
3. ✅ Create simple sequential workflow (5 agents)
4. ✅ Add customer authentication (API keys)
5. ✅ Set up PostgreSQL database (customers, configs)
6. ✅ Implement prompt caching for Shieldstone manual

**Deliverable:** End-to-end property analysis (screening level) with 5 agents

---

### Phase 3: Advanced Orchestration (Weeks 5-6)
**Goal:** Dynamic workflow builder with 15 agents

**Tasks:**
1. ✅ Build 10 more specialized agents across Shieldstone phases:
   - Phase 1: T12Analyzer, PropertyConditionAssessor
   - Phase 2: DemographicAnalyzer, ComparableSalesAgent
   - Phase 3: RevenueOptimizer, ExpenseAnalyzer
   - Phase 4: MarketRiskAnalyzer, EnvironmentalRiskAgent
   - Phase 7: IRRCalculator, SensitivityAnalyzer
2. ✅ Implement dynamic workflow builder (Claude plans workflows based on request)
3. ✅ Add parallel execution in LangGraph
4. ✅ Add conditional routing (screening vs. full underwriting)
5. ✅ Implement usage tracking and cost logging
6. ✅ Add Shieldstone Python calculation integration

**Deliverable:** Intelligent system that adapts workflow to user's question, supporting both screening and full underwriting

---

### Phase 4: Scale to 50+ Agents (Weeks 7-10)
**Goal:** Comprehensive agent library covering all 8 Shieldstone phases

**Tasks:**
1. ✅ Build remaining agents to reach 50-60 total (5-8 agents per week):
   - **Phase 1** (complete): 15 agents
   - **Phase 2** (complete): 12 agents
   - **Phase 3** (complete): 10 agents
   - **Phase 4** (expand): 15 agents
   - **Phase 5** (new): 8 agents
   - **Phase 6** (new): 8 agents
   - **Phase 7** (expand): 10 agents
   - **Phase 8** (new): 6 agents
2. ✅ Add Redis caching for agent results
3. ✅ Implement streaming responses (for real-time UX)
4. ✅ Build customer dashboard (usage, cost tracking)
5. ✅ Add monitoring and logging (Sentry, LogRocket)
6. ✅ Optimize costs (model selection, caching strategy)

**Deliverable:** Production-ready platform with 50-60 core agents covering all Shieldstone phases

---

### Phase 5: Due Diligence Agents (Weeks 11-12)
**Goal:** Post-LOI/PSA diligence tracking and analysis

**Tasks:**
1. ✅ Build diligence-specific agents (10-15 agents):
   - DiligenceTrackerAgent
   - ThirdPartyReportAnalyzer (PCA, Phase I ESA, Survey, etc.)
   - RiskMitigationAgent
   - RenegotiationRecommendationAgent
   - GoNoGoDecisionAgent
2. ✅ Integrate with deal state management (track deal from screening → underwriting → memo → diligence)
3. ✅ Build comparison engine (original underwriting vs. diligence findings)
4. ✅ Add financial impact calculator (how diligence findings affect returns)

**Deliverable:** Full lifecycle support from initial screening through due diligence completion

---

### Phase 6: Specialized & Long-Tail Agents (Weeks 13-16)
**Goal:** Reach 100+ agents with specialized capabilities

**Tasks:**
1. ✅ Build specialized agents (30-40 more agents):
   - Asset class specific (garden-style, mid-rise, high-rise, student housing, affordable)
   - Market specific (top 20 MSAs)
   - Scenario-specific (value-add, core, opportunistic)
   - Report generators (IC memo, executive summary, investment highlights)
2. ✅ Add support for different file formats (PDF, Excel, CSV, images via OCR)
3. ✅ Implement multi-property comparison (portfolio analysis)
4. ✅ Add benchmark database (how does this deal compare to others?)

**Deliverable:** Comprehensive 100+ agent system with deep specialization

---

### Phase 7: Polish & Launch Prep (Weeks 17-18)
**Goal:** Production-ready SaaS platform

**Tasks:**
1. ✅ Build customer onboarding flow
2. ✅ Create landing page and marketing site
3. ✅ Implement billing integration (Stripe)
4. ✅ Add customer configuration UI (set underwriting criteria)
5. ✅ Build documentation and help center
6. ✅ Set up customer support system
7. ✅ Security audit and penetration testing
8. ✅ Performance optimization and load testing

**Deliverable:** Live SaaS product ready for first 10 paying customers

---

### Phase 8: Customer Acquisition (Weeks 19+)
**Goal:** First 10-50 paying customers

**Tasks:**
1. ✅ Launch beta program (5-10 customers)
2. ✅ Gather feedback and iterate
3. ✅ Build referral program
4. ✅ Create case studies and testimonials
5. ✅ Paid marketing (Google Ads, LinkedIn, industry publications)
6. ✅ Conference presence (NMHC, Multifamily events)
7. ✅ Outbound sales (targeted lists of PE firms, family offices, sponsors)

**Deliverable:** $10K+ MRR with 20-50 paying customers

---

## Critical Success Factors

### 1. Start Simple, Scale Gradually
- ✅ **Don't build 100 agents on Day 1**
- ✅ Build 5 core agents that deliver value
- ✅ Add more based on customer feedback
- ✅ Iterate based on usage patterns

### 2. Optimize for Prompt Caching
- ✅ Use the same system prompts repeatedly
- ✅ Cache the entire Shieldstone Manual v2 (saves 90% on costs)
- ✅ Structure prompts to maximize cache hits
- ✅ Monitor cache hit rates and optimize

### 3. Multi-Tenant from Day 1
- ✅ Design for multiple customers from the start
- ✅ Customer-specific configs in database
- ✅ Easier to build multi-tenant upfront than retrofit later
- ✅ Enables rapid scaling without architecture changes

### 4. Hybrid AI + Python Approach
- ✅ Use Claude for unstructured data, reasoning, narrative
- ✅ Use Shieldstone Python for precise calculations
- ✅ Validate AI outputs with deterministic code
- ✅ Best of both worlds: intelligence + accuracy

### 5. Measure Everything
Track:
- ✅ Which agents are used most (optimize these first)
- ✅ Which agents fail most (improve prompts, add error handling)
- ✅ Cost per request type (identify expensive patterns)
- ✅ Customer usage patterns (what features matter?)
- ✅ Performance bottlenecks (where to optimize)

Use this data to continuously improve the system.

### 6. User Experience is King
Users don't care about your 100 agents. They care about:
- ✅ **Response quality** - Is the analysis accurate and actionable?
- ✅ **Speed** - How fast do they get answers? (streaming helps)
- ✅ **Ease of use** - Can they just upload files and ask questions?
- ✅ **Reliability** - Does it work every time?

Focus obsessively on these four dimensions.

### 7. Shieldstone Compliance as Differentiator
- ✅ Emphasize that analysis follows proven methodology
- ✅ "Not just AI - AI trained on institutional-grade underwriting standards"
- ✅ Build trust through consistent, rigorous analysis
- ✅ Make Shieldstone compliance visible to users

---

## Next Steps

### Immediate Actions (This Week)

1. **Review Shieldstone Manual v2 structure**
   - Confirm 8-phase organization
   - Identify which sections have Python code
   - List key calculation modules to integrate

2. **Set up project repository**
   - Initialize FastAPI project
   - Set up git repo
   - Create initial folder structure
   - Add Shieldstone manual and Python modules

3. **Build first agent (RentRollAgent)**
   - Implement BaseAgent class
   - Create RentRollAgent with Phase 1 guidance
   - Test with sample rent roll
   - Deploy to Railway

4. **Define agent registry structure**
   - Map all 8 Shieldstone phases to agent categories
   - List 20-30 high-priority agents to build first
   - Document each agent's inputs, outputs, responsibilities

5. **Plan frontend redesign** (separate track)
   - Review current Gemini UI integration
   - Design new conversational interface
   - Plan file upload UX
   - Consider streaming response display

### Questions to Resolve

1. **Shieldstone Manual Structure**
   - How are the 8 phases currently organized in the manual?
   - Which sections are narrative vs. calculation-heavy?
   - What Python modules already exist?

2. **Customer Configuration**
   - What underwriting criteria should be customizable per customer?
   - Min occupancy, target IRR, markets, hold period, etc.?
   - How granular should config overrides be?

3. **Deal State Management**
   - How do we track deal progression (screening → underwriting → memo → diligence)?
   - Should this be user-driven ("analyze this as a screening") or automatic?
   - Do we need deal versioning (e.g., pre-diligence vs. post-diligence underwriting)?

4. **Frontend Integration**
   - Keep Gemini UI or rebuild?
   - What conversational interface patterns work best for file-heavy workflows?
   - Mobile vs. desktop priorities?

---

## Conclusion

You now have a **complete architecture** for transforming Dream into a production-grade, multi-agent real estate underwriting platform:

✅ **100+ agent system** mapped to Shieldstone Manual v2's 8 phases
✅ **Multi-tenant architecture** serving many customers from one server
✅ **Intelligent orchestration** via LangGraph with parallel execution
✅ **Cost-optimized** with prompt caching (90% savings on Shieldstone manual)
✅ **Hybrid AI + Python** approach for accuracy and intelligence
✅ **Full deal lifecycle** support from screening through due diligence
✅ **Scalable infrastructure** from MVP to thousands of customers
✅ **Clear development path** from 5 agents to 100+

### The Big Idea

Transform Dream from "LLM + manual" into **"100 specialized agents orchestrated by a master agent, all trained on Shieldstone methodology, serving users through a single conversational interface."**

Users see: Simple chat interface
Reality: Sophisticated multi-agent system executing institutional-grade analysis

### Start Building Today

**Phase 1 (Week 1-2):** Build RentRollAgent + FastAPI endpoint → Deploy to Railway → Test with real data

**Phase 2 (Week 3-4):** Add 4 more agents → LangGraph orchestration → End-to-end screening analysis

**Phase 3 (Week 5-6):** Dynamic workflows → 15 agents → Full underwriting capability

**Keep building...**

---

**The key is to start simple and iterate. Don't wait for perfection—get something working, get feedback, improve.**

Let's build this. 🚀

---

## Appendix: Claude SDK Agents at Scale - Deep Dive

### Understanding SDK Agents vs. Traditional API Calls

This section provides a beginner-friendly explanation of how to leverage Claude SDK agents in a production SaaS environment with multiple customers.

#### What IS a Claude SDK Agent?

Think of a Claude SDK Agent like hiring a smart assistant who can:
- Remember instructions you gave them
- Use tools (calculator, web browser, database access)
- Make decisions about what to do next
- Call other specialist assistants when needed

**Regular Claude API:**
- You send a message → Claude responds → Done
- Like texting someone

**Claude SDK Agent:**
- You give Claude a job + access to tools → It figures out the steps to complete the task
- Like hiring an intern who can think for themselves

---

### The Restaurant Analogy: Three Scaling Patterns

#### Scenario 1: Traditional API Calls (What We Have Now)

You (the chef) do everything yourself:
- Customer orders → You cook from scratch
- Every dish made one step at a time
- You follow the recipe exactly: read menu → get ingredients → cook → serve
- If something goes wrong, the whole meal stops

**Pros:**
- ✅ Simple, you control everything
- ✅ Predictable costs
- ✅ No surprises

**Cons:**
- ❌ You're doing ALL the work
- ❌ Can't handle rush hour well
- ❌ Same process even for simple vs complex orders

#### Scenario 2: With SDK Agents

You hire smart line cooks (agents) who can:
- Read the order themselves
- Decide what tools to use (oven vs stovetop)
- Call other specialists ("Hey pasta chef, I need linguine!")
- Handle problems ("Out of basil? I'll use oregano")

**Pros:**
- ✅ Agents figure out the best way to complete tasks
- ✅ Can handle complex, multi-step work
- ✅ Better at dealing with weird situations

**Cons:**
- ❌ More expensive per dish
- ❌ Need to manage multiple cooks
- ❌ Have to make sure Cook A doesn't mix up orders with Cook B

---

### The Core Challenge: Stateful Agents in Multi-Tenant SaaS

Your architecture already solves multi-tenancy beautifully with PostgreSQL row-level security and tenant isolation. But SDK agents introduce a **fundamental state management problem:**

```python
# ❌ WRONG: Shared agent instance across requests
class AnalysisService:
    def __init__(self):
        self.coordinator_agent = Agent(...)  # Shared state!

    async def analyze_deal(self, tenant_id: str, deal_id: str):
        # Multiple tenants using same agent = context leakage
        return await self.coordinator_agent.run(...)
```

**This is DANGEROUS** - Customer A might see Customer B's deals!

---

### Three Production-Ready Patterns

#### Pattern 1: Ephemeral Agents (⭐ Recommended for 0-150 Customers)

Create fresh agent instances per request, manage state in PostgreSQL.

**How it works:**
Every time a customer uploads a deal:
1. Create a brand new agent just for them
2. Give it ONLY that customer's information and rules
3. Agent does the work
4. Agent disappears when done
5. Results saved to your database

**Code Example:**

```python
from anthropic import Anthropic
import asyncio
from contextlib import asynccontextmanager

class TenantAwareAgentService:
    def __init__(self, db_pool, redis_client):
        self.anthropic = Anthropic()
        self.db = db_pool
        self.redis = redis_client

    @asynccontextmanager
    async def get_coordinator_agent(self, tenant_id: str, deal_id: str):
        """Create ephemeral agent with tenant-specific context"""

        # Load tenant configuration from DB
        tenant_config = await self.db.fetchrow(
            "SELECT investment_criteria, custom_instructions "
            "FROM tenants WHERE id = $1",
            tenant_id
        )

        # Load deal context from DB
        deal_context = await self.db.fetchrow(
            "SELECT property_data, documents, analysis_history "
            "FROM deals WHERE id = $1 AND tenant_id = $2",
            deal_id, tenant_id
        )

        # Build tenant-specific instructions
        instructions = f"""
        You are analyzing a real estate deal for {tenant_config['name']}.

        Investment Criteria:
        {json.dumps(tenant_config['investment_criteria'], indent=2)}

        Deal Context:
        {json.dumps(deal_context['property_data'], indent=2)}

        Previous Analysis:
        {deal_context['analysis_history'] or 'First analysis'}
        """

        # Create ephemeral agent
        agent = Agent(
            client=self.anthropic,
            name="Deal Coordinator",
            instructions=instructions,
            tools=[
                self._get_property_analysis_tool(tenant_id),
                self._get_financial_analysis_tool(tenant_id),
                self._get_market_research_tool(tenant_id),
            ]
        )

        try:
            yield agent
        finally:
            # Cleanup happens automatically with context manager
            pass

    async def analyze_deal(self, tenant_id: str, deal_id: str):
        """Main analysis endpoint"""
        async with self.get_coordinator_agent(tenant_id, deal_id) as agent:

            # Run analysis with agent
            result = await asyncio.to_thread(
                agent.run,
                f"Analyze deal {deal_id} and provide investment recommendation"
            )

            # Persist results to database
            await self.db.execute(
                """
                INSERT INTO analyses (deal_id, tenant_id, agent_output, created_at)
                VALUES ($1, $2, $3, NOW())
                """,
                deal_id, tenant_id, result.output
            )

            return result
```

**Pros:**
- ✅ Super safe - customers NEVER see each other's data
- ✅ Simple to understand and debug
- ✅ Each customer gets custom analysis based on THEIR rules
- ✅ No weird "memory leaks" between customers

**Cons:**
- ❌ Slightly slower (creating new agent takes ~1-2 seconds)
- ❌ Costs a bit more (~$0.20 per analysis vs $0.15)

**When to use:** Starting out, up to ~150 customers

---

#### Pattern 2: Agent Pooling (For 100-500 Customers)

Pre-warm a pool of agents, assign them to requests temporarily.

**How it works:**
You pre-hire 10 agents who just stand around waiting. When an order comes in:
1. Grab an available agent
2. Give them TODAY's customer rules
3. They make the dish
4. They forget everything and go back to waiting

**Why this matters:** Creating a new agent takes 1-2 seconds. If you have 100 customers all uploading deals at 9am Monday morning, that's slow. Pre-made agents can start working immediately.

**Code Example:**

```python
from asyncio import Queue
import uuid

class AgentPool:
    def __init__(self, anthropic_client, pool_size: int = 10):
        self.anthropic = anthropic_client
        self.pool_size = pool_size
        self.available_agents = Queue(maxsize=pool_size)
        self._init_pool()

    def _init_pool(self):
        """Pre-create agent instances"""
        for _ in range(self.pool_size):
            agent = Agent(
                client=self.anthropic,
                name="Generic Coordinator",
                instructions="You are a real estate analysis coordinator.",
                tools=[]  # Tools will be injected per-request
            )
            self.available_agents.put_nowait(agent)

    @asynccontextmanager
    async def checkout_agent(self, tenant_id: str, deal_id: str):
        """Checkout agent from pool, customize for tenant, return after use"""

        # Wait for available agent
        agent = await self.available_agents.get()

        try:
            # Inject tenant-specific context via system message
            customized_agent = self._customize_agent_for_tenant(
                agent, tenant_id, deal_id
            )
            yield customized_agent
        finally:
            # Reset agent state and return to pool
            await self._reset_agent(agent)
            await self.available_agents.put(agent)

    def _customize_agent_for_tenant(self, agent, tenant_id, deal_id):
        """Inject tenant context without recreating agent"""
        # Implementation depends on SDK capabilities
        # May need to use prompt engineering to inject context
        pass

    async def _reset_agent(self, agent):
        """Clear any tenant-specific state"""
        # Implementation depends on SDK state management
        pass
```

**Pros:**
- ✅ Faster (no 1-2 second startup time)
- ✅ Handles rush hour better
- ✅ Still keeps customers separate

**Cons:**
- ❌ More complex to manage
- ❌ Uses more memory (10 agents always running)
- ❌ Have to be REALLY careful clearing context between customers

**When to use:** 100-500 customers, busy times

---

#### Pattern 3: Async Task Queue with Worker Pool (500+ Customers)

For true production scale, use Celery workers with agent instances.

**How it works:**
Customer uploads deal → Goes into a queue → Separate "kitchen" workers grab jobs when ready

**Code Example:**

```python
# worker.py - Runs on separate worker processes
from celery import Celery
from anthropic import Anthropic

celery_app = Celery('dreamvision', broker='redis://localhost:6379/0')

# Each worker maintains its own agent instance
anthropic = Anthropic()

@celery_app.task
def analyze_deal_task(tenant_id: str, deal_id: str):
    """Celery task for deal analysis"""

    # Load tenant context from DB
    with get_db_connection() as conn:
        tenant_config = conn.execute(
            "SELECT * FROM tenants WHERE id = %s", (tenant_id,)
        ).fetchone()

        deal_data = conn.execute(
            "SELECT * FROM deals WHERE id = %s AND tenant_id = %s",
            (deal_id, tenant_id)
        ).fetchone()

    # Create ephemeral agent for this task
    agent = Agent(
        client=anthropic,
        name="Deal Coordinator",
        instructions=build_instructions(tenant_config, deal_data),
        tools=build_tools(tenant_id)
    )

    # Run analysis
    result = agent.run(f"Analyze deal {deal_id}")

    # Store results
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO analyses (deal_id, tenant_id, result) VALUES (%s, %s, %s)",
            (deal_id, tenant_id, result.output)
        )

    return {"deal_id": deal_id, "status": "completed"}


# FastAPI endpoint
@app.post("/api/deals/{deal_id}/analyze")
async def trigger_analysis(deal_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Async endpoint that queues analysis task"""

    # Queue the task
    task = analyze_deal_task.delay(tenant_id, deal_id)

    # Return immediately
    return {
        "deal_id": deal_id,
        "task_id": task.id,
        "status": "queued",
        "estimated_completion": "2-5 minutes"
    }
```

**Pros:**
- ✅ Can handle 1000+ customers easily
- ✅ Website stays fast (doesn't wait for analysis)
- ✅ Can add more "kitchen workers" if busy
- ✅ If one worker crashes, others keep going

**Cons:**
- ❌ More complex (multiple computers coordinating)
- ❌ Costs more to run (more servers)
- ❌ Customer waits a few minutes instead of instant

**When to use:** 500+ customers, enterprise scale

---

### Critical Production Considerations

#### 1. Cost Management at Scale

Your current target is $0.15/analysis. SDK agents add overhead.

```python
class CostAwareLLMRouter:
    """Wrap agents with cost tracking"""

    async def analyze_with_budget(
        self,
        tenant_id: str,
        deal_id: str,
        max_cost: float = 0.50
    ):
        # Track costs in real-time
        cost_tracker = CostTracker()

        async with self.get_coordinator_agent(tenant_id, deal_id) as agent:
            # Intercept tool calls to track costs
            wrapped_agent = CostTrackingAgentWrapper(
                agent,
                cost_tracker,
                max_cost
            )

            try:
                result = await wrapped_agent.run(...)

                # Log costs to database
                await self.db.execute(
                    """
                    INSERT INTO usage_tracking
                    (tenant_id, deal_id, cost, tokens_used, model_calls)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    tenant_id, deal_id,
                    cost_tracker.total_cost,
                    cost_tracker.total_tokens,
                    cost_tracker.model_call_count
                )

                return result

            except BudgetExceededError:
                # Fallback to cheaper analysis
                return await self.run_basic_analysis(tenant_id, deal_id)
```

#### 2. Rate Limiting & Throttling

SDK agents don't automatically respect rate limits across tenants.

```python
from aiolimiter import AsyncLimiter

class TenantRateLimiter:
    def __init__(self):
        # Per-tenant rate limiters
        self.limiters = {}

    def get_limiter(self, tenant_id: str, plan: str) -> AsyncLimiter:
        if tenant_id not in self.limiters:
            if plan == "starter":
                # 10 analyses per hour
                self.limiters[tenant_id] = AsyncLimiter(10, 3600)
            elif plan == "professional":
                # 50 analyses per hour
                self.limiters[tenant_id] = AsyncLimiter(50, 3600)
            else:  # enterprise
                # 200 analyses per hour
                self.limiters[tenant_id] = AsyncLimiter(200, 3600)

        return self.limiters[tenant_id]

    async def acquire(self, tenant_id: str, plan: str):
        limiter = self.get_limiter(tenant_id, plan)
        await limiter.acquire()

# Usage in endpoint
@app.post("/api/deals/{deal_id}/analyze")
async def analyze_deal(
    deal_id: str,
    tenant_id: str = Depends(get_tenant_id),
    limiter: TenantRateLimiter = Depends(get_rate_limiter)
):
    # Check rate limit
    await limiter.acquire(tenant_id, request.user.plan)

    # Proceed with analysis
    ...
```

#### 3. Observability & Debugging

Multi-tenant agent debugging is HARD. Instrument everything.

```python
import structlog

logger = structlog.get_logger()

class InstrumentedAgent:
    def __init__(self, agent, tenant_id: str, deal_id: str):
        self.agent = agent
        self.tenant_id = tenant_id
        self.deal_id = deal_id

    async def run(self, *args, **kwargs):
        with logger.contextualize(
            tenant_id=self.tenant_id,
            deal_id=self.deal_id,
            agent_name=self.agent.name
        ):
            logger.info("agent.started")

            try:
                result = await self.agent.run(*args, **kwargs)

                logger.info(
                    "agent.completed",
                    output_length=len(result.output),
                    tool_calls=len(result.tool_calls),
                    cost=result.cost
                )

                return result

            except Exception as e:
                logger.error(
                    "agent.failed",
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
```

---

### Real-World Scaling Numbers

Based on your projections:

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Customers | 25 | 150 | 400 |
| Deals/month | 1,250 | 9,000 | 24,000 |
| Concurrent analyses | ~10 | ~75 | ~200 |
| **SDK Agent Strategy** | **Ephemeral** | **Pooling** | **Worker Queue** |
| Worker count needed | 2-3 | 10-15 | 30-50 |
| Redis required | No | Yes | Yes + Celery |
| Cost/analysis with agents | $0.20 | $0.18 | $0.15 |

---

### Bottom Line Recommendation

**For DreamVision Launch (Year 1):**
- Use Pattern 1 (Ephemeral Agents) - simplest, most reliable
- Each request creates fresh agent with tenant context from PostgreSQL
- No complex state management needed
- Costs slightly higher ($0.20 vs $0.15) but acceptable at launch scale

**For Scale (Year 2+):**
- Migrate to Pattern 3 (Celery Workers) for production volume
- Pre-warm worker pool with agent instances
- Use Redis for task queue and result caching
- Implement comprehensive cost tracking and rate limiting

**Critical Success Factors:**
- ✅ **Tenant isolation via database, NOT agent memory**
- ✅ **Ephemeral agents per request prevents context leakage**
- ✅ **Cost tracking at every LLM call for billing accuracy**
- ✅ **Comprehensive logging with tenant_id in every log entry**
- ✅ **Graceful degradation when agents exceed budget**

---

### The Cost Question: "Wait, This Sounds Expensive"

Let's break down what each analysis ACTUALLY costs:

**Without Agents (Current):**
- You manually call Claude API multiple times
- You write all the logic yourself
- Cost per analysis: **$0.15**
  - $0.11 for Claude API calls
  - $0.04 for your server/database

**With Agents:**
- Agent makes decisions about what to do next
- Agent might call Claude 2-3 extra times to "think"
- Cost per analysis: **$0.20**
  - $0.14 for Claude API calls (more calls)
  - $0.04 for your server/database
  - $0.02 for agent "coordination"

**So agents cost $0.05 more per analysis.**

**But here's the math:**
- You charge customers $99-$999/month
- Let's say average customer does 50 deals/month
- That's $299/month = **$6 per deal**
- Spending $0.20 instead of $0.15 = **Only 5 cents more**
- **You're still making $5.80 profit per deal**

**The value:** Agents handle complex edge cases better, so you spend less time fixing bugs = saves you $$$ on engineering time.

---

### The Safety Question: "How Do I Keep Customers Apart?"

This is CRITICAL. You can't have Customer A seeing Customer B's deals.

**The Key Rule: Agents Get Memory from Your Database, Not From Each Other**

```python
# ❌ BAD - One agent for everyone
global_agent = Agent()  # Created once, used by everyone

def analyze_deal(customer_id, documents):
    # Everyone uses the same agent - it remembers previous customers!
    result = global_agent.run(...)  # DANGEROUS!

# ✅ GOOD - Fresh agent per customer
def analyze_deal(customer_id, documents):
    # Get THIS customer's info from database
    customer_data = database.get(customer_id)

    # Create NEW agent just for them
    agent = Agent(instructions=f"Working for {customer_data['name']}")

    # Agent only knows about THIS customer
    result = agent.run(...)

    # Agent disappears after this function ends
    return result
```

**Think of it like:**
- ❌ Bad: Everyone shares the same notebook (cross-contamination)
- ✅ Good: Everyone gets a fresh sheet of paper (clean slate)

---

### Real-World Example: A Customer's Deal Flow

Let's walk through what happens when "Acme Investments" (your customer) uploads a deal:

**Step 1: Upload (10 seconds)**
- Customer uploads: Offering memo PDF, Excel financial model, Rent roll

**Step 2: Your Code Creates Agent (2 seconds)**

```python
# Get Acme's rules from your database
acme_rules = {
    "company": "Acme Investments",
    "min_return": "12%",
    "max_price": "$10M",
    "markets": ["Austin", "Dallas", "Phoenix"],
    "must_have": "Class B multifamily, 100+ units"
}

# Create agent with THEIR rules
agent = Agent(
    name="Deal Analyzer for Acme",
    instructions=f"""
    You're analyzing deals for Acme Investments.
    Only recommend deals matching their criteria:
    - Minimum {acme_rules['min_return']} return
    - Maximum {acme_rules['max_price']} price
    - Only in {acme_rules['markets']}
    - Must be {acme_rules['must_have']}
    """,
    tools=[
        extract_pdf_tool,
        analyze_financials_tool,
        research_market_tool
    ]
)
```

**Step 3: Agent Does Its Thing (2 minutes)**

Agent's internal thought process:
1. "I need to extract data from the PDF first"
   - → Calls `extract_pdf_tool`
   - → Gets: Property address, price, unit count, etc.

2. "Now I need to check the financials"
   - → Calls `analyze_financials_tool`
   - → Gets: 14.2% projected return

3. "Let me research the Austin market"
   - → Calls `research_market_tool`
   - → Gets: Market is strong, rents increasing

4. "Now I can make a recommendation"
   - → Thinks: 14.2% > 12% minimum ✓
   - → Thinks: $8.5M < $10M maximum ✓
   - → Thinks: Austin is approved ✓
   - → Thinks: 156 units > 100 units ✓
   - → **Conclusion: "RECOMMEND - Meets all criteria"**

**Step 4: Results Saved & Sent (5 seconds)**

```python
# Save to database
database.save({
    "customer_id": "acme_investments",
    "deal_id": "austin_property_2025",
    "recommendation": "BUY",
    "score": 8.5/10,
    "reason": "Strong returns, growing market, meets all criteria"
})

# Send notification
send_email("acme@example.com", "Your deal analysis is ready!")
send_slack(acme_workspace, "#deals", "New analysis: RECOMMEND BUY")
```

**Step 5: Agent Disappears**

The agent is destroyed, memory cleared. Next customer gets a completely fresh agent.

---

### Your Decision Tree: Which Option Should You Pick?

**Just Starting (0-25 customers):**
- → **Pattern 1: Ephemeral agents per request**
- Simplest code
- Costs slightly more but you're not processing many deals yet
- Easy to debug when things go wrong
- Can always upgrade later

**Growing (25-150 customers):**
- → **Still Pattern 1**, but monitor performance
- If analyses start taking >30 seconds, consider Pattern 2
- If your server CPU is constantly at 100%, consider Pattern 2
- Otherwise stick with Pattern 1 - simpler is better

**Scaling (150+ customers):**
- → **Pattern 3: Background workers**
- You're now processing 1000+ deals/month
- Need reliability (one customer's broken deal shouldn't slow everyone)
- Can justify the complexity
- Can afford DevOps help

---

### The Most Important Part: Start Simple

Here's my honest advice:

**Month 1-3 (Launch):**
- Use Pattern 1 (fresh agents)
- Don't overthink it
- Focus on getting customers
- Costs $0.20/analysis instead of $0.15? Who cares, you have 5 customers

**Month 4-6 (Traction):**
- If you have 50+ customers and things are slow → Consider Pattern 2
- If everything works fine → DO NOTHING, keep Pattern 1

**Month 7-12 (Scale):**
- If you have 200+ customers → Plan migration to Pattern 3
- Hire a DevOps engineer to help
- This is now a real business, worth the investment

---

### Red Flags to Watch For

**Sign you need to upgrade from Pattern 1 → Pattern 2:**
- ⚠️ Analyses taking >30 seconds regularly
- ⚠️ Customers complaining about speed
- ⚠️ Your server CPU constantly at 90%+

**Sign you need to upgrade from Pattern 2 → Pattern 3:**
- ⚠️ Processing 500+ deals/day
- ⚠️ One broken deal analysis crashes everything
- ⚠️ You're waking up at 3am to restart servers

**Sign something is WRONG and you messed up:**
- 🚨 Customers seeing each other's deals (data leak!)
- 🚨 Costs suddenly jumping 10x (runaway agents)
- 🚨 Analyses giving weird results (context contamination)

---

### TL;DR - The Simplest Possible Explanation

**What are agents?**
Smart assistants that can use tools and make decisions.

**Why use them?**
They handle complex, multi-step tasks better than you manually coding every step.

**What's the catch?**
They cost slightly more and you need to be careful about keeping customers' data separate.

**Which option for your SaaS?**
Start with Pattern 1 (fresh agent per customer). It's simple, safe, and you can always upgrade later.

**When to worry about scale?**
Not until you have 100+ customers. Before that, keep it simple.

---

**Now you have both the big vision AND the practical implementation details for building Dream's multi-agent architecture. Start with Pattern 1, build your first 5 agents, and scale from there!**
