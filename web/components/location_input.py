"""
Stellium Web - Location Autocomplete Component

A location input with autocomplete suggestions using Nominatim (OpenStreetMap).
Debounces input and shows dropdown with matching locations.
"""

import asyncio
from collections.abc import Callable

from config import COLORS
from geopy.geocoders import Nominatim
from nicegui import ui

# Geocoder instance (reused for all queries)
_geolocator = Nominatim(user_agent="stellium_web_autocomplete")


async def search_locations(query: str, limit: int = 5) -> list[dict]:
    """
    Search for locations matching the query.

    Args:
        query: Search string (city, address, etc.)
        limit: Maximum number of results

    Returns:
        List of location dicts with display_name, lat, lon
    """
    if not query or len(query) < 3:
        return []

    try:
        # Run geocoding in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: _geolocator.geocode(
                query,
                exactly_one=False,
                limit=limit,
                addressdetails=True,
            ),
        )

        if not results:
            return []

        locations = []
        for loc in results:
            # Build a nice display name
            address = loc.raw.get("address", {})

            # Try to build a sensible short name
            parts = []
            if address.get("city"):
                parts.append(address["city"])
            elif address.get("town"):
                parts.append(address["town"])
            elif address.get("village"):
                parts.append(address["village"])
            elif address.get("municipality"):
                parts.append(address["municipality"])

            if address.get("state"):
                parts.append(address["state"])
            elif address.get("region"):
                parts.append(address["region"])

            if address.get("country"):
                parts.append(address["country"])

            short_name = ", ".join(parts) if parts else loc.address

            locations.append(
                {
                    "display_name": loc.address,
                    "short_name": short_name,
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                }
            )

        return locations

    except Exception as e:
        print(f"Geocoding error: {e}")
        return []


def create_location_input(
    value: str = "",
    placeholder: str = "City, Country",
    on_change: Callable[[str], None] | None = None,
    on_select: Callable[[dict], None] | None = None,
    debounce_ms: int = 400,
):
    """
    Create a location input with autocomplete dropdown.

    Args:
        value: Initial value
        placeholder: Placeholder text
        on_change: Callback when text changes (receives the text value)
        on_select: Callback when a location is selected (receives full location dict)
        debounce_ms: Milliseconds to wait before searching

    Returns:
        Reference to the input element
    """

    # State
    state = {
        "value": value,
        "suggestions": [],
        "show_dropdown": False,
        "debounce_timer": None,
        "selected_location": None,
    }

    # UI references
    refs = {
        "dropdown": None,
        "input": None,
    }

    async def do_search(query: str):
        """Perform the search and update suggestions."""
        if len(query) < 3:
            state["suggestions"] = []
            state["show_dropdown"] = False
            if refs["dropdown"]:
                refs["dropdown"].set_visibility(False)
            return

        results = await search_locations(query)
        state["suggestions"] = results
        state["show_dropdown"] = len(results) > 0

        # Update dropdown
        if refs["dropdown"]:
            refs["dropdown"].clear()
            with refs["dropdown"]:
                for loc in results:
                    create_suggestion_item(loc)
            refs["dropdown"].set_visibility(state["show_dropdown"])

    def create_suggestion_item(loc: dict):
        """Create a clickable suggestion item."""
        with (
            ui.element("div")
            .classes("px-3 py-2 cursor-pointer hover:bg-gray-100")
            .style(f"border-bottom: 1px solid {COLORS['border']};")
            .on("click", lambda loc=loc: select_location(loc))
        ):
            # Short name (prominent)
            ui.label(loc["short_name"]).classes("text-sm font-medium").style(
                f"color: {COLORS['text']}"
            )
            # Full address (smaller)
            if loc["display_name"] != loc["short_name"]:
                ui.label(loc["display_name"]).classes("text-xs truncate").style(
                    f"color: {COLORS['text_muted']}; max-width: 300px;"
                )

    def select_location(loc: dict):
        """Handle location selection."""
        state["value"] = loc["short_name"]
        state["selected_location"] = loc
        state["show_dropdown"] = False

        # Update input
        if refs["input"]:
            refs["input"].value = loc["short_name"]

        # Hide dropdown
        if refs["dropdown"]:
            refs["dropdown"].set_visibility(False)

        # Callbacks
        if on_change:
            on_change(loc["short_name"])
        if on_select:
            on_select(loc)

    async def on_input_change(e):
        """Handle input change with debouncing."""
        query = e.value or ""
        state["value"] = query

        # Clear selected location when user types
        state["selected_location"] = None

        # Notify change
        if on_change:
            on_change(query)

        # Debounced search
        await do_search(query)

    def on_blur(e):
        """Hide dropdown when input loses focus (with delay for click)."""

        async def delayed_hide():
            await asyncio.sleep(0.2)  # Allow click to register
            state["show_dropdown"] = False
            if refs["dropdown"]:
                refs["dropdown"].set_visibility(False)

        asyncio.create_task(delayed_hide())

    def on_focus(e):
        """Show dropdown if we have suggestions."""
        if state["suggestions"]:
            state["show_dropdown"] = True
            if refs["dropdown"]:
                refs["dropdown"].set_visibility(True)

    # Build the UI
    with ui.element("div").classes("relative w-full"):
        # Input field
        refs["input"] = (
            ui.input(
                value=state["value"],
                placeholder=placeholder,
                on_change=on_input_change,
            )
            .classes("minimal-input w-full")
            .props(f"borderless dense debounce={debounce_ms}")
            .on("blur", on_blur)
            .on("focus", on_focus)
        )

        # Dropdown container (absolute positioned)
        refs["dropdown"] = (
            ui.element("div")
            .classes("absolute left-0 right-0 z-50 rounded shadow-lg overflow-hidden")
            .style(
                f"background-color: {COLORS['white']}; "
                f"border: 1px solid {COLORS['border']}; "
                f"max-height: 250px; overflow-y: auto; "
                f"top: 100%; margin-top: 4px;"
            )
        )
        refs["dropdown"].set_visibility(False)

    return refs["input"]
