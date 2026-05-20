# Memory — UX

> Durable scratchpad for the **UX** pane. UX owns: user journey, wireframes, design notes.
>
> READ this file at the start of every task (alongside
> `memory/_PROJECT_STATE.md`). APPEND a dated entry before exiting any
> OpenCode turn. See `memory/README.md` for format and discipline.

## Decisions

- **Navigation**: Top bar + sidebar (collapsible on mobile)
- **Family selector**: Dropdown in top navbar; persistent visibility
- **Table component**: Full-width on desktop; card-view fallback on mobile
- **Color semantics**: Green (income), Red (expense), Purple (investment), Amber (cash withdrawal)

## Conventions

- **Chart placement**: Primary visualization (pie/bar) left; data table right on desktop
- **Modal z-index**: 1000 (dropdowns: 100, alerts: 999)
- **Form validation**: Inline on blur/input; error text below field in red
- **Accessibility baseline**: WCAG AA (color contrast 4.5:1 text, focus indicators on all interactive elements)

## Gotchas

- **Multi-family data**: Must clearly show active family in top bar; easy family-switching essential
- **Transaction timestamps**: Include time if available; otherwise just date + "Today/Yesterday" labels
- **Role-based visibility**: Members and Viewers have different action sets (owner only on certain actions)

## Open items I'm tracking

- FE will need to confirm responsive breakpoints match this design's tablet/mobile assumptions
- Chart library choice (Recharts vs Chart.js) affects animated transitions
- Email template design for invitations not in scope (referenced only)

---

### 2026-05-16 21:25 — blocked on missing inputs
Waiting for PM to produce docs/product/PRD.md (needed for UX flow/wireframes). Registered file_watch for auto-resume when PRD lands.

### 2026-05-16 21:26 — UX flows, wireframes, design system complete
Created comprehensive UX_FLOW.md with 9 primary flows (setup, invitations, auth, transactions, dashboard, categories, settings, analytics, error handling). Wireframes include desktop layouts for all key screens + responsive breakpoint notes. Design system covers color palette, typography (8px grid), component specs (buttons, inputs, tables, modals), accessibility (WCAG AA target), and developer notes. Navigation pattern: top bar + collapsible sidebar; family selector in navbar.

### 2026-05-16 21:59 — UX flows refined based on business requirements & API contract
**Refinements made:**
- Added explicit Password Reset flow (Flow 1) addressing US-1.4
- Enhanced Transaction Management flows (7.4-7.6): soft-delete (Disable/Enable - all members), hard-delete (permanent - owner only), and transaction edit history view
- Added Member Management flows (8.1-8.3): disable/enable members, manage roles, resend/revoke invitations
- Added comprehensive Role-Based Access section: clarified Superadmin, Owner, Member (editor), and Viewer permissions
- Created wireframes for password reset (W1b, W1c), transaction detail with edit history (W5b), member edit modal (W9b)
- Updated Family Management wireframe (W7) to show grouped sections (Active/Disabled/Pending) with conditional actions
- Added UI Visibility & Conditional Components guidance in DESIGN_NOTES with role-based feature table and implementation code examples
- Key clarification: All members can soft-delete (disable); only owner can hard-delete (permanent). All members see transaction edit history. Members have equal edit rights (no owner-only edit restriction).
