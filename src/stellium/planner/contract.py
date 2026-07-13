"""The planner's JSON contract — Python emits data, Typst decides how it looks.

This mirrors ``presentation/typst_render.build_report_data``: everything visual
(colour, type, layout) lives in the ``.typ`` design system, and Python's only job
is to hand over structured data plus a theme name.

The front matter is assembled here, and its *order* is the design: a planner is
consulted, not read, so it runs "this year → your chart → how to read it" rather
than the natal report's "identity → detail". Most of it is expressible in the
report's existing section kinds (tables, key-value grids, planet tables, embedded
SVGs); only ``year_overview`` and ``glyph_key`` are planner-native.
"""

from __future__ import annotations

import calendar
from datetime import date
from typing import Any

from stellium.planner.almanac import YearAlmanac
from stellium.planner.events import DailyEvent

# Typst paper names for the sizes the builder offers.
PAPER_SIZES: dict[str, str] = {
    "a4": "a4",
    "a5": "a5",
    "letter": "us-letter",
    "half-letter": "us-statement",
}

_ORDINAL_SUFFIX = {1: "st", 2: "nd", 3: "rd"}


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = _ORDINAL_SUFFIX.get(n % 10, "th")
    return f"{n}{suffix}"


def _fmt_date(d: date) -> str:
    return d.strftime("%b %-d")


def _fmt_time(dt: Any, fmt: str = "12h") -> str:
    """Compact event time. Calendar cells are tiny, so 12-hour loses the 'm'.

    '2:49p' (12h) or '14:49' (24h).
    """
    if fmt == "24h":
        return dt.strftime("%H:%M")
    stamp = dt.strftime("%-I:%M%p").lower()
    return stamp.replace("am", "a").replace("pm", "p")


# ---------------------------------------------------------------------------
# front matter
# ---------------------------------------------------------------------------


def _year_at_a_glance(almanac: YearAlmanac) -> dict[str, Any]:
    """The dashboard: the single page you flip back to all year.

    Everything that defines *this year* — who rules it, when the retrogrades run,
    where the eclipses land in your houses, which slow transits shape it. All of
    this existed already, but only ever as scattered lines on daily pages.
    """
    lord_where = ""
    if almanac.lord_natal_sign:
        lord_where = f"{almanac.lord_natal_sign}"
        if almanac.lord_natal_house:
            lord_where += f", {_ordinal(almanac.lord_natal_house)} house"

    pairs = [
        [
            "Lord of the Year",
            almanac.lord_of_year + (f"  ·  natal {lord_where}" if lord_where else ""),
        ],
        [
            "Profection",
            f"{_ordinal(almanac.profected_house)} house "
            f"({almanac.profected_sign})  ·  age {almanac.age}",
        ],
    ]
    if almanac.solar_return:
        pairs.append(
            ["Solar Return", almanac.solar_return.strftime("%B %-d, %Y at %-I:%M %p")]
        )
    for period in almanac.zr_periods:
        if period.level == 1:
            pairs.append(["Releasing (L1)", f"{period.sign}, ruled by {period.ruler}"])

    # "Overview", not "The Year" — the page title already names the span, and the
    # span is not necessarily a year.
    sections: list[dict[str, Any]] = [
        {"kind": "key_value", "title": "Overview", "pairs": pairs}
    ]

    if almanac.eclipses:
        sections.append(
            {
                "kind": "table",
                "title": "Eclipses — and where they fall for you",
                "headers": ["Date", "Type", "Degree", "Your House"],
                "rows": [
                    [
                        _fmt_date(e.date),
                        f"{e.detail.title()} {e.eclipse_type.title()}".strip(),
                        f"{e.degree:.0f}° {e.sign}",
                        _ordinal(e.natal_house) if e.natal_house else "—",
                    ]
                    for e in almanac.eclipses
                ],
            }
        )

    if almanac.retrogrades:
        rows = []
        for r in almanac.retrogrades:
            begins = _fmt_date(r.station_retrograde) if r.station_retrograde else "—"
            ends = _fmt_date(r.station_direct) if r.station_direct else "—"
            note = ""
            if r.starts_before_year:
                note = "began last year"
            elif r.ends_after_year:
                note = "runs into next year"
            rows.append([r.planet, begins, ends, note])

        sections.append(
            {
                "kind": "table",
                "title": "Retrogrades",
                "headers": ["Planet", "Stations Rx", "Stations Direct", ""],
                "rows": rows,
            }
        )

    return {
        "kind": "compound",
        # A planner is not necessarily a year (see _period_label), so neither is its
        # dashboard. The old hardcoding also produced "March 2026 – March 2026" for a
        # single-month planner.
        "title": f"{_period_label(almanac.start, almanac.end)} at a Glance",
        "descriptor": _span_descriptor(almanac.start, almanac.end),
        "new_page": True,
        "sections": sections,
    }


