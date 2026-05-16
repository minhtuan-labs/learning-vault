# Frontend Implementation Plan — NestFi
**Version:** 1.0  
**Last Updated:** 2026-05-16  
**Owner:** FE  
**Phase:** 3_IMPLEMENTATION_PLANNING

---

## Executive Summary

This document outlines the FE implementation plan for NestFi's Dash + Tailwind + Python stack. The frontend is organized into 6 main pages (Login, Family Selector, Dashboard, Ledger, Settings, Invitations), with reusable Dash components and a centralized API client. Multi-family switching is managed via URL parameters and app state, keeping the architecture stateless and horizontally scalable.

---

## 1. Page Structure & Routing

### 1.1 Page Hierarchy

NestFi frontend uses **Dash multi-page apps** with URL-based routing. Each page corresponds to a UX flow from `docs/product/UX_FLOW.md`.

```
frontend/
├── app/
│   ├── pages/
│   │   ├── 0_login.py              # POST /auth/login → family selector
│   │   ├── 1_family_selector.py    # GET /family-selector → dashboard (with family_id)
│   │   ├── 2_dashboard.py          # GET /dashboard?family_id=1 → main overview
│   │   ├── 3_ledger.py             # GET /ledger?family_id=1 → transaction history
│   │   ├── 4_settings.py           # GET /settings?family_id=1 → category management
│   │   ├── 5_invitation.py         # GET /accept?token=xyz → onboarding
│   │   └── error.py                # 404, 401, 403 error pages
│   ├── components/
│   │   ├── navbar.py               # Header with family switcher
│   │   ├── sidebar.py              # Navigation sidebar (optional for v1)
│   │   ├── forms.py                # Reusable form components
│   │   ├── charts.py               # Dashboard charts (pie, bar, trend)
│   │   ├── modals.py               # Transaction modal, invite modal
│   │   └── alerts.py               # Error/success/loading alerts
│   └── utils/
│       └── api_client.py           # Centralized API abstraction layer
```

### 1.2 Page Details

#### **Page 0: Login** (`pages/0_login.py`)
- **Route:** `/` (default), `/login`
- **Purpose:** Authenticate user; display superadmin panel if logged in as superadmin
- **Components:**
  - Email input
  - Password input
  - "Forgot Password?" link → password reset flow (deferred to v2)
  - "Login" button
  - Error message display (invalid credentials, etc.)
- **On Success:**
  - Store JWT token in `dcc.Store(id='auth-token-store')`
  - If user has 1 family → redirect to dashboard
  - If user has N families (N > 1) → redirect to family selector
  - If user is superadmin → show "Create Family" form (embedded or modal)
- **Data Flow:**
  - POST `/auth/login` with email + password
  - Receive: `access_token`, user object, list of families
  - Store: token in `dcc.Store`, user in `dcc.Store`

#### **Page 1: Family Selector** (`pages/1_family_selector.py`)
- **Route:** `/family-selector`
- **Purpose:** Choose which family to manage (multi-family support)
- **Components:**
  - List of family cards (name, member count, role)
  - "Create New Family" button (superadmin only)
  - Logout button
- **On Family Select:**
  - Store `family_id` in URL query param (`?family_id=1`)
  - Redirect to `/dashboard`
- **Data Flow:**
  - GET `/families` to retrieve user's families
  - Display list; on click, pass `family_id` to dashboard

#### **Page 2: Dashboard** (`pages/2_dashboard.py`)
- **Route:** `/dashboard?family_id={id}` (required param)
- **Purpose:** Main overview of household finances
- **Components:**
  - **Navbar** with:
    - Family switcher (dropdown → GET `/families` → redirect to `/dashboard?family_id=X`)
    - Member menu (view profile, logout)
  - **Summary Cards:**
    - Total Income (current month)
    - Total Expense (current month)
    - Net Savings (current month)
    - (Optional) Savings rate % 
  - **Charts:**
    - Pie chart: Category breakdown (expense) — from analytics summary
    - Bar chart: Monthly trends (last 6 months) — from analytics trends
    - Table: Recent transactions (last 10)
  - **CTA Buttons:**
    - "Log Transaction" → modal
    - "View All Transactions" → ledger page
    - "Settings" → settings page
