# Backend Implementation Plan — NestFi

**Version:** 1.0  
**Phase:** 3_IMPLEMENTATION_PLANNING  
**Owner:** BE  
**Last Updated:** 2026-05-16

---

## Executive Summary

This plan describes the backend implementation strategy for NestFi MVP (v1). Backend is responsible for:
- FastAPI REST API (async Python web framework)
- SQLAlchemy ORM with Alembic migrations (PostgreSQL 16)
- JWT authentication and RBAC authorization
- Core modules: auth, users, families, transactions, categories, admin
- Audit logging and soft deletes

**Timeline estimate:** 5-7 days (parallel with FE); blocking gate is schema finalization + API contract approval (done).

---

## 1. Module Breakdown & Responsibilities

### 1.1 Auth Module (`app/services/auth_service.py`, `app/api/routes/auth.py`)

**Responsibility:** User authentication, token issuance, credential validation.

**Endpoints (v1):**
- `POST /auth/login` — email + password → JWT token + user profile
- `GET /auth/me` — return current user from token
- `POST /users/change-password` — update user password (authenticated)

**Key Classes & Functions:**
- `AuthService.login(email, password)` → validate credentials, hash check, return token
- `AuthService.issue_token(user_id, email, role)` → sign JWT (HS256, 24h expiry)
- `AuthService.verify_token(token)` → decode JWT, validate expiry, return sub (user_id)
- `get_current_user(token)` — FastAPI dependency for protected endpoints
- Password hashing via `passlib.context` (bcrypt)

**Database Tables:**
- `users` — id, email (UNIQUE), password_hash, full_name, role, is_active, created_at, updated_at

**Security Considerations:**
- Passwords hashed with bcrypt (cost factor 12)
- JWT secret stored in env var `JWT_SECRET`
- Tokens expire in 24 hours (refresh endpoint deferred to v2)
- Rate limiting on login endpoint (deferred to v2)

---

### 1.2 Users Module (`app/models/user.py`, `app/schemas/user.py`, `app/crud/user.py`, `app/api/routes/users.py`)

**Responsibility:** User account management, profile operations.

**Endpoints (v1):**
- `GET /users/me` — authenticated user profile
- `POST /users/change-password` — update password

**Key Classes:**
- `User` (SQLAlchemy model)
  - id (PK), email (UNIQUE), password_hash, full_name, role (superadmin|owner|member), is_active, created_at, updated_at
  - Relationships: families (via FamilyMember), transactions

- `UserSchema` (Pydantic)
  - Request: email, password, full_name
  - Response: id, email, full_name, role, created_at

- `CRUD.get_user_by_email(db, email)` → User or None
- `CRUD.get_user_by_id(db, user_id)` → User or None
- `CRUD.create_user(db, email, password_hash, full_name, role)` → User

**Database Constraints:**
- email UNIQUE
- Check: is_active IN (TRUE, FALSE)
- Index on email (query performance)

**Authorization Rules:**
- Users can view/edit their own profile
- Superadmin can view any user profile

---

### 1.3 Families Module (`app/models/family.py`, `app/schemas/family.py`, `app/crud/family.py`, `app/api/routes/families.py`)

**Responsibility:** Family lifecycle, member management, invitations.

**Endpoints (v1):**
- `GET /families` — list families for authenticated user
- `GET /families/{id}` — family details
- `POST /families` (superadmin only) — create family + invite owner
- `PUT /families/{id}` (owner only) — update family settings
- `GET /families/{id}/members` — list family members
- `POST /families/{id}/members` (owner only) — invite member
- `DELETE /families/{id}/members/{member_id}` (owner only) — remove member

**Key Classes:**

**`Family` (SQLAlchemy model)**
- id (PK), name, description, currency (default USD), created_by_user_id (FK), created_at, updated_at
- Relationships: family_members, transactions, categories, invitations

**`FamilyMember` (SQLAlchemy model)**
- id (PK), family_id (FK), user_id (FK, nullable for pending), role (owner|member|view_only), status (active|pending|declined), joined_at, created_at, updated_at
- Constraints: (family_id, user_id) UNIQUE (when user_id not NULL)
- Relationships: user, family

