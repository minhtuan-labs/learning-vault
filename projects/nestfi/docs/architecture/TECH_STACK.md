# Tech Stack — NestFi

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** SA  
**Status:** Confirmed by user (question id: SA_20260516_172526)

---

## Executive Summary

NestFi uses a **Python-first monorepo** with Dash + Tailwind for frontend, FastAPI for backend, PostgreSQL 16 for persistence, and Docker Compose for local development and v1 deployment.

---

## Rationale

This stack prioritizes:
- **Rapid iteration** — Dash enables quick UI building; FastAPI provides fast APIs
- **Developer velocity** — Python + SQL avoids language switching; SQLAlchemy + Alembic = flexible migrations
- **Simplicity in v1** — Docker Compose is self-hosted; no cloud lock-in; easy local onboarding
- **Image readiness** — CDN-ready filesystem structure allows future migration without code refactoring

---

## Confirmed Technology Choices

| Dimension | Choice | Rationale |
|---|---|---|
| **Frontend Framework** | Dash (Plotly) | Rich interactive charts, Python-native, minimal JS friction |
| **Frontend Language** | Python | Monorepo coherence; no FE/BE language split |
| **UI / Design System** | Tailwind CSS | Utility-first; pairs well with Dash components |
| **Backend Language** | Python | Ecosystem maturity; quick to prototype |
| **Backend Framework** | FastAPI | Modern async support; auto-docs (OpenAPI/Swagger) |
| **Primary Datastore** | PostgreSQL 16 | Relational; mature; excellent for user/category/transaction schema |
| **ORM / Data Layer** | SQLAlchemy 2 + Alembic | Declarative; type-safe; migrations are first-class |
| **Authentication** | JWT (PyJWT) | Stateless; scales horizontally; no session store overhead in v1 |
| **File Storage (Images)** | Local filesystem with CDN-ready structure | Simplicity for v1; prepared for future S3 or CDN migration |
| **Cache / Queue** | None in v1 | Can add Redis / Celery later if performance requires |
| **Hosting (v1)** | Docker Compose | Self-hosted; full control; portable |
| **Hosting (future)** | Railway / Fly.io / own VPS | Keep options open; Docker Compose is the bridge |
| **Code Layout** | Monorepo: `backend/` + `frontend/` | Shared models, single deployment story, easier refactoring |
| **Package Manager (BE)** | pip + poetry | poetry for lock files; pip install for reproducible builds |
| **Package Manager (FE)** | pip + poetry (shared with BE) | Python-only monorepo; no npm/pnpm overhead |

---

## Directory Structure

```
nestfi/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings (DB, JWT secret, etc.)
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas (request/response)
│   │   ├── crud/                # CRUD operations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/          # Endpoints (auth, users, families, transactions, etc.)
│   │   │   └── dependencies.py  # Shared dependencies (auth, DB session)
│   │   ├── services/            # Business logic layer
│   │   ├── utils/               # Helpers
│   │   └── static/              # Uploaded images (CDN-ready)
│   ├── tests/
│   ├── alembic/                 # Database migrations
│   │   └── versions/
│   ├── requirements.txt          # pip dependencies
│   ├── pyproject.toml           # poetry config
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Dash app entry
│   │   ├── config.py            # Frontend settings (API base, etc.)
│   │   ├── pages/               # Multi-page Dash (auth, dashboard, etc.)
│   │   ├── components/          # Reusable Dash components
│   │   ├── utils/               # Helpers, API client
│   │   └── assets/              # CSS (Tailwind), images
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml           # Local dev and v1 deployment
├── pyproject.toml               # Monorepo-level poetry config (optional)
├── poetry.lock                  # Shared lock file
└── .env.example                 # Top-level env template
```

---

## Development Environment

### Prerequisites
- Python 3.12+ (system or via `pyenv`)
- PostgreSQL 16 (via Docker or local install)
- Docker & Docker Compose

### Local Setup
```bash
git clone <repo>
cd nestfi

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies (both BE and FE)
cd backend && pip install -r requirements.txt
cd ../frontend && pip install -r requirements.txt
cd ..

# Copy and configure env files
cp .env.example .env
# Edit .env with local DB credentials, JWT secret, etc.

# Start database (Docker Compose)
docker compose up -d postgres

# Run migrations
cd backend
alembic upgrade head
cd ..

# Run backend and frontend in separate terminals
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd frontend && python app/main.py  # Dash runs on http://localhost:8050
```

