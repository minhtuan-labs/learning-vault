import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from ..components import create_text_input, create_password_input
from ..utils import APIClient, APIError
import os

dash.register_page(__name__, path="/accept", name="Accept Invitation")

api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))


def layout():
    return html.Div([
        dcc.Location(id="invitation-url", refresh=False),
        dcc.Store(id="auth-token-store"),
        dcc.Store(id="user-store"),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("💰 NestFi", className="text-center fw-bold text-primary mb-2"),
                        html.P("Accept Invitation", className="text-center text-muted mb-4")
                    ]),

                    dbc.Card([
                        dbc.CardBody([
                            dbc.Alert(
                                id="invitation-error-alert",
                                color="danger",
                                dismissable=True,
                                className="mb-3",
                                style={"display": "none"}
                            ),

                            html.Div(id="invitation-form-container")
                        ])
                    ], className="shadow-lg")
                ], lg=4, md=6, sm=12, className="mx-auto")
            ], className="vh-100 d-flex align-items-center")
        ], fluid=True)
    ])


@callback(
    Output("invitation-form-container", "children"),
    Input("invitation-url", "search"),
    prevent_initial_call=True
)
def load_invitation_form(search):
    """Load invitation form based on token in URL."""
    if not search or "token=" not in search:
        return dbc.Alert("Invalid or missing invitation token.", color="danger")

    token = search.split("token=")[1].split("&")[0]

    # Simple form - check if user exists or new
    return html.Div([
        html.H5("Complete Your Registration", className="card-title fw-bold mb-4"),

        dbc.FormGroup([
            dbc.Label("Full Name", className="form-label fw-bold"),
            dbc.Input(
                id="invitation-fullname-input",
                placeholder="Your full name",
                className="form-control"
            )
        ]),

        dbc.FormGroup([
            dbc.Label("Email", className="form-label fw-bold"),
            dbc.Input(
                id="invitation-email-input",
                type="email",
                placeholder="your@email.com",
                className="form-control"
            )
        ]),

        dbc.FormGroup([
            dbc.Label("Password", className="form-label fw-bold"),
            dbc.Input(
                id="invitation-password-input",
                type="password",
                placeholder="Create a password",
                className="form-control"
            ),
            dbc.FormText("Minimum 8 characters, with uppercase, lowercase, and number.", color="muted", className="small")
        ]),

        dbc.FormGroup([
            dbc.Label("Confirm Password", className="form-label fw-bold"),
            dbc.Input(
                id="invitation-password-confirm-input",
                type="password",
                placeholder="Confirm password",
                className="form-control"
            )
        ]),

        dbc.Button(
            "Accept Invitation",
            id="invitation-submit-btn",
            color="primary",
            size="lg",
            className="w-100 mt-3"
        ),

        dcc.Store(id="invitation-token-store", data=token)
    ])


@callback(
    [Output("auth-token-store", "data"),
     Output("user-store", "data"),
     Output("invitation-error-alert", "children"),
     Output("invitation-error-alert", "style"),
     Output("invitation-url", "pathname")],
    Input("invitation-submit-btn", "n_clicks"),
    [State("invitation-fullname-input", "value"),
     State("invitation-email-input", "value"),
     State("invitation-password-input", "value"),
     State("invitation-password-confirm-input", "value"),
     State("invitation-token-store", "data")],
    prevent_initial_call=True
)
def handle_invitation(n_clicks, fullname, email, password, password_confirm, token):
    """Handle invitation acceptance."""
    if not n_clicks:
        return dash.no_update, dash.no_update, "", {"display": "none"}, "/"

    if not fullname or not email or not password or not password_confirm:
        return dash.no_update, dash.no_update, "Please fill in all fields.", \
               {"display": "block"}, "/"

    if password != password_confirm:
        return dash.no_update, dash.no_update, "Passwords do not match.", \
               {"display": "block"}, "/"

    if len(password) < 8:
        return dash.no_update, dash.no_update, "Password must be at least 8 characters.", \
               {"display": "block"}, "/"

    try:
        result = api_client.accept_invitation(token, full_name=fullname, password=password)

        access_token = result.get("access_token")
        user = result.get("user", {})
        family_id = result.get("family_id")

        api_client.set_token(access_token)

        return access_token, user, "", {"display": "none"}, f"/dashboard?family_id={family_id}"

    except APIError as e:
        return dash.no_update, dash.no_update, e.user_message(), \
               {"display": "block"}, "/"
    except Exception as e:
        return dash.no_update, dash.no_update, "An unexpected error occurred.", \
               {"display": "block"}, "/"
