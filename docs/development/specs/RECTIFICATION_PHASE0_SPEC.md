# Spec: Rectification Build — Phase 0 (harness) + Phase 1 (sect classifier)

| | |
|---|---|
| **Status** | Draft — the buildable unit |
| **Created** | 2026-07-11 |
| **Owner** | Kate |
| **Type** | Implementation spec (SDD) |
| **Parent** | [RECTIFICATION_SPEC.md](./RECTIFICATION_SPEC.md) · [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md) |
| **Corpus** | [rectification-corpus-events.yaml](./rectification-corpus-events.yaml) (63 people, 888 events) |

---

## 1. Purpose & the one question it answers

Build the smallest honest thing that tells us **whether the whole idea works**:
a **sect classifier** benchmarked on the 63-person corpus. If, given only a
person's dated events, we can recover **day vs night** better than chance, the
rectifier has signal and the later phases are worth building. If we can't, we
learn that cheaply, before writing any calibration machinery.

Two build layers:
- **Phase 0 — the harness.** A fast candidate-time re-cast + a benchmark driver
  that blanks a corpus person's time, runs a technique across candidates, and
  scores the result against the known truth.
- **Phase 1 — the sect classifier.** The first technique on that harness:
  walk the day-sect and night-sect interpretations of a life and score which one
  the events fit. Output `P(day)/P(night)` + a contrastive report.

## 2. Location & promotion (per Q1 = standalone-first)

- **Lives at** `docs/development/specs/rectification/` — a standalone package
  that **imports stellium's public API** as a consumer (like `examples/`).
  **Nothing goes into `src/stellium/` in this phase.**
- **Its own tests** live beside it and run on their own (`python -m pytest
  docs/development/specs/rectification/`), *not* wired into the package suite.
- **Promotion gate → `stellium/rectification/`:** the sect classifier runs
  reproducibly on all 63 and **beats the baseline (§6) by a pre-registered
  margin**. Whatever the re-cast needed that the public API didn't expose is the
  promotion checklist.

```
docs/development/specs/rectification/
  __init__.py
  recast.py          # fast angle-only re-cast (Phase 0)
  harness.py         # corpus loader, blank-the-time, run-across-candidates, scoring
  significators.py   # event-type -> significators table (theory §6)
  sect.py            # Phase 1 sect classifier + contrastive report
  models.py          # LifeEvent, Evidence (standalone; mirror the parent spec)
  run_benchmark.py   # CLI: score the classifier over the 63, emit the report
  tests/
    test_recast.py         # re-cast == full .calculate() to tolerance
    test_sect.py           # determinism + known-sect sanity
```

## 3. Resolved open questions (for this phase)

- **Q1 location** — standalone-first (§2).
- **Q2 grid** — a **uniform fine grid**, default **4 min** (≈ 1° of ASC) across
  the day. Regime-aware cells (sect-flip / ASC-sign boundaries) are deferred to
  Phase 3, where the sharp continuous techniques need them. *For sect
  specifically the grid barely matters* — see §5.2.
- **Q3 significators** — a **fixed weighted table** from theory §6
  (`significators.py`); marginalising over significators is a later refinement.
- **Q4 soft evidence** — **out of Phase 1.** The classifier uses only **hard,
  dated events**; temperament (the soft channel) is Phase 5. Keeps the first
  result defensible.
- **Q5 corpus size** — empirical; 63 is what we have, report accuracy with a
  binomial confidence interval so we don't over-read a small sample.

## 4. Phase 0 — the harness

### 4.1 Fast re-cast — angles per candidate, **Moon per candidate**, slow bodies once

The speed trick from theory §2 — compute the day's bodies once, sweep only the
angles — but with **two corrections that are load-bearing, not niceties:**

