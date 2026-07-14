# The Stellium Astrology Guide

The `examples/` cookbooks teach you the **code**: how to build a chart, swap a
house system, render a dial. This guide teaches you the **astrology**: what a
house *is*, where quadrant systems came from, why anyone argues about Placidus,
and how a working astrologer actually reads the thing.

It's written for two people who are often the same person:

- **The Pythonista** who can call `chart.get_houses()` but isn't sure what
  they're looking at.
- **The beginner astrologer** who knows the difference between a trine and a
  square but wants the history and the theory underneath the keywords.

You don't need to believe anything to read this. The guide explains each
technique *from inside its own tradition's logic* (what a placement means in the
system, how practitioners use it) without either overselling it as literal fate
or undercutting every sentence with a disclaimer. Where a technique is
contested even among astrologers (house systems, outer-planet rulerships,
tropical vs. sidereal), the guide lays out the actual disagreement instead of
pretending there's a consensus.

---

## How each chapter is built

Every chapter follows the same six-beat structure, so you always know where to
find what you need:

1. **The one-line version** — what this is, in a sentence, before any history.
2. **A brief history** — where it came from and how it changed. Astrology's
   techniques are dated artifacts; knowing the era explains the logic.
3. **The theory** — how it works and what it means, explained as a structured
   system with internal rules (the same way you'd explain any framework).
4. **In practice** — how astrologers actually read it, including the modern
   debates and the places reasonable practitioners disagree.
5. **In Stellium** — the code. Every concept mapped to the method that computes
   it, cross-linked to the matching `examples/` cookbook.
6. **Going deeper** — related chapters and further reading (primary sources
   where they exist).

If you only want the code, skip to beat 5 in any chapter. If you only want the
astrology, beats 1–4 stand alone.

### The cast

The guide keeps one chart at the center, so you build familiarity with a single
sky instead of meeting a stranger every chapter, and brings in a small
supporting cast where someone else teaches a point better.

**Carl Jung** (26 July 1875, Kesswil, Switzerland) is the lead, pulled with
`ChartBuilder.from_notable("Carl Jung")`. He earns it: a practicing astrologer
who cast charts for patients, coined *synchronicity*, and stands at the head of
modern psychological astrology. His chart is also a teaching gift, with a
late-degree Ascendant (29°58′ Capricorn) that makes the house-system debate
vivid and enough going on to illustrate nearly every technique here.

The supporting cast, each with one clear job:

| Native | Data | The job they do |
|---|---|---|
| **Wong Kar-wai** (1958) | 12:00 noon, time unknown | The unknown-birth-time chapter's hero. Proof that a chart with no verified time still delineates richly: planet-to-planet aspects and patterns survive, angles and houses don't. Doubles as the aspects/patterns showcase. |
| **Marilyn Monroe** (1926) | AA (birth certificate) | The data-quality contrast to WKW, plus the Ascendant-as-persona case (Leo rising, Norma Jeane becoming "Marilyn") and the Neptune/glamour/illusion case. |
| **Bruce Lee** (1940) | AA (verified) | The cross-cultural bridge, equally iconic East and West, and the two-traditions-in-one-person example: his Western chart (Sagittarius Sun on the Ascendant, a Scorpio Mars stellium) and his BaZi (born in the hour *and* year of the Dragon, Yang Wood Day Master) tell the same story in two languages. Anchors the Chinese/BaZi chapter. |

Beyond the recurring cast, individual chapters reach for a fitting local guest
where a tradition has an obvious avatar: **William Lilly** for horary and
traditional dignity, **B.V. Raman** for the Vedic chapter, **Dane Rudhyar** for
the modern synthesis. When a chapter swaps in a guest, it says so.

---

## The chapters

Grouped roughly from "you need this first" to "advanced and specialized." The
**Audit** column ties each chapter back to
[`CAPABILITY_AUDIT.md`](https://github.com/katelouie/stellium/blob/main/docs/astrology/CAPABILITY_AUDIT.md); the **Cookbook** column points at
the runnable code.

### Foundations

| # | Chapter | Covers | Cookbook |
|---|---|---|---|
| 00 | Orientation | What a chart is; the sky as a set of coordinates; how to read this guide | `chart_cookbook.py` |
| 01 | The Zodiac | Signs, elements, modalities; tropical vs. sidereal; ayanamsa | `chart_cookbook.py` |
| 02 | Planets & Points | Luminaries → outer planets; nodes, Lilith, asteroids, centaurs, TNOs | `chart_cookbook.py` |
| 03 | Houses | The twelve places; quadrant vs. whole-sign; the house-division debate | `chart_cookbook.py` |
| 04 | Aspects | Major/minor/harmonic; orbs; applying/separating; aspect patterns | `aspects_and_orbs_cookbook.py` |

### Traditional / Hellenistic

| # | Chapter | Covers | Cookbook |
|---|---|---|---|
| 05 | Sect & the Day/Night Chart | The single most under-taught traditional concept | `dignities_cookbook.py` |
| 06 | Dignity & Rulership | Essential/accidental dignity; triplicity, bounds, decans; dispositors | `dignities_cookbook.py` |
| 07 | Lots (Arabic Parts) | Fortune, Spirit, and the sect-based formula machine | `dignities_cookbook.py` |
| 14 | Profections | Annual/monthly time-lords; lord of the year | `profections_cookbook.py` |
| 15 | Zodiacal Releasing | Valens' peak-and-period technique; Loosing of the Bond | `zodiacal_releasing_cookbook.py` |

### The Moon, stars, and declination

| # | Chapter | Covers | Cookbook |
|---|---|---|---|
| 08 | The Moon | Phases, void-of-course, the nodal axis | `transit_cookbook.py` |
| 09 | Fixed Stars | Royal Stars; tiers; how stars differ from planets | `chart_cookbook.py` |
| 10 | Declination | Out-of-bounds planets; parallels & contraparallels | `chart_cookbook.py` |

### Prediction & timing

| # | Chapter | Covers | Cookbook |
|---|---|---|---|
| 12 | Transits | The engine of modern prediction; orbs, retrograde passes, Gantt | `transit_cookbook.py` |
| 13 | Progressions & Directions | Secondary progressions; solar arc; primary & zodiacal directions | `progressions_cookbook.py`, `arc_directions_cookbook.py`, `directions_cookbook.py` |
| 16 | Returns | Solar, lunar, planetary; relocation | `returns_cookbook.py` |
| 17 | Electional & Horary | Choosing a time; planetary hours; the horary question | `electional_cookbook.py` |

### Relationship & specialized Western

| # | Chapter | Covers | Cookbook |
|---|---|---|---|
| 11 | Relationship Astrology | Synastry, composite, Davison; house overlays | `multichart_cookbook.py`, `comparison_cookbook.py` |
| 18 | Uranian & Midpoints | Hamburg School; dials; midpoint trees; antiscia | `dial_cookbook.py` |
| 19 | Harmonics & Draconic | Addey harmonics; the draconic zodiac | `chart_cookbook.py` |
| 20 | Chart Shapes | Jones patterns: Bowl, Bucket, Locomotive, and the rest | `chart_cookbook.py` |

### Other traditions

| # | Chapter | Covers | Cookbook |
|---|---|---|---|
| 21 | Vedic / Jyotish | Sidereal logic; N/S Indian charts; KP; **what Stellium does and doesn't do** | `vedic_cookbook.py` |
| 22 | Chinese / BaZi | Four Pillars; Ten Gods; Wu Xing; Day Master strength | `bazi_cookbook.py` |
| 23 | The Modern Synthesis | Psychological, evolutionary, traditional-revival, and data-driven astrology | `analysis_cookbook.ipynb` |

That's **24 chapters**. The numbering leaves room to reorder without renaming
files (chapters are grouped by theme above but numbered by a suggested reading
order).

---

## Status — 8 chapters of 24

:::{admonition} 🚧 Under construction
:class: warning

**Eight of twenty-four chapters are written.** The rest are planned — listed above —
and not yet drafted.

Chapters **06 Dignity & Rulership** and **07 Lots** have been checked against computed
output: every figure in them comes from a chart that was run, and their code blocks are
pinned by the test suite. The other six are drafts. Read them, but don't quote a number
from them yet.
:::

| Chapter | Status |
|---|---|
| 00 Orientation · 01 The Zodiac · 02 Planets & Points | Draft — prose unverified |
| 03 Houses | Draft — the flagship / voice reference |
| 04 Aspects · 05 Sect | Draft — prose unverified |
| **06 Dignity & Rulership** · **07 Lots** | **Verified against computed output** |
| 08–23 | Not yet written |

New here? Start with [00 Orientation](guide/00_orientation.md), or jump to
[03 Houses](guide/03_houses.md) — the fully-written reference chapter that sets the
voice, depth and structure for the rest.

```{toctree}
:hidden:
:maxdepth: 1

guide/00_orientation
guide/01_the_zodiac
guide/02_planets_and_points
guide/03_houses
guide/04_aspects
guide/05_sect
guide/06_dignity_and_rulership
guide/07_lots_arabic_parts
```

---

## A note on stance

This guide takes a **practical-within-the-tradition** stance by default:
astrology as a symbolic system with real internal logic and a long documented
history, explained clearly enough to *use*, without adjudicating whether it
predicts anything. Where the psychological framing and the traditional-fate
framing genuinely diverge on what a technique is *for* (transits are the classic
case), the chapter names both rather than picking one.
