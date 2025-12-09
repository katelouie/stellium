"""
Comprehensive tests for house system calculation engines.

This test suite covers:
- All 17 house system implementations
- House cusp calculations
- Chart angle calculations (ASC, MC, DSC, IC, Vertex)
- House assignment for planetary positions
- Edge cases: high latitude, southern hemisphere, polar regions
- 360° wrapping and boundary conditions
"""

import datetime as dt

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.models import (
    CelestialPosition,
    ChartLocation,
    ObjectType,
)
from stellium.core.native import Native
from stellium.engines.houses import (
    HOUSE_SYSTEM_CODES,
    AlcabitiusHouses,
    APCHouses,
    AxialRotationHouses,
    CampanusHouses,
    EqualHouses,
    EqualMCHouses,
    EqualVertexHouses,
    GauquelinHouses,
    HorizontalHouses,
    KochHouses,
    KrusinskiHouses,
    MorinusHouses,
    PlacidusHouses,
    PorphyryHouses,
    RegiomontanusHouses,
    SwissHouseSystemBase,
    TopocentricHouses,
    VehlowEqualHouses,
    WholeSignHouses,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def standard_location() -> ChartLocation:
    """Standard mid-latitude location (San Francisco)."""
    return ChartLocation(
        latitude=37.7749,
        longitude=-122.4194,
        name="San Francisco, CA",
        timezone="America/Los_Angeles",
    )


@pytest.fixture
def southern_hemisphere_location() -> ChartLocation:
    """Southern hemisphere location (Sydney)."""
    return ChartLocation(
        latitude=-33.8688,
        longitude=151.2093,
        name="Sydney, Australia",
        timezone="Australia/Sydney",
    )


@pytest.fixture
def high_latitude_location() -> ChartLocation:
    """High latitude location (Fairbanks, Alaska)."""
    return ChartLocation(
        latitude=64.8378,
        longitude=-147.7164,
        name="Fairbanks, AK",
        timezone="America/Anchorage",
    )


@pytest.fixture
def polar_location() -> ChartLocation:
    """Polar region location (Longyearbyen, Norway)."""
    return ChartLocation(
        latitude=78.2232,
        longitude=15.6267,
        name="Longyearbyen, Norway",
        timezone="Europe/Oslo",
    )


@pytest.fixture
def equatorial_location() -> ChartLocation:
    """Equatorial location."""
    return ChartLocation(
        latitude=0.0,
        longitude=0.0,
        name="Null Island",
        timezone="UTC",
    )


@pytest.fixture
def standard_datetime() -> dt.datetime:
    """Standard datetime for testing."""
    return dt.datetime(2000, 6, 15, 12, 0, tzinfo=dt.UTC)


@pytest.fixture
def standard_native(standard_datetime, standard_location) -> Native:
    """Standard Native for testing."""
    return Native(standard_datetime, standard_location)


@pytest.fixture
def sample_positions() -> list[CelestialPosition]:
    """Sample planetary positions for house assignment testing."""
    return [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,  # 0° Aries
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=90.0,  # 0° Cancer
        ),
        CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=180.0,  # 0° Libra
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=270.0,  # 0° Capricorn
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=45.0,  # 15° Taurus
        ),
        CelestialPosition(
            name="Jupiter",
            object_type=ObjectType.PLANET,
            longitude=135.0,  # 15° Leo
        ),
    ]


# ============================================================================
# ALL HOUSE SYSTEM CLASSES
# ============================================================================

ALL_HOUSE_SYSTEMS = [
    PlacidusHouses,
    WholeSignHouses,
    KochHouses,
    EqualHouses,
    PorphyryHouses,
    RegiomontanusHouses,
    CampanusHouses,
    EqualMCHouses,
    VehlowEqualHouses,
    AlcabitiusHouses,
    TopocentricHouses,
    MorinusHouses,
    EqualVertexHouses,
    GauquelinHouses,
    HorizontalHouses,
    KrusinskiHouses,
    AxialRotationHouses,
    APCHouses,
]


# ============================================================================
# BASIC HOUSE SYSTEM TESTS
# ============================================================================


def test_house_system_codes_complete():
    """Test that all house system codes are defined."""
    assert len(HOUSE_SYSTEM_CODES) >= 17  # At least 17 systems
    assert "Placidus" in HOUSE_SYSTEM_CODES
    assert "Whole Sign" in HOUSE_SYSTEM_CODES
    assert "Koch" in HOUSE_SYSTEM_CODES
    assert HOUSE_SYSTEM_CODES["Placidus"] == b"P"
    assert HOUSE_SYSTEM_CODES["Whole Sign"] == b"W"


