# Open Questions — Phase 0_DISCOVERY

These questions require user/stakeholder clarification before proceeding to detailed design and implementation.

## Priority: BLOCKING (Must answer before proceeding to Phase 1)

### Q1: MVP Feature Scope — Bill Splitting
**Context**: PRODUCT_IDEA mentions "tách bill cho cặp vợ chồng" (bill splitting for couples), but user clarified that v1 focuses on **account-centric tracking** (which account money comes from) rather than person-to-person splitting.

**Question**: Should bill splitting be in MVP (v1.0) or deferred to v2.0?

**Decision**: ✅ **DECIDED — Deferred to v2.0**

**Rationale**: 
- V1 focus is on account-centric household tracking (track which account money comes from)
- Bill splitting (person-to-person expense sharing) is a post-MVP feature
- Faster MVP delivery with core tracking; bill-splitting can be added as advanced feature

**Impact**: 
- MVP scope remains lean; focus on core transaction tracking and account management
- Bill-splitting will be addressed in v2.0 roadmap

---

### Q2: Superadmin Password Management
**Context**: Default superadmin credentials are hardcoded in spec (admin123). 

**Question**: Should the default password be forced to change on first login, or is it okay for users to keep it?

**Options**:
1. **Force change**: More secure; better for production
2. **Allow optional change**: Simpler UX; assume private/internal use
3. **Other**: Different security model?

**Impact**: 
- Option 1: Better security posture, 1-2 days dev effort
- Option 2: Faster time-to-MVP

**Decision**: ✅ **DECIDED — Force password change on first login (for superadmin, owner, and all users)**

**Rationale**:
- Better security posture for household financial data
- Applies to superadmin on system initialization
- Applies to new owners and members when they first accept invitations
- Ensures users set a strong password before accessing family finances

**Impact**: 
- All new users must set their own password on first login
- Medium complexity in authentication flow (1-2 days dev effort)
- Better security for MVP release

---

### Q3: Multi-Family Dashboard Experience
**Context**: Users can belong to multiple families and select on login.

**Question**: What should happen when a user logs in if they belong to multiple families?

**Options**:
1. **Selection prompt**: Show a family selector before main dashboard
2. **Default family**: Auto-load the last family accessed
3. **Family switcher in dashboard**: Load one family by default, offer quick-switch dropdown
4. **Separate dashboards**: Show combined view of all families' finances

**Impact**:
- Option 1: Explicit but slower UX
- Option 2/3: Faster, but risk selecting wrong family
- Option 4: Complex analytics, not in MVP scope

**Decision**: ✅ **DECIDED — Family selector at login + family switcher in dashboard (Options 1 & 3 combined)**

**Rationale**:
- Show family selector prompt at login for explicit selection (no accidental wrong family access)
- Also provide in-dashboard family switcher for quick context switching
- Explicit control while maintaining fast UX for repeated access
- Aligns with account-centric design: families are the primary scope

**Impact**: 
- Login flow adds family selection step (users can switch families anytime)
- Dashboard includes family context switcher (quick toggle)
- Better safety + usability for multi-family users

---

## Priority: HIGH (Should clarify before Phase 2 Backlog)

### Q4: Transaction Categories — Flexibility
**Context**: MVP mentions predefined categories (salary, groceries, utilities, etc.).

**Question**: Should users be able to create custom categories, or only use predefined ones?

**Options**:
1. **Predefined only**: Simpler schema, better for analytics consistency
2. **Custom categories**: More flexibility, harder to aggregate analytics
3. **Hybrid**: Predefined + custom allowed, but analytics focus on predefined

**Impact**:
- Option 1: Simpler, but users frustrated by limited categories
- Option 2: Feature creep, but better UX
- Option 3: Best compromise, medium complexity

**Decision**: _[PENDING USER INPUT]_

---

### Q5: Investment Tracking Detail
**Context**: PRODUCT_IDEA mentions "các loại đầu tư" (investment types) but no detail on tracking requirements.

**Question**: What should be tracked for investments?

