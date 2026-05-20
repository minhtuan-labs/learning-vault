# Solution Architecture — NestFi

## Overview

NestFi is a web-based family financial management system. The architecture is a **synchronous monolith** (v1) with clear separation between frontend (Next.js) and backend (FastAPI) via REST APIs. Both are containerized and orchestrated with Docker Compose for local development.

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser (HTTP/S)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
    ┌─────▼──────────┐          ┌──────▼──────────┐
    │  Frontend      │          │  Backend       │
    │  Next.js 15    │◄────────►│  FastAPI       │
    │  Port 3000     │  REST    │  Port 8000     │
    │                │  JSON    │                │
    │ ├─ Pages       │          │ ├─ Auth routes │
    │ ├─ Components  │          │ ├─ Family APIs │
    │ ├─ Forms       │          │ ├─ Account APIs│
    │ ├─ Charts      │          │ ├─ Category    │
    │ └─ State mgmt  │          │ ├─ Transaction │
    │    (TBD)       │          │ └─ Analytics   │
    └────────────────┘          └──────┬─────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
    ┌────▼──────────────┐     ┌────────▼──────────┐     ┌───────────▼────┐
    │   PostgreSQL 16   │     │   Redis (opt)     │     │  File System   │
    │   Port 5432       │     │   Port 6379       │     │  (images, etc) │
    │                   │     │                   │     │                │
    │ ├─ users          │     │ ├─ Sessions (opt) │     │ ├─ Uploads     │
    │ ├─ families       │     │ ├─ Cache (TBD)    │     │ └─ Static      │
    │ ├─ members        │     │ └─ Jobs (future)  │     └────────────────┘
    │ ├─ accounts       │     │                   │
    │ ├─ categories     │     │                   │
    │ ├─ transactions   │     │                   │
    │ ├─ transaction    │     │                   │
    │ │ _edits          │     │                   │
    │ └─ invitations    │     │                   │
    └───────────────────┘     └───────────────────┘
```

## Key Design Decisions

### 1. Synchronous Request-Response (Not Event-Driven)

For v1, all operations are **synchronous**:
- User action (e.g., record transaction) → API request → DB update → UI updates
- No message queue, no eventual consistency
- Simpler debugging, consistent state, acceptable for household-scale usage

**Future:** Event-driven queues for multi-family notifications, background analytics jobs (v2+).

### 2. Database-Centric Auth + Sessions

- **Web:** Session cookie (httpOnly, Secure flags) + server-side session store in Postgres/Redis
- **API:** JWT Bearer tokens for programmatic access (mobile, integrations)
- Superadmin account seeded at deploy; password-reset flow via email tokens

### 3. Family-Scoped Data Isolation

All data (accounts, transactions, members) is scoped to a family. No global queries; all queries filtered by `family_id` at API boundary.

**Authorization:** Middleware checks `family_id` in request context against user's `family_memberships`.

### 4. Immutable Transactions with Edit Tracking

- Transactions are recorded and can be edited by any family member
- Edit history is tracked in `transaction_edits` table (who, when, before/after snapshot)
- Soft-delete (disable) via `is_enabled` flag; only owner can hard-delete
- Balance rollup is computed from non-disabled transactions

### 5. No Person-Level Tracking

- All transactions are account-centric (not person-centric)
- No bill-splitting or person-level ledgers in v1
- All family members have equal visibility and edit rights

## System Boundaries

### Frontend Responsibilities

- **Authentication:** Login/password reset forms, session state
- **Presentation:** Dashboard, account views, transaction forms, charts
- **Validation:** Client-side form validation for UX
- **State Management:** TBD (React Context, Zustand, Redux Lite, or none)
- **Offline:** None in v1 (online-only assumption)

### Backend Responsibilities

- **Authorization:** Enforce family_id context, role-based access (owner vs. member)
- **Data Validation:** Enforce business rules (amounts > 0, dates, category membership)
- **Persistence:** PostgreSQL schema, migrations, data integrity
- **API Contract:** REST endpoints with OpenAPI spec
- **Email:** Invitation and password-reset tokens (mock in v1)

## Database Schema Outline

### Core Tables

1. **users** — App-wide users
   - `id, email, password_hash, created_at, updated_at`

2. **families** — Household groupings
   - `id, name, owner_id (fk users), created_at, updated_at`

3. **family_memberships** — Users ↔ Families
   - `id, user_id, family_id, role (owner|member), status (active|disabled), joined_at`

4. **accounts** — Bank/investment accounts within a family
   - `id, family_id, name, type (bank|savings|investment|cash), balance_cents, currency, created_at, updated_at`

5. **categories** — Income/Expense/Investment categories per family
   - `id, family_id, name, type (income|expense|investment), is_default, created_at`

6. **transactions** — Financial records
   - `id, account_id, category_id, amount_cents, direction (in|out), date, description, creator_id, is_enabled, created_at, updated_at`

7. **transaction_edits** — Audit trail for changes
   - `id, transaction_id, editor_id, change_summary, before_snapshot, after_snapshot, edited_at`

8. **invitations** — Email invites for users and family members
   - `id, email, family_id (nullable for user invites), token, expires_at, claimed_at`

(Additional tables for sessions if using DB-backed sessions, auth tokens, etc.)

## API Layer

### Authentication Endpoints

```
POST   /api/v1/auth/register          — Create user account
POST   /api/v1/auth/login             — Create session
POST   /api/v1/auth/logout            — Destroy session
POST   /api/v1/auth/password-reset    — Request reset token
PUT    /api/v1/auth/password          — Set new password
```

### Family Management

```
GET    /api/v1/families               — List user's families
POST   /api/v1/families               — Create new family (owner)
GET    /api/v1/families/{id}          — Get family details
PUT    /api/v1/families/{id}          — Update family (owner)

