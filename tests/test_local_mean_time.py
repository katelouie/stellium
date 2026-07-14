"""Before standard time, the clock showed Local Mean Time.

Noon was when the Sun crossed *your* meridian, so the offset from UT was a function
of your longitude and nothing else. Britain adopted standard time in 1880, the United
States in 1883, Germany in 1893. Before that there was no zone to belong to.

IANA models the period as an `LMT` offset and pytz will hand it to you — but it is the
LMT of the zone's **reference city**, not of the birthplace, and those are different
numbers. `Europe/London`'s LMT is −1m; Diseworth, where William Lilly was born, is at
1°16′W, whose LMT is −5m04s. Four minutes of clock is about a degree of Ascendant.

For Lilly it was the difference between a rising sign of Pisces and one of Aquarius:

    AstroDatabank publishes    Asc  2°04'  Pisces
    LMT from his longitude     Asc  2°03.6' Pisces
    LMT from the IANA zone     Asc 29°47'  Aquarius   <- what Stellium used to compute

The tests here are pinned to **AstroDatabank**, not to our own output, because a
snapshot of ourselves would have happily ratified the wrong Ascendant for years — and
did. 64 of the 211 dated notables are born before standard time reached their zone.
"""

import datetime as dt
import warnings

import pytest

from stellium import ChartBuilder, Native
from stellium.core.native import build_chart_datetime
from stellium.exceptions import TimeZoneWarning

pytestmark = pytest.mark.slow

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _sign_and_degree(longitude: float) -> tuple[str, float]:
    return SIGNS[int(longitude // 30)], longitude % 30


def test_lilly_reproduces_astrodatabank():
    """The whole case, end to end, against an external source.

    Lilly's is the one pre-standard chart in the database whose positions are published
    by someone other than us, which makes it the only one that can actually falsify our
    arithmetic. All three agree to under an arcminute.
    """
    # 1 May 1602 Old Style = 11 May Gregorian; 02:00 local at Diseworth.
    native = Native(dt.datetime(1602, 5, 11, 2, 0), (52.8333, -1.2667))
    chart = ChartBuilder.from_native(native).calculate()

    asc_sign, asc_degree = _sign_and_degree(chart.get_houses().cusps[0])
    assert asc_sign == "Pisces"  # NOT Aquarius, which is what the zone's LMT gives
    assert abs(asc_degree - (2 + 4 / 60)) < 0.05  # ADB: 2°04'

    sun_sign, sun_degree = _sign_and_degree(chart.get_object("Sun").longitude)
    assert (sun_sign, round(sun_degree)) == ("Taurus", 20)  # ADB: 19°59'

    moon_sign, moon_degree = _sign_and_degree(chart.get_object("Moon").longitude)
    assert moon_sign == "Capricorn"
    assert abs(moon_degree - (14 + 48 / 60)) < 0.1  # ADB: 14°48'


def test_the_offset_comes_from_the_birth_longitude_not_the_zone():
    """Diseworth is 1°16'W: LMT is 5m04s behind UT. Europe/London's LMT is 1m."""
    stamp = build_chart_datetime(
        dt.datetime(1602, 5, 11, 2, 0), "Europe/London", longitude=-1.2667
    )
    # UT = local - longitude/15 hours. West longitude ⇒ UT is *later* than local.
    assert stamp.utc_datetime.hour == 2
    assert stamp.utc_datetime.minute == 5
    assert 3 <= stamp.utc_datetime.second <= 5  # 1.2667/15 h = 5m04s


def test_standard_time_is_left_completely_alone():
    """This must not touch the 147 modern records, or anybody's actual birth chart."""
    stamp = build_chart_datetime(
        dt.datetime(2000, 1, 6, 12, 0), "America/Los_Angeles", longitude=-122.3301
    )
    # PST is UTC-8 exactly — *not* -122.33/15 = -8.155 hours, which is what LMT
    # would give. If this ever reads 20:09 instead of 20:00, LMT has leaked forward.
    assert stamp.utc_datetime.hour == 20
    assert stamp.utc_datetime.minute == 0


@pytest.mark.parametrize(
    "year,timezone,expect_lmt",
    [
        (1602, "Europe/London", True),  # Lilly
        (1875, "Europe/Zurich", True),  # Jung
        (1879, "Europe/Berlin", True),  # Einstein
        (1869, "Asia/Kolkata", True),  # Gandhi
        (1990, "Europe/London", False),
        (2000, "America/Los_Angeles", False),
    ],
)
def test_the_era_is_detected_from_the_zone_not_a_hardcoded_year(
    year, timezone, expect_lmt
):
    """Adoption was staggered — Britain 1880, the US 1883, Germany 1893 — so there is
    no single cutoff year to hardcode. IANA knows the real date for every zone, and
    names the period `LMT`; that is the signal, and it is the only one that is right
    for all of them."""
    east = build_chart_datetime(
        dt.datetime(year, 6, 1, 12, 0), timezone, longitude=10.0
    )
    west = build_chart_datetime(
        dt.datetime(year, 6, 1, 12, 0), timezone, longitude=-10.0
    )
    # Under LMT the longitude decides the offset, so two longitudes must disagree.
    # Under standard time the zone decides, so they must agree.
    differ = east.utc_datetime != west.utc_datetime
    assert differ is expect_lmt


def test_a_pre_standard_time_without_a_longitude_says_so():
    """Falling back on the zone's LMT is wrong by a degree or more of Ascendant. It
    must not be silent — that is how it went unnoticed in the first place."""
    with pytest.warns(TimeZoneWarning, match="Local Mean Time"):
        build_chart_datetime(dt.datetime(1602, 5, 11, 2, 0), "Europe/London")


def test_einstein_keeps_cancer_rising():
    """A guard on the blast radius. LMT moves 64 of 211 notables, and it moved
    Einstein's Mars across a house cusp — but it must not have been so large a change
    that his documented rising sign flips. If this ever fails, the sign convention on
    `longitude` has been inverted."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    assert _sign_and_degree(chart.get_houses().cusps[0])[0] == "Cancer"
