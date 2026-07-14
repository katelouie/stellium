# 04 · Aspects

> Part of the [Stellium Astrology Guide](../README.md). Code companion:
> [`examples/aspects_and_orbs_cookbook.py`](../../../examples/aspects_and_orbs_cookbook.py).
> Prerequisites: [01 The Zodiac](./01_the_zodiac.md),
> [02 Planets & Points](./02_planets_and_points.md), [03 Houses](./03_houses.md).


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

An **aspect** is a meaningful angle between two planets. If houses tell you
*where* a planet acts and signs tell you *how*, aspects tell you *who a planet is
in conversation with*, and whether that conversation is easy, tense, or fused.

## The example for this chapter, and why he has no birth time

This chapter runs on **Wong Kar-wai**, the Hong Kong filmmaker (*In the Mood for
Love*, *Chungking Express*, *Happy Together*). He's here on purpose, because his
birth time is unknown. The chart Stellium builds for him uses 12:00 noon as a
placeholder, which means his houses and his Ascendant are fiction: they would
rotate to something completely different if we learned he was born at 4pm.

Here is the thing a lot of astrologers won't tell you: you can still read that
chart, and read it well. Aspects between planets barely care about the birth
time. Mars is at 27° Aries whether he was born at dawn or midnight; Jupiter is at
22° Libra either way; the angle between them is fixed. Almost everything in this
chapter, the entire aspect layer, survives a missing birth time intact. The only
casualties are aspects involving the fast-moving Moon (whose exact degree shifts
up to ~13° across a day) and aspects to the Ascendant and Midheaven (which are
pure birth-time artifacts). Set those aside and Wong Kar-wai's chart still hands
you a T-square, a mystic rectangle, and a dozen tight planetary conversations.
That is most of a delineation, with no time at all.

So this chapter does double duty. It teaches aspects, and it quietly makes the
case that "we don't have a birth time" is the start of the reading, not the end
of it.

---

## A brief history

### Aspects began as sightlines

The Greek word behind "aspect" is about *looking*. In Hellenistic astrology
(roughly the 1st century BCE onward), two planets were in aspect if their signs
could "see" each other, and in **aversion** if they could not. This was not a
metaphor they were casual about: a planet you are averse to is a planet you
cannot deal with directly, turned to an angle where you cannot meet its eye.

Which signs could see each other? The ones connected by the tidy geometric
divisions of the circle. Ptolemy (2nd century CE, in the *Tetrabiblos*)
formalized the five that survived as the **major** or **Ptolemaic** aspects, and
they come straight out of dividing 360° by small whole numbers:

- Divide by 1: **conjunction** (0°), same place.
- Divide by 2: **opposition** (180°).
- Divide by 3: **trine** (120°).
- Divide by 4: **square** (90°).
- Divide by 6: **sextile** (60°).

Notice what is missing: 30° and 150°. Signs one apart or five apart (the
semisextile and the quincunx) were precisely the aversions, the angles where two
signs share no element, no modality, and no polarity, and so genuinely cannot see
each other. Classical astrology did not count them as aspects at all. When modern
astrology later adopted them as "minor aspects," it was overturning a deliberate
exclusion, not filling an oversight.

### Kepler turned aspects into music

The next big move was Johannes Kepler (17th century), who happened to be a
working astrologer as well as the man who worked out how planets orbit. Kepler
argued the aspects were not arbitrary sacred angles but *harmonics*, the same
whole-number ratios that make musical intervals sound consonant. Dividing the
circle by 5 gave him the **quintile** (72°); other divisions gave the rest of the
minor and harmonic aspects. This reframing, aspects as the harmonic division of
the circle, is the seed of everything that came later.

### The 20th century opened the floodgates

John Addey built Kepler's hunch into full **harmonic theory** in the mid-1900s,
proposing that harmonics underlie *all* of astrology. Meanwhile the Uranian
school and cosmobiology leaned hard on the 45° and 135° aspects (the semisquare
and sesquiquadrate), and modern astrologers folded in the quincunx as the aspect
of awkward adjustment. The result is the menu Stellium implements: five majors,
four minors, three harmonic families, and the declination aspects. More aspects
mean more sensitivity and more noise, and where you draw the line is one of the
real stylistic choices in astrology (more on that below).

