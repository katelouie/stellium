# Spec: Length of Life (Hyleg / Alcocoden / Years-Table)

| | |
|---|---|
| **Status** | Draft — for review |
| **Created** | 2026-07-09 |
| **Owner** | Kate |
| **Type** | SDD design doc (short) |
| **Depends on** | `core/planetary_years.py` (greater/mean/least years) |
| **Research** | `~/Downloads/hellenistic-years.md` (alcocoden section) |

---

## 1. Summary

Build the classical **length-of-life** technique (Perso-Arabic years-table
method) — and, along the way, two **reusable primitives** it needs: an
**almuten-of-a-degree** calculator and a **hyleg** finder.

Scope is the years-table path (hyleg → alcocoden → years → modifiers), **Lilly**
as default authority. Ptolemy's *directional* method (primary-directing the
hyleg to the anareta) is **deferred** — noted, not built.

**Framing:** this is a *computed traditional indicator*, not a prediction of
actual lifespan. Docstrings and docs state this plainly; the result object is
built to "show its work," never to emit a bare number as fact.

---

## 2. Reusable primitives (built here, useful everywhere)

### 2.1 Almuten of a degree — `engines/almuten.py`

The essential-dignity *victor* over a longitude: for each of the seven planets,
sum its essential dignities at that degree (domicile 5, exaltation 4, triplicity
3, term 2, face 1), return the highest scorer.

```python
def almuten_of_degree(
    longitude: float, sect: str, *, system: str = "traditional"
) -> AlmutenResult: ...

@dataclass(frozen=True)
class AlmutenResult:
    winner: str                    # planet with most essential dignity
    scores: dict[str, int]         # per-planet essential-dignity score
    dignities: dict[str, list[str]]  # which dignities each planet holds here
    tie: tuple[str, ...]           # winners if tied (see tie-break)
```

Notes: triplicity is sect-dependent (hence the `sect` arg). Tie-break: prefer the
planet with the higher accidental strength (angular > succedent > cadent); expose
the raw `scores` so callers can apply their own rule. This is **distinct** from
the existing `chart.get_strongest_planet()`, which finds the almuten *among
placed planets*; this is the almuten *of a point*.

### 2.2 Hyleg finder — `engines/length_of_life.py` (or a `hyleg()` helper)

The prorogator/giver-of-life. Candidates are tested in a sect-ordered priority
list; the first that sits in a **hylegiacal ("aphetic") place** wins.

- **Candidates (Lilly, default):** by day — Sun, Moon, Ascendant, Lot of
  Fortune, prenatal Syzygy; by night — Moon, Sun, Ascendant, Fortune, Syzygy.
- **Hylegiacal places:** Ptolemy's aphetic houses — 1, 11, 10, 9, 7 (above the
  horizon). The exact degree boundaries (e.g. 5° above the Asc) are a documented
  refinement; v1 uses whole-house membership and flags this as a config point.
- **Prenatal Syzygy:** the New/Full Moon immediately before birth — computed via
  the existing search engine (`find_...` lunation helpers). Its *degree* is the
  candidate.

```python
@dataclass(frozen=True)
class HylegResult:
    point: str            # "Sun" | "Moon" | "Ascendant" | "Fortune" | "Syzygy"
    longitude: float
    place: int            # the hylegiacal house it occupies
    method: str           # "lilly"
    candidates_tried: tuple[tuple[str, bool], ...]  # (candidate, qualified?) trace
```

---

## 3. Length of life — `chart.length_of_life(method="lilly")`

### 3.1 Procedure

1. **Hyleg** via §2.2.
2. **Alcocoden** = `almuten_of_degree(hyleg.longitude, sect)` (§2.1), subject to
   Lilly's condition that it **aspects/beholds the hyleg** (or occupies the
   hyleg's place). If the top almuten doesn't behold the hyleg, fall to the next
   qualifying planet; record the choice.
3. **Base years** by the alcocoden's **angularity**:
   angular → `greater_years`, succedent → `mean_years`, cadent → `least_years`.