- **Filters:**
  - Period toggle: Month / Year (URL param: `?period=month`)
  - Category filter (optional for v1)
- **Data Flow:**
  - GET `/families/{family_id}` → family info
  - GET `/families/{family_id}/analytics/summary?period=month` → summary + category breakdown
  - GET `/families/{family_id}/analytics/trends?months=6` → trend data
  - GET `/families/{family_id}/transactions?limit=10` → recent txns
- **Real-time Refresh:**
  - Use `dcc.Interval(interval=10000)` for 10s polling
  - Refresh analytics & transactions on interval
  - Show "updated X seconds ago" indicator

#### **Page 3: Ledger** (`pages/3_ledger.py`)
- **Route:** `/ledger?family_id={id}` (required param)
- **Purpose:** Full transaction history with filters & search
- **Components:**
  - **Filters (sticky header):**
    - Date range (from/to date pickers)
    - Category dropdown (multi-select)
    - Member dropdown (multi-select)
    - Type toggle (Income / Expense / All)
    - Search box (notes field)
  - **Table:**
    - Date, Member, Category, Type, Amount, Notes, Actions
    - Sortable columns (by date, amount)
    - Pagination: 20/50 per page
    - Hoverable rows → expand detail view
  - **Row Actions:**
    - Edit (if own transaction or owner)
    - Delete (if own transaction or owner) → confirmation modal
  - **Export** (deferred to v1.1, nice-to-have)
- **Data Flow:**
  - GET `/families/{family_id}/transactions?skip=0&limit=20&category_id=X&date_from=Y&date_to=Z&type=expense` → paginated list
  - PUT/DELETE transactions on edit/delete
- **Auto-refresh:** Same as dashboard (10s interval)

#### **Page 4: Settings** (`pages/4_settings.py`)
- **Route:** `/settings?family_id={id}` (required param)
- **Purpose:** Family configuration (categories, members, bank accounts)
- **Tabs:**
  - **General:** Family name, description, currency (read-only in v1)
  - **Members:** List of members, roles, invite form
  - **Income Categories:** CRUD categories (Income type)
  - **Expense Categories:** CRUD categories (Expense type)
  - **Investment Categories:** CRUD categories (Investment type)
- **Components (per tab):**
  - **Members Tab:**
    - Table: Member name, email, role, status, actions (remove)
    - "Invite Member" button → modal with email + role select
  - **Categories Tabs:**
    - Table: Category name, color, icon, active/inactive, actions (edit/delete)
    - "Add Category" button → modal with name, color picker, icon select
    - Archive (soft delete) on delete action
- **Permissions:**
  - Only owner can edit settings
  - Members can view categories
  - View-only members can only view
- **Data Flow:**
  - GET `/families/{family_id}` → family info
  - GET `/families/{family_id}/members` → member list
  - GET `/families/{family_id}/categories?type=income` (etc.) → category lists
  - POST/PUT/DELETE for all CRUD operations
  - POST `/families/{family_id}/members` → invite member
  - GET `/families/{family_id}/members` → check invitation status

#### **Page 5: Invitation Acceptance** (`pages/5_invitation.py`)
- **Route:** `/accept?token={token}` (GET param)
- **Purpose:** New user onboarding via invitation link
- **Steps:**
  1. Parse token from URL
  2. Show email (pre-filled from token metadata)
  3. Ask: "Is this your email?" with option to change
  4. Form: Full name + password (+ confirm password)
  5. Show password strength indicator
  6. Submit: POST `/invitations/{token}/accept` with full_name + password
  7. On success: Log user in, store token, redirect to dashboard
  8. On error: Show error message, offer to request new invitation
