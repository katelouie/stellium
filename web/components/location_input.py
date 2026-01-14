"""
Stellium Web - Location Input Component

A location input that supports:
1. Place name search with autocomplete (using Nominatim/OpenStreetMap)
2. Manual coordinate entry (latitude/longitude)

Toggle between modes with a Place/Coords switch.
"""

import asyncio
from collections.abc import Callable

from config import COLORS
from geopy.geocoders import Nominatim
from nicegui import ui
from timezonefinder import TimezoneFinder

# Geocoder instance (reused for all queries)
_geolocator = Nominatim(user_agent="stellium_web_autocomplete")

# Timezone finder (lazy loaded)
_timezone_finder = None


def _get_timezone_finder():
    """Get cached TimezoneFinder instance."""
    global _timezone_finder
    if _timezone_finder is None:
        _timezone_finder = TimezoneFinder()
    return _timezone_finder


def validate_latitude(value: str) -> tuple[bool, str]:
    """Validate latitude value (-90 to 90)."""
    if not value:
        return True, ""
    try:
        lat = float(value)
        if lat < -90 or lat > 90:
            return False, "Must be -90 to 90"
        return True, ""
    except ValueError:
        return False, "Invalid number"


def validate_longitude(value: str) -> tuple[bool, str]:
    """Validate longitude value (-180 to 180)."""
    if not value:
        return True, ""
    try:
        lon = float(value)
        if lon < -180 or lon > 180:
            return False, "Must be -180 to 180"
        return True, ""
    except ValueError:
        return False, "Invalid number"


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

    def on_input_change(e):
        """Handle input change with debouncing."""
        query = e.value or ""
        state["value"] = query

        # Clear selected location when user types
        state["selected_location"] = None

        # Notify change
        if on_change:
            on_change(query)

        # Debounced search
        asyncio.create_task(do_search(query))

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


