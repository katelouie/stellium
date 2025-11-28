"""
Stellium Web - Notable Selector Component

A searchable dropdown to select from the notable births registry.
"""

from config import COLORS
from nicegui import ui
from stellium.data import get_notable_registry


def create_notable_selector(
    on_select=None,
    placeholder: str = "Search famous charts...",
):
    """
    Create a searchable notable selector.

    Args:
        on_select: Callback when a notable is selected. Receives the Notable object.
        placeholder: Placeholder text for the search input.

    Returns:
        Reference to the component container.
    """

    # Load registry
    registry = get_notable_registry()
    all_notables = registry.get_all()

    # Build options dict: name -> Notable
    # Format: "Name (Category, Year)"
    notable_options = {}
    for n in sorted(all_notables, key=lambda x: x.name):
        year = n.datetime.local_datetime.year
        label = f"{n.name} ({n.category.title()}, {year})"
        notable_options[n.name] = label

    def on_change(e):
        """Handle selection change."""
        if e.value and on_select:
            notable = registry.get_by_name(e.value)
            if notable:
                on_select(notable)

    # Create the select with search
    select = (
        ui.select(
            notable_options,
            with_input=True,
            on_change=on_change,
        )
        .classes("w-full")
        .props(f'outlined dense options-dense use-input input-debounce="200"')
        .props(f'placeholder="{placeholder}"')
    )

    return select


def create_notable_autocomplete(
    value: str = "",
    on_select=None,
    placeholder: str = "Search famous charts...",
):
    """
    Create a notable autocomplete input with dropdown suggestions.

    This is a more custom implementation that shows filtered results
    as you type, similar to the location autocomplete.

    Args:
        value: Initial value
        on_select: Callback when a notable is selected. Receives the Notable object.
        placeholder: Placeholder text.

    Returns:
        Reference to the input element.
    """

    # Load registry
    registry = get_notable_registry()
    all_notables = registry.get_all()

    # State
    state = {
        "value": value,
        "suggestions": [],
        "show_dropdown": False,
        "selected_notable": None,
    }

    # UI references
    refs = {
        "dropdown": None,
        "input": None,
    }

    def search_notables(query: str, limit: int = 8) -> list:
        """Search notables by name."""
        if not query or len(query) < 2:
            return []

        query_lower = query.lower().strip()
        results = []

        for n in all_notables:
            # Match name, category, or notable_for
            if (
                query_lower in n.name.lower()
                or query_lower in n.category.lower()
                or query_lower in n.notable_for.lower()
            ):
                results.append(n)

            if len(results) >= limit:
                break

        # Sort by name
        return sorted(results, key=lambda x: x.name)

    def create_suggestion_item(notable):
        """Create a clickable suggestion item."""
        year = notable.datetime.local_datetime.year

        with (
            ui.element("div")
            .classes("px-3 py-2 cursor-pointer hover:bg-gray-100")
            .style(f"border-bottom: 1px solid {COLORS['border']};")
            .on("click", lambda n=notable: select_notable(n))
        ):
            with ui.row().classes("items-center justify-between w-full"):
                with ui.column().classes("gap-0"):
                    ui.label(notable.name).classes("text-sm font-medium").style(
                        f"color: {COLORS['text']}"
                    )
                    ui.label(f"{notable.category.title()}").classes("text-xs").style(
                        f"color: {COLORS['accent']}"
                    )
                ui.label(str(year)).classes("text-xs").style(
                    f"color: {COLORS['text_muted']}"
                )

    def select_notable(notable):
        """Handle notable selection."""
        state["value"] = notable.name
        state["selected_notable"] = notable
        state["show_dropdown"] = False

        # Update input
        if refs["input"]:
            refs["input"].value = notable.name

        # Hide dropdown
        if refs["dropdown"]:
            refs["dropdown"].set_visibility(False)

        # Callback
        if on_select:
            on_select(notable)

    def on_input_change(e):
        """Handle input change."""
        query = e.value or ""
        state["value"] = query

        # Clear selection when user types
        state["selected_notable"] = None

        # Search and update suggestions
        results = search_notables(query)
        state["suggestions"] = results
        state["show_dropdown"] = len(results) > 0

        # Update dropdown
        if refs["dropdown"]:
            refs["dropdown"].clear()
            with refs["dropdown"]:
                for notable in results:
                    create_suggestion_item(notable)
            refs["dropdown"].set_visibility(state["show_dropdown"])

    def on_blur(e):
        """Hide dropdown on blur (with delay for click)."""
        import asyncio

        async def delayed_hide():
            await asyncio.sleep(0.2)
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
            .props("borderless dense debounce=200")
            .on("blur", on_blur)
            .on("focus", on_focus)
        )

        # Dropdown container
        refs["dropdown"] = (
            ui.element("div")
            .classes("absolute left-0 right-0 z-50 rounded shadow-lg overflow-hidden")
            .style(
                f"background-color: {COLORS['white']}; "
                f"border: 1px solid {COLORS['border']}; "
                f"max-height: 300px; overflow-y: auto; "
                f"top: 100%; margin-top: 4px;"
            )
        )
        refs["dropdown"].set_visibility(False)

    return refs["input"]
