# 06 · Dignity & Rulership

> Part of the [Stellium Astrology Guide](../README.md). Code companion:
> [`examples/dignities_cookbook.py`](../../../examples/dignities_cookbook.py).
> Prerequisites: [01 The Zodiac](./01_the_zodiac.md), [03 Houses](./03_houses.md),
> [05 Sect](./05_sect.md).

:::{admonition} ✅ Figures computed
:class: note

Every figure in this chapter comes from Stellium's own output, and its code blocks are
pinned by the test suite: a library change that moved a number would fail here.
:::

## The one-line version

**Dignity** is how much power a planet actually has to do its job. A planet can
*mean* love or discipline or communication, but dignity tells you whether it can
*deliver*: whether it's working from a position of strength or scrambling from a
position of weakness.

## The metaphor that unlocks it

Think of every planet as a worker, and dignity as their working conditions. A
planet in its own sign is a craftsman in their own fully-stocked workshop:
everything they need is to hand. A planet in exile is that same craftsman working
in a stranger's kitchen with the wrong tools. Same skill, wildly different
results. Dignity is the traditional astrologer's performance review, and it
splits into two independent questions: does the planet have the right *resources*
(essential dignity), and is it in good *circumstances* (accidental dignity)? Those
two can disagree, and when they do, that disagreement is the whole story.

Our guide for this chapter is **William Lilly**, the 17th-century English
astrologer whose *Christian Astrology* (1647) codified the scoring the Western
tradition still uses. Reading the dignity master's own chart with his own tables
is the kind of recursion I can't resist.

---

## A brief history

Dignity is old and layered, assembled from several ancient sources. The
**rulerships** (which planet owns which sign) and **exaltations** are Babylonian
and Hellenistic. The **bounds** come down to us mainly in an "Egyptian" scheme.
The **triplicity** rulers (element rulers by sect) and the **decans** are
Hellenistic refinements. By the medieval period these had been welded into a
single scoring system, and Lilly's *Christian Astrology* fixed the point values
in the form most Western traditional astrologers still cite.

Modern astrology mostly dropped the scoring. It kept a loose sense of rulership
(Mars "rules" Aries, so a Mars in Aries feels strong) but abandoned the arithmetic
of bounds and faces and the idea that you could tally a planet's condition. The
traditional revival brought it back, and with it the recognition that dignity is
not decoration: it's how you tell a promise a planet can keep from one it can't.

---

## The theory

### Essential dignity: a planet's resources

Essential dignity is determined entirely by a planet's *sign and degree*. There
are five dignities (five ways to be strong) and three debilities (ways to be
weak), and the tradition assigns each a score.

| Condition | Score | What it means |
|---|---|---|
| **Domicile** (rulership) | +5 | In its own sign. Fully at home, maximally resourced. |
| **Exaltation** | +4 | In its sign of honor. An esteemed guest, elevated but not home. |
| **Triplicity** | +3 | Rules the sign's *element*, by sect (see below). |
| **Bound** (term) | +2 | In its own bound, a small sub-rulership of a few degrees. |
| **Decan** (face) | +1 | In its own 10° face. The faintest dignity, "at the door." |
| **Peregrine** | 0 | No dignity at all. A wanderer with no home and no rank. |
| **Fall** | −4 | Opposite its exaltation. Dishonored, out of favor. |
| **Detriment** | −5 | Opposite its domicile. In exile, in hostile territory. |

A planet can hold several dignities at once and you add them up. Lilly's **Venus
is in Taurus, which it rules**: domicile, **+5**. That is the strongest essential
condition in his chart — Venus is the craftsman in the fully-stocked workshop.

And the adding-up cuts both ways, which his Moon shows better than Venus does. It
sits in **Capricorn, its detriment** (−5) — the sign opposite the one it rules. But
Lilly was born at two in the morning, so this is a **night** chart, and the Moon is
the night **triplicity ruler** of the earth signs (+3). Net: **−2**. Badly placed,
and not without resource. A single number would have thrown that away.

By contrast, his **Sun and his Saturn are both peregrine** (score 0): they sit in
signs where they hold no rulership, exaltation, triplicity, bound, or face. Not
afflicted, exactly, but rootless, working without any home advantage.

> [!NOTE]
> **Triplicity is where sect comes back.** Each element has a *day* ruler, a
> *night* ruler, and a participating ruler, so whether a planet earns triplicity
> dignity depends on whether the chart is diurnal or nocturnal
> ([chapter 05](./05_sect.md)). Sect isn't a separate topic from dignity; it's
> wired into it.

### Traditional vs modern rulerships

The dignity tables were built for the seven visible planets, so "which planet
rules Aquarius" has a traditional answer (**Saturn**) and a modern one
(**Uranus**). This choice ripples: it changes domiciles, detriments, dispositor
chains, and the chart ruler. This guide uses **traditional rulerships** for
dignity work, because the whole scoring system was designed around them and the
outer planets have no exaltations, bounds, or faces to score. Lilly's chart ruler
is traditional Saturn; a modern reading would hand it to Uranus and lose the
elegant seven-planet logic that makes the tables cohere.

