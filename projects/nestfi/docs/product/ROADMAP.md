# NestFi — Product Roadmap

## Release Timeline

```
Phase 2 (Plan)  →  Phase 4 (Build)  →  Phase 5 (Test)  →  Phase 6 (Deploy)
         ↓              ↓                    ↓                    ↓
    2_BACKLOG_    4_BUILD              5_TEST_AND_FIX       6_DELIVERY
    AND_SPEC      (Weeks 1-3)          (Week 4)             (Week 4)
                                                                 ↓
         v1.0 MVP Release          →  v1.1 Polish  →  v1.2 UX/Polish  →  v2.0 Advanced
         (Production Ready)          (Week 5-6)      (Week 7-8)           (Month 3+)
```

---

## v1.0 — MVP (Core Features)

**Phase**: Phase 4_BUILD (Weeks 1-3) + Phase 5_TEST_AND_FIX (Week 4) + Phase 6_DELIVERY (Week 4)  
**Priority**: MUST-HAVE (Blocks Release)  
**Status**: PLANNED (begins after Phase 2_BACKLOG_AND_SPEC complete)

### User Stories Included

#### Milestone 1: Auth & Family Foundation (Week 1)
- **US-1.1** Superadmin Login
  - Default superadmin account (superadmin/admin123)
  - Forced password change on first login
  - Can log in and access superadmin panel
- **US-1.2** User Registration via Email Invitation
  - Superadmin can invite family owners via email
  - Email contains unique confirmation link (7-day validity)
  - Owner accepts invitation and sets password
- **US-1.3** User Login
  - Email/password authentication
  - Family selector if user belongs to multiple families
  - Direct dashboard access if single family
- **US-2.1** Create a New Family
  - Owner prompted to name family after accepting invitation
  - Owner automatically designated as family owner
- **US-2.2** Add Family Members
  - Owner can invite members via email
  - Members accept invitation and set password

**Deliverable**: Fully functional authentication system; family creation workflow

#### Milestone 2: Finance & Transactions (Week 2)
- **US-3.1** Create Bank Account
  - Add multiple accounts (bank, savings, investment, cash)
  - Optional initial balance
  - Visible to all family members
- **US-3.2** View All Accounts
  - List all family accounts with balances
  - Sortable by type/balance
- **US-4.1** View Default Categories
  - Pre-populated categories for all families
  - Income, expense, and investment categories
- **US-5.1** Record Income Transaction
  - Create income transactions linked to accounts
  - Amount, date, category, description
- **US-5.2** Record Expense Transaction
  - Create expense transactions (including "Cash Withdrawal" category)
  - Amount, date, category, description
- **US-5.4** Edit Transaction
  - All members can edit any transaction
  - Edit history tracked (who, when, before/after)

**Deliverable**: Complete transaction recording and editing capability

#### Milestone 3: Dashboard & Reports (Week 3)
- **US-6.1** View Dashboard Summary
  - Total income, expenses, net balance
  - Account balances
  - Recent transaction history
  - Load time < 2 seconds
- **US-6.2** View Expense Breakdown by Category
  - Pie/bar chart of expenses by category
  - Period selector (month/year/custom)
  - Sortable by amount
- **US-6.4** Export Financial Report
  - CSV/PDF export of transactions
  - Date-range filtering
  - Includes all categories
- **US-7.1** Logout
  - Clear session
  - Invalidate tokens
  - Redirect to login

**Deliverable**: Fully functional dashboard and reporting

### Acceptance Criteria (MVP)
- ✅ All 14 MUST stories implemented and merged
- ✅ TEST_REPORT.md shows VERDICT: PASS
- ✅ BUG_REPORT.md has no OPEN_CRITICAL or OPEN_MAJOR bugs
- ✅ All family workflows work end-to-end (superadmin → owner → member)
- ✅ Dashboard loads < 2 seconds
- ✅ Data isolation: No cross-family data leakage
- ✅ Email invitations working (mocked in dev, real in prod)
- ✅ Role-based access control enforced on backend
- ✅ Performance requirements met

### Non-Functional Requirements Met
- **Security**: Passwords hashed (bcrypt); session tokens; family-scoped authorization
- **Performance**: Dashboard < 2sec; pagination for large datasets; efficient queries
- **Reliability**: No data loss; transaction audit trail; edit history preserved
- **Usability**: Clear navigation; intuitive forms; responsive design (desktop-first)

### Deployment Readiness
- ✅ docker-compose.yml configured
- ✅ Database schema migrated
- ✅ Superadmin account seeded
- ✅ Email service configured (SMTP/SendGrid)
- ✅ Release notes documented
- ✅ Running app accessible at http://localhost:3000 (or production URL)

