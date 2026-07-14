import os
import sys

sys.path.insert(0, os.path.abspath("../src"))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Import version from package to avoid hardcoding
from stellium import __version__

project = "Stellium"
copyright = "2025, Kate Louie"
author = "Kate Louie"
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.napoleon",  # Support Google/NumPy docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other docs
    "sphinx_autodoc_typehints",  # Better type hints
    # myst_nb supersedes myst_parser: it IS myst_parser, plus .ipynb.
    "myst_nb",
]

# Render a Google-style `Attributes:` block as :ivar: fields inside the class body,
# rather than as free-standing `.. attribute::` directives.
#
# This is not cosmetic. Nearly every result model is a frozen dataclass that documents
# its fields in an `Attributes:` block, and autodoc's `:undoc-members:` *also* emits an
# attribute for each field — so every one was being registered twice, from one directive:
# 253 "duplicate object description" warnings, all of them `SomeModel.some_field`.
napoleon_use_ivar = True

# In the "on this page" rail, a method is `add_analyzer()` — not
# `ChartBuilder.add_analyzer()`. The rail is 232px wide and the class name is the same
# on every entry, so the prefix is the one part guaranteed to carry no information,
# while being the part that survives truncation: thirteen consecutive links all
# reading "ChartBuilder.a…". The parent is already the heading they sit under.
toc_object_entries_show_parents = "hide"

# MyST configuration
myst_enable_extensions = [
    "colon_fence",  # ::: fences
    "deflist",  # Definition lists
    "tasklist",  # Task lists
    # `{{ n_recipes }}` — see _site_stats() at the foot of this file. Counts are
    # resolved from the library at build time rather than typed into prose.
    "substitution",
    # `[42]{.st-n}` — a span with a class, so the landing pages can be laid out in
    # plain Markdown (whose links Sphinx therefore checks) instead of raw HTML
    # (whose links it cannot). The theme's CSS does the rest.
    "attrs_inline",
]

# Generate an anchor for every heading down to h4.
#
# Without this MyST creates NO heading anchors, so every `[Quick Start](#quick-start)`
# in every hand-written table of contents silently resolved to nothing — which is most
# of the 121 broken cross-references the build was reporting. The links rendered, they
# just went nowhere.
myst_heading_anchors = 4

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}

# EXECUTE the notebook at build time; never publish its stored outputs.
#
# analysis_cookbook.ipynb shipped 52 stored outputs, and they were WRONG: it
# claimed "Calculated 146 charts" from a notables registry that now holds 211, and
# "14 scientist charts" where there are 20. They were computed against a library
# that has since changed its dignity tables, its chart ordering, its Local Mean
# Time handling, and eight notables' birthdays. Publishing them would be publishing
# results nobody had re-run — the exact failure the astrology guide made.
#
# So the library computes them, every build. A cell that fails now fails the docs
# build, which is the same contract as scripts/update_doc_outputs.py --check: the
# author writes the question, the library writes the answer.
# "force", NOT "cache". The cache is keyed on the NOTEBOOK's content — so when the
# library changes and the notebook does not, which is exactly the case we care
# about, "cache" happily serves the old outputs. It executes in 7 seconds.
nb_execution_mode = "force"
nb_execution_timeout = 180
nb_execution_raise_on_error = True
nb_merge_streams = True  # one output block per cell, not one per print()

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "archive",
    "planning",
    # docs/development/ is the contributor/agent architecture reference — read on
    # GitHub, by people working ON Stellium, and written with GitHub-relative links
    # (./specs/, ../development/) that Sphinx cannot resolve. Sphinx was compiling all
    # of it anyway: 34 documents in no toctree (built, reachable from nowhere) and 19
    # broken cross-references between them — a build compiling files it had no business
    # compiling, not a defect in the docs.
    #
    # docs/methodology/ is NOT in this list, and that is deliberate. It answers "what
    # does Stellium implement, and on whose authority?" — Valens, Firmicus, Ptolemy,
    # Houlding; which forks the tradition genuinely disagrees on and which default we
    # ship; which received claims are folk-etymology. For a computational astrology
    # library that is the most trust-establishing writing in the repository, and it
    # belongs in front of users, not behind them.
    "development",
    "DOCS_INDEX.md",  # an index OF the docs, for contributors; the site has a nav
    # Superseded by docs/development/ — its own first line reads "⚠️ SUPERSEDED —
    # do not use as an API reference." It has no business being built, let alone
    # (as it was until today) sitting in the Reference section of the nav.
    "ARCHITECTURE.md",
    "images/README.md",  # a note about the image directory, addressed to us
    # A planning document — "what does Stellium implement, and what is still missing?"
    # It is a map of our own gaps, addressed to us, and it goes stale the moment one
    # is filled. The user-facing answer to the same question is docs/methodology/.
    "astrology/CAPABILITY_AUDIT.md",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "stellium_theme"
html_theme_path = ["_themes"]

html_theme_options = {
    # These are declared in theme.conf and rendered into stellium.css_t, so they
    # genuinely drive the palette — they are not decoration.
    "accent": "#5b46b0",
    "accent_dark": "#9b8ae8",
    "gold": "#a9782a",
    "gold_dark": "#d9b46a",
    "github_url": "https://github.com/katelouie/stellium",
    "default_mode": "light",
    "show_version": True,
}

html_title = "Stellium"
html_short_title = "Stellium"

