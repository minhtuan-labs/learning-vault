import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from ..utils import APIClient, APIError
import os

dash.register_page(__name__, path="/family-selector", name="Family Selector")

api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))


def layout():
    return html.Div([
        dcc.Location(id="family-selector-url", refresh=False),
        dcc.Store(id="families-store"),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Select a Family", className="fw-bold mb-4 mt-4"),
                    html.Div(id="families-cards-container"),
                    dbc.Button("Logout", id="family-selector-logout-btn", color="secondary", className="mt-4")
                ], lg=8, className="mx-auto")
            ], className="mt-5")
        ], fluid=True)
    ])


@callback(
    Output("families-cards-container", "children"),
    Input("family-selector-url", "pathname"),
    State("auth-token-store", "data"),
    prevent_initial_call=True
)
def load_families(pathname, token):
    """Load families for the current user."""
    if not token:
        return dbc.Alert("Please log in first.", color="danger")

    api_client.set_token(token)

    try:
        result = api_client.get_families()
        families = result.get("families", [])

        if not families:
            return dbc.Alert("You don't belong to any families yet. Contact an administrator.", color="info")

        cards = []
        for family in families:
            card = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H5(family.get("name", "Unknown"), className="card-title fw-bold"),
                        html.P(family.get("description", ""), className="card-text text-muted"),
                        html.P([
                            html.Span(f"👥 {family.get('member_count', 0)} members", className="me-3"),
                            html.Span(f"Role: {family.get('role', 'member')}", className="text-muted")
                        ], className="small")
                    ]),
                    dbc.Button(
                        "Open Family",
                        id={"type": "family-select-btn", "index": family.get("id")},
                        color="primary",
                        className="w-100 mt-3"
                    )
                ])
            ], className="mb-3 shadow-sm")
            cards.append(card)

        return html.Div(cards)

    except APIError as e:
        return dbc.Alert(f"Error loading families: {e.user_message()}", color="danger")
    except Exception as e:
        return dbc.Alert("An unexpected error occurred.", color="danger")


@callback(
    Output("family-selector-url", "pathname"),
    Input({"type": "family-select-btn", "index": dash.ALL}, "n_clicks"),
    State({"type": "family-select-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=True
)
def select_family(n_clicks_list, btn_ids):
    """Handle family selection."""
    if not n_clicks_list or not any(n_clicks_list):
        return dash.no_update

    # Find the button that was clicked
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks:
            family_id = btn_ids[i]["index"]
            return f"/dashboard?family_id={family_id}"

    return dash.no_update


@callback(
    Output("family-selector-url", "pathname", allow_duplicate=True),
    Input("family-selector-logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def logout(n_clicks):
    """Handle logout."""
    if n_clicks:
        api_client.clear_token()
        return "/"
    return dash.no_update
