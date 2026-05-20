# NestFi — Product Backlog

Prioritized list of user stories for implementation, organized by MVP scope and dependencies.

**Phase**: 2_BACKLOG_AND_SPEC (current) → Phase 4_BUILD  
**MVP Target**: All MUST stories complete and tested before Phase 6_DELIVERY

## Priority Levels (MoSCoW)

- **MUST** (P0): Essential for MVP v1.0 launch; blocks release if incomplete
- **SHOULD** (P1): High-value features for MVP; implement if time allows
- **COULD** (P2): Nice-to-have; suitable for v1.1+ if MVP timeline is tight
- **WON'T** (P3): Explicitly out of v1.x scope; defer to v2.0+

---

## Story Group 1: Authentication & Account Setup (Foundation)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-1.1** | Superadmin Login | MUST | PENDING | M | System bootstrap | Default account: superadmin/admin123; forced password change on first login |
| **US-1.2** | User Registration via Email Invitation | MUST | PENDING | L | Email service, US-1.1 | Invitation link valid 7 days; email confirmation required; new owners/members force password change on first login |
| **US-1.3** | User Login | MUST | PENDING | M | US-1.1, US-1.2 | Email/password login; family selector if multiple families; no auto-timeout |
| **US-1.4** | Password Reset | SHOULD | PENDING | M | US-1.3 | Forgot password flow; reset link expires 1 hour; deferred to v1.1 if time-constrained |

**Acceptance Criteria (Group 1):**
- [ ] Superadmin can log in and is prompted to change password (security requirement)
- [ ] Owner can receive email invitation, accept, and set password before accessing family data
- [ ] New members inherit password-change-on-first-login requirement
- [ ] User can log in with email and password
- [ ] Users with multiple families see family selector at login
- [ ] Users with one family log directly into dashboard
- [ ] Sessions persist until manual logout (no automatic timeout)

---

## Story Group 2: Family Management (Core Domain)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-2.1** | Create a New Family | MUST | PENDING | M | US-1.3 (owner logged in) | Owner prompted to name family after email acceptance; becomes family owner automatically |
| **US-2.2** | Add Family Members | MUST | PENDING | L | US-2.1, email invitations | Owner can invite members; email confirmation required; members can belong to multiple families |
| **US-2.3** | View Family Members | SHOULD | PENDING | S | US-2.2 | Show active members and pending invitations; resend invitation option |
| **US-2.4** | Disable/Enable Family Members | SHOULD | PENDING | M | US-2.3 | Owner can revoke/restore access; transactions remain (audit trail preserved); disabled members see no data |

**Acceptance Criteria (Group 2):**
- [ ] Superadmin creates family and designates owner (via email invitation)
- [ ] Owner sets password and can name the family after accepting invitation
- [ ] Owner can invite members via email
- [ ] Invited members can accept and set password (forced change on first login)
- [ ] All family members can see other members and pending invitations
- [ ] Owner can disable/enable members; disabled members are immediately logged out
- [ ] Users can switch families in-dashboard via family selector dropdown

---

## Story Group 3: Account (Bank Account) Management (Finance Foundation)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-3.1** | Create Bank Account | MUST | PENDING | M | US-2.1 (family exists) | Types: bank, savings, investment, cash; optional initial balance; all members can create |
| **US-3.2** | View All Accounts | MUST | PENDING | S | US-3.1 | Show all family accounts with current balances; sortable by type/balance; calculated from transactions |
| **US-3.3** | Edit Account | SHOULD | PENDING | S | US-3.2 | Update account name and type; changes reflected across family; deferred to v1.1 if time-constrained |

**Acceptance Criteria (Group 3):**
- [ ] User can create account with name, type (bank/savings/investment/cash), and optional initial balance
- [ ] Account appears in account list visible to all family members
- [ ] Account balance calculated from non-disabled transactions
- [ ] User can edit account name and type (changes reflected for all members)
- [ ] Account type influences transaction category defaults (e.g., investment account shows investment categories)

---

