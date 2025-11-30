"""
Tests for ReturnBuilder - planetary return chart calculations.

Covers:
- Solar return factory method
- Lunar return factory method
- Planetary return factory method
- Deferred configuration methods
- Return moment calculation
- Location resolution (including relocated returns)
- Error handling
"""

from datetime import datetime

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.orbs import SimpleOrbEngine
from stellium.engines.patterns import AspectPatternAnalyzer
from stellium.returns.builder import ReturnBuilder, ReturnInfo


class TestSolarReturn:
    """Tests for solar return calculation."""

    @pytest.fixture
    def natal_chart(self):
        """Create a natal chart for testing."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).with_aspects().calculate()

    def test_solar_return_basic(self, natal_chart):
        """Test basic solar return calculation."""
        sr = ReturnBuilder.solar(natal_chart, 2025).calculate()

        assert sr is not None
        assert len(sr.positions) > 0
        # Solar return should be in 2025
        assert sr.datetime.local_datetime.year == 2025

    def test_solar_return_sun_position_matches_natal(self, natal_chart):
        """Test that solar return Sun matches natal Sun longitude."""
        natal_sun = natal_chart.get_object("Sun")
        sr = ReturnBuilder.solar(natal_chart, 2025).calculate()
        sr_sun = sr.get_object("Sun")

        # Solar return Sun should be very close to natal Sun position
        # (within ~0.01 degrees due to calculation precision)
        diff = abs(natal_sun.longitude - sr_sun.longitude)
        # Handle wraparound at 360°
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.1, f"Sun positions differ by {diff}°"

    def test_solar_return_metadata(self, natal_chart):
        """Test solar return has correct metadata."""
        sr = ReturnBuilder.solar(natal_chart, 2025).calculate()

        assert sr.metadata.get("chart_type") == "return"
        assert sr.metadata.get("return_planet") == "Sun"
        assert "natal_planet_longitude" in sr.metadata
        assert "return_julian_day" in sr.metadata

    def test_solar_return_with_name(self, natal_chart):
        """Test solar return includes name in chart name."""
        # Add name to natal chart metadata
        natal_chart = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY", name="Kate"
        ).calculate()

        sr = ReturnBuilder.solar(natal_chart, 2025).calculate()

        assert "Kate" in sr.metadata.get("name", "")
        assert "Sun Return" in sr.metadata.get("name", "")
        assert "2025" in sr.metadata.get("name", "")


class TestSolarReturnRelocated:
    """Tests for relocated solar returns."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_relocated_solar_return_string_location(self, natal_chart):
        """Test relocated solar return with string location."""
        sr = ReturnBuilder.solar(
            natal_chart, 2025, location="Los Angeles, CA"
        ).calculate()

        assert sr is not None
        # Location should be Los Angeles, not New York
        assert "Los Angeles" in sr.location.name or sr.location.longitude < -100

    def test_relocated_solar_return_tuple_location(self, natal_chart):
        """Test relocated solar return with (lat, lon) tuple."""
        sr = ReturnBuilder.solar(
            natal_chart,
            2025,
            location=(34.0522, -118.2437),  # Los Angeles
        ).calculate()

        assert sr is not None
        assert abs(sr.location.latitude - 34.0522) < 0.01
        assert abs(sr.location.longitude - (-118.2437)) < 0.01


