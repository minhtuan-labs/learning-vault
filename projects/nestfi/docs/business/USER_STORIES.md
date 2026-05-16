# User Stories — NestFi

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** BA  

---

## Overview

This document contains the user stories for NestFi MVP (v1), prioritized by phase and role. Stories follow the standard format: **As a [actor], I want [feature] so that [benefit]**, with acceptance criteria defining "done".

---

## 1. Superadmin Account & System Administration

### US-001: Superadmin logs in with default credentials

**As a** system administrator  
**I want** to access the NestFi superadmin dashboard using default credentials (superadmin/admin123)  
**so that** I can manage families and invite initial owners.

**Acceptance Criteria:**
- [ ] System provides default superadmin account at setup
- [ ] Login page accepts username and password
- [ ] Superadmin can authenticate and reach admin dashboard
- [ ] Default password can be changed by superadmin after first login
- [ ] Failed login attempts prevent unauthorized access

---

### US-002: Superadmin changes initial password

**As a** system administrator  
**I want** to change the default superadmin password upon first login  
**so that** the account is secure and no longer uses hardcoded credentials.

**Acceptance Criteria:**
- [ ] Superadmin prompted to change password on first login (or via settings)
- [ ] Password change requires entering current password
- [ ] New password meets security requirements (min 8 chars, mixed case, numbers/symbols)
- [ ] Confirmation message appears after successful change
- [ ] Old password no longer works for authentication

---

## 2. Family Creation & Superadmin Management

### US-003: Superadmin creates a new family

**As a** superadmin  
**I want** to create a new family in the system  
**so that** I can onboard a household to NestFi.

**Acceptance Criteria:**
- [ ] Superadmin can access "Create Family" form in dashboard
- [ ] Form requires family name and optional description
- [ ] Family is created in the database with active status
- [ ] Success message confirms family created
- [ ] Family ID generated and retrievable by superadmin
- [ ] Created family appears in superadmin's family list

---

### US-004: Superadmin invites initial owner via email

**As a** superadmin  
**I want** to invite the initial owner of a family via email  
**so that** the owner can accept and begin managing the family.

**Acceptance Criteria:**
- [ ] Superadmin enters owner's email address in create/edit family flow
- [ ] Email invitation is sent with unique acceptance link/token
- [ ] Email contains family name, invitation context, and acceptance instructions
- [ ] Acceptance link is unique and one-time-use
- [ ] Link expires after 30 days (or configurable timeout)
- [ ] Superadmin can resend invitation if needed
- [ ] Invitation status (pending, accepted, declined) visible to superadmin

---

## 3. Owner Onboarding & Invitation Acceptance

### US-005: Owner receives and views family invitation

**As a** prospective owner  
**I want** to receive an email invitation to join a family  
**so that** I understand my role and can decide whether to accept.

**Acceptance Criteria:**
- [ ] Email received from noreply@nestfi (or similar) address
- [ ] Subject line includes family name ("You've been invited to NestFi — <FamilyName>")
- [ ] Email body includes family name and sender context (from superadmin)
- [ ] Email contains clickable acceptance link
- [ ] Email contains fallback text with manual link if HTML fails
- [ ] Email delivered within 5 minutes of superadmin invite
- [ ] Link tracking shows whether owner opened email (optional)

---

### US-006: Owner accepts family invitation and creates account

**As a** prospective owner  
**I want** to accept a family invitation and create my account  
**so that** I can log in and manage the family.

**Acceptance Criteria:**
- [ ] Clicking acceptance link redirects to "Accept Invitation" page
- [ ] Page displays family name and acceptance context
- [ ] Form collects: email (pre-filled), full name, password
- [ ] Password field includes validation feedback (length, complexity)
- [ ] Form includes email verification step (if not pre-verified)
- [ ] After submission, account is created and user is logged in
- [ ] Superadmin sees invitation status as "accepted"
- [ ] User redirected to family dashboard

---

### US-007: Owner declines family invitation

**As a** prospective owner  
**I want** to decline a family invitation  
**so that** I am not added to a family I cannot manage.

**Acceptance Criteria:**
- [ ] Acceptance link page includes "Decline" button/option
- [ ] Clicking decline shows confirmation ("This family won't be added to your account")
- [ ] After decline, superadmin sees invitation status as "declined"
- [ ] Declined user does not appear in family member list
- [ ] Superadmin can re-invite the same email to a different family

---

## 4. Family Member Management

### US-008: Owner invites family members via email

