"""
Tests for stellium.io.aaf module - AAF file parsing.
"""

import tempfile
from pathlib import Path

import pytest

from stellium.io.aaf import (
    _parse_a93_line,
    _parse_b93_line,
    _parse_coordinate,
    _parse_timezone_offset,
    parse_aaf,
)

# =============================================================================
# Test coordinate parsing
# =============================================================================


class TestParseCoordinate:
    """Tests for _parse_coordinate function."""

    def test_north_latitude(self):
        """Parse northern latitude."""
        assert _parse_coordinate("37n23") == pytest.approx(37.383333, rel=1e-4)

    def test_south_latitude(self):
        """Parse southern latitude - should be negative."""
        assert _parse_coordinate("33s52") == pytest.approx(-33.866667, rel=1e-4)

    def test_east_longitude(self):
        """Parse eastern longitude."""
        assert _parse_coordinate("151e12") == pytest.approx(151.2, rel=1e-4)

    def test_west_longitude(self):
        """Parse western longitude - should be negative."""
        assert _parse_coordinate("122w05") == pytest.approx(-122.083333, rel=1e-4)

    def test_zero_minutes(self):
        """Parse coordinate with zero minutes."""
        assert _parse_coordinate("45n00") == pytest.approx(45.0, rel=1e-4)

    def test_uppercase_direction(self):
        """Parse coordinate with uppercase direction letter."""
        assert _parse_coordinate("37N23") == pytest.approx(37.383333, rel=1e-4)
        assert _parse_coordinate("122W05") == pytest.approx(-122.083333, rel=1e-4)

    def test_single_digit_degrees(self):
        """Parse coordinate with single-digit degrees."""
        assert _parse_coordinate("5e30") == pytest.approx(5.5, rel=1e-4)

    def test_invalid_format_raises(self):
        """Invalid coordinate format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinate format"):
            _parse_coordinate("invalid")

    def test_missing_direction_raises(self):
        """Missing direction letter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinate format"):
            _parse_coordinate("3723")


# =============================================================================
# Test timezone parsing
# =============================================================================


class TestParseTimezoneOffset:
    """Tests for _parse_timezone_offset function."""

    def test_west_timezone(self):
        """Parse western timezone (negative offset)."""
        assert _parse_timezone_offset("8hw00") == pytest.approx(-8.0, rel=1e-4)

    def test_east_timezone(self):
        """Parse eastern timezone (positive offset)."""
        assert _parse_timezone_offset("2he00") == pytest.approx(2.0, rel=1e-4)

    def test_timezone_with_minutes(self):
        """Parse timezone with fractional hours."""
        assert _parse_timezone_offset("5he30") == pytest.approx(5.5, rel=1e-4)
        assert _parse_timezone_offset("9hw30") == pytest.approx(-9.5, rel=1e-4)

    def test_uppercase_direction(self):
        """Parse timezone with uppercase direction."""
        assert _parse_timezone_offset("8hW00") == pytest.approx(-8.0, rel=1e-4)
        assert _parse_timezone_offset("2hE00") == pytest.approx(2.0, rel=1e-4)

    def test_invalid_format_raises(self):
        """Invalid timezone format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timezone format"):
            _parse_timezone_offset("invalid")

    def test_missing_direction_raises(self):
        """Missing direction letter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timezone format"):
            _parse_timezone_offset("8h00")


# =============================================================================
# Test A93 line parsing
# =============================================================================


