# Open Questions — NestFi

**Product:** NestFi - Family Financial Management Platform  
**Last Updated:** 2026-05-16  
**Owner:** PM  

---

## Questions Requiring User Input

These items should be clarified with the user before advancing to Phase 1_SOLUTION_DESIGN.

### Q1: Multi-Currency Support — v1 vs v1.2+

**Question:**  
Should NestFi support families with multiple currencies in v1? For example, a family with income in USD and expenses in VND (Vietnamese Dong).

**Context:**
- MVP assumes single currency per family (simplifies data model and UI)
- Multi-currency would require: currency selection on categories, conversion rates, multiple currency displays
- Impacts: database schema, calculation logic, dashboard complexity

**Options:**
1. **Single currency per family (MVP):** Each family picks one currency; all transactions in that currency. Multi-currency deferred to v1.2+.
2. **Multi-currency in v1:** Implement currency selection for categories/transactions; real-time conversion rates.
3. **Hybrid:** Allow multi-currency tracking but no conversion (just display each currency separately).

**PM Recommendation:** Option 1 (single currency per family) for MVP. Reduces complexity and time-to-launch.

**Decision:** Pending user input.  
**Impact if deferred:** +2-3 weeks development time; +complexity in dashboard/analytics.

---

### Q2: Bill Splitting Feature — v1 vs v1.3+

**Question:**  
Should v1 include bill-splitting logic (e.g., restaurant bill split 3 ways, automatic settlement)?

**Context:**
- MVP does not include bill splitting
- Workaround: manually log expense with category "Shared Expense" or create custom categories
- Full feature would require: transaction splitting, settlement tracking, payment requests between members
- Impacts: transaction data model, payment system integration, member-to-member transfers

**Options:**
1. **No bill splitting in v1 (MVP approach):** Manual categorization workaround. Feature v1.3+.
2. **Simple bill splitting in v1:** Can split expense among family members, no automatic settlement.
3. **Full bill splitting with settlement:** Split expenses, track IOUs, payment requests, settlements.

**PM Recommendation:** Option 1 (defer to v1.3+). Most families can manually categorize; full feature adds significant complexity.

**Decision:** Pending user input.  
**Impact if included:** +3-4 weeks; payment system integration required.

---

### Q3: Investment Portfolio Tracking Depth — v1 vs v1.2+

**Question:**  
Should v1 track detailed investment portfolio metrics (cost basis, returns, unrealized gains) or just simple category-based tracking?

**Context:**
- MVP v1: Simple tracking only (total amount by investment category, e.g., "Stock Portfolio: $10,000")
- Full feature would require: cost basis tracking, return calculations, performance metrics, tax-loss harvesting info
- Impacts: data model complexity, financial calculations, UI for portfolio details

**Options:**
1. **Simple tracking only (MVP):** Amount per category, no performance metrics.
2. **Basic metrics:** Cost basis, current value, unrealized gain/loss per investment.
3. **Advanced metrics:** Returns by holding period, tax-loss data, dividend tracking.

**PM Recommendation:** Option 1 (simple tracking in v1). Deferred metrics in v1.2+.

**Decision:** Pending user input.  
**Impact if advanced:** +2 weeks; financial calculation library required.

---

### Q4: Analytics Depth — ML Suggestions vs Manual v1

**Question:**  
Should v1 include ML-powered categorization suggestions or rely on manual categorization?

**Context:**
- MVP v1: Manual categorization only (user selects category when logging transaction)
- ML feature would: automatically suggest categories based on transaction description, learn from user corrections
- Impacts: ML infrastructure, training data, model maintenance

**Options:**
1. **Manual categorization only (MVP):** User always selects category. No ML. Simple and predictable.
2. **Suggest categories from history:** Based on past transactions, suggest most-used category for amount range.
3. **ML-powered suggestions:** Analyze description text and suggest categories; learn from user corrections over time.

**PM Recommendation:** Option 1 (manual in v1). ML features deferred to v1.2+ pending user demand.

**Decision:** Pending user input.  
**Impact if included:** +2-3 weeks; requires data science resources.

---

### Q5: Transaction Editing Permissions — Self-Only vs Owner-All

**Question:**  
Should family members only edit their own transactions, or should the owner be able to edit all members' transactions?