class TestLunarReturn:
    """Tests for lunar return calculation."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_lunar_return_near_date(self, natal_chart):
        """Test lunar return nearest to a specific date."""
        lr = ReturnBuilder.lunar(natal_chart, near_date="2025-03-15").calculate()

        assert lr is not None
        assert len(lr.positions) > 0
        # Should be around March 2025
        assert lr.datetime.local_datetime.year == 2025

    def test_lunar_return_by_occurrence(self, natal_chart):
        """Test lunar return by occurrence number."""
        lr = ReturnBuilder.lunar(natal_chart, occurrence=100).calculate()

        assert lr is not None
        assert lr.metadata.get("return_number") == 100

    def test_lunar_return_defaults_to_now(self, natal_chart):
        """Test lunar return defaults to current date when no params."""
        lr = ReturnBuilder.lunar(natal_chart).calculate()

        assert lr is not None
        # Should be relatively recent
        now = datetime.now()
        lr_date = lr.datetime.local_datetime
        # Should be within a month of now
        delta = abs((now - lr_date.replace(tzinfo=None)).days)
        assert delta < 60

    def test_lunar_return_moon_position_matches_natal(self, natal_chart):
        """Test lunar return Moon matches natal Moon longitude."""
        natal_moon = natal_chart.get_object("Moon")
        lr = ReturnBuilder.lunar(natal_chart, near_date="2025-03-15").calculate()
        lr_moon = lr.get_object("Moon")

        # Moon positions should be very close
        diff = abs(natal_moon.longitude - lr_moon.longitude)
        if diff > 180:
            diff = 360 - diff
        assert diff < 0.5, f"Moon positions differ by {diff}°"


class TestPlanetaryReturn:
    """Tests for planetary returns (Saturn, Jupiter, etc.)."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_saturn_return_by_occurrence(self, natal_chart):
        """Test first Saturn return calculation."""
        # Saturn return takes ~29 years
        sr = ReturnBuilder.planetary(natal_chart, "Saturn", occurrence=1).calculate()

        assert sr is not None
        assert sr.metadata.get("return_planet") == "Saturn"
        assert sr.metadata.get("return_number") == 1

    def test_jupiter_return_near_date(self, natal_chart):
        """Test Jupiter return nearest to date."""
        jr = ReturnBuilder.planetary(
            natal_chart, "Jupiter", near_date="2025-06-01"
        ).calculate()

        assert jr is not None
        assert jr.metadata.get("return_planet") == "Jupiter"

    def test_planetary_return_requires_date_or_occurrence(self, natal_chart):
        """Test planetary return requires either near_date or occurrence."""
        with pytest.raises(ValueError) as exc_info:
            ReturnBuilder.planetary(natal_chart, "Saturn")

        assert "Must specify" in str(exc_info.value)

    def test_planetary_return_invalid_planet_raises_error(self, natal_chart):
        """Test planetary return with invalid planet raises error."""
        with pytest.raises(ValueError) as exc_info:
            ReturnBuilder.planetary(
                natal_chart, "NonexistentPlanet", occurrence=1
            ).calculate()

        assert "not found" in str(exc_info.value)