class TestParseA93Line:
    """Tests for _parse_a93_line function."""

    def test_standard_format(self):
        """Parse standard A93 line."""
        line = "Louie,Kate,f,6.1.1994,11:47,Mountain View (Santa Clara County),CA (US)"
        result = _parse_a93_line(line)

        assert result["name"] == "Kate Louie"
        assert result["year"] == 1994
        assert result["month"] == 1
        assert result["day"] == 6
        assert result["hour"] == 11
        assert result["minute"] == 47
        assert result["second"] == 0
        assert "Mountain View" in result["location_str"]

    def test_with_seconds(self):
        """Parse A93 line with seconds in time."""
        line = "Einstein,Albert,m,14.3.1879,11:30:15,Ulm,Germany"
        result = _parse_a93_line(line)

        assert result["name"] == "Albert Einstein"
        assert result["hour"] == 11
        assert result["minute"] == 30
        assert result["second"] == 15

    def test_single_digit_date_components(self):
        """Parse date with single-digit day/month."""
        line = "Test,Person,m,1.2.2000,9:05,City,Country"
        result = _parse_a93_line(line)

        assert result["day"] == 1
        assert result["month"] == 2
        assert result["hour"] == 9
        assert result["minute"] == 5

    def test_wildcard_last_name(self):
        """Parse A93 line with wildcard (*) last name."""
        line = "*,SingleName,f,15.6.1990,14:30,Paris,France"
        result = _parse_a93_line(line)

        assert result["name"] == "SingleName"

    def test_empty_first_name(self):
        """Parse A93 line with empty first name."""
        line = "OnlyLast,,m,1.1.2000,12:00,London,UK"
        result = _parse_a93_line(line)

        assert result["name"] == "OnlyLast"

    def test_location_with_commas(self):
        """Parse location that contains commas."""
        line = "Test,User,f,1.1.2000,12:00,New York,NY,USA"
        result = _parse_a93_line(line)

        assert "New York" in result["location_str"]
        assert "NY" in result["location_str"]
        assert "USA" in result["location_str"]

    def test_too_few_parts_raises(self):
        """A93 line with too few parts raises ValueError."""
        with pytest.raises(ValueError, match="expected 7\\+ parts"):
            _parse_a93_line("Only,Four,Parts,Here")

    def test_invalid_date_raises(self):
        """Invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            _parse_a93_line("Last,First,m,invalid-date,12:00,City,Country")

    def test_invalid_time_raises(self):
        """Invalid time format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time format"):
            _parse_a93_line("Last,First,m,1.1.2000,invalid,City,Country")


# =============================================================================
# Test B93 line parsing
# =============================================================================


class TestParseB93Line:
    """Tests for _parse_b93_line function."""

    def test_standard_format(self):
        """Parse standard B93 line."""
        line = "2449359.32431,37n23,122w05,8hw00,0"
        result = _parse_b93_line(line)

        assert result["julian_day"] == pytest.approx(2449359.32431, rel=1e-6)
        assert result["latitude"] == pytest.approx(37.383333, rel=1e-4)
        assert result["longitude"] == pytest.approx(-122.083333, rel=1e-4)
        assert result["tz_offset"] == pytest.approx(-8.0, rel=1e-4)
        assert result["dst_flag"] == 0

    def test_with_dst(self):
        """Parse B93 line with DST flag set."""
        line = "2449359.32431,37n23,122w05,8hw00,1"
        result = _parse_b93_line(line)

        assert result["dst_flag"] == 1

    def test_east_coordinates(self):
        """Parse B93 line with eastern coordinates."""
        line = "2440000.5,51n30,0e07,0he00,0"
        result = _parse_b93_line(line)

        assert result["latitude"] == pytest.approx(51.5, rel=1e-4)
        assert result["longitude"] == pytest.approx(0.116667, rel=1e-4)
        assert result["tz_offset"] == pytest.approx(0.0, rel=1e-4)

    def test_too_few_parts_raises(self):
        """B93 line with too few parts raises ValueError."""
        with pytest.raises(ValueError, match="expected 5 parts"):
            _parse_b93_line("2440000.5,37n23,122w05,8hw00")


# =============================================================================
# Test full AAF file parsing
# =============================================================================


