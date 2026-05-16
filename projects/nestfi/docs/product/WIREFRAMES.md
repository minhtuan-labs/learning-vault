# Wireframes — NestFi Family Financial Management

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** UX  

---

## Wireframe Index

This document describes the key screens and layouts for NestFi. Each section describes layout, components, interactions, and notes for the frontend team.

---

## WF-1: Login Screen

**Purpose:** Authenticate user  
**Accessed by:** All users  
**Triggers:** Session expired or user navigates to /login  

### Layout (Desktop, 1920×1080)

```
┌─────────────────────────────────────────┐
│                                         │
│   ┌─────────────────────────────────┐   │
│   │                                 │   │
│   │     🏠 NestFi                   │   │
│   │                                 │   │
│   │   [Email input field]           │   │
│   │                                 │   │
│   │   [Password input field]        │   │
│   │                                 │   │
│   │   ☐ Remember me                │   │
│   │                                 │   │
│   │   [Sign In Button - Primary]    │   │
│   │                                 │   │
│   │   Forgot password? [Link]       │   │
│   │                                 │   │
│   └─────────────────────────────────┘   │
│                                         │
│   Background: light gradient            │
│   (or family photo area)                │
└─────────────────────────────────────────┘
```

### Components
- **Logo/Brand:** NestFi with icon
- **Email field:** Standard text input, auto-focus
- **Password field:** Masked input, show/hide toggle
- **Remember me checkbox:** Optional
- **Sign In button:** Full width, primary color
- **Forgot password link:** Navigate to password reset flow
- **Error messages:** Inline, below form (red text, icon)

### Interactions
- Enter key submits form
- Real-time email validation (optional)
- Loading state on button during submission
- Error display: "Invalid email or password"

---

## WF-2: Family Selector (Multi-Family)

**Purpose:** Choose which family to access  
**Accessed by:** Users with multiple families  
**Triggers:** Login success with 2+ families  

### Layout

