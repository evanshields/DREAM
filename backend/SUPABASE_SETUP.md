# Supabase Setup Guide - Step by Step

**Follow these steps in order to set up Supabase for DREAM AI Phase 1**

---

## Step 1: Create Supabase Project (5 minutes)

1. **Go to Supabase**
   - Visit: https://supabase.com
   - Sign in or create account

2. **Create New Project**
   - Click "New Project"
   - **Project Name**: `dream-ai` (or `dream-production` for production)
   - **Database Password**: Generate a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., `US East (N. Virginia)`)
   - **Pricing Plan**: Free tier is fine to start
   - Click "Create new project"

3. **Wait for Project Setup** (2-3 minutes)
   - Supabase will provision your database
   - You'll see "Setting up your project" screen

---

## Step 2: Get Your Connection Details (2 minutes)

Once your project is ready:

1. **Go to Project Settings**
   - Look for the **gear icon (⚙️)** at the **bottom of the left sidebar** (under "PROJECT SETTINGS" section)
   - Click the gear icon
   - This opens the "Project Settings" page with tabs at the top

2. **Get Database Connection String**
   - In the Project Settings page, click the **"Database" tab** at the top (not "Database Settings" in the left menu)
   - Scroll down to find the **"Connection string"** section
   - You'll see different connection methods (URI, JDBC, etc.)
   - Click the **"URI" tab** within the Connection string section
   - Copy the connection string shown
   - **Format**: `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`
   - **Replace `[PASSWORD]`** with the password you saved in Step 1
   - **Note**: If you see a placeholder like `[YOUR-PASSWORD]` in the connection string, replace it with your actual database password

3. **Get API Keys**
   - Still in Project Settings
   - Click "API" in the left menu
   - Copy these values:
     - **Project URL**: `https://[PROJECT_REF].supabase.co`
     - **anon/public key**: (starts with `eyJ...`)
     - **service_role key**: (starts with `eyJ...`) - **KEEP THIS SECRET!**

---

## Step 3: Create Environment File (2 minutes)

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create `.env` file**
   ```bash
   # Windows PowerShell
   New-Item -Path .env -ItemType File

   # Or create manually in your editor
   ```

3. **Add your Supabase credentials**
   ```env
   # Database Connection (from Step 2)
   DATABASE_URL="postgresql://postgres.[PROJECT_REF]:[YOUR_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

   # Supabase API (from Step 2)
   SUPABASE_URL="https://[PROJECT_REF].supabase.co"
   SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

   # LLM API Keys (add these later)
   ANTHROPIC_API_KEY=""
   GOOGLE_API_KEY=""

   # Optional: App Environment
   NODE_ENV="development"
   ```

4. **Replace placeholders**:
   - `[PROJECT_REF]` → Your project reference ID
   - `[YOUR_PASSWORD]` → The password you saved in Step 1
   - Keep the `eyJ...` keys exactly as copied

5. **Important**: Add `.env` to `.gitignore` if not already there!

---

## Step 4: Install Prisma (if not already installed) (2 minutes)

```bash
# Check if Prisma is installed
npx prisma --version

# If not installed, install it
npm install -D prisma @prisma/client
```

---

## Step 5: Deploy Schema to Supabase (5 minutes)

1. **Make sure you're using the optimized schema**
   ```bash
   # Copy optimized schema to main schema file
   # (Or use schema_phase1_optimized.prisma directly)
   cp schema_phase1_optimized.prisma schema.prisma
   ```

2. **Generate Prisma Client**
   ```bash
   npx prisma generate
   ```

3. **Push schema to Supabase**
   ```bash
   npx prisma db push
   ```

   This will:
   - Create all tables
   - Create all enums
   - Create all indexes
   - Set up relationships

4. **Verify in Supabase Dashboard**
   - Go to "Table Editor" in Supabase
   - You should see all tables: `organizations`, `users`, `deals`, `documents`, etc.

---

## Step 6: Set Up Storage Buckets (3 minutes)

1. **Go to Storage**
   - Click "Storage" in left sidebar
   - Click "New bucket"

2. **Create `documents` bucket**
   - **Name**: `documents`
   - **Public bucket**: ❌ Unchecked (private)
   - Click "Create bucket"

