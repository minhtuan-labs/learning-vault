# Architecture Decision Records (ADR) — NestFi

## ADR-001: Synchronous Request-Response Architecture (v1)

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

NestFi is a family financial management system where users (family members) record and review transactions together. For v1, we need a simple, debuggable architecture that ensures strong consistency and avoids operational complexity.

**Decision:**

Implement a **synchronous monolith** (Next.js ↔ FastAPI ↔ Postgres) with no message queues, no event streaming, and no eventual consistency requirements.

- User action → API request → single DB transaction → response → UI update
- All state changes are immediately visible to all connected clients

**Rationale:**

- **Simplicity:** Easier to test, debug, and reason about state
- **Consistency:** Family members see real-time accurate balances and transaction history
- **Acceptable latency:** Single household's transaction volume (tens per day) doesn't require async
- **Foundation:** Easy to migrate to event-driven (Celery queue, webhooks) in v2+ if scaling demands it

**Consequences:**

- Long-running operations (bulk export, analytics recalculation) will block; defer to v2
- No offline mode or optimistic updates; users must be online to record transactions
- Database must be fast and reliable; indexing and connection pooling are critical

---

## ADR-002: Family-Scoped Data Isolation

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

NestFi supports multiple families per instance (e.g., "Smith household" and "Jones household"). Data (accounts, transactions, members) must be isolated per family. A compromised user's token should not expose other families' data.

**Decision:**

All data queries are filtered by `family_id` at the API boundary:

```python
# FastAPI dependency
async def get_family_context(request):
    family_id = request.path_params.get('family_id')
    user = get_current_user(request)
    assert_user_in_family(user, family_id)  # 403 if not a member
    return family_id
```

Every request to `/api/v1/families/{family_id}/...` validates that the authenticated user is a member of that family. Database schema uses `family_id` FK on all tables (accounts, transactions, categories, memberships).

**Rationale:**

