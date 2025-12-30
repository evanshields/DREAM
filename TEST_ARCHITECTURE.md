# Dream AI Test Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DREAM AI APPLICATION                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │   Frontend      │  │   Python        │  │   Backend       │        │
│  │   (React)       │  │   Calculations  │  │   (FastAPI)     │        │
│  │                 │  │   (Shieldstone) │  │   [Future]      │        │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘        │
│           │                    │                     │                  │
└───────────┼────────────────────┼─────────────────────┼──────────────────┘
            │                    │                     │
            │                    │                     │
┌───────────┼────────────────────┼─────────────────────┼──────────────────┐
│           │   TEST SUITE       │                     │                  │
│           │                    │                     │                  │
│  ┌────────▼───────────┐  ┌────▼──────────────┐  ┌──▼─────────────┐   │
│  │                    │  │                    │  │                 │   │
│  │  E2E TESTS         │  │  UNIT TESTS        │  │  INTEGRATION    │   │
│  │  (Playwright)      │  │  (Pytest)          │  │  TESTS          │   │
│  │                    │  │                    │  │  (Pytest)       │   │
│  │  • User Flows      │  │  • NOI Calc        │  │                 │   │
│  │  • Deal Creation   │  │  • DSCR Calc       │  │  • Scenario Mgmt│   │
│  │  • Assumption Edit │  │  • IRR Calc        │  │  • State Sync   │   │
│  │  • Scenario Switch │  │  • EM Calc         │  │  • Propagation  │   │
│  │  • Export          │  │  • CoC Calc        │  │                 │   │
│  │                    │  │  • Leverage        │  │  18 Tests       │   │
│  │  22 Tests          │  │  • Rent Growth     │  │  <2 seconds     │   │
│  │  5-30s each        │  │                    │  │                 │   │
│  │                    │  │  27 Tests          │  │                 │   │
│  │                    │  │  <1ms each         │  │                 │   │
│  └────────────────────┘  └────────────────────┘  └─────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    SHARED TEST INFRASTRUCTURE                     │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                   │  │
│  │  • conftest.py       - Fixtures & config                         │  │
│  │  • pytest.ini        - Pytest settings                           │  │
│  │  • fixtures/         - Test data (mock_deals.json)               │  │
│  │  • requirements      - Dependencies                              │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CI/CD PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Commit  │→ │ Unit     │→ │ Integrate│→ │   E2E    │→ │ Coverage │ │
│  │  / PR    │  │ Tests    │  │ Tests    │  │  Tests   │  │  Report  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                                           │
│  ✓ Python 3.10/3.11    ✓ Fast (<1s)    ✓ Fast (<2s)    ✓ Full (~10m)  │
│  ✓ Lint & Type Check   ✓ Deterministic  ✓ State Tests  ✓ Real Browser │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Test Coverage Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRITICAL PATHS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. CREATE/EDIT DEAL                                            │
│     ├─ Create from dashboard          [E2E ✓]                  │
│     ├─ Upload OM                       [E2E ✓]                  │
│     ├─ Extract data                    [E2E ✓]                  │
│     ├─ Edit details                    [E2E ✓]                  │
│     └─ Pipeline navigation             [E2E ✓]                  │
│                                                                  │
│  2. EDIT ASSUMPTIONS                                            │
│     ├─ Open editor                     [E2E ✓]                  │
│     ├─ Change rent growth              [E2E ✓][INT ✓][UNIT ✓]  │
│     ├─ Change exit cap                 [E2E ✓][INT ✓][UNIT ✓]  │
│     ├─ Change vacancy                  [E2E ✓][INT ✓][UNIT ✓]  │
│     ├─ Change debt terms               [E2E ✓][UNIT ✓]         │
│     └─ Real-time recalc (<100ms)       [UNIT ✓]                │
│                                                                  │
│  3. RUN SCENARIOS                                               │
│     ├─ Create Base Case                [INT ✓]                  │
│     ├─ Create Upside                   [E2E ✓][INT ✓]          │
│     ├─ Create Downside                 [E2E ✓][INT ✓]          │
│     ├─ Switch between scenarios        [E2E ✓][INT ✓]          │
│     ├─ Compare side-by-side            [E2E ✓][INT ✓]          │
│     └─ Delete scenarios                [E2E ✓][INT ✓]          │
│                                                                  │
│  4. VIEW/EXPORT METRICS                                         │
│     ├─ View summary (IRR, EM, CoC)     [E2E ✓][UNIT ✓]         │
│     ├─ View pro forma                  [E2E ✓][UNIT ✓]         │
│     ├─ View sensitivity                [E2E ✓]                  │
│     ├─ View recommendation             [E2E ✓]                  │
│     ├─ Export to Excel                 [E2E ✓]                  │
│     ├─ Generate PDF memo               [E2E ✓]                  │
│     └─ Share link                      [E2E ✓]                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Financial Calculations Coverage

