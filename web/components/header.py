"""
Stellium Web - Header Component

Site header with logo, navigation, and user actions.
"""

from config import COLORS
from nicegui import ui


def create_header():
    """Create the site header."""

    with (
        ui.element("header")
        .classes("w-full py-4 px-6 border-b")
        .style(
            f"border-color: {COLORS['border']}; background-color: {COLORS['cream']};"
        )
    ):
        with ui.element("div").classes(
            "w-full max-w-6xl mx-auto flex items-center justify-center"
        ):
            # Center: Logo (clickable link to home)
            with ui.element("a").classes("no-underline cursor-pointer").props('href="/"'):
                with ui.row().classes("items-center gap-2"):
                    ui.label("★").classes("text-sm").style(f"color: {COLORS['gold']}")
                    ui.label("Stellium").classes(
                        "font-display text-2xl md:text-3xl tracking-wide"
                    ).style(f"color: {COLORS['text']}")
                    ui.label("★").classes("text-sm").style(f"color: {COLORS['gold']}")


def create_nav():
    """Create the navigation bar."""

    nav_items = [
        ("HOME", "/"),
        ("BIRTH CHART", "/natal"),
        ("RELATIONSHIPS", "/relationships"),
        ("TIMING", "/timing"),
        ("EXPLORE", "/explore"),
    ]

    with (
        ui.element("nav")
        .classes("w-full py-3 border-b")
        .style(
            f"border-color: {COLORS['border']}; background-color: {COLORS['cream']};"
        )
    ):
        with ui.row().classes("max-w-4xl mx-auto justify-center gap-8 md:gap-12"):
            for label, href in nav_items:
                ui.link(label, href, new_tab=False).classes(
                    "no-underline text-xs tracking-[0.2em] transition-colors"
                ).style(f"color: {COLORS['text_muted']}")
