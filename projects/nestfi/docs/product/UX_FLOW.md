# NestFi — User Experience Flow

## Overview

NestFi is a family financial management platform supporting multi-user collaboration with role-based access (Superadmin, Family Owner, Family Member). Users authenticate, manage families, track transactions (income/expense/investment), and view analytics.

**Primary flows:**
1. Superadmin setup and family creation
2. Family owner invitation & acceptance
3. Family member management
4. User authentication & family selection
5. Transaction lifecycle (create, read, update, delete)
6. Dashboard & analytics viewing
7. Category management

---

## Flow 1: Password Reset (Forgot Password)

**Actor**: User on login page who forgot password  
**Precondition**: User has an active account but doesn't remember password

```
[Login Page]
  ↓
[Click "Forgot Password?"]
  ↓
[Password Reset - Email Entry Page]
  ├─ Input: Email address
  └─ Action: [Send Reset Link]
  ↓
[Confirmation Page]
  ├─ Show: "If an account with that email exists, a reset link has been sent."
  └─ Show: "Link expires in 1 hour"
  ↓
[User receives email with reset link]
  ↓
[Click Reset Link]
  ↓
[Set New Password Page]
  ├─ Input: New password
  ├─ Input: Confirm password
  └─ Action: [Set Password]
  ↓
[Success Page]
  ├─ Show: "Password reset successfully"
  └─ Action: [Return to Login]
  ↓
[User logs in with new password]
```

**Success criteria**: User can reset password and regain access.  
**Error cases**: Expired link, invalid email, token mismatch.

---

## Flow 2: Initial System Setup (Superadmin)

**Actor**: System administrator on first login  
**Precondition**: System newly deployed with default superadmin account

```
[System Ready]
  ↓
[Superadmin Login] → username: superadmin, password: admin123
  ↓
[Dashboard/Home] (Superadmin View)
  ├─ Option: Create New Family
  ├─ Option: View Families
  └─ Option: Change Password
```

**Success criteria**: Superadmin logged in and can access family creation panel.

---

## Flow 3: Create Family & Invite Owner

**Actor**: Superadmin  
**Precondition**: Logged in as superadmin

```
[Superadmin Dashboard]
  ↓
[Click "Create New Family"]
  ↓
[Family Creation Form]
  ├─ Input: Family Name (e.g., "Pham Family")
  ├─ Input: Owner Email (e.g., owner@example.com)
  └─ Action: [Submit]
  ↓
[Email Sent Confirmation]
  ├─ Show: "Invitation sent to owner@example.com"
  └─ Family Status: "Pending Owner Acceptance"
  ↓
[Return to Dashboard]
```

**Success criteria**: Email invitation sent; family appears in list with status "Pending Acceptance".

---

## Flow 4: Owner Invitation Acceptance

**Actor**: Family owner (email recipient)  
**Precondition**: Superadmin has invited owner via email

```
[Email Received]
  ├─ Subject: "You've been invited to manage family finances on NestFi"
  └─ Body: Invitation link (with token/code)
  ↓
[Click Invitation Link]
  ↓
[Acceptance Page]
  ├─ Display: Family name, invitation details
  ├─ Action: [Accept]
  └─ Action: [Decline]
  ↓
  IF Accept:
    ↓
    [Set Password] → Create unique password
    ↓
    [Email Confirmation] → "You are now family owner"
    ↓
    [Redirect to Owner Dashboard]
  ELSE:
    ↓
    [Decline Confirmation] → Email sent to superadmin
```

**Success criteria**: Owner password set; owner can log in; status changes to "Active".

---

## Flow 5: Add Family Members (by Owner)

**Actor**: Family owner  
**Precondition**: Owner accepted invitation and logged in

```
[Owner Dashboard]
  ↓
[Click "Manage Family Members"]
  ↓
[Family Members List]
  ├─ Current Members: [Owner]
  ├─ Action: [Add New Member]
  └─ Action: [Edit/Remove Member]
  ↓
[Add Member Modal]
  ├─ Input: Member Email
  ├─ Input: Member Name (optional)
  └─ Select: Role (Member / Viewer)
  ↓
[Invite Confirmation]
  ├─ Send: Invitation email to new member
  └─ Show: "Invitation sent; awaiting acceptance"
  ↓
[New Member Receives Email]
  ├─ Accept Invitation
  ├─ Set Password
  └─ Joins Family
```