def create_location_input_with_coords(
    value: str = "",
    latitude: float | None = None,
    longitude: float | None = None,
    placeholder: str = "City, Country",
    on_change: Callable[[str], None] | None = None,
    on_select: Callable[[dict], None] | None = None,
    on_coords_change: Callable[[float | None, float | None], None] | None = None,
    initial_mode: str = "place",
):
    """
    Create a location input with Place/Coords toggle.

    Args:
        value: Initial place name value
        latitude: Initial latitude (for coords mode)
        longitude: Initial longitude (for coords mode)
        placeholder: Placeholder for place name input
        on_change: Callback when place name changes
        on_select: Callback when a location is selected from autocomplete
        on_coords_change: Callback when coordinates change (lat, lon)
        initial_mode: Starting mode ("place" or "coords")

    Returns:
        Dict with methods to access/update the input
    """

    # State
    state = {
        "mode": initial_mode,
        "place_value": value,
        "latitude": str(latitude) if latitude is not None else "",
        "longitude": str(longitude) if longitude is not None else "",
        "selected_location": None,
    }

    # UI references
    refs = {
        "content_container": None,
        "lat_input": None,
        "lon_input": None,
        "lat_error": None,
        "lon_error": None,
    }

    def update_coord_validation(which: str, value: str):
        """Update coordinate validation visuals."""
        if which == "lat":
            is_valid, error_msg = validate_latitude(value)
            if refs["lat_input"]:
                if not value:
                    refs["lat_input"].style(
                        remove="border-color: #ef4444; border-color: #22c55e;"
                    )
                elif is_valid:
                    refs["lat_input"].style(
                        remove="border-color: #ef4444;", add="border-color: #22c55e;"
                    )
                else:
                    refs["lat_input"].style(
                        remove="border-color: #22c55e;", add="border-color: #ef4444;"
                    )
            if refs["lat_error"]:
                refs["lat_error"].set_text(error_msg)
                refs["lat_error"].set_visibility(bool(error_msg))
        else:
            is_valid, error_msg = validate_longitude(value)
            if refs["lon_input"]:
                if not value:
                    refs["lon_input"].style(
                        remove="border-color: #ef4444; border-color: #22c55e;"
                    )
                elif is_valid:
                    refs["lon_input"].style(
                        remove="border-color: #ef4444;", add="border-color: #22c55e;"
                    )
                else:
                    refs["lon_input"].style(
                        remove="border-color: #22c55e;", add="border-color: #ef4444;"
                    )
            if refs["lon_error"]:
                refs["lon_error"].set_text(error_msg)
                refs["lon_error"].set_visibility(bool(error_msg))

    def on_lat_change(e):
        """Handle latitude input change."""
        value = e.value or ""
        state["latitude"] = value
        update_coord_validation("lat", value)
        notify_coords_change()

    def on_lon_change(e):
        """Handle longitude input change."""
        value = e.value or ""
        state["longitude"] = value
        update_coord_validation("lon", value)
        notify_coords_change()

    def notify_coords_change():
        """Notify callback of coordinate changes."""
        if on_coords_change:
            try:
                lat = float(state["latitude"]) if state["latitude"] else None
                lon = float(state["longitude"]) if state["longitude"] else None
                on_coords_change(lat, lon)
            except ValueError:
                pass  # Invalid number, don't callback

    def on_place_change(value: str):
        """Handle place name change."""
        state["place_value"] = value
        if on_change:
            on_change(value)

    def on_place_select(loc: dict):
        """Handle place selection from autocomplete."""
        state["selected_location"] = loc
        state["place_value"] = loc["short_name"]
        # Also update coordinates in state (for potential mode switch)
        state["latitude"] = str(loc["latitude"])
        state["longitude"] = str(loc["longitude"])
        if on_select:
            on_select(loc)

    def on_mode_change(e):
        """Handle mode toggle."""
        state["mode"] = e.value
        refresh_content()

        # If switching to coords and we have a selected location, show its coords
        if state["mode"] == "coords" and state["selected_location"]:
            loc = state["selected_location"]
            state["latitude"] = str(loc["latitude"])
            state["longitude"] = str(loc["longitude"])
            refresh_content()

    def refresh_content():
        """Refresh the content area based on mode."""
        if refs["content_container"]:
            refs["content_container"].clear()
            with refs["content_container"]:
                create_content()

    def create_content():
        """Create content based on current mode."""
        if state["mode"] == "place":
            # Place name search
            create_location_input(
                value=state["place_value"],
                placeholder=placeholder,
                on_change=on_place_change,
                on_select=on_place_select,
            )
        else:
            # Coordinate entry
            with ui.column().classes("gap-2 w-full"):
                # Latitude
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label("Lat:").classes("text-sm w-8").style(
                        f"color: {COLORS['text_muted']}"
                    )
                    refs["lat_input"] = (
                        ui.input(
                            value=state["latitude"],
                            placeholder="-90 to 90",
                            on_change=on_lat_change,
                        )
                        .classes("minimal-input flex-grow")
                        .props("borderless dense")
                        .style(
                            f"color: {COLORS['text']}; "
                            "border-bottom: 2px solid transparent; "
                            "transition: border-color 0.2s;"
                        )
                    )
                refs["lat_error"] = (
                    ui.label("").classes("text-xs ml-10").style("color: #ef4444;")
                )
                refs["lat_error"].set_visibility(False)

                # Longitude
                with ui.row().classes("items-center gap-2 w-full"):
                    ui.label("Lon:").classes("text-sm w-8").style(
                        f"color: {COLORS['text_muted']}"
                    )
                    refs["lon_input"] = (
                        ui.input(
                            value=state["longitude"],
                            placeholder="-180 to 180",
                            on_change=on_lon_change,
                        )
                        .classes("minimal-input flex-grow")
                        .props("borderless dense")
                        .style(
                            f"color: {COLORS['text']}; "
                            "border-bottom: 2px solid transparent; "
                            "transition: border-color 0.2s;"
                        )
                    )
                refs["lon_error"] = (
                    ui.label("").classes("text-xs ml-10").style("color: #ef4444;")
                )
                refs["lon_error"].set_visibility(False)

                # Hint about timezone
                ui.label("Timezone will be auto-detected from coordinates").classes(
                    "text-xs mt-1"
                ).style(f"color: {COLORS['text_muted']}")

    # Build UI
    with ui.column().classes("w-full gap-1"):
        # Mode toggle
        with ui.row().classes("items-center gap-2 mb-1"):
            ui.toggle(
                {"place": "Place", "coords": "Coords"},
                value=state["mode"],
                on_change=on_mode_change,
            ).props("dense no-caps size=sm")

        # Content container
        refs["content_container"] = ui.element("div").classes("w-full")
        with refs["content_container"]:
            create_content()

    return {
        "get_mode": lambda: state["mode"],
        "get_place": lambda: state["place_value"],
        "get_coords": lambda: (
            float(state["latitude"]) if state["latitude"] else None,
            float(state["longitude"]) if state["longitude"] else None,
        ),
        "get_selected_location": lambda: state["selected_location"],
    }
