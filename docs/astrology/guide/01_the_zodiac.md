# 01 · The Zodiac

> Part of the [Stellium Astrology Guide](../README.md). Code companion:
> [`examples/chart_cookbook.py`](../../../examples/chart_cookbook.py).
> Prerequisites: [00 Orientation](./00_orientation.md).

:::{admonition} 🚧 Draft chapter
:class: warning

This chapter is a draft. Its figures have not yet been checked against Stellium's
computed output — read it, but treat any specific degree, score or placement in it as
provisional.
:::

## The one-line version

The **zodiac** is the coordinate ring from [chapter 00](./00_orientation.md),
sliced into twelve 30° **signs**. A planet's sign is the *style* it operates in:
signs are the adverbs of the chart, the *how* behind every planet's *what*.

## A note on what a sign is not

A sign is not a personality type, and "I'm a Leo" is shorthand that hides how the
system actually works. You are not your Sun sign; you are ten-ish planets, each in
its own sign, each coloring a different function. Jung has his Sun in Leo, sure,
but his Moon is in Taurus and his Mercury is in Cancer, so his will expresses one
way, his feelings another, his mind a third. Learn signs as *modifiers you apply
to planets*, and the whole chart opens up. Learn them as twelve personality boxes
and you'll stay stuck at horoscope-column depth.

---

## A brief history

The twelve-sign zodiac is **Babylonian**. By around the 5th century BCE,
Mesopotamian astronomers had taken the ragged band of constellations the Sun
passes through and regularized it into twelve equal 30° segments, a clean
coordinate system laid over the messy real sky. The signs kept the constellations'
names and images (the ram, the bull, the twins), but from the start the *signs*
were tidy math and the *constellations* were the lumpy originals. That distinction
matters more than almost anything else in this chapter, so hold onto it.

The **elements** (fire, earth, air, water) came from Greek natural philosophy,
mapped onto the signs in the Hellenistic period as the **triplicities**. The
**modalities** (cardinal, fixed, mutable) came from the same era, keyed to the
seasons: cardinal signs *start* the seasons, fixed signs sit in their *middle*,
mutable signs *end and transition* them.

