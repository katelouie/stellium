"""Is the notables database internally honest?

These are data tests, not code tests. The YAML in `stellium/data/notables/` ships in
the wheel and is what `ChartBuilder.from_notable()` computes from, so a wrong field
there is a wrong chart for every user — and unlike a code bug it will never raise.

Four things went wrong at once, and each has a test here now:

**The calendar.** Historical records are cited in the calendar of their day. Lilly's
birth is "1 May 1602" in Gadbury, in his own letter to Ashmole, and in AstroDatabank
— and all three mean the *Julian* 1 May. Fed to an ephemeris as Gregorian it computes
a chart ten days early: Lilly's Moon came out in **Virgo** instead of Capricorn. Some
records had been converted by whoever entered them and some had not, and **no field
said which**, so you could not tell by looking and neither could the library.

**Duplicate keys.** PyYAML silently keeps the *last* of a repeated key. Two records
carried two `calendar:` keys and nothing anywhere complained.

**Circular notes.** `astrological_notes` are only a check if they come from the
*source*. Leonardo's were computed from our own (wrong, off-by-one) date, so they
corroborated the error instead of catching it — his stored 23 April is a **Friday**,
while the family diary that is his only source says *"born April 15, Saturday"*. The
correct reading, 15 April Old Style = 24 April Gregorian, is a Saturday.

**Silent defaults.** "Absent calendar means Gregorian" is right for the ~180 modern
records and a coin-flip for a 17th-century one. So it is required to be explicit
exactly where it is dangerous, rather than inherited.
"""

import re
from collections import Counter
from pathlib import Path

import pytest
import yaml

from stellium.utils.time import GREGORIAN_ADOPTION_BACKSTOP

pytestmark = pytest.mark.slow

NOTABLES = Path(__file__).parent.parent / "src" / "stellium" / "data" / "notables"
YAML_FILES = sorted(NOTABLES.rglob("*.yaml"))

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

VALID_CALENDARS = {"julian", "gregorian"}


def _records():
    for path in YAML_FILES:
        for record in yaml.safe_load(path.read_text()) or []:
            yield path, record


def test_the_yaml_files_load_and_are_not_empty():
    assert YAML_FILES, f"no notable YAML found under {NOTABLES}"
    assert sum(1 for _ in _records()) > 100


def test_no_record_repeats_a_key():
    """PyYAML keeps the last of a duplicated key and says nothing.

    Two records carried two `calendar:` keys. `yaml.safe_load` cannot see this — by
    the time it returns, one of them is simply gone — so the check has to read the
    raw text.
    """
    offenders = []
    for path in YAML_FILES:
        chunks = re.split(r"^- (?=name:)", path.read_text(), flags=re.M)[1:]
        for chunk in chunks:
            keys = re.findall(r"^  ([a-z_]+):", chunk, flags=re.M)
            who = re.match(r"name: (.+)", chunk).group(1).strip()
            for key, count in Counter(keys).items():
                if count > 1:
                    offenders.append(f"{path.name}: {who} has {count}x '{key}'")
    assert not offenders, (
        "duplicate keys (PyYAML silently keeps the last):\n  " + "\n  ".join(offenders)
    )


def test_calendar_values_are_known():
    """`calendar: julian_original` shipped for months. It parses, and means nothing."""
    offenders = [
        f"{path.name}: {r['name']} -> calendar: {r['calendar']!r}"
        for path, r in _records()
        if r.get("calendar") is not None and r["calendar"] not in VALID_CALENDARS
    ]
    assert not offenders, (
        f"calendar must be one of {sorted(VALID_CALENDARS)}:\n  "
        + "\n  ".join(offenders)
    )


def test_early_births_must_declare_their_calendar():
    """The default must not be allowed to guess where guessing is dangerous.

    Britain kept the Julian calendar until 1752, Catholic Europe until 1582, Russia
    until 1918 — so "which calendar is this?" is a property of the *record*, not of
    the year, and cannot be inferred. Absent means Gregorian, which is correct for the
    modern records and a coin flip for these. So these must say.
    """
    silent = [
        f"{path.name}: {r['name']} ({r['year']})"
        for path, r in _records()
        if r.get("year") is not None
        and r["year"] < GREGORIAN_ADOPTION_BACKSTOP
        and r.get("calendar") is None
    ]
    assert not silent, (
        f"born before {GREGORIAN_ADOPTION_BACKSTOP} and does not say which calendar "
        f"the date is in — add `calendar: julian` or `calendar: gregorian`:\n  "
        + "\n  ".join(silent)
    )


def test_every_record_computes_the_chart_its_own_notes_describe():
    """The database ships its own answer key. Hold it to it.

    `astrological_notes` records the positions the *source* gives. If our computed Sun
    disagrees with the note, then either the date, the time, the location or the
    calendar is wrong — this is the test that caught the Julian dates, because Lilly's
    note said Sun 19 Taurus and we were computing 10 Taurus.

    A caveat that is the whole lesson of Leonardo: this only works when the note comes
    from the **source**. His was computed from our own incorrect date, so it agreed
    with the error and hid it. A note that is regenerated from our own chart is not
    evidence of anything.
    """
    from stellium import ChartBuilder

    disagreements = []
    for _path, r in _records():
        note = r.get("astrological_notes") or ""
        if r.get("event_type") != "birth":
            continue
        match = re.search(r"Sun\s+(\d+)\s*°?\s*(\w+)", note)
        if not match or match.group(2) not in SIGNS:
            continue  # no usable claim to check against

        chart = ChartBuilder.from_notable(r["name"]).calculate()
        sun = chart.get_object("Sun").longitude
        sign, degree = SIGNS[int(sun // 30)], sun % 30
        claim_degree, claim_sign = int(match.group(1)), match.group(2)

        # Generous: the note is rounded to the degree, and an unknown-time record is
        # noon-defaulted, which moves the Sun by up to half a degree.
        if sign != claim_sign or abs(degree - claim_degree) > 2.5:
            disagreements.append(
                f"{r['name']} ({r['year']}): note says Sun {claim_degree} {claim_sign}, "
                f"we compute {degree:.1f} {sign}"
            )

    assert not disagreements, (
        "records whose computed chart contradicts their own astrological_notes — the "
        "date, time, location or calendar is wrong:\n  " + "\n  ".join(disagreements)
    )