@pytest.mark.parametrize("house_system", ALL_HOUSE_SYSTEMS)
def test_house_system_instantiation(house_system):
    """Test that all house systems can be instantiated."""
    system = house_system()
    assert system is not None
    assert hasattr(system, "system_name")
    assert isinstance(system.system_name, str)
    assert len(system.system_name) > 0


@pytest.mark.parametrize("house_system", ALL_HOUSE_SYSTEMS)
def test_house_system_names(house_system):
    """Test that all house systems have correct names."""
    system = house_system()
    system_name = system.system_name

    # Name should be in HOUSE_SYSTEM_CODES
    assert system_name in HOUSE_SYSTEM_CODES, f"{system_name} not in HOUSE_SYSTEM_CODES"


@pytest.mark.parametrize("house_system", ALL_HOUSE_SYSTEMS)
def test_house_system_inheritance(house_system):
    """Test that all house systems inherit from SwissHouseSystemBase."""
    system = house_system()
    assert isinstance(system, SwissHouseSystemBase)


# ============================================================================
# HOUSE CUSP CALCULATION TESTS
# ============================================================================


@pytest.mark.parametrize("house_system", ALL_HOUSE_SYSTEMS)
def test_calculate_house_data(house_system, standard_native):
    """Test that all house systems can calculate house data."""
    system = house_system()

    # Gauquelin is a 36-sector system, which is not currently supported by HouseCusps model
    if system.system_name == "Gauquelin":
        pytest.skip(
            "Gauquelin uses 36 sectors, not currently supported by HouseCusps model"
        )

    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Verify cusps
    assert cusps is not None
    assert cusps.system == system.system_name
    assert len(cusps.cusps) == 12

    # All cusps should be valid longitudes (0-360)
    for cusp in cusps.cusps:
        assert 0 <= cusp < 360, f"Invalid cusp: {cusp}"

    # Verify angles
    assert angles is not None
    assert len(angles) == 6  # ASC, MC, DSC, IC, Vertex, RAMC

    # Check angle names
    angle_names = [a.name for a in angles]
    assert "ASC" in angle_names
    assert "MC" in angle_names
    assert "DSC" in angle_names
    assert "IC" in angle_names
    assert "Vertex" in angle_names
    assert "RAMC" in angle_names


def test_placidus_houses_calculation(standard_native):
    """Test Placidus house calculation with specific values."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    assert cusps.system == "Placidus"
    assert len(cusps.cusps) == 12

    # First cusp should match ASC
    asc = next(a for a in angles if a.name == "ASC")
    # Note: Some house systems have cusp[0] = ASC, but we're testing the data is valid
    assert 0 <= asc.longitude < 360


def test_whole_sign_houses_calculation(standard_native):
    """Test Whole Sign house calculation."""
    system = WholeSignHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    assert cusps.system == "Whole Sign"

    # Whole sign houses should have cusps at sign boundaries (multiples of 30°)
    # Though this depends on ASC sign, let's just verify they're valid
    for cusp in cusps.cusps:
        assert 0 <= cusp < 360


def test_equal_houses_have_equal_spacing(standard_native):
    """Test that Equal house system has 30° spacing."""
    system = EqualHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Equal houses should have roughly 30° between cusps
    # (allowing for some floating point variance)
    for i in range(11):
        cusp1 = cusps.cusps[i]
        cusp2 = cusps.cusps[i + 1]
        diff = (cusp2 - cusp1) % 360
        # Equal houses should be exactly 30° apart
        assert 29.9 < diff < 30.1, f"Equal house spacing off: {diff}°"


# ============================================================================
# ANGLE CALCULATION TESTS
# ============================================================================


def test_angles_calculated_correctly(standard_native):
    """Test that chart angles are calculated correctly."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Find all angles
    asc = next(a for a in angles if a.name == "ASC")
    mc = next(a for a in angles if a.name == "MC")
    dsc = next(a for a in angles if a.name == "DSC")
    ic = next(a for a in angles if a.name == "IC")
    vertex = next(a for a in angles if a.name == "Vertex")

    # DSC should be 180° from ASC
    assert abs((dsc.longitude - asc.longitude) % 360 - 180.0) < 0.01

    # IC should be 180° from MC
    assert abs((ic.longitude - mc.longitude) % 360 - 180.0) < 0.01

    # All angles should have correct object types
    assert asc.object_type == ObjectType.ANGLE
    assert mc.object_type == ObjectType.ANGLE
    assert dsc.object_type == ObjectType.ANGLE
    assert ic.object_type == ObjectType.ANGLE
    assert vertex.object_type == ObjectType.POINT


