import datetime as dt

import pytest
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.core.native import Native
from stellium.engines.ephemeris import MockEphemerisEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses


def test_basic_chart_building():
    """Test basic chart construction."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="SF")
    native = Native(datetime, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_ephemeris(MockEphemerisEngine())
        .calculate()
    )

    assert chart.datetime.utc_datetime == datetime
    assert chart.location.name == "SF"
    assert len(chart.positions) > 0


def test_house_system_swapping():
    """Test that we can easily swap house systems."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(datetime, location)

    # Placidus
    chart1 = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses()])
        .calculate()
    )

    # Placidus
    chart2 = (
        ChartBuilder.from_native(native)
        .with_house_systems([WholeSignHouses()])
        .calculate()
    )

    assert "Placidus" in chart1.house_systems
    assert "Whole Sign" in chart2.house_systems
    # Cusps should be different
    assert (
        chart1.house_systems["Placidus"].cusps
        != chart2.house_systems["Whole Sign"].cusps
    )


class TestChartBuilderFromDetails:
    """Test ChartBuilder.from_details() convenience method."""

    def test_from_details_with_string_inputs(self):
        """Test from_details with string datetime and string location."""
        chart = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()

        assert chart.datetime.local_datetime.year == 1994
        assert chart.datetime.local_datetime.month == 1
        assert chart.datetime.local_datetime.day == 6
        assert "Palo Alto" in chart.location.name

    def test_from_details_with_us_format(self):
        """Test from_details with US date format."""
        chart = ChartBuilder.from_details(
            "01/06/1994 11:47", "Palo Alto, CA"
        ).calculate()

        assert chart.datetime.local_datetime.year == 1994
        assert chart.datetime.local_datetime.month == 1

    def test_from_details_with_tuple_coordinates(self):
        """Test from_details with (lat, lon) tuple."""
        chart = ChartBuilder.from_details(
            "2024-11-24 14:30", (37.4419, -122.1430)
        ).calculate()

        assert chart.location.latitude == 37.4419
        assert chart.location.longitude == -122.1430

    def test_from_details_with_datetime_object(self):
        """Test from_details with datetime object (backward compatibility)."""
        dt_obj = dt.datetime(1994, 1, 6, 11, 47)
        chart = ChartBuilder.from_details(dt_obj, "Palo Alto, CA").calculate()

        assert chart.datetime.local_datetime.year == 1994

    def test_from_details_stores_native_reference(self):
        """Test that from_details creates and stores Native internally."""
        builder = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")

        assert builder.native is not None
        assert isinstance(builder.native, Native)
        assert builder.native.datetime.local_datetime.year == 1994

    def test_from_details_chainable_with_aspects(self):
        """Test that from_details can chain with other builder methods."""
        chart = (
            ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
            .with_aspects()
            .calculate()
        )

        assert len(chart.aspects) > 0

    def test_from_details_vs_from_native_equivalent(self):
        """Test that from_details produces equivalent chart to from_native."""
        # Using from_details
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()

        # Using from_native (old way)
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart2 = ChartBuilder.from_native(native).calculate()

        # Should produce same results
        assert chart1.datetime.local_datetime == chart2.datetime.local_datetime
        assert chart1.location.latitude == chart2.location.latitude
        assert chart1.location.longitude == chart2.location.longitude


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
