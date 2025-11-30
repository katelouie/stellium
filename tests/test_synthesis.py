"""
Tests for synthesis charts (Davison and Composite).
"""

import datetime as dt

import pytest
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import CalculatedChart, ChartDateTime, ChartLocation
from stellium.core.synthesis import (
    SynthesisBuilder,
    SynthesisChart,
    calculate_datetime_midpoint,
    calculate_location_midpoint,
    calculate_midpoint_longitude,
    julian_day_to_datetime,
)

# =============================================================================
# Helper Function Tests
# =============================================================================


class TestMidpointLongitude:
    """Tests for zodiac longitude midpoint calculation."""

    def test_same_sign_midpoint(self):
        """Test midpoint when both planets in same sign."""
        assert calculate_midpoint_longitude(10, 20) == 15.0

    def test_same_sign_midpoint_reversed(self):
        """Test midpoint when arguments reversed."""
        assert calculate_midpoint_longitude(20, 10) == 15.0

    def test_adjacent_signs_midpoint(self):
        """Test midpoint crossing sign boundary."""
        # 25 Aries and 5 Taurus = 0 Taurus (30 degrees)
        result = calculate_midpoint_longitude(25, 35)
        assert result == 30.0

    def test_opposite_signs_short_arc(self):
        """Test short arc midpoint for opposite planets."""
        # 10 Aries (10) and 10 Libra (190)
        # Short arc midpoint = 10 Cancer (100)
        result = calculate_midpoint_longitude(10, 190, "short_arc")
        assert result == 100.0

    def test_opposite_signs_long_arc(self):
        """Test long arc midpoint for opposite planets."""
        # 10 Aries (10) and 10 Libra (190)
        # Long arc midpoint = 10 Capricorn (280)
        result = calculate_midpoint_longitude(10, 190, "long_arc")
        assert result == 280.0

    def test_near_zero_crossing(self):
        """Test midpoint near 0 Aries / 30 Pisces boundary."""
        # 350 (20 Pisces) and 10 (10 Aries)
        # Short arc midpoint should be 0 (0 Aries)
        result = calculate_midpoint_longitude(350, 10)
        assert result == 0.0

    def test_near_zero_crossing_long_arc(self):
        """Test long arc near 0 Aries boundary."""
        # 350 and 10: long arc goes the other way around the zodiac
        result = calculate_midpoint_longitude(350, 10, "long_arc")
        # Long arc: 350 -> 180 -> 10 = 180 degrees (0 Libra)
        assert result == 180.0

    def test_invalid_method_raises(self):
        """Test that invalid method raises ValueError."""
        with pytest.raises(ValueError, match="Unknown midpoint method"):
            calculate_midpoint_longitude(10, 20, "invalid")


class TestJulianDayConversion:
    """Tests for Julian day to datetime conversion."""

    def test_known_date_conversion(self):
        """Test conversion of a known Julian day."""
        # J2000.0 epoch: January 1, 2000, 12:00 TT
        # JD = 2451545.0
        result = julian_day_to_datetime(2451545.0)
        assert result.year == 2000
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
        assert result.tzinfo is not None  # Should be timezone-aware

    def test_returns_utc(self):
        """Test that result is in UTC."""
        result = julian_day_to_datetime(2451545.0)
        assert result.tzinfo == pytz.UTC


class TestDatetimeMidpoint:
    """Tests for datetime midpoint calculation."""

    def test_same_day_midpoint(self):
        """Test midpoint of two times on same day."""
        dt1 = ChartDateTime(
            utc_datetime=dt.datetime(2000, 1, 1, 10, 0, tzinfo=pytz.UTC),
            julian_day=2451544.9166666665,  # Approximate
        )
        dt2 = ChartDateTime(
            utc_datetime=dt.datetime(2000, 1, 1, 14, 0, tzinfo=pytz.UTC),
            julian_day=2451545.0833333335,  # Approximate
        )

        mid_dt, mid_jd = calculate_datetime_midpoint(dt1, dt2)

        # Midpoint should be around noon
        assert mid_dt.hour == 12
        assert mid_dt.day == 1
        assert mid_dt.month == 1

    def test_different_days_midpoint(self):
        """Test midpoint of dates several days apart."""
        dt1 = ChartDateTime(
            utc_datetime=dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC),
            julian_day=2451545.0,
        )
        dt2 = ChartDateTime(
            utc_datetime=dt.datetime(2000, 1, 11, 12, 0, tzinfo=pytz.UTC),
            julian_day=2451555.0,  # 10 days later
        )

        mid_dt, mid_jd = calculate_datetime_midpoint(dt1, dt2)

        # Midpoint should be Jan 6
        assert mid_dt.day == 6
        assert mid_dt.month == 1
        # Julian day should be exactly between
        assert mid_jd == 2451550.0


