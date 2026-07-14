"""Old Style dates: the Julian calendar conversion.

Every case here is a real record from the notables database, checked against an
external source rather than against our own output — the whole reason the bug existed
is that the data was corroborating itself.
"""

import datetime as dt

import pytest

from stellium.utils.time import julian_to_gregorian, to_gregorian


@pytest.mark.parametrize(
    "old_style,new_style,why",
    [
        (
            dt.datetime(1602, 5, 1, 2, 0),
            dt.datetime(1602, 5, 11, 2, 0),
            "William Lilly. AstroDatabank: 1 May 1602 Jul. = 11 May 1602 greg.",
        ),
        (
            dt.datetime(1571, 12, 27, 14, 30),
            dt.datetime(1572, 1, 6, 14, 30),
            "Kepler. The conversion rolls the YEAR — 1571 becomes 1572.",
        ),
        (
            dt.datetime(1642, 12, 25, 1, 38),
            dt.datetime(1643, 1, 4, 1, 38),
            "Newton, born Christmas Day 1642 (OS) = 4 January 1643.",
        ),
        (
            dt.datetime(1452, 4, 15, 21, 40),
            dt.datetime(1452, 4, 24, 21, 40),
            "Leonardo. The 1400s offset is NINE days, not ten.",
        ),
        (
            dt.datetime(1207, 9, 30, 12, 0),
            dt.datetime(1207, 10, 7, 12, 0),
            "Rumi. The 1200s offset is SEVEN days — it is not a constant.",
        ),
    ],
)
def test_julian_to_gregorian(old_style, new_style, why):
    assert julian_to_gregorian(old_style) == new_style, why


def test_the_offset_is_not_a_constant_ten_days():
    """The single most likely way to get this wrong is `+ timedelta(days=10)`."""
    offsets = {
        century: (
            julian_to_gregorian(dt.datetime(century, 6, 1)) - dt.datetime(century, 6, 1)
        ).days
        for century in (1207, 1452, 1602, 1729)
    }
    assert offsets == {1207: 7, 1452: 9, 1602: 10, 1729: 11}


def test_the_clock_time_is_not_disturbed():
    """Only the date shifts. Rebuilding the time from revjul's float hour would put
    rounding into a value that was exact."""
    converted = julian_to_gregorian(dt.datetime(1602, 5, 1, 2, 4, 33, 123456))
    assert (
        converted.hour,
        converted.minute,
        converted.second,
        converted.microsecond,
    ) == (
        2,
        4,
        33,
        123456,
    )


def test_leonardo_lands_on_the_saturday_his_source_names():
    """His only source is a family diary: 'born April 15, Saturday, three hours into
    the night.' The database stored 23 April, which is a FRIDAY — and his
    astrological_notes had been computed from that wrong date, so they agreed with it.
    An independent fact is the only thing that could catch this."""
    converted = julian_to_gregorian(dt.datetime(1452, 4, 15, 21, 40))
    assert converted.strftime("%A") == "Saturday"
    assert dt.date(1452, 4, 23).strftime("%A") == "Friday"  # what we had


def test_gregorian_and_none_pass_through_untouched():
    stamp = dt.datetime(1990, 6, 1, 9, 30)
    assert to_gregorian(stamp, None) == stamp
    assert to_gregorian(stamp, "gregorian") == stamp


def test_an_unknown_calendar_is_refused_rather_than_guessed():
    """`calendar: julian_original` shipped in the data for months. It parsed fine and
    meant nothing, so it was silently treated as Gregorian."""
    with pytest.raises(ValueError, match="unknown calendar"):
        to_gregorian(dt.datetime(1990, 6, 1), "julian_original")