- **Security:** Prevents horizontal privilege escalation (user accessing other families' data)
- **Compliance:** Clear audit trail per family; easier to implement data retention/deletion per family
- **Multi-Tenancy Ready:** Same codebase can serve multiple independent organizations in future

**Consequences:**

- All queries must include `family_id` filter; no global "admin view" of all transactions (by design)
- Bulk operations (export, analytics) must iterate per family
- Schema design requires foreign keys; database growth is linear with number of families

---

## ADR-003: Database-Backed Sessions + JWT for API

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

NestFi needs two authentication flows:

1. **Web UI:** Users log in via browser; sessions persist across page reloads
2. **API/Mobile:** Programmatic clients (Postman, future mobile app) need stateless auth

**Decision:**

- **Web Sessions:** httpOnly + Secure cookies backed by Postgres session store (or Redis for scaling)
  - Session token is opaque; server-side lookup required
  - Automatic invalidation on logout or timeout
  - Secure by default (httpOnly prevents XSS token theft)

- **API Bearer Tokens:** JWT (self-contained, stateless)
  - Token issued on login; client includes in `Authorization: Bearer <token>` header
  - Server validates signature without database lookup
  - User can request multiple tokens (mobile + web client simultaneously)

**Rationale:**

- **Sessions:** Stateful, short-lived (30 min default), high security for web
- **JWT:** Stateless, long-lived (TBD hours), flexible for distributed systems / mobile
- **Flexibility:** Supports both browser cookies and bearer tokens without architectural debt
- **Standards:** Both patterns are industry standard; easy for future developers to maintain

**Consequences:**

- Session table grows with number of logged-in users; cleanup job required (cascade delete on user logout)
- JWT tokens can't be revoked instantly (token remains valid until expiry); logout instructions include "wait for token expiration" as fallback
- Clients must handle token refresh (out of v1 scope)

---

## ADR-004: No Person-Level Transaction Tracking (Account-Centric Design)

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

NestFi tracks family finances via accounts (checking, savings, investment). The question: Do we track *who* spent the money (person-centric), or just which *account* (account-centric)?

**Decision:**

**Account-centric only.** All transactions belong to an account, not a person. The family's checking account shows "expenses: $500" without breaking down "Alice paid $300, Bob paid $200."

- Transactions include `creator_id` for audit (who recorded it), but no bill-splitting or person-level ledgers
- All family members can record and edit any account's transactions
- No "my spending" vs. "household spending" distinction

**Rationale:**

- **Simplicity:** Easier UI, simpler schema, less permission logic
- **User Story Fit:** PRODUCT_IDEA.md doesn't mention bill-splitting or per-person budgets
- **Scope:** Bill-splitting (v2+) can be added later without breaking v1 schema (new `splits` table)
- **Fairness:** All members see all accounts equally; no privacy assumptions

**Consequences:**

- No "my expenses" dashboard (feature deferred to v2)
- Household members must trust each other or use separate accounts if they want privacy
- Analytics are family-wide only; no per-member spending reports

---

## ADR-005: Immutable Transactions with Edit Audit Trail

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

Users will make mistakes recording transactions (wrong amount, wrong date, typo in description). The decision: Allow edits? If so, how to prevent fraud or enable auditing?

**Decision:**

- **Editable Transactions:** Any family member can edit any transaction (amount, date, category, description)
- **Audit Trail:** Every edit recorded in `transaction_edits` table with editor ID, timestamp, before/after snapshots
- **No Direct Overwriting:** `transactions` table is never updated in-place; only `transaction_edits` records are appended
- **Full History:** Family members can view complete edit history for any transaction via transaction detail view

**Rationale:**

- **Ease of Use:** Users can fix mistakes without losing the record
- **Compliance:** Audit trail prevents "invisible" fraud (edit without trace)
- **Transparency:** All family members see who changed what and when
- **Balance Rollup:** Account balance recomputed from non-disabled transactions; edits instantly update balances

**Consequences:**

- Edit history grows with transaction volume; archival strategy needed long-term
- `transaction_edits` table may be larger than `transactions` table over time
- UI must surface edit history clearly (not hidden in logs)

---

## ADR-006: Soft-Delete for Transactions + Hard-Delete for Owner Only

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

Mistakes happen. Users may want to hide a transaction from reports without losing history. Example: "I recorded the transaction twice by mistake; hide one but keep the record."

**Decision:**

- **Soft-Delete (Disable):** Any family member can disable/hide a transaction (sets `is_enabled = false`)
- **Excluded from Reports:** Disabled transactions excluded from P&L, dashboards, balance rollup
- **Recoverable:** Disabled transactions remain in DB; any member can re-enable them
- **Hard-Delete:** Only family owner can permanently delete (hard-delete) transactions
- **No Recovery:** Hard-deleted transactions cannot be recovered

**Rationale:**

- **Mistake Recovery:** Soft-delete is a safety net for accidental duplicates
- **Fraud Prevention:** Hard-delete requires owner approval (prevents members from erasing evidence)
- **Audit Trail:** Hard-deleted transactions retained in `transaction_edits` table (immutable)

**Consequences:**

- Dashboard and reports must filter `is_enabled = true` in all queries
- Database size includes disabled transactions indefinitely (storage cheap, deletion risky)
- Owner needs clear warning before hard-delete ("This cannot be undone")

---

## ADR-007: Monorepo (backend/ + frontend/) Structure

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

Where to organize code? Single repository or separate repos for backend and frontend?

**Decision:**

**Monorepo:** Single Git repository with `backend/` and `frontend/` directories.

```
nestfi/
├── backend/             (FastAPI, migrations, models, routes)
├── frontend/            (Next.js, components, pages)
├── docs/                (shared architecture, business docs)
├── docker-compose.yml
├── .gitignore
└── README.md
```

**Rationale:**

- **Shared Context:** Architecture docs, business rules in one place visible to all team members
- **Atomic Commits:** Schema changes + API changes + UI changes in single commit; easier to review
- **CI/CD:** Single pipeline; easier to test backend + frontend integration
- **Onboarding:** New developer clones one repo; everything in one place

**Consequences:**

- Backend and frontend releases are tied together (not independent deployments)
- Both services deployed from same commit SHA; schema version = API version = UI version
- Harder to scale teams independently (but fine for v1)

---

## ADR-008: Email Delivery via Mock/Print (v1) → Real Provider (v2+)

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

Invitations and password resets require email delivery. Should we integrate Sendgrid/Mailgun in v1, or stub it out?

**Decision:**

**v1 (Development):** Mock email delivery — print tokens to console logs

```python
# dev mode: print to logs
if settings.SMTP_ENABLED:
    send_real_email(user.email, invitation_link)
else:
    logger.info(f"[MOCK EMAIL] Send to {user.email}: {invitation_link}")
```

**v2 (Production):** Integrate SendGrid or Mailgun via `settings.SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`.

**Rationale:**

- **v1 Scope:** No external dependencies; easier local testing without email account
- **v2 Ready:** Settings structure supports real provider without code change
- **Cost:** No monthly email service bill in dev/test
- **Testing:** QA can see all invitation links in logs

**Consequences:**

- Invitations don't actually email in v1; manual testing requires checking logs
- Real environment (v2) requires Sendgrid/Mailgun API keys in `.env`
- Users in v1 can't test email reset flow end-to-end (but can verify DB state)

---

## ADR-009: Docker Compose for v1, Cloud TBD for v2+

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

Where to deploy v1? Heroku? AWS? Docker container service? Keep it local?

**Decision:**

**v1:** Docker Compose only. No cloud deployment in v1.

```bash
docker-compose up -d
# Services running on localhost
```

**v2:** Choose from Render, Railway, Fly.io, AWS ECS, etc. (user decision via clarification protocol).

**Rationale:**

- **v1 Scope:** Local development + testing only; no need for cloud infrastructure
- **Foundation:** Docker Compose is portable; easy to migrate to any cloud provider later
- **Cost:** Zero infrastructure cost for development
- **Decision Delay:** Cloud choice depends on scaling, cost tolerance, and compliance needs (TBD at v2)

**Consequences:**

- No public URL in v1; app only accessible on `localhost:3000`
- Team testing requires Docker and `docker-compose` CLI installed locally
- v2 requires infrastructure setup (cloud account, managed DB, reverse proxy config)

---

## ADR-010: SQLAlchemy ORM + Alembic Migrations

**Date:** 2026-05-16  
**Status:** DECIDED  
**Context:**

NestFi backend uses FastAPI + PostgreSQL. How to manage database schema and migrations?

**Decision:**

- **ORM:** SQLAlchemy 2 with async support (`async_engine`, `AsyncSession`)
- **Migrations:** Alembic for schema versioning and migrations
- **Async:** All database queries use `await` for non-blocking I/O

**Rationale:**

- **Async Support:** Matches FastAPI's async nature; full async stack for performance
- **Type Hints:** SQLAlchemy 2 supports Python type hints (matches backend language choice)
- **Mature:** Both projects are battle-tested; excellent documentation
- **Flexibility:** ORM for simple queries, raw SQL for complex analytics

**Consequences:**

- Setup complexity: async session management, dependency injection for DB connections
- Limited NoSQL capabilities (if needed in future, can add MongoDB alongside)
- Requires knowledge of relational patterns; not ideal for unstructured data

---

## Summary of Major Decisions

| ADR | Title | Status | Implication |
|-----|-------|--------|-------------|
| 001 | Synchronous Monolith | ✅ DECIDED | No queues, no async jobs in v1 |
| 002 | Family-Scoped Isolation | ✅ DECIDED | All queries filtered by family_id |
| 003 | Sessions + JWT | ✅ DECIDED | Browser cookies + bearer tokens |
| 004 | Account-Centric (no bill-split) | ✅ DECIDED | No person-level transaction tracking |
| 005 | Edit Audit Trail | ✅ DECIDED | transaction_edits table for compliance |
| 006 | Soft-Delete + Owner Hard-Delete | ✅ DECIDED | is_enabled flag, owner-only permanent deletion |
| 007 | Monorepo | ✅ DECIDED | Single backend/ + frontend/ repo |
| 008 | Mock Email (v1) | ✅ DECIDED | Print to logs; real provider in v2+ |
| 009 | Docker Compose (v1) | ✅ DECIDED | Local only; cloud TBD for v2+ |
| 010 | SQLAlchemy + Alembic | ✅ DECIDED | Async ORM + migrations |

---

**Next Steps:**
- Backend team implements schema based on ADRs 002, 005, 006, 010
- Frontend team designs dashboard/form components per ADR 004
- Both teams verify API_CONTRACT.md captures all decision implications