Then precession split the zodiac in two. Around 127 BCE, Hipparchus noticed that
the equinox point drifts slowly backward against the stars (about 1° every 72
years, a wobble in Earth's axis). This forced a choice about what 0° Aries should
be anchored to. Ptolemy, codifying Western astrology in the 2nd century CE, tied
it to the **spring equinox**, giving the **tropical** zodiac. Indian astrology
kept it tied to the **stars**, giving the **sidereal** zodiac. Two thousand years
of drift later, the two rings sit about 24° apart, and that gap is the single
biggest technical fork in world astrology. We'll settle it below.

---

## The theory

### The twelve signs

Each sign is a unique blend of an element (its substance), a modality (its way of
moving), and a ruling planet (its inner boss). The keyphrases are the traditional
"I" mottos, a beginner's shortcut to the core drive.

| Sign | Element | Modality | Ruler (trad.) | Core |
|---|---|---|---|---|
| Aries ♈ | Fire | Cardinal | Mars | "I am." Initiative, drive, the raw self. |
| Taurus ♉ | Earth | Fixed | Venus | "I have." Stability, the senses, worth. |
| Gemini ♊ | Air | Mutable | Mercury | "I think." Curiosity, language, plurality. |
| Cancer ♋ | Water | Cardinal | Moon | "I feel." Care, memory, belonging. |
| Leo ♌ | Fire | Fixed | Sun | "I will." Expression, pride, creativity. |
| Virgo ♍ | Earth | Mutable | Mercury | "I analyze." Refinement, service, craft. |
| Libra ♎ | Air | Cardinal | Venus | "I balance." Relationship, fairness, form. |
| Scorpio ♏ | Water | Fixed | Mars | "I desire." Depth, intensity, the hidden. |
| Sagittarius ♐ | Fire | Mutable | Jupiter | "I seek." Meaning, distance, faith. |
| Capricorn ♑ | Earth | Cardinal | Saturn | "I build." Ambition, structure, mastery. |
| Aquarius ♒ | Air | Fixed | Saturn | "I know." Ideals, systems, the collective. |
| Pisces ♓ | Water | Mutable | Jupiter | "I believe." Compassion, dissolution, dream. |

Modern astrology adds three rulers from the outer planets: Uranus for Aquarius,
Neptune for Pisces, Pluto for Scorpio. Whether to use traditional or modern
rulerships is a real choice, and [chapter 06](./06_dignity_and_rulership.md) does
it properly. For now, notice the elegance of the traditional scheme: the two
lights (Sun, Moon) rule one sign each (Leo, Cancer), and the other five planets
rule two apiece, fanning out symmetrically from there.

### The twelve signs are every combination of four elements and three modalities

Here is the structure that makes the zodiac feel designed rather than arbitrary.
Four elements times three modalities equals twelve, and *every* sign is a unique
pairing. No combination repeats, none is missing:

| | Cardinal | Fixed | Mutable |
|---|---|---|---|
| **Fire** | Aries | Leo | Sagittarius |
| **Earth** | Capricorn | Taurus | Virgo |
| **Air** | Libra | Aquarius | Gemini |
| **Water** | Cancer | Scorpio | Pisces |

Read a sign straight off the grid and you already know most of it. Scorpio is
Water plus Fixed: sustained (fixed) emotional depth (water). Sagittarius is Fire
plus Mutable: restless (mutable) enthusiasm (fire). You don't have to memorize
twelve personalities, you have to learn four elements, three modalities, and how
they combine.

**The four elements** are the *what it's made of*:

- **Fire** (Aries, Leo, Sagittarius): energy, spirit, enthusiasm, action.
- **Earth** (Taurus, Virgo, Capricorn): matter, practicality, the body, results.
- **Air** (Gemini, Libra, Aquarius): mind, ideas, language, connection.
- **Water** (Cancer, Scorpio, Pisces): feeling, intuition, depth, the unconscious.

**The three modalities** are the *how it moves*:

- **Cardinal** (Aries, Cancer, Libra, Capricorn): initiating. Starts things.
- **Fixed** (Taurus, Leo, Scorpio, Aquarius): sustaining. Holds and stabilizes.
- **Mutable** (Gemini, Virgo, Sagittarius, Pisces): adapting. Bends and transitions.

There's also **polarity**, alternating around the wheel: fire and air signs are
*active/yang* (traditionally "masculine" or "diurnal"), earth and water signs are
*receptive/yin* ("feminine" or "nocturnal"). Aries is active, Taurus receptive,
Gemini active, and so on. It's a coarse layer, but it's the reason fire-and-air
charts read as outward and earth-and-water charts as inward.

### The two zodiacs, and the gap between them

Now the fork the history set up. Both zodiacs are twelve equal 30° signs. They
differ only in *where they put 0° Aries*.

- The **tropical zodiac** anchors 0° Aries to the **spring equinox**. It measures
  a planet's position relative to the *seasons*, the Sun-Earth relationship. This
  is Western astrology's default.
- The **sidereal zodiac** anchors 0° Aries to the **fixed stars**. It measures
  position relative to the actual constellations. This is Vedic astrology's
  default.

Because the equinox precesses (drifts backward ~1° per 72 years), the two anchors
have pulled apart by roughly 24° over the last two millennia. That offset is
called the **ayanamsa**. It is not small: it's most of a sign. A planet at 3° Leo
in the tropical zodiac sits back around 11° Cancer in the sidereal one. Same
planet, same sky, different label, because the two rings start in different
places.

The ayanamsa isn't a single agreed number, either. Different schools anchor
sidereal 0° to slightly different reference stars, so they disagree by a degree or
two. **Lahiri** (the Indian government standard, and Stellium's sidereal default)
anchors near the star Spica; **Fagan-Bradley** is the main Western sidereal
standard; Stellium ships nine in total. The differences only matter much near a
sign cusp, where a degree can flip a placement.

---

## In practice

### Reading a sign, and then a whole chart

To read one placement, stack its three facts. Jung's Moon in Taurus is Water?
No: Taurus is Earth plus Fixed, ruled by Venus. So his emotional life (Moon) is
grounded, sensual, slow to shift, and steadying (Earth plus Fixed plus Venus).
That's a man whose feelings were a bedrock, not weather.

To read the *whole* chart, count the balance. Tally how many planets fall in each
element and each modality, and the imbalances tell you as much as any single
placement. Jung is a clean example. His ten planets split fairly evenly by element
(three Fire, three Earth, two Air, two Water), but by modality he is lopsided:
**six of ten planets are fixed, and only one is mutable.** A fixed-dominant chart
is persistent, deep, hard to move, and allergic to changing course. For a man who
spent fifty years deepening a single vision of the psyche and was famously
immovable once he'd decided something, that six-fixed signature is almost on the
nose. A *missing* element or modality is just as loud: with one mutable planet,
easy adaptability was never his native gift.

### The tropical-vs-sidereal question, honestly

> [!NOTE]
> **Tropical and sidereal are parallel frameworks, not rival accuracy claims.**
> They measure two different real things, so neither is "the real one." Don't
> blend them in one reading: Western astrology uses tropical, Vedic uses sidereal.

Here's the calm version of a debate beginners expect to be a fight. Tropical asks
*where was the Sun relative to the seasons*, which is why a tropical Leo is born
at a particular point in the solar year. Sidereal asks *where was the Sun relative
to the stars*, which is why a sidereal reading tracks the actual constellations.
Neither is "the real one," because they aren't answering the same question.

The genuine arguments, so you know the shape of the disagreement:

- **The tropical case:** the signs' meanings were built from the seasons. Aries is
  cardinal fire because it's the green surge of spring; Capricorn is the depth of
  winter. Cut the signs loose from the seasons and you cut them loose from the
  logic that gave them meaning. So the tropical camp keeps them pinned to the
  equinox.
- **The sidereal case:** the signs are named for constellations, so they should
  point at those constellations. A "Leo" whose Sun is sitting in the stars of
  Cancer is, to a sidereal astrologer, mislabeled. So the sidereal camp keeps them
  pinned to the stars.

Both are internally coherent. In practice: if you're doing Western astrology, use
tropical; if you're doing Vedic, use sidereal; and don't blend them in a single
reading, because they're different measuring sticks. This is the one place I'll
push a default rather than stay neutral, because the frameworks come as packages,
and half of each doesn't make a whole.

### Defusing the two famous headlines

- **"Ophiuchus is a 13th sign!"** No. The Sun passes through thirteen
  *constellations*, but the *zodiac* (tropical and sidereal alike) is twelve equal
  30° *signs* by definition. This headline confuses constellations with signs, the
  exact distinction from the history section. There is no 13th sign because the
  zodiac was never the constellations in the first place.
- **"You're not really your sign, it shifted!"** This is just precession. If
  you're a tropical Leo, the Sun at your birth really was in the constellation
  Cancer (that's your sidereal sign). Both are true, in their own frame. Nothing
  shifted out from under you; the two systems were always ~24° apart.

---

## In Stellium

Tropical is the default, so a plain chart is already a Western tropical chart.

### Signs, and their element and modality

```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Carl Jung").calculate()

sun = chart.get_object("Sun")
print(sun.sign)             # Leo
print(sun.sign_position)    # 3°18' Leo
print(f"{sun.longitude:.4f}")  # the raw coordinate underneath
```
<!--pytest-codeblocks:expected-output-->
```
Leo
3°18' Leo
123.3053
```

Element and modality aren't a single field, but they're a two-line lookup, and
counting them across the chart is the balance technique from above:

```python
from collections import Counter

ELEMENT = {"Aries":"Fire","Leo":"Fire","Sagittarius":"Fire",
           "Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth",
           "Gemini":"Air","Libra":"Air","Aquarius":"Air",
           "Cancer":"Water","Scorpio":"Water","Pisces":"Water"}
MODALITY = {"Aries":"Cardinal","Cancer":"Cardinal","Libra":"Cardinal","Capricorn":"Cardinal",
            "Taurus":"Fixed","Leo":"Fixed","Scorpio":"Fixed","Aquarius":"Fixed",
            "Gemini":"Mutable","Virgo":"Mutable","Sagittarius":"Mutable","Pisces":"Mutable"}

planets = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
elements = Counter(ELEMENT[chart.get_object(p).sign] for p in planets)
modes    = Counter(MODALITY[chart.get_object(p).sign] for p in planets)
print(dict(elements))   # {'Fire': 3, 'Earth': 3, 'Water': 2, 'Air': 2}
print(dict(modes))      # {'Fixed': 6, 'Cardinal': 3, 'Mutable': 1}  <- fixed-dominant
```

(If you install the analysis extra, `stellium.analysis.ChartStats` will compute
element and modality distributions across many charts for you; see
**chapter 23** *(not yet written)*.)

### Switching to the sidereal zodiac

```python
from stellium import ChartBuilder

trop = ChartBuilder.from_notable("Carl Jung").calculate()
sid  = ChartBuilder.from_notable("Carl Jung").with_sidereal("lahiri").calculate()

sun_t = trop.get_object("Sun")
sun_s = sid.get_object("Sun")
print("Tropical:", sun_t.sign_position)   # 3°18' Leo
print("Sidereal:", sun_s.sign_position)   # 11°11' Cancer
print(f"Ayanamsa: {sun_t.longitude - sun_s.longitude:.1f}°")   # ~22.1  (for 1875)
```
<!--pytest-codeblocks:expected-output-->
```
Tropical: 3°18' Leo
Sidereal: 11°11' Cancer
Ayanamsa: 22.1°
```

His Sun crosses a whole sign, Leo to Cancer, when you change the ring. That single
line of output is the entire tropical-vs-sidereal debate in miniature.

### Choosing an ayanamsa

```python
from stellium import ChartBuilder
from stellium.core.ayanamsa import list_ayanamsas

print(list_ayanamsas())

chart = ChartBuilder.from_notable("Carl Jung").with_sidereal("fagan_bradley").calculate()
print(chart.get_object("Sun").sign_position)
```
<!--pytest-codeblocks:expected-output-->
```
['deluce', 'fagan_bradley', 'jn_bhasin', 'krishnamurti', 'lahiri', 'raman', 'true_citra', 'true_revati', 'yukteshwar']
10°18' Cancer
```

`with_tropical()` switches back explicitly. The full ayanamsa reference, with what
each one anchors to, is in
[`docs/options_list.md`](../../options_list.md#ayanamsas--sidereal-zodiacs-9-systems),
and the sidereal machinery gets its full workout in the Vedic chapter
(**21** *(not yet written)*).

---

## Going deeper

- **Next:** [02 Planets & Points](./02_planets_and_points.md) covers the *what*
  that the signs are styling.
- **Rulership in depth:** [06 Dignity & Rulership](./06_dignity_and_rulership.md)
  builds on the sign rulers here into the full essential-dignity system (a planet
  is strong or weak partly by which sign it's in).
- **The sidereal world:** **21 Vedic / Jyotish** *(not yet written)* is where the
  sidereal zodiac is the home team, not the alternative.

**Further reading:**

- Chris Brennan, *Hellenistic Astrology* (2017), on the seasonal logic of the
  signs and the tropical/sidereal split.
- Deborah Houlding's writing on the elements and modalities for the traditional
  reasoning behind the grid.
- On precession and the ayanamsa, any good positional-astronomy reference; the
  Swiss Ephemeris documentation covers the sidereal modes Stellium wraps.
