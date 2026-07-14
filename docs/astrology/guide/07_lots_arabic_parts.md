# 07 · Lots (Arabic Parts)

> Part of the [Stellium Astrology Guide](../README.md). Code companion:
> [`examples/dignities_cookbook.py`](../../../examples/dignities_cookbook.py).
> Prerequisites: [05 Sect](./05_sect.md), [06 Dignity & Rulership](./06_dignity_and_rulership.md).

## The one-line version

A **lot** (or Arabic part) is a calculated point built from the arc between two
planets, projected out from the Ascendant. It's a formula that turns a
relationship between two things in the chart into a single sensitive spot about a
specific topic. The two great lots, **Fortune** and **Spirit**, are the ones to
learn first, and they run on a switch flipped by sect.

## The idea in one picture

Take the distance from your Sun to your Moon. Now lay that exact same distance
down starting from your Ascendant. Where it lands is your **Lot of Fortune**.
That's the entire mechanism: measure an arc between two points, transfer it to the
Ascendant, mark the spot. The lot "carries" the Sun-Moon relationship to a new
place on the wheel and makes it a topic you can read. Change the two ingredients
and you get a lot for a different topic. It is, genuinely, a little formula
machine, and Stellium ships 28 of the formulas.

We'll keep **William Lilly** as our guide, closing out the traditional trilogy
(sect, dignity, lots) on the same chart, because his lots tie back beautifully to
the dignity work from the last chapter.

---

## A brief history

The Greeks called these *klēroi*, "lots" or "allotments," as in casting lots, and
they were central to Hellenistic astrology, not a footnote. The **Lot of
Fortune** in particular was one of the most important points in the whole chart, a
kind of second Ascendant standing in for the body and material life. Astrologers
like Vettius Valens and Paulus Alexandrinus used dozens of lots, one for nearly
every topic you might ask about.

The tradition passed east into Persian and Arabic astrology, where the lots became
"parts" (Latin *pars*), and al-Biruni catalogued something like 97 of them. That
transmission route is why the West inherited them under the name **"Arabic
parts."**

> [!NOTE]
> "Arabic parts" is a misnomer of convenience. The lots are **Hellenistic** in
> origin; they just reached medieval Europe through Arabic-language texts. If you
> see "Arabic parts" and "Hellenistic lots," they're the same technique.

Modern astrology kept almost none of them. The Lot of Fortune survived in most
20th-century practice, but frequently mis-computed (more on that below), and the
rest were largely forgotten until the Hellenistic revival brought the full formula
machine back.

---

## The theory

### What a lot is, mechanically

Every lot is a sum of three points:

```
Lot = Ascendant + PointB - PointA
```

You can read it as: take the arc from PointA to PointB, and project it from the
Ascendant. The lot inherits the *relationship* between two planets and stamps it
onto the wheel as a new degree, with a sign and a house, that you then interpret.

### The two great lots: Fortune and Spirit

Two lots tower over the rest, and they're mirror images of each other.

- **The Lot of Fortune** is the lunar lot: the **body, health, livelihood,
  material circumstance**, and fortune in the old sense, *what happens to you*, the
  hand you're dealt. It's the more passive, embodied, circumstantial lot.
- **The Lot of Spirit** is the solar lot: the **soul, mind, will, action, and
  career**, *what you do*, the choices you make with the hand you're dealt. It's
  the more active, volitional lot.

Fortune is what fortune gives you; Spirit is what you make of it. Together they map
the classic tension between fate and will, and they sit as reflections of each
other across the Ascendant.

### The sect flip: the formula machine's master switch

Here is the thing almost everyone gets wrong, and the reason this chapter needs
chapter 05. The formulas for Fortune and Spirit **swap based on sect**:

| Lot | Day chart | Night chart |
|---|---|---|
| **Fortune** | ASC + Moon − Sun | ASC + Sun − Moon |
| **Spirit** | ASC + Sun − Moon | ASC + Moon − Sun |

Look closely: the two formulas are the *same pair*, `ASC + Moon − Sun` and
`ASC + Sun − Moon`. Sect just decides **which one is Fortune and which is
Spirit.** By day, Fortune follows the Moon; by night, the whole thing flips.

You can watch it happen across our sect pair from chapter 05. Marilyn Monroe is a
day chart, so her Fortune is `ASC + Moon − Sun` = 21° Aries. Muhammad Ali is a
night chart, so *his* Fortune is `ASC + Sun − Moon` = 4° Leo. Feed a night chart
the day formula and you haven't computed a slightly-off Fortune; you've computed
his **Spirit** and mislabeled it.