**(a) The Moon is not fixed.** It moves ~12–15°/day (~0.5°/hr) — an order of
magnitude more than any other body across a birth-day (inner planets ≤ ~1°/day,
outers < 0.1°). So the split is **slow bodies once, Moon per candidate**:
- Compute Sun + planets **once** for the day (their ≤1°/day drift is negligible).
- Recompute (or interpolate) the **Moon** at each candidate time. Baseline:
  one Moon ephemeris call per candidate (still ~1/15th of a full recompute).
  Optional optimization: sample the Moon at a handful of points and
  cubic-interpolate (its motion is smooth) — decide by profiling, not up front.
- This is not optional cleanliness: the Moon feeds Moon-significator techniques,
  the **progressed Moon**, and the **Lot of Fortune/Spirit** = `Asc ± (Moon −
  Sun)`, which therefore moves with *both* the fast Asc **and** the drifting Moon.

**(b) Everything else is angle-only.** Per candidate, recompute ASC/MC/cusps
(cheap sidereal-time trig via the house engine) and re-place the fixed slow
bodies + the freshly-computed Moon into the new houses.

- `recast(date, lat, lon, tz, times) -> list[AngleSet]`; each `AngleSet` has
  ASC, MC, cusps, the **Moon** at that time, the recomputed **Lots**, and the
  derived **sect** (§4.2). Built **on the public API**; surface gaps → promotion
  checklist.

**Correctness test (blocking):** for a spread of times on several corpus births,
the re-cast's ASC/MC/cusps, **Moon longitude**, Lots, sect, and house placements
match a full `ChartBuilder…calculate()` at the same time to tolerance (angles &
Moon < 0.01°; sect & house placements exact). This is the invariant everything
rides on — and the Moon tolerance is what catches corrections (a).

### 4.2 Sect is a multi-region step function — **compute it, don't assume it**

Sect is simply **Sun above the horizon (day) or below it (night)** at the
candidate time. Because the re-cast already places the fixed-longitude Sun into a
per-candidate house, **sect falls out for free** — and correctly at any date and
latitude. **Never hardcode the region structure or fixed boundary clock times;**
derive `sect(t)` from the Sun's actual altitude.

At **temperate latitudes** — where the whole corpus sits (max ~55°N, London) —
the day sweep does cross the horizon twice, giving the intuitive three regions,
but the boundaries are the *real* sunrise/sunset for that date + place and their
widths swing hard with **season** (a 55°N summer "day" region is ~17 h; in winter
it inverts):

```
00:00 ──night── sunrise ──day── sunset ──night── 24:00   (typical temperate case)
      (pre-dawn)         (daylight)       (post-dusk)
```

But this is **not universal**: above the polar circle you get midnight sun (all
24 h **day**, zero night regions) or polar night (all **night**), and the count
of regions is 1, not 3. The corpus has no such cases, but the harness must be
correct-by-construction rather than assume the temperate picture.

Consequences the harness must honour from the start:
- **The sect marginal sums cells by computed sect:** `P(night) = Σ (cells where
  sect(t)=night)`, `P(day) = Σ (cells where sect(t)=day)` — *however many*
  contiguous runs there are (usually two night + one day here; possibly one of
  each at the extremes). Never a single midpoint split.
- The sect **boundaries** (Sun-altitude zero-crossings) are date/latitude
  dependent and become the first **regime edges** for the Phase-3 grid.
- **True-sect labeling** of each corpus person = the re-cast's sect at the *true*
  time. Get this exactly right — it is the benchmark's ground truth.
- The two firdaria orderings (day vs night) are unchanged; only the *time →
  ordering* mapping steps with sect. The v0 classifier still compares two
  hypotheses; "night" is the one covering **all** night cells, whatever their
  layout.

### 4.3 Benchmark driver (`harness.py`)

- **Load** the corpus YAML → for each person: `birth_data` (truth), `events`,
  `temperament`. Compute the **true sect** and true time from `birth_data`.
- **Blank** the time → the candidate grid over the local day (§3 Q2).
- **Run-across-candidates:** given a scoring function `f(chart_at_t, events) →
  score`, evaluate it on every candidate (using the fast re-cast), returning the
  per-candidate scores.