def _year_transits(almanac: YearAlmanac) -> dict[str, Any] | None:
    """The slow transits, on their own page.

    Long enough (a couple of dozen exact hits) that tacking it onto the dashboard
    just orphans its heading at the foot of the page.
    """
    if not almanac.transits:
        return None

    return {
        "kind": "table",
        "title": f"Transits That Shape the {_span_noun(almanac.start, almanac.end)}",
        "descriptor": "The slow movers, and when they land",
        "new_page": True,
        "headers": ["Date", "Transit", "Aspect", "Natal"],
        "rows": [
            [
                _fmt_date(t.exact.date()),
                t.transit_planet,
                t.aspect_name,
                t.natal_planet,
            ]
            for t in almanac.transits
        ],
    }


def _contacts_glyphs(contacts, limit: int = 8, focus: tuple[str, ...] = ()) -> str:
    """Natal contacts as a compact glyph run: `♂☌♆  ☉□♀  ☽□♀`.

    Spelled out in words this would swamp the page — the whole point of these
    reference tables is that a sky event carries its natal contacts *inline*.

    `focus` names the bodies the event is *about* (the Sun and Moon for a lunation,
    the turning planet for a station) and floats their contacts to the front. Sorted
    by orb alone, the slow outer planets — which sit in aspect for months on end —
    crowd out the very thing the reader opened the page to find.
    """
    from stellium.planner.events import ASPECT_GLYPHS_BY_NAME, PLANET_GLYPHS

    if focus:
        contacts = sorted(
            contacts,
            key=lambda c: (0 if c.transit_planet in focus else 1, c.orb),
        )

    parts = []
    for contact in contacts[:limit]:
        transit = PLANET_GLYPHS.get(contact.transit_planet, contact.transit_planet[:2])
        aspect = ASPECT_GLYPHS_BY_NAME.get(contact.aspect_name, "")
        natal = PLANET_GLYPHS.get(contact.natal_planet, contact.natal_planet[:2])
        parts.append(f"{transit}{aspect}{natal}")

    text = "  ".join(parts)
    if len(contacts) > limit:
        text += f"  +{len(contacts) - limit}"
    return text


def _ingresses_section(almanac: YearAlmanac) -> dict[str, Any] | None:
    """Every sign change in the range — the sky's itinerary."""
    if not almanac.ingresses:
        return None

    return {
        "kind": "table",
        "title": "Planetary Ingresses",
        "descriptor": "When each planet changes sign",
        "new_page": True,
        "headers": ["Date", "Planet", "Enters", ""],
        "rows": [
            [
                _fmt_date(i.date),
                i.planet,
                i.sign,
                "℞" if i.retrograde else "",
            ]
            for i in almanac.ingresses
        ],
    }


def _stations_section(almanac: YearAlmanac) -> dict[str, Any] | None:
    """Stations, with the retrograde shadow and what each one touches in the chart.

    The shadow is what makes a station actionable: the retrograde's real reach is
    from the day the planet first crosses the degree it will station direct at,
    to the day it finally clears the degree it stationed retrograde at.
    """
    if not almanac.stations:
        return None

    rows = []
    for station in almanac.stations:
        shadow = ""
        if station.shadow_enter:
            shadow = f"enters shadow {_fmt_date(station.shadow_enter)}"
        elif station.shadow_exit:
            shadow = f"leaves shadow {_fmt_date(station.shadow_exit)}"

        rows.append(
            [
                _fmt_date(station.date),
                station.planet,
                "℞" if station.direction == "retrograde" else "D",
                f"{station.degree:.0f}° {station.sign}",
                shadow,
                _contacts_glyphs(
                    station.natal_contacts, limit=6, focus=(station.planet,)
                ),
            ]
        )

    return {
        "kind": "table",
        "title": "Stations",
        "descriptor": "Where each planet turns — and what it touches in your chart",
        "new_page": True,
        "headers": ["Date", "Planet", "", "Degree", "Shadow", "Your chart"],
        "rows": rows,
    }


