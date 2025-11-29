"""
Pytest Configuration and Shared Test Fixtures.

This file contains reusable test fixtures that can be used across all test files.
Fixtures help reduce code duplication and make tests more maintainable.

=== TESTING CONCEPTS FOR BEGINNERS ===

1. **What are fixtures?**
   Fixtures are reusable pieces of test data or setup code. Instead of creating
   the same test data in every test, you define it once as a fixture and reuse it.

2. **How to use fixtures:**
   Simply add the fixture name as a parameter to your test function:

   def test_something(sample_chart):  # 'sample_chart' is a fixture
       assert sample_chart is not None

3. **Fixture scopes:**
   - "function" (default): New instance for each test
   - "class": Shared across all tests in a test class
   - "module": Shared across all tests in a file
   - "session": Shared across all test files

4. **When to use each fixture:**

   DATETIME FIXTURES:
   - Use `utc_datetime` when you need a simple timezone-aware datetime
   - Use `local_datetime` when testing timezone-naive scenarios
   - Use `historical_datetime` for testing edge cases with old dates

   LOCATION FIXTURES:
   - Use `chart_location` for basic location testing
   - Use `sf_location` when you need a real US location
   - Use `london_location` for European/GMT timezone tests
   - Use `sydney_location` for Southern Hemisphere tests

   NATIVE FIXTURES:
   - Use `sample_native` for most basic chart tests
   - Use `historical_native` for testing historical date handling

   CHART FIXTURES:
   - Use `simple_chart` for quick tests that don't care about accuracy
   - Use `full_chart` when you need aspects, houses, etc.
   - Use `sample_positions` when you only need celestial positions

   COMPONENT FIXTURES:
   - Use `sample_aspects` when testing aspect-related code
   - Use these when you need specific test data without full chart calculation

5. **Parametrized tests:**
   Some fixtures return lists of values for testing multiple scenarios:

   @pytest.mark.parametrize("house_system", house_systems())
   def test_all_house_systems(house_system):
       # This test runs once for each house system
       ...

=== AVAILABLE FIXTURES ===
"""

import datetime as dt
import os
from collections.abc import Generator

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.models import (
    Aspect,
    CelestialPosition,
    ChartLocation,
    ObjectType,
)
from stellium.core.native import Native
from stellium.engines.aspects import HarmonicAspectEngine, ModernAspectEngine
from stellium.engines.ephemeris import MockEphemerisEngine, SwissEphemerisEngine
from stellium.engines.houses import (
    CampanusHouses,
    EqualHouses,
    KochHouses,
    PlacidusHouses,
    PorphyryHouses,
    RegiomontanusHouses,
    WholeSignHouses,
)
from stellium.engines.orbs import LuminariesOrbEngine, SimpleOrbEngine

# ============================================================================
# DATETIME FIXTURES
# ============================================================================


@pytest.fixture
def utc_datetime() -> dt.datetime:
    """
    A basic UTC datetime for testing.

    Use this when: You need a simple, timezone-aware datetime for basic tests.
    Example: Testing chart serialization, basic calculations.
    """
    return dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)


@pytest.fixture
def local_datetime() -> dt.datetime:
    """
    A timezone-naive datetime for testing.

    Use this when: Testing scenarios where timezone is provided separately
    or when using Native class which handles timezone conversion.
    Example: Testing Native initialization, location-based timezone handling.
    """
    return dt.datetime(2000, 1, 1, 12, 0)


@pytest.fixture
def historical_datetime() -> dt.datetime:
    """
    A historical datetime for testing edge cases.

    Use this when: Testing historical chart calculations (pre-1900).
    Example: Testing ephemeris accuracy for old dates.
    """
    return dt.datetime(1879, 3, 14, 11, 30)  # Einstein's birth


@pytest.fixture
def future_datetime() -> dt.datetime:
    """
    A future datetime for testing transits/progressions.

    Use this when: Testing future transits, progressions, solar returns.
    Example: Calculating 2030 transits for a natal chart.
    """
    return dt.datetime(2030, 6, 15, 14, 30, tzinfo=dt.UTC)


# ============================================================================
# LOCATION FIXTURES
# ============================================================================


@pytest.fixture
def chart_location() -> ChartLocation:
    """
    A basic chart location at the equator.

    Use this when: You need a simple location for basic tests.
    Example: Testing chart serialization, basic location handling.
    """
    return ChartLocation(latitude=0, longitude=0, name="Test Location")