**As a** family owner  
**I want** to invite other family members by email  
**so that** they can access and log transactions in our family account.

**Acceptance Criteria:**
- [ ] Owner can access "Invite Members" interface from family settings
- [ ] Form accepts email address(es) and optional permission level (member/admin)
- [ ] Invitation email sent to member with unique acceptance link
- [ ] Member email included in invitation for context
- [ ] Invitation status visible in family member management panel
- [ ] Owner can resend or cancel pending invitations
- [ ] Member receives email within 5 minutes

---

### US-009: Family member accepts family invitation

**As a** invited family member  
**I want** to accept an invitation to join a family  
**so that** I can log in and access the family's financial data.

**Acceptance Criteria:**
- [ ] Email invitation received with acceptance link (similar to owner invitation)
- [ ] Clicking link shows "Accept Invitation" page with family name
- [ ] If user has existing account, form shows "Log in to accept"
- [ ] If user is new, form collects email, name, and password
- [ ] After acceptance, user is logged in
- [ ] User appears in family member list with "Active" status
- [ ] User can immediately access family dashboard

---

### US-010: Family member declines family invitation

**As a** invited family member  
**I want** to decline a family invitation  
**so that** I am not added to a family I cannot manage.

**Acceptance Criteria:**
- [ ] Acceptance link page includes "Decline" button
- [ ] After decline, owner sees member status as "declined"
- [ ] Declined member does not appear in active member list
- [ ] Owner can re-invite the same email

---

### US-011: Owner views family member list

**As a** family owner  
**I want** to see all current and pending members of my family  
**so that** I know who has access and can manage permissions.

**Acceptance Criteria:**
- [ ] Family settings / member management page displays all members
- [ ] List shows: name, email, role (owner/member), join date, status (active/pending/declined)
- [ ] Members sorted by join date (newest first) or name
- [ ] Owner can see count of active members
- [ ] Pending invitations clearly marked with expiration date
- [ ] Declined invitations archived/hidden or clearly marked as declined

---

### US-012: Owner removes a family member

**As a** family owner  
**I want** to remove a family member from the family  
**so that** they can no longer view or edit family financial data.

**Acceptance Criteria:**
- [ ] Owner can click "Remove" button next to member name
- [ ] Confirmation dialog appears ("Are you sure? <Name> will lose access to this family")
- [ ] After confirmation, member is removed from member list
- [ ] Removed member cannot log in to family account (receives "Access Denied")
- [ ] Member's transactions are archived/retained (for audit)
- [ ] Owner can re-invite removed member later

---

### US-013: User switches between multiple families

**As a** user who belongs to multiple families  
**I want** to switch between families without logging out  
**so that** I can quickly access different household accounts.

**Acceptance Criteria:**
- [ ] Dashboard or main menu shows family selector (dropdown, sidebar, or switcher)
- [ ] Clicking selector shows list of families user belongs to
- [ ] Selecting a family loads that family's dashboard without re-login
- [ ] Current family is highlighted/indicated
- [ ] URL or breadcrumb shows current family context
- [ ] Switching families is immediate (no page reload delay)

---

## 5. Transaction Logging

### US-014: Family member logs an income transaction

**As a** family member  
**I want** to log an income transaction (e.g., salary, bonus)  
**so that** the family can track household income.

**Acceptance Criteria:**
- [ ] "Add Transaction" form accessible from dashboard
- [ ] Form fields: amount, category (income category), date, optional notes
- [ ] Category dropdown shows only income categories
- [ ] Amount field accepts decimal numbers (e.g., 1500.50)
- [ ] Date field defaults to today but can be changed
- [ ] Notes field is optional
- [ ] Submit button logs transaction and displays confirmation
- [ ] Transaction immediately appears in family ledger (visible to all members)
- [ ] Transaction attributed to logged-in user as author

---

### US-015: Family member logs an expense transaction

**As a** family member  
**I want** to log an expense transaction (e.g., groceries, utilities)  
**so that** the family can track household spending.

**Acceptance Criteria:**
- [ ] "Add Transaction" form accessible from dashboard
- [ ] Form fields: amount, category (expense category), date, optional notes
- [ ] Category dropdown shows only expense categories
- [ ] Amount field accepts decimal numbers
- [ ] Date field defaults to today but can be changed
- [ ] Notes field is optional
- [ ] Submit button logs transaction and displays confirmation
- [ ] Transaction immediately appears in family ledger
- [ ] Transaction attributed to logged-in user as author