- **Scoring utilities:** sect-classification accuracy (Phase 1); time MAE and
  calibration coverage are stubbed for later phases.

## 5. Phase 1 — the sect classifier

### 5.1 The signal

Sect flips two things that are (near-)independent of the exact time within the
day, so they're the honest first signal:

1. **Firdaria order** — day charts run Sun→Venus→…; night charts run Moon→…
   (theory / `core/planetary_years`). The **time-lord active at each life event
   differs** between the two sect assumptions.
2. *(layer in only if firdaria alone is weak)* **sect-dependent dignity** — the
   benefic/malefic **of the sect** and the sect light; and the **Lot of
   Fortune/Spirit** formula flip.

### 5.2 Method (v0 — firdaria + significators)

For each person, with time unknown:

1. Build **two** firdaria timelines from birth — `day`-order and `night`-order.
   (Period boundaries shift only trivially with time-of-day, so the grid is
   almost irrelevant here — that's *why* sect is the safe first target.)
2. For each dated **event**, find the active firdaria **period lord** (and
   sub-lord) under each timeline.
3. Score the match between that lord and the event's **significators**
   (`significators.py`): e.g. a `relationship` event scores high if the lord is
   Venus / ruler-of-7th; `career` if Sun / Saturn / ruler-of-10th; etc.
4. Sum across events → `S_day`, `S_night`; normalise (softmax w/ a temperature)
   → `P(day)`, `P(night)`.
5. `predicted_sect = argmax`. Compare to the true sect.

Deterministic, no calibration, no full posterior — the minimum that can show
signal.

### 5.3 Output

- `classify_sect(person) -> {"day": p, "night": 1-p, "detail": [...per-event...]}`
- A **contrastive day/night report**: walk both timelines side by side and show,
  per event, which sect's time-lord fit better — the human-readable "why."

## 6. Benchmark & baseline (the go/no-go)

`run_benchmark.py` over all 63:

- **Metric:** sect-classification accuracy, with a **binomial 95% CI** (n=63 is
  small — report the interval, not just the point).
- **Baselines to beat:**
  - **majority-class** (always predict the more common sect in the corpus), and
  - **time-of-day null** (chance ≈ 50%).
- **Pre-registered success:** accuracy point estimate **≥ 65%** *and* CI lower
  bound above the majority-class rate. (Modest on purpose — we're testing for
  *any* signal, not tuning.)
- **Report:** overall accuracy + CI, confusion (day↔night), and the per-person
  contrastive reports for spot-checking the ones it gets wrong.

## 7. Data models (`models.py`, standalone)

Mirror the parent spec's `LifeEvent` / `Evidence` (frozen dataclasses) so
promotion is a move, not a rewrite. Loader maps the corpus YAML
(`date/precision/type/description/significance/…`) straight onto them.

## 8. Testing

- **`test_recast.py`** — re-cast == full calculation to tolerance (§4.1). Blocking.
- **`test_sect.py`** — determinism (same input → same P), and a sanity case:
  feeding a known-time person's real events makes the classifier favour the true
  sect. Run standalone, not in the package suite.

## 9. Build order

1. `models.py` + corpus loader (+ a couple of load tests).
2. `recast.py` + `test_recast.py` — **stop here until the re-cast is proven**; it's
   the foundation.
3. `significators.py` (table from theory §6).
4. `sect.py` — classifier + contrastive report.
5. `run_benchmark.py` — accuracy + CI over the 63.
6. Read the number. **Go** (promote per §2) / **no-go** (rethink the signal).

## 10. Acceptance criteria

- [ ] Fast re-cast verified against full calculation to tolerance.
- [ ] Harness blanks a corpus time, runs a scorer across candidates, and scores
      sect accuracy over the 63.
- [ ] `classify_sect` + a contrastive day/night report.
- [ ] Benchmark report: accuracy + 95% CI + confusion, vs. both baselines.
- [ ] A written go/no-go call against §6, and — if go — the promotion checklist
      of public-API gaps found while building the re-cast.