---

## v1.1 — Polish & Stability (Post-MVP)

**Phase**: Week 5-6 (after v1.0 ships)  
**Priority**: SHOULD-HAVE (Quality improvements)  
**Depends On**: v1.0 MVP shipped and in production

### User Stories Included
- **US-1.4** Password Reset
  - Forgot password flow
  - Reset link expires 1 hour
- **US-2.3** View Family Members
  - List active members and pending invitations
  - Resend invitation option
- **US-2.4** Disable/Enable Family Members
  - Owner can revoke/restore access
  - Transactions preserved
- **US-3.3** Edit Account
  - Update account name and type
- **US-4.2** Create Custom Category
  - Owner can add custom categories
- **US-5.3** Record Investment Transaction
  - Investment tracking with source account
- **US-5.5** Disable/Restore Transaction
  - Members soft-delete (disable) transactions
  - Only owner can hard-delete
- **US-6.3** View Income vs. Expense Trends
  - Monthly trend lines
  - Custom date ranges

### Key Improvements
- 📊 Enhanced dashboard UI/UX
- 🔍 Transaction search and filtering
- 📅 Advanced date-range filtering
- 💾 Enhanced export options
- ⚡ Performance optimization (caching, query optimization)
- 🐛 Bug fixes from v1.0
- 📧 Email confirmations for critical actions

### Success Criteria
- All SHOULD stories merged
- Dashboard UX improvements validated
- Page load time maintained < 2 seconds
- Transaction search covers all fields
- Zero regressions in MUST story workflows

---

## v1.2 — UX & Mobile Enhancement

**Phase**: Week 7-8 (after v1.1 complete)  
**Priority**: COULD-HAVE (Nice-to-have improvements)  
**Depends On**: v1.1 shipped and stable

### Deliverables
- 📱 Mobile-responsive design improvements
  - Responsive tables and forms
  - Touch-friendly buttons and inputs
  - Mobile-optimized navigation
- 🎨 Dark mode support
  - Theme toggle (light/dark)
  - Persistent user preference
- 📊 Enhanced analytics
  - Advanced income vs. expense comparisons
  - Custom period selections
- 💬 Tooltips and contextual help
  - On-hover help for form fields
  - Feature tours for new users
- ♿ Accessibility improvements
  - WCAG AA compliance audit
  - Screen reader support
  - Keyboard navigation
- 🌐 Internationalization prep
  - i18n framework setup
  - Vietnamese translation (primary market)
  - English fallback

### Success Criteria
- App fully usable on mobile devices (480px+)
- Dark mode toggle working on all pages
- Accessibility audit passes WCAG AA
- All interactive elements keyboard-accessible
- i18n strings extracted and translated

---

## v2.0 — Advanced Features

**Phase**: Month 3+ (after v1.2 shipped)  
**Priority**: NICE-TO-HAVE (Future enhancements)  
**Depends On**: v1.2 stable, user feedback collected

### Planned Features
- 🔄 **Recurring Transactions**
  - Auto-create monthly income/expenses
  - Configurable schedule (monthly, bi-weekly, etc.)
  - Manual override capability
- 📸 **Receipt Attachments**
  - Photo/image attachment to transactions
  - OCR text extraction (optional)
  - Receipt storage and organization
- 🏦 **Bank Account Sync**
  - Limited manual API integration
  - Transaction auto-import (optional, manual)
  - Reconciliation matching
- 🔔 **Notifications & Alerts**
  - Email digests (weekly/monthly)
  - Budget alerts when spending threshold exceeded
  - Important action reminders
- 📱 **Native Mobile App**
  - iOS app (via React Native or native)
  - Android app (via React Native or native)
  - Offline-first capability
- 🌍 **Multi-Currency Support**
  - Currency conversion rates
  - Multi-currency accounts
  - Consolidated reporting
- 👥 **Bill Splitting**
  - Person-to-person expense splitting
  - Settlement tracking
  - Debt ledger (who owes whom)
- 📈 **Advanced Forecasting**
  - Budget planning and tracking
  - Spending trend analysis
  - Financial goal setting
- 🤖 **AI-Powered Categorization**
  - ML-based auto-categorization on transaction entry
  - Learning from user corrections
  - Batch re-categorization
- 📊 **Tax Reporting**
  - Tax-compliant summaries
  - Deductible expense tracking
  - Export for accountants (Vietnamese formats)

### Out of Scope for v1.x
- Bill splitting (person-to-person) — will implement account-centric model first
- Multi-currency — single currency in v1
- Bank API auto-import — manual only
- AI categorization — rule-based only in v1
- Mobile native app — web-first in v1

---

## Dependency & Gate Framework