---

### US-016: Family member logs a cash withdrawal transaction

**As a** family member  
**I want** to log a cash withdrawal as a transaction  
**so that** cash spending is tracked in the household finances.

**Acceptance Criteria:**
- [ ] Cash withdrawal can be logged as an expense with category "Cash Withdrawal"
- [ ] Form fields: amount, date, optional notes (no category picker needed)
- [ ] Cash withdrawal is automatically assigned to "Cash Withdrawal" category
- [ ] Amount field accepts decimal numbers
- [ ] Date field defaults to today
- [ ] Submit button logs transaction and displays confirmation
- [ ] Transaction appears in ledger as expense
- [ ] Contributes to total expenses on dashboard

---

### US-017: Family member views transaction history

**As a** family member  
**I want** to view the complete transaction history for my family  
**so that** I can understand our spending and income patterns.

**Acceptance Criteria:**
- [ ] Ledger/history view accessible from main menu or dashboard
- [ ] Displays all transactions (income, expense, cash withdrawal) in reverse chronological order
- [ ] Shows for each transaction: date, category, amount, member, notes
- [ ] Default view shows last 30 days or all transactions (configurable)
- [ ] List can be sorted by date, category, or amount
- [ ] List includes count of total transactions displayed
- [ ] Page loads within 3 seconds for typical household (100-1000 transactions)

---

### US-018: Family member filters transaction history by category

**As a** family member  
**I want** to filter transaction history by category  
**so that** I can analyze spending in a specific area (e.g., groceries).

**Acceptance Criteria:**
- [ ] Ledger view includes category filter (dropdown or checkbox)
- [ ] Filter shows all active categories for the family
- [ ] Selecting a category shows only transactions in that category
- [ ] Multiple categories can be selected (OR logic)
- [ ] Filter results update immediately
- [ ] Clear filter button resets to all transactions
- [ ] Filter persists while browsing, resets on page reload

---

### US-019: Family member filters transaction history by date range

**As a** family member  
**I want** to filter transaction history by date range  
**so that** I can analyze spending for a specific month or period.

**Acceptance Criteria:**
- [ ] Ledger view includes date range filter (start date, end date)
- [ ] Date picker allows selecting custom range
- [ ] Preset options available (Last 7 days, Last 30 days, This month, Year-to-date)
- [ ] Filter results update immediately
- [ ] Clear filter button resets to default range
- [ ] Invalid ranges (end before start) show error message

---

### US-020: Family member edits their own transaction

**As a** family member  
**I want** to edit a transaction I logged  
**so that** I can correct mistakes in amount, category, or date.

**Acceptance Criteria:**
- [ ] "Edit" button appears on own transactions in ledger view
- [ ] Clicking edit opens form with pre-filled transaction data
- [ ] Form allows changing: amount, category, date, notes
- [ ] Submit button saves changes and displays confirmation
- [ ] Updated transaction immediately reflects in ledger and dashboard
- [ ] Audit log records: original values, updated values, timestamp, user
- [ ] Member cannot edit other members' transactions

---

### US-021: Family owner edits any transaction

**As a** family owner  
**I want** to edit any family transaction (not just my own)  
**so that** I can correct data entry errors from any member.

