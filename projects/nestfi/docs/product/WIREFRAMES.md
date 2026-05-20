# NestFi — Wireframes & Screen Layout

## Overview

This document describes the layout and component structure for key screens. Each wireframe follows a consistent responsive grid system (max-width: 1200px) and uses standard UI components (buttons, forms, tables, charts).

---

## W1: Login Screen

### Layout
```
┌─────────────────────────────────────────┐
│                                         │
│           NestFi Logo                   │
│     (centered, hero section)            │
│                                         │
│     [Email Input]                       │
│     [Password Input]                    │
│     [Forgot Password?] (link)           │
│     [Login Button] (CTA, full width)    │
│                                         │
│     Contact support (footer link)       │
│                                         │
└─────────────────────────────────────────┘
```

**Responsive**: Centered card on desktop; full-width on mobile.  
**Components**:
- Email input with validation
- Password input with show/hide toggle
- Submit button (disabled until both fields filled)
- Error messages displayed above form
- "Forgot Password?" link routes to W1b (Password Reset Request)

---

## W1b: Password Reset - Email Request

### Layout
```
┌─────────────────────────────────────────┐
│                                         │
│   Reset Your Password                   │
│                                         │
│   Enter your email and we'll send      │
│   a reset link (valid for 1 hour)      │
│                                         │
│   [Email Input]                         │
│                                         │
│   [Send Reset Link] (CTA)               │
│   [Back to Login] (link)                │
│                                         │
└─────────────────────────────────────────┘
```

**Components**:
- Email input with validation
- Send button
- Back to login link

---

## W1c: Password Reset - Set New Password

### Layout
```
┌─────────────────────────────────────────┐
│                                         │
│   Set New Password                      │
│                                         │
│   [New Password Input]                  │
│   [Confirm Password Input]              │
│   Password requirements (optional text) │
│                                         │
│   [Set Password] (CTA)                  │
│                                         │
│   Success confirmation shows:           │
│   "Password reset successfully."         │
│   [Return to Login]                     │
│                                         │
└─────────────────────────────────────────┘
```

**Components**:
- Password input with show/hide
- Confirm password input
- Validation feedback (passwords match, strength)
- Submit button

---

## W2: Family Selection Screen

