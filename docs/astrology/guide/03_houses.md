# 03 · Houses

> Part of the [Stellium Astrology Guide](../README.md). Code companion:
> [`examples/chart_cookbook.py`](../../../examples/chart_cookbook.py).
> Prerequisites: [01 The Zodiac](./01_the_zodiac.md),
> [02 Planets & Points](./02_planets_and_points.md).


:::{admonition} 🚧 Under construction
:class: warning

This chapter is a **draft**. Its prose has not yet been re-verified against
Stellium's computed output — so treat any specific degree, score or placement in it
as unconfirmed until it has been.

Two chapters of this guide were previously found to contain figures that had never
been computed at all (see [Dignity & Rulership](06_dignity_and_rulership.md)). That is
the check this chapter is still waiting for.
:::

## The one-line version

The **houses** are twelve slices of the sky anchored to the horizon at your
exact birth moment and place. Signs tell you *how* a planet behaves; houses tell
you *where in your life* it plays out.

## Why this is the chapter people get stuck on

Signs and planets are portable. The Sun is in Leo for everyone born across a
whole month, no matter where they are on Earth. Houses are the opposite: they
depend on the minute you were born and the spot you were standing on, because
they're built from the horizon, and the horizon is different in Quito than it is
in Reykjavík at the same instant. That's why two people with nearly identical
planetary positions can have completely different charts. Same planets,
different houses, different lives.

This is also why an accurate birth time matters so much. Miss it by four minutes
and every planet is still in the same sign, but the whole house framework can
rotate by a degree. Miss it by two hours and you may be reading the wrong chart
entirely. Carl Jung, whose chart runs through this guide, is the cautionary
poster child: his Ascendant sits at 29°58′ Capricorn, the very last two arcminutes
of the sign. A birth a few minutes earlier would have given him an Aquarius
Ascendant and a different chart to live in. When the rising degree is that close
to a sign boundary, the birth time isn't a detail, it's the whole foundation.

---

## A brief history

### Houses came before quadrant math

The oldest house system is the simplest one. In **Hellenistic astrology** (the
Greek-Egyptian synthesis that ran from roughly the 1st century BCE through late
antiquity), the houses were just the signs, counted from the rising sign. If
Cancer was rising, Cancer was the whole 1st house, Leo the whole 2nd, Virgo the
whole 3rd, and so on around the wheel. One sign, one house, no arithmetic. This
is **Whole Sign houses**, and for about seven centuries it was simply *how
houses worked*.

The word we translate as "house" was *topos* in Greek, meaning **place**. A
place where a topic of life lives. The 7th place is where you meet the other
person; the 10th is where the world can see you. That older word is worth
keeping in your head, because "house" in English drags in a domestic image that
the concept doesn't really mean.

### The angles were always special

Even in the whole-sign era, four points were treated as more powerful than the
rest: the **Ascendant** (the degree rising on the eastern horizon), the
**Midheaven** or MC (the highest point the ecliptic reaches, roughly overhead),
the **Descendant** (setting in the west), and the **IC** (the lowest point,
underfoot). These four are the **angles**, and they're computed from spherical
astronomy, not from counting signs. In whole-sign charts the angles float
*inside* the houses rather than marking their edges, which surprises people
coming from modern charts. The MC might sit in the 9th place or the 11th, and
that's fine; it's information, not an error.

### Then astrologers started slicing

Once astrologers wanted the *degree* of the Ascendant and Midheaven to actually
begin the 1st and 10th houses, they needed a way to divide the space between the
angles into intermediate cusps. This is the **quadrant** problem: given four
corners fixed by astronomy, how do you cut the four quarters into three houses
each?

There is no single correct answer, because you're projecting a 3D rotating
sphere onto a flat wheel, and you can choose *what* to divide evenly: space,
time, or arc. Every quadrant house system is a different answer to that one
question.

- **Porphyry** (3rd century, the simplest quadrant method): just trisect each
  quarter of the ecliptic by longitude. Crude but honest.
- **Alcabitius** (Hellenistic, popular through the medieval Arabic tradition):
  divides the *time* it takes the Ascendant degree to rise to the MC.
- **Regiomontanus** and **Campanus** (medieval/Renaissance): divide great
  circles (the celestial equator and the prime vertical respectively) into equal
  arcs and project back to the ecliptic.
- **Placidus** (named for Placidus de Titis, a 17th-century monk, though the
  method is older): divides the *time* each degree spends moving from the
  horizon to the meridian. It became the default mostly because the first widely
  printed house tables, in the 19th and 20th centuries, were Placidus tables.
  Availability, not superiority, made it standard.
