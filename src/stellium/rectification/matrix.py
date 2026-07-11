"""The two-lens Tebbs convergence matrix (exploratory, heavy) — as data.

One candidate-time sweep feeds two lenses:

* **Lens A — structural band:** the genuinely distinct charts across the 24h (each
  sect region × Ascendant sign), each scored by the time-discriminating methods.
* **Lens B — event hooks:** how many distinct events get an apt directed/transiting
  hit at each candidate time — the times the events themselves nominate.

Every timing score is whisper-level and never summed; the matrix is a *display* for
human adjudication. Heavy (~10 s: a 96-candidate sweep with directions per
candidate). See ``docs/development/specs/rectification/RECTIFICATION_REPORT.md``.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from stellium.core.models import CalculatedChart
from stellium.rectification._data import DOMICILE_RULER
from stellium.rectification._recast import local_birth_date, recast, require_obj
from stellium.rectification.firdaria import firdaria_convergence
from stellium.rectification.model import calibrated_p_day
from stellium.rectification.timing import (
    directions_hooks,
    make_directions_scorer,
    make_profection_scorer,
    make_transits_scorer,
    progressed_moon_signal,
    transiter_positions,
    transits_hooks,
)

SWEEP_STEP = 15  # minutes


@dataclass(frozen=True)
class MatrixColumn:
    start_minute: int
    sect: str
    asc_sign: str
    asc_ruler: str
    dir: float
    trans: float
    prof: float


@dataclass(frozen=True)
class HookPeak:
    minute: int
    sect: str
    asc_sign: str
    count: int
    detail: tuple[str, ...]


@dataclass(frozen=True)
class ConvergenceMatrix:
    """Renderer-neutral two-lens convergence data."""

    name: str
    p_day: float
    columns: tuple[MatrixColumn, ...]
    firdaria_day: float
    firdaria_night: float
    progressed_moon: float
    convergence_counts: tuple[int, ...]
    method_peak_index: dict  # 'dir'/'trans'/'prof' -> column index
    hooks_by_hour: tuple[int, ...]  # 24 buckets
    hook_peaks: tuple[HookPeak, ...]
    hooks_spread: bool
    a_convergent: bool
    a_winner_index: int | None

    @property
    def anchor_sect(self) -> str:
        return "day" if self.p_day >= 0.5 else "night"


def _sweep(chart: CalculatedChart, events: Sequence) -> list[dict]:
    birth = local_birth_date(chart)
    dir_score = make_directions_scorer(events, birth)
    prof_score = make_profection_scorer(events, birth)
    tpos = transiter_positions(events, chart)
    trans_score = make_transits_scorer(events, tpos)

    grid: list[dict] = []
    for minute in range(0, 24 * 60, SWEEP_STEP):
        c = recast(chart, minute // 60, minute % 60)
        grid.append(
            {
                "minute": minute,
                "sect": c.sect,
                "asc": require_obj(c, "ASC").sign,
                "dir": dir_score(c),
                "prof": prof_score(c),
                "trans": trans_score(c),
                "dir_hooks": directions_hooks(c, events, birth),
                "trans_hooks": transits_hooks(c, events, tpos),
            }
        )
    return grid


def _columns(grid: list[dict]) -> list[MatrixColumn]:
    groups: list[dict] = []
    for cell in grid:
        key = (cell["sect"], cell["asc"])
        if not groups or groups[-1]["key"] != key:
            groups.append({"key": key, "members": [cell]})
        else:
            groups[-1]["members"].append(cell)
    if len(groups) > 1 and groups[0]["key"] == groups[-1]["key"]:
        groups[0]["members"] = groups[-1]["members"] + groups[0]["members"]
        groups.pop()

    cols: list[MatrixColumn] = []
    for g in groups:
        sect, asc = g["key"]
        members = g["members"]
        cols.append(
            MatrixColumn(
                start_minute=members[0]["minute"],
                sect=sect,
                asc_sign=asc,
                asc_ruler=DOMICILE_RULER[asc],
                dir=statistics.mean(m["dir"] for m in members),
                trans=statistics.mean(m["trans"] for m in members),
                prof=statistics.mean(m["prof"] for m in members),
            )
        )
    cols.sort(key=lambda c: c.start_minute)
    return cols


def convergence_matrix(
    chart: CalculatedChart, *, events: Iterable | None = None
) -> ConvergenceMatrix:
    """Compute the two-lens convergence matrix for ``chart``.

    Args:
        chart: the natal chart (hypotheses re-cast from its date + place).
        events: life events to weigh; auto-looked-up for notables if ``None``.

    Returns:
        A :class:`ConvergenceMatrix` (a display, not a verdict).
    """
    from stellium.rectification.analysis import _auto_events

    ev: list = list(events) if events is not None else list(_auto_events(chart))

    p_day = calibrated_p_day(chart, ev)
    name = chart.metadata.get("name") or "this chart"
    if not ev:
        # Nothing to sweep against; return an empty-but-valid matrix.
        return ConvergenceMatrix(
            name=name,
            p_day=p_day,
            columns=(),
            firdaria_day=0.0,
            firdaria_night=0.0,
            progressed_moon=0.0,
            convergence_counts=(),
            method_peak_index={},
            hooks_by_hour=tuple([0] * 24),
            hook_peaks=(),
            hooks_spread=False,
            a_convergent=False,
            a_winner_index=None,
        )

    grid = _sweep(chart, ev)
    cols = _columns(grid)
    fird = firdaria_convergence(chart, ev)
    pmoon = progressed_moon_signal(chart, ev)

    # Lens A convergence: which column each method peaks in
    peak_index = {}
    for key in ("dir", "trans", "prof"):
        vals = [getattr(c, key) for c in cols]
        peak_index[key] = max(range(len(cols)), key=lambda i: vals[i])
    counts = tuple(
        sum(1 for k in peak_index if peak_index[k] == i) for i in range(len(cols))
    )
    best_count = max(counts) if counts else 0
    a_convergent = best_count >= 2
    a_winner = counts.index(best_count) if counts else None

    # Lens B: hooks per candidate → per-hour histogram + peaks
    for cell in grid:
        cell["hooked"] = cell["dir_hooks"] | cell["trans_hooks"]
    by_hour = [0] * 24
    for cell in grid:
        h = cell["minute"] // 60
        by_hour[h] = max(by_hour[h], len(cell["hooked"]))
    maxh = max(by_hour) if by_hour else 0
    spread = sum(1 for v in by_hour if v >= 0.6 * maxh) >= 8 if maxh else False

    peaks: list[HookPeak] = []
    for cell in sorted(grid, key=lambda c: -len(c["hooked"]))[:3]:
        if not cell["hooked"]:
            continue
        detail = []
        for i in sorted(cell["hooked"]):
            e = ev[i]
            tech = []
            if i in cell["dir_hooks"]:
                tech.append("dir")
            if i in cell["trans_hooks"]:
                tech.append("tr")
            detail.append(f"{e.date}·{e.type}[{'+'.join(tech)}]")
        peaks.append(
            HookPeak(
                minute=cell["minute"],
                sect=cell["sect"],
                asc_sign=cell["asc"],
                count=len(cell["hooked"]),
                detail=tuple(detail[:6]),
            )
        )

    return ConvergenceMatrix(
        name=name,
        p_day=p_day,
        columns=tuple(cols),
        firdaria_day=fird.signal_day,
        firdaria_night=fird.signal_night,
        progressed_moon=pmoon,
        convergence_counts=counts,
        method_peak_index=peak_index,
        hooks_by_hour=tuple(by_hour),
        hook_peaks=tuple(peaks),
        hooks_spread=spread,
        a_convergent=a_convergent,
        a_winner_index=a_winner,
    )
