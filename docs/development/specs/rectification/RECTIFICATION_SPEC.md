# Spec: Rectification Tooling

| | |
|---|---|
| **Status** | Draft — exploration (`explore/rectification`) |
| **Created** | 2026-07-10 |
| **Owner** | Kate |
| **Type** | Spec-Driven Development (SDD) design doc |
| **Theory** | [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md) |

---

## 1. Summary

Build a **computational birth-time rectifier**: given a chart with unknown/
uncertain time plus a set of dated life events (and optionally temperament
notes), return a **calibrated posterior distribution over birth time**, with
**sect** as its robust coarse marginal, and a per-event, per-technique
explanation of *why*.

The model is a hierarchical Bayesian grid posterior with a simulation-based
forward model (the astrology engine); see the theory doc. The build is
**incremental and validation-first**: the smallest honest milestone is a **sect
classifier benchmarked on the AA-rated notables**, which proves signal exists
before any calibration machinery is written.

## 2. Goals / Non-Goals

### Goals
- **G1** — A `RectificationResult` posterior over birth time, with a sect
  marginal, credible intervals, and itemised per-event/per-technique
  contributions (explainable by construction).
- **G2** — Reuse existing engines as the forward model (ZR, firdaria,
  profections, directions, returns, transits/search, dignities) — no
  re-derivation.
- **G3** — A **fast candidate re-cast** (planets once; angles-only per candidate).
- **G4** — A **validation harness** over the notables DB: sect-classification
  accuracy, time MAE, and calibration curves.
- **G5** — Empirical **calibration** so credible intervals are honest.
- **G6** — Framed and documented as a *computed indicator, human-in-the-loop*.

### Non-Goals
- **N1** — No deep learning for the inference (grid is exact at 1-D).
- **N2** — No single-timestamp "answer"; always a distribution.
- **N3** — Automatic personality inference is *optional/soft*, not the core.
- **N4** — Not a fully-automatic oracle; the practitioner keeps the final call.

## 3. Architecture

```
UnknownTimeChart + Evidence
        │
        ▼
RectificationEngine
  ├─ candidate grid over the window            (§4.1)
  ├─ fast re-cast: planets once, angles/houses per candidate   (§4.2)
  ├─ per-candidate forward pass → activation features          (§4.3)
  ├─ likelihood combiner (weighted) → log-posterior grid       (§4.4)
  └─ normalise → RectificationResult (posterior, sect marginal, explanations)
        │
        ▼
Calibration (global weights/temperature) ── fit on the notables corpus (§6)
```

### 3.1 Data models (`core/models.py` or a `rectification/` package)

```python
@dataclass(frozen=True)
class LifeEvent:
    date: date                     # best-known date
    precision: str                 # "day" | "month" | "year"
    type: str                      # taxonomy key (relationship, career, ...)
    description: str
    significance: str = "major"    # major | moderate | minor
    significators: tuple[str, ...] = ()   # optional override; else derived

@dataclass(frozen=True)
class Evidence:
    events: tuple[LifeEvent, ...]
    traits: tuple[str, ...] = ()   # soft, optional

@dataclass(frozen=True)
class EventContribution:
    event: LifeEvent
    technique: str
    weight: float
    log_likelihood_peak_time: datetime | None   # where this evidence pulls
    detail: str                                 # human explanation

@dataclass(frozen=True)
class RectificationResult:
    window_start: datetime
    window_end: datetime
    posterior: tuple[tuple[datetime, float], ...]   # (candidate time, prob)
    p_day: float
    p_night: float
    map_estimate: datetime                          # posterior mode
    credible_intervals: dict[float, tuple[datetime, datetime]]  # e.g. {0.68: (...)}
    contributions: tuple[EventContribution, ...]
    information_budget: float                        # expected achievable sharpness
    notes: tuple[str, ...]
```

### 3.2 API

```python
result = chart.rectify(evidence, resolution="4min")   # on an UnknownTimeChart
result.p_day, result.p_night
result.map_estimate, result.credible_intervals[0.68]
for c in result.contributions: ...          # explain

# Coarse-only shortcut (the first milestone):
sect = chart.classify_sect(evidence)         # -> {"day": 0.82, "night": 0.18}
```

Underneath: `RectificationEngine(chart, evidence, *, calibration=...)`. On a
timed chart, `rectify()` can still *refine* around the known time.

## 4. Mechanics

- **4.1 Candidate grid.** Window = full day (unknown) or ±N hr (approximate),
  stepped at a configurable resolution (default ~4 min ≈ 1° of ASC). Optionally
  **regime-aware**: bound cells by sect flips and ASC sign-changes so discrete
  techniques evaluate once per regime.
- **4.2 Fast re-cast.** Compute planetary positions once for the day; per
  candidate, recompute only ASC/MC/cusps and anything angle-derived (sect,
  Fortune/Spirit, house placements). Avoid full `.calculate()` per candidate.
- **4.3 Activation features.** Per (candidate, event): for each technique,
  extract "how well and how sharply is this event's significator activated near
  its date" — e.g. directed-angle arc vs. age, ZR peak/LB coincidence, active
  firdaria period ruler, profected-year lord, transit-to-angle proximity. Reuse
  the search engine's `find_*` inverters and the electional `predicates` as
  ready-made "does this hold" primitives.