## Story Group 4: Categories & Transaction Setup (Transaction Foundation)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-4.1** | View Default Categories | MUST | PENDING | S | US-2.1 (on family creation) | Pre-populate on family creation: Income (Salary, Bonus, Other), Expense (Groceries, Utilities, Entertainment, Transportation, Healthcare, Cash Withdrawal, Other), Investment (Stocks, Bonds, Real Estate, Other) |
| **US-4.2** | Create Custom Category | SHOULD | PENDING | M | US-4.1, owner role | Owner can add categories; custom categories family-scoped; default categories immutable |

**Acceptance Criteria (Group 4):**
- [ ] Default categories pre-populated when family is created
- [ ] All members can view available categories (income, expense, investment)
- [ ] Owner can create custom categories
- [ ] Categories are family-scoped (not shared across families)
- [ ] Default categories cannot be deleted (immutable protection)

---

## Story Group 5: Transaction Recording & Lifecycle (Core Business Logic)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-5.1** | Record Income Transaction | MUST | PENDING | M | US-3.1, US-4.1 | Log salary, bonus, gifts; all members can record; amount > 0 validation |
| **US-5.2** | Record Expense Transaction | MUST | PENDING | M | US-3.1, US-4.1 | Log expenses, including "Cash Withdrawal" as simple category; permit overdraft |
| **US-5.3** | Record Investment Transaction | SHOULD | PENDING | M | US-3.1, US-4.1 | Log investment purchases; can include optional dates in future; deferred to v1.1 if time-constrained |
| **US-5.4** | Edit Transaction | MUST | PENDING | M | US-5.1/5.2 | All members can edit any transaction; edit history tracked (who, when, before/after snapshot) |
| **US-5.5** | Disable/Restore Transaction | SHOULD | PENDING | M | US-5.4 | Members can soft-delete (disable); disabled txns excluded from P&L; only owner can hard-delete; deferred to v1.1 if time-constrained |

**Acceptance Criteria (Group 5):**
- [ ] User can record income with amount, date, category, account, optional description
- [ ] User can record expense with amount, date, category, account, optional description
- [ ] Amount must be > 0; date can be future-dated
- [ ] Cash withdrawal is a standard expense category (no detailed sub-tracking)
- [ ] All family members can view all transactions (full transparency)
- [ ] All family members can edit any transaction
- [ ] Edit history shows editor, timestamp, and what changed
- [ ] Members can disable (soft-delete) transactions; disabled txns hidden from reports
- [ ] Only owner can permanently delete (hard-delete); action is irreversible
- [ ] Account balance recalculated from enabled transactions

---

## Story Group 6: Dashboard & Reporting (User-Facing Value)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-6.1** | View Dashboard Summary | MUST | PENDING | L | US-5.1/5.2 (txns exist) | Show total income, expenses, net balance; recent transactions; family context indicator; load < 2 sec |
| **US-6.2** | View Expense Breakdown by Category | MUST | PENDING | L | US-6.1 | Pie/bar chart with period selector (month/year/custom range); sortable by amount |
| **US-6.3** | View Income vs. Expense Trends | SHOULD | PENDING | L | US-6.1, US-6.2 | Monthly trend lines; net savings over time; custom date range; deferred to v1.1 if time-constrained |
| **US-6.4** | Export Financial Report | MUST | PENDING | L | US-6.1, report generation | CSV/PDF export; date-range filtering; includes all selected transactions with categories |

**Acceptance Criteria (Group 6):**
- [ ] Dashboard displays total income (period-selectable: month/year/all-time)
- [ ] Dashboard displays total expenses
- [ ] Dashboard displays net savings (income - expenses)
- [ ] Dashboard shows account balances by account
- [ ] Dashboard shows recent transaction history (last 5-10 txns)
- [ ] Dashboard loads in < 2 seconds
- [ ] Expense breakdown shows pie/bar chart by category
- [ ] Period selector allows month, year, or custom range
- [ ] Export function available for transactions and summaries
- [ ] Export includes date-range filtering
- [ ] Disabled transactions excluded from all reports and dashboards

---

## Story Group 7: Security & Data (Safety & Compliance)

