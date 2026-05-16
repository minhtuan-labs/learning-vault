import dash_bootstrap_components as dbc
from dash import html, dcc


def create_alert(message: str, color: str = "info", id: str = None, dismissable: bool = True):
    """Create an alert component."""
    return dbc.Alert(
        message,
        color=color,
        id=id,
        dismissable=dismissable,
        className="mb-3"
    )


def create_error_alert(message: str = None, id: str = "error-alert"):
    """Create error alert (displayed conditionally)."""
    return dbc.Alert(
        [
            html.I(className="fas fa-exclamation-circle me-2"),
            html.Span(message or "An error occurred. Please try again.")
        ],
        color="danger",
        id=id,
        dismissable=True,
        className="mb-3",
        style={"display": "none"}
    )


def create_success_alert(message: str = None, id: str = "success-alert"):
    """Create success alert."""
    return dbc.Alert(
        [
            html.I(className="fas fa-check-circle me-2"),
            html.Span(message or "Success!")
        ],
        color="success",
        id=id,
        dismissable=True,
        className="mb-3",
        style={"display": "none"}
    )


def create_loading_spinner(message: str = "Loading...", id: str = None):
    """Create loading spinner."""
    return html.Div(
        [
            dbc.Spinner(color="primary", size="sm", className="me-2"),
            html.Span(message)
        ],
        id=id,
        style={"display": "none"}
    )
