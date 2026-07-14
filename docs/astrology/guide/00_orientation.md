# 00 · Orientation

> Part of the [Stellium Astrology Guide](../README.md). Code companion:
> [`examples/chart_cookbook.py`](../../../examples/chart_cookbook.py).
> Prerequisites: none. This is the front door.

## The one-line version

A **birth chart** is a map of the sky as it looked from one exact spot on Earth
at one exact moment: the moment someone was born. Everything else in astrology is
a way of reading that map.

## What this chapter does

This is the orientation. By the end you'll know what a chart actually is (a
coordinate system, not a mystery), the four moving parts every chart is built
from, how much the birth time really matters, what to do when you don't have one,
and how to build any of it in Stellium. The later chapters go deep on each piece;
this one hands you the frame they all hang on.

You do not have to believe astrology predicts anything to follow along. Treat it
the way you'd treat any structured symbolic system: learn its internal logic, see
how practitioners use it, and decide for yourself what it's worth. The guide
explains from inside the tradition without asking you to sign anything.

---

## A brief history

Astrology is old, and knowing roughly *how* old explains why its pieces fit
together the way they do.

It began as **sky-watching for omens** in Mesopotamia, well over three thousand
years ago. Babylonian priests tracked eclipses, planetary risings, and
conjunctions as messages about the king and the state, not the individual. Your
personal horoscope did not exist yet; the sky spoke about the realm.

The **birth chart proper** is a Hellenistic invention, roughly the 2nd to 1st
century BCE, when Babylonian omen-lore met Egyptian and Greek astronomy and
philosophy in the melting pot of Alexandria. That fusion produced the whole
apparatus this guide is about: the rising sign, the twelve houses, the aspects,
the lots. For the first time the sky spoke about a *person*.

From there it traveled. Hellenistic astrology passed into Sassanian Persia, then
flowered in the Islamic Golden Age (Abu Ma'shar, al-Biruni, Māshā'allāh extended
and systematized it), returned to Europe through 12th-century translations,
and peaked in the Renaissance with working astrologers like William Lilly and,
yes, Johannes Kepler. The Enlightenment pushed it to the cultural margins.

Then it came back in waves: a late-1800s revival through Theosophy and Alan Leo,
a 20th-century **psychological turn** (this is where Carl Jung, our lead example,
enters as an influence, alongside Dane Rudhyar), and a **traditional revival** in
the 1990s and 2000s when scholars translated the original Greek sources and
astrologers rediscovered techniques that had been lost for centuries.

Meanwhile, other traditions grew on their own roots. **Vedic astrology**
(Jyotish) in India shares some early Hellenistic contact but built a vast native
system of its own. **Chinese astrology** (BaZi and others) is independent
entirely, built from the calendar and the five elements rather than the zodiac.
Stellium touches all three; the bulk of this guide is Western, because that's
where the library goes deepest.

The practical upshot: when a later chapter says a technique is "Hellenistic" or
"medieval" or "modern," it's placing it on this timeline, and the era usually
explains the logic.

---

## The theory

### A chart is the sky in coordinates

Strip away the symbolism and a chart is a coordinate readout. Here's the whole
mechanism.

We plot the sky **geocentrically**, from Earth's point of view: where the planets
*appear* from here, not where they sit relative to the Sun. (Stellium can do
heliocentric too, but Earth-centered is the tradition and the default.)

Nearly everything in the solar system orbits in roughly the same flat plane. Seen
from Earth, that plane becomes a line the Sun traces across the sky over a year,
called the **ecliptic**. Because the planets share the plane, they all appear
strung out near that same line, which is why the zodiac is a narrow *band* and
why a single number can locate any planet.

That number is **ecliptic longitude**: a position from 0° to 360° measured around
the ecliptic. The **zodiac** simply chops that ring into twelve 30° signs. So
"Sun in Leo" is not poetry, it's an address. Jung's Sun sits at ecliptic
longitude **123.3°**, and since Leo runs from 120° to 150°, that's **3.3° into
Leo**. Sign plus degree is just longitude in friendlier units.

Where does 0° (the start of Aries) come from? In the **tropical zodiac** used by
Western astrology, 0° Aries is pinned to the spring equinox, a seasonal anchor.
The **sidereal zodiac** pins it to the fixed stars instead, which is why the two
drift about 24° apart. That's a whole chapter of its own
([01 The Zodiac](./01_the_zodiac.md)); for now, just know the ring has to be
anchored to *something*, and the two traditions anchor it differently.

### Two clocks build the chart

A chart runs on two independent clocks, and almost every beginner confusion comes
from mixing them up.

