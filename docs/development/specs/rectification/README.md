# Rectification — the arc

Computational birth-time rectification: the research that asked *can we recover an
unknown birth time from life events?*, found that **minute-level time is an
ill-posed inverse** (unrecoverable), and that **sect (day/night) is recoverable at
~70%** — which then shipped as the `stellium.rectification` package subsystem.

**Start here:** [`RECTIFICATION_REPORT.md`](./RECTIFICATION_REPORT.md) — the capstone
write-up (corpus, methodology, the ill-posed-inverse framing, the convergence test,
confound checks, and the one traditional doctrine that survived).

## What's in this folder

| Path | What it is |
|---|---|
| [`RECTIFICATION_REPORT.md`](./RECTIFICATION_REPORT.md) | **The capstone.** The full empirical study and its conclusions. |
| [`RECTIFICATION_THEORY.md`](./RECTIFICATION_THEORY.md) | The original Bayesian-grid theory (forward model, sect as a marginal). |
| [`RECTIFICATION_SPEC.md`](./RECTIFICATION_SPEC.md) | Data models, API, phased plan for the (unbuilt) grand engine. |
| [`RECTIFICATION_PHASE0_SPEC.md`](./RECTIFICATION_PHASE0_SPEC.md) | The standalone re-cast + benchmark harness + sect classifier spec. |
| [`RECTIFICATION_PHASEA_SPEC.md`](./RECTIFICATION_PHASEA_SPEC.md) | The time-posterior from time-dependent techniques (profection → directions). |
| [`RECTIFICATION_PHASE1_FINDINGS.md`](./RECTIFICATION_PHASE1_FINDINGS.md) | The running lab log of every sub-finding. |
| [`data/`](./data/) | The frozen **63-person verified corpus** (`rectification-corpus-events.yaml`, 888 events) + the out-of-sample `rectification-modern-cohort.yaml`. |
| [`research/`](./research/) | The provenance-first research prompts, candidate roster, and the events worklist (ADB source pages) used to gather the corpus. |
| [`tooling/`](./tooling/) | `assemble_corpus.py` (batches → corpus YAML) and `apply_research_verdicts.py` (writes provenance verdicts back to the notables DB). |
| `harness/` | The standalone proving code that produced the report's numbers. **Untracked/local** (git-ignored) — superseded by the package subsystem, kept for reproducibility. |

## Where it shipped

The validated finding — sect recovery — is now first-class package surface:

- **Package:** `stellium.rectification` (`analyze_sect`, `convergence_matrix`) — see
  [../../SUBSYSTEMS.md](../../SUBSYSTEMS.md).
- **User guide:** [../../../astrology/RECTIFICATION.md](../../../astrology/RECTIFICATION.md)
  — what it is, how to use it, and how *not* to.

## Re-running the harness (local)

The `harness/` is git-ignored but kept on disk. It uses flat imports (a `conftest.py`
puts its own dir on `sys.path`) and reads the corpus from `../data/`:

```bash
source ~/.zshrc && pyenv activate starlight
cd docs/development/specs/rectification/harness
python -m pytest            # the harness's own tests
python probe_malefic_sect.py   # e.g. the malefic-of-sect probe
```