**Options**:
1. **Simple list**: Just record investment type, amount, date (like transactions)
2. **Portfolio view**: Track cost basis, current value, gains/losses
3. **Advanced**: Include dividend tracking, rebalancing, asset allocation

**Impact**:
- Option 1: Simple MVP, easy to implement
- Option 2: More valuable analytics, medium complexity
- Option 3: Significantly more complex, deferred to v2.0

**Decision**: _[PENDING USER INPUT]_

---

### Q6: Cash Withdrawal Handling
**Context**: User clarified that cash withdrawal = single spending transaction (not detailed sub-tracking). Focus is on which account money comes from.

**Question**: Should cash withdrawals just be a transaction entry, or should there be subsequent tracking of how the cash was spent?

**Decision**: ✅ **DECIDED — One-time entry**

**Rationale**: 
- Cash withdrawals are treated as simple "Rút Cash" transactions
- No sub-tracking of how cash is spent (to keep MVP lean and account-centric)
- User can categorize the withdrawal as "Cash" expense category

**Impact**: 
- Simpler data model and UI
- MVP remains focused on account-based tracking, not individual cash spending details

---

### Q7: Data Ownership & Privacy
**Context**: Multiple family members have access to shared financial data. Per account-centric design, NestFi tracks accounts (not people), so all family members have equal access to the family's financial information.

**Question**: Should all family members see all transactions, or should there be per-member visibility controls?

**Options**:
1. **Full transparency**: Everyone sees all transactions
2. **Role-based**: Different roles (owner/member) see different data
3. **Privacy controls**: Members can mark transactions as private

**Decision**: ✅ **DECIDED — Full Transparency (Option 1)**

**Rationale**:
- Account-centric design: Transactions belong to accounts (not to people)
- BUSINESS_REQUIREMENTS state family members have "Full access to family financial data"
- No person-level spending tracking (all members are equal in v1)
- Simpler implementation, clearer audit trail

**Impact**:
- All family members see all transactions in all family accounts
- Transparency enables better collective financial decision-making
- No privacy controls per transaction in v1 (can be added in v2.0)

---

## Priority: MEDIUM (Nice-to-clarify, can decide internally)

### Q8: Reporting & Export Features
**Question**: Should the dashboard include export/reporting features in v1.0 MVP?

**Decision**: ✅ **DECIDED — Yes, include export reports in v1.0**

**Rationale**:
- Families want the ability to export financial reports for budgeting, tax prep, or external sharing
- Core feature that adds significant value without major complexity (CSV/PDF export)
- Can be implemented alongside dashboard analytics

**Impact**: 
- Dashboard includes export button/menu for reports (CSV/PDF formats)
- Exports include transaction lists, category breakdowns, income/expense summaries
- Report generation added to Phase 4 BUILD

---

### Q9: Transaction Approval Workflow
**Question**: Should family transactions require approval from owner before posting, or are they visible immediately?

**Decision** (PM discretion): Immediate visibility for MVP; optional approval workflow in v2.0.

---

### Q10: Reporting Frequency
**Question**: What reporting/notification frequency should families expect (weekly summary, monthly report, alerts)?

**Decision** (PM discretion): No automated reports in MVP; on-demand dashboard. Automated reports in v1.1.

---

## Summary

- **DECIDED (User clarification received)**: 
  - ✅ Q1 (bill-splitting deferred to v2.0)
  - ✅ Q2 (force password change on first login for all users)
  - ✅ Q3 (family selector at login + in-dashboard switcher)
  - ✅ Q6 (cash withdrawal one-time entry)
  - ✅ Q7 (full transparency on transactions)
  - ✅ Q8 (include export reports in v1.0)
  - ✅ Additional: Session timeout = NEVER (manual logout only)

- **High priority (Stakeholder input wanted)**: Q4 (custom categories), Q5 (investment tracking detail)
- **Medium priority (PM can decide)**: Q9 (transaction approval workflow), Q10 (reporting frequency)

**Next step**: Phase 0_DISCOVERY complete. All blocking user decisions resolved. Ready to advance to Phase 1_SOLUTION_DESIGN with SA/UX for architecture & detailed design.
