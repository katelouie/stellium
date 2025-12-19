"""
AtlasBuilder - Fluent API for creating chart atlas PDFs.

Generates multi-page PDFs with one chart per page, like an
old-school astrologer's chart atlas.
"""

from typing import Any

from stellium.core.native import Native
from stellium.visualization.atlas.config import AtlasConfig, AtlasEntry


class AtlasBuilder:
    """
    Fluent builder for chart atlas PDF generation.

    Generates a PDF document with multiple charts, one per page.
    Supports both natal wheel charts and Uranian dial charts.

    Example::

        # Basic atlas from list of natives
        AtlasBuilder().add_natives([native1, native2]).save("atlas.pdf")

        # With configuration
        (AtlasBuilder()
            .add_notable("Albert Einstein")
            .add_notable("Marie Curie")
            .with_chart_type("dial", degrees=90)
            .with_header()
            .with_theme("midnight")
            .save("scientists.pdf"))

        # Mixed chart types
        (AtlasBuilder()
            .add_entry(native1, chart_type="wheel")
            .add_entry(native2, chart_type="dial", degrees=90)
            .save("mixed.pdf"))

        # Entire notables database
        AtlasBuilder.from_all_notables().save("complete_atlas.pdf")
    """

    # =========================================================================
    # Class Methods (Factory Methods)
    # =========================================================================

    @classmethod
    def from_all_notables(
        cls,
        category: str | None = None,
        sort_by: str = "name",
    ) -> "AtlasBuilder":
        """
        Create an atlas from all notables in the registry.

        Args:
            category: Optional category filter (e.g., "scientist", "artist")
            sort_by: Sort order - "name" (alphabetical) or "date" (chronological)

        Returns:
            AtlasBuilder pre-populated with all matching notables

        Example::

            # All notables
            AtlasBuilder.from_all_notables().save("complete_atlas.pdf")

            # Only scientists, sorted by birth date
            (AtlasBuilder.from_all_notables(category="scientist", sort_by="date")
                .with_title_page("Famous Scientists")
                .save("scientists.pdf"))
        """
        from stellium.data import get_notable_registry

        registry = get_notable_registry()
        builder = cls()

        # Get all notables
        if category:
            notables = registry.get_by_category(category)
        else:
            notables = registry.get_all()

        # Sort
        if sort_by == "name":
            notables = sorted(notables, key=lambda n: n.name)
        elif sort_by == "date":
            notables = sorted(
                notables,
                key=lambda n: n.datetime.utc_datetime if n.datetime else n.name,
            )

        # Add all to builder
        for notable in notables:
            builder.add_native(notable)

        return builder

    def __init__(self) -> None:
        """Initialize the atlas builder."""
        self._entries: list[AtlasEntry] = []

        # Default settings
        self._default_chart_type: str = "wheel"
        self._default_chart_options: dict[str, Any] = {}
        self._theme: str = "atlas"
        self._zodiac_palette: str = "rainbow"
        self._show_header: bool = True
        self._show_aspects: bool = True
        self._show_extended_tables: bool = False
        self._show_aspect_counts: bool = True
        self._show_element_modality: bool = True
        self._page_size: str = "letter"
        self._title: str | None = None
        self._filename: str = "atlas.pdf"

    # =========================================================================
    # Entry Addition Methods
    # =========================================================================

    def add_native(self, native: Native) -> "AtlasBuilder":
        """
        Add a single native to the atlas.

        Uses the default chart type and options.

        Args:
            native: Native object with birth data

        Returns:
            Self for chaining
        """
        entry = AtlasEntry(
            native=native,
            chart_type=self._default_chart_type,
            chart_options=self._default_chart_options.copy(),
        )
        self._entries.append(entry)
        return self

    def add_natives(self, natives: list[Native]) -> "AtlasBuilder":
        """
        Add multiple natives to the atlas.

        Uses the default chart type and options for all.

        Args:
            natives: List of Native objects

        Returns:
            Self for chaining
        """
        for native in natives:
            self.add_native(native)
        return self

    def add_notable(self, name: str) -> "AtlasBuilder":
        """
        Add a notable person by name lookup.

        Looks up the notable in the registry and adds their chart.

        Args:
            name: Name of the notable (e.g., "Albert Einstein")

        Returns:
            Self for chaining

        Raises:
            ValueError: If notable not found in registry
        """
        from stellium.data import get_notable_registry

        registry = get_notable_registry()
        notable = registry.get_by_name(name)

        if notable is None:
            raise ValueError(f"Notable not found: {name}")

        return self.add_native(notable)

    def add_notables(self, names: list[str]) -> "AtlasBuilder":
        """
        Add multiple notables by name lookup.

        Args:
            names: List of notable names

        Returns:
            Self for chaining
        """
        for name in names:
            self.add_notable(name)
        return self

    def add_entry(
        self,
        native: Native,
        chart_type: str | None = None,
        **chart_options: Any,
    ) -> "AtlasBuilder":
        """
        Add an entry with custom chart configuration.

        Allows per-entry chart type and options, overriding defaults.

        Args:
            native: Native object with birth data
            chart_type: Chart type ("wheel" or "dial"), defaults to builder default
            **chart_options: Additional options (e.g., degrees=90 for dial)

        Returns:
            Self for chaining

        Example::

            builder.add_entry(native1, chart_type="wheel")
            builder.add_entry(native2, chart_type="dial", degrees=90)
        """
        entry = AtlasEntry(
            native=native,
            chart_type=chart_type or self._default_chart_type,
            chart_options=chart_options or self._default_chart_options.copy(),
        )
        self._entries.append(entry)
        return self

    # =========================================================================
    # Configuration Methods
    # =========================================================================

    def with_chart_type(self, chart_type: str, **options: Any) -> "AtlasBuilder":
        """
        Set the default chart type for all entries.

        Args:
            chart_type: "wheel" or "dial"
            **options: Chart-specific options (e.g., degrees=90 for dial)

        Returns:
            Self for chaining

        Example::

            builder.with_chart_type("dial", degrees=90)
        """
        if chart_type not in ("wheel", "dial"):
            raise ValueError(
                f"Invalid chart_type: {chart_type}. Must be 'wheel' or 'dial'"
            )

        self._default_chart_type = chart_type
        self._default_chart_options = options
        return self

    def with_theme(self, theme: str) -> "AtlasBuilder":
        """
        Set the visual theme for all charts.

        Args:
            theme: Theme name (e.g., "classic", "midnight", "dark", "celestial")

        Returns:
            Self for chaining
        """
        self._theme = theme
        return self

    def with_zodiac_palette(self, palette: str) -> "AtlasBuilder":
        """
        Set the zodiac ring color palette.

        Args:
            palette: Palette name (default: "rainbow")

        Returns:
            Self for chaining
        """
        self._zodiac_palette = palette
        return self

    def with_aspects(self, enabled: bool = True) -> "AtlasBuilder":
        """
        Enable or disable aspect lines on charts.

        Args:
            enabled: True to show aspects (default), False to hide

        Returns:
            Self for chaining
        """
        self._show_aspects = enabled
        return self

    def without_aspects(self) -> "AtlasBuilder":
        """
        Disable aspect lines on charts.

        Returns:
            Self for chaining
        """
        self._show_aspects = False
        return self

    def with_extended_tables(self, enabled: bool = True) -> "AtlasBuilder":
        """
        Enable extended tables (positions, aspects, houses).

        When enabled, pages are rendered in landscape orientation
        to accommodate the additional table columns.

        Args:
            enabled: True to show extended tables

        Returns:
            Self for chaining
        """
        self._show_extended_tables = enabled
        return self

    def with_aspect_counts(self, enabled: bool = True) -> "AtlasBuilder":
        """
        Enable or disable aspect counts corner display.

        Shows a summary of aspect counts (conjunctions, trines, etc.)
        in the top-right corner of each chart.

        Args:
            enabled: True to show aspect counts (default), False to hide

        Returns:
            Self for chaining
        """
        self._show_aspect_counts = enabled
        return self

    def without_aspect_counts(self) -> "AtlasBuilder":
        """
        Disable aspect counts corner display.

        Returns:
            Self for chaining
        """
        self._show_aspect_counts = False
        return self

    def with_element_modality(self, enabled: bool = True) -> "AtlasBuilder":
        """
        Enable or disable element/modality table corner display.

        Shows a cross-table of elements (Fire, Earth, Air, Water) and
        modalities (Cardinal, Fixed, Mutable) in the bottom-left corner.

        Args:
            enabled: True to show table (default), False to hide

        Returns:
            Self for chaining
        """
        self._show_element_modality = enabled
        return self

    def without_element_modality(self) -> "AtlasBuilder":
        """
        Disable element/modality table corner display.

        Returns:
            Self for chaining
        """
        self._show_element_modality = False
        return self

    def without_info_corners(self) -> "AtlasBuilder":
        """
        Disable all info corner displays (aspect counts and element/modality).

        Returns:
            Self for chaining
        """
        self._show_aspect_counts = False
        self._show_element_modality = False
        return self

    def with_header(self, enabled: bool = True) -> "AtlasBuilder":
        """
        Enable or disable chart headers.

        When enabled, each chart shows native name and birth info.

        Args:
            enabled: True to show headers, False to hide

        Returns:
            Self for chaining
        """
        self._show_header = enabled
        return self

    def without_header(self) -> "AtlasBuilder":
        """
        Disable chart headers.

        Returns:
            Self for chaining
        """
        self._show_header = False
        return self

    def with_page_size(self, size: str) -> "AtlasBuilder":
        """
        Set the page size for the PDF.

        Args:
            size: Page size ("letter", "a4", "half-letter")

        Returns:
            Self for chaining
        """
        if size not in ("letter", "a4", "half-letter"):
            raise ValueError(
                f"Invalid page_size: {size}. Must be 'letter', 'a4', or 'half-letter'"
            )

        self._page_size = size
        return self

    def with_title_page(self, title: str) -> "AtlasBuilder":
        """
        Add a title page to the atlas.

        Args:
            title: Title text for the title page

        Returns:
            Self for chaining

        Example::

            builder.with_title_page("Famous Scientists")
        """
        self._title = title
        return self

    def with_filename(self, filename: str) -> "AtlasBuilder":
        """
        Set the output filename.

        Args:
            filename: Output PDF filename

        Returns:
            Self for chaining
        """
        self._filename = filename
        return self

    # =========================================================================
    # Build and Save
    # =========================================================================

    def save(self, filename: str | None = None) -> str:
        """
        Generate the atlas PDF and save to file.

        Args:
            filename: Output filename (overrides with_filename if provided)

        Returns:
            Path to the saved PDF file

        Raises:
            ValueError: If no entries have been added
            ImportError: If typst library is not available
        """
        if not self._entries:
            raise ValueError(
                "No entries added to atlas. Use add_native() or add_notable()."
            )

        # Build config
        config = AtlasConfig(
            entries=self._entries,
            page_size=self._page_size,
            theme=self._theme,
            zodiac_palette=self._zodiac_palette,
            show_header=self._show_header,
            show_aspects=self._show_aspects,
            show_extended_tables=self._show_extended_tables,
            show_aspect_counts=self._show_aspect_counts,
            show_element_modality=self._show_element_modality,
            title=self._title,
            filename=filename or self._filename,
        )

        # Render
        from stellium.visualization.atlas.renderer import AtlasRenderer

        renderer = AtlasRenderer(config)
        pdf_bytes = renderer.render()

        # Save to file
        output_path = config.filename
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        return output_path

    def render(self) -> bytes:
        """
        Generate the atlas PDF and return as bytes.

        Useful for serving directly or further processing.

        Returns:
            PDF content as bytes

        Raises:
            ValueError: If no entries have been added
            ImportError: If typst library is not available
        """
        if not self._entries:
            raise ValueError(
                "No entries added to atlas. Use add_native() or add_notable()."
            )

        # Build config
        config = AtlasConfig(
            entries=self._entries,
            page_size=self._page_size,
            theme=self._theme,
            zodiac_palette=self._zodiac_palette,
            show_header=self._show_header,
            show_aspects=self._show_aspects,
            show_extended_tables=self._show_extended_tables,
            show_aspect_counts=self._show_aspect_counts,
            show_element_modality=self._show_element_modality,
            title=self._title,
            filename=self._filename,
        )

        # Render
        from stellium.visualization.atlas.renderer import AtlasRenderer

        renderer = AtlasRenderer(config)
        return renderer.render()
