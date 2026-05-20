# Test Cases — NestFi v1.0

**Status**: DRAFT (Phase 3 — Implementation Planning)  
**Prepared by**: QA  
**Last Updated**: 2026-05-16

This document maps test cases to user stories and acceptance criteria. Each test is numbered TC-xxx and includes preconditions, steps, and expected results.

---

## Story Group 1: Authentication & Account Setup

### US-1.1: Superadmin Login

**TC-1.1.1**: Superadmin logs in with superadmin/admin123
- **Precondition**: System deployed; superadmin account exists
- **Steps**: Enter credentials, click [Login]
- **Expected**: Redirected to superadmin dashboard

**TC-1.1.2**: Superadmin forced password change on first login
- **Precondition**: Fresh deploy
- **Steps**: Log in; system prompts for password change
- **Expected**: Password changed; old password no longer works

---

### US-1.2: User Registration via Email Invitation

**TC-1.2.1**: Owner accepts invitation and sets password
- **Precondition**: Superadmin invited owner@example.com
- **Steps**: Click invitation link, see family details, click [Accept], enter password
- **Expected**: Account activated; can log in

**TC-1.2.2**: Invitation link expires after 7 days
- **Precondition**: Invitation token > 7 days old
- **Expected**: "Invitation expired" message

**TC-1.2.3**: Cannot accept same invitation twice
- **Precondition**: Owner accepted invitation
- **Steps**: Try to open same URL again
- **Expected**: "Already accepted" or redirect to login

---

### US-1.3: User Login

**TC-1.3.1**: User logs in with email and password
- **Steps**: Enter email/password, click [Login]
- **Expected**: Authenticated; redirected to dashboard or family selector

**TC-1.3.2**: Single-family user redirected directly
- **Precondition**: User in 1 family
- **Expected**: Directly to family dashboard (no selector)

**TC-1.3.3**: Multi-family user sees selector
- **Precondition**: User in 2+ families
- **Expected**: Family selector dropdown shown

**TC-1.3.4**: Invalid credentials show error
- **Steps**: Try non-existent email or wrong password
- **Expected**: "Invalid email or password"

---

### US-1.4: Password Reset (SHOULD)

**TC-1.4.1**: User requests reset and uses token from logs
- **Steps**: Click [Forgot Password], enter email, extract token from logs, set new password
- **Expected**: Password reset; can log in with new password

**TC-1.4.2**: Reset token expires after 1 hour
- **Precondition**: Token > 1 hour old
- **Expected**: "Link expired" message

---

## Story Group 2: Family Management

### US-2.1: Create a New Family

**TC-2.1.1**: Owner creates family after accepting invitation
- **Precondition**: Owner logged in after password setup
- **Steps**: Click [Create Family], enter name "Test Family", click [Create]
- **Expected**: Family created; owner designated; redirected to dashboard

**TC-2.1.2**: Family name is required
- **Steps**: Leave name blank, click [Create]
- **Expected**: Validation error

---

### US-2.2: Add Family Members

**TC-2.2.1**: Owner invites member
- **Steps**: Click [Add Member], enter email, click [Send Invitation]
- **Expected**: Invitation sent; member in pending list

**TC-2.2.2**: Member accepts invitation and joins family
- **Precondition**: Invitation sent
- **Steps**: Click invitation link, set password, click [Join]
- **Expected**: Member added to family; can access family data

**TC-2.2.3**: Member belongs to multiple families
- **Precondition**: Member invited to Family A and B
- **Steps**: Accept both invitations, log in
- **Expected**: Family selector shown with both families

---

### US-2.3: View Family Members (SHOULD)

**TC-2.3.1**: Owner views active members and pending invitations
- **Expected**: List shows active members with role; pending section shows pending invitations with [Resend]/[Revoke]

---

### US-2.4: Disable/Enable Members (SHOULD)

**TC-2.4.1**: Owner disables member
- **Steps**: Click [Edit] on member, click [Disable Member], confirm
- **Expected**: Member status → disabled; member immediately logged out

**TC-2.4.2**: Disabled member cannot access family
- **Steps**: Log in as disabled member, try to select family
- **Expected**: "Access denied" message

**TC-2.4.3**: Disabled member's transactions remain
- **Steps**: Log in as owner, view transactions
- **Expected**: Transactions created by disabled member still visible

**TC-2.4.4**: Owner re-enables member
- **Steps**: Click [Edit] on disabled member, click [Re-enable], confirm
- **Expected**: Member status → active; can access family again

---

## Story Group 3: Account Management

### US-3.1: Create Bank Account

**TC-3.1.1**: User creates account
- **Steps**: Click [+ New Account], enter name "Main Checking", type "Bank", initial balance 5000, click [Create]
- **Expected**: Account created; appears in account list

