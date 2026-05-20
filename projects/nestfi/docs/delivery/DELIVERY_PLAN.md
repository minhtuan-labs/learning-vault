# Delivery Plan — NestFi v1

**Last Updated:** 2026-05-16  
**Locked By:** Phase 3 (IMPLEMENTATION_PLANNING) → Phase 4 (BUILD)

This document specifies how NestFi v1 is containerized, deployed, and verified locally and in production.

---

## Overview

NestFi is a monorepo with three containerized services:

| Service | Technology | Image | Port |
|---------|-----------|-------|------|
| **Frontend** | Node 18 LTS + Next.js 15 | `node:18-alpine` | `3000` (host) |
| **Backend API** | Python 3.12 + FastAPI | `python:3.12-slim` | `8000` (host) |
| **Database** | PostgreSQL 16 | `postgres:16-alpine` | `5432` (internal, not exposed) |

All services run via `docker compose` on `localhost` for v1. Production deployment (AWS, Railway, etc.) is deferred to v2.

---

## Environment Configuration

### `.env.example` Template

Every environment variable the stack needs. **NEVER commit `.env` (with actual secrets); only commit `.env.example`.**

```bash
# Frontend (Next.js)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=NestFi
NODE_ENV=development

# Backend (FastAPI)
FASTAPI_ENV=development
DATABASE_URL=postgresql+asyncpg://nestfi_user:nestfi_pass@postgres:5432/nestfi
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRY_HOURS=24
SESSION_TIMEOUT_MINUTES=30

# Database (PostgreSQL)
POSTGRES_USER=nestfi_user
POSTGRES_PASSWORD=nestfi_pass
POSTGRES_DB=nestfi

# Optional: Redis
REDIS_ENABLED=true
```

**Note:** In development, these are safe defaults. In production, use a secrets vault (AWS Secrets Manager, HashiCorp Vault, etc.).

---

## Docker Compose Setup

### `docker-compose.yml` Structure

Orchestrates three services with dependency ordering:

```yaml
version: '3.9'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"  # Exposed for local CLI access; remove in prod
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"  # For local testing; remove in prod
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      JWT_EXPIRY_HOURS: ${JWT_EXPIRY_HOURS}
      FASTAPI_ENV: ${FASTAPI_ENV}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL}
      NODE_ENV: ${NODE_ENV}
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  default:
    name: nestfi_network
```

**Key Decisions:**
- DB is internal-only in v1 (remove port mapping if storing sensitive prod data).
- Redis is optional; enabled in `.env` for session scaling.
- `condition: service_healthy` ensures correct startup order.
- All services restart on failure: `restart_policy: always` (can be made explicit if needed).

---

## Build Process

### Step 1: Prepare Environment
```bash
cp .env.example .env
# Edit .env with local values (usually just defaults are fine for dev)
```

### Step 2: Build Images
```bash
docker compose build 2>&1 | tee docs/delivery/_last_build.log
```

- Builds multi-stage Dockerfiles for each service.
- Logs captured to `docs/delivery/_last_build.log` for debugging.
- **If build fails**, capture the error and route the appropriate owner (BE, FE, or SA).

### Step 3: Start Services
```bash
docker compose up --build -d
docker compose ps
```

Starts all services in detached mode. All healthchecks run automatically.

---

## Deployment & Verification

### Health Checks

Each service has a `healthcheck` defined in `docker-compose.yml`. Docker monitors them continuously.

**Manual verification (after `docker compose up`):**

```bash
# Wait 5 seconds for healthchecks
sleep 5

# Frontend
curl -fsS http://localhost:3000/ >/dev/null && echo "✓ Frontend OK" || echo "✗ Frontend FAIL"

# Backend API
curl -fsS http://localhost:8000/health >/dev/null && echo "✓ Backend OK" || echo "✗ Backend FAIL"

# Database (via backend)
curl -fsS http://localhost:8000/api/v1/families -H "Authorization: Bearer $TOKEN" >/dev/null && echo "✓ Database OK" || echo "✗ Database FAIL"
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

---

## Local Development Workflow

### First Time Setup
```bash
# 1. Ensure Docker daemon is running
docker --version

# 2. Build and start
docker compose build
docker compose up -d

