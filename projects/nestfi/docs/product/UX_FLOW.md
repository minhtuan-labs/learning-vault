# UX Flow — NestFi Family Financial Management

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** UX  

---

## Flow Overview

NestFi has four main user journeys:
1. **Superadmin Journey** — manage families and invite initial owners
2. **Owner Onboarding Journey** — accept invitation, set account, add family members
3. **Family Member Journey** — log transactions, view dashboard, manage family
4. **Multi-family Switching** — navigate between multiple families

---

## Flow 1: Superadmin Journey

### Goal
Superadmin creates a new family and invites its initial owner via email.

### Steps

```
START
  ↓
[Superadmin Login] → Verify credentials (superadmin/admin123)
  ↓
[Superadmin Dashboard] → List all families, invite owners, manage accounts
  ↓
[Create Family Form]
  • Enter family name
  • Enter owner email
  • (Optional) family description/photo
  ↓
[System sends invitation email]
  • Email contains unique acceptance link + token
  • Link expires in 7 days (standard invitation lifecycle)
  ↓
[Superadmin sees confirmation] → "Invitation sent to [email]"
  ↓
END
```

### Key Interactions
- Superadmin can see status of each family (active, pending owner, etc.)
- Superadmin can resend or revoke invitations
- Superadmin can view all family members and their roles

---

## Flow 2: Owner Onboarding Journey

### Goal
Owner accepts invitation email, creates account, verifies identity, and becomes family admin.

### Steps

```
START (Owner receives email)
  ↓
[Email Invitation] → Click "Accept Invitation" link
  ↓
[Verify Email Page]
  • Show email address from token
  • Ask: "Is this your email?"
  • Option: Enter different email (triggers new invite)
  ↓
[Set Account Details]
  • First name, last name
  • Password (with strength indicator)
  • Phone (optional)
  ↓
[Confirm & Create Account] → Account created, owner assigned to family
  ↓
[Onboarding Setup Screen]
  • Show family name
  • Quick setup: "Invite family members" CTA
  • Option: "Skip for now"
  ↓
[Owner Dashboard] → Ready to manage family
  ↓
END
```

### Key Interactions
- Email verification confirms identity before account creation
- Password requirements enforced (8+ chars, mixed case, number)
- Owner can immediately invite family members or defer setup
- Clear success message on account creation

---

## Flow 3: Family Member Onboarding & Invitation

### Goal
Owner invites family members; members accept and join the family.

### Steps

```
START (Owner in Family Settings)
  ↓
[Family Settings → Members Tab]
  • View current family members
  • "Invite Member" button
  ↓
[Invite Member Form]
  • Enter member email
  • Select role (view-only member vs editor member)
  • (Optional) personal message
  ↓
[System sends invitation email]
  • Similar to owner invitation but for existing users
  • If user exists: auto-login option
  • If new user: ask to create account
  ↓
[Member receives email]
  ↓
[IF existing user:] 
  → [Accept Invitation] → Add to family → [Family Dashboard]
  ↓
[IF new user:]
  → [Set Account Details] → [Family Dashboard]
  ↓
END
```

### Key Interactions
- Role selection at invitation (view-only restricts transaction editing)
- Batch invitation for families >2 people
- Cancel/revoke pending invitations from settings

---

## Flow 4: Core Family Usage — Transaction Logging & Dashboard

### Goal
Family members log transactions and view household financial overview.

### Steps

```
START (Member logs in)
  ↓
[Family Selector] 
  • If multiple families: choose which one to access
  • If one family: skip to dashboard
  ↓
[Family Dashboard]
  • View summary: Total Income, Total Expenses, Net Savings (month/year toggles)
  • View category breakdown (pie chart or bar chart)
  • View monthly trends (last 6-12 months)
  • Recent transaction list
  • "Log Transaction" prominent CTA button
  ↓
[Log Transaction Form]
  • Type: Income / Expense / Cash Withdrawal
  • Category: Dropdown (pre-populated from family categories)
  • Amount: Numeric input
  • Date: Date picker (defaults to today)
  • Notes: Optional text field
  • Member: Auto-populated (current user), read-only
  ↓
[Submit] → Transaction saved, analytics update in real-time
  ↓
[Dashboard refreshes] → New transaction appears in ledger and charts
  ↓
END
```

### Key Interactions
- Transaction form is lightweight (~5 fields)
- Categories are family-configured; default set provided on setup
- Real-time updates: other family members see new transactions immediately
- Undo/Edit: member can edit their own transactions within 24 hours (or any edit reverts to view-only after owner decision)

