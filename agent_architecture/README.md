# Dream Multi-Agent Architecture

This directory contains all agent-related code for the Dream real estate underwriting platform.

## Directory Structure

```
agent_architecture/
├── DREAM_MULTI_AGENT_ARCHITECTURE.md  # Complete architecture specification
├── README.md                           # This file
│
├── agents/                             # All agent implementations
│   ├── base_agent.py                   # BaseAgent class (foundation for all agents)
│   ├── agent_registry.py               # Central registry of all agents
│   │
│   ├── phase1_property_fundamentals/   # Shieldstone Phase 1 agents
│   │   ├── rent_roll_analyzer.py
│   │   ├── om_analyzer.py
│   │   ├── t12_analyzer.py
│   │   ├── property_condition_assessor.py
│   │   └── ...
│   │
│   ├── phase2_market_analysis/         # Shieldstone Phase 2 agents
│   │   ├── market_research_agent.py
│   │   ├── demographic_analyzer.py
│   │   ├── comparable_sales_agent.py
│   │   └── ...
│   │
│   ├── phase3_financial_modeling/      # Shieldstone Phase 3 agents
│   │   ├── pro_forma_builder.py
│   │   ├── revenue_optimizer.py
│   │   ├── expense_analyzer.py
│   │   └── ...
│   │
│   ├── phase4_risk_assessment/         # Shieldstone Phase 4 agents
│   │   ├── market_risk_analyzer.py
│   │   ├── environmental_risk_agent.py
│   │   └── ...
│   │
│   ├── phase5_value_add_strategy/      # Shieldstone Phase 5 agents
│   │   ├── renovation_planner.py
│   │   ├── repositioning_strategist.py
│   │   └── ...
│   │
│   ├── phase6_financing_structure/     # Shieldstone Phase 6 agents
│   │   ├── debt_optimizer.py
│   │   ├── equity_structure_agent.py
│   │   └── ...
│   │
│   ├── phase7_investment_returns/      # Shieldstone Phase 7 agents
│   │   ├── irr_calculator.py
│   │   ├── cash_flow_analyzer.py
│   │   └── ...
│   │
│   ├── phase8_exit_strategy/           # Shieldstone Phase 8 agents
│   │   ├── exit_strategist.py
│   │   ├── disposition_planner.py
│   │   └── ...
│   │
│   ├── cross_phase/                    # Cross-cutting agents
│   │   ├── shieldstone_synthesizer.py
│   │   ├── diligence_tracker.py
│   │   └── ...
│   │
│   └── utilities/                      # Utility agents
│       ├── pdf_parser_agent.py
│       ├── excel_parser_agent.py
│       └── ...
│
├── orchestration/                      # Agent orchestration logic
│   ├── orchestrator.py                 # Main orchestrator (plans workflows)
│   ├── workflow_builder.py             # Dynamic LangGraph workflow builder
│   ├── agent_nodes.py                  # LangGraph node wrappers for agents
│   └── state.py                        # AgentState definition
│
├── tools/                              # Tools that agents can use
│   ├── document_tools.py               # PDF/Excel extraction tools
│   ├── calculation_tools.py            # Shieldstone calculation tools
│   ├── market_research_tools.py        # Perplexity/web search tools
│   └── database_tools.py               # Database query tools
│
└── tests/                              # Agent tests
    ├── test_base_agent.py
    ├── test_rent_roll_analyzer.py
    └── ...
```

## Quick Start

### 1. Set up environment

```bash
cd agent_architecture
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run tests

```bash
pytest tests/
```

## Development Workflow

### Adding a New Agent

1. **Create the agent class** in the appropriate phase directory
2. **Register the agent** in `agents/agent_registry.py`
3. **Create a LangGraph node wrapper** in `orchestration/agent_nodes.py`
4. **Write tests** in `tests/`
5. **Deploy** (see deployment guide)

See [DREAM_MULTI_AGENT_ARCHITECTURE.md](DREAM_MULTI_AGENT_ARCHITECTURE.md) for detailed instructions.

## Key Concepts

### Shieldstone Manual Integration

Every agent is mapped to one of the 8 Shieldstone phases:
- **Phase 1:** Property Fundamentals (rent roll, unit mix, condition)
- **Phase 2:** Market Analysis (supply/demand, demographics, trends)
- **Phase 3:** Financial Modeling (pro forma, revenue, expenses)
- **Phase 4:** Risk Assessment (market, execution, structural risk)
- **Phase 5:** Value-Add Strategy (renovations, repositioning)
- **Phase 6:** Financing Structure (debt, equity, capital stack)
- **Phase 7:** Investment Returns (IRR, cash-on-cash, equity multiple)
- **Phase 8:** Exit Strategy (hold period, disposition, timing)

### Multi-Tenant Architecture

All agents support multi-tenancy:
- Customer-specific configurations loaded from database
- Ephemeral agent instances per request (Pattern 1)
- No shared state between customers

### Prompt Caching

Shieldstone manual content is cached in agent system prompts for 90% cost savings.

## Integration with Main App

This agent architecture integrates with the main Dream app via FastAPI endpoints:

```python
# In main app: backend/api/routes/deals.py
from agent_architecture.orchestration.orchestrator import DreamOrchestrator

@app.post("/api/deals/{deal_id}/analyze")
async def analyze_deal(deal_id: str, tenant_id: str):
    orchestrator = DreamOrchestrator(tenant_id)
    result = await orchestrator.analyze_deal(deal_id)
    return result
```

## Documentation

- **Architecture Overview:** [DREAM_MULTI_AGENT_ARCHITECTURE.md](DREAM_MULTI_AGENT_ARCHITECTURE.md)
- **Shieldstone Manual:** `../shieldstone/manual_v2.md`
- **API Documentation:** Auto-generated at `/docs` when running FastAPI

## Roadmap

- [x] Phase 1: Architecture design
- [ ] Phase 2: Build 5 core agents (MVP)
- [ ] Phase 3: Dynamic workflow builder
- [ ] Phase 4: Scale to 50+ agents
- [ ] Phase 5: Due diligence agents
- [ ] Phase 6: Reach 100+ agents
- [ ] Phase 7: Production polish
- [ ] Phase 8: Customer acquisition

See full roadmap in architecture document.
