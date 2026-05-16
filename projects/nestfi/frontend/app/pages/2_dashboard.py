import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from ..components import (
    create_navbar, create_summary_card, create_category_pie_chart,
    create_trends_chart, create_transactions_table, create_transaction_modal
)
from ..utils import APIClient, APIError
import os
from datetime import datetime

dash.register_page(__name__, path="/dashboard", name="Dashboard")

api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))


def layout():
    return html.Div([
        dcc.Location(id="dashboard-url", refresh=False),
        dcc.Store(id="dashboard-family-store"),
        dcc.Store(id="dashboard-analytics-store"),
        dcc.Store(id="dashboard-transactions-store"),
        dcc.Interval(id="dashboard-refresh-interval", interval=10000, n_intervals=0),

        html.Div(id="dashboard-navbar"),

        dbc.Container([
            dbc.Alert(
                id="dashboard-error-alert",
                color="danger",
                dismissable=True,
                className="mt-4",
                style={"display": "none"}
            ),

            # Period selector
            dbc.Row([
                dbc.Col([
                    html.H4("Dashboard", className="fw-bold mb-3"),
                    dcc.RadioItems(
                        id="period-radio",
                        options=[
                            {"label": " Month", "value": "month"},
                            {"label": " Year", "value": "year"}
                        ],
                        value="month",
                        inline=True
                    )
                ], md=6),
                dbc.Col([
                    dbc.Button(
                        "Log Transaction",
                        id="log-txn-btn",
                        color="primary",
                        size="sm",
                        className="float-end mt-2"
                    )
                ], md=6, className="text-end")
            ], className="mb-4"),

            # Summary cards
            dbc.Row([
                dbc.Col([html.Div(id="income-card")], lg=3, md=6, className="mb-3"),
                dbc.Col([html.Div(id="expense-card")], lg=3, md=6, className="mb-3"),
                dbc.Col([html.Div(id="savings-card")], lg=3, md=6, className="mb-3"),
                dbc.Col([html.Div(id="savings-rate-card")], lg=3, md=6, className="mb-3"),
            ], className="mb-4"),

            # Charts
            dbc.Row([
                dbc.Col([html.Div(id="pie-chart-container")], lg=6, className="mb-4"),
                dbc.Col([html.Div(id="trends-chart-container")], lg=6, className="mb-4"),
            ]),

            # Recent transactions
            dbc.Row([
                dbc.Col([
                    html.H5("Recent Transactions", className="fw-bold mb-3"),
                    html.Div(id="recent-txns-container")
                ], lg=12, className="mb-4")
            ]),

            # Link to ledger
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "View All Transactions →",
                        href="#/ledger",
                        color="link",
                        className="ps-0"
                    )
                ])
            ])
        ], fluid=True, className="py-4"),

        # Modals
        create_transaction_modal([])
    ])


@callback(
    Output("dashboard-navbar", "children"),
    Input("dashboard-url", "pathname"),
    State("auth-token-store", "data"),
    State("user-store", "data"),
    prevent_initial_call=True
)
def load_navbar(pathname, token, user):
    """Load navbar with family info."""
    if not token or not user:
        return html.Div()

    api_client.set_token(token)

    try:
        result = api_client.get_families()
        families = result.get("families", [])
        user_name = user.get("full_name", user.get("email", "User"))

        return create_navbar(user_name, None, families)
    except:
        return create_navbar("User", None, [])


@callback(
    [Output("income-card", "children"),
     Output("expense-card", "children"),
     Output("savings-card", "children"),
     Output("savings-rate-card", "children"),
     Output("pie-chart-container", "children"),
     Output("trends-chart-container", "children"),
     Output("recent-txns-container", "children"),
     Output("dashboard-error-alert", "children"),
     Output("dashboard-error-alert", "style")],
    [Input("dashboard-url", "pathname"),
     Input("period-radio", "value"),
     Input("dashboard-refresh-interval", "n_intervals")],
    [State("auth-token-store", "data"),
     State("dashboard-url", "search")],
    prevent_initial_call=True
)
def load_dashboard_data(pathname, period, n_intervals, token, search):
    """Load dashboard analytics and transactions."""
    if not token or not search:
        return [html.Div()] * 7 + ["Auth error", {"display": "block"}]

    # Extract family_id from URL
    try:
        family_id = int(search.split("family_id=")[1].split("&")[0])
    except:
        return [html.Div()] * 7 + ["Invalid family ID", {"display": "block"}]

    api_client.set_token(token)

    try:
        # Get analytics summary
        analytics = api_client.get_analytics_summary(family_id, period=period)
        total_income = analytics.get("total_income", 0)
        total_expense = analytics.get("total_expense", 0)
        net_savings = analytics.get("net_savings", 0)
        savings_rate = analytics.get("savings_rate", 0)
        category_breakdown = analytics.get("category_breakdown", [])

        # Get trends
        trends = api_client.get_analytics_trends(family_id, months=6)
        trends_data = trends.get("trends", [])

        # Get recent transactions
        txns = api_client.get_transactions(family_id, limit=10)
        transactions = txns.get("transactions", [])

        # Create summary cards
        income_card = create_summary_card(
            "Total Income",
            f"${total_income:,.2f}",
            color="success",
            icon="📈"
        )
        expense_card = create_summary_card(
            "Total Expense",
            f"${total_expense:,.2f}",
            color="danger",
            icon="📉"
        )
        savings_card = create_summary_card(
            "Net Savings",
            f"${net_savings:,.2f}",
            color="info",
            icon="💰"
        )
        savings_rate_card = create_summary_card(
            "Savings Rate",
            f"{savings_rate*100:.1f}%" if savings_rate else "0%",
            color="primary",
            icon="📊"
        )

        # Create charts
        pie_chart = create_category_pie_chart(category_breakdown)
        trends_chart = create_trends_chart(trends_data)

        # Create transactions table
        txns_table = create_transactions_table(transactions)

        return income_card, expense_card, savings_card, savings_rate_card, \
               pie_chart, trends_chart, txns_table, "", {"display": "none"}

    except APIError as e:
        if e.is_auth_error():
            return [html.Div()] * 7 + [e.user_message(), {"display": "block"}]
        return [html.Div()] * 7 + [e.user_message(), {"display": "block"}]
    except Exception as e:
        return [html.Div()] * 7 + ["Failed to load dashboard", {"display": "block"}]


@callback(
    Output("log-txn-btn", "n_clicks"),
    Input("log-txn-btn", "n_clicks"),
    prevent_initial_call=True
)
def toggle_txn_modal(n_clicks):
    """Toggle transaction modal."""
    # This would be handled by dbc.Modal's toggle property
    return n_clicks