**`Invitation` (SQLAlchemy model)**
- id (PK), email, family_id (FK), token (UNIQUE, UUID), invited_by_user_id (FK), status (pending|accepted|declined), expires_at (now + 30 days), created_at, updated_at
- Relationships: family, invited_by_user

**`FamilySchema` (Pydantic)**
- Request: name, description, owner_email (for create by superadmin)
- Response: id, name, description, currency, role (of current user), member_count, created_at

**`FamilyMemberSchema` (Pydantic)**
- Response: id, user_id, email, full_name, role, status, joined_at, expires_at (if pending)

**`InvitationSchema` (Pydantic)**
- Response: id, email, family_id, role, status, expires_at, invitation_sent

**CRUD Operations:**
- `CRUD.create_family(db, name, description, currency, created_by_user_id)` → Family
- `CRUD.get_user_families(db, user_id)` → list of Family (via FamilyMember)
- `CRUD.invite_member(db, family_id, email, role, invited_by_user_id)` → Invitation
- `CRUD.accept_invitation(db, token, user_id)` → FamilyMember (create if new user)
- `CRUD.remove_member(db, family_id, member_id)` → FamilyMember (soft/hard delete)

**Business Logic (`FamilyService`):**
- `invite_member(family_id, email, role, current_user)` → create invitation + send email
- `accept_invitation(token, user_id_or_email, password)` → handle new/existing user signup
- `get_family_members(family_id, user_id)` → verify member, return list
- `remove_member(family_id, member_id, current_user)` → verify owner, remove

**Email Service Integration:**
- Invitation emails sent via SMTP (configured in env)
- Template: "You've been invited to <FamilyName>. Click: <base_url>/invitations/<token>"
- Retry logic (deferred to v2)

**Authorization Rules:**
- User can only view families they're members of
- Only owner can invite/remove members
- Only superadmin can create families

---

### 1.4 Transactions Module (`app/models/transaction.py`, `app/schemas/transaction.py`, `app/crud/transaction.py`, `app/api/routes/transactions.py`)

**Responsibility:** Transaction logging, filtering, editing, soft deletion.

**Endpoints (v1):**
- `GET /families/{id}/transactions` (with pagination, filters) — list transactions
- `POST /families/{id}/transactions` — create transaction
- `PUT /families/{id}/transactions/{txn_id}` — edit transaction (author or owner)
- `DELETE /families/{id}/transactions/{txn_id}` — soft delete (author or owner)

**Key Classes:**

**`Transaction` (SQLAlchemy model)**
- id (PK), family_id (FK), user_id (FK, author), category_id (FK), type (income|expense|cash_withdrawal), amount (decimal, > 0), description (optional), transaction_date (date), created_at, updated_at, deleted_at (nullable, for soft delete), deleted_by (FK, nullable)
- Constraints: amount > 0, (family_id, category_id, type) — implicit (no explicit constraint, but enforced in service layer)
- Indexes: (family_id, deleted_at), (family_id, transaction_date), (category_id)
- Relationships: family, user (author), category

**`TransactionSchema` (Pydantic)**
- Request: category_id, type, amount, description (optional), transaction_date
- Response: id, family_id, user_id, user_name, category_id, category_name, type, amount, description, transaction_date, created_at, updated_at

**CRUD Operations:**
- `CRUD.create_transaction(db, family_id, user_id, category_id, type, amount, description, transaction_date)` → Transaction
- `CRUD.get_transactions(db, family_id, skip, limit, filters={category_id, member_id, type, date_from, date_to}, sort_by, sort_order)` → list of Transaction (excluding deleted)
- `CRUD.get_transaction(db, txn_id, family_id)` → Transaction or 404
- `CRUD.update_transaction(db, txn_id, updates)` → Transaction (audit trail)
- `CRUD.soft_delete_transaction(db, txn_id, deleted_by_user_id)` → mark deleted_at, deleted_by