GET    /api/v1/families/{id}/members  — List members + pending invites
POST   /api/v1/families/{id}/members  — Invite member (owner)
PATCH  /api/v1/families/{id}/members/{user_id} — Disable/enable (owner)
```

### Accounts

```
GET    /api/v1/families/{id}/accounts              — List accounts
POST   /api/v1/families/{id}/accounts              — Create account
GET    /api/v1/families/{id}/accounts/{account_id} — Get account details
PUT    /api/v1/families/{id}/accounts/{account_id} — Update account
```

### Categories

```
GET    /api/v1/families/{id}/categories           — List categories
POST   /api/v1/families/{id}/categories           — Create custom category (owner)
```

### Transactions

```
GET    /api/v1/families/{id}/accounts/{account_id}/transactions    — List
POST   /api/v1/families/{id}/accounts/{account_id}/transactions    — Create
GET    /api/v1/families/{id}/accounts/{account_id}/transactions/{tx_id} — Detail + edit history
PUT    /api/v1/families/{id}/accounts/{account_id}/transactions/{tx_id} — Update
PATCH  /api/v1/families/{id}/accounts/{account_id}/transactions/{tx_id} — Disable/enable

DELETE /api/v1/families/{id}/accounts/{account_id}/transactions/{tx_id} — Hard delete (owner only)
```

### Analytics (TBD)

```
GET    /api/v1/families/{id}/dashboard            — Summary (totals, recent txns)
GET    /api/v1/families/{id}/reports/expenses     — Expense breakdown by category
GET    /api/v1/families/{id}/reports/income       — Income breakdown
GET    /api/v1/families/{id}/reports/trends       — Income vs. expense over time
```

## Deployment Topology (v1)

### Local Development

```
docker-compose up -d
→ Frontend:  http://localhost:3000
→ Backend:   http://localhost:8000
→ Postgres:  localhost:5432 (internal)
→ Redis:     localhost:6379 (optional, internal)
```

### Production v1 (TBD)

- Single Docker Compose or managed container service (Render, Railway, Fly.io, AWS ECS)
- RDS/managed Postgres for database
- Optional managed Redis or Valkey for session store
- Reverse proxy (nginx, Caddy) for SSL termination, CORS, static file serving

## Security Model

### Authentication

- Superadmin account created at first deploy with default password
- Invitations use secure tokens (email verification)
- Password reset tokens expire after 1 hour
- Sessions invalidate on logout or timeout (TBD: 30 min default)

### Authorization

- **API Boundary:** Every request checked for valid session/JWT + family_id
- **Family Scope:** User can only access families they're a member of
- **Role Checks:** Owner-only actions (delete transaction, manage members) enforced server-side

### Data Protection

- Passwords hashed with bcrypt (never logged)
- Session tokens (JWT/cookies) marked httpOnly + Secure in production
- Sensitive fields (password, tokens) excluded from logs
- Audit trail (transaction_edits) for compliance

## Scalability Considerations (v2+)

1. **Database:** Indexes on `family_id`, `user_id`, `created_at`; connection pooling
2. **Caching:** Redis for frequently-accessed families, dashboard metrics
3. **Background Jobs:** Message queue (Celery, RQ) for bulk exports, email campaigns
4. **Async API:** WebSocket support for real-time multi-user updates
5. **Search:** Elasticsearch or Meilisearch for transaction search (v2+)

## Known Constraints & TBDs

1. **Image Storage:** No media handling in v1; images sourced by team
2. **Reporting Export:** Deferred to v1.1 (marked as stretch goal)
3. **Session Timeout:** Duration TBD (default assumption: 30 minutes)
4. **Mobile:** Not in v1; API designed for future mobile client
5. **Multi-Tenancy:** Not planned; single org instance per deployment

---

**Phase:** 1_SOLUTION_DESIGN  
**Next:** BE and FE review this doc, confirm API contract specifics, write detailed implementation plans.