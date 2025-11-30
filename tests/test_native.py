"""Tests for Native class, including datetime string parsing."""

from datetime import datetime

import pytest

from stellium.core.native import Native


class TestNativeDatetimeStringParsing:
    """Test Native's ability to parse datetime strings in various formats."""

    def test_iso_format_with_space(self):
        """Test ISO 8601 format with space separator."""
        native = Native("2024-11-24 14:30", "Palo Alto, CA")

        assert native.datetime.local_datetime.year == 2024
        assert native.datetime.local_datetime.month == 11
        assert native.datetime.local_datetime.day == 24
        assert native.datetime.local_datetime.hour == 14
        assert native.datetime.local_datetime.minute == 30

    def test_iso_format_with_t_separator(self):
        """Test ISO 8601 format with T separator."""
        native = Native("2024-11-24T14:30:00", "Seattle, WA")

        assert native.datetime.local_datetime.year == 2024
        assert native.datetime.local_datetime.month == 11
        assert native.datetime.local_datetime.day == 24
        assert native.datetime.local_datetime.hour == 14
        assert native.datetime.local_datetime.minute == 30

    def test_us_format_24hr(self):
        """Test US date format with 24-hour time."""
        native = Native("11/24/2024 14:30", "New York, NY")

        assert native.datetime.local_datetime.year == 2024
        assert native.datetime.local_datetime.month == 11
        assert native.datetime.local_datetime.day == 24
        assert native.datetime.local_datetime.hour == 14
        assert native.datetime.local_datetime.minute == 30

    def test_us_format_12hr_am_pm(self):
        """Test US date format with 12-hour AM/PM time."""
        native = Native("01/06/1994 11:47 AM", "Palo Alto, CA")

        assert native.datetime.local_datetime.year == 1994
        assert native.datetime.local_datetime.month == 1
        assert native.datetime.local_datetime.day == 6
        assert native.datetime.local_datetime.hour == 11
        assert native.datetime.local_datetime.minute == 47

    def test_date_only_assumes_midnight(self):
        """Test date-only string defaults to midnight."""
        native = Native("2024-11-24", "Palo Alto, CA")

        assert native.datetime.local_datetime.year == 2024
        assert native.datetime.local_datetime.month == 11
        assert native.datetime.local_datetime.day == 24
        assert native.datetime.local_datetime.hour == 0
        assert native.datetime.local_datetime.minute == 0

    def test_invalid_format_raises_helpful_error(self):
        """Test that invalid format raises ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            Native("not a valid date", "Palo Alto, CA")

        error_message = str(exc_info.value)
        assert "Could not parse datetime string" in error_message
        assert "Supported formats:" in error_message
        assert "ISO 8601" in error_message
        assert "US format" in error_message

    def test_string_parsing_with_tuple_location(self):
        """Test string parsing works with tuple coordinates."""
        native = Native("2024-11-24 14:30", (37.4419, -122.1430))

        assert native.datetime.local_datetime.year == 2024
        assert native.location.latitude == 37.4419
        assert native.location.longitude == -122.1430


class TestNativeTimezoneHandling:
    """Test Native's timezone handling with string parsing."""

    def test_string_datetime_localizes_to_location_timezone(self):
        """Test that naive datetime string is localized to location's timezone."""
        # Palo Alto is in America/Los_Angeles (PST/PDT)
        native = Native("2024-11-24 14:30", "Palo Alto, CA")

        # Check that location has correct timezone
        assert "America/Los_Angeles" in native.location.timezone

        # Check that datetime was localized (should have UTC datetime)
        assert native.datetime.utc_datetime is not None

        # Local time should be what we specified
        assert native.datetime.local_datetime.hour == 14
        assert native.datetime.local_datetime.minute == 30

    def test_different_timezones_produce_different_utc(self):
        """Test that same local time in different timezones produces different UTC."""
        # Same local time in two different timezones
        native_ca = Native("2024-11-24 14:30", "Palo Alto, CA")  # PST
        native_ny = Native("2024-11-24 14:30", "New York, NY")  # EST

        # Local times are the same
        assert native_ca.datetime.local_datetime.hour == 14
        assert native_ny.datetime.local_datetime.hour == 14

        # But UTC times differ by 3 hours
        utc_diff = abs(
            (
                native_ca.datetime.utc_datetime - native_ny.datetime.utc_datetime
            ).total_seconds()
            / 3600
        )
        assert utc_diff == 3.0


class TestNativeBackwardCompatibility:
    """Test that existing Native API still works."""

    def test_datetime_object_still_works(self):
        """Test that passing datetime object still works."""
        dt = datetime(1994, 1, 6, 11, 47)
        native = Native(dt, "Palo Alto, CA")

        assert native.datetime.local_datetime.year == 1994
        assert native.datetime.local_datetime.month == 1

    def test_dict_input_still_works(self):
        """Test that passing dict input still works."""
        dt_dict = {
            "year": 1994,
            "month": 1,
            "day": 6,
            "hour": 11,
            "minute": 47,
        }
        native = Native(dt_dict, "Palo Alto, CA")

        assert native.datetime.local_datetime.year == 1994
        assert native.datetime.local_datetime.month == 1

    def test_string_location_still_works(self):
        """Test that string location still works."""
        native = Native("2024-11-24 14:30", "Palo Alto, CA")

        assert "Palo Alto" in native.location.name

    def test_tuple_location_still_works(self):
        """Test that tuple location still works."""
        native = Native("2024-11-24 14:30", (37.4419, -122.1430))

        assert native.location.latitude == 37.4419
        assert native.location.longitude == -122.1430