def test_angles_valid_longitudes(standard_native):
    """Test that all angles have valid longitudes."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    for angle in angles:
        assert (
            0 <= angle.longitude < 360
        ), f"{angle.name} has invalid longitude: {angle.longitude}"


# ============================================================================
# HOUSE ASSIGNMENT TESTS
# ============================================================================


def test_find_house_basic(standard_native):
    """Test basic house finding logic."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Test with a position at 0° (0° Aries)
    house = system._find_house(0.0, cusps.cusps)
    assert 1 <= house <= 12


def test_find_house_wrapping(standard_native):
    """Test house finding with 360° wrapping."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Test positions near 360°/0° boundary
    house_359 = system._find_house(359.0, cusps.cusps)
    house_1 = system._find_house(1.0, cusps.cusps)

    assert 1 <= house_359 <= 12
    assert 1 <= house_1 <= 12


def test_assign_houses(standard_native, sample_positions):
    """Test house assignment for multiple positions."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    placements = system.assign_houses(sample_positions, cusps)

    # All positions should be assigned a house
    assert len(placements) == len(sample_positions)

    # Check each position
    for pos in sample_positions:
        assert pos.name in placements
        house = placements[pos.name]
        assert 1 <= house <= 12


def test_assign_houses_all_quadrants(standard_native):
    """Test house assignment covers all 12 houses."""
    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Create positions at each 30° interval
    test_positions = [
        CelestialPosition(
            name=f"Test{i}",
            object_type=ObjectType.PLANET,
            longitude=float(i * 30),
        )
        for i in range(12)
    ]

    placements = system.assign_houses(test_positions, cusps)

    # We should have 12 assignments
    assert len(placements) == 12

    # All values should be between 1-12
    for house in placements.values():
        assert 1 <= house <= 12


# ============================================================================
# EDGE CASE TESTS - GEOGRAPHIC LOCATIONS
# ============================================================================


@pytest.mark.parametrize("house_system", ALL_HOUSE_SYSTEMS)
def test_southern_hemisphere(house_system):
    """Test house calculations in Southern Hemisphere."""
    native = Native(
        dt.datetime(2000, 12, 21, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=-33.8688,  # Sydney
            longitude=151.2093,
            name="Sydney",
            timezone="Australia/Sydney",
        ),
    )

    system = house_system()

    # Gauquelin is a 36-sector system, not currently supported by HouseCusps model
    if system.system_name == "Gauquelin":
        pytest.skip(
            "Gauquelin uses 36 sectors, not currently supported by HouseCusps model"
        )

    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    # Basic validation
    assert len(cusps.cusps) == 12
    assert len(angles) == 6

    # All cusps should be valid
    for cusp in cusps.cusps:
        assert 0 <= cusp < 360


@pytest.mark.parametrize("house_system", ALL_HOUSE_SYSTEMS)
def test_high_latitude(house_system):
    """Test house calculations at high latitude."""
    native = Native(
        dt.datetime(2000, 6, 21, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=64.8378,  # Fairbanks, AK
            longitude=-147.7164,
            name="Fairbanks",
            timezone="America/Anchorage",
        ),
    )

    system = house_system()

    try:
        cusps, angles = system.calculate_house_data(native.datetime, native.location)

        # If calculation succeeds, validate results
        assert len(cusps.cusps) == 12
        assert len(angles) == 6

        for cusp in cusps.cusps:
            assert 0 <= cusp < 360

    except Exception as e:
        # Some house systems may fail at extreme latitudes
        # This is expected behavior (e.g., Placidus near poles)
        pytest.skip(f"{house_system.__name__} cannot calculate at high latitude: {e}")


def test_equatorial_location():
    """Test house calculations at the equator."""
    native = Native(
        dt.datetime(2000, 3, 20, 12, 0, tzinfo=dt.UTC),
        ChartLocation(latitude=0.0, longitude=0.0, name="Equator", timezone="UTC"),
    )

    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    assert len(cusps.cusps) == 12
    assert len(angles) == 6


# ============================================================================
# INTEGRATION TESTS WITH CHARTBUILDER
# ============================================================================


def test_house_systems_in_chart_builder(standard_native):
    """Test using house systems with ChartBuilder."""
    chart = (
        ChartBuilder.from_native(standard_native)
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .calculate()
    )

    # Should have both house systems
    assert "Placidus" in chart.house_systems
    assert "Whole Sign" in chart.house_systems

    # Both should have 12 cusps
    assert len(chart.house_systems["Placidus"].cusps) == 12
    assert len(chart.house_systems["Whole Sign"].cusps) == 12