@pytest.fixture
def sf_location() -> ChartLocation:
    """
    San Francisco location for testing US/West Coast charts.

    Use this when: You need a real-world US location.
    Example: Testing Pacific timezone handling, US-based charts.
    """
    return ChartLocation(latitude=37.7749, longitude=-122.4194, name="San Francisco, CA")


@pytest.fixture
def london_location() -> ChartLocation:
    """
    London location for testing European/GMT charts.

    Use this when: You need a European location with GMT timezone.
    Example: Testing GMT/BST timezone handling.
    """
    return ChartLocation(latitude=51.5074, longitude=-0.1278, name="London, UK")


@pytest.fixture
def sydney_location() -> ChartLocation:
    """
    Sydney location for testing Southern Hemisphere charts.

    Use this when: Testing Southern Hemisphere house calculations.
    Example: Verifying houses work correctly below the equator.
    """
    return ChartLocation(latitude=-33.8688, longitude=151.2093, name="Sydney, Australia")


@pytest.fixture
def polar_location() -> ChartLocation:
    """
    High-latitude location for testing polar region edge cases.

    Use this when: Testing house systems at extreme latitudes.
    Example: Verifying Placidus handles high latitudes (may fail gracefully).
    """
    return ChartLocation(latitude=64.8378, longitude=-147.7164, name="Fairbanks, AK")


# ============================================================================
# NATIVE (BIRTH DATA) FIXTURES
# ============================================================================


@pytest.fixture
def sample_native(utc_datetime, chart_location) -> Native:
    """
    A basic Native (birth data) object for testing.

    Use this when: You need simple birth data for chart calculations.
    Example: Most chart calculation tests.
    """
    return Native(utc_datetime, chart_location)


@pytest.fixture
def historical_native(historical_datetime, london_location) -> Native:
    """
    Historical Native for testing old dates.

    Use this when: Testing historical chart accuracy.
    Example: Calculating Einstein's chart.
    """
    return Native(historical_datetime, london_location)


@pytest.fixture
def southern_hemisphere_native(utc_datetime, sydney_location) -> Native:
    """
    Native for Southern Hemisphere testing.

    Use this when: Testing Southern Hemisphere house calculations.
    Example: Verifying houses in Australia.
    """
    return Native(utc_datetime, sydney_location)


# ============================================================================
# CELESTIAL POSITION FIXTURES
# ============================================================================


@pytest.fixture
def sample_positions() -> list[CelestialPosition]:
    """
    A list of sample celestial positions for testing.

    Use this when: You need positions without calculating a full chart.
    Example: Testing aspect calculations, position filtering.
    """
    return [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=45.5,  # Mid-Taurus
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=165.5,  # Mid-Virgo (120° from Sun - Trine)
            latitude=0.0,
            distance=1.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=50.0,  # Close to Sun (conjunction)
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.2,
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=135.5,  # 90° from Sun (square)
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.1,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=225.5,  # 180° from Sun (opposition)
            latitude=0.0,
            distance=1.0,
            speed_longitude=0.5,
        ),
    ]


@pytest.fixture
def grand_trine_positions() -> list[CelestialPosition]:
    """
    Positions forming a Grand Trine (perfect 120° triangle).

    Use this when: Testing aspect pattern detection (Grand Trine).
    Example: Testing pattern analyzer.
    """
    return [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,  # 0° Aries
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=120.0,  # 0° Leo (120° trine)
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Jupiter",
            object_type=ObjectType.PLANET,
            longitude=240.0,  # 0° Sagittarius (120° trine)
            speed_longitude=0.08,
        ),
    ]


@pytest.fixture
def t_square_positions() -> list[CelestialPosition]:
    """
    Positions forming a T-Square (two squares + opposition).

    Use this when: Testing T-Square pattern detection.
    Example: Testing pattern analyzer.
    """
    return [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,  # 0° Aries
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=180.0,  # 0° Libra (opposition)
            speed_longitude=0.5,
        ),
        CelestialPosition(
            name="Pluto",
            object_type=ObjectType.PLANET,
            longitude=90.0,  # 0° Cancer (square to both)
            speed_longitude=0.01,
        ),
    ]