3. **Create `archived-documents` bucket** (optional, for future)
   - **Name**: `archived-documents`
   - **Public bucket**: ❌ Unchecked (private)
   - Click "Create bucket"

---

## Step 7: Set Up Row Level Security (RLS) (5 minutes)

1. **Go to SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New query"

2. **Run RLS Setup Script**
   ```sql
   -- Enable RLS on all tables
   ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
   ALTER TABLE users ENABLE ROW LEVEL SECURITY;
   ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
   ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
   ALTER TABLE extraction_jobs ENABLE ROW LEVEL SECURITY;
   ALTER TABLE extraction_corrections ENABLE ROW LEVEL SECURITY;
   ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
   ALTER TABLE deal_tags ENABLE ROW LEVEL SECURITY;
   ALTER TABLE extraction_data_cache ENABLE ROW LEVEL SECURITY;

   -- Policy: Users can only see their own organization's data
   CREATE POLICY "Users can view their organization"
   ON organizations FOR SELECT
   USING (id IN (
     SELECT organization_id FROM users WHERE id = auth.uid()
   ));

   -- Policy: Users can only see users in their organization
   CREATE POLICY "Users can view organization users"
   ON users FOR SELECT
   USING (organization_id IN (
     SELECT organization_id FROM users WHERE id = auth.uid()
   ));

   -- Policy: Users can only see deals from their organization
   CREATE POLICY "Users can view organization deals"
   ON deals FOR SELECT
   USING (organization_id IN (
     SELECT organization_id FROM users WHERE id = auth.uid()
   ));

   -- Policy: Users can only see documents from their organization's deals
   CREATE POLICY "Users can view organization documents"
   ON documents FOR SELECT
   USING (deal_id IN (
     SELECT id FROM deals 
     WHERE organization_id IN (
       SELECT organization_id FROM users WHERE id = auth.uid()
     )
   ));

   -- Similar policies for other tables...
   -- (We'll add INSERT/UPDATE/DELETE policies as needed)
   ```

3. **Click "Run"** to execute the SQL

---

## Step 8: Verify Setup (2 minutes)

1. **Test Database Connection**
   ```bash
   npx prisma studio
   ```
   - This opens Prisma Studio in your browser
   - You should see all your tables
   - Try viewing the `organizations` table

2. **Test in Supabase Dashboard**
   - Go to "Table Editor"
   - Click on `deals` table
   - Should see empty table (no errors)

3. **Check Storage**
   - Go to "Storage"
   - Should see `documents` bucket

---

## ✅ Setup Complete!

You now have:
- ✅ Supabase project created
- ✅ Database schema deployed
- ✅ Storage buckets configured
- ✅ Row Level Security enabled
- ✅ Environment variables set

---

## Next Steps

1. **Update Implementation Plan**
   - Task 1.1 is now mostly complete!
   - You can mark it as done or update it to reflect Supabase setup

2. **Start Task 1.2**
   - Begin with UX prototype for manual entry form
   - Or start with backend API endpoints

3. **Test Your Setup**
   - Try creating a test organization via Prisma Studio
   - Verify RLS is working

---

## Troubleshooting

### Issue: "Can't find Connection string"
- **Solution**: Make sure you're in **Project Settings** (gear icon at bottom of sidebar), NOT "Database Settings" (under Configuration)
- The connection string is in: **Project Settings → Database tab** (at the top of the page)
- If you see "Connection pooling configuration" and "SSL Configuration", you're in the wrong place - go back and click the gear icon

### Issue: "Connection refused"
- **Solution**: Check your DATABASE_URL format
- Make sure password is URL-encoded if it has special characters

### Issue: "Schema push failed"
- **Solution**: Check Supabase dashboard for error messages
- Try running `npx prisma db push --force-reset` (⚠️ deletes all data!)

### Issue: "RLS policies not working"
- **Solution**: Make sure you're authenticated in Supabase
- Check that `auth.uid()` is returning a user ID

### Issue: "Storage bucket not found"
- **Solution**: Make sure bucket name matches exactly
- Check bucket permissions in Storage settings

---

## Need Help?

If you run into issues:
1. Check Supabase logs (Project Settings → Logs)
2. Check Prisma error messages
3. Verify your `.env` file has correct values
4. Make sure you're using the optimized schema

---

*Setup Guide Version: 1.0*  
*Created: December 20, 2025*