**TC-3.1.2**: Account name is required
- **Steps**: Leave name blank, click [Create]
- **Expected**: Validation error

**TC-3.1.3**: Initial balance can be negative
- **Steps**: Enter name, balance -1000, click [Create]
- **Expected**: Account created with negative balance (overdraft)

**TC-3.1.4**: Account visible to all family members
- **Precondition**: Account created by owner
- **Steps**: Log in as member, select same family
- **Expected**: Account appears in account list

---

### US-3.2: View All Accounts

**TC-3.2.1**: Dashboard shows all accounts with balances
- **Expected**: Accounts section displays all accounts with current balances

**TC-3.2.2**: Balance calculated from transactions
- **Precondition**: Account: initial 5000, +2000 income, -500 expense
- **Expected**: Balance = 6500

**TC-3.2.3**: Accounts sortable by type (optional)
- **Expected**: Accounts grouped by type (bank, savings, investment, cash)

**TC-3.2.4**: Accounts sortable by balance (optional)
- **Expected**: Accounts sorted by balance amount

---

### US-3.3: Edit Account (SHOULD)

**TC-3.3.1**: Member edits account name
- **Steps**: Click [Edit] on account, change name to "Primary Checking", click [Save]
- **Expected**: Name updated; visible to all members

---

## Story Group 4: Categories

### US-4.1: View Default Categories

**TC-4.1.1**: Default categories pre-populated on family creation
- **Precondition**: Family created
- **Steps**: Open transaction form, see category dropdown
- **Expected**: Categories include Income (Salary, Bonus, Investment Return, Other), Expense (Groceries, Utilities, Entertainment, Transportation, Healthcare, Cash Withdrawal, Other), Investment (Stocks, Bonds, Real Estate, Other)

**TC-4.1.2**: All members can view categories
- **Expected**: Full category list visible in transaction form

---

### US-4.2: Create Custom Category (SHOULD)

**TC-4.2.1**: Owner creates custom category
- **Steps**: Click [+ Add Category], enter name "Pet Care", type "Expense", click [Create]
- **Expected**: Category created; visible in dropdowns

**TC-4.2.2**: Member cannot create category
- **Expected**: [+ Add Category] button disabled or shows "Permission denied"

**TC-4.2.3**: Default categories cannot be deleted
- **Expected**: No delete option for default categories

---

## Story Group 5: Transaction Recording

### US-5.1: Record Income Transaction

**TC-5.1.1**: Member records income
- **Steps**: Click [+ Transaction], type Income, amount 5000, category "Salary", account "Checking", click [Save]
- **Expected**: Transaction created; account balance += 5000

**TC-5.1.2**: Amount must be > 0
- **Steps**: Enter amount 0, click [Save]
- **Expected**: "Amount must be greater than 0"

**TC-5.1.3**: Future-dated income allowed
- **Steps**: Enter future date (2026-12-31), click [Save]
- **Expected**: Transaction saved with future date

**TC-5.1.4**: All members see transaction
- **Precondition**: Member1 recorded income
- **Steps**: Log in as member2, view transaction list
- **Expected**: Income visible with member1 as creator

---

### US-5.2: Record Expense Transaction

**TC-5.2.1**: Member records expense
- **Steps**: Click [+ Transaction], type Expense, amount 125.50, category "Groceries", account "Checking", click [Save]
- **Expected**: Transaction created; account balance -= 125.50

**TC-5.2.2**: Overdraft allowed
- **Precondition**: Account balance = 1000
- **Steps**: Record expense 2000, click [Save]
- **Expected**: Balance = -1000 (overdraft permitted)

**TC-5.2.3**: Cash Withdrawal is standard category
- **Steps**: Select category "Cash Withdrawal", record 500
- **Expected**: Transaction recorded as expense

---

### US-5.3: Record Investment (SHOULD)

**TC-5.3.1**: Member records investment
- **Steps**: Type Investment, amount 10000, category "Stocks", account "Investment", click [Save]
- **Expected**: Transaction recorded in investment account

---

### US-5.4: Edit Transaction

**TC-5.4.1**: Member edits transaction
- **Precondition**: Transaction created
- **Steps**: Click [Edit], change amount 5000 → 5500, click [Save]
- **Expected**: Amount updated; balance recalculated; edit recorded

**TC-5.4.2**: Member can edit another member's transaction
- **Precondition**: Member1 created transaction; member2 logged in
- **Steps**: Click [Edit], change category, click [Save]
- **Expected**: Updated; member2 recorded as editor

**TC-5.4.3**: Edit history shows editor, timestamp, change summary
- **Precondition**: Transaction edited
- **Steps**: Click [View Edit History]
- **Expected**: Shows editor name, timestamp, change description