---

## The theory

### An aspect is an angle, plus a tolerance

Two planets are in aspect when the angular distance between them (measured along
the ecliptic) lands near one of the significant angles. "Near," not "exactly,"
because aspects have **orbs**: a margin of allowance around the exact angle
within which the aspect still counts. A trine is exact at 120°, but two planets
118° or 123° apart are still trine, just less precisely. The tighter the orb, the
louder the aspect. An aspect at 0.3° of orb is doing far more in the chart than
one straining at 7°.

### The five majors and what they feel like

| Aspect | Angle | Nature | The one-liner |
|---|---|---|---|
| Conjunction | 0° | fusion | Two planets become one voice. Whether that is good depends entirely on who's talking. |
| Sextile | 60° | easy, active | Opportunity that needs a nudge. Talent you have to choose to use. |
| Square | 90° | tension | Friction that forces action. The aspect of getting things done by banging into them. |
| Trine | 120° | flow | Natural ease and talent, sometimes so easy you never develop it. |
| Opposition | 180° | polarity | Awareness through the other. Balance, projection, or tug-of-war. |

The modern shorthand sorts these into **soft** (sextile, trine: flowing, easy)
and **hard** (square, opposition: dynamic, challenging), with the conjunction
neutral because it just intensifies whatever it touches. It's a useful shorthand
as long as you don't over-moralize it. Hard aspects build the muscle; a chart
made only of trines can be talented and inert. The traditional view was subtler
still, keyed to whether the signs involved shared an element or a modality, but
soft and hard will carry you a long way.

### The minors and harmonics, briefly

- **Minor aspects:** semisextile (30°), semisquare (45°), sesquiquadrate (135°),
  quincunx (150°). Quieter, and used at tighter orbs. The **quincunx** is the
  memorable one: two planets that share nothing and must constantly recalibrate
  to work together, the astrological equivalent of a persistent slight misfit.
- **Harmonic aspects:** the quintile family (72°, creativity and personal
  talent), the septile family (~51°, fate, inspiration, the numinous), the novile
  family (40°, gestation and spiritual completion). These come from Kepler and
  Addey's harmonic view and are specialist tools, not everyday reading.

### Applying vs separating: is it building or fading?

This is the piece beginners skip and traditionalists live by. If the faster
planet is still moving *toward* the exact aspect, the aspect is **applying**: it
is building, gaining strength, oriented to what's coming. If the faster planet
has already passed exactness and is moving away, the aspect is **separating**:
waning, spending itself, oriented to what's done. Traditional astrology weights
applying aspects more heavily, treating them as the ones with real force.
Stellium computes this for you from the planets' relative speeds and marks each
aspect applying or separating.

---

## In practice

### How to prioritize (because every chart has too many aspects)

A real chart throws dozens of aspects at you. The craft is triage:

1. **Tightest orbs first.** A 0.3° aspect is a headline; a 6° aspect is
   background texture.
2. **Aspects to the Sun, the Moon, and (if you trust the time) the angles and the
   chart ruler.** These involve the load-bearing points.
3. **Applying over separating**, if you work traditionally.
4. **Hard aspects often shout louder than soft ones.** They are where the person
   feels friction, and friction is what people notice.

### The major-vs-minor line is a real stylistic fork

Traditional astrologers often use *only* the five Ptolemaic aspects, at tight
orbs, and ignore the rest. Harmonic and modern astrologers use a wide menu of
minors. Neither is wrong; they are different resolutions of the same picture. My
advice for a beginner: learn to read the five majors fluently before you touch a
single quincunx. The majors carry most of the signal, and a chart drowned in
minor aspects is a chart you can't prioritize.

### Aspect patterns: when three or more planets lock together

Individual aspects are conversations. **Aspect patterns** are the recurring group
dynamics, geometric figures formed when three or more planets aspect each other
in a named shape. They are worth learning because a pattern is more than the sum
of its aspects; it has its own behavior.

- **Stellium:** three or more planets piled together. Overwhelming focus in one
  sign or house.
