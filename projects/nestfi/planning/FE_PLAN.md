# Frontend Implementation Plan — NestFi v1

**Phase:** 3_IMPLEMENTATION_PLANNING  
**Status:** DRAFT (pending state management confirmation)  
**Last Updated:** 2026-05-16

---

## 1. Project Overview

NestFi is a family financial management platform requiring:
- Multi-user authentication with role-based access (Superadmin, Owner, Member, Viewer)
- Family-scoped multi-account transaction tracking (Income, Expense, Investment)
- Real-time dashboard with financial analytics
- Family member invitation & management workflows

**Frontend Scope (MVP):**
- Authentication flows (login, registration via email invitation, password reset)
- Family management (creation, member invitation, member management)
- Transaction lifecycle (create, read, update, soft-delete, hard-delete)
- Dashboard & analytics views
- Settings & category management

---

## 2. Tech Stack (Locked)

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Framework** | Next.js 15 (App Router) | Modern meta-framework with SSR/SSG support |
| **Language** | TypeScript | Type safety for financial logic |
| **Styling** | Tailwind CSS + shadcn/ui | Component library with accessibility |
| **Package Manager** | npm or pnpm | Standard Node.js ecosystem |
| **Node Version** | 18 LTS+ | Compatibility with Next.js 15 |

---

## 3. State Management (PENDING USER CONFIRMATION)

> **PENDING — FE needs user input on state management approach.**

**Options considered:**
- **TanStack Query v5** (server state): Best for API data caching, sync, background refetch
- **Zustand** (client state): Lightweight for UI state (modals, filters, temporary UI)
- **Context API** (auth state): Built-in, suitable for global auth context

**Proposed approach (awaiting confirmation):**
- **TanStack Query v5** for all server state (API responses, families, accounts, transactions, categories)
  - Automatic caching, deduplication, background refetch
  - Built-in optimistic updates for transaction edits
  - Reduces component re-renders
- **Zustand** for client state (auth user, selected family, modals, filter panel state)
  - Lightweight, minimal boilerplate
  - Easy to persist selected family to localStorage
- **React Context** for auth session (logged-in user, JWT token if needed)

**Does this approach work for NestFi? Or do you prefer Context API for all state, Redux, or another approach?**

See `.pane_questions/FE_*.md` for decision details.

---

## 4. App Structure (Next.js App Router)

