# Spec: Hellenistic Planetary Periods & Firdaria

| | |
|---|---|
| **Status** | Draft — for review |
| **Created** | 2026-07-09 |
| **Owner** | Kate |
| **Type** | Spec-Driven Development (SDD) design doc |
| **Sources** | [docs/methodology/README.md](../../methodology/README.md) · report: [research/planetary-years.md](../../methodology/research/planetary-years.md) |

---

## 1. Summary

The "planetary years" (Saturn 30, Jupiter 12, …) are not a Zodiacal-Releasing
detail — they're a **shared primitive** that ZR, Firdaria, length-of-life
(alcocoden), and decennials all draw on, in different *families* (least / mean /
greater / greatest). Today the least years live as a private `PLANET_PERIODS`
dict inside `engines/releasing.py`.

This spec (1) hoists all the period data into one canonical, source-attributed
module `stellium/core/planetary_years.py`; (2) refactors ZR onto it and corrects
a folk-etymology comment; and (3) builds the first new consumer, a **Firdaria**
time-lord engine (`chart.firdaria()`).

It also records a **real data bug** the design surfaced: your Egyptian terms for
Sagittarius are transposed, which a cross-check test built here will permanently
guard (§5).

---

## 2. Motivation

- **One source of truth.** When Firdaria and length-of-life arrive, Saturn's
  numbers should not be re-typed in a third and fourth file. Centralizing now
  prevents transcription drift — a live risk with these fiddly tables (see §5).
- **Different techniques want different families.** ZR uses *least* years;
  alcocoden uses *greater/mean/least* by angularity; the greater years already
  matter today (they're the sourced origin of Capricorn's 27 story — which turns
  out to be folk-etymology, §6). A primitive that holds all four families lets
  each technique ask for what it needs.
- **Attribution matters.** The research is emphatic: least/greater/mean are
  near-universal, but **greatest years genuinely disagree between authors**
  (esp. the Moon: 25 / 320 / 420 / 520). The structure must hold variants with
  sources, not a single "authoritative" number.
- **Firdaria is the natural next time-lord.** It reuses the sect machinery ZR
  already has (`chart.sect`) and slots into the existing `chart.<technique>()`
  pattern.

---

## 3. Goals / Non-Goals

### Goals

- **G1** — A canonical `stellium/core/planetary_years.py` holding least, greater,
  mean, and greatest years + Firdaria periods, keyed by planet, with source
  attribution and a clear reliability tier per family.
- **G2** — `engines/releasing.py` consumes `LEAST_YEARS` from it (drops its
  private copy) with no behavior change; the Capricorn=27 comment is corrected.
- **G3** — A test derives the non-luminary greater years from the existing
  `bound_egypt` term data and asserts they match — guarding transcription drift
  in *both* the years table and the dignity terms.
- **G4** — A working **Firdaria** engine: `chart.firdaria()` → `FirdariaTimeline`,
  day/night sequenced, with sub-periods, mirroring the ZR/profection API.
- **G5** — Zero new runtime dependencies; no change to existing ZR/profection
  output.

### Non-Goals

- **N1** — No length-of-life / alcocoden, decennials, or planetary-days engine
  yet. The primitive is *designed* for them (§8) but they're separate work.
- **N2** — No attempt to resolve the greatest-years scholarly dispute — we
  *record* the variants, we don't pick a winner.
- **N3** — Firdaria v1 does two levels (major + sub-period), not the deeper
  sub-sub-divisions some software offers.
- **N4** — Not silently "fixing" the Sagittarius terms as part of the merge —
  that's flagged for explicit sign-off (§5) because it changes dignity output.

---

## 4. The primitive — `stellium/core/planetary_years.py`

Pure data + small accessors, **zero stellium imports** (a leaf module safe to
import from `core`, `engines`, `components`). Lives in `core/` alongside the
other astrological reference (registries); `data/` is reserved for the ephemeris
and notables DB.

### 4.1 The four families

```python
# LEAST / MINOR years — canonical, effectively invariant.
# Valens Anthology III/IV; Firmicus Mathesis II.29. Sum = 129 (basis of Decennials).
LEAST_YEARS = {
    "Sun": 19, "Moon": 25, "Mercury": 20, "Venus": 8,
    "Mars": 15, "Jupiter": 12, "Saturn": 30,
}

# GREATER years — canonical. Non-luminaries = sum of each planet's Egyptian
# terms across the zodiac (Ptolemy Tetrabiblos I.20); the five sum to 360.
# Luminaries: Sun 120 (greatest solar semi-arc), Moon 108 (120 - 12° visibility).
GREATER_YEARS = {
    "Sun": 120, "Moon": 108, "Saturn": 57, "Jupiter": 79,
    "Mars": 66, "Venus": 82, "Mercury": 76,
}

# MEAN years — DERIVED, never hand-typed: (least + greater) / 2.
# Half-integer luminaries (Sun 69.5, Moon 66.5) per the alcocoden tables.
MEAN_YEARS = {p: (LEAST_YEARS[p] + GREATER_YEARS[p]) / 2 for p in LEAST_YEARS}
```

