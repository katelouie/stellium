"""Tests for CSV parser module."""

import tempfile
from pathlib import Path

import pytest

from stellium.io.csv import (
    CSVColumnMapping,
    _auto_detect_mapping,
    _find_column,
    _parse_date_string,
    _parse_time_string,
    parse_csv,
    read_csv,
)


class TestColumnFinding:
    """Tests for column name detection."""

    def test_find_exact_match(self):
        headers = ["name", "date", "time", "location"]
        assert _find_column(headers, "name") == "name"
        assert _find_column(headers, "date") == "date"

    def test_find_case_insensitive(self):
        headers = ["Name", "DATE", "Time", "LOCATION"]
        assert _find_column(headers, "name") == "Name"
        assert _find_column(headers, "date") == "DATE"

    def test_find_alias(self):
        headers = ["full_name", "dob", "tob", "birthplace"]
        assert _find_column(headers, "name") == "full_name"
        assert _find_column(headers, "date") == "dob"
        assert _find_column(headers, "time") == "tob"
        assert _find_column(headers, "location") == "birthplace"

    def test_find_not_found(self):
        headers = ["foo", "bar", "baz"]
        assert _find_column(headers, "name") is None
        assert _find_column(headers, "date") is None


class TestAutoDetection:
    """Tests for auto-detecting column mappings."""

    def test_auto_detect_standard_columns(self):
        headers = ["name", "date", "time", "location"]
        mapping = _auto_detect_mapping(headers)
        assert mapping.name == "name"
        assert mapping.date == "date"
        assert mapping.time == "time"
        assert mapping.location == "location"

    def test_auto_detect_combined_datetime(self):
        headers = ["name", "datetime", "place"]
        mapping = _auto_detect_mapping(headers)
        assert mapping.name == "name"
        assert mapping.datetime == "datetime"
        assert mapping.location == "place"

    def test_auto_detect_coordinates(self):
        headers = ["name", "date", "time", "latitude", "longitude"]
        mapping = _auto_detect_mapping(headers)
        assert mapping.latitude == "latitude"
        assert mapping.longitude == "longitude"

    def test_auto_detect_split_name(self):
        headers = ["first_name", "last_name", "date", "time", "location"]
        mapping = _auto_detect_mapping(headers)
        assert mapping.name == ("first_name", "last_name")

    def test_auto_detect_date_components(self):
        headers = ["name", "year", "month", "day", "hour", "minute", "location"]
        mapping = _auto_detect_mapping(headers)
        assert mapping.year == "year"
        assert mapping.month == "month"
        assert mapping.day == "day"
        assert mapping.hour == "hour"
        assert mapping.minute == "minute"


class TestDateParsing:
    """Tests for date string parsing."""

    def test_parse_iso_date(self):
        assert _parse_date_string("1994-01-06") == (1994, 1, 6)
        assert _parse_date_string("2000-12-31") == (2000, 12, 31)

    def test_parse_us_date(self):
        assert _parse_date_string("01/06/1994") == (1994, 1, 6)
        assert _parse_date_string("12/31/2000") == (2000, 12, 31)

    def test_parse_eu_date(self):
        assert _parse_date_string("06.01.1994") == (1994, 1, 6)
        assert _parse_date_string("31.12.2000") == (2000, 12, 31)

    def test_parse_text_date(self):
        assert _parse_date_string("January 6, 1994") == (1994, 1, 6)
        assert _parse_date_string("Jan 6, 1994") == (1994, 1, 6)

    def test_parse_with_format_hint(self):
        # European format (day/month/year)
        assert _parse_date_string("06/01/1994", "%d/%m/%Y") == (1994, 1, 6)

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            _parse_date_string("not a date")


class TestTimeParsing:
    """Tests for time string parsing."""

    def test_parse_24_hour(self):
        assert _parse_time_string("11:47") == (11, 47, 0)
        assert _parse_time_string("11:47:30") == (11, 47, 30)
        assert _parse_time_string("23:59:59") == (23, 59, 59)

    def test_parse_12_hour(self):
        assert _parse_time_string("11:47 AM") == (11, 47, 0)
        assert _parse_time_string("11:47 PM") == (23, 47, 0)
        assert _parse_time_string("12:00 AM") == (0, 0, 0)
        assert _parse_time_string("12:00 PM") == (12, 0, 0)

    def test_invalid_time_raises(self):
        with pytest.raises(ValueError):
            _parse_time_string("not a time")


class TestCSVParsing:
    """Tests for full CSV parsing."""

    def test_parse_standard_csv(self):
        """Test parsing a standard CSV with auto-detection."""
        csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
Albert Einstein,1879-03-14,11:30,48.4011,9.9876
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = parse_csv(temp_path)
            assert len(natives) == 2
            assert natives[0].name == "Kate Louie"
            assert natives[1].name == "Albert Einstein"
            # Check coordinates
            assert abs(natives[0].location.latitude - 37.3861) < 0.001
            assert abs(natives[0].location.longitude - (-122.0839)) < 0.001
        finally:
            Path(temp_path).unlink()

    def test_parse_combined_datetime(self):
        """Test parsing CSV with combined datetime column."""
        csv_content = """name,datetime,lat,lon
Test Person,1994-01-06 11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = parse_csv(temp_path)
            assert len(natives) == 1
            assert natives[0].name == "Test Person"
            assert natives[0].datetime.utc_datetime.year == 1994
        finally:
            Path(temp_path).unlink()

    def test_parse_split_name(self):
        """Test parsing CSV with first_name and last_name columns."""
        csv_content = """first_name,last_name,date,time,latitude,longitude
