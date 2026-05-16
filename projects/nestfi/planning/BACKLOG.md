# Product Backlog — NestFi

**Product:** NestFi - Family Financial Management Platform  
**Last Updated:** 2026-05-16  
**Owner:** PM  

---

## Backlog Structure

This backlog is organized by epic (feature area) and prioritized for MVP (v0.1) delivery. Items marked with **🚀 MVP** are in scope for the first release; others are deferred to v0.2+ or treated as nice-to-haves.

---

## Epic 1: Authentication & User Management 🚀 MVP

### US-1.1: User Registration via Email Invitation 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 8  
**Description:**  
As a family owner, I want to invite family members via email so that they can join our household financial management without manual account setup.

**Acceptance Criteria:**
- [ ] Owner clicks "Invite Member" button
- [ ] Owner enters member email address
- [ ] System sends invitation email with unique acceptance link/token
- [ ] Email arrives within 5 minutes (99% of invitations)
- [ ] Link is valid for 7 days
- [ ] Member clicks link and is prompted to create password
- [ ] System validates email uniqueness (no duplicate invitations)
- [ ] Owner receives confirmation that invitation was sent

**Tasks:** (for engineering team)
- [ ] Email template design
- [ ] Invitation token generation & storage (DB)
- [ ] Email service setup (AWS SES or SendGrid)
- [ ] Frontend: invitation form UI
- [ ] Backend: POST /invite endpoint
- [ ] Backend: GET /accept-invite/:token endpoint

---

### US-1.2: Superadmin Account & Family Creation 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a superadmin, I want to create new families and invite initial owners via email so that each family has a starting point for household financial management.

**Acceptance Criteria:**
- [ ] Superadmin can login with default credentials (superadmin/admin123)
- [ ] Superadmin can create a new family (name, description)
- [ ] System generates unique family ID
- [ ] Superadmin can invite owner via email from family creation flow
- [ ] Owner invitation includes family details
- [ ] Only superadmin can create families (no other users)
- [ ] Superadmin can list all families and their members

**Tasks:**
- [ ] Database schema for families & roles
- [ ] Superadmin login flow
- [ ] Family creation API (POST /families)
- [ ] Permission middleware (superadmin-only checks)
- [ ] Family settings page (superadmin panel)

---

### US-1.3: Password Reset & Account Recovery 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 5  
**Description:**  
As a user, I want to reset my password via email so that I can regain access if I forget my credentials.

**Acceptance Criteria:**
- [ ] User clicks "Forgot Password" link on login page
- [ ] User enters email address
- [ ] System sends password reset email with token
- [ ] Reset link valid for 24 hours
- [ ] User clicks link and creates new password
- [ ] New password is validated (length, complexity)
- [ ] Old password is invalidated after reset
- [ ] User receives confirmation email

**Tasks:**
- [ ] Password reset token flow
- [ ] Email template for reset
- [ ] Frontend: password reset form
- [ ] Backend: password reset endpoints
- [ ] Validation logic for password strength

---

### US-1.4: Multi-Family Account Support 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 8  
**Description:**  
As a user, I want to belong to multiple families and switch between them without re-logging-in so that I can manage multiple households from one account.

**Acceptance Criteria:**
- [ ] User can be invited to and accept multiple families
- [ ] After login, user sees list of families they belong to
- [ ] User can switch families from dashboard (without re-login)
- [ ] Each family view is independent (different transactions, categories, members)
- [ ] System tracks which family is "active" per session
- [ ] "Switch family" action is clearly visible on dashboard

**Tasks:**
- [ ] Database design: family membership (user-to-family mapping)
- [ ] API endpoint: GET /me/families
- [ ] API endpoint: POST /switch-family/:familyId
- [ ] Frontend: family switcher component
- [ ] Session/context management for active family
- [ ] Authorization checks on all endpoints (verify family membership)

---

## Epic 2: Transaction Logging 🚀 MVP

### US-2.1: Log Income Transaction 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a family member, I want to log an income transaction so that the household income is tracked and visible to all family members.

