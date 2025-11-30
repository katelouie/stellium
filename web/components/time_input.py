"""
Stellium Web - Time Input Component

A user-friendly time input with separate hour/minute fields and AM/PM toggle.
Auto-advances from hour to minute after typing 2 digits.
"""

from config import COLORS
from nicegui import ui


def create_time_input(
    hour_value: str = "",
    minute_value: str = "",
    period_value: str = "AM",
    on_change=None,
    disabled: bool = False,
):
    """
    Create a time input with separate hour, minute, and AM/PM fields.

    Args:
        hour_value: Initial hour (1-12)
        minute_value: Initial minute (00-59)
        period_value: Initial period ("AM" or "PM")
        on_change: Callback when any value changes. Called with (hour, minute, period)
        disabled: Whether the input is disabled

    Returns:
        A dict with references to update values: {"hour": str, "minute": str, "period": str}
    """

    # State container
    state = {
        "hour": hour_value,
        "minute": minute_value,
        "period": period_value,
    }

    # References to UI elements
    refs = {
        "minute_input": None,
    }

    def notify_change():
        if on_change:
            on_change(state["hour"], state["minute"], state["period"])

    def on_hour_change(e):
        value = e.value or ""
        # Only allow digits
        digits = "".join(c for c in value if c.isdigit())

        # Limit to 2 digits
        if len(digits) > 2:
            digits = digits[:2]

        # Validate hour (1-12)
        if digits:
            hour_int = int(digits)
            if hour_int > 12:
                digits = "12"
            elif hour_int < 1 and len(digits) == 2:
                digits = "1"

        state["hour"] = digits
        e.sender.value = digits

        # Auto-advance to minute when 2 digits entered
        if len(digits) == 2 and refs["minute_input"]:
            refs["minute_input"].run_method("focus")
            refs["minute_input"].run_method("select")

        notify_change()

    def on_minute_change(e):
        value = e.value or ""
        # Only allow digits
        digits = "".join(c for c in value if c.isdigit())

        # Limit to 2 digits
        if len(digits) > 2:
            digits = digits[:2]

        # Validate minute (00-59)
        if digits and len(digits) == 2:
            minute_int = int(digits)
            if minute_int > 59:
                digits = "59"

        state["minute"] = digits
        e.sender.value = digits
        notify_change()

    def on_period_change(e):
        state["period"] = e.value
        notify_change()

    # Build the UI
    with ui.row().classes("items-center gap-1"):
        # Hour input
        hour_input = (
            ui.input(
                value=state["hour"],
                placeholder="HH",
                on_change=on_hour_change,
            )
            .classes("minimal-input")
            .props("borderless dense maxlength=2")
            .style(f"width: 3rem; text-align: center; color: {COLORS['text']};")
        )
        if disabled:
            hour_input.props("disable")

        # Colon separator
        ui.label(":").classes("text-lg font-bold").style(f"color: {COLORS['text']}")

        # Minute input
        minute_input = (
            ui.input(
                value=state["minute"],
                placeholder="MM",
                on_change=on_minute_change,
            )
            .classes("minimal-input")
            .props("borderless dense maxlength=2")
            .style(f"width: 3rem; text-align: center; color: {COLORS['text']};")
        )
        refs["minute_input"] = minute_input
        if disabled:
            minute_input.props("disable")

        # AM/PM toggle
        period_toggle = (
            ui.toggle(
                ["AM", "PM"],
                value=state["period"],
                on_change=on_period_change,
            )
            .props("dense no-caps")
            .classes("ml-2")
        )
        if disabled:
            period_toggle.props("disable")

    return state


def parse_time_to_24h(hour: str, minute: str, period: str) -> str:
    """
    Convert hour/minute/period to 24-hour format string.

    Args:
        hour: Hour string (1-12)
        minute: Minute string (00-59)
        period: "AM" or "PM"

    Returns:
        Time string in HH:MM format (24-hour)
    """
    if not hour or not minute:
        return ""

    try:
        h = int(hour)
        m = int(minute)

        # Convert to 24-hour
        if period == "AM":
            if h == 12:
                h = 0
        else:  # PM
            if h != 12:
                h += 12

        return f"{h:02d}:{m:02d}"
    except ValueError:
        return ""


def parse_24h_to_components(time_str: str) -> tuple[str, str, str]:
    """
    Parse a 24-hour time string into components.

    Args:
        time_str: Time in HH:MM format (24-hour)

    Returns:
        Tuple of (hour, minute, period) where hour is 1-12 and period is AM/PM
    """
    if not time_str or ":" not in time_str:
        return ("", "", "AM")

    try:
        parts = time_str.split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0

        # Convert to 12-hour
        if h == 0:
            hour = "12"
            period = "AM"
        elif h < 12:
            hour = str(h)
            period = "AM"
        elif h == 12:
            hour = "12"
            period = "PM"
        else:
            hour = str(h - 12)
            period = "PM"

        return (hour, f"{m:02d}", period)
    except ValueError:
        return ("", "", "AM")
