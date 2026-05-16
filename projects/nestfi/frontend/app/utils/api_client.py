import requests
import os
from typing import Dict, Optional, Any


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, detail: str, code: str = "UNKNOWN", status_code: Optional[int] = None):
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)

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


class APIClient:
    """Centralized API client for all FastAPI endpoints."""

    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def set_token(self, token: str) -> None:
        """Set JWT token for all subsequent requests."""
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        """Clear token (on logout)."""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal request handler."""
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.request(method, url, timeout=10, **kwargs)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.HTTPError as e:
            # Parse error from response
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", str(e))
                code = error_data.get("code", "UNKNOWN")
            except:
                detail = str(e)
                code = "UNKNOWN"
            raise APIError(detail=detail, code=code, status_code=e.response.status_code)
        except requests.RequestException as e:
            raise APIError(detail="Network error", code="NETWORK_ERROR")

    # ========== Authentication ==========

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login with email and password."""
        return self._request("POST", "/auth/login", json={
            "email": email,
            "password": password
        })

    def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user."""
        return self._request("GET", "/auth/me")

    # ========== Families ==========

    def get_families(self) -> Dict[str, Any]:
        """List all families the current user belongs to."""
        return self._request("GET", "/families")

    def get_family(self, family_id: int) -> Dict[str, Any]:
        """Get family details."""
        return self._request("GET", f"/families/{family_id}")

    def create_family(self, name: str, owner_email: str, description: str = None, currency: str = "USD") -> Dict[str, Any]:
        """Create a new family (superadmin only)."""
        data = {"name": name, "owner_email": owner_email, "currency": currency}
        if description:
            data["description"] = description
        return self._request("POST", "/families", json=data)

    def update_family(self, family_id: int, name: str = None, description: str = None) -> Dict[str, Any]:
        """Update family details (owner only)."""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        return self._request("PUT", f"/families/{family_id}", json=data)

    # ========== Family Members ==========

    def get_members(self, family_id: int) -> Dict[str, Any]:
        """List all members of a family."""
        return self._request("GET", f"/families/{family_id}/members")

    def invite_member(self, family_id: int, email: str, role: str = "member") -> Dict[str, Any]:
        """Invite a new member to family (owner only)."""
        return self._request("POST", f"/families/{family_id}/members", json={
            "email": email,
            "role": role
        })

    def remove_member(self, family_id: int, member_id: int) -> None:
        """Remove member from family (owner only)."""
        self._request("DELETE", f"/families/{family_id}/members/{member_id}")

    # ========== Invitations ==========

    def accept_invitation(self, token: str, full_name: str = None, password: str = None) -> Dict[str, Any]:
        """Accept a family invitation (new or existing user)."""
        data = {}
        if full_name:
            data["full_name"] = full_name
        if password:
            data["password"] = password
        return self._request("POST", f"/invitations/{token}/accept", json=data)

    def decline_invitation(self, token: str) -> Dict[str, Any]:
        """Decline a family invitation."""
        return self._request("POST", f"/invitations/{token}/decline", json={})

    # ========== Transactions ==========

    def get_transactions(self, family_id: int, skip: int = 0, limit: int = 30, **filters) -> Dict[str, Any]:
        """Get paginated transaction history for a family."""
        params = {"skip": skip, "limit": limit}
        params.update(filters)  # category_id, date_from, type, sort_by, etc.
        return self._request("GET", f"/families/{family_id}/transactions", params=params)

    def create_transaction(self, family_id: int, category_id: int, txn_type: str,
                          amount: float, description: str = None, transaction_date: str = None) -> Dict[str, Any]:
        """Create a new transaction."""
        data = {
            "category_id": category_id,
            "type": txn_type,
            "amount": amount
        }
        if description:
            data["description"] = description
        if transaction_date:
            data["transaction_date"] = transaction_date
        return self._request("POST", f"/families/{family_id}/transactions", json=data)

    def update_transaction(self, family_id: int, transaction_id: int, **fields) -> Dict[str, Any]:
        """Update a transaction (author or owner only)."""
        return self._request("PUT", f"/families/{family_id}/transactions/{transaction_id}", json=fields)

    def delete_transaction(self, family_id: int, transaction_id: int) -> None:
        """Delete a transaction (author or owner only)."""
        self._request("DELETE", f"/families/{family_id}/transactions/{transaction_id}")

    # ========== Categories ==========

    def get_categories(self, family_id: int, category_type: str = None, active_only: bool = False) -> Dict[str, Any]:
        """Get all categories for a family."""
        params = {}
        if category_type:
            params["type"] = category_type
        if active_only:
            params["active_only"] = True
        return self._request("GET", f"/families/{family_id}/categories", params=params)

    def create_category(self, family_id: int, name: str, category_type: str,
                       description: str = None, color: str = None, icon: str = None) -> Dict[str, Any]:
        """Create a new category (owner only)."""
        data = {"name": name, "type": category_type}
        if description:
            data["description"] = description
        if color:
            data["color"] = color
        if icon:
            data["icon"] = icon
        return self._request("POST", f"/families/{family_id}/categories", json=data)

    def update_category(self, family_id: int, category_id: int, **fields) -> Dict[str, Any]:
        """Update a category (owner only)."""
        return self._request("PUT", f"/families/{family_id}/categories/{category_id}", json=fields)

    def delete_category(self, family_id: int, category_id: int) -> None:
        """Archive (deactivate) a category (owner only)."""
        self._request("DELETE", f"/families/{family_id}/categories/{category_id}")

    # ========== Analytics ==========

    def get_analytics_summary(self, family_id: int, period: str = "month", date: str = None) -> Dict[str, Any]:
        """Get financial summary for current period."""
        params = {"period": period}
        if date:
            params["date"] = date
        return self._request("GET", f"/families/{family_id}/analytics/summary", params=params)

    def get_analytics_trends(self, family_id: int, months: int = 6) -> Dict[str, Any]:
        """Get spending trends over last N months."""
        return self._request("GET", f"/families/{family_id}/analytics/trends", params={"months": months})

    # ========== Health ==========

    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return self._request("GET", "/")
