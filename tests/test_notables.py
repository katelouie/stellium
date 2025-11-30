"""
Tests for the Notable system (Notable class and NotableRegistry).

OPTIMIZED VERSION - uses dicts with timezone to avoid slow TimezoneFinder lookups.
"""

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartDateTime, ChartLocation
from stellium.core.native import Native, Notable
from stellium.data import NotableRegistry, get_notable_registry


# Test fixtures with timezone data (fast!)
@pytest.fixture
def test_location_nyc():
    """New York location with timezone - no lookup needed."""
    return {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "name": "New York, USA",
    }


@pytest.fixture
def test_location_null():
    """Null island location with timezone."""
    return {"latitude": 0.0, "longitude": 0.0, "timezone": "UTC", "name": "Null Island"}


@pytest.fixture
def sample_notable(test_location_nyc):
    """Create a sample Notable for testing."""
    return Notable(
        name="Test Person",
        event_type="birth",
        year=1990,
        month=6,
        day=15,
        hour=12,
        minute=30,
        location_input=test_location_nyc,  # ✅ Fast!
        category="test",
        subcategories=["example"],
        notable_for="Testing purposes",
        data_quality="C",
        verified=False,
    )


@pytest.fixture
def registry():
    """Get the NotableRegistry instance."""
    return get_notable_registry()


class TestNotableClass:
    """Test the Notable class directly."""

    def test_notable_creation_with_dict_location(self, test_location_nyc):
        """Test creating a Notable with location dict (fast!)."""
        notable = Notable(
            name="Test Person",
            event_type="birth",
            year=1990,
            month=6,
            day=15,
            hour=12,
            minute=30,
            location_input=test_location_nyc,
            category="test",
        )

        assert notable.name == "Test Person"
        assert notable.event_type == "birth"
        assert notable.category == "test"
        assert notable.is_birth is True
        assert notable.is_event is False

        # Check inherited Native attributes
        assert isinstance(notable.datetime, ChartDateTime)
        assert isinstance(notable.location, ChartLocation)
        assert notable.location.latitude == 40.7128
        assert notable.location.longitude == -74.0060
        assert notable.location.timezone == "America/New_York"

    def test_notable_inherits_from_native(self, test_location_null):
        """Test that Notable is an instance of Native."""
        notable = Notable(
            name="Test",
            event_type="birth",
            year=2000,
            month=1,
            day=1,
            hour=0,
            minute=0,
            location_input=test_location_null,
            category="test",
        )

        assert isinstance(notable, Native)
        assert isinstance(notable, Notable)

    def test_notable_datetime_conversion(self):
        """Test that Notable properly converts local time to UTC."""
        # Create notable with known timezone
        notable = Notable(
            name="Einstein",
            event_type="birth",
            year=1879,
            month=3,
            day=14,
            hour=11,
            minute=30,
            location_input={
                "latitude": 48.3984,
                "longitude": 9.9916,
                "timezone": "Europe/Berlin",
                "name": "Ulm, Germany",
            },
            category="scientist",
        )

        # Check that datetime was created
        assert notable.datetime is not None
        assert notable.datetime.utc_datetime is not None
        assert notable.datetime.local_datetime is not None

        # Local time should be 11:30
        local = notable.datetime.local_datetime
        assert local.hour == 11
        assert local.minute == 30

    def test_notable_metadata_fields(self, test_location_null):
        """Test all metadata fields are stored correctly."""
        notable = Notable(
            name="Test Person",
            event_type="birth",
            year=1990,
            month=1,
            day=1,
            hour=0,
            minute=0,
            location_input=test_location_null,
            category="scientist",
            subcategories=["physicist", "theorist"],
            notable_for="Test achievements",
            astrological_notes="Test notes",
            data_quality="AA",
            sources=["Test Source"],
            verified=True,
        )

        assert notable.name == "Test Person"
        assert notable.category == "scientist"
        assert notable.subcategories == ["physicist", "theorist"]
        assert notable.notable_for == "Test achievements"
        assert notable.astrological_notes == "Test notes"
        assert notable.data_quality == "AA"
        assert notable.sources == ["Test Source"]
        assert notable.verified is True

    def test_notable_default_values(self, test_location_null):
        """Test that optional fields have correct defaults."""
        notable = Notable(
            name="Test",
            event_type="birth",
            year=2000,
            month=1,
            day=1,
            hour=0,
            minute=0,
            location_input=test_location_null,
            category="test",
        )

        assert notable.subcategories == []
        assert notable.notable_for == ""
        assert notable.astrological_notes == ""
        assert notable.data_quality == "C"
        assert notable.sources == []
        assert notable.verified is False

    def test_notable_is_birth_property(self, test_location_null):
        """Test is_birth property."""
        birth = Notable(
            name="Birth Test",
            event_type="birth",
            year=2000,
            month=1,
            day=1,
            hour=0,
            minute=0,
            location_input=test_location_null,
            category="test",
        )
        assert birth.is_birth is True
        assert birth.is_event is False

    def test_notable_is_event_property(self, test_location_null):
        """Test is_event property."""
        event = Notable(
            name="Event Test",
            event_type="event",
            year=2000,
            month=1,
            day=1,
            hour=0,
            minute=0,
            location_input=test_location_null,
            category="eclipse",
        )
        assert event.is_event is True
        assert event.is_birth is False

    def test_notable_repr(self, test_location_null):
        """Test string representation."""
        notable = Notable(
            name="Test Person",
            event_type="birth",
            year=2000,
            month=1,
            day=1,
            hour=0,
            minute=0,
            location_input=test_location_null,
            category="scientist",
        )
        assert repr(notable) == "<Notable: Test Person (scientist)>"


