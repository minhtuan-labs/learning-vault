# Test Plan — NestFi MVP (v1)

**Version:** 1.0  
**Phase:** 3_IMPLEMENTATION_PLANNING  
**Owner:** QA  
**Last Updated:** 2026-05-16  
**Timeline:** 2-3 days (Phase 5: Test & Fix, following 6-7 day Phase 4 build)

---

## 1. Overview & Test Strategy

### 1.1 Scope

NestFi MVP is a household financial management application.

**In Scope for v1:**
- All 37 user stories (US-001 to US-037)
- 21 backend API endpoints
- 6 frontend pages
- PostgreSQL 16 database
- Email service integration (SMTP)

**Out of Scope for v1:**
- Rate limiting, advanced security (v2)
- Password reset flow (v2)
- Token refresh endpoint (v2)
- Mobile-responsive design (v1.1)
- CSV/PDF export (v1.1)
- WebSocket real-time updates (v2)

### 1.2 Test Strategy

**Testing Pyramid:**
- Unit Tests (60%): CRUD operations, auth logic, business logic, validation
- Integration Tests (35%): API endpoint flows, database interactions, permission checks
- E2E Tests (5%): Critical user journeys (login → family creation → transaction logging → dashboard)

**Testing Focus:**
1. Happy Path: Standard workflows per user stories
2. Edge Cases: Boundary conditions, empty data, pagination limits
3. Authorization: RBAC enforcement (superadmin, owner, member, view_only)
4. Error Handling: Invalid inputs, missing resources, permission denials
5. Data Integrity: Soft deletes, audit logs, transaction consistency

---

## 2. Test Types & Breakdown

### 2.1 Unit Tests

**Coverage Target:** 70% of backend code

**Test Categories:**
- Models & Schemas: 20 tests
- CRUD Operations: 30 tests
- Auth & Security: 15 tests
- Business Logic: 20 tests
- Validation: 15 tests
- Utilities: 10 tests
- **Total Unit Tests:** ~110

**Tools:** pytest, pytest-cov, unittest.mock, faker

**Fixtures (conftest.py):**
- `db_session`: In-memory SQLite for fast tests
- `user_factory`: Create users with roles (superadmin, owner, member)
- `family_factory`: Create families with members
- `transaction_factory`: Create transactions with categories
- `category_factory`: Create categories (income, expense, investment)

### 2.2 Integration Tests

**Coverage Target:** 100% of API endpoints (21 endpoints)

**Test Categories:**
- Auth (2 endpoints): 6 tests
- Families (4 endpoints): 12 tests
- Family Members (3 endpoints): 12 tests
- Invitations (2 endpoints): 8 tests
- Transactions (4 endpoints): 16 tests
- Categories (4 endpoints): 12 tests
- Analytics (2 endpoints): 6 tests
- Health (1 endpoint): 2 tests
- **Total Integration Tests:** ~78

**Tools:** pytest, httpx, TestClient (FastAPI), pytest-asyncio

**Test Data:**
- Pre-populated test families, users, transactions
- Clean state per test (rollback after each)

### 2.3 End-to-End Tests

**Coverage Target:** 5% (critical user journeys only)

**Scenarios:**
1. Superadmin → Create Family → Invite Owner → Owner Accepts → Family Ready
2. Owner → Log Transactions → View Dashboard
3. Member → Edit Own Transaction → Verify Audit Trail

**Tools:** Docker Compose, Playwright (v1.1), Manual testing

---

## 3. Test Environment & Tools

### 3.1 Test Database

**Database:** PostgreSQL 16 (same as production)

**Setup:**
```bash
DATABASE_URL=postgresql://testuser:testpass@localhost:5432/nestfi_test
pytest runs alembic upgrade head before first test
```

**Isolation:** Each test transaction rolled back after completion; clean state guaranteed

### 3.2 Test Tools & Stack

| Tool | Purpose | Version |
|---|---|---|
| pytest | Test runner | 7.4+ |
| pytest-cov | Coverage reporting | 4.1+ |
| pytest-asyncio | Async/await support | 0.21+ |
| httpx | Async HTTP client | 0.24+ |
| TestClient (FastAPI) | Simulated API requests | FastAPI 0.100+ |
| faker | Random test data | 19.0+ |
| freezegun | Mock time/datetime | 1.2+ |
| Alembic | Database migrations | 1.11+ |
| Docker Compose | E2E environment | 2.0+ |

