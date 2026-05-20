# BE Implementation Plan — NestFi v1.0

**Phase:** 3_IMPLEMENTATION_PLANNING  
**Status:** DRAFT → Ready for Phase 4_BUILD  
**Last Updated:** 2026-05-16  

---

## Overview

This document outlines the backend implementation strategy for NestFi v1.0, organized by feature group, dependencies, and sequencing. All architecture, API contracts, and tech stack have been confirmed in upstream docs; this plan breaks down the work into implementable tasks.

---

## Technology Stack (Confirmed)

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.11+ | Type safety with Pydantic, fast dev iteration |
| **Framework** | FastAPI | Built-in async, OpenAPI auto-docs, Starlette foundation |
| **Database** | PostgreSQL 16 | ACID compliance, JSON support, battle-tested |
| **ORM** | SQLAlchemy 2.0 + Alembic | Migrations, type hints, mature ecosystem |
| **Validation** | Pydantic v2 | Request/response serialization, type safety |
| **Auth** | Session cookies + JWT | Cookies for web, JWT for API clients |
| **Password Hashing** | bcrypt (via passlib) | Industry standard, slow by design |
| **Testing** | pytest + pytest-asyncio | Async support, fixture management, community standard |
| **Server** | Uvicorn (FastAPI default) | ASGI-compliant, production-ready |
| **Containerization** | Docker + Docker Compose | Local dev consistency, production portability |

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + startup
│   ├── config.py               # Settings (env-based)
│   ├── database.py             # SQLAlchemy setup
│   ├── dependencies.py         # FastAPI dependency injection
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── invitation.py
│   │   └── session.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── account.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   └── pagination.py
│   ├── routes/                 # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── families.py
│   │   ├── accounts.py
│   │   ├── categories.py
│   │   ├── transactions.py
│   │   └── analytics.py (stretch)
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── family_service.py
│   │   ├── auth_service.py
│   │   ├── account_service.py
│   │   ├── category_service.py
│   │   ├── transaction_service.py
│   │   └── email_service.py (stub)
│   ├── middleware/             # Auth, logging, error handling
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── error_handler.py
│   └── utils/                  # Helpers (hashing, tokens, etc.)
│       ├── __init__.py
│       ├── security.py         # bcrypt, JWT, session handling
│       ├── email.py            # Email templates (mock v1)
│       └── validators.py       # Custom validation logic
├── migrations/                 # Alembic migration scripts
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── tests/                      # Pytest test suite
│   ├── __init__.py
│   ├── conftest.py             # Fixtures, DB setup
│   ├── test_auth.py
│   ├── test_families.py
│   ├── test_accounts.py
│   ├── test_categories.py
│   ├── test_transactions.py
│   └── integration/            # End-to-end API tests
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition (DELIVERY owns)
├── .env.example               # Environment template
└── README.md                  # Backend setup guide
```

---

## Implementation Phases

### Phase 1: Project Setup & Database (2-3 days)

**Tasks:**
1. Initialize FastAPI project structure
2. Set up Alembic migrations framework
3. Create SQLAlchemy models for: User, Family, FamilyMembership, Account, Category, Transaction, TransactionEdit, Invitation
4. Write initial migration: `initial_schema`
5. Implement database connection pooling
6. Create seed script for default categories and superadmin account
7. Write conftest.py with test DB fixture and session handling

**Dependencies:** None  
**Blockers:** None

---

### Phase 2: Authentication & Sessions (3-4 days)

**Tasks:**
1. POST /auth/register — User registration with password hashing
2. POST /auth/login — Session cookie + JWT token creation
3. POST /auth/logout — Session invalidation
4. POST /auth/request-password-reset — Token generation (mock email)
5. POST /auth/reset-password — Password update via token
6. Middleware: get_current_user() dependency for auth checks
7. Tests: 50+ pytest cases for auth flows and edge cases

**Dependencies:** Phase 1  
**Blockers:** None

---

### Phase 3: Family Management & Members (2-3 days)

**Tasks:**
1. GET /families — List user's families
2. POST /families — Create family (owner-only)
3. GET /families/{id} — Get family details
4. PUT /families/{id} — Update family name (owner-only)
5. GET /families/{id}/members — List active + pending members
6. POST /families/{id}/members — Invite member (owner-only)
7. POST /families/{id}/members/confirm — Accept invitation
8. PATCH /families/{id}/members/{user_id} — Disable/enable member (owner-only)
9. Tests: 40+ cases for family ops, role checks, invitations

**Dependencies:** Phase 2  
**Blockers:** None

---

### Phase 4: Accounts & Categories (1-2 days)

**Tasks:**
1. GET /families/{id}/accounts — List accounts with balance
2. POST /families/{id}/accounts — Create account
3. GET /families/{id}/accounts/{account_id} — Get account detail
4. PUT /families/{id}/accounts/{account_id} — Update account
5. GET /families/{id}/categories — List categories
6. POST /families/{id}/categories — Create custom category (owner-only)
7. Tests: 25+ cases for CRUD, balance calculation, permissions

**Dependencies:** Phase 3  
**Blockers:** None

---

### Phase 5: Transactions & Edit Tracking (3-4 days)

**Tasks:**
1. GET /families/{id}/accounts/{account_id}/transactions — List with pagination & filters
2. POST /families/{id}/accounts/{account_id}/transactions — Create transaction
3. GET /families/{id}/accounts/{account_id}/transactions/{tx_id} — Detail + edit history
4. PUT /families/{id}/accounts/{account_id}/transactions/{tx_id} — Update (creates audit entry)
5. PATCH /families/{id}/accounts/{account_id}/transactions/{tx_id} — Disable/enable
6. DELETE /families/{id}/accounts/{account_id}/transactions/{tx_id} — Hard delete (owner-only)
7. Tests: 50+ cases for lifecycle, audit trail, balance consistency

**Dependencies:** Phase 4  
**Blockers:** None

---

### Phase 6: Analytics & Dashboard (Stretch — 2-3 days)

**Tasks:**
1. GET /families/{id}/dashboard — Summary metrics (income, expense, net savings, accounts)
2. GET /families/{id}/reports/expenses — Category breakdown
3. GET /families/{id}/reports/income — Income breakdown
4. Tests: 20+ cases for aggregation, period filtering

**Dependencies:** Phase 5  
**Blockers:** None (defer if time-constrained)

---

## Task Sequencing

| Seq | Phase | Duration | Dependency |
|-----|-------|----------|-----------|
| 1 | Setup & DB | 2-3d | None |
| 2 | Auth | 3-4d | Phase 1 |
| 3 | Families | 2-3d | Phase 2 |
| 4 | Accounts | 1-2d | Phase 3 |
| 5 | Transactions | 3-4d | Phase 4 |
| 6 | Analytics | 2-3d | Phase 5 (optional) |

**Total Estimate:** 13-21 days (11-17 days for MVP)

---

## Cross-Functional Dependencies

### From SA
- ✅ Solution Architecture confirms FastAPI + PostgreSQL
- ✅ API Contract fully specified (all endpoints + schemas)
- ✅ Database schema outlined
- ✅ Family-scoped authorization pattern

### From BA
- ✅ 28 user stories with acceptance criteria
- ✅ Transaction edit tracking requirement
- ✅ Member roles and permissions
- ✅ Soft-delete vs. hard-delete rules

### For FE
- BE provides OpenAPI spec at GET /api/v1/docs
- Session cookies automatically handled by browsers
- Error responses follow standardized JSON format
- All /api/v1/families/** endpoints return consistent schemas

### For QA
- BE provides seed script for test data
- All endpoints match API_CONTRACT.md (status codes, schemas)
- Comprehensive test coverage for edge cases

### For DELIVERY
- BE code + tests must be production-ready
- Migrations must be idempotent
- .env.example documents all required vars
- Dockerfile ready for containerization

---

## Authorization Pattern

Every protected endpoint enforces family-scoped access:

```python
@router.get("/families/{family_id}/...")
async def endpoint(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify membership
    membership = check_family_membership(current_user, family_id, db)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # Owner-only checks (if needed)
    if is_owner_only and membership.role != "owner":
        raise HTTPException(status_code=403, detail="Owner-only action")
    
    # Proceed with business logic
```

---

## Testing Strategy

### Unit Tests
- Services layer: user creation, hashing, token generation, balance rollup
- 20+ tests per service module

### Integration Tests
- Auth flows (register → login → logout)
- Family CRUD + member invites
- Account + category operations
- Transaction lifecycle with edit history
- Authorization checks (403 on unauthorized)
- 40+ tests per route module

### End-to-End (QA-owned, BE-seeded)
- Multi-user scenarios
- Transaction consistency
- Audit trail completeness

---

## Deployment Checklist

- [ ] All MUST user stories implemented + passing
- [ ] OpenAPI spec available at GET /api/v1/docs
- [ ] Migrations tested on fresh DB
- [ ] Seed script works (superadmin + categories)
- [ ] .env.example documents all vars
- [ ] requirements.txt pinned to exact versions
- [ ] Test coverage ≥80% (routes), ≥90% (services)
- [ ] Error responses match API_CONTRACT.md

---

## Known Constraints (v1)

1. **Email:** Tokens printed to logs (mock service)
   - v2: Real SMTP / Sendgrid integration
2. **Session Timeout:** Manual logout only (no auto-timeout)
   - v2: Background job for idle session cleanup
3. **Caching:** None; direct DB queries
   - v2: Redis for frequently-accessed data
4. **Rate Limiting:** Not implemented
   - v2: SlowAPI for per-user/IP limits
5. **Multi-Currency:** Field exists; assume single currency per family
   - v2: Exchange rate service + conversion

---

## Success Criteria (Phase 4 Exit)

- [ ] Phases 1-5 complete
- [ ] 28 user stories tested
- [ ] 0 open CRITICAL/MAJOR bugs
- [ ] Test coverage ≥80%
- [ ] OpenAPI spec accurate
- [ ] Seed script + migrations runnable
- [ ] All endpoints match API_CONTRACT.md
- [ ] FE integration tested
- [ ] Ready for Phase 5_TEST_AND_FIX

---

**Prepared by:** BE Agent  
**Date:** 2026-05-16  
**Next Review:** Phase 4 gate completion