class TestNotableRegistry:
    """Test the NotableRegistry class."""

    def test_registry_singleton(self):
        """Test that get_notable_registry returns singleton."""
        registry1 = get_notable_registry()
        registry2 = get_notable_registry()
        assert registry1 is registry2

    def test_registry_loads_data(self):
        """Test that registry loads YAML data."""
        registry = get_notable_registry()
        assert len(registry) > 0
        assert isinstance(registry, NotableRegistry)

    def test_registry_contains_notables(self):
        """Test that loaded data are Notable objects."""
        registry = get_notable_registry()
        all_notables = registry.get_all()

        assert len(all_notables) > 0
        for notable in all_notables:
            assert isinstance(notable, Notable)
            assert isinstance(notable, Native)

    def test_get_by_name_exact_match(self):
        """Test getting notable by exact name."""
        registry = get_notable_registry()
        einstein = registry.get_by_name("Albert Einstein")

        assert einstein is not None
        assert einstein.name == "Albert Einstein"
        assert einstein.category == "scientist"
        assert isinstance(einstein, Notable)

    def test_get_by_name_case_insensitive(self):
        """Test case-insensitive name lookup."""
        registry = get_notable_registry()

        einstein1 = registry.get_by_name("Albert Einstein")
        einstein2 = registry.get_by_name("albert einstein")
        einstein3 = registry.get_by_name("ALBERT EINSTEIN")

        assert einstein1 is not None
        assert einstein2 is not None
        assert einstein3 is not None
        assert einstein1.name == einstein2.name == einstein3.name

    def test_get_by_name_not_found(self):
        """Test that non-existent names return None."""
        registry = get_notable_registry()
        result = registry.get_by_name("Nonexistent Person")
        assert result is None

    def test_get_by_category(self):
        """Test getting notables by category."""
        registry = get_notable_registry()
        scientists = registry.get_by_category("scientist")

        assert len(scientists) > 0
        for scientist in scientists:
            assert scientist.category == "scientist"
            assert isinstance(scientist, Notable)

    def test_get_by_category_empty(self):
        """Test getting notables from non-existent category."""
        registry = get_notable_registry()
        results = registry.get_by_category("nonexistent_category")
        assert results == []

    def test_get_births(self):
        """Test getting all birth records."""
        registry = get_notable_registry()
        births = registry.get_births()

        assert len(births) > 0
        for birth in births:
            assert birth.event_type == "birth"
            assert birth.is_birth is True

    def test_get_events(self):
        """Test getting all event records."""
        registry = get_notable_registry()
        events = registry.get_events()

        # May be empty if no events in test data
        for event in events:
            assert event.event_type == "event"
            assert event.is_event is True

    def test_get_by_event_type(self):
        """Test getting by event type."""
        registry = get_notable_registry()
        births = registry.get_by_event_type("birth")

        assert len(births) > 0
        for birth in births:
            assert birth.event_type == "birth"

    def test_search_single_filter(self):
        """Test search with single filter."""
        registry = get_notable_registry()
        results = registry.search(category="scientist")

        assert len(results) > 0
        for result in results:
            assert result.category == "scientist"

    def test_search_multiple_filters(self):
        """Test search with multiple filters."""
        registry = get_notable_registry()
        results = registry.search(category="scientist", verified=False)

        for result in results:
            assert result.category == "scientist"
            assert result.verified is False

    def test_search_no_matches(self):
        """Test search with no matches."""
        registry = get_notable_registry()
        results = registry.search(
            category="nonexistent", verified=True, data_quality="AAA"
        )
        assert results == []

    def test_get_all(self):
        """Test getting all notables."""
        registry = get_notable_registry()
        all_notables = registry.get_all()

        assert len(all_notables) > 0
        assert isinstance(all_notables, list)

        # Ensure it's a copy (not the internal list)
        original_len = len(all_notables)
        all_notables.append(None)
        all_notables2 = registry.get_all()
        assert len(all_notables2) == original_len

    def test_registry_len(self):
        """Test __len__ method."""
        registry = get_notable_registry()
        length = len(registry)
        all_notables = registry.get_all()
        assert length == len(all_notables)

    def test_registry_repr(self):
        """Test __repr__ method."""
        registry = get_notable_registry()
        repr_str = repr(registry)

        assert "NotableRegistry" in repr_str
        assert "births" in repr_str
        assert "events" in repr_str


