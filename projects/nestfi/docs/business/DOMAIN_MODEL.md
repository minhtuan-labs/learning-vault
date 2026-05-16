# Domain Model — NestFi

## 1. Core Entities

### 1.1 User (Actor)
**Attributes**:
- user_id: unique identifier
- email: email address (unique)
- password_hash: secure password hash
- name: full name
- created_at: registration timestamp
- is_superadmin: boolean (default false)

**Behavior**:
- Can belong to multiple families
- Can switch between families
- Can accept/decline family invitations
- Can view only data for families they belong to

---

### 1.2 Family (Aggregate Root)
**Attributes**:
- family_id: unique identifier
- name: family name (e.g., "Smith Household")
- owner_id: references the User who is the primary owner
- created_by: references Superadmin who created the family
- created_at: family creation timestamp
- is_active: boolean (default true)

**Relationships**:
- 1 Family → Many Users (via FamilyMember)
- 1 Family → Many BankAccounts
- 1 Family → Many TransactionCategories (Income, Expense, Investment)
- 1 Family → Many Transactions

**Behavior**:
- Only superadmin creates families
- Only owner can invite members
- Only owner can manage categories and bank accounts
- Soft delete supported (is_active flag)

---

### 1.3 FamilyMember (Join)
**Attributes**:
- family_member_id: unique identifier
- family_id: references Family
- user_id: references User
- role: enum (OWNER, MEMBER)
- invitation_status: enum (PENDING, ACCEPTED, DECLINED)
- invited_at: timestamp when invitation was sent
- accepted_at: timestamp when invitation was accepted (null if pending)
- joined_date: date when member was added to family

**Constraints**:
- One user can have one role per family (no duplicate memberships)
- Owner always has ACCEPTED status
- Members can only see data after ACCEPTED

**Behavior**:
- Track invitation lifecycle (PENDING → ACCEPTED / DECLINED)
- Support member removal by owner

---

### 1.4 BankAccount (Value Object within Family)
**Attributes**:
- bank_account_id: unique identifier
- family_id: references Family
- account_name: e.g., "Joint Checking", "Savings"
- account_number: masked/encrypted
- account_type: enum (CHECKING, SAVINGS, INVESTMENT, OTHER)
- balance: current balance (calculated from transactions, not stored directly)
- currency: currency code (e.g., USD)
- is_active: boolean (default true)
- created_at: timestamp

**Behavior**:
- Owned by family, created/managed by owner
- Multiple accounts per family supported
- Balance is derived from transactions (no direct balance field persisted)

---

### 1.5 Transaction (Core Domain)
**Attributes**:
- transaction_id: unique identifier
- family_id: references Family
- bank_account_id: references BankAccount
- user_id: references User who logged the transaction
- description: transaction description
- amount: transaction amount (positive)
- type: enum (INCOME, EXPENSE, INVESTMENT)
- category_id: references TransactionCategory
- transaction_date: date of transaction
- created_at: timestamp when logged
- is_deleted: boolean (soft delete)

**Behavior**:
- Immutable after creation (updates logged as adjustments)
- Amount always positive; type (INCOME/EXPENSE/INVESTMENT) determines sign
- Cash withdrawals have type=EXPENSE, category="Cash Withdrawal"
- All family members can see all transactions immediately

---

### 1.6 TransactionCategory (Value Object within Family)
**Attributes**:
- category_id: unique identifier
- family_id: references Family
- category_type: enum (INCOME, EXPENSE, INVESTMENT)
- name: category name (e.g., "Salary", "Groceries", "Stocks")
- description: optional description
- color: optional color tag for UI
- is_active: boolean (default true)
- created_at: timestamp
- created_by: references User (owner)

**Constraints**:
- Category names are unique per family per type (e.g., cannot have two "Salary" categories in same family)
- Built-in category "Cash Withdrawal" for all families

**Behavior**:
- Created/managed by family owner
- Can be marked inactive (soft delete)
- Statistics aggregated by category (sum of transactions, count, average)

---

## 2. Domain Value Objects

### 2.1 Money
**Attributes**:
- amount: decimal (e.g., 100.50)
- currency: currency code (e.g., USD, VND)

**Behavior**:
- Immutable
- Supports comparison, addition
- Always positive; sign determined by transaction type

---

