# Guide: Seamless Agent Development Across Platforms

**How to build AI agents that work seamlessly across Claude Code (Desktop/Cursor) and Claude Mobile/iPad apps**

---

## 🎯 The Problem This Solves

You want to:
- Start coding agents on your desktop in Claude Code/Cursor
- Continue the same conversation on your phone while getting coffee
- Have full context available anywhere, anytime
- Track progress across all platforms automatically

This guide shows you how to set up ANY codebase for seamless agent development across all Claude platforms.

---

## 📋 Prerequisites

1. **GitHub Repository** for your project
2. **Claude Code** installed (Desktop or Cursor integration)
3. **Claude Mobile/iPad App** with GitHub integration
4. **Claude.ai Desktop** (optional, for browser-based work)

---

## 🏗️ Setup Steps (One-Time Per Project)

### Step 1: Create Agent Architecture Directory

In your project root, create this structure:

```bash
cd your-project-name
mkdir -p agent_architecture/agents
mkdir -p agent_architecture/orchestration
mkdir -p agent_architecture/tools
mkdir -p agent_architecture/tests
mkdir -p .claude/skills
```

### Step 2: Create Core Documentation Files

Create these three essential files:

#### A. `agent_architecture/AGENT_ARCHITECTURE.md`

This is your **complete technical specification**. Include:

```markdown
# [Your App Name] Multi-Agent Architecture

## System Overview
[What your multi-agent system does]

## Agent Organization
[How your agents are structured - by feature, domain, etc.]

## Technology Stack
- Agent Orchestration: LangGraph
- AI APIs: Claude, Gemini, etc.
- Database: PostgreSQL, etc.
- Deployment: Your hosting setup

## Cost Strategy
- Model selection guidelines
- When to use Flash vs Haiku vs Sonnet
- Target cost per operation

## Agent Patterns
[Templates and patterns for your agents]

## Multi-Tenancy
[If applicable - how you handle multiple customers]

## Implementation Roadmap
[Your phased build plan]
```

**Example:** See `dream_vision_claude_code/agent_architecture/DREAM_MULTI_AGENT_ARCHITECTURE.md`

---

#### B. `agent_architecture/CONVERSATION_CONTEXT.md`

This is your **living context file** that updates as you build. Template:

```markdown
# [Your App Name] Agent Development - Context

**Last Updated:** [Date]

## Key Decisions Made

### Architecture Pattern
- [Your chosen architecture]
- [Why you chose it]

### Cost Optimization Strategy
- Model selection by task type
- Target costs
- Optimization techniques

### Agent Organization
- [How agents are grouped]
- [Total agent count target]

## Model Selection Strategy

### Gemini Flash 2.0 ($0.10/1M tokens)
Use for:
- [Task type 1]
- [Task type 2]
- ~X% of agent tasks

### Claude Haiku ($0.25/$1.25/1M tokens)
Use for:
- [Task type 1]
- [Task type 2]
- ~X% of agent tasks

### Claude Sonnet 4.5 ($3/$15/1M tokens)
Use for:
- [Task type 1]
- [Task type 2]
- ~X% of agent tasks

## Agent Progress Tracker

**Total agents planned:** [Number]
**Agents built:** 0
**Agents in progress:** None

### By Category:
- **[Category 1]:** 0/X built
- **[Category 2]:** 0/X built
- **[Category 3]:** 0/X built

---

## Agents Built

*Use `/[your-command]` to build agents and automatically update this section.*

<!-- Template entry:
### [AgentName] - Built on [Date]
- **Model:** [Flash/Haiku/Sonnet]
- **Purpose:** [One sentence]
- **Cost per run:** ~$X.XX
- **Location:** `agents/[category]/[agent_name].py`
- **Key decisions:**
  - [Decision 1]
  - [Decision 2]
- **Dependencies:** [Other agents it needs]
- **Used by:** [Which features use it]
-->

---

## Quick Start Commands

### Build a new agent:
```
/[your-command]
```

### Test an agent:
```bash
pytest tests/test_[agent_name].py
```

### Run full test suite:
```bash
pytest agent_architecture/tests/
```

## Integration with Main App

[How agents integrate with your main application code]

## Files to Reference

When building agents, reference:
1. `AGENT_ARCHITECTURE.md` - Complete technical spec
2. `CONVERSATION_CONTEXT.md` - Current progress and decisions (this file)
3. `STRUCTURE.md` - Directory organization
```

**Example:** See `dream_vision_claude_code/agent_architecture/CONVERSATION_CONTEXT.md`

---

#### C. `agent_architecture/STRUCTURE.md`