**Acceptance Criteria:**
- [ ] Member clicks "Add Transaction" → "Income"
- [ ] Form displays: amount, category (dropdown), date, optional notes
- [ ] Amount field accepts decimals (e.g., 1500.50)
- [ ] Date defaults to today but can be changed
- [ ] Category dropdown shows all active income categories
- [ ] Notes field is optional, max 500 characters
- [ ] System auto-fills member name (logged-in user)
- [ ] Member submits form; transaction created immediately
- [ ] Transaction visible in family ledger within 1 second
- [ ] Success message confirms creation

**Tasks:**
- [ ] API endpoint: POST /transactions (type: "income")
- [ ] Frontend: transaction creation form
- [ ] Category dropdown/autocomplete component
- [ ] Real-time update (WebSocket or polling) for other family members
- [ ] Validation (amount > 0, category exists, member belongs to family)
- [ ] Audit logging (who created what, when)

---

### US-2.2: Log Expense Transaction 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a family member, I want to log an expense transaction so that household spending is tracked and categorized.

**Acceptance Criteria:**
- [ ] Member clicks "Add Transaction" → "Expense"
- [ ] Form displays: amount, category (dropdown), date, optional notes
- [ ] Amount field accepts decimals
- [ ] Date defaults to today
- [ ] Category dropdown shows all active expense categories
- [ ] Notes field optional (e.g., "groceries at Whole Foods")
- [ ] Member name auto-filled
- [ ] System validates: amount > 0, category exists, member in family
- [ ] Transaction created and visible to all family members immediately
- [ ] Expense reduces household balance (reflected in dashboard)

**Tasks:**
- [ ] API endpoint: POST /transactions (type: "expense")
- [ ] Form validation (amount, category)
- [ ] Real-time broadcast to family
- [ ] Dashboard update (total expenses)

---

### US-2.3: Log Cash Withdrawal 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 3  
**Description:**  
As a family member, I want to log a cash withdrawal so that household cash spending is tracked.

**Acceptance Criteria:**
- [ ] Member clicks "Add Transaction" → "Cash Withdrawal"
- [ ] System treats cash withdrawal as an expense (reduces total)
- [ ] Category defaults to "Cash Withdrawal" (auto-filled)
- [ ] Form displays: amount, optional notes, date
- [ ] User can override default category if desired
- [ ] Transaction created and visible like any other expense

**Tasks:**
- [ ] "Cash Withdrawal" category created by default in every family
- [ ] API validation: cash withdrawal → expense type, "Cash Withdrawal" category
- [ ] Frontend: separate button/path for cash withdrawal (for simplicity)

---

### US-2.4: View Transaction History & Ledger 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 8  
**Description:**  
As a family member, I want to view all family transactions in a searchable ledger so that I can find specific transactions and understand household financial history.

**Acceptance Criteria:**
- [ ] Dashboard shows transaction ledger (most recent first)
- [ ] Each row displays: date, member name, amount, category, notes
- [ ] Ledger shows last 100 transactions (paginated)
- [ ] Filter by category (dropdown or chips)
- [ ] Filter by date range (calendar picker)
- [ ] Search by member name or notes (text input)
- [ ] Sort by date, amount, or member name
- [ ] Ledger updates in real-time when new transactions added
- [ ] Performance: ledger loads and filters in <500ms

**Tasks:**
- [ ] API endpoint: GET /transactions (with filters: category, date range, search)
- [ ] Database indexing on category, date, member for query performance
- [ ] Frontend: transaction table/list component
- [ ] Filtering & search UI
- [ ] Pagination component
- [ ] Real-time updates (WebSocket subscription)

---

### US-2.5: Edit/Delete Own Transactions 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 5  
**Description:**  
As a family member, I want to edit or delete my own transactions so that I can correct mistakes.

**Acceptance Criteria:**
- [ ] Member can click edit icon on their transaction
- [ ] Edit form displays current values (amount, category, date, notes)
- [ ] Member can change any field
- [ ] Submit updates transaction immediately
- [ ] Member can click delete on their transaction
- [ ] Confirmation dialog appears ("Are you sure?")
- [ ] Delete removes transaction and recalculates totals
- [ ] Owner can edit/delete any family member's transaction (with audit log)
- [ ] Edit/delete operations are logged (who, what, when)

