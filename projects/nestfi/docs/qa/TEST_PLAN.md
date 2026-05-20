# Test Plan — NestFi v1.0

**Status**: DRAFT (Phase 3 — Implementation Planning)  
**Prepared by**: QA  
**Last Updated**: 2026-05-16

---

## Executive Summary

This document defines the test strategy, scope, and exit criteria for NestFi v1.0 MVP. Testing will cover core user flows (authentication, family management, transactions, and dashboards) across unit, integration, and end-to-end levels. The release gate requires **VERDICT: PASS** with no `OPEN_CRITICAL` or `OPEN_MAJOR` bugs.

---

## 1. Scope

### 1.1 In Scope for MVP (Phase 5 Release Gate)

**MUST user stories** (all acceptance criteria must pass):
- US-1.1: Superadmin login
- US-1.2: User registration via email invitation
- US-1.3: User login & family selector
- US-2.1: Create family
- US-2.2: Add family members
- US-3.1: Create account
- US-3.2: View all accounts
- US-4.1: View default categories
- US-5.1: Record income transaction
- US-5.2: Record expense transaction
- US-5.4: Edit transaction
- US-6.1: View dashboard summary
- US-6.2: View expense breakdown by category
- US-7.1: Logout

**SHOULD user stories** (best effort; optional for v1):
- US-1.4: Password reset
- US-2.3: View family members
- US-2.4: Disable/enable members
- US-3.3: Edit account
- US-4.2: Create custom category
- US-5.3: Record investment transaction
- US-5.5: Disable/restore transaction
- US-6.3: Income vs. expense trends
- US-6.4: Export financial report

**Out of Scope**:
- US-7.2: Session timeout (deferred to v1.1)
- Rate limiting, advanced security
- Mobile optimization
- Email delivery (mocked; tokens in logs)

---

## 2. Test Types

### 2.1 Layered Approach

| Level | Owner | Scope | Tools |
|---|---|---|---|
| **Unit** | BE/FE | Model validation, business logic | pytest, vitest |
| **Integration** | BE/FE | API endpoints with test DB, component + API mocks | pytest, vitest |
| **End-to-End** | QA | Real BE + FE via Docker Compose; full workflows | curl, manual browser |
| **Manual** | QA | UX, edge cases, cross-browser | Browser, checklist |

### 2.2 Test Matrix by Story Group

| Story Group | Unit | Integration | E2E | Manual |
|---|---|---|---|---|
| **Auth** (US-1.x) | ✓ | ✓ Endpoints | ✓ Login flow | ✓ UX |
| **Family** (US-2.x) | ✓ | ✓ CRUD | ✓ Create + invite | ✓ Selector UX |
| **Accounts** (US-3.x) | ✓ Balance calc | ✓ CRUD | ✓ Create, view | ✓ Sorting |
| **Categories** (US-4.x) | ✓ Seed logic | ✓ CRUD | ✓ Seed on family | ✓ Dropdown |
| **Transactions** (US-5.x) | ✓ Validation | ✓ CRUD, disable | ✓ Record, edit, disable | ✓ Real-time balance |
| **Dashboard** (US-6.x) | ✓ Aggregation | ✓ API | ✓ Load, data correct | ✓ Charts, perf |
| **Security** (US-7.x) | ✓ Logout | ✓ Session clear | ✓ Full logout flow | ✓ Back-button |

---

## 3. Test Environment

### 3.1 Setup (Phase 5)

```bash
# Backend: FastAPI + PostgreSQL
cd backend && pytest -v --cov=app --tb=short 2>&1 | tee ../reports/_be_test_stdout.log

# Frontend: React + Vite
cd frontend && npm test -- --run 2>&1 | tee ../reports/_fe_test_stdout.log

# Integration: Docker Compose
docker compose up --build -d
# Run E2E tests, verify endpoints
docker compose down
```

### 3.2 Test Data Seed

- **Superadmin**: `superadmin` / `admin123`
- **Test family**: "Test Family Smith"
- **Test users**: owner@example.com, member1@example.com
- **Accounts**: Checking, Savings (with initial balances)
- **Categories**: Pre-seeded per US-4.1 (Income, Expense, Investment)
- **Sample transactions**: 10–15 varied transactions for dashboards