- **Data Flow:**
  - Token decoded server-side (if needed) or validated on POST
  - POST `/invitations/{token}/accept` with full_name + password
  - Receive: `access_token`, user, family info
  - Auto-login and redirect

### 1.3 Navigation Model

- **Nav hierarchy (not hierarchical; flat):**
  - Login → Family Selector → Dashboard (default)
  - Dashboard → Ledger, Settings, Logout
  - All pages (except Login) show navbar with family switcher
  - Sidebar (optional; can use horizontal nav for v1)
- **Family Switching:**
  - Via navbar dropdown: GET `/families`, display list, click → redirect to `/dashboard?family_id=X`
  - No re-login required
  - All page data re-fetches with new family_id

---

## 2. Dash Component Layout & Design

### 2.1 Component Organization

```
components/
├── navbar.py              # Persistent header, family switcher
├── sidebar.py             # (optional) collapsible nav
├── forms.py               # Reusable form fields & input groups
├── modals.py              # Transaction log, invite, confirm
├── charts.py              # Pie chart, bar chart, trends
├── alerts.py              # Success/error/loading toast or inline
└── layout_helpers.py      # Common grid/spacing utilities
```

### 2.2 Navbar Component

```python
# navbar.py

def create_navbar(user=None, current_family=None):
    """
    Sticky header with:
    - App logo + title (left)
    - Family switcher dropdown (center)
    - User menu (profile, logout) (right)
    """
    # Family dropdown with client-side callback for redirect
    # User menu with logout button
```

### 2.3 Forms

Reusable form building blocks using Dash HTML components:

- **TextInput:** Email, name, description
- **PasswordInput:** With strength meter for registration
- **NumberInput:** Amount, with formatting
- **DatePicker:** Transaction date
- **Select/Dropdown:** Category, member, type, period
- **Checkbox/Radio:** Filter options
- **Textarea:** Notes/description

### 2.4 Charts & Analytics

Using **Plotly (included with Dash)**:

- **Pie chart:** Category breakdown (expense by %)
  - Click on slice → filter ledger to that category (optional)
- **Bar chart:** Monthly income/expense/net trends
  - X-axis: Month, Y-axis: Amount
  - Stacked bars (income vs expense)
- **Table:** Recent transactions (custom Dash table with sorting)

### 2.5 Modals

Common modal components:

- **Log Transaction Modal:**
  - Type select (Income/Expense/Cash Withdrawal)
  - Category select (populated from family categories)
  - Amount input
  - Date picker (default today)
  - Notes textarea
  - Submit button
- **Invite Member Modal:**
  - Email input
  - Role select (member / view_only)
  - Message (optional)
  - Submit button
- **Confirm Delete Modal:**
  - "Are you sure?" message
  - Confirm / Cancel buttons

### 2.6 Alerts & Toasts

- **Error alerts:** Inline below form or persistent top banner
- **Success alerts:** Temporary toast (fade out after 3s)
- **Loading spinners:** During API calls (on button or full-page)
- **Implementation:** 
  - Use `dbc.Alert` (Dash Bootstrap Components) or custom HTML
  - Trigger via callback → store message in `dcc.Store`

### 2.7 Responsive Design Approach

- **Desktop first:** Layout assumes 1024px+ (dashboard primary use case)
- **Tablet friendly:** Single-column layouts for filters/settings
- **Mobile support (v1.1):** Stack components vertically
- **Dash Bootstrap Components (dbc):**
  - Use `dbc.Container`, `dbc.Row`, `dbc.Col` for grid
  - Built-in breakpoints: `lg`, `md`, `sm`, `xs`

---

## 3. Tailwind CSS Styling Strategy & Component Library

### 3.1 Tailwind Setup