**TC-5.4.4**: Before/after snapshots visible (expandable)
- **Expected**: Full before/after data visible when expanded

**TC-5.4.5**: Account balance recalculated on edit
- **Expected**: Balance reflects new amount

---

### US-5.5: Disable/Restore Transaction (SHOULD)

**TC-5.5.1**: Member disables transaction
- **Steps**: Click [Disable], confirm "Hide from reports?"
- **Expected**: Transaction marked disabled; grayed out

**TC-5.5.2**: Disabled transactions excluded from P&L
- **Precondition**: Transaction disabled
- **Steps**: View dashboard totals
- **Expected**: Disabled transaction not in totals

**TC-5.5.3**: Member re-enables transaction
- **Steps**: Click [Enable]
- **Expected**: Transaction re-enabled; counted in reports

**TC-5.5.4**: Owner hard-deletes (irreversible)
- **Precondition**: Owner viewing transaction
- **Steps**: Click [Delete Permanently], confirm
- **Expected**: Transaction permanently deleted; cannot recover

**TC-5.5.5**: Member cannot hard-delete
- **Expected**: [Delete Permanently] button not visible

---

## Story Group 6: Dashboard & Reporting

### US-6.1: View Dashboard Summary

**TC-6.1.1**: Dashboard shows total income
- **Expected**: "Total Income" card shows correct sum

**TC-6.1.2**: Dashboard shows total expenses
- **Expected**: "Total Expenses" card shows correct sum

**TC-6.1.3**: Dashboard shows net savings
- **Expected**: "Net Savings" = Income - Expenses

**TC-6.1.4**: Dashboard shows account balances
- **Expected**: Accounts section lists all with balances

**TC-6.1.5**: Dashboard shows recent transactions
- **Expected**: Last 5–10 transactions visible

**TC-6.1.6**: Dashboard loads < 2 seconds
- **Expected**: Load time < 2000 ms

**TC-6.1.7**: Dashboard updates in real-time (optional)
- **Expected**: New transactions appear without refresh

---

### US-6.2: View Expense Breakdown by Category

**TC-6.2.1**: Chart shows expense categories
- **Expected**: Pie/bar chart shows categories: Groceries ($500), Utilities ($200), etc.

**TC-6.2.2**: Period selector available
- **Expected**: Options: "This Month", "This Year", "Last 3 Months", "Custom Range"

**TC-6.2.3**: Sortable by amount (optional)
- **Expected**: Categories sorted highest to lowest spending

---

### US-6.3: View Trends (SHOULD)

**TC-6.3.1**: Trend chart shows monthly income/expense
- **Expected**: Line chart with Income and Expense by month

---

### US-6.4: Export Report (SHOULD)

**TC-6.4.1**: Owner exports as CSV
- **Steps**: Click [Export], select date range, click [Download]
- **Expected**: CSV file with all transactions and categories

---

## Story Group 7: Security & Data

### US-7.1: Logout

**TC-7.1.1**: User clicks Logout
- **Steps**: Click [Logout]
- **Expected**: Redirected to login page

**TC-7.1.2**: Session cookie/token invalidated
- **Expected**: Session cookie deleted or expired

**TC-7.1.3**: Cannot access authenticated pages after logout
- **Steps**: Try to navigate to dashboard via URL
- **Expected**: Redirected to login

**TC-7.1.4**: Cannot reuse old session
- **Expected**: Old session cookie/token rejected

---

### US-7.2: Session Timeout (COULD — v1.1)

**TC-7.2.1**: Auto-logout after 30 min inactivity
- **Expected**: Redirected to login after timeout (deferred to v1.1)

---

## Happy Path Integration Test

**TC-Cross-1**: Full workflow — Login → Create Family → Add Member → Record Transactions → View Dashboard

1. Superadmin logs in
2. Creates family via owner invitation
3. Owner accepts invitation, sets password
4. Owner creates family "Test Family"
5. Owner invites member1@example.com
6. Member1 accepts, joins family
7. Member1 creates account "Checking" with $5000
8. Member1 records income $8000 (salary)
9. Member1 records expense $500 (groceries)
10. Owner records expense $200 (utilities)
11. Both view dashboard: income $8000, expense $700, balance $5000 + $8000 - $700 = $12,300
12. View expense breakdown by category
13. Both logout
14. Both log back in; family selector shows "Test Family"

**Expected**: All steps succeed; no errors; dashboard reflects correct aggregates

---

## Summary

- **MUST stories**: 14 (28–40 test cases)
- **SHOULD stories**: 9 (9–18 test cases)
- **Total**: ~60 test cases
- **Integration**: 1 full happy-path flow (TC-Cross-1)
- **Execution**: Phase 5 (TEST_AND_FIX)

For test execution results and verdict, see `reports/TEST_REPORT.md`.
