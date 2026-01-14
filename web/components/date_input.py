"""
Stellium Web - Date Input Component

A date input with:
- Text field for keyboard entry (YYYY-MM-DD format)
- Calendar picker button for visual selection
- Real-time validation with visual feedback
"""

from datetime import datetime

from config import COLORS
from nicegui import ui


def validate_date(date_str: str) -> tuple[bool, str]:
    """
    Validate a date string.

    Args:
        date_str: Date string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_str:
        return True, ""  # Empty is valid (will be caught by form submission)

    # Check format
    if len(date_str) < 10:
        return False, "Use format YYYY-MM-DD"

    # Try to parse
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")

        # Check reasonable year range for astrology (1 CE to 2200)
        if parsed.year < 1:
            return False, "Year must be 1 or later"
        if parsed.year > 2200:
            return False, "Year must be before 2200"

        return True, ""
    except ValueError as e:
        error_msg = str(e)
        if "day is out of range" in error_msg:
            return False, "Invalid day for this month"
        elif "month must be in" in error_msg:
            return False, "Month must be 1-12"
        else:
            return False, "Use format YYYY-MM-DD"


def create_date_input(
    value: str = "",
    placeholder: str = "YYYY-MM-DD",
    on_change=None,
    show_validation: bool = True,
):
    """
    Create a date input with validation and optional date picker.

    Args:
        value: Initial date value (YYYY-MM-DD format)
        placeholder: Placeholder text
        on_change: Callback when value changes (receives date string)
        show_validation: Whether to show validation feedback

    Returns:
        Dict with references to update/access the input
    """

    # State
    state = {
        "value": value,
        "is_valid": True,
        "error_message": "",
    }

    # UI references
    refs = {
        "input": None,
        "error_label": None,
        "picker_menu": None,
    }

    def update_validation(date_str: str):
        """Update validation state and visual feedback."""
        is_valid, error_msg = validate_date(date_str)
        state["is_valid"] = is_valid
        state["error_message"] = error_msg

        if refs["input"]:
            if not date_str:
                # Empty - neutral styling
                refs["input"].style(
                    remove="border-color: #ef4444; border-color: #22c55e;"
                )
            elif is_valid:
                # Valid - green border
                refs["input"].style(
                    remove="border-color: #ef4444;",
                    add="border-color: #22c55e;",
                )
            else:
                # Invalid - red border
                refs["input"].style(
                    remove="border-color: #22c55e;",
                    add="border-color: #ef4444;",
                )

        if refs["error_label"] and show_validation:
            if error_msg:
                refs["error_label"].set_text(error_msg)
                refs["error_label"].set_visibility(True)
            else:
                refs["error_label"].set_visibility(False)

    def on_input_change(e):
        """Handle text input change."""
        date_str = e.value or ""
        state["value"] = date_str
        update_validation(date_str)

        if on_change:
            on_change(date_str)

    def on_picker_change(e):
        """Handle date picker selection."""
        date_str = e.value
        state["value"] = date_str

        # Update text input
        if refs["input"]:
            refs["input"].value = date_str

        update_validation(date_str)

        # Close menu
        if refs["picker_menu"]:
            refs["picker_menu"].close()

        if on_change:
            on_change(date_str)

    # Build UI
    with ui.column().classes("w-full gap-1"):
        with ui.row().classes("items-center gap-2 w-full"):
            # Text input
            refs["input"] = (
                ui.input(
                    value=state["value"],
                    placeholder=placeholder,
                    on_change=on_input_change,
                )
                .classes("minimal-input flex-grow")
                .props("borderless dense mask='####-##-##'")
                .style(
                    f"color: {COLORS['text']}; "
                    "border-bottom: 2px solid transparent; "
                    "transition: border-color 0.2s;"
                )
            )

            # Calendar picker button
            with (
                ui.button(icon="event", color=None)
                .props("flat dense round")
                .classes("text-gray-500") as _picker_btn
            ):
                # Don't use auto-close - it closes when clicking year/month dropdowns
                # We manually close in on_picker_change when a date is actually selected
                refs["picker_menu"] = ui.menu()
                with refs["picker_menu"]:
                    ui.date(
                        value=state["value"] if state["value"] else None,
                        on_change=on_picker_change,
                    ).props("minimal")

        # Error message (hidden by default)
        if show_validation:
            refs["error_label"] = (
                ui.label("")
                .classes("text-xs")
                .style("color: #ef4444; margin-top: 2px;")
            )
            refs["error_label"].set_visibility(False)

    # Initial validation if value provided
    if value:
        update_validation(value)

    return {
        "get_value": lambda: state["value"],
        "is_valid": lambda: state["is_valid"],
        "set_value": lambda v: on_input_change(type("Event", (), {"value": v})()),
        "input_ref": refs["input"],
    }