### MVP Release Gate (v1.0 → Production)

**Must Complete (Phase 2):**
- [ ] All 14 MUST stories have final acceptance criteria
- [ ] API contract finalized (SA + BE agreement)
- [ ] Test plan written (QA)
- [ ] Implementation plans ready (BE + FE)
- [ ] Email service provider selected and configured

**Must Pass (Phase 5):**
- [ ] TEST_REPORT.md exists with VERDICT: PASS
- [ ] BUG_REPORT.md has no OPEN_CRITICAL or OPEN_MAJOR bugs
- [ ] All MUST story workflows tested end-to-end
- [ ] Performance targets met (dashboard < 2sec)
- [ ] Security audit passed (family data isolation, password hashing, HTTPS)

**Must Complete (Phase 6):**
- [ ] Docker image builds successfully
- [ ] docker-compose up -d runs without errors
- [ ] Database migrations apply cleanly
- [ ] RUNNING_APP.md contains production URL
- [ ] Release notes documented

### v1.0 → v1.1 Gate

**Blocker**: v1.0 must be in production for 1 week with zero OPEN_CRITICAL bugs

**Owner Decision**: PM + User agree v1.1 scope

### v1.1 → v1.2 Gate

**Blocker**: v1.1 performance targets met (page load < 2sec sustained)

**Owner Decision**: UX/PM validate design improvements

### v1.2 → v2.0 Gate

**Blocker**: v1.2 user feedback collected and analyzed

**Owner Decision**: User confirms v2.0 priorities (bill-splitting? multi-currency? mobile-first redesign?)

---

## Resource Plan (Estimated)

| Phase | BE | FE | QA | DELIVERY | SA | Duration |
|-------|----|----|----|-----------|----|----------|
| **2_BACKLOG** | 10% | 10% | 20% | - | 40% | 1 week |
| **3_PLANNING** | 30% | 30% | 30% | 10% | 30% | 1 week |
| **4_BUILD (v1.0)** | 50% | 50% | 10% | - | 5% | 3 weeks |
| **5_TEST** | 30% | 20% | 70% | 10% | - | 1 week |
| **6_DELIVERY** | 10% | 10% | 10% | 70% | 5% | 1 week |
| **v1.1 (Week 5-6)** | 40% | 40% | 20% | - | - | 2 weeks |
| **v1.2 (Week 7-8)** | 20% | 60% | 20% | - | - | 2 weeks |

---

## Key Decision Points (Awaiting User Input)

1. ✅ **Bill-Splitting Model** (DECIDED)
   - Account-centric, NOT person-to-person
   - Deferred to v2.0
   - User approved: "Tracks which account money comes from"

2. ✅ **Session Timeout** (DECIDED)
   - Manual logout only in v1.0
   - Auto-timeout deferred to v1.1+
   - User approved: "No automatic timeout for household sharing"

3. ✅ **Export Reports** (DECIDED)
   - CSV/PDF in v1.0
   - Scheduled exports deferred to v1.1
   - User approved: "Include in v1.0 with date-range filtering"

4. ⏳ **Email Provider** (PENDING)
   - SMTP server, SendGrid, Mailgun, etc.?
   - User action: Provide email service credentials or approve provider

5. ⏳ **Hosting Target** (PENDING for v1.0 production)
   - Docker Compose (local dev ready)
   - Cloud: Render, Railway, Fly.io, AWS ECS, GCP, etc.?
   - User action: Select hosting + provide deployment resources

---

## Success Metrics

### MVP (v1.0) Success
- **Functional**: All 14 MUST stories shipped without critical bugs
- **Performance**: Dashboard loads < 2 seconds consistently
- **Security**: Zero data leakage between families; all passwords hashed
- **User Satisfaction**: Superadmin → owner → member workflow intuitive and complete

### Post-MVP (v1.1+) Success
- **Quality**: User satisfaction 4/5 stars or higher
- **Performance**: Page load time sustained < 2 seconds with 10x transaction volume
- **Reliability**: 99.5% uptime; zero data loss incidents
- **User Growth**: Users able to invite other families and grow organically

### v2.0 Success Criteria (TBD)
- Pending v1.x user feedback and market validation

---

## References

- **Backlog Detail**: See `planning/BACKLOG.md` (prioritized user stories with MoSCoW)
- **User Stories**: See `docs/business/USER_STORIES.md` (28 detailed stories with AC)
- **PRD**: See `docs/product/PRD.md` (vision, features, non-functional requirements)
- **UX Flows**: See `docs/product/UX_FLOW.md` (wireflows and navigation)
- **Architecture**: See `docs/architecture/SOLUTION_ARCHITECTURE.md` (API, database, deployment)
