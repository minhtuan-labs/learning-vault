# Architecture Decision Records

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** SA

This document captures key architectural decisions made during solution design. Each ADR follows the format: **Status**, **Context**, **Decision**, **Consequences**.

---

## ADR-0001: Python Monorepo (Dash + FastAPI) vs Multi-Language Microservices

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
NestFi MVP requires rapid iteration with minimal infrastructure overhead. Team is Python-first. Options:
1. Python monorepo (Dash frontend + FastAPI backend)
2. Separate Node.js/Next.js FE + Python BE (language split)
3. Microservices with multiple languages (Go, Rust, etc.)
4. Serverless (AWS Lambda, etc.)

**Decision:**  
**Python monorepo with Dash (Plotly) + FastAPI** in single codebase (`backend/` + `frontend/` folders).

**Rationale:**
- **Velocity:** No language context-switching; shared models, types, utilities
- **Simplicity:** One runtime (Python), one package manager (poetry/pip), one deployment unit (Docker)
- **Dash strength:** Interactive charts out-of-box (financial dashboards benefit)
- **Team fit:** Python expertise available; Dash has a lower learning curve than React+Next.js
- **Scalability path:** Stateless FastAPI + JWT auth allows horizontal scaling; Dash can be containerized independently later

**Consequences:**
- ✓ Faster development (no FE/BE language gap)
- ✓ Simpler deployment (single monorepo, one Docker Compose file)
- ✗ JavaScript ecosystem features (npm packages) unavailable; Tailwind is CSS-only solution
- ✗ Dash is less mature than React; fewer third-party component libraries
- **Future mitigation:** v2+ can migrate FE to React/Next.js if needed; REST API is clean boundary

**Links:**
- Dash documentation: https://dash.plotly.com/
- FastAPI: https://fastapi.tiangolo.com/

---

## ADR-0002: JWT Stateless Authentication vs Session-Based Auth

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
NestFi needs to authenticate users and manage families/permissions. Options:
1. JWT tokens (stateless)
2. Server-side sessions (session store + cookies)
3. OAuth / Third-party (Auth0, Supabase, etc.)

**Decision:**  
**JWT (JSON Web Tokens) with HS256** issued by `/auth/login` endpoint. Tokens expire in 24 hours.

**Rationale:**
- **Scalability:** Stateless tokens allow load-balanced backends without session affinity
- **Simplicity:** No session store needed (PostgreSQL-backed sessions would require additional infra)
- **REST-friendly:** JWT is standard for REST APIs; Dash frontend can store in localStorage
- **v1 constraint:** No cache layer (Redis) in v1; JWT avoids needing one for session lookup

**Consequences:**
- ✓ Horizontal scaling without session affinity
- ✓ No session store overhead
- ✓ Easy for mobile apps later (tokens in HTTP header)
- ✗ Token revocation is hard (requires blacklist or new expiration field)
- ✗ Token size increases with claims; may need careful payload design
- **Future mitigation:** Token refresh endpoint (v2) to shorten expiration; opt-in blacklist if needed

**Decision:** Single JWT implementation (no refresh tokens in v1 for simplicity).

---

## ADR-0003: Single Datastore (PostgreSQL) vs Polyglot Persistence

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
NestFi stores users, families, transactions, categories, audit logs. Options:
1. PostgreSQL only (relational, ACID, normalization)
2. PostgreSQL + NoSQL (Mongo, DynamoDB) for logs / cache
3. SQLite (for simplicity)

**Decision:**  
**PostgreSQL 16 as single source of truth** with SQLAlchemy ORM. No secondary datastore (cache, queue) in v1.