class TestLocationMidpoint:
    """Tests for geographic location midpoint."""

    def test_simple_midpoint(self):
        """Test simple arithmetic mean of coordinates."""
        loc1 = ChartLocation(latitude=40.0, longitude=-120.0, name="Location A")
        loc2 = ChartLocation(latitude=50.0, longitude=-100.0, name="Location B")

        mid = calculate_location_midpoint(loc1, loc2, method="simple")

        assert mid.latitude == 45.0
        assert mid.longitude == -110.0
        assert "Location A" in mid.name
        assert "Location B" in mid.name

    def test_great_circle_midpoint_nearby_points(self):
        """Test great circle midpoint for nearby points (should be similar to simple)."""
        # SF and LA - nearby on same coast
        loc1 = ChartLocation(
            latitude=37.7749, longitude=-122.4194, name="San Francisco"
        )
        loc2 = ChartLocation(latitude=34.0522, longitude=-118.2437, name="Los Angeles")

        mid = calculate_location_midpoint(loc1, loc2, method="great_circle")

        # For nearby points, great circle ≈ simple
        simple_mid = calculate_location_midpoint(loc1, loc2, method="simple")
        assert abs(mid.latitude - simple_mid.latitude) < 0.1
        assert abs(mid.longitude - simple_mid.longitude) < 0.1

    def test_great_circle_midpoint_distant_points(self):
        """Test great circle midpoint for distant points (JFK to Singapore)."""
        # This is a classic geodesic test case
        loc1 = ChartLocation(latitude=40.640, longitude=-73.779, name="JFK Airport")
        loc2 = ChartLocation(latitude=1.359, longitude=103.989, name="Singapore")

        mid = calculate_location_midpoint(loc1, loc2, method="great_circle")

        # The great circle path goes over the Arctic!
        # Midpoint should be roughly in northern latitudes, not in the Indian Ocean
        # Expected: approximately (67.5°N, 32°E) - over Russia/Scandinavia region
        assert mid.latitude > 50  # Should be in high northern latitudes

        # Simple method would give ~21°N (middle of Indian Ocean) - wrong!
        simple_mid = calculate_location_midpoint(loc1, loc2, method="simple")
        assert simple_mid.latitude < 25  # Simple gives low latitude (incorrect)

        # Great circle is very different for distant points
        assert abs(mid.latitude - simple_mid.latitude) > 30

    def test_great_circle_is_default(self):
        """Test that great_circle is the default method."""
        loc1 = ChartLocation(latitude=40.0, longitude=-120.0)
        loc2 = ChartLocation(latitude=50.0, longitude=-100.0)

        # No method specified - should use great_circle
        mid_default = calculate_location_midpoint(loc1, loc2)
        mid_gc = calculate_location_midpoint(loc1, loc2, method="great_circle")

        assert mid_default.latitude == mid_gc.latitude
        assert mid_default.longitude == mid_gc.longitude

    def test_same_location_midpoint(self):
        """Test midpoint of same location is that location."""
        loc = ChartLocation(latitude=37.7749, longitude=-122.4194, name="San Francisco")

        mid = calculate_location_midpoint(loc, loc)

        assert abs(mid.latitude - loc.latitude) < 0.0001
        assert abs(mid.longitude - loc.longitude) < 0.0001

    def test_antipodal_points(self):
        """Test midpoint of antipodal points (opposite sides of Earth)."""
        # North pole area and south pole area (but not exact poles to avoid singularity)
        loc1 = ChartLocation(latitude=80.0, longitude=0.0)
        loc2 = ChartLocation(latitude=-80.0, longitude=180.0)

        mid = calculate_location_midpoint(loc1, loc2, method="great_circle")

        # Midpoint should be on the equator
        assert abs(mid.latitude) < 1.0  # Very close to equator

    def test_invalid_method_raises(self):
        """Test that invalid method raises ValueError."""
        loc = ChartLocation(latitude=0, longitude=0)
        with pytest.raises(ValueError, match="Unknown location midpoint method"):
            calculate_location_midpoint(loc, loc, method="invalid")


# =============================================================================
# SynthesisBuilder Tests
# =============================================================================


