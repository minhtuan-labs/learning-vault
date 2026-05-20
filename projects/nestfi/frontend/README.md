# NestFi Frontend

Next.js 15 frontend for NestFi family financial management platform.

## Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query v5 (server state) + Zustand (client state)
- **API Client**: Axios
- **Package Manager**: npm

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── (auth)/              # Auth routes (login, register, password reset)
│   ├── (app)/               # Protected routes (dashboard, transactions, etc.)
│   └── layout.tsx           # Root layout
├── components/              # React components
│   ├── auth/                # Auth forms (LoginForm, RegisterForm)
│   ├── common/              # Common components (Navbar, Sidebar)
│   ├── dashboard/           # Dashboard components
│   ├── transactions/        # Transaction components
│   ├── analytics/           # Analytics components
│   └── ui/                  # Reusable UI components
├── lib/                     # Utilities and configuration
│   ├── api-client.ts        # Axios API client
│   ├── api-queries.ts       # TanStack Query hooks
│   ├── stores.ts            # Zustand stores (auth, UI)
│   ├── types.ts             # TypeScript types
│   ├── utils.ts             # Helper functions
│   └── constants.ts         # App constants
├── middleware.ts            # Next.js middleware for auth
├── tailwind.config.ts       # Tailwind configuration
├── next.config.js           # Next.js configuration
├── tsconfig.json            # TypeScript configuration
└── package.json
```

## Getting Started

### Install dependencies

```bash
npm install
```

### Set environment variables

Copy `.env.example` to `.env.local` and update if needed:

```bash
cp .env.example .env.local
```

### Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Key Features Implemented

### Phase A: Auth Foundation (In Progress)
- [x] API client setup with Axios
- [x] TanStack Query configuration
- [x] Zustand auth store
- [x] Login page and form
- [x] Registration page
- [x] Password reset flow (UI)
- [x] Family selection page
- [x] Logout functionality
- [x] Auth middleware for protected routes

### Phase B: Core Layouts & Navigation (In Progress)
- [x] Main app layout with sidebar
- [x] Navbar with user menu
- [x] Sidebar navigation
- [x] Settings page stub

### Phase C: Dashboard (In Progress)
- [x] Dashboard page with summary cards
- [ ] Real data integration from API

### Phase D: Transactions (Planned)
- [ ] Transaction list with filters
- [ ] Create/edit transaction modals
- [ ] Transaction detail view

### Phase E: Analytics (Planned)
- [ ] Chart components
- [ ] Category breakdown

### Phase F: Family Management (Planned)
- [ ] Family members list
- [ ] Member invitation/management

## State Management

### Server State (TanStack Query v5)
- User authentication (`useAuth`)
- Families, accounts, categories
- Transactions (with mutations)

### Client State (Zustand)
- Selected family ID (persisted to localStorage)
- Current user info
- UI state (sidebar open/closed)

### Auth Context
- Session management via cookies
- User info stored in Zustand

## API Integration

All API calls go through `lib/api-client.ts` which handles:
- Base URL configuration from env vars
- Session cookie support (withCredentials)
- Error handling (401 redirects to /login)

Query hooks are defined in `lib/api-queries.ts` following TanStack Query conventions.

## Development

### Add a new page

1. Create the page file in `app/` folder (e.g., `app/(app)/transactions/page.tsx`)
2. Export a default component
3. Next.js automatically creates the route

### Add a new query

1. Define the query hook in `lib/api-queries.ts`
2. Use it in your component with `const { data, isLoading } = useYourQuery()`

### Add a new store

1. Create the store in `lib/stores.ts` using `create()` from Zustand
2. Use it with `const state = useYourStore((state) => state.prop)`

## Testing

Unit and integration tests are deferred to v1.1. Use:
- Vitest for unit tests
- Playwright for e2e tests

## Next Steps

1. **Connect to real backend**: Update API endpoints once BE is ready
2. **Implement transaction pages**: Create/edit modals, detail views
3. **Add analytics charts**: Integrate chart library (Recharts or shadcn/ui charts)
4. **Family management UI**: Full CRUD for members and categories
5. **E2E tests**: Playwright test suite for critical flows
6. **Error handling**: Improve error messages and retry logic
