# Phase 1 Task Parallelization Guide

**Created:** December 2025  
**Purpose:** Identify tasks that can be completed asynchronously/in parallel

---

## Overview

This guide identifies which Phase 1 tasks can be completed in parallel, allowing for faster development by working on independent tasks simultaneously.

---

## Task Dependency Analysis

### Critical Path (Must be sequential)

```
1.1 (DB Schema) → 1.6 (Backend API) → 1.10 (Document Upload API) → 1.17 (Extraction Processor)
```

### Independent Workstreams (Can be done in parallel)

#### Workstream A: Frontend Components (UX → UI → React)
- Tasks 1.2, 1.3, 1.4 (Manual Entry Form)
- Tasks 1.7, 1.8, 1.9 (Document Upload)
- Tasks 1.19, 1.20 (Extraction Review)

#### Workstream B: Backend Services (Independent services)
- Task 1.11 (Storage Service) - Independent
- Task 1.12 (Classification Service) - Independent
- Task 1.13 (LLM Router) - Independent
- Tasks 1.14, 1.15, 1.16 (Extraction Services) - Can be parallel

#### Workstream C: Backend APIs (After DB is ready)
- Task 1.6 (Create Deal API)
- Task 1.10 (Document Upload API)
- Task 1.18 (Extraction Status API)

---

## Parallelization Opportunities

### ✅ Can Start Immediately (No Dependencies)

#### UX Prototypes (Independent)
- **Task 1.2**: Manual Entry Form UX Prototype
- **Task 1.7**: Document Upload UX Prototype  
- **Task 1.19**: Extraction Review UX Prototype

**Why**: Pure HTML prototypes don't depend on backend or database.

**Can be done by**: UX Engineer (all 3 in parallel)

---

#### Backend Services (Independent)
- **Task 1.11**: File Storage Service ✅ (Already complete)
- **Task 1.12**: Document Classification Service
- **Task 1.13**: LLM Router Implementation

**Why**: These are standalone services that only need:
- External APIs (LLM providers)
- Configuration (env vars)
- No database dependencies

**Can be done by**: Backend Engineer (all 3 in parallel)

---

### ✅ Can Start After Task 1.1 (Database Schema)

#### Backend APIs (Need DB)
- **Task 1.6**: Create Deal Endpoint ✅ (Already complete)
- **Task 1.10**: Document Upload Endpoint ✅ (Already complete)
- **Task 1.18**: Extraction Status API Endpoint

**Why**: Need database schema but are independent of each other.

**Can be done by**: Backend Engineer (can work on 1.18 while others are done)

---

#### Extraction Services (Can be parallel after 1.13)
- **Task 1.14**: OM Extraction Service
- **Task 1.15**: T-12 Extraction Service
- **Task 1.16**: Rent Roll Extraction Service

**Why**: All use the same LLM router (Task 1.13) but extract different document types.

**Can be done by**: Backend Engineer (all 3 in parallel after 1.13)

---

### ⚠️ Sequential Tasks (Must wait for dependencies)

#### Frontend Components (Sequential within workstream)
- **Task 1.3** → Depends on **Task 1.2** (UX → UI)
- **Task 1.4** → Depends on **Task 1.3** and **Task 1.6** (UI → React + API)
- **Task 1.8** → Depends on **Task 1.7** (UX → UI)
- **Task 1.9** → Depends on **Task 1.8** and **Task 1.10** (UI → React + API)
- **Task 1.20** → Depends on **Task 1.19** and **Task 1.18** (UX → React + API)

#### Backend Integration (Sequential)
- **Task 1.17** → Depends on Tasks 1.12, 1.13, 1.14, 1.15, 1.16 (Extraction Processor)

---

## Recommended Parallel Execution Plan

### Week 1: Foundation (Parallel)

**Day 1-2:**
- ✅ **Task 1.1**: Database Schema (Backend Engineer) - CRITICAL PATH
- ✅ **Task 1.2**: Manual Entry UX Prototype (UX Engineer) - PARALLEL
- ✅ **Task 1.7**: Document Upload UX Prototype (UX Engineer) - PARALLEL
- ✅ **Task 1.11**: Storage Service (Backend Engineer) - PARALLEL ✅ DONE

**Day 3-4:**
- ✅ **Task 1.6**: Create Deal API (Backend Engineer) - After 1.1
- ✅ **Task 1.3**: Manual Entry UI Styling (UI Engineer) - After 1.2
- ✅ **Task 1.8**: Document Upload UI Styling (UI Engineer) - After 1.7
- ✅ **Task 1.12**: Classification Service (Backend Engineer) - PARALLEL
- ✅ **Task 1.13**: LLM Router (Backend Engineer) - PARALLEL

**Day 5:**
- ✅ **Task 1.10**: Document Upload API (Backend Engineer) - After 1.1, 1.11 ✅ DONE
- ✅ **Task 1.4**: Manual Entry React Component (Full-Stack) - After 1.3, 1.6
- ✅ **Task 1.9**: Document Upload React Component (Full-Stack) - After 1.8, 1.10 ✅ DONE

### Week 2: Extraction (Parallel)