```
┌────────────────────────────────────────────────────────────────────┐
│                 SHIELDSTONE METHODOLOGY VALIDATION                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  NOI (Net Operating Income)                            [UNIT ✓ 4]  │
│  ├─ GPR - Vacancy + Other Income = EGI                             │
│  ├─ EGI - Operating Expenses = NOI                                 │
│  ├─ NOI per unit                                                   │
│  └─ NOI margin                                                     │
│                                                                     │
│  DSCR (Debt Service Coverage Ratio)                   [UNIT ✓ 4]  │
│  ├─ NOI / Annual Debt Service                                      │
│  ├─ LTV vs DSCR constraint                                         │
│  ├─ Loan = MIN(LTV Loan, DSCR Loan)                               │
│  └─ DSCR ≥ 1.25x validation                                        │
│                                                                     │
│  IRR (Internal Rate of Return)                        [UNIT ✓ 6]  │
│  ├─ Simple IRR calculation                                         │
│  ├─ IRR with zero cash flows (renovation)                          │
│  ├─ IRR ≥ 12% minimum validation                                   │
│  ├─ Negative IRR (loss scenario)                                   │
│  ├─ IRR precision (NPV ≈ 0)                                        │
│  └─ IRR impact from rent growth                                    │
│                                                                     │
│  Equity Multiple                                      [UNIT ✓ 3]  │
│  ├─ Total Distributions / Total Equity                             │
│  ├─ EM ≥ 1.4x validation                                           │
│  └─ Consistency with IRR calc                                      │
│                                                                     │
│  Cash-on-Cash Return                                  [UNIT ✓ 4]  │
│  ├─ Annual CF / Total Equity                                       │
│  ├─ CoC ≥ 6% validation                                            │
│  ├─ Year 1 vs Stabilized CoC                                       │
│  └─ CoC from NOI and debt service                                  │
│                                                                     │
│  Sources & Uses                                       [UNIT ✓ 2]  │
│  ├─ Sources = Uses balance                                         │
│  └─ Equity = Down + Closing + CapEx                                │
│                                                                     │
│  Impact Analysis                                      [UNIT ✓ 4]  │
│  ├─ Leverage impact on DSCR                                        │
│  ├─ Leverage impact on CoC                                         │
│  ├─ Rent growth impact on NOI                                      │
│  └─ Rent growth impact on IRR                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Total Financial Tests: 27
Coverage: 100% of core calculations
Performance: <1ms per test
```

## Test Execution Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Developer Workflow                                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Write code                                                │
│     ↓                                                         │
│  2. Run fast tests                                            │
│     $ npm run test:fast                                       │
│     → Unit tests (27) + Integration tests (18)               │
│     → Complete in ~2 seconds                                  │
│     ↓                                                         │
│  3. If tests pass → commit                                    │
│     If tests fail → fix and repeat                           │
│     ↓                                                         │
│  4. Before PR: Run full suite                                 │
│     $ npm test                                                │
│     → Includes E2E tests                                      │
│     → Complete in ~5 minutes                                  │
│     ↓                                                         │
│  5. Push to GitHub                                            │
│     ↓                                                         │
│  6. CI/CD runs automatically                                  │
│     → Unit + Integration + E2E                                │
│     → Coverage report uploaded                                │
│     → PR blocked if tests fail                                │
│     ↓                                                         │
│  7. Merge when all checks pass ✓                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

**Legend:**
- `[UNIT ✓]` - Unit test coverage
- `[INT ✓]` - Integration test coverage  
- `[E2E ✓]` - End-to-end test coverage
- Numbers indicate test count

**Last Updated:** December 20, 2025