Document your directory structure:

```markdown
# Agent Architecture Directory Structure

## Complete Directory Tree

```
agent_architecture/
├── AGENT_ARCHITECTURE.md       # Complete architecture spec
├── CONVERSATION_CONTEXT.md     # Living context & progress
├── STRUCTURE.md                # This file
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
│
├── agents/                     # All agent implementations
│   ├── __init__.py
│   ├── base_agent.py           # Base class
│   ├── agent_registry.py       # Central registry
│   │
│   ├── [category_1]/           # Organized by your logic
│   │   ├── [agent_1].py
│   │   └── [agent_2].py
│   │
│   └── [category_2]/
│       ├── [agent_3].py
│       └── [agent_4].py
│
├── orchestration/              # Agent orchestration
│   ├── orchestrator.py
│   └── workflow_builder.py
│
├── tools/                      # Tools agents use
│   └── [tool_files].py
│
└── tests/                      # Agent tests
    └── test_[agent_name].py
```

## Agent Count by Category

| Category | Description | Planned Agents |
|----------|-------------|----------------|
| [Category 1] | [Description] | ~X |
| [Category 2] | [Description] | ~X |
| **TOTAL** | | **~X agents** |

## Next Steps

[Your implementation plan]
```

---

### Step 3: Create Your Custom Slash Command (Skill)

Create `.claude/skills/[your-command].claud`:

