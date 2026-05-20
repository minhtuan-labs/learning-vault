# User Stories — NestFi

## Story Group 1: Authentication & Account Setup

### US-1.1: Superadmin Login
**As a** system administrator  
**I want to** log in with the default superadmin account  
**So that** I can initialize the system and create the first family

**Acceptance Criteria:**
- [ ] System creates superadmin account (username: `superadmin`, password: `admin123`) on first deploy
- [ ] Superadmin can log in with these credentials
- [ ] After first login, superadmin can change their password
- [ ] Subsequent logins require the new password (old one no longer works)

**Edge Cases:**
- What if superadmin changes password then forgets it? (Out of v1 scope - manual admin reset)

---

### US-1.2: User Registration via Email Invitation
**As a** superadmin  
**I want to** invite a user to be a family owner via email  
**So that** the user can accept and start managing family finances

**Acceptance Criteria:**
- [ ] Superadmin can input an email address to invite
- [ ] An email invitation is sent to the provided email
- [ ] Email contains a unique confirmation link (valid for 7 days, or TBD)
- [ ] User clicks link and is prompted to create/confirm account details
- [ ] Account is marked "active" only after email confirmation
- [ ] Confirmed user can immediately log in

**Edge Cases:**
- What if user clicks confirmation link twice? (Second click should show "already confirmed" message)
- What if invitation expires? (User sees "invitation expired, ask superadmin to resend")
- What if email is already registered to another account? (Show "email already in use, try logging in instead")

---

### US-1.3: User Login
**As a** registered user  
**I want to** log in with email and password  
**So that** I can access my families' financial data

**Acceptance Criteria:**
- [ ] User can enter email and password
- [ ] On correct credentials, user is authenticated
- [ ] On incorrect credentials, user sees "Invalid email or password" (same message for both cases for security)
- [ ] After login, if user belongs to multiple families, they are prompted to select which one to view
- [ ] If user belongs to only one family, they are logged directly into that family's dashboard

**Edge Cases:**
- User attempts login with non-existent email (show "Invalid email or password")
- User attempts login with correct email but wrong password (show "Invalid email or password")

---

### US-1.4: Password Reset
**As a** user  
**I want to** reset my password if I forget it  
**So that** I can regain access to my account

**Acceptance Criteria:**
- [ ] User clicks "Forgot Password" on login page
- [ ] User enters their email address
- [ ] Email with reset link is sent
- [ ] Link is unique and expires after 1 hour (or TBD)
- [ ] User clicks link and sets a new password
- [ ] User can then log in with new password

**Edge Cases:**
- User requests multiple password resets (previous link is invalidated)
- User tries to use an expired reset link (show "link expired, request a new one")

---

## Story Group 2: Family Management

### US-2.1: Create a New Family
**As a** family owner (invited by superadmin)  
**I want to** set up a family and name it  
**So that** I can start managing household finances

**Acceptance Criteria:**
- [ ] After email confirmation, owner is prompted to name their family
- [ ] Family name is saved and becomes the main label
- [ ] Owner is automatically set as the family owner
- [ ] Family can have 1 or more bank accounts created later
- [ ] Family is ready to accept member invitations

