"""Tier 1 — import smoke test.

Importing every page and component module catches syntax errors, broken
imports, and accidental shadowing (e.g. a ``for name, _ in ...`` loop
rebinding the ``_`` translator). Cheapest, highest-ROI web test there is.
"""

import importlib

import pytest

MODULES = [
    # Core
    "config",
    "state",
    "i18n",
    # Pages
    "pages.home",
    "pages.explore",
    "pages.natal",
    "pages.relationships",
    "pages.timing",
    "pages.planner",
    # Components
    "components.header",
    "components.chart_options",
    "components.report_options",
    "components.birth_input",
    "components.birth_input_unified",
    "components.chart_display",
    "components.location_input",
    "components.date_input",
    "components.time_input",
    "components.notable_selector",
    "components.code_preview",
    "components.pdf_options",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)
