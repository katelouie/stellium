"""Locale patterns for the things that are not words: dates, times, numbers, degrees.

A date is the case that proves why post-hoc translation cannot work. ``March 14, 1879``
→ ``1879年3月14日`` is a *reorder*; no amount of word substitution produces it. So the
pattern itself is locale data:

    "format.date": "{year}年{month_num}月{day}日"

Every slot is always supplied, so a locale takes whichever it needs and ignores the rest
— a locale wanting the month spelled out uses ``{month}``, one wanting it numeric uses
``{month_num}``, and neither has to tell us in advance. The English default *is* the
fallback pattern, so a locale that defines nothing still renders correctly.

See docs/development/specs/STRUCTURE_FIRST_SECTIONS.md §4.4.
"""

from __future__ import annotations

import datetime as dt

from stellium.i18n.loader import t

# The English patterns. Each is also the translation *key* for its locale override, so a
# locale file's "format.date" replaces the whole layout rather than any single word.
# The English defaults reproduce the strftime calls they replace ("%B %d, %Y" and
# "%I:%M %p"), including the zero-padded day and hour, so migrating a section to
# format_date/format_time leaves English output byte-identical. A locale wanting an
# unpadded day (Chinese: "3日", not "03日") uses {day}/{hour12} instead of the _pad forms.
DEFAULT_PATTERNS: dict[str, str] = {
    "format.date": "{month} {day_pad}, {year}",
    "format.date_short": "{month_abbr} {day_pad}, {year}",
    "format.time": "{hour12_pad}:{minute} {ampm}",
    "format.datetime": "{date} {time}",
    "format.degrees": "{deg}°{min:02d}'",
    "format.decimal_sep": ".",
    "format.latitude": "{value}°{hemisphere}",
    "format.longitude": "{value}°{hemisphere}",
}

MONTHS: tuple[str, ...] = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def pattern(key: str, locale: str | None = None) -> str:
    """The locale's pattern for ``key``, or the English default."""
    default = DEFAULT_PATTERNS[key]
    found = t(key, locale=locale)
    # t() echoes the key back when there is no translation.
    return default if found == key else found


def format_date(
    value: dt.date, locale: str | None = None, *, short: bool = False
) -> str:
    """A date, laid out the way the locale lays out dates.

    ``short=True`` uses ``format.date_short`` (an abbreviated month, "Mar"), for the
    compact header line. A locale with no concept of month abbreviation just uses the
    numeric month in its short pattern.
    """
    key = "format.date_short" if short else "format.date"
    return pattern(key, locale).format(
        year=value.year,
        month=_month_name(value.month, locale),
        month_abbr=_month_abbr(value.month, locale),
        month_num=value.month,
        month_pad=f"{value.month:02d}",
        day=value.day,
        day_pad=f"{value.day:02d}",
    )


def _month_abbr(month: int, locale: str | None) -> str:
    """The 3-letter month ("Mar"). Localizable via ``month_abbr.<English>`` keys."""
    english = MONTHS[month - 1][:3]
    key = f"month_abbr.{MONTHS[month - 1]}"
    found = t(key, locale=locale)
    return english if found == key else found


def _month_name(month: int, locale: str | None) -> str:
    """The month's name. Falls back to English, never to a bare key."""
    english = MONTHS[month - 1]
    key = f"month.{english}"
    found = t(key, locale=locale)
    return english if found == key else found


def format_time(value: dt.time | dt.datetime, locale: str | None = None) -> str:
    """A time of day. A locale on a 24-hour clock simply omits ``{ampm}``."""
    hour24 = value.hour
    hour12 = hour24 % 12 or 12
    return pattern("format.time", locale).format(
        hour24=hour24,
        hour24_pad=f"{hour24:02d}",
        hour12=hour12,
        hour12_pad=f"{hour12:02d}",
        minute=f"{value.minute:02d}",
        second=f"{value.second:02d}",
        ampm=t("AM" if hour24 < 12 else "PM", locale=locale),
    )


def format_datetime(value: dt.datetime, locale: str | None = None) -> str:
    """A date and time together, laid out per the locale's ``format.datetime``."""
    return pattern("format.datetime", locale).format(
        date=format_date(value.date(), locale),
        time=format_time(value, locale),
    )


def format_degrees(longitude: float, locale: str | None = None) -> str:
    """Degrees and arcminutes *within a sign* (0–30°), the notation reports use."""
    within = longitude % 30
    deg = int(within)
    minute = int(round((within - deg) * 60))
    if minute == 60:  # rounding can carry
        deg, minute = deg + 1, 0
    return pattern("format.degrees", locale).format(deg=deg, min=minute)


def format_number(value: float, locale: str | None = None, decimals: int = 2) -> str:
    """A decimal number. Several locales write ``3,14`` where English writes ``3.14``."""
    text = f"{value:.{decimals}f}"
    sep = pattern("format.decimal_sep", locale)
    return text.replace(".", sep) if sep != "." else text