def _lunations_section(almanac: YearAlmanac) -> dict[str, Any] | None:
    """Every new and full Moon, in your houses, with its natal contacts."""
    if not almanac.lunations:
        return None

    rows = []
    for lunation in almanac.lunations:
        label = "New Moon" if lunation.phase == "new" else "Full Moon"
        if lunation.eclipse:
            label = lunation.eclipse.title()

        rows.append(
            [
                _fmt_date(lunation.date),
                label,
                f"{lunation.degree:.0f}° {lunation.sign}",
                _ordinal(lunation.natal_house) if lunation.natal_house else "—",
                _contacts_glyphs(
                    lunation.natal_contacts, limit=6, focus=("Sun", "Moon")
                ),
            ]
        )

    return {
        "kind": "table",
        "title": "Lunations",
        "descriptor": "Each new and full Moon, and where it lands for you",
        "new_page": True,
        "headers": ["Date", "Phase", "Degree", "Your House", "Your chart"],
        "rows": rows,
    }


def _chart_analysis_section(condition) -> dict[str, Any] | None:
    """The traditional condition of the natal chart.

    Who governs the ground each planet stands on — its domicile, exaltation, bound,
    triplicity and decan lords — plus the sect judgement that decides which benefic
    helps most and which malefic hurts most.

    Deliberately stops short of bonification and maltreatment: that is a further
    layer of Hellenistic doctrine Stellium does not model, and inventing it here
    would dress a guess up as a judgement.
    """
    if condition is None or not condition.planets:
        return None

    sect = condition.sect
    pairs = [
        ["Sect", f"{sect.sect.title()} chart  ·  sect light {sect.sect_light}"],
        [
            "Benefics",
            f"{sect.benefic_of_sect} is of the sect  ·  "
            f"{sect.benefic_contrary} is contrary",
        ],
        [
            "Malefics",
            f"{sect.malefic_of_sect} is of the sect  ·  "
            f"{sect.malefic_contrary} is contrary",
        ],
    ]

    # The engine's internal dignity names are not reader-facing.
    pretty = {
        "triplicity_ruler": "triplicity",
        "term": "bound",
        "decan": "decan",
        "domicile": "domicile",
        "exaltation": "exaltation",
        "detriment": "detriment",
        "fall": "fall",
    }

    rows = []
    for p in condition.planets:
        # A planet can be peregrine *and* in detriment — peregrine only means it
        # holds no essential dignity, and detriment is a debility, not a dignity.
        # Printing "peregrine" alone would hide the more telling fact.
        named = [pretty.get(d, d) for d in p.dignities if d != "peregrine"]
        standing = ", ".join(named) if named else "peregrine"

        rows.append(
            [
                p.planet,
                f"{p.degree:.0f}° {p.sign}",
                _ordinal(p.house) if p.house else "—",
                p.domicile_lord or "—",
                p.exaltation_lord or "—",
                p.bound_lord or "—",
                ", ".join(p.triplicity_lords) or "—",
                p.decan_lord or "—",
                f"{standing} ({p.score:+d})",
            ]
        )

    return {
        "kind": "compound",
        "title": "Chart Analysis",
        "descriptor": "Traditional condition",
        "new_page": True,
        "sections": [
            {"kind": "key_value", "title": "Sect", "pairs": pairs},
            {
                "kind": "table",
                "title": "Who rules the ground each planet stands on",
                "headers": [
                    "Planet",
                    "Position",
                    "House",
                    "Domicile",
                    "Exalt",
                    "Bound",
                    "Triplicity",
                    "Decan",
                    "Standing",
                ],
                "rows": rows,
            },
        ],
    }


