"""
Stellium Web - Header Component

Site header with logo, navigation, language selector, and user actions.
"""

from config import COLORS
from i18n import get_available_locales, get_user_locale, set_user_locale, wt
from nicegui import ui


def create_header():
    """Create the site header with language selector."""

    with (
        ui.element("header")
        .classes("w-full py-4 px-6 border-b")
        .style(
            f"border-color: {COLORS['border']}; background-color: {COLORS['cream']};"
        )
    ):
        with ui.element("div").classes(
            "w-full max-w-6xl mx-auto flex items-center justify-between"
        ):
            # Left spacer (for centering the logo)
            ui.element("div").classes("w-24")

            # Center: Logo (clickable link to home)
            with (
                ui.element("a").classes("no-underline cursor-pointer").props('href="/"')
            ):
                with ui.row().classes("items-center gap-2"):
                    ui.label("★").classes("text-sm").style(f"color: {COLORS['gold']}")
                    ui.label("Stellium").classes(
                        "font-display text-2xl md:text-3xl tracking-wide"
                    ).style(f"color: {COLORS['text']}")
                    ui.label("★").classes("text-sm").style(f"color: {COLORS['gold']}")

            # Right: Language selector
            locales = get_available_locales()
            if len(locales) > 1:
                ui.select(
                    options=locales,
                    value=get_user_locale(),
                    on_change=lambda e: _change_language(e.value),
                ).classes("w-24").props("dense borderless").style(
                    f"color: {COLORS['text_muted']}; font-size: 0.75rem;"
                )
            else:
                ui.element("div").classes("w-24")


def _change_language(locale: str) -> None:
    """Change language and reload the page."""
    set_user_locale(locale)
    ui.navigate.reload()


def create_nav():
    """Create the navigation bar."""
    _ = wt()

    nav_items = [
        (_("HOME"), "/"),
        (_("BIRTH CHART"), "/natal"),
        (_("RELATIONSHIPS"), "/relationships"),
        (_("TIMING"), "/timing"),
        (_("PLANNER"), "/planner"),
        (_("EXPLORE"), "/explore"),
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
                    "nav-link no-underline text-xs tracking-[0.2em]"
                )
