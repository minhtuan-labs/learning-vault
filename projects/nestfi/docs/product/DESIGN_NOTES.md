# Design Notes — NestFi Family Financial Management

**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** UX  

---

## Design Philosophy

NestFi is designed around three core principles:

1. **Simplicity:** Families should add transactions and members with minimal friction (5 fields, 2 clicks).
2. **Transparency:** Real-time shared visibility into household finances builds trust and enables informed decisions.
3. **Collaboration:** The UI is designed for *team* (family) management, not individual personal finance tracking.

### Why These Principles Matter

- **Simplicity** addresses the primary user pain point: families currently use spreadsheets or multiple disconnected apps because centralized solutions are too complex for casual household use.
- **Transparency** differentiates NestFi from personal budgeting apps (e.g., Mint, YNAB) by emphasizing shared data and real-time updates.
- **Collaboration** ensures the product feels like a family tool, not a surveillance system or individual tracker.

---

## Design Decisions & Rationale

### 1. Transaction Form: Lightweight vs. Comprehensive

**Decision:** 5-field transaction form (type, category, amount, date, notes) with member auto-populated.

**Why:**
- Competing apps (Mint, Splitwise) require 6+ fields or multi-screen flows, which creates friction.
- Households log transactions opportunistically (at checkout, during meal prep) — fast entry is critical.
- Optional fields (notes, date picker) enable power users without burdening casual users.

**Trade-off:**
- Bank account assignment deferred to v2 (simplifies this phase; can be added as optional step later).
- Tags / splitting deferred to v2 (align with "bill splitting" nice-to-have).

**Frontend note:** Consider auto-focus on amount field (pre-populated type/category can be sensible defaults).

---

### 2. Category Management: Family-Owned Customization

**Decision:** Categories are owned by family (not per-member). Owner manages; all members see the same taxonomy.

**Why:**
- Families need a shared categorization scheme to enable meaningful analysis (e.g., "Groceries" must mean the same thing to every member).
- Giving individual members custom categories creates data inconsistency.
- Owner curation ensures only used categories remain (reduces cognitive load for members).

**Implementation:**
- System provides sensible defaults: Groceries, Utilities, Entertainment, Transport, Other (income side: Salary, Freelance, Bonus, Other).
- Owner can add, rename, archive (not delete, to preserve history).
- Cash Withdrawal is a system category (always present, not deletable).

**Frontend note:** Category dropdown should be a typeahead (search as you type) if 10+ categories exist.

---

### 3. Real-Time Updates: Polling vs. WebSocket

**Decision:** Dashboard auto-refreshes every 10 seconds (polling); configurable per family.

**Why:**
- WebSocket adds infrastructure complexity; polling works for "small" families (2–50 members, reasonable transaction volume).
- 10s refresh balances freshness with server load; most users don't need <5s reactivity.
- Polling survives network interruptions better; easier to implement and debug.

**Future (v2):** Consider WebSocket as opt-in for power users or high-activity families.

**Backend note:** Implement efficient delta queries (only send transactions added since last refresh).

---

### 4. Multi-Family Navigation: Always Visible, Never Forced

**Decision:** Family selector is a dropdown in header (not a separate screen). Users can switch instantly without re-login.

**Why:**
- User research (Splitwise, Honeydue) shows users with multiple groups/families switch 1–3 times per session.
- A separate "Choose Family" page adds friction; header dropdown is discoverable and fast.
- No re-login required (persistent auth token) matches user mental model: "I'm logged in; let me switch contexts."

**Trade-off:**
- Requires clear visual indicator of current family (name + avatar/color).
- Permissions reset when switching families (important for security; frontend must handle gracefully).

**Frontend note:** When switching families, show loading state; invalidate cached data from previous family.

---

### 5. Permission Model: Three Tiers (Superadmin, Owner, Member)

**Decision:** Three roles with clear, enforced boundaries.

| Role | Manage Members? | Manage Categories? | Add Transactions? | Edit Own Txn? | Edit Others' Txn? | View Analytics? |
|---|---|---|---|---|---|---|
| **Superadmin** | Create families | — | — | — | — | — |
| **Owner** | Yes (invite/remove) | Yes | Yes | Yes | Yes (any) | Yes |
| **Member (Editor)** | No | No | Yes | Yes (own) | No | Yes |
| **Member (Viewer)** | No | No | No | No | No | Yes |