### docker-compose.yml (v1 deployable)
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: nestfi
      POSTGRES_PASSWORD: <set in .env>
      POSTGRES_DB: nestfi
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://nestfi:<pw>@postgres:5432/nestfi
      JWT_SECRET: <set in .env>
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    environment:
      API_BASE_URL: http://backend:8000
    ports:
      - "8050:8050"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## API Contract

- **Format:** RESTful JSON with OpenAPI (auto-generated by FastAPI)
- **Base URL (local):** `http://localhost:8000`
- **Base URL (docker):** `http://backend:8000`
- **Auth:** JWT Bearer token in `Authorization` header
- **Errors:** JSON with `{ "detail": "error message", "code": "ERROR_CODE" }`

See `docs/architecture/API_CONTRACT.md` for detailed endpoint spec.

---

## Security Considerations

### Authentication
- Passwords hashed with **bcrypt** (via `passlib`)
- JWT tokens issued with **PyJWT**; `HS256` algorithm
- Tokens expire in 24 hours (refresh via `/auth/refresh` endpoint, deferred to v2)

### Data Protection
- **HTTPS in production** (enforce via reverse proxy / load balancer)
- **Database:** PostgreSQL user/password in env file (never in code)
- **JWT secret:** In env file (rotate before public launch)
- **Audit logging:** User ID, timestamp, action (required in CRUD operations)

### Authorization
- **Superadmin:** Can create families, view all users (hardcoded role)
- **Owner:** Can manage family members, categories, transactions, settings
- **Member:** Can log transactions, view shared data, edit own transactions
- **View-only members:** Can view only (future v2 feature)

---

## Performance & Scalability Notes

### v1 Constraints
- Single Docker Compose instance
- No horizontal scaling
- No caching layer (Redis)
- Synchronous request/response model

### Path to v2+
- **Stateless FastAPI** → easy container replication
- **JWT auth** → no session affinity needed
- **PostgreSQL** → can scale to managed cloud (Railway, AWS RDS, etc.)
- **Filesystem images** → swap to S3 + CloudFront without code changes
- **No session store** → Dash can run as stateless containers with load balancing

---

## Deployment Checklist

### For v1 (Docker Compose local / VPS)
- [ ] Database schema initialized (alembic migrate)
- [ ] Superadmin account seeded (default credentials)
- [ ] `.env` file configured (DB, JWT secret)
- [ ] Docker images built and tested locally
- [ ] Healthcheck endpoints defined
- [ ] Email service configured (simple SMTP or SendGrid)

### For v2+ (cloud migration)
- [ ] Managed database (Railway, AWS RDS, Supabase, etc.)
- [ ] Container registry (Docker Hub, AWS ECR, etc.)
- [ ] Reverse proxy / load balancer (Nginx, AWS ALB, etc.)
- [ ] HTTPS / TLS certificates (Let's Encrypt, AWS ACM, etc.)
- [ ] Image storage on S3 / CDN
- [ ] Monitoring and logging (CloudWatch, DataDog, etc.)
- [ ] CI/CD pipeline (GitHub Actions, GitLab CI, etc.)

---

## Rationale for Deferred v2 Features

- **Redis / Caching:** Not needed until query time exceeds 3s on typical household (100-1000 txns)
- **Celery / Async Queue:** Not needed until email/report generation blocks requests
- **GraphQL:** REST + OpenAPI sufficient for current feature set; GraphQL adds complexity
- **Mobile app:** Web-responsive Dash sufficient for v1; native apps deferred
- **Multi-currency:** Single currency per family reduces schema complexity; add in v2 if needed

---

## Reference Links

- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy 2:** https://docs.sqlalchemy.org/
- **Dash:** https://dash.plotly.com/
- **Tailwind CSS:** https://tailwindcss.com/
- **PyJWT:** https://pyjwt.readthedocs.io/
- **Alembic:** https://alembic.sqlalchemy.org/

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | SA | Created TECH_STACK.md with user-confirmed Python stack (Dash + FastAPI + PostgreSQL) |
