# Memory — BE

> Durable scratchpad for the **BE** pane. BE owns: backend implementation and backend tests.
>
> READ this file at the start of every task (alongside
> `memory/_PROJECT_STATE.md`). APPEND a dated entry before exiting any
> OpenCode turn. See `memory/README.md` for format and discipline.

## Decisions

- Module structure: auth, users, families, transactions, categories, admin + analytics
- ORM: SQLAlchemy 2.0 with Alembic migrations; startup runs `alembic upgrade head`
- Auth: JWT HS256, 24h expiry, no refresh endpoint in v1
- Category archival: soft deactivation (is_active=FALSE), transactions retain refs
- Soft deletes on transactions with audit trail (deleted_at, deleted_by)
- P0 endpoints: 21 routes covering auth, families, transactions, categories, analytics
- Phase 4 build estimate: 6-7 days (1 FTE), parallel with FE

## Conventions

- Models inherit from Base + TimestampMixin (id, created_at, updated_at)
- All endpoints return HTTP exceptions (HTTPException) with clear detail messages
- Type hints on all functions; docstrings only if non-obvious
- Database indexes on foreign keys + frequently queried columns (family_id, user_id, transaction_date)
- Test fixtures in conftest.py; ~70% code coverage target

## Gotchas

- Soft-delete queries must always filter `deleted_at IS NULL` (not just SELECT)
- Role-based access control: owner role varies by context (superadmin > family owner > member)
- Category type cannot be changed after creation (enforce in service layer)
- Email invitations critical path; SMTP misconfiguration blocks family setup flow

## Open items I'm tracking

- CORS headers: confirm with FE team that localhost:8050 → localhost:8000 allowed
- SMTP configuration: .env.example needs SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
- Seed data: plan script to create superadmin account at startup (or manual init)
- Health check endpoint GET / for docker-compose and monitoring

### 2026-05-16 17:36 — Phase 3 Backend Planning
Completed BE_PLAN.md with 7 sections: module breakdown (auth/users/families/transactions/categories/admin/analytics), ORM strategy (SQLAlchemy 2.0 + Alembic), 21 P0 API endpoints prioritized, identified risks + mitigations, and 6-7 day build timeline. All prerequisites met; ready for Phase 4 (Build). No blocking questions identified.

### 2026-05-16 17:46 — Phase 4 Backend Scaffold Complete
Implemented complete FastAPI backend scaffold with all 21 P0 endpoints. Includes: SQLAlchemy models (User, Family, FamilyMember, Invitation, Transaction, Category, AuditLog) with TimestampMixin; Pydantic schemas for validation; JWT auth (HS256, bcrypt) with get_current_user dependency; role-based access control (superadmin/owner/member); core routes for auth, users, families, transactions, categories, analytics, admin; soft deletes on transactions; invitation system with token-based acceptance; default category seeding (15 per type); pagination and filtering on transactions; error handling with custom exceptions. Dockerfile, requirements.txt, and pytest fixtures created. Code committed. Next: test coverage, seeding superadmin, SMTP integration, optional: caching/async improvements.
