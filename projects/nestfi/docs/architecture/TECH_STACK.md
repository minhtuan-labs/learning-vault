# Tech Stack — NestFi

**Confirmed by user (question id: SA_20260516_214416)**

This document specifies the complete technology stack for NestFi v1. All choices below were validated with the user and are locked for this phase.

## Frontend Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | Next.js 15 (App Router) | Modern, full-stack, excellent for dashboards with SSR/SSG capabilities |
| Language | TypeScript | Type safety for complex financial logic and state management |
| UI Library | Tailwind CSS + shadcn/ui | Fast iteration, accessible components, composable design system |
| Package Manager | npm or pnpm | Standard Node.js ecosystem |
| Node Version | 18 LTS or higher | Compatibility with Next.js 15 |

## Backend Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.12 | Strong data processing, excellent for financial calculations and business logic |
| Framework | FastAPI | Async-first, modern, excellent API documentation (OpenAPI/Swagger), type hints |
| Package Manager | uv | Fast Python package manager, handles virtual environments efficiently |
| Python Version | 3.12+ | Latest stable Python with performance improvements |

## Data Layer

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Primary Datastore | PostgreSQL 16 | Relational, robust, handles complex family/account/transaction structures |
| ORM | SQLAlchemy 2 + Alembic | Mature, flexible, excellent migrations, supports async patterns |
| Connection Pool | SQLAlchemy with asyncpg | Async-compatible, connection pooling for concurrent requests |

## Authentication & Sessions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Web Session Auth | Database-backed sessions (server-side) | Matches long-lived session requirement, secure session storage |
| API Auth | JWT (Bearer tokens) | Standard for API clients and future mobile apps |
| Session Store | PostgreSQL (v1) or Redis (optional v1) | PostgreSQL for simplicity; Redis for scaling multi-user scenarios |
| Password Hashing | bcrypt via passlib | Industry standard, resistant to attacks |
| Email Delivery | Mock/Print (v1) → SendGrid/Mailgun (v2) | Print to logs for development; integrate external provider later |

## Infrastructure & Deployment

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Containerization | Docker & Docker Compose | Local development consistency, foundation for cloud deployment |
| Runtime | Python 3.12 Alpine image for BE, Node 18 for FE | Minimal image sizes, security updates |
| Development Mode | Docker Compose (local) | All services (Postgres, Redis, FE, BE) in containers |
| Production v1 | Docker Compose (single-host or cloud) | TBD cloud platform later (AWS, Render, Railway, etc.) |
| Cache Layer | Redis (optional v1) | Session store optimization, future job queue foundation |

## Code Organization

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Layout | Monorepo (backend/ + frontend/) | Single repository, shared docs/architecture, coordinated versioning |
| Backend Structure | `backend/` folder with `app/`, `models/`, `schemas/`, `routes/` | FastAPI standard project structure |
| Frontend Structure | `frontend/` folder with Next.js App Router conventions | Next.js standard; components/, lib/, app/ directories |
| Shared Assets | `docs/` for architecture, business, QA specs | Central reference for all team members |

## API Contract

- **API Format:** RESTful with JSON payloads
- **Versioning:** v1 in URL path: `/api/v1/...`
- **Docs:** Auto-generated OpenAPI/Swagger at `GET /api/v1/docs`
- **CORS:** Configured for localhost:3000 (FE) in dev; restricted in prod

## Database Design

- **Schema:** Normalized relational design with families as root entities
- **Migrations:** Alembic for version control; `backend/alembic/` folder
- **Seeding:** Initial superadmin, default categories, sample families (dev only)
- **Constraints:** Foreign keys for referential integrity, unique constraints where needed

## Development & Testing

| Tool | Purpose |
|------|---------|
| pytest | Backend unit & integration tests |
| jest / vitest | Frontend unit tests (deferred v1.1) |
| Docker Compose | Local environment orchestration |
| Postman / Insomnia | API testing during development |

## Security Assumptions

- **HTTPS:** Not enforced in v1 (local Docker); TLS termination by reverse proxy in production
- **CORS:** Whitelisted origins in development; restrictive in production
- **Password Policy:** Minimum 8 characters (v1); complexity rules in v2
- **Session Timeout:** TBD (default: 30 minutes inactivity)
- **Sensitive Data:** Passwords hashed with bcrypt; never logged; PII handled per user preference

## Version Lock

This stack is confirmed and locked for Phase 1–4 BUILD. Any changes require user approval via clarification protocol.

**Next Steps:**
- BE writes architecture review of database schema and API routes
- FE writes component architecture and state management plan
- Both teams verify API_CONTRACT.md covers their needs