class TestParseAaf:
    """Tests for parse_aaf function."""

    def test_single_record(self):
        """Parse AAF file with single record."""
        content = """#A93:Louie,Kate,f,6.1.1994,11:47,Mountain View,CA (US)
#B93:2449359.32431,37n23,122w05,8hw00,0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            natives = parse_aaf(f.name)

            assert len(natives) == 1
            assert natives[0].name == "Kate Louie"
            assert natives[0].location.latitude == pytest.approx(37.383333, rel=1e-4)
            assert natives[0].location.longitude == pytest.approx(-122.083333, rel=1e-4)

            # Clean up
            Path(f.name).unlink()

    def test_multiple_records(self):
        """Parse AAF file with multiple records."""
        content = """#A93:Einstein,Albert,m,14.3.1879,11:30,Ulm,Germany
#B93:2407851.97917,48n24,10e00,1he00,0
#A93:Curie,Marie,f,7.11.1867,12:00,Warsaw,Poland
#B93:2403511.00000,52n14,21e01,1he24,0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            natives = parse_aaf(f.name)

            assert len(natives) == 2
            assert natives[0].name == "Albert Einstein"
            assert natives[1].name == "Marie Curie"

            Path(f.name).unlink()

    def test_with_comments(self):
        """Parse AAF file with comment lines."""
        content = """#: This is a comment
#A93:Test,User,f,1.1.2000,12:00,London,UK
#: Another comment
#B93:2451545.00000,51n30,0w07,0he00,0
#: Final comment
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            natives = parse_aaf(f.name)

            assert len(natives) == 1
            assert natives[0].name == "User Test"

            Path(f.name).unlink()

    def test_with_empty_lines(self):
        """Parse AAF file with empty lines between records."""
        # Note: Empty lines are allowed before #A93 and after #B93,
        # but NOT between #A93 and #B93 (only comments allowed there)
        content = """
#A93:Test,User,f,1.1.2000,12:00,London,UK
#B93:2451545.00000,51n30,0w07,0he00,0

#A93:Another,Person,m,1.1.2001,10:00,Paris,France
#B93:2451910.91667,48n52,2e20,1he00,0

"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            natives = parse_aaf(f.name)

            assert len(natives) == 2

            Path(f.name).unlink()

    def test_file_not_found(self):
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="AAF file not found"):
            parse_aaf("/nonexistent/path/file.aaf")

    def test_path_object(self):
        """Accept Path object as input."""
        content = """#A93:Test,User,f,1.1.2000,12:00,London,UK
#B93:2451545.00000,51n30,0w07,0he00,0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            # Pass Path object instead of string
            natives = parse_aaf(Path(f.name))

            assert len(natives) == 1

            Path(f.name).unlink()

    def test_native_datetime_values(self):
        """Verify Native datetime values are correct."""
        content = """#A93:Test,User,f,15.6.1990,14:30,New York,NY (US)
#B93:2448088.10417,40n43,74w00,5hw00,0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            natives = parse_aaf(f.name)
            native = natives[0]

            # Check the native has proper datetime
            assert native.datetime.local_datetime.year == 1990
            assert native.datetime.local_datetime.month == 6
            assert native.datetime.local_datetime.day == 15
            assert native.datetime.local_datetime.hour == 14
            assert native.datetime.local_datetime.minute == 30

            Path(f.name).unlink()


# =============================================================================
# Integration test
# =============================================================================


class TestIntegration:
    """Integration tests for AAF parsing with chart calculation."""

    def test_parse_and_calculate_chart(self):
        """Parse AAF file and calculate chart from resulting Native."""
        from stellium import ChartBuilder

        content = """#A93:Einstein,Albert,m,14.3.1879,11:30,Ulm,Germany
#B93:2407851.97917,48n24,10e00,1he00,0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
            f.write(content)
            f.flush()

            natives = parse_aaf(f.name)
            native = natives[0]

            # Calculate chart from Native
            chart = ChartBuilder.from_native(native).calculate()

            # Verify chart has expected objects
            sun = chart.get_object("Sun")
            assert sun is not None
            # Einstein's Sun is in Pisces
            assert sun.sign == "Pisces"

            Path(f.name).unlink()
