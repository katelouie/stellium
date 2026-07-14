"""The docs build executes the examples, so it needs what the examples import.

Read the Docs installs `docs/requirements.txt` and the package — nothing else. Every
local environment has the dev extras, so a dependency missing from that file is
invisible here and only fails on the published site. It has: the analysis notebook
imports `scipy` unguarded, and the docs build died on it.

This checks the one thing a local run cannot: that every third-party module the
cookbooks and the notebook import is declared where Read the Docs will see it.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
EXAMPLES = REPO / "examples"
REQUIREMENTS = REPO / "docs" / "requirements.txt"

# Provided by the package itself (RTD does `pip install .`), so they need no entry.
FROM_THE_PACKAGE = {
    "stellium",
    "swisseph",
    "pytz",
    "geopy",
    "rich",
    "svgwrite",
    "typst",
}


def third_party_imports() -> set[str]:
    """Every non-stdlib module the executed examples import."""
    modules: set[str] = set()
    sources = list(EXAMPLES.glob("*_cookbook.py"))

    notebook = EXAMPLES / "analysis_cookbook.md"
    cells = re.findall(
        r"```\{code-cell\}[^\n]*\n(.*?)```", notebook.read_text(encoding="utf-8"), re.S
    )

    for source in [p.read_text(encoding="utf-8") for p in sources] + cells:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                modules.add(node.module.split(".")[0])

    return {
        m
        for m in modules
        if m not in sys.stdlib_module_names and m not in FROM_THE_PACKAGE
    }


def declared() -> set[str]:
    """Distribution names in docs/requirements.txt, normalised."""
    names = set()
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        name = re.split(r"[<>=!~\[]", line)[0].strip().lower().replace("-", "_")
        names.add(name)
    return names


@pytest.mark.parametrize("module", sorted(third_party_imports()))
def test_docs_requirements_cover_the_examples(module):
    assert module.lower() in declared(), (
        f"`{module}` is imported by an example the docs build executes, but is not in "
        f"docs/requirements.txt — which is all Read the Docs installs besides the "
        f"package itself.\n\n"
        f"It will work locally (the dev extras have it) and fail on the published site."
    )