**Tasks:**
- [ ] API endpoint: PATCH /transactions/:id (edit)
- [ ] API endpoint: DELETE /transactions/:id (delete)
- [ ] Authorization: user can only edit own, owner can edit any
- [ ] Audit logging table for transaction changes
- [ ] Frontend: edit modal/form
- [ ] Frontend: delete confirmation dialog
- [ ] Update dashboard totals after edit/delete

---

## Epic 3: Categories & Configuration 🚀 MVP

### US-3.1: Create Custom Income Categories 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a family owner, I want to create custom income categories so that family income can be categorized by source (e.g., "Salary", "Freelance", "Investments").

**Acceptance Criteria:**
- [ ] Owner clicks "Add Category" under Income section
- [ ] Form displays: category name, optional icon/color
- [ ] Name field required, max 50 characters
- [ ] Icon/color selection (optional, preset colors)
- [ ] Submit creates category
- [ ] New category immediately available in "Log Income" dropdown
- [ ] Category visible to all family members
- [ ] Owner can edit category name/icon after creation
- [ ] Owner can archive category (remove from dropdowns but keep data)

**Tasks:**
- [ ] API endpoint: POST /categories (type: "income")
- [ ] Database schema: categories table (name, type, family_id, color, icon)
- [ ] Frontend: category management page
- [ ] Category creation form
- [ ] Category list with edit/archive actions
- [ ] Validation: unique category name per family per type

---

### US-3.2: Create Custom Expense Categories 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a family owner, I want to create custom expense categories so that household spending can be tracked by category (e.g., "Groceries", "Utilities", "Entertainment").

**Acceptance Criteria:**
- [ ] Owner navigates to Expense Categories section
- [ ] Form similar to income categories (name, icon, color)
- [ ] Submit creates expense category
- [ ] Immediately available in "Log Expense" dropdown
- [ ] Visible to all family members
- [ ] Owner can edit or archive expense categories
- [ ] Default categories provided on first family setup (Groceries, Utilities, Entertainment, etc.)

**Tasks:**
- [ ] Same API as US-3.1 (POST /categories with type: "expense")
- [ ] Seeding: default expense categories when family created
- [ ] Frontend: same as US-3.1 but for expenses
- [ ] Validation: prevent deletion of categories with transactions (offer archive instead)

---

### US-3.3: Create Custom Investment Categories 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 5  
**Description:**  
As a family owner, I want to track investments in custom categories so that investment portfolio is visible (e.g., "Stock Portfolio", "Retirement Accounts", "Crypto").

**Acceptance Criteria:**
- [ ] Owner can create investment categories like income/expense
- [ ] Investment transactions are separate from income/expense
- [ ] Investment category values displayed on dashboard
- [ ] Categories can be marked as active/inactive

**Tasks:**
- [ ] Extend POST /categories to support type: "investment"
- [ ] Update transaction schema to support "investment" type
- [ ] Dashboard update to show investment totals
- [ ] Frontend: investment category management

---

### US-3.4: View & Edit Family Categories 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a family member, I want to view all family categories and understand available options for categorizing transactions.

**Acceptance Criteria:**
- [ ] Dashboard has "Categories" or "Settings" section
- [ ] Shows all active categories grouped by type (Income, Expense, Investment)
- [ ] Owner can edit category details (name, color)
- [ ] Owner can archive/restore categories
- [ ] Members see only active categories in dropdowns
- [ ] Archive is soft-delete (data preserved, category hidden)

**Tasks:**
- [ ] API endpoint: GET /categories (grouped by type)
- [ ] API endpoint: PATCH /categories/:id (edit)
- [ ] API endpoint: DELETE /categories/:id (soft-delete/archive)
- [ ] Frontend: category management UI (list, edit modal, archive confirmation)

---

## Epic 4: Dashboard & Analytics 🚀 MVP

### US-4.1: Real-Time Dashboard Overview 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 8  
**Description:**  
As a family member, I want to see a real-time dashboard with household financial overview so that I understand household finances at a glance.