class TestSynthesisBuilderAPI:
    """Tests for SynthesisBuilder API surface."""

    @pytest.fixture
    def sample_charts(self):
        """Create two sample charts for testing."""
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47",
            (37.4419, -122.1430),  # Palo Alto
        ).calculate()

        chart2 = ChartBuilder.from_details(
            "2000-06-15 17:00",
            (47.6062, -122.3321),  # Seattle
        ).calculate()

        return chart1, chart2

    def test_davison_classmethod_returns_builder(self, sample_charts):
        """Test that .davison() returns a builder."""
        chart1, chart2 = sample_charts
        builder = SynthesisBuilder.davison(chart1, chart2)
        assert isinstance(builder, SynthesisBuilder)

    def test_composite_classmethod_returns_builder(self, sample_charts):
        """Test that .composite() returns a builder."""
        chart1, chart2 = sample_charts
        builder = SynthesisBuilder.composite(chart1, chart2)
        assert isinstance(builder, SynthesisBuilder)

    def test_fluent_api_chaining(self, sample_charts):
        """Test that configuration methods return self for chaining."""
        chart1, chart2 = sample_charts
        builder = (
            SynthesisBuilder.davison(chart1, chart2)
            .with_location_method("simple")
            .with_labels("Person A", "Person B")
        )
        assert isinstance(builder, SynthesisBuilder)