class TestReturnBuilderConfiguration:
    """Tests for deferred configuration methods."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_with_ephemeris(self, natal_chart):
        """Test with_ephemeris() deferred configuration."""
        from stellium.engines.ephemeris import SwissEphemerisEngine

        sr = (
            ReturnBuilder.solar(natal_chart, 2025)
            .with_ephemeris(SwissEphemerisEngine())
            .calculate()
        )

        assert sr is not None

    def test_with_house_systems(self, natal_chart):
        """Test with_house_systems() deferred configuration."""
        sr = (
            ReturnBuilder.solar(natal_chart, 2025)
            .with_house_systems([WholeSignHouses()])
            .calculate()
        )

        assert "Whole Sign" in sr.house_systems
        assert "Placidus" not in sr.house_systems

    def test_add_house_system(self, natal_chart):
        """Test add_house_system() deferred configuration."""
        sr = (
            ReturnBuilder.solar(natal_chart, 2025)
            .add_house_system(WholeSignHouses())
            .calculate()
        )

        # Should have both default and added systems
        assert "Whole Sign" in sr.house_systems

    def test_add_house_system_initializes_list(self, natal_chart):
        """Test add_house_system() initializes list when None."""
        builder = ReturnBuilder.solar(natal_chart, 2025)
        builder._deferred_house_systems = None  # Ensure it's None

        builder.add_house_system(WholeSignHouses())

        assert builder._deferred_house_systems is not None
        assert len(builder._deferred_house_systems) == 1

    def test_with_aspects(self, natal_chart):
        """Test with_aspects() deferred configuration."""
        sr = (
            ReturnBuilder.solar(natal_chart, 2025)
            .with_aspects(ModernAspectEngine())
            .calculate()
        )

        assert len(sr.aspects) > 0

    def test_with_aspects_default_enabled(self, natal_chart):
        """Test aspects are enabled by default in returns."""
        sr = ReturnBuilder.solar(natal_chart, 2025).calculate()

        # Default behavior enables aspects
        assert len(sr.aspects) > 0

    def test_with_orbs(self, natal_chart):
        """Test with_orbs() deferred configuration."""
        custom_orbs = SimpleOrbEngine(orb_map={"Conjunction": 5.0, "Trine": 4.0})
        sr = ReturnBuilder.solar(natal_chart, 2025).with_orbs(custom_orbs).calculate()

        assert sr is not None

    def test_add_component(self, natal_chart):
        """Test add_component() deferred configuration."""
        from stellium.components.arabic_parts import ArabicPartsCalculator

        sr = (
            ReturnBuilder.solar(natal_chart, 2025)
            .add_component(ArabicPartsCalculator())
            .calculate()
        )

        position_names = [p.name for p in sr.positions]
        assert "Part of Fortune" in position_names

    def test_add_analyzer(self, natal_chart):
        """Test add_analyzer() deferred configuration."""
        sr = (
            ReturnBuilder.solar(natal_chart, 2025)
            .add_analyzer(AspectPatternAnalyzer())
            .calculate()
        )

        assert "aspect_patterns" in sr.metadata

    def test_with_config(self, natal_chart):
        """Test with_config() deferred configuration."""
        from stellium.core.config import CalculationConfig

        config = CalculationConfig(include_chiron=False)
        sr = ReturnBuilder.solar(natal_chart, 2025).with_config(config).calculate()

        position_names = [p.name for p in sr.positions]
        assert "Chiron" not in position_names


class TestReturnBuilderChaining:
    """Tests for method chaining."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_all_methods_chainable(self, natal_chart):
        """Test all configuration methods return builder for chaining."""
        from stellium.components.arabic_parts import ArabicPartsCalculator

        builder = (
            ReturnBuilder.solar(natal_chart, 2025)
            .with_house_systems([PlacidusHouses()])
            .add_house_system(WholeSignHouses())
            .with_aspects(ModernAspectEngine())
            .with_orbs(SimpleOrbEngine())
            .add_component(ArabicPartsCalculator())
            .add_analyzer(AspectPatternAnalyzer())
        )

        assert isinstance(builder, ReturnBuilder)

        chart = builder.calculate()
        assert chart is not None


class TestReturnInfo:
    """Tests for ReturnInfo dataclass."""

    def test_return_info_creation(self):
        """Test ReturnInfo can be created."""
        from stellium.core.models import ChartLocation

        loc = ChartLocation(latitude=40.0, longitude=-74.0, name="Test")
        info = ReturnInfo(
            return_jd=2460000.5,
            return_datetime=datetime(2025, 1, 15, 12, 0),
            natal_longitude=123.45,
            return_number=1,
            location=loc,
        )

        assert info.return_jd == 2460000.5
        assert info.natal_longitude == 123.45
        assert info.return_number == 1

    def test_return_info_none_return_number(self):
        """Test ReturnInfo with None return_number (for near_date returns)."""
        from stellium.core.models import ChartLocation

        loc = ChartLocation(latitude=40.0, longitude=-74.0, name="Test")
        info = ReturnInfo(
            return_jd=2460000.5,
            return_datetime=datetime(2025, 1, 15, 12, 0),
            natal_longitude=123.45,
            return_number=None,  # near_date returns don't have occurrence number
            location=loc,
        )

        assert info.return_number is None


