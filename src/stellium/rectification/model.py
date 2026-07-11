"""The baked sect classifier — daylight prior × malefic-of-sect event evidence.

A two-feature logistic regression (logit of the daylight prior, malefic-of-sect
event score), **frozen** from the fit on the 63-chart validated corpus so it needs
no research data at runtime. LOO-CV 70%, out-of-sample 70.6% — see
``docs/development/specs/RECTIFICATION_REPORT.md``. This is the only sect signal
that survived cross-validation; treat its output as an *indicator, not an oracle*.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from stellium.core.models import CalculatedChart
from stellium.rectification._recast import daylight_fraction
from stellium.rectification.evidence import malefic_event_score


@dataclass(frozen=True)
class SectModel:
    """Standardised two-feature logistic model."""

    bias: float
    weights: tuple[float, ...]
    mean: tuple[float, ...]
    std: tuple[float, ...]

    def p_day(self, feats: tuple[float, ...]) -> float:
        z = self.bias
        for w, x, m, s in zip(self.weights, feats, self.mean, self.std, strict=True):
            z += w * (x - m) / s
        return 1.0 / (1.0 + math.exp(-z))


# Frozen from the corpus fit (docs/development/specs/rectification/sect_classifier.py).
BAKED_SECT_MODEL = SectModel(
    bias=0.1753265016649117,
    weights=(0.7990877015021179, 0.7157693588851441),
    mean=(0.08890705864783742, -0.47619047619047616),
    std=(0.40921424024851183, 1.7106310249148882),
)


def sect_features(chart: CalculatedChart, events: Iterable) -> tuple[float, float]:
    """(logit of the daylight prior, malefic-of-sect event score) for this chart."""
    dl = min(max(daylight_fraction(chart), 1e-3), 1 - 1e-3)
    return (math.log(dl / (1 - dl)), malefic_event_score(events))


def calibrated_p_day(chart: CalculatedChart, events: Iterable) -> float:
    """P(day) from the baked classifier — daylight prior tempered by event evidence."""
    return BAKED_SECT_MODEL.p_day(sect_features(chart, events))