| ID | User Story | Priority | Status | Complexity | Dependencies | Notes |
|---|---|---|---|---|---|---|
| **US-7.1** | Logout | MUST | PENDING | S | US-1.3 (login exists) | Clear session and invalidate token; redirect to login page |
| **US-7.2** | Session Timeout | COULD | PENDING | M | US-7.1, user decision | Auto-logout after inactivity; **deferred to v1.1** (MVP requires manual logout only per user requirement) |

**Acceptance Criteria (Group 7):**
- [ ] User can click "Logout" button
- [ ] Session is immediately terminated
- [ ] User redirected to login page
- [ ] Session cookie/JWT invalidated
- [ ] User cannot use back-button to access authenticated page

---

## Summary: MVP Scope

### MUST Stories (v1.0 MVP Launch) — 14 stories

- **Authentication**: US-1.1, US-1.3 (2)
- **Family Management**: US-2.1, US-2.2 (2)
- **Accounts**: US-3.1, US-3.2 (2)
- **Categories**: US-4.1 (1)
- **Transactions**: US-5.1, US-5.2, US-5.4 (3)
- **Dashboard**: US-6.1, US-6.2, US-6.4 (3)
- **Security**: US-7.1 (1)

**Estimated Effort**: ~150-180 points (assuming standard estimation)  
**Timeline**: Phase 4_BUILD (Weeks 1-3)  
**Success Criteria**: All stories implemented, tested (Phase 5), and deployed (Phase 6)

### SHOULD Stories (v1.1 Polish) — 5 stories

- **Authentication**: US-1.4 (1)
- **Family Management**: US-2.3, US-2.4 (2)
- **Accounts**: US-3.3 (1)
- **Transactions**: US-5.3, US-5.5 (2)
- **Dashboard**: US-6.3 (1)

**Estimated Effort**: ~50-70 points  
**Timeline**: Post-MVP (Phase 6+ or Week 4-5)  
**Conditions**: Implement if MVP shipped on time; defer if critical bugs found

### COULD Stories (v1.2+) — 1 story

- **Security**: US-7.2 Session Timeout (1)

**Deferred to v1.1+**: User requirement specifies manual logout only; auto-timeout not needed for MVP

### WON'T Stories (v2.0+)

- Bill splitting (person-to-person expense tracking)
- Receipt attachments
- Bank API auto-import
- Multi-currency support
- AI auto-categorization
- Recurring transactions
- Mobile native app

---

## Implementation Sequencing (Recommended Order)

### Milestone 1: Auth & Family Foundation (Unblocks everything else)
1. **US-1.1** → Superadmin bootstrap (BE)
2. **US-1.2** → Email invitations (BE + DELIVERY for email service setup)
3. **US-1.3** → User login + family selector (BE + FE)
4. **US-2.1** → Create family (BE + FE)
5. **US-2.2** → Add members (BE)

**Duration**: ~2 weeks  
**Blockers**: Email service (SMTP/SendGrid/etc.) must be configured early

### Milestone 2: Finance & Transactions (Core value delivery)
6. **US-3.1** → Create bank account (BE + FE)
7. **US-3.2** → View accounts (BE + FE)
8. **US-4.1** → Seed default categories (BE)
9. **US-5.1** → Record income transactions (BE + FE)
10. **US-5.2** → Record expense transactions (BE + FE)
11. **US-5.4** → Edit transactions (BE + FE)

**Duration**: ~2 weeks  
**Dependencies**: Milestone 1 complete

### Milestone 3: Dashboard & Analytics (User-facing value)
12. **US-6.1** → Dashboard summary (FE + BE)
13. **US-6.2** → Expense breakdown by category (FE + BE)
14. **US-6.4** → Export reports (BE + FE)
15. **US-7.1** → Logout (BE + FE)

**Duration**: ~1 week  
**Dependencies**: Milestone 2 complete; transactions exist

