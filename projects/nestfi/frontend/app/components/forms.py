import dash_bootstrap_components as dbc
from dash import html, dcc


def create_text_input(label: str, id: str, placeholder: str = "", required: bool = False, type: str = "text"):
    """Reusable text input component."""
    return dbc.FormFloating([
        dbc.Input(
            type=type,
            id=id,
            placeholder=placeholder,
            className="form-control",
            required=required
        ),
        dbc.Label(label)
    ])


def create_password_input(label: str, id: str, placeholder: str = "", required: bool = False):
    """Reusable password input component."""
    return create_text_input(label, id, placeholder, required, type="password")


def create_number_input(label: str, id: str, placeholder: str = "", min_val: float = 0, step: float = 0.01):
    """Reusable number input component."""
    return dbc.FormFloating([
        dbc.Input(
            type="number",
            id=id,
            placeholder=placeholder,
            min=min_val,
            step=step,
            className="form-control"
        ),
        dbc.Label(label)
    ])


def create_dropdown(label: str, id: str, options: list, value = None, multi: bool = False):
    """Reusable dropdown component."""
    return dbc.FormFloating([
        dcc.Dropdown(
            id=id,
            options=options,
            value=value,
            multi=multi,
            clearable=True,
            className="form-control p-2"
        ),
        dbc.Label(label)
    ])


def create_date_picker(label: str, id: str, date: str = None):
    """Reusable date picker component."""
    return dbc.FormFloating([
        dcc.DatePickerSingle(
            id=id,
            date=date,
            display_format="YYYY-MM-DD",
            className="form-control"
        ),
        dbc.Label(label)
    ])


def create_textarea(label: str, id: str, placeholder: str = "", rows: int = 3):
    """Reusable textarea component."""
    return dbc.FormFloating([
        dbc.Textarea(
            id=id,
            placeholder=placeholder,
            rows=rows,
            className="form-control"
        ),
        dbc.Label(label)
    ])


def create_form_group(label: str, input_component, help_text: str = None, error_message: str = None):
    """Wrapper for form group with label and optional help text."""
    return dbc.FormGroup([
        dbc.Label(label, className="form-label fw-bold mb-2"),
        input_component,
        dbc.FormText(help_text, color="muted") if help_text else None,
        dbc.FormFeedback(error_message, type="invalid", className="d-block text-danger") if error_message else None
    ])