> [!IMPORTANT]
> **Compute lots with the correct sect or Fortune and Spirit silently swap.** This
> is the single most common error in lot work, and it's not a small one: you get
> the right degree with the wrong meaning. Stellium reads `chart.sect` and flips
> the formula for you, but if you ever compute a lot by hand, get the sect first.

### A lot has no power of its own: read it through its ruler

A lot is a *point*, not a planet. It doesn't act; it marks. So you read a lot in
two moves: first its **sign and house** (where the topic lives), and then,
crucially, the **condition of the planet that rules its sign**. A well-dignified
ruler means the topic is well-supported; a debilitated or out-of-sect ruler means
it struggles. This is exactly where [chapter 06](./06_dignity_and_rulership.md)
comes back: the dignity of the lot's ruler *is* the reading.

### The wider catalog

Fortune and Spirit are the head of a family. Stellium computes 28 lots in all: the
**Hermetic lots** (Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis),
the **family lots** (father, mother, siblings, children, marriage), a set of
**life-topic lots**, and the **planetary lots**. Each is just another arc
projected from the Ascendant, a formula for a topic. Eros is the lot of desire and
what you love; Nemesis, the lot of what undoes you; the marriage lot, of union.

---

## In practice

### Reading the pair: Lilly's Spirit is the one that married

Lilly was born at two in the morning, so his is a **night** chart, and the sect flip
is live: Fortune takes the night formula, Spirit the day one. Run them and you get a
pair that says two different things.

**Spirit** — purpose, career, what you *steer* — lands at **26° Libra in the 7th
house**, and its ruler is **Venus in Taurus in the 2nd**, in domicile: the strongest
planet in his chart, and (from chapter 06) the final dispositor everything answers to.
Spirit in the house of partnership, ruled by a domicile Venus in the house of money.

Now read his life. AstroDatabank's own biography: *"Lilly acquired a fortune by
marriage **which allowed him the leisure to study and follow his bent**."* He married
well, and the money bought him the time to become an astrologer. That is not a
statement about his body or his luck. It is a statement about **what he was able to
do with his life** — and that is Spirit's department, not Fortune's, arriving through
the 7th (marriage) and paid for by Venus in the 2nd (money).

**Fortune** — body, circumstance, the substrate you are handed — sits at **7° Cancer
in the 5th**, ruled by the **Moon in Capricorn, in detriment** (−2 even with its night
triplicity). The given part of his life is thinly resourced. The chosen part is not.

> [!WARNING]
> **This chapter used to say the opposite, and the way it got there is worth knowing.**
> An earlier draft claimed *"Lilly's Lot of Fortune is 12° Libra, in the 7th house,
> ruled by Venus"* and read it as fortune-through-marriage. Libra, the 7th, Venus — all
> three are real, and all three belong to **Spirit**. The name of one lot had been
> attached to the placement of the other, and then a tidy story was written on top of
> it that happened to match a biography anybody could look up.
>
> It read beautifully. It was never computed. Every code block in this guide now has
> its output generated by running it (`scripts/update_doc_outputs.py`), precisely so
> that a sentence like that one cannot survive again.

### Fortune vs Spirit in a reading

Read **Fortune** for questions of body, health, money, and circumstance, the
fated material substrate. Read **Spirit** for purpose, action, career, and
volition, what the person actively steers. A strong, well-ruled Fortune with a
weak Spirit is someone life hands things to who struggles to direct them; the
reverse is someone who makes their own luck against a difficult hand. (Ali's
Spirit, fittingly, lands at 4° Virgo in his **1st house**: his will was his identity.)

### Don't drown in lots

The formula machine can produce a lot for everything, which tempts beginners into
lot soup, the same mistake as [asteroid soup](./02_planets_and_points.md). Learn
Fortune and Spirit cold first. Reach for a topical lot (Eros, the marriage lot)
when you have a *question* it answers, not because the software will compute all
28.

> [!CAUTION]
> A historical wrinkle worth knowing: **Ptolemy used the same Fortune formula day
> and night** (no flip), while Valens and most of the tradition flipped it by
> sect. Stellium follows the majority sect-flipping convention. If your Fortune
> ever disagrees with another source by exactly the Sun-Moon distance, this
> day/night disagreement is usually why.

---

## In Stellium

