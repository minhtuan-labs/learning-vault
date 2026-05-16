# Test Strategy — NestFi

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** QA  
**Phase:** 3_IMPLEMENTATION_PLANNING

---

## 1. Test Coverage Strategy

### Scope: What We're Testing

NestFi v1 is a full-stack application: Dash (frontend) + FastAPI (backend) + PostgreSQL (database).

**In scope for v1:**
- Authentication flows (login, invitation acceptance, password changes)
- Transaction logging (income, expense, cash withdrawal)
- Family management (create, invite, remove members)
- Category management (create, edit, archive categories)
- Dashboard and analytics (summary, category breakdown, trends)
- Authorization checks (role-based access, family membership)
- Database consistency (soft deletes, audit logs, foreign keys)
- Email delivery (invitations, password resets)
- Data integrity (no lost transactions, no orphaned records)

**Out of scope for v1:**
- Performance/load testing (defer to v2 if needed)
- Mobile responsiveness (covered in FE styling, not QA)
- Third-party integrations (none in v1)
- Advanced analytics algorithms (simple sums/counts only)
- Multi-currency edge cases (single currency per family)

### Test Pyramid

```
         E2E (Dash UI)           ~20% coverage
              ↑
         Integration (API)       ~40% coverage
              ↑
         Unit (Backend + FE)     ~40% coverage
```

**Unit Tests** (~40% effort):
- Backend: `pytest` for FastAPI endpoints, CRUD operations, services, validation
- Frontend: Unit tests for Dash callbacks and utility functions
- Database: Migration validation, schema constraints
- **Target:** 80%+ line coverage for critical modules (auth, transactions, family management)

**Integration Tests** (~40% effort):
- API endpoint tests (REST calls with real database)
- Authentication flow (login → get families → get transactions)
- Transactional flows (create family → invite members → log transaction)
- Authorization tests (verify role-based access, family boundaries)
- Email service (mock SMTP or MailTrap verification)
- **Test against:** Real PostgreSQL instance in isolated test DB

**E2E Tests** (~20% effort):
- Critical user flows via Dash frontend (Selenium or Playwright)
- Login → dashboard → log transaction → verify in ledger
- Family switching → member invitations → accept/decline
- **Test against:** Full docker-compose stack (backend + frontend + DB)
- **Manual fallback:** If E2E framework setup delayed, manual exploratory testing covers gaps

---

## 2. Manual vs. Automated Testing Split

### Automated Testing (70%)

**Backend (FastAPI + SQLAlchemy):**
- Unit tests for all CRUD operations, services, validators
- Integration tests for API endpoints
- Database migration validation
- Authorization/permission tests
- Run on every build: `cd backend && pytest -v`

**Frontend (Dash):**
- Unit tests for callbacks, data transformations
- Integration tests for multi-page flows (navigate between pages, verify state)
- Run on every build: `cd frontend && pytest -v` (if pytest-dash available)

**API Contract:**
- Automated REST client tests (hit all endpoints with valid/invalid inputs)
- Response schema validation (JSON structure matches OpenAPI spec)
- Error code validation (401, 403, 404, etc. match spec)

### Manual Testing (30%)

**Critical UI flows (hard to automate):**
- Email invitation workflow (send, receive, click link, accept/decline)
- Dashboard chart rendering and interactivity
- Form validation messages and UX feedback
- Family selector dropdown and switching experience
- Mobile responsiveness (Dash responsive design)

**Edge cases and exploratory:**
- Concurrent transaction logging from multiple family members
- Soft delete visibility (verify deleted transactions hidden)
- JWT token expiration (24-hour timeout behavior)
- Category archival with existing transactions
- Image upload (if avatars implemented)
- Session timeout and re-login flows

**Security checks:**
- Password reset tokens (unique, one-time-use, expire after 24h)
- CSRF protection (if applicable)
- SQL injection attempts (parameterized queries)
- XSS prevention (sanitized input/output)

---

## 3. Critical User Flows for Testing

### CUF-1: Authentication & Onboarding

**Flow:** Superadmin creates family → Owner accepts invitation → Owner sets up categories → Member accepts invitation → All members log in

