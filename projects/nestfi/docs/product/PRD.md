# NestFi — Product Requirements Document

## Product Vision
NestFi is a web-based family financial management platform that helps households track income, expenses, savings, and investments **by tracking which bank account money comes from**, with a unified dashboard and multi-user collaboration features.

## Problem Statement
Families lack a centralized, easy-to-use platform to track shared finances across multiple bank accounts, categorize transactions, and gain visibility into their collective financial health. Existing solutions are either too complex for household use or lack multi-user collaboration. **NestFi focuses on account-based tracking** (which account funds come from) rather than person-to-person splitting.

## Target Users
- **Primary**: Household managers / breadwinners responsible for family finances
- **Secondary**: Other family members who need visibility into household finances
- **Administrators**: System administrators managing multiple families

## Key Features (MVP)

### 1. User & Family Management
- **Superadmin Account**: Pre-configured superadmin account (default: username `superadmin`, password `admin123`)
  - Can create new families
  - Can designate family owners
  - **Must change password on first login** (security requirement)
- **Family Creation**: Superadmin creates a family and invites an owner
- **Owner Invitations**: Owner is invited via email, accepts invitation to activate
  - **New owners must set their own password on first login** (before accessing family data)
- **Multi-Family Support**: Users can belong to multiple families
  - **Family selector at login**: Users select their family when logging in
  - **Family switcher in dashboard**: Quick-switch dropdown to change families without logout
  - **Users can switch families anytime** (within their access)
- **Family Members**: Owner can add additional family members after accepting invitation
  - **New members must set their own password on first login** (before accessing family data)

### 2. Financial Management
- **Transaction Tracking** (account-centric model):
  - Income transactions (linked to source account)
  - Expense transactions (deducted from source account)
  - **Cash withdrawals**: Single "Rút Cash" / "Cash Withdrawal" transaction (treated as a simple expense, not detailed sub-tracking)
  - Investment tracking (linked to source account)
- **Categories**: 
  - Income categories (salary, bonus, other income)
  - Expense categories (groceries, utilities, entertainment, etc.)
  - Investment categories (stocks, crypto, real estate, etc.)
- **Bank Accounts**: Track multiple bank accounts within a family; **every transaction is associated with a source bank account**

### 3. Dashboard & Analytics
- **Overview Dashboard**: 
  - Summary of total income, total expenses, net balance
  - Transaction history (recent activity)
  - Family context indicator and switcher
- **Analytics & Reports**:
  - Expense breakdown by category
  - Income breakdown by source
  - Savings trend analysis
  - Investment summary
  - **Export reports** (CSV/PDF formats):
    - Transaction list export
    - Category breakdown reports
    - Income/expense summary reports
    - Date-range filtering for exports

## Scope: MVP vs Future

### MVP (Phase 1)
- User authentication (email-based)
  - Forced password change on first login (superadmin, owners, members)
  - Family selector at login + in-dashboard family switcher
- Family creation and basic member management
- Transaction CRUD operations (create, read, update, delete)
- Category management for income/expenses
- Basic dashboard with summary statistics
- Simple category-based analytics
- **Report export functionality** (CSV/PDF formats)

### Future (Post-MVP)
- Advanced analytics (forecasting, budget planning)
- Recurring transactions and auto-categorization
- Receipt attachment / photo scanning
- Notifications and alerts
- Mobile app
- Multi-currency support
- Bill splitting features
- Tax reporting tools

## Technical Requirements (Non-Functional)

### Performance
- Dashboard should load in < 2 seconds
- Transaction list pagination for large datasets
- Efficient database queries for analytics

### Security
- Secure password hashing
- Email-based user verification
- Role-based access control (superadmin, owner, member)
- Data isolation between families
- Session management: No automatic session timeout (users must manually logout)
  - Long-lived sessions for household use (family members accessing together)
  - Manual logout is the only way to end a session

### Usability
- Responsive web design (desktop-first, mobile-friendly)
- Intuitive navigation
- Clear labeling and categorization

## Success Metrics

### Functional
- All CRUD operations for transactions working end-to-end
- Dashboard displays correct financial summaries
- Multi-user family access functional

### Non-Functional
- Page load time < 2 seconds
- No data leakage between families
- Email invitations working correctly

## Assumptions & Constraints

### Assumptions
- Users have valid email addresses for invitations
- Families will have 2-10 members (not massive teams)
- Transactions are primarily for household tracking, not business accounting
- Cash withdrawals are a simple category, not a detailed tracking mechanism

### Constraints
- MVP targets desktop/web (mobile not in scope)
- No complex accounting rules (single-currency, household focus)
- No automatic transaction importing from bank APIs in MVP

## Out of Scope (v1)
- Supply chain integration (no bank API auto-import)
- Multi-currency
- AI-powered categorization
- **Bill splitting (person-to-person expense splitting deferred to v2.0)**
- Mobile-first design (responsive, not native app)
- Detailed cash sub-transaction tracking

## Acceptance Criteria

The product is considered complete when:
1. ✅ Superadmin account (username `superadmin`, password `admin123`) can create families
2. ✅ Superadmin is forced to change password on first login
3. ✅ Owner receives email invitation and accepts to activate account
4. ✅ New owners/members are forced to set their own password on first login
5. ✅ Users can log in and see a family selector (if they belong to multiple families)
6. ✅ Users can access the dashboard and see in-dashboard family switcher
7. ✅ Owner can add family members after account activation
8. ✅ Users can create income, expense, and investment transactions
9. ✅ Users can manage transaction categories
10. ✅ Dashboard shows accurate income, expense, and net balance summaries
11. ✅ Dashboard displays recent transaction history with family context
12. ✅ Analytics show expense/income breakdowns by category and account
13. ✅ Users can export reports (CSV/PDF) with date-range filtering
14. ✅ Role-based access control enforced (members cannot delete family, etc.)
15. ✅ All family members see all transactions (full transparency model)
16. ✅ Session remains active until user manually logs out (no automatic timeout)
