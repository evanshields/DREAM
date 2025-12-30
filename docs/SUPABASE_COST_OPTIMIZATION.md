# Supabase Cost Optimization Guide for DREAM AI

**Date:** December 20, 2025  
**Purpose:** Optimize database schema and storage for maximum cost efficiency on Supabase

---

## Supabase Pricing Context

### Free Tier Limits
- **Database**: 500MB
- **File Storage**: 1GB
- **Bandwidth**: 2GB/month
- **Real-time**: Unlimited connections

### Pro Tier ($25/month)
- **Database**: 8GB
- **File Storage**: 100GB
- **Bandwidth**: 250GB/month
- **Real-time**: Unlimited

### Cost Drivers
1. **Database Size**: Primary cost factor (stay under 8GB on Pro)
2. **File Storage**: Secondary cost (documents can be large)
3. **Bandwidth**: Usually not an issue for B2B app
4. **API Calls**: Unlimited on both tiers

---

## Schema Optimization Strategies

### 1. **Optimize Data Types** (Save ~20-30% storage)

#### Current Issues:
```sql
-- TOO LARGE
notes TEXT,                    -- Can be huge, rarely queried
extraction_data JSONB,         -- Can be very large
tags TEXT[],                   -- Array overhead
```

#### Optimized:
```sql
-- OPTIMIZED
notes VARCHAR(5000),           -- Limit size, most notes < 5K chars
extraction_data JSONB,         -- Keep but compress/archive old
tags VARCHAR(50)[],            -- Limit tag length
```

#### Specific Optimizations:

**Deals Table:**
```sql
-- BEFORE (wasteful)
property_name VARCHAR(200),   -- Usually < 50 chars
address_street VARCHAR(200),  -- Usually < 100 chars
notes TEXT,                    -- Can be huge

-- AFTER (optimized)
property_name VARCHAR(100),   -- Sufficient for most
address_street VARCHAR(150),   -- Sufficient
notes VARCHAR(5000),           -- Limit to 5K, archive longer
```

**Documents Table:**
```sql
-- BEFORE
extraction_data JSONB,        -- Can be 100KB+ per doc
processing_error TEXT,         -- Rarely used, can be large

-- AFTER
extraction_data JSONB,         -- Keep but add compression
processing_error VARCHAR(2000), -- Limit error message size
```

**Extraction Jobs Table:**
```sql
-- BEFORE
extracted_data JSONB,         -- Duplicates document extraction_data
error_message TEXT,            -- Can be large

-- AFTER
extracted_data JSONB,         -- Keep but reference document instead
error_message VARCHAR(1000),  -- Limit size
```

### 2. **Archive Old Data** (Save 40-60% long-term)

#### Strategy: Move old data to archive tables

```sql
-- Archive table (same structure, but compressed)
CREATE TABLE deals_archive (
    LIKE deals INCLUDING ALL
);

-- Archive extraction data separately (largest bloat)
CREATE TABLE extraction_data_archive (
    id UUID PRIMARY KEY,
    document_id UUID,
    extraction_data JSONB,
    archived_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Archive Policy:
- **Active Deals**: Keep in main table (last 6 months activity)
- **Closed/Passed Deals**: Archive after 90 days
- **Extraction Data**: Archive after deal is closed + 30 days
- **Old Corrections**: Archive after 1 year

#### Implementation:
```sql
-- Function to archive old deals
CREATE OR REPLACE FUNCTION archive_old_deals()
RETURNS void AS $$
BEGIN
    -- Move closed deals older than 90 days
    INSERT INTO deals_archive
    SELECT * FROM deals
    WHERE stage IN ('CLOSED', 'PASSED', 'DEAD')
    AND updated_at < NOW() - INTERVAL '90 days';
    
    DELETE FROM deals
    WHERE stage IN ('CLOSED', 'PASSED', 'DEAD')
    AND updated_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Run monthly via cron
```

### 3. **Optimize JSONB Storage** (Save 30-50% on extraction_data)

#### Problem:
- `extraction_data` JSONB can be 50-200KB per document
- Stored in multiple places (documents, extraction_jobs)
- Duplicated across tables

#### Solution: Reference Pattern

```sql
-- Store extraction data once
CREATE TABLE extraction_data_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID UNIQUE REFERENCES documents(id),
    extraction_data JSONB NOT NULL,
    compressed_data BYTEA,  -- Compressed version
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reference from documents table
ALTER TABLE documents 
ADD COLUMN extraction_data_id UUID REFERENCES extraction_data_cache(id);

-- Remove extraction_data from documents table (store reference only)
-- Remove extracted_data from extraction_jobs (reference document instead)
```

#### Compression:
```sql
-- Compress large JSONB before storing
CREATE OR REPLACE FUNCTION compress_extraction_data(data JSONB)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data::text, 'encryption_key');
END;
$$ LANGUAGE plpgsql;
```

### 4. **Smart Indexing** (Balance performance vs storage)

#### Current Indexes (Good):
```sql
-- Essential indexes (keep)
CREATE INDEX idx_deals_org ON deals(organization_id);
CREATE INDEX idx_deals_stage ON deals(stage);
CREATE INDEX idx_deals_created ON deals(created_at DESC);
CREATE INDEX idx_documents_deal ON documents(deal_id);
CREATE INDEX idx_extraction_jobs_deal ON extraction_jobs(deal_id);
```

#### Add Composite Indexes (Better performance, minimal storage):
```sql
-- Composite indexes for common queries
CREATE INDEX idx_deals_org_stage ON deals(organization_id, stage);
CREATE INDEX idx_deals_org_created ON deals(organization_id, created_at DESC);
CREATE INDEX idx_documents_deal_type ON documents(deal_id, document_type);
```

#### Remove Unnecessary Indexes:
```sql
-- REMOVE if not frequently queried
-- CREATE INDEX idx_deals_address ON deals(address_city, address_state);
-- (Only keep if you frequently search by location)
```

### 5. **Normalize Repeated Data** (Save 10-20%)

#### Current: Tags stored as array
```sql
tags TEXT[]  -- Stored per deal, duplicates across deals
```

#### Optimized: Normalized tags
```sql
-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7),  -- Hex color
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, name)
);

