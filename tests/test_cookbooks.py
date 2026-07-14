"""Smoke tests for all cookbook example files.

Imports and runs each cookbook's main() function to verify that
examples don't crash with the current codebase. This catches
API drift (renamed methods, changed signatures, removed attributes)
that would otherwise go unnoticed until a user tries the examples.

These tests write output files (SVGs, etc.) to the normal cookbook
output directories under examples/. This is intentional — it also
verifies that file output works correctly.

Marked as slow: runs in CI and full suite, not in TDD loop.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

pytestmark = [pytest.mark.slow, pytest.mark.docs]

REPO_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"


def _snapshot_files(directory: Path) -> set[Path]:
    """Capture all files currently in a directory tree."""
    return {p for p in directory.rglob("*") if p.is_file()}


@pytest.fixture(autouse=True, scope="session")
def _cleanup_cookbook_output():
    """Remove files created by cookbook runs after all tests finish."""
    before = _snapshot_files(EXAMPLES_DIR) | _snapshot_files(REPO_ROOT)
    yield
    after = _snapshot_files(EXAMPLES_DIR) | _snapshot_files(REPO_ROOT)
    new_files = after - before
    for f in new_files:
        # Only clean generated output, not source files
        if f.suffix in (".svg", ".pdf", ".txt", ".png", ".html", ".ipynb"):
            f.unlink(missing_ok=True)
    # Remove empty directories left behind
    for d in sorted(
        (p for p in EXAMPLES_DIR.rglob("*") if p.is_dir()),
        key=lambda p: len(p.parts),
        reverse=True,
    ):
        if d.exists() and not any(d.iterdir()):
            d.rmdir()


def _run_cookbook(filename: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a cookbook file as a subprocess.

    Using subprocess rather than direct import because:
    - Cookbooks use module-level OUTPUT_DIR / os.makedirs
    - Some modify global state or have conflicting imports
    - Subprocess isolation prevents test pollution
    - We get the exact same behavior as a user running the file
    """
    filepath = EXAMPLES_DIR / filename

    # Send the cookbook's output somewhere disposable. A cookbook resolves its output
    # directory from __file__, so running one writes into examples/ no matter the
    # working directory — and the artifacts committed there (report PDFs, dial and
    # transit SVGs) were being rewritten by every test run. They churn even when
    # nothing changed: a PDF carries its creation time, and a transit chart carries
    # today's sky. The suite must not touch them.
    env = {**os.environ, "STELLIUM_EXAMPLE_OUTPUT": tempfile.mkdtemp()}

    result = subprocess.run(
        [sys.executable, str(filepath)],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(EXAMPLES_DIR),
        env=env,
    )
    return result


# ─── Clean cookbooks (no external dependencies) ─────────────────────────


class TestCleanCookbooks:
    """Cookbooks that need only stellium + standard dependencies."""

    # analysis_cookbook is no longer a .ipynb — it is analysis_cookbook.md, executed
    # by the Sphinx build (nb_execution_raise_on_error=True), which runs in this same
    # workflow. A cell that fails there fails the docs job.

    def test_chart_cookbook(self):
        result = _run_cookbook("chart_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_dial_cookbook(self):
        result = _run_cookbook("dial_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_directions_cookbook(self):
        result = _run_cookbook("directions_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_io_cookbook(self):
        result = _run_cookbook("io_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_transit_cookbook(self):
        result = _run_cookbook("transit_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_vedic_cookbook(self):
        result = _run_cookbook("vedic_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_aspects_and_orbs_cookbook(self):
        result = _run_cookbook("aspects_and_orbs_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_bazi_cookbook(self):
        result = _run_cookbook("bazi_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_dignities_cookbook(self):
        result = _run_cookbook("dignities_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_comparison_cookbook(self):
        result = _run_cookbook("comparison_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_multichart_cookbook(self):
        result = _run_cookbook("multichart_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_progressions_cookbook(self):
        result = _run_cookbook("progressions_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_arc_directions_cookbook(self):
        result = _run_cookbook("arc_directions_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_returns_cookbook(self):
        result = _run_cookbook("returns_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_profections_cookbook(self):
        result = _run_cookbook("profections_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_ephemeris_cookbook(self):
        result = _run_cookbook("ephemeris_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_zodiacal_releasing_cookbook(self):
        result = _run_cookbook("zodiacal_releasing_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_hellenistic_cookbook(self):
        result = _run_cookbook("hellenistic_cookbook.py")
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"


# ─── Expensive cookbooks (longer timeout) ────────────────────────────────


class TestExpensiveCookbooks:
    """Cookbooks that do time-range searches or heavy computation."""

    def test_electional_cookbook(self):
        result = _run_cookbook("electional_cookbook.py", timeout=300)
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"


# ─── Cookbooks requiring external tools ──────────────────────────────────


class TestExternalToolCookbooks:
    """Cookbooks that require external binaries (Typst for PDF)."""

    @pytest.fixture(autouse=True)
    def _check_typst(self):
        """Skip if typst Python package is not installed."""
        try:
            import typst  # noqa: F401
        except ImportError:
            pytest.skip("typst package not installed (pip install typst)")

    def test_report_cookbook(self):
        result = _run_cookbook("report_cookbook.py", timeout=180)
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"

    def test_planner_cookbook(self):
        result = _run_cookbook("planner_cookbook.py", timeout=180)
        assert result.returncode == 0, f"STDERR:\n{result.stderr}"


# ─── Notebook cookbooks ──────────────────────────────────────────────────


def _run_notebook(filename: str, timeout: int = 180) -> subprocess.CompletedProcess:
    """Execute a Jupyter notebook and check for errors."""
    filepath = EXAMPLES_DIR / filename
    # Write executed notebook to a temp file (avoid /dev/null issues on macOS)
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=True) as tmp:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--ExecutePreprocessor.timeout=120",
                str(filepath),
                "--output",
                tmp.name,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
    return result


@pytest.mark.notebooks
class TestNotebookCookbooks:
    """Jupyter notebook cookbooks executed via nbconvert.

    These are expensive (each notebook generates many charts) so they have
    their own marker. Run with: pytest -m notebooks
    Excluded from the normal full suite to keep it under 5 minutes.
    """

    def test_chart_cookbook_notebook(self):
        result = _run_notebook("chart_cookbook.ipynb")
        assert result.returncode == 0, f"STDERR:\n{result.stderr[-2000:]}"