**Edge Cases:**
- Family name is blank (show validation error "Family name is required")
- Family name is duplicate of another (allow it; family names don't need to be globally unique)

---

### US-2.2: Add Family Members
**As a** family owner  
**I want to** invite other users (e.g., spouse, adult children) to join the family  
**So that** we can collectively manage finances

**Acceptance Criteria:**
- [ ] Owner can input an email address to invite as member
- [ ] Invitation is sent to the email
- [ ] Email contains confirmation link specific to this family
- [ ] Invitee clicks link and joins the family (as "member" role)
- [ ] Once confirmed, member can log in and view/edit family transactions
- [ ] Owner can see a list of pending and active members

**Edge Cases:**
- Invitee is not yet a NestFi user (invitation still works; they create account on first login)
- Invitee already belongs to another family (they can now belong to this family too)
- Owner invites the same email twice (second invite replaces/supersedes first)
- Invitee declines invitation (out of v1 scope; assume accept-only for now)

---

### US-2.3: View Family Members
**As a** family owner or member  
**I want to** see who is in my family  
**So that** I know who has access to our financial data

**Acceptance Criteria:**
- [ ] Members list shows all active members with their email and join date
- [ ] Pending invitations are shown separately with "Pending" badge
- [ ] Owner can resend invitation to pending members

---

### US-2.4: Disable/Enable Family Members
**As a** family owner  
**I want to** disable or remove access for family members  
**So that** only active members can view family financial data

**Acceptance Criteria:**
- [ ] Owner can view list of family members
- [ ] Owner can disable a member (not hard-delete) from the family
- [ ] Disabled member no longer sees family data and is immediately logged out
- [ ] All transactions recorded by the disabled member remain on family accounts (attributed by creator name)
- [ ] Owner can re-enable a disabled member to restore their access
- [ ] Edit history and transaction records are preserved across disable/enable cycles

**Edge Cases:**
- Can owner remove themselves? (No; must invite another owner first or have another owner present)
- What happens if a disabled member is re-enabled? (They regain full access, and all their transactions/edits remain intact)

---

## Story Group 3: Account Management

### US-3.1: Create Bank Account
**As a** family owner or member  
**I want to** add a bank account (checking, savings, etc.) to track funds  
**So that** I can record transactions against it

**Acceptance Criteria:**
- [ ] User can create a new account with name (e.g., "Main Checking")
- [ ] Account type is selected (bank, savings, investment, cash)
- [ ] Initial balance is optional (defaults to 0)
- [ ] Currency is selected (defaults to account owner's preference or USD)
- [ ] Account is created and appears in the account list
- [ ] Account is visible to all family members

**Edge Cases:**
- Account name is blank (show validation error)
- Initial balance is negative (allow it; might represent overdraft)

---

### US-3.2: View All Accounts
**As a** family member  
**I want to** see all bank accounts and their current balances  
**So that** I know total household liquidity at a glance

**Acceptance Criteria:**
- [ ] Dashboard shows a list of all family accounts
- [ ] Each account shows current balance (calculated from transactions)
- [ ] Account type is displayed
- [ ] Accounts can be sorted by type or balance

---

### US-3.3: Edit Account
**As a** family member  
**I want to** update account details (name, type)  
**So that** I can keep account information accurate

**Acceptance Criteria:**
- [ ] User can edit account name and type
- [ ] Changes are saved and reflected across the family
- [ ] Edit history is optional for v1 (not required)

---

## Story Group 4: Categories & Transaction Setup

### US-4.1: View Default Categories
**As a** family member  
**I want to** see predefined income and expense categories  
**So that** I can quickly categorize transactions

**Acceptance Criteria:**
- [ ] Income categories exist: Salary, Bonus, Investment Return, Other Income
- [ ] Expense categories exist: Groceries, Utilities, Entertainment, Transportation, Healthcare, Cash Withdrawal, Other Expense
- [ ] Investment categories exist: Stocks, Bonds, Real Estate, Other Investment
- [ ] Categories are pre-populated per family on family creation

---

### US-4.2: Create Custom Category
**As a** family owner  
**I want to** add custom categories for unique expense/income types  
**So that** categorization reflects our household needs

**Acceptance Criteria:**
- [ ] Owner can create new categories (income, expense, or investment)
- [ ] Category name is required
- [ ] Optional icon/emoji for visual identification
- [ ] Custom categories are visible to all family members
- [ ] Default categories cannot be deleted (soft-delete or flag as immutable)

**Edge Cases:**
- Category name is blank (validation error)
- Category name duplicates existing one (allow it; use distinct IDs)
- Member attempts to create category (owner-only; show "permission denied")

---

## Story Group 5: Transaction Recording

**Note:** All transactions in NestFi are account-centric. When recording a transaction, the user must select which account it belongs to. There is no person-level spending tracking or bill-splitting; all family members have equal visibility and can record transactions to any family account.

**Transaction Lifecycle Rules:**
- All family members can **disable/enable** (hide/show) any transaction; disabled transactions are excluded from P&L reports and dashboards
- Only family owner can **permanently delete** a transaction (hard delete); this action is irreversible
- All transaction edits are tracked with editor info and timestamp; edit history is visible to all family members in transaction detail view

### US-5.1: Record Income Transaction
**As a** family member  
**I want to** record an income event (salary, bonus, gift, etc.)  
**So that** the family budget accounts for total income

**Acceptance Criteria:**
- [ ] User selects an account and category
- [ ] User enters amount, date, and optional description
- [ ] Amount is recorded as "incoming" to the account
- [ ] Transaction is saved and appears in account history
- [ ] All family members can view this transaction

**Edge Cases:**
- Amount is 0 or negative (validation: amount must be > 0)
- Date is in the future (allow it; future-dated transactions for planning)
- Date is very far in the past (allow it; no hardcoded date limits)

---

### US-5.2: Record Expense Transaction
**As a** family member  
**I want to** record an expense (groceries, utilities, etc.)  
**So that** we track where money is going

**Acceptance Criteria:**
- [ ] User selects an account and expense category
- [ ] User enters amount, date, and optional description
- [ ] Amount is recorded as "outgoing" from the account
- [ ] Transaction is saved and appears in account history
- [ ] All family members can view this transaction

**Edge Cases:**
- Amount exceeds account balance (allow it; permit negative balance for overdraft scenarios)
- Special case: "Cash Withdrawal" category records as expense (handled transparently)

---

### US-5.3: Record Investment Transaction
**As a** family member  
**I want to** record an investment purchase or contribution  
**So that** we track savings and investment growth

**Acceptance Criteria:**
- [ ] User selects investment account and investment category
- [ ] User enters amount, date, and optional description
- [ ] Amount is recorded as "outgoing" from source account (if buying)
- [ ] Transaction is saved in investment account history
- [ ] All family members can view investment activity

---

### US-5.4: Edit Transaction
**As a** family member  
**I want to** correct or update a transaction  
**So that** our records stay accurate

**Acceptance Criteria:**
- [ ] User can click "Edit" on any transaction (all members have equal editing rights)
- [ ] User can change amount, category, date, or description
- [ ] Changes are saved immediately
- [ ] All family members see updated transaction
- [ ] Edit is recorded with editor name, timestamp, and summary of what changed
- [ ] Edit history is visible to all family members via transaction detail view
- [ ] Full audit trail of all edits is maintained (no edit is overwritten)

**Edge Cases:**
- User tries to edit a transaction recorded by another member (allowed; all members have equal access)
- Editing changes account balance retroactively (balance is recalculated)
- User makes multiple edits to same transaction (each edit is logged separately)

---

### US-5.5: Disable/Restore Transaction
**As a** family member  
**I want to** hide a transaction from reports  
**So that** I can correct mistakes without losing the record

**Acceptance Criteria:**
- [ ] Any family member can disable (hide) a transaction
- [ ] Disabled transactions do not appear in P&L reports, dashboards, or summaries
- [ ] Disabled transactions remain in the transaction archive (can be viewed if explicitly filtered)
- [ ] Any family member can re-enable a disabled transaction to restore it to reports
- [ ] Only family owner can permanently delete (hard-delete) a transaction
- [ ] Hard-deleted transactions cannot be recovered

**Edge Cases:**
- User disables a transaction from a month ago (allowed; P&L for that month is recalculated)
- Owner hard-deletes a transaction (it is permanently removed; cannot be recovered)
- Multiple members disable/enable the same transaction (last action determines current state)

---

## Story Group 6: Dashboard & Reporting

### US-6.1: View Dashboard Summary
**As a** family member  
**I want to** see a dashboard with key financial metrics  
**So that** I understand the family's financial health at a glance

**Acceptance Criteria:**
- [ ] Dashboard displays total income (current month/year, or selectable)
- [ ] Dashboard displays total expenses
- [ ] Dashboard displays net savings (income - expenses)
- [ ] Dashboard shows account balances by account
- [ ] Dashboard is updated in real-time as transactions are added

---

### US-6.2: View Expense Breakdown by Category
**As a** family member  
**I want to** see how much we spent in each category  
**So that** I can identify spending patterns and areas to cut

**Acceptance Criteria:**
- [ ] Chart or table shows total spent per category for selected period
- [ ] Period is selectable (current month, last 3 months, year, custom range)
- [ ] Categories are sortable by amount
- [ ] Can filter by category (e.g., show only entertainment expenses)

---

### US-6.3: View Income vs. Expense Trends
**As a** family member  
**I want to** see income and expense trends over time  
**So that** I can track whether we're saving more or spending more

**Acceptance Criteria:**
- [ ] Chart displays income and expense for each month (or week/day, configurable)
- [ ] Trend line shows net savings over time
- [ ] User can select custom date range
- [ ] Chart is easy to read and mobile-friendly (stretch goal for v1)

---

### US-6.4: Export Financial Report
**As a** family owner  
**I want to** download a report of transactions and summaries  
**So that** I can share with accountant or for personal records

**Acceptance Criteria:**
- [ ] User can export transactions as CSV
- [ ] User can export summary report as PDF (or TBD format)
- [ ] Export includes date range selection
- [ ] Export includes all selected transactions with category

**Note:** This is a stretch goal for v1; may defer to v1.1.

---

## Story Group 7: Security & Data

### US-7.1: Logout
**As a** user  
**I want to** log out of my session  
**So that** someone else cannot access my account on shared device

**Acceptance Criteria:**
- [ ] User can click "Logout" button
- [ ] Session is terminated
- [ ] User is redirected to login page
- [ ] Session cookie/token is invalidated

---

### US-7.2: Session Timeout
**As a** system  
**I want to** automatically log out inactive users  
**So that** we reduce security risk

**Acceptance Criteria:**
- [ ] User is logged out after 30 minutes of inactivity (or TBD)
- [ ] User is shown warning before logout (e.g., 5-minute warning)
- [ ] Inactivity timer resets on any user action

**Note:** Stretch goal for v1; may defer.

---

## Open Questions

**DECIDED:**
- ✅ **Q4 — Transaction Deletion:** All users can disable/enable transactions (soft-delete); disabled txns don't count in P&L. Only owner can permanently delete (hard-delete). See US-5.5.
- ✅ **Q5 — Edit History:** Yes, track edit history with editor name and timestamp. All edits visible to family members. See US-5.4.
- ✅ **Q7 — Member Removal:** Owner can disable members (not hard-delete) to preserve transactions. See US-2.4.

**DEFERRED (v1.1 or TBD):**
- What is the session timeout duration? (Currently marked as TBD in US-7.2)
- Should we support exporting reports in v1, or defer to v1.1? (Marked as stretch goal in US-6.4)
