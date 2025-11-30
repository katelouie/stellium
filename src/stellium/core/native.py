"""
The Native class represents the core data for a single person or event.

Its job is to handle messy inputs (strings, dicts, naive datetimes, etc.) and process
them into the clean, immutable ChartDateTime and ChartLocation objects
that the rest of the system requires.
"""

import datetime as dt
from typing import Any

import pytz
import swisseph as swe
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from stellium.core.models import ChartDateTime, ChartLocation
from stellium.utils.cache import cached

# Cache TimezoneFinder instance - initialization is expensive
_timezone_finder: TimezoneFinder | None = None


def _get_timezone_finder() -> TimezoneFinder:
    """Get cached TimezoneFinder instance."""
    global _timezone_finder
    if _timezone_finder is None:
        _timezone_finder = TimezoneFinder()
    return _timezone_finder


# Define the messy input types we'll accept
DateTimeInput = dt.datetime | ChartDateTime | dict[str, Any] | str
LocationInput = str | ChartLocation | tuple[float, float] | dict[str, float | str]


class Native:
    """
    Represents the "native" data (time and place) for a chart.
    This class handles all the input parsing and data cleaning.
    """

    datetime: ChartDateTime
    location: ChartLocation
    name: str | None
    time_unknown: bool

    def __init__(
        self,
        datetime_input: DateTimeInput,
        location_input: LocationInput,
        *,
        name: str | None = None,
        time_unknown: bool = False,
    ) -> None:
        """Creates a new Native object by parsing flexible inputs.

        Args:
            datetime_input: Can be a timezone-aware datetime, a datetime string,
                a dict, or a pre-made ChartDateTime object
            location_input: Can be a string to geocode, a (lat, lon) tuple,
                a dict, or a pre-made ChartLocation object
            name: Optional name of the person or event (for display purposes)
            time_unknown: If True, only the date is known (time set to noon,
                houses/angles will not be calculated, Moon shown as range)
        """
        self.location = self._process_location(location_input)
        self.time_unknown = time_unknown

        # If time is unknown, normalize to noon for calculation
        if time_unknown:
            datetime_input = self._normalize_to_noon(datetime_input)

        self.datetime = self._process_datetime(datetime_input, self.location.timezone)
        self.name = name

    def _normalize_to_noon(self, datetime_input: DateTimeInput) -> dt.datetime:
        """
        Normalize a datetime input to noon on the same date.

        Used for unknown birth time charts where we calculate for noon
        as the midpoint of the day.

        Args:
            datetime_input: Any supported datetime input

        Returns:
            A naive datetime set to 12:00:00 on the same date
        """
        # Handle string input
        if isinstance(datetime_input, str):
            parsed = self._parse_datetime_string(datetime_input)
            return dt.datetime(parsed.year, parsed.month, parsed.day, 12, 0, 0)

        # Handle datetime object
        if isinstance(datetime_input, dt.datetime):
            return dt.datetime(
                datetime_input.year, datetime_input.month, datetime_input.day, 12, 0, 0
            )

        # Handle dict input
        if isinstance(datetime_input, dict):
            return dt.datetime(
                int(datetime_input["year"]),
                int(datetime_input["month"]),
                int(datetime_input["day"]),
                12,
                0,
                0,
            )

        # Handle ChartDateTime (extract date, set to noon)
        if isinstance(datetime_input, ChartDateTime):
            utc = datetime_input.utc_datetime
            return dt.datetime(utc.year, utc.month, utc.day, 12, 0, 0)

        raise TypeError(
            f"Cannot normalize datetime input of type: {type(datetime_input)}"
        )

    def _process_location(self, loc_in: LocationInput) -> ChartLocation:
        """Internal helper to parse any location input."""

        # 1. Already have a ChartLocation? We're done
        if isinstance(loc_in, ChartLocation):
            return loc_in

        # 2. A string? Geocode it.
        if isinstance(loc_in, str):
            location_data = _cached_geocode(loc_in)
            if not location_data:
                raise ValueError(f"Could not geocode location: {loc_in}")
            return ChartLocation(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                name=location_data["address"],
                timezone=location_data["timezone"],
            )

        # 3. A tuple? Assume (lat, lon)
        if isinstance(loc_in, tuple) and len(loc_in) == 2:
            lat, lon = loc_in

            # Find the timezone for this lat/lon
            tf = _get_timezone_finder()
            timezone_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"

            return ChartLocation(
                latitude=float(lat),
                longitude=float(lon),
                name=f"{lat}, {lon}",
                timezone=timezone_str,
            )

        # 4. A dict? Assume {lat, lon, ...}
        if isinstance(loc_in, dict):
            if "latitude" not in loc_in or "longitude" not in loc_in:
                raise ValueError(
                    "Location dict must contain 'latitude' and 'longitude'"
                )
            lat = float(loc_in["latitude"])
            lon = float(loc_in["longitude"])

            # Find timezone if not provided
            timezone_str = loc_in.get("timezone")
            if not timezone_str:
                tf = _get_timezone_finder()
                timezone_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"

            return ChartLocation(
                latitude=lat,
                longitude=lon,
                name=str(loc_in.get("name", f"{lat}, {lon}")),
                timezone=str(timezone_str),
            )

        raise TypeError(f"Unsupported location input type: {type(loc_in)}")

    def _parse_datetime_string(self, dt_string: str) -> dt.datetime:
        """
        Parse a datetime string into a datetime object.

        Supports formats:
        - ISO 8601: "2024-11-24T14:30:00"
        - Common: "2024-11-24 14:30:00", "2024-11-24 14:30"
        - US: "11/24/2024 14:30", "11/24/2024 2:30 PM"
        - European: "24/11/2024 14:30"
        - Compact: "20241124143000", "20241124 1430"

        Args:
            dt_string: The datetime string to parse

        Returns:
            A naive datetime object (will be localized later)

        Raises:
            ValueError: If the string cannot be parsed with helpful suggestions
        """
        # Strip whitespace
        dt_string = dt_string.strip()

        # Common formats to try, in order of likelihood
        formats = [
            # ISO 8601 and variants
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            # Common variants
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            # US format
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %I:%M %p",  # With AM/PM
            "%m/%d/%Y",
            # European format
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            # Compact formats
            "%Y%m%d%H%M%S",
            "%Y%m%d %H%M",
            "%Y%m%d",
        ]

        # Try each format
        for fmt in formats:
            try:
                return dt.datetime.strptime(dt_string, fmt)
            except ValueError:
                continue

        # If we got here, nothing worked - provide helpful error
        raise ValueError(
            f"Could not parse datetime string: '{dt_string}'\n\n"
            "Supported formats:\n"
            "  - ISO 8601: '2024-11-24T14:30:00' or '2024-11-24 14:30'\n"
            "  - US format: '11/24/2024 14:30' or '11/24/2024 2:30 PM'\n"
            "  - European: '24/11/2024 14:30'\n"
            "  - Date only: '2024-11-24' (assumes midnight)\n"
            "\nTime is optional and defaults to midnight if not provided."
        )

    def _process_datetime(
        self, time_input: DateTimeInput, loc_timezone: str
    ) -> ChartDateTime:
        """
        Parses any time input into a ChartDateTime object.

        Args:
            time_input: A dt.datetime, string, dict, or ChartDateTime.
            location_timezone: The IANA timezone string (e.g., "America/New_York")
                               found during location parsing.
        """
        # 1. Already a ChartDateTime? We're done.
        if isinstance(time_input, ChartDateTime):
            return time_input

        utc_dt: dt.datetime | None = None
        local_dt: dt.datetime | None = None

        # 2. String Input - Parse datetime string
        if isinstance(time_input, str):
            time_input = self._parse_datetime_string(time_input)
            # Now time_input is a dt.datetime, continue to next step

        # 3. Datetime Object Input
        if isinstance(time_input, dt.datetime):
            local_dt = time_input  # Store for the final object
            if time_input.tzinfo is None:
                # Naive datetime. Localize it using the location's timezone.
                if not loc_timezone:
                    raise ValueError(
                        "Datetime is naive (no timezone) and location has no timezone. "
                        "Cannot determine time."
                    )
                try:
                    loc_tz = pytz.timezone(loc_timezone)
                    aware_dt = loc_tz.localize(time_input)
                    utc_dt = aware_dt.astimezone(dt.UTC)
                except pytz.UnknownTimeZoneError:
                    raise ValueError(
                        f"Invalid location timezone: {loc_timezone}"
                    ) from pytz.UnknownTimeZoneError
            else:
                # Aware datetime. Just convert to UTC.
                utc_dt = time_input.astimezone(dt.UTC)

        # 4. Dictionary Input
        elif isinstance(time_input, dict):
            try:
                naive_dt = dt.datetime(
                    year=int(time_input["year"]),
                    month=int(time_input["month"]),
                    day=int(time_input["day"]),
                    hour=int(time_input.get("hour", 0)),
                    minute=int(time_input.get("minute", 0)),
                    second=int(time_input.get("second", 0)),
                )
                local_dt = naive_dt  # Store this as the local time

                # Now, use the location's timezone to make it aware
                if not loc_timezone:
                    raise ValueError(
                        "Time was input as a dict (naive) and location has no timezone. "
                        "Cannot determine time."
                    )
                try:
                    loc_tz = pytz.timezone(loc_timezone)
                    aware_dt = loc_tz.localize(naive_dt)
                    utc_dt = aware_dt.astimezone(dt.UTC)
                    local_dt = aware_dt  # Store the *aware* local time
                except pytz.UnknownTimeZoneError:
                    raise ValueError(
                        f"Invalid location timezone: {loc_timezone}"
                    ) from pytz.UnknownTimeZoneError

            except KeyError as e:
                raise KeyError(f"Missing required time key in dict: {e}") from KeyError
            except Exception as e:
                raise ValueError(f"Error parsing time dict: {e}") from Exception

        else:
            raise TypeError(f"Invalid datetime_input type: {type(time_input)}")

        # --- Final Conversion ---
        if utc_dt:
            # Calculate Julian day from the (now guaranteed) UTC datetime
            # We must use the UTC time for swe.julday to get ET
            hour_decimal = (
                (utc_dt.minute / 60.0)
                + (utc_dt.second / 3600.0)
                + (utc_dt.microsecond / 3600000000.0)
            )
            julian_day_et = swe.julday(
                utc_dt.year,
                utc_dt.month,
                utc_dt.day,
                utc_dt.hour + hour_decimal,
            )

            # Get Delta T and convert to Julian Day UT (Universal Time)
            # This is the correct Julian Day for calculations.
            delta_t = swe.deltat(julian_day_et)
            julian_day_ut = julian_day_et - delta_t

            return ChartDateTime(
                utc_datetime=utc_dt, julian_day=julian_day_ut, local_datetime=local_dt
            )

        raise ValueError("Could not parse datetime input.")


