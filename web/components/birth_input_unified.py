"""
Stellium Web - Unified Birth Input Component

A birth input that can toggle between:
1. Manual entry (name, date, time, location)
2. Notable selection (search famous charts)
"""

from components.location_input import create_location_input
from components.notable_selector import create_notable_autocomplete
from components.time_input import (
    create_time_input,
    parse_24h_to_components,
    parse_time_to_24h,
)
from config import COLORS
from nicegui import ui
from state import ChartState


def create_unified_birth_input(
    state: ChartState,
    on_change=None,
    on_notable_select=None,
    label: str = "BIRTH DETAILS",
    show_notable_toggle: bool = True,
):
    """
    Create a unified birth input with manual/notable toggle.

    Args:
        state: ChartState instance to bind to
        on_change: Callback when any field changes
        on_notable_select: Callback when a notable is selected (receives Notable object)
        label: Section label
        show_notable_toggle: Whether to show the toggle (disable for explore page)

    Returns:
        Reference to the container element.
    """

    # Local state for input mode
    mode_state = {"mode": "manual"}  # "manual" or "notable"

    # UI references for refreshing
    refs = {
        "form_container": None,
    }

    def update_field(field: str, value):
        setattr(state, field, value)
        if on_change:
            on_change()

    def on_time_change(hour: str, minute: str, period: str):
        """Convert time components to 24h format and update state."""
        time_24h = parse_time_to_24h(hour, minute, period)
        update_field("time", time_24h)

    def on_location_change(value: str):
        """Update location in state."""
        update_field("location", value)

    def on_notable_selected(notable):
        """Handle notable selection - fill in all fields from notable."""
        # Fill state from notable
        state.name = notable.name
        state.location = notable.location.name

        # Format date
        dt = notable.datetime.local_datetime
        state.date = dt.strftime("%Y-%m-%d")
        state.time = dt.strftime("%H:%M")
        state.time_unknown = False

        if on_change:
            on_change()

        if on_notable_select:
            on_notable_select(notable)

        # Refresh the form to show filled values
        refresh_form()

        ui.notify(f"Loaded: {notable.name}", type="positive")

    def on_mode_change(e):
        """Handle mode toggle change."""
        mode_state["mode"] = e.value
        refresh_form()

    def refresh_form():
        """Refresh the form based on current mode."""
        if refs["form_container"]:
            refs["form_container"].clear()
            with refs["form_container"]:
                create_form_content()

    def create_form_content():
        """Create the form content based on mode."""
        # Parse existing time to components
        hour, minute, period = parse_24h_to_components(state.time)

        if mode_state["mode"] == "notable":
            # Notable search mode
            with ui.column().classes("gap-4 w-full"):
                ui.label("Search famous charts:").classes("text-sm").style(
                    f"color: {COLORS['text_muted']}"
                )
                create_notable_autocomplete(
                    on_select=on_notable_selected,
                    placeholder="Type a name...",
                )

                # Show current selection if any
                if state.name:
                    with (
                        ui.element("div")
                        .classes("p-3 rounded mt-2")
                        .style(f"background-color: {COLORS['cream']}; border: 1px solid {COLORS['border']};")
                    ):
                        ui.label("Selected:").classes("text-xs").style(
                            f"color: {COLORS['text_muted']}"
                        )
                        ui.label(state.name).classes("font-medium").style(
                            f"color: {COLORS['text']}"
                        )
                        if state.date:
                            ui.label(f"{state.date} {state.time}").classes("text-sm").style(
                                f"color: {COLORS['text_muted']}"
                            )
                        if state.location:
                            ui.label(state.location).classes("text-sm").style(
                                f"color: {COLORS['accent']}"
                            )

        else:
            # Manual entry mode
            with ui.column().classes("gap-6 w-full"):
                # Name field
                with ui.row().classes("items-center gap-4 w-full"):
                    ui.label("Name:").classes("w-28 flex-shrink-0 text-base").style(
                        f"color: {COLORS['text']}"
                    )
                    ui.input(
                        value=state.name,
                        placeholder="(optional)",
                        on_change=lambda e: update_field("name", e.value),
                    ).classes("minimal-input flex-grow").props("borderless dense")

                # Location field with autocomplete
                with ui.row().classes("items-center gap-4 w-full"):
                    ui.label("Birth place:").classes("w-28 flex-shrink-0 text-base").style(
                        f"color: {COLORS['text']}"
                    )
                    with ui.element("div").classes("flex-grow"):
                        create_location_input(
                            value=state.location,
                            placeholder="City, State, Country",
                            on_change=on_location_change,
                        )

                # Date field
                with ui.row().classes("items-center gap-4 w-full"):
                    ui.label("Birth date:").classes("w-28 flex-shrink-0 text-base").style(
                        f"color: {COLORS['text']}"
                    )
                    ui.input(
                        value=state.date,
                        placeholder="YYYY-MM-DD",
                        on_change=lambda e: update_field("date", e.value),
                    ).classes("minimal-input flex-grow").props("borderless dense")

                # Time field with hour/minute/AM-PM
                with ui.row().classes("items-center gap-4 w-full"):
                    ui.label("Birth time:").classes("w-28 flex-shrink-0 text-base").style(
                        f"color: {COLORS['text']}"
                    )
                    with ui.element("div").classes("flex-grow"):
                        create_time_input(
                            hour_value=hour,
                            minute_value=minute,
                            period_value=period,
                            on_change=on_time_change,
                            disabled=state.time_unknown,
                        )

                # Unknown time checkbox
                ui.checkbox(
                    "I don't know my birth time",
                    value=state.time_unknown,
                    on_change=lambda e: update_field("time_unknown", e.value),
                ).classes("mt-2").style(f"color: {COLORS['text_muted']}")

    # Build the UI
    with ui.element("div").classes("w-full") as container:
        # Section label with optional toggle
        with ui.row().classes("items-center justify-between w-full mb-4"):
            ui.label(f"☆  {label}").classes(
                "font-display text-xs tracking-[0.2em]"
            ).style(f"color: {COLORS['primary']}")

            if show_notable_toggle:
                ui.toggle(
                    {"manual": "Enter", "notable": "Famous"},
                    value=mode_state["mode"],
                    on_change=on_mode_change,
                ).props("dense no-caps")

        # Form container
        refs["form_container"] = ui.element("div").classes("w-full")
        with refs["form_container"]:
            create_form_content()

    return container