- **The year** (Earth's orbit) sets *where the planets are in the zodiac*. The Sun
  moves about 1° per day, the Moon a racing ~13° per day, the outer planets a
  crawl. This clock gives you **signs**.
- **The day** (Earth's rotation) sets *what's rising, overhead, and setting right
  now*. In 24 hours the whole zodiac appears to wheel past. This clock gives you
  the **houses** and the four **angles** ([03 Houses](./03_houses.md)).

Signs come from the slow clock, houses from the fast one. That's why two people
born the same day share almost all their planet positions but have completely
different houses: the fast clock had moved.

(One apparent-motion note, since it trips people up: **retrograde** planets aren't
really reversing. From our moving vantage point on Earth, a planet can appear to
loop backward the way a slower car seems to slide backward when you overtake it.
Stellium marks it with a negative speed; more in [02 Planets & Points](./02_planets_and_points.md).)

### The grammar of a chart: what, how, where, and how they talk

A chart has thousands of things to say, and they're all built from four kinds of
element. Learn these four and you can read the sentence structure of any chart:

- **Planets** are the *what*. The drives, functions, and actors: the will (Sun),
  the instincts (Moon), the mind (Mercury), and so on. [Chapter 02](./02_planets_and_points.md).
- **Signs** are the *how*. The style or manner a planet operates in. Mars (drive)
  in Aries acts one way, Mars in Libra another. [Chapter 01](./01_the_zodiac.md).
- **Houses** are the *where*. The area of life a planet plays out in: money, love,
  career, the hidden. [Chapter 03](./03_houses.md).
- **Aspects** are the *relationships*. The angles between planets that put them in
  conversation, easy or tense. [Chapter 04](./04_aspects.md).

Put them together and each placement reads like a sentence: *Venus* (what: love
and values) *in Gemini* (how: curious, verbal, many-at-once) *in the 7th house*
(where: partnership) *square Saturn* (in tense conversation with: limits and
fear). Delineation, the actual craft, is reading thousands of those sentences and
knowing which ones matter most.

### The anatomy of the wheel

When you look at a chart wheel, you're looking at all four layers at once. The
outer ring is the **zodiac**. The pie-slices are the twelve **houses**, starting
from the **Ascendant** on the left (the degree rising in the east) and running
counter-clockwise. The glyphs around the ring are the **planets**, placed by their
longitude. The lines crossing the middle are the **aspects**. The four spokes at
left, top, right, and bottom are the **angles** (Ascendant, Midheaven,
Descendant, IC). That's the entire picture; the rest of the guide is learning to
read it.

---

## In practice

### How to actually approach a chart

Faced with a full chart, beginners freeze because everything seems equally
important. It isn't. A workable first pass:

1. **Start with the big three:** Sun sign, Moon sign, and rising sign
   (Ascendant). For Jung that's **Sun in Leo, Moon in Taurus, Capricorn rising**.
   These three carry the core: conscious identity, inner emotional life, and the
   lens the whole chart looks through.
2. **Find the loud placements:** planets on the angles, tight aspects, any
   stellium (pile-up of planets).
3. **Then layer in** houses, rulerships, and the subtler aspects.

You build outward from the strongest signal. Every later chapter is really a tool
for deciding what counts as "strongest."

### The birth-data question (and why the time is the fragile part)

A chart needs three inputs, and they are not equally demanding:

- **Date** fixes almost all the planet signs. Even a date-only chart gets you most
  of the zodiac placements.
- **Place** fixes the horizon, and so the houses and angles.
- **Time** fixes the houses, the four angles, and the exact degree of the fast
  Moon.

The time is the fragile one, and astrologers grade how much they trust it with
the **Rodden rating** system: **AA** (from a birth certificate or official
record), **A** (from the person or family, i.e. memory), **B** (from a
biography), **C** (uncertain, original source unknown), **DD** ("dirty data,"
sources conflict), and **X** (no time known at all). It's a data-quality label,
and it should change how hard you lean on the time-dependent parts of a chart.

Here's how much this matters, using Jung. His recorded time is 19:24, but his
data is only **C-rated**, so it's genuinely uncertain by more than a couple of
minutes. Watch what a few minutes do to his Ascendant:

| Birth time | Ascendant |
|---|---|
| 19:18 | 28°00′ Capricorn |
| 19:24 (recorded) | 29°58′ Capricorn |
| 19:27 | 0°59′ Aquarius |
| 19:33 | 3°02′ Aquarius |

Three minutes (19:24 to 19:27) flips his **rising sign** from Capricorn to
Aquarius. His entire "Capricorn rising" identity, the lens his whole chart is
read through, hangs on data we can't fully trust. This is not a Jung quirk; it's
the general rule.

> [!IMPORTANT]
> Planet **signs** are robust, but **houses and angles are only as good as the
> birth time.** When a chart's data is rated C or DD, or the time is a guess, hold
> everything time-dependent (houses, angles, the exact Moon, the rising sign and
> its ruler) loosely.

(When the time is genuinely lost, astrologers sometimes work backward from major
life events to estimate it, a practice called **rectification**. It's real, it's
advanced, and it's honest about being an estimate.)

### Reading a chart with no birth time at all

You will constantly meet charts with no reliable time. Wong Kar-wai, who anchors
[chapter 04](./04_aspects.md), is one. A lot of astrologers will tell you a
timeless chart is unreadable. They're wrong, and it's worth being clear about why.

**What you lose without a time:** the houses, the four angles (Ascendant,
Midheaven, and the rest), the exact degree of the Moon, and anything built on
those (the rising sign and its ruler, whole-sign house topics, sometimes the
day/night distinction if the birth is near dawn or dusk).

**What you keep:** every planet's sign, every planet-to-planet aspect, the aspect
patterns among planets, the dignities, the elemental and modal balance. That is
most of a chart's grammar, still intact.

So you have two honest ways to work:

1. **The noon placeholder.** Cast the chart for 12:00 and read it, but treat the
   houses and angles as fiction and hold the Moon loosely. This is what Wong
   Kar-wai's report does, and [chapter 04](./04_aspects.md) shows how to read it
   without being fooled by the fake angles.
2. **Tell the software the truth.** Stellium's unknown-time mode refuses to draw
   houses it can't know and hands you a *range* for the Moon instead of a false
   exact degree. That's the principled version, and it's below in the code.

> [!NOTE]
> **A missing birth time is where the reading starts, not where it stops.** Read
> the layer that survives (signs, planet-to-planet aspects, dignities, element and
> modality balance) and be honest about the layer that doesn't (houses, angles,
> the exact Moon).

---

## In Stellium

Every chart in this guide starts from one of three constructors. They're
equivalent; pick the one that fits what you have.

### Building a chart

```python
from stellium import ChartBuilder, Native
from datetime import datetime

# 1. From the curated notables database (no birth data to type).
chart = ChartBuilder.from_notable("Carl Jung").calculate()

# 2. From a datetime string + a place name (geocoded and timezone-resolved).
chart = ChartBuilder.from_details("1875-07-26 19:24", "Kesswil, Switzerland").calculate()

# 3. From an explicit Native object (most control).
native = Native(datetime(1875, 7, 26, 19, 24), "Kesswil, Switzerland")
chart = ChartBuilder.from_native(native).calculate()
```

All three build the identical chart (Sun 3°18′ Leo, Ascendant 29°58′ Capricorn).
`from_details` accepts ISO, US, or European date formats and a place name *or* a
`(lat, lon)` tuple; it geocodes the place and resolves the historical timezone for
you. (Getting that timezone right for an 1875 Swiss birth is exactly the kind of
thing you want handled for you.)

### Reading the big three

```python
chart = ChartBuilder.from_notable("Carl Jung").calculate()

for name in ("Sun", "Moon", "ASC"):
    obj = chart.get_object(name)
    print(f"{name:4} {obj.sign_position}")
# Sun  3°18' Leo
# Moon 15°27' Taurus
# ASC  29°58' Capricorn
```

`chart.get_object(...)` fetches any planet, point, or angle;
`obj.sign_position` gives the friendly "degree + sign," while `obj.longitude`
gives the raw ecliptic longitude if you want the coordinate underneath.

### When there's no birth time

```python
from stellium import ChartBuilder

# Either flag the Native as time-unknown...
chart = ChartBuilder.from_details(
    "1958-07-17", "Shanghai, China", time_unknown=True
).with_aspects().calculate()

# ...or ask the builder to drop the time on any chart.
chart = ChartBuilder.from_notable("Wong Kar-wai").with_unknown_time().with_aspects().calculate()

print(type(chart).__name__)   # UnknownTimeChart
print(chart.get_houses())     # None: it won't invent houses it can't know
print(chart.moon_range)       # a Moon range, not a false exact degree
```
<!--pytest-codeblocks:expected-output-->
```
UnknownTimeChart
None
Moon: Cancer 22° - Leo 6° (arc: 13.8°)
```

Both routes return an `UnknownTimeChart`: no houses, no angles, and a
`moon_range` instead of a single Moon position. Your planet-to-planet aspects
still calculate normally, which is the whole point. [Chapter 04](./04_aspects.md)
puts this to work on Wong Kar-wai.

---

## How to use this guide, and where to go next

Every chapter follows the same six beats (the one-line version, a brief history,
the theory, in practice, in Stellium, and going deeper), so you can read a
chapter top to bottom or jump straight to the code in beat five. The guide keeps a
small recurring **cast** of example charts (Jung leads; Wong Kar-wai, Marilyn
Monroe, and Bruce Lee guest where they teach a point better); the
[README](../README.md) introduces them and lists all the chapters.

From here, the natural path is straight ahead:

- **[01 The Zodiac](./01_the_zodiac.md)** — the signs, the elements and
  modalities, and the tropical-vs-sidereal question raised above.
- **[02 Planets & Points](./02_planets_and_points.md)** — the actors themselves.
- **[03 Houses](./03_houses.md)** — the *where*, and the house-system debate.
- **[04 Aspects](./04_aspects.md)** — how the planets talk to each other, and how
  to read a chart (like Wong Kar-wai's) with no birth time.

Read those four in order and you can read a chart. Everything after is
specialization.

**Further reading:**

- Chris Brennan, *Hellenistic Astrology: The Study of Fate and Fortune* (2017),
  for the history and the foundations, in far more depth.
- Kevin Burk, *Astrology: Understanding the Birth Chart*, for a clear modern
  beginner's synthesis.
- The [AstroDatabank](https://www.astro.com/astro-databank/) Rodden-rating system,
  for how birth-time reliability is actually catalogued.
