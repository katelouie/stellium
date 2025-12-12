"""
MultiWheel chart implementation for 2-4 chart comparisons.

This module provides a unified interface for rendering multiple charts
concentrically inside a single zodiac wheel:
- Biwheel (2 charts): Natal + transits, synastry, etc.
- Triwheel (3 charts): Natal + progressed + transits
- Quadwheel (4 charts): Maximum supported

Ring order (center → out):
- Tiny aspect center (no aspect lines drawn)
- Chart 1 ring (innermost) - houses + objects
- Chart 2 ring
- Chart 3 ring (if present)
- Chart 4 ring (if present)
- Zodiac ring (outermost)

Each chart ring includes:
- Alternating house fills (theme-colored per chart)
- House divider lines (full ring width)
- Planet glyphs with compact info (degree only)
- Position ticks on ring's inner rim
"""

import datetime as dt
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from stellium.core.models import CalculatedChart, ComparisonAspect

if TYPE_CHECKING:
    from stellium.visualization.builder import ChartDrawBuilder


@dataclass(frozen=True)
class MultiWheel:
    """
    Multi-chart comparison supporting 2-4 charts rendered concentrically.

    All charts are rendered inside the zodiac ring, with Chart 1 as the
    innermost ring and subsequent charts expanding outward.

    Attributes:
        charts: Tuple of 2-4 CalculatedChart objects
        labels: Optional labels for each chart (auto-generated if empty)
        cross_aspects: Dict mapping chart index pairs to their cross-aspects
        calculation_timestamp: When this MultiWheel was created
    """

    # The charts (2-4 required)
    charts: tuple[CalculatedChart, ...]

    # Labels for each chart
    labels: tuple[str, ...] = ()

    # Optional cross-chart aspects (between any pair of charts)
    # Key: (chart_idx1, chart_idx2), Value: aspects between them
    cross_aspects: dict[tuple[int, int], tuple[ComparisonAspect, ...]] = field(
        default_factory=dict
    )

    # Metadata
    calculation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(dt.UTC)
    )

    def __post_init__(self) -> None:
        """Validate chart count and auto-generate labels if needed."""
        warnings.warn(
            "MultiWheel is deprecated, use MultiChart instead. "
            "See stellium.core.multichart.MultiChart for the unified API.",
            DeprecationWarning,
            stacklevel=2,
        )
        if len(self.charts) < 2:
            raise ValueError("MultiWheel requires at least 2 charts")
        if len(self.charts) > 4:
            raise ValueError("MultiWheel supports at most 4 charts")

        # Auto-generate labels if not provided
        if not self.labels:
            default_labels = ("Chart 1", "Chart 2", "Chart 3", "Chart 4")
            object.__setattr__(self, "labels", default_labels[: len(self.charts)])

    @property
    def chart_count(self) -> int:
        """Number of charts in this MultiWheel."""
        return len(self.charts)

    @property
    def chart1(self) -> CalculatedChart:
        """Primary chart (innermost ring)."""
        return self.charts[0]

    @property
    def chart2(self) -> CalculatedChart:
        """Second chart."""
        return self.charts[1]

    @property
    def chart3(self) -> CalculatedChart | None:
        """Third chart (if present)."""
        return self.charts[2] if len(self.charts) > 2 else None

    @property
    def chart4(self) -> CalculatedChart | None:
        """Fourth chart (if present)."""
        return self.charts[3] if len(self.charts) > 3 else None

    def draw(self, filename: str = "multiwheel.svg") -> "ChartDrawBuilder":
        """
        Start building a multiwheel visualization.

        Args:
            filename: Output filename for the SVG

        Returns:
            ChartDrawBuilder configured for this MultiWheel
        """
        from stellium.visualization.builder import ChartDrawBuilder

        return ChartDrawBuilder(self).with_filename(filename)


class MultiWheelBuilder:
    """
    Fluent builder for creating MultiWheel objects.

    Usage:
        multiwheel = (MultiWheelBuilder
            .from_charts([natal, transit, progressed])
            .with_labels(["Natal", "Transit", "Progressed"])
            .calculate())

        # Or simply:
        multiwheel = MultiWheelBuilder.from_charts([chart1, chart2]).calculate()
    """

    def __init__(self, charts: list[CalculatedChart]) -> None:
        """
        Initialize builder with charts.

        Args:
            charts: List of 2-4 CalculatedChart objects

        Raises:
            ValueError: If chart count is not 2-4
        """
        warnings.warn(
            "MultiWheelBuilder is deprecated, use MultiChartBuilder instead. "
            "See stellium.core.multichart.MultiChartBuilder for the unified API.",
            DeprecationWarning,
            stacklevel=2,
        )
        if len(charts) < 2:
            raise ValueError("MultiWheel requires at least 2 charts")
        if len(charts) > 4:
            raise ValueError("MultiWheel supports at most 4 charts")

        self._charts = charts
        self._labels: list[str] = []
        self._calculate_cross_aspects: bool = False

    @classmethod
    def from_charts(cls, charts: list[CalculatedChart]) -> "MultiWheelBuilder":
        """
        Create a MultiWheelBuilder from a list of calculated charts.

        Args:
            charts: List of 2-4 CalculatedChart objects

        Returns:
            MultiWheelBuilder ready for configuration
        """
        return cls(charts)

    def with_labels(self, labels: list[str]) -> "MultiWheelBuilder":
        """
        Set labels for each chart.

        Args:
            labels: List of labels (should match chart count)

        Returns:
            self for chaining
        """
        self._labels = labels
        return self

    def with_cross_aspects(self) -> "MultiWheelBuilder":
        """
        Enable cross-chart aspect calculation.

        Note: This can be expensive for 3-4 charts as it calculates
        aspects between all chart pairs.

        Returns:
            self for chaining
        """
        self._calculate_cross_aspects = True
        return self

    def calculate(self) -> MultiWheel:
        """
        Build the MultiWheel object.

        Returns:
            Configured MultiWheel ready for visualization
        """
        cross_aspects: dict[tuple[int, int], tuple[ComparisonAspect, ...]] = {}

        if self._calculate_cross_aspects:
            # Calculate aspects between each pair of charts
            from stellium.engines.aspects import CrossChartAspectEngine
            from stellium.engines.orbs import SimpleOrbEngine

            engine = CrossChartAspectEngine()
            orb_engine = SimpleOrbEngine()

            for i in range(len(self._charts)):
                for j in range(i + 1, len(self._charts)):
                    aspects = engine.calculate_cross_aspects(
                        list(self._charts[i].positions),
                        list(self._charts[j].positions),
                        orb_engine,
                    )
                    cross_aspects[(i, j)] = tuple(aspects)

        return MultiWheel(
            charts=tuple(self._charts),
            labels=tuple(self._labels) if self._labels else (),
            cross_aspects=cross_aspects,
        )