**Test scenarios:**
- [ ] Superadmin login with default credentials
- [ ] Superadmin creates family (captures new family ID)
- [ ] Superadmin sends owner invitation (email sent within 5 min)
- [ ] Owner clicks invitation link (pre-filled email, form validation)
- [ ] Owner creates account (password complexity checked)
- [ ] Owner logs in with new credentials
- [ ] Owner can access empty dashboard (no transactions yet)
- [ ] Owner invites member via email
- [ ] Member accepts invitation (existing user → no password step)
- [ ] Member logs in and sees same family dashboard
- [ ] Authorization: Member cannot access superadmin functions

**Critical assertions:**
- Email delivery within 5 minutes (SLA check)
- Invitation tokens are unique and one-time-use
- Failed auth attempts don't expose user existence
- JWT token stored correctly, used in subsequent requests

---

### CUF-2: Transaction Logging & Consistency

**Flow:** Member logs transaction → Appears in ledger → Owner verifies it → Member edits own transaction → All members see update

**Test scenarios:**
- [ ] Member logs income transaction (amount, category, date, notes)
- [ ] Transaction appears in family ledger immediately (no refresh needed)
- [ ] Transaction attributed to correct member/date/category
- [ ] Audit log captures creation (timestamp, user, values)
- [ ] Owner edits the same transaction (allowed)
- [ ] All family members see updated transaction
- [ ] Member deletes own transaction (soft delete)
- [ ] Deleted transaction no longer appears in ledger
- [ ] Audit log captures deletion (timestamp, user, deleted_at, deleted_by)
- [ ] Owner can see deleted_at indicator (optional admin view)

**Critical assertions:**
- No data loss (deleted transactions retained in DB)
- Authorization: Member cannot edit other members' transactions
- Authorization: Owner can edit all transactions
- Soft delete queries exclude deleted_at IS NOT NULL
- Dashboard statistics exclude deleted transactions

---

### CUF-3: Family Switching & Multi-Family Access

**Flow:** User belongs to 2 families → Switches between them → Sees correct data per family

