# Dream Multi-Agent Architecture - Conversation Context

**Date:** January 11, 2026
**Context:** Planning session for Dream's 100-agent architecture

## Key Decisions Made

### 1. Architecture Pattern
- **100+ specialized agents** organized by Shieldstone Manual v2's 8 phases
- **LangGraph orchestration** for parallel/sequential execution
- **Multi-tenant design** with ephemeral agents (Pattern 1 for MVP)
- **Hybrid AI + Python** approach (Claude for reasoning, Python for calculations)

### 2. Cost Optimization Strategy
**Important:** We're NOT using expensive models for every agent.
- Use **cheaper LLMs** (Gemini Flash, Haiku) for simple tasks
- Reserve **Sonnet 4.5** only for complex reasoning
- **Prompt caching** reduces Shieldstone manual costs by 90%
- **Target cost: $0.15-0.20 per analysis** (cheaper than manual Sonnet calls)

### 3. Scaling Strategy
- **Year 1 (0-150 customers):** Pattern 1 - Ephemeral Agents
  - Fresh agent per request
  - Simple, safe, easy to debug
  - Acceptable $0.20/analysis cost at low volume

- **Year 2 (150-500 customers):** Pattern 2 - Agent Pooling
  - Pre-warmed agent pool
  - Faster response times
  - Cost drops to ~$0.18/analysis

- **Year 3 (500+ customers):** Pattern 3 - Celery Workers
  - Background task queue
  - Horizontal scaling
  - Cost optimized to ~$0.15/analysis

### 4. Directory Structure
```
agent_architecture/
├── agents/
│   ├── phase1_property_fundamentals/  (15 agents)
│   ├── phase2_market_analysis/        (12 agents)
│   ├── phase3_financial_modeling/     (10 agents)
│   ├── phase4_risk_assessment/        (15 agents)
│   ├── phase5_value_add_strategy/     (8 agents)
│   ├── phase6_financing_structure/    (8 agents)
│   ├── phase7_investment_returns/     (10 agents)
│   ├── phase8_exit_strategy/          (6 agents)
│   ├── cross_phase/                   (10 agents)
│   └── utilities/                     (6 agents)
├── orchestration/
├── tools/
└── tests/
```

### 5. First 5 Agents to Build (MVP - Weeks 1-2)
1. **RentRollAgent** (Phase 1) - Analyzes rent rolls
2. **OMAnalyzerAgent** (Phase 1) - Extracts OM data
3. **MarketResearchAgent** (Phase 2) - Real-time market research
4. **ProFormaBuilderAgent** (Phase 3) - 10-year financial projections
5. **ShieldstoneSynthesizerAgent** (Cross-phase) - Synthesizes all results

## Model Selection Strategy (IMPORTANT!)

**DO NOT use Sonnet 4.5 for everything!**

### Use Cases by Model:

**Gemini Flash 2.0 ($0.10 per 1M tokens):**
- Simple data extraction (rent roll parsing, OM field extraction)
- Basic calculations that don't require reasoning
- File format conversions
- ~40% of agent tasks

**Claude Haiku ($0.25/$1.25 per 1M tokens):**
- Structured data analysis
- Template-based outputs
- Simple decision trees
- ~30% of agent tasks

**Claude Sonnet 4.5 ($3/$15 per 1M tokens):**
- Complex reasoning (should we buy this deal?)
- Multi-step analysis requiring judgment
- Synthesis across multiple data sources
- Final recommendations
- ~30% of agent tasks (reserve for high-value tasks)

### Example Cost Breakdown:

**Screening Analysis (8 agents):**
- 3 extraction agents (Gemini Flash): $0.01
- 3 analysis agents (Haiku): $0.05
- 2 synthesis agents (Sonnet): $0.10
- **Total: ~$0.16** (vs $0.25 if all Sonnet)

**Full Underwriting (30 agents):**
- 12 extraction/simple agents (Flash): $0.03
- 10 analysis agents (Haiku): $0.15
- 8 complex/synthesis agents (Sonnet): $0.35
- **Total: ~$0.53** (vs $0.80 if all Sonnet)

## Integration with Shieldstone Manual

Each agent maps to specific Shieldstone phase:
- System prompt includes relevant phase content (cached)
- Python calculation modules for precise math
- Customer-specific overrides stored in PostgreSQL

## Multi-Tenant Safety

**Critical Rule:** Fresh agent per customer, state from database
```python
# ✅ CORRECT
def analyze_deal(customer_id, deal_id):
    customer_config = db.get(customer_id)
    agent = Agent(instructions=f"Analyze for {customer_config}")
    result = agent.run(...)
    return result

# ❌ WRONG - Never share agents!
global_agent = Agent()  # Dangerous!
```

## Next Steps After This Conversation

1. **Implement BaseAgent class** with:
   - Shieldstone manual loading
   - Model selection logic (Flash/Haiku/Sonnet)
   - Prompt caching
   - Cost tracking

2. **Build first agent** (RentRollAgent):
   - Use Gemini Flash for extraction
   - Use Haiku for analysis
   - Return structured JSON

3. **Create orchestrator**:
   - Plans which agents to use
   - Selects appropriate model per agent
   - Tracks total cost per request

## Files to Reference

When building new agents, always reference:
1. `DREAM_MULTI_AGENT_ARCHITECTURE.md` - Complete architecture
2. `README.md` - Quick start guide
3. `STRUCTURE.md` - Directory organization
4. This file (`CONVERSATION_CONTEXT.md`) - Key decisions

## Questions Answered

**Q: Why not just use Sonnet for everything?**
A: Cost! Using cheaper models for simple tasks saves 60-70% on costs while maintaining quality.

**Q: How do we keep customer data separate?**
A: Ephemeral agents created per request with customer config from database. No shared state.

**Q: Can we handle 500+ customers on one server?**
A: Yes! Most time is waiting for LLM APIs, not CPU. Single server handles 10K-50K requests/month.

**Q: What if we need to scale beyond 500 customers?**
A: Migrate to Pattern 3 (Celery workers) with background task queue.

## Conversation ID (for reference)

This conversation happened in Claude Code (desktop) on January 11, 2026.
All decisions and architecture are captured in the markdown files in this directory.

---

**To continue this work from mobile/desktop Claude:**
1. Open Claude with GitHub access
2. Reference this file: `agent_architecture/CONVERSATION_CONTEXT.md`
3. Ask Claude to read the architecture files
4. Specify which agent you want to build

Example prompt:
```
I want to build the RentRollAgent for Dream.

Read these files:
- agent_architecture/CONVERSATION_CONTEXT.md
- agent_architecture/DREAM_MULTI_AGENT_ARCHITECTURE.md
- agent_architecture/README.md

Follow the architecture patterns and model selection strategy
documented there. Use Gemini Flash for extraction, Haiku for
analysis. Return structured JSON output.
```