- **Grand Trine:** three planets in a triangle of trines, all one element.
  Enormous ease, and a tendency to coast on it.
- **T-Square:** two planets opposed, both square a third. The third planet (the
  **apex**) is the pressure valve where the tension discharges. Driven, restless,
  productive under strain.
- **Grand Cross:** four planets, two oppositions, all squaring each other. A
  T-square with a fourth arm. Maximum tension, pulled four directions.
- **Yod** ("finger of fate"): two planets in sextile, both quincunx a third. The
  apex becomes a focal point of fated, must-be-worked-out adjustment.
- **Mystic Rectangle:** two oppositions laced together by trines and sextiles. A
  container: it channels the strain of the oppositions through the ease of the
  soft aspects, so the tension has somewhere productive to go.
- **Kite:** a grand trine with a fourth planet opposing one corner, giving the
  otherwise self-contained trine a point of release.

### Reading the patterns off an unknown-time chart: Wong Kar-wai

Here is the promised payoff. Wong Kar-wai has no verified birth time, and yet his
planetary aspects give us two clean, powerful patterns, both completely
independent of the missing time.

**A cardinal T-square: Mars opposite Jupiter, apex Sun.** His Mars (27° Aries)
opposes his Jupiter (22° Libra) across the me/we axis, and his Sun (24° Cancer)
squares both from the apex. All three sit in cardinal signs (Aries, Libra,
Cancer), the signs of initiation and crisis. A cardinal T-square is a restless
engine: it can't sit still, and it resolves tension by *starting things*. The
apex is the Sun in Cancer, the sign of memory and longing, so all that driving
tension pours out through a Cancerian preoccupation with the past, with what's
lost, with the ache of what didn't happen. If you have ever seen one of his
films, you have seen this T-square running. None of it required knowing when he
was born.

**A mystic rectangle: Jupiter, Venus, Saturn, Mars.** Two oppositions (Jupiter in
Libra opposite Mars in Aries; Venus in Gemini opposite Saturn in Sagittarius),
woven together by trines and sextiles into a closed, self-reinforcing figure. His
aesthetic sense (Venus), his reach for meaning and beauty (Jupiter), his formal
discipline (Saturn), and his restless desire (Mars) are locked in one loop where
each feeds the others. That closed circuit is a fair description of an auteur's
signature style rendered as geometry, and again, no birth time needed.

> [!CAUTION]
> **Don't trust raw pattern counts.** Run the detector on his chart and it reports
> **22 T-squares and 9 mystic rectangles**. There are really about *two*
> T-squares and *one* rectangle. Conjunct points get counted as separate vertices
> and the figures multiply combinatorially, so collapse the duplicates by eye.

The inflation comes from three stacked conjunctions: his Mars sits right on his
South Node (and so opposes his North Node), his Sun sits on his Moon (that New
Moon again), and in the noon chart his Ascendant sits on his Jupiter. Every one of
those conjunct points becomes an interchangeable corner, and the detector
faithfully recombines them into dozens of near-identical figures. This is a
genuinely useful lesson in reading software output: **conjunctions inflate
pattern counts combinatorially**, so you collapse the duplicates by eye. The two
real T-squares are the cardinal Jupiter-Mars-Sun one above and a second,
mixed-modality one that swaps in Neptune (which also opposes Mars) for Jupiter.
The nine rectangles are one figure wearing nine costumes.

**What we don't get to trust.** His report also lists a Sun-Moon-MC "stellium."
The real content there is a **New Moon in Cancer** (Sun 24° Cancer, Moon 29°
Cancer, born within about 5° of an exact new moon), which is a genuine and
evocative signature: a self-contained, instinct-driven person born at the dark of
the moon, seeding things from inside himself. But the "MC" leg of that stellium is
a noon artifact, and the Moon at 29° Cancer sits right at the sign's edge. Ask
Stellium how uncertain that Moon really is and it will tell you the exact range:
anywhere from **22° Cancer to 6° Leo** across the unknown day, a full sign of
wobble. Read the New Moon; ignore the MC; hold the Moon loosely. That triage,
knowing which parts of a chart survive a missing time and which don't, is the
whole skill this chapter is quietly teaching.

---