```
┌─────────────────────────────────────────┐
│   NestFi                    [Settings] │
├─────────────────────────────────────────┤
│                                         │
│   Select a Family                       │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │ [Emoji] The Smiths              │   │
│   │ 4 members • Last active 2h ago  │   │
│   └─────────────────────────────────┘   │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │ [Emoji] Johnson Household       │   │
│   │ 2 members • Last active 5d ago  │   │
│   └─────────────────────────────────┘   │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │ [Emoji] Multi-Gen Family        │   │
│   │ 6 members • Last active 1mo ago │   │
│   └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Components
- **Family card:** Shows family name, member count, last active
- **Card emoji/avatar:** Visual identifier for family
- **Click to select:** Card becomes selected/highlighted, navigates to dashboard

### Interactions
- Cards are clickable, navigate directly to family dashboard
- Hover state: subtle shadow/scale
- Profile dropdown: Switch without re-selecting each time (future v1.1)

---

## WF-3: Family Dashboard

**Purpose:** Overview of household finances  
**Accessed by:** All family members  
**Primary action:** Log Transaction  

### Layout (Desktop)

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 The Smiths        [Family Selector ▼] [Settings] [Logout]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [+ Log Transaction]  [Filters ▼]  [Reports]            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────┬────────────────────────┐           │
│  │ Income (This Month)    │ Expenses (This Month)  │           │
│  │ $5,000                 │ $1,800                 │           │
│  └────────────────────────┴────────────────────────┘           │
│                                                                 │
│  ┌────────────────────────┬────────────────────────┐           │
│  │ Savings This Month     │ Savings Rate           │           │
│  │ $3,200                 │ 64%                    │           │
│  └────────────────────────┴────────────────────────┘           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Expenses by Category (This Month)                       │   │
│  │                                                         │   │
│  │  [Pie Chart or Bar Chart]                              │   │
│  │  • Groceries: $600 (33%)                               │   │
│  │  • Utilities: $400 (22%)                               │   │
│  │  • Entertainment: $300 (17%)                           │   │
│  │  • Transport: $250 (14%)                               │   │
│  │  • Other: $250 (14%)                                  │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Monthly Trend (Last 6 Months)                           │   │
│  │                                                         │   │
│  │  [Line Chart: Income vs Expenses]                      │   │
│  │  May: $5000 income, $1800 expense                      │   │
│  │  Apr: $5000 income, $1600 expense                      │   │
│  │  ...                                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Recent Transactions                                     │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ Today, 2:30 PM  | John      | Groceries    | -$45.67  │   │
│  │ Today, 1:15 PM  | Sarah     | Salary       | +$2500   │   │
│  │ Yesterday       | John      | Gas          | -$35.00  │   │
│  │ May 14          | Sarah     | Electricity  | -$120    │   │
│  │                 [View All Transactions]                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

**Header:**
- Family name with logo
- Family selector dropdown
- Settings and logout

**Summary Cards (KPIs):**
- Income this month
- Expenses this month
- Net savings
- Savings rate (%)
- Toggle: Month / Year / Custom date range

**Charts:**
- **Expense breakdown:** Pie or bar chart by category
- **Monthly trend:** Line chart showing income vs expenses over 6-12 months
- Legend, hover tooltips showing exact values

**Recent Transactions:**
- Date, member name, category, amount, notes (truncated)
- Click to expand details or edit
- "View All" link to full ledger

**Primary CTA:**
- Large "+ Log Transaction" button at top (fixed or sticky on mobile)

### Interactions
- Click summary cards to drill down by category
- Hover on charts for tooltips
- Click transaction to view/edit details (if authorized)
- Date range filter updates all charts in real-time
- Refresh icon or auto-refresh every 10s

---

## WF-4: Log Transaction Modal

**Purpose:** Quick transaction entry  
**Accessed by:** Click "+ Log Transaction" button  
**Success state:** Transaction saved, modal closes, dashboard updates  

### Layout

```
┌──────────────────────────────────┐
│  Log Transaction           [×]   │
├──────────────────────────────────┤
│                                  │
│  Type:                           │
│  ○ Income   ○ Expense  ○ Other   │
│                                  │
│  Category:                       │
│  [Dropdown: Groceries ▼]        │
│                                  │
│  Amount:                         │
│  [$ _________ ]  (num only)     │
│                                  │
│  Date:                           │
│  [May 16, 2026 ▼]  (date picker)│
│                                  │
│  Notes: (optional)               │
│  [_________________________]     │
│                                  │
│  Member:                         │
│  John Smith (read-only)          │
│                                  │
│  ┌──────────────────────────────┐│
│  │ [Save]     [Cancel]          ││
│  └──────────────────────────────┘│
│                                  │
└──────────────────────────────────┘
```

### Components
- **Type toggle:** Income / Expense / Cash Withdrawal (radio buttons or pills)
- **Category dropdown:** Populated from family categories (income/expense/investment based on type)
- **Amount field:** Numeric input, can accept decimals, currency symbol optional
- **Date picker:** Calendar widget, defaults to today
- **Notes field:** Optional text, max 200 chars
- **Member field:** Read-only, shows current user
- **Action buttons:** Save (primary), Cancel (secondary)

### Interactions
- Type selection filters category dropdown dynamically
- Amount auto-formats with currency symbol
- Tab key navigates between fields
- Escape key closes modal (with unsaved changes warning if content entered)
- Save button disabled until amount and category filled
- Loading state on Save button during submission
- Success toast: "Transaction saved!" with undo option

### Validation
- Amount: required, positive number
- Category: required
- Date: cannot be in future
- Error messages inline under field

---

## WF-5: Transaction Ledger (Full View)

**Purpose:** Searchable, filterable transaction history  
**Accessed by:** "View All Transactions" link from dashboard or nav  

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 The Smiths              [Family Selector ▼]  [Settings]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Transaction History                                            │
│                                                                 │
│  Filters:                                                       │
│  [Date Range: Last 30 days ▼] [Category: All ▼] [Member: All ▼]│
│  [Search: _________________]  [Apply Filters]                   │
│                                                                 │
│  Results: 24 transactions  [CSV Export]                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Date       Member      Category      Amount     Notes   │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ May 16     John        Groceries     -$45.67    --      │   │
│  │ May 16     Sarah       Salary        +$2500     --      │   │
│  │ May 15     John        Gas           -$35.00    --      │   │
│  │ May 14     Sarah       Electricity   -$120.00   --      │   │
│  │ May 13     John        Dining Out    -$62.45    --      │   │
│  │                                                         │   │
│  │ [Previous Page] 1 2 3 [Next Page]                       │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components
- **Filters row:**
  - Date range dropdown (Last 7 / 30 / 90 days, custom, year-to-date)
  - Category dropdown (all active categories + "All")
  - Member dropdown (all family members + "All")
  - Search field (free-text search on notes)
  - Apply Filters button

- **Results table:**
  - Columns: Date, Member, Category, Amount (color-coded: green for income, red for expense), Notes
  - Sortable by clicking column headers
  - Rows are clickable to expand details
  - Row actions on hover: Edit (if authorized), Delete (if authorized)

- **Pagination:** Show N per page (20/50), prev/next buttons, page indicator

- **Export:** CSV button in top right

### Interactions
- Clicking transaction row expands inline details or opens detail modal
- Filter state persists during session (stored in URL or sessionStorage)
- Clearing filters resets to default view (all transactions, last 30 days)
- Click member name to filter by that member
- Click category name to filter by that category

---

## WF-6: Family Settings - Members Tab

**Purpose:** Manage family members, invitations, roles  
**Accessed by:** [Settings] → Members  
**Permission:** Owner and above only  

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 The Smiths              [Family Selector ▼]  [Settings]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Settings > Members                                             │
│                                                                 │
│  ┌────┬────┬────────┬─────────────┬─────────────┬──────┐       │
│  │Tabs│ Gen│Members│ Categories  │ Bank Accts  │Other │       │
│  └────┴────┴────────┴─────────────┴─────────────┴──────┘       │
│                                                                 │
│  [+ Invite Member]                                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Member          Email             Role        Status   │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │ John Smith      john@...          Owner       Active   │   │
│  │ Sarah Smith     sarah@...         Editor      Active   │   │
│  │ Emily Johnson   emily@...         Viewer      Pending  │   │
│  │ Marcus Brown    marcus@...        Editor      Active   │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Actions on member row (hover):                                 │
│  - Edit role / Change permissions                              │
│  - Remove member (with confirmation)                           │
│  - Resend invitation (if pending)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components
- **Settings navigation tabs:** General, Members, Categories, Bank Accounts, etc.
- **Invite Member button:** Opens invite modal
- **Members table:**
  - Member name
  - Email
  - Role: Owner, Editor, Viewer (can edit own transactions), Viewer-only
  - Status: Active, Pending (invitation not accepted)
  - Row actions: Edit, Remove, Resend invite

### Interactions
- Click "Invite Member" → modal form (email, role, optional message)
- Hover row → action buttons appear
- Click "Remove member" → confirmation modal ("Are you sure? They'll lose access.")
- Click "Edit role" → dropdown to change role
- "Resend invitation" → confirms re-send and shows timestamp

### Validation
- Email format validation
- Prevent inviting same email twice
- Owner role cannot be removed (needs transfer first)

---

## WF-7: Family Settings - Categories Tab

**Purpose:** Configure income, expense, investment categories  
**Accessed by:** [Settings] → Categories  
**Permission:** Owner and above  

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 The Smiths              [Family Selector ▼]  [Settings]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Settings > Categories                                          │
│                                                                 │
│  ┌────┬────────┬──────────┬─────────────┬──────┐               │
│  │Tabs│Expense │ Income   │ Investment  │Other │               │
│  └────┴────────┴──────────┴─────────────┴──────┘               │
│                                                                 │
│  Expense Categories                                             │
│                                                                 │
│  [+ Add Category]                                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │ Category         Icon/Color  Status    Actions   │          │
│  ├──────────────────────────────────────────────────┤          │
│  │ 🛒 Groceries    [■] Green    Active    [Edit][×]│          │
│  │ 💡 Utilities    [■] Blue     Active    [Edit][×]│          │
│  │ 🎬 Entertainment[■] Purple   Active    [Edit][×]│          │
│  │ 🚗 Transport    [■] Orange   Active    [Edit][×]│          │
│  │ 💰 Cash Withdraw[■] Gray     System    ----     │          │
│  │ ❓ Other        [■] Gray     Active    [Edit][×]│          │
│  │ 🍽 Dining Out  [■] Red      Inactive  [Edit][✓]│          │
│  │                                                  │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components
- **Category tabs:** Expense / Income / Investment
- **Add Category button:** Opens add/edit modal
- **Category table:**
  - Category name (with emoji/icon)
  - Color swatch (clickable to change)
  - Status toggle: Active / Inactive (archive)
  - Edit button
  - Delete button (disabled for "Cash Withdrawal" and used categories)

- **Add/Edit Category Modal:**
  - Name field
  - Emoji picker or icon selector
  - Color picker (pre-set palette)
  - Set as default (for auto-categorization)
  - Save / Cancel

### Interactions
- Clicking "Add Category" opens form modal
- Clicking "Edit" on a row opens that category's form
- Toggling status to Inactive doesn't delete history; transactions stay tagged
- Color and icon changes apply immediately across family
- Deleting a category that has transactions shows warning: "X transactions use this category. Archive instead?"

### Validation
- Category name: required, unique per family + type
- Emoji/color: optional but recommended for UX

---

## WF-8: Owner Invitation & Onboarding (Email Flow)

**Purpose:** Superadmin creates family and invites owner  

### Email Template

```
Subject: Join [Family Name] on NestFi

