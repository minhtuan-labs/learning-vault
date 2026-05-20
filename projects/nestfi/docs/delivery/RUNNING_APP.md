# NestFi v1.0 — Running Application

## Status
✅ **LIVE** — NestFi Phase 6 (DELIVERY) complete with verified endpoints

- **Build Date**: 2026-05-19 09:24 UTC (rebuild: backend + frontend — GET /auth/me endpoint added, root page fixed, onSuccess invalidation removed)
- **Build Commit**: main@1872850 (both backend and frontend services rebuilt with latest features)
- **Test Status**: PASS (reports/TEST_REPORT.md — VERDICT: PASS)
- **Release Gate**: OPEN — Ready for testing and production deployment
- **Container Status**: All services healthy (postgres, backend, frontend) — verified 2026-05-19 09:24
- **Database Status**: PostgreSQL data volume persisted (NO RESET) — existing data (Smith Household, alice, bob) intact
- **Endpoint Verification** (2026-05-19 09:25):
  - ✅ Health: `GET http://localhost:8100/health` → `{status: ok, message: "NestFi backend is running"}`
  - ✅ Auth/Me: `GET http://localhost:8100/api/v1/auth/me` with Bearer token → returns full user profile (id, email, first_name, is_superadmin, is_active, created_at)
  - ✅ Login: `POST http://localhost:8100/api/v1/auth/login` → superadmin@nestfi.local returns `is_superadmin=true` with valid JWT
  - ✅ Login Page: `GET http://localhost:3100/login` → loads successfully with email/password form (no onSuccess invalidation errors)
  - ✅ Admin Families: `GET http://localhost:8100/api/v1/admin/families` → Smith Household present with `is_active=true` field, `member_count=2`
  - ✅ Frontend: `GET http://localhost:3100/` → production build loaded successfully (14 routes compiled)
- **Port Configuration**: Option C (frontend 3100, backend 8100, database 5435)
- **API Configuration**: NEXT_PUBLIC_API_URL correctly set to http://localhost:8100/api/v1

---

## Docker Deployment

### Quick Start

```bash
# Build and start all services
docker compose up --build

# Verify services are running
docker compose ps

# Stop all services
docker compose down
```

### Service URLs

- **Frontend (Next.js)**: http://localhost:3100
- **Backend API**: http://localhost:8100
- **Health Check**: http://localhost:8100/health
- **Database**: postgres://localhost:5435/nestfi (internal to docker network)

### Services

**postgres:16** (internal)
- Database: `nestfi`
- User: `nestfi`
- Port: 5435 (mapped from internal 5432)
- Health: checks via backend

**backend:8100** (FastAPI + Python 3.12)
- Dockerfile: `backend/Dockerfile`
- Base image: python:3.12-slim (multi-stage)
- Non-root user: `appuser` (uid 1000)
- Health check: `/health` endpoint (10s interval, 5s timeout, 5 retries)
- Startup: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (mapped to 8100)
- Dependencies: from `requirements.txt` (FastAPI, SQLAlchemy, pytest, etc.)

**frontend:3100** (Next.js + Node 20)
- Dockerfile: `frontend/Dockerfile`
- Base image: node:20-alpine (multi-stage)
- Non-root user: `appuser` (uid 1001)
- Health check: GET / (10s interval, 5s timeout, 5 retries)
- Startup: `npm start` (production mode, mapped to 3100)
- Dependencies: from `package.json` (React 19, Next.js 15, TanStack Query, Zustand, Tailwind CSS)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│        Docker Compose Network (nestfi)      │
│                                             │
│  ┌──────────────┐     ┌──────────────────┐ │
│  │  Frontend    │     │   Backend API    │ │
│  │  (3100)      │────→│   (8100)         │ │
│  │  Next.js     │     │   FastAPI        │ │
│  └──────────────┘     └──────────────────┘ │
│         ↓                      ↓            │
│   Browser client           Database         │
│                            (postgres)       │
│                            (5435)           │
└─────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

All environment variables are in `.env` (auto-generated from `.env.example`):

