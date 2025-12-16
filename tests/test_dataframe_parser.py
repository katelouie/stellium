"""Tests for DataFrame parser module."""

import pytest

from stellium.io.csv import CSVColumnMapping
from stellium.io.dataframe import (
    dataframe_from_natives,
    parse_dataframe,
    read_dataframe,
)

# Skip all tests if pandas is not available
pd = pytest.importorskip("pandas")


class TestParseDataframe:
    """Tests for parse_dataframe function."""

    def test_parse_standard_dataframe(self):
        """Test parsing a standard DataFrame with auto-detection."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie", "Albert Einstein"],
                "date": ["1994-01-06", "1879-03-14"],
                "time": ["11:47", "11:30"],
                "latitude": [37.3861, 48.4011],
                "longitude": [-122.0839, 9.9876],
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 2
        assert natives[0].name == "Kate Louie"
        assert natives[1].name == "Albert Einstein"
        assert abs(natives[0].location.latitude - 37.3861) < 0.001

    def test_parse_combined_datetime(self):
        """Test parsing DataFrame with combined datetime column."""
        df = pd.DataFrame(
            {
                "name": ["Test Person"],
                "datetime": ["1994-01-06 11:47"],
                "lat": [37.3861],
                "lon": [-122.0839],
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 1
        assert natives[0].datetime.utc_datetime.year == 1994

    def test_parse_split_name(self):
        """Test parsing DataFrame with first_name and last_name columns."""
        df = pd.DataFrame(
            {
                "first_name": ["Kate"],
                "last_name": ["Louie"],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "latitude": [37.3861],
                "longitude": [-122.0839],
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 1
        assert natives[0].name == "Kate Louie"

    def test_parse_date_components(self):
        """Test parsing DataFrame with separate year/month/day columns."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie"],
                "year": [1994],
                "month": [1],
                "day": [6],
                "hour": [11],
                "minute": [47],
                "latitude": [37.3861],
                "longitude": [-122.0839],
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 1
        assert natives[0].datetime.utc_datetime.year == 1994
        assert natives[0].datetime.utc_datetime.month == 1
        assert natives[0].datetime.utc_datetime.day == 6

    def test_parse_with_location_name(self):
        """Test parsing DataFrame with coordinates AND location name."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie"],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "latitude": [37.3861],
                "longitude": [-122.0839],
                "city": ["Mountain View CA"],
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 1
        assert natives[0].location.name == "Mountain View CA"
        assert abs(natives[0].location.latitude - 37.3861) < 0.001

    def test_parse_custom_mapping(self):
        """Test parsing with explicit column mapping."""
        df = pd.DataFrame(
            {
                "Full Name": ["Kate Louie"],
                "DOB": ["1994-01-06"],
                "Birth Time": ["11:47"],
                "Lat": [37.3861],
                "Long": [-122.0839],
            }
        )

        mapping = CSVColumnMapping(
            name="Full Name",
            date="DOB",
            time="Birth Time",
            latitude="Lat",
            longitude="Long",
        )
        natives = parse_dataframe(df, mapping=mapping)
        assert len(natives) == 1
        assert natives[0].name == "Kate Louie"

    def test_skip_invalid_rows(self):
        """Test that invalid rows are skipped when skip_errors=True."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie", "Invalid Row", "Einstein"],
                "date": ["1994-01-06", "bad date", "1879-03-14"],
                "time": ["11:47", "bad time", "11:30"],
                "latitude": [37.3861, "not a lat", 48.4011],
                "longitude": [-122.0839, "not a lon", 9.9876],
            }
        )

        natives = parse_dataframe(df, skip_errors=True)
        assert len(natives) == 2

    def test_error_on_invalid_row_when_not_skipping(self):
        """Test that errors are raised when skip_errors=False."""
        df = pd.DataFrame(
            {
                "name": ["Invalid Row"],
                "date": ["bad date"],
                "time": ["bad time"],
                "latitude": ["not a lat"],
                "longitude": ["not a lon"],
            }
        )

        with pytest.raises(ValueError):
            parse_dataframe(df, skip_errors=False)

    def test_handles_none_values(self):
        """Test that None values in DataFrame are handled gracefully."""
        df = pd.DataFrame(
            {
                "name": [None],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "latitude": [37.3861],
                "longitude": [-122.0839],
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 1
        assert natives[0].name is None

    def test_handles_numeric_columns(self):
        """Test that numeric columns (not strings) are handled correctly."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie"],
                "year": [1994],  # int
                "month": [1],  # int
                "day": [6],  # int
                "hour": [11],  # int
                "minute": [47],  # int
                "latitude": [37.3861],  # float
                "longitude": [-122.0839],  # float
            }
        )

        natives = parse_dataframe(df)
        assert len(natives) == 1
        assert natives[0].datetime.utc_datetime.year == 1994


class TestReadDataframe:
    """Tests for the read_dataframe convenience function."""

    def test_read_dataframe_auto(self):
        """Test read_dataframe with auto-detection."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie"],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "latitude": [37.3861],
                "longitude": [-122.0839],
            }
        )

        natives = read_dataframe(df)
        assert len(natives) == 1
        assert natives[0].name == "Kate Louie"

    def test_read_dataframe_custom_columns(self):
        """Test read_dataframe with custom column names."""
        df = pd.DataFrame(
            {
                "Person": ["Kate Louie"],
                "Birthday": ["1994-01-06"],
                "Time of Birth": ["11:47"],
                "Lat": [37.3861],
                "Long": [-122.0839],
            }
        )

        natives = read_dataframe(
            df,
            name="Person",
            date="Birthday",
            time="Time of Birth",
            latitude="Lat",
            longitude="Long",
        )
        assert len(natives) == 1
        assert natives[0].name == "Kate Louie"

    def test_read_dataframe_tuple_name(self):
        """Test read_dataframe with tuple name for first/last."""
        df = pd.DataFrame(
            {
                "First": ["Kate"],
                "Last": ["Louie"],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "lat": [37.3861],
                "lon": [-122.0839],
            }
        )

        natives = read_dataframe(
            df,
            name=("First", "Last"),
            date="date",
            time="time",
            latitude="lat",
            longitude="lon",
        )
        assert len(natives) == 1
        assert natives[0].name == "Kate Louie"


