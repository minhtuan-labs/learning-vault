# API Contract — NestFi

**Status:** DRAFT (ready for BE/FE review)

This document specifies all REST API endpoints, request/response schemas, and authorization rules for NestFi v1.

## API Principles

- **Base URL:** `http://localhost:8000/api/v1` (development) or `https://api.nestfi.example.com/api/v1` (production)
- **Format:** JSON request/response bodies
- **Versioning:** All endpoints under `/api/v1/` prefix
- **Documentation:** Auto-generated OpenAPI spec at `GET /api/v1/docs` (Swagger UI)
- **Authentication:** Session cookie (web) or JWT Bearer token (API clients)
- **Authorization:** Family-scoped; user must be a member of the family in the URL path
- **Errors:** Standard HTTP status codes + JSON error object (see Error Handling)

---

## Authentication Endpoints

### POST /auth/register

Register a new user account. Used by:
- Superadmin inviting an owner (owner creates account via confirmation link)
- Members accepting family invitation (creates account if not exists)

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "secure_password",
  "first_name": "Alice",
  "last_name": "Smith"
}
```

**Response (201 Created):**
```json
{
  "id": "user-123",
  "email": "alice@example.com",
  "first_name": "Alice",
  "last_name": "Smith",
  "created_at": "2026-05-16T12:00:00Z"
}
```

**Status Codes:**
- `201 Created` — Account created successfully
- `400 Bad Request` — Invalid input (email already exists, password too weak, etc.)
- `422 Unprocessable Entity` — Validation error (missing field)

---

### POST /auth/login

Authenticate user and create session. Returns session cookie (for browser) or JWT token (for API).

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "secure_password"
}
```

**Response (200 OK) — Browser:**
Sets `session` cookie (httpOnly, Secure, SameSite=Strict) and responds:
```json
{
  "user": {
    "id": "user-123",
    "email": "alice@example.com",
    "first_name": "Alice"
  },
  "families": [
    { "id": "fam-1", "name": "Smith Household" }
  ]
}
```

**Response (200 OK) — API Token:**
If client requests JWT (header `Accept: application/json` or flag), returns:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { ... }
}
```

**Status Codes:**
- `200 OK` — Login successful
- `401 Unauthorized` — Invalid email/password

**Cookie Details (Session):**
- `HttpOnly=true` (JavaScript cannot access)
- `Secure=true` (HTTPS only, not HTTP)
- `SameSite=Strict` (CSRF protection)
- `Max-Age=1800` (30 minutes default)

---

### POST /auth/logout

Terminate session / invalidate token.

**Request:**
```
(No body; session cookie included automatically by browser)
```

**Response (200 OK):**
```json
{ "message": "Logged out successfully" }
```

Clears `session` cookie on client side.

---

### POST /auth/request-password-reset

Request a password reset email (mock: print token to logs).

**Request:**
```json
{
  "email": "alice@example.com"
}
```

**Response (202 Accepted):**
```json
{
  "message": "If an account with that email exists, a reset link has been sent."
}
```

**Notes:**
- Always returns 202 regardless of whether email exists (prevents email enumeration)
- Reset token stored in DB with 1-hour expiration
- v1: Token printed to logs for testing
- v2: Sent via email (Sendgrid, etc.)

---

### POST /auth/reset-password

Set new password using reset token.

**Request:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "new_secure_password"
}
```

**Response (200 OK):**
```json
{ "message": "Password reset successfully" }
```

**Status Codes:**
- `200 OK` — Password changed
- `400 Bad Request` — Token expired or invalid
- `422 Unprocessable Entity` — Password validation failed

---

## Family Management Endpoints

### GET /families

List all families the user is a member of.

**Request:**
```
GET /api/v1/families
(authenticated; session or JWT)
```

**Response (200 OK):**
```json
{
  "families": [
    {
      "id": "fam-1",
      "name": "Smith Household",
      "owner_id": "user-123",
      "role": "owner",
      "created_at": "2026-05-14T10:00:00Z"
    },
    {
      "id": "fam-2",
      "name": "Extended Family",
      "owner_id": "user-456",
      "role": "member",
      "created_at": "2026-05-15T14:30:00Z"
    }
  ]
}
```

---

### POST /families

Create a new family. Only superadmin or invited owners.

**Request:**
```json
{
  "name": "Johnson Household",
  "invitation_token": "token-from-superadmin"
}
```

**Response (201 Created):**
```json
{
  "id": "fam-3",
  "name": "Johnson Household",
  "owner_id": "user-789",
  "role": "owner",
  "created_at": "2026-05-16T12:00:00Z"
}
```

