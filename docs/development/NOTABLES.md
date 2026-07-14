# The Notables Database

`src/stellium/data/notables/` is the curated birth and event data behind
`ChartBuilder.from_notable("Carl Jung")`. It ships in the wheel, so **a wrong field
here is a wrong chart for every user** — and unlike a code bug it will never raise.
It just quietly produces a different sky.

That is not hypothetical. Until recently the database stored William Lilly's birth as
`1602-05-01`, which is the date every source gives — but every source means the
**Julian** 1 May. Read as Gregorian, his chart came out ten days early, with his Moon
in **Virgo** instead of Capricorn. Nothing complained. See [The calendar
field](#the-calendar-field).

---

## Layout

| Directory | Records | Shape | Read by |
|---|---|---|---|
| `births/` | 190, in 13 files by category | full birth records | `data/registry.py` → `core/native.py::Notable` |
| `events/` | 21, in `historical.yaml` | same schema, `event_type: event` | same |
| `life_events/` | 63 | `name` + `events[]` (dated biography) | `data/biography.py` |
| `temperament/` | 63 | `name` + `temperament[]` (**soft, interpretive**) | `data/biography.py` |

`life_events/` feeds `stellium.rectification` — the dated events a rectification is
tested against. `temperament/` is explicitly non-empirical and warns when you read it.

`notables/generate_index.py` regenerates `INDEX.md`.

---

## The birth/event schema

Every field below is a top-level key of a record in `births/*.yaml` or `events/*.yaml`.
**"Read"** means some `.py` file actually pulls it out; a field nothing reads is
decoration that will rot.

### Identity and time

| Field | Required | Read | Meaning |
|---|---|---|---|
| `name` | ✅ | ✅ | The lookup key for `from_notable()`. Must be unique. |
| `event_type` | ✅ | ✅ | `birth` or `event`. |
| `year` `month` `day` | ✅ | ✅ | The **local** calendar date, *as the sources give it* — see below. |
| `hour` `minute` | — | ✅ | The **local** clock time. Omit entirely when no time is on record; do **not** invent noon (the loader does that, and marks the chart unknown-time). |
| `calendar` | when `year < 1753` | ✅ | `julian` or `gregorian`. See [The calendar field](#the-calendar-field). |

### Place

| Field | Required | Read | Meaning |
|---|---|---|---|
| `latitude` `longitude` | ✅ | ✅ | Decimal degrees. Stored, not geocoded — so a notable never depends on a network call. |
| `location_name` | ✅ | ✅ | Human-readable; display only. |
| `timezone` | ✅ | ✅ | IANA name. **See [Known gaps](#known-gaps): this is wrong for any pre-1880 birth**, which predates standard time. |

### Provenance — the part that matters

| Field | Required | Read | Meaning |
|---|---|---|---|
| `data_quality` | ✅ | ✅ | The **Rodden rating** of the *source*: `AA` (birth record), `A` (quoted from memory), `B` (biography), `C` (no source / rectified), `DD` (conflicting), `X` (no time). |
| `has_reliable_time` | — | ✅ | Whether the *time* may be used. `false` ⇒ the chart is built **unknown-time** (noon, no houses, no angles, no Lots). `null` ⇒ not audited; use the time if one exists. |
| `verified` | ✅ | ✅ | Whether a human has audited the record against its sources. |
| `sources` | ✅ | ✅ | Citations. AstroDatabank URLs where they exist. |
| `verification_notes` | — | ✅ | The audit's reasoning. Free text. |
| `astrological_notes` | — | ✅ | Positions **as the source states them**. This is the answer key — see below. |

> ### `data_quality` and `has_reliable_time` are different axes, and both are needed
>
> Rodden rates **where the datum came from**. `has_reliable_time` rates **whether you
> should build houses out of it**. They come apart, and William Lilly is exactly why:
> his rating is **A** (the time is quoted by the person — his own letter to Ashmole),
> and yet ADB's source notes say *"the time may have been rectified by him,"* with
> Gadbury giving 2:00, Sibly 2:08 and Wangemann 3:00. A good provenance for a number
> he probably back-solved. So: `data_quality: A`, `has_reliable_time: false`.
>
> **Route on `has_reliable_time`, never on `data_quality`.**

### Category

| Field | Required | Read | Meaning |
|---|---|---|---|
| `category` | ✅ | ✅ | One primary category (`scientist`, `artist`, `leader`, `astrologer`, …). Drives `get_by_category()`. |
| `subcategories` | — | ✅ | Free list. |
| `notable_for` | ✅ | ✅ | One paragraph. Display only. |

### Dead fields

| Field | Status |
|---|---|
| `time_system` | **Not read by anything.** Appears on one record (Leonardo, `florentine` — his source gives the time in Florentine hours counted from sunset, already converted). Either wire it up or delete it; a field nothing reads is a claim nobody checks. |

---

## The calendar field

**Store the date the sources give. Declare which calendar that is.**

Historical records are cited in the calendar of their day, and usually do not say so.
Lilly's birth is "1 May 1602" in Gadbury, in Lilly's own letter, and in AstroDatabank
— and all three mean the **Julian** 1 May. Fed to Swiss Ephemeris as a Gregorian date
it computes a chart for a day ten days earlier.

```yaml
- name: William Lilly
  year: 1602
  month: 5
  day: 1          # as every source gives it…
  calendar: julian  # …and this is what they mean
```

`Notable.__init__` converts to Gregorian at load (`utils/time.py::to_gregorian`), so
everything downstream sees a normal date.

**Why store the source's date rather than the converted one?** Because a record whose
date disagrees with every citation in its own `sources:` list is a record nobody can
audit — the next curator checks it against ADB, sees a mismatch, and "fixes" it back.
AstroDatabank itself displays both. So do we.

**Three traps, all of which we hit:**

- **The offset is not ten days.** It is 9 in the 1400s, 7 in the 1200s. Do not write
  `+ timedelta(days=10)`. We use Swiss Ephemeris's own `julday`/`revjul`, so there is
  no calendar arithmetic in this codebase to get wrong.
- **The conversion can roll the year.** Kepler's 27 December **1571** (OS) is 6 January
  **1572**.
- **Adoption is per-country and staggered.** Catholic Europe 1582, Britain and its
  colonies 1752, Russia 1918. So the calendar is a property of the *record*, not of the
  year, and it cannot be inferred — which is why `tests/test_notables_data.py` **requires**
  any birth before 1753 to declare it. Absent means Gregorian, which is right for the
  180 modern records and a coin flip for these.

Valid values are `julian` and `gregorian`. Nothing else. (`calendar: julian_original`
shipped for months, parsed fine, and meant nothing.)

---

## `astrological_notes` is the answer key — so it must come from the source

This field is the reason the Julian bug was findable at all. It records the positions
**the source states**, so it is an independent check on the date, time, place and
calendar all at once:

```yaml
astrological_notes: Sun 19 Taurus, Moon 14 Capricorn, Asc Pisces   # from ADB
```

`test_every_record_computes_the_chart_its_own_notes_describe` computes each chart and
compares. Lilly's note said Sun 19 Taurus while we were computing 10 Taurus — that is
how the bug surfaced.

> ### It is only a check if it comes from outside
>
> Leonardo's note said *Sun 3 Taurus, Moon 3 Pisces*, and our chart agreed exactly —
> because the note had been **computed from our own record** rather than taken from a
> source. The record's date was wrong by a day (23 April; his family diary says *"born
> April 15, **Saturday**"*, and 15 April OS = 24 April Gregorian, a Saturday — while
> our 23 April is a **Friday**). The note corroborated the error instead of catching it.
>
> **Never regenerate `astrological_notes` from a Stellium chart.** A note that agrees
> with us because it was derived from us is not evidence of anything. If you cannot
> source it, leave it out — 81 records currently have no usable note, and an empty
> field is honest where a circular one is not.

---

## Adding or editing a notable

1. **Find the AstroDatabank page.** Put the URL in `sources`.
2. **Copy the date and time exactly as ADB gives them** — including the Old Style date
   if that is what it shows. Set `calendar:` accordingly.
3. **Set `data_quality` from ADB's Rodden rating.** Do not upgrade it because the
   person is famous.
4. **Set `has_reliable_time`** — `false` if the time is rectified, rounded to the hour,
   a noon default, or contradicted by another source, whatever the Rodden rating says.
   If there is no time at all, **omit `hour`/`minute` entirely** rather than writing noon.
5. **Copy `astrological_notes` from the source's own listed positions.** Not from a
   chart you just drew.
6. **Run the tests.** `pytest tests/test_notables_data.py tests/test_calendars.py`

## What the tests guard

`tests/test_notables_data.py`

- every YAML parses, and no record repeats a key — *PyYAML silently keeps the last of a
  duplicate, and two records shipped with two `calendar:` keys*
- `calendar` is `julian` or `gregorian`, never anything else
- any birth before 1753 declares its calendar explicitly
- **every record's computed chart matches its own `astrological_notes`**

`tests/test_calendars.py` — the conversion itself, against externally-sourced dates
(Lilly, Kepler's year-roll, Newton, Leonardo's 9-day offset, Rumi's 7-day offset).

---

## Known gaps

- **Local Mean Time.** `timezone: Europe/London` is an anachronism for anyone born
  before standard time (Britain adopted it in 1880). Lilly's record should be LMT at
  1w16, which is ~5 minutes off GMT — around 1.3° of Ascendant. Every pre-1880 record
  is affected, and the residual disagreement between our Lilly and ADB's is exactly
  this. Tracked in `TODO.md`.
- **81 birth records have no usable `astrological_notes`**, so nothing validates them.
  They are not known-wrong; they are unchecked, which is different and worth closing.
- **`time_system` is read by nothing.**
- **Leonardo's `astrological_notes` are flagged for re-sourcing** — the old ones were
  computed from the wrong date and must be replaced from ADB, not regenerated by us.
