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
        method: str = "valens",
    ) -> None:
        self.chart = chart
        self.lot = lot
        self.max_level = max_level
        self.lifespan = lifespan
        self.method = method  # Can be "valens" or "fractal"

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

        self._setup_quality_lookups()  # Get all sect-relevant placements

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

    def _setup_quality_lookups(self) -> None:
        """Build fast lookups for planet roles and sign contents."""
        sect = self.chart.sect()

        # 1. Define Roles based on Sect
        # Format: (PlanetName, RoleName, ScoreModifier)
        if sect == "day":
            mapping = [
                ("Jupiter", "sect_benefic", 2),
                ("Venus", "contrary_benefic", 1),
                ("Saturn", "sect_malefic", -1),  # Constructive difficulty
                ("Mars", "contrary_malefic", -2),  # Destructive difficulty
                ("Sun", "sect_light", 1),
                ("Moon", "contrary_light", 0),
            ]
        else:  # Night
            mapping = [
                ("Venus", "sect_benefic", 2),
                ("Jupiter", "contrary_benefic", 1),
                ("Mars", "sect_malefic", -1),
                ("Saturn", "contrary_malefic", -2),
                ("Moon", "sect_light", 1),
                ("Sun", "contrary_light", 0),
            ]

        # 2. Build Lookup Maps
        self.ruler_roles = {}  # { "Jupiter": ("sect_benefic", 2) }
        self.sign_contents = {}  # { "Pisces": [("sect_benefic", 2)] }

        for planet_name, role, score in mapping:
            # A. Ruler Lookup
            self.ruler_roles[planet_name] = (role, score)

            # B. Presence Lookup
            # Find where this planet is in the chart
            planet_pos = next(
                (p for p in self.chart.positions if p.name == planet_name), None
            )
            if planet_pos:
                if planet_pos.sign not in self.sign_contents:
                    self.sign_contents[planet_pos.sign] = []
                self.sign_contents[planet_pos.sign].append((role, score))

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

            # === Quality calculation ===
            period_score = 0

            # Analyze ruler
            period_ruler_name = DIGNITIES[current_sign]["traditional"]["ruler"]
            ruler_info = self.ruler_roles.get(period_ruler_name)

            ruler_role_name = None
            if ruler_info:
                ruler_role_name, r_score = ruler_info
                period_score += r_score

            # 2. Analyze Planets Present in the Sign
            present_roles_list = []
            if current_sign in self.sign_contents:
                for role, p_score in self.sign_contents[current_sign]:
                    present_roles_list.append(role)
                    # Presence is usually "louder" than rulership, so we might weight it
                    period_score += p_score

            # 3. Angularity Boost (Optional)
            # Peak periods amplify the good AND the bad
            if angle == 10:
                # If bad score, make it worse. If good score, make it better.
                if period_score < 0:
                    period_score -= 1
                if period_score > 0:
                    period_score += 1

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
                    is_loosing_bond=False,
                    # Qualitative fields
                    ruler_role=ruler_role_name,
                    tenant_roles=present_roles_list,
                    score=period_score,
                )
            )

            current_date = end_date
            current_sign = self._next_sign(current_sign)
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

    def _calculate_periods_valens(
        self,
        level: int,
        start_sign: str,
        start_date: dt.datetime,
        total_duration: float,
    ) -> list[ZRPeriod]:
        """Calculate the traditional Valens-style period traversal with loosing of the bond."""
        level_multipliers = {
            1: 365.25,  # Years
            2: 30.437,  # Months
            3: 1.0146,  # Days
            4: 0.0417,  # Hours
        }

        periods = []
        current_sign = start_sign
        current_date = start_date
        signs_processed = 0
        time_passed = 0.0

        while True:
            # Calculate the "ideal" duration for this sign period
            sign_period = self.sign_periods[current_sign]
            ideal_period_days = sign_period * level_multipliers[level]

            # Check remaining budget (for L2+)
            final_duration = ideal_period_days
            is_truncated = False

            if level > 1:
                remaining_time = total_duration - time_passed

                # Floating point precision check: if we are practically out of time, stop.
                if remaining_time <= 0.01:
                    break

                # TRUNCATION LOGIC:
                # If this period would go over the parent's limit, cut it short.
                if ideal_period_days > remaining_time:
                    final_duration = remaining_time
                    is_truncated = True

            # Calculate the end date
            end_date = current_date + dt.timedelta(days=final_duration)

            angle = self.angular_signs.get(current_sign)

            # === Quality calculation ===
            period_score = 0

            # Analyze ruler
            period_ruler_name = DIGNITIES[current_sign]["traditional"]["ruler"]
            ruler_info = self.ruler_roles.get(period_ruler_name)

            ruler_role_name = None
            if ruler_info:
                ruler_role_name, r_score = ruler_info
                period_score += r_score

            # 2. Analyze Planets Present in the Sign
            present_roles_list = []
            if current_sign in self.sign_contents:
                for role, p_score in self.sign_contents[current_sign]:
                    present_roles_list.append(role)
                    # Presence is usually "louder" than rulership, so we might weight it
                    period_score += p_score

            # 3. Angularity Boost (Optional)
            # Peak periods amplify the good AND the bad
            if angle == 10:
                # If bad score, make it worse. If good score, make it better.
                if period_score < 0:
                    period_score -= 1
                if period_score > 0:
                    period_score += 1

            periods.append(
                ZRPeriod(
                    level=level,
                    sign=current_sign,
                    ruler=DIGNITIES[current_sign]["traditional"]["ruler"],
                    start=current_date,
                    end=end_date,
                    length_days=final_duration,
                    angle_from_lot=angle,
                    is_angular=angle is not None,
                    is_peak=angle == 10,
                    is_loosing_bond=signs_processed == 12,
                    # Qualitative fields
                    ruler_role=ruler_role_name,
                    tenant_roles=present_roles_list,
                    score=period_score,
                )
            )

            # Break if we just truncated (time ran out)
            if is_truncated:
                break

            time_passed += final_duration
            current_date = end_date
            # Loosing of the bond after first cycle -- jump to opposite
            current_sign = self._next_sign(current_sign, jump=signs_processed == 11)
            signs_processed += 1

            # Exit conditions
            if level == 1:
                # L1: continue until lifespan exceeded
                age_years = (
                    current_date - self.chart.datetime.utc_datetime
                ).days / 365.25
                if age_years > self.lifespan:
                    break

        return periods

    def _next_sign(self, current_sign: str, jump: bool = False) -> str:
        """Calculate the next sign in the cycle.

        Args:
            current_sign: current sign name
            jump: If the transition is a "loosing of the bond" jump to the opposite sign of the next

        Returns:
            Name of "next" sign
        """
        consecutive_sign = self.signs[(self.signs.index(current_sign) + 1) % 12]
        if jump:
            return self.signs[(self.signs.index(consecutive_sign) + 6) % 12]

        return consecutive_sign

    def calculate_all_periods(self) -> dict[int, list[ZRPeriod]]:
        """Build all periods for all levels"""
        all_periods: dict[int, list[ZRPeriod]] = {}

        # Set the calculation function used
        calc_fn = (
            self._calculate_periods
            if self.method == "fractal"
            else self._calculate_periods_valens
        )

        # L1: base duration = 208 years in days (so scaling = identity)
        base_duration = self.total_cycle_period * 365.25
        all_periods[1] = calc_fn(
            level=1,
            start_sign=self.lot_sign,
            start_date=self.chart.datetime.utc_datetime,
            total_duration=base_duration,
        )

        # L2+: iterate parent periods
        for level in range(2, self.max_level + 1):
            all_periods[level] = []
            for parent in all_periods[level - 1]:
                subperiods = calc_fn(
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