## In Stellium

Aspects are opt-in. Call `.with_aspects()` (or a preset that does) or
`chart.aspects` comes back empty.

### Basic aspects

```python
from stellium import ChartBuilder

# Wong Kar-wai: no verified birth time, stored as a 12:00 noon chart.
chart = ChartBuilder.from_notable("Wong Kar-wai").with_aspects().calculate()

# Every aspect, sorted loudest (tightest orb) first, with applying/separating.
for asp in sorted(chart.aspects, key=lambda a: a.orb):
    if asp.is_applying is True:
        direction = "applying"
    elif asp.is_applying is False:
        direction = "separating"
    else:
        direction = "exact/stationary"
    print(f"{asp.object1.name:12} {asp.aspect_name:12} {asp.object2.name:12} "
          f"orb {asp.orb:4.2f}°  {direction}")
```
<!--pytest-codeblocks:expected-output-->
```
Mars         Opposition   True Node    orb 0.31°  separating
Mars         Conjunction  South Node   orb 0.31°  separating
Venus        Trine        Jupiter      orb 1.04°  separating
Mercury      Trine        Saturn       orb 1.05°  applying
Sun          Square       Jupiter      orb 1.18°  separating
Neptune      Sextile      Pluto        orb 1.22°  exact/stationary
Saturn       Sextile      Chiron       orb 1.31°  separating
Jupiter      Trine        Chiron       orb 1.40°  separating
Moon         Square       Mars         orb 1.77°  separating
Moon         Square       True Node    orb 2.07°  separating
Moon         Square       South Node   orb 2.07°  separating
Mercury      Opposition   Chiron       orb 2.36°  applying
Venus        Trine        Chiron       orb 2.45°  separating
Jupiter      Sextile      Saturn       orb 2.71°  separating
Mercury      Trine        Mean Apogee  orb 2.77°  separating
Moon         Square       Neptune      orb 2.88°  exact/stationary
Sun          Square       True Node    orb 2.97°  applying
Sun          Square       South Node   orb 2.97°  applying
Venus        Trine        True Node    orb 3.11°  applying
Venus        Sextile      South Node   orb 3.11°  applying
Sun          Square       Mars         orb 3.28°  applying
Venus        Sextile      Mars         orb 3.41°  applying
Mars         Trine        Pluto        orb 3.42°  applying
Pluto        Sextile      True Node    orb 3.73°  separating
Pluto        Trine        South Node   orb 3.73°  applying
Venus        Opposition   Saturn       orb 3.76°  separating
Mercury      Sextile      Jupiter      orb 3.76°  applying
Saturn       Trine        Mean Apogee  orb 3.81°  applying
Jupiter      Conjunction  True Node    orb 4.15°  applying
Jupiter      Opposition   South Node   orb 4.15°  separating
Mars         Opposition   Jupiter      orb 4.46°  separating
Mars         Opposition   Neptune      orb 4.65°  exact/stationary
Mercury      Sextile      Venus        orb 4.81°  applying
Neptune      Conjunction  True Node    orb 4.95°  exact/stationary
Neptune      Opposition   South Node   orb 4.95°  exact/stationary
Sun          Conjunction  Moon         orb 5.05°  separating
Chiron       Sextile      Mean Apogee  orb 5.13°  applying
Uranus       Trine        Mean Apogee  orb 5.54°  separating
True Node    Trine        Chiron       orb 5.55°  applying
Chiron       Sextile      South Node   orb 5.55°  separating
Mars         Sextile      Chiron       orb 5.86°  separating
Moon         Square       Jupiter      orb 6.22°  separating
Jupiter      Opposition   Mean Apogee  orb 6.53°  applying
Saturn       Trine        South Node   orb 6.86°  separating
Mars         Trine        Saturn       orb 7.17°  separating
Sun          Square       Mean Apogee  orb 7.70°  separating
Mercury      Trine        South Node   orb 7.91°  applying
Sun          Square       Neptune      orb 7.93°  exact/stationary
```

