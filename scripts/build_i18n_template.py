"""Generate the translator's template locale: every string the library can localize.

A new language starts here. Copy the generated ``_TEMPLATE.json`` to
``locales/<code>/strings.json``, translate the values, drop the groups you don't need.
The values are the **English source text** — what you translate *from*.

Four tiers, and the file says which is which in its metadata:

- **catalog** — the closed vocabulary, generated from the registries, so it is always
  complete and current (adding a body to ``CELESTIAL_REGISTRY`` adds a line here).
- **extended** — astrology vocabulary the report/chart/planner don't all emit *yet*, but
  that a locale will want for fuller coverage: aspect patterns, planetary conditions,
  chart types, house topics, Vedic nakshatras, Chinese BaZi pillars, and so on. These
  are namespaced (``pattern.*``, ``condition.*``, ``heavenly_stem.*``) so they never
  collide with anything, and they are harmless if unused.
- **message** — the report/UI strings the renderers look up by English text, plus the
  templates with ``{slots}``.
- **format** — date/number/degree patterns.

Regenerate:  python scripts/build_i18n_template.py
"""

from __future__ import annotations

import json
from pathlib import Path

from stellium.i18n.catalog import build_catalog
from stellium.i18n.formats import DEFAULT_PATTERNS

OUT = Path(__file__).parent.parent / "src/stellium/i18n/locales/_TEMPLATE.json"

# The catalog namespaces (12 of them) are generated. Everything below is CURATED
# forward-looking vocabulary — grouped, English-keyed, translate the values.

# Aspect configurations the pattern analyzer can name.
PATTERNS = [
    "Stellium",
    "Grand Trine",
    "Minor Grand Trine",
    "T-Square",
    "Grand Cross",
    "Grand Sextile",
    "Yod",
    "Kite",
    "Mystic Rectangle",
    "Cradle",
    "Wedge",
    "Thor's Hammer",
    "Rectangle",
    "Star of David",
    "Hourglass",
]

# Accidental dignities and planetary conditions (traditional astrology).
CONDITIONS = [
    "Combust",
    "Cazimi",
    "Under the Beams",
    "Free of the Sun",
    "Oriental",
    "Occidental",
    "Besieged",
    "Feral",
    "Void of Course",
    "Mutual Reception",
    "Reception",
    "In Sect",
    "Out of Sect",
    "Halb",
    "Hayz",
    "Angular",
    "Succedent",
    "Cadent",
    "Swift",
    "Slow",
    "Increasing in Light",
    "Decreasing in Light",
    "Rising",
    "Setting",
    "Culminating",
]

CHART_TYPES = [
    "Natal",
    "Transit",
    "Progressed",
    "Secondary Progression",
    "Solar Arc Direction",
    "Primary Direction",
    "Solar Return",
    "Lunar Return",
    "Planetary Return",
    "Synastry",
    "Composite",
    "Davison",
    "Draconic",
    "Harmonic",
    "Electional",
    "Horary",
    "Event",
    "Relocated",
    "Mundane",
]

# The traditional topic of each house.
HOUSE_TOPICS = {
    "1": "Self & Identity",
    "2": "Money & Values",
    "3": "Communication & Siblings",
    "4": "Home & Roots",
    "5": "Creativity & Pleasure",
    "6": "Work & Health",
    "7": "Partnership",
    "8": "Death & Transformation",
    "9": "Philosophy & Travel",
    "10": "Career & Reputation",
    "11": "Friends & Hopes",
    "12": "Solitude & Undoing",
}

DIRECTIONS = {
    "North": "North",
    "South": "South",
    "East": "East",
    "West": "West",
    "N": "N",
    "S": "S",
    "E": "E",
    "W": "W",
    "Northeast": "Northeast",
    "Northwest": "Northwest",
    "Southeast": "Southeast",
    "Southwest": "Southwest",
}

TIME_UNITS = [
    "year",
    "years",
    "month",
    "months",
    "week",
    "weeks",
    "day",
    "days",
    "hour",
    "hours",
    "minute",
    "minutes",
    "second",
    "seconds",
]

POLARITY = ["Positive", "Negative", "Masculine", "Feminine", "Diurnal", "Nocturnal"]

# Calendar names. format_date already looks these up as month.<English>; a comprehensive
# template must include them or dates render with English month names.
MONTHS = [
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
]
WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
# Meridiem markers, looked up by format_time.
MERIDIEM = ["AM", "PM"]

# The 27 Vedic lunar mansions.
NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

# Chinese Four Pillars (BaZi). The chinese/ subsystem is currently English-only.
HEAVENLY_STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
EARTHLY_BRANCHES = [
    "Zi",
    "Chou",
    "Yin",
    "Mao",
    "Chen",
    "Si",
    "Wu",
    "Wei",
    "Shen",
    "You",
    "Xu",
    "Hai",
]
ZODIAC_ANIMALS = [
    "Rat",
    "Ox",
    "Tiger",
    "Rabbit",
    "Dragon",
    "Snake",
    "Horse",
    "Goat",
    "Monkey",
    "Rooster",
    "Dog",
    "Pig",
]
WUXING = ["Wood", "Fire", "Earth", "Metal", "Water"]

