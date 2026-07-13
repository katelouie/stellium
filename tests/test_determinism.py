"""The same chart, calculated twice, must be the same chart.

This sounds too obvious to test. It was not true.

`ChartBuilder._get_objects_list()` ended with `list(set(objects))` — a correct dedupe
followed by an arbitrary order. `AspectPatternAnalyzer` built each Grand Cross and
Mystic Rectangle's membership as a set literal and then called `list()` on it. In
both cases the container was right and the *order coming out of it* was garbage.

And it was not merely arbitrary, it was **arbitrary per process**: Python randomizes
string hashing on every interpreter start (PYTHONHASHSEED), and `CelestialPosition`
is a frozen dataclass whose hash derives from its string fields. So:

    run 1:  Moon Trine Venus,      Moon Square MC,      Chiron Conjunction Neptune
    run 2:  Neptune Square Node,   Neptune Conj Chiron, Neptune Trine Uranus
    run 3:  Saturn Sextile Node,   Saturn Conj Mercury, Saturn Trine South Node

Same chart. Same code. Three different orderings of `chart.aspects`, because the
order of `chart.positions` flowed into `combinations()` in the aspect engines. Every
report, every aspectarian, every exported JSON listed things in an order that would
not survive being run again — and two people running identical code got documents
that differed.

**Why nothing caught it.** Within a single process the hash seed is fixed, so a test
that builds two charts and compares them passes. The bug is only visible *across*
processes. So these tests spawn real ones, with hash seeds chosen to disagree.

That is the general lesson worth keeping: a nondeterminism test that does not cross a
process boundary is testing the seed, not the code.
"""

import json
import subprocess
import sys
import textwrap

import pytest

pytestmark = pytest.mark.slow

# Hash seeds that actually differ. 0 disables randomization entirely; the others are
# arbitrary but fixed, so a failure here reproduces instead of flapping.
SEEDS = ["0", "1", "42", "12345"]

MAXIMAL_CHART = textwrap.dedent("""
    import json
    from stellium import ChartBuilder
    from stellium.components import (
        ArabicPartsCalculator, DignityComponent, MidpointCalculator,
    )
    from stellium.engines.houses import PlacidusHouses, WholeSignHouses
    from stellium.engines.patterns import AspectPatternAnalyzer

    chart = (ChartBuilder.from_notable("Albert Einstein")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .with_named_asteroids()
        .add_component(DignityComponent())
        .add_component(ArabicPartsCalculator())
        .add_component(MidpointCalculator())
        .add_analyzer(AspectPatternAnalyzer())
        .calculate())

    print(json.dumps(chart.to_dict(), default=str))
""")


def _run(code: str, seed: str) -> str:
    """Run a snippet in a fresh interpreter with a given PYTHONHASHSEED."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env={"PYTHONHASHSEED": seed, "PATH": "/usr/bin:/bin"},
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, f"seed {seed} failed:\n{result.stderr[-2000:]}"
    return result.stdout


def test_a_maximal_chart_is_byte_identical_across_hash_seeds():
    """Everything a chart can express — positions, aspects, houses, components,
    analyzers — pinned at once. Any set that leaks its iteration order into output
    shows up here, including ones nobody has written yet."""
    outputs = {seed: _run(MAXIMAL_CHART, seed) for seed in SEEDS}

    first = outputs[SEEDS[0]]
    for seed, out in outputs.items():
        if out == first:
            continue
        # Report *where*, not just that — a bare "not equal" on 76 KB of JSON is
        # useless to whoever picks this up.
        a, b = json.loads(first), json.loads(out)
        differing = [k for k in a if a[k] != b.get(k)]
        pytest.fail(
            f"chart output depends on PYTHONHASHSEED "
            f"({SEEDS[0]} vs {seed}) — differing top-level keys: {differing}. "
            f"Something is iterating a set. Use dict.fromkeys() to dedupe while "
            f"preserving order."
        )


def test_positions_and_aspects_come_out_in_a_stable_order():
    """The narrow version of the above, with a readable failure.

    `chart.positions` must come out in the order it was asked for, not in whatever
    order a hash table happened to produce.
    """
    code = textwrap.dedent("""
        from stellium import ChartBuilder
        chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
        print("|".join(p.name for p in chart.positions))
        print("|".join(f"{a.object1.name}-{a.aspect_name}-{a.object2.name}"
                       for a in chart.aspects))
    """)
    results = {seed: _run(code, seed) for seed in SEEDS}

    baseline = results[SEEDS[0]].splitlines()
    for seed, out in results.items():
        lines = out.splitlines()
        assert lines[0] == baseline[0], (
            f"chart.positions order depends on the hash seed "
            f"({SEEDS[0]} vs {seed}):\n  {baseline[0][:120]}\n  {lines[0][:120]}"
        )
        assert lines[1] == baseline[1], (
            f"chart.aspects order depends on the hash seed ({SEEDS[0]} vs {seed}) — "
            f"positions are stable, so this is a set inside an aspect engine."
        )

    # And the order should be the one the caller asked for: the Sun comes first
    # because the config lists it first, not by luck.
    assert baseline[0].split("|")[:3] == ["Sun", "Moon", "Mercury"]


def test_aspect_pattern_membership_is_stable():
    """Grand Cross / Mystic Rectangle members were built as a set literal, so a
    pattern's own planets were listed in a different order every run."""
    code = textwrap.dedent("""
        from stellium import ChartBuilder
        from stellium.engines.patterns import AspectPatternAnalyzer
        chart = (ChartBuilder.from_notable("Albert Einstein")
            .with_aspects().with_named_asteroids()
            .add_analyzer(AspectPatternAnalyzer()).calculate())
        for p in chart.metadata["aspect_patterns"]:
            print(p.name, ",".join(pl.name for pl in p.planets))
    """)
    results = {seed: _run(code, seed) for seed in SEEDS}

    baseline = results[SEEDS[0]]
    for seed, out in results.items():
        assert out == baseline, (
            f"aspect pattern membership depends on the hash seed "
            f"({SEEDS[0]} vs {seed}). A pattern is reporting the same planets in a "
            f"different order run to run."
        )