### Layout (multi-family)
```
┌─────────────────────────────────────────┐
│ ← Back  |  Select Your Family            │
├─────────────────────────────────────────┤
│                                         │
│  [ Family Card 1 ]  [ Family Card 2 ]   │
│  ┌──────────┐       ┌──────────┐        │
│  │  Pham    │       │  Smith   │        │
│  │ Family   │       │ Family   │        │
│  │          │       │          │        │
│  │ (3 mem.) │       │ (2 mem.) │        │
│  │          │       │          │        │
│  │ [Select] │       │ [Select] │        │
│  └──────────┘       └──────────┘        │
│                                         │
│  ☑ Remember selection                   │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Components**:
- Family cards showing: family name, member count, selection button
- Checkbox to remember selection (optional)
- Clear visual indication of selected family

---

## W3: Dashboard - Overview

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ NestFi  |  ☰ Menu  |  📊 Dashboard  |  👤 Profile  | ⋮   │
│                                                           │
│ Family: Pham Family ▼                                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─ This Month ──────────────┬──────────┬──────────┐     │
│  │                           │          │          │     │
│  │ Total Income: $5,000      │ Total    │ Net      │     │
│  │ Total Expenses: $3,200    │ Savings: │ Balance: │     │
│  │ Net Balance: $1,800       │ $1,200   │ $3,000   │     │
│  │                           │          │          │     │
│  └───────────────────────────┴──────────┴──────────┘     │
│                                                           │
│  ┌─ Quick Stats ──────────────────────────────────────┐   │
│  │                                                     │   │
│  │ 📊 Top Expense: Groceries ($800)                   │   │
│  │ 💰 Top Income: Salary ($4,500)                     │   │
│  │ 📈 Saving Rate: 36%                                │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─ Recent Transactions ──────────────────────────────┐   │
│  │                                                     │   │
│  │ May 16  |  Salary            | Income   | $4,500   │   │
│  │ May 15  |  Groceries         | Expense  | -$120    │   │
│  │ May 14  |  Netflix Subscribe | Expense  | -$15     │   │
│  │ May 13  |  Apple Stock       | Invest   | -$500    │   │
│  │ May 12  |  Utilities         | Expense  | -$200    │   │
│  │                                                     │   │
│  │ [View All Transactions →]                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Components**:
- Header with family selector dropdown
- Summary cards (Income, Expenses, Net, Savings) with clear typography
- Quick stats row (badges or mini cards)
- Recent transactions table (scrollable on mobile)
- CTA to view full transaction list

---

## W4: Transactions List

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ NestFi  |  ☰ Menu  |  💳 Transactions  |  👤 Profile      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  [+ Add Transaction]                    [Filter ▼] [Sort ▼]│
│                                                           │
│  ┌─ Filters ─────────────────────────────────────────┐   │
│  │ Date Range: [Start] to [End]                      │   │
│  │ Type: [All ▼]  Category: [All ▼]                  │   │
│  │ [Apply Filters]  [Reset]                          │   │
│  └───────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─ Transactions ────────────────────────────────────┐   │
│  │ Date      | Description    | Type     | Category | $ │   │
│  ├───────────┼────────────────┼──────────┼──────────┼───┤   │
│  │ May 16    | Salary         | Income   | Salary   | +  │   │
│  │           |                |          |          | 4.5K│   │
│  │ May 15    | Groceries      | Expense  | Food     | -  │   │
│  │           |                |          |          | 120 │   │
│  │ May 14    | Netflix        | Expense  | Entert.  | -15 │   │
│  │ [⋮ More] [Edit] [Delete]                         │   │
│  │ [⋮ More] [Edit] [Delete]                         │   │
│  │                                                     │   │
│  │ Page 1 of 15  [< Prev] [1] [2] [3] ... [Next >]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Components**:
- Filter panel (collapsible on mobile)
- Table with columns: Date, Description, Type, Category, Amount
- Row actions: Edit, Delete
- Pagination controls
- Responsive: Collapsible columns on mobile

---

## W5: Add/Edit Transaction Modal

### Layout
```
┌─ Add Transaction ──────────────────────────┐
│                                             │
│  ✕ (close)                                  │
│                                             │
│  Transaction Type: ◉ Income ○ Expense      │
│                    ○ Investment ○ Withdraw  │
│                                             │
│  Date: [May 16, 2024]                      │
│                                             │
│  Category: [Salary ▼]                      │
│  (auto-filtered by type)                   │
│                                             │
│  Amount: [$] [input] (required)            │
│                                             │
│  Bank Account: [Primary Checking ▼]        │
│                                             │
│  Description: [text input, optional]       │
│               (e.g., "May salary payment")  │
│                                             │
│  [Cancel]  [Save Transaction] (CTA)        │
│                                             │
└─────────────────────────────────────────────┘
```

**Components**:
- Radio buttons for transaction type
- Date picker with calendar
- Select dropdown for category (dynamic based on type)
- Currency input with validation
- Optional description field
- Action buttons: Cancel, Save

---

## W5b: Transaction Detail & Edit History

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Transactions                                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Transaction Details                                       │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Description: Weekly groceries at Whole Foods        │   │
│ │ Amount: $120 | Category: Groceries                  │   │
│ │ Date: May 16, 2026 | Account: Checking              │   │
│ │ Created by: Alice Smith | May 16, 2:00 PM          │   │
│ │                                                     │   │
│ │ [Edit] [Disable Transaction] [⋮ More]              │   │
│ │ (For Owner: [Delete Permanently] button visible)    │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                           │
│ Edit History ⏷                                            │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Edit by Bob Smith - May 16, 2:30 PM                │   │
│ │ Changed amount from $100 to $120                    │   │
│ │ [Show Before/After]                                │   │
│ │                                                     │   │
│ │ Created by Alice Smith - May 16, 2:00 PM           │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Components**:
- Transaction details (read-only display)
- Edit button (opens edit modal)
- Disable button (soft-delete; text: "Disable" or "Enable" if already disabled)
- Delete button (hard-delete; owner only; red, destructive styling)
- Collapsible Edit History section
- Each edit shows editor, timestamp, and change summary

**Button Styling**:
- [Edit]: Primary button (blue)
- [Disable]: Secondary button (gray)
- [Delete Permanently]: Destructive button (red) - owner only, hidden from non-owners

---

## W6: Analytics - Expense Breakdown

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ NestFi  |  ☰ Menu  |  📈 Analytics  |  👤 Profile         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Time Period: [This Month ▼]  [Custom Range]            │
│                                                           │
│  ┌─ Expense Breakdown ──────────────────────────────┐   │
│  │                                                     │   │
│  │     ┌──────────────────────┐                       │   │
│  │     │         PIE CHART    │                       │   │
│  │     │    Groceries: 35%    │  📊 Table:            │   │
│  │     │    Utilities: 20%    │                       │   │
│  │     │    Entert.: 15%      │  Groceries    $1,120  │   │
│  │     │    Other: 30%        │  Utilities      $640  │   │
│  │     │                      │  Entert.        $480  │   │
│  │     └──────────────────────┘  Other         $960   │   │
│  │                                                     │   │
│  │                                 Total: $3,200      │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
│  [Expense] [Income] [Savings Trend] [Investments]        │
│  (tab navigation)                                         │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Components**:
- Time period selector
- Pie/Doughnut chart visualization
- Accompanying data table
- Tab navigation to switch between views
- Color coding for categories

---

## W7: Family Management (Owner Only)

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ NestFi  |  ☰ Menu  |  ⚙️ Settings  |  👤 Profile          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  [Settings] [Family] [Categories] [Bank Accounts]        │
│                      ← Tab Navigation                     │
│                                                           │
│  ┌─ Family Members ──────────────────────────────────┐   │
│  │                                                     │   │
│  │ [+ Add Member]                                      │   │
│  │                                                     │   │
│  │ ACTIVE MEMBERS                                      │   │
│  │ Name           | Email           | Role    | Action │   │
│  ├────────────────┼──────────────────┼─────────┼────────┤   │
│  │ You            | owner@mail.com   | Owner   | (-)    │   │
│  │ Spouse         | spouse@mail.com  | Member  | [Edit] │   │
│  │ Son            | son@mail.com     | Viewer  | [Edit] │   │
│  │                                                     │   │
│  │ DISABLED MEMBERS                                    │   │
│  │ Aunt           | aunt@mail.com    | Member  | [Edit] │   │
│  │ (access revoked)                                   │   │
│  │                                                     │   │
│  │ PENDING INVITATIONS                                 │   │
│  │ Email          | Role   | Expires | Actions        │   │
│  ├────────────────┼────────┼─────────┼────────────────┤   │
│  │ daughter@mail..| Member | May 23  | [Resnd][Revke] │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Components**:
- Tab navigation (Settings, Family, Categories, Bank Accounts)
- Family members grouped by status (Active, Disabled, Pending)
- Add member button (modal form)
- [Edit] for active/disabled members (opens W9b modal)
- [Resend] / [Revoke] for pending invitations
- Status badges showing disabled status

**Color Coding**:
- Active members: Normal styling
- Disabled members: Grayed out or with "disabled" badge
- Pending invitations: With expiration date and countdown

---

## W8: Settings - Categories

### Layout
```
┌──────────────────────────────────────────────────────────┐
│ NestFi  |  ☰ Menu  |  ⚙️ Settings  |  👤 Profile          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  [Settings] [Family] [Categories] [Bank Accounts]        │
│                                                           │
│  ┌─ Income Categories ───────────────────────────────┐   │
│  │                                                     │   │
│  │ Salary (3 trans.)      [✎ Edit]  [✕ Delete]       │   │
│  │ Bonus (1 trans.)       [✎ Edit]  [✕ Delete]       │   │
│  │ Other Income (0)       [✎ Edit]  [✕ Delete]       │   │
│  │ [+ Add Income Category]                            │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─ Expense Categories ──────────────────────────────┐   │
│  │                                                     │   │
│  │ Groceries (12 trans.)  [✎ Edit]  [✕ Delete]       │   │
│  │ Utilities (4 trans.)   [✎ Edit]  [✕ Delete]       │   │
│  │ Entertainment (8)      [✎ Edit]  [✕ Delete]       │   │
│  │ [+ Add Expense Category]                           │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Components**:
- Category list grouped by type (Income/Expense/Investment)
- Each category shows usage count
- Inline edit/delete actions
- Add new category button
- Confirmation before deletion