@pytest.fixture
def stellium_positions() -> list[CelestialPosition]:
    """
    Positions forming a Stellium (3+ planets in same sign).

    Use this when: Testing Stellium detection.
    Example: Testing pattern analyzer.
    """
    return [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=45.0,  # 15° Taurus
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=50.0,  # 20° Taurus
            speed_longitude=1.2,
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=55.0,  # 25° Taurus
            speed_longitude=1.1,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=58.0,  # 28° Taurus
            speed_longitude=0.5,
        ),
    ]


# ============================================================================
# ASPECT FIXTURES
# ============================================================================


@pytest.fixture
def sample_aspects(sample_positions) -> list[Aspect]:
    """
    Sample aspects calculated from sample_positions.

    Use this when: You need aspects without full chart calculation.
    Example: Testing aspect filtering, aspect analysis.
    """
    engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    return engine.calculate_aspects(sample_positions, orb_engine)


@pytest.fixture
def aspect_info_conjunction():
    """
    AspectInfo for Conjunction (0°).

    Use this when: Testing aspect-specific logic for conjunctions.
    """
    from stellium.core.registry import ASPECT_REGISTRY

    return ASPECT_REGISTRY.get_aspect("Conjunction")


@pytest.fixture
def aspect_info_trine():
    """
    AspectInfo for Trine (120°).

    Use this when: Testing aspect-specific logic for trines.
    """
    from stellium.core.registry import ASPECT_REGISTRY

    return ASPECT_REGISTRY.get_aspect("Trine")


# ============================================================================
# CHART FIXTURES
# ============================================================================


@pytest.fixture
def simple_chart(sample_native):
    """
    A simple chart with mock ephemeris (fast, no real calculations).

    Use this when: You need a chart quickly and don't care about accuracy.
    Example: Testing chart structure, serialization.
    """
    return (
        ChartBuilder.from_native(sample_native)
        .with_ephemeris(MockEphemerisEngine())
        .calculate()
    )


@pytest.fixture
def full_chart(sample_native):
    """
    A full chart with real ephemeris, houses, and aspects.

    Use this when: You need accurate calculations with all features.
    Example: Integration tests, real-world scenario tests.
    """
    return (
        ChartBuilder.from_native(sample_native)
        .with_ephemeris(SwissEphemerisEngine())
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects(ModernAspectEngine())
        .with_orbs(LuminariesOrbEngine())
        .calculate()
    )


@pytest.fixture
def chart_with_all_house_systems(sample_native):
    """
    Chart with all available house systems.

    Use this when: Testing house system comparisons.
    Example: Verifying all house systems work correctly.
    """
    return (
        ChartBuilder.from_native(sample_native)
        .with_house_systems(
            [
                PlacidusHouses(),
                WholeSignHouses(),
                KochHouses(),
                EqualHouses(),
                PorphyryHouses(),
                RegiomontanusHouses(),
                CampanusHouses(),
            ]
        )
        .calculate()
    )


# ============================================================================
# ENGINE FIXTURES
# ============================================================================


@pytest.fixture
def mock_ephemeris() -> MockEphemerisEngine:
    """
    Mock ephemeris engine for fast testing.

    Use this when: Speed is more important than accuracy.
    Example: Unit tests, structure tests.
    """
    return MockEphemerisEngine()


@pytest.fixture
def swiss_ephemeris() -> SwissEphemerisEngine:
    """
    Real Swiss Ephemeris engine for accurate calculations.

    Use this when: You need accurate planetary positions.
    Example: Integration tests, accuracy verification.
    """
    return SwissEphemerisEngine()


@pytest.fixture
def modern_aspect_engine() -> ModernAspectEngine:
    """
    Modern aspect engine (includes minor aspects).

    Use this when: Testing modern aspect calculations.
    """
    return ModernAspectEngine()


@pytest.fixture
def harmonic_aspect_engine() -> HarmonicAspectEngine:
    """
    Harmonic aspect engine (for harmonic aspects like septiles, noviles).

    Use this when: Testing harmonic aspect calculations.
    """
    return HarmonicAspectEngine(harmonic=7)  # Septile series


@pytest.fixture
def simple_orb_engine() -> SimpleOrbEngine:
    """
    Simple orb engine with default orbs.

    Use this when: You don't need custom orb calculations.
    """
    return SimpleOrbEngine()


@pytest.fixture
def luminaries_orb_engine() -> LuminariesOrbEngine:
    """
    Orb engine with larger orbs for Sun/Moon.

    Use this when: Testing luminaries-specific orb handling.
    """
    return LuminariesOrbEngine()