---

## Flow 5: Settings & Category Management

### Goal
Owner configures family financial categories and settings.

### Steps

```
START (Owner in Family Settings)
  ↓
[Settings Navigation]
  • General (family name, logo, members list)
  • Categories (income, expense, investment)
  • Bank Accounts (optional for v1)
  • Permissions & Roles
  ↓
[Manage Income Categories]
  • View all active categories (pre-populated: Salary, Freelance, Bonus, Other)
  • Add new category: name, color, icon
  • Edit/deactivate existing (archive instead of delete)
  • Set default for cash/transfers
  ↓
[Manage Expense Categories]
  • View all active categories (pre-populated: Groceries, Utilities, Entertainment, Transport, Other)
  • Add new category: name, color, icon
  • Edit/deactivate existing
  • "Cash Withdrawal" is a special system category (always visible)
  ↓
[Manage Investment Categories]
  • View: Stock Portfolio, Crypto, Retirement, Other
  • Add/edit as needed
  • Mark active/inactive
  ↓
[Save] → Categories synced across family, all members see them immediately
  ↓
END
```

### Key Interactions
- Categories have color + icon for quick visual identification
- Default categories provided; full customization available
- Archiving categories keeps historical transactions tagged correctly
- Changes visible to all members instantly

---

## Flow 6: Multi-Family Navigation

### Goal
User with multiple family accounts switches between families without re-logging.

### Steps

```
START (User logged into Family A)
  ↓
[Top Navigation → Family Selector]
  • Show current family name + avatar
  • Dropdown: list all families user belongs to
  ↓
[Select Family B]
  ↓
[Dashboard switches to Family B]
  • Transactions, categories, members, settings all change context
  • No re-login required
  ↓
[User works in Family B]
  ↓
[Can switch back to Family A] → Same instant switch
  ↓
END
```

### Key Interactions
- Family switcher is persistent in header/navigation
- Clear visual indicator of current family (name + color)
- No page reload required; smooth context switch
- Permissions reset based on role in selected family

---

## Flow 7: Transaction History & Search

### Goal
Member views transaction history, filters, and searches for specific transactions.

### Steps

```
START (Member clicks "Transaction History" or similar)
  ↓
[Transaction Ledger View]
  • List of all transactions (newest first)
  • Show: date, member, category, amount, notes
  • Filters: date range, category, member, type (income/expense)
  • Search: text search on notes
  ↓
[Apply Filters]
  • Select date range (e.g., "Last 30 days")
  • Select category from dropdown
  • Select member from dropdown
  ↓
[Results refresh] → Ledger filtered, summary stats update
  ↓
[Click transaction]
  ↓
[Transaction Detail] → View full details
  • If own transaction: Edit / Delete options
  • If other member's transaction: View-only
  ↓
END
```

### Key Interactions
- Default view: current month
- Filter state persists during session
- Export to CSV available (nice-to-have v2)
- Pagination: show 20-50 per page

---

## Key UX Principles Applied

1. **Simplicity:** Minimal steps to log transactions (5 fields max)
2. **Transparency:** Real-time updates; all members see consistent data
3. **Role clarity:** Superadmin, Owner, Member roles have distinct, enforced capabilities
4. **Visual hierarchy:** Primary CTAs (Log Transaction, Invite Member) prominent
5. **Context switching:** Multi-family navigation seamless and quick
6. **Safety:** Confirmation for destructive actions (delete transaction, remove member)

---

## Accessibility & Device Considerations

- **Keyboard navigation:** All forms and modals fully accessible via Tab/Enter
- **Screen reader:** Labels, ARIA attributes for charts and interactive elements
- **Mobile responsive:** Touch-friendly buttons (48px min tap target), readable on mobile (v2 refinement)
- **Color contrast:** WCAG AA minimum for all text and interactive elements
- **Error handling:** Clear, plain-language error messages (not red-only)

---

## Open Design Questions

1. **Chart type preference:** Pie chart (easy visual ratio) vs Bar chart (easier to read precise values) for category breakdown?
   - Current: Recommend both — pie in dashboard, bar in reports
   
2. **Cash withdrawal UX:** Should cash withdrawal have a separate form or be a category in expense form?
   - Current: Category in expense form, marked as system-level (can't delete)
   
3. **Real-time updates polling:** Should dashboard auto-refresh every N seconds, or only on action?
   - Current: Recommend auto-refresh every 10s (can be configured per family)

---
