import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go


def create_summary_card(title: str, value: str, color: str = "primary", icon: str = "💰"):
    """Create a summary card for dashboard."""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, className="fs-3 me-2"),
                html.H6(title, className="card-title text-muted mb-0")
            ]),
            html.H4(value, className=f"text-{color} fw-bold mt-2")
        ])
    ], className="mb-3")


def create_category_pie_chart(category_data: list = None):
    """Create pie chart for category breakdown."""
    if not category_data:
        category_data = [
            {"category_name": "No data", "percentage": 100}
        ]

    labels = [item.get("category_name", "Other") for item in category_data]
    values = [item.get("percentage", 0) for item in category_data]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        marker=dict(line=dict(color="white", width=2))
    )])

    fig.update_layout(
        title="Expense Breakdown by Category",
        template="plotly_white",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return dcc.Graph(figure=fig, className="rounded border p-3")


def create_trends_chart(trends_data: list = None):
    """Create bar chart for income/expense trends."""
    if not trends_data:
        trends_data = [{"month": "No data", "income": 0, "expense": 0}]

    months = [item.get("month", "") for item in trends_data]
    income = [item.get("income", 0) for item in trends_data]
    expense = [item.get("expense", 0) for item in trends_data]

    fig = go.Figure(data=[
        go.Bar(name="Income", x=months, y=income, marker_color="#16a34a", hovertemplate="<b>Income</b><br>%{y:,.0f}<extra></extra>"),
        go.Bar(name="Expense", x=months, y=expense, marker_color="#dc2626", hovertemplate="<b>Expense</b><br>%{y:,.0f}<extra></extra>")
    ])

    fig.update_layout(
        title="Income vs Expense Trends (Last 6 Months)",
        xaxis_title="Month",
        yaxis_title="Amount",
        barmode="group",
        template="plotly_white",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )

    return dcc.Graph(figure=fig, className="rounded border p-3")


def create_transactions_table(transactions: list = None):
    """Create table of recent transactions."""
    if not transactions:
        transactions = []

    if not transactions:
        return html.Div(
            dbc.Alert("No recent transactions", color="info", className="mb-0"),
            className="rounded border p-3"
        )

    rows = []
    for txn in transactions[:10]:  # Limit to 10 recent
        color = "success" if txn.get("type") == "income" else "danger"
        amount_sign = "+" if txn.get("type") == "income" else "-"
        rows.append(
            html.Tr([
                html.Td(txn.get("transaction_date", ""), className="text-muted small"),
                html.Td(txn.get("user_name", ""), className="text-muted small"),
                html.Td(txn.get("category_name", ""), className="small"),
                html.Td(
                    html.Span(f"{amount_sign}${txn.get('amount', 0):,.2f}", className=f"text-{color} fw-bold"),
                ),
                html.Td(txn.get("description", ""), className="text-muted small"),
            ])
        )

    return html.Div(
        dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Date", className="text-muted small"),
                    html.Th("Member", className="text-muted small"),
                    html.Th("Category", className="text-muted small"),
                    html.Th("Amount", className="text-muted small"),
                    html.Th("Description", className="text-muted small"),
                ])
            ),
            html.Tbody(rows)
        ], striped=True, hover=True, responsive=True, size="sm"),
        className="rounded border p-3"
    )