```bash
# In frontend/
pip install tailwindcss  # or use npm if needed
npm install -D tailwindcss postcss autoprefixer  # OR python equivalent

# tailwind.config.js
module.exports = {
  content: [
    "./app/**/*.py",
    "./app/**/*.html",
  ],
  theme: {
    colors: {
      primary: "#2563eb",      # Blue for CTAs
      success: "#16a34a",      # Green for success
      danger: "#dc2626",       # Red for errors/delete
      warning: "#ea580c",      # Orange for warnings
      neutral: "#6b7280",      # Gray
      light: "#f3f4f6",        # Off-white for backgrounds
    },
  },
}
```

### 3.2 Tailwind + Dash Styling

Tailwind generates `dist/styles.css` → link in Dash layout:

```python
# main.py
external_stylesheets = [
    'assets/dist/styles.css',  # Tailwind
    'assets/custom.css',       # Dash-specific overrides
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
```

### 3.3 Component Library

Use **Dash Bootstrap Components (dbc)** as primary component library:

- **Buttons:** `dbc.Button` with Tailwind classes
- **Cards:** `dbc.Card` for summary cards, member cards
- **Forms:** `dbc.Form`, `dbc.FormGroup`, `dbc.FormFloating`
- **Modals:** `dbc.Modal`
- **Alerts:** `dbc.Alert`
- **Tables:** `dash.dash_table.DataTable` (or custom with `dbc.Table`)
- **Input:** `dbc.Input`, `dcc.Dropdown`, `dcc.DatePickerSingle`
- **Dropdowns:** `dbc.DropdownMenu` (navbar user menu)

### 3.4 Color & Spacing System

```python
# assets/tailwind.css (generated)

# Color usage:
# - Primary (blue): Buttons, active nav, highlights
# - Success (green): Confirmation, savings, positive deltas
# - Danger (red): Errors, delete actions, negative numbers
# - Neutral (gray): Text, dividers, inactive elements
# - Light (off-white): Card/modal backgrounds

# Spacing (Tailwind defaults):
# 4px (scale 1), 8px (2), 12px (3), 16px (4), 24px (6), 32px (8)

# Typography:
# Heading 1 (h1): 32px, bold, primary color
# Heading 2 (h2): 24px, bold, neutral
# Body: 14-16px, neutral
# Small: 12px, gray, for dates/times
```

### 3.5 Dark Mode (Deferred)

Tailwind dark mode can be added in v1.1 with `dark:` prefix classes. For v1, use light mode only.

---

## 4. API Client Abstraction & Error Handling

### 4.1 Centralized API Client