The tightest few are his Sun-MC conjunction (0.03°, a noon artifact, ignore it),
Mars conjunct South Node (0.31°), Jupiter conjunct Ascendant (another artifact),
Chiron trine Ascendant (artifact), then Venus trine Jupiter (1.04°). Sorting by
orb is the fastest way to see which conversations are loudest, and which are just
the noon placeholder talking.

### Filtering to what you can trust on an unknown-time chart

```python
# Drop anything touching a time-sensitive point (angles + Moon),
# so you're left with the robust planet-to-planet aspects.
TIME_SENSITIVE = {"ASC", "MC", "DSC", "IC", "Vertex", "Moon"}

robust = [
    a for a in chart.aspects
    if a.object1.name not in TIME_SENSITIVE
    and a.object2.name not in TIME_SENSITIVE
]
for asp in sorted(robust, key=lambda a: a.orb):
    print(f"{asp.object1.name:10} {asp.aspect_name:12} {asp.object2.name:10} {asp.orb:.2f}°")
```

That leaves 42 of his 68 aspects, and the real reading is right at the top:
Mars-South Node (0.31°), Venus-Jupiter (1.04°), Mercury-Saturn (1.05°),
Jupiter-Sun (the square, 1.18°), Neptune-Pluto (1.22°, generational, so discount
it), then Saturn-Chiron and Jupiter-Chiron. None of it can be taken away by a
missing birth time.

### Aspect patterns

```python
from stellium import ChartBuilder, ReportBuilder
from stellium.engines.patterns import AspectPatternAnalyzer

chart = (ChartBuilder.from_notable("Wong Kar-wai")
    .with_aspects()
    .add_analyzer(AspectPatternAnalyzer())
    .calculate())

# Patterns surface in the report's aspect-patterns section (prints to terminal).
(ReportBuilder().from_chart(chart)
    .with_aspect_patterns()
    .render(format="rich_table"))
```
<!--pytest-codeblocks:expected-output-->
```

Aspect Patterns
───────────────
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern          ┃ Planets                           ┃ Element/Quality ┃ Details                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Mystic Rectangle │ ☿ Mercury, ⚷ Chiron, ♀ Venus, ♄   │ —               │ 4 planets               │
│                  │ Saturn                            │                 │                         │
│ Mystic Rectangle │ ☿ Mercury, ⚷ Chiron, ♃ Jupiter, ⚸ │ —               │ 4 planets               │
│                  │ Black Moon Lilith                 │                 │                         │
│ Mystic Rectangle │ ☿ Mercury, ⚷ Chiron, ♃ Jupiter, ☋ │ —               │ 4 planets               │
│                  │ South Node                        │                 │                         │
│ Mystic Rectangle │ ♀ Venus, ♄ Saturn, ♂ Mars, ♃      │ —               │ 4 planets               │
│                  │ Jupiter                           │                 │                         │
│ Mystic Rectangle │ ♀ Venus, ♄ Saturn, ♃ Jupiter, ☋   │ —               │ 4 planets               │
│                  │ South Node                        │                 │                         │
│ T-Square         │ ♂ Mars, ♃ Jupiter, ☉ Sun          │ Cardinal        │ 3 planets, Apex: ☉ Sun  │
│ T-Square         │ ♂ Mars, ♃ Jupiter, ☽ Moon         │ Cardinal        │ 3 planets, Apex: ☽ Moon │
│ T-Square         │ ♂ Mars, ♆ Neptune, ☉ Sun          │ Mixed           │ 3 planets, Apex: ☉ Sun  │
│ T-Square         │ ♂ Mars, ♆ Neptune, ☽ Moon         │ Mixed           │ 3 planets, Apex: ☽ Moon │
│ T-Square         │ ♂ Mars, ☊ North Node, ☉ Sun       │ Cardinal        │ 3 planets, Apex: ☉ Sun  │
│ T-Square         │ ♂ Mars, ☊ North Node, ☽ Moon      │ Cardinal        │ 3 planets, Apex: ☽ Moon │
│ T-Square         │ ♃ Jupiter, ⚸ Black Moon Lilith, ☉ │ Cardinal        │ 3 planets, Apex: ☉ Sun  │
│                  │ Sun                               │                 │                         │
│ T-Square         │ ♃ Jupiter, ☋ South Node, ☉ Sun    │ Cardinal        │ 3 planets, Apex: ☉ Sun  │
│ T-Square         │ ♃ Jupiter, ☋ South Node, ☽ Moon   │ Cardinal        │ 3 planets, Apex: ☽ Moon │
│ T-Square         │ ♆ Neptune, ☋ South Node, ☉ Sun    │ Mixed           │ 3 planets, Apex: ☉ Sun  │
│ T-Square         │ ♆ Neptune, ☋ South Node, ☽ Moon   │ Mixed           │ 3 planets, Apex: ☽ Moon │
└──────────────────┴───────────────────────────────────┴─────────────────┴─────────────────────────┘
```

