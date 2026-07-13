"""Perceptual guarantees for the Typst design system's palettes.

The eight structural tokens (bg, panel, ink, rule, hair, muted, accent, gold) are
about *surfaces and emphasis*. They deliberately make **no promise** that any two
of them are perceptually distinct, and in practice several are not:

    house      ΔE(accent, ink)  =  5.9   — indistinguishable
    blues      ΔE(accent, ink)  =  9.5   — indistinguishable
    celestial  ΔE(accent, gold) =  0.0   — the *same hex*; it is the gold-on-indigo
                                           theme, and that is intentional

So a component that encodes *categorical* data must never reach for two structural
tokens and hope they contrast — that is a category error, and it is exactly the bug
that shipped in the planner's first colour-coded calendar, where "touches your natal
chart" (accent) rendered identically to "a planet changed sign" (ink).

Categorical encodings use a dedicated semantic palette instead. These tests hold
that palette to the promise the structural tokens don't make.
"""

import math
import re
from pathlib import Path

import pytest

PALETTES = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "stellium"
    / "presentation"
    / "typst_theme"
    / "palettes.typ"
)

# Below ~10 two colours read as the same ink at 5.5pt; 15 gives real headroom for
# the tiny type the calendar uses.
MIN_DELTA_E = 15.0


# ---------------------------------------------------------------------------
# colour maths (CIE76 — plenty for "are these obviously different")
# ---------------------------------------------------------------------------


def _linear(channel: float) -> float:
    channel /= 255
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _lab(value: str) -> tuple[float, float, float]:
    r, g, b = (_linear(c) for c in _rgb(value))
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    xn, yn, zn = 0.95047, 1.0, 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(a: str, b: str) -> float:
    """Perceptual distance. <10 reads as the same colour; >25 is clearly different."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(_lab(a), _lab(b), strict=True)))


def contrast_ratio(a: str, b: str) -> float:
    def luminance(value: str) -> float:
        r, g, b_ = (_linear(c) for c in _rgb(value))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b_

    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


# ---------------------------------------------------------------------------
# read the palette straight out of the design system
# ---------------------------------------------------------------------------


def _parse_block(name: str) -> dict[str, dict[str, str]]:
    """Pull a `#let <name> = (...)` mapping of theme -> {key: "#hex"} out of the .typ."""
    source = PALETTES.read_text(encoding="utf-8")
    match = re.search(rf"#let {re.escape(name)} = \((.*?)\n\)", source, re.S)
    assert match, f"{name} not found in palettes.typ"

    out: dict[str, dict[str, str]] = {}
    for theme, body in re.findall(r"(\w+):\s*\((.*?)\)", match.group(1), re.S):
        entries = dict(re.findall(r"(\w[\w-]*):\s*\"(#[0-9A-Fa-f]{6})\"", body))
        if entries:
            out[theme] = entries
    return out


@pytest.fixture(scope="module")
def event_colors() -> dict[str, dict[str, str]]:
    return _parse_block("theme-event-colors")


@pytest.fixture(scope="module")
def themes() -> dict[str, dict[str, str]]:
    return _parse_block("themes")


# ---------------------------------------------------------------------------
# the promise the semantic palette must keep
# ---------------------------------------------------------------------------


def test_every_theme_defines_every_event_class(event_colors, themes):
    """Schema discipline: a missing key is a bug, not a default to paper over."""
    assert set(event_colors) == set(themes)
    for theme, colors in event_colors.items():
        assert set(colors) == {"natal", "notable", "mundane", "lunar"}, theme


@pytest.mark.parametrize("first", ["natal", "notable", "mundane", "lunar"])
@pytest.mark.parametrize("second", ["natal", "notable", "mundane", "lunar"])
def test_event_classes_are_perceptually_distinct(event_colors, first, second):
    """The guardrail.

    A day cell is unreadable if two classes render as the same ink. This is the
    test that would have caught reusing accent/ink for natal/mundane, where
    ΔE was 5.9 in the house theme.
    """
    if first >= second:
        pytest.skip("each pair once")

    for theme, colors in event_colors.items():
        distance = delta_e(colors[first], colors[second])
        assert distance >= MIN_DELTA_E, (
            f"{theme}: {first} ({colors[first]}) and {second} ({colors[second]}) "
            f"are only ΔE {distance:.1f} apart — they will read as the same ink"
        )


def test_event_colors_are_legible_on_the_page(event_colors, themes):
    """Every class must be readable against its own theme's background."""
    for theme, colors in event_colors.items():
        background = themes[theme]["bg"]
        for name, value in colors.items():
            ratio = contrast_ratio(value, background)
            assert ratio >= 3.0, (
                f"{theme}: {name} ({value}) has only {ratio:.1f}:1 contrast against "
                f"the {background} page"
            )


def test_natal_is_the_one_that_pops(event_colors, themes):
    """`natal` is the reason the reader owns the planner, so it must not recede.

    It has to out-shout the Moon's housekeeping, which is the class designed to
    disappear.
    """
    for theme, colors in event_colors.items():
        background = themes[theme]["bg"]
        natal = contrast_ratio(colors["natal"], background)
        lunar = contrast_ratio(colors["lunar"], background)
        assert natal > lunar, (
            f"{theme}: natal ({natal:.1f}:1) does not stand out more than "
            f"lunar ({lunar:.1f}:1)"
        )


# ---------------------------------------------------------------------------
# and a note-to-self about the structural tokens
# ---------------------------------------------------------------------------


def test_structural_tokens_make_no_distinctness_promise(themes):
    """Documents the trap, so nobody re-derives it the hard way.

    This asserts the *status quo*: accent and ink genuinely collapse in some themes.
    If a future palette change makes them all distinct, that is fine — but it still
    would not license encoding data with them, because nothing guarantees it stays
    that way. Categorical data belongs in a semantic palette.
    """
    collapsed = {
        theme
        for theme, tokens in themes.items()
        if delta_e(tokens["accent"], tokens["ink"]) < MIN_DELTA_E
    }
    # house and blues are the known offenders; greyscale is value-only by design.
    assert "house" in collapsed, (
        "house's accent/ink used to be ΔE 5.9 apart — if that changed, update the "
        "docstring above, but do not start encoding data with structural tokens"
    )