class TestReturnNearDateParsing:
    """Tests for near_date parsing in returns."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_near_date_string_iso_format(self, natal_chart):
        """Test near_date with ISO format string."""
        lr = ReturnBuilder.lunar(natal_chart, near_date="2025-03-15").calculate()

        assert lr is not None

    def test_near_date_string_with_time(self, natal_chart):
        """Test near_date with string including time."""
        lr = ReturnBuilder.lunar(
            natal_chart, near_date="2025-03-15 14:30:00"
        ).calculate()

        assert lr is not None

    def test_near_date_datetime_object(self, natal_chart):
        """Test near_date with datetime object."""
        lr = ReturnBuilder.lunar(
            natal_chart, near_date=datetime(2025, 3, 15, 14, 30)
        ).calculate()

        assert lr is not None

    def test_near_date_datetime_with_timezone(self, natal_chart):
        """Test near_date with timezone-aware datetime."""
        import pytz

        lr = ReturnBuilder.lunar(
            natal_chart, near_date=datetime(2025, 3, 15, 14, 30, tzinfo=pytz.UTC)
        ).calculate()

        assert lr is not None


class TestReturnYearCalculation:
    """Tests for year-based return calculation (Solar returns)."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_solar_return_different_years(self, natal_chart):
        """Test solar returns for different years."""
        sr_2024 = ReturnBuilder.solar(natal_chart, 2024).calculate()
        sr_2025 = ReturnBuilder.solar(natal_chart, 2025).calculate()

        assert sr_2024.datetime.local_datetime.year == 2024
        assert sr_2025.datetime.local_datetime.year == 2025

        # Should be ~1 year apart
        delta = sr_2025.datetime.julian_day - sr_2024.datetime.julian_day
        assert 364 < delta < 367  # Allow for variation

    def test_solar_return_past_year(self, natal_chart):
        """Test solar return for past year."""
        sr = ReturnBuilder.solar(natal_chart, 2020).calculate()

        assert sr.datetime.local_datetime.year == 2020


class TestReturnBuilderEnsureBuilder:
    """Tests for _ensure_builder() lazy initialization."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_builder_created_on_calculate(self, natal_chart):
        """Test inner builder is created when calculate() is called."""
        builder = ReturnBuilder.solar(natal_chart, 2025)

        # Before calculate, inner builder should be None
        assert builder._inner_builder is None

        chart = builder.calculate()

        # After calculate, inner builder should exist
        assert builder._inner_builder is not None
        assert chart is not None

    def test_builder_not_recreated_on_second_call(self, natal_chart):
        """Test inner builder is not recreated on second _ensure_builder() call."""
        builder = ReturnBuilder.solar(natal_chart, 2025)

        builder._ensure_builder()
        first_builder = builder._inner_builder

        builder._ensure_builder()
        second_builder = builder._inner_builder

        assert first_builder is second_builder


class TestReturnLocationResolution:
    """Tests for _resolve_location() method."""

    @pytest.fixture
    def natal_chart(self):
        """Create natal chart."""
        native = Native("1990-01-15 10:00", "New York, NY")
        return ChartBuilder.from_native(native).calculate()

    def test_resolve_location_natal_default(self, natal_chart):
        """Test location defaults to natal location."""
        sr = ReturnBuilder.solar(natal_chart, 2025).calculate()

        # Should use natal location (New York)
        assert (
            "New York" in sr.location.name or abs(sr.location.longitude - (-74.0)) < 1.0
        )

    def test_resolve_location_chart_location_object(self, natal_chart):
        """Test location with ChartLocation object."""
        from stellium.core.models import ChartLocation

        la_loc = ChartLocation(
            latitude=34.0522, longitude=-118.2437, name="Los Angeles"
        )

        sr = ReturnBuilder.solar(natal_chart, 2025, location=la_loc).calculate()

        assert abs(sr.location.latitude - 34.0522) < 0.01