---

## W9: Add Member Modal

### Layout
```
┌─ Invite Family Member ─────────────────────────────┐
│                                                     │
│  ✕ (close)                                          │
│                                                     │
│  Email: [text input, required]                     │
│  (Must be valid email format)                      │
│                                                     │
│  Name (optional): [text input]                     │
│                                                     │
│  Role: ◉ Member  ○ Viewer                          │
│  (Members can add/edit transactions;               │
│   Viewers can only view)                           │
│                                                     │
│                                                     │
│  [Cancel]  [Send Invitation] (CTA, blue)           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Components**:
- Email input with validation
- Name field (optional)
- Role radio buttons with explanatory text
- Cancel/Submit buttons

---

## W9b: Edit Member Modal

### Layout
```
┌─ Edit Family Member ───────────────────────────────┐
│                                                     │
│  ✕ (close)                                          │
│                                                     │
│  Member: Alice Smith (alice@example.com)           │
│  Status: Active  (or "Disabled" if disabled)       │
│                                                     │
│  Change Role: ◉ Member  ○ Viewer                   │
│                                                     │
│  [Save Changes] (blue button)                      │
│                                                     │
│  ─────────────────────────────────────────         │
│                                                     │
│  Member Access:                                     │
│  [Disable Member] (gray button)                    │
│  (They will lose access immediately)               │
│                                                     │
│  OR (if already disabled):                          │
│  [Re-enable Member] (blue button)                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Components**:
- Member name and email (read-only)
- Current status (Active/Disabled)
- Role selector (radio buttons)
- Save changes button
- Disable/Re-enable button (separate section, red for disable)
- Confirmation dialogs for enable/disable actions