**Why:**
- Superadmin is a system role (not a family member); separates platform admin from family admin.
- Owner clearly owns family data and configuration; can recover from accidental member removal.
- Two member tiers address the "shared access but limited authority" use case (e.g., teenage family members can log transactions but not delete others').

**Trade-off:**
- Member-to-Owner transfer not supported in v1 (can be added later); only Superadmin can change.
- Invite-accept workflow adds latency vs. direct owner invitation, but provides security (email verification).

**Frontend note:** UI must reflect permissions; hide "delete" and "edit" buttons for unauthorized users.

---

### 6. Dashboard Layout: Metrics First, Trends Second

**Decision:** Summary cards (KPIs) at top, then category breakdown chart, then monthly trend chart, then transaction ledger.

**Why:**
- F-shaped reading pattern: users scan top-left → down left edge → across bottom.
- KPIs answer the primary question: "How much did we spend this month?"
- Category breakdown immediately shows "where did the money go?"
- Trends reveal patterns (useful for planning).
- Ledger is present but not the focal point (detailed view available via "View All").

**Order rationale:**
1. KPIs: Answer the immediate question.
2. Category breakdown: Show the composition.
3. Trends: Show history and patterns.
4. Ledger: Show details.

**Mobile adaptation:** Stack vertically; keep KPI cards prominent; collapse chart details into toggles.

---

### 7. Onboarding Flow: Email-First Verification

**Decision:** Superadmin invites owner via email → owner accepts link → owner verifies email → owner creates account.

**Why:**
- Email verification confirms identity without SMS (avoids phone dependency; international-friendly).
- Token-based invites (7-day expiry) balance security with usability.
- Two-step verification (email + password) is industry standard for financial apps.

**Trade-off:**
- Slower onboarding than "sign up directly" (adds 1–2 steps).
- Requires email service (SES, SendGrid, etc.); adds operational cost.
- Mitigates: impersonation, accidental family creation, spam account creation.

**Backend note:** Implement token expiry, resend logic, and audit logging for security.

---

### 8. Category Colors & Icons: Visual Consistency

**Decision:** Each category has an emoji/icon and color. Colors consistent across family (not per-member customization).

**Why:**
- Emojis are universally recognizable and don't require translation.
- Colors enable quick scanning of transaction ledger and charts.
- Consistent colors across all members prevent confusion ("did they mean green Utilities or my green Utilities?").

**Pre-set palette (v1):**
- Groceries: 🛒 Green
- Utilities: 💡 Blue
- Entertainment: 🎬 Purple
- Transport: 🚗 Orange
- Dining Out: 🍽 Red
- Other: ❓ Gray
- Income (Salary): 💰 Green
- Cash Withdrawal: 💸 Gray (system, not customizable)

**Frontend note:** Use a consistent color palette across charts, transaction rows, and category list for brand cohesion.

---

## Accessibility & Inclusive Design

### WCAG 2.1 AA Compliance (Target)

NestFi targets **WCAG 2.1 AA** compliance for all screens in v1. Key practices:

#### 1. Color Contrast
- **Text:** Minimum 4.5:1 contrast ratio (normal) or 3:1 (large text).
- **UI components:** Minimum 3:1 contrast ratio.
- **Charts:** Use patterns or textures in addition to colors (colorblind-friendly).

**Example:** Spending breakdown pie chart should use:
- Green for income
- Red for expenses
- Diagonal stripes / patterns within slices for additional distinction

#### 2. Keyboard Navigation
- All interactive elements (buttons, dropdowns, form fields) must be accessible via Tab key.
- Logical tab order: top-to-bottom, left-to-right.
- Focus indicator must be visible (minimum 2px border or outline).
- No keyboard trap: users can always escape from any element.

**Implementation checklist:**
- [ ] Login form: email → password → remember me → sign in button
- [ ] Dashboard: + Log Txn → filters → charts → transaction list
- [ ] Settings: tabs → form fields → save/cancel buttons

#### 3. Screen Reader Support
- **Images:** All images have alt text (e.g., family avatar: "The Smiths family logo").
- **Icons:** Icon buttons have aria-label (e.g., "+ Log Transaction" button).
- **Form labels:** Each input has associated `<label>` element or aria-label.
- **Dynamic content:** Use aria-live regions for real-time updates (e.g., "Transaction added" notification).
- **Charts:** Provide text summary or data table fallback (users should understand chart content via screen reader).

**Example for a spending pie chart:**
```html
<div role="img" aria-label="Spending breakdown: Groceries 33%, Utilities 22%, Entertainment 17%, Transport 14%, Other 14%">
  <svg><!-- chart SVG --></svg>
</div>
```

#### 4. Form Accessibility
- **Error messages:** Clear, linked to the offending field via aria-describedby.
- **Required fields:** Marked with `required` attribute and visual indicator (not color-only).
- **Placeholders:** Should NOT be used as the only label; use `<label>` elements.

**Example:**
```html
<label for="amount">Amount (required)</label>
<input id="amount" type="number" required aria-describedby="amount-error">
<span id="amount-error" role="alert">Amount must be greater than 0</span>
```

#### 5. Motion & Animation
- Avoid auto-playing animations; let users trigger them.
- Respect `prefers-reduced-motion` media query for animations.
- Flashing content: avoid if >3 flashes per second (seizure risk).

---

### Inclusive Language

- Use clear, plain language (avoid financial jargon where possible; explain when necessary).
- Pronouns: use they/them as default or ask users for preference (future v2).
- Colors described in addition to shown (e.g., "green checkmark" not just the color).
- Avoid terms like "normal" / "abnormal"; use "expected" / "unexpected" or "typical" / "atypical" for inclusivity.

---

## Interaction Patterns

### Modals & Overlays

**Use modals for:**
- Log Transaction form (lightweight data entry)
- Invite Member form
- Confirm destructive actions (delete transaction, remove member)

**Avoid modals for:**
- Settings pages (use full-page layouts instead for complexity/screen real estate)
- Transaction ledger (use dedicated page)

**Modal UX rules:**
- Escape key closes modal (unless changes unsaved; prompt user).
- Focus trap: Tab loops within modal; returns to trigger button on close.
- Backdrop click closes modal (optional; can be disabled for critical forms).
- Loading state: disable buttons, show spinner.
- Success: close modal, show toast notification, update parent view.

### Dropdowns & Selects

**Use native HTML `<select>` for:**
- Static lists (<50 items): category dropdown, family selector
- Mobile (native select better UX than custom dropdown)

**Use custom typeahead dropdown for:**
- Large lists (50+ items): filter by member name in future v2

**Rules:**
- Label clearly associated
- Keyboard: arrow keys navigate, Enter selects
- Mouse: click to open, click to select, click outside to close
- Hover state on options

### Notifications & Toasts

**Toast notifications (bottom-right, auto-dismiss 3–5s):**
- "Transaction added" (success)
- "Transaction deleted" (with undo option)
- "Family switched to The Smiths" (info)
- "Email invitation resent" (success)

**Inline error messages (stay until user fixes):**
- Form validation errors (required field, invalid amount, etc.)
- Permission errors (e.g., "You don't have permission to delete this transaction")

**Modal alerts (require user action to close):**
- "Are you sure?" confirmation for destructive actions
- Critical errors (e.g., "Failed to save transaction; please try again")

---

## Design System Baseline (v1)

### Spacing
- Base unit: 4px
- Padding: 8px, 12px, 16px, 24px, 32px (multiples of 4)
- Margins: 16px, 24px, 32px (between sections)
- Gap (flex): 8px (tight), 12px (normal), 16px (loose)

### Border Radius
- Buttons, inputs, small cards: 4px
- Modals, large panels: 8px
- Avatars: 50% (circle)

### Shadows (Subtle, not heavy)
- Card hover: `0 2px 8px rgba(0, 0, 0, 0.08)`
- Modal background: `0 4px 16px rgba(0, 0, 0, 0.12)`
- Avoid drop shadows on text (reduces readability)

### Typography
- Font family: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` (system fonts for performance)
- Line height: 1.5 (readable; accounts for larger touch targets)
- Letter spacing: default (no letter spacing unless intentional)

### Responsive Design

**Breakpoints:**
- Mobile: <640px
- Tablet: 640px–1024px
- Desktop: >1024px

**Key changes:**
- Mobile: full-width modals, bottom-sheet for actions, hamburger nav
- Tablet: 2-column layout when needed (e.g., settings sidebar + content)
- Desktop: 3-column or wider layouts

**Testing:** Test at common sizes: 375px (iPhone), 768px (iPad), 1440px (desktop).

---

## Brand & Tone

### Brand Personality
- **Trustworthy:** Financial data requires confidence. Design conveys security (clear warnings, explicit confirmations).
- **Approachable:** Not formal or intimidating. Families should feel comfortable, not lectured.
- **Collaborative:** Emphasize "we" and "family" language. Celebrate shared financial wins (even small ones).

### Tone Examples
- ✅ "Invite a family member to get started"
- ❌ "A family unit must be created before proceeding"

- ✅ "Transaction added! You're saving together."
- ❌ "Transaction recorded."

- ✅ "You've saved $300 this month. Keep it up!"
- ❌ "Savings: $300.00"

---

## Known Design Risks & Mitigation

### Risk 1: Over-Simplified Transaction Form
**Problem:** 5-field form might not capture all use cases (shared expenses, reimbursements, bill splits).
**Mitigation:** Notes field captures context. v1 uses workaround (manual category "Shared Expense"); v2 adds bill-splitting feature.
**Acceptance criteria:** Users report ability to log 95%+ of household transactions without friction.

### Risk 2: Real-Time Update Latency
**Problem:** 10s polling feels slow if multiple members actively logging.
**Mitigation:** Toast notifications provide immediate feedback to *logging* user; other members see update within 10s. Frontend shows "updated X seconds ago" timestamp.
**Acceptance criteria:** Users report sufficient freshness in testing; v2 can upgrade to WebSocket if needed.

### Risk 3: Category Proliferation
**Problem:** Owner might create 50+ categories, causing dropdown clutter and decision fatigue.
**Mitigation:** Limit to 20 active categories per type (enforced in backend). Owner must archive or delete before adding more. Pre-set 6 categories to establish convention.
**Acceptance criteria:** User testing confirms categories are discoverable and not overwhelming.

### Risk 4: Accessibility Gaps
**Problem:** Financial domain complexity (charts, tables, permissions) can be hard to navigate for users with disabilities.
**Mitigation:** Early testing with screen reader users and keyboard-only navigation. Provide text fallback for charts. Ensure error messages are clear and linked to fields.
**Acceptance criteria:** Automated a11y scan (Axe, Lighthouse) + manual testing with assistive tech.

---

## Design Debt & Future Enhancements (v2+)

### High-Priority Enhancements
1. **Mobile app (iOS/Android):** Desktop-first v1; mobile web responsive. Native apps would improve experience.
2. **Bill splitting:** Dedicated UI for splitting expenses among members (not just manual workaround).
3. **Advanced analytics:** Trends, forecasts, budget alerts.
4. **Search:** Full-text search across transactions, family members, categories.
5. **Audit trail:** Show who edited what transaction, when (for trust & dispute resolution).

### Medium-Priority Enhancements
6. **Dark mode:** Respects `prefers-color-scheme` media query.
7. **Export:** CSV/PDF reports for families.
8. **Notifications:** Email digests, in-app alerts for spending thresholds.
9. **Member permissions granularity:** Which categories can each member see/edit (privacy for multi-generational families).

### Low-Priority Enhancements
10. **Bank integration:** Connect bank accounts for automatic transaction import.
11. **Currency support:** Multi-currency transactions with conversion.
12. **Goals tracking:** Save goals, progress tracking.

---

## Testing & Validation Plan

### Usability Testing (Pre-Launch)
- **Participants:** 5–8 target users (couples, small families)
- **Tasks:** Create family, add transaction, invite member, view analytics, switch families
- **Metrics:** Task completion rate, time to completion, error rate, SUS (System Usability Scale)
- **Target:** >80% task completion, <5 min for common workflows

### Accessibility Testing
- Automated scan: Axe, Lighthouse, WAVE
- Manual testing: Keyboard-only navigation, screen reader (NVDA, JAWS, VoiceOver)
- Participants: 2–3 users with disabilities (various impairments)

### Performance Testing
- Page load time: <2s (target)
- Transaction logging: <1s (backend latency + UI update)
- Chart rendering: <500ms for 100+ data points
- Dashboard refresh: <200ms for auto-refresh

### Browser & Device Testing
- Browsers: Chrome, Safari, Firefox (latest 2 versions)
- Devices: iPhone 12/14, iPad, Android phone (Samsung/Pixel), Desktop (Windows/Mac)

---

## Design Handoff Checklist

- [ ] Figma file created with all screens (linked in FE_PLAN.md)
- [ ] Component library documented (colors, typography, spacing, buttons, forms)
- [ ] Interaction patterns documented (modals, dropdowns, notifications, transitions)
- [ ] Accessibility guidelines reviewed with frontend team
- [ ] Responsive breakpoints confirmed with frontend
- [ ] Icon/emoji set provided (or link to Figma asset library)
- [ ] Brand guidelines (tone, voice, usage examples) shared with team
- [ ] Design review scheduled with FE before implementation starts

---

## Questions for Product & Stakeholders

1. **Cash Withdrawal category:** Should it be auto-applied, or should users manually select it each time? (Currently: user selects; can be changed based on feedback.)

2. **Member permission levels:** Is "view-only" vs "editor" sufficient, or do we need granular category-level permissions in v1? (Currently: recommend two tiers; v2 adds granularity.)

3. **Real-time update frequency:** Is 10-second refresh acceptable, or do you need faster updates? (Currently: 10s; can be tuned based on testing.)

4. **Multi-currency:** Should families be able to mix currencies (e.g., USD and VND), or enforce single currency per family? (Currently: single currency; v2 adds multi-currency.)

---

