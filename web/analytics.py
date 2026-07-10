"""
Stellium Web - Analytics Event Tracking

Centralized event tracking via Umami. All tracking calls go through this
module so switching providers (e.g., self-hosted Umami) requires changing
only the SCRIPT_URL constant.

Usage:
    from analytics import track_event

    # Track a chart generation
    track_event("chart-generated", {"page": "natal", "type": "natal"})

    # Track a download
    track_event("svg-downloaded", {"page": "natal"})
"""

from nicegui import ui

# -----------------------------------------------------------------------
# Configuration — change these if you self-host or switch providers.
# -----------------------------------------------------------------------
SCRIPT_URL = "https://cloud.umami.is/script.js"
WEBSITE_ID = "9dba0c8a-b33a-4c19-a659-46b09218dbc6"

# -----------------------------------------------------------------------
# Event names (constants to prevent typos)
# -----------------------------------------------------------------------
CHART_GENERATED = "chart-generated"
SVG_DOWNLOADED = "svg-downloaded"
PDF_DOWNLOADED = "pdf-downloaded"
PLANNER_GENERATED = "planner-generated"
GITHUB_CLICKED = "github-clicked"


def tracking_script() -> str:
    """Return the <script> tag for the analytics provider.

    Used in setup_styles() to inject into <head>.
    """
    return f'<script defer src="{SCRIPT_URL}" data-website-id="{WEBSITE_ID}"></script>'


def track_event(event_name: str, data: dict | None = None) -> None:
    """Fire a custom analytics event via JavaScript.

    Args:
        event_name: Event name (use the constants above).
        data: Optional dict of event properties.
    """
    if data:
        # Convert Python dict to JS object literal
        props = ", ".join(f'"{k}": "{v}"' for k, v in data.items())
        js = f'if (typeof umami !== "undefined") umami.track("{event_name}", {{{props}}})'
    else:
        js = f'if (typeof umami !== "undefined") umami.track("{event_name}")'

    ui.run_javascript(js)