**Conditional Display**:
- If member is active: Show [Disable Member] button
- If member is disabled: Show [Re-enable Member] button
- Owner cannot disable themselves

---

## Layout & Grid System

### Desktop (1200px+)
- Main content: max-width 1200px, centered
- Sidebar navigation: ~250px fixed left OR top navbar
- Tables: full-width columns visible
- Charts: side-by-side layout

### Tablet (768px - 1199px)
- Sidebar collapses to top navbar with hamburger menu
- Tables: horizontal scrolling for dense data
- Charts: responsive layout, single column on small tablets

### Mobile (< 768px)
- Full-width layout
- Hamburger menu navigation
- Table columns collapse or switch to card view
- Modals: full-screen
- Charts: stacked vertically

---

## Color & Typography Guidelines

See DESIGN_NOTES.md for detailed color palette, typography scale, and component styling.

---

## Interaction Patterns

### Confirmation Dialogs
- Red CTA for destructive actions (delete)
- Two options clearly presented
- Escape key closes without action

### Forms
- Inline validation as user types
- Error messages in red below field
- Submit button disabled until valid
- Success toast after submission

### Tables/Lists
- Hover: subtle background color change
- Selection: checkbox on left
- Pagination: numbered buttons + prev/next
- Sorting: click column header; arrow indicator

### Dropdowns
- Click to open; click away or Esc to close
- Keyboard navigation (arrow keys, Enter)
- Search/filter if list > 10 items

---

## Accessibility Notes

- All interactive elements keyboard-accessible (Tab, Enter, Esc)
- Color not sole indicator of state (+ text, icons, patterns)
- Form labels associated with inputs
- ARIA attributes for modals, dropdowns, alerts
- Focus visible on interactive elements
- Sufficient color contrast (WCAG AA minimum)

See DESIGN_NOTES.md for full accessibility checklist.