def _progressed_moon_section(almanac: YearAlmanac) -> dict[str, Any] | None:
    """The progressed Moon's year.

    Secondary progression moves the Moon only ~13° in a year, so it changes sign
    at most once — the dated aspects to natal planets are the payload, not the
    ingress. A full progressed *wheel* would be decorative here; nothing in the
    daily pages cites one.
    """
    pm = almanac.progressed_moon
    if pm is None:
        return None

    where = (
        f"{pm.start_degree:.0f}° {pm.start_sign} → {pm.end_degree:.0f}° {pm.end_sign}"
    )
    if pm.natal_house:
        where += f"  ·  {_ordinal(pm.natal_house)} house"

    pairs = [["Through the year", where]]
    if pm.ingress_date and pm.ingress_sign:
        pairs.append(
            ["Enters a new sign", f"{pm.ingress_sign} on {_fmt_date(pm.ingress_date)}"]
        )
    else:
        pairs.append(
            ["Enters a new sign", "Not this year — a sign takes about 2½ years"]
        )

    sections: list[dict[str, Any]] = [
        {"kind": "key_value", "title": "Position", "pairs": pairs}
    ]

    if pm.aspects:
        sections.append(
            {
                "kind": "table",
                "title": "Aspects to your natal planets",
                "headers": ["Date", "Aspect", "Natal Planet"],
                "rows": [
                    [_fmt_date(a.date), a.aspect_name, a.natal_planet]
                    for a in pm.aspects
                ],
            }
        )

    return {
        "kind": "compound",
        "title": "The Progressed Moon",
        "new_page": False,
        "sections": sections,
    }


def _zr_section(almanac: YearAlmanac, svg: str | None) -> dict[str, Any] | None:
    """Releasing, scoped to the year rather than the lifetime.

    A planner covers twelve months; the lifetime view is the report's job.
    """
    if not almanac.zr_periods and not svg:
        return None

    sections: list[dict[str, Any]] = []
    if svg:
        sections.append({"kind": "svg", "title": "", "svg_content": svg})

    if almanac.zr_periods:
        rows = []
        for period in almanac.zr_periods:
            flags = []
            if period.is_peak:
                flags.append("Peak")
            if period.is_loosing_bond:
                flags.append("Loosing of the Bond")
            rows.append(
                [
                    f"L{period.level}",
                    period.sign,
                    period.ruler,
                    f"{_fmt_date(period.start)} – {_fmt_date(period.end)}",
                    ", ".join(flags),
                ]
            )
        sections.append(
            {
                "kind": "table",
                "title": f"Periods active this {_span_noun(almanac.start, almanac.end).lower()}",
                "headers": ["Level", "Sign", "Ruler", "Runs", ""],
                "rows": rows,
            }
        )

    return {
        "kind": "compound",
        "title": "Zodiacal Releasing",
        "new_page": True,
        "sections": sections,
    }