**Acceptance Criteria:**
- [ ] "Edit" button appears on all transactions (not just owner's)
- [ ] Clicking edit opens form with pre-filled transaction data
- [ ] Form allows changing: amount, category, date, notes
- [ ] Submit button saves changes with audit trail
- [ ] Updated transaction immediately reflects in ledger and dashboard
- [ ] Audit log records: transaction ID, original values, updated values, timestamp, owner
- [ ] Regular members cannot edit other members' transactions

---

### US-022: Family member deletes their own transaction

**As a** family member  
**I want** to delete a transaction I logged  
**so that** I can remove duplicate or erroneous entries.

**Acceptance Criteria:**
- [ ] "Delete" button appears on own transactions in ledger view
- [ ] Clicking delete shows confirmation ("Are you sure? This cannot be undone")
- [ ] After confirmation, transaction is marked as deleted (soft delete)
- [ ] Deleted transaction no longer appears in ledger
- [ ] Audit log records deletion: transaction ID, deleted by, timestamp
- [ ] Dashboard statistics exclude deleted transactions
- [ ] Member cannot delete other members' transactions

---

## 6. Category Management

### US-023: Owner creates a custom income category

**As a** family owner  
**I want** to create a new income category  
**so that** the family can categorize different income sources (salary, freelance, etc.).

**Acceptance Criteria:**
- [ ] "Add Category" form accessible from category management interface
- [ ] Form requires: category name, type (income), optional description
- [ ] Name field accepts alphanumeric and common symbols
- [ ] Optional: color/icon selection for visual organization
- [ ] Submit button creates category and displays confirmation
- [ ] New category immediately appears in category list
- [ ] New category available in transaction logging forms

---

### US-024: Owner creates a custom expense category

**As a** family owner  
**I want** to create a new expense category  
**so that** the family can categorize different types of spending.

**Acceptance Criteria:**
- [ ] "Add Category" form accessible from category management interface
- [ ] Form requires: category name, type (expense), optional description
- [ ] Name field accepts alphanumeric and common symbols
- [ ] Optional: color/icon selection for visual organization
- [ ] Submit button creates category and displays confirmation
- [ ] New category immediately appears in category list
- [ ] New category available in transaction logging forms

---

### US-025: Owner creates a custom investment category

**As a** family owner  
**I want** to create a custom investment category  
**so that** the family can track investment accounts and portfolio entries.

**Acceptance Criteria:**
- [ ] "Add Category" form accessible from category management interface
- [ ] Form requires: category name, type (investment), optional description
- [ ] Optional: color/icon selection for visual organization
- [ ] Submit button creates category and displays confirmation
- [ ] New category immediately appears in category list
- [ ] Category available for investment tracking (v1: simple amount tracking)

---

### US-026: System provides default categories

**As a** family owner  
**I want** the system to provide standard categories at family setup  
**so that** we can start logging transactions immediately.

**Acceptance Criteria:**
- [ ] When a family is created, default categories are auto-generated
- [ ] Default income categories: Salary, Bonus, Freelance, Interest, Other Income
- [ ] Default expense categories: Groceries, Utilities, Entertainment, Transport, Cash Withdrawal, Other Expense
- [ ] Default investment categories: Stock Portfolio, Retirement, Crypto, Other Investment
- [ ] Owner can modify or delete default categories
- [ ] Default categories are marked as "system default" (optional visual indicator)

---

### US-027: Owner views family category list

**As a** family owner  
**I want** to view all income, expense, and investment categories for the family  
**so that** I can manage and customize financial categories.

**Acceptance Criteria:**
- [ ] Category management page displays all categories
- [ ] Categories grouped by type (income, expense, investment)
- [ ] Each category shows: name, description, count of transactions using it
- [ ] Categories sorted alphabetically within each type
- [ ] Owner can see which categories are system default
- [ ] Page indicates total count of active categories

---

### US-028: Owner edits a category

**As a** family owner  
**I want** to edit a category's name, description, or appearance  
**so that** the category remains relevant to our family's needs.

**Acceptance Criteria:**
- [ ] "Edit" button appears on each category
- [ ] Edit form allows changing: name, description, color/icon
- [ ] Submit button saves changes and displays confirmation
- [ ] Changed category name updates in transaction history
- [ ] Cannot change category type (income → expense, etc.)
- [ ] Transactions previously tagged with category remain unchanged
- [ ] Edit immediately reflects in ledger and transaction forms

---

### US-029: Owner archives a category

**As a** family owner  
**I want** to archive a category that we no longer use  
**so that** it doesn't clutter the transaction form but history is preserved.

**Acceptance Criteria:**
- [ ] "Archive" button available on each active category
- [ ] Clicking archive shows confirmation ("This category will no longer appear in transaction forms")
- [ ] After archive, category moved to "Inactive" section
- [ ] Archived category no longer appears in transaction logging dropdowns
- [ ] Existing transactions with archived category still display correctly
- [ ] Statistics still include archived category data (historical)
- [ ] Owner can reactivate archived categories later

---

### US-030: Owner reactivates an archived category

**As a** family owner  
**I want** to reactivate an archived category  
**so that** we can use it again if our needs change.

**Acceptance Criteria:**
- [ ] Inactive/archived categories section shows "Reactivate" button
- [ ] Clicking reactivate moves category back to active list
- [ ] Reactivated category immediately available in transaction logging
- [ ] Previous transactions with this category remain unchanged
- [ ] Confirmation message shown after reactivation

---

## 7. Dashboard & Analytics

### US-031: Family member views financial overview dashboard

**As a** family member  
**I want** to see a dashboard with household financial overview  
**so that** I understand our family's financial health at a glance.

**Acceptance Criteria:**
- [ ] Dashboard accessible immediately after login
- [ ] Displays current month summary: total income, total expenses, net savings
- [ ] Savings rate calculated and displayed (income - expenses)
- [ ] Dashboard shows transaction count (how many logged this month)
- [ ] Layout optimized for desktop; responsive for tablets
- [ ] Page loads within 3 seconds
- [ ] Clicking on summary cards shows detailed breakdown (optional drill-down)

---

### US-032: Family member views category spending breakdown

**As a** family member  
**I want** to see a breakdown of spending by category (pie chart or bar chart)  
**so that** I can identify where our money is going.

**Acceptance Criteria:**
- [ ] Dashboard includes category breakdown chart (pie or bar)
- [ ] Chart displays only expense categories by default
- [ ] Each category shows absolute amount and percentage of total
- [ ] Chart is interactive (hover for details, click for drilldown)
- [ ] Chart renders within 2 seconds
- [ ] Mobile-responsive chart layout
- [ ] Color coding matches category colors (if configured)

---

### US-033: Family member views income by category

**As a** family member  
**I want** to see income categorized and tracked  
**so that** I understand household income sources.

**Acceptance Criteria:**
- [ ] Dashboard or separate income view shows income categories
- [ ] Each category displays total amount for current period (month/year)
- [ ] Income chart or table shows breakdown by category
- [ ] Sortable by amount (descending by default)
- [ ] Comparison with previous month available (optional)

---

### US-034: Family member views monthly spending trends

**As a** family member  
**I want** to see historical spending trends (last 6-12 months)  
**so that** I understand seasonal patterns and long-term trends.

**Acceptance Criteria:**
- [ ] Dashboard includes line or area chart showing monthly expenses
- [ ] Chart displays last 6-12 months (configurable)
- [ ] Y-axis shows amount, X-axis shows month/year
- [ ] Hover shows exact amount for each month
- [ ] Chart is interactive (can zoom, pan, or filter by category)
- [ ] Mobile-responsive chart layout
- [ ] Chart renders within 3 seconds

---

### US-035: Family member views member activity log

**As a** family member  
**I want** to see which family members logged transactions and when  
**so that** I understand who is contributing to household finances.

**Acceptance Criteria:**
- [ ] Dashboard or separate activity view shows recent transactions by member
- [ ] Displays member name, transaction date, category, amount
- [ ] Sortable by member, date, or amount
- [ ] Filter by member available
- [ ] Activity feed shows latest transactions first
- [ ] Shows count of transactions per member (summary)

---

### US-036: Family member exports dashboard data

**As a** family member  
**I want** to export financial data to a file (CSV, PDF)  
**so that** I can analyze data in spreadsheets or share with financial advisors.

**Acceptance Criteria:**  
*(Deferred to v2; noted here for completeness)*
- [ ] Export button on dashboard
- [ ] Format options: CSV, PDF
- [ ] Export includes: transactions, categories, summary statistics
- [ ] File includes date range and family name

---

## 8. Bank Accounts (Optional for v1, Tracked for v2)

### US-037: Owner adds a family bank account

**As a** family owner  
**I want** to add a bank account to the family's financial system  
**so that** we can track multiple accounts and balances.

**Acceptance Criteria:**  
*(Optional for v1; placeholder for v2)*
- [ ] "Add Account" form accessible from settings
- [ ] Form requires: account name, account type, currency, optional balance
- [ ] Submit creates account record
- [ ] Account appears in account list
- [ ] Transactions can be assigned to accounts (optional)

---

## Notes & Conventions

### Priority & Phasing
- **US-001 to US-012**: Core authentication and family management (Phase 0-1)
- **US-013 to US-022**: Transaction logging and ledger (Phase 2)
- **US-023 to US-030**: Category management (Phase 2-3)
- **US-031 to US-036**: Dashboard and analytics (Phase 2-3)
- **US-037**: Bank accounts (deferred to v2)

### Acceptance Criteria Notes
- All acceptance criteria should be verified by QA before marking stories as "done"
- "Immediately" in criteria means within 5 seconds (typical web response time)
- Email delivery targets are SLAs; monitoring required in production
- Chart performance requirements assume data sets up to 1000 transactions

### Future Considerations (v2+)
- Budget tracking and alerts
- Bill splitting logic
- Advanced analytics and forecasting
- Mobile app
- Multi-currency support
- Tax reporting integration

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | BA | Created initial user stories from PRD and business requirements |
