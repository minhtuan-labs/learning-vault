import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime


def create_transaction_modal(categories: list = None):
    """Create modal for logging a new transaction."""
    if categories is None:
        categories = []

    category_options = [{"label": c.get("name", ""), "value": c.get("id")} for c in categories]

    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Log Transaction"), close_button=True),
        dbc.ModalBody([
            dbc.FormGroup([
                dbc.Label("Type", className="form-label fw-bold"),
                dcc.RadioItems(
                    id="txn-type-radio",
                    options=[
                        {"label": " Income", "value": "income"},
                        {"label": " Expense", "value": "expense"},
                        {"label": " Investment", "value": "investment"}
                    ],
                    value="expense",
                    inline=True,
                    className="mb-3"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Category", className="form-label fw-bold"),
                dcc.Dropdown(
                    id="txn-category-dropdown",
                    options=category_options,
                    placeholder="Select category...",
                    clearable=False,
                    className="form-control"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Amount", className="form-label fw-bold"),
                dbc.Input(
                    id="txn-amount-input",
                    type="number",
                    min=0,
                    step=0.01,
                    placeholder="0.00",
                    className="form-control"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Date", className="form-label fw-bold"),
                dcc.DatePickerSingle(
                    id="txn-date-picker",
                    date=datetime.today(),
                    display_format="YYYY-MM-DD",
                    className="form-control"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Notes (optional)", className="form-label fw-bold"),
                dbc.Textarea(
                    id="txn-notes-input",
                    rows=3,
                    placeholder="Add notes...",
                    className="form-control"
                )
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="txn-cancel-btn", color="secondary"),
            dbc.Button("Save Transaction", id="txn-submit-btn", color="primary")
        ])
    ], id="transaction-modal", size="lg")


def create_invite_member_modal():
    """Create modal for inviting a family member."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Invite Member"), close_button=True),
        dbc.ModalBody([
            dbc.FormGroup([
                dbc.Label("Email", className="form-label fw-bold"),
                dbc.Input(
                    id="invite-email-input",
                    type="email",
                    placeholder="member@example.com",
                    className="form-control"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Role", className="form-label fw-bold"),
                dcc.Dropdown(
                    id="invite-role-dropdown",
                    options=[
                        {"label": "Member (can edit)", "value": "member"},
                        {"label": "View Only", "value": "view_only"}
                    ],
                    value="member",
                    clearable=False,
                    className="form-control"
                )
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="invite-cancel-btn", color="secondary"),
            dbc.Button("Send Invite", id="invite-submit-btn", color="primary")
        ])
    ], id="invite-modal", size="lg")


def create_confirm_delete_modal(item_type: str = "item"):
    """Create modal for confirming delete action."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Confirm Delete"), close_button=True),
        dbc.ModalBody(f"Are you sure you want to delete this {item_type}? This action cannot be undone."),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="confirm-cancel-btn", color="secondary"),
            dbc.Button("Delete", id="confirm-delete-btn", color="danger")
        ])
    ], id="confirm-modal", size="sm")


def create_category_form_modal():
    """Create modal for adding/editing a category."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add Category"), close_button=True),
        dbc.ModalBody([
            dbc.FormGroup([
                dbc.Label("Name", className="form-label fw-bold"),
                dbc.Input(
                    id="cat-name-input",
                    placeholder="Category name",
                    className="form-control"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Type", className="form-label fw-bold"),
                dcc.Dropdown(
                    id="cat-type-dropdown",
                    options=[
                        {"label": "Income", "value": "income"},
                        {"label": "Expense", "value": "expense"},
                        {"label": "Investment", "value": "investment"}
                    ],
                    value="expense",
                    clearable=False,
                    className="form-control"
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Color", className="form-label fw-bold"),
                dbc.Input(
                    id="cat-color-input",
                    type="color",
                    value="#2563eb",
                    className="form-control",
                    style={"height": "40px"}
                )
            ]),
            dbc.FormGroup([
                dbc.Label("Icon (optional)", className="form-label fw-bold"),
                dcc.Dropdown(
                    id="cat-icon-dropdown",
                    options=[
                        {"label": "💰 Dollar", "value": "dollar-sign"},
                        {"label": "🛒 Shopping Cart", "value": "shopping-cart"},
                        {"label": "⚡ Zap", "value": "zap"},
                        {"label": "🍔 Food", "value": "coffee"},
                        {"label": "🚗 Car", "value": "truck"},
                        {"label": "🏥 Health", "value": "heart"},
                        {"label": "🎬 Entertainment", "value": "film"},
                        {"label": "📱 Phone", "value": "smartphone"},
                        {"label": "🏠 Home", "value": "home"},
                    ],
                    placeholder="Select icon...",
                    className="form-control"
                )
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="cat-cancel-btn", color="secondary"),
            dbc.Button("Save Category", id="cat-submit-btn", color="primary")
        ])
    ], id="category-modal", size="lg")
