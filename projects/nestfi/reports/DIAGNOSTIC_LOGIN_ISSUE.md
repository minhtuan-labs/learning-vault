# Login Failure Diagnostic Report
**Date**: 2026-05-18 08:50  
**Issue**: Login fails with "Login failed" message on frontend  
**Severity**: CRITICAL

## Diagnostic Findings

### 1. Backend Endpoint Status ✓ WORKING
- **Endpoint**: POST http://localhost:8100/api/v1/auth/login
- **Test credentials**: admin@example.com / admin123
- **Response Code**: 200 OK
- **Response Body**: Valid JWT token + user object
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "536e2356-6a4d-4325-a4f0-bff06c1bb748",
    "email": "admin@example.com",
    "first_name": "Admin"
  }
}
```

### 2. Docker Container Status ✓ ALL HEALTHY
- nestfi_backend: Up 26 hours (healthy)
- nestfi_frontend: Up 26 hours (healthy)
- nestfi_postgres: Up 26 hours (healthy)

### 3. Frontend Configuration ❌ MISCONFIGURED
**Root Cause**: Frontend uses localhost:8100 API endpoint, which fails inside Docker

**Details**:
- Frontend `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8100/api/v1`
- Frontend Dockerfile: Does NOT set NEXT_PUBLIC_API_URL as build argument
- Frontend container network: Isolated Docker network (not host network)
- When frontend makes request: `localhost:8100` resolves to 127.0.0.1 inside container
- But backend service is on `http://nestfi_backend:8000` (Docker service name)

**Why it fails**:
1. Frontend calls: `http://localhost:8100/api/v1/auth/login` (from browser perspective via localhost:3100)
2. Browser tries to reach: `http://localhost:8100` ← fails (frontend can't reach host's 8100 from container)
3. This creates a CORS error or network timeout
4. Frontend error handler catches exception and shows "Login failed"

### 4. CORS Configuration (Secondary)
- Backend allows: `http://localhost:3100` (correct for host access)
- BUT: Frontend in Docker container makes requests from `http://nestfi_frontend:3000` internally
- This might be OK since browser requests come from localhost:3100, but API requests fail at network layer first

## Solution Required

Fix frontend environment variable handling for Docker:

**Option A (Recommended)**: Use ARG in Dockerfile to set API_URL at build time
```dockerfile
ARG NEXT_PUBLIC_API_URL=http://localhost:8100/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
```

Update docker-compose.yml:
```yaml
frontend:
  build:
    context: ./frontend
    args:
      NEXT_PUBLIC_API_URL: http://nestfi_backend:8000/api/v1
```

**Option B**: Keep .env.local for local dev, add .env.docker or use environment variable substitution in runtime

## Files Affected
- `frontend/Dockerfile` — needs ARG/ENV for NEXT_PUBLIC_API_URL
- `docker-compose.yml` — frontend service needs build args
- Possibly: `frontend/.env.local` — might need conditional logic

## Next Steps
Route FE engineer to:
1. Update Dockerfile to accept NEXT_PUBLIC_API_URL as build argument
2. Update docker-compose.yml to pass correct API URL to frontend build
3. Test login flow end-to-end after rebuild