class TestNotableRegistryData:
    """Test specific notable data from YAML files."""

    def test_einstein_data(self):
        """Test Albert Einstein's data."""
        registry = get_notable_registry()
        einstein = registry.get_by_name("Albert Einstein")

        assert einstein is not None
        assert einstein.name == "Albert Einstein"
        assert einstein.category == "scientist"
        assert "physicist" in einstein.subcategories
        assert einstein.event_type == "birth"
        assert (
            "Relativity" in einstein.notable_for
            or "relativity" in einstein.notable_for.lower()
        )

    def test_curie_data(self):
        """Test Marie Curie's data."""
        registry = get_notable_registry()
        curie = registry.get_by_name("Marie Curie")

        assert curie is not None
        assert curie.category == "scientist"
        assert "physicist" in curie.subcategories or "chemist" in curie.subcategories

    def test_all_notables_have_required_fields(self):
        """Test that all notables have required fields."""
        registry = get_notable_registry()
        all_notables = registry.get_all()

        for notable in all_notables:
            # Required fields
            assert notable.name
            assert notable.event_type in ["birth", "event"]
            assert notable.category
            assert notable.datetime is not None
            assert notable.location is not None

            # Datetime components
            assert notable.datetime.utc_datetime is not None
            assert notable.datetime.julian_day > 0

            # Location components
            assert -90 <= notable.location.latitude <= 90
            assert -180 <= notable.location.longitude <= 180