- **Koch** (Walter Koch, mid-20th century): a birthplace-latitude refinement
  ("birthplace houses") that had a strong following in mid-century European
  astrology. Fails hard at high latitudes.
- **Topocentric** (Polich-Page, Argentina, 1961): built from the observer's
  actual local rotational geometry, a cone around the polar axis passing through
  the exact birthplace. Lands within a fraction of a degree of Placidus at
  moderate latitudes, but from a completely different premise: not an abstract
  division of the sky, but *you, standing on a specific spot on a spinning
  Earth*.
- **Equal** (ancient, still common): the simplest idea after Whole Sign. Start
  at the exact Ascendant degree and mark off 30° twelve times. It keeps the
  *degree* of the ASC as the 1st cusp (which Whole Sign gives up) while keeping
  equal-size houses (which quadrant systems give up). A middle path.

### The systems, sorted by what they actually divide

The eighteen systems collapse into a handful of families once you ask the right
question: *what does this method cut into twelve?* This is the single most
useful way to hold them in your head, because it also tells you how a system
will behave (equal-size houses never break; time-based systems distort near the
poles).

| Family | What it divides | Systems | Character |
|---|---|---|---|
| Sign-based | nothing (house = whole sign) | Whole Sign | most abstract; pure sign-from-Ascendant |
| Equal-arc | the ecliptic into fixed 30° arcs | Equal, Equal (MC), Vehlow, Equal (Vertex) | clean, angle-anchored, never breaks |
| Ecliptic-proportional | the ecliptic arc between the angles | Porphyry | simplest quadrant method |
| Space (great-circle) | a great circle in space, projected onto the ecliptic | Campanus (prime vertical), Regiomontanus (equator), Morinus (equator), Horizontal, Axial Rotation | geometric, mundane |
| Time / diurnal | the *time* a degree takes to rise or culminate | Placidus, Koch, Alcabitius, Topocentric, APC, Krusinski | temporal, maximally tied to the exact birth moment and latitude |
| Research | the diurnal circle into fixed sectors | Gauquelin (36 sectors) | statistical |

Read that table top to bottom and you're reading a **spectrum of abstraction**.
At the top, Whole Sign ignores the precise geometry of your horizon entirely and
works from the archetypal relationship between signs. At the bottom, the
time-based systems are built from nothing *but* the exact rotation of the sky at
your latitude in your minute of birth. Every system is a choice about how much
local, embodied, this-exact-spot geometry to let into the chart.

So the "default" most software ships with (Placidus) won by a printing accident,
and the oldest system (Whole Sign) came roaring back in the 1990s and 2000s when
astrologers rediscovered and translated the Hellenistic sources. Both facts are
worth knowing before you pick one.

---

## The theory

### Where houses actually come from: the daily rotation

Planets move through the zodiac slowly, over days and years. The **houses come
from the Earth spinning once a day.** In 24 hours, the entire zodiac appears to
rise, culminate, set, and pass underfoot, because you're the one rotating. The
Ascendant moves through all twelve signs in a day, about one degree every four
minutes. Freeze that rotation at the birth moment and you get the house
framework: a snapshot of which part of the sky was rising, overhead, setting,
and hidden.

That's the whole physical basis. Signs are the Earth's orbit (the year); houses
are the Earth's rotation (the day). Two different clocks.

### The twelve topics

Each house governs a domain of life. The keywords below are the traditional
core; modern astrology has layered on psychological readings, but the skeleton
is ancient and remarkably stable across traditions.

| House | Core topic | Angular / Succedent / Cadent |
|---|---|---|
| 1st | Self, body, vitality, appearance, the "front door" | Angular |
| 2nd | Resources, money, possessions, self-worth | Succedent |
| 3rd | Siblings, neighbors, short trips, everyday mind | Cadent |
| 4th | Home, roots, family, the private self, endings | Angular |
| 5th | Children, creativity, pleasure, romance, play | Succedent |
| 6th | Work, health, service, daily routine, animals | Cadent |
| 7th | Partners, marriage, open enemies, the other | Angular |
| 8th | Death, shared resources, sex, transformation, the hidden | Succedent |
| 9th | Travel, higher learning, philosophy, religion, the foreign | Cadent |
| 10th | Career, reputation, public role, authority | Angular |
| 11th | Friends, groups, hopes, allies, the future | Succedent |
| 12th | Isolation, loss, the unconscious, undoing, retreat | Cadent |

### Angular, succedent, cadent: the strength gradient

The houses come in a rhythm of three, and it matters more than beginners expect.

- **Angular** houses (1, 4, 7, 10) sit on the angles. A planet here is loud,
  active, and consequential. Things happen.