---

## 4. Manual vs. Automated Testing Split

### 4.1 Automated (70% of effort)

- ✅ All CRUD operations (create, read, update, delete)
- ✅ Auth logic (password hashing, JWT signing)
- ✅ Validation (schemas, business rules)
- ✅ All 21 API endpoints (happy path + error cases)
- ✅ Permission checks (RBAC enforcement)
- ✅ Soft-delete behavior
- ✅ Pagination, filtering, sorting
- ✅ Database constraints, foreign keys

### 4.2 Manual (30% of effort)

| Area | Effort | Timeline |
|---|---|---|
| UI/UX flows | 6h | Day 1 afternoon |
| Email delivery | 3h | Day 1 evening |
| Multi-browser testing | 2h | Day 2 morning |
| Edge cases | 4h | Day 2 afternoon |
| Data scenarios | 2h | Day 2 evening |
| Performance spot-checks | 2h | Day 3 morning |

---

## 5. Bug Severity & Release Blockers

### 5.1 Bug Status Convention

```
OPEN_CRITICAL → (fix) → RETESTING → RETEST_PASS / RETEST_FAIL
OPEN_MAJOR → FIXED / WONT_FIX
OPEN_MINOR → (soft warning allowed to ship)
```

### 5.2 Severity Definitions

| Severity | Definition | Blocks Release? | Examples |
|---|---|---|---|
| **CRITICAL** | Blocks all use of app; core feature broken | YES | Login 500, migration fails, data deleted |
| **MAJOR** | Affects primary user story; partially broken | YES | Txns don't save, can't invite, permissions broken |
| **MINOR** | Cosmetic or non-critical; workaround exists | NO | Typo, icon missing, chart misaligned |
| **WONT_FIX** | Deferred to v2 (by design) | NO | Password reset not implemented, WebSocket not available |

### 5.3 Release Gate

**Release BLOCKED if:**
- Any `OPEN_CRITICAL` exists
- Any `OPEN_MAJOR` exists
- Any `RETEST_FAIL` exists

**Release ALLOWED if:**
- All CRITICAL and MAJOR resolved
- `TEST_REPORT.md` starts with `VERDICT: PASS`
- Manual testing checklist completed

---

## 6. Test Coverage & Acceptance Criteria

### 6.1 Coverage Targets

| Category | Target | Method |
|---|---|---|
| Unit Test Coverage | 70% lines | pytest-cov report |
| Integration Test Coverage | 100% endpoints (21/21) | Test list vs API_CONTRACT.md |
| Manual Test Coverage | 100% user stories | Checklist completion |
| Critical Path Coverage | 100% | E2E test per flow |

### 6.2 Test Case Inventory (49+ cases)

- Authentication: 4 cases
- Family Management: 8 cases
- Member Management: 8 cases
- Transactions: 12 cases
- Categories: 9 cases
- Analytics: 5 cases
- Authorization (Cross-cutting): 7 cases

### 6.3 Acceptance Criteria

Test Suite is COMPLETE when:
- [ ] Unit tests: 110+ passing, ≥70% code coverage
- [ ] Integration tests: 78+ passing, all 21 endpoints covered
- [ ] Manual tests: Checklist 100% complete
- [ ] Test data: Isolated per test, consistent
- [ ] Bug report: All CRITICAL and MAJOR resolved
- [ ] Performance: Dashboard <3s, pagination <1s
- [ ] Soft-delete: Deleted transactions hidden
- [ ] RBAC: All permission tests passing
- [ ] Audit: Edits/deletes logged
- [ ] Errors: User-friendly, no stack traces
- [ ] Frontend: Zero console errors

---

## 7. Test Execution Timeline

### Phase 4: Build (Days 1–7)

**BE Track (Days 1–5, parallel with FE):**
- Day 1: Unit tests (models, schemas, auth) — 30 tests
- Day 2: Integration tests (auth, families, members) — 20 tests
- Day 3: Integration tests (transactions, categories) — 30 tests
- Day 4: Integration tests (analytics, health) — 10 tests
- Day 5: Full suite, 70% coverage, all passing

