# Spec: Rectification Build — Phase A (time-posterior, sect as marginal)

| | |
|---|---|
| **Status** | Draft — the buildable unit for the full posterior |
| **Created** | 2026-07-11 |
| **Owner** | Kate |
| **Type** | Implementation spec (SDD) |
| **Parent** | [RECTIFICATION_SPEC.md](./RECTIFICATION_SPEC.md) §3–5 (this is "Phase 3") · [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md) |
| **Precursor** | [RECTIFICATION_PHASE1_FINDINGS.md](./RECTIFICATION_PHASE1_FINDINGS.md) — cheap event-character probes topped out at a modest prior (malefic-of-sect: 65%, corr +0.35) |

---

## 1. Why we're here

The cheap, near-time-independent probes are exhausted: firdaria timing = null,
malefic-of-sect character = a real but modest **prior** (65%), benefic = null. To
do better — and to get *time*, not just sect — we need the chart itself: sweep
candidate birth times and score how well each candidate's **time-dependent
timing techniques** light the person's dated events. Birth time is inferred by
grid evaluation; **sect is read off as the marginal** (theory §3–4).

This is the theoretically-grounded core. It is bigger than everything so far.

## 2. The one thing this phase actually delivers

**The pipeline**, not any single technique:

```
candidate grid over the day
  → per candidate: cast chart (full recompute) + evaluate technique activations vs events
  → combine (de-confounded) → un-normalised log-posterior over t
  → normalise → posterior; sect marginal = Σ posterior over day-cells
  → benchmark: sect-marginal accuracy (vs the 65% malefic prior) + time recovery
```

The first technique to *drive* it is **annual profection** — chosen because it is
the cheapest time-dependent technique, reuses our significator table, and directly
upgrades the failed firdaria experiment (firdaria was ~time-independent;
profection's year-lord depends on the **rising sign**, so sweeping the time
changes the lords and the events can discriminate). The **decisive** signal is
expected from the sharp techniques (directions) that plug into the same pipeline
in A2 — but A1 validates the whole machine cheaply.

## 3. Location & reuse

Standalone (`docs/development/specs/rectification/`), promote later. Reuses:
`harness.build_chart` (full recompute — profiled at ~7 ms/chart, so a 360-cell ×
63-person sweep ≈ a couple of minutes, acceptable), `models`, `significators`,
`sect_signals` (the malefic prior, as an optional independent stream), and the
benchmark's Wilson-CI / confusion machinery.

## 4. The model (concrete)

For a candidate time `t` on the birth day:

```
log P(t | events) = log P(t) + Σ_i Σ_j w_j · logL_ij(t)
```

- **Prior `P(t)`** — uniform over the day for v1 (birth-hour base rates later).
- **`L_ij(t)`** — activation of technique `j` for event `i` at chart-cast-`t`:
  "how well are event `i`'s significators lit by technique `j` around its date."
- **De-confounding is built in from the start** (the firdaria lesson): raw
  activation is confounded by base rates, so each technique's contribution is
  scored as **excess over a per-person permutation null** (shuffle event
  type→date), exactly as in `sect.py`. A technique that lights up for everyone
  contributes nothing.
- **Sect marginal** — `P(day) = Σ_{t: sect(t)=day} P(t|events)`, sect computed per
  candidate (Phase-0 spec §4.2; never assume the region structure).

## 5. Milestones

### A1 — the pipeline, driven by profection *(the proving build)*
- Candidate grid over the day (coarse is fine for profection: the year-lord only
  changes when the **rising sign** changes, ~12×/day, so ~20–30 min resolution).
- Per candidate `t`, per event `i`: profected year-lord at `age(d_i)` = ruler of
  the sign `(rising_sign + whole_years) mod 12`; activation = `planet_significance`
  of that lord for event `i`'s type (reuse the table). De-confound vs the
  permutation null. Combine → posterior over `t` → **sect marginal**.