**Business Logic (`TransactionService`):**
- `create_transaction(family_id, user_id, category_id, type, amount, ...)` → validate category belongs to family, validate amount > 0, create + audit
- `list_transactions(family_id, user_id, ...)` → verify user is member, apply filters, return paginated
- `update_transaction(txn_id, family_id, user_id, updates)` → verify author/owner, validate updates, apply + audit
- `delete_transaction(txn_id, family_id, user_id)` → verify author/owner, soft delete + audit

**Filtering:**
- category_id, member_id, type, date_from, date_to, sort_by (date|amount), sort_order (asc|desc)
- Pagination: skip, limit (default 30, max 100)

**Audit Logging:**
- Every create/update/delete logged to `audit_logs` table
- Records: user_id, entity_type=transaction, entity_id, action, old_values (JSON), new_values (JSON), timestamp

**Authorization Rules:**
- Only family members can view/create transactions
- Member can edit/delete only own transactions
- Owner can edit/delete any transaction in family

---

### 1.5 Categories Module (`app/models/category.py`, `app/schemas/category.py`, `app/crud/category.py`, `app/api/routes/categories.py`)

**Responsibility:** Category lifecycle, defaults, archival.

**Endpoints (v1):**
- `GET /families/{id}/categories` (with optional filters) — list categories
- `POST /families/{id}/categories` (owner only) — create category
- `PUT /families/{id}/categories/{cat_id}` (owner only) — edit category
- `DELETE /families/{id}/categories/{cat_id}` (owner only) — archive category

**Key Classes:**

