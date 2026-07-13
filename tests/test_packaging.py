"""Does the wheel actually contain the files the code reads at runtime?

Issue #60: the Typst design system (`presentation/typst_theme/*.typ`) was missing
from the published wheel, so **every PDF and planner render failed** for anyone who
installed Stellium from PyPI. It worked perfectly from a source checkout, which is
why it shipped: the files were right there on disk the whole time.

`[tool.setuptools.packages.find]` collects **Python modules only**. Every non-`.py`
file has to be declared in `[tool.setuptools.package-data]` or it silently does not
ship — silently being the operative word, since nothing warns you.

So this asserts the invariant directly: *every data file the source tree contains is
covered by a package-data glob.* It would have caught #60, and it caught
`i18n/locales/zh_CN/strings.json` (the Chinese locale, broken in the wheel for the
same reason) at the same time.
"""

import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "stellium"
PYPROJECT = REPO_ROOT / "pyproject.toml"

# Suffixes that are runtime data — if one of these is in the tree, the code can read
# it, so it had better be in the wheel.
DATA_SUFFIXES = {
    ".typ",  # Typst design system  <- issue #60
    ".json",  # locales, geocode cache
    ".yaml",
    ".yml",  # notables
    ".se1",  # Swiss Ephemeris
    ".ttf",
    ".otf",  # bundled fonts
    ".css",
    ".html",  # any templating
}

# Files deliberately NOT shipped. Each needs a reason — this list is a confession,
# not a convenience.
INTENTIONALLY_UNSHIPPED = {
    # Orphaned template from the pre-design-system PDF renderer. Nothing reads it:
    # the only class that ever could (`presentation/renderers.py::TypstRenderer`) is
    # itself unreferenced, unexported and untested. Left in the tree pending removal;
    # shipping a dead file would be worse than not shipping it.
    "presentation/templates/astro_report.typ",
}


def _declared_globs() -> dict[str, list[str]]:
    with PYPROJECT.open("rb") as handle:
        config = tomllib.load(handle)
    return config["tool"]["setuptools"]["package-data"]


def _files_the_wheel_will_contain() -> set[Path]:
    """Every path matched by a package-data glob, resolved against its package."""
    shipped: set[Path] = set()
    for package, patterns in _declared_globs().items():
        package_dir = SRC_ROOT / Path(*package.split("."))
        for pattern in patterns:
            shipped.update(p.resolve() for p in package_dir.glob(pattern))
    return shipped


def _data_files_in_the_source_tree() -> list[Path]:
    found = []
    for path in PACKAGE_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in DATA_SUFFIXES:
            continue
        # Skip build/editor/cache detritus: __pycache__, .DS_Store, a stray .cache/
        if any(
            part.startswith((".", "__")) for part in path.relative_to(SRC_ROOT).parts
        ):
            continue
        found.append(path.resolve())
    return found


def _package_relative(path: Path) -> str:
    """Always forward slashes.

    `str(PurePath)` gives backslashes on Windows, so comparing against the
    forward-slash keys in INTENTIONALLY_UNSHIPPED silently never matched there — and
    this test failed on Windows only. (It caught that about itself, which is at least
    the right kind of embarrassing.)
    """
    return path.relative_to(PACKAGE_ROOT).as_posix()


def test_every_data_file_in_the_tree_is_declared_in_package_data():
    """The invariant. A data file present in src/ but absent from the wheel is a bug
    that only shows up for people who `pip install`, never for us."""
    shipped = _files_the_wheel_will_contain()

    missing = sorted(
        _package_relative(path)
        for path in _data_files_in_the_source_tree()
        if path not in shipped
        and _package_relative(path) not in INTENTIONALLY_UNSHIPPED
    )

    assert not missing, (
        "these files exist in src/stellium/ but will NOT be in the wheel — add a glob "
        "to [tool.setuptools.package-data] in pyproject.toml, or list them in "
        "INTENTIONALLY_UNSHIPPED with a reason:\n  " + "\n  ".join(missing)
    )


def test_the_typst_design_system_ships():
    """Issue #60, stated as a fact rather than a rule.

    Without these five files, ReportBuilder.render(format="pdf") and every planner
    raise FileNotFoundError on an installed wheel.
    """
    shipped = _files_the_wheel_will_contain()
    theme_dir = PACKAGE_ROOT / "presentation" / "typst_theme"

    on_disk = {p.resolve() for p in theme_dir.glob("*.typ")}
    assert on_disk, "no .typ files found — did the design system move?"

    not_shipping = sorted(p.name for p in on_disk - shipped)
    assert not not_shipping, (
        f"design-system files missing from the wheel: {not_shipping}"
    )


def test_the_locale_strings_ship():
    """The same bug, one directory over: i18n/loader.py reads locales/*/strings.json
    from `Path(__file__).parent`, so an unshipped locale silently falls back to English.
    """
    shipped = _files_the_wheel_will_contain()
    locales = PACKAGE_ROOT / "i18n" / "locales"

    on_disk = {p.resolve() for p in locales.glob("*/strings.json")}
    assert on_disk, "no locale files found — did i18n move?"
    assert not (on_disk - shipped), "locale strings are missing from the wheel"


def test_package_data_globs_do_not_sweep_in_junk():
    """Keep the patterns tight.

    A stray `.cache/` once accumulated **37,000 files inside typst_theme/**. The
    obvious fix for #60 — a `typst_theme/**/*` glob — would have shipped every one of
    them. Nothing matched by package-data may be a cache file or a pickle.
    """
    junk = sorted(
        str(path)
        for path in _files_the_wheel_will_contain()
        if path.suffix == ".pickle" or ".cache" in path.parts
    )
    assert not junk, f"package-data is sweeping in cache/junk files: {junk}"


@pytest.mark.slow
def test_a_built_wheel_really_contains_the_design_system(tmp_path):
    """The artifact is the only real oracle.

    Everything above reasons about pyproject.toml. This builds the actual wheel and
    looks inside it — the check that cannot be fooled by a glob that resolves
    differently under setuptools than under pathlib.
    """
    import subprocess
    import sys
    import zipfile

    build = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(tmp_path), "."],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if build.returncode != 0:
        pytest.skip(f"could not build a wheel here: {build.stderr[-300:]}")

    wheels = list(tmp_path.glob("*.whl"))
    assert wheels, "build produced no wheel"

    names = zipfile.ZipFile(wheels[0]).namelist()

    typ = [n for n in names if n.endswith(".typ")]
    assert len(typ) >= 5, f"the wheel contains only {len(typ)} .typ files: {typ}"

    assert any(n.endswith("i18n/locales/zh_CN/strings.json") for n in names)

    swept = [n for n in names if n.endswith(".pickle") or "/.cache/" in n]
    assert not swept, f"the wheel contains cache junk: {swept[:5]}"
