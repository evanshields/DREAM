# Agent Architecture Directory Structure

## Complete Directory Tree

```
agent_architecture/
│
├── DREAM_MULTI_AGENT_ARCHITECTURE.md    # Complete architecture specification (99KB)
├── README.md                             # Quick start guide and overview
├── STRUCTURE.md                          # This file
├── .env.example                          # Environment variable template
├── requirements.txt                      # Python dependencies
│
├── agents/                               # All agent implementations
│   ├── __init__.py                       # Package initialization
│   ├── base_agent.py                     # BaseAgent class (TODO)
│   ├── agent_registry.py                 # Central agent registry (TODO)
│   │
│   ├── phase1_property_fundamentals/     # Phase 1: Property Fundamentals
│   │   ├── __init__.py
│   │   ├── rent_roll_analyzer.py         # Analyzes rent rolls
│   │   ├── om_analyzer.py                # Extracts data from OMs
│   │   ├── t12_analyzer.py               # Analyzes T12 financials
│   │   ├── property_condition_assessor.py
│   │   ├── unit_mix_analyzer.py
│   │   └── ... (15 total agents planned)
│   │
│   ├── phase2_market_analysis/           # Phase 2: Market Analysis
│   │   ├── __init__.py
│   │   ├── market_research_agent.py      # Real-time market research
│   │   ├── demographic_analyzer.py       # Census/demographic data
│   │   ├── comparable_sales_agent.py     # Comps analysis
│   │   ├── supply_demand_analyzer.py
│   │   ├── submarket_analyzer.py
│   │   └── ... (12 total agents planned)
│   │
│   ├── phase3_financial_modeling/        # Phase 3: Financial Modeling
│   │   ├── __init__.py
│   │   ├── pro_forma_builder.py          # 10-year pro forma
│   │   ├── revenue_optimizer.py          # Revenue projections
│   │   ├── expense_analyzer.py           # Operating expenses
│   │   ├── rent_growth_modeler.py
│   │   ├── other_income_analyzer.py
│   │   └── ... (10 total agents planned)
│   │
│   ├── phase4_risk_assessment/           # Phase 4: Risk Assessment
│   │   ├── __init__.py
│   │   ├── market_risk_analyzer.py
│   │   ├── execution_risk_assessor.py
│   │   ├── environmental_risk_agent.py
│   │   ├── legal_risk_agent.py
│   │   ├── operational_risk_agent.py
│   │   └── ... (15 total agents planned)
│   │
│   ├── phase5_value_add_strategy/        # Phase 5: Value-Add Strategy
│   │   ├── __init__.py
│   │   ├── renovation_planner.py
│   │   ├── repositioning_strategist.py
│   │   ├── amenity_optimizer.py
│   │   ├── operational_improvement_agent.py
│   │   └── ... (8 total agents planned)
│   │
│   ├── phase6_financing_structure/       # Phase 6: Financing Structure
│   │   ├── __init__.py
│   │   ├── debt_optimizer.py
│   │   ├── equity_structure_agent.py
│   │   ├── capital_stack_modeler.py
│   │   ├── lender_requirements_agent.py
│   │   └── ... (8 total agents planned)
│   │
│   ├── phase7_investment_returns/        # Phase 7: Investment Returns
│   │   ├── __init__.py
│   │   ├── irr_calculator.py             # IRR calculations
│   │   ├── cash_flow_analyzer.py         # Cash-on-cash analysis
│   │   ├── equity_multiple_calculator.py
│   │   ├── sensitivity_analyzer.py       # Sensitivity analysis
│   │   ├── return_attribution_agent.py
│   │   └── ... (10 total agents planned)
│   │
│   ├── phase8_exit_strategy/             # Phase 8: Exit Strategy
│   │   ├── __init__.py
│   │   ├── exit_strategist.py
│   │   ├── hold_period_optimizer.py
│   │   ├── disposition_planner.py
│   │   ├── market_timing_agent.py
│   │   └── ... (6 total agents planned)
│   │
│   ├── cross_phase/                      # Cross-cutting agents
│   │   ├── __init__.py
│   │   ├── shieldstone_synthesizer.py    # Synthesizes all results
│   │   ├── diligence_tracker.py          # Due diligence tracking
│   │   ├── third_party_report_analyzer.py
│   │   ├── risk_mitigation_agent.py
│   │   ├── report_generator.py
│   │   └── ... (10 total agents planned)
│   │
│   └── utilities/                        # Utility agents
│       ├── __init__.py
│       ├── pdf_parser_agent.py           # PDF extraction
│       ├── excel_parser_agent.py         # Excel extraction
│       ├── data_formatter_agent.py
│       └── ... (6 total agents planned)
│
├── orchestration/                        # Agent orchestration logic
│   ├── __init__.py
│   ├── orchestrator.py                   # Main orchestrator (TODO)
│   ├── workflow_builder.py               # Dynamic workflow builder (TODO)
│   ├── agent_nodes.py                    # LangGraph node wrappers (TODO)
│   ├── state.py                          # AgentState definition (TODO)
│   └── patterns.py                       # Common workflow patterns (TODO)
│
├── tools/                                # Tools that agents can use
│   ├── __init__.py
│   ├── document_tools.py                 # PDF/Excel extraction (TODO)
│   ├── calculation_tools.py              # Shieldstone calculations (TODO)
│   ├── market_research_tools.py          # Perplexity/web search (TODO)
│   └── database_tools.py                 # Database queries (TODO)
│
└── tests/                                # Agent tests
    ├── __init__.py
    ├── test_base_agent.py                # Base agent tests (TODO)
    ├── test_rent_roll_analyzer.py        # Rent roll agent tests (TODO)
    └── ... (tests for each agent)
```