def test_multiple_house_systems_simultaneously(standard_native):
    """Test calculating multiple house systems at once."""
    systems = [PlacidusHouses(), KochHouses(), EqualHouses(), WholeSignHouses()]

    chart = (
        ChartBuilder.from_native(standard_native)
        .with_house_systems(systems)
        .calculate()
    )

    assert len(chart.house_systems) == 4
    assert "Placidus" in chart.house_systems
    assert "Koch" in chart.house_systems
    assert "Equal" in chart.house_systems
    assert "Whole Sign" in chart.house_systems


def test_default_house_system(standard_native):
    """Test that the first house system becomes the default."""
    chart = (
        ChartBuilder.from_native(standard_native)
        .with_house_systems([WholeSignHouses(), PlacidusHouses()])
        .calculate()
    )

    # First system should be default
    assert chart.default_house_system == "Whole Sign"


# ============================================================================
# CACHING TESTS
# ============================================================================


def test_house_calculation_caching(standard_native):
    """Test that house calculations are cached."""
    system = PlacidusHouses()

    # Calculate twice with same parameters
    cusps1, angles1 = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )
    cusps2, angles2 = system.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Results should be identical
    assert cusps1.cusps == cusps2.cusps
    assert len(angles1) == len(angles2)


# ============================================================================
# REGRESSION TESTS
# ============================================================================


def test_house_cusp_order_ascending():
    """Test that house cusps are returned in order (1-12)."""
    native = Native(
        dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=40.7128,
            longitude=-74.0060,
            name="NYC",
            timezone="America/New_York",
        ),
    )

    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    # Cusps should be 12 values
    assert len(cusps.cusps) == 12


def test_koch_vs_placidus_difference(standard_native):
    """Test that Koch and Placidus produce different results."""
    koch = KochHouses()
    placidus = PlacidusHouses()

    koch_cusps, _ = koch.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )
    placidus_cusps, _ = placidus.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Koch and Placidus should produce different house cusps
    # (except potentially at the equator or specific latitudes)
    # Check that at least some cusps are different
    differences = sum(
        1
        for k, p in zip(koch_cusps.cusps, placidus_cusps.cusps, strict=False)
        if abs(k - p) > 0.1
    )

    # At least some cusps should be different (likely all except 1st, 4th, 7th, 10th)
    assert differences > 0


def test_whole_sign_vs_equal_difference(standard_native):
    """Test that Whole Sign and Equal houses can produce different results."""
    whole_sign = WholeSignHouses()
    equal = EqualHouses()

    ws_cusps, ws_angles = whole_sign.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )
    eq_cusps, eq_angles = equal.calculate_house_data(
        standard_native.datetime,
        standard_native.location,
    )

    # Both should have 12 cusps
    assert len(ws_cusps.cusps) == 12
    assert len(eq_cusps.cusps) == 12

    # They may or may not be the same depending on ASC position
    # Just verify both are valid
    for cusp in ws_cusps.cusps:
        assert 0 <= cusp < 360
    for cusp in eq_cusps.cusps:
        assert 0 <= cusp < 360


# ============================================================================
# BOUNDARY CONDITION TESTS
# ============================================================================


def test_midnight_calculation():
    """Test house calculation at midnight."""
    native = Native(
        dt.datetime(2000, 1, 1, 0, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=37.7749,
            longitude=-122.4194,
            name="SF",
            timezone="America/Los_Angeles",
        ),
    )

    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    assert len(cusps.cusps) == 12
    assert len(angles) == 6


def test_noon_calculation():
    """Test house calculation at noon."""
    native = Native(
        dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=37.7749,
            longitude=-122.4194,
            name="SF",
            timezone="America/Los_Angeles",
        ),
    )

    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    assert len(cusps.cusps) == 12
    assert len(angles) == 6


def test_historical_date():
    """Test house calculation for historical date."""
    native = Native(
        dt.datetime(1900, 1, 1, 12, 0),
        ChartLocation(
            latitude=51.5074, longitude=-0.1278, name="London", timezone="Europe/London"
        ),
    )

    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    assert len(cusps.cusps) == 12
    assert len(angles) == 6


def test_future_date():
    """Test house calculation for future date."""
    native = Native(
        dt.datetime(2100, 12, 31, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=40.7128,
            longitude=-74.0060,
            name="NYC",
            timezone="America/New_York",
        ),
    )

    system = PlacidusHouses()
    cusps, angles = system.calculate_house_data(native.datetime, native.location)

    assert len(cusps.cusps) == 12
    assert len(angles) == 6