```python
# utils/api_client.py

class APIClient:
    """
    Centralized API client for all FastAPI endpoints.
    Handles:
    - Base URL configuration
    - JWT token injection
    - Request/response logging
    - Error parsing & transformation
    - Automatic retry on 401 (token expiry)
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def set_token(self, token: str):
        """Set JWT token for all subsequent requests."""
        self.session.headers["Authorization"] = f"Bearer {token}"
    
    def clear_token(self):
        """Clear token (on logout)."""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Internal request handler:
        - Raises APIError on non-2xx (parsed from response)
        - Logs request/response (debug mode)
        - Handles connection errors
        """
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.HTTPError as e:
            # Parse error from response
            detail = e.response.json().get("detail", str(e))
            code = e.response.json().get("code", "UNKNOWN")
            raise APIError(detail=detail, code=code, status_code=e.response.status_code)
        except requests.RequestException as e:
            raise APIError(detail="Network error", code="NETWORK_ERROR")
    
    # Endpoint methods (for each API route)
    def login(self, email: str, password: str) -> dict:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})
    
    def get_families(self) -> dict:
        return self._request("GET", "/families")
    
    def get_family(self, family_id: int) -> dict:
        return self._request("GET", f"/families/{family_id}")
    
    def get_analytics_summary(self, family_id: int, period: str = "month", date: str = None) -> dict:
        params = {"period": period}
        if date:
            params["date"] = date
        return self._request("GET", f"/families/{family_id}/analytics/summary", params=params)
    
    def get_transactions(self, family_id: int, skip: int = 0, limit: int = 30, **filters) -> dict:
        params = {"skip": skip, "limit": limit}
        params.update(filters)  # category_id, date_from, type, etc.
        return self._request("GET", f"/families/{family_id}/transactions", params=params)
    
    def create_transaction(self, family_id: int, data: dict) -> dict:
        return self._request("POST", f"/families/{family_id}/transactions", json=data)
    
    def update_transaction(self, family_id: int, txn_id: int, data: dict) -> dict:
        return self._request("PUT", f"/families/{family_id}/transactions/{txn_id}", json=data)
    
    def delete_transaction(self, family_id: int, txn_id: int) -> None:
        self._request("DELETE", f"/families/{family_id}/transactions/{txn_id}")
    
    def get_categories(self, family_id: int, category_type: str = None, active_only: bool = False) -> dict:
        params = {}
        if category_type:
            params["type"] = category_type
        if active_only:
            params["active_only"] = True
        return self._request("GET", f"/families/{family_id}/categories", params=params)
    
    def create_category(self, family_id: int, data: dict) -> dict:
        return self._request("POST", f"/families/{family_id}/categories", json=data)
    
    def update_category(self, family_id: int, cat_id: int, data: dict) -> dict:
        return self._request("PUT", f"/families/{family_id}/categories/{cat_id}", json=data)
    
    def delete_category(self, family_id: int, cat_id: int) -> None:
        self._request("DELETE", f"/families/{family_id}/categories/{cat_id}")
    
    def invite_member(self, family_id: int, data: dict) -> dict:
        return self._request("POST", f"/families/{family_id}/members", json=data)
    
    def get_members(self, family_id: int) -> dict:
        return self._request("GET", f"/families/{family_id}/members")
    
    def accept_invitation(self, token: str, data: dict) -> dict:
        return self._request("POST", f"/invitations/{token}/accept", json=data)


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, detail: str, code: str, status_code: int = None):
        self.detail = detail
        self.code = code
        self.status_code = status_code
    
    def is_auth_error(self) -> bool:
        return self.status_code in (401, 403)
    
    def user_message(self) -> str:
        """Return user-friendly error message."""
        messages = {
            "UNAUTHORIZED": "Please log in again.",
            "FORBIDDEN": "You don't have permission to do this.",
            "NOT_FOUND": "This item doesn't exist.",
            "CONFLICT": "This already exists. Try something else.",
            "NETWORK_ERROR": "Network error. Please check your connection.",
        }
        return messages.get(self.code, self.detail)
```

### 4.2 Global API Client Instance

```python
# main.py

# Create singleton client
api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))

# Inject into app (make accessible to callbacks)
app.api_client = api_client
```

### 4.3 Error Handling in Callbacks

Callbacks use try/except to catch `APIError` and display to user:

```python
@app.callback(
    [Output('alert', 'children'), Output('alert', 'is_open')],
    [Input('log-txn-btn', 'n_clicks')],
    [State('txn-amount', 'value'), ...],
)
def log_transaction(n_clicks, amount, ...):
    if not n_clicks:
        raise PreventUpdate
    
    try:
        # Get family_id from URL or app state
        family_id = get_family_id_from_url()
        
        data = {
            "type": txn_type,
            "category_id": category_id,
            "amount": amount,
            "description": notes,
            "transaction_date": txn_date,
        }
        
        result = app.api_client.create_transaction(family_id, data)
        
        # Success: return success message, refresh data
        return dbc.Alert("Transaction logged!", color="success"), True
        
    except APIError as e:
        return dbc.Alert(e.user_message(), color="danger"), True
```

---

## 5. State Management & Multi-Family Switching

### 5.1 State Storage Strategy

Dash state is managed via:

1. **URL Parameters:** Primary state for multi-family context
   - `?family_id=1` → which family is active
   - `?period=month` → which period for dashboard
   - Persistent across page refreshes and browser history
