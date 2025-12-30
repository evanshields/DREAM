# DREAM AI - Backend Architecture & Deployment Guide

**Version:** 1.0  
**Date:** December 2025  
**Product:** DREAM AI - CRE Underwriting Platform

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Data Model Summary](#data-model-summary)
4. [API Design Principles](#api-design-principles)
5. [Deployment Guide](#deployment-guide)
6. [Environment Setup](#environment-setup)
7. [Database Management](#database-management)
8. [Performance Optimization](#performance-optimization)
9. [Security Considerations](#security-considerations)
10. [Cost Optimization](#cost-optimization)

---

## 1. Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DREAM AI BACKEND                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   FastAPI    │  │   Prisma     │  │   Celery     │          │
│  │   REST API   │  │     ORM      │  │  Task Queue  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                          │  │
│  │  - Organizations, Users, Deals, Properties                │  │
│  │  - Analyses, Pro Formas, Market Research                  │  │
│  │  - Documents, Reports, Tasks                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              External Integrations                         │  │
│  │  - LLM APIs: Claude, Perplexity                           │  │
│  │  - Market Data: Census, BLS, Walk Score                   │  │
│  │  - Storage: S3-compatible (documents, reports)            │  │
│  │  - Cache: Redis (market data, sessions)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Shieldstone Calculation Engine (Python)           │  │
│  │  - Return hurdle calculations                             │  │
│  │  - Pro forma modeling (DCF)                               │  │
│  │  - Deal screening logic                                   │  │
│  │  - All financial calculations (deterministic, no LLM)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Python-First Calculations**: ALL financial calculations in Python (not LLM) for speed, reliability, and cost
2. **Async by Default**: Long-running operations (extraction, analysis, reports) use background jobs
3. **LLM Cost Tracking**: Every LLM call tracked in `llm_cost_cents` field
4. **Aggressive Caching**: Market data cached to minimize API calls
5. **Auditability**: All calculations stored with assumptions for reproducibility
6. **Separation of Concerns**: LLM generates assumptions/narratives; Python calculates; Database stores

---

## 2. Technology Stack

### Core Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Framework** | FastAPI | REST API endpoints |
| **Database** | PostgreSQL 14+ | Primary data store |
| **ORM** | Prisma | Type-safe database access |
| **Task Queue** | Celery + Redis | Async job processing |
| **Cache** | Redis | Market data, sessions |
| **File Storage** | S3-compatible | Documents, reports |

### Python Dependencies

```txt
# Core
fastapi==0.104.0
uvicorn[standard]==0.24.0
prisma==0.11.0
celery[redis]==5.3.4
redis==5.0.1

# Data & Calculation
pandas==2.1.3
numpy==1.26.2
scipy==1.11.4
pydantic==2.5.0

# LLM & External APIs
anthropic==0.7.0
openai==1.3.0
httpx==0.25.0

# Market Data
census==0.8.19
requests==2.31.0

# Storage
boto3==1.29.0
python-multipart==0.0.6

# Auth & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Monitoring
sentry-sdk==1.38.0
prometheus-client==0.19.0
```

### Infrastructure

| Component | Recommended Service | Alternative |
|-----------|-------------------|-------------|
| **Backend Hosting** | Railway / Render | AWS ECS / GCP Cloud Run |
| **Database** | Supabase / Neon | AWS RDS / GCP Cloud SQL |
| **Cache/Queue** | Upstash Redis | AWS ElastiCache / Redis Cloud |
| **Storage** | AWS S3 | Cloudflare R2 / GCP Storage |
| **Monitoring** | Sentry + Datadog | Grafana + Prometheus |

---

## 3. Data Model Summary

### Core Entities

```
Organizations (Multi-tenant)
├── Users (ADMIN, ANALYST, VIEWER roles)
├── InvestmentCriteria (configurable per org)
└── Deals
    ├── Property (address, units, financials)
    │   ├── UnitMix (by unit type)
    │   └── RentRoll (unit-level detail)
    ├── Documents (OMs, T-12s, rent rolls)
    ├── Analyses (BOE, Full UW, IC Memo, Full Memo)
    │   ├── ProForma (DCF model)
    │   │   ├── OperatingStatementLines (T-12, Pro Forma)
    │   │   └── DebtFacilities (senior, mezz, preferred)
    │   ├── Scenarios (Base, Upside, Downside)
    │   └── Reports (PDF, Excel, Slides)
    ├── MarketResearch (MSA, submarket, location data)
    ├── Notes (collaboration)
    └── Tasks (workflow management)
```

### Key Relationships

- **Organization → Deals**: One-to-many (multi-tenant isolation)
- **Deal → Property**: One-to-one
- **Deal → Analyses**: One-to-many (versioned)
- **Analysis → ProForma**: One-to-one
- **ProForma → OperatingStatementLines**: One-to-many (T-12, PF by year)
- **Deal → MarketResearch**: One-to-one (cached)

### Data Versioning

- **Analyses**: Version number increments on regeneration
- **Assumptions**: Full snapshot stored with each analysis
- **Results**: Calculated results stored for auditability
- **Historical**: All versions retained (not overwritten)

---

## 4. API Design Principles

### RESTful Conventions

```
Resource-based URLs:
  GET    /api/v1/deals              List deals
  POST   /api/v1/deals              Create deal
  GET    /api/v1/deals/{id}         Get deal
  PATCH  /api/v1/deals/{id}         Update deal
  DELETE /api/v1/deals/{id}         Delete deal

Nested resources:
  POST   /api/v1/deals/{id}/documents       Upload document
  GET    /api/v1/deals/{id}/analysis        Get latest analysis
  POST   /api/v1/analyses/{id}/regenerate   Regenerate analysis
```

### Async Operation Pattern

Long-running operations return `202 Accepted` immediately:

```json
// Request
POST /api/v1/deals/{id}/analyze
{
  "analysis_type": "FULL_UW"
}

// Response (202 Accepted)
{
  "job_id": "job_abc123",
  "status": "PROCESSING",
  "estimated_time_seconds": 420
}

// Poll status
GET /api/v1/jobs/job_abc123

// Response when complete
{
  "job_id": "job_abc123",
  "status": "COMPLETED",
  "result": {
    "analysis_id": "analysis_xyz789"
  }
}
```

### Response Format Standards

```json
// Success (200, 201)
{
  "id": "uuid",
  "data": {...},
  "metadata": {...}
}

// Error (4xx, 5xx)
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid deal ID",
    "details": {...}
  }
}

// List response
{
  "data": [...],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

---

## 5. Deployment Guide

### Prerequisites

1. PostgreSQL 14+ database
2. Redis instance
3. S3-compatible storage
4. Python 3.11+
5. Environment variables configured

### Step-by-Step Deployment

#### 1. Clone and Setup

```bash
git clone https://github.com/your-org/dream-ai-backend.git
cd dream-ai-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

#### 2. Environment Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL="postgresql://user:password@host:5432/dream_ai"

# Redis
REDIS_URL="redis://localhost:6379/0"

# S3 Storage
S3_BUCKET_NAME="dream-ai-documents"
S3_REGION="us-east-1"
AWS_ACCESS_KEY_ID="your_key"
AWS_SECRET_ACCESS_KEY="your_secret"

# LLM APIs
ANTHROPIC_API_KEY="sk-ant-..."
OPENAI_API_KEY="sk-..."  # For ChatGPT/Codex (see OPENAI_SETUP.md)
PERPLEXITY_API_KEY="pplx-..."

# External APIs
CENSUS_API_KEY="your_census_key"
WALK_SCORE_API_KEY="your_walkscore_key"

# Auth
JWT_SECRET_KEY="your_jwt_secret"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=24

# Environment
ENVIRONMENT="production"
LOG_LEVEL="INFO"
SENTRY_DSN="https://..."
```

#### 3. Database Migration

```bash
# Generate Prisma client
prisma generate

# Run migrations
prisma migrate deploy

# Seed database (optional)
python backend/seed.py
```

#### 4. Start Services

```bash
# Terminal 1: API Server
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
celery -A backend.tasks worker --loglevel=info

# Terminal 3: Celery Beat (scheduled tasks)
celery -A backend.tasks beat --loglevel=info
```

#### 5. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### Production Deployment (Railway Example)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Add services
railway add --database postgresql
railway add --database redis

# Set environment variables
railway variables set DATABASE_URL="..."
railway variables set REDIS_URL="..."
# ... (set all env vars)

# Deploy
railway up
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY prisma/ ./prisma/

RUN prisma generate

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    
  worker:
    build: .
    command: celery -A backend.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=dream_ai
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

```bash
# Run with Docker Compose
docker-compose up -d
```

---

## 6. Environment Setup

### Development Environment

```bash
# Install dev dependencies
pip install -r backend/requirements-dev.txt

# Run with auto-reload
uvicorn backend.main:app --reload --port 8000

# Run tests
pytest backend/tests/

# Code formatting
black backend/
isort backend/

# Linting
flake8 backend/
mypy backend/
```

### Environment Variables by Stage

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `ENVIRONMENT` | `development` | `staging` | `production` |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` |
| `DATABASE_URL` | Local PG | Staging DB | Production DB |
| `REDIS_URL` | Local Redis | Staging Redis | Production Redis |
| `SENTRY_DSN` | (empty) | Staging DSN | Production DSN |

---

## 7. Database Management

### Migrations

```bash
# Create new migration
prisma migrate dev --name add_investor_table

# Apply migrations (production)
prisma migrate deploy

# Reset database (development only!)
prisma migrate reset
```

### Backup & Restore

```bash
# Backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20251220.sql

# Automated backups (cron)
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/dream_ai_$(date +\%Y\%m\%d).sql.gz
```

### Performance Monitoring

```sql
-- Check slow queries
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 8. Performance Optimization

### API Response Times

| Endpoint | Target | Optimization Strategy |
|----------|--------|----------------------|
| GET /deals | <200ms | Index on org_id, status; pagination |
| POST /deals | <100ms | Simple insert, async processing |
| GET /proforma | <100ms | Index on analysis_id |
| PATCH /proforma | <100ms | Python recalc only (no LLM) |
| POST /analyze | <500ms | Queue job immediately, return 202 |

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_deals_org_status ON deals(organization_id, status);
CREATE INDEX CONCURRENTLY idx_analyses_deal_type ON analyses(deal_id, type);
CREATE INDEX CONCURRENTLY idx_market_research_expires ON msa_cache(expires_at);

-- Analyze tables regularly
ANALYZE deals;
ANALYZE analyses;
ANALYZE pro_formas;
```

### Caching Strategy

```python
# Market data caching (7 days)
cache_key = f"msa:{msa_code}"
cached_data = redis.get(cache_key)
if cached_data:
    return json.loads(cached_data)

# Fetch and cache
fresh_data = fetch_msa_data(msa_code)
redis.setex(cache_key, 7 * 24 * 3600, json.dumps(fresh_data))
return fresh_data
```

### Async Processing Best Practices

```python
# Celery task configuration
@celery.task(
    name="analyze_deal",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def analyze_deal(self, deal_id: str, analysis_type: str):
    try:
        # Long-running analysis
        result = perform_analysis(deal_id, analysis_type)
        return result
    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc)
```

---

## 9. Security Considerations

### Authentication & Authorization

```python
# JWT token verification
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401)
        return await get_user(user_id)
    except JWTError:
        raise HTTPException(status_code=401)

# Multi-tenant isolation
async def get_current_org(user: User = Depends(get_current_user)):
    return await get_organization(user.organization_id)

# Permission checking
def require_role(required_role: UserRole):
    def decorator(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403)
        return user
    return decorator
```

### Data Encryption

```python
# Encrypt sensitive fields before storage
from cryptography.fernet import Fernet

def encrypt_credentials(credentials: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.encrypt(credentials.encode()).decode()

def decrypt_credentials(encrypted: str) -> str:
    f = Fernet(ENCRYPTION_KEY)
    return f.decrypt(encrypted.encode()).decode()
```

### SQL Injection Prevention

✅ **GOOD**: Use Prisma ORM (parameterized queries)

```python
# Prisma automatically parameterizes
await prisma.deal.find_many(
    where={"organization_id": org_id, "status": status}
)
```

❌ **BAD**: Raw SQL with string interpolation

```python
# NEVER DO THIS
query = f"SELECT * FROM deals WHERE organization_id = '{org_id}'"
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/deals")
@limiter.limit("10/minute")
async def create_deal(request: Request, ...):
    # Limited to 10 requests per minute per IP
    pass
```

---

## 10. Cost Optimization

### LLM Cost Management

**Target Costs per Deal:**

| Operation | Target | Current Model | Optimization |
|-----------|--------|---------------|-------------|
| Document extraction | <$0.10 | Haiku | Switch to Gemini Flash for routine docs |
| Deal screening | <$0.05 | Haiku | Open-source for simple screens |
| Market research | <$0.15 | Perplexity + APIs | Aggressive caching (7 days) |
| BOE analysis | <$0.20 | Haiku | Fine-tuned open-source |
| Full UW | <$1.50 | Haiku + Sonnet | Cascade: open → Haiku → Sonnet |
| IC/Full Memo | <$4.00 | Sonnet + Opus | Sonnet only, Opus for polish |

**Cost Tracking:**

```python
# Track LLM costs in database
llm_cost_cents = calculate_cost(
    input_tokens=request_tokens,
    output_tokens=response_tokens,
    model="claude-3-haiku-20240307"
)

await prisma.analysis.update(
    where={"id": analysis_id},
    data={"llm_cost_cents": llm_cost_cents}
)
```

### Infrastructure Cost Optimization

| Component | Free Tier | Paid Tier | Monthly Cost (1K deals) |
|-----------|-----------|-----------|------------------------|
| **Database** | Supabase | Neon Pro | $25-50 |
| **Redis** | Upstash | Redis Cloud | $10-20 |
| **API Hosting** | Railway | Railway Pro | $20-40 |
| **Storage** | Cloudflare R2 | AWS S3 | $5-15 |
| **LLM APIs** | N/A | Anthropic | $1,000-2,000 |
| **Monitoring** | Sentry Free | Sentry Team | $29 |
| **Total** | | | **$1,089-2,154** |

**Cost per Deal:** $1.09 - $2.15

**Target Margin:** 70%+ (at $99/month subscription = 50 deals)

---

## Additional Resources

### API Documentation

- Interactive API docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`

### Database Schema

- Prisma schema: `backend/schema.prisma`
- Migrations: `backend/migrations/`
- ERD diagram: Generate with `prisma studio`

### Testing

```bash
# Run all tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/test_analysis.py

# Run with coverage
pytest --cov=backend backend/tests/

# Generate coverage report
pytest --cov=backend --cov-report=html backend/tests/
```

### Monitoring & Logging

```python
# Structured logging
import logging
import structlog

logger = structlog.get_logger()

logger.info(
    "deal_created",
    deal_id=deal.id,
    organization_id=org.id,
    user_id=user.id
)

# Sentry error tracking
import sentry_sdk

sentry_sdk.capture_exception(exception)
```

---

## Support & Maintenance

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "version": "1.0.0"
    }
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection timeout | Check `DATABASE_URL`, increase connection pool |
| Celery tasks not processing | Verify Redis connection, check worker logs |
| High LLM costs | Review usage logs, implement cascading |
| Slow API responses | Check database indexes, enable query caching |

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Maintained By:** DREAM AI Engineering Team