**Test scenarios:**
- [ ] User accepts invitation from Family A
- [ ] User accepts invitation from Family B
- [ ] Login shows list of 2 families
- [ ] User selects Family A → sees Family A transactions, members, categories
- [ ] User switches to Family B → sees Family B transactions, members, categories
- [ ] Family A and B have different transaction histories (no cross-contamination)
- [ ] Authorization: User cannot see Family B data while viewing Family A
- [ ] Family selector persists selection (doesn't reset to Family A on refresh)

**Critical assertions:**
- Family membership queries filter by user_id and family_id
- Dashboard queries filtered by selected family_id
- Transactions from Family A don't leak into Family B analytics
- Member removal from Family A doesn't affect Family B membership

---

### CUF-4: Category Management & Defaults

**Flow:** Family created → Default categories auto-generated → Owner creates custom category → Categories used in transactions

**Test scenarios:**
- [ ] On family creation, default categories generated (5 income, 6 expense, 3 investment)
- [ ] Owner can view all 14 default categories
- [ ] Owner creates new custom expense category "Utilities & Internet"
- [ ] Custom category appears in transaction form immediately
- [ ] Member logs transaction with custom category
- [ ] Category appears correctly in ledger and dashboard
- [ ] Owner archives "Entertainment" category
- [ ] Archived category no longer appears in transaction form dropdown
- [ ] Existing "Entertainment" transactions still display correctly
- [ ] Owner reactivates "Entertainment" category
- [ ] Category available again in transaction form

**Critical assertions:**
- Default categories created atomically with family (no race condition)
- Category active_only filter works in queries
- Archived categories excluded from dropdown, but included in historical views
- Transactions retain category reference even if category deleted (foreign key ON DELETE CASCADE mitigation)

---

### CUF-5: Dashboard & Analytics Accuracy

**Flow:** Family logs 10 transactions over 2 months → Dashboard shows correct summary, breakdown, trends

**Test scenarios:**
- [ ] Dashboard displays current month: total income, total expenses, net savings
- [ ] Savings rate calculated correctly: (income - expenses) / income
- [ ] Category breakdown chart shows correct percentages
- [ ] Deleted transactions excluded from dashboard totals
- [ ] Monthly trends chart shows correct values for last 6 months
- [ ] Member activity log shows correct member names and transaction counts
- [ ] Filter by month/year updates all dashboard elements
- [ ] Performance: Dashboard loads within 3 seconds with 100+ transactions

**Critical assertions:**
- SUM(amount) WHERE type='income' and deleted_at IS NULL
- SUM(amount) WHERE type='expense' and deleted_at IS NULL
- Category breakdown: SUM(amount) GROUP BY category_id WHERE deleted_at IS NULL
- No double-counting or missing transactions
- Floating-point precision (decimal fields, not floats)

---

## 4. Acceptance Criteria Mapping

Each user story in USER_STORIES.md has acceptance criteria. QA will create a test case for each criterion:

| User Story | # Criteria | Coverage | Notes |
|---|---|---|---|
| US-001 (Superadmin login) | 5 | 100% | Unit + integration tests |
| US-002 (Change password) | 4 | 100% | Unit + integration tests |
| US-003 to US-012 (Family/member management) | 45 | 100% | Mix of API + E2E tests |
| US-013 (Family switching) | 6 | 100% | E2E Dash UI test |
| US-014 to US-022 (Transaction logging) | 45 | 100% | API + E2E tests |
| US-023 to US-030 (Category management) | 35 | 100% | API + E2E tests |
| US-031 to US-035 (Dashboard/analytics) | 20 | 100% | Mostly integration (API responses) |
| **Total** | **160+** | **100%** | All covered by tests |

---

## 5. Known Risks & Mitigation

### Risk-1: JWT Token Expiry (24 hours)

**Risk:** Users logged in when token expires; error handling unclear.

**Mitigation:**
- [ ] Test endpoint response at token expiry (should return 401)
- [ ] FE should detect 401 and prompt re-login
- [ ] Test manual token refresh (if refresh endpoint added in v2)
- [ ] Monitoring: Alert if 401 rate spikes (indication of widespread expiry)

### Risk-2: Soft Delete Query Coverage

**Risk:** New queries forget to exclude `deleted_at IS NOT NULL`, showing deleted records.

**Mitigation:**
- [ ] Code review: Every CRUD query must include soft delete filter
- [ ] Base CRUD class enforces filter (developers don't forget)
- [ ] Test: Verify deleted transactions excluded from all views (ledger, analytics)
- [ ] Test: Audit log query includes deleted records (for recovery)

### Risk-3: Email Delivery SLAs (5 minutes)

**Risk:** Email service delays or failures; invitations not sent or spam-filtered.

**Mitigation:**
- [ ] Use MailTrap (free) for dev/test, real SMTP for staging
- [ ] Test: Verify email received within 5 minutes
- [ ] Monitor: Email bounce rate, delivery errors
- [ ] Fallback: Manual resend button in UI (for superadmin/owner)
- [ ] Logging: Log all email send attempts (success/failure)

### Risk-4: Concurrent Transaction Logging

**Risk:** Multiple family members log transactions simultaneously; database deadlocks or lost updates.

**Mitigation:**
- [ ] Test: Simulate 5 members logging transactions concurrently (load test or manual parallel requests)
- [ ] Verify: All transactions recorded, counts correct
- [ ] Database indexes on family_id, user_id, created_at
- [ ] PostgreSQL ACID guarantees handle most cases; test and document

### Risk-5: Authorization Bypass

**Risk:** Role-based access control (RBAC) allows unauthorized actions.

**Mitigation:**
- [ ] Test: Member tries to edit other member's transaction (should fail 403)
- [ ] Test: Non-owner tries to invite members (should fail 403)
- [ ] Test: Superadmin can create families; owner cannot (should fail 403)
- [ ] Code review: Every endpoint has `@require_auth` + role check
- [ ] Audit logging: All authorization denials logged

### Risk-6: Category Archival with Existing Transactions

**Risk:** Owner archives category used in historical transactions; category disappears from views.

**Mitigation:**
- [ ] Test: Archive category with 10 existing transactions
- [ ] Verify: Transactions still display with correct category name
- [ ] Verify: Category appears in "Historical" view (dashboard still counts it)
- [ ] Verify: Archived category not in dropdown for new transactions
- [ ] Database: No cascade delete; just `is_active = false`

### Risk-7: Multi-Family Data Isolation

**Risk:** User's data from Family A leaks into Family B view.

**Mitigation:**
- [ ] Test: Create 2 test families, add same user to both
- [ ] Verify: Family A transactions invisible in Family B view
- [ ] Verify: Family A members not shown in Family B member list
- [ ] Test: Switch between families; verify data isolation
- [ ] Code review: Every query filters by `family_id`

### Risk-8: Image Upload / File Handling

**Risk:** Large uploads, malicious files, or missing images cause crashes.

**Mitigation:**
- [ ] Test: Upload valid image file (if implemented in v1)
- [ ] Test: Upload oversized file (should fail gracefully)
- [ ] Test: Attempt to upload non-image file (should fail validation)
- [ ] Verify: Filesystem paths are CDN-ready (no hardcoded server names)
- [ ] Monitoring: Disk space usage alerts

### Risk-9: Database Migration & Schema Rollback

**Risk:** Alembic migrations fail, leaving DB in inconsistent state.

**Mitigation:**
- [ ] Test: Run migrations forward (empty DB → final schema)
- [ ] Test: Run migrations backward (final → empty)
- [ ] Test: Manual data verification (row counts, constraints intact)
- [ ] Documentation: Migration rollback procedure documented
- [ ] Staging: All migrations tested in staging before production

### Risk-10: Form Validation & Error Messages

**Risk:** Invalid input accepted, or error messages confuse users.

**Mitigation:**
- [ ] Test: Submit form with missing required field (should show validation error)
- [ ] Test: Submit negative amount (should reject)
- [ ] Test: Submit duplicate email (should reject with "Email already registered")
- [ ] Test: Password too short (should show error with requirements)
- [ ] User-facing error messages reviewed (clear, not technical)

---

## 6. Test Environment & Prerequisites

### Local Development (Laptop)

```bash
# Prerequisites
python3 -m venv venv
source venv/bin/activate
cd backend && pip install -r requirements.txt
cd ../frontend && pip install -r requirements.txt

# Start services
docker-compose up -d postgres
cd backend && alembic upgrade head
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && python app/main.py  # Dash on 8050

# Run tests
cd backend && pytest -v --tb=short
cd frontend && pytest -v --tb=short
```

### CI/CD (GitHub Actions, deferred to v2)

```bash
# Build docker images
docker-compose build

# Run test suite inside containers
docker-compose run backend pytest -v
docker-compose run frontend pytest -v

# Start services and run E2E tests
docker-compose up -d
# E2E tests via Selenium/Playwright
docker-compose down
```

---

## 7. Test Execution & Reporting

### Phase 5 (TEST_AND_FIX) Activities

**Week 1: Unit + Integration Testing**
- Run backend unit tests (target: 80%+ coverage)
- Run frontend unit tests (target: 70%+ coverage)
- Run API integration tests (all 40+ endpoints)
- Fix failing tests; document blockers

**Week 2: E2E & Manual Testing**
- Run critical user flow E2E tests (Selenium/Playwright)
- Manual exploratory testing: email, UI flows, edge cases
- Log bugs in BUG_REPORT.md with clear steps to reproduce

**Week 3: Regression & Performance**
- Re-run all tests after bug fixes
- Verify soft deletes and authorization
- Basic performance check (dashboard with 100+ transactions)

**Exit Criteria:**
- TEST_REPORT.md: **VERDICT: PASS**
- All critical flows passing
- No OPEN_CRITICAL or OPEN_MAJOR bugs
- BUG_REPORT.md: All bugs either FIXED or WONT_FIX

---

## 8. Tools & Technologies

| Component | Tool | Rationale |
|---|---|---|
| **Backend testing** | pytest | Python standard; FastAPI-compatible |
| **Frontend testing** | pytest (Dash callbacks) | Python-only; no JavaScript testing |
| **E2E testing** | Selenium or Playwright (TBD) | Browser automation; deferred if setup delayed |
| **API testing** | curl + pytest | Manual curl or automated via requests library |
| **Database** | PostgreSQL 16 (isolated test DB) | Same as production; no mocking |
| **Email mock** | MailTrap (free tier) or mock SMTP | Avoid real email in tests |
| **Performance** | Apache JMeter (if needed, v2) | Deferred to v2 load testing |
| **Bug tracking** | BUG_REPORT.md (CSV/markdown) | Structured; reviewed before release |

---

## 9. Sign-Off

> **QA Planning Complete:** 2026-05-16  
> **Next Phase:** 4_BUILD (BE + FE write code to match API_CONTRACT.md)  
> **When:** Phase 5 (TEST_AND_FIX), QA will execute these tests and produce TEST_REPORT.md + BUG_REPORT.md

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | QA | Created TEST_STRATEGY.md with coverage strategy, manual vs automated split, critical flows, risks, and tools |