**Context:**
- MVP assumes: Each member can only edit/delete their own transactions; owner can edit/delete any.
- Alternative: Members can only edit own; owner cannot edit others' (more privacy-focused).
- Impacts: permission model, audit logging, data integrity controls

**Options:**
1. **Member-own + Owner-all (current MVP design):** Members edit own; owner can edit all.
2. **Member-own only:** Members edit own; owner cannot edit others (stronger privacy guarantee).
3. **Restricted to creator only:** No one, not even owner, can edit another's transaction (append-only ledger).

**PM Recommendation:** Option 1 (current MVP design). Owner needs ability to correct errors; audit logging ensures accountability.

**Decision:** Pending user input.  
**Impact if changed:** Permission model adjustment; may reduce feature set for owner.

---

## Questions for Technical Review (SA/BE)

These will be addressed during Phase 1_SOLUTION_DESIGN but are noted here for context.

### T1: Email Service Provider Selection

**For SA/BE to decide:**
- Use AWS SES, SendGrid, Mailgun, or custom SMTP?
- Cost vs reliability trade-off?
- Recommended: SendGrid (reliable, easy to integrate, $20/month starter tier).

---

### T2: Real-Time Updates Architecture

**For SA/BE to decide:**
- WebSocket (full duplex, lower latency) vs Server-Sent Events (SSE, simpler) vs polling (simplest)?
- Impacts: dashboard refresh speed, infrastructure complexity, cost.
- Recommended for MVP: Start with polling (simplest), upgrade to WebSocket if users demand <2s updates.

---

### T3: Database Technology

**For SA/BE to decide:**
- PostgreSQL (recommended for relational data, scalable), MySQL, SQLite (dev-only), or NoSQL?
- Impacts: schema design, query complexity, scaling story.
- Recommended for MVP: PostgreSQL (mature, ACID compliance, strong for financial data).

---

## Questions for Design Review (UX)

These will be addressed during Phase 2_BACKLOG_AND_SPEC.

### D1: Primary Navigation Model

**For UX to decide:**
- Sidebar nav vs top nav vs bottom nav?
- Dashboard-centric (dashboard as home) vs feature-list navigation?
- Mobile: drawer menu vs bottom tab bar?
- Recommended: Sidebar + responsive drawer for mobile (standard for web apps).

---

### D2: Category Management UX

**For UX to decide:**
- Where to place category management? (Settings → Categories vs Dashboard → Categories section?)
- How to present category selection in transaction form? (dropdown, search, recently-used?)
- Recommended: Dashboard → Settings tab for owner; recently-used + search in transaction form.

---

## Resolved Questions (History)

### RQ1: Product Idea Completeness — RESOLVED

**Question:** PRODUCT_IDEA.md was skeleton-only (headers with no content). What is the full product vision?

**User Answer (2026-05-16):** User provided complete product idea including problem, target users, core use cases, features, constraints, and success metrics. See PRODUCT_IDEA.md for full details.

**Resolution:** ✅ PRD, ROADMAP, and BACKLOG created based on provided product idea.

---

## Timeline for Resolution

| Question | Type | Priority | Target Resolution | Owner |
|---|---|---|---|---|
| Q1: Multi-currency | User | P1 | Before Phase 1_SOLUTION_DESIGN | User |
| Q2: Bill splitting | User | P2 | Before Phase 2_BACKLOG_AND_SPEC | User |
| Q3: Investment tracking | User | P2 | Before Phase 2_BACKLOG_AND_SPEC | User |
| Q4: ML categorization | User | P2 | Before Phase 2_BACKLOG_AND_SPEC | User |
| Q5: Edit permissions | User | P1 | Before Phase 1_SOLUTION_DESIGN | User |
| T1: Email provider | Technical | P0 | Phase 1_SOLUTION_DESIGN | SA/BE |
| T2: Real-time updates | Technical | P0 | Phase 1_SOLUTION_DESIGN | SA/BE |
| T3: Database tech | Technical | P0 | Phase 1_SOLUTION_DESIGN | SA/BE |
| D1: Navigation | Design | P0 | Phase 2_BACKLOG_AND_SPEC | UX |
| D2: Category management | Design | P0 | Phase 2_BACKLOG_AND_SPEC | UX |

---

## Change Log

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | PM | Created OPEN_QUESTIONS with 5 user clarifications + 5 technical/design items |