# 3. Verify
docker compose ps
curl http://localhost:3000
curl http://localhost:8000/docs  # FastAPI OpenAPI
```

### Running Database Migrations
```bash
# Backend will run migrations on startup (if using Alembic)
# Manual migration (if needed):
docker compose exec backend alembic upgrade head
```

### Seeding Data (Dev Only)
```bash
docker compose exec backend python -m scripts.seed_dev
```

### Stopping Services
```bash
docker compose down
# Or, to also remove volumes (careful — data loss):
docker compose down -v
```

---

## Rollback Strategy

### v1 (Local Development)
Rollback is **not applicable** for local dev — just rebuild:
```bash
docker compose down -v
git checkout <previous-commit>
docker compose build
docker compose up -d
```

### v2+ (Production)
When production is deployed to AWS/Railway/etc., rollback strategy:
1. **Blue-Green Deployment:** Keep two full stacks running; switch load balancer to the old one.
2. **Database Migrations:** Only *forward* migrations allowed; rollback via schema versioning (Alembic).
3. **Image Tagging:** Tag each release with a git commit hash (e.g., `nestfi:2026-05-16-abc123def`).
4. **Rollback Playbook:** Document in `docs/delivery/ROLLBACK.md` once production is live.

For v1, we'll document this as a TBD post-release item.

---

## Security Notes (v1)

- **No HTTPS:** v1 uses plain HTTP on localhost. TLS termination will be handled by a reverse proxy (nginx, CloudFront, etc.) in production.
- **Exposed Ports:** DB and Redis are accessible from the host in dev for debugging. Firewall rules will restrict them in production.
- **Secrets:** `.env` is in `.gitignore` and never committed. Use a vault service (AWS Secrets Manager, HashiCorp Vault) in production.
- **Image Scanning:** Consider container scanning (Trivy, Snyk) in a pre-commit hook once production is online.

---

## Phase Gates (Release Checklist)

Before merging to `main` and running `docker compose up`:

- [ ] `reports/TEST_REPORT.md` exists with `VERDICT: PASS`
- [ ] No `OPEN_CRITICAL` or `OPEN_MAJOR` bugs in `reports/BUG_REPORT.md`
- [ ] Backend Dockerfile builds without errors
- [ ] Frontend Dockerfile builds without errors
- [ ] `docker compose up -d` starts all services without crashing
- [ ] All healthchecks pass (green in `docker compose ps`)
- [ ] Manual verification of all endpoints returns 200/success
- [ ] `docs/delivery/RUNNING_APP.md` written with live URLs

Once all checks pass, DELIVERY notifies the Orchestrator and the URL is relayed to the user.

---

## Known Limitations (v1)

| Limitation | v1 Status | v2+ Plan |
|-----------|-----------|---------|
| Single-host deployment | Docker Compose (localhost) | AWS ECS, Railway, Render, or k8s |
| No persistent logging | Local `docker compose logs` | CloudWatch, Datadog, or ELK Stack |
| No monitoring/alerting | N/A | Prometheus + Grafana or equivalent |
| No secrets vault | `.env.example` only | AWS Secrets Manager or HashiCorp Vault |
| No CI/CD pipeline | Manual build + test | GitHub Actions, GitLab CI, or Jenkins |

---

## Appendix: Dockerfile Conventions

### Backend (Python 3.12)
- **Multi-stage build:** `builder` (installs deps) → `runtime` (executes app)
- **Base image:** `python:3.12-slim` (minimal, ~150MB)
- **Entry point:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Healthcheck:** `curl -f http://localhost:8000/health`

### Frontend (Node 18)
- **Multi-stage build:** `builder` (npm install + next build) → `runtime` (next start)
- **Base image:** `node:18-alpine` (minimal, ~170MB)
- **Entry point:** `next start` (production Next.js server on port 3000)
- **Healthcheck:** `curl -f http://localhost:3000/`

Both will be created with proper optimization (pinned versions, non-root user, minimal dependencies).

---

## Next Steps

1. **Phase 4 (BUILD):** BE and FE produce Dockerfiles and source code.
2. **Phase 5 (TEST_AND_FIX):** QA runs test suite; DELIVERY validates via `docker compose build`.
3. **Phase 6 (DELIVERY):** DELIVERY executes `docker compose up --build -d`, writes `RUNNING_APP.md`, and notifies Orchestrator with the live URL.