### 4.2 Greatest years — variants, not a number

The research shows two conflicting traditions and a specifically-contested Moon.
We store them as attributed variants and expose no single default:

```python
# GREATEST / MAXIMUM years — genuinely contested; present variants, pick none.
GREATEST_YEARS_VARIANTS = {
    "de_vore": {  # De Vore, Encyclopedia of Astrology (widely reproduced)
        "Saturn": 465, "Jupiter": 428, "Mars": 264, "Sun": 1460,
        "Venus": 151, "Mercury": 450, "Moon": 320,
    },
    "astronomical": {  # Neugebauer / Houlding reconstruction (sidereal × period no.)
        "Saturn": 265, "Jupiter": 427, "Mars": 284, "Sun": 1461,
        "Venus": 1151, "Mercury": 461, "Moon": 520,
    },
}
# The Moon is the flashpoint: Antiochus/Rhetorius 25, Lilly 320, Bonatti 420,
# Al-Qabisi/Al-Biruni/Ibn Ezra/astronomical 520. Documented, not resolved.
MOON_GREATEST_VARIANTS = {
    "antiochus_rhetorius": 25, "lilly": 320, "bonatti": 420, "later_arabic": 520,
}
```

### 4.3 Firdaria periods — a SEPARATE table

⚠️ **These are NOT the least years** (Firdaria Sun 10 vs. least 19; Moon 9 vs.
25). Abu Ma'shar via Dykes, *Persian Nativities*:

```python
# FIRDARIA periods (years). Sum = 75. NOT the least years — see warning above.
FIRDARIA_YEARS = {
    "Sun": 10, "Venus": 8, "Mercury": 13, "Moon": 9,
    "Saturn": 11, "Jupiter": 12, "Mars": 7,
    "North Node": 3, "South Node": 2,
}

# Ordering is sect-dependent, descending Chaldean from the sect light, nodes last.
FIRDARIA_ORDER_DAY = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter",
                      "Mars", "North Node", "South Node"]
FIRDARIA_ORDER_NIGHT = ["Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus",
                        "Mercury", "North Node", "South Node"]
```

### 4.4 Accessors

```python
def least_years(planet: str) -> int: ...
def greater_years(planet: str) -> int: ...
def mean_years(planet: str) -> float: ...
def firdaria_years(planet: str) -> int: ...
def firdaria_order(sect: str) -> list[str]:   # "day" | "night"
    ...
```

Backwards-compat: `engines/releasing.py` keeps a `PLANET_PERIODS = LEAST_YEARS`
alias so any external importer doesn't break.

---

## 5. The term-sum cross-check — and the Sagittarius bug it found

The five non-luminary greater years **are** the sums of each planet's Egyptian
terms (`DIGNITIES[sign]["bound_egypt"]`) across the zodiac. A test computes them
and asserts they equal `GREATER_YEARS` — a permanent guard against transcription
drift in either table.

Running it against the current code **fails**, and pinpoints why:

| Planet | Term-sum from `bound_egypt` | Canonical greater |
|---|---|---|
| Saturn | **56** | 57 |
| Mars | **67** | 66 |
| Jupiter / Venus / Mercury | 79 / 82 / 76 ✓ | 79 / 82 / 76 |

The total is 360 both ways — it's a single 1° Saturn↔Mars transposition, located
in **Sagittarius**:

- Current: `… Mercury(17), Mars(21), Saturn(26)` → Mars 21–26°, Saturn 26–30°.
- Canonical (Ptolemy/Lilly/Houlding): `… Mercury(17), Saturn(21), Mars(26)` →
  Saturn 21–26°, Mars 26–30°.

**Impact beyond bookkeeping:** any planet at 21–30° Sagittarius currently gets
the wrong Egyptian-term ruler (Mars instead of Saturn for 21–26°). This affects
`get_planet_dignity`, term scores, and anything downstream.