```
frontend/
├── app/
│   ├── layout.tsx               # Root layout with navigation, auth check
│   ├── page.tsx                 # Home/redirect (→ /dashboard if authed, → /login if not)
│   ├── error.tsx                # Global error boundary
│   ├── not-found.tsx            # 404 page
│   │
│   ├── (auth)/
│   │   ├── layout.tsx           # Auth layout (no sidebar, centered form)
│   │   ├── login/
│   │   │   └── page.tsx         # Login page
│   │   ├── register/
│   │   │   └── page.tsx         # Registration (via invitation token)
│   │   ├── forgot-password/
│   │   │   └── page.tsx         # Password reset request
│   │   ├── reset-password/
│   │   │   └── page.tsx         # Password reset confirmation (token-based)
│   │   └── family-selection/
│   │       └── page.tsx         # Family selector (if user has multiple families)
│   │
│   ├── (app)/
│   │   ├── layout.tsx           # Main app layout (sidebar + header)
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Dashboard overview
│   │   ├── transactions/
│   │   │   ├── page.tsx         # Transactions list with filters
│   │   │   ├── [account_id]/
│   │   │   │   └── page.tsx     # Transactions for specific account
│   │   │   └── [transaction_id]/
│   │   │       └── page.tsx     # Transaction detail + edit modal
│   │   ├── analytics/
│   │   │   └── page.tsx         # Analytics & charts
│   │   ├── settings/
│   │   │   ├── page.tsx         # Settings tabs (account, family, categories)
│   │   │   ├── account/
│   │   │   │   └── page.tsx     # Personal account settings
│   │   │   ├── family/
│   │   │   │   └── page.tsx     # Family members (owner only)
│   │   │   └── categories/
│   │   │       └── page.tsx     # Category management (owner only)
│   │   └── profile/
│   │       └── page.tsx         # User profile
│   │
│   └── api/
│       └── auth/
│           ├── login/
│           │   └── route.ts     # (Optional local wrapper if needed)
│           └── logout/
│               └── route.ts     # (Optional local wrapper)
│
├── components/
│   ├── common/
│   │   ├── Navbar.tsx           # Top navigation bar
│   │   ├── Sidebar.tsx          # Left sidebar navigation
│   │   ├── FamilySelector.tsx   # Family dropdown selector
│   │   ├── UserMenu.tsx         # User profile dropdown
│   │   └── LoadingSpinner.tsx   # Loading indicator
│   │
│   ├── auth/
│   │   ├── LoginForm.tsx        # Email + password login
│   │   ├── RegisterForm.tsx     # Password + name setup (for invitations)
│   │   ├── ForgotPasswordForm.tsx
│   │   ├── ResetPasswordForm.tsx
│   │   └── ProtectedRoute.tsx   # HOC for auth-protected routes
│   │
│   ├── dashboard/
│   │   ├── SummaryCards.tsx     # Income/Expense/Savings cards
│   │   ├── QuickStats.tsx       # Top expense, income, savings rate
│   │   ├── RecentTransactions.tsx
│   │   └── Dashboard.tsx        # Composition component
│   │
│   ├── transactions/
│   │   ├── TransactionForm.tsx  # Create/edit modal
│   │   ├── TransactionTable.tsx # List with filters
│   │   ├── TransactionRow.tsx   # Table row with actions
│   │   ├── TransactionDetail.tsx # Detail view + edit history
│   │   ├── FilterPanel.tsx      # Date, type, category filters
│   │   └── TransactionList.tsx  # Composition component
│   │
│   ├── analytics/
│   │   ├── PieChart.tsx         # (shadcn/ui chart or Recharts)
│   │   ├── LineChart.tsx        # Trends
│   │   ├── BreakdownTable.tsx   # Category breakdown table
│   │   └── Analytics.tsx        # Composition component
│   │
│   ├── family/
│   │   ├── MembersList.tsx      # Family members table
│   │   ├── MemberForm.tsx       # Invite/edit member modal
│   │   ├── MemberActions.tsx    # Edit, disable, resend, revoke
│   │   └── FamilyManagement.tsx # Composition component
│   │
│   ├── categories/
│   │   ├── CategoryList.tsx     # By type (Income/Expense/Investment)
│   │   ├── CategoryForm.tsx     # Add/edit modal
│   │   └── Categories.tsx       # Composition component
│   │
│   └── ui/
│       ├── Modal.tsx            # Reusable modal wrapper
│       ├── Confirmation.tsx     # Confirmation dialog
│       ├── Toast.tsx            # Toast notifications (success/error)
│       ├── Form.tsx             # Form wrapper with validation
│       ├── Table.tsx            # Reusable table component
│       └── Pagination.tsx       # Pagination controls
│
├── lib/
│   ├── api-client.ts            # Axios/fetch wrapper for API calls
│   ├── hooks.ts                 # Custom React hooks (useAuth, useFamily, useCatergories)
│   ├── utils.ts                 # Utility functions (currency formatting, date parsing)
│   ├── constants.ts             # Enums, constants, default values
│   ├── api-queries.ts           # TanStack Query query definitions
│   └── types.ts                 # TypeScript interfaces/types
│
├── middleware.ts                # Next.js middleware for auth checks
├── next.config.js               # Next.js config
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json                # TypeScript config
├── package.json
├── README.md
└── .env.local                   # Local env vars (API_URL, etc.)
```

---

## 5. Component Architecture

### 5.1 Layout Structure

**Auth Routes** (`/(auth)/layout.tsx`):
- Centered card layout
- No sidebar, no main navigation
- Company branding/logo
- Back to login link where appropriate

**App Routes** (`/(app)/layout.tsx`):
- Header with:
  - NestFi logo/home
  - Family selector dropdown
  - Notifications (future)
  - User profile menu
- Sidebar with:
  - Dashboard
  - Transactions (with sub-items: All, Income, Expenses, Investments)
  - Analytics
  - Settings (owner-only in v1)
  - Logout

### 5.2 Page Components

