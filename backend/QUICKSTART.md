# DREAM AI Backend - Quick Start Guide

**Get up and running in 10 minutes**

---

## What You Got

```
backend/
├── schema.prisma                    # Database schema (Prisma)
├── migrations/
│   └── 001_initial_schema.sql      # PostgreSQL migration
├── api/
│   └── endpoints.py                # API route specifications
├── seed.py                         # Sample data generator
├── README.md                       # Full documentation
└── DELIVERABLES_SUMMARY.md         # This summary
```

---

## Setup (5 minutes)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install fastapi uvicorn prisma celery redis pandas anthropic
```

### 2. Set Environment Variables

Create `backend/.env`:

```bash
DATABASE_URL="postgresql://user:pass@localhost:5432/dream_ai"
REDIS_URL="redis://localhost:6379/0"
ANTHROPIC_API_KEY="sk-ant-your-key"
OPENAI_API_KEY="sk-your-key-here"  # Optional: for ChatGPT/Codex (see OPENAI_SETUP.md)
PERPLEXITY_API_KEY="pplx-your-key"
JWT_SECRET_KEY="your-secret-key-here"
```

### 3. Initialize Database

```bash
# Generate Prisma client
cd backend
prisma generate

# Run migration
psql $DATABASE_URL < migrations/001_initial_schema.sql

# OR if using Prisma migrate:
prisma migrate deploy
```

### 4. Load Sample Data (Optional)

```bash
python seed.py
```

This creates:
- Sample organization "Shieldstone Acquisitions"
- 2 users
- 1 complete deal (Oak Creek Apartments, Austin, TX)
- Full analysis with 18.5% IRR

---

## Run (2 minutes)

### Terminal 1: API Server

```bash
uvicorn main:app --reload --port 8000
```

### Terminal 2: Worker (for async jobs)

```bash
celery -A tasks worker --loglevel=info
```

### Terminal 3: Test

```bash
# Health check
curl http://localhost:8000/health

# API docs (interactive)
open http://localhost:8000/docs
```

---

## Key Files to Understand

### 1. **`schema.prisma`** - Data Model
```prisma
model Deal {
  id             String   @id @default(uuid())
  name           String
  status         DealStatus
  property       Property?
  analyses       Analysis[]
  // ... more fields
}
```

### 2. **`endpoints.py`** - API Routes
```python
@deals_router.post("/", response_model=DealResponse)
async def create_deal(deal: DealCreate):
    # Create new deal
    pass
```

### 3. **`seed.py`** - Sample Data
```python
SAMPLE_PROPERTY = {
    "address": "1234 Oak Creek Drive",
    "city": "Austin",
    "units": 196,
    "asking_price": 34300000
}
```

---

## Test with Sample Data

Once seeded, you can:

```bash
# List deals
curl http://localhost:8000/api/v1/deals

# Get specific deal
curl http://localhost:8000/api/v1/deals/{deal_id}

# Get analysis
curl http://localhost:8000/api/v1/deals/{deal_id}/analysis

# Get pro forma
curl http://localhost:8000/api/v1/deals/{deal_id}/proforma
```

---

## Common Tasks

### Add a New Deal

```bash
curl -X POST http://localhost:8000/api/v1/deals \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sunset Apartments",
    "property_address": "456 Sunset Blvd",
    "property_city": "Phoenix",
    "property_state": "AZ"
  }'
```

### Trigger Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "deal_id": "{deal_id}",
    "analysis_type": "FULL_UW"
  }'
```

### Generate Report

```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "{analysis_id}",
    "report_type": "IC_MEMO",
    "format": "PDF"
  }'
```

---

## Database Quick Reference

### Connect to Database

```bash
psql $DATABASE_URL
```

### Useful Queries

```sql
-- List all deals
SELECT id, name, status FROM deals;

-- Get deal with property
SELECT d.name, p.address, p.units 
FROM deals d 
JOIN properties p ON p.deal_id = d.id;

-- Get analyses with scores
SELECT d.name, a.type, a.recommendation, 
       a.scores->>'overall' as score
FROM analyses a
JOIN deals d ON d.id = a.deal_id;

-- Get market data
SELECT msa_name, market_tier, vacancy_rate, rent_growth_1yr
FROM msa_cache
ORDER BY population DESC;
```

---

## Architecture at a Glance

```
┌──────────────┐
│   Frontend   │
│  (Next.js)   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│      FastAPI Backend         │
│  ┌─────────┐  ┌───────────┐ │
│  │   API   │  │  Celery   │ │
│  │ Routes  │  │  Workers  │ │
│  └─────────┘  └───────────┘ │
└──────────┬───────────────────┘
           │
           ▼
    ┌──────────────┐
    │  PostgreSQL  │
    │  (Deals,     │
    │   Analyses)  │
    └──────────────┘
```

**Flow:**
1. Frontend calls API endpoint
2. API validates, queues job (if long-running)
3. Returns `202 Accepted` with job ID
4. Worker processes job
5. Frontend polls job status
6. Returns result when complete

---

## Cost Breakdown

### Per Deal Analysis

| Operation | LLM Cost | Time |
|-----------|----------|------|
| Document extraction | $0.05 | 2 min |
| Market research | $0.10 | 1 min |
| BOE analysis | $0.15 | 2 min |
| Full UW | $1.00 | 7 min |
| IC Memo | $2.50 | 3 min |
| **Total** | **$3.80** | **15 min** |

### Infrastructure (per month)

- Database: $25-50
- Redis: $10-20  
- Hosting: $20-40
- Storage: $5-15
- **Total: ~$60-125/month**

---

## Next Steps

1. ✅ **You are here** - Backend running locally
2. 🔄 **Integrate Shieldstone** - Add calculation library
3. 🔄 **Connect Frontend** - Wire up API calls
4. 🔄 **Add Auth** - Clerk or Auth0
5. 🔄 **Deploy** - Railway, Render, or Docker
6. 🚀 **Launch MVP** - Start testing with users

---

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
echo $DATABASE_URL
```

### Prisma Client Not Found
```bash
# Regenerate Prisma client
prisma generate
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return "PONG"
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

---

## Resources

- **Full docs:** `backend/README.md`
- **API docs:** http://localhost:8000/docs
- **Prisma studio:** `prisma studio` (database GUI)
- **Sample data:** `backend/seed.py`

---

## Support

**Questions?** Check:
1. `backend/README.md` - Full documentation
2. `backend/DELIVERABLES_SUMMARY.md` - What's included
3. API docs at `/docs` - Interactive testing
4. Sample data in `seed.py` - Complete example

**Ready to build!** 🚀

