# NestFi Frontend

Python + Dash multi-page web application for family financial management.

## Stack

- **Framework:** Dash (Python) with Plotly charts
- **Components:** Dash Bootstrap Components (dbc)
- **Styling:** Tailwind CSS (utility-first)
- **State Management:** URL params + dcc.Store (JWT token)
- **API Client:** Centralized requests.Session wrapper

## Structure

```
frontend/
├── app/
│   ├── pages/
│   │   ├── 0_login.py              # Login page
│   │   ├── 1_family_selector.py    # Family selection
│   │   ├── 2_dashboard.py          # Main dashboard
│   │   ├── 3_ledger.py             # Transaction history
│   │   ├── 4_settings.py           # Family settings
│   │   └── 5_invitation.py         # Invitation acceptance
│   ├── components/
│   │   ├── navbar.py               # Navigation bar
│   │   ├── forms.py                # Reusable form inputs
│   │   ├── alerts.py               # Alert/toast components
│   │   ├── charts.py               # Plotly charts
│   │   └── modals.py               # Modal dialogs
│   ├── utils/
│   │   └── api_client.py           # Centralized API client
│   └── main.py                     # Dash app entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image
└── README.md
```

## Setup

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export API_BASE_URL=http://localhost:8000
export DEBUG=true

# Run locally
python app/main.py
```

App runs at `http://localhost:8080`

### Docker

```bash
# Build image
docker build -t nestfi-frontend .

# Run container
docker run -p 8080:8080 \
  -e API_BASE_URL=http://backend:8000 \
  nestfi-frontend
```

## Features (v1.0)

### Pages
- **Login:** Email/password authentication
- **Family Selector:** Choose family context (multi-family support)
- **Dashboard:** Summary cards, analytics charts, recent transactions
- **Ledger:** Filtered transaction history with pagination
- **Settings:** Category and member management
- **Invitation:** Accept family invitations (new users)

### Components
- **Navbar:** Family switcher, user menu
- **Forms:** Email, password, number, date, dropdown, textarea inputs
- **Modals:** Transaction logging, member invite, category form
- **Charts:** Pie chart (category breakdown), bar chart (trends)
- **Alerts:** Error, success, loading states

### State Management
- JWT token stored in `dcc.Store` (browser session)
- URL params for family context (`?family_id=X`)
- 10-second auto-refresh polling on dashboard/ledger

## API Integration

All API calls via centralized `APIClient` in `utils/api_client.py`:

```python
from app.utils import APIClient

client = APIClient(base_url="http://localhost:8000")
client.set_token(jwt_token)

# Login
result = client.login(email, password)

# Families
families = client.get_families()
family = client.get_family(family_id)

# Analytics
summary = client.get_analytics_summary(family_id, period="month")
trends = client.get_analytics_trends(family_id, months=6)

# Transactions
txns = client.get_transactions(family_id, skip=0, limit=30)
client.create_transaction(family_id, category_id, txn_type, amount)

# Categories
cats = client.get_categories(family_id, category_type="expense")
client.create_category(family_id, name, category_type)

# Members
members = client.get_members(family_id)
client.invite_member(family_id, email, role="member")
```

### Error Handling

All API errors raise `APIError` with `user_message()`:

```python
try:
    result = client.get_family(family_id)
except APIError as e:
    if e.is_auth_error():
        # Redirect to login
    else:
        # Show user-friendly error message
        print(e.user_message())
```

## Testing

### Unit Tests (API Client)
```bash
pytest app/utils/test_api_client.py -v
```

### Integration Tests (Pages/Callbacks)
```bash
pytest tests/integration/ -v
```

## Known Limitations (v1.0)

- ✅ No WebSocket; uses 10s polling (acceptable for household budget)
- ✅ No real-time collaboration; transactions update on refresh
- ✅ No offline mode; internet required
- ✅ Mobile responsive for tablet (iPad 768px+); mobile redesign in v1.1
- ✅ Icon picker uses fixed list; visual picker in v1.1
- ✅ No transaction export (CSV); deferred to v1.1

## Next Steps (v1.1+)

- [ ] Real-time updates via Server-Sent Events (SSE)
- [ ] Visual icon picker for categories
- [ ] Dark mode support
- [ ] Transaction export (CSV)
- [ ] Mobile-optimized UI redesign
- [ ] Infinite scroll for large transaction lists
- [ ] Refresh token support (extend session beyond 24h)

## Performance

- **Page load:** ~1s (with 10 recent transactions)
- **Dashboard refresh:** ~2-3s (10s polling interval)
- **API latency SLA:** <200ms per endpoint (backend)
- **Chart rendering:** <500ms (Plotly handles 1000+ points)

## Troubleshooting

### Token Expired (401)
User is logged out after 24 hours. Redirect to login on 401 response.

### Family ID Missing
Redirect to `/family-selector` if `?family_id=` not in URL.

### API Connection Error
Check `API_BASE_URL` environment variable points to correct backend.

---

**Last Updated:** 2026-05-16  
**Owner:** FE  
**Phase:** 4_BUILD