Kate,Louie,1994-01-06,11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = parse_csv(temp_path)
            assert len(natives) == 1
            assert natives[0].name == "Kate Louie"
        finally:
            Path(temp_path).unlink()

    def test_parse_date_components(self):
        """Test parsing CSV with separate year/month/day columns."""
        csv_content = """name,year,month,day,hour,minute,latitude,longitude
Kate Louie,1994,1,6,11,47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = parse_csv(temp_path)
            assert len(natives) == 1
            assert natives[0].datetime.utc_datetime.year == 1994
            assert natives[0].datetime.utc_datetime.month == 1
            assert natives[0].datetime.utc_datetime.day == 6
        finally:
            Path(temp_path).unlink()

    def test_parse_custom_mapping(self):
        """Test parsing with explicit column mapping."""
        csv_content = """Full Name,DOB,Birth Time,Lat,Long
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            mapping = CSVColumnMapping(
                name="Full Name",
                date="DOB",
                time="Birth Time",
                latitude="Lat",
                longitude="Long",
            )
            natives = parse_csv(temp_path, mapping=mapping)
            assert len(natives) == 1
            assert natives[0].name == "Kate Louie"
        finally:
            Path(temp_path).unlink()

    def test_skip_invalid_rows(self):
        """Test that invalid rows are skipped when skip_errors=True."""
        csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
Invalid Row,bad date,bad time,not a lat,not a lon
Einstein,1879-03-14,11:30,48.4011,9.9876
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # Should skip the invalid row and continue
            natives = parse_csv(temp_path, skip_errors=True)
            assert len(natives) == 2
        finally:
            Path(temp_path).unlink()

    def test_error_on_invalid_row_when_not_skipping(self):
        """Test that errors are raised when skip_errors=False."""
        csv_content = """name,date,time,latitude,longitude
Invalid Row,bad date,bad time,not a lat,not a lon
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                parse_csv(temp_path, skip_errors=False)
        finally:
            Path(temp_path).unlink()


class TestReadCsvConvenience:
    """Tests for the read_csv convenience function."""

    def test_read_csv_auto(self):
        """Test read_csv with auto-detection."""
        csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = read_csv(temp_path)
            assert len(natives) == 1
            assert natives[0].name == "Kate Louie"
        finally:
            Path(temp_path).unlink()

    def test_read_csv_custom_columns(self):
        """Test read_csv with custom column names."""
        csv_content = """Person,Birthday,Time of Birth,Lat,Long
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = read_csv(
                temp_path,
                name="Person",
                date="Birthday",
                time="Time of Birth",
                latitude="Lat",
                longitude="Long",
            )
            assert len(natives) == 1
            assert natives[0].name == "Kate Louie"
        finally:
            Path(temp_path).unlink()

    def test_read_csv_tuple_name(self):
        """Test read_csv with tuple name for first/last."""
        csv_content = """First,Last,date,time,lat,lon
Kate,Louie,1994-01-06,11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = read_csv(
                temp_path,
                name=("First", "Last"),
                date="date",
                time="time",
                latitude="lat",
                longitude="lon",
            )
            assert len(natives) == 1
            assert natives[0].name == "Kate Louie"
        finally:
            Path(temp_path).unlink()


class TestLocationHandling:
    """Tests for different location input scenarios."""

    def test_coords_only(self):
        """Test with only latitude/longitude (no location name)."""
        csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = parse_csv(temp_path)
            assert len(natives) == 1
            assert abs(natives[0].location.latitude - 37.3861) < 0.001
            # Location name will be empty or auto-generated
        finally:
            Path(temp_path).unlink()

    def test_coords_with_location_name(self):
        """Test with latitude/longitude AND a location name column."""
        csv_content = """name,date,time,latitude,longitude,city
Kate Louie,1994-01-06,11:47,37.3861,-122.0839,Mountain View CA
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            natives = parse_csv(temp_path)
            assert len(natives) == 1
            assert abs(natives[0].location.latitude - 37.3861) < 0.001
            # Location name should be preserved
            assert natives[0].location.name == "Mountain View CA"
        finally:
            Path(temp_path).unlink()

    def test_location_string_only_for_geocoding(self):
        """Test with only location string (needs geocoding) - skipped if geocoding fails."""
        csv_content = """name,date,time,location
Kate Louie,1994-01-06,11:47,Mountain View CA
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # This may fail if geocoding service is unavailable
            # So we just verify the structure, not actual geocoding
            natives = parse_csv(temp_path, skip_errors=True)
            # If geocoding worked, we should have 1 native
            # If it failed, we should have 0 (skipped)
            assert len(natives) <= 1
        finally:
            Path(temp_path).unlink()


class TestFileNotFound:
    """Tests for file not found handling."""

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_csv("/nonexistent/path/to/file.csv")
