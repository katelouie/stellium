"""Implementation of standard Zodiacal Releasing system."""

import datetime as dt

from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG, ArabicPartsCalculator
from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    ZRPeriod,
    ZRTimeline,
)
from stellium.engines.dignities import DIGNITIES

PLANET_PERIODS = {
    "Moon": 25,
    "Mercury": 20,
    "Venus": 8,
    "Sun": 19,
    "Mars": 15,
    "Jupiter": 12,
    "Saturn": 27,
}


class ZodiacalReleasingEngine:
    """Calculate Zodiacal Releasing periods."""

    def __init__(
        self,
        chart: CalculatedChart,
        lot: str = "Part of Fortune",
        max_level: int = 4,
        lifespan: int = 100,
    ) -> None:
        self.chart = chart
        self.lot = lot
        self.max_level = max_level
        self.lifespan = lifespan

        self.planet_periods = PLANET_PERIODS

        self.sign_periods = {
            sign: PLANET_PERIODS[info["traditional"]["ruler"]]
            for sign, info in DIGNITIES.items()
        }

        self.signs = list(self.sign_periods.keys())

        self.total_cycle_period = sum(self.sign_periods.values())  # 208

        self.lot_position = self._get_lot_position()
        self.lot_sign = self.lot_position.sign

        self.angular_signs = self._get_angular_signs()

    def _get_lot_position(self) -> CelestialPosition:
        """Get the base lot position."""
        if self.lot not in ARABIC_PARTS_CATALOG:
            raise ValueError(
                "Provided Lot name unknown. Try 'Part of Fortune', 'Part of Spirit', or others."
            )
        else:
            # Check if lot has already been calculated
            lot_options = [x for x in self.chart.positions if x.name == self.lot]

            if lot_options:
                lot_pos = lot_options[0]
            else:
                # Calculate just this lot
                calculator = ArabicPartsCalculator([self.lot])
                lot_pos = calculator.calculate(
                    self.chart.datetime,
                    self.chart.location,
                    self.chart.positions,
                    self.chart.house_systems,
                    self.chart.house_placements,
                )[0]

        return lot_pos

    def _get_period_duration(self, sign: str, parent_duration: float) -> float:
        sign_period = self.sign_periods[sign]
        return parent_duration * (sign_period / self.total_cycle_period)

    def _get_angular_signs(self) -> dict[str, int]:
        """Get signs that are angular to the Lot."""
        lot_sign_index = self.signs.index(self.lot_sign)

        return {
            self.signs[lot_sign_index]: 1,
            self.signs[(lot_sign_index + 3) % 12]: 4,
            self.signs[(lot_sign_index + 6) % 12]: 7,
            self.signs[(lot_sign_index + 9) % 12]: 10,  # Peak!
        }

    def _calculate_periods(
        self,
        level: int,
        start_sign: str,
        start_date: dt.datetime,
        total_duration: float,
    ) -> list[ZRPeriod]:
        """
        Unified period calculator for all levels.

        L1: total_duration_days = 208 * 365.25, loops until lifespan
        L2+: total_duration_days = parent.length_days, loops exactly 12
        """
        periods = []
        current_sign = start_sign
        current_date = start_date
        signs_processed = 0

        while True:
            sign_period = self.sign_periods[current_sign]
            period_days = total_duration * (sign_period / self.total_cycle_period)
            end_date = current_date + dt.timedelta(days=period_days)

            angle = self.angular_signs.get(current_sign)

            periods.append(
                ZRPeriod(
                    level=level,
                    sign=current_sign,
                    ruler=DIGNITIES[current_sign]["traditional"]["ruler"],
                    start=current_date,
                    end=end_date,
                    length_days=period_days,
                    angle_from_lot=angle,
                    is_angular=angle is not None,
                    is_peak=angle == 10,
                    is_loosing_bond=(angle is not None) and (level >= 2),
                )
            )

            current_date = end_date
            current_sign = self.signs[(self.signs.index(current_sign) + 1) % 12]
            signs_processed += 1

            # Exit conditions
            if level == 1:
                # L1: continue until lifespan exceeded
                age_years = (
                    current_date - self.chart.datetime.utc_datetime
                ).days / 365.25
                if age_years > self.lifespan:
                    break
            else:
                # L2+: exactly one cycle (12 signs)
                if signs_processed >= 12:
                    break

        return periods

    def calculate_all_periods(self) -> dict[int, list[ZRPeriod]]:
        """Build all periods for all levels"""
        all_periods: dict[int, list[ZRPeriod]] = {}

        # L1: base duration = 208 years in days (so scaling = identity)
        base_duration = self.total_cycle_period * 365.25
        all_periods[1] = self._calculate_periods(
            level=1,
            start_sign=self.lot_sign,
            start_date=self.chart.datetime.utc_datetime,
            total_duration=base_duration,
        )

        # L2+: iterate parent periods
        for level in range(2, self.max_level + 1):
            all_periods[level] = []
            for parent in all_periods[level - 1]:
                subperiods = self._calculate_periods(
                    level=level,
                    start_sign=parent.sign,
                    start_date=parent.start,
                    total_duration=parent.length_days,
                )
                all_periods[level].extend(subperiods)

        return all_periods

    def build_timeline(self) -> ZRTimeline:
        """Build complete timeline with all periods."""
        all_periods = self.calculate_all_periods()

        return ZRTimeline(
            lot=self.lot,
            lot_sign=self.lot_sign,
            birth_date=self.chart.datetime.utc_datetime,
            periods=all_periods,
            max_level=self.max_level,
        )


class ZodiacalReleasingAnalyzer:
    """Calculate Zodiacal Releasing timeline and periods."""

    def __init__(
        self,
        lots: list[str],
        engine=ZodiacalReleasingEngine,
        max_level: int = 4,
        lifespan: int = 100,
    ) -> None:
        self.lots = lots
        self.engine = engine
        self.max_level = max_level
        self.lifespan = lifespan

    @property
    def analyzer_name(self) -> str:
        return "ZodiacalReleasing"

    @property
    def metadata_name(self) -> str:
        return "zodiacal_releasing"

    def analyze(self, chart: CalculatedChart) -> dict:
        """Add zodiacial releasing timeline to metadata.

        Args:
            chart: Chart to analyze

        Returns:
            Dict of {lot name: ZRTimeline}
        """
        results = {}
        for lot in self.lots:
            lot_engine = self.engine(
                chart, lot, max_level=self.max_level, lifespan=self.lifespan
            )
            results[lot] = lot_engine.build_timeline()

        return results
