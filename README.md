# DREAM AI

**Development, Real Estate and Asset Management Analysis Interface**

> AI-powered acquisitions intelligence platform for institutional real estate investors

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Status](https://img.shields.io/badge/status-Production%20Ready-green)

---

## 🎯 Overview

DREAM AI transforms real estate deal analysis from a 4-8 hour manual process to an **institutional-quality underwriting in under 7 minutes**. Built on the Shieldstone Technical Underwriting Manual V2.0, it combines AI-powered data extraction with deterministic financial modeling to deliver defensible, auditable investment analysis.

### Core Value Proposition

- **10x Faster:** Reduce deal analysis from 4-8 hours to <7 minutes
- **Institutional Quality:** Follows rigorous Shieldstone methodology
- **Cost Efficient:** $99-199/month vs. $15K-50K/year for traditional tools
- **AI-Native:** Intelligent document processing, market research, and narrative generation
- **Deterministic Calculations:** All financial math in Python (zero hallucination risk)

---

## 🏗️ Architecture

### Stack Overview

```
Frontend:  React + TypeScript + Tailwind CSS
Backend:   Python + FastAPI + PostgreSQL
AI Layer:  Claude (Haiku/Sonnet/Opus) + Perplexity
Financial: Shieldstone Python Library (deterministic calculations)
Hosting:   Vercel (frontend) + Railway (backend)
```

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DREAM AI PLATFORM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  USER UPLOADS DEAL DOCUMENTS                                    │
│  ├── Offering Memorandum (PDF)                                  │
│  ├── T-12 Operating Statement (Excel/PDF)                       │
│  ├── Rent Roll (Excel/PDF)                                      │
│  └── Photos                                                      │
│                                                                  │
│  AI DOCUMENT EXTRACTION (Claude Haiku)                          │
│  ├── Property details, financials, rent roll data               │
│  ├── Confidence scoring on extracted fields                     │
│  └── Flagging uncertain values for review                       │
│                                                                  │
│  MARKET RESEARCH (Perplexity + Public APIs)                     │
│  ├── MSA classification & tier assignment                       │
│  ├── Submarket fundamentals & trends                            │
│  ├── Employment data & top employers                            │
│  └── Demographics & regulatory environment                      │
│                                                                  │
│  SCREENING & SCORING (Shieldstone Section 2)                    │
│  ├── Merit-based screening (no arbitrary cutoffs)               │
│  ├── Risk-adjusted return hurdles                               │
│  ├── Red flag identification                                    │
│  └── Investment score (0-100) with recommendation               │
│                                                                  │
│  PRO FORMA ENGINE (Python - Shieldstone Sections 3-7)           │
│  ├── AI suggests assumptions (Claude Sonnet)                    │
│  ├── User edits any assumption                                  │
│  ├── Python recalculates everything instantly (<100ms)          │
│  └── 10-year DCF with monthly detail                            │
│                                                                  │
│  REPORT GENERATION (AI + Templates)                             │
│  ├── BOE Memo (1-2 pages, <1 min)                              │
│  ├── IC Memo (4-6 pages, <3 min)                               │
│  ├── Full UW Memo (8-10 pages, <5 min)                         │
│  └── Excel export with working formulas                         │
│                                                                  │
│  PIPELINE CRM                                                    │
│  ├── Kanban board with drag-drop stages                        │
│  ├── Task management & team collaboration                       │
│  ├── Document storage & activity logging                        │
│  └── Map, calendar, and list views                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 14+
- Claude API key
- Perplexity API key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/dream-ai.git
cd dream-ai

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database URL

# Run database migrations
alembic upgrade head

# Seed sample data (optional)
python seed.py
```

### Running Locally

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
npm run dev
```

Visit `http://localhost:5173` to access the application.

---

## 📁 Project Structure

```
dream-ai/
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route pages
│   │   ├── lib/               # Utilities & Shieldstone calculations
│   │   ├── types/             # TypeScript definitions
│   │   └── styles/            # Tailwind config & custom CSS
│   └── public/                # Static assets
│
├── backend/
│   ├── app/
│   │   ├── api/               # FastAPI routes
│   │   ├── core/              # Configuration & security
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── extraction/    # Document processing
│   │   │   ├── analysis/      # Deal analysis
│   │   │   ├── proforma/      # Financial modeling
│   │   │   ├── reports/       # Report generation
│   │   │   └── market/        # Market research
│   │   └── shieldstone/       # Shieldstone library
│   │       ├── hurdles.py
│   │       ├── screening.py
│   │       ├── revenue.py
│   │       ├── expenses.py
│   │       ├── financing.py
│   │       └── returns.py
│   └── tests/                 # Test suite
│
├── docs/
│   ├── flows.md               # User flow documentation
│   ├── cre-underwriting-concepts.md  # Analyst guide
│   ├── demo-script.md         # Live demo walkthrough
│   └── api/                   # API documentation
│
└── infrastructure/            # Deployment configs
```

---

## 🧮 Shieldstone Methodology

DREAM AI implements the **Shieldstone Technical Underwriting Manual V2.0** — a comprehensive institutional-grade methodology for multifamily underwriting. This ensures:

- **Consistent Analysis:** Same methodology every time
- **Defensible Outputs:** Every calculation traceable to source
- **Risk-Adjusted Hurdles:** Market tier + property-specific factors
- **Merit-Based Screening:** No arbitrary cutoffs, economics determine viability

### Key Methodologies

| Section | Topic | Implementation |
|---------|-------|----------------|
| 1.1 | Return Hurdles | Market tier + risk adjustments |
| 2.1 | Deal Screening | Merit-based, red flag identification |
| 3 | Revenue Underwriting | In-place, market, pro forma rents |
| 4 | Operating Expenses | State-specific property tax modeling |
| 5 | Capital Expenditure | Renovation budgeting & phasing |
| 6 | Financing | Debt modeling, refinancing (90/90 rule) |
| 7 | Returns Analysis | Exit cap triangulation, sensitivity |
| 13 | Master Workflow | Complete underwriting orchestration |

---

## 💡 Key Features

### Phase 1: Deal Intake & Document Processing
- Drag-drop document upload (PDF, Excel, images)
- AI-powered data extraction with confidence scoring
- Manual override interface for corrections
- Multi-document support (OM, T-12, rent roll, models)

### Phase 2: Screening & Investment Criteria
- Configurable investment criteria by user
- Merit-based screening (no arbitrary disqualifiers)
- Risk-adjusted hurdle calculation
- Deal scoring (0-100) with weighted categories
- Pass/Proceed/Hold/Pass recommendations

### Phase 3: Market Research
- Automated MSA identification & tier classification
- Real-time market data via Perplexity
- Employment trends & top employers
- Demographics & regulatory environment
- Walk Score / Transit Score integration

### Phase 4: Pro Forma Engine
- AI-suggested assumptions (user-editable)
- Complete 10-year DCF modeling
- Monthly and annual cash flow views
- Debt modeling with refinancing scenarios
- Waterfall analysis (GP/LP splits, promotes)
- **Real-time recalculation (<100ms)** — all math in Python, not LLM

### Phase 5: Excel Export
- Working formulas (not just values)
- Professional formatting
- House model templates (institutional standards)
- Custom template mapping (enterprise tier)

### Phase 6: Report Generation
- **BOE Memo** (1-2 pages, ~$0.10 LLM cost)
- **IC Memo** (4-6 pages, ~$0.50 LLM cost)
- **Full UW Memo** (8-10 pages, ~$2.00 LLM cost)
- HTML-first design (beautiful, responsive)
- PDF export via Playwright
- Excel workbooks with multiple sheets

### Phase 7: Pipeline CRM
- Kanban board with drag-drop stages
- List, map, and calendar views
- Task management with assignments
- Notes and activity logging
- Team collaboration
- Document attachments

---

## 🎨 Design Language

DREAM AI uses a **Minimal Pro** design language optimized for financial clarity:

- **Low-chroma, high-clarity** color palette
- **Subtle borders**, minimal shadows
- **Numeric legibility** with tabular figures
- **Professional aesthetic** suitable for institutional presentations
- **Responsive design** for desktop and tablet

See [`design-language-dream.md`](design-language-dream.md) for complete specifications.

---

## 🔐 Security & Compliance

- **SOC2 Type II** compliance (planned)
- **End-to-end encryption** for data at rest and in transit
- **Role-based access control** (admin, analyst, viewer)
- **Audit logging** of all user actions
- **CCPA/GDPR** compliant data handling
- **Secure API key management** via environment variables

---

## 📊 Cost Optimization

DREAM AI uses intelligent LLM routing to minimize API costs while maintaining quality:

| Analysis Type | Target Cost | Volume (50 deals) | Monthly Cost |
|---------------|-------------|-------------------|--------------|
| Document Extraction | $0.05-0.10 | 50 | $2.50-5.00 |
| Deal Screening | $0.02-0.05 | 50 | $1.00-2.50 |
| Market Research | $0.10-0.15 | 50 | $5.00-7.50 |
| BOE Analysis | $0.10-0.20 | 40 | $4.00-8.00 |
| Full UW Analysis | $0.75-1.50 | 8 | $6.00-12.00 |
| IC/Full Memo | $2.00-4.00 | 2 | $4.00-8.00 |
| **Total** | | | **$22.50-43.00** |

**Key Cost Strategies:**
- **Python-first calculations:** All financial math in Python ($0.00 per recalculation)
- **Model routing:** Use cheapest model meeting quality threshold per task
- **Caching:** Market research cached for 7 days
- **Batch processing:** Combine related prompts

---

## 🧪 Testing

```bash
# Run frontend tests
npm test

# Run backend tests
cd backend
pytest

# Run Shieldstone library tests
cd shieldstone_library
pytest tests/

# Check test coverage
pytest --cov=app --cov-report=html
```

### Test Coverage Targets

- **Shieldstone calculations:** 100% (critical path)
- **API endpoints:** >80%
- **Business logic:** >80%
- **UI components:** >70%

---

## 📖 Documentation

- **[User Flows](docs/flows.md)** — Core user journeys through the platform
- **[CRE Underwriting Concepts](docs/cre-underwriting-concepts.md)** — Metrics explained for analysts
- **[Demo Script](docs/demo-script.md)** — Live demo walkthrough with sample deal
- **[API Documentation](docs/api/)** — Complete API reference (OpenAPI/Swagger)
- **[Shieldstone Integration Guide](docs/SHIELDSTONE_INTEGRATION_GUIDE.md)** — Methodology implementation details

---

## 🎯 Competitive Positioning

| Competitor | Price | DREAM AI Advantage |
|------------|-------|-------------------|
| Argus Enterprise | $15K-50K/year | **10x cheaper**, AI-native, faster learning curve |
| RedIQ | $500-1,500/month | More comprehensive analysis, better UX |
| Reonomy | $500-2,000/month | Integrated underwriting (not just data) |
| CoStar | $500-1,500/month | Actionable analysis, not just data |
| Excel + Manual | "Free" (labor) | **90% time savings**, institutional methodology |

---

## 🛣️ Roadmap

### ✅ Phase 1-7 (MVP) — Completed
- Deal intake & document processing
- Screening & investment criteria
- Market research (lite)
- Pro forma engine
- Excel export & assumption mapping
- Report generation (BOE, IC, Full UW)
- Pipeline CRM

### 🔜 Phase 8-10 (Post-MVP)
- Slack AI agent
- Sensitivity & scenario analysis
- Deal sourcing & market alerts

### 🔮 Phase 11+ (Future)
- **SFR Business Purpose Lending** (fix & flip, DSCR rentals)
- **Affordable Housing / LIHTC** (400+ page manual ready)
- Student housing, mobile home parks, senior housing
- Industrial, retail, self-storage, office

---

## 👥 Target Users

- **Investment Firms:** Real estate PE firms evaluating 20-100+ deals/month
- **Emerging Sponsors:** Operators seeking to scale without scaling headcount
- **Family Offices:** Institutional investors wanting AI-powered advantage
- **Brokers & Advisors:** Professionals needing fast, consistent screening

---

## 📞 Support

For technical issues, feature requests, or questions:

- **Email:** support@dream.ai
- **Slack Community:** [Join here](https://dream-ai-community.slack.com)
- **Documentation:** [docs.dream.ai](https://docs.dream.ai)

---

## 📄 License

Proprietary. All rights reserved.

© 2025 DREAM.AI — A Shieldstone Acquisitions Company

---

## 🙏 Acknowledgments

Built with:
- [Claude AI](https://anthropic.com) — Document processing, analysis, report generation
- [Perplexity](https://perplexity.ai) — Real-time market research
- [Shieldstone Manual V2.0](docs/SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md) — Institutional underwriting methodology
- [shadcn/ui](https://ui.shadcn.com) — Beautiful UI components
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python web framework
- [React](https://react.dev) — Frontend framework

---

**DREAM AI** — Institutional-quality underwriting in 7 minutes. No spreadsheets required.