class TestDataframeFromNatives:
    """Tests for converting Natives back to DataFrame."""

    def test_round_trip(self):
        """Test converting to DataFrame and back."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie", "Albert Einstein"],
                "date": ["1994-01-06", "1879-03-14"],
                "time": ["11:47", "11:30"],
                "latitude": [37.3861, 48.4011],
                "longitude": [-122.0839, 9.9876],
                "city": ["Mountain View CA", "Ulm Germany"],
            }
        )

        # Parse to natives
        natives = parse_dataframe(df)
        assert len(natives) == 2

        # Convert back to DataFrame
        result_df = dataframe_from_natives(natives)
        assert len(result_df) == 2
        assert "name" in result_df.columns
        assert "date" in result_df.columns
        assert "latitude" in result_df.columns
        assert result_df.iloc[0]["name"] == "Kate Louie"

    def test_dataframe_from_natives_without_coords(self):
        """Test conversion without coordinates."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie"],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "latitude": [37.3861],
                "longitude": [-122.0839],
            }
        )

        natives = parse_dataframe(df)
        result_df = dataframe_from_natives(natives, include_coords=False)

        assert "latitude" not in result_df.columns
        assert "longitude" not in result_df.columns

    def test_dataframe_from_natives_with_timezone(self):
        """Test conversion with timezone column."""
        df = pd.DataFrame(
            {
                "name": ["Kate Louie"],
                "date": ["1994-01-06"],
                "time": ["11:47"],
                "latitude": [37.3861],
                "longitude": [-122.0839],
            }
        )

        natives = parse_dataframe(df)
        result_df = dataframe_from_natives(natives, include_timezone=True)

        assert "timezone" in result_df.columns
