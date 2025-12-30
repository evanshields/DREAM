# Supabase Architecture Recommendation for DREAM AI

**Date:** December 20, 2025  
**Decision:** Use Supabase for Backend Infrastructure

---

## Recommendation: **YES, Use Supabase**

### Why Supabase Makes Sense for DREAM AI

#### 1. **Unified Platform Benefits**
- **Database**: PostgreSQL (same as current plan)
- **Auth**: Built-in authentication (replaces Clerk/Auth0)
- **Storage**: Built-in file storage (replaces separate S3 setup)
- **Real-time**: Built-in subscriptions (perfect for extraction job status updates)
- **Edge Functions**: Can handle some API logic (though we'll keep FastAPI for complex Python)

#### 2. **Cost Efficiency**
- **Single Platform**: One bill instead of multiple services
- **Free Tier**: Generous free tier for development/testing
- **Scaling**: Predictable pricing as you grow
- **No Infrastructure Management**: Supabase handles scaling, backups, etc.

#### 3. **Developer Experience**
- **Familiarity**: You're already using it for other apps
- **Consistency**: Same patterns across your applications
- **Type Safety**: Supabase generates TypeScript types automatically
- **Local Development**: Supabase CLI for local development

#### 4. **Perfect Fit for Phase 1 Features**
- **Document Storage**: Supabase Storage for file uploads
- **Real-time Updates**: Perfect for extraction job status (no polling needed)
- **Row-Level Security**: Built-in multi-tenant isolation
- **Database Functions**: Can handle some business logic

---

## Recommended Architecture: Hybrid Approach

### Use Supabase For:
1. **Database**: PostgreSQL (via Supabase)
2. **Authentication**: Supabase Auth (replaces Clerk/Auth0)
3. **File Storage**: Supabase Storage (replaces S3)
4. **Real-time Subscriptions**: Extraction job status, deal updates
5. **Database Functions**: Simple queries, triggers

### Keep FastAPI For:
1. **LLM Services**: Document extraction, classification (Python-heavy)
2. **Complex Business Logic**: Shieldstone calculations, underwriting
3. **External Integrations**: Email, WhatsApp, Slack bots
4. **Background Jobs**: Celery/Redis for async processing
5. **API Gateway**: Main API endpoints

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - ShadCN Components (via MCP)                          │
│  - Supabase Client (auth, real-time)                    │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│   Supabase   │   │   FastAPI    │
│              │   │              │
│ • PostgreSQL │   │ • LLM APIs  │
│ • Auth       │   │ • Extraction │
│ • Storage    │   │ • Processing │
│ • Real-time  │   │ • Integrations│
└──────────────┘   └──────────────┘
```

---

## Implementation Changes Needed

### 1. Database Schema
- **Current**: Prisma schema → PostgreSQL
- **New**: Prisma schema → Supabase PostgreSQL (same schema, different connection)
- **Change**: Update `DATABASE_URL` to Supabase connection string
- **Benefit**: No schema changes needed, just connection

### 2. Authentication
- **Current Plan**: Clerk or Auth0
- **New**: Supabase Auth
- **Changes**:
  - Remove Clerk/Auth0 setup
  - Use Supabase Auth in frontend
  - Use Supabase JWT tokens for FastAPI auth
- **Benefit**: One less service, built-in user management

### 3. File Storage
- **Current Plan**: S3-compatible storage (AWS S3, DigitalOcean Spaces)
- **New**: Supabase Storage
- **Changes**:
  - Replace S3 client with Supabase Storage client
  - Update storage service implementation
  - Use Supabase Storage buckets
- **Benefit**: Integrated with auth, easier permissions

### 4. Real-time Updates
- **Current Plan**: Polling or WebSockets (manual setup)
- **New**: Supabase Real-time subscriptions
- **Changes**:
  - Use Supabase subscriptions for extraction job status
  - Real-time deal updates
  - No polling needed
- **Benefit**: Better UX, less server load

### 5. API Structure
- **Keep**: FastAPI for LLM services and complex logic
- **Add**: Supabase REST API for simple CRUD
- **Hybrid**: 
  - Frontend → Supabase (direct) for simple queries
  - Frontend → FastAPI for extraction, LLM, complex operations

---

## Migration Path

### Phase 1: Setup Supabase
1. Create Supabase project
2. Run Prisma migrations to Supabase
3. Set up Supabase Auth
4. Configure Supabase Storage buckets

### Phase 2: Update Backend
1. Update database connection to Supabase
2. Replace auth middleware with Supabase JWT verification
3. Replace storage service with Supabase Storage
4. Add real-time subscriptions

### Phase 3: Update Frontend
1. Add Supabase client
2. Replace auth library with Supabase Auth
3. Add real-time subscriptions for job status
4. Update file upload to use Supabase Storage

---

## Code Changes Summary

### Backend Changes
```python
# OLD: S3 Storage
from boto3 import client
s3 = client('s3')

# NEW: Supabase Storage
from supabase import create_client
supabase = create_client(url, key)
supabase.storage.from_('documents').upload(...)
```

```python
# OLD: Custom Auth
from fastapi.security import HTTPBearer
security = HTTPBearer()

# NEW: Supabase Auth
from supabase import create_client
# Verify JWT from Supabase
```

### Frontend Changes
```typescript
// OLD: Clerk Auth
import { useAuth } from '@clerk/nextjs'

// NEW: Supabase Auth
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(url, key)
```

```typescript
// NEW: Real-time subscriptions
supabase
  .channel('extraction-jobs')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'extraction_jobs',
    filter: `id=eq.${jobId}`
  }, (payload) => {
    // Update UI with job status
  })
  .subscribe()
```

---

## Benefits Summary

| Feature | Without Supabase | With Supabase |
|---------|------------------|---------------|
| **Database** | Separate PostgreSQL | ✅ Included |
| **Auth** | Clerk/Auth0 ($25-50/mo) | ✅ Included |
| **Storage** | S3 ($5-20/mo) | ✅ Included |
| **Real-time** | Manual WebSocket setup | ✅ Included |
| **Setup Time** | 2-3 days | ✅ 1 day |
| **Monthly Cost** | $30-70+ | ✅ $0-25 (free tier) |
| **Complexity** | Multiple services | ✅ Single platform |

---

## Recommendations

### ✅ Do Use Supabase For:
- Database (PostgreSQL)
- Authentication
- File storage
- Real-time subscriptions
- Simple CRUD operations

### ✅ Keep FastAPI For:
- LLM integration (Claude, Gemini)
- Document extraction services
- Complex business logic (Shieldstone)
- External integrations (Email, WhatsApp, Slack)
- Background job processing (Celery)

### ⚠️ Considerations:
- **Edge Functions**: Supabase Edge Functions are Deno/TypeScript, not Python. Keep complex Python logic in FastAPI.
- **Rate Limits**: Supabase has rate limits. For high-volume LLM operations, use FastAPI.
- **Cost**: Monitor Supabase usage as you scale. May need Pro plan ($25/mo) for production.

---

## Next Steps

1. **Create Supabase Project**: Set up new project for DREAM AI
2. **Update Implementation Plan**: Modify tasks to use Supabase
3. **Update Database Connection**: Point Prisma to Supabase
4. **Set Up Auth**: Configure Supabase Auth
5. **Set Up Storage**: Create storage buckets
6. **Update Tasks**: Modify relevant implementation tasks

---

*Recommendation Version: 1.0*  
*Created: December 20, 2025*