**Status Codes:**
- `201 Created` — Family created
- `400 Bad Request` — Invalid token or name already exists

---

### GET /families/{family_id}

Get family details. User must be a member.

**Request:**
```
GET /api/v1/families/fam-1
(authenticated; family membership verified)
```

**Response (200 OK):**
```json
{
  "id": "fam-1",
  "name": "Smith Household",
  "owner_id": "user-123",
  "member_count": 3,
  "account_count": 2,
  "created_at": "2026-05-14T10:00:00Z"
}
```

**Status Codes:**
- `200 OK` — Family found
- `403 Forbidden` — User not a member of this family
- `404 Not Found` — Family doesn't exist

---

### PUT /families/{family_id}

Update family details (name, etc.). Owner only.

**Request:**
```json
{
  "name": "Updated Household Name"
}
```

**Response (200 OK):**
```json
{
  "id": "fam-1",
  "name": "Updated Household Name",
  "owner_id": "user-123",
  "updated_at": "2026-05-16T14:00:00Z"
}
```

**Status Codes:**
- `200 OK` — Updated
- `403 Forbidden` — Not the family owner

---

## Family Members Endpoints

### GET /families/{family_id}/members

List active and pending members.

**Request:**
```
GET /api/v1/families/fam-1/members
```

**Response (200 OK):**
```json
{
  "active_members": [
    {
      "user_id": "user-123",
      "email": "alice@example.com",
      "first_name": "Alice",
      "role": "owner",
      "status": "active",
      "joined_at": "2026-05-14T10:00:00Z"
    },
    {
      "user_id": "user-789",
      "email": "bob@example.com",
      "first_name": "Bob",
      "role": "member",
      "status": "active",
      "joined_at": "2026-05-15T14:00:00Z"
    }
  ],
  "pending_invitations": [
    {
      "invitation_id": "inv-1",
      "email": "charlie@example.com",
      "expires_at": "2026-05-23T10:00:00Z",
      "created_at": "2026-05-16T10:00:00Z"
    }
  ]
}
```

---

### POST /families/{family_id}/members

Invite a member. Owner only.

**Request:**
```json
{
  "email": "newmember@example.com"
}
```

**Response (201 Created):**
```json
{
  "invitation_id": "inv-2",
  "email": "newmember@example.com",
  "family_id": "fam-1",
  "expires_at": "2026-05-23T10:00:00Z",
  "created_at": "2026-05-16T10:00:00Z"
}
```

**Notes:**
- v1: Invitation link printed to logs
- Email in invitation_token format: `/confirm-family/{invitation_token}`

---

### POST /families/{family_id}/members/confirm

Member accepts invitation (via token from email).

**Request:**
```json
{
  "invitation_token": "token-from-email",
  "password": "new_password (if creating account)"
}
```

**Response (200 OK):**
```json
{
  "user_id": "user-new",
  "email": "newmember@example.com",
  "role": "member",
  "status": "active"
}
```

---

### PATCH /families/{family_id}/members/{user_id}

Disable/enable member access. Owner only.

**Request:**
```json
{
  "status": "disabled"
}
```

**Response (200 OK):**
```json
{
  "user_id": "user-789",
  "email": "bob@example.com",
  "status": "disabled"
}
```

**Notes:**
- Disabled member immediately loses access (session invalidated)
- All transactions created by disabled member remain on family accounts
- Owner can re-enable to restore access

---

## Accounts Endpoints

### GET /families/{family_id}/accounts

List all family accounts.

**Request:**
```
GET /api/v1/families/fam-1/accounts
```

**Response (200 OK):**
```json
{
  "accounts": [
    {
      "id": "acc-1",
      "name": "Checking",
      "type": "bank",
      "balance_cents": 50000,
      "currency": "USD",
      "created_at": "2026-05-14T10:00:00Z"
    },
    {
      "id": "acc-2",
      "name": "Savings",
      "type": "savings",
      "balance_cents": 100000,
      "currency": "USD",
      "created_at": "2026-05-14T10:05:00Z"
    }
  ]
}
```

---

### POST /families/{family_id}/accounts

Create new account.

**Request:**
```json
{
  "name": "Emergency Fund",
  "type": "savings",
  "initial_balance_cents": 25000,
  "currency": "USD"
}
```

**Response (201 Created):**
```json
{
  "id": "acc-3",
  "name": "Emergency Fund",
  "type": "savings",
  "balance_cents": 25000,
  "currency": "USD",
  "created_at": "2026-05-16T12:00:00Z"
}
```

---

