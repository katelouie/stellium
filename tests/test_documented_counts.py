"""Every count the README states out loud must match the registry it describes.

The docs site solved this by not writing numbers down: `docs/options_list.md` says
`{{ n_house_systems }}` and Sphinx resolves it from the library at build time. The
README cannot — it is rendered by GitHub and PyPI, which have no build step — so the
numbers in it are typed by a human, and a typed number is a snapshot with no expiry.

They expire. The README advertised **"23+ house systems"**; there are **17**. That is
an overclaim, on the project's front page, in the direction that disappoints someone.
`options_list.md` — the "full list" that line links to — said **37 celestial objects**
against a registry holding **83**, and **26 aspect types** against **19**. Nobody lied;
each was true once.

So the README's numbers are pinned here instead. If a registry grows, this test fails
and tells you which line to edit. That is the whole mechanism: you may still write a
number down, but you may no longer be the only one who knows it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG
from stellium.core.ayanamsa import AYANAMSA_REGISTRY
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    FIXED_STARS_REGISTRY,
)
from stellium.engines.houses import HOUSE_SYSTEM_CODES

README = Path(__file__).parent.parent / "README.md"

# (regex capturing the number, what it counts, the live value)
#
# A `\d+\+` claim ("25+ Arabic Parts") is a *floor*, and is asserted as one: it may
# undercount, it may not overcount. An exact claim must be exact.
CLAIMS = [
    (r"\*\*(\d+) house systems\*\*", "house systems", len(HOUSE_SYSTEM_CODES), "exact"),
    (
        r"\*\*(\d+)\+ Arabic Parts\*\*",
        "Arabic parts",
        len(ARABIC_PARTS_CATALOG),
        "floor",
    ),
]


@pytest.mark.parametrize("pattern,label,actual,kind", CLAIMS)
def test_readme_count_matches_the_library(pattern, label, actual, kind):
    text = README.read_text(encoding="utf-8")
    match = re.search(pattern, text)
    assert match, f"README no longer states a count for {label} (pattern: {pattern})"

    claimed = int(match.group(1))
    if kind == "floor":
        assert claimed <= actual, (
            f"README claims '{claimed}+ {label}' but there are only {actual}. "
            f"A '+' claim is a floor — it must not overcount."
        )
    else:
        assert claimed == actual, (
            f"README says {claimed} {label}; the library has {actual}. "
            f"Update README.md — and check docs/options_list.md, which resolves the "
            f"same number from the registry via a MyST substitution and is therefore "
            f"already right."
        )


def test_registries_are_not_empty():
    """A count that matches zero against zero is not a passing test."""
    for name, registry in [
        ("CELESTIAL_REGISTRY", CELESTIAL_REGISTRY),
        ("ASPECT_REGISTRY", ASPECT_REGISTRY),
        ("FIXED_STARS_REGISTRY", FIXED_STARS_REGISTRY),
        ("AYANAMSA_REGISTRY", AYANAMSA_REGISTRY),
        ("HOUSE_SYSTEM_CODES", HOUSE_SYSTEM_CODES),
        ("ARABIC_PARTS_CATALOG", ARABIC_PARTS_CATALOG),
    ]:
        assert len(registry) > 0, f"{name} is empty"