**Proposed fix** (needs sign-off — it changes dignity output): in
`DIGNITIES["Sagittarius"]["bound_egypt"]`, swap `21: "Mars"` → `21: "Saturn"` and
`26: "Saturn"` → `26: "Mars"`. Then the cross-check passes and greater years read
57/66 from data. **Until signed off, the test is written to the *canonical*
values and this fix ships in the same PR, or the test is `xfail`-documented.**

---

## 6. ZR refactor + Capricorn comment fix

- `engines/releasing.py` imports `LEAST_YEARS` (via the `PLANET_PERIODS` alias
  path) instead of defining its own dict. No behavior change — same values.
- **Correct the comment.** It currently reads *"Valens: Capricorn, opposite
  Cancer, receives 1/4 of Cancer's greater years"* — the research shows this
  ¼-greater-years derivation is **not in Valens and not endorsed by any major
  commentator** (folk-etymology; the arithmetic 108÷4=27 is coincidental). New
  comment: Capricorn's 27 is an inherited exception whose original rationale is
  not preserved in the text; the sourced symbolic note (if wanted) is Manwaring's
  "27 lunar mansions," not ¼ of greater years.

---

## 7. Firdaria engine

Mirrors the existing time-lord API (`chart.zodiacal_releasing()`,
`chart.profection()`).

### 7.1 Surface

```python
timeline = chart.firdaria()          # -> FirdariaTimeline
ruler = timeline.at(some_datetime)   # -> FirdariaPeriod (major+sub in effect)
```

Underneath: `FirdariaEngine(chart).calculate() -> FirdariaTimeline`. Requires a
timed chart (needs `chart.sect`); on an `UnknownTimeChart`, `firdaria()` raises a
clear error (sect/ASC unavailable), consistent with profections.

### 7.2 Algorithm

1. **Sect** from `chart.sect`. Day → `FIRDARIA_ORDER_DAY`, night → `_NIGHT`.
   (The seven-planet day/night orders are undisputed across all sources.)