class Notable(Native):
    """
    A Native with curated metadata from the registry.

    Represents famous births and notable events. The base Native class
    handles all datetime/location parsing - Notable just adds metadata.

    Example:
        >>> notable = Notable(
        ...     name="Albert Einstein",
        ...     event_type="birth",
        ...     year=1879, month=3, day=14, hour=11, minute=30,
        ...     location_input="Ulm, Germany",
        ...     category="scientist"
        ... )
        >>> chart = ChartBuilder.from_native(notable).calculate()
    """

    # Metadata fields
    name: str
    event_type: str  # "birth" or "event"
    category: str
    subcategories: list[str] | None
    notable_for: str
    astrological_notes: str
    data_quality: str
    sources: list[str] | None
    verified: bool

    def __init__(
        self,
        name: str,
        event_type: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        location_input: LocationInput,  # Reuse Native's type!
        category: str,
        subcategories: list[str] | None = None,
        notable_for: str = "",
        astrological_notes: str = "",
        data_quality: str = "C",
        sources: list[str] | None = None,
        verified: bool = False,
    ):
        """
        Create Notable from structured data.

        The datetime is assumed to be in LOCAL time for the location,
        and Native will handle timezone conversion automatically.

        Args:
            name: Name of person or event
            event_type: "birth" or "event"
            year, month, day, hour, minute: Local time components
            location_input: Location (string name, (lat, lon) tuple, or ChartLocation)
            category: Primary category (scientist, artist, leader, etc.)
            subcategories: Optional subcategories
            notable_for: Brief description of why this person/event is notable
            astrological_notes: Astrological observations
            data_quality: Rodden rating (AA, A, B, C, DD)
            sources: List of data sources
            verified: Whether data has been verified
        """
        # Create naive datetime (local time)
        local_dt = dt.datetime(year, month, day, hour, minute)

        # Let Native handle ALL the parsing!
        super().__init__(
            datetime_input=local_dt,  # Naive datetime
            location_input=location_input,  # String, tuple, or ChartLocation
        )

        # Add our metadata
        self.name = name
        self.event_type = event_type
        self.category = category
        self.subcategories = subcategories or []
        self.notable_for = notable_for
        self.astrological_notes = astrological_notes
        self.data_quality = data_quality
        self.sources = sources or []
        self.verified = verified

    @property
    def is_birth(self) -> bool:
        """Check if this is a birth record."""
        return self.event_type == "birth"

    @property
    def is_event(self) -> bool:
        """Check if this is an event record."""
        return self.event_type == "event"

    def __repr__(self) -> str:
        return f"<Notable: {self.name} ({self.category})>"


# --- Geocoding Helper ---
@cached(cache_type="geocoding", max_age_seconds=604800)
def _cached_geocode(location_name: str) -> dict:
    """Cached geocoding."""
    try:
        geolocator = Nominatim(user_agent="stellium_astrology_package")
        location = geolocator.geocode(location_name)
        if location:
            lat, lon = location.latitude, location.longitude

            tf = _get_timezone_finder()
            timezone_str = tf.timezone_at(lng=lon, lat=lat)
            return {
                "latitude": lat,
                "longitude": lon,
                "address": str(location),
                "timezone": timezone_str,
            }
        return {}
    except GeocoderUnavailable:
        print("Warning: Geocoding service is unavailable.")
        return {}
    except Exception as e:
        print(f"Warning: Geocoding error: {e}")
        return {}
