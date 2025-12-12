"""Measures elements before rendering."""

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart
from stellium.core.multichart import MultiChart
from stellium.visualization.config import ChartVisualizationConfig, Dimensions
from stellium.visualization.extended_canvas import _filter_objects_for_tables


class ContentMeasurer:
    """
    Measures chart elements without rendering them.

    This is crucial for calculating layout before creating the SVG.
    """

    def _get_house_systems_to_display(
        self,
        chart: CalculatedChart | Comparison | MultiChart,
        config: ChartVisualizationConfig,
    ) -> list[str]:
        """Determine which house systems to display in tables.

        Returns list of house system names based on config settings.
        """
        # Get the actual chart object (for Comparison/MultiChart, use first chart)
        if isinstance(chart, MultiChart):
            actual_chart = chart.charts[0]
        elif isinstance(chart, Comparison):
            actual_chart = chart.chart1
        else:
            actual_chart = chart

        if not actual_chart.house_systems:
            return []

        # Check config for house_systems setting
        config_systems = config.wheel.house_systems
        if config_systems == "all":
            # Show all available house systems
            return list(actual_chart.house_systems.keys())
        elif isinstance(config_systems, list):
            # Show specific systems (filter to only those available)
            return [s for s in config_systems if s in actual_chart.house_systems]

        # Default: just show the default house system
        if actual_chart.default_house_system:
            return [actual_chart.default_house_system]
        return list(actual_chart.house_systems.keys())[:1]  # First available

    def measure_position_table(
        self,
        chart: CalculatedChart | Comparison | MultiChart,
        config: ChartVisualizationConfig,
    ) -> Dimensions:
        """
        Measure position table dimensions.

        For comparison/multichart with 2 charts, this measures TWO side-by-side tables.
        """
        # Get filtered objects
        if isinstance(chart, MultiChart):
            # For MultiChart, measure based on number of charts
            if chart.chart_count >= 2:
                chart1_objects = _filter_objects_for_tables(
                    chart.charts[0].positions, config.tables.object_types
                )
                chart2_objects = _filter_objects_for_tables(
                    chart.charts[1].positions, config.tables.object_types
                )
                num_rows = max(len(chart1_objects), len(chart2_objects))
                num_tables = min(chart.chart_count, 2)  # Max 2 tables side by side
            else:
                objects = _filter_objects_for_tables(
                    chart.charts[0].positions, config.tables.object_types
                )
                num_rows = len(objects)
                num_tables = 1
        elif isinstance(chart, Comparison):
            chart1_objects = _filter_objects_for_tables(
                chart.chart1.positions, config.tables.object_types
            )
            chart2_objects = _filter_objects_for_tables(
                chart.chart2.positions, config.tables.object_types
            )
            num_rows = max(len(chart1_objects), len(chart2_objects))
            num_tables = 2
        else:  # Is a single chart
            objects = _filter_objects_for_tables(
                chart.positions, config.tables.object_types
            )
            num_rows = len(objects)
            num_tables = 1

        # Get config values
        col_widths = config.tables.position_col_widths
        padding = config.tables.padding
        gap_between_cols = config.tables.gap_between_columns
        gap_between_tables = config.tables.gap_between_tables
        line_height = 16  # Match DEFAULT_STYLE in extended_canvas.py

        # Determine which columns are shown
        col_names = ["planet", "sign", "degree"]
        # TODO: Make show_house and show_speed configurable
        show_house = True
        show_speed = True

        # Get house systems to display (may be multiple)
        house_systems = (
            self._get_house_systems_to_display(chart, config) if show_house else []
        )

        # Add a "house" column for each house system
        for _ in house_systems:
            col_names.append("house")

        if show_speed:
            col_names.append("speed")

        # Calculate single table width: padding + columns + gaps + padding
        single_table_width = 2 * padding  # left and right padding
        for i, col_name in enumerate(col_names):
            single_table_width += col_widths.get(col_name, 50)
            if i < len(col_names) - 1:  # Add gap between columns
                single_table_width += gap_between_cols

        # Account for multiple tables (for comparison charts)
        total_width = (single_table_width * num_tables) + (
            gap_between_tables * (num_tables - 1)
        )

        # Height: padding + header + rows + padding
        # For comparison: also add title height (20px) above each table
        title_height = 20 if num_tables == 2 else 0
        header_height = line_height
        rows_height = num_rows * line_height
        total_height = padding + title_height + header_height + rows_height + padding

        return Dimensions(total_width, total_height)

    def measure_house_table(
        self,
        chart: CalculatedChart | Comparison | MultiChart,
        config: ChartVisualizationConfig,
    ) -> Dimensions:
        """
        Measure house cusp table dimensions.

        Always 12 rows (houses). For multiple house systems, adds columns (sign + degree)
        for each system. For comparison/multichart, shows separate tables for each chart.
        """
        # Get config values
        col_widths = config.tables.house_col_widths
        padding = config.tables.padding
        gap_between_cols = config.tables.gap_between_columns
        gap_between_tables = config.tables.gap_between_tables
        line_height = 16  # Match DEFAULT_STYLE in extended_canvas.py

        # Get house systems to display
        house_systems = self._get_house_systems_to_display(chart, config)
        num_house_systems = max(len(house_systems), 1)  # At least 1

        # Build column list: house number + (sign, degree) for each system
        col_names = ["house"]
        for _ in range(num_house_systems):
            col_names.extend(["sign", "degree"])

        # Calculate single table width: padding + columns + gaps + padding
        single_table_width = 2 * padding  # left and right padding
        for i, col_name in enumerate(col_names):
            single_table_width += col_widths.get(col_name, 50)
            if i < len(col_names) - 1:  # Add gap between columns
                single_table_width += gap_between_cols

        # For comparisons/multicharts with 2+ charts, we have 2 chart tables
        if isinstance(chart, MultiChart):
            num_chart_tables = min(chart.chart_count, 2)
        elif isinstance(chart, Comparison):
            num_chart_tables = 2
        else:
            num_chart_tables = 1
        total_width = (single_table_width * num_chart_tables) + (
            gap_between_tables * (num_chart_tables - 1)
        )

        # Height: padding + title (for comparison) + header + 12 rows + padding
        title_height = 20 if num_chart_tables == 2 else 0
        total_height = (
            padding + title_height + line_height + (12 * line_height) + padding
        )

        return Dimensions(total_width, total_height)

    def measure_aspectarian(
        self,
        chart: CalculatedChart | Comparison | MultiChart,
        config: ChartVisualizationConfig,
    ) -> Dimensions:
        """
        Measure aspectarian grid dimensions.

        Triangle for single charts, square for comparisons/multicharts.
        """
        cell_size = config.tables.aspectarian_cell_size

        if isinstance(chart, MultiChart) and chart.chart_count >= 2:
            # Square grid: chart1 objects × chart2 objects
            chart1_objects = _filter_objects_for_tables(
                chart.charts[0].positions, config.tables.object_types
            )
            chart2_objects = _filter_objects_for_tables(
                chart.charts[1].positions, config.tables.object_types
            )
            # Add 1 for header row/column
            width = (len(chart2_objects) + 1) * cell_size
            height = (len(chart1_objects) + 1) * cell_size
        elif isinstance(chart, Comparison):
            # Square grid: chart1 objects × chart2 objects
            chart1_objects = _filter_objects_for_tables(
                chart.chart1.positions, config.tables.object_types
            )
            chart2_objects = _filter_objects_for_tables(
                chart.chart2.positions, config.tables.object_types
            )
            # Add 1 for header row/column
            width = (len(chart2_objects) + 1) * cell_size
            height = (len(chart1_objects) + 1) * cell_size
        else:
            # Triangle grid - single chart
            objects = _filter_objects_for_tables(
                chart.positions, config.tables.object_types
            )
            num_objects = len(objects)

            # Triangle: width and height both num_objects * cell_size
            # (includes header row/col)
            width = num_objects * cell_size
            height = num_objects * cell_size

        return Dimensions(width, height)

    def measure_corner_element(
        self,
        element_name: str,
        chart: CalculatedChart | Comparison | MultiChart,
        config: ChartVisualizationConfig,
    ) -> Dimensions:
        """
        Estimate dimensions for corner elements.

        These are roughly fixed size, but we can be more precise
        by counting lines of text, etc.
        """
        # TODO: Make these more precise
        estimates = {
            "chart_info": Dimensions(200, 100),
            "aspect_counts": Dimensions(150, 80),
            "element_modality": Dimensions(120, 90),
            "chart_shape": Dimensions(150, 60),
        }

        return estimates.get(element_name, Dimensions(100, 80))
