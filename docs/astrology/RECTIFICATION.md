# Birth-Time Rectification & Sect Recovery — A User's Guide

This guide is different from the other cookbooks. Rectification in Stellium is
essentially **one function call** — but it comes with more caveats than code,
because the honest version of this technique is mostly about knowing *what it can't
do*. Read the "how **not** to use it" section; it's the important one.

---

## TL;DR — the one call

```python
from stellium import ChartBuilder, analyze_sect

chart = ChartBuilder.from_notable("Frida Kahlo").calculate()
a = analyze_sect(chart)

print(f"{a.p_day:.2f}  → {a.leans}")   # 0.80  → day
```

Or drop it straight into a report (renders in every format):

```python
from stellium import ReportBuilder

print(ReportBuilder().from_chart(chart).with_sect_rectification().to_string("markdown"))
```

That's the whole API surface. The rest of this document explains what that number
means, and — more importantly — what it does not.

---

## What rectification is, and why Stellium refuses to fake it

**The dream.** You have someone's date and place of birth but not the *time*. Their
Ascendant, houses, Moon, and every timing technique depend on that time. Classical
rectification promises to recover it by matching known life events against the
chart: find the birth time whose directions/progressions/transits "light up" the
right ages.

**The reality.** We tested this dream as rigorously as we knew how — a 63-person
corpus of AA-rated (certificate-verified) birth times with documented life events,
pre-registered gates, leave-one-out cross-validation, permutation nulls, confound
controls, and an out-of-sample holdout. The full write-up is in
[`RECTIFICATION_REPORT.md`](../development/specs/rectification/RECTIFICATION_REPORT.md). The short
version:

> The map from **birth time → chart → life** is many-to-one. Two different birth
> times can produce lives that fit the events equally well. So the **inverse is
> ill-posed** (non-unique) — a textbook ill-posed inverse problem, the same species
> as deconvolution or CT reconstruction. Minute-level birth time is not recoverable
> from life events, by any method, because the information isn't there.

Concretely: individual timing techniques placed the *true* birth time at only the
~55th–59th percentile of candidates — a whisper above chance — and **blind
combination of them made it worse, not better** (the noise adds faster than the
signal). So Stellium deliberately **does not** ship a `chart.rectify() -> a birth
time`. That would be selling a false precision the evidence says doesn't exist.

---

## What *is* recoverable: sect (one bit)

One thing survived every test: **sect**.

- **Sect** is whether you were born by **day** (Sun above the horizon) or **night**
  (Sun below it). It's the coarsest possible fact about a birth time — a single bit
  — and the most robust.
- Stellium recovers it at **~70% accuracy** (leave-one-out cross-validated; 70.6%
  on a fully out-of-sample modern cohort) from two ingredients:
  1. **The daylight prior** — the fraction of the birth day the Sun is above the
     horizon (`P(day | date, latitude)`), pure geometry. Longer day ⇒ more likely
     born by day.
  2. **The malefic contrary to sect** — a 2,000-year-old doctrine that turned out to
     leave a real, confound-robust fingerprint: a Mars-flavoured life (accidents,
     violence, heat) leans day; a Saturn-flavoured one (illness, poverty, slow
     decline) leans night.

**The ceiling is truth resolution, not method.** Sect is recoverable, unlike
minute-level time — but *how well* depends on how rich your knowledge of the person
is. A one-line biography caps you near 70%. Knowing the person first-hand — their
temperament, the texture of their hardships — can push a skilled reader to ~90%. The
tool gives you the geometry and the structure; **you** supply the resolution.

---

## The one call: `analyze_sect`

```python
analyze_sect(chart, *, events=None, temperament=None) -> SectAnalysis
```

- **`chart`** — any natal chart. Both hypotheses are re-cast from its date + place,
  so the *time* you built it with doesn't matter (noon is fine).