# ============================================================================
# PARAMETRIZED FIXTURE DATA
# ============================================================================


def pytest_generate_tests(metafunc):
    """
    Generate parametrized tests for common scenarios.

    This function is called by pytest to generate test parameters.
    """
    # Parametrize all zodiac signs
    if "zodiac_sign" in metafunc.fixturenames:
        signs = [
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
        metafunc.parametrize("zodiac_sign", signs)

    # Parametrize all house systems
    if "house_system_class" in metafunc.fixturenames:
        systems = [
            PlacidusHouses,
            WholeSignHouses,
            KochHouses,
            EqualHouses,
            PorphyryHouses,
            RegiomontanusHouses,
            CampanusHouses,
        ]
        metafunc.parametrize("house_system_class", systems)


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


# Pre-geocoded locations for CI testing (avoids Nominatim network calls)
# These are used when CI=true environment variable is set (GitHub Actions)
GEOCODED_LOCATIONS = {
    # US Locations
    "Palo Alto, CA": {
        "latitude": 37.4419,
        "longitude": -122.1430,
        "address": "Palo Alto, Santa Clara County, California, USA",
        "timezone": "America/Los_Angeles",
    },
    "New York, NY": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "address": "New York, New York, USA",
        "timezone": "America/New_York",
    },
    "Seattle, WA": {
        "latitude": 47.6062,
        "longitude": -122.3321,
        "address": "Seattle, King County, Washington, USA",
        "timezone": "America/Los_Angeles",
    },
    "Los Angeles, CA": {
        "latitude": 34.0522,
        "longitude": -118.2437,
        "address": "Los Angeles, Los Angeles County, California, USA",
        "timezone": "America/Los_Angeles",
    },
    "San Francisco, CA": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "San Francisco, San Francisco County, California, USA",
        "timezone": "America/Los_Angeles",
    },
    # International Locations
    "Ulm, Germany": {
        "latitude": 48.4011,
        "longitude": 9.9876,
        "address": "Ulm, Baden-Württemberg, Germany",
        "timezone": "Europe/Berlin",
    },
    "Tokyo, Japan": {
        "latitude": 35.6762,
        "longitude": 139.6503,
        "address": "Tokyo, Japan",
        "timezone": "Asia/Tokyo",
    },
    "London, UK": {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "address": "London, Greater London, England, United Kingdom",
        "timezone": "Europe/London",
    },
    "Sydney, Australia": {
        "latitude": -33.8688,
        "longitude": 151.2093,
        "address": "Sydney, New South Wales, Australia",
        "timezone": "Australia/Sydney",
    },
    "Fairbanks, AK": {
        "latitude": 64.8378,
        "longitude": -147.7164,
        "address": "Fairbanks, Fairbanks North Star Borough, Alaska, USA",
        "timezone": "America/Anchorage",
    },
}


@pytest.fixture(autouse=True)
def mock_geocoding_in_ci(monkeypatch):
    """
    Mock geocoding when running in CI to avoid network calls.

    GitHub Actions sets CI=true. Locally, real geocoding is used with the
    file-based cache (~/.cache/geocoding/).

    This fixture is autouse=True, so it applies to ALL tests automatically.
    """
    # Only mock in CI environments
    if not os.environ.get("CI"):
        return  # Local dev - use real geocoding with cache

    def mock_cached_geocode(location_name: str) -> dict:
        """Mock implementation of _cached_geocode for CI testing."""
        normalized = location_name.strip()

        # Check exact match first
        if normalized in GEOCODED_LOCATIONS:
            return GEOCODED_LOCATIONS[normalized]

        # Check case-insensitive partial match
        for key, value in GEOCODED_LOCATIONS.items():
            if key.lower() in normalized.lower() or normalized.lower() in key.lower():
                return value

        # Fallback: return a default location (prevents test failure)
        # This handles any locations we haven't pre-geocoded
        return {
            "latitude": 0.0,
            "longitude": 0.0,
            "address": normalized,
            "timezone": "UTC",
        }

    monkeypatch.setattr(
        "stellium.core.native._cached_geocode",
        mock_cached_geocode
    )


@pytest.fixture
def temp_cache_dir(tmp_path) -> Generator[str, None, None]:
    """
    Temporary directory for cache testing.

    Use this when: Testing cache functionality.
    Example: Testing cache storage, cache invalidation.
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    yield str(cache_dir)
    # Cleanup happens automatically via tmp_path
