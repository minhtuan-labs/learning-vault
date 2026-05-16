# Memory — FE

> Durable scratchpad for the **FE** pane. FE owns: frontend implementation and frontend tests.
>
> READ this file at the start of every task (alongside
> `memory/_PROJECT_STATE.md`). APPEND a dated entry before exiting any
> OpenCode turn. See `memory/README.md` for format and discipline.

## Decisions

**2026-05-16 17:36 — Tech Stack Confirmations**
- Dash multi-page apps for routing (URL params drive state)
- Dash Bootstrap Components (dbc) as primary component library
- Tailwind CSS for styling (not CSS Modules; utility-first)
- Centralized APIClient class in `utils/api_client.py` (single source of truth)
- dcc.Store for JWT token + user object (transient session state)
- 10-second polling interval for dashboard auto-refresh (WebSocket deferred to v2)
- Fixed icon dropdown for category selection (visual picker deferred to v1.1)

**2026-05-16 17:36 — State Management Strategy**
- URL params (family_id, period) as source of truth for multi-family context
- No Redux/Zustand for v1 (dcc.Store + callbacks sufficient)
- Multi-family switching: Via navbar dropdown → GET /families → redirect to /dashboard?family_id=X
- Token persistence: localStorage (synced via dcc.Store on page load)

**2026-05-16 17:36 — Error Handling Approach**
- APIError custom exception with detail + code + status_code fields
- User-friendly message mapping (UNAUTHORIZED → "Please log in again")
- 401/403 triggers redirect to login; other errors show inline alerts

## Conventions

**2026-05-16 17:36 — File & Directory Organization**
- Pages: `pages/0_login.py`, `1_family_selector.py`, `2_dashboard.py`, `3_ledger.py`, `4_settings.py`, `5_invitation.py`
- Components: `components/navbar.py`, `modals.py`, `charts.py`, `forms.py`, `alerts.py`
- Utils: `utils/api_client.py` (main API abstraction)
- Assets: `assets/tailwind.config.js`, `assets/custom.css`

**2026-05-16 17:36 — Naming Conventions**
- Callbacks: snake_case with action verb (e.g., `log_transaction`, `switch_family`)
- Components: CamelCase functions that return Dash layout (e.g., `create_navbar`, `create_dashboard_summary_cards`)
- Store IDs: kebab-case (e.g., `auth-token-store`, `selected-family-id`)
- CSS classes: Tailwind utility classes + `.custom-*` for custom overrides

**2026-05-16 17:36 — API Error Handling Pattern**
All API calls wrapped in try/except for APIError:
1. Catch APIError → check status_code
2. If 401/403 → redirect to login
3. Otherwise → show user-friendly message in alert
4. Log full error server-side for debugging

## Gotchas

**2026-05-16 17:36 — Multi-Family Context**
- Always validate family_id from URL before rendering page
- Never infer family context from token; always pass family_id explicitly
- Backend enforces permission check; FE trusts API 403 responses

**2026-05-16 17:36 — Token Expiry (24h)**
- No refresh token in v1; user must re-login after 24h
- 401 response → redirect to login with "session expired" message
- (Implement refresh token endpoint in v2 if needed)

**2026-05-16 17:36 — Dashboard Polling Lag**
- 10s poll interval creates ~10s stale data window
- Acceptable for household use case (not financial trading)
- Display "updated X seconds ago" indicator
- If real-time required in future, upgrade to WebSocket/SSE

## Open items I'm tracking

**2026-05-16 17:36 — Mobile Responsiveness (v1.1)**
- Tablet (iPad 768px) tested in phase 5 (testing)
- Mobile-specific CSS overrides as needed
- Full mobile redesign deferred to v1.1

**2026-05-16 17:36 — Icon Picker for Categories (v1.1)**
- Currently: Fixed dropdown list of 12-15 common icons
- Future: Visual icon picker library (if business demands)

**2026-05-16 17:36 — Large Transaction Lists (v1.1)**
- Server-side pagination (20-50 per page) sufficient for v1
- Virtual scrolling or infinite scroll in v1.1 if performance needed
