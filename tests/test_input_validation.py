"""Tests for public API input validation.

Verifies that invalid inputs are caught early with clear error messages
rather than failing deep in the calculation stack.
"""

import pytest

from stellium.core.native import Native


class TestNativeLocationValidation:
    """Validate latitude/longitude bounds on Native construction."""

    def test_valid_tuple_location(self):
        native = Native("2000-01-06 12:00", (47.6, -122.3))
        assert native.location.latitude == pytest.approx(47.6)

    def test_latitude_too_high(self):
        with pytest.raises(ValueError, match="Latitude.*outside valid range"):
            Native("2000-01-06 12:00", (91.0, 0.0))

    def test_latitude_too_low(self):
        with pytest.raises(ValueError, match="Latitude.*outside valid range"):
            Native("2000-01-06 12:00", (-91.0, 0.0))

    def test_longitude_too_high(self):
        with pytest.raises(ValueError, match="Longitude.*outside valid range"):
            Native("2000-01-06 12:00", (0.0, 181.0))

    def test_longitude_too_low(self):
        with pytest.raises(ValueError, match="Longitude.*outside valid range"):
            Native("2000-01-06 12:00", (0.0, -181.0))

    def test_boundary_values_valid(self):
        """Exact boundary values should be accepted."""
        native = Native("2000-01-06 12:00", (90.0, 180.0))
        assert native.location.latitude == 90.0

    def test_dict_location_lat_out_of_range(self):
        with pytest.raises(ValueError, match="Latitude.*outside valid range"):
            Native("2000-01-06 12:00", {"latitude": 999, "longitude": 0})

    def test_dict_location_lon_out_of_range(self):
        with pytest.raises(ValueError, match="Longitude.*outside valid range"):
            Native("2000-01-06 12:00", {"latitude": 0, "longitude": -999})


class TestNativeHistoricalDates:
    """Verify that historical dates work (no artificial year range restriction)."""

    def test_historical_date_accepted(self):
        """Isaac Newton (1643) should work — ephemeris supports it analytically."""
        native = Native("1643-01-04 12:00", (52.8, -0.6))
        assert native.datetime.utc_datetime.year == 1643

    def test_modern_date_accepted(self):
        native = Native("2400-01-06 12:00", (47.6, -122.3))
        assert native.datetime.utc_datetime.year == 2400


class TestElectionalSearchValidation:
    """Validate ElectionalSearch date range."""

    def test_start_after_end(self):
        from stellium.electional import ElectionalSearch

        with pytest.raises(ValueError, match="must be before end date"):
            ElectionalSearch("2025-06-01", "2025-01-01", "Seattle, WA")

    def test_start_equals_end(self):
        from stellium.electional import ElectionalSearch

        with pytest.raises(ValueError, match="must be before end date"):
            ElectionalSearch("2025-06-01", "2025-06-01", "Seattle, WA")

    def test_valid_range(self):
        from stellium.electional import ElectionalSearch

        search = ElectionalSearch("2025-01-01", "2025-06-01", "Seattle, WA")
        assert search.start < search.end


class TestReturnBuilderValidation:
    """Validate ReturnBuilder factory methods."""

    @pytest.fixture
    def natal(self):
        from stellium import ChartBuilder

        return ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()

    def test_solar_year_before_birth(self, natal):
        from stellium.returns.builder import ReturnBuilder

        with pytest.raises(ValueError, match="before the natal birth year"):
            ReturnBuilder.solar(natal, 1990)

    def test_solar_year_not_int(self, natal):
        from stellium.returns.builder import ReturnBuilder

        with pytest.raises(TypeError, match="year must be an integer"):
            ReturnBuilder.solar(natal, 2025.5)

    def test_lunar_occurrence_zero(self, natal):
        from stellium.returns.builder import ReturnBuilder

        with pytest.raises(ValueError, match="positive integer"):
            ReturnBuilder.lunar(natal, occurrence=0)

    def test_lunar_occurrence_negative(self, natal):
        from stellium.returns.builder import ReturnBuilder

        with pytest.raises(ValueError, match="positive integer"):
            ReturnBuilder.lunar(natal, occurrence=-5)

    def test_planetary_empty_planet(self, natal):
        from stellium.returns.builder import ReturnBuilder

        with pytest.raises(TypeError, match="non-empty string"):
            ReturnBuilder.planetary(natal, "", near_date="2025-01-01")

    def test_planetary_occurrence_zero(self, natal):
        from stellium.returns.builder import ReturnBuilder

        with pytest.raises(ValueError, match="positive integer"):
            ReturnBuilder.planetary(natal, "Saturn", occurrence=0)