def _glyph_key(planets: list[str], aspects: list[str]) -> dict[str, Any]:
    """The legend.

    A report spells everything out in prose and never needs one. A planner's daily
    pages are dense glyph shorthand at 5.5pt — without a key they are unreadable
    to anyone but the author.
    """
    from stellium.planner.events import (
        ASPECT_GLYPHS_BY_NAME,
        PLANET_GLYPHS,
        SIGN_GLYPHS,
    )

    signs = [
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

    return {
        "kind": "glyph_key",
        "title": "How to Read This Planner",
        "descriptor": "The daily pages use these glyphs",
        "new_page": True,
        "groups": [
            {
                "title": "Planets",
                "items": [
                    {"glyph": PLANET_GLYPHS.get(p, ""), "label": p} for p in planets
                ],
            },
            {
                "title": "Aspects",
                "items": [
                    {"glyph": ASPECT_GLYPHS_BY_NAME.get(a, ""), "label": a}
                    for a in aspects
                ],
            },
            {
                "title": "Signs",
                "items": [{"glyph": SIGN_GLYPHS.get(s, ""), "label": s} for s in signs],
            },
            {
                "title": "Notation",
                "items": [
                    {"glyph": "(n)", "label": "Aspect to a natal planet"},
                    {"glyph": "→", "label": "Planet enters a new sign"},
                    {"glyph": "℞", "label": "Stations retrograde"},
                    {"glyph": "D", "label": "Stations direct"},
                    {"glyph": "VOC", "label": "Moon void of course"},
                ],
            },
            # The colour code is the fastest thing on the daily pages, so it has to
            # be the most clearly explained thing in the key.
            {
                "title": "Colour",
                "swatches": True,
                "items": [
                    {"class": "natal", "label": "Touches your natal chart"},
                    {"class": "notable", "label": "Eclipse, station or lunation"},
                    {"class": "mundane", "label": "Happening in the sky"},
                    {"class": "lunar", "label": "The Moon's comings and goings"},
                ],
            },
        ],
    }


# ---------------------------------------------------------------------------
# the calendar
# ---------------------------------------------------------------------------


def _month_calendar(
    year: int,
    month: int,
    events_by_date: dict[date, list[DailyEvent]],
    marks: dict[date, str],
    first_weekday: int,
    time_format: str = "12h",
) -> dict[str, Any]:
    """One month as a 7-column grid of day cells."""
    cal = calendar.Calendar(firstweekday=first_weekday)

    weeks: list[list[dict[str, Any]]] = []
    for week in cal.monthdatescalendar(year, month):
        row = []
        for day in week:
            events = events_by_date.get(day, [])
            row.append(
                {
                    "day": day.day,
                    "in_month": day.month == month,
                    "mark": marks.get(day),
                    "events": [
                        {
                            "time": _fmt_time(e.time, time_format),
                            "symbol": e.symbol,
                            "class": e.event_class,
                        }
                        for e in sorted(events)
                    ],
                }
            )
        weeks.append(row)

    return {
        "name": calendar.month_name[month],
        "year": year,
        "weekdays": _weekday_names(first_weekday),
        "weeks": weeks,
    }


def _month_weeks_detail(
    year: int,
    month: int,
    events_by_date: dict[date, list[DailyEvent]],
    first_weekday: int,
    start: date,
    end: date,
    time_format: str = "12h",
) -> list[dict[str, Any]]:
    """The month's weeks as writable day pages."""
    cal = calendar.Calendar(firstweekday=first_weekday)
    pages: list[dict[str, Any]] = []

    for week in cal.monthdatescalendar(year, month):
        # A week belongs to the month that owns most of it; skip weeks whose days
        # all sit outside the planner's range.
        if all(day < start or day > end for day in week):
            continue
        if not any(day.month == month for day in week):
            continue

        days = []
        for day in week:
            events = sorted(events_by_date.get(day, []))
            days.append(
                {
                    "weekday": day.strftime("%A"),
                    "day": day.day,
                    "in_range": start <= day <= end,
                    "events": [
                        {
                            "time": _fmt_time(e.time, time_format),
                            "description": e.description,
                            "class": e.event_class,
                        }
                        for e in events
                    ],
                }
            )

        label = f"{week[0]:%b %-d} – {week[-1]:%b %-d, %Y}"
        pages.append({"label": label, "days": days})

    return pages


def _weekday_names(first_weekday: int) -> list[str]:
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return names[first_weekday:] + names[:first_weekday]


def _weekday_initials(first_weekday: int) -> list[str]:
    names = ["M", "T", "W", "T", "F", "S", "S"]
    return names[first_weekday:] + names[:first_weekday]


def _year_overview(
    start: date,
    end: date,
    marks: dict[date, str],
    first_weekday: int,
) -> dict[str, Any]:
    """Twelve mini-months — the "where am I in the year" anchor.

    Days carrying something big (an eclipse, a station) are discs, so the shape of
    the year is legible at a glance without reading a word.
    """
    cal = calendar.Calendar(firstweekday=first_weekday)
    months: list[dict[str, Any]] = []

    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        weeks = []
        month_marks: dict[str, str] = {}
        for week in cal.monthdatescalendar(cursor.year, cursor.month):
            row = []
            for day in week:
                if day.month != cursor.month:
                    row.append(0)
                    continue
                row.append(day.day)
                if day in marks:
                    month_marks[str(day.day)] = marks[day]
            weeks.append(row)

        months.append(
            {
                "name": calendar.month_abbr[cursor.month],
                "weekday_initials": _weekday_initials(first_weekday),
                "weeks": weeks,
                "marks": month_marks,
            }
        )

        cursor = (
            date(cursor.year + 1, 1, 1)
            if cursor.month == 12
            else date(cursor.year, cursor.month + 1, 1)
        )

    return {
        "kind": "year_overview",
        # "Calendar", not "{period} at a Glance" — that title now belongs to the
        # dashboard, and two pages called the same thing is worse than a plain name.
        "title": "Calendar",
        "descriptor": "Highlighted days carry an eclipse or a station",
        "new_page": True,
        "months": months,
    }


def build_marks(almanac: YearAlmanac) -> dict[date, str]:
    """Days worth flagging on a calendar: eclipses and stations."""
    marks: dict[date, str] = {}
    for retro in almanac.retrogrades:
        if retro.station_retrograde:
            marks[retro.station_retrograde] = "station"
        if retro.station_direct:
            marks[retro.station_direct] = "station"
    # Eclipses win over stations when they collide.
    for eclipse in almanac.eclipses:
        marks[eclipse.date] = "eclipse"
    return marks


# ---------------------------------------------------------------------------
# the whole contract
# ---------------------------------------------------------------------------


def build_planner_data(
    natal_chart: Any,
    almanac: YearAlmanac,
    events_by_date: dict[date, list[DailyEvent]],
    *,
    name: str,
    theme: str,
    page_size: str = "letter",
    binding_margin: float = 0.0,
    week_starts_on: str = "sunday",
    weekly_starts_on: str | None = None,
    time_format: str = "12h",
    location_label: str | None = None,
    include_natal: bool = True,
    svgs: dict[str, str] | None = None,
    transit_planets: list[str] | None = None,
    condition: Any = None,
) -> dict[str, Any]:
    """Serialise a planner to the JSON contract the Typst design system renders.

    Args:
        natal_chart: The native's natal chart
        almanac: The year's reference data
        events_by_date: Daily events, keyed by local date
        name: Title for the planner (the native's name)
        theme: Design-system theme name
        page_size: One of PAPER_SIZES
        binding_margin: Extra inner margin in inches, for a bound planner
        week_starts_on: "sunday" or "monday"
        svgs: Rendered SVG markup, keyed by slot ("natal", "ephemeris",
            "solar_return", "profections", "zr")
        transit_planets: Planets appearing on the daily pages, for the legend

    Returns:
        The JSON-serialisable contract
    """
    from stellium.presentation.sections.core import PlanetPositionSection

    svgs = svgs or {}
    # calendar.Calendar: Monday=0 … Sunday=6
    first_weekday = 6 if week_starts_on.lower() == "sunday" else 0
    weekly_first = weekly_starts_on or week_starts_on
    weekly_weekday = 6 if weekly_first.lower() == "sunday" else 0
    marks = build_marks(almanac)

    start, end = almanac.start, almanac.end

    front: list[dict[str, Any]] = [_year_at_a_glance(almanac)]

    transits_page = _year_transits(almanac)
    if transits_page:
        front.append(transits_page)

    front.append(_year_overview(start, end, marks, first_weekday))

    # The sky's own calendar — each event annotated with what it touches in you.
    for section in (
        _lunations_section(almanac),
        _stations_section(almanac),
        _ingresses_section(almanac),
    ):
        if section:
            front.append(section)

    # The natal chart as a *lookup*, not a portrait: the positions table leads,
    # because that is what the daily pages send you here to find. `.without_natal_chart()`
    # drops the whole reference — table AND wheel — not just the drawing.
    natal_sections: list[dict[str, Any]] = []
    positions = (
        PlanetPositionSection().generate_data(natal_chart) if include_natal else {}
    )
    if positions.get("planets"):
        natal_sections.append(
            {
                "kind": "planet_positions",
                "title": "Your placements",
                "planets": positions["planets"],
                "house_headers": [str(h) for h in positions.get("house_headers", [])],
                "show_speed": False,
            }
        )
    if natal_sections:
        front.append(
            {
                "kind": "compound",
                "title": "Your Natal Chart",
                "descriptor": "What the daily pages refer to",
                "new_page": True,
                "sections": natal_sections,
            }
        )

    # The wheel gets its own page. Bolted onto the placements table it just
    # orphans the last planet row across a page break.
    if svgs.get("natal"):
        front.append(
            {
                "kind": "svg",
                "title": "Your Chart Wheel",
                "new_page": True,
                "svg_content": svgs["natal"],
            }
        )

    analysis = _chart_analysis_section(condition)
    if analysis:
        front.append(analysis)

    if svgs.get("ephemeris"):
        front.append(
            {
                "kind": "svg",
                # Span-agnostic titles: the running header already says which
                # months this planner covers, and it may not be a year.
                "title": "The Slow Transits",
                "descriptor": "Where the slow movers travel",
                "new_page": True,
                "svg_content": svgs["ephemeris"],
            }
        )

    year_charts: list[dict[str, Any]] = []
    for slot, label in (
        ("solar_return", "Solar Return"),
        ("profections", "Profections"),
    ):
        if svgs.get(slot):
            year_charts.append(
                {"kind": "svg", "title": label, "svg_content": svgs[slot]}
            )
    if year_charts:
        front.append(
            {
                "kind": "compound",
                "title": "Your Charts",
                "new_page": True,
                "sections": year_charts,
            }
        )

    progressed = _progressed_moon_section(almanac)
    if progressed:
        progressed["new_page"] = True
        front.append(progressed)

    zr = _zr_section(almanac, svgs.get("zr"))
    if zr:
        front.append(zr)

    front.append(
        _glyph_key(
            planets=transit_planets or ["Sun", "Moon", "Mercury", "Venus", "Mars"],
            aspects=["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
        )
    )

    # --- the months ---------------------------------------------------------
    months: list[dict[str, Any]] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        month = _month_calendar(
            cursor.year,
            cursor.month,
            events_by_date,
            marks,
            first_weekday,
            time_format,
        )
        month["weeks_detail"] = _month_weeks_detail(
            cursor.year,
            cursor.month,
            events_by_date,
            weekly_weekday,
            start,
            end,
            time_format,
        )
        months.append(month)
        cursor = (
            date(cursor.year + 1, 1, 1)
            if cursor.month == 12
            else date(cursor.year, cursor.month + 1, 1)
        )

    birth = natal_chart.datetime.local_datetime or natal_chart.datetime.utc_datetime
    metadata = [
        birth.strftime("%B %-d, %Y"),
        getattr(natal_chart.location, "name", "") or "",
    ]
    # Times are local to wherever the planner is *used*, which is not necessarily
    # where the native was born. Say so, the way a good almanac does.
    if location_label:
        metadata.append(f"All times local to {location_label}")

    period = _period_label(start, end)

    return {
        "meta": {
            "name": name,
            "year": start.year,
            "period": period,
            "metadata": [m for m in metadata if m],
            "page_size": PAPER_SIZES.get(page_size.lower(), "us-letter"),
            "binding_margin": float(binding_margin),
            "running_left": name,
            "running_right": period,
            "footer": f"{name} · {period}",
            "theme": theme,
        },
        "front": front,
        "months": months,
    }


def _period_label(start: date, end: date) -> str:
    """What to call the planner's span.

    A planner does not have to be a calendar year — Honeycomb's run Sep→Aug — so a
    bare "2026" would be a lie for any range that crosses a New Year.
    """
    if start.month == 1 and end.month == 12 and start.year == end.year:
        return str(start.year)
    if start.year == end.year:
        if start.month == end.month:
            return f"{start:%B %Y}"  # a single month is not a "Jan–Jan" range
        return f"{start:%b}–{end:%b} {start.year}"
    return f"{start:%b %Y} – {end:%b %Y}"


def _span_descriptor(start: date, end: date) -> str:
    """The exact days the planner covers, spelled out under its title.

    The title says what to *call* the span; this says where it actually begins and
    ends — which is the thing you want when the planner is a custom range.
    """
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.day} – {end.day} {start:%B %Y}"
    if start.year == end.year:
        return f"{start.day} {start:%B} – {end.day} {end:%B %Y}"
    return f"{start.day} {start:%B %Y} – {end.day} {end:%B %Y}"


def _span_noun(start: date, end: date) -> str:
    """What to call the span in running prose: "the Year" or "the Period".

    A Sep→Aug planner is still a year, so this goes by length rather than by whether
    the range happens to sit inside one calendar year. Only say "Year" when it is
    one — "Transits That Shape the Period" is stiff, but it beats lying.
    """
    return "Year" if (end - start).days >= 300 else "Period"