**Dependencies:**
- Models defined
- API endpoints implemented
- Database migrations finalized
- SMTP service available (or mocked)

### Phase 5: Test & Fix (Days 1–3)

**Day 1 Morning (4h):** Test Execution
- Run full automated suite (pytest)
- Document failures, capture logs
- Begin bug triage

**Day 1 Afternoon (4h):** Manual Testing
- Browser-based UI flow testing
- Email delivery validation
- Create initial BUG_REPORT.md

**Day 1 Evening (2h):** Bug Analysis
- Prioritize bugs (CRITICAL, MAJOR, MINOR)
- Assign to BE/FE for fixing
- Update TEST_REPORT.md initial verdict

**Day 2 (8h):** Fix & Retest
- BE fixes CRITICAL/MAJOR bugs
- QA retests (RETESTING → RETEST_PASS)
- Update BUG_REPORT.md status
- Final coverage analysis

**Day 3 (4h):** Final Validation
- Run full test suite one more time
- Manual smoke tests on critical flows
- Finalize TEST_REPORT.md with VERDICT

---

## 8. Test Environment Setup

### 8.1 Prerequisites

Before QA Phase 5:
- [ ] `backend/` source code complete
- [ ] `frontend/` source code complete
- [ ] `docker-compose.yml` available
- [ ] PostgreSQL 16 accessible
- [ ] Test data seeds prepared
- [ ] `.env.test` configured (DB URL, JWT secret, email service)
- [ ] `alembic upgrade head` runs

### 8.2 Quick Start

```bash
cd backend/
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt

cp .env.example .env.test
# Edit .env.test with test DB URL, JWT secret

alembic upgrade head
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 9. Test Deliverables

| File | Owner | Deadline | Content |
|---|---|---|---|
| `TEST_CASES.md` | QA | Day 1 Phase 5 | List of 49+ test cases |
| `TEST_REPORT.md` | QA | Day 3 Phase 5 | Verdict, metrics, evidence |
| `BUG_REPORT.md` | QA | Day 3 Phase 5 | Bugs, status, assignments |
| `coverage.html` | BE | Day 3 Phase 5 | Coverage report |
| `test_*.py` | BE | Day 5 Phase 4 | Unit & integration tests |

### 9.1 TEST_REPORT.md Format

Starts with: `VERDICT: PASS`

Then includes: Executive summary, per-suite results, failures, bugs found, risks

---

## 10. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Email service unavailable | Medium | Medium | Mock SMTP in tests |
| Soft-delete filter leak | Low | Critical | Query tests verify deleted_at |
| Permission bypass | Low | Critical | RBAC test matrix |
| Token expiry | Low | Medium | Mock clock in tests |
| Pagination off-by-one | Low | Low | Boundary tests |

---

## 11. Acceptance Criteria (Phase 5 Exit Gate)

Phase 5 is COMPLETE when:

- [ ] TEST_REPORT.md with `VERDICT: PASS`
- [ ] Coverage ≥ 70%
- [ ] All 21 endpoints tested
- [ ] BUG_REPORT.md: No OPEN_CRITICAL/MAJOR/RETEST_FAIL
- [ ] Manual checklist 100% complete
- [ ] Performance <3s dashboard, <1s pagination
- [ ] Soft-delete verified
- [ ] RBAC enforced
- [ ] Audit logging works
- [ ] User-friendly errors only
- [ ] No frontend console errors

**If PASS:** Route DELIVERY to deploy (Phase 6)  
**If FAIL:** Route BE/FE to fix bugs; QA retests until PASS

---

## 12. References

- USER_STORIES.md: docs/business/USER_STORIES.md
- API_CONTRACT.md: docs/architecture/API_CONTRACT.md
- BE_PLAN.md: planning/BE_PLAN.md
- FE_PLAN.md: planning/FE_PLAN.md
- TECH_STACK.md: docs/architecture/TECH_STACK.md
- pytest: https://docs.pytest.org/
- FastAPI Testing: https://fastapi.tiangolo.com/advanced/testing-databases/

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | QA | Created TEST_PLAN.md with comprehensive strategy, timeline, criteria, risk assessment |