**Success criteria**: New member invited and can accept; appears in family members list.

---

## Flow 6: User Login & Family Selection

**Actor**: Any authenticated user (owner or member)  
**Precondition**: User has accepted invitation and set password

```
[Login Page]
  ├─ Input: Email
  ├─ Input: Password
  └─ Action: [Login]
  ↓
[Verify Credentials]
  ↓
  IF User belongs to 1 family:
    ↓
    [Redirect to Family Dashboard]
  ELSE (Multiple families):
    ↓
    [Family Selection Screen]
    ├─ Display: List of families user belongs to
    ├─ Action: [Select Family]
    └─ [Remember last selection? Toggle]
    ↓
    [Redirect to Selected Family Dashboard]
```

**Success criteria**: User authenticated and viewing correct family's data.

---

## Flow 7: Transaction Management

### 6.1 Create Transaction

**Actor**: Family member  
**Precondition**: User logged in and family selected

```
[Dashboard/Transactions Tab]
  ↓
[Click "Add Transaction" / "+ New"]
  ↓
[Transaction Form]
  ├─ Select: Type (Income / Expense / Investment / Cash Withdrawal)
  ├─ Input: Amount
  ├─ Input: Date
  ├─ Select: Category (from available list for type)
  ├─ Input: Description (optional)
  ├─ Select: Bank Account (if relevant)
  └─ Action: [Save]
  ↓
[Transaction Created]
  ├─ Show: Confirmation message + transaction summary
  ├─ Dashboard updates in real-time
  └─ Transaction appears in history
```

**Success criteria**: Transaction saved; visible in list and reflected in dashboard summaries.

### 6.2 View/Filter Transactions

```
[Transactions List]
  ├─ Display: All transactions (paginated)
  ├─ Filter: Date range, Type, Category
  ├─ Sort: Date (newest first by default)
  ├─ Action: [Edit] transaction
  ├─ Action: [Delete] transaction
  └─ Action: [View Details]
```

### 6.3 Update Transaction

```
[Transaction Detail / Edit Modal]
  ├─ Pre-fill: Current data
  ├─ Editable Fields: Amount, Date, Category, Description
  └─ Action: [Update]
```

### 7.4 Disable/Enable Transaction (Soft-Delete)

**Actor**: Any family member  
**Precondition**: User viewing transaction detail or transaction list

```
[Transaction Detail / Row]
  ↓
[Click "Disable" button]
  ↓
[Confirmation]
  ├─ Show: "Hide this transaction from reports? (Can be restored later)"
  └─ Action: [Confirm] / [Cancel]
  ↓
[Transaction Disabled]
  ├─ Visually mark as hidden (strikethrough, grayed out)
  ├─ Show: "Enable" button (for re-enabling)
  └─ Dashboard updates: Transaction no longer counted in P&L
  ↓
[User can click "Enable" to restore]
  ↓
[Transaction Re-enabled]
  ├─ Visible again in all reports
  └─ Dashboard updates: Transaction counted again
```

**Success criteria**: Disabled transactions not shown in reports; can be re-enabled by any member.  
**Note**: All family members can disable/enable. See Flow 7.5 for hard-delete (owner only).

### 7.5 Delete Transaction (Hard-Delete)

**Actor**: Family owner only  
**Precondition**: Owner viewing transaction detail

```
[Transaction Detail - Owner View]
  ↓
[Click "Delete Permanently" button] (red, destructive)
  ↓
[Confirmation Dialog]
  ├─ Show: "Permanently delete this transaction? This cannot be undone."
  ├─ Show: Transaction details for confirmation
  └─ Action: [Delete Permanently] / [Cancel]
  ↓
[Transaction Hard-Deleted]
  ├─ Show: "Transaction permanently deleted"
  ├─ Cannot be recovered
  └─ Dashboard updates: Transaction removed from all history
```

**Success criteria**: Transaction completely removed; not recoverable.  
**Warning**: Owner-only action; permanent action.

### 7.6 View Transaction Edit History

**Actor**: Any family member  
**Precondition**: User viewing transaction detail