# The docs' web fonts are generated by scripts/build_web_fonts.py and live in
# assets/fonts/web/ — the repo's font home, NOT src/stellium/data/fonts/, which
# ships in the wheel. Adding the directory here copies the .woff2 into _static/,
# where the theme's @font-face rules expect them.
html_static_path = ["_static", "../assets/fonts/web"]
html_extra_path = ["starlight_colors.html"]  # Copy HTML reference to build output

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Syntax highlighting -----------------------------------------------------
# The design specifies a five-colour palette (keyword #c4b5fd, call #e8c07d, string
# #a3d0a8, class #7fd0a8, comment #6b6d82), identical in light and dark — only the
# ground shifts. The docs were shipping stock **monokai**: magenta keywords, amber
# strings. Nothing was wrong with it except that it was not the design.
#
# docs/_pygments/stellium_syntax.py is that palette, plus the lexer filter it needs:
# Pygments marks a name as a function only where it is *defined*, so in a fluent chain
# — which is the whole public API — every method arrived as an uncoloured bare Name.
sys.path.insert(0, os.path.abspath("_pygments"))
pygments_style = "stellium_syntax.StelliumStyle"  # code chrome is dark in BOTH themes


def setup(app):
    from stellium_syntax import StelliumPythonLexer

    app.add_lexer("python", StelliumPythonLexer)


# -- Generated pages ---------------------------------------------------------
# The cookbooks in examples/ hold every runnable recipe we have, and none of them
# appeared anywhere in this site. They are turned into pages here, on every build
# (including on Read the Docs), rather than being committed — a generated page
# that lives in git is a copy of the code that can drift from it, and the pages
# `literalinclude` the real functions precisely so that they cannot.
#
# This runs at *config* time, not on the `builder-inited` event, and it has to:
# MyST snapshots `myst_substitutions` into its parser config before the first
# document is read, so a substitution assigned from an event handler is already too
# late and every `{{ n_recipes }}` resolves to nothing.
def _build_cookbook_pages() -> None:
    import subprocess
    import sys
    from pathlib import Path

    scripts = Path(__file__).parent.parent / "scripts"
    subprocess.run(
        [sys.executable, str(scripts / "build_cookbook_pages.py")], check=True
    )
    # The galleries are a *view of a registry*, not a document. Enumerated, not authored.
    subprocess.run(
        [sys.executable, str(scripts / "build_gallery_pages.py")], check=True
    )


# -- Counts, taken from the library rather than typed ------------------------
# Every number the prose quotes — recipes, cookbooks, themes, palettes, notables —
# is a substitution resolved at build time from the thing it describes.
#
# This exists because the numbers do not hold still and nobody notices when they
# stop being true. The home page said "374 recipes" while the generator produced
# 421. The generator's own docstring said 357. The design mockup promised "thirteen
# themes"; there are fourteen. Not one of these was a lie anyone told on purpose —
# they were all true once. A count in prose is a snapshot with no expiry date, so
# the fix is not to correct them, it is to stop writing them down.
def _site_stats() -> dict:
    import json
    from pathlib import Path

    from stellium.data import get_notable_registry
    from stellium.visualization.palettes import (
        AspectPalette,
        PlanetGlyphPalette,
        ZodiacPalette,
    )
    from stellium.visualization.themes import ChartTheme

    stats_file = Path(__file__).parent / "_generated" / "site_stats.json"
    cookbooks = json.loads(stats_file.read_text())

    subs = {
        "version": __version__,
        "n_recipes": cookbooks["recipes"],
        "n_cookbooks": cookbooks["cookbooks"],
        "n_themes": len(ChartTheme),
        "n_zodiac_palettes": len(ZodiacPalette),
        "n_aspect_palettes": len(AspectPalette),
        "n_planet_palettes": len(PlanetGlyphPalette),
        "n_palettes": len(ZodiacPalette) + len(AspectPalette) + len(PlanetGlyphPalette),
        "n_notables": len(get_notable_registry().get_all()),
        "n_notable_births": len(get_notable_registry().get_births()),
    }

    # The biography dataset — life events and temperament, both interpretive and both
    # graded for provenance. Counted, not quoted.
    import warnings

    from stellium.data.biography import get_notable_life_events
    from stellium.exceptions import DataQualityWarning

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DataQualityWarning)
        events = [
            get_notable_life_events(n.name) or []
            for n in get_notable_registry().get_all()
        ]
    subs["n_life_events"] = sum(len(e) for e in events)
    subs["n_notables_with_events"] = sum(1 for e in events if e)

    # The options catalogue. options_list.md's summary line said "37 celestial objects"
    # and "26 aspect types" against registries holding 83 and 19; the README claimed
    # "23+ house systems" where there are 17 — an *overclaim*, which is the worst
    # direction to be wrong in. tests/test_documented_counts.py pins the README, which
    # is not a Sphinx page and so cannot use these.
    from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG
    from stellium.core.ayanamsa import AYANAMSA_REGISTRY
    from stellium.core.registry import (
        ASPECT_REGISTRY,
        CELESTIAL_REGISTRY,
        FIXED_STARS_REGISTRY,
    )
    from stellium.engines.houses import HOUSE_SYSTEM_CODES

    subs["n_objects"] = len(CELESTIAL_REGISTRY)
    subs["n_house_systems"] = len(HOUSE_SYSTEM_CODES)
    subs["n_ayanamsas"] = len(AYANAMSA_REGISTRY)
    subs["n_fixed_stars"] = len(FIXED_STARS_REGISTRY)
    subs["n_arabic_parts"] = len(ARABIC_PARTS_CATALOG)
    subs["n_aspects"] = len(ASPECT_REGISTRY)
    # Per-cookbook recipe counts, e.g. {{ cb_electional }} -> 43. The home page picks
    # *which* cookbooks to feature; the build supplies how many recipes each one has.
    for slug, count in cookbooks["by_slug"].items():
        subs[f"cb_{slug}"] = count
    return subs


_build_cookbook_pages()
myst_substitutions = _site_stats()