### Accidental dignity: a planet's circumstances

Accidental dignity has nothing to do with the sign. It's about the planet's
*situation*: where it sits and how it's behaving. The main factors:

- **Angularity.** Planets in angular houses (1, 4, 7, 10) are strong and active;
  cadent houses (3, 6, 9, 12) weaken them ([chapter 03](./03_houses.md)).
- **Speed and direction.** Direct and swift is strong; **retrograde** is an
  accidental debility (the planet's function turns hesitant, internalized).
- **Relationship to the Sun.** A planet within about 8.5° of the Sun is
  **combust**, burned up and obscured, badly weakened. Within about 15° it's
  "under the beams," mildly weakened. But within about 17 *arcminutes* it's
  **cazimi**, "in the heart of the Sun," and hugely *strengthened*, the exception
  that flips the rule.
- **Planetary joys.** Each planet rejoices in a particular house and is happier
  there.

> [!IMPORTANT]
> **Essential and accidental dignity are independent, and they can conflict.**
> Lilly's Venus is essentially dignified to the hilt (+5, in domicile) *and*
> accidentally debilitated — **combust**, a mere **0°50′** from the Sun, which is
> close enough to be all but swallowed. A brilliant craftsman, working in a locked
> and darkened room. Never collapse the two into a
> single "good/bad" verdict; read them as two separate layers and let the tension
> between them tell the story.

### Dispositors: the chart's chain of command

Here's the technique that turns dignity into structure. A planet is **disposited**
by whatever planet rules the sign it sits in. Lilly's Moon is in Capricorn, so
Saturn (Capricorn's ruler) is the Moon's dispositor. But Saturn is in Scorpio, ruled
by Mars; Mars is in Virgo, ruled by Mercury; Mercury is in Taurus, ruled by Venus.
And Venus is in Taurus, its *own* sign, so Venus disposits itself. The chain stops
there.

Follow every planet's chain up and, in Lilly's chart, they *all* terminate at
Venus:

```
Sun    → Venus → (Venus rules itself: stop)
Moon   → Saturn → Mars → Mercury → Venus → (stop)
Saturn → Mars → Mercury → Venus → (stop)
```

When one planet swallows every chain like this, it's the **final dispositor**: the
single planet the entire chart ultimately answers to. Lilly's is Venus, in Taurus,
in the 2nd house of money and resources. The whole chart flows toward Taurean
material security, which is a fair one-line summary of the pragmatic, prosperous
man who married well and made astrology pay.

Sometimes two planets rule each other's signs and the chain loops between them
forever: that's **mutual reception**, and the two planets prop each other up, able
to "trade places." Lilly has **none** — every chain runs straight to Venus without
looping — which is itself the point of drawing the graph: a chart with a single
final dispositor and no receptions has one unambiguous centre of gravity. A chart
full of loops does not.

### Chart ruler vs final dispositor (not the same thing)

Two "most important planet" concepts that beginners fuse, and Lilly pulls them
cleanly apart:

- The **chart ruler** is the planet that rules the *rising sign*: it stands for the
  native, the self. Lilly has **Pisces rising** (2°04′), so his chart ruler is
  **Jupiter** — the greater benefic, sitting at 13°29′ Libra in the **7th house** of
  partnership, holding a modest **+2** (participating triplicity ruler).
- The **final dispositor** is where the dispositor chains *terminate*: the chart's
  structural authority. Lilly's is **Venus**, in Taurus in the 2nd.

They are different planets doing different jobs, and in Lilly's case they tell the
same story from two directions. The **self** (Jupiter, from Pisces rising) stands in
the house of **partnership**. The **structure** (Venus, final dispositor) stands in
the house of **money**. AstroDatabank's biography, in one sentence: *"Lilly acquired a
fortune by marriage, which allowed him the leisure to study and follow his bent."*
Marriage, then money, then the freedom to become the most famous astrologer in
England — and his chart puts each of those exactly where you would look for it.

Notice too what the *self* is made of. Jupiter is only lightly dignified: it can act,
but it is not a powerhouse. The real concentration of the chart is a **Taurus stellium
in the 2nd** — Sun, Mercury and Venus all crowded into the house of resources, with
Venus (the only planet in the chart with real essential dignity) sitting **0°50′ from
the Sun**, close enough to be swallowed by it. That is a man whose whole chart points
at material security and whose single strongest planet is hidden inside the Sun's
glare. Whether that reads as "the craftsman working in a darkened room" or as
something else is a judgment call — but the *configuration* is not.

---

## In practice

### The core question: can this planet deliver?

When a planet is doing something important in a chart (ruling a key house, tightly
aspecting a luminary, carrying a lot), dignity asks the follow-up: *is it in any
shape to deliver?* A dignified planet keeps its promises. A debilitated one means
well but struggles, over-reaches, or needs help from elsewhere. This is the single
most useful thing dignity adds: it's the difference between a planet that *can* and
one that merely *wants to*.

> [!TIP]
> Run both layers, in order. First essential: does the planet have resources
> (dignified) or not (peregrine, fall, detriment)? Then accidental: is it well
> placed and free (angular, direct, not combust) or hindered (cadent, retrograde,
> combust)? A planet strong on both is a powerhouse; strong on one and weak on the
> other is the interesting, mixed case, like Lilly's dignified-but-combust Venus.

### Reading the chain

The dispositor chain tells you what a chart is *organized around*. Trace it to the
final dispositor and you've found the planet everything reports to. If there's no
single final dispositor (the chains split, or loop in mutual receptions), that's
information too: a chart with divided authority, no single center of gravity.

### The traditional-vs-modern fork, again

As with houses and zodiacs, dignity has a real stylistic choice baked in. Score
with the seven traditional rulers and the full five-dignity system, or use modern
rulerships and lean mostly on domicile/exaltation. Traditional gives you the whole
apparatus (bounds, faces, triplicities, the scoring); modern gives you a looser,
outer-planet-inclusive reading. For dignity specifically, traditional is the
system that was actually built for the job.

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

### Essential dignity and scoring

```python
from stellium import ChartBuilder
from stellium.components import DignityComponent

chart = (ChartBuilder.from_notable("William Lilly", use_recorded_time=True)
    .add_component(DignityComponent(traditional=True))
    .calculate())

venus = chart.get_planet_dignity("Venus", system="traditional")
print(venus["score"], venus["dignities"])

for p in ("Sun", "Moon", "Venus", "Saturn"):
    d = chart.get_planet_dignity(p, system="traditional")
    print(f"{p:8} {d['sign']:8} {d['score']:+d}  {d['dignities']}")

print(chart.get_strongest_planet())     # ('Venus', 7)
print(chart.get_mutual_receptions())     # Mercury <-> Moon by exaltation
```
<!--pytest-codeblocks:expected-output-->
```
5 ['domicile']
Sun      Taurus   +0  ['peregrine']
Moon     Capricorn -2  ['triplicity_ruler', 'detriment']
Venus    Taurus   +5  ['domicile']
Saturn   Scorpio  +0  ['peregrine']
('Venus', 5)
[]
```

### Dispositors, final dispositor, and chart ruler

```python
from stellium import ChartBuilder
from stellium.engines.dispositors import DispositorEngine
from stellium.utils.chart_ruler import get_chart_ruler_from_chart

chart = ChartBuilder.from_notable("William Lilly", use_recorded_time=True).calculate()

disp = DispositorEngine(chart, rulership_system="traditional").planetary()
print(disp.final_dispositor)
print(disp.chains["Saturn"])
print(disp.chains["Moon"])

print(get_chart_ruler_from_chart(chart))
```
<!--pytest-codeblocks:expected-output-->
```
Venus
['Saturn', 'Mars', 'Mercury', 'Venus', 'Venus']
['Moon', 'Saturn', 'Mars', 'Mercury', 'Venus', 'Venus']
('Jupiter', 'Pisces')
```

The chart ruler is a `(planet, rising_sign)` pair; note it's **Saturn** here
(traditional ruler of Aquarius), not the final dispositor **Venus**. Two different
jobs, as above. Pass `rulership_system="modern"` to the `DispositorEngine` (and it
would hand Aquarius to Uranus) to see how the whole chain-of-command shifts.

### Accidental dignity

```python
from stellium import ChartBuilder
from stellium.components import AccidentalDignityComponent

chart = (ChartBuilder.from_notable("William Lilly", use_recorded_time=True)
    .add_component(AccidentalDignityComponent())
    .calculate())
# Scores angularity, retrograde, combustion/cazimi, joys, etc. into chart.metadata
# (This is what flags Lilly's Venus as combust — 0°50' from the Sun — despite its +5.)
```

The [dignities cookbook](../../../examples/dignities_cookbook.py) walks through
essential and accidental scoring, mutual reception, dispositor graphs, and
peregrine detection in full.

---

## Going deeper

- **Prev:** [05 Sect](./05_sect.md), which supplies the triplicity rulers and the
  "in sect" credit that feed a planet's condition.
- **Next:** [07 Lots (Arabic Parts)](./07_lots_arabic_parts.md), which are read
  partly through the dignity of the planets involved.
- **Angularity in depth:** [03 Houses](./03_houses.md) for the accidental-dignity
  side of house placement.
- **Chart shape and the chart ruler:** **20 Chart Shapes** *(not yet written)*.

**Primary sources & further reading:**

- William Lilly, *Christian Astrology* (1647), for the scoring straight from the
  source; the dignity tables are in Book I.
- Benjamin Dykes, *Traditional Astrology* translations, for the medieval dignity
  system in depth.
- Chris Brennan, *Hellenistic Astrology* (2017), for dignity's origins and its
  place in the wider system.
