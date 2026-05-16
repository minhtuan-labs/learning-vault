# NestFi Deployment Guide

## Local Development

### Quick Start with Docker Compose

```bash
# Clone and setup
git clone <repo> nestfi
cd nestfi

# Create .env from template
cp .env.example .env
# Edit .env with your settings (optional for dev)

# Start all services
docker compose up --build

# Initialize database
docker exec nestfi_backend alembic upgrade head

# Seed superadmin account (in another terminal)
docker exec nestfi_backend python scripts/seed_superadmin.py

# Access the application
- Frontend: http://localhost:8050
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
```

### Manual Setup (without Docker)

```bash
# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env

# Configure database in .env
# Start PostgreSQL separately (locally or docker)

# Run migrations
alembic upgrade head

# Seed superadmin
python scripts/seed_superadmin.py

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend setup (in another terminal)
cd frontend
pip install -r requirements.txt
python app/main.py  # Runs on http://localhost:8050
```

## Environment Variables

```
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nestfi

# JWT
JWT_SECRET=your-secret-key-here

# Email/SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API URLs
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8050

# Debug
DEBUG=False
```

## Default Superadmin Credentials

After running `seed_superadmin.py`:
- Email: `admin@nestfi.local`
- Password: `changeme123`
- **IMPORTANT:** Change this password immediately in production!

## Production Deployment

### Prerequisites
- PostgreSQL 16 (managed service recommended: Railway, AWS RDS, etc.)
- Docker/Kubernetes cluster or VPS
- SMTP service (Gmail, SendGrid, AWS SES, etc.)
- Environment variables configured securely

### Docker Build

```bash
# Build images
docker build -t nestfi-backend ./backend
docker build -t nestfi-frontend ./frontend

# Run with docker compose
docker compose -f docker-compose.yml up -d
```

### Kubernetes Deployment (v2+)

```bash
# Create configmaps and secrets
kubectl create configmap nestfi-config --from-env-file=.env
kubectl create secret generic nestfi-secrets --from-literal=jwt_secret=your_secret

# Deploy
kubectl apply -f k8s/
```

## Database Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

```bash
# Run all tests
pytest backend/tests/

# With coverage
pytest --cov=app backend/tests/

# Specific test
pytest backend/tests/test_auth.py::test_login_success
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/
# Response: {"status": "ok", "version": "1.0", "timestamp": "..."}
```

### API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Troubleshooting

### Database Connection Issues
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check credentials and permissions
- Ensure database exists

### JWT Token Issues
- Verify JWT_SECRET is set
- Check token expiry (24 hours default)
- Frontend should send `Authorization: Bearer <token>` header

### Email Not Sending
- Verify SMTP credentials
- Check SMTP_HOST and SMTP_PORT
- For Gmail: use App Password, not regular password
- Check spam folder

### CORS Issues
- Verify frontend URL in CORS settings (app/main.py)
- Check `Authorization` header is in allowed headers
- Browser dev tools → Network tab to see CORS errors

## Performance Optimization (v2+)

- Add Redis caching layer
- Implement request rate limiting
- Use CDN for static assets
- Add database query caching
- Implement async job queue (Celery/RQ)

## Security Checklist

- [ ] Change default superadmin password
- [ ] Set strong JWT_SECRET
- [ ] Enable HTTPS/TLS in production
- [ ] Use managed PostgreSQL (encrypted at rest)
- [ ] Configure CORS properly
- [ ] Enable database backups
- [ ] Implement logging/monitoring
- [ ] Use environment variables (never hardcode secrets)
- [ ] Regular security updates

## Support

For issues and questions:
1. Check API documentation at `/docs`
2. Review logs in `.pane_logs/`
3. Run tests to verify setup
4. Check deployment guide above
