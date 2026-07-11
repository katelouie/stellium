"""Combined sect classifier: daylight prior × malefic-of-sect event evidence.

The Phase-A discovery: the strongest single sect signal is a *free geometric
prior* — the daylight fraction of the birth day (longer day ⇒ more likely born by
day), `P(day | date, latitude)` under a uniform birth-time. On the 63 it scores
68%, beating every event-based signal alone. But the malefic-of-sect event signal
(Mars-flavoured hardship → day, Saturn → night) carries **independent** information
(partial corr +0.30 after controlling for daylight), so combining them — an
informed prior × event likelihood, exactly the theory's structure — beats either:
LOO-CV 70%, clearing the pre-registered gate.

Two features, a tiny logistic regression, pure Python (deterministic).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import harness
import sect_signals as sig
from models import CorpusPerson


def daylight_fraction(person: CorpusPerson, step_minutes: int = 10) -> float:
    """Fraction of the birth day that is day-sect = P(day) under uniform time."""
    sweep = harness.candidate_sects(person, step_minutes=step_minutes)
    return sum(s == "day" for _, s in sweep) / len(sweep)


def features(person: CorpusPerson) -> tuple[float, float]:
    """(logit of the daylight prior, malefic-of-sect signal)."""
    dl = min(max(daylight_fraction(person), 1e-3), 1 - 1e-3)
    return (math.log(dl / (1 - dl)), sig.sect_score(person, use_benefic=False))


@dataclass(frozen=True)
class SectModel:
    """Standardised 2-feature logistic model."""

    bias: float
    weights: tuple[float, float]
    mean: tuple[float, float]
    std: tuple[float, float]

    def p_day(self, feats: tuple[float, float]) -> float:
        z = self.bias
        for w, x, m, s in zip(self.weights, feats, self.mean, self.std, strict=True):
            z += w * (x - m) / s
        return 1.0 / (1.0 + math.exp(-z))


def fit(
    rows: list[tuple[float, float]],
    y: list[int],
    *,
    epochs: int = 4000,
    lr: float = 0.1,
    l2: float = 0.5,
) -> SectModel:
    """Deterministic gradient-descent logistic regression on standardised features."""
    k = len(rows[0])
    mean = tuple(sum(r[j] for r in rows) / len(rows) for j in range(k))
    std = tuple(
        (sum((r[j] - mean[j]) ** 2 for r in rows) / len(rows)) ** 0.5 or 1.0
        for j in range(k)
    )
    xs = [[(r[j] - mean[j]) / std[j] for j in range(k)] for r in rows]
    w = [0.0] * k
    b = 0.0
    n = len(rows)
    for _ in range(epochs):
        gw = [0.0] * k
        gb = 0.0
        for xi, yi in zip(xs, y, strict=True):
            p = 1.0 / (1.0 + math.exp(-(b + sum(w[j] * xi[j] for j in range(k)))))
            err = p - yi
            gb += err
            for j in range(k):
                gw[j] += err * xi[j]
        b -= lr * gb / n
        for j in range(k):
            w[j] -= lr * (gw[j] / n + l2 * w[j] / n)
    return SectModel(bias=b, weights=(w[0], w[1]), mean=mean, std=std)