- **Succedent** houses (2, 5, 8, 11) follow the angles. Planets here are stable
  and resource-building, slower to act.
- **Cadent** houses (3, 6, 9, 12) fall away from the angles. Traditionally the
  weakest by placement, though the 9th (astrology, travel, meaning) got a
  reputation boost it arguably deserves.

This is a form of **accidental dignity** (strength by circumstance rather than
by sign). A brilliant planet in a cadent house can be like a great chef working
from a closet: the talent is real, the platform is small. See
[06 Dignity & Rulership](./06_dignity_and_rulership.md).

### The ruler of the house does the real work

Here's the move that separates a keyword reader from an actual astrologer.
You don't just read *what's in* a house; you find the planet that **rules the
sign on the cusp** and see where *it* is. That ruler carries the house's affairs
across the chart.

Say your 10th house (career) has Libra on the cusp. Venus rules Libra, so Venus
is your "lord of the 10th." If Venus sits in your 5th house of creativity, the
chart is telling you a story: career runs through creative or artistic work. The
house is the topic; its ruler is the plot. Empty houses (no planets inside) are
completely normal and not a deficiency; you read them entirely through their
ruler. Most people have several empty houses, because ten-ish planets can't fill
twelve rooms.

---

## In practice

### The house-system debate, honestly

This is the one genuine schism you'll hit early, so here's the real state of it
rather than a fake consensus.

**The Whole Sign camp** (much of the traditional/Hellenistic revival) argues
that quadrant systems solve a problem that didn't need solving, distort house
sizes badly at high latitudes, and lose the clean one-sign-one-house logic that
makes rulership and profection work elegantly. They point out that Whole Sign is
what the oldest surviving texts actually use.

**The Placidus camp** (much of modern and psychological astrology) argues that
the degree of the Ascendant and MC clearly *feels* like a threshold, that
intermediate cusps carry real information, and that decades of modern practice
were built on quadrant houses and work fine.

The honest technical points, which both camps agree on:

- At **high latitudes** (past ~66°, and getting weird well before that), most
  quadrant systems break down. Houses become wildly unequal, and near the poles
  Placidus and Koch can fail to define houses at all. Whole Sign and Equal
  never break, because they don't depend on the geometry that fails.
- Quadrant systems can put a planet in different houses depending on the system,
  which is exactly the ambiguity Whole Sign avoids and quadrant fans accept as
  the price of more resolution.

> [!TIP]
> **Don't pick a house system in the abstract, compare on a real chart.** Run
> Whole Sign and Placidus side by side on charts you know well and see which house
> a contested planet lands in and which story rings true. Stellium computes
> several systems at once precisely so you can do this instead of arguing about it.

### Reading houses in order

A workable beginner sequence:

1. Find the **Ascendant** sign. That's the lens the whole chart looks through.
2. Note which planets are **angular** (near the ASC, MC, DSC, IC). Those are
   your headline actors.
3. For each house you care about, find its **ruler** and see where it lives.
4. Read planets **in** houses as "this energy shows up in this area of life."
5. Empty houses: go straight to the ruler. Silence in a room isn't absence, it's
   "look elsewhere for the key."

---

## In Stellium

Stellium computes house cusps and, critically, lets you run **multiple house
systems on a single chart** so you can compare them directly. Placidus is the
default; everything else is one method call.

### One house system

```python
from stellium import ChartBuilder

# from_notable pulls Jung's verified birth data from Stellium's database.
# (To build a chart from raw birth details, see chapter 00.)
# Placidus is the default, so this is a Placidus chart.
chart = ChartBuilder.from_notable("Carl Jung").calculate()

# The whole cusp set for the default system
houses = chart.get_houses()               # HouseCusps object
for h in range(1, 13):
    print(f"House {h:2}: {houses.get_sign(h):12} (cusp {houses.get_cusp(h):.2f}°)")

# Which house is a given planet in?
print("Sun is in house", chart.get_house("Sun"))    # 7
print("Moon is in house", chart.get_house("Moon"))   # 3
```
<!--pytest-codeblocks:expected-output-->
```
House  1: Capricorn    (cusp 298.88°)
House  2: Pisces       (cusp 352.12°)
House  3: Taurus       (cusp 31.74°)
House  4: Taurus       (cusp 57.34°)
House  5: Gemini       (cusp 77.03°)
House  6: Cancer       (cusp 95.75°)
House  7: Cancer       (cusp 118.88°)
House  8: Virgo        (cusp 172.12°)
House  9: Scorpio      (cusp 211.74°)
House 10: Scorpio      (cusp 237.34°)
House 11: Sagittarius  (cusp 257.03°)
House 12: Capricorn    (cusp 275.75°)
Sun is in house 7
Moon is in house 3
```