class TestDavisonChart:
    """Tests for Davison chart calculation."""

    @pytest.fixture
    def sample_charts(self):
        """Create two sample charts for testing."""
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47",
            (37.4419, -122.1430),  # Palo Alto
        ).calculate()

        chart2 = ChartBuilder.from_details(
            "2000-06-15 17:00",
            (47.6062, -122.3321),  # Seattle
        ).calculate()

        return chart1, chart2

    def test_davison_returns_synthesis_chart(self, sample_charts):
        """Test that davison calculation returns SynthesisChart."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert isinstance(davison, SynthesisChart)

    def test_davison_is_calculated_chart(self, sample_charts):
        """Test that SynthesisChart is also a CalculatedChart (inheritance)."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert isinstance(davison, CalculatedChart)

    def test_davison_has_positions(self, sample_charts):
        """Test that davison chart has calculated positions."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert len(davison.positions) > 0
        assert davison.get_object("Sun") is not None
        assert davison.get_object("Moon") is not None

    def test_davison_has_houses(self, sample_charts):
        """Test that davison chart has house calculations."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert len(davison.house_systems) > 0

    def test_davison_aspects_tuple_exists(self, sample_charts):
        """Test that davison chart has aspects attribute (even if empty by default)."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        # By default, ChartBuilder doesn't add aspect engine, so aspects may be empty
        # The key test is that the attribute exists and is the right type
        assert isinstance(davison.aspects, tuple)

    def test_davison_stores_source_charts(self, sample_charts):
        """Test that davison stores references to source charts."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert davison.source_chart1 is chart1
        assert davison.source_chart2 is chart2

    def test_davison_synthesis_method(self, sample_charts):
        """Test that synthesis_method is set correctly."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert davison.synthesis_method == "davison"

    def test_davison_datetime_is_midpoint(self, sample_charts):
        """Test that davison datetime is between source datetimes."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        # The davison datetime should be between the two source datetimes
        jd1 = chart1.datetime.julian_day
        jd2 = chart2.datetime.julian_day
        jd_davison = davison.datetime.julian_day

        assert min(jd1, jd2) < jd_davison < max(jd1, jd2)

    def test_davison_location_is_midpoint(self, sample_charts):
        """Test that davison location is between source locations."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        lat1, lat2 = chart1.location.latitude, chart2.location.latitude
        lon1, lon2 = chart1.location.longitude, chart2.location.longitude

        # Should be approximately between (within floating point tolerance)
        assert min(lat1, lat2) <= davison.location.latitude <= max(lat1, lat2)
        assert min(lon1, lon2) <= davison.location.longitude <= max(lon1, lon2)

    def test_davison_with_labels(self, sample_charts):
        """Test that custom labels are stored."""
        chart1, chart2 = sample_charts
        davison = (
            SynthesisBuilder.davison(chart1, chart2)
            .with_labels("Alice", "Bob")
            .calculate()
        )

        assert davison.chart1_label == "Alice"
        assert davison.chart2_label == "Bob"

    def test_davison_location_method_stored(self, sample_charts):
        """Test that location_method configuration is stored."""
        chart1, chart2 = sample_charts
        davison = (
            SynthesisBuilder.davison(chart1, chart2)
            .with_location_method("simple")
            .calculate()
        )

        assert davison.location_method == "simple"

    def test_davison_default_location_method_is_great_circle(self, sample_charts):
        """Test that the default location method is great_circle."""
        chart1, chart2 = sample_charts
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        assert davison.location_method == "great_circle"


class TestSynthesisChartMethods:
    """Tests for SynthesisChart method inheritance."""

    @pytest.fixture
    def davison_chart(self):
        """Create a davison chart for testing."""
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47", (37.4419, -122.1430)
        ).calculate()

        chart2 = ChartBuilder.from_details(
            "2000-06-15 17:00", (47.6062, -122.3321)
        ).calculate()

        return SynthesisBuilder.davison(chart1, chart2).calculate()

    def test_get_object_works(self, davison_chart):
        """Test that inherited get_object method works."""
        sun = davison_chart.get_object("Sun")
        assert sun is not None
        assert sun.name == "Sun"

    def test_get_planets_works(self, davison_chart):
        """Test that inherited get_planets method works."""
        planets = davison_chart.get_planets()
        assert len(planets) > 0
        planet_names = [p.name for p in planets]
        assert "Sun" in planet_names
        assert "Moon" in planet_names

    def test_get_houses_works(self, davison_chart):
        """Test that inherited get_houses method works."""
        houses = davison_chart.get_houses()
        assert houses is not None
        assert len(houses.cusps) == 12

    def test_to_dict_includes_synthesis_data(self, davison_chart):
        """Test that to_dict includes synthesis-specific data."""
        data = davison_chart.to_dict()

        assert "synthesis" in data
        assert data["synthesis"]["method"] == "davison"
        assert "chart1_label" in data["synthesis"]
        assert "chart2_label" in data["synthesis"]


class TestCompositeChart:
    """Tests for composite chart calculation."""

    @pytest.fixture
    def sample_charts(self):
        """Create two sample charts for testing."""
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47",
            (37.4419, -122.1430),  # Palo Alto
        ).calculate()

        chart2 = ChartBuilder.from_details(
            "2000-06-15 17:00",
            (47.6062, -122.3321),  # Seattle
        ).calculate()

        return chart1, chart2

    def test_composite_returns_synthesis_chart(self, sample_charts):
        """Test that composite calculation returns SynthesisChart."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert isinstance(composite, SynthesisChart)

    def test_composite_is_calculated_chart(self, sample_charts):
        """Test that SynthesisChart is also a CalculatedChart (inheritance)."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert isinstance(composite, CalculatedChart)

    def test_composite_has_positions(self, sample_charts):
        """Test that composite chart has calculated positions."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert len(composite.positions) > 0
        assert composite.get_object("Sun") is not None
        assert composite.get_object("Moon") is not None

    def test_composite_sun_is_midpoint(self, sample_charts):
        """Test that composite Sun is the midpoint of both Suns."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        sun1 = chart1.get_object("Sun")
        sun2 = chart2.get_object("Sun")
        comp_sun = composite.get_object("Sun")

        # Calculate expected midpoint
        expected = calculate_midpoint_longitude(sun1.longitude, sun2.longitude)

        assert abs(comp_sun.longitude - expected) < 0.0001

    def test_composite_stores_source_charts(self, sample_charts):
        """Test that composite stores references to source charts."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert composite.source_chart1 is chart1
        assert composite.source_chart2 is chart2

    def test_composite_synthesis_method(self, sample_charts):
        """Test that synthesis_method is set correctly."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert composite.synthesis_method == "composite"

    def test_composite_has_aspects(self, sample_charts):
        """Test that composite chart has aspects calculated."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        # Composite should have aspects between composite positions
        assert len(composite.aspects) > 0

    def test_composite_default_has_houses(self, sample_charts):
        """Test that composite chart has houses by default (derived method)."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert len(composite.house_systems) > 0
        assert composite.houses_config is True

    def test_composite_with_houses_false(self, sample_charts):
        """Test composite chart with no houses."""
        chart1, chart2 = sample_charts
        composite = (
            SynthesisBuilder.composite(chart1, chart2).with_houses(False).calculate()
        )

        assert len(composite.house_systems) == 0
        assert composite.houses_config is False

    def test_composite_with_houses_place(self, sample_charts):
        """Test composite chart with reference place method."""
        chart1, chart2 = sample_charts
        composite = (
            SynthesisBuilder.composite(chart1, chart2).with_houses("place").calculate()
        )

        assert len(composite.house_systems) > 0
        assert composite.houses_config == "place"

    def test_composite_with_labels(self, sample_charts):
        """Test that custom labels are stored."""
        chart1, chart2 = sample_charts
        composite = (
            SynthesisBuilder.composite(chart1, chart2)
            .with_labels("Alice", "Bob")
            .calculate()
        )

        assert composite.chart1_label == "Alice"
        assert composite.chart2_label == "Bob"

    def test_composite_midpoint_method_stored(self, sample_charts):
        """Test that midpoint_method configuration is stored."""
        chart1, chart2 = sample_charts
        composite = (
            SynthesisBuilder.composite(chart1, chart2)
            .with_midpoint_method("long_arc")
            .calculate()
        )

        assert composite.midpoint_method == "long_arc"

    def test_composite_default_midpoint_is_short_arc(self, sample_charts):
        """Test that the default midpoint method is short_arc."""
        chart1, chart2 = sample_charts
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        assert composite.midpoint_method == "short_arc"