**Day 1-2:**
- ✅ **Task 1.14**: OM Extraction Service (Backend Engineer) - After 1.13
- ✅ **Task 1.15**: T-12 Extraction Service (Backend Engineer) - After 1.13 (PARALLEL)
- ✅ **Task 1.16**: Rent Roll Extraction Service (Backend Engineer) - After 1.13 (PARALLEL)
- ✅ **Task 1.19**: Extraction Review UX Prototype (UX Engineer) - PARALLEL

**Day 3-4:**
- ✅ **Task 1.17**: Extraction Processor (Backend Engineer) - After 1.14, 1.15, 1.16
- ✅ **Task 1.18**: Extraction Status API (Backend Engineer) - After 1.17
- ✅ **Task 1.20**: Extraction Review UI Component (UI Engineer) - After 1.19

**Day 5:**
- ✅ **Task 1.21**: Extraction Review React Component (Full-Stack) - After 1.20, 1.18

---

## Maximum Parallelization Strategy

### Phase 1a: Manual Entry (Can parallelize 3 tracks)

**Track 1: UX/UI/React (Sequential within track)**
- Task 1.2 → Task 1.3 → Task 1.4

**Track 2: Backend API (After DB)**
- Task 1.6

**Track 3: Database (Blocks Track 2)**
- Task 1.1

**Parallelization**: Track 1 can start immediately, Track 2 waits for Track 3

---

### Phase 1b: Document Upload (Can parallelize 3 tracks)

**Track 1: UX/UI/React (Sequential within track)**
- Task 1.7 → Task 1.8 → Task 1.9

**Track 2: Backend API (After DB + Storage)**
- Task 1.10

**Track 3: Storage Service (Independent)**
- Task 1.11 ✅ DONE

**Parallelization**: All tracks can start after Task 1.1, Track 2 needs Track 3

---

### Phase 1c: AI Extraction (Maximum parallelization)

**Track 1: Classification & Router (Independent)**
- Task 1.12 (Classification) - PARALLEL
- Task 1.13 (LLM Router) - PARALLEL

**Track 2: Extraction Services (After Router, can be parallel)**
- Task 1.14 (OM) - PARALLEL
- Task 1.15 (T-12) - PARALLEL
- Task 1.16 (Rent Roll) - PARALLEL

**Track 3: Processor & API (After all extraction services)**
- Task 1.17 (Processor) - Sequential
- Task 1.18 (Status API) - Sequential

**Parallelization**: Track 1 can start immediately, Track 2 can run 3 tasks in parallel after Track 1

---

## Key Insights

### ✅ Best Parallelization Opportunities

1. **UX Prototypes**: All 3 can be done simultaneously (Tasks 1.2, 1.7, 1.19)
2. **Backend Services**: Classification, Router, Storage can be parallel (Tasks 1.11, 1.12, 1.13)
3. **Extraction Services**: OM, T-12, Rent Roll can be parallel (Tasks 1.14, 1.15, 1.16)
4. **Backend APIs**: Deal API, Document API, Status API are independent (Tasks 1.6, 1.10, 1.18)

### ⚠️ Sequential Bottlenecks

1. **Database Schema (Task 1.1)**: Blocks all backend API tasks
2. **Extraction Processor (Task 1.17)**: Must wait for all extraction services
3. **Frontend Components**: Must follow UX → UI → React sequence

---

## Resource Allocation Recommendations

### Single Developer
- Focus on critical path first (1.1 → 1.6 → 1.10 → 1.17)
- Do independent tasks (1.11, 1.12, 1.13) during waiting periods
- Batch similar tasks (all UX prototypes together, all extraction services together)

### Team of 2-3 Developers
- **Developer 1**: Backend (APIs, Services, Processor)
- **Developer 2**: Frontend (UX → UI → React components)
- **Developer 3**: Backend Services (Classification, Router, Extraction services)

### Team of 4+ Developers
- **UX Engineer**: All UX prototypes (Tasks 1.2, 1.7, 1.19) in parallel
- **UI Engineer**: UI styling tasks (Tasks 1.3, 1.8, 1.20) sequentially after UX
- **Backend Engineer 1**: APIs (Tasks 1.6, 1.10, 1.18) after DB ready
- **Backend Engineer 2**: Services (Tasks 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17)
- **Full-Stack Developer**: React components (Tasks 1.4, 1.9, 1.21) after UI + API ready

---

## Summary: Tasks That Can Be Done Asynchronously

### ✅ Completely Independent (Start Anytime)
- Task 1.2: Manual Entry UX Prototype
- Task 1.7: Document Upload UX Prototype
- Task 1.11: Storage Service ✅ DONE
- Task 1.12: Classification Service
- Task 1.13: LLM Router
- Task 1.19: Extraction Review UX Prototype

### ✅ Independent After DB Schema (Task 1.1)
- Task 1.6: Create Deal API ✅ DONE
- Task 1.10: Document Upload API ✅ DONE
- Task 1.18: Extraction Status API

### ✅ Can Be Parallel After Prerequisites
- Tasks 1.14, 1.15, 1.16: Extraction Services (after Task 1.13)
- Tasks 1.3, 1.8: UI Styling (after UX prototypes)
- Tasks 1.4, 1.9: React Components (after UI + API)

---

**Recommendation**: Start with independent tasks (UX prototypes, backend services) while waiting for database schema completion, then parallelize extraction services and frontend components.