Dear [Owner Email],

You've been invited to manage [Family Name] finances on NestFi.

[Button: Accept Invitation]

Or copy this link: https://nestfi.app/invite/[TOKEN]
This link expires in 7 days.

Questions? Contact support@nestfi.app

—
NestFi Team
```

### Acceptance Flow (Browser)

```
1. User clicks "Accept Invitation" link
2. Page shows: "Setting up your account..."
3. Email verification: "Is this your email? [email@domain]"
   - Options: Yes / No (change email)
4. If Yes:
   - Form: First name, Last name, Password, Phone
5. Confirm & Create Account
6. Success page: "Welcome to [Family Name]! 
   You can now invite other family members."
7. Redirect to dashboard or "Invite Members" setup wizard
```

---

## WF-9: Mobile Layout Considerations (Responsive)

For v1, desktop-first design. Mobile responsiveness (v1 or v1.1):

### Dashboard (Mobile)
- Stack summary cards vertically
- Charts become interactive/swipeable
- Transaction list as compact cards
- Sticky "+ Log Transaction" button at bottom
- Tab navigation or drawer menu for settings

### Modal Forms (Mobile)
- Full-screen modals (not overlay)
- Bottom-aligned action buttons
- Larger touch targets (48px minimum)
- Keyboard-aware layout (account for mobile keyboard)

### Table Views (Mobile)
- Convert to card-based layout
- Hide less important columns (notes become expandable)
- Actions in dropdown menu per row

---

## Component Specifications

### Color Scheme
- **Primary:** Teal / Green (#2E7D6E or similar) — trust, finance, household
- **Secondary:** Neutral gray (#F5F5F5 background, #333 text)
- **Accent:** Warm orange/gold (#FF9500) for CTAs
- **Status colors:**
  - Income: Green (#22C55E)
  - Expense: Red (#EF4444)
  - Neutral: Gray (#6B7280)

### Typography
- **Headlines (H1):** 32px, bold, dark gray
- **Section titles (H2):** 20px, bold, dark gray
- **Body text:** 14px or 16px, regular, dark gray, 1.5 line-height
- **Form labels:** 14px, semi-bold, dark gray
- **Numbers/amounts:** Monospace font (18px, bold) for clarity

### Buttons
- **Primary button:** Teal background, white text, 12px padding, rounded corners (4px)
- **Secondary button:** Gray background, dark text, 12px padding, rounded corners
- **Danger button:** Red background, white text (for delete/remove actions)
- **Disabled state:** 50% opacity, cursor: not-allowed
- **Hover state:** Darkened background, subtle shadow

### Input Fields
- **Border:** 1px gray, rounded 4px
- **Padding:** 10px 12px
- **Focus state:** Blue border, box-shadow: 0 0 0 3px rgba(63, 121, 230, 0.1)
- **Error state:** Red border, error text below field

---

## Navigation Structure

```
NestFi App (Authenticated)
├── Header
│   ├── Logo / Home
│   ├── Family Selector (dropdown)
│   ├── Family Name
│   ├── Profile Menu
│   │   ├── Settings
│   │   ├── Help
│   │   └── Logout
│   └── Search (future)
│
├── Left Sidebar / Nav
│   ├── Dashboard (home)
│   ├── Transactions
│   ├── Analytics (or part of dashboard)
│   ├── Settings
│   │   ├── General (family info)
│   │   ├── Members
│   │   ├── Categories
│   │   ├── Bank Accounts
│   │   └── Permissions
│   └── Help / Feedback
│
└── Main Content Area
    ├── Dashboard (default)
    ├── Transaction Ledger
    ├── Settings Screens
    └── Modals (Log Tx, Invite, etc.)
```

---

## Notes for Frontend Team

1. **Charts:** Use a charting library (e.g., Chart.js, Recharts, or D3) for interactive tooltips and responsiveness.
2. **Real-time updates:** Consider WebSocket or polling for live transaction updates across family members.
3. **Date handling:** All dates in local family timezone (store in UTC, display in user/family timezone).
4. **Responsive breakpoints:**
   - Desktop: 1200px+
   - Tablet: 768px–1199px
   - Mobile: <768px
5. **Accessibility:** Test with screen readers; ensure keyboard navigation works for all flows.
6. **Performance:** Lazy-load transaction history (pagination); debounce filter search.

---