```markdown
---
name: [your-command]
description: Load [your app] agent architecture and help build new agents
tags: [[your-app], agents, architecture]
---

# [Your App Name] Agent Builder

You are helping build a new agent for the [Your App Name] platform.

## Step 1: Load Context

First, read these files from the repository:

1. **agent_architecture/CONVERSATION_CONTEXT.md** - Current progress and decisions
2. **agent_architecture/AGENT_ARCHITECTURE.md** - Complete architecture spec
3. **agent_architecture/STRUCTURE.md** - Directory structure

## Step 2: Understand Requirements

Ask the user which agent they want to build. Get clarity on:
- **Agent name** (e.g., "UserAnalyzer", "DataProcessor")
- **Category** this agent belongs to
- **Primary function** (what does this agent do?)
- **Input data** (what data does it need?)
- **Output format** (what should it return?)

## Step 3: Model Selection

Based on agent complexity, recommend the appropriate LLM:

- **Gemini Flash 2.0** ($0.10/1M tokens) - Use for:
  - Simple data extraction and parsing
  - Format conversions
  - Template-based outputs
  - **~40% of agent tasks**

- **Claude Haiku** ($0.25/$1.25 per 1M tokens) - Use for:
  - Structured data analysis
  - Moderate complexity reasoning
  - Classification tasks
  - **~30% of agent tasks**

- **Claude Sonnet 4.5** ($3/$15 per 1M tokens) - Use for:
  - Complex multi-step reasoning
  - High-stakes decisions
  - Synthesis across data sources
  - **~30% of agent tasks (reserve for high-value)**

## Step 4: Follow Architecture Patterns

Build the agent following patterns from the architecture docs:

### File Structure
```
agent_architecture/agents/[category]/[agent_name].py
```

### Agent Template
```python
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class {AgentName}Agent(BaseAgent):
    """[Description of what this agent does]"""

    def get_category(self) -> str:
        return "[category]"

    def get_recommended_model(self) -> str:
        """Which model to use: 'flash', 'haiku', or 'sonnet'"""
        return "haiku"  # or "flash" or "sonnet"

    def get_system_prompt(self) -> str:
        rules = self.config.get('business_rules', {})

        return f"""You are a [role description].

# YOUR TASK

[Specific instructions]

Return JSON with these keys: [key1, key2, key3]
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

### Registry Entry
```python
# In agents/agent_registry.py
"{agent_name}": {
    "class": {AgentName}Agent,
    "description": "One sentence description",
    "category": "[category]",
    "model": "{flash|haiku|sonnet}",
    "inputs": ["what it needs"],
    "outputs": ["what it produces"],
    "typical_runtime": "X seconds",
    "cost_per_run": "$X.XX",
    "state_key": "{agent_name}_result"
}
```

### Test Template
```python
# In tests/test_{agent_name}.py
from agents.[category].{agent_name} import {AgentName}Agent

def test_{agent_name}():
    agent = {AgentName}Agent(config={})

    test_input = {
        "field1": "test_value",
        "field2": 12345
    }

    result = agent.execute(test_input)

    assert result['parsed_result'] is not None
    assert 'expected_key' in result['parsed_result']
```

## Step 5: Implementation

After gathering requirements:

1. **Create the agent file** in the appropriate category directory
2. **Implement the agent class** following the template
3. **Register the agent** in agent_registry.py
4. **Create the test file**
5. **Verify it works** by running the test

## Step 6: Update CONVERSATION_CONTEXT.md

**CRITICAL:** After successfully building the agent, update the conversation context:

Read `agent_architecture/CONVERSATION_CONTEXT.md` and add a new entry under "## Agents Built" section:

```markdown
### [Agent Name] ([Category]) - Built on [Date]
- **Model:** [Flash/Haiku/Sonnet]
- **Purpose:** [One sentence description]
- **Cost per run:** ~$[X.XX]
- **Location:** `agents/[category]/[agent_name].py`
- **Key decisions:**
  - [Decision 1]
  - [Decision 2]
- **Dependencies:** [Which agents does it depend on?]
- **Used by:** [Which features use this agent?]
```

Then update the agent count:
```markdown
## Agent Progress Tracker

Total agents planned: [X]
Agents built: [increment this number]

By category:
- [Category 1]: [X/Y] built
- [Category 2]: [X/Y] built
```

**Always commit this update** after building an agent!

## Step 7: Integration

Explain how this agent fits into your system:
- Which other agents does it depend on?
- Which agents use its output?
- Which features/workflows use this agent?

## Important Reminders

- ✅ **Cost optimized** - Use cheapest model that can do the job
- ✅ **Structured output** - Return JSON with clear, documented keys
- ✅ **Testable** - Write tests that verify core functionality
- ✅ **Update CONVERSATION_CONTEXT.md** - Keep the context file current!
- ✅ **Multi-tenant safe** (if applicable) - Isolate customer data

## Ask the User

Now ask: **"Which agent would you like to build?"**

Then follow the steps above to help them create it!
```

**Example:** See `.claude/skills/dreamagent.claud`

---

### Step 4: Create Supporting Files

#### `agent_architecture/requirements.txt`
```txt
# Core Framework
anthropic==0.18.1
google-generativeai==0.3.2

# Agent Orchestration
langgraph==0.2.0
langchain-anthropic==0.1.0
langchain-core==0.2.0

# Database (adjust for your stack)
sqlalchemy==2.0.25
asyncpg==0.29.0

# Utilities
pydantic==2.5.3
python-dotenv==1.0.1

# Testing
pytest==8.0.0
pytest-asyncio==0.23.3
```

#### `agent_architecture/.env.example`
```bash
# AI API Keys
ANTHROPIC_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

#### `agent_architecture/README.md`
```markdown
# [Your App] Multi-Agent Architecture

Quick start guide for building agents.

## Setup

```bash
cd agent_architecture
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys
```

## Building Agents

Use the slash command:
```
/[your-command]
```

## Testing

```bash
pytest tests/
```

## Documentation

- **Architecture Overview:** `AGENT_ARCHITECTURE.md`
- **Current Progress:** `CONVERSATION_CONTEXT.md`
- **Directory Structure:** `STRUCTURE.md`
```

---

### Step 5: Commit Everything to GitHub

```bash
git add agent_architecture/ .claude/
git commit -m "feat: Add multi-agent architecture with cross-platform development

- Create agent_architecture/ with complete structure
- Add /{your-command} skill for seamless agent building
- Include architecture docs and progress tracking
- Works across Claude Code, mobile, and desktop

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

git push origin main
```

---

## 🎉 You're Done! Now You Can:

### On Desktop (Claude Code/Cursor):
```
/[your-command]
```

### On Mobile/iPad (Claude App):
```
/[your-command]
```

### On Desktop Browser (Claude.ai):
```
/[your-command]
```

---

## 🔄 How It Works

### When You Type `/[your-command]`:

1. **Loads context** from your GitHub repo:
   - `CONVERSATION_CONTEXT.md` (current progress)
   - `AGENT_ARCHITECTURE.md` (complete spec)
   - `STRUCTURE.md` (directory layout)

2. **Asks you** which agent to build

3. **Guides you** through:
   - Model selection (optimize costs)
   - Code generation
   - Testing
   - Integration

4. **Updates** `CONVERSATION_CONTEXT.md` automatically:
   - Increments agent count
   - Documents decisions
   - Tracks dependencies

5. **Commits** the changes to GitHub

### Next Session (Any Platform):

You type `/[your-command]` and it:
- ✅ Knows which agents are already built
- ✅ Knows what decisions were made
- ✅ Knows your cost optimization strategy
- ✅ Shows exactly where you left off

**No context loss. Ever.**

---

## 📱 Real-World Workflow Example

### Monday Morning (Desktop):
```
/dreamagent
> "Build RentRollAnalyzer"
[Agent built, tested, committed]
```

### Tuesday Afternoon (Coffee Shop, iPhone):
```
/dreamagent
> "Build MarketResearchAgent"
[Claude sees RentRollAnalyzer was already built]
[Builds new agent, updates context]
```

### Wednesday Evening (Home, iPad):
```
/dreamagent
> "What agents have we built so far?"
[Claude shows: 2/100 agents built, lists them]
> "Build ProFormaBuilder next"
[Continues seamlessly]
```

---

## 🎯 Best Practices

### 1. Always Update CONVERSATION_CONTEXT.md
Every agent built = update the context file. This is your "source of truth" for progress.

### 2. Commit Often
After each agent, commit to GitHub. Makes it available everywhere instantly.

### 3. Use the Slash Command
Don't manually load files - let the skill do it. Ensures consistency.

### 4. Document Decisions
When you make a key decision (model choice, architecture change), add it to CONVERSATION_CONTEXT.md.

### 5. Test Before Moving On
Don't build 5 agents without testing. Test each one as you go.

---

## 🚀 Scaling This Approach

### For Multiple Projects:

Each project gets its own:
- `agent_architecture/` directory
- Custom skill (`/dreamagent`, `/builtdifferentagent`, `/inspireagent`)
- Context files tracked separately

But the **pattern is identical**:
1. Architecture docs in repo
2. Custom skill loads them
3. Progress tracked in CONVERSATION_CONTEXT.md
4. Works everywhere

---

## 📚 Example Projects Using This Pattern

### Dream (Real Estate):
- **Skill:** `/dreamagent`
- **Agents:** 100 planned (Shieldstone 8 phases)
- **Context:** `dream_vision_claude_code/agent_architecture/`

### Built Different (Your Next App):
- **Skill:** `/builtdifferentagent`
- **Agents:** [Your count] planned
- **Context:** `built_different/agent_architecture/`

### INSPIRE (Your Other App):
- **Skill:** `/inspireagent`
- **Agents:** [Your count] planned
- **Context:** `inspire/agent_architecture/`

---

## 🛠️ Customization Checklist

When setting up a new project, customize:

- [ ] Replace `[Your App Name]` with your actual app name
- [ ] Replace `[your-command]` with your chosen slash command
- [ ] Define your agent categories (replace "Shieldstone phases" with your structure)
- [ ] Set target agent count
- [ ] Define model selection criteria for your use case
- [ ] Adjust cost targets
- [ ] Update integration points with your main app
- [ ] Set up project-specific tests

---

## 💰 Cost Optimization Across Projects

### Universal Principle:
**Use the cheapest model that can do the job.**

### Model Selection Matrix:

| Task Type | Recommended Model | Cost Impact |
|-----------|------------------|-------------|
| Data extraction/parsing | Gemini Flash | 10% of cost |
| Structured analysis | Claude Haiku | 20% of cost |
| Complex reasoning | Claude Sonnet | 70% of cost |

### Optimize By:
1. **Batching** simple tasks to Flash
2. **Caching** frequently used prompts (90% savings)
3. **Streaming** for better UX without cost increase
4. **Monitoring** actual costs and adjusting

---

## 📖 Additional Resources

### Claude Documentation:
- [Claude Code Guide](https://docs.anthropic.com/claude/docs)
- [Building with Claude SDK](https://github.com/anthropics/anthropic-sdk-python)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)

### Your Project Docs:
- `AGENT_ARCHITECTURE.md` - Complete technical spec
- `CONVERSATION_CONTEXT.md` - Living progress tracker
- `STRUCTURE.md` - Directory organization

---

## 🎓 Summary: The 5-Minute Setup

1. **Create** `agent_architecture/` directory structure
2. **Write** 3 core docs (Architecture, Context, Structure)
3. **Create** `.claude/skills/[your-command].claud`
4. **Commit** to GitHub
5. **Type** `/[your-command]` anywhere, anytime

**Result:** Seamless agent development across all platforms with zero context loss.

---

## ✅ Success Criteria

You've successfully replicated this pattern when:

- ✅ You can type your custom slash command on any platform
- ✅ Full context loads automatically from GitHub
- ✅ Progress tracking updates automatically
- ✅ You can switch platforms mid-project without losing context
- ✅ New team members can jump in using the same pattern

---

**Built with ❤️ using Claude Code**

*This pattern works for any AI agent development project, any platform, any time.*
