# Domain Model — NestFi

## Design Principle: Account-Centric

NestFi is designed around **accounts**, not people. All financial tracking is tied to bank/investment accounts, not individual household members. This means:
- Transactions always belong to a specific account (e.g., "Main Checking", "Savings")
- There is no bill-splitting or person-to-person expense tracking
- A cash withdrawal is a single transaction from the account, categorized as "Cash Withdrawal"
- All family members have equal visibility to all accounts and transactions
- Family members are not assigned individual spending budgets or tracked separately

---

## Core Entities

### User
Represents a person with a login account in the system.

| Attribute | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Primary key |
| `email` | String | Unique identifier for login |
| `username` | String | Display name (e.g., "superadmin") |
| `password_hash` | String | Securely hashed password |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last profile update |

**Relationships:**
- 1 User : Many FamilyMemberships (user can belong to multiple families)

---

### Family
Represents a household or group managing finances together.

| Attribute | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Primary key |
| `name` | String | Family display name (e.g., "Smith Household") |
| `description` | String | Optional notes about the family |
| `created_by` | UUID | FK to User (owner who created it) |
| `created_at` | DateTime | Family creation timestamp |

**Relationships:**
- 1 Family : Many FamilyMemberships (members of the family)
- 1 Family : Many Accounts (bank/investment accounts)
- 1 Family : Many Categories (transaction categories)
- 1 Family : Many Transactions (financial activity)

---

### FamilyMembership
Join table linking Users to Families with roles.

| Attribute | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Primary key |
| `family_id` | UUID | FK to Family |
| `user_id` | UUID | FK to User |
| `role` | Enum | "owner" or "member" |
| `invited_at` | DateTime | When invitation was sent |
| `accepted_at` | DateTime | When user accepted (NULL if pending) |
| `status` | Enum | "pending", "active", or "disabled" |
| `disabled_at` | DateTime | When owner disabled this membership (NULL if active) |

**Rules:**
- Invitation lifecycle: pending → active (on email confirmation) → disabled (owner action) → active (owner re-enables)
- Owner can add members; members have read-write access to family transactions (all members equal access)
- Superadmin is implicit owner of all families
- Disabled members cannot log in and cannot access family data
- Re-enabling a disabled member restores full access; all their past edits/transactions remain intact

---

### Account
Represents a bank or investment account within a family.

| Attribute | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Primary key |
| `family_id` | UUID | FK to Family |
| `name` | String | Account name (e.g., "Checking", "Savings") |
| `account_type` | Enum | "bank", "savings", "investment", "cash" |
| `balance` | Decimal | Current balance (calculated from transactions) |
| `currency` | String | ISO 4217 code (e.g., "USD", "VND") |
| `created_at` | DateTime | Account creation date |

**Relationships:**
- 1 Account : Many Transactions (all activity on this account)

---

### Category
Represents a classification for income, expense, or investment transactions.

| Attribute | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Primary key |
| `family_id` | UUID | FK to Family |
| `name` | String | Category name (e.g., "Salary", "Groceries") |
| `type` | Enum | "income", "expense", "investment" |
| `icon` | String | Optional emoji or icon identifier |
| `created_at` | DateTime | Creation timestamp |

**Rules:**
- Categories are family-specific (not global)
- "Cash Withdrawal" is an expense category
- Families can customize their category list

**Relationships:**
- 1 Category : Many Transactions

---

### Transaction
Represents a single financial event (income, expense, or transfer). Always belongs to a specific account.

| Attribute | Type | Notes |
|-----------|------|-------|
| `id` | UUID | Primary key |
| `family_id` | UUID | FK to Family |
| `account_id` | UUID | FK to Account (required; all transactions belong to an account) |
| `category_id` | UUID | FK to Category |
| `amount` | Decimal | Transaction amount (always positive) |
| `direction` | Enum | "in" (income) or "out" (expense) |
| `date` | Date | When the transaction occurred |
| `description` | String | Optional notes (e.g., "Grocery shopping") |
| `created_by` | UUID | FK to User (who recorded it; metadata only, not ownership) |
| `created_at` | DateTime | When it was recorded |
| `enabled` | Boolean | True if active; False if disabled by any family member. Default: True. |
| `updated_at` | DateTime | Last update timestamp (for tracking when edits occur) |

**Related Entity — Transaction Edit History**
Track all edits to a transaction (separate table or embedded in transaction):

| Attribute | Type | Notes |
|-----------|------|-------|
| `transaction_id` | UUID | FK to Transaction |
| `edited_by` | UUID | FK to User (who made the edit) |
| `edited_at` | DateTime | When the edit occurred |
| `change_summary` | String | What fields changed (e.g., "amount: 100 → 150, category: Groceries → Entertainment") |

**Rules:**
- Amount is always stored as positive; direction indicates in/out
- All transactions must have a category (enforces categorization rule)
- Cash withdrawal is recorded as a single "out" transaction with "Cash Withdrawal" category against the account
- No person-level expense tracking or bill-splitting (all family members have equal access to all accounts)
- Transactions are account-specific; no cross-account transfers in v1
- Enabled transactions count in P&L and dashboard metrics; disabled transactions are excluded but preserved
- Only family owner can permanently delete a transaction; all other members can only disable/enable
- Edit history is immutable and visible to all family members

**Relationships:**
- 1 Transaction : 1 Account
- 1 Transaction : 1 Category
- 1 Transaction : 1 User (creator)
- 1 Transaction : Many TransactionEditHistory entries

---

### Dashboard / Reporting View (Computed)
Not a stored entity, but a business concept. Computed from **enabled transactions only**.

**Metrics:**
- Total Income (sum of "in" transactions where enabled=True, by date range)
- Total Expenses (sum of "out" transactions where enabled=True, by date range)
- Net Savings (Income - Expenses)
- Balance by Account (calculated from enabled transactions only)
- Breakdown by Category (sum spent per category, enabled only)
- Trends over time (month-by-month, year-over-year, enabled only)

**Note:** Disabled transactions are excluded from all P&L and reporting metrics but remain in the transaction archive for audit purposes.

---

## Key Business Relationships

```
User
  |
  +-- (1:M) FamilyMemberships
       |
       +-- Family
            |
            +-- (1:M) Accounts
            |    |
            |    +-- (1:M) Transactions
            |         |
            |         +-- Category
            |
            +-- (1:M) Categories
            |
            +-- (1:M) Transactions
```

---

## Data Constraints & Invariants

1. **Email Uniqueness**: No two Users can have the same email
2. **Account Balance**: Derived from enabled transactions only; never stored directly
3. **Category Ownership**: A category belongs to exactly one family
4. **Transaction Soft-Delete Default**: All members can disable/enable transactions; disabled txns preserved for audit. Only owner can hard-delete (irreversible).
5. **Transaction Edit Audit Trail**: All edits tracked with user, timestamp, and change summary; edit history immutable
6. **Member Disable/Enable**: Owner can disable/enable members; disabled members lose access but their transactions/edits remain. Disabling is reversible.
7. **Multi-Tenancy**: No transaction, account, or membership from one family can be viewed/modified by a user not in that family
