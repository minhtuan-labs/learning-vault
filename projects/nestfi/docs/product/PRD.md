# Product Requirements Document (PRD) — NestFi

**Product:** NestFi - Family Financial Management Platform  
**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** PM  

---

## Executive Summary

NestFi is a web-based family financial management platform that enables households to collaboratively track, categorize, and analyze their finances in real-time. The product targets couples and families who share finances and need unified visibility into income, expenses, savings, and investments.

**MVP Scope:** Core income/expense tracking with categorization, family member management via email invitations, multi-family support, and analytics dashboard.

---

## Problem Statement

**Pain Point:**  
Families lack a centralized way to track and manage household finances. Without unified visibility, family members cannot easily understand spending patterns, manage shared budgets, or plan financial goals together.

**Current State:**  
- Families use spreadsheets, multiple banking apps, or no system at all
- No shared visibility across family financial activity
- Difficult to categorize and analyze household spending
- No clear way to invite and manage multiple family members

**Opportunity:**  
A single, collaborative platform that acts as the "home base" for household financial management.

---

## Target Users & Personas

### Primary Users
- **Couples managing joint finances** (age 25-55)
  - Share bank accounts and need transaction visibility
  - Want joint budget tracking and spending analysis
  - Prefer simplicity and minimal setup friction

- **Families with 3+ members** (age 25-65)
  - Manage household expenses collectively
  - Track who spent what and on what category
  - Benefit from shared financial oversight
  - May include multi-generational members (adult children, parents)

### Secondary Users
- **Young professionals** managing side income and expenses
- **Roommates** splitting shared household costs

---

## Product Vision

**Vision Statement:**  
"NestFi brings financial transparency and collaboration to households. Every family member has real-time visibility into household finances, enabling informed decisions and shared financial goals."

**Key Principles:**
- **Simplicity:** Easy to add transactions and family members
- **Transparency:** Real-time, shared visibility into all financial activity
- **Collaboration:** Designed for team (family) management, not individual budgeting
- **Categories-driven:** Spending analysis powered by user-defined categories

---

## Core Use Cases

### UC-1: Family tracks household income and expenses with custom categories
- Family creates custom income categories (e.g., "Salary", "Freelance", "Investments")
- Family creates custom expense categories (e.g., "Groceries", "Utilities", "Entertainment")
- Cash withdrawals treated as expenses under "Cash Withdrawal" category
- Categories appear across all family members' transaction logs

### UC-2: Family members log transactions
- Member opens dashboard and logs a transaction (amount, category, date, notes)
- Options: income, expense, or cash withdrawal
- Transaction immediately visible to all family members in shared ledger

### UC-3: Family views dashboard with spending trends and analysis
- Dashboard shows:
  - Total household income (month/year)
  - Total household expenses (month/year) by category
  - Spending trends (month-over-month, category breakdown)
  - Savings rate (income - expenses)
  - Investment category totals if tracked
- Charts and summaries update in real-time

### UC-4: Superadmin creates families and invites owners
- Superadmin logs in (default: superadmin/admin123)
- Superadmin can:
  - Create a new family (name, optional details)
  - Invite initial owner via email with unique link/token
  - Manage all families (audit, suspend, etc.)

### UC-5: Owner accepts invitation and adds family members
- Owner receives email with invitation link
- Owner clicks link, verifies email, sets password/account details
- Owner can now:
  - Add other family members via email invitations
  - Set up bank accounts and categories
  - View and manage family dashboard
  - Manage family member permissions (view-only vs edit)

### UC-6: User belongs to multiple families and switches between them
- User can accept invitations from multiple families
- On login, user sees list of families they belong to
- User selects which family to view/manage
- User can switch families without re-logging-in

### UC-7: Family manages financial configuration
- Owner (or designated admin) can:
  - Add/edit bank accounts (name, account type, currency)
  - Create/edit income categories
  - Create/edit expense categories
  - Create/edit investment categories
  - Set permissions for other members (who can add transactions, edit categories, etc.)

---

## Feature Set — MVP (v1)

### Must-Have Features

#### Authentication & User Management
- [x] Superadmin account with hardcoded initial credentials (superadmin/admin123, changeable)
- [x] Email-based invitation and acceptance workflow for owners and members
- [x] Password reset via email
- [x] Multi-family support (one user account → multiple families)
- [x] Family switching on login/dashboard
- [x] Permission levels: Superadmin, Owner, Member (view-only vs edit)

#### Transaction Tracking
- [x] Income transaction logging (amount, category, date, notes, member)
- [x] Expense transaction logging (amount, category, date, notes, member)
- [x] Cash withdrawal (treated as expense, auto-categorized or user-selected)
- [x] Transaction history/ledger (searchable, filterable by date/category/member)
- [x] Ability to edit/delete own transactions (with audit log)

#### Categories & Configuration
- [x] Custom income categories (e.g., "Salary", "Bonus", "Freelance", "Other")
- [x] Custom expense categories (e.g., "Groceries", "Utilities", "Entertainment", "Transport")
- [x] Custom investment categories (e.g., "Stock Portfolio", "Retirement", "Crypto")
- [x] Category default color/icon for visual organization
- [x] Ability to mark categories as active/inactive (archive)

