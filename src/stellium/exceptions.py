"""Stellium warning (and future exception) types.

This module houses the warning hierarchy so callers can filter Stellium's
diagnostics precisely. All warnings derive from :class:`StelliumWarning`, so a
single filter silences everything::

    import warnings
    from stellium.exceptions import StelliumWarning
    warnings.filterwarnings("ignore", category=StelliumWarning)

Or target one kind::

    from stellium.exceptions import DataQualityWarning
    warnings.filterwarnings("ignore", category=DataQualityWarning)

Warnings are for conditions the *caller* should know about and could act on or
suppress (questionable input, degraded results). Internal operational
diagnostics use the :mod:`stellium._logging` logger instead; see
``docs/development/specs/STRUCTURED_LOGGING_SPEC.md``.
"""

from __future__ import annotations


class StelliumWarning(UserWarning):
    """Base class for all Stellium warnings.

    Filter this category to silence every Stellium warning at once.
    """


class DataQualityWarning(StelliumWarning):
    """Input data was malformed, incomplete, or skipped.

    Raised when a row, record, or entry supplied by the caller (a CSV/AAF
    import, a notable YAML file, a requested lot) could not be used and was
    skipped. The rest of the operation continues.
    """


class GeocodingWarning(StelliumWarning):
    """A location could not be geocoded, or the geocoding service failed.

    Often actionable by the caller (offline, rate-limited, or a place name the
    geocoder can't resolve); pass explicit coordinates to avoid geocoding.
    """


class ConfigurationWarning(StelliumWarning):
    """A configuration value was invalid and ignored.

    Raised when caller-supplied configuration can't be honored (e.g. a
    malformed orb ``by_pair`` key, or a house system requested for a chart that
    doesn't have it). A sensible default or degraded result is used instead.
    """


class MissingEphemerisWarning(StelliumWarning):
    """A body was skipped because its ephemeris file is unavailable.

    Emitted via the :mod:`warnings` module (not a bare print) so callers can
    capture, filter, or silence it -- e.g.::

        import warnings
        from stellium.exceptions import MissingEphemerisWarning
        warnings.filterwarnings("ignore", category=MissingEphemerisWarning)
        # or capture which bodies were skipped:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", MissingEphemerisWarning)
            chart = ChartBuilder.from_native(n).with_tnos().calculate()
        skipped = [w for w in caught if issubclass(w.category, MissingEphemerisWarning)]

    Importable from ``stellium.engines`` as well, for backward compatibility.
    """