Remember the caveat: this prints 22 T-squares and 9 mystic rectangles, which are
really about two and one. The detector counts conjunct points (Mars on the South
Node, Sun on the Moon, ASC on Jupiter) as separate vertices, so collapse the
duplicates by eye.

### Choosing your aspects and orbs

```python
from stellium import ChartBuilder
from stellium.engines import ModernAspectEngine, LuminariesOrbEngine
from stellium.core.config import AspectConfig

# Only the five Ptolemaic majors (the traditional, tight-orb approach).
majors = AspectConfig(aspects=["Conjunction", "Sextile", "Square", "Trine", "Opposition"])

chart = (ChartBuilder.from_notable("Wong Kar-wai")
    .with_aspects(ModernAspectEngine(majors))
    .with_orbs(LuminariesOrbEngine())   # wider orbs for the Sun & Moon
    .calculate())
```

Swap `LuminariesOrbEngine` for `SimpleOrbEngine` (flat orbs), `ComplexOrbEngine`
(per-pair rules), or `MoietyOrbEngine` (traditional moiety orbs). For harmonic
aspects (quintiles, septiles, noviles), use `HarmonicAspectEngine(harmonic=5)`.
The full menu of 26 aspects and their default orbs lives in
[`docs/options_list.md`](../../options_list.md#aspects-26-aspects), and the
[aspects & orbs cookbook](../../../examples/aspects_and_orbs_cookbook.py) works
through all four orb engines.

### Handling the unknown time honestly

The noon chart quietly lies about houses and angles. If you'd rather Stellium
*refuse* to draw fictional houses, build the chart with `with_unknown_time()`:

```python
chart = (ChartBuilder.from_notable("Wong Kar-wai")
    .with_unknown_time()
    .with_aspects()
    .calculate())
# Returns an UnknownTimeChart: no houses, no ASC/MC, and a `moon_range`
# (here: Cancer 22° to Leo 6°, a full sign of uncertainty) instead of a
# single Moon position. Your planet-to-planet aspects still work.

print(chart.moon_range)          # Moon: Cancer 22° - Leo 6° (arc: 13.8°)
print(chart.get_houses())        # None: it won't invent houses it can't know
```

That is the principled version of everything this chapter argued: keep the
aspects, drop the pretend angles, and let the Moon be a range instead of a false
certainty. (More on unknown-time charts in [chapter 00](./00_orientation.md).)

---

## Going deeper

- **Prev:** [03 Houses](./03_houses.md) placed the planets. Aspects connect them.
- **Chart shape:** **20 Chart Shapes** *(not yet written)* zooms out from
  individual patterns to the whole chart's silhouette.
- **Declination aspects:** **10 Declination** *(not yet written)* covers parallels
  and contraparallels, aspects measured north-south instead of around the zodiac.
- **Orbs in depth:** the [aspects & orbs cookbook](../../../examples/aspects_and_orbs_cookbook.py)
  is the code-side companion, with all four orb engines and the traditional
  moiety system.
- **Unknown-time charts:** [00 Orientation](./00_orientation.md) for the full
  treatment of reading a chart without a time.

**Primary sources & further reading:**

- Ptolemy, *Tetrabiblos*, Book I, for the classical aspect doctrine and aversion.
- Johannes Kepler, *Harmonices Mundi* (1619), for aspects as harmonic ratios.
- John Addey, *Harmonics in Astrology* (1976), for the modern harmonic revival.
- Bernadette Brady, *Predictive Astrology*, for aspect patterns in working
  practice.
