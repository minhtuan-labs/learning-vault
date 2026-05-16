import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from ..components import create_navbar, create_category_form_modal, create_invite_member_modal
from ..utils import APIClient, APIError
import os

dash.register_page(__name__, path="/settings", name="Settings")

api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))


def layout():
    return html.Div([
        dcc.Location(id="settings-url", refresh=False),

        html.Div(id="settings-navbar"),

        dbc.Container([
            html.H4("Family Settings", className="fw-bold mb-4 mt-4"),

            dbc.Alert(
                id="settings-error-alert",
                color="danger",
                dismissable=True,
                className="mb-3",
                style={"display": "none"}
            ),

            dbc.Alert(
                id="settings-success-alert",
                color="success",
                dismissable=True,
                className="mb-3",
                style={"display": "none"}
            ),

            # Tabs
            dbc.Tabs([
                dbc.Tab(label="General", tab_id="general", children=[
                    html.Div(id="general-tab-content", className="mt-3")
                ]),
                dbc.Tab(label="Members", tab_id="members", children=[
                    html.Div(id="members-tab-content", className="mt-3")
                ]),
                dbc.Tab(label="Income Categories", tab_id="income-cats", children=[
                    html.Div(id="income-cats-tab-content", className="mt-3")
                ]),
                dbc.Tab(label="Expense Categories", tab_id="expense-cats", children=[
                    html.Div(id="expense-cats-tab-content", className="mt-3")
                ]),
                dbc.Tab(label="Investment Categories", tab_id="investment-cats", children=[
                    html.Div(id="investment-cats-tab-content", className="mt-3")
                ]),
            ], id="settings-tabs", active_tab="general")
        ], fluid=True, className="py-4"),

        # Modals
        create_invite_member_modal(),
        create_category_form_modal()
    ])


@callback(
    Output("settings-navbar", "children"),
    Input("settings-url", "pathname"),
    State("auth-token-store", "data"),
    State("user-store", "data"),
    prevent_initial_call=True
)
def load_navbar(pathname, token, user):
    """Load navbar."""
    if not token or not user:
        return html.Div()

    api_client.set_token(token)

    try:
        result = api_client.get_families()
        families = result.get("families", [])
        user_name = user.get("full_name", user.get("email", "User"))
        return create_navbar(user_name, None, families)
    except:
        return html.Div()


@callback(
    Output("general-tab-content", "children"),
    Input("settings-url", "pathname"),
    State("auth-token-store", "data"),
    State("settings-url", "search"),
    prevent_initial_call=True
)
def load_general_tab(pathname, token, search):
    """Load general settings."""
    if not token or not search:
        return html.Div()

    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return html.Div()

    api_client.set_token(token)

    try:
        family = api_client.get_family(family_id)

        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Family Name", className="form-label fw-bold"),
                        dbc.Input(type="text", value=family.get("name", ""), disabled=True, className="form-control")
                    ], md=6),
                    dbc.Col([
                        dbc.Label("Currency", className="form-label fw-bold"),
                        dbc.Input(type="text", value=family.get("currency", "USD"), disabled=True, className="form-control")
                    ], md=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Description", className="form-label fw-bold mt-3"),
                        dbc.Textarea(value=family.get("description", ""), disabled=True, rows=3, className="form-control")
                    ])
                ])
            ])
        ])

    except:
        return html.Div()


@callback(
    Output("members-tab-content", "children"),
    Input("settings-url", "pathname"),
    State("auth-token-store", "data"),
    State("settings-url", "search"),
    prevent_initial_call=True
)
def load_members_tab(pathname, token, search):
    """Load members tab with invite button."""
    if not token or not search:
        return html.Div()

    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return html.Div()

    api_client.set_token(token)

    try:
        result = api_client.get_members(family_id)
        members = result.get("members", [])

        rows = []
        for member in members:
            status_badge = dbc.Badge(member.get("status", "").title(), color="info" if member.get("status") == "active" else "warning")
            rows.append(
                html.Tr([
                    html.Td(member.get("full_name", member.get("email", "")), className="small"),
                    html.Td(member.get("email", ""), className="small text-muted"),
                    html.Td(member.get("role", "").title(), className="small"),
                    html.Td(status_badge),
                ])
            )

        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Name", className="small"),
                    html.Th("Email", className="small"),
                    html.Th("Role", className="small"),
                    html.Th("Status", className="small"),
                ])
            ),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm", className="rounded border mb-3")

        return html.Div([
            dbc.Button("Invite Member", id="invite-member-btn", color="primary", className="mb-3"),
            table
        ])

    except:
        return html.Div()