| Page | Routes | Components | Owner |
|------|--------|-----------|-------|
| **Login** | `/login` | LoginForm | Both |
| **Registration** | `/register?token=...` | RegisterForm | Both |
| **Forgot Password** | `/forgot-password` | ForgotPasswordForm | FE |
| **Reset Password** | `/reset-password?token=...` | ResetPasswordForm | FE |
| **Family Selection** | `/family-selection` | FamilySelector modal (can be page or inline) | FE |
| **Dashboard** | `/dashboard` | SummaryCards, QuickStats, RecentTransactions | FE |
| **Transactions** | `/transactions`, `/transactions?type=income` | TransactionTable, FilterPanel, TransactionForm | FE |
| **Transaction Detail** | `/transactions/[id]` | TransactionDetail, EditHistory, Actions | FE |
| **Analytics** | `/analytics` | PieChart, LineChart, BreakdownTable, TabNav | FE |
| **Settings** | `/settings` | TabNav (Account, Family, Categories) | FE |
| **Family Members** | `/settings/family` | MembersList, MemberForm, MemberActions | FE |
| **Categories** | `/settings/categories` | CategoryList, CategoryForm | FE |
| **Profile** | `/profile` | UserInfo, ChangePassword | FE |

### 5.3 Reusable Components

**Common:**
- `Navbar` — Header with family selector, notifications, user menu
- `Sidebar` — Navigation menu
- `FamilySelector` — Dropdown for family switching
- `LoadingSpinner` — Skeleton loaders for async data

**UI Kit (shadcn/ui + custom):**
- `Modal` / `Dialog` — For forms and confirmations
- `Button` — CTA, secondary, destructive variants
- `Input` / `Select` / `Textarea` — Form fields
- `Table` — Transactions, members, categories
- `Tabs` — Settings tabs
- `DatePicker` — For transaction dates
- `Toast` / `Alert` — Notifications

**Data Display:**
- `TransactionRow` — Individual transaction with edit/delete
- `MemberCard` — Family member card or table row
- `CategoryBadge` — Category label with color

---

## 6. API Integration Strategy

### 6.1 API Client Setup

```typescript
// lib/api-client.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  withCredentials: true, // Include session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 6.2 TanStack Query Setup

**Query Keys Convention:**
```typescript
// lib/api-queries.ts
export const queryKeys = {
  auth: {
    me: () => ['auth', 'me'],
    user: () => ['auth', 'user'],
  },
  families: {
    all: () => ['families'],
    detail: (id: string) => ['families', id],
    members: (id: string) => ['families', id, 'members'],
    accounts: (id: string) => ['families', id, 'accounts'],
    categories: (id: string) => ['families', id, 'categories'],
  },
  transactions: {
    byAccount: (familyId: string, accountId: string) => 
      ['families', familyId, 'accounts', accountId, 'transactions'],
    detail: (familyId: string, accountId: string, txId: string) => 
      ['families', familyId, 'accounts', accountId, 'transactions', txId],
  },
};
```

**Hooks for common queries:**
```typescript
// lib/hooks.ts
export const useAuth = () => useQuery({
  queryKey: queryKeys.auth.me(),
  queryFn: () => apiClient.get('/auth/me'),
});

export const useFamilies = () => useQuery({
  queryKey: queryKeys.families.all(),
  queryFn: () => apiClient.get('/families'),
});

export const useTransactions = (familyId: string, accountId: string) =>
  useQuery({
    queryKey: queryKeys.transactions.byAccount(familyId, accountId),
    queryFn: () => apiClient.get(
      `/families/${familyId}/accounts/${accountId}/transactions`
    ),
  });
```

### 6.3 Mutations for Write Operations

```typescript
// Create transaction
const createTransactionMutation = useMutation({
  mutationFn: (data) => apiClient.post(
    `/families/${familyId}/accounts/${accountId}/transactions`,
    data
  ),
  onSuccess: () => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.transactions.byAccount(familyId, accountId),
    });
  },
});

