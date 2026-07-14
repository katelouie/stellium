# Traditional Methods & Sources

This is the canonical record of **what Stellium's traditional (Hellenistic /
Perso-Arabic) techniques actually compute, and on whose authority.** For each
technique it states the default, the key citations, the genuinely *contested*
forks (and which Stellium ships as default and why), and any simplifications —
with a link to the full source-verification report behind it.

It sits between three neighbours and overlaps none of them:

| Doc area | Answers |
|---|---|
| [`docs/astrology/`](../astrology/RECTIFICATION.md) | *How do I use this technique as a practitioner?* (teaching) |
| **`docs/methodology/`** (here) | *What does Stellium implement, and from which sources?* (scholarship) |
| [`docs/development/`](https://github.com/katelouie/stellium/tree/main/docs/development) | *How is it built in the code?* (architecture) |

Design specs in [`docs/development/specs/`](https://github.com/katelouie/stellium/tree/main/docs/development/specs) capture a
change *before* it's built; this doc is the durable sourcing that outlives them.

**A principle throughout:** where the tradition genuinely disagrees, Stellium
surfaces the fork as a **toggle or preset** rather than silently choosing —
and documents which default it ships and why. The raw investigations (with verbatim quotes and full bibliographies) are the
[planetary years](research/planetary-years.md), [zodiacal releasing](research/zodiacal-releasing.md)
and [firdaria](research/firdaria.md) reports.

---

## Planetary years

The shared primitive (`stellium.core.planetary_years`) behind ZR, Firdaria, and
length of life. Full report: [research/planetary-years.md](./research/planetary-years.md).

- **Least / minor years** (Sun 19, Moon 25, Mercury 20, Venus 8, Mars 15,
  Jupiter 12, Saturn 30; sum 129) — canonical and near-universal. *Valens,
  Anthology III/IV; Firmicus, Mathesis II.29.* What ZR consumes.
- **Greater years** (Sun 120, Moon 108, Saturn 57, Jupiter 79, Mars 66,
  Venus 82, Mercury 76) — the five non-luminary values are the **sum of each
  planet's Egyptian terms** across the zodiac (they total 360). *Ptolemy,
  Tetrabiblos I.20; Houlding (Annotated Lilly, fn 154).* Stellium verifies this
  against its own term tables in the test suite.
- **Mean years** — *derived* as `(least + greater) / 2` (half-integer luminaries
  Sun 69.5, Moon 66.5), never hand-typed. *Skyscript/Houlding; the alcocoden
  Table of Years.*
- **Greatest years** — **genuinely contested; stored as attributed variants with
  no default.** De Vore vs. the astronomical reconstruction (Neugebauer/
  Houlding); the Moon is the flashpoint (25 / 320 / 420 / 520 across
  Antiochus-Rhetorius / Lilly / Bonatti / later-Arabic).
- **Firdaria periods** are a *separate* table (see below) — **not** the least
  years.

**Correction shipped:** the popular claim that Capricorn's ZR period of 27 =
"¼ of the Moon's greater years (108/4)" is **folk-etymology, not in Valens** —
the arithmetic is coincidental and no source connects it to the sign-periods.
Stellium's code comment was corrected accordingly. (The sourced symbolic note,
if wanted, is Manwaring's "27 lunar mansions.") Code: `engines/releasing.py`.

**Dignity-data fix it surfaced:** the term-sum cross-check caught a transposed
pair of Egyptian terms in Sagittarius (Saturn/Mars at 21–30°), now corrected
(*Ptolemy I.20; Lilly*). Code: `engines/dignities.py`.

---

## Zodiacal Releasing

Full report: [research/zodiacal-releasing.md](./research/zodiacal-releasing.md).

- **Single source:** *Vettius Valens, Anthology Book IV* (chs. 4–10, Riley
  numbering). Named "Zodiacal Releasing" and reconstructed by **Robert Schmidt**
  (Project Hindsight, 1996); popularized by **Chris Brennan** (*Hellenistic
  Astrology*, 2017). Also Demetra George (Vol. II), Manwaring (Delphic Oracle).
- **Stellium default = the "Brennan / Modern Standard":** release from the Lot
  (Spirit for career, Fortune for body), whole-sign tropical, **360-day years**,
  **Capricorn 27 / Aquarius 30**, sect-reversed lots, **loosing of the bond to
  the opposite sign** after a full 12-sign circuit, truncation at parent
  boundaries, peaks measured from Fortune, same-sign Spirit rule.

**Contested forks & our choice:**

| Fork | Positions | Stellium |
|---|---|---|
| Reverse Fortune/Spirit by sect | Valens/Schmidt/Brennan: yes · Ptolemy/Lilly: no | **yes** (default; toggle) |
| Period → date year length | Valens/Brennan: 360-day · minority: 365.25 | **360** (`year_length` toggle) |
| Capricorn period | 27 (standard) · 30 (minority) | **27** (`capricorn_years` toggle) |
| Loosing target | opposite (Valens) · trine (some contemporaries) | **opposite** (`loosing_target` toggle) |

Code: `engines/releasing.py` (`ZodiacalReleasingEngine`), `chart.zodiacal_releasing()`.

---

## Firdaria

Full report: [research/firdaria.md](./research/firdaria.md).

- **Period values** (Sun 10, Venus 8, Mercury 13, Moon 9, Saturn 11, Jupiter 12,
  Mars 7, Head 3, Tail 2; sum 75) and the sect-ordered Chaldean sequence are
  **near-universal.** *Abu Ma'shar (Dykes, Persian Nativities); al-Biruni;
  al-Qabisi; Bonatti; Lilly.*
- **Sub-periods:** seven equal parts in Chaldean order from the major ruler;
  node majors don't subdivide and nodes aren't sub-rulers (*Abu Ma'shar*).
- **Stellium default = the "Abu Ma'shar / Persian" preset:** nodes at the end in
  both sects, 7 equal sub-periods, repeat past 75, real **365.2425-day** year
  (the 360-day year is mundane-only, *not* natal firdaria).

**The one real fork — nocturnal node placement**, shipped as presets:

| Preset | Nocturnal nodes | Basis |
|---|---|---|
| **`abu_mashar`** (default) | at the end (both sects) | Abu Ma'shar / al-Biruni / Hand / Birchfield |
| `bonatti` | after Mars (~ages 39–44) | Bonatti / Zoller (from an ambiguous al-Qabisi paraphrase) |
| `al_biruni` | at the end (alias of default) | — |
| `no_nodes` | none (70-year cycle) | practitioners who reject the node periods |

*Deferred (noted, not built):* the AB Method (Subramanyan) — proportional
sub-periods with the nodes participating. Code: `engines/firdaria.py`,
`chart.firdaria()`.

---

## Length of life (hyleg / alcocoden)

Full report: [research/planetary-years.md](./research/planetary-years.md)
(alcocoden section). **A computed traditional *indicator*, not a prediction of
actual lifespan** — the result is fully itemized so the reasoning is auditable.

- **Method = Perso-Arabic years table, `method="lilly"` default.** The
  years-table apparatus is Perso-Arabic (Māshā'allāh, Sahl, Abū Ma'shar,
  al-Qabisi) synthesized into **Bonatti** and **Lilly** (via Houlding's
  annotated edition); Ptolemy's rival *directional* method (*Tetrabiblos*
  III.10–11) has **no years table** and is **reserved but not implemented**
  (`method="ptolemy"` raises).
- **Hyleg:** sect-ordered candidates (sect light, other light, Lot of Fortune,
  prenatal Syzygy, Ascendant backstop); first in a hylegiacal place wins.
- **Alcocoden:** the almuten of the hyleg's degree that beholds it; grants years
  by angularity — **angular → greater, succedent → mean, cadent → least.**
- **Modifiers (Lilly):** benefics add / malefics subtract their least years,
  the lights add by soft aspect / subtract by hard, fall or retrograde halves,
  combustion → months.

**Documented simplifications (v1):**
- Hylegiacal places use **whole-house** membership (the degree-based Ptolemaic
  boundaries, e.g. 5° above the Asc, are a noted future refinement).
- The Full-Moon syzygy uses the **Moon's degree** (the "luminary above the
  horizon" refinement isn't applied).
- Year modifiers use **real moiety-orb aspects** (not whole-sign, which
  over-counts) and the total is **floored at 0**.
- Lilly-only; a Bonatti preset (differing modifier list) is a future addition.
- **Known behaviour:** the years table tends to **overshoot for a strong
  (angular) alcocoden** — this is the technique, not a defect.

Code: `engines/length_of_life.py`, `chart.length_of_life()` / `chart.hyleg()`.

### Almuten of a degree

The essential-dignity victor over a longitude (domicile 5, exaltation 4,
triplicity 3, term 2, face 1). *Ibn Ezra / Lilly weighting.* Triplicity is
sect-dependent; node exaltations are never scored. Distinct from
`get_strongest_planet()` (almuten *among placed planets*). Code:
`engines/almuten.py`.

---

## Recurring sources

Primary texts and the translations/editions Stellium's implementations lean on:

- **Vettius Valens**, *Anthology* — Mark Riley (CSU Sacramento PDF; print ed.
  Brennan, 2022); Robert Schmidt (Project Hindsight, 1996).
- **Ptolemy**, *Tetrabiblos* I.20–21 (terms/greater years), III.10–11 (length of
  life).
- **Firmicus Maternus**, *Mathesis* II.29.
- **Abū Ma'shar**, *On the Revolutions of the Years of Nativities* — trans.
  Benjamin Dykes, *Persian Nativities*.
- **al-Bīrūnī**, *Book of Instruction* — trans. R. Ramsay Wright (1934).
- **al-Qabīsī**, *Introduction to Astrology* — trans. Dykes.
- **Guido Bonatti**, *Liber Astronomiae* — trans. Dykes.
- **William Lilly**, *Christian Astrology* — Deborah Houlding's annotated
  edition (Skyscript) for the greater/mean/least tables and the term-sum
  derivation.
- **Modern:** Chris Brennan (*Hellenistic Astrology*, 2017), Demetra George
  (*Ancient Astrology in Theory and Practice*), Robert Hand (ARHAT), Curtis
  Manwaring (Delphic Oracle; the "27 lunar mansions" note), Steven Birchfield.

Full per-parameter attribution, verbatim quotes, and the contested-point
evidence are in the three reports under [research reports](research/planetary-years.md).