```
[Transaction Detail Page]
  ├─ Show: Current transaction data
  ├─ Show: "Edit History" section (collapsed by default)
  └─ Click: [Show Edit History]
  ↓
[Edit History Expanded]
  ├─ Show: List of all edits in reverse chronological order
  ├─ For each edit:
  │  ├─ Editor name (e.g., "Alice Smith")
  │  ├─ Edit timestamp (e.g., "May 16, 2:30 PM")
  │  ├─ Change summary (e.g., "Changed amount from $100 to $150")
  │  └─ Before/after snapshots (expandable)
  └─ Show: Original creation timestamp and creator
```

**Success criteria**: Full audit trail visible; users know who changed what and when.

---

## Flow 8: Manage Family Members (Enable/Disable/Edit)

**Actor**: Family owner  
**Precondition**: Owner logged in and viewing family members list

### 8.1 Disable Family Member

```
[Family Members List]
  ├─ Active members with role badges
  ├─ Pending invitations with [Resend] / [Revoke] buttons
  └─ For each active member: [Edit] button
  ↓
[Click "Edit" on member row]
  ↓
[Member Edit Modal]
  ├─ Show: Member name, email
  ├─ Show: Current role (Member or Viewer)
  ├─ Option 1: [Change Role] (Member ↔ Viewer)
  └─ Option 2: [Disable Member] (destructive, red button)
  ↓
[Click "Disable Member"]
  ↓
[Confirmation Dialog]
  ├─ Show: "Disable member? They will lose access immediately."
  ├─ Show: "Their transactions and edits will remain in the record."
  └─ Action: [Disable Member] / [Cancel]
  ↓
[Member Disabled]
  ├─ Member immediately logged out (session invalidated)
  ├─ Status changed to "disabled" in members list
  ├─ Show: [Re-enable] option
  └─ Member no longer sees family data
```

**Success criteria**: Member loses access; transactions preserved; can be re-enabled.

### 8.2 Re-enable Family Member

```
[Family Members List - showing disabled member]
  ↓
[Click "Edit" on disabled member]
  ↓
[Member Edit Modal]
  ├─ Show: "Status: Disabled"
  ├─ Show: [Re-enable Member] button
  └─ Show: [Resend Invitation] option
  ↓
[Click "Re-enable Member"]
  ↓
[Confirmation]
  ├─ Show: "Re-enable member? They will regain full access."
  └─ Action: [Re-enable] / [Cancel]
  ↓
[Member Re-enabled]
  ├─ Status changed to "active"
  ├─ Member regains access on next login
  └─ All transactions/edits remain intact
```

**Success criteria**: Member can log in again; full access restored.

### 8.3 Manage Pending Invitations

```
[Family Members List]
  ├─ Show: Pending invitations with email and expiration
  ├─ Actions: [Resend Invitation] [Revoke Invitation]
  ↓
[Click "Resend Invitation"]
  ↓
[Confirmation]
  ├─ Show: "Resend invitation to (email)?"
  └─ Action: [Resend] / [Cancel]
  ↓
[Invitation Resent]
  ├─ Show: Confirmation message
  └─ New invitation email sent; previous link invalidated
  ↓
OR [Click "Revoke Invitation"]
  ↓
[Confirmation]
  ├─ Show: "Revoke invitation? They can no longer accept it."
  └─ Action: [Revoke] / [Cancel]
  ↓
[Invitation Revoked]
  ├─ Removed from pending list
  └─ Invitee cannot accept old link
```

**Success criteria**: Invitations can be resent or revoked; user sees status updates.

---

## Flow 10: Category Management

**Actor**: Family owner (admin permissions)  
**Precondition**: Logged in as owner

```
[Settings / Categories Panel]
  ↓
[View Category Lists]
  ├─ Income Categories: Salary, Bonus, Other Income, ...
  ├─ Expense Categories: Groceries, Utilities, Entertainment, ...
  └─ Investment Categories: Stocks, Crypto, Real Estate, ...
  ↓
[Manage Categories]
  ├─ Action: [Add New Category]
  │  └─ Input: Category Name, Type (Income/Expense/Investment)
  ├─ Action: [Edit Category]
  ├─ Action: [Delete Category]
  └─ Show: Category usage (number of transactions)
```

**Success criteria**: Owner can add/edit/delete custom categories; categories available in transaction form.

---

## Flow 11: Dashboard & Analytics

**Actor**: Any family member  
**Precondition**: User logged in