2. **dcc.Store (client-side storage):** Transient state within session
   - JWT token → persisted in browser storage (accessible via localStorage callback)
   - Current user object
   - Cached family list (to avoid re-fetching on every page)
3. **Callback outputs:** Transient UI state
   - Open/closed modals
   - Filter selections (before submission)
   - Pagination state

### 5.2 Multi-Family Context

On every page that requires `family_id`:

```python
# In callback or page function

def get_family_id_from_url():
    """Extract family_id from URL query params."""
    # Use dash.callback_context or pass as URL param to page
    return int(request.args.get('family_id', None))

# Validate that user is member of this family:
# (This happens server-side in API; FE just trusts API errors)

def load_dashboard(pathname, search):
    """Parse query params and load data for dashboard."""
    params = parse_qs(search.lstrip('?'))
    family_id = int(params.get('family_id', [None])[0])
    
    if not family_id:
        return dcc.Location(pathname="/family-selector", id="url")
    
    try:
        family = app.api_client.get_family(family_id)
        analytics = app.api_client.get_analytics_summary(family_id)
        # ... render dashboard
    except APIError as e:
        if e.is_auth_error():
            # Redirect to login
            return dcc.Location(pathname="/login", id="url")
        else:
            # Show error
            return dbc.Alert(f"Error loading dashboard: {e.user_message()}")
```

### 5.3 Family Switching Callback

```python
@app.callback(
    Output('url', 'pathname'),
    Output('url', 'search'),
    [Input('family-dropdown', 'value')],  # User selects family
    prevent_initial_call=True,
)
def switch_family(selected_family_id):
    """User selected a new family → redirect to dashboard with new family_id."""
    if not selected_family_id:
        raise PreventUpdate
    
    return '/dashboard', f'?family_id={selected_family_id}'
```

### 5.4 Token Management

```python
# Store JWT token in localStorage (accessible from JS)

@app.callback(
    Output('auth-token-store', 'data'),
    [Input('url', 'pathname')],  # On any page load
    [State('auth-token-store', 'data')],
)
def sync_token_from_storage(pathname, stored_token):
    """
    On page load, check if token exists in localStorage.
    If dcc.Store is empty but localStorage has token, sync it.
    (Handles browser refresh scenario.)
    """
    # Use clientside callback for this (no Python roundtrip needed)
    # OR use JS to inject token into dcc.Store on load
```

**Clientside callback (JS) for token persistence:**

```javascript
// assets/token_manager.js
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('authToken');
    if (token) {
        // Inject into Dash store or fetch fresh token
        // (This is handled via dash.callback on login)
    }
});
```

### 5.5 Logout Flow

```python
@app.callback(
    [Output('url', 'pathname'), Output('auth-token-store', 'data')],
    [Input('logout-btn', 'n_clicks')],
    prevent_initial_call=True,
)
def logout(n_clicks):
    """Clear token and redirect to login."""
    if not n_clicks:
        raise PreventUpdate
    
    app.api_client.clear_token()  # Clear auth header
    # Also clear localStorage via clientside script
    return '/login', None
```

---

## 6. Dependencies & Risks

### 6.1 Python Dependencies

```
# frontend/requirements.txt
dash==2.14.2                    # Web framework
plotly==5.17.0                  # Charts (included with Dash)
dash-bootstrap-components==1.5.0 # Component library
requests==2.31.0                # HTTP client
python-dotenv==1.0.0            # Environment variables
gunicorn==21.2.0                # Production server
```

### 6.2 Technology Decisions

| Decision | Rationale | Risk | Mitigation |
|---|---|---|---|
| **Dash** (not Next.js/React) | Python monorepo, rapid prototyping | Smaller JS ecosystem; less component library | Use dbc + Plotly cover 90% of needs |
| **dcc.Store** (not Redux) | Simple for v1; no extra state management | Limited for complex multi-step flows | Can add TanStack Query in v2 if needed |
| **URL params** (not Zustand) | SEO-friendly; shareable links | Clutters URL; manual parsing | Acceptable for v1 scale |
| **Polling** (not WebSocket) | Simpler server; no connection mgmt | 10s latency; higher API load | Acceptable for household scale; upgrade to SSE in v2 |
| **Tailwind** (not CSS Modules) | Utility-first faster; no naming conflicts | File size if not tree-shaken | Configure Tailwind purge correctly |