### GET /families/{family_id}/accounts/{account_id}

Get account details with summary stats.

**Request:**
```
GET /api/v1/families/fam-1/accounts/acc-1
```

**Response (200 OK):**
```json
{
  "id": "acc-1",
  "name": "Checking",
  "type": "bank",
  "balance_cents": 50000,
  "currency": "USD",
  "transaction_count": 24,
  "last_transaction_date": "2026-05-16T08:00:00Z",
  "created_at": "2026-05-14T10:00:00Z"
}
```

---

### PUT /families/{family_id}/accounts/{account_id}

Update account (name, type).

**Request:**
```json
{
  "name": "Primary Checking",
  "type": "bank"
}
```

**Response (200 OK):**
```json
{
  "id": "acc-1",
  "name": "Primary Checking",
  "type": "bank",
  "updated_at": "2026-05-16T12:00:00Z"
}
```

---

## Categories Endpoints

### GET /families/{family_id}/categories

List income, expense, and investment categories.

**Request:**
```
GET /api/v1/families/fam-1/categories?type=expense
```

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": "cat-1",
      "name": "Groceries",
      "type": "expense",
      "is_default": true,
      "created_at": "2026-05-14T10:00:00Z"
    },
    {
      "id": "cat-2",
      "name": "Utilities",
      "type": "expense",
      "is_default": true,
      "created_at": "2026-05-14T10:00:00Z"
    },
    {
      "id": "cat-10",
      "name": "Pet Care",
      "type": "expense",
      "is_default": false,
      "created_at": "2026-05-16T12:00:00Z"
    }
  ]
}
```

**Query Parameters:**
- `type` (optional): `income`, `expense`, `investment`

---

### POST /families/{family_id}/categories

Create custom category. Owner only.

**Request:**
```json
{
  "name": "Pet Expenses",
  "type": "expense"
}
```

**Response (201 Created):**
```json
{
  "id": "cat-10",
  "name": "Pet Expenses",
  "type": "expense",
  "is_default": false,
  "created_at": "2026-05-16T12:00:00Z"
}
```

---

## Transactions Endpoints

### GET /families/{family_id}/accounts/{account_id}/transactions

List transactions for an account.

**Request:**
```
GET /api/v1/families/fam-1/accounts/acc-1/transactions?limit=20&offset=0&start_date=2026-05-01&end_date=2026-05-16
```

**Query Parameters:**
- `limit` (default: 20)
- `offset` (default: 0)
- `start_date` (ISO 8601)
- `end_date` (ISO 8601)
- `category_id` (optional: filter by category)
- `include_disabled` (default: false; if true, show hidden transactions)

**Response (200 OK):**
```json
{
  "transactions": [
    {
      "id": "tx-1",
      "account_id": "acc-1",
      "category_id": "cat-1",
      "category_name": "Groceries",
      "amount_cents": 5000,
      "direction": "out",
      "date": "2026-05-16",
      "description": "Weekly groceries at Whole Foods",
      "creator_id": "user-123",
      "creator_name": "Alice",
      "is_enabled": true,
      "created_at": "2026-05-16T08:00:00Z",
      "updated_at": "2026-05-16T08:00:00Z"
    }
  ],
  "total_count": 24,
  "has_more": true
}
```

---

### POST /families/{family_id}/accounts/{account_id}/transactions

Record a new transaction.

**Request:**
```json
{
  "category_id": "cat-1",
  "amount_cents": 5000,
  "direction": "out",
  "date": "2026-05-16",
  "description": "Weekly groceries"
}
```

**Response (201 Created):**
```json
{
  "id": "tx-new",
  "account_id": "acc-1",
  "category_id": "cat-1",
  "amount_cents": 5000,
  "direction": "out",
  "date": "2026-05-16",
  "description": "Weekly groceries",
  "creator_id": "user-123",
  "is_enabled": true,
  "created_at": "2026-05-16T12:00:00Z"
}
```

**Validation:**
- `amount_cents` > 0
- `direction` ∈ {`in`, `out`}
- `date` is valid ISO 8601
- `category_id` belongs to family

---

### GET /families/{family_id}/accounts/{account_id}/transactions/{transaction_id}

Get transaction detail + edit history.

**Request:**
```
GET /api/v1/families/fam-1/accounts/acc-1/transactions/tx-1
```

**Response (200 OK):**
```json
{
  "transaction": {
    "id": "tx-1",
    "account_id": "acc-1",
    "category_id": "cat-1",
    "amount_cents": 5000,
    "direction": "out",
    "date": "2026-05-16",
    "description": "Weekly groceries at Whole Foods",
    "creator_id": "user-123",
    "is_enabled": true,
    "created_at": "2026-05-16T08:00:00Z",
    "updated_at": "2026-05-16T10:30:00Z"
  },
  "edit_history": [
    {
      "id": "edit-1",
      "editor_id": "user-456",
      "editor_name": "Bob",
      "change_summary": "Corrected amount from 4500 to 5000",
      "before_snapshot": { "amount_cents": 4500, "description": "Weekly groceries" },
      "after_snapshot": { "amount_cents": 5000, "description": "Weekly groceries at Whole Foods" },
      "edited_at": "2026-05-16T10:30:00Z"
    }
  ]
}
```

---

### PUT /families/{family_id}/accounts/{account_id}/transactions/{transaction_id}

Update transaction.

**Request:**
```json
{
  "amount_cents": 5500,
  "description": "Weekly groceries + household items"
}
```

**Response (200 OK):**
```json
{
  "id": "tx-1",
  "amount_cents": 5500,
  "description": "Weekly groceries + household items",
  "updated_at": "2026-05-16T14:00:00Z"
}
```

**Notes:**
- Creates an entry in `transaction_edits` table automatically
- Account balance is recalculated
- All members see the change immediately

---

### PATCH /families/{family_id}/accounts/{account_id}/transactions/{transaction_id}

Disable/enable transaction (soft-delete).

**Request:**
```json
{
  "is_enabled": false
}
```

**Response (200 OK):**
```json
{
  "id": "tx-1",
  "is_enabled": false,
  "updated_at": "2026-05-16T14:00:00Z"
}
```

**Notes:**
- Disabled transactions excluded from balance rollup and P&L reports
- Can be re-enabled by any member

---

### DELETE /families/{family_id}/accounts/{account_id}/transactions/{transaction_id}

Permanently delete transaction. Owner only.

**Request:**
```
DELETE /api/v1/families/fam-1/accounts/acc-1/transactions/tx-1
```

**Response (204 No Content):**
```
(empty body)
```

**Status Codes:**
- `204 No Content` — Deleted
- `403 Forbidden` — Not the family owner
- `404 Not Found` — Transaction doesn't exist

**Warning:** Deletion is irreversible.

---

## Analytics Endpoints (Stretch Goal for v1)

### GET /families/{family_id}/dashboard

Summary metrics for dashboard.

**Request:**
```
GET /api/v1/families/fam-1/dashboard?period=month
```

**Query Parameters:**
- `period`: `week`, `month` (default), `year`, `custom`
- `start_date`, `end_date` (if `period=custom`)

**Response (200 OK):**
```json
{
  "period": "May 2026",
  "total_income_cents": 500000,
  "total_expense_cents": 150000,
  "net_savings_cents": 350000,
  "accounts": [
    { "id": "acc-1", "name": "Checking", "balance_cents": 50000 },
    { "id": "acc-2", "name": "Savings", "balance_cents": 100000 }
  ],
  "recent_transactions": [
    { "date": "2026-05-16", "description": "Groceries", "amount_cents": 5000, "direction": "out" }
  ]
}
```

**Status:** Deferred to v1.1 if resource-constrained.

---

## Error Handling

All errors return JSON with the following format:

**Error Response:**
```json
{
  "error": "validation_error",
  "message": "Amount must be greater than 0",
  "details": {
    "field": "amount_cents",
    "value": -500
  }
}
```

**Common HTTP Status Codes:**

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Deletion succeeded |
| 400 | Bad Request | Invalid input (negative amount) |
| 401 | Unauthorized | Missing/invalid session or JWT |
| 403 | Forbidden | User not a member of family, or insufficient role |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error (malformed body) |
| 500 | Internal Server Error | Backend error; check logs |

---

## Rate Limiting (v2+)

Not implemented in v1. Expected in v2:
- Per-user rate limit: 100 requests/min
- Per-IP rate limit: 1000 requests/min

---

## Versioning & Deprecation

All endpoints are under `/api/v1/`. When breaking changes are needed (v2+), new endpoints will be introduced at `/api/v2/`. Old endpoints will have a deprecation warning in headers.

---

## Testing & Documentation

- **OpenAPI Spec:** Auto-generated by FastAPI at `GET /api/v1/docs`
- **Postman Collection:** TODO (to be created during implementation)
- **Integration Tests:** `backend/tests/test_api.py` (pytest)

---

**Next Steps:**
- Backend team implements endpoints with authorization checks and validation
- Frontend team integrates API calls into React components
- Both teams verify error handling and edge cases