### Milestone 4: Polish & Optional (Post-MVP)
16. **US-1.4** → Password reset (BE + FE)
17. **US-2.3** → View family members (BE + FE)
18. **US-2.4** → Disable members (BE + FE)
19. **US-3.3** → Edit accounts (BE + FE)
20. **US-4.2** → Custom categories (BE + FE)
21. **US-5.3** → Investment transactions (BE + FE)
22. **US-5.5** → Disable transactions (BE + FE)
23. **US-6.3** → Income vs. Expense trends (FE + BE)

**Duration**: ~1-2 weeks (v1.1+)  
**Dependencies**: v1.0 MVP shipped

---

## Key Constraints & Decisions

1. **Email Invitations**: US-1.2 requires email service (SMTP, SendGrid, etc.); **MUST be configured before Phase 4_BUILD starts**
2. **Session Management**: User requirement = NO automatic timeout; manual logout only (US-7.1). Auto-timeout deferred to v1.1.
3. **Account-Centric Model**: All transactions track which account funds come from, NOT person-to-person splitting (v2.0+ feature)
4. **Full Transparency**: All family members see all transactions; no privacy/access restrictions within family (design decision per user)
5. **Role-Based Access**: Superadmin → Family Owner → Family Member; only owners can create families, manage members, hard-delete transactions
6. **Edit Audit Trail**: Every transaction edit tracked with editor, timestamp, before/after snapshot (compliance requirement)
7. **Soft-Delete Pattern**: Members disable (soft-delete); disabled txns excluded from P&L; only owner can hard-delete
8. **Performance Target**: Dashboard < 2 seconds; requires query optimization, pagination for large transaction lists

---

## Dependency Map

```
Milestone 1 (Auth & Family)
├─ US-1.1 (Superadmin bootstrap)
├─ US-1.2 (Email invitations) [blocks family invites]
├─ US-1.3 (Login) [blocks all user flows]
├─ US-2.1 (Create family) [blocks account/transaction recording]
└─ US-2.2 (Add members) [blocks member workflows]
   │
   └──────────────────────┐
                          │
Milestone 2 (Finance)     │
├─ US-3.1 (Create account)├─ blocks transaction recording
├─ US-3.2 (View accounts)
├─ US-4.1 (Default categories) [blocks transaction creation]
├─ US-5.1 (Income)
├─ US-5.2 (Expense)
└─ US-5.4 (Edit)
   │
   └──────────────────────┐
                          │
Milestone 3 (Dashboard)   │
├─ US-6.1 (Dashboard)     ├─ blocks analytics
├─ US-6.2 (Breakdown)
├─ US-6.4 (Export)
└─ US-7.1 (Logout)

Milestone 4 (Polish) — All of the above must complete first
├─ US-1.4 (Password reset)
├─ US-2.3 (View members)
├─ US-2.4 (Disable members)
├─ US-3.3 (Edit accounts)
├─ US-4.2 (Custom categories)
├─ US-5.3 (Investment)
├─ US-5.5 (Disable transaction)
└─ US-6.3 (Trends)
```

---

## References

- **Full story details**: See `docs/business/USER_STORIES.md` (28 detailed user stories with edge cases and AC)
- **Product requirements**: See `docs/product/PRD.md` (vision, features, acceptance criteria)
- **UX flows**: See `docs/product/UX_FLOW.md` (wireflows and navigation)
- **Architecture**: See `docs/architecture/SOLUTION_ARCHITECTURE.md` (API contract, database schema)
- **Roadmap**: See `docs/product/ROADMAP.md` (v1.0/1.1/1.2/2.0 phases and timeline)

---

## Next Steps (Phase 3_IMPLEMENTATION_PLANNING)

1. **BE**: Break down MUST stories into detailed backend tasks (API endpoints, DB schema, validation)
2. **FE**: Break down MUST stories into detailed frontend tasks (pages, components, forms, state mgmt)
3. **QA**: Write test plan (unit, integration, E2E test cases for all MUST stories)
4. **DELIVERY**: Prepare docker-compose, deployment script, env vars
5. **SA**: Confirm API contract details and finalize OpenAPI spec

**Gate Before Phase 4_BUILD**: All MUST stories must have clear AC, dependencies resolved, team alignment confirmed.