-- Deal tags junction table
CREATE TABLE deal_tags (
    deal_id UUID REFERENCES deals(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (deal_id, tag_id)
);

-- Index for fast lookups
CREATE INDEX idx_deal_tags_deal ON deal_tags(deal_id);
CREATE INDEX idx_deal_tags_tag ON deal_tags(tag_id);
```

**Savings**: If 100 deals share 10 tags, saves ~90 tag arrays worth of storage.

### 6. **File Storage Optimization** (Critical for cost)

#### Strategy: Compress before upload
```python
# Compress PDFs before storing
import gzip
import base64

def compress_document(file_content: bytes) -> bytes:
    """Compress document before storing in Supabase"""
    return gzip.compress(file_content, compresslevel=9)
```

#### Storage Tiers:
- **Active Documents**: Store in Supabase Storage (fast access)
- **Archived Documents**: Move to cheaper storage (S3 Glacier) or delete after retention period

#### Retention Policy:
```sql
-- Delete old documents after retention period
CREATE OR REPLACE FUNCTION cleanup_old_documents()
RETURNS void AS $$
BEGIN
    -- Delete documents for closed deals older than 1 year
    DELETE FROM documents
    WHERE deal_id IN (
        SELECT id FROM deals
        WHERE stage IN ('CLOSED', 'PASSED', 'DEAD')
        AND updated_at < NOW() - INTERVAL '1 year'
    );
END;
$$ LANGUAGE plpgsql;
```

### 7. **Partition Large Tables** (Future-proofing)

#### For High-Volume Scenarios:
```sql
-- Partition extraction_jobs by date (if > 100K rows)
CREATE TABLE extraction_jobs (
    -- ... columns ...
) PARTITION BY RANGE (created_at);

-- Monthly partitions
CREATE TABLE extraction_jobs_2025_01 PARTITION OF extraction_jobs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

**Benefit**: Can drop old partitions instead of deleting rows (faster, less storage).

---

## Recommended Optimized Schema

### Key Changes from PRD Schema:

1. **Smaller VARCHAR sizes** (where appropriate)
2. **Archive tables** for old data
3. **Extraction data cache** (single source of truth)
4. **Normalized tags** (junction table)
5. **Limited TEXT fields** (use VARCHAR with reasonable limits)
6. **Compression** for large JSONB fields

### Storage Estimates (Optimized):

| Table | Rows | Size (Optimized) | Notes |
|-------|------|------------------|-------|
| deals | 10,000 | ~50MB | With archived old deals |
| documents | 50,000 | ~100MB | Metadata only, files in storage |
| extraction_jobs | 50,000 | ~75MB | Without duplicated JSONB |
| extraction_data_cache | 50,000 | ~150MB | Compressed JSONB |
| extraction_corrections | 100,000 | ~25MB | Small records |
| **Total** | | **~400MB** | Well under 8GB limit |

**With 10,000 active deals**: ~400MB database size
**With 100,000 active deals**: ~4GB database size (still under 8GB)

---

## Implementation Priority

### Phase 1 (Immediate):
1. ✅ Use appropriate VARCHAR sizes (not TEXT)
2. ✅ Limit JSONB duplication
3. ✅ Add composite indexes
4. ✅ Normalize tags

### Phase 2 (After 1,000 deals):
1. Implement archive tables
2. Add extraction_data_cache
3. Implement compression
4. Set up retention policies

### Phase 3 (After 10,000 deals):
1. Implement partitioning
2. Move archived files to cheaper storage
3. Optimize queries further

---

## Cost Monitoring

### Track These Metrics:
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- JSONB field sizes
SELECT 
    AVG(pg_column_size(extraction_data)) AS avg_size,
    MAX(pg_column_size(extraction_data)) AS max_size
FROM documents
WHERE extraction_data IS NOT NULL;
```

### Set Up Alerts:
- Alert when database > 6GB (80% of 8GB limit)
- Alert when storage > 80GB (80% of 100GB limit)
- Monitor JSONB field growth

---

## Quick Wins (Implement First)

1. **Change TEXT to VARCHAR(5000)** for notes fields → Save ~20%
2. **Remove extraction_data duplication** → Save ~30%
3. **Normalize tags** → Save ~10%
4. **Add archive policy** → Save 40-60% long-term
5. **Compress documents** → Save 50-70% on storage

**Total Potential Savings**: 60-80% reduction in database size

---

## Recommended Schema Updates

I'll create an optimized schema file that implements these changes. Should I proceed with creating the optimized Prisma schema?

---

*Cost Optimization Guide Version: 1.0*  
*Created: December 20, 2025*