```
[Dashboard - Overview Tab]
  ├─ Time Period: Current month (configurable to YTD, custom range)
  ├─ Summary Cards:
  │  ├─ Total Income (month)
  │  ├─ Total Expenses (month)
  │  ├─ Net Balance (month)
  │  └─ Total Savings / Investment
  ├─ Recent Transactions: Last 5 transactions
  └─ Quick Stats: Most spent category, income sources
  ↓
[Analytics - Detailed View]
  ├─ Tab 1: Expense Breakdown
  │  └─ Pie/Bar chart: Expenses by category
  ├─ Tab 2: Income Breakdown
  │  └─ Pie/Bar chart: Income by source
  ├─ Tab 3: Savings Trend
  │  └─ Line chart: Monthly savings over time
  ├─ Tab 4: Investment Summary
  │  └─ Table: Investment accounts, values, growth
  └─ Filter: Date range selector
```

**Success criteria**: Dashboard loads < 2 seconds; charts update when transactions change.

---

## Flow 12: User Settings & Logout

**Actor**: Any authenticated user

```
[Settings Menu / User Profile]
  ├─ Option: [Change Password]
  ├─ Option: [Edit Profile]
  │  └─ Name, Email (display only)
  ├─ Option: [Notifications] (future)
  ├─ Option: [Leave Family] (if member)
  └─ Option: [Logout]
  ↓
[Logout Confirmation]
  ├─ Clear session
  └─ Redirect to login page
```

---

---

## Role-Based Access & Permissions

### Superadmin (System Administrator)
- Create new families
- Invite family owners
- Reset superadmin password
- No access to family financial data

### Family Owner
- Full access to all family data and features
- Invite/manage family members (assign roles: Member or Viewer)
- Enable/disable family members
- Create, edit, delete (hard-delete) transactions
- Manage categories (create, edit, delete custom categories)
- Manage family settings (name, members, accounts)
- Export reports (stretch goal v1.1)
- CANNOT: Remove themselves if they're the only owner

### Family Member (Editor)
- View all family financial data (accounts, transactions, analytics)
- Create transactions (income, expense, investment)
- Edit any transaction (all members have equal edit rights)
- Disable/enable (soft-delete) transactions (cannot hard-delete)
- View transaction edit history
- CANNOT: Hard-delete transactions
- CANNOT: Manage members or categories
- CANNOT: Edit family settings

### Family Viewer (Read-Only)
- View all family financial data (accounts, transactions, analytics)
- CANNOT: Create or edit transactions
- CANNOT: Disable/enable transactions
- CANNOT: Manage members or categories
- CANNOT: Edit family settings

---

## Key UX Principles

1. **Multi-family support**: Always visible which family is active; easy family switching
2. **Role clarity**: Members see appropriate actions based on role (owner vs. member)
3. **Data isolation**: No family data leaks; strict family-level filtering
4. **Responsive layout**: Desktop-first; readable on tablet/mobile (not optimized for mobile)
5. **Minimal friction**: Quick transaction entry; sensible defaults
6. **Real-time feedback**: Transaction confirmations, summary updates without page reload
7. **Accessibility**: Clear labels, logical tab order, color contrast (WCAG AA target)

---

## Navigation Structure

```
Main Navigation (Top bar or Sidebar):
├─ Dashboard (home icon)
├─ Transactions
│  ├─ All Transactions
│  ├─ Income
│  ├─ Expenses
│  └─ Investments
├─ Analytics (if member) / Reports
├─ Settings (owner only)
│  ├─ Categories
│  ├─ Bank Accounts
│  └─ Family Members
├─ [Family Selector Dropdown]
└─ User Profile / Logout
```

---

## Error Handling

### Invalid Invitation Link
```
[Expired/Invalid Link Page]
├─ Message: "This invitation has expired or is invalid"
└─ Action: [Contact superadmin] or [Request new invitation]
```

### Duplicate Email
```
[User already exists for this email]
├─ Message: "Email already registered. Please log in or reset password"
└─ Action: [Login] / [Forgot Password]
```

### Insufficient Permissions
```
[Access Denied]
├─ Message: "You don't have permission to perform this action"
└─ Action: [Return to Dashboard]
```

---

## Future Enhancements (Out of Scope - MVP)

- Recurring transaction templates
- Receipt attachment / photo scanning
- Budget planning & alerts
- Advanced forecasting
- Mobile-native app
- Auto-categorization with ML
- Bill splitting workflow
- Notifications (email/SMS)