**Acceptance Criteria:**
- [ ] Dashboard shows:
  - Current month total income
  - Current month total expenses
  - Net savings (income - expenses)
  - Current year total income
  - Current year total expenses
  - Current year net savings
- [ ] Values update in real-time as transactions are added
- [ ] Dashboard loads in <2 seconds (MVP goal)
- [ ] Dashboard layout is responsive (mobile, tablet, desktop)
- [ ] Summary cards are clear and easy to understand

**Tasks:**
- [ ] API endpoint: GET /dashboard (returns summary stats)
- [ ] Database query optimization (aggregations on indexed columns)
- [ ] Frontend: dashboard layout & styling
- [ ] Real-time updates (WebSocket subscription to transaction changes)
- [ ] Performance testing (load in <2 seconds with 1000+ transactions)

---

### US-4.2: Expense Category Breakdown 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a family member, I want to see expense breakdown by category so that I can understand where household money is being spent.

**Acceptance Criteria:**
- [ ] Dashboard displays pie chart or bar chart of expenses by category (current month)
- [ ] Chart shows category name and amount
- [ ] Chart is interactive (hover for details)
- [ ] Legend shows all categories in use
- [ ] Chart updates in real-time as new expenses added
- [ ] "No expense data" message if no expenses logged yet

**Tasks:**
- [ ] API endpoint: GET /dashboard/expenses-by-category (monthly)
- [ ] Database: aggregation query for expenses by category
- [ ] Frontend: charting library (Chart.js, Recharts, or similar)
- [ ] Chart component with tooltip/legend

---

### US-4.3: Monthly Spending Trends 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 5  
**Description:**  
As a family member, I want to see spending trends over time so that I can identify patterns and plan ahead.

**Acceptance Criteria:**
- [ ] Dashboard shows line chart: income and expenses over last 6-12 months
- [ ] X-axis: months, Y-axis: amount
- [ ] Separate lines for income (green) and expenses (red)
- [ ] Hover to see exact values for each month
- [ ] Chart updates with new data automatically

**Tasks:**
- [ ] API endpoint: GET /dashboard/trends (6 or 12 months)
- [ ] Database aggregation: monthly sums
- [ ] Frontend: line chart component
- [ ] Tooltip/legend for clarity

---

### US-4.4: Family Member Activity Feed 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 5  
**Description:**  
As a family member, I want to see recent activity (who added what transactions) so that I can stay informed about household finances.

**Acceptance Criteria:**
- [ ] Dashboard shows activity feed: "Alice added $50 in Groceries", "Bob added $100 salary", etc.
- [ ] Feed shows last 20 transactions (most recent first)
- [ ] Displays: member name, transaction type, amount, category, date/time
- [ ] Feed updates in real-time as new transactions added
- [ ] Clicking transaction shows full details (if needed)

**Tasks:**
- [ ] API endpoint: GET /dashboard/activity-feed
- [ ] Frontend: activity feed component (list of recent transactions with formatted text)
- [ ] Real-time updates

---

### US-4.5: Savings Rate Calculation 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 3  
**Description:**  
As a family member, I want to see household savings rate so that I understand how much of income is being saved vs spent.

**Acceptance Criteria:**
- [ ] Dashboard displays: "Savings Rate: X%" (calculated as (Income - Expenses) / Income * 100)
- [ ] Shown for current month and current year
- [ ] Updates in real-time
- [ ] Handles edge case: no income (shows N/A or 0%)

**Tasks:**
- [ ] Calculation logic in dashboard stats query
- [ ] Frontend display (card or summary line)

---

## Epic 5: Family Management 🚀 MVP

### US-5.1: Create Family (Superadmin) 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a superadmin, I want to create a new family so that a household can start using NestFi.

**Acceptance Criteria:**
- [ ] Superadmin navigates to "Create Family"
- [ ] Form displays: family name, optional description
- [ ] Submit creates family with unique ID
- [ ] System automatically invites initial owner (superadmin enters owner email)
- [ ] Confirmation shows family created and invitation sent

**Tasks:**
- [ ] API endpoint: POST /families (superadmin-only)
- [ ] Superadmin dashboard page
- [ ] Family creation form
- [ ] Trigger email invitation to initial owner

