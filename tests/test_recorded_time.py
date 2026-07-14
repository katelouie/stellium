"""`from_notable(..., use_recorded_time=True)` — using a time the audit distrusts.

Some records carry a clock time we will not build houses from. William Lilly is the
type case: AstroDatabank rates his time **A** (quoted by the person — his own letter to
Elias Ashmole) *and* notes that "the time may have been rectified by him," with Gadbury
giving 2:00, Sibly 2:08 and Wangemann 3:00. The record's own audit note is blunter:

    verdict=reject bucket=rectified rating=A:
    Rectified by the astrologer himself; cannot validate a rectifier.

So `has_reliable_time: false`, and by default his chart is unknown-time — noon, no
houses, no angles, no Lots. That default is right.

But as a *hard* block it protected nothing, and that is the argument for this flag.
The determined reader simply wrote:

    Native(datetime(1602, 5, 11, 2, 0), "Diseworth, England")

and got the identical chart with **no caveat anywhere** — the same report, the same
PDF, the same to_dict() as a chart built from a birth certificate. The guard did not
reduce the risk. It pushed the risk somewhere nothing could see it.

So the flag is **provenance-preserving, not provenance-erasing**: you get the chart,
you get a `DataQualityWarning` once, and the chart *carries what it is standing on* in
`metadata["time_provenance"]`, which travels into reports and to_dict(). A chart built
on a rectified time can then never quietly pass for one built on a birth record.
"""

import warnings

import pytest

from stellium import ChartBuilder
from stellium.exceptions import DataQualityWarning

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

# Lilly's is the only distrusted-time record whose chart is published by somebody
# other than us, so it is the only one that can actually falsify the arithmetic.
LILLY_ASC_PER_ADB = (2 + 4 / 60, "Pisces")  # AstroDatabank: 2°04' Pisces


def test_the_default_still_refuses_the_time():
    """The flag must be opt-in. Nothing changes for anybody who does not ask."""
    chart = ChartBuilder.from_notable("William Lilly").calculate()
    assert chart.get_houses() is None
    assert chart.metadata.get("time_unknown") is True
    assert "time_provenance" not in chart.metadata


def test_it_warns_and_says_what_the_chart_is_standing_on():
    with pytest.warns(DataQualityWarning, match="marked it unreliable"):
        ChartBuilder.from_notable("William Lilly", use_recorded_time=True).calculate()


def test_the_chart_reproduces_astrodatabank():
    """The point of the flag is an Ascendant. It had better be the right one.

    This only holds because two other bugs were fixed first: his stored date is Old
    Style (Julian), and his birthplace predates standard time, so the clock showed
    Local Mean Time from Diseworth's longitude, not London's. Get either wrong and
    this flag delivers a confident, wrong Ascendant — which would have been worse than
    refusing to draw one.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DataQualityWarning)
        chart = ChartBuilder.from_notable(
            "William Lilly", use_recorded_time=True
        ).calculate()

    houses = chart.get_houses()
    assert houses is not None
    asc = houses.cusps[0]
    degree, sign = LILLY_ASC_PER_ADB
    assert SIGNS[int(asc // 30)] == sign
    assert abs(asc % 30 - degree) < 0.1


def test_the_caveat_travels_with_the_chart():
    """`metadata` is what reports and to_dict() read, so the caveat cannot be lost at
    the door — which is the entire difference between this and hand-rolling a Native."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DataQualityWarning)
        chart = ChartBuilder.from_notable(
            "William Lilly", use_recorded_time=True
        ).calculate()

    provenance = chart.metadata["time_provenance"]
    assert provenance["source"] == "recorded_time_override"
    assert provenance["recorded_time"] == "02:00"
    assert provenance["has_reliable_time"] is False
    assert provenance["data_quality"] == "A"  # a *good* rating, and still distrusted
    assert "rectif" in provenance["note"].lower()

    # And it must survive export, or a JSON consumer sees a chart with no caveat.
    assert chart.to_dict()["metadata"]["time_provenance"]["source"] == (
        "recorded_time_override"
    )


def test_it_cannot_invent_a_time_that_was_never_written_down():
    """The flag overrides the *audit*, not the absence of data. Three records carry no
    clock time at all; for those there is nothing to override."""
    with pytest.raises(ValueError, match="no clock time on record"):
        ChartBuilder.from_notable("Faye Wong", use_recorded_time=True)


def test_it_is_a_no_op_where_nothing_is_being_overridden():
    """Asking for the recorded time of a record whose time is already trusted must not
    warn, and must not stamp a caveat onto a chart that does not need one."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        chart = ChartBuilder.from_notable(
            "Albert Einstein", use_recorded_time=True
        ).calculate()

    assert not [w for w in caught if issubclass(w.category, DataQualityWarning)]
    assert "time_provenance" not in chart.metadata
    assert chart.get_houses() is not None


def test_the_recorded_time_survives_the_calendar_conversion():
    """Lilly's record stores 1 May 1602 *Julian* at 02:00. Reassembling the moment must
    put the recorded clock time back onto the **converted** (11 May Gregorian) date —
    not onto the raw stored one, which would be ten days early."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DataQualityWarning)
        chart = ChartBuilder.from_notable(
            "William Lilly", use_recorded_time=True
        ).calculate()

    local = chart.datetime.local_datetime
    assert (local.month, local.day) == (5, 11)  # Gregorian, not the stored 1 May
    assert (local.hour, local.minute) == (2, 0)  # and the recorded clock time
