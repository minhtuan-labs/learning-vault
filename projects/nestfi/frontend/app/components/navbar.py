import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash


def create_navbar(user_name: str = None, current_family: str = None, families: list = None):
    """Create top navigation bar with family switcher and user menu."""

    if families is None:
        families = []

    # Family dropdown options
    family_options = [{"label": f.get("name", "Family"), "value": f.get("id")} for f in families]
    current_family_id = families[0]["id"] if families else None

    navbar = dbc.Navbar(
        dbc.Container([
            # Logo/Brand
            dbc.Row([
                dbc.Col(html.A("💰 NestFi", href="/", className="navbar-brand fw-bold fs-5"), width="auto"),
            ], align="center", className="flex-grow-1"),

            # Family Switcher (center)
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="family-selector-dropdown",
                        options=family_options,
                        value=current_family_id,
                        clearable=False,
                        searchable=False,
                        className="rounded"
                    )
                ], width=3) if families else None
            ], align="center") if families else None,

            # User Menu (right)
            dbc.Row([
                dbc.Col([
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(f"👤 {user_name or 'User'}", header=True),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Profile", href="#"),
                            dbc.DropdownMenuItem("Settings", href="#"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("Logout", id="logout-btn", className="text-danger"),
                        ],
                        label="☰ Menu",
                        align_end=True,
                        toggle_class_name="btn btn-sm btn-outline-primary"
                    )
                ], width="auto")
            ], align="center")
        ], fluid=True),
        color="light",
        dark=False,
        className="border-bottom mb-4"
    )

    return navbar


def create_sidebar_nav():
    """Create optional sidebar navigation (for v1.1)."""
    # Deferred to v1.1 — using navbar only for v1
    return None