- **4.4 Likelihood combiner.** Map features → per-pair log-likelihood; weight and
  sum with the prior (theory §3.2). Start with **hand-set weights**; the
  calibration layer (§6) fits them later.

## 5. Phased plan (each independently shippable & informative)

- **Phase 0 — Harness.** Candidate grid + fast angle-only re-cast + a way to run
  any technique across candidates. Pure plumbing; tested for correctness/speed.
- **Phase 1 — Sect classifier (the proving experiment).** Only the coarse
  evidence (sect-dependent dignity/almuten shift, firdaria period matching,
  optional soft traits) → `P(day)/P(night)`. Ship `chart.classify_sect()` and a
  **contrastive day/night report** (walk both paths, show what differs).
- **Phase 2 — Notables validation harness.** Blind-test sect classification over
  the AA corpus → accuracy; wire the plumbing for time MAE + calibration curves.
  *This is the go/no-go gate: does the signal exist?*
- **Phase 3 — Continuous posterior.** Add the sharp, time-sensitive techniques
  (directions/transits to angles, ZR peaks, returns) → full posterior over `t`
  with credible intervals and the explanation object.
- **Phase 4 — Calibration.** Fit global weights/temperature on the corpus;
  calibrate credible-interval coverage. Escalate combiner complexity only if
  validation demands (expert weights → logistic regression → GBT).
- **Phase 5 — Soft evidence & extensions.** Personality channel (human-in-loop
  or LLM-elicited, flagged); the information-budget elicitation UX; optionally the
  prenatal-epoch contributor.

## 6. Calibration & data

- **Corpus:** AA-rated notables with documented, dated life events + temperament
  notes, gathered via the companion research prompt
  (`rectification-corpus-research-prompt.md`). **Provenance is verified at the
  source, not trusted from our DB** — our `data_quality`/`has_reliable_time`
  layer proved unreliable (rectified times mislabeled AA, uncited biography times
  mislabeled A), so the prompt independently re-establishes each birth time from
  an AstroDataBank/primary source note and *rejects* anything rectified,
  aggregator-sourced, or undocumented before it can enter the corpus. Its
  `rejected:` output back-corrects the notables DB, so the verify-reject loop
  runs **once**. Critically, **rectified times are excluded** — validating a
  rectifier against a rectified time is circular.
- **Fit:** global per-technique weights + temperature; hold out a slice for
  honest reporting.
- **Report:** sect accuracy; time median-abs-error; **coverage** (does the 68%
  interval contain truth ~68% of the time?).

## 7. Testing strategy

- **Correctness:** the fast re-cast matches a full `.calculate()` at the same
  time (angles, sect, house placements) to tolerance.
- **Sanity:** on a known-time notable, feeding its true events makes the
  posterior peak near the true time and `classify_sect` returns the correct sect.
- **Determinism:** grid + fixed weights → reproducible posterior.
- **Benchmark (slow tier):** the notables harness runs as an offline script/test
  producing the accuracy/MAE/coverage report (not a per-commit gate).

## 8. Open questions

- **Q1 — Package home:** ~~a new top-level `stellium/rectification/`, or fold into
  an existing subsystem?~~ **Resolved (2026-07-11): standalone-first.** Build the
  proving harness *outside* the package as a consumer of stellium's public API
  (under `docs/development/specs/rectification/`), keep `src/stellium/` untouched
  until the sect classifier proves signal on the 63-person benchmark, then
  **promote** the proven core into `stellium/rectification/`. Building against the
  public surface doubles as a test of whether that surface suffices; gaps found
  become the promotion checklist. See the build spec:
  [RECTIFICATION_PHASE0_SPEC.md](./RECTIFICATION_PHASE0_SPEC.md).
- **Q2 — Resolution/regime cells:** uniform grid vs. regime-bounded cells. (Lean:
  regime-aware for the discrete techniques, fine grid for the sharp ones.)
- **Q3 — Significator mapping:** fixed table vs. weighted-and-marginalised. (Lean:
  start fixed table from theory §6; marginalise later if it helps.)
- **Q4 — Soft evidence in v1?** Recommend deferring to Phase 5; keep the core
  purely event-driven and defensible first.
- **Q5 — Corpus size for meaningful calibration:** how many notables/events are
  needed before the fitted weights are trustworthy (vs. staying with expert
  priors)? Determined empirically in Phase 2.

## 9. Acceptance criteria

- [ ] `RectificationEngine` + `RectificationResult` with sect marginal, credible
      intervals, and itemised contributions.
- [ ] Fast angle-only re-cast verified against full calculation.
- [ ] `chart.classify_sect()` + a contrastive day/night report.
- [ ] Notables validation harness reporting sect accuracy, time MAE, and
      calibration coverage.
- [ ] Posterior credible intervals are calibrated (coverage ≈ nominal) after
      Phase 4.
- [ ] Docs framing it as a computed, explainable, human-in-the-loop indicator;
      theory + spec linked from `docs/development/README.md`.
- [ ] No regression in the engines it orchestrates.