---

### US-5.2: View & Manage Family Members 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 8  
**Description:**  
As a family owner, I want to view and manage family members so that I can add, remove, and control access to household finances.

**Acceptance Criteria:**
- [ ] Owner sees list of all family members (name, email, role, join date)
- [ ] Owner can invite new members via email
- [ ] Owner can remove members (with confirmation)
- [ ] Member list updates in real-time
- [ ] Owner cannot remove themselves (unless family has another owner)
- [ ] Status column shows: "Owner", "Member", "Pending Invite"
- [ ] Pending invites can be resent or revoked

**Tasks:**
- [ ] API endpoint: GET /family/:familyId/members
- [ ] API endpoint: POST /family/:familyId/members (invite)
- [ ] API endpoint: DELETE /family/:familyId/members/:userId (remove)
- [ ] Member management UI
- [ ] Invite/remove confirmation dialogs
- [ ] Real-time member list updates

---

### US-5.3: Accept Family Invitation 🚀 MVP
**Priority:** P0 (Critical)  
**Story Points:** 5  
**Description:**  
As a new user, I want to accept a family invitation and join the household so that I can start logging and viewing transactions.

**Acceptance Criteria:**
- [ ] User receives email with invitation link
- [ ] Clicking link brings user to acceptance page
- [ ] If not logged in, user prompted to create account (email pre-filled)
- [ ] If logged in, user can directly accept
- [ ] After acceptance, user immediately has access to family dashboard
- [ ] Acceptance confirmation email sent
- [ ] User added to family member list

**Tasks:**
- [ ] API endpoint: GET /invite/:token (validate token, return family info)
- [ ] API endpoint: POST /invite/:token/accept (accept invitation)
- [ ] Frontend: invitation acceptance page
- [ ] Redirect to login if needed
- [ ] Redirect to family dashboard after acceptance

---

### US-5.4: Remove Family Member 🚀 MVP
**Priority:** P1 (High)  
**Story Points:** 3  
**Description:**  
As a family owner, I want to remove a member so that they no longer have access to family finances.

**Acceptance Criteria:**
- [ ] Owner clicks "Remove" next to member name
- [ ] Confirmation dialog: "This user will lose access to all family data"
- [ ] After confirmation, member is removed
- [ ] Member can no longer see family in their dashboard
- [ ] All historical transactions remain (for audit)
- [ ] Member's previous transactions remain visible but are marked (e.g., "former member")

**Tasks:**
- [ ] API endpoint: DELETE /family/:familyId/members/:userId
- [ ] Authorization: only owner can remove
- [ ] Frontend: remove button & confirmation
- [ ] Transaction history: preserve but mark removed members

---

## Backlog Summary

| Epic | Status | # Stories | # MVP | Estimated Points |
|---|---|---|---|---|
| 1. Authentication | — | 4 | 4 | 26 |
| 2. Transactions | — | 5 | 5 | 26 |
| 3. Categories | — | 4 | 4 | 20 |
| 4. Dashboard | — | 5 | 5 | 26 |
| 5. Family Management | — | 4 | 4 | 21 |
| **TOTAL (MVP v0.1)** | — | **22** | **22** | **119 points** |

---

## Nice-to-Have Backlog (v0.2+)

- [ ] US-6.1: Bank Account Management (add/edit accounts, assign transactions)
- [ ] US-6.2: Transaction Bulk Upload (CSV import)
- [ ] US-6.3: Spending Alerts (email notification when overspend)
- [ ] US-6.4: Budget Tracking (set monthly budgets per category, track vs actual)
- [ ] US-6.5: Export to PDF/CSV (generate financial report)
- [ ] US-6.6: Dark Mode UI Theme
- [ ] US-6.7: Bill Splitting (split transaction among multiple members)
- [ ] US-6.8: Financial Goal Setting (savings goals, track progress)
- [ ] US-6.9: Multi-Currency Support (USD, EUR, VND, etc.)
- [ ] US-6.10: Mobile App (iOS/Android native)

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | PM | Created detailed backlog with 22 MVP user stories (119 points) |

