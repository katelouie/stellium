# Phase 1 findings — sect classifier v0 (firdaria × significators)

| | |
|---|---|
| **Date** | 2026-07-11 |
| **Verdict** | **NO-GO** — firdaria-lord matching does not recover sect |
| **Code** | `docs/development/specs/rectification/` (sect.py, run_benchmark.py) |
| **Spec** | [RECTIFICATION_PHASE0_SPEC.md](./RECTIFICATION_PHASE0_SPEC.md) §5–6 |

## The experiment

Blank each of the 63 corpus people's birth time; predict day vs night from their
dated events alone, by matching the active firdaria time-lord (day-order vs
night-order) to each event's natural planetary significators (theory §6). This is
the pre-registered proving experiment: does the approach beat chance?

## Result

| Variant | Accuracy | Notes |
|---|---|---|
| Raw day-vs-night sums | 49.2% | strong **night bias** (predicted night 43/63) |
| Permutation-null de-confounded | 41.3% | bias gone, balanced confusion, still chance |
| Best achievable (any threshold, any ablation) | **54.0%** | = majority class ("always day") |

- 95% CI (de-confounded) = [30%, 54%] — **straddles 50%**.
- corr(continuous signal, true sect) = **−0.17 to −0.22** across all variants —
  slightly *negative*, ≈ 1.7 SE from zero at n=63, i.e. **indistinguishable from
  no signal**.
- Ablations (major-lord-only, major-events-only, ± sub-lord) all land at the
  majority-class 54%. The null is robust.

**Pre-registered gate (acc ≥ 65% AND CI-low > majority): NO-GO.**

## What we learned (the diagnosis)

1. **The raw comparison is confounded.** The night firdaria order front-loads
   Saturn/Jupiter/Mars in the event-dense early decades, and those are the
   *generically-significant* planets (Saturn signifies 8/15 event types). So the
   night ordering scores higher for *anyone*, regardless of true sect — a nuisance
   factor, not sect signal. A per-person permutation null removes it cleanly.
2. **De-confounded, there is simply no signal.** Firdaria periods are long
   (7–13 yr), so a documented life samples only ~5–7 distinct major lords — very
   few "measurements" of a type↔lord association that is itself weak. Firdaria
   lacks the resolution to fix sect.
3. This is a *clean, cheap* result: the shortcut of reading sect off firdaria
   alone — appealing because it's near time-independent — does not work. Better to
   know before building a posterior on it.

## Options from here (a genuine fork)

- **A — Sharp techniques, not coarse firdaria.** The theory's real claim is sect
  as the *marginal of the full event-posterior*. Firdaria was a hopeful shortcut;
  the signal may live in the **sharp, angle-tied techniques** (directions/transits
  to the angles, ZR peaks, profected-year lords) that the shortcut skipped. This
  is bigger (needs the candidate grid + more engines) but is the theoretically
  grounded path.
- **B — The sect-dependent dignity/lots channel** (spec §5.1 fallback): benefic/
  malefic *of the sect*, the sect light, and the Lot of Fortune/Spirit formula
  flip. Fuzzier and more temperament-linked (leans on the soft channel we
  deferred).
- **C — Reconsider whether events-only can fix sect at all**, vs. needing the
  temperament/chart-coherence signal a human rectifier actually uses.

The machinery (loader, harness, significators, benchmark, contrastive report) is
built, tested, and reusable for whichever direction we take.

---

## Phase 1B — malefic-contrary-to-sect probe (option B) — **SIGNAL**

`probe_malefic_sect.py`. Doctrine: the malefic *out of sect* is the sharper
destroyer — **Mars out of sect by day, Saturn out of sect by night** — so a life's
misfortunes should carry the flavour of its contrary-sect malefic. Prediction:
Mars-flavoured hardship → **day**, Saturn-flavoured → **night**. Nearly chart-free
(reads the *character* of the misfortunes via a priori Mars/Saturn keyword lists),
and a completely different mechanism from firdaria.

| metric | value |
|---|---|
| accuracy | **65.1%** (41/63) |
| decided-only (drop 14 keyword-silent ties) | 65.3% (32/49) |
| **corr(mars−saturn, day)** | **+0.346** — ≈ 2.9 SE from 0, **p ≈ 0.005** |
| 95% CI | [52.8%, 75.7%] (lower bound just under the 54% majority) |
| confusion | both diagonals dominant (day 22/12, night 10/19) |

**Pre-registered gate: still NO-GO** (CI-low 52.8% < majority 54%) — but this is a
*genuine, directionally-correct effect*, not the firdaria null. The extremes are
convincing: strongest-Saturn lives (Ted Bundy, Hannah Arendt, Ali, Obama) classify
night; strongest-Mars (Hemingway, Frida Kahlo, JFK, van Gogh, Plath) classify day.

**Interpretation:** events *do* carry sect information — via the malefic-of-sect
character of misfortune, **not** via the firdaria time-lord sequence. Modest
(65%), needs development, and the keyword lists carry some researcher DOF (set a
priori, but worth a holdout).

### Phase 1C — benefic-of-sect mirror + combination — **benefic is NULL**

`sect_signals.py`, `probe_sect_combined.py`. Symmetric hypothesis: Jupiter is
benefic *of sect* by day, Venus by night → Jupiter-flavoured fortune → day,
Venus-flavoured → night.

| signal | accuracy | corr(score, day) |
|---|---|---|
| malefic-only | 65.1% | **+0.346** |
| benefic-only | 52.4% | **+0.021** (null) |
| combined | 52.4% | +0.169 (diluted) |

The benefic mirror carries **no signal**, and combining it *dilutes* the malefic
(+0.35 → +0.17). Diagnosis: **fortune-character is domain-linked, not sect-linked**
— artists accumulate Venus-flavoured fortune (art/exhibitions), scientists and
politicians Jupiter-flavoured (awards/office), independent of sect — so the
benefic channel injects profession noise. Misfortune-character (sudden/violent vs
slow/chronic) is far more universal, which is why the malefic side works and the
benefic doesn't.

**Conclusion:** keep **malefic-only** (corr +0.346, p ≈ 0.005) as a real but
modest sect *prior*; drop the benefic. The cheap event-character approach tops out
≈ 65% — useful as one evidence stream, not a decisive classifier.

## Where things stand (post-B)

- Two mechanisms tried from events alone: firdaria timing = **null**;
  malefic-of-sect character = **real but modest** (65%, p≈0.005, doesn't clear the
  strict gate); benefic-of-sect = **null** (domain confound).
- Events *do* carry sect signal, but weakly and only through misfortune character.
  A decisive sect read likely needs the chart itself (option A: the sharp,
  angle-tied techniques → full posterior, sect as the marginal), which is the
  larger build we deferred.