4. **Modifiers** (Lilly; each itemized in the result):
   - Benefic (Jupiter/Venus) beholding the alcocoden → **+ its least years**.
   - Mercury (if strong / free of the malefics) beholding → **+ its least years**.
   - Sun/Moon in sextile/trine → **+ its least years**.
   - Malefic (Saturn/Mars) by conjunction/square/opposition → **− its least
     years**; Sun/Moon by conj/square/opp → **− its least years**.
   - Alcocoden in **fall or retrograde** → **× ½**.
   - Alcocoden **combust** → yields **months** (or days) instead of years — the
     result carries a `unit` field.

### 3.2 Result model

```python
@dataclass(frozen=True)
class LengthOfLifeResult:
    hyleg: HylegResult
    alcocoden: str
    alcocoden_angularity: str          # "angular" | "succedent" | "cadent"
    base_years: float                  # from the years family
    base_family: str                   # "greater" | "mean" | "least"
    modifiers: tuple[YearModifier, ...]  # itemized adjustments
    total: float
    unit: str                          # "years" | "months" | "days"
    method: str                        # "lilly"
    notes: tuple[str, ...]             # caveats, fallbacks taken

@dataclass(frozen=True)
class YearModifier:
    source: str        # e.g. "Jupiter"
    reason: str        # e.g. "benefic trine to alcocoden"
    delta: float       # +/- years (or a factor description in `reason`)
```

### 3.3 Presets / authorities

`method`: `"lilly"` (default) and `"bonatti"` (close variant — differs mainly in
the modifier list and a couple of hyleg-order details). `"ptolemy"` (directional)
is **reserved but not implemented** in this PR; requesting it raises
`NotImplementedError` with a pointer to the follow-up.

### 3.4 Requirements & refusals

Requires houses, angles, and sect — so it **raises on unknown-time charts**
(like Firdaria/profections). Best on a house system with clear angularity
(Whole Sign or Placidus); the house system is a parameter.

---

## 4. Public API

- `chart.length_of_life(method="lilly", house_system=None) -> LengthOfLifeResult`
- `chart.hyleg(method="lilly") -> HylegResult` (the general primitive)
- `almuten_of_degree(longitude, sect)` from `stellium.engines`
  (+ `AlmutenResult`, `HylegResult`, `LengthOfLifeResult`, `YearModifier`
  exported like the other engine result types).

---

## 5. Testing

- **Almuten primitive:** hand-checked degrees → known victor (e.g. 15° Aries →
  Sun/Mars contest; a term boundary case); tie handling; sect-sensitivity of
  triplicity.
- **Hyleg:** on fixture charts, the expected candidate wins and the trace records
  the ones skipped; day vs night ordering; a chart where the sect light is *not*
  hylegiacal falls through correctly.
- **Alcocoden + years:** angularity → correct family (greater/mean/least);
  behold-the-hyleg fallback taken when needed.
- **Modifiers:** each rule fires on a constructed configuration; combust →
  `unit="months"`; fall/retrograde halves; itemized `modifiers` add up to
  `total`.
- **Refusal:** unknown-time chart raises.

---

## 6. Open questions

- **Q1 — Syzygy in v1?** Include the prenatal-lunation candidate now, or ship
  hyleg with Sun/Moon/Asc/Fortune first and add Syzygy as a fast-follow?
  *(Recommend include it — the search engine already finds lunations; leaving it
  out changes hyleg results for a real fraction of charts.)*
- **Q2 — Aphetic-place precision.** Whole-house membership (simple, v1) vs. the
  degree-based Ptolemaic boundaries (5° above Asc, etc.). *(Recommend
  whole-house v1, boundaries as a documented toggle later.)*
- **Q3 — Bonatti preset in v1** or Lilly-only first? *(Recommend Lilly-only v1;
  add Bonatti once the modifier framework is proven.)*

---

## 7. Acceptance criteria

- [ ] `almuten_of_degree` primitive + `AlmutenResult`, unit-tested and exported.
- [ ] `chart.hyleg()` returns a traced `HylegResult`; sect-ordered; refuses
      unknown-time.
- [ ] `chart.length_of_life()` returns an itemized `LengthOfLifeResult` whose
      `modifiers` sum to `total`; Lilly default; `ptolemy` raises
      `NotImplementedError`.
- [ ] Base years read from `core/planetary_years` by angularity.
- [ ] Docstrings + a short user note frame it as a computed indicator, not a
      lifespan prediction; spec linked from `docs/development/README.md`.
- [ ] No regression in dignity/ZR/firdaria/profection suites.