**Rationale:**
- **ACID guarantees:** Transaction consistency (money can't be lost / duplicated)
- **Relationships:** Families ↔ Members ↔ Transactions ↔ Categories = relational graph
- **Audit trail:** Append-only audit logs in same DB; no sync issues
- **Simplicity:** One database to manage, backup, scale
- **Cost:** PostgreSQL managed services (Railway, Fly.io) are free-tier eligible

**Consequences:**
- ✓ Strong consistency (transactions never corrupt)
- ✓ No data synchronization bugs between stores
- ✓ Familiar for team; broad ecosystem
- ✗ Must design schema carefully (no schema-less collections)
- ✗ Vertical scaling limits (billions of txns would need sharding)
- **Future mitigation:** v2 can add Redis cache if dashboard queries slow down; no code change needed (abstraction layer already in place)

---

## ADR-0004: Single Currency (per Family) vs Multi-Currency

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
NestFi is global; some families span multiple countries. Options:
1. Single global currency (e.g., USD)
2. Single currency per family (configurable)
3. Multi-currency support with conversion rates

**Decision:**  
**Single currency per family, default USD**. Family owner can select currency at creation time. All transactions in family are in that currency.

**Rationale:**
- **v1 simplicity:** No exchange rate APIs, no conversion logic
- **Accuracy:** Avoids rounding errors in multi-currency calculations
- **Schema:** currency column on families table; transactions inherit it
- **User experience:** Families that span countries can use USD (common) or pick their reference currency

**Consequences:**
- ✓ Schema simplicity (no per-transaction exchange rates)
- ✓ Calculations are straightforward (sum without conversion)
- ✗ Families with mixed-currency accounts can't track per-account splits
- **Workaround (v1):** Create separate families per currency; use "exchange" transaction type (v2)
- **Future:** v2 can add multi-currency if needed (add column: currency_pairs, exchange_rate_map, etc.)

---

## ADR-0005: Image Upload / Storage: Local Filesystem (CDN-Ready) vs Cloud (S3/CDN)

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
NestFi needs to store user avatars, family logos, and receipts (future). Options:
1. Local filesystem (simplicity, full control, portable)
2. AWS S3 (cloud-native, expensive, vendor lock-in)
3. Azure Blob / GCP Cloud Storage (similar)
4. Cloudinary / Imgix (managed, costly, third-party)

**Decision:**  
**Local filesystem in v1** with CDN-ready directory structure. Path pattern:
```
backend/app/static/uploads/
├── users/
│   └── {user_id}/
│       └── avatar.{ext}
├── families/
│   └── {family_id}/
│       └── logo.{ext}
└── receipts/  (future)
    └── {family_id}/
        └── {receipt_id}.{ext}
```

**Rationale:**
- **v1 simplicity:** No cloud credentials, no API calls, no storage costs
- **Portability:** Filesystem directory can be mounted as volume in Docker or Kubernetes
- **CDN-ready:** If we later add Cloudflare/S3, we just change the service layer; paths stay same
- **Control:** Full control over image lifecycle, no vendor API limits
- **Development:** Works on local laptop for testing

**Consequences:**
- ✓ Zero additional cost
- ✓ Works offline / in Docker containers
- ✓ Easy to test (just filesystem operations)
- ✗ Not highly available (single server failure = loss)
- ✗ Not globally distributed (users far from server see slow downloads)
- **Future mitigation:** v2 swap to S3/CDN via new ImageStorageService; code structure already supports it

**Abstraction layer (Python):**
```python
class ImageStorageService:
    def save(self, user_id, file): pass
    def delete(self, user_id, file_key): pass
    def get_url(self, user_id, file_key): pass
```

Implementation v1: FilesystemImageStorage  
Implementation v2+: S3ImageStorage

---

## ADR-0006: Docker Compose for v1 Deployment vs Kubernetes / Cloud-Native

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
v1 needs simple, repeatable deployment. Options:
1. Docker Compose (local dev + single-server prod)
2. Kubernetes (complex, over-engineered for v1)
3. Managed platforms (Railway, Fly.io, Render)

**Decision:**  
**Docker Compose for v1**. Images pushed to local registry or Docker Hub. Deployment = `docker compose -f docker-compose.prod.yml up -d`.

**Rationale:**
- **v1 scale:** 10–100 families, <1000 users; single instance sufficient
- **Developer experience:** `docker-compose up` runs entire stack locally
- **Portability:** Works on any host with Docker (laptop, VPS, small cloud)
- **Cost:** No managed service fees; just host compute
- **Path to v2:** Can containerize separately (Dockerfile already written); transition to Railway/Fly.io is straightforward

**Consequences:**
- ✓ Simple deployment story
- ✓ Works on any host; no cloud vendor lock-in
- ✓ Cheap (single instance + managed PostgreSQL)
- ✗ No horizontal scaling (one app instance, one DB)
- ✗ No automatic failover (single point of failure)
- ✗ Manual deployment (no CI/CD in v1; deferred to v2)
- **Future (v2):** Containerize FE + BE separately; push to Railway / Fly.io / own Kubernetes cluster

**v2 migration path:**
```
v1:  docker-compose.yml (all-in-one)
v2:  backend/Dockerfile → Railway / Fly.io
     frontend/Dockerfile → Vercel / Netlify / Railway
     PostgreSQL → Managed (Railway, Supabase, AWS RDS)
```

---

## ADR-0007: Soft Delete (is_deleted flag) vs Hard Delete for Audit Trail

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
Transactions are critical for financial audits. Users may accidentally delete transactions. Options:
1. Hard delete (impossible to recover)
2. Soft delete (mark deleted, keep in DB)
3. Immutable append-only log

**Decision:**  
**Soft delete on transactions** using `deleted_at` and `deleted_by` columns. Queries exclude soft-deleted records by default.

**Rationale:**
- **Audit compliance:** Deleted records are recoverable; audit trail intact
- **Accidental recovery:** User deletes transaction by mistake; admin can undelete
- **Performance:** No separate archive table; soft delete is lightweight
- **Audit log:** AuditLog table also captures all changes (create, update, delete)

**Consequences:**
- ✓ Transaction history preserved
- ✓ Recovery possible
- ✓ Audit trail complete
- ✗ Requires `deleted_at IS NULL` in all queries (ORM can abstract this)
- ✗ Disk space includes deleted records (not a problem for MVP)
- **Mitigation:** Base CRUD class auto-excludes soft-deleted; developers don't have to remember

**Pattern (SQLAlchemy):**
```python
class Transaction(Base):
    __tablename__ = "transactions"
    id: int
    deleted_at: datetime | None = None
    deleted_by: int | None = None

class TransactionCRUD:
    @staticmethod
    def get_all(family_id, db):
        return db.query(Transaction).filter(
            Transaction.family_id == family_id,
            Transaction.deleted_at.is_(None)
        )
    
    @staticmethod
    def soft_delete(txn_id, user_id, db):
        txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
        txn.deleted_at = datetime.now()
        txn.deleted_by = user_id
        db.commit()
```

---

## ADR-0008: Monorepo Code Layout (backend/ + frontend/) vs Separate Repos

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
Where to store BE and FE code? Options:
1. Single monorepo (backend/, frontend/, both under version control)
2. Separate repos (independently versioned, deployed)

**Decision:**  
**Single monorepo** with `backend/` and `frontend/` folders, single git history, single Docker Compose.

**Rationale:**
- **Coupling:** FE calls BE APIs; tightly coupled by design
- **Atomic commits:** Bug fix that touches both FE + BE = single commit + PR
- **CI/CD simplicity:** One pipeline, one build artifact
- **v1 scope:** Small codebase (<10K lines total); monorepo overhead is minimal

**Consequences:**
- ✓ Easier refactoring across FE/BE boundary
- ✓ Single CI/CD pipeline
- ✓ Cleaner history for related changes
- ✗ Monorepo tools overhead (if codebase grows)
- ✗ Deployments are all-or-nothing (FE + BE together)
- **Future:** v2+ can split if teams grow; tools exist (yarn workspaces, pnpm, etc.)

**Structure:**
```
nestfi/
├── backend/        (Python, FastAPI)
├── frontend/       (Python, Dash)
├── docker-compose.yml
├── pyproject.toml  (optional, monorepo-level)
└── poetry.lock     (shared lock)
```

---

## ADR-0009: API Design: REST vs GraphQL

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
FE needs to fetch families, transactions, categories, analytics data. Options:
1. REST (multiple endpoints, simple, standard)
2. GraphQL (flexible queries, larger learning curve)

**Decision:**  
**REST with JSON** and OpenAPI (Swagger) auto-documentation.

**Rationale:**
- **Simplicity:** Standard HTTP methods (GET, POST, PUT, DELETE)
- **Caching:** REST is cache-friendly (GET is idempotent)
- **Authentication:** Bearer tokens in headers work seamlessly
- **Dash support:** Dash makes HTTP calls easily; no GraphQL client needed
- **API documentation:** FastAPI auto-generates OpenAPI docs (/docs, /redoc)
- **Debugging:** Browser can call REST endpoints; GraphQL requires tools

**Endpoints (defined in SOLUTION_ARCHITECTURE.md):**
```
GET  /families
POST /families/{id}/transactions
GET  /families/{id}/transactions?category_id=5&date_from=2026-01-01&date_to=2026-12-31
PUT  /families/{id}/transactions/{txn_id}
```

**Consequences:**
- ✓ Widely understood (every developer knows REST)
- ✓ Cacheable
- ✓ Easy to debug
- ✗ Over-fetching / under-fetching (FE must make multiple requests for related data)
- **Mitigation:** Pagination + filtering on endpoints; can batch if needed (v2)

---

## ADR-0010: Email Delivery: SMTP vs Third-Party Service

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
NestFi needs to send invitations, password resets, notifications. Options:
1. Local SMTP (simple, requires mail server)
2. SendGrid / Mailgun / AWS SES (managed, scalable, costs)
3. Third-party like Twilio (managed, more features)

**Decision:**  
**SMTP in v1** (simple self-hosted mail or free tier like MailTrap for dev). **Abstraction layer** to swap to SendGrid/SES in v2.

**Rationale:**
- **v1 simplicity:** No third-party API keys, credentials, costs
- **Abstraction:** EmailService class allows swapping implementation
- **Development:** MailTrap (free) or local Docker mail container works locally
- **v1 scale:** <100 invitations/day; self-hosted SMTP sufficient

**Consequences:**
- ✓ Zero cost
- ✓ Full control over emails
- ✗ Deliverability depends on mail server setup (can end up in spam)
- ✗ No built-in tracking / analytics
- **Future:** v2 integrates SendGrid (higher deliverability, replay, etc.)

**Pattern (EmailService):**
```python
class EmailService:
    def send_invitation(self, email: str, family_name: str, token: str): pass
    def send_password_reset(self, email: str, token: str): pass

class SMTPEmailService(EmailService):  # v1
    def send_invitation(self, ...):
        smtplib.send(...)

class SendGridEmailService(EmailService):  # v2+
    def send_invitation(self, ...):
        sendgrid_client.send(...)
```

---

## ADR-0011: Transaction Audit Log: Same DB vs Separate Archive

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
Transactions are critical for finance; must log all changes for compliance. Options:
1. Audit logs in same PostgreSQL DB
2. Separate audit database (archive)
3. Event log (Kafka, RabbitMQ)

**Decision:**  
**Single PostgreSQL DB with `audit_logs` table**. All changes (create, update, delete) logged with user, timestamp, old/new values.

**Rationale:**
- **Simplicity:** No distributed system; single DB transaction consistency
- **ACID guarantees:** Transaction + audit log are atomic
- **Compliance:** Audit trail is queryable via SQL
- **v1 scale:** Audit logs grow linearly; acceptable for MVP (<1000 users)

**Consequences:**
- ✓ Simple to implement
- ✓ Audit trail is transactionally consistent
- ✗ Audit logs consume disk space (no archival in v1)
- **Future:** v2 can archive old logs to S3 (cold storage) if needed

**Audit Log Schema:**
```sql
audit_logs (
  id PK,
  user_id FK,
  entity_type (user, family, transaction, category),
  entity_id,
  action (create, update, delete),
  old_values JSON,
  new_values JSON,
  timestamp,
  ip_address
)
```

---

## ADR-0012: Default Categories System vs User-Defined Only

**Status:** Accepted (confirmed by user, 2026-05-16)

**Context:**  
Families need categories (income, expense, investment). Options:
1. System provides defaults (e.g., "Salary", "Groceries"); user can add/modify
2. User creates all categories from scratch
3. Hybrid (defaults + customization)

**Decision:**  
**System provides default categories** at family creation time. User can modify, delete, or add new categories.

**Rationale:**
- **UX:** Users can start logging transactions immediately without category setup
- **Consistency:** Default categories are familiar ("Salary", "Groceries", etc.)
- **Flexibility:** Users can rename or delete defaults if needed
- **Data analysis:** Default categories enable comparison across families

**Default Categories (created at family setup):**

*Income:*
- Salary
- Bonus
- Freelance
- Interest
- Other Income

*Expense:*
- Groceries
- Utilities
- Entertainment
- Transport
- Cash Withdrawal
- Other Expense

*Investment:*
- Stock Portfolio
- Retirement
- Crypto
- Other Investment

**Consequences:**
- ✓ Users can transact immediately
- ✓ Familiar category names
- ✓ Enables cross-family analytics
- ✗ Categories may not match every family's needs
- **Mitigation:** Users can edit/archive categories; new ones can be created anytime

---

## Future ADRs (TBD in v2+)

- **ADR-0013:** Refresh tokens (if needed for mobile apps)
- **ADR-0014:** Notification system (in-app vs email vs push)
- **ADR-0015:** Batch operations (reporting, exports)
- **ADR-0016:** Rate limiting and DDoS protection
- **ADR-0017:** Caching strategy (Redis) for high-traffic reads
- **ADR-0018:** API versioning (v1, v2) and backwards compatibility

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | SA | Created ADR.md with 12 key architectural decisions for Python stack (Dash + FastAPI + PostgreSQL) |