class TestChartBuilderIntegration:
    """Test ChartBuilder integration with Notable."""

    def test_from_native_with_notable(self):
        """Test that from_native works with Notable objects."""
        registry = get_notable_registry()
        einstein = registry.get_by_name("Albert Einstein")

        # Notable IS-A Native, so from_native should work
        builder = ChartBuilder.from_native(einstein)
        assert builder is not None
        assert isinstance(builder, ChartBuilder)

        chart = builder.calculate()
        assert chart is not None

    def test_from_notable_success(self):
        """Test ChartBuilder.from_notable() success case."""
        chart = ChartBuilder.from_notable("Albert Einstein").calculate()

        assert chart is not None
        assert chart.location is not None
        assert chart.datetime is not None
        assert len(chart.positions) > 0

    def test_from_notable_case_insensitive(self):
        """Test from_notable with different cases."""
        chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
        chart2 = ChartBuilder.from_notable("albert einstein").calculate()
        chart3 = ChartBuilder.from_notable("MARIE CURIE").calculate()

        assert chart1 is not None
        assert chart2 is not None
        assert chart3 is not None

    def test_from_notable_not_found(self):
        """Test from_notable with non-existent name."""
        with pytest.raises(ValueError) as exc_info:
            ChartBuilder.from_notable("Nonexistent Person").calculate()

        assert "No notable found" in str(exc_info.value)
        assert "Nonexistent Person" in str(exc_info.value)

    def test_from_notable_chart_has_correct_data(self):
        """Test that chart built from notable has correct data."""
        registry = get_notable_registry()
        einstein = registry.get_by_name("Albert Einstein")

        chart = ChartBuilder.from_notable("Albert Einstein").calculate()

        # Chart should have same location/datetime as notable
        assert chart.location.latitude == einstein.location.latitude
        assert chart.location.longitude == einstein.location.longitude
        assert chart.datetime.utc_datetime == einstein.datetime.utc_datetime

    def test_notable_chart_has_planets(self):
        """Test that chart from notable calculates planets."""
        chart = ChartBuilder.from_notable("Albert Einstein").calculate()

        # Should have basic planets
        sun = chart.get_object("Sun")
        moon = chart.get_object("Moon")

        assert sun is not None
        assert moon is not None
        assert sun.sign is not None
        assert moon.sign is not None

    def test_multiple_notables_charts(self):
        """Test creating charts for multiple notables."""
        names = ["Albert Einstein", "Marie Curie", "Nikola Tesla"]
        charts = []

        for name in names:
            chart = ChartBuilder.from_notable(name).calculate()
            charts.append(chart)

        assert len(charts) == 3
        for chart in charts:
            assert chart is not None
            assert len(chart.positions) > 0


class TestNotableWithChartLocation:
    """Test Notable with ChartLocation objects (from YAML with lat/long)."""

    def test_notable_from_yaml_with_coordinates(self):
        """Test that YAML entries with lat/long create proper ChartLocations."""
        registry = get_notable_registry()
        einstein = registry.get_by_name("Albert Einstein")

        # Should have ChartLocation with coordinates
        assert isinstance(einstein.location, ChartLocation)
        assert einstein.location.latitude == pytest.approx(48.3984, rel=1e-3)
        assert einstein.location.longitude == pytest.approx(9.9916, rel=1e-3)
        assert einstein.location.timezone  # Should have timezone


class TestErrorHandling:
    """Test error handling in Notable system."""

    def test_notable_with_invalid_date(self, test_location_null):
        """Test Notable creation with invalid date raises error."""
        with pytest.raises(ValueError):
            Notable(
                name="Test",
                event_type="birth",
                year=2000,
                month=13,  # Invalid month
                day=1,
                hour=0,
                minute=0,
                location_input=test_location_null,
                category="test",
            )

    def test_notable_with_invalid_location(self):
        """Test Notable with invalid location coordinates."""
        with pytest.raises(ValueError):
            Notable(
                name="Test",
                event_type="birth",
                year=2000,
                month=1,
                day=1,
                hour=0,
                minute=0,
                location_input={
                    "latitude": 100.0,  # Invalid latitude
                    "longitude": 0.0,
                    "timezone": "UTC",
                    "name": "Invalid",
                },
                category="test",
            )