## Agent Count by Phase

| Phase | Description | Planned Agents |
|-------|-------------|----------------|
| Phase 1 | Property Fundamentals | ~15 |
| Phase 2 | Market Analysis | ~12 |
| Phase 3 | Financial Modeling | ~10 |
| Phase 4 | Risk Assessment | ~15 |
| Phase 5 | Value-Add Strategy | ~8 |
| Phase 6 | Financing Structure | ~8 |
| Phase 7 | Investment Returns | ~10 |
| Phase 8 | Exit Strategy | ~6 |
| Cross-Phase | Synthesizers, trackers | ~10 |
| Utilities | Parsers, formatters | ~6 |
| **TOTAL** | | **~100 agents** |

## Next Steps: Building the Foundation

### Week 1-2: MVP (5 Core Agents)

1. **Create BaseAgent class** (`agents/base_agent.py`)
   - Shieldstone manual loading
   - Prompt caching
   - Standard run method

2. **Build 5 core agents:**
   - `phase1_property_fundamentals/rent_roll_analyzer.py`
   - `phase1_property_fundamentals/om_analyzer.py`
   - `phase2_market_analysis/market_research_agent.py`
   - `phase3_financial_modeling/pro_forma_builder.py`
   - `cross_phase/shieldstone_synthesizer.py`

3. **Create orchestration layer:**
   - `orchestration/state.py` (AgentState TypedDict)
   - `orchestration/agent_nodes.py` (LangGraph wrappers)
   - `orchestration/orchestrator.py` (simple sequential workflow)

4. **Write tests:**
   - `tests/test_base_agent.py`
   - `tests/test_rent_roll_analyzer.py`

### Week 3-4: Multi-Agent Foundation (15 Agents)

Build 10 more agents across phases 1-7, add:
- Dynamic workflow builder
- Parallel execution
- Customer configuration loading

### Week 5+: Scale to 100 Agents

Continue building specialized agents according to roadmap.

## Integration Points

### With Main Dream App

```python
# In backend/api/routes/deals.py
from agent_architecture.orchestration.orchestrator import DreamOrchestrator

@app.post("/api/deals/{deal_id}/analyze")
async def analyze_deal(deal_id: str, tenant_id: str):
    orchestrator = DreamOrchestrator(tenant_id)
    result = await orchestrator.analyze_deal(deal_id)
    return result
```

### With Shieldstone Manual

```python
# Agents load Shieldstone manual sections
from agent_architecture.agents.base_agent import BaseAgent

class RentRollAgent(BaseAgent):
    def get_shieldstone_phase(self) -> int:
        return 1  # Phase 1: Property Fundamentals
```

### With Database

```python
# Customer configs loaded from PostgreSQL
tenant_config = await db.fetchrow(
    "SELECT investment_criteria FROM tenants WHERE id = $1",
    tenant_id
)
```

## Development Commands

```bash
# Set up environment
cd agent_architecture
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest tests/

# Run specific test
pytest tests/test_rent_roll_analyzer.py -v

# Type checking (if using mypy)
mypy agents/

# Format code (if using black)
black agents/
```

## Status

- [x] Directory structure created
- [x] Architecture documentation complete
- [x] README and setup files created
- [ ] BaseAgent class implementation
- [ ] First agent (RentRollAgent) implementation
- [ ] Orchestration layer
- [ ] Tests
- [ ] Integration with main app

---

**Ready to start building! Next: Implement `agents/base_agent.py`**