#### Dashboard & Analytics
- [x] Real-time overview: total income, total expenses, net savings (current month/year)
- [x] Category breakdown: pie chart or bar chart of expenses by category
- [x] Monthly trends: income and expenses over time (last 6-12 months)
- [x] Family member activity: who logged what, when
- [x] Savings rate calculation
- [x] Summary statistics (avg transaction, highest/lowest category)

#### Family Management
- [x] Create family (name, description, initial owner email)
- [x] Invite family members via email
- [x] Accept/decline invitations
- [x] View family member list (name, email, role, join date)
- [x] Remove members (with confirmation)
- [x] Family settings: name, description, logo (optional)

#### Bank Accounts (Optional for v1, but tracked)
- [ ] Add bank account (name, account type, currency, balance)
- [ ] Assign transactions to accounts
- [ ] View account balances

### Nice-to-Have Features (Deferred to v2)
- Budget tracking and alerts
- Investment portfolio detailed tracking
- Financial goal setting and progress tracking
- Automated categorization suggestions (ML)
- Mobile app (iOS/Android)
- Bill splitting among family members
- Financial reports and exports (CSV, PDF)
- Multi-currency support and currency conversion
- Bank account integration (API)
- Dark mode

---

## Out of Scope (v1)

- Tax reporting integration
- Bill splitting algorithm
- Mobile-native apps (web-responsive is MVP)
- Advanced financial planning (forecasting, goal-based budgeting)
- Investment portfolio API integrations
- Bank statement import/reconciliation
- Multi-currency support

---

## Success Metrics

### Activation & Engagement
1. **Fast onboarding:** Family members can log in and view household financial overview within 2 minutes
2. **Data consistency:** All family members see consistent, up-to-date transaction data
3. **Category adoption:** Categories are used meaningfully (>80% of transactions categorized)
4. **Regular usage:** Users log transactions at least once per week (weekly activity)

### Product Quality
1. **Uptime:** >99.5% platform availability
2. **Transaction accuracy:** 100% of transactions recorded correctly, no data loss
3. **Email delivery:** Email invitations delivered within 5 minutes, >99% success rate

### User Retention
- Week 1 retention: >60% of invited users complete onboarding
- Month 1 retention: >40% of Week 1 users remain active
- Month 3 retention: >25% of Month 1 users remain active

### Business/Growth
- Monthly active families: grow from 0 to 50+ by end of Q2
- Monthly active users: grow from 0 to 150+ by end of Q2
- Net Promoter Score: target >40 by end of Q2

---

## Constraints & Assumptions

### Constraints
- **Timeline:** Not specified (assumes iterative delivery, 8-12 week MVP)
- **Budget:** Startup/self-funded (minimize infrastructure costs)
- **Deployment:** Web-based (desktop-first, mobile-responsive)
- **Security & Compliance:** 
  - Email verification required for invitations
  - Secure password handling (no plaintext storage)
  - GDPR compliance for user data
  - PII encryption at rest

### Assumptions
- Target users have joint bank accounts or shared access to household transaction data
- Email is the primary communication channel for invitations and account management
- Users can categorize their own transactions (no ML required for v1)
- Families are 2-5 members on average (scaled design for up to 50 members per family)
- Initial users are tech-savvy enough to navigate web app

---

## Known Open Questions

> **NOTE:** These should be confirmed with user and documented in planning/OPEN_QUESTIONS.md.

1. **Multi-currency support:** Should NestFi support families with multiple currencies in v1? (e.g., USD, EUR, VND)
   - Impacts: Database schema, calculation logic, UI complexity
   - Recommendation for v1: Single currency per family (simplify MVP)

2. **Bill splitting feature:** Should v1 include bill-splitting logic (e.g., restaurant bill split 3 ways)?
   - Impacts: Transaction data model, UI for splitting
   - Recommendation for v1: Deferred to v2 (document workaround: manual category "Shared Expense")

3. **Investment tracking depth:** Should v1 track portfolio returns, cost basis, unrealized gains?
   - Impacts: Data complexity, UX for investment section
   - Recommendation for v1: Simple tracking only (amount by category, no performance metrics)

4. **Analytics depth:** Should v1 include ML-powered categorization suggestions or advanced forecasting?
   - Impacts: Infrastructure, data science requirements
   - Recommendation for v1: No ML, manual categorization only

5. **Transaction editing permissions:** Can members edit each other's transactions or only their own?
   - Impacts: Permission model, audit trail requirements
   - Recommendation: Each member can edit/delete their own; Owner can edit/delete any

---

## Product Roadmap (Sequencing)

See docs/product/ROADMAP.md for detailed phases and timelines.

**High-level phases:**
- **Phase 0 (v0.1):** MVP core (auth, transaction logging, dashboard)
- **Phase 1 (v0.2):** Polish & scaling (UX refinement, performance, bug fixes)
- **Phase 2 (v1.0):** Release candidate (full QA, documentation, deployment)
- **Phase 3 (v1.1+):** Feature expansion (nice-to-haves, community feedback)

---

## Acceptance Criteria for Phase Gate

**Phase 0_DISCOVERY exit criteria:**
- [x] PRD created with feature list and acceptance criteria
- [x] ROADMAP created with sequencing and timelines
- [x] OPEN_QUESTIONS documented (if any blockers exist)
- [x] No major scope ambiguity remaining

**Next phase:** 1_SOLUTION_DESIGN  
**Owner:** SA (Solution Architect)  
**Trigger:** PRD review + user confirmation of tech stack direction

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | PM | Created PRD from PRODUCT_IDEA.md |

