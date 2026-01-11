# Server Startup Guide - Troubleshooting localhost:8000

## The Problem

The server won't start because:
1. **Prisma client needs to be generated** - Requires a valid `DATABASE_URL` in `.env`
2. **Module-level imports** - `api.deals` imports Prisma at startup, which requires database connection

## Quick Fix Options

### Option 1: Minimal Setup (Just to see API docs)

1. **Create `.env` file** in `backend/` directory:
```bash
cd backend
copy .env.example .env
```

2. **Edit `.env`** and add a placeholder DATABASE_URL:
```
DATABASE_URL="postgresql://user:password@localhost:5432/dream_ai"
```

3. **Generate Prisma client**:
```bash
python -m prisma generate
```

4. **Start server**:
```bash
python -m uvicorn main:app --reload --port 8000
```

**Note**: Endpoints that use the database will fail, but you can still view the API docs at `http://localhost:8000/docs`

### Option 2: Full Setup (With Real Database)

1. **Set up Supabase** (see `SUPABASE_SETUP.md`):
   - Create project at https://supabase.com
   - Get connection string from Project Settings > Database

2. **Create `.env` file**:
```bash
cd backend
copy .env.example .env
```

3. **Add your DATABASE_URL** to `.env`:
```
DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

4. **Run migrations** (if needed):
```bash
python -m prisma db push
```

5. **Generate Prisma client**:
```bash
python -m prisma generate
```

6. **Start server**:
```bash
python -m uvicorn main:app --reload --port 8000
```

7. **Verify**:
   - Open http://localhost:8000/docs
   - Test http://localhost:8000/health

## What Was Already Done

✅ FastAPI installed  
✅ Uvicorn installed  
✅ Prisma package installed  
✅ Requirements.txt created  

## What's Still Needed

❌ `.env` file with `DATABASE_URL`  
❌ Prisma client generated (needs DATABASE_URL)  
❌ Database connection (Supabase or local PostgreSQL)  

## Alternative: Review Without Running Server

If you just want to review the API structure:
- Check `backend/api/deals.py` for endpoint definitions
- Check `backend/api/endpoints.py` for other endpoints
- Check `TASKS_1.1_1.3_1.5_COMPLETE.md` for what was completed

## Next Steps

1. **For API docs**: Follow Option 1 (minimal setup)
2. **For full testing**: Follow Option 2 (Supabase setup)
3. **For code review**: Just read the Python files directly