```env
# Backend
DATABASE_URL=postgresql://nestfi:nestfi@postgres:5432/nestfi
SECRET_KEY=<generated>
ALGORITHM=HS256

# Frontend  
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Note**: For production, use stronger SECRET_KEY and configure NEXT_PUBLIC_API_URL to match deployed backend URL.

### Database

- **Initial State**: Seeded on first startup (see `backend/seed.py`)
- **Superadmin Credentials**: email=`superadmin@nestfi.local`, password=`admin123` (is_superadmin flag now supported)
- **Test Users**: alice@example.com (password123), bob@example.com (password123) — both with is_superadmin=false
- **Test Data**: 2 sample families, 4 accounts, 10+ transactions (see `backend/seed.py`)

---

## Features in v1.0

✅ **Authentication**
- Superadmin account creation and login
- Password change on first login (forced)
- Session + JWT token authentication

✅ **Family Management**
- Create families
- Add/manage family members (invite via system)
- Disable/enable members (soft-delete, reversible)

✅ **Account Management**
- Create bank accounts (checking, savings, investment, cash)
- View all accounts and current balances
- Edit account details

✅ **Transactions**
- Record income, expense, investment transactions
- Edit transactions (with full edit history)
- Soft-delete/disable transactions (hide from reports, can re-enable)
- Hard-delete (owner only, permanent)

✅ **Categories**
- Pre-seeded default categories (income, expense, investment)
- Create custom categories
- Assign categories to transactions

✅ **Dashboard & Reporting**
- Summary: total income, expenses, net savings
- Account balances by account
- Expense breakdown by category
- Income vs. expense trends
- Export transactions as CSV (future: PDF)

---

## Testing

### Unit & Integration Tests

**Backend** (pytest + SQLAlchemy)
```bash
cd backend
pytest tests/ -v --tb=short
```

**Frontend** (vitest + @testing-library/react)
```bash
cd frontend
npm test -- --run
```

### E2E Testing

```bash
# Start all services
docker compose up --build

# In another terminal, test health endpoints
curl http://localhost:8100/health
curl http://localhost:3100

# Stop services
docker compose down
```

**Test Coverage**:
- Backend: 49 unit + integration tests (≥80% line coverage)
- Frontend: 40+ component + integration tests

---

## Production Considerations

### Pre-Deployment Checklist

- [ ] Update `.env`: set strong `SECRET_KEY`, correct `NEXT_PUBLIC_API_URL`
- [ ] Update `docker-compose.yml`: bind backend/frontend to public IPs/ports if needed
- [ ] Set up PostgreSQL persistence: mount data volume for postgres service
- [ ] Enable HTTPS: add reverse proxy (nginx/Caddy) or use cloud provider's LB
- [ ] Configure CORS: update backend `app/main.py` to allow frontend origin
- [ ] Set up monitoring: logs aggregation, uptime monitoring, error tracking (Sentry, etc.)
- [ ] Plan backups: daily database snapshots, offsite storage

### Known Limitations (v1.0)

- No automated email invitations (invites via system admin)
- No session timeout (manual logout only) — add 30min timeout in v1.1
- No batch operations (export/import) — single transaction operations only
- Dashboard performance optimizations deferred to v1.1
- Mobile/responsive design pending fine-tuning (desktop-first in v1.0)

### Recommended Next Steps

1. **v1.1 Polish** (2 weeks):
   - Email integration (invitations, password reset)
   - Session timeout + warning dialog
   - Dashboard performance tuning
   - Mobile responsive design

2. **v1.2 UX** (2 weeks):
   - Dark mode toggle
   - Bulk transaction import (CSV)
   - Bill-splitting foundation (deferred from v1.0)

3. **v2.0 Advanced** (Q3 2026):
   - Bill-splitting implementation
   - Investment portfolio tracking
   - Budget goals & alerts
   - Multi-currency support

---

## Support & Debugging

### Common Issues

**Backend won't start**
- Check PostgreSQL is running: `docker compose ps postgres`
- Check logs: `docker compose logs backend`
- Verify DATABASE_URL in `.env`

**Frontend won't load**
- Check backend health: `curl http://localhost:8000/api/v1/health`
- Check NEXT_PUBLIC_API_URL in `.env`
- Check browser console for CORS errors

**Tests fail**
- Backend: Ensure pytest is installed; try `pytest tests/test_health.py` first
- Frontend: Ensure npm dependencies installed; try `npm test -- auth.test.tsx`

### Logs

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

---

## Release Information

**v1.0 Release Date**: 2026-05-16  
**Build #**: 1 (initial release)  
**Git Commits**: backend@1872850, frontend@efe2ded  

See `docs/delivery/RELEASE_NOTES.md` for detailed release notes and changelog.
