"""Sect rectification — the compare-hypothesis workbench, promoted from research.

An honest, human-in-the-loop sect (day/night) analysis for charts whose birth
*time* is uncertain. It does **not** claim to invert time (the empirical study
found minute-level rectification is an ill-posed inverse); it recovers the one
recoverable bit — sect — at ~70% from biography-thin data, and lays out both
hypotheses for a practitioner to adjudicate with real knowledge.

Public API::

    from stellium.rectification import analyze_sect
    a = analyze_sect(chart)              # notables: events auto-looked-up
    a = analyze_sect(chart, events=...)  # anyone: supply LifeEvents
    print(a.p_day, a.leans)

Full write-up: ``docs/development/specs/rectification/RECTIFICATION_REPORT.md``.
"""

from stellium.rectification.analysis import (
    Hypothesis,
    PlanetCondition,
    SectAnalysis,
    analyze_sect,
)
from stellium.rectification.firdaria import FirdariaConvergence, firdaria_convergence
from stellium.rectification.matrix import (
    ConvergenceMatrix,
    HookPeak,
    MatrixColumn,
    convergence_matrix,
)
from stellium.rectification.model import BAKED_SECT_MODEL, SectModel, calibrated_p_day

__all__ = [
    "analyze_sect",
    "SectAnalysis",
    "Hypothesis",
    "PlanetCondition",
    "FirdariaConvergence",
    "firdaria_convergence",
    "calibrated_p_day",
    "SectModel",
    "BAKED_SECT_MODEL",
    "convergence_matrix",
    "ConvergenceMatrix",
    "MatrixColumn",
    "HookPeak",
]
