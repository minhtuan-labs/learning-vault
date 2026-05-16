import dash
from dash import dcc, html, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from ..utils import APIClient, APIError
import os

# Register page
dash.register_page(__name__, path="/", name="Login")

api_client = APIClient(base_url=os.getenv("API_BASE_URL", "http://localhost:8000"))


def layout():
    return html.Div([
        dcc.Location(id="login-url", refresh=False),
        dcc.Store(id="auth-token-store"),
        dcc.Store(id="user-store"),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.H1("💰 NestFi", className="text-center fw-bold text-primary mb-2"),
                            html.P("Family Financial Management", className="text-center text-muted mb-4")
                        ]),

                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Sign In", className="card-title fw-bold mb-4"),

                                # Error alert
                                dbc.Alert(
                                    id="login-error-alert",
                                    color="danger",
                                    dismissable=True,
                                    className="mb-3",
                                    style={"display": "none"}
                                ),

                                # Email input
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="login-email-input",
                                        type="email",
                                        placeholder="Email address",
                                        className="form-control",
                                        autoComplete="email"
                                    ),
                                    dbc.Label("Email address")
                                ], className="mb-3"),

                                # Password input
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="login-password-input",
                                        type="password",
                                        placeholder="Password",
                                        className="form-control",
                                        autoComplete="current-password"
                                    ),
                                    dbc.Label("Password")
                                ], className="mb-3"),

                                # Login button
                                dbc.Button(
                                    [
                                        dbc.Spinner(
                                            size="sm",
                                            color="light",
                                            className="me-2",
                                            id="login-spinner",
                                            style={"display": "none"}
                                        ),
                                        "Sign In"
                                    ],
                                    id="login-submit-btn",
                                    color="primary",
                                    size="lg",
                                    className="w-100 mb-3"
                                ),

                                # Demo credentials
                                dbc.Alert([
                                    html.Strong("Demo Credentials:"),
                                    html.Br(),
                                    html.Code("superadmin@nestfi.local / admin123")
                                ], color="info", className="small")
                            ])
                        ], className="shadow-lg")
                    ], className="login-container mt-5")
                ], lg=4, md=6, sm=12, className="mx-auto")
            ], className="vh-100 d-flex align-items-center")
        ], fluid=True)
    ])


@callback(
    [Output("auth-token-store", "data"),
     Output("user-store", "data"),
     Output("login-error-alert", "children"),
     Output("login-error-alert", "style"),
     Output("login-spinner", "style"),
     Output("login-submit-btn", "disabled"),
     Output("login-url", "pathname")],
    Input("login-submit-btn", "n_clicks"),
    [State("login-email-input", "value"),
     State("login-password-input", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    """Handle login submission."""
    if not n_clicks:
        return dash.no_update, dash.no_update, "", {"display": "none"}, {"display": "none"}, False, "/"

    if not email or not password:
        return dash.no_update, dash.no_update, "Please enter both email and password.", \
               {"display": "block"}, {"display": "none"}, False, "/"

    try:
        # Show loading spinner
        result = api_client.login(email, password)

        # Store token and user
        token = result.get("access_token")
        user = result.get("user", {})

        # Set token for future requests
        api_client.set_token(token)

        # Redirect based on family count
        families = result.get("families", [])
        if len(families) == 1:
            redirect_path = f"/dashboard?family_id={families[0]['id']}"
        else:
            redirect_path = "/family-selector"

        return token, user, "", {"display": "none"}, {"display": "none"}, False, redirect_path

    except APIError as e:
        return dash.no_update, dash.no_update, e.user_message(), \
               {"display": "block"}, {"display": "none"}, False, "/"
    except Exception as e:
        return dash.no_update, dash.no_update, "An unexpected error occurred. Please try again.", \
               {"display": "block"}, {"display": "none"}, False, "/"
