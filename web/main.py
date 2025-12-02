#!/usr/bin/env python3
"""
Stellium Web - Main Entry Point

A beautiful web interface for the Stellium astrology library.

Usage:
    cd web
    python main.py

    # Or from repo root:
    python web/main.py

Then visit http://localhost:8080
"""

from config import COLORS, FONTS, GOOGLE_FONTS_URL
from nicegui import ui
from pages.explore import create_explore_page
from pages.home import create_home_page
from pages.natal import create_natal_page
from pages.relationships import create_relationships_page
from pages.timing import create_timing_page

# =============================================================================
# GLOBAL STYLES
# =============================================================================


def setup_styles():
    """Add global CSS styles and fonts."""

    # Set Quasar's color palette using NiceGUI's built-in method
    ui.colors(
        primary=COLORS["primary"],
        secondary=COLORS["secondary"],
        accent=COLORS["accent"],
        positive=COLORS["primary"],
        warning=COLORS["gold"],
    )

    ui.add_head_html(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="{GOOGLE_FONTS_URL}" rel="stylesheet">
    <style>
        /* Base styles */
        body {{
            font-family: 'Crimson Pro', serif;
            background-color: {COLORS["cream"]};
            color: {COLORS["text"]};
        }}

        /* Typography */
        .font-display {{ font-family: '{FONTS["display"]}', serif; }}

        /* Links */
        a {{ color: {COLORS["gold"]}; }}
        a:hover {{ color: {COLORS["primary"]}; }}

        /* Nav links */
        .nav-link {{
            color: {COLORS["text_muted"]} !important;
            transition: color 0.2s ease !important;
        }}
        .nav-link:hover {{
            color: {COLORS["gold"]} !important;
        }}

        /* Remove NiceGUI default padding */
        .nicegui-content {{
            padding: 0 !important;
        }}

        /* Underline-only inputs */
        .minimal-input .q-field__control {{
            background: transparent !important;
        }}
        .minimal-input .q-field__control:before,
        .minimal-input .q-field__control:after {{
            display: none !important;
        }}
        .minimal-input .q-field__native {{
            border: none !important;
            border-bottom: 1px solid {COLORS["text"]} !important;
            border-radius: 0 !important;
            padding: 8px 0 !important;
            font-family: 'Crimson Pro', serif !important;
            font-size: 1.1rem !important;
            color: {COLORS["text"]} !important;
        }}
        .minimal-input .q-field__native:focus {{
            border-bottom-color: {COLORS["secondary"]} !important;
        }}
        .minimal-input .q-field__native::placeholder {{
            color: {COLORS["accent"]} !important;
        }}

        /* Checkbox/Radio styling */
        .q-checkbox__inner--truthy, .q-radio__inner--truthy {{
            color: {COLORS["secondary"]} !important;
        }}

        /* Toggle/Button-toggle styling - flat and subtle */
        .q-btn-toggle {{
            border: none !important;
            border-radius: 0.25rem !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
        /* All toggle buttons - base typography */
        .q-btn-toggle .q-btn {{
            font-family: 'Crimson Pro', serif !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em !important;
            padding: 2px 8px !important;
            min-height: 24px !important;
            box-shadow: none !important;
        }}
        /* Inactive toggle buttons */
        .q-btn-toggle .q-btn:not(.q-btn--active) {{
            color: {COLORS["text_muted"]} !important;
            background-color: transparent !important;
        }}
        .q-btn-toggle .q-btn:not(.q-btn--active):hover {{
            color: {COLORS["text"]} !important;
            background-color: {COLORS["cream_dark"]} !important;
        }}
        /* Active toggle button */
        .q-btn-toggle .q-btn.q-btn--active {{
            color: {COLORS["primary"]} !important;
            background-color: {COLORS["cream_dark"]} !important;
            font-weight: 600 !important;
        }}
        /* Remove inner borders between toggle buttons */
        .q-btn-toggle .q-btn + .q-btn {{
            border-left: none !important;
        }}

        /* Button styling - override Quasar defaults */
        .q-btn {{
            font-family: 'Crimson Pro', serif !important;
            letter-spacing: 0.05em;
        }}

        /* Primary filled buttons */
        .q-btn--standard:not(.q-btn--outline) {{
            background-color: {COLORS["primary"]} !important;
            color: white !important;
        }}
        .q-btn--standard:not(.q-btn--outline):hover {{
            background-color: {COLORS["secondary"]} !important;
        }}

        /* Outline buttons */
        .q-btn--outline {{
            color: {COLORS["primary"]} !important;
            border-color: {COLORS["primary"]} !important;
        }}
        .q-btn--outline:hover {{
            background-color: {COLORS["cream_dark"]} !important;
        }}

        /* Flat buttons (icon buttons, etc) */
        .q-btn--flat {{
            color: {COLORS["text"]} !important;
        }}
        .q-btn--flat:hover {{
            background-color: {COLORS["cream_dark"]} !important;
        }}

        /* Gold accent buttons */
        .btn-gold.q-btn--outline {{
            color: {COLORS["gold"]} !important;
            border-color: {COLORS["gold"]} !important;
        }}
        .btn-gold.q-btn--outline:hover {{
            background-color: rgba(184, 149, 61, 0.1) !important;
        }}

        /* Expansion panel styling */
        .q-expansion-item__container {{
            border: 1px solid {COLORS["border"]} !important;
            border-radius: 0.25rem !important;
            margin-bottom: 0.5rem !important;
        }}

        /* Selection highlight */
        ::selection {{
            background-color: {COLORS["accent"]};
            color: white;
        }}

        /* Scrollbar styling (webkit) */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {COLORS["cream_dark"]};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {COLORS["accent"]};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS["secondary"]};
        }}
    </style>
    """)


# =============================================================================
# PAGES
# =============================================================================


@ui.page("/")
async def home():
    """Home/landing page."""
    setup_styles()
    create_home_page()


@ui.page("/natal")
async def natal():
    """Natal chart builder page."""
    setup_styles()
    create_natal_page()


@ui.page("/relationships")
async def relationships():
    """Relationships chart page (synastry, composite, davison)."""
    setup_styles()
    create_relationships_page()


@ui.page("/timing")
async def timing():
    """Timing chart page (transits, progressions, returns)."""
    setup_styles()
    create_timing_page()


@ui.page("/explore")
async def explore():
    """Notable births explorer."""
    setup_styles()
    create_explore_page()


# =============================================================================
# MAIN
# =============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    import os

    # Get port from environment (Railway sets PORT), default to 8080 for local dev
    port = int(os.environ.get("PORT", 8080))

    # Check if running in production (Railway sets RAILWAY_ENVIRONMENT)
    is_production = os.environ.get("RAILWAY_ENVIRONMENT") is not None

    # Only print startup message in main process (not multiprocessing worker)
    if __name__ == "__main__":
        print("\n" + "=" * 50)
        print("  ★  Stellium Web  ★")
        print("=" * 50)
        print(f"\n  Starting server on port {port}\n")

    ui.run(
        title="Stellium",
        favicon="★",
        host="0.0.0.0",  # Bind to all interfaces (required for Railway)
        port=port,
        reload=not is_production,  # Hot reload only in development
        show=False,  # Don't auto-open browser
    )