@callback(
    Output("income-cats-tab-content", "children"),
    Input("settings-url", "pathname"),
    State("auth-token-store", "data"),
    State("settings-url", "search"),
    prevent_initial_call=True
)
def load_income_cats(pathname, token, search):
    """Load income categories."""
    if not token or not search:
        return html.Div()

    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return html.Div()

    api_client.set_token(token)

    try:
        result = api_client.get_categories(family_id, category_type="income")
        categories = result.get("categories", [])

        rows = []
        for cat in categories:
            rows.append(
                html.Tr([
                    html.Td([html.Span("●", style={"color": cat.get("color", "#999")}, className="me-2"), cat.get("name", "")], className="small"),
                    html.Td(cat.get("description", ""), className="small text-muted"),
                    html.Td(dbc.Badge(cat.get("transaction_count", 0), color="secondary"), className="small"),
                ])
            )

        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Category", className="small"),
                    html.Th("Description", className="small"),
                    html.Th("Transactions", className="small"),
                ])
            ),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm", className="rounded border mb-3")

        return html.Div([
            dbc.Button("Add Category", id="add-income-cat-btn", color="primary", className="mb-3"),
            table
        ])

    except:
        return html.Div()


@callback(
    Output("expense-cats-tab-content", "children"),
    Input("settings-url", "pathname"),
    State("auth-token-store", "data"),
    State("settings-url", "search"),
    prevent_initial_call=True
)
def load_expense_cats(pathname, token, search):
    """Load expense categories."""
    if not token or not search:
        return html.Div()

    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return html.Div()

    api_client.set_token(token)

    try:
        result = api_client.get_categories(family_id, category_type="expense")
        categories = result.get("categories", [])

        rows = []
        for cat in categories:
            rows.append(
                html.Tr([
                    html.Td([html.Span("●", style={"color": cat.get("color", "#999")}, className="me-2"), cat.get("name", "")], className="small"),
                    html.Td(cat.get("description", ""), className="small text-muted"),
                    html.Td(dbc.Badge(cat.get("transaction_count", 0), color="secondary"), className="small"),
                ])
            )

        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Category", className="small"),
                    html.Th("Description", className="small"),
                    html.Th("Transactions", className="small"),
                ])
            ),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm", className="rounded border mb-3")

        return html.Div([
            dbc.Button("Add Category", id="add-expense-cat-btn", color="primary", className="mb-3"),
            table
        ])

    except:
        return html.Div()


@callback(
    Output("investment-cats-tab-content", "children"),
    Input("settings-url", "pathname"),
    State("auth-token-store", "data"),
    State("settings-url", "search"),
    prevent_initial_call=True
)
def load_investment_cats(pathname, token, search):
    """Load investment categories."""
    if not token or not search:
        return html.Div()

    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return html.Div()

    api_client.set_token(token)

    try:
        result = api_client.get_categories(family_id, category_type="investment")
        categories = result.get("categories", [])

        rows = []
        for cat in categories:
            rows.append(
                html.Tr([
                    html.Td([html.Span("●", style={"color": cat.get("color", "#999")}, className="me-2"), cat.get("name", "")], className="small"),
                    html.Td(cat.get("description", ""), className="small text-muted"),
                    html.Td(dbc.Badge(cat.get("transaction_count", 0), color="secondary"), className="small"),
                ])
            )

        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Category", className="small"),
                    html.Th("Description", className="small"),
                    html.Th("Transactions", className="small"),
                ])
            ),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm", className="rounded border mb-3")

        return html.Div([
            dbc.Button("Add Category", id="add-investment-cat-btn", color="primary", className="mb-3"),
            table
        ])

    except:
        return html.Div()
