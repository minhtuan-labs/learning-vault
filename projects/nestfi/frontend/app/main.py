import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import os

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, use_pages=True, pages_folder="pages")

# Configure meta tags
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Configure external stylesheets
app.config.external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
]

# Set up app layout with multi-page router
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    dash.page_container
], fluid=True, className="p-0")

# Suppress callback exceptions (multi-page pages have different callbacks)
app.config.suppress_callback_exceptions = True

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