// Update transaction
const updateTransactionMutation = useMutation({
  mutationFn: ({ txId, data }) => apiClient.put(
    `/families/${familyId}/accounts/${accountId}/transactions/${txId}`,
    data
  ),
  onSuccess: () => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.transactions.detail(familyId, accountId, txId),
    });
  },
});
```

---

## 7. Authentication Flow

### 7.1 Session/JWT Strategy

**Browser Session (Primary for v1):**
- Backend sets `session` cookie (httpOnly, Secure, SameSite=Strict)
- Frontend automatically includes cookie in all requests
- On login, FE stores user info in client state (Zustand)
- On logout, FE clears state and makes POST request to `/auth/logout`

**Protected Routes:**
- Middleware (`middleware.ts`) checks session on every request
- If no session, redirect to `/login`
- If session exists, allow access

### 7.2 Auth Flow Sequence

1. **Login Page**
   - User enters email + password
   - `POST /auth/login` (backend sets cookie)
   - If single family: redirect to `/dashboard`
   - If multiple families: redirect to `/family-selection`
   - Store user data in Zustand auth store

2. **Registration (Invitation)**
   - User clicks email link with `?token=...`
   - Validation fetches family info via token (or display from link)
   - User sets password + name
   - `POST /auth/register` with token
   - Redirect to login

3. **Password Reset**
   - User enters email → `POST /auth/request-password-reset`
   - Show confirmation message
   - User clicks email link with `?token=...`
   - User enters new password
   - `POST /auth/reset-password` with token + password
   - Redirect to login

---

## 8. Implementation Priorities (Task Breakdown)

### Phase A: Auth Foundation (Stories: US-1.1, US-1.2, US-1.3)

**Sprint A1: Login & Session**
- [ ] API client setup + TanStack Query
- [ ] Middleware for auth checks
- [ ] Login page + form component
- [ ] Session persistence (auth store)
- [ ] Protected route HOC
- [ ] Logout endpoint wrapper

**Sprint A2: Registration & Invitation**
- [ ] Registration page + form (via invitation token)
- [ ] Confirmation toast after registration
- [ ] Redirect to login

**Sprint A3: Password Reset**
- [ ] Forgot password page + form
- [ ] Reset password page + form
- [ ] Token validation on reset page

**Sprint A4: Family Selection** 
- [ ] Family selector page (if multiple families)
- [ ] Family selector dropdown (in navbar when in app)
- [ ] Store selected family in state + localStorage

---

### Phase B: Core Layouts & Navigation (US-2.1, US-2.2)

**Sprint B1: Main App Layout**
- [ ] Root layout with error boundary
- [ ] Navbar component (family selector, user menu)
- [ ] Sidebar navigation
- [ ] Responsive layout (desktop, tablet, mobile)

**Sprint B2: Settings Pages** 
- [ ] Settings tab layout
- [ ] Family members tab (read-only initially)
- [ ] Categories tab (read-only initially)
- [ ] Personal account tab (change password)

---

### Phase C: Dashboard (US-6.1)

**Sprint C1: Dashboard Overview**
- [ ] Dashboard page layout
- [ ] SummaryCards component (Income, Expenses, Savings, Net)
- [ ] Query family dashboard summary via API
- [ ] Update in real-time when transactions change

**Sprint C2: Quick Stats & Recent Transactions**
- [ ] QuickStats component (top expense, income, rate)
- [ ] RecentTransactions component
- [ ] Link to full transactions list

---

### Phase D: Transactions (US-5.1, US-5.2, US-5.4)

**Sprint D1: Transaction List & Filters**
- [ ] Transactions page layout
- [ ] TransactionTable component with columns
- [ ] FilterPanel (date range, type, category)
- [ ] Pagination
- [ ] Sorting (by date, amount)

**Sprint D2: Create Transaction Modal**
- [ ] TransactionForm component (create & edit)
- [ ] Type selector (Income, Expense, Investment)
- [ ] Category dropdown (filtered by type)
- [ ] Amount + date inputs
- [ ] Optional description field
- [ ] Account selector
- [ ] Form validation

**Sprint D3: Edit & Transaction Detail**
- [ ] Transaction detail page
- [ ] Edit history section
- [ ] Edit mutation (updates transaction + refreshes list)
- [ ] Disable/enable transaction (if user is member)
- [ ] Delete transaction button (if user is owner)

---

### Phase E: Analytics (US-6.2, US-6.3)

**Sprint E1: Expense Breakdown**
- [ ] Analytics page layout
- [ ] Pie/doughnut chart for expenses by category
- [ ] Breakdown table
- [ ] Time period selector

**Sprint E2: Income & Trends**
- [ ] Income breakdown chart
- [ ] Savings trend line chart
- [ ] Tab navigation between views

---

### Phase F: Family & Category Management (US-2.2, US-2.3, US-2.4, US-4.1, US-4.2)

**Sprint F1: Family Members (Read)**
- [ ] Members list view
- [ ] Show active members + pending invitations

**Sprint F2: Add/Edit Members**
- [ ] Add member modal (email, name, role)
- [ ] Edit member modal (change role, disable)
- [ ] Resend/revoke invitation buttons
- [ ] Disabled members show re-enable option

**Sprint F3: Categories**
- [ ] Category list by type
- [ ] Add/edit category modals (owner only)
- [ ] Show usage count per category
- [ ] Delete with confirmation (if not in use)

---

## 9. Key Implementation Notes

### 9.1 Conventions

- **Component naming**: PascalCase for components, camelCase for hooks/utils
- **File structure**: Organize by feature, not by type
- **Styling**: Use Tailwind utility classes; custom CSS only for complex layouts
- **API response types**: Auto-generate from OpenAPI spec (or manually define)
- **Error handling**: Toast notifications for user-facing errors, console.error for logs

### 9.2 Gotchas & Considerations

1. **Family-scoped data**: Every API call needs `family_id` in URL path. Easy to miss.
2. **Optimistic updates**: Transaction edits should update UI immediately, then sync with server.
3. **Account selector**: Transactions belong to accounts, not families directly. Remember to pass `account_id` in routes.
4. **Category filtering**: Categories are filtered by transaction type (Income/Expense/Investment). Don't hardcode.
5. **Date handling**: Use ISO 8601 (YYYY-MM-DD) for API; display in user's local timezone.
6. **Edit history**: Transaction detail page shows full edit history. Keep snapshots in mind (before/after).
7. **Role-based UI**: Hide owner-only buttons (delete, manage members, custom categories) for non-owners.
8. **Session persistence**: After refresh, check `/auth/me` to restore session; don't assume stored state is valid.

### 9.3 Testing Strategy (Post-MVP)

- **Unit tests**: Component logic, utility functions (Vitest)
- **Integration tests**: Page flows, API interactions (Playwright)
- **E2E tests**: Full user journeys (Playwright, deferred to v1.1)
- **API mocking**: Mock API responses in development (MSW or Postman)

---

## 10. Next Steps

1. **Confirm state management** → Proceed with TanStack Query + Zustand or propose alternative
2. **Set up Next.js project** → Install dependencies, configure middleware
3. **Implement Phase A** → Auth flows (login, register, password reset)
4. **Parallel backend implementation** → BE builds API endpoints in same order
5. **Integration testing** → Once API + FE endpoints ready, test end-to-end flows

---

## Appendix: Feature Parity with User Stories

| Story ID | Feature | Component(s) | Sprint |
|----------|---------|-------------|--------|
| US-1.1 | Superadmin login | LoginForm | A1 |
| US-1.2 | User registration (invitation) | RegisterForm | A2 |
| US-1.3 | User login & family selector | LoginForm, FamilySelector | A1, A4 |
| US-1.4 | Password reset | ForgotPasswordForm, ResetPasswordForm | A3 |
| US-2.1 | Create family | (owned by BE + backend flow) | - |
| US-2.2 | Add family members | MemberForm, FamilyManagement | F2 |
| US-2.3 | View family members | MembersList | F1 |
| US-2.4 | Disable/enable members | MemberForm, MemberActions | F2 |
| US-3.1 | Create bank account | (owned by BE, FE shows account selector) | D2 |
| US-3.2 | View all accounts | (FE shows in account selector + list) | D1, D2 |
| US-4.1 | View default categories | (FE fetches and filters) | D2 |
| US-4.2 | Create custom category | CategoryForm | F3 |
| US-5.1 | Record income transaction | TransactionForm | D2 |
| US-5.2 | Record expense transaction | TransactionForm | D2 |
| US-5.3 | Record investment transaction | TransactionForm | D2 |
| US-5.4 | Edit transaction | TransactionForm, TransactionDetail | D3 |
| US-5.5 | Disable/enable transaction | TransactionActions | D3 |
| US-6.1 | Dashboard summary | Dashboard, SummaryCards | C1 |
| US-6.2 | Expense breakdown | Analytics, ExpenseChart | E1 |
| US-6.3 | Income vs. expense trends | Analytics, TrendChart | E2 |
| US-7.1 | Logout | UserMenu, logout mutation | A1 |

