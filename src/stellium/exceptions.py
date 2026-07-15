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


class MissingGlyphWarning(StelliumWarning):
    """A body's bundled SVG glyph could not be found, so a Unicode glyph was used.

    These SVGs exist precisely *because* the Unicode codepoint is inadequate — Pholus
    is U+2B30, which is present in no font on any platform, and Sedna's fallback is
    the literal string "Sed". So this is a visible failure, not a graceful
    degradation, and it is almost always a **packaging fault** rather than anything
    the caller did.

    Silence it as usual if you must::

        warnings.filterwarnings("ignore", category=MissingGlyphWarning)
    """


class MissingFontWarning(StelliumWarning):
    """A chart's text needs a font that is not installed, so it will render as boxes.

    Distinct from :class:`MissingGlyphWarning` (a missing *object* glyph): this is about
    the *text* — a Chinese name, a localized label — whose script the bundled Latin and
    symbol fonts do not cover. In a PNG or PDF (which are rasterised with only the
    bundled/downloaded fonts, for reproducibility) that text becomes tofu boxes; in an
    SVG opened in a browser it may still work via the host's system fonts. The remedy,
    named in the message, is ``stellium fonts download <script>`` or
    ``ChartDrawBuilder.with_font(path)``.

    Silence it as usual::

        warnings.filterwarnings("ignore", category=MissingFontWarning)
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


class TimeZoneWarning(StelliumWarning):
    """A time could not be resolved to UT as accurately as it should have been.

    Raised when a birth predates standard time in its zone — when the clock on the
    wall showed **Local Mean Time**, an offset determined by the birthplace's
    longitude and nothing else — but no longitude was supplied. We then have to fall
    back on the IANA zone's own LMT, which is its *reference city's*, not the
    birthplace's: `Europe/London`'s LMT is −1m, while Diseworth (1°16′W, where William
    Lilly was born) is −5m04s. Four minutes of clock is roughly a degree of Ascendant,
    and for Lilly it was the difference between Pisces rising and Aquarius rising.
    """
