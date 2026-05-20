# NestFi Backend

FastAPI-based backend for the NestFi family budgeting application.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (for containerized setup)

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database:**
   ```bash
   # Create PostgreSQL database
   createdb nestfi
   
   # Run migrations (when ready)
   alembic upgrade head
   ```

3. **Run development server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Access API documentation:**
   - Swagger UI: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc

## Docker Compose

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on `localhost:5432`
- FastAPI server on `localhost:8000`

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── database.py       # SQLAlchemy setup
│   ├── dependencies.py   # Auth dependencies
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic schemas
│   ├── routes/           # API endpoints
│   └── utils/            # Security, hashing, etc.
├── tests/                # Pytest test suite
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## Key Endpoints

- `GET /health` — Health check
- `POST /api/v1/auth/login` — User authentication
- `GET /api/v1/families` — List user's families
- `GET /api/v1/families/{id}` — Get family details
- `GET /api/v1/families/{id}/accounts/{account_id}/transactions` — List transactions
- `POST /api/v1/families/{id}/accounts/{account_id}/transactions` — Create transaction

## Testing

```bash
pytest
pytest tests/ -v  # Verbose
pytest tests/test_auth.py  # Specific file
```

## Status

**Phase 4_BUILD** - Initial FastAPI scaffold with working structure:
- ✅ FastAPI app setup
- ✅ SQLAlchemy models (User, Family, Account, Transaction, etc.)
- ✅ Basic authentication (JWT)
- ✅ Priority endpoints (health, login, families, transactions)
- 🔄 Full business logic implementation
- 🔄 Comprehensive test coverage
- 🔄 Database migrations

See `docs/architecture/API_CONTRACT.md` for full endpoint specifications.