- **Benchmark:** sect-marginal accuracy + CI vs (a) chance 50%, (b) majority 54%,
  (c) **the malefic prior 65%**. Also report **rising-sign recovery** (does the
  posterior mode land near the true ascendant?) as a sanity signal even if sect is
  weak.
- **Go/continue if** the sect marginal is at least on par with the malefic prior
  *and* rising-sign recovery beats chance — i.e. the pipeline extracts real
  time-signal. (Profection is coarse; we do not expect it alone to be decisive.)

### A2 — sharp technique: directions to the angles *(expected decisive signal)*
- Directed MC/ASC (solar-arc ≈ 1°/yr) or transits reaching natal planets/angles:
  exact **age → minute-level** time constraint. Narrow, sharp `L_ij(t)` bumps.
- Adds **time resolution**: report time median-absolute-error, not just sect.
- The sharp bumps × the coarse profection plateau = the coarse-to-fine behaviour
  of theory §4.

### A3 — combine + calibrate
- Combine profection + directions (+ optionally the malefic prior as an
  independent stream) with per-technique weights; **calibrate** weights +
  temperature on the corpus (hold out a slice) so the posterior's credible
  intervals are honest (theory §7). Escalate combiner complexity only if
  validation demands (expert weights → logistic → GBT).

## 6. Data models (extend `models.py` / a new `posterior.py`)

```python
@dataclass(frozen=True)
class Candidate:
    minute_of_day: int
    sect: str                       # "day" | "night" (computed)
    log_like: float                 # Σ de-confounded technique activations

@dataclass(frozen=True)
class TimePosterior:
    person: str
    candidates: tuple[Candidate, ...]   # normalised P in .prob
    p_day: float
    p_night: float
    map_minute: int                     # posterior mode
    # (credible interval + per-event/technique contributions added in A2/A3)
```

## 7. Testing

- **Determinism** — same grid + seed → same posterior.
- **Sanity** — feeding a known chart's events makes the posterior mass fall in the
  correct sect region and near the true ascendant more often than chance.
- **Marginal correctness** — `p_day + p_night == 1`; `p_day` = summed day-cells.
- Standalone tier, not the package suite.

## 8. Build order

1. `posterior.py` — grid + prior + normalise + sect-marginal (technique-agnostic).
2. Profection activation (A1) + wire into the posterior.
3. `run_posterior_benchmark.py` — sect-marginal + rising-sign recovery vs baselines.
4. **Read the number.** Pipeline works? → A2 directions. Weak? → the pipeline is
   still the reusable foundation; go straight to the sharp technique.
5. A2 directions → time MAE. 6. A3 combine + calibrate.

## 9. Open questions

- **Q-A1 — grid resolution:** coarse (rising-sign, ~24 cells) for profection; fine
  (~4 min, 360 cells) once sharp techniques enter. Lean: adaptive per technique.
- **Q-A2 — which sharp technique first:** solar-arc directions to angles vs
  transits-to-angles vs ZR-from-Fortune peaks. Decide from the API scout + which
  carries signal. (ZR-from-Fortune is attractive: it flips by sect *and* is
  event-timed.)
- **Q-A3 — is the malefic prior folded in** as an independent evidence stream, or
  kept separate as a reported cross-check? Lean: fold in at A3, weighted.
- **Q-A4 — combiner:** start hand-weighted; calibrate on the corpus with a holdout
  to avoid overfitting n=63.

## 10. Acceptance criteria

- [ ] `posterior.py`: grid → posterior → sect marginal, technique-agnostic, tested.
- [ ] Profection activation wired in; benchmark reports sect-marginal + CI +
      rising-sign recovery vs chance / majority / the malefic prior.
- [ ] A written call: does the time-posterior beat the cheap prior?
- [ ] (A2) sharp technique → time median-abs-error reported.
- [ ] (A3) calibrated posterior; credible-interval coverage ≈ nominal on a holdout.
