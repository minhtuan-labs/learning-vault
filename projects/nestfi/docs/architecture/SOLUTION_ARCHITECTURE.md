# Solution Architecture — NestFi

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** SA  

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Browser                            │
│              (Desktop / Tablet Responsive)                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frontend Layer                            │
│            Dash (Plotly) + Tailwind CSS                     │
│          (http://localhost:8050 — v1)                      │
├─────────────────────────────────────────────────────────────┤
│ • Authentication pages (login, password reset)              │
│ • Family selector / dashboard switcher                      │
│ • Financial dashboard (charts, analytics)                   │
│ • Transaction ledger (add, edit, delete, filter)            │
│ • Category management (CRUD)                                │
│ • Family member management                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (JSON)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway                               │
│              FastAPI + CORS Middleware                      │
│          (http://localhost:8000 — v1)                      │
├─────────────────────────────────────────────────────────────┤
│ • Request validation (Pydantic schemas)                      │
│ • JWT authentication & authorization                        │
│ • Rate limiting (deferred to v2)                            │
│ • OpenAPI docs (/docs, /redoc)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                ┌────┴─────┬───────────────┐
                ▼          ▼               ▼
        ┌────────────┐ ┌──────────┐ ┌────────────┐
        │   Auth     │ │ Financial│ │  Family &  │
        │  Routes    │ │  Routes  │ │   Config   │
        │ (JWT/user) │ │(trans.)  │ │   Routes   │
        └────┬───────┘ └────┬─────┘ └────┬───────┘
             │              │            │
             └──────┬───────┴────────────┘
                    ▼
         ┌──────────────────────┐
         │  Service Layer       │
         │  (Business Logic)    │
         ├──────────────────────┤
         │ • AuthService        │
         │ • TransactionService │
         │ • FamilyService      │
         │ • CategoryService    │
         │ • EmailService       │
         └──────┬───────────────┘
                │
                ▼
         ┌──────────────────────┐
         │   Data Access        │
         │ (SQLAlchemy ORM)     │
         └──────┬───────────────┘
                │
                ▼
         ┌──────────────────────┐
         │  PostgreSQL 16       │
         │   (Persistence)      │
         │ • Users & Auth       │
         │ • Families & Members │
         │ • Transactions       │
         │ • Categories         │
         │ • Audit logs         │
         └──────────────────────┘
```

---

## Component Breakdown

### Frontend: Dash + Tailwind

**Purpose:** Browser-based UI for family financial management  
**Framework:** Dash (Python Plotly reactive web framework)  
**Styling:** Tailwind CSS (utility-first)

**Key Pages:**
1. **Auth Pages**
   - Login (email/password)
   - Password reset flow
   - Invitation acceptance (owner / member)
   - Account setup

2. **Dashboard**
   - Family selector (dropdown / sidebar)
   - Financial overview (income, expenses, savings)
   - Category breakdown chart (pie/bar)
   - Monthly trends (line chart)
   - Member activity log

3. **Ledger / Transactions**
   - Transaction history (paginated, filterable)
   - Add transaction form (income/expense/cash)
   - Edit transaction (own or owner)
   - Delete transaction (confirm)
   - Filter by date range, category, member

4. **Category Management**
   - List all categories (income, expense, investment)
   - Add new category
   - Edit category (name, description, color)
   - Archive / reactivate category

5. **Family Settings**
   - Family profile (name, description)
   - Member list (name, email, role, status)
   - Invite new members
   - Remove members

**API Integration:**
- REST client built in utils; wraps `requests` library
- JWT token stored in browser session / localStorage
- Requests include `Authorization: Bearer <token>` header
- Error handling: show toast/alert on 4xx/5xx

---

### Backend: FastAPI

**Purpose:** REST API for all business logic and data access  
**Framework:** FastAPI (async Python web framework)  
**Server:** Uvicorn (ASGI server)

**Layer Structure:**

```
app/
├── main.py                  # FastAPI() instance, middleware, startup hooks
├── config.py                # Settings (DB URL, JWT secret, CORS, etc.)
├── models/
│   ├── user.py              # User, UserRole
│   ├── family.py            # Family, FamilyMember
│   ├── transaction.py       # Transaction, TransactionType
│   ├── category.py          # Category, CategoryType
│   └── audit.py             # AuditLog
├── schemas/                 # Pydantic models for request/response
│   ├── user.py
│   ├── family.py
│   ├── transaction.py
│   ├── category.py
│   └── common.py            # ErrorResponse, PaginationParams, etc.
├── crud/                    # Create, Read, Update, Delete operations
│   ├── user.py
│   ├── family.py
│   ├── transaction.py
│   ├── category.py
│   └── base.py              # Base CRUD class
├── api/
│   ├── dependencies.py      # get_current_user, get_db, etc.
│   └── routes/
│       ├── auth.py          # POST /auth/login, /auth/register, /auth/refresh
│       ├── users.py         # GET /users/me, POST /users/change-password
│       ├── families.py      # GET/POST families, CRUD family members
│       ├── transactions.py  # GET/POST/PUT/DELETE transactions
│       ├── categories.py    # GET/POST/PUT/DELETE categories
│       ├── admin.py         # POST /admin/families (superadmin only)
│       └── health.py        # GET / (health check)
├── services/                # Business logic (not just CRUD)
│   ├── auth_service.py      # Validate credentials, issue JWT
│   ├── email_service.py     # Send invitations, password resets
│   ├── family_service.py    # Family setup, member invitations
│   ├── transaction_service.py # Income/expense/cash logic
│   └── category_service.py  # Category defaults, archival
├── utils/
│   ├── security.py          # Hash password, verify JWT
│   ├── email.py             # SMTP client wrapper
│   └── exceptions.py        # Custom exception classes
└── static/
    └── uploads/             # User-uploaded images (CDN-ready structure)
```

**Key Routes:**

| Endpoint | Method | Purpose | Auth |
|---|---|---|---|
| `/auth/login` | POST | Email + password → JWT token | None |
| `/auth/register` (deferred v2) | POST | New user signup | None |
| `/users/me` | GET | Current user profile | Required |
| `/users/{id}/change-password` | POST | Update password | Required |
| `/families` | GET | List user's families | Required |
| `/families` | POST | Create family (owner only) | Required |
| `/families/{id}` | GET | Family details + members | Required |
| `/families/{id}/members` | GET | List family members | Required |
| `/families/{id}/members` | POST | Invite member | Owner |
| `/families/{id}/members/{member_id}` | DELETE | Remove member | Owner |
| `/families/{id}/categories` | GET | List family categories | Required |
| `/families/{id}/categories` | POST | Create category | Owner |
| `/families/{id}/categories/{cat_id}` | PUT | Update category | Owner |
| `/families/{id}/categories/{cat_id}` | DELETE | Archive category | Owner |
| `/families/{id}/transactions` | GET | List transactions (paginated, filterable) | Required |
| `/families/{id}/transactions` | POST | Add transaction | Required |
| `/families/{id}/transactions/{txn_id}` | PUT | Edit transaction | Owner or author |
| `/families/{id}/transactions/{txn_id}` | DELETE | Delete transaction | Owner or author |
| `/admin/families` | POST | Create family + invite owner | Superadmin |
| `/health` | GET | Health check | None |

---

### Database: PostgreSQL 16

**Purpose:** Persistent storage for all app data

**Schema Overview:**

```sql
-- Users & Auth
users
├─ id (PK)
├─ email (UNIQUE)
├─ password_hash
├─ full_name
├─ role (superadmin, owner, member)
├─ created_at
├─ updated_at
└─ is_active

-- Families & Membership
families
├─ id (PK)
├─ name
├─ description
├─ currency (v1: default 'USD', all transactions in family currency)
├─ created_at
└─ updated_at

family_members
├─ id (PK)
├─ family_id (FK → families)
├─ user_id (FK → users)
├─ role (owner, member, view_only [v2])
├─ joined_at
└─ status (active, pending, declined)

invitations
├─ id (PK)
├─ email
├─ family_id (FK → families)
├─ token (unique, for email link)
├─ invited_by_user_id (FK → users)
├─ status (pending, accepted, declined)
├─ expires_at
├─ created_at
└─ updated_at

-- Transactions
transactions
├─ id (PK)
├─ family_id (FK → families)
├─ user_id (FK → users) [who logged it]
├─ category_id (FK → categories)
├─ type (income, expense, cash_withdrawal)
├─ amount (decimal)
├─ description (optional)
├─ transaction_date
├─ created_at
├─ updated_at
├─ deleted_at (soft delete)
└─ deleted_by (FK → users, if soft deleted)

-- Categories
categories
├─ id (PK)
├─ family_id (FK → families)
├─ type (income, expense, investment)
├─ name
├─ description (optional)
├─ color (hex, e.g., '#FF5733')
├─ icon (optional, e.g., 'utensils')
├─ is_default (system default)
├─ is_active
├─ created_at
└─ updated_at

-- Audit Trail
audit_logs
├─ id (PK)
├─ user_id (FK → users)
├─ entity_type (user, family, transaction, category)
├─ entity_id
├─ action (create, update, delete)
├─ old_values (JSON, for updates)
├─ new_values (JSON)
├─ timestamp
└─ ip_address (optional)
```

**Key Constraints:**
- Foreign keys cascade delete (except audit logs)
- Soft deletes on transactions for audit trail
- Unique (family_id, category_id, type) for default categories
- Check constraint: `amount > 0`
- Indexes on: user_id, family_id, transaction_date, category_id (for query performance)

---

## Data Flow: Core Use Cases

### UC1: User logs in and views family dashboard

```
1. Frontend: POST /auth/login { email, password }
   ↓
2. Backend: Hash password, compare to user.password_hash
   ├─ Success → Generate JWT (sub=user_id, exp=24h)
   ├─ Return { token, user { id, email, full_name } }
   └─ Failure → Return 401 Unauthorized
   ↓
3. Frontend: Store JWT in session/localStorage
   GET /families { Authorization: Bearer <token> }
   ↓
4. Backend: Verify JWT, extract user_id
   Query: SELECT * FROM families f
           JOIN family_members fm ON f.id = fm.family_id
           WHERE fm.user_id = ? AND fm.status = 'active'
   Return [{ id, name, ... }, ...]
   ↓
5. Frontend: User selects family
   GET /families/{id} { Authorization: Bearer <token> }
   ↓
6. Backend: Verify user is member of family (check family_members)
   Query dashboard data:
   ├─ SELECT SUM(amount) FROM transactions WHERE family_id=? AND type='income'
   ├─ SELECT SUM(amount) FROM transactions WHERE family_id=? AND type='expense'
   ├─ SELECT category_id, SUM(amount) FROM transactions ... GROUP BY category_id
   └─ Return dashboard_data
   ↓
7. Frontend: Render dashboard with charts
```

### UC2: Family member logs an expense

```
1. Frontend: POST /families/{family_id}/transactions
   { type: 'expense', category_id: 5, amount: 25.50, description: 'groceries', transaction_date: '2026-05-16' }
   Authorization: Bearer <token>
   ↓
2. Backend: Verify JWT, get user_id
   ├─ Check: user is member of family
   ├─ Validate: category_id belongs to family AND type matches
   ├─ Validate: amount > 0
   ├─ Create transaction record (INSERT)
   ├─ Log audit entry: { user_id, entity_type: 'transaction', action: 'create', ... }
   └─ Return transaction { id, category_id, amount, ... }
   ↓
3. Frontend: Show confirmation toast, refresh ledger
   GET /families/{family_id}/transactions (with pagination, filters)
   ↓
4. Backend: Query all transactions for family (excluding soft-deleted)
   Return [{ id, category, amount, user, date, ... }, ...]
   ↓
5. Frontend: Update transaction list on screen
```

### UC3: Owner invites a family member

```
1. Frontend: POST /families/{family_id}/members
   { email: 'spouse@example.com' }
   Authorization: Bearer <token>
   ↓
2. Backend: Verify JWT, check user is OWNER of family
   ├─ Create invitation record { email, family_id, token=uuid4(), expires_at=now+30d, status='pending' }
   ├─ Compose email: "Hi spouse@example.com, you've been invited to NestFi family 'Smith Household'. Click: <base_url>/invitations/<token>"
   ├─ Send email via SMTP
   ├─ Log audit
   └─ Return { invitation_id, status, expires_at }
   ↓
3. Frontend: Show confirmation "Invitation sent to spouse@example.com"
   ↓
4. Recipient receives email (5-min SLA)
   ↓
5. Recipient clicks link → Frontend: GET /invitations/<token>
   (if not logged in, show "Sign up or log in to accept")
   ↓
6. Recipient submits acceptance form → POST /invitations/<token>/accept
   { password: '...', full_name: '...' } (if new user) OR { } (if existing user)
   ↓
7. Backend: Validate token (not expired, exists, status='pending')
   ├─ If new user: CREATE user record
   ├─ CREATE family_members { family_id, user_id, status='active' }
   ├─ UPDATE invitation { status='accepted' }
   ├─ Log audit
   └─ Return { success: true, family_name: 'Smith Household' }
   ↓
8. Frontend: Redirect to login (new user) or to family dashboard (existing user)
```

---

## Security & Authorization Model

### Authentication: JWT Tokens

- **Issuer:** Backend `/auth/login`
- **Algorithm:** HS256 (secret in `JWT_SECRET` env var)
- **Payload:**
  ```json
  {
    "sub": "user_id",
    "email": "user@example.com",
    "role": "owner|member|superadmin",
    "iat": 1234567890,
    "exp": 1234567890 + 86400
  }
  ```
- **Verification:** Every protected endpoint checks signature + expiration

### Authorization: Role-Based Access Control (RBAC)

| Action | Superadmin | Owner | Member | ViewOnly (v2) |
|---|---|---|---|---|
| Create family | ✓ | — | — | — |
| Invite owner | ✓ | — | — | — |
| Edit family settings | ✓ (any) | ✓ (own) | — | — |
| View members | ✓ | ✓ | ✓ | ✓ |
| Invite members | ✓ | ✓ | — | — |
| Remove members | ✓ | ✓ | — | — |
| View transactions | ✓ | ✓ | ✓ | ✓ |
| Log transaction | ✓ | ✓ | ✓ | — |
| Edit own transaction | ✓ | ✓ | ✓ | — |
| Edit any transaction | ✓ | ✓ | — | — |
| Delete own transaction | ✓ | ✓ | ✓ | — |
| Delete any transaction | ✓ | ✓ | — | — |
| Create category | ✓ | ✓ | — | — |
| Edit category | ✓ | ✓ | — | — |
| Archive category | ✓ | ✓ | — | — |

### Endpoint Protection Pattern

```python
@router.get("/families/{family_id}/transactions")
async def get_transactions(
    family_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check: user is member of family
    membership = db.query(FamilyMember).filter(
        FamilyMember.family_id == family_id,
        FamilyMember.user_id == current_user.id,
        FamilyMember.status == 'active'
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this family")
    
    # Query and return transactions
    transactions = db.query(Transaction).filter(
        Transaction.family_id == family_id,
        Transaction.deleted_at.is_(None)
    ).all()
    
    return transactions
```

---

## Deployment Architecture (v1)

```
┌────────────────────────────────────────────┐
│     Host / VPS / Docker Machine             │
├────────────────────────────────────────────┤
│  docker-compose up -d                      │
│                                             │
│  ┌──────────────────────────────────┐      │
│  │  PostgreSQL 16 Container         │      │
│  │  (port 5432 internal)            │      │
│  │  Volume: postgres_data (persist) │      │
│  └──────────────────────────────────┘      │
│                    ▲                        │
│                    │ (DB conn)              │
│                    │                        │
│  ┌──────────────────────────────────┐      │
│  │  FastAPI Backend Container       │      │
│  │  (Uvicorn, port 8000)            │      │
│  │  ENV: DATABASE_URL, JWT_SECRET   │      │
│  └──────────────────────────────────┘      │
│          ▲                                  │
│          │ (REST API)                       │
│          │                                  │
│  ┌──────────────────────────────────┐      │
│  │  Dash Frontend Container         │      │
│  │  (port 8050)                     │      │
│  │  ENV: API_BASE_URL=http://...    │      │
│  └──────────────────────────────────┘      │
│          ▲                                  │
│          │ (HTTP port 8050)                 │
│          │                                  │
└────────────────────────────────────────────┘
                    ▲
                    │ (user browser)
                    │
         [Internet / user's machine]
```

---

## Migration Path: v1 → v2+ (Scalability)

### What Changes
1. **Database:** Managed PostgreSQL (Railway, AWS RDS, Supabase)
   - ✓ No code change; just update `DATABASE_URL`

2. **Frontend + Backend:** Containerized on Kubernetes or managed platform (Fly.io, Railway, etc.)
   - ✓ Docker images already built; just push to registry

3. **Image storage:** From filesystem → AWS S3 / Cloudflare R2
   - ✓ Filesystem path structure is CDN-ready; update service to use S3 SDK

4. **Email:** From local SMTP → SendGrid / AWS SES
   - ✓ Abstraction layer (EmailService) already in place

5. **Reverse proxy:** Add Nginx / AWS ALB for HTTPS + load balancing
   - ✓ Stateless backend (JWT) allows multiple instances

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | SA | Created SOLUTION_ARCHITECTURE.md with detailed system design, components, and data flow for Python stack |