> [!IMPORTANT]
> **Why `use_recorded_time=True`?** Lilly's birth time (02:00) is on record, and
> AstroDatabank rates it **A** — quoted by the person, in his own letter to Elias
> Ashmole. It also notes that *"the time may have been rectified by him"*, with
> Gadbury giving 2:00, Sibly 2:08 and Wangemann 3:00. Good provenance for a number
> he probably back-solved. So Stellium marks it `has_reliable_time: false` and, by
> default, builds him **unknown-time**: noon, no houses, no angles, no Lots.
>
> This chapter needs his houses, so it asks for the recorded time explicitly. The
> flag warns once and stamps `chart.metadata["time_provenance"]` onto the chart, so
> it can never quietly pass for a birth-certificate chart. **That is the honest way
> to work with a rectified time: use it, and never forget that you did.**

### Fortune, Spirit, and the whole set

```python
from stellium import ChartBuilder
from stellium.components import ArabicPartsCalculator, DignityComponent

# Add DignityComponent too, so we can read each lot through its ruler further down.
chart = (ChartBuilder.from_notable("William Lilly", use_recorded_time=True)
    .add_component(ArabicPartsCalculator())
    .add_component(DignityComponent(traditional=True))
    .calculate())

fortune = chart.get_object("Part of Fortune")
spirit  = chart.get_object("Part of Spirit")
print(fortune.sign_position, "house", chart.get_house("Part of Fortune"))
print(spirit.sign_position, "house", chart.get_house("Part of Spirit"))

all_lots = chart.get_component_result("Arabic Parts")
print(len(all_lots), "lots calculated")   # 28
```
<!--pytest-codeblocks:expected-output-->
```
7°15' Cancer house 5
26°52' Libra house 7
28 lots calculated
```

### The sect flip is automatic (but here's the proof)

```python
asc  = chart.get_object("ASC").longitude
sun  = chart.get_object("Sun").longitude
moon = chart.get_object("Moon").longitude

day_formula   = (asc + moon - sun) % 360    # 68.50  -> this is Lilly's SPIRIT
night_formula = (asc + sun - moon) % 360    # 192.30 -> this is Lilly's FORTUNE

print(chart.sect)                          # 'night'
print(round(chart.get_object("Part of Fortune").longitude, 2))   # 192.30
# night chart -> Fortune uses ASC + Sun - Moon, exactly as computed by hand
```

Because `chart.sect` is `night`, Stellium picked `ASC + Sun − Moon` for Fortune.
On a day chart it would pick the other formula. You never have to remember the
switch; you just have to trust that it's reading the sect.

### Reading a lot through its ruler

```python
from stellium import ChartBuilder
from stellium.components import ArabicPartsCalculator, DignityComponent
from stellium.utils.chart_ruler import get_sign_ruler

chart = (ChartBuilder.from_notable("William Lilly", use_recorded_time=True)
    .add_component(ArabicPartsCalculator())
    .add_component(DignityComponent(traditional=True))
    .calculate())

# Chase each lot to the ruler of its sign, and read that ruler's condition.
for lot in ("Part of Fortune", "Part of Spirit"):
    position = chart.get_object(lot)
    ruler = get_sign_ruler(position.sign)
    dignity = chart.get_planet_dignity(ruler, system="traditional")
    print(f"{lot}: {position.sign_position}, house {chart.get_house(lot)}")
    print(f"    ruled by {ruler} -> {dignity['score']:+d} {dignity['dignities']}")
```
<!--pytest-codeblocks:expected-output-->
```
Part of Fortune: 7°15' Cancer, house 5
    ruled by Moon -> -2 ['triplicity_ruler', 'detriment']
Part of Spirit: 26°52' Libra, house 7
    ruled by Venus -> +5 ['domicile']
```

That last line is the whole reading in three variables: Lilly's fortune is ruled
by a planet in its own sign. The [dignities
cookbook](../../../examples/dignities_cookbook.py) runs Fortune, Spirit, and the
topical lots alongside the dignity scoring they depend on.

---

## Going deeper

- **Prev:** [06 Dignity & Rulership](./06_dignity_and_rulership.md), which supplies
  the ruler-condition that turns a lot from a point into a reading.
- **The sect switch:** [05 Sect](./05_sect.md) is what flips the Fortune/Spirit
  formulas; the two chapters are a matched pair.
- **Timing with lots:** [15 Zodiacal Releasing](./15_zodiacal_releasing.md) uses
  the Lot of Fortune and the Lot of Spirit as its starting points, so this chapter
  is a prerequisite for the most powerful Hellenistic timing technique.

**Primary sources & further reading:**

- Chris Brennan, *Hellenistic Astrology* (2017), for the lots in their original
  role and the sect-flip debate laid out in full.
- Vettius Valens, *Anthology* (2nd century CE), the ancient source richest in lot
  technique.
- Robert Zoller, *The Arabic Parts in Astrology*, for the medieval "parts"
  tradition.