### 2.2 Email Invitation
**Attributes**:
- invitation_id: unique identifier
- family_id: references Family
- recipient_email: email address of invitee
- status: enum (SENT, ACCEPTED, DECLINED, EXPIRED)
- created_at: timestamp
- expires_at: expiration timestamp (30 days default)
- accepted_at: timestamp of acceptance

**Behavior**:
- Email verification required
- One-time token for acceptance link
- Expiration enforced

---

## 3. Key Domain Rules

### 3.1 Family Access Control
- User can only view/edit data for families they are a member of
- User must be OWNER to create categories or invite members
- Superadmin has full access to all families (for support/administration)

### 3.2 Transaction Immutability
- Transactions are immutable after creation
- Changes are logged as new transactions or adjustments (v2+)
- Deletions are soft deletes (is_deleted flag)

### 3.3 Category Isolation
- Categories belong to families; no cross-family category sharing
- Each family manages its own category taxonomy
- Categories can be inactivated but not permanently deleted (history preservation)

### 3.4 Superadmin Constraints
- Superadmin creates families but does not automatically join them
- Superadmin can view all families for support purposes
- Superadmin cannot edit user passwords (only reset/generate temporary)

### 3.5 Member Invitation Lifecycle
- Owner invites via email
- Invitee receives email with acceptance link/token
- Invitee accepts and is added as MEMBER
- Declined invitations are archived (not retried automatically)

---

## 4. Aggregates

### Aggregate 1: Family (Root)
- Aggregate ID: family_id
- Entities: Family, FamilyMember, BankAccount, Transaction, TransactionCategory
- Invariants:
  - Every family has at least one owner
  - All transactions and categories belong to exactly one family
  - BankAccounts are family-specific

### Aggregate 2: Transaction (Root)
- Aggregate ID: transaction_id
- Value Objects: Money, Category reference
- Invariants:
  - Amount is always positive
  - Type determines sign (INCOME → +, EXPENSE → -)
  - Category must exist in family

---

## 5. Domain Events (Event Sourcing — v2+)

1. FamilyCreated
2. MemberInvited
3. MemberAccepted
4. MemberDeclined
5. MemberRemoved
6. TransactionLogged
7. CategoryCreated
8. CategoryInactivated
9. BankAccountCreated
10. BankAccountClosed

---

## 6. Ubiquitous Language

| Term | Definition |
|------|-----------|
| **Family** | A group of users sharing financial data |
| **Member** | A user belonging to a family |
| **Owner** | A member with permission to manage family (create categories, invite members) |
| **Superadmin** | Platform administrator who creates families and manages system-level settings |
| **Category** | A classification for transactions (e.g., Salary, Groceries, Stocks) |
| **Transaction** | A financial event (income, expense, investment) logged with amount, date, category |
| **Bank Account** | A linked financial account tracked by the family |
| **Dashboard** | Family's financial overview showing trends, savings rate, investments |
| **Cash Withdrawal** | A transaction type representing cash taken from bank account (treated as expense) |
| **Invitation** | Email-based request for a user to join a family |
| **Acceptance** | Act of confirming an invitation and joining a family |

---

## 7. Data Consistency & Integrity

### Invariants
1. Every transaction belongs to exactly one family
2. Every user invitation has exactly one family and one recipient email
3. Category names are unique per family per type
4. FamilyMember records are unique per (family_id, user_id) pair
5. Balance calculations are derived from transactions (not stored directly)

### Constraints
- Transactions with null category_id are invalid (must have a category)
- Invitations expire after 30 days (or configurable interval)
- Transaction amounts must be > 0
- Family names are unique (or allow duplicates but track by ID)

---

## 8. Relationships Summary

```
User
  ├─ N FamilyMember
  │   ├─ 1 Family
  │   └─ invitation_status (PENDING, ACCEPTED, DECLINED)
  └─ N Transaction (logged_by)

Family (Aggregate Root)
  ├─ N FamilyMember
  ├─ N BankAccount
  ├─ N TransactionCategory
  │   ├─ INCOME categories
  │   ├─ EXPENSE categories (includes "Cash Withdrawal")
  │   └─ INVESTMENT categories
  └─ N Transaction
      ├─ 1 BankAccount
      ├─ 1 TransactionCategory
      └─ 1 User (logged_by)

Superadmin (User with is_superadmin=true)
  └─ can create N Family
  └─ can view all data across all families
```