### 6.3 Known Risks & Mitigations

#### **Risk 1: Token Expiry (24 hours)**
- **Problem:** User logged in; left app idle 24h; token expired; next action fails silently
- **Mitigation:** 
  - On 401 response, redirect to login
  - Display "session expired" message
  - (Future v2: Implement refresh token endpoint)

#### **Risk 2: Race Conditions in Multi-Family**
- **Problem:** User switches family mid-request; data mismatch
- **Mitigation:** 
  - All API calls include `family_id` in URL (not inferred from token)
  - Backend enforces permission check (user must be member of family)
  - FE validates `family_id` matches URL before rendering

#### **Risk 3: Dashboard Polling Lag**
- **Problem:** Family member logs transaction; another member's dashboard shows stale data for 10s
- **Mitigation:** 
  - 10s poll interval is acceptable for household (not HFT)
  - Display "updated X seconds ago" so user knows
  - (Future: Add WebSocket/SSE for real-time)

#### **Risk 4: Category Icon Picker**
- **Problem:** No standard JS icon picker in Dash ecosystem
- **Mitigation:** 
  - Use fixed icon list (12-15 common icons: dollar, shopping-cart, zap, etc.)
  - Dropdown select, not visual picker
  - OR: Icon picker lib in v1.1

#### **Risk 5: Large Transaction Lists**
- **Problem:** Ledger with 10k+ transactions; table slow to render
- **Mitigation:** 
  - Pagination: 20-50 per page (handled by backend)
  - Server-side sorting/filtering (not client-side)
  - Virtual scrolling in v1.1 if needed

#### **Risk 6: Responsive Design Gap**
- **Problem:** Dash Bootstrap doesn't work perfectly on mobile
- **Mitigation:** 
  - Test on iPhone/Android in phase 5 (testing)
  - Mobile-specific CSS overrides if needed
  - Full mobile redesign in v1.1 if business demands

### 6.4 Testing Strategy

#### **Unit Tests** (utils, api_client)
- Mock API calls with `unittest.mock`
- Test error parsing, token injection
- ~30% coverage (high-value functions only)

#### **Integration Tests** (callbacks)
- Use `dash.testing` module
- Simulate user actions (button clicks, form fills)
- Verify API calls made with correct params
- ~20% coverage (happy path + error cases)

#### **E2E Tests** (Playwright, deferred to v1.1)
- Real browser; real backend
- Test full flows: login → family switch → log transaction
- ~5% coverage (golden path only)

### 6.5 Performance Considerations

| Concern | Approach |
|---|---|
| **Page load time** | Lazy load analytics; show skeleton loaders |
| **API latency** | 200ms SLA per endpoint (backend timeout) |
| **Chart rendering** | Plotly handles 1000+ data points; okay for 100-1000 txns |
| **Browser memory** | dcc.Store limited to ~5MB; not a concern for v1 |
| **CSS file size** | Tailwind purge: ~50-70KB minified (acceptable) |

---

## 7. Implementation Roadmap

### **Phase 3 (Current): Planning**
- ✅ Confirm tech stack (Dash + Tailwind)
- ✅ Define page structure
- ✅ Design component layout
- ✅ Outline API client

### **Phase 4: Build**
1. **Week 1-2: Scaffolding & Auth**
   - Dash multi-page app structure
   - Login page + API client
   - Token storage & JWT injection
   - Family selector page

2. **Week 2-3: Core Pages**
   - Dashboard (summary + charts)
   - Ledger (table + filters)
   - Settings (category management, members)