# Report / UI strings the renderers look up by English text. The live ones are pulled
# from the zh_CN locale (proven in use); these are additional labels a fuller report
# wants. Section names, column headers, key-value labels, empty states, common words.
EXTRA_MESSAGES = [
    # section titles not yet in the live set
    "Synastry",
    "Composite Chart",
    "Progressed Chart",
    "Transits",
    "Secondary Progressions",
    "Solar Arc Directions",
    "Solar Return",
    "Lunar Return",
    "Chart Shape",
    "Chart Patterns",
    "Element Balance",
    "Modality Balance",
    "Hemisphere Emphasis",
    "Planetary Sect",
    "Temperament",
    "Almuten Figuris",
    "Lunar Nodes",
    "Retrograde Planets",
    "Void of Course Moon",
    "Antiscia",
    "Declinations",
    "Parallels",
    "Fixed Stars",
    "Firdaria",
    "Time Lords",
    "Dashas",
    "Primary Directions",
    "Rectification",
    # column headers / labels
    "Object",
    "Almuten",
    "Score",
    "Total",
    "Dignity",
    "Debility",
    "Condition",
    "Rulership",
    "Longitude",
    "Latitude",
    "Declination",
    "Right Ascension",
    "Retrograde",
    "Combustion",
    "Polarity",
    "Triplicity",
    "Term",
    "Face",
    "Decan",
    "Dispositor",
    "Final Dispositor",
    "Ruler",
    "Almuten of the Chart",
    "Nakshatra",
    "Pada",
    "Pillar",
    "Stem",
    "Branch",
    "Hidden Stems",
    # values / common words
    "None",
    "N/A",
    "True",
    "False",
    "Male",
    "Female",
    "Other",
    "Exact",
    "Separating",
    "Applying",
    "Diurnal",
    "Nocturnal",
    "Day Chart",
    "Night Chart",
    # empty states
    "No fixed star conjunctions in this chart.",
    "No midpoints found.",
    "No retrograde planets in this chart.",
    "No data available.",
    "Not calculated.",
    # templates with slots
    "House {number}",
    "Age {age}",
    "{planet} Return",
    "{degrees} {sign}",
    "{planet} in {sign}",
    "{planet} in House {number}",
    "{planet} is {condition}",
    "Lord of the {ordinal} Year",
    "{value}°{hemisphere}",
]


def _catalog_groups() -> dict[str, dict[str, str]]:
    groups: dict[str, dict[str, str]] = {}
    for key, english in build_catalog().items():
        ns, rest = key.split(".", 1)
        groups.setdefault(ns, {})[rest] = english
    return groups


def _identity(names) -> dict[str, str]:
    """A group whose English value equals its key (the source text to translate)."""
    return {n: n for n in names}


def build_template() -> dict:
    catalog = _catalog_groups()

    extended = {
        "month": _identity(MONTHS),
        "weekday": _identity(WEEKDAYS),
        "pattern": _identity(PATTERNS),
        "condition": _identity(CONDITIONS),
        "chart_type": _identity(CHART_TYPES),
        "house_topic": dict(HOUSE_TOPICS),
        "direction": dict(DIRECTIONS),
        "time_unit": _identity(TIME_UNITS),
        "polarity": _identity(POLARITY),
        "nakshatra": _identity(NAKSHATRAS),
        "wuxing": _identity(WUXING),
        "heavenly_stem": _identity(HEAVENLY_STEMS),
        "earthly_branch": _identity(EARTHLY_BRANCHES),
        "zodiac_animal": _identity(ZODIAC_ANIMALS),
    }

    # Messages: the live English-string keys from zh_CN + the curated extras.
    live = json.loads((OUT.parent / "zh_CN/strings.json").read_text(encoding="utf-8"))
    live_msgs = set(live.get("message", {})) | set(live.get("legacy", {}))
    message = _identity(sorted(live_msgs | set(EXTRA_MESSAGES) | set(MERIDIEM)))

    fmt = {k.split(".", 1)[1]: v for k, v in DEFAULT_PATTERNS.items()}

    doc: dict = {
        "metadata": {
            "language": "?? — ISO code, e.g. 'es', 'fr', 'ja', 'zh_Hant'",
            "status": "template",
            "fallback": "en",
            "notes": (
                "Translation template. Values are the ENGLISH source text; replace them "
                "with your language. Tiers: 'catalog' groups (body, sign, aspect, "
                "house_system, phase, element, modality, motion, aspect_motion, dignity, "
                "sect, star) are the core vocabulary and are generated from the "
                "registries. 'extended' groups (pattern, condition, chart_type, "
                "house_topic, direction, time_unit, polarity, nakshatra, wuxing, "
                "heavenly_stem, earthly_branch, zodiac_animal) are forward-looking and "
                "optional. 'message' holds report/UI strings and {slot} templates; keep "
                "the {slots} intact and you may reorder them. 'format' holds date/number "
                "patterns; {month} is the name, {month_num} the number — pick what your "
                "language needs. Delete any group you do not translate; missing keys "
                "fall back to English. Regenerate: python scripts/build_i18n_template.py"
            ),
            "counts": {},  # filled below
        }
    }

    # catalog namespaces (alpha), then extended (alpha), then message, then format.
    for ns in sorted(catalog):
        doc[ns] = dict(sorted(catalog[ns].items()))
    for ns in sorted(extended):
        doc[ns] = dict(sorted(extended[ns].items()))
    doc["message"] = message
    doc["format"] = dict(sorted(fmt.items()))

    doc["metadata"]["counts"] = {
        "catalog": sum(len(catalog[k]) for k in catalog),
        "extended": sum(len(v) for v in extended.values()),
        "message": len(message),
        "format": len(fmt),
        "total": sum(len(v) for k, v in doc.items() if k != "metadata"),
    }
    return doc


def main() -> int:
    doc = build_template()
    OUT.write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    counts = doc["metadata"]["counts"]
    print(f"wrote {OUT.relative_to(OUT.parent.parent.parent.parent)}")
    for tier, n in counts.items():
        print(f"  {tier:10} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
