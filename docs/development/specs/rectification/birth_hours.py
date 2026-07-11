"""External birth-hour distributions → an informed P(day) prior.

Replaces the uniform-birth-time assumption in the sect prior with a real hourly
birth distribution (theory §3.1). Source:
`docs/development/specs/birth_times_research.md` — population vital-statistics /
epidemiology, NO chart samples, so the prior stays independent of the target.

`spontaneous_prewar` (Distribution A) is the default for our historical
international cohort (concentrated 1850–1970): nocturnal, peak ~04:00, trough
~15:00. `modern_us` (Distribution C, 6-hour blocks spread to hours) is the
medicalized daytime-concentrated contrast for era-blending late-20th-c. births.
"""

from __future__ import annotations

import harness

# Distribution A — modelled reconstruction, peak 04:00 / trough 15:00 (sums ~1).
SPONTANEOUS_PREWAR = {
    0: 0.050,
    1: 0.054,
    2: 0.057,
    3: 0.059,
    4: 0.060,
    5: 0.058,
    6: 0.055,
    7: 0.051,
    8: 0.047,
    9: 0.044,
    10: 0.042,
    11: 0.040,
    12: 0.038,
    13: 0.035,
    14: 0.033,
    15: 0.032,
    16: 0.033,
    17: 0.035,
    18: 0.037,
    19: 0.040,
    20: 0.043,
    21: 0.045,
    22: 0.047,
    23: 0.049,
}

# Distribution C — US 2021 NCHS 6-hour blocks, spread uniformly within each block.
_MODERN_BLOCKS = {(0, 6): 0.181, (6, 12): 0.287, (12, 18): 0.303, (18, 24): 0.229}
MODERN_US = {
    h: share / 6 for (lo, hi), share in _MODERN_BLOCKS.items() for h in range(lo, hi)
}

UNIFORM = dict.fromkeys(range(24), 1 / 24)


def blend(hour_dist_a: dict, hour_dist_b: dict, w_b: float) -> dict:
    """(1-w_b)*A + w_b*B, renormalised."""
    raw = {h: (1 - w_b) * hour_dist_a[h] + w_b * hour_dist_b[h] for h in range(24)}
    z = sum(raw.values())
    return {h: v / z for h, v in raw.items()}


def prior_for_year(year: int) -> dict:
    """Era-aware prior (research §Recommendations 4): pre-1935 pure A; 1935–1970
    mild blend; post-1970 material daytime weight."""
    if year < 1935:
        return SPONTANEOUS_PREWAR
    if year <= 1970:
        return blend(SPONTANEOUS_PREWAR, MODERN_US, 0.25)
    return blend(SPONTANEOUS_PREWAR, MODERN_US, 0.6)


def p_day(person, dist: dict, step_minutes: int = 10) -> float:
    """Birth-hour-weighted P(day) = Σ f(h)·[day-cell] / Σ f(h) over the day."""
    sweep = harness.candidate_sects(person, step_minutes=step_minutes)
    num = sum(dist[m // 60] for m, s in sweep if s == "day")
    den = sum(dist[m // 60] for m, s in sweep)
    return num / den if den else 0.5