3. **Week 3-4: Polish & Edge Cases**
   - Error handling (all pages)
   - Responsive design (tablet/mobile)
   - Confirmation modals
   - Loading indicators

4. **Week 4-5: Testing**
   - Unit tests for API client
   - Integration tests for pages
   - E2E smoke tests

### **Phase 5: Test & Fix**
- QA runs through all flows (see TEST_PLAN.md)
- Bug fixes and regression testing

### **Phase 6: Delivery**
- Build Docker image
- Deploy with docker-compose
- Live validation

---

## 8. Open Questions & Decisions

1. **Icon Picker for Categories**
   - Approach: Fixed list dropdown vs. visual icon picker?
   - **Decision:** Dropdown (simpler for v1; icon picker in v1.1)

2. **Real-time Updates**
   - Approach: 10s polling vs. WebSocket/SSE?
   - **Decision:** 10s polling (simpler; SSE in v2)

3. **Mobile Responsiveness**
   - Approach: Mobile-first CSS vs. desktop-first?
   - **Decision:** Desktop-first for v1; mobile-specific tweaks for v1.1

4. **Transaction Edit Window**
   - Approach: Unlimited edit vs. 24-hour window?
   - **Decision:** Per UX Flow: 24-hour edit window for members (owner can always edit)

---

## 9. Files to Create/Modify

### **New Files**
- `frontend/app/pages/0_login.py`
- `frontend/app/pages/1_family_selector.py`
- `frontend/app/pages/2_dashboard.py`
- `frontend/app/pages/3_ledger.py`
- `frontend/app/pages/4_settings.py`
- `frontend/app/pages/5_invitation.py`
- `frontend/app/pages/error.py`
- `frontend/app/components/navbar.py`
- `frontend/app/components/sidebar.py`
- `frontend/app/components/forms.py`
- `frontend/app/components/charts.py`
- `frontend/app/components/modals.py`
- `frontend/app/components/alerts.py`
- `frontend/app/utils/api_client.py`
- `frontend/app/main.py` (Dash app entry)
- `frontend/assets/tailwind.config.js`
- `frontend/assets/custom.css`
- `frontend/Dockerfile`
- `frontend/requirements.txt`
- `frontend/.env.example`

### **Existing Files to Modify**
- None (FE starting from scratch)

---

## 10. Success Criteria

FE implementation is **complete** when:

1. ✅ All 6 main pages exist and are navigable
2. ✅ Multi-family switching works without re-login
3. ✅ API client abstraction is centralized (single source of truth)
4. ✅ Error handling shows user-friendly messages for all 400/401/403/404/409 scenarios
5. ✅ Tailwind styling applied consistently (no inline styles; utility classes only)
6. ✅ Dashboard analytics (summary + charts) render correctly
7. ✅ Ledger filters & pagination work
8. ✅ Transaction CRUD (create, read, update, delete) works end-to-end
9. ✅ Category CRUD works (owner only)
10. ✅ Member invite form works
11. ✅ Invitation acceptance flow works (new user + existing user paths)
12. ✅ Unit tests for API client (>80% coverage)
13. ✅ Integration tests for 3+ pages (happy path + error path)
14. ✅ Responsive design works on tablet (iPad 768px)
15. ✅ No console errors or warnings

---

## References

- **Dash Documentation:** https://dash.plotly.com/
- **Plotly Charts:** https://plotly.com/python/
- **Dash Bootstrap Components:** https://dash-bootstrap-components.opensource.faculty.ai/
- **Tailwind CSS:** https://tailwindcss.com/
- **API Contract:** `docs/architecture/API_CONTRACT.md`
- **UX Flow:** `docs/product/UX_FLOW.md`
- **Tech Stack:** `docs/architecture/TECH_STACK.md`

---

## Revision History

| Date | Author | Change |
|---|---|---|
| 2026-05-16 | FE | Created FE_PLAN.md with page structure, component layout, styling strategy, API client, state management, and risks |
