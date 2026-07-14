"""
Registry for curated notable births and events.

Provides access to a compendium of famous births and historical events
that can be used for examples, testing, and research.
"""

import importlib.resources
import warnings
from pathlib import Path

import yaml

from stellium.core.native import Notable
from stellium.exceptions import DataQualityWarning


class NotableRegistry:
    """
    Registry for curated notable births and events.

    This provides access to a compendium of famous births and historical
    events that can be used for examples, testing, and research.

    Example:
        >>> from stellium.data import get_notable_registry
        >>> registry = get_notable_registry()
        >>> einstein = registry.get_by_name("Albert Einstein")
        >>> print(einstein.name, einstein.category)
        Albert Einstein scientist
    """

    def __init__(self):
        self._notables: list[Notable] = []
        self._load_all()

    def _get_notables_path(self) -> Path | None:
        """
        Get the path to the notables data directory.

        Uses importlib.resources to find package data, which works both
        in development (editable install) and when installed as a package.

        Returns:
            Path to notables directory, or None if not found
        """
        try:
            # Use importlib.resources to find package data
            files = importlib.resources.files("stellium.data")
            notables_path = files / "notables"

            # For editable installs, this returns the actual filesystem path
            # For installed packages, we may need to use as_file()
            if hasattr(notables_path, "_path"):
                real_path = Path(notables_path._path)
                if real_path.exists():
                    return real_path

            # Try traversable interface
            with importlib.resources.as_file(notables_path) as path:
                if path.exists():
                    return path

            return None
        except (TypeError, FileNotFoundError, AttributeError):
            return None

    def _load_all(self) -> None:
        """Load all YAML files and create Notable objects."""
        data_dir = self._get_notables_path()

        if data_dir is None:
            # No notable data found - this is OK for minimal installs
            return

        # Load YAML files from births/ and events/ ONLY. Other subdirectories
        # (life_events/, temperament/) are biographical datasets with their own
        # schema + loaders (stellium.data.biography), not Notable birth/event
        # records — scanning them here would emit a warning per entry.
        yaml_files = sorted((data_dir / "births").glob("*.yaml")) + sorted(
            (data_dir / "events").glob("*.yaml")
        )
        for yaml_file in yaml_files:
            try:
                with open(yaml_file) as f:
                    entries = yaml.safe_load(f) or []
            except Exception as e:
                warnings.warn(
                    f"Failed to read {yaml_file}: {e}",
                    DataQualityWarning,
                    stacklevel=2,
                )
                continue

            for entry in entries:
                # Determine location input format
                location_input = self._parse_location(entry)

                if location_input is None:
                    warnings.warn(
                        f"No valid location data in {yaml_file} for "
                        f"{entry.get('name', 'unknown')}",
                        DataQualityWarning,
                        stacklevel=2,
                    )
                    continue

                try:
                    # Create Notable - it calls Native.__init__ internally!
                    notable = Notable(
                        name=entry["name"],
                        event_type=entry["event_type"],
                        year=entry["year"],
                        month=entry["month"],
                        day=entry["day"],
                        # hour/minute may be absent for timeless notables — the
                        # audit removes speculative times (null). Tolerate it.
                        hour=entry.get("hour"),
                        minute=entry.get("minute"),
                        location_input=location_input,  # Native handles it!
                        category=entry["category"],
                        subcategories=entry.get("subcategories"),
                        notable_for=entry.get("notable_for", ""),
                        astrological_notes=entry.get("astrological_notes", ""),
                        data_quality=entry.get("data_quality", "C"),
                        sources=entry.get("sources"),
                        verified=entry.get("verified", False),
                        has_reliable_time=entry.get("has_reliable_time"),
                        verification_notes=entry.get("verification_notes", ""),
                        # Absent means Gregorian, which is right for the ~180 modern
                        # records and a coin-flip for a 17th-century one — so
                        # tests/test_notable_calendars.py *requires* a pre-1753 birth
                        # to say which calendar it means, rather than inherit this.
                        calendar=entry.get("calendar"),
                    )

                    self._notables.append(notable)
                except Exception as e:
                    warnings.warn(
                        f"Failed to load notable "
                        f"'{entry.get('name', 'unknown')}' from {yaml_file.name}: {e}",
                        DataQualityWarning,
                        stacklevel=2,
                    )

    def _parse_location(self, entry: dict) -> str | tuple[float, float] | dict | None:
        """
        Parse location from YAML entry.

        Supports multiple formats:

        - location: "City, Country" (geocoded)
        - latitude/longitude: as tuple
        - latitude/longitude/timezone: as tuple (timezone will be found by Native)
        """
        # Option 1: location name string
        if "location" in entry:
            return entry["location"]

        # Option 2: lat/long with timezone (BEST - avoids TimezoneFinder)
        if "latitude" in entry and "longitude" in entry and "timezone" in entry:
            return {
                "latitude": entry["latitude"],
                "longitude": entry["longitude"],
                "name": entry.get("location_name", ""),
                "timezone": entry["timezone"],
            }

        # Option 3: lat/long tuple
        if "latitude" in entry and "longitude" in entry:
            return (entry["latitude"], entry["longitude"])

        # No valid location format
        return None

    def get_by_name(self, name: str) -> Notable | None:
        """
        Get notable by name (case-insensitive).

        Args:
            name: Name of person or event

        Returns:
            Notable object or None if not found
        """
        for notable in self._notables:
            if notable.name.lower() == name.lower():
                return notable
        return None

    def get_by_category(self, category: str) -> list[Notable]:
        """
        Get all notables in a category.

        Args:
            category: Category name (scientist, artist, leader, etc.)

        Returns:
            List of Notable objects in that category
        """
        return [n for n in self._notables if n.category == category]

    def get_by_event_type(self, event_type: str) -> list[Notable]:
        """
        Get all births or all events.

        Args:
            event_type: "birth" or "event"

        Returns:
            List of Notable objects of that type
        """
        return [n for n in self._notables if n.event_type == event_type]

    def get_births(self) -> list[Notable]:
        """Get all birth records."""
        return self.get_by_event_type("birth")

    def get_events(self) -> list[Notable]:
        """Get all event records."""
        return self.get_by_event_type("event")

    def search(self, **filters) -> list[Notable]:
        """
        Search with arbitrary filters.

        Examples:
            >>> registry.search(category="scientist")
            >>> registry.search(event_type="birth", verified=True)
            >>> registry.search(data_quality="AA")

        Args:
            **filters: Keyword arguments matching Notable attributes

        Returns:
            List of Notable objects matching all filters
        """
        results = self._notables

        for key, value in filters.items():
            results = [n for n in results if getattr(n, key, None) == value]

        return results

    def get_all(self) -> list[Notable]:
        """Get all notable data entries."""
        return self._notables.copy()

    def __len__(self) -> int:
        """Number of notables in registry."""
        return len(self._notables)

    def __repr__(self) -> str:
        births = len(self.get_births())
        events = len(self.get_events())
        return f"<NotableRegistry: {births} births, {events} events>"


# Singleton instance
_registry: NotableRegistry | None = None


def get_notable_registry() -> NotableRegistry:
    """
    Get the global notable registry instance.

    Returns:
        The singleton NotableRegistry instance

    Example:
        >>> registry = get_notable_registry()
        >>> einstein = registry.get_by_name("Albert Einstein")
    """
    global _registry
    if _registry is None:
        _registry = NotableRegistry()
    return _registry