- **`events`** — a sequence of [`LifeEvent`](#supplying-your-own-events). For
  notables in the catalog, they're **looked up automatically** by name. Pass `()`
  to force a geometry-only read.
- **`temperament`** — soft character traits; auto-looked-up for notables. Flagged
  low-confidence (see the guardrails).

### What you get back — `SectAnalysis`

| Field | Meaning |
|---|---|
| `p_day` | Calibrated probability of a **day** birth (the headline number). |
| `leans`, `confidence` | `"day"`/`"night"` and `max(p_day, 1-p_day)`. |
| `daylight_fraction` | The geometric prior alone (before event evidence). |
| `day`, `night` | The `Hypothesis` structures each sect implies (sect light, out-of-sect malefic, in-sect benefic, with sign + dignity). |
| `moon_band` | A warning if the Moon changes sign within the 24 h — i.e. its sign is a *band*, not a point. |
| `hardship`, `fortune` | `(Mars, Saturn)` and `(Jupiter, Venus)` event-flavour tallies. |
| `firdaria` | Firdaria time-lord convergence (`day_hits`/`night_hits`/`favors`). |
| `malefic_temper`, `sect_light_temper` | Soft temperament signals (see guardrails). |
| `technique_votes()` | Each technique's day/night vote, for the convergence tally. |

---

## Reading the output

For Frida Kahlo, `with_sect_rectification()` produces (abridged):

```
Anchor:
  Daylight prior P(day)  0.55   (geometry, the base rate)
  Calibrated  P(day)     0.80   → leans DAY (80% conf)
  ⚠ Moon band: Moon crosses Taurus → Gemini within the 24h — a band, not a point.

                       IF DAY                         IF NIGHT
  Sect light           Sun in Cancer (peregrine)      Moon in Taurus (exalted)
  Out-of-sect malefic  Mars in Capricorn (exalted)    Saturn in Pisces (peregrine)
    → hardship reads   hot, sharp — accidents…        cold, slow — illness…
  In-sect benefic      Jupiter in Cancer (exalted)    Venus in Gemini (peregrine)

  hardship flavour: leans DAY (4.0 / 2.0)     fortune flavour: leans NIGHT (0.6 / 7.6)
  Convergence: DAY 3 · NIGHT 1
```

Read it top-down: the **anchor** is the quantitative answer; the **day/night table**
lays out what each hypothesis *means* so you can check it against what you know; the
**evidence** shows which way the life actually tilts. Note the honesty — Frida's
*fortune* reads Venus/night (she was an artist) even as her *hardship* reads
Mars/day. A real cross-current, shown rather than smoothed over. Her true birth was
by day; the anchor recovers it.

---

## How **not** to use it — the guardrails

This is the part that matters.

1. **`p_day` is one bit, not a clock.** It tells you day vs night, nothing finer. It
   is *not* a birth time and cannot be turned into one. If you need a house or an
   exact Ascendant, this tool can't give it to you — and neither can anything else,
   honestly (see the ill-posed section).

2. **It's an indicator, not an oracle.** ~70% on biography-thin data means it's
   *wrong about one chart in three*. Treat a lean as a hypothesis to weigh, never a
   verdict to act on. Every output says so; believe it.

3. **Don't feed it the answer.** The classifier reads the *character* of a life, not
   chart placements that depend on the time you're trying to find. Keep your inputs
   (events, temperament) independent of any time you already suspect.

4. **Don't trust the soft temperament signals on strangers.** `malefic_temper` and
   `sect_light_temper` were **null** on the corpus — a keyword tally can't tell
   "hot-tempered" from "the opposite of hot-tempered." They light up only when *you*
   supply real, first-hand knowledge of the person. The output flags them; heed it.

5. **Convergence is *counted*, never *summed*.** We measured that blindly adding the
   timing techniques together *cancels* the signal. The tool shows you how many
   independent techniques vote each way — it never fuses them into one score, and
   neither should you.

6. **When the anchor and the timing lenses disagree on sect, trust the anchor.** The
   daylight × malefic anchor is the only cross-validated signal. The timing lenses
   (directions/transits/profection in the convergence matrix) are whisper-level and
   routinely point the wrong way. Use them to explore *time-within-sect*, not to
   overrule the anchor on *sect*.

7. **It doesn't replace your judgment — it structures it.** The right mental model:
   this is a decision-support display that constructs both hypotheses and lays out
   the evidence, so a knowledgeable human can adjudicate. The one step it will never
   take for you is the final call. That's by design.

---

## Supplying your own events

For anyone not in the notables catalog, pass events explicitly:

```python
from stellium import ChartBuilder, Native, analyze_sect
from stellium.data import LifeEvent

chart = ChartBuilder.from_native(Native("1974-05-20 12:00:00", "Lima, Peru")).calculate()

events = [
    LifeEvent(date="1998-09", precision="month", type="accident",
              description="serious motorcycle crash, broke leg", significance="major"),
    LifeEvent(date="2005", precision="year", type="career",
              description="promoted, took over the family firm", significance="moderate"),
]
a = analyze_sect(chart, events=events)
print(a.p_day, a.leans)
```

`LifeEvent` fields: `date` (`"YYYY"`, `"YYYY-MM"`, or `"YYYY-MM-DD"`), `precision`,
`type` (an event-taxonomy key — `accident`, `health_crisis`, `bereavement_parent`,
`career`, `relationship`, `windfall`, …), `description` (free text; the Mars/Saturn
and Jupiter/Venus keyword flavour is read from here), and `significance`
(`major`/`moderate`/`minor`). With no events, pass `events=()` for a **geometry-only**
read — the daylight prior with no event tempering.

> **Note on the geometry-only number.** With no events, `p_day` reflects the daylight
> prior *as seen by the trained model*, which centres the malefic feature at its
> corpus mean — so "no evidence" reads slightly day-leaning rather than exactly the
> raw daylight fraction. That's expected; the raw geometric prior is in
> `daylight_fraction`.

---

## Advanced: the convergence matrix (exploratory)

For a fuller picture — and to *see* why timing can't pin the time — there's a heavier
two-lens display:

```python
print(ReportBuilder().from_chart(chart).with_sect_convergence_matrix().to_string("markdown"))
# or, as data:
from stellium import convergence_matrix
m = convergence_matrix(chart)
```

It runs ~3–10 s (it sweeps 96 candidate times with primary directions at each) and
shows two lenses over that sweep:

- **Lens A — the structural band:** every genuinely distinct chart across the 24 h
  (each sect region × Ascendant sign), scored by solar-arc directions, transiting
  chronocrators to the angles, and annual profection.
- **Lens B — the event hooks:** a histogram of how many events get an apt
  directed/transiting hit at each candidate time — the times the events themselves
  "nominate."

It exists to be *read*, not obeyed. Its timing rows are whisper-level and it **never
sums them into a verdict** — expect the event-hook histogram to be spread across the
whole day (the ill-posed signature), and expect the two lenses to sometimes fight the
anchor. When they do, re-read guardrail #6. This is the honest, mechanised form of
the "convergence of multiple techniques" that traditional rectifiers rely on — with
the quiet truth made visible: convergence *displays* candidates, it doesn't *prove*
one.

---

## The data behind it

The auto-lookup for notables draws on two curated datasets shipped with Stellium
(kept separate from birth data because their provenance is lower):

```python
from stellium import get_notable_life_events, get_notable_temperament

events = get_notable_life_events("Frida Kahlo")     # ~Rodden-B, taxonomy-tagged
traits = get_notable_temperament("Frida Kahlo")     # soft/interpretive (warns on access)
```

- **Life events** — dated, taxonomy-tagged, gathered from biographies + AstroDataBank
  via research. Sourced but **not** certificate-verified — roughly Rodden **B**
  grade. Each carries an honest `precision` and a `representative_date` helper.
- **Temperament** — **soft, interpretive** character descriptors, not measurements.
  The getter emits a `DataQualityWarning` on access, on purpose.

---

## Further reading

- **[The full empirical study](../development/specs/rectification/RECTIFICATION_REPORT.md)** — the
  corpus, methodology, the ill-posed-inverse framing, the convergence test, the
  confound checks, and the one traditional doctrine that survived.
- **[CHART_TYPES.md](../CHART_TYPES.md)** — where sect, directions, profections, and
  firdaria fit in the broader map of techniques.