### Whole Sign (the traditional default)

```python
from stellium import ChartBuilder
from stellium.engines import WholeSignHouses

chart = (ChartBuilder.from_notable("Carl Jung")
    .with_house_systems([WholeSignHouses()])
    .calculate())

print("House system:", chart.default_house_system)   # "Whole Sign"
print("Sun (Whole Sign):", chart.get_house("Sun"))   # 8
```
<!--pytest-codeblocks:expected-output-->
```
House system: Whole Sign
Sun (Whole Sign): 8
```

### Compare systems side by side (the reason to use Stellium)

```python
from stellium import ChartBuilder
from stellium.engines import (
    PlacidusHouses, WholeSignHouses, KochHouses, TopocentricHouses,
)

chart = (ChartBuilder.from_notable("Carl Jung")
    .with_house_systems([
        PlacidusHouses(), WholeSignHouses(), KochHouses(), TopocentricHouses(),
    ])
    .calculate())

# A planet near a cusp is where systems disagree. Watch the Sun:
for system in ("Placidus", "Whole Sign", "Koch", "Topocentric"):
    print(f"{system:12}: Sun in house {chart.get_house('Sun', system)}")
# Placidus    : Sun in house 7
# Whole Sign  : Sun in house 8      <- the interesting disagreement
# Koch        : Sun in house 7
# Topocentric : Sun in house 7

# Jupiter is even starker: three systems, three different houses.
for system in ("Placidus", "Koch", "Whole Sign"):
    print(f"{system:12}: Jupiter in house {chart.get_house('Jupiter', system)}")
# Placidus    : Jupiter in house 8
# Koch        : Jupiter in house 9
# Whole Sign  : Jupiter in house 10

# Pull the full cusp set for any one of them
whole = chart.get_houses("Whole Sign")
topo  = chart.get_houses("Topocentric")
```
<!--pytest-codeblocks:expected-output-->
```
Placidus    : Sun in house 7
Whole Sign  : Sun in house 8
Koch        : Sun in house 7
Topocentric : Sun in house 7
Placidus    : Jupiter in house 8
Koch        : Jupiter in house 9
Whole Sign  : Jupiter in house 10
```

When Whole Sign puts the Sun in the 8th and the quadrant systems put it in the
7th, that disagreement is the interesting part, not a problem to resolve. Jung's
chart makes this unusually dramatic: because his Ascendant sits at the very end
of Capricorn (29°58′), the whole-sign houses are shifted almost a full sign from
the quadrant ones, so nearly every planet lands in a different house depending on
the system. Most charts disagree less than his does. Read both stories; keep the
one the person recognizes (or, if you're feeling ambitious, keep both and ask how
they relate).

### The angles

The four angles are computed per house system and appended to the chart's
positions, so you can read them like any other point:

```python
for angle in chart.get_angles():
    print(f"{angle.name:5} {angle.sign_position}")
# ASC   29°58' Capricorn
# MC    28°08' Scorpio
# DSC   29°58' Cancer
# IC    28°08' Taurus
```

(`sign_position` already includes the sign name, so you don't need to print
`angle.sign` separately.)

### Draw the wheel with house cusps visible

```python
(chart.draw("chart_with_houses.svg")
    .with_house_systems("Placidus")   # which system's cusps to draw
    .preset_detailed()
    .save())
```

Full house options (all 18 systems and their codes) live in
[`docs/options_list.md`](../../options_list.md#house-systems-18-systems).

---

## Going deeper

- **Next:** [04 Aspects](./04_aspects.md) shows how planets in different houses
  talk to each other.
- **The angles in prediction:** **14 Profections** *(not yet written)* uses
  whole-sign houses to hand each year of life to a different house and its
  ruler. It's the cleanest argument for why one-sign-one-house is elegant.
- **House strength:** [06 Dignity & Rulership](./06_dignity_and_rulership.md)
  covers angularity as accidental dignity and the ruler-of-the-house technique
  in full.
- **The high-latitude problem in code:** compare systems on a chart born in
  Reykjavík or Tromsø and watch quadrant houses distort while Whole Sign holds.

**Primary sources & further reading:**

- Chris Brennan, *Hellenistic Astrology* (2017) for the whole-sign history and
  the *topos* concept.
- Deborah Houlding, *The Houses: Temples of the Sky* for the meaning-history of
  the twelve places.
- The Swiss Ephemeris documentation on house systems for the raw geometry of
  each quadrant method.