---

## 4. Coverage Targets

### 4.1 Code Coverage (Backend)

- **Target**: ≥ 80% line coverage for core modules
  - `app/auth/` — login, registration, password reset
  - `app/families/` — CRUD, member management
  - `app/accounts/` — CRUD, balance calculation
  - `app/transactions/` — CRUD, edit history, disable/enable
  - `app/dashboards/` — aggregation logic

### 4.2 User Story Acceptance Criteria

- **Target**: 100% of MUST story ACs tested (automated or manual)
- **Approach**: ≥1 E2E test per acceptance criterion

---

## 5. Entry Criteria

✓ All upstream inputs present (checked via `check_prerequisites.sh QA`)
✓ BE/FE code complete and unit-tested (Phase 4 — BUILD)
✓ Docker Compose successfully runs with test data seed
✓ API endpoints respond (health check: `GET /api/v1/docs`)

---

## 6. Exit Criteria (Release Gate)

**Mandatory for PASS**:
1. ✓ `reports/TEST_REPORT.md` marked `VERDICT: PASS`
2. ✓ All MUST user stories: 100% AC pass
3. ✓ `reports/BUG_REPORT.md`: No `OPEN_CRITICAL`, `OPEN_MAJOR`, or `RETEST_FAIL`
4. ✓ Backend: ≥ 80% line coverage (reported)
5. ✓ E2E happy path: Zero errors
6. ✓ Dashboard: Loads < 2 seconds

**Release-blocking statuses**:
- `OPEN_CRITICAL`: App unusable
- `OPEN_MAJOR`: Feature broken
- `RETEST_FAIL`: Fix did not work

**Allowed to ship**:
- `OPEN_MINOR`: Cosmetic issues
- `FIXED`, `RETEST_PASS`, `WONT_FIX`: Closed issues

---

## 7. Test Execution Timeline

| Phase | Days | Activity | Owner |
|---|---|---|---|
| **Prep** | 1–2 | Unit/integration tests by BE/FE; E2E env setup | BE, FE, QA |
| **Execute** | 3–4 | QA runs E2E tests, files bugs | QA |
| **Fix** | 5–6 | BE/FE fix bugs, QA retests | BE, FE, QA |
| **Sign-off** | 7 | QA writes TEST_REPORT with VERDICT | QA |

---

## 8. Bug Severity Rules

| Severity | Impact | Release Blocks? | Example |
|---|---|---|---|
| **CRITICAL** | App unusable, data lost | YES | Superadmin can't log in |
| **MAJOR** | Core feature broken | YES | Can't record transactions |
| **MINOR** | Workaround exists, cosmetic | NO | Typo in label |

---

## 9. Automated Test Helpers

### Backend (pytest)

```bash
cd backend
pytest -v --cov=app --cov-report=term-missing --tb=short \
  tests/test_auth.py \
  tests/test_families.py \
  tests/test_accounts.py \
  tests/test_transactions.py \
  tests/test_dashboards.py \
  2>&1 | tee ../reports/_be_test_stdout.log
```

### Frontend (vitest)

```bash
cd frontend
npm test -- --run 2>&1 | tee ../reports/_fe_test_stdout.log
```

---

## 10. Known Risks & Limitations

| Risk | Mitigation |
|---|---|
| Email not sent (v1 mocked) | Tokens printed to logs; QA uses manually |
| No mobile testing | Desktop-only; defer to v1.1 |
| Test data reset | Docker cleanup; seed scripts ensure clean state |
| Flaky tests | Avoid hardcoded delays; use wait-for conditions |

---

## Next Steps

1. BE/FE write unit + integration tests (Phase 4)
2. QA executes E2E tests + manual validation (Phase 5)
3. File bugs, track retests, sign off on PASS/FAIL (Phase 5)
4. Route DELIVERY on PASS; route BE/FE on FAIL (Phase 5→6)

For detailed test cases, see `docs/qa/TEST_CASES.md`.
