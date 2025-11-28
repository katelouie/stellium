"""
Stellium Web - Explore Page

Browse and view charts for notable births and historical events.
"""

from components.chart_display import create_chart_actions, create_chart_display
from components.header import create_header, create_nav
from config import COLORS
from nicegui import ui

# Stellium imports
from stellium import ChartBuilder
from stellium.data import get_notable_registry


def create_explore_page():
    """Create the explore/notable births page."""

    # Load registry
    registry = get_notable_registry()
    all_notables = registry.get_all()

    # Get unique categories
    categories = sorted(set(n.category for n in all_notables))

    # Page state
    state = {
        "selected_notable": None,
        "search_query": "",
        "selected_category": "all",
        "chart_svg": None,
        "calculated_chart": None,
    }

    # UI references
    refs = {
        "results_container": None,
        "chart_container": None,
        "actions_container": None,
        "notable_info": None,
    }

    def get_filtered_notables():
        """Get notables filtered by search and category."""
        results = all_notables

        # Filter by category
        if state["selected_category"] != "all":
            results = [n for n in results if n.category == state["selected_category"]]

        # Filter by search query
        query = state["search_query"].lower().strip()
        if query:
            results = [
                n for n in results
                if query in n.name.lower()
                or query in n.notable_for.lower()
                or query in n.category.lower()
                or any(query in sub.lower() for sub in (n.subcategories or []))
            ]

        # Sort by name
        return sorted(results, key=lambda n: n.name)

    def refresh_results():
        """Refresh the results list."""
        if refs["results_container"]:
            refs["results_container"].clear()
            with refs["results_container"]:
                create_results_list()

    def create_results_list():
        """Create the list of notable results."""
        filtered = get_filtered_notables()

        if not filtered:
            ui.label("No results found").classes("text-center py-8").style(
                f"color: {COLORS['text_muted']}"
            )
            return

        ui.label(f"{len(filtered)} results").classes("text-xs mb-2").style(
            f"color: {COLORS['text_muted']}"
        )

        for notable in filtered:
            is_selected = state["selected_notable"] == notable
            bg_color = COLORS["cream_dark"] if is_selected else "transparent"
            border_color = COLORS["primary"] if is_selected else COLORS["border"]

            with (
                ui.element("div")
                .classes("p-3 rounded cursor-pointer mb-2 transition-all")
                .style(
                    f"background-color: {bg_color}; "
                    f"border: 1px solid {border_color};"
                )
                .on("click", lambda n=notable: select_notable(n))
            ):
                with ui.row().classes("items-center justify-between w-full"):
                    with ui.column().classes("gap-0"):
                        ui.label(notable.name).classes("font-medium").style(
                            f"color: {COLORS['text']}"
                        )
                        ui.label(f"{notable.category.title()}").classes("text-xs").style(
                            f"color: {COLORS['accent']}"
                        )
                    # Birth year
                    ui.label(str(notable.datetime.local_datetime.year)).classes(
                        "text-sm"
                    ).style(f"color: {COLORS['text_muted']}")

    def select_notable(notable):
        """Select a notable and generate their chart."""
        state["selected_notable"] = notable
        refresh_results()
        refresh_notable_info()
        generate_chart(notable)

    def refresh_notable_info():
        """Refresh the notable info panel."""
        if refs["notable_info"]:
            refs["notable_info"].clear()
            with refs["notable_info"]:
                create_notable_info()

    def create_notable_info():
        """Create the notable info display."""
        notable = state["selected_notable"]
        if not notable:
            ui.label("Select a notable to view their chart").classes(
                "text-center py-4"
            ).style(f"color: {COLORS['text_muted']}")
            return

        with ui.column().classes("gap-2"):
            ui.label(notable.name).classes("font-display text-xl").style(
                f"color: {COLORS['text']}"
            )

            # Category and subcategories
            cats = [notable.category.title()]
            if notable.subcategories:
                cats.extend(sub.replace("_", " ").title() for sub in notable.subcategories)
            ui.label(" · ".join(cats)).classes("text-sm").style(
                f"color: {COLORS['accent']}"
            )

            # Birth info
            dt = notable.datetime.local_datetime
            loc = notable.location
            ui.label(
                f"{dt.strftime('%B %d, %Y')} at {dt.strftime('%I:%M %p')}"
            ).classes("text-sm").style(f"color: {COLORS['text']}")
            ui.label(loc.name).classes("text-sm").style(
                f"color: {COLORS['text_muted']}"
            )

            # Notable for
            if notable.notable_for:
                ui.label(notable.notable_for).classes("text-sm mt-2 italic").style(
                    f"color: {COLORS['text']}"
                )

            # Data quality
            quality_colors = {
                "AA": COLORS["primary"],
                "A": COLORS["secondary"],
                "B": COLORS["accent"],
                "C": COLORS["text_muted"],
                "DD": COLORS["gold"],
            }
            with ui.row().classes("items-center gap-2 mt-2"):
                ui.label("Data quality:").classes("text-xs").style(
                    f"color: {COLORS['text_muted']}"
                )
                ui.label(notable.data_quality).classes("text-xs font-bold").style(
                    f"color: {quality_colors.get(notable.data_quality, COLORS['text_muted'])}"
                )

    def generate_chart(notable):
        """Generate chart for the selected notable."""
        try:
            # Build chart using the Notable directly
            chart = ChartBuilder.from_notable(notable.name).with_aspects().calculate()
            state["calculated_chart"] = chart

            # Generate SVG
            drawer = chart.draw()
            drawer = drawer.with_theme("classic")
            drawer = drawer.with_zodiac_palette("rainbow")
            drawer = drawer.with_header()
            drawer = drawer.with_moon_phase(position="bottom-right")
            drawer = drawer.with_chart_info(position="top-left")

            state["chart_svg"] = drawer.save(to_string=True)
            refresh_chart_display()

        except Exception as e:
            ui.notify(f"Error generating chart: {str(e)}", type="negative")
            import traceback
            traceback.print_exc()

    def refresh_chart_display():
        """Refresh the chart display."""
        if refs["chart_container"]:
            refs["chart_container"].clear()
            with refs["chart_container"]:
                create_chart_display(state["chart_svg"])

        if refs["actions_container"]:
            refs["actions_container"].clear()
            with refs["actions_container"]:
                create_chart_actions(
                    on_download_svg=download_svg,
                    on_download_pdf=lambda: ui.notify("PDF coming soon!"),
                    on_view_code=lambda: ui.notify("Code preview coming soon!"),
                    enabled=state["chart_svg"] is not None,
                )

    def download_svg():
        """Download the chart as SVG."""
        if state["chart_svg"] and state["selected_notable"]:
            name = state["selected_notable"].name.replace(" ", "_").lower()
            filename = f"{name}_natal_chart.svg"
            ui.download(state["chart_svg"].encode("utf-8"), filename, "image/svg+xml")

    def on_search_change(e):
        """Handle search input change."""
        state["search_query"] = e.value or ""
        refresh_results()

    def on_category_change(e):
        """Handle category filter change."""
        state["selected_category"] = e.value
        refresh_results()

    # ===== PAGE LAYOUT =====

    create_header()
    create_nav()

    with (
        ui.element("main")
        .classes("w-full min-h-screen py-8 px-6")
        .style(f"background-color: {COLORS['cream']}")
    ):
        with ui.element("div").classes("w-full max-w-7xl mx-auto"):
            # Page title
            with ui.element("div").classes("w-full text-center mb-8"):
                ui.label("★  ☆  ★").classes("text-lg mb-4").style(
                    f"color: {COLORS['gold']}"
                )
                ui.label("Explore Notable Charts").classes(
                    "font-display text-3xl md:text-4xl tracking-wide"
                ).style(f"color: {COLORS['text']}")
                ui.label(f"{len(all_notables)} births and events").classes(
                    "text-base mt-2"
                ).style(f"color: {COLORS['text_muted']}")

            # Two column layout
            with ui.row().classes("w-full gap-8 flex-wrap lg:flex-nowrap"):
                # LEFT COLUMN: Search and list
                with ui.column().classes("w-full lg:w-[350px] lg:flex-shrink-0 gap-4"):
                    # Search and filter
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  SEARCH").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        # Search input
                        ui.input(
                            placeholder="Search by name...",
                            on_change=on_search_change,
                        ).classes("w-full mb-3").props("outlined dense")

                        # Category filter
                        category_options = {"all": "All Categories"}
                        for cat in categories:
                            category_options[cat] = cat.title()

                        ui.select(
                            category_options,
                            value="all",
                            on_change=on_category_change,
                        ).classes("w-full").props("outlined dense")

                    # Results list
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg overflow-hidden")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  NOTABLES").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        with (
                            ui.element("div")
                            .classes("w-full rounded-lg")
                            .style("max-height: 55vh; overflow-y: auto;")
                        ):
                            refs["results_container"] = ui.element("div").classes("w-full")
                            with refs["results_container"]:
                                create_results_list()

                # RIGHT COLUMN: Chart display
                with ui.column().classes("w-full lg:flex-1 min-w-0 gap-4"):
                    # Notable info
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        refs["notable_info"] = ui.element("div").classes("w-full")
                        with refs["notable_info"]:
                            create_notable_info()

                    # Chart display
                    refs["chart_container"] = ui.element("div").classes("w-full")
                    with refs["chart_container"]:
                        create_chart_display(None)

                    # Actions
                    refs["actions_container"] = ui.element("div").classes("w-full")
                    with refs["actions_container"]:
                        create_chart_actions(
                            on_download_svg=download_svg,
                            on_download_pdf=lambda: ui.notify("PDF coming soon!"),
                            on_view_code=lambda: ui.notify("Code preview coming soon!"),
                            enabled=False,
                        )
