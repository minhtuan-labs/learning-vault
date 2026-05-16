import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from ..components import create_navbar
from ..utils import APIClient, APIError
import os

dash.register_page(__name__, path="/ledger", name="Ledger")

api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))


def layout():
    return html.Div([
        dcc.Location(id="ledger-url", refresh=False),
        dcc.Interval(id="ledger-refresh-interval", interval=10000, n_intervals=0),

        html.Div(id="ledger-navbar"),

        dbc.Container([
            html.H4("Transaction Ledger", className="fw-bold mb-4 mt-4"),

            dbc.Alert(
                id="ledger-error-alert",
                color="danger",
                dismissable=True,
                className="mb-3",
                style={"display": "none"}
            ),

            # Filters
            dbc.Row([
                dbc.Col([
                    dbc.Label("Date From", className="form-label fw-bold small"),
                    dcc.DatePickerSingle(
                        id="ledger-date-from",
                        placeholder="Select date",
                        className="form-control"
                    )
                ], md=3, className="mb-3"),

                dbc.Col([
                    dbc.Label("Date To", className="form-label fw-bold small"),
                    dcc.DatePickerSingle(
                        id="ledger-date-to",
                        placeholder="Select date",
                        className="form-control"
                    )
                ], md=3, className="mb-3"),

                dbc.Col([
                    dbc.Label("Category", className="form-label fw-bold small"),
                    dcc.Dropdown(
                        id="ledger-category-filter",
                        placeholder="All categories",
                        clearable=True,
                        className="form-control"
                    )
                ], md=3, className="mb-3"),

                dbc.Col([
                    dbc.Label("Type", className="form-label fw-bold small"),
                    dcc.Dropdown(
                        id="ledger-type-filter",
                        options=[
                            {"label": "All", "value": ""},
                            {"label": "Income", "value": "income"},
                            {"label": "Expense", "value": "expense"},
                            {"label": "Investment", "value": "investment"}
                        ],
                        value="",
                        clearable=False,
                        className="form-control"
                    )
                ], md=3, className="mb-3"),
            ], className="sticky-top bg-white py-3 border-bottom"),

            # Transactions table
            html.Div(id="ledger-table-container", className="mt-4 mb-4"),

            # Pagination
            dbc.Row([
                dbc.Col([
                    dbc.Pagination(
                        id="ledger-pagination",
                        max_value=1,
                        fully_expanded=False,
                        className="justify-content-center"
                    )
                ])
            ])
        ], fluid=True, className="py-4")
    ])


@callback(
    Output("ledger-navbar", "children"),
    Input("ledger-url", "pathname"),
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
    [Output("ledger-category-filter", "options"),
     Output("ledger-table-container", "children"),
     Output("ledger-pagination", "max_value"),
     Output("ledger-error-alert", "children"),
     Output("ledger-error-alert", "style")],
    [Input("ledger-url", "pathname"),
     Input("ledger-date-from", "date"),
     Input("ledger-date-to", "date"),
     Input("ledger-category-filter", "value"),
     Input("ledger-type-filter", "value"),
     Input("ledger-pagination", "active_page"),
     Input("ledger-refresh-interval", "n_intervals")],
    [State("auth-token-store", "data"),
     State("ledger-url", "search")],
    prevent_initial_call=True
)
def load_ledger(pathname, date_from, date_to, category, txn_type, page, n_intervals, token, search):
    """Load transaction ledger with filters."""
    if not token or not search:
        return [], html.Div(), 1, "Auth error", {"display": "block"}

    # Extract family_id
    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return [], html.Div(), 1, "Invalid family ID", {"display": "block"}

    api_client.set_token(token)
    page = page or 1
    limit = 20

    try:
        # Get categories
        cats = api_client.get_categories(family_id)
        categories = cats.get("categories", [])
        category_options = [{"label": c.get("name"), "value": c.get("id")} for c in categories]

        # Build filters
        filters = {"skip": (page - 1) * limit, "limit": limit}
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if category:
            filters["category_id"] = category
        if txn_type:
            filters["type"] = txn_type

        # Get transactions
        result = api_client.get_transactions(family_id, **filters)
        transactions = result.get("transactions", [])
        total = result.get("total", 0)
        max_page = (total + limit - 1) // limit

        # Build table
        rows = []
        for txn in transactions:
            color = "success" if txn.get("type") == "income" else "danger"
            amount_sign = "+" if txn.get("type") == "income" else "-"
            rows.append(
                html.Tr([
                    html.Td(txn.get("transaction_date", ""), className="small"),
                    html.Td(txn.get("user_name", ""), className="small"),
                    html.Td(txn.get("category_name", ""), className="small"),
                    html.Td(html.Span(f"{amount_sign}${txn.get('amount', 0):,.2f}", className=f"fw-bold text-{color}"), className="small"),
                    html.Td(txn.get("description", ""), className="small text-muted"),
                ])
            )

        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Date", className="small"),
                    html.Th("Member", className="small"),
                    html.Th("Category", className="small"),
                    html.Th("Amount", className="small"),
                    html.Th("Description", className="small"),
                ])
            ),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm", className="rounded border")

        return category_options, table, max_page, "", {"display": "none"}

    except APIError as e:
        return [], html.Div(), 1, e.user_message(), {"display": "block"}
    except Exception as e:
        return [], html.Div(), 1, "Failed to load ledger", {"display": "block"}