**`Category` (SQLAlchemy model)**
- id (PK), family_id (FK), type (income|expense|investment), name, description (optional), color (hex, e.g., #FF5733), icon (optional, e.g., dollar-sign), is_default (boolean), is_active (boolean), created_at, updated_at
- Constraints: (family_id, name, type) UNIQUE, is_active IN (TRUE, FALSE)
- Indexes: (family_id, is_active), (family_id, type)
- Relationships: family, transactions

**`CategorySchema` (Pydantic)**
- Request: name, type, description (optional), color, icon
- Response: id, family_id, name, type, description, color, icon, is_default, is_active, transaction_count, created_at

**CRUD Operations:**
- `CRUD.create_category(db, family_id, type, name, description, color, icon, is_default)` → Category
- `CRUD.get_categories(db, family_id, type_filter=None, active_only=False)` → list of Category
- `CRUD.get_category(db, cat_id, family_id)` → Category or 404
- `CRUD.update_category(db, cat_id, updates)` → Category
- `CRUD.deactivate_category(db, cat_id)` → mark is_active=False

**Business Logic (`CategoryService`):**
- `create_family_categories(family_id)` — seed default categories on family creation
  - Income defaults: Salary, Bonus, Freelance, Interest, Other Income
  - Expense defaults: Groceries, Utilities, Entertainment, Transport, Cash Withdrawal, Other Expense
  - Investment defaults: Stock Portfolio, Retirement, Crypto, Other Investment
- `create_custom_category(family_id, user_id, type, name, ...)` → verify owner, validate unique name, create
- `update_category(cat_id, family_id, user_id, updates)` → verify owner, forbid type change, apply
- `deactivate_category(cat_id, family_id, user_id)` → verify owner, archive (preserves transaction history)

**Archival:**
- Soft deactivation: set is_active=FALSE
- Existing transactions retain reference; they still display correctly
- Archived categories no longer appear in transaction form dropdowns (FE filters)

**Authorization Rules:**
- Only owner can create/edit/archive categories
- Members can view categories (for transaction logging)

---

### 1.6 Admin Module (`app/api/routes/admin.py`)

**Responsibility:** Superadmin-only operations.

**Endpoints (v1):**
- `POST /admin/families` (superadmin only) — create family + invite owner

**Key Functions:**
- `create_family_with_owner(name, description, owner_email, currency)` → Family + Invitation + email sent
- Validates superadmin role
- Creates family, invites owner, seeds default categories
- Returns family_id, invitation status

**Authorization Rules:**
- Only superadmin (role='superadmin') can access

---

### 1.7 Analytics Module (`app/services/analytics_service.py`, `app/api/routes/analytics.py`)

**Responsibility:** Dashboard summary and trends (v1 basic, v2 advanced).

**Endpoints (v1):**
- `GET /families/{id}/analytics/summary` — monthly/yearly overview (income, expense, net, rate, breakdown)
- `GET /families/{id}/analytics/trends` — 6-month trend data

**Key Functions:**
- `get_summary(family_id, period='month', date=today)` → {total_income, total_expense, net_savings, rate, category_breakdown}
- `get_trends(family_id, months=6)` → [{month, income, expense, net}, ...]

**Database Queries:**
- Aggregations via SQLAlchemy `.group_by()` + `.func.sum()`
- Exclude deleted transactions (WHERE deleted_at IS NULL)

**Performance:**
- Index on (family_id, transaction_date) helps query speed
- Cache results in Redis (deferred to v2 if needed)

---

## 2. ORM & Migration Strategy

### 2.1 SQLAlchemy Setup

**Version:** SQLAlchemy 2.0 (modern async support)

**Location:** `backend/app/models/base.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

Base = declarative_base()

# Database URL from env: postgresql://user:pass@localhost:5432/nestfi
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)  # or async_engine for AsyncSession
SessionLocal = sessionmaker(bind=engine, class_=Session)
```

**Model Inheritance:**
- All models inherit from `Base`
- Common fields (id, created_at, updated_at) in mixin

```python
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime

class TimestampMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### 2.2 Alembic Migration Setup

**Version:** Alembic (SQLAlchemy-native migration tool)

**Directory Structure:**
```
backend/
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_audit_logs.py
│   │   └── ... (future migrations)
│   ├── env.py               (migration runtime config)
│   ├── script.py.mako       (migration template)
│   └── alembic.ini          (Alembic config)
```

**Initialization & Usage:**
```bash
# Initialize Alembic (one-time)
alembic init alembic

# Generate migration from model changes
alembic revision --autogenerate -m "initial schema"

# Apply migration to database
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

**Naming Convention:**
- Migration files: `001_schema_description.py`, `002_add_feature.py`, etc.
- Semver-like progression for clarity
- Each migration idempotent (can run multiple times safely)

**Startup Migration:**
- FastAPI app runs `alembic upgrade head` on startup (in `app/main.py`)
- Ensures schema matches code before serving requests

**Deferred Migrations Strategy (v2+):**
- Blue-green deployment: migrate schema, then deploy code
- Backward-compatible migrations (add columns, deferred removals)
- No zero-downtime required for v1 (small user base)

---

## 3. API Endpoint Priorities

### 3.1 Phase 1 (Core — must ship in v1)

**Must-have endpoints for MVP:**

| Module | Endpoint | Method | Priority | Est. Effort |
|---|---|---|---|---|
| Auth | `/auth/login` | POST | P0 | 2h |
| Auth | `/auth/me` | GET | P0 | 1h |
| Users | `/users/change-password` | POST | P0 | 2h |
| Families | `GET /families` | GET | P0 | 2h |
| Families | `/families/{id}` | GET | P0 | 1h |
| Families | `/families` (superadmin) | POST | P0 | 3h |
| Families | `/families/{id}/members` | GET | P0 | 2h |
| Families | `/families/{id}/members` | POST | P0 | 3h |
| Families | `/families/{id}/members/{member_id}` | DELETE | P0 | 2h |
| Families | `/invitations/{token}/accept` | POST | P0 | 3h |
| Families | `/invitations/{token}/decline` | POST | P0 | 2h |
| Transactions | `GET /families/{id}/transactions` | GET | P0 | 3h |
| Transactions | `POST /families/{id}/transactions` | POST | P0 | 3h |
| Transactions | `PUT /families/{id}/transactions/{txn_id}` | PUT | P0 | 2h |
| Transactions | `DELETE /families/{id}/transactions/{txn_id}` | DELETE | P0 | 2h |
| Categories | `GET /families/{id}/categories` | GET | P0 | 2h |
| Categories | `POST /families/{id}/categories` | POST | P0 | 2h |
| Categories | `PUT /families/{id}/categories/{cat_id}` | PUT | P0 | 2h |
| Categories | `DELETE /families/{id}/categories/{cat_id}` | DELETE | P0 | 2h |
| Analytics | `GET /families/{id}/analytics/summary` | GET | P0 | 3h |
| Analytics | `GET /families/{id}/analytics/trends` | GET | P0 | 3h |
| Health | `/` | GET | P0 | 0.5h |

**Estimated P0 total:** ~50 hours (6-7 days, 1 FTE, with parallel FE work)

---

### 3.2 Phase 2 (Deferred to v2)

| Endpoint | Reason | Est. Effort |
|---|---|---|
| `PUT /families/{id}` | Update family settings | 2h |
| `POST /auth/register` | Self-signup (deferred; superadmin creates initially) | 2h |
| `POST /auth/refresh` | Token refresh | 1h |
| Rate limiting middleware | Not needed for v1 low traffic | 2h |
| `POST /families/{id}/export` | CSV/PDF export | 4h |
| `/admin/users` | User management (view/edit/ban) | 3h |

---

## 4. Dependencies & Risks

### 4.1 External Dependencies

| Dependency | Purpose | Version | Risk Level |
|---|---|---|---|
| FastAPI | REST framework | 0.100+ | Low (mature, stable) |
| SQLAlchemy | ORM | 2.0+ | Low (mature, type-safe) |
| Alembic | Migrations | 1.11+ | Low (standard tool) |
| Pydantic | Validation | 2.0+ | Low (FastAPI default) |
| PyJWT | JWT signing | 2.8+ | Low (standard) |
| passlib + bcrypt | Password hashing | 1.7.4 + 4.0+ | Low (industry standard) |
| python-multipart | Form parsing | 0.0.5+ | Low (FastAPI req) |
| psycopg2 | PostgreSQL driver | 2.9+ | Low (mature) |
| python-dotenv | Env var loading | 1.0+ | Low (simple) |
| uvicorn | ASGI server | 0.23+ | Low (standard) |
| pytest | Testing framework | 7.4+ | Low (standard) |
| httpx | HTTP client for tests | 0.24+ | Low (standard) |

---

### 4.2 Internal Dependencies (Upstream Tasks)

**All resolved (Phase 1 & 2 outputs exist):**
- ✅ TECH_STACK.md (confirmed by user)
- ✅ SOLUTION_ARCHITECTURE.md (reviewed by SA)
- ✅ API_CONTRACT.md (approved by SA)
- ✅ USER_STORIES.md (BA complete)

**BE can proceed immediately after FE starts (parallel work).**

---

### 4.3 Identified Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Schema design changes mid-build** | Medium | High | Finalize schema early, test migrations, allow 2-3 iter days |
| **JWT secret not configured** | Low | Critical | .env.example includes JWT_SECRET; startup validation |
| **Database connection timeout** | Low | High | Retry logic in SessionLocal, health check endpoint |
| **Email service outage** | Low | Medium | Log failures, retry in background (v2: queue); warn user if invite fails |
| **Pagination performance (1000+ txns)** | Low | Medium | Index on (family_id, transaction_date), pagination limits, cache (v2) |
| **Concurrent transaction edits** | Low | Medium | Optimistic locking via `updated_at` timestamp (detect conflicts) |
| **Soft-delete queries** | Low | Medium | Always exclude `deleted_at IS NOT NULL`; query tests verify |
| **Frontend API client misconfiguration** | Medium | Medium | Mock API in FE tests, verify CORS headers |
| **Role-based access control bypass** | Low | Critical | Comprehensive tests for each endpoint + role, code review |

---

### 4.4 Mitigation & Testing Strategy

**Unit Tests:**
- CRUD operations (create, read, update, delete for each model)
- Business logic (auth validation, category defaults, etc.)
- Schema validation (Pydantic schemas)
- Utilities (JWT signing, password hashing)

**Integration Tests:**
- Auth flow (login → token → protected endpoint)
- Family creation + member invitation + acceptance flow
- Transaction lifecycle (create, edit, delete)
- Soft-delete behavior (deleted txns hidden, audit logged)
- Permission checks (member cannot edit other's txn, etc.)
- Pagination + filtering

**Database Tests:**
- Migration idempotence (run twice, same result)
- Foreign key constraints (cascade deletes work)
- Unique constraints (no duplicate emails, etc.)
- Indexes exist and are used (query plans)

**API Tests:**
- All endpoints return expected status codes (200, 201, 400, 403, 404)
- Error messages are clear (not database stack traces)
- CORS headers present
- OpenAPI/Swagger docs generated correctly

---

## 5. Implementation Timeline

### Phase 3: Implementation Planning (current)
- **Duration:** 1 day
- **Deliverable:** BE_PLAN.md (this document)
- **Next:** Orchestrator advances to Phase 4 (Build)

### Phase 4: Build (BE + FE parallel)
- **Duration:** 6-7 days
- **BE Focus:**
  - Day 1: Models, schemas, CRUD base classes (auth, users, families)
  - Day 2: Auth routes, login/JWT (integration test)
  - Day 3: Family routes, invitations, membership (integration test)
  - Day 4: Transaction routes, CRUD, soft delete, pagination (integration test)
  - Day 5: Category routes, defaults, archival (integration test)
  - Day 6: Analytics routes, aggregations (integration test)
  - Day 7: Admin routes, health check, Dockerfile, `.env.example`, integration tests
- **Deliverable:** `backend/` source code + tests
- **Gate:** All unit + integration tests pass; API docs accessible

### Phase 5: Test & Fix (QA)
- **Duration:** 2-3 days
- **QA Task:** Run TEST_PLAN.md against API; report bugs
- **BE Task:** Fix bugs, retest, finalize docs
- **Gate:** TEST_REPORT.md has `VERDICT: PASS`

### Phase 6: Delivery (DELIVERY + BE)
- **Duration:** 1 day
- **Task:** Docker build, docker-compose up -d, verify endpoints, seed test data
- **Deliverable:** `docs/delivery/RUNNING_APP.md` with URL

---

## 6. Code Organization & Standards

### 6.1 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app, startup hooks
│   ├── config.py                    # Settings (env-based)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base class, TimestampMixin
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   └── audit.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   └── common.py                # ErrorResponse, PaginationParams
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base CRUD class
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── transaction.py
│   │   └── category.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── family_service.py
│   │   ├── transaction_service.py
│   │   ├── category_service.py
│   │   ├── email_service.py
│   │   └── analytics_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py              # Hash, verify password
│   │   ├── exceptions.py            # Custom exceptions
│   │   └── email.py                 # SMTP client
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py          # get_current_user, get_db, etc.
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── families.py
│   │       ├── transactions.py
│   │       ├── categories.py
│   │       ├── analytics.py
│   │       ├── admin.py
│   │       └── health.py
│   └── static/
│       └── uploads/                 # User-uploaded images (future CDN)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures, test DB
│   ├── test_auth.py
│   ├── test_families.py
│   ├── test_transactions.py
│   ├── test_categories.py
│   └── test_admin.py
├── alembic/                         # (initialized separately)
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

### 6.2 Code Standards

**Imports:**
- Order: stdlib, third-party, local
- Type hints on all functions (PEP 484)
- Docstrings on public functions (one-line summary; examples if non-obvious)

**Naming:**
- Functions/variables: snake_case
- Classes/models: PascalCase
- Constants: UPPER_SNAKE_CASE
- Database columns: snake_case
- API fields: snake_case (JSON serialized as-is)

**Error Handling:**
- Raise `HTTPException(status_code=..., detail="...")` in endpoints
- Log errors with timestamps and context
- Never expose database errors to clients (sanitize messages)

**Testing:**
- All CRUD functions have unit tests
- All endpoints have integration tests
- ~70% code coverage target (routes can be lower)
- Test fixtures for common objects (user, family, transaction)

---

## 7. Handoff & Questions

**Clarifications requested from SA/BA (if any arise during build):**
- If API contract ambiguity → route SA a clarification task
- If business rule ambiguity → route BA a clarification task

**Ready to start:** Phase 4 (Build) once Orchestrator advances.

**Blockers:** None identified. All prerequisites met.

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | BE | Created BE_PLAN.md with module breakdown, ORM strategy, endpoint priorities, dependencies, and risks |