2. **Major periods**: walk the order from birth, each ruler for `FIRDARIA_YEARS`
   years (default **365.2425**-day years — a real solar year; the 360-day ideal
   year is **not** used for natal firdaria, it belongs to the mundane "mighty
   fardar"). Seven planets = 70 yr; with nodes = 75 yr; then the sequence
   **repeats** ("then it returns to the Sun" — Abu Ma'shar), capped at `max_age`.
3. **Sub-periods**: each planetary major divides into **7 equal sub-periods**
   (each = major/7) in descending Chaldean order **starting from the major ruler
   itself** (a 10-yr Sun period → Sun, Venus, Mercury, Moon, Saturn, Jupiter,
   Mars). Sub-period order is unambiguous across sources — no alternative needed.
   The **node majors do not subdivide, and nodes never appear as sub-rulers**
   (Abu Ma'shar: "they do not partner with the planets… because they do not have
   houses").

### 7.3 The one real fork — nocturnal node placement, and presets

Node *values* (Head 3, Tail 2) and the fact they come last **for day charts**
are undisputed. The single genuine disagreement is where the nodes fall in
**nocturnal** charts:

- **Abu Ma'shar / al-Biruni / Hand / Birchfield (default):** nodes at the **end**
  in both sects (ages 70–75). This is the fullest, earliest primary source and
  the dominant modern-scholarly reading.
- **Bonatti / Zoller:** nodes **after Mars** in nocturnal charts (~ages 39–44),
  from an ambiguous al-Qabisi paraphrase. Defended on practice, not text.

v1 ships this as a preset with the fork exposed, since practitioners are
genuinely split:

| Preset | node_mode | nocturnal nodes | sub-periods |
|---|---|---|---|
| **`abu_mashar`** (default) | on | at end | 7 equal, from ruler |
| `bonatti` (a.k.a. Zoller/Lilly) | on | after Mars | 7 equal, from ruler |
| `al_biruni` | on | at end | 7 equal (alias of default) |
| `no_nodes` | off | — (70-yr cycle) | 7 equal, from ruler |

Deferred to a follow-up (changes the sub-period model): the **AB Method**
(Subramanyan) — *proportional* sub-periods (share = major × sub-years / 75) with
the nodes *participating* as a 9th sub-ruler. Noted as a future preset, not v1.

### 7.4 Constructor toggles

`FirdariaEngine(chart, *, preset="abu_mashar", year_length=365.2425,
repeat=True, max_age=96, levels=2)`. The preset expands to the underlying
`node_mode` / `nocturnal_node_placement` / `node_subdivision` flags (all also
directly overridable), mirroring how `ZodiacalReleasingEngine` exposes its
Brennan-standard defaults with escape hatches.

**Sunrise/sunset guard:** because the entire sequence hinges on sect, a birth
within ~10 minutes of sunrise/sunset can flip it. When the Sun is that close to
the horizon, emit a warning (the `StelliumWarning` family from the logging work
fits — a `ConfigurationWarning` or a dedicated `SectAmbiguityWarning`) noting the
firdaria may be unreliable and rectification is advisable.

### 7.5 Data models (`core/models.py`, frozen dataclasses)

```python
@dataclass(frozen=True)
class FirdariaPeriod:
    ruler: str
    sub_ruler: str | None       # None for the node majors (no subdivision)
    level: int                  # 1 = major, 2 = sub
    start: datetime
    end: datetime
    start_age: float
    end_age: float

@dataclass(frozen=True)
class FirdariaTimeline:
    periods: tuple[FirdariaPeriod, ...]
    sect: str
    def at(self, when: datetime) -> FirdariaPeriod | None: ...
    def major_periods(self) -> tuple[FirdariaPeriod, ...]: ...
```

---

## 8. Future consumers (designed-for, not built)

- **Length-of-life / alcocoden** — angular → `greater_years`, succedent →
  `mean_years`, cadent → `least_years`, with the aspect modifiers. The primitive's
  three families + the documented angular/cadent mapping (and its minority
  inversion, footnoted) are exactly what it needs.
- **Decennials** — least years as *months* (sum 129 = 10 yr 9 mo each).
- **Planetary days / distributions** — least years and their fractions.

Each imports from `planetary_years` — no re-typing.

---

## 9. Testing strategy

- **Primitive:** least/greater/firdaria exact-value tests; mean = (least+greater)/2;
  greatest variants present & distinct; firdaria sum = 75, least sum = 129,
  greater non-luminary sum = 360.
- **Cross-check (G3):** derive non-luminary greater years from `bound_egypt`;
  assert == `GREATER_YEARS` (ships with the Sagittarius fix, §5).
- **ZR regression:** existing ZR tests unchanged (same values); add one asserting
  ZR reads Capricorn 27 / Aquarius 30 and total 211 as before.
- **Firdaria:** day vs night start ruler; major-period boundaries and total (75);
  sub-period count (7) and Chaldean order; `at()` lookup; nodes don't subdivide;
  unknown-time chart raises.

---

## 10. Open questions

- **Q1 — Sagittarius terms fix in this PR?** (Still open — your call.) Recommend
  yes (it's a clear bug; the cross-check guards it), but it changes dignity
  output, so bundle-here vs. separate dignity-fix PR is your decision.

**Resolved by the Firdaria research** ([docs/methodology/research/firdaria.md](../../methodology/research/firdaria.md)):

- **Q2 — `year_length` → 365.2425** (Gregorian mean solar year). The 360-day
  ideal year is explicitly *not* appropriate for natal firdaria. Toggle exposed
  (365.25 / 365.2422 also allowed) but 360 is documented as mundane-only.
- **Q3 — Repeat past 75 → yes** (Abu Ma'shar "returns to the Sun"; Schoener
  delineates the recurrence), capped at `max_age` (default 96).
- **Q4 — Node subdivision → off** (classical: node majors don't subdivide, nodes
  aren't sub-rulers). The `on`/participating behavior belongs to the deferred AB
  Method preset.
- **Q5 — Unknown-time charts → refuse** (needs sect/ASC), matching profections;
  additionally warn near sunrise/sunset where sect can flip (§7.4).
- **Q6 — Nocturnal node placement → `abu_mashar` (nodes at end) default**, with a
  `bonatti` (after-Mars) preset. This is the field's genuine split, so it ships
  as a prominent, documented toggle rather than a silent choice (§7.3).

---

## 11. Acceptance criteria

- [ ] `stellium/core/planetary_years.py` exists with the four families + Firdaria
      tables + accessors; zero stellium imports; unit-tested.
- [ ] `engines/releasing.py` uses `LEAST_YEARS`; ZR output unchanged; Capricorn
      comment corrected.
- [ ] Greater-years cross-check test passes (with the Sagittarius terms
      corrected, or `xfail` + issue if deferred).
- [ ] `chart.firdaria()` returns a correct day/night-sequenced timeline with
      sub-periods; covered by tests; raises on unknown-time charts.
- [ ] CHANGELOG + a short user note; this spec linked from
      `docs/development/README.md`.
- [ ] No regression in dignity/ZR/profection suites.
