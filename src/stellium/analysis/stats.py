"""
Statistical aggregation for chart collections.

ChartStats provides methods for computing aggregate statistics across
multiple charts, including element distributions, sign frequencies,
aspect counts, and cross-tabulations.
"""

from collections import Counter
from collections.abc import Sequence
from typing import Any

from stellium.analysis.frames import (
    _count_elements,
    _count_modalities,
    _has_pattern,
    _require_pandas,
)
from stellium.core.models import CalculatedChart

# All zodiac signs in order
ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


class ChartStats:
    """
    Statistical aggregation across chart collections.

    Computes distributions, frequencies, and cross-tabulations for
    research and analysis purposes.

    Example::

        from stellium.analysis import BatchCalculator, ChartStats

        charts = BatchCalculator.from_registry(category="scientist").calculate_all()
        stats = ChartStats(charts)

        # Element distribution
        print(stats.element_distribution())

        # Sun sign frequency
        print(stats.sign_distribution("Sun"))

        # Cross-tabulation
        print(stats.cross_tab("sun_sign", "moon_sign"))
    """

    def __init__(self, charts: Sequence[CalculatedChart]) -> None:
        """
        Initialize with a collection of charts.

        Args:
            charts: Sequence of CalculatedChart objects to analyze
        """
        self._charts = list(charts)

    @property
    def chart_count(self) -> int:
        """Number of charts in the collection."""
        return len(self._charts)

    # ---- Element & Modality ----

    def element_distribution(self, normalize: bool = True) -> dict[str, float]:
        """
        Calculate element distribution across all charts.

        Counts planets in each element across all charts and returns
        the distribution as proportions (default) or raw counts.

        Args:
            normalize: Return proportions (0-1) instead of counts

        Returns:
            Dictionary with element names as keys and counts/proportions as values

        Example::

            stats.element_distribution()
            # {'fire': 0.28, 'earth': 0.31, 'air': 0.22, 'water': 0.19}

            stats.element_distribution(normalize=False)
            # {'fire': 280, 'earth': 310, 'air': 220, 'water': 190}
        """
        totals: dict[str, int] = {"fire": 0, "earth": 0, "air": 0, "water": 0}

        for chart in self._charts:
            counts = _count_elements(chart)
            for element, count in counts.items():
                totals[element] += count

        if normalize:
            total = sum(totals.values())
            if total > 0:
                return {k: v / total for k, v in totals.items()}
            return dict.fromkeys(totals, 0.0)

        return {k: float(v) for k, v in totals.items()}

    def modality_distribution(self, normalize: bool = True) -> dict[str, float]:
        """
        Calculate modality distribution across all charts.

        Args:
            normalize: Return proportions (0-1) instead of counts

        Returns:
            Dictionary with modality names as keys and counts/proportions as values

        Example::

            stats.modality_distribution()
            # {'cardinal': 0.35, 'fixed': 0.33, 'mutable': 0.32}
        """
        totals: dict[str, int] = {"cardinal": 0, "fixed": 0, "mutable": 0}

        for chart in self._charts:
            counts = _count_modalities(chart)
            for modality, count in counts.items():
                totals[modality] += count

        if normalize:
            total = sum(totals.values())
            if total > 0:
                return {k: v / total for k, v in totals.items()}
            return dict.fromkeys(totals, 0.0)

        return {k: float(v) for k, v in totals.items()}

    # ---- Sign Distribution ----

    def sign_distribution(
        self,
        object_name: str,
        normalize: bool = False,
    ) -> dict[str, int | float]:
        """
        Count sign placements for a specific object across all charts.

        Args:
            object_name: Name of the object (e.g., "Sun", "Moon", "ASC")
            normalize: Return proportions instead of counts

        Returns:
            Dictionary with sign names as keys and counts as values

        Example::

            stats.sign_distribution("Sun")
            # {'Aries': 45, 'Taurus': 38, 'Gemini': 42, ...}

            stats.sign_distribution("Moon", normalize=True)
            # {'Aries': 0.08, 'Taurus': 0.09, ...}
        """
        counts: Counter[str] = Counter()

        for chart in self._charts:
            obj = chart.get_object(object_name)
            if obj is not None:
                counts[obj.sign] += 1

        # Ensure all signs are represented
        result: dict[str, int] = {sign: counts.get(sign, 0) for sign in ZODIAC_SIGNS}

        if normalize:
            total = sum(result.values())
            if total > 0:
                return {k: v / total for k, v in result.items()}
            return dict.fromkeys(result, 0.0)

        return result

    def house_distribution(
        self,
        object_name: str,
        house_system: str | None = None,
        normalize: bool = False,
    ) -> dict[int, int | float]:
        """
        Count house placements for a specific object across all charts.

        Args:
            object_name: Name of the object (e.g., "Sun", "Moon")
            house_system: House system to use (default: chart's default)
            normalize: Return proportions instead of counts

        Returns:
            Dictionary with house numbers (1-12) as keys and counts as values

        Example::

            stats.house_distribution("Sun")
            # {1: 35, 2: 42, 3: 38, ..., 12: 41}
        """
        counts: Counter[int] = Counter()

        for chart in self._charts:
            try:
                system = house_system or chart.default_house_system
                placements = chart.house_placements.get(system, {})
                house = placements.get(object_name)
                if house is not None:
                    counts[house] += 1
            except ValueError:
                # No house system available
                continue

        # Ensure all houses are represented
        result: dict[int, int] = {h: counts.get(h, 0) for h in range(1, 13)}

        if normalize:
            total = sum(result.values())
            if total > 0:
                return {k: v / total for k, v in result.items()}
            return dict.fromkeys(result, 0.0)

        return result

    # ---- Aspect Statistics ----

    def aspect_frequency(self, normalize: bool = False) -> dict[str, int | float]:
        """
        Count aspect types across all charts.

        Args:
            normalize: Return proportions instead of counts

        Returns:
            Dictionary with aspect names as keys and counts as values

        Example::

            stats.aspect_frequency()
            # {'Conjunction': 1234, 'Square': 987, 'Trine': 876, ...}
        """
        counts: Counter[str] = Counter()

        for chart in self._charts:
            for aspect in chart.aspects:
                counts[aspect.aspect_name] += 1

        result = dict(counts.most_common())

        if normalize:
            total = sum(result.values())
            if total > 0:
                return {k: v / total for k, v in result.items()}
            return dict.fromkeys(result, 0.0)

        return result

    def aspect_pair_frequency(
        self,
        object1: str,
        object2: str,
    ) -> dict[str, int]:
        """
        Count aspect types between two specific objects.

        Args:
            object1: First object name
            object2: Second object name

        Returns:
            Dictionary with aspect names as keys and counts as values

        Example::

            stats.aspect_pair_frequency("Sun", "Moon")
            # {'Conjunction': 45, 'Sextile': 38, 'Square': 42, ...}
        """
        counts: Counter[str] = Counter()

        for chart in self._charts:
            for aspect in chart.aspects:
                names = {aspect.object1.name, aspect.object2.name}
                if object1 in names and object2 in names:
                    counts[aspect.aspect_name] += 1

        return dict(counts)

    # ---- Pattern Statistics ----

    def pattern_frequency(self) -> dict[str, int]:
        """
        Count aspect patterns across all charts.

        Returns:
            Dictionary with pattern names as keys and counts as values

        Example::

            stats.pattern_frequency()
            # {'Grand Trine': 23, 'T-Square': 45, 'Yod': 12, ...}
        """
        counts: Counter[str] = Counter()
        pattern_names = [
            "Grand Trine",
            "T-Square",
            "Grand Cross",
            "Yod",
            "Kite",
            "Mystic Rectangle",
            "Stellium",
        ]

        for chart in self._charts:
            for pattern_name in pattern_names:
                if _has_pattern(chart, pattern_name):
                    counts[pattern_name] += 1

        return dict(counts)

    # ---- Retrograde Statistics ----

    def retrograde_frequency(self, normalize: bool = False) -> dict[str, int | float]:
        """
        Count retrograde occurrences by planet.

        Args:
            normalize: Return proportions instead of counts

        Returns:
            Dictionary with planet names as keys and retrograde counts as values

        Example::

            stats.retrograde_frequency()
            # {'Mercury': 89, 'Venus': 23, 'Mars': 45, ...}
        """
        counts: Counter[str] = Counter()
        totals: Counter[str] = Counter()

        for chart in self._charts:
            for planet in chart.get_planets():
                totals[planet.name] += 1
                if planet.is_retrograde:
                    counts[planet.name] += 1

        if normalize:
            result: dict[str, float] = {}
            for name, total in totals.items():
                if total > 0:
                    result[name] = counts.get(name, 0) / total
                else:
                    result[name] = 0.0
            return result

        return dict(counts)

    # ---- Sect Statistics ----

    def sect_distribution(self) -> dict[str, int]:
        """
        Count day vs night charts.

        Returns:
            Dictionary with "day" and "night" keys and counts as values

        Example::

            stats.sect_distribution()
            # {'day': 523, 'night': 477}
        """
        counts: Counter[str] = Counter()

        for chart in self._charts:
            sect = chart.sect()
            if sect:
                counts[sect.lower()] += 1

        return dict(counts)

    # ---- Cross-Tabulation ----

    def cross_tab(
        self,
        row_var: str,
        col_var: str,
    ) -> Any:
        """
        Create a cross-tabulation (contingency table) of two variables.

        Requires pandas: pip install stellium[analysis]

        Supported variables:
        - "sun_sign", "moon_sign", "asc_sign", "mc_sign"
        - "sun_house", "moon_house", etc. (any object + "_house")
        - "sect" (day/night)
        - Any object name followed by "_sign" or "_house"

        Args:
            row_var: Variable for rows
            col_var: Variable for columns

        Returns:
            pandas DataFrame with cross-tabulation

        Example::

            # Sun sign vs Moon sign
            df = stats.cross_tab("sun_sign", "moon_sign")

            # Sun sign vs sect
            df = stats.cross_tab("sun_sign", "sect")
        """
        _require_pandas()
        import pandas as pd

        row_data = []
        col_data = []

        for chart in self._charts:
            row_val = self._get_variable(chart, row_var)
            col_val = self._get_variable(chart, col_var)

            if row_val is not None and col_val is not None:
                row_data.append(row_val)
                col_data.append(col_val)

        df = pd.DataFrame({row_var: row_data, col_var: col_data})
        return pd.crosstab(df[row_var], df[col_var])

    def _get_variable(self, chart: CalculatedChart, var_name: str) -> Any:
        """Extract a variable value from a chart."""
        # Sect
        if var_name == "sect":
            return chart.sect()

        # Sign variables (object_sign)
        if var_name.endswith("_sign"):
            obj_name = var_name[:-5]  # Remove "_sign"
            # Map common names
            obj_name = {
                "sun": "Sun",
                "moon": "Moon",
                "asc": "ASC",
                "mc": "MC",
                "mercury": "Mercury",
                "venus": "Venus",
                "mars": "Mars",
                "jupiter": "Jupiter",
                "saturn": "Saturn",
            }.get(obj_name.lower(), obj_name)

            obj = chart.get_object(obj_name)
            return obj.sign if obj else None

        # House variables (object_house)
        if var_name.endswith("_house"):
            obj_name = var_name[:-6]  # Remove "_house"
            obj_name = {
                "sun": "Sun",
                "moon": "Moon",
                "mercury": "Mercury",
                "venus": "Venus",
                "mars": "Mars",
                "jupiter": "Jupiter",
                "saturn": "Saturn",
            }.get(obj_name.lower(), obj_name)

            return chart.get_house(obj_name)

        return None

    # ---- Summary ----

    def summary(self) -> dict[str, Any]:
        """
        Generate a comprehensive summary of the chart collection.

        Returns:
            Dictionary with various statistics

        Example::

            summary = stats.summary()
            print(summary['chart_count'])
            print(summary['element_distribution'])
        """
        return {
            "chart_count": self.chart_count,
            "element_distribution": self.element_distribution(),
            "modality_distribution": self.modality_distribution(),
            "sect_distribution": self.sect_distribution(),
            "pattern_frequency": self.pattern_frequency(),
            "retrograde_frequency": self.retrograde_frequency(),
            "sun_sign_distribution": self.sign_distribution("Sun"),
            "moon_sign_distribution": self.sign_distribution("Moon"),
        }

    def __repr__(self) -> str:
        return f"<ChartStats: {self.chart_count} charts>"

    def __len__(self) -> int:
        return self.chart_count
