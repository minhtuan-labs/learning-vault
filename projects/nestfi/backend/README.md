# NestFi Backend

FastAPI REST API for NestFi family finance management application.

## Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure:
- DATABASE_URL
- JWT_SECRET
- SMTP settings

### Database

```bash
# Initialize database
alembic upgrade head
```

### Running

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST /auth/login
- GET /auth/me

### Users
- POST /users/change-password

### Families
- GET /families
- GET /families/{id}
- POST /families (superadmin only)
- PUT /families/{id}
- GET /families/{id}/members
- POST /families/{id}/members
- DELETE /families/{id}/members/{member_id}

### Invitations
- POST /invitations/{token}/accept
- POST /invitations/{token}/decline

### Transactions
- GET /families/{id}/transactions
- POST /families/{id}/transactions
- PUT /families/{id}/transactions/{txn_id}
- DELETE /families/{id}/transactions/{txn_id}

### Categories
- GET /families/{id}/categories
- POST /families/{id}/categories
- PUT /families/{id}/categories/{cat_id}
- DELETE /families/{id}/categories/{cat_id}

### Analytics
- GET /families/{id}/analytics/summary
- GET /families/{id}/analytics/trends

### Admin
- POST /admin/families (superadmin only)

## Testing

```bash
pytest tests/
```

## Architecture

- **Models**: SQLAlchemy ORM models with TimestampMixin
- **Schemas**: Pydantic validation schemas
- **CRUD**: Database operations layer
- **Services**: Business logic
- **Routes**: FastAPI endpoint definitions
- **Utils**: Security, exceptions, helpers

## Security

- Passwords hashed with bcrypt
- JWT tokens (HS256, 24h expiry)
- Role-based access control (RBAC)
- Soft deletes for transactions
- Audit logging

## Tech Stack

- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Alembic 1.12.1
- PostgreSQL 16
- Pydantic 2.5.0
- PyJWT 1.2.0
- Passlib + bcrypt
