"""
Tests for the Stellium command-line interface.

This module tests all CLI commands including:
- Main CLI group and version
- Cache management commands (info, clear, size)
- Chart generation commands (from-registry)
- Ephemeris management commands (download, list)
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from stellium.cli import cli
from stellium.cli.ephemeris_download import (
    EPHEMERIS_BASE_URL,
    FILE_PATTERNS,
    YEAR_RANGES,
    calculate_download_size,
    get_data_directory,
    get_required_files,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def runner() -> CliRunner:
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_cache_info() -> dict:
    """Sample cache info response."""
    return {
        "cache_directory": "/tmp/.cache",
        "max_age_seconds": 86400,
        "total_cached_files": 42,
        "cache_size_mb": 15.5,
        "by_type": {
            "ephemeris": 20,
            "geocoding": 15,
            "general": 7,
        },
    }


@pytest.fixture
def mock_cache_size() -> dict:
    """Sample cache size response."""
    return {
        "ephemeris": 20,
        "geocoding": 15,
        "general": 7,
    }


# ============================================================================
# MAIN CLI GROUP TESTS
# ============================================================================


class TestMainCLI:
    """Tests for the main CLI group."""

    def test_cli_help(self, runner: CliRunner):
        """Test that --help shows help message."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Stellium - Professional Astrology Library" in result.output
        assert "cache" in result.output
        assert "ephemeris" in result.output
        assert "chart" in result.output

    def test_cli_version(self, runner: CliRunner):
        """Test that --version shows version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        # Version should contain a version number pattern
        assert "version" in result.output.lower() or "." in result.output

    def test_cli_no_args(self, runner: CliRunner):
        """Test CLI with no arguments shows usage info."""
        result = runner.invoke(cli)
        # Click shows usage info with exit code 0 or 2 depending on config
        # Both are acceptable - the important thing is it shows usage
        assert result.exit_code in (0, 2)
        # Should show available commands or usage
        assert "cache" in result.output or "Usage" in result.output

    def test_cli_invalid_command(self, runner: CliRunner):
        """Test CLI with invalid command shows error."""
        result = runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0
        assert "Error" in result.output or "No such command" in result.output


# ============================================================================
# CACHE COMMAND TESTS
# ============================================================================


class TestCacheCommands:
    """Tests for cache management commands."""

    def test_cache_group_help(self, runner: CliRunner):
        """Test cache group --help."""
        result = runner.invoke(cli, ["cache", "--help"])
        assert result.exit_code == 0
        assert "Manage Stellium cache" in result.output
        assert "info" in result.output
        assert "clear" in result.output
        assert "size" in result.output

    def test_cache_info_cmd(self, runner: CliRunner, mock_cache_info: dict):
        """Test 'cache info' command."""
        with patch("stellium.cli.cache.cache_info", return_value=mock_cache_info):
            result = runner.invoke(cli, ["cache", "info"])

        assert result.exit_code == 0
        assert "Stellium Cache Information" in result.output
        assert "Cache Directory:" in result.output
        assert "Max Age:" in result.output
        assert "Total Files:" in result.output
        assert "Total Size:" in result.output
        assert "By Type:" in result.output
        assert "ephemeris:" in result.output
        assert "geocoding:" in result.output

    def test_cache_clear_all(self, runner: CliRunner):
        """Test 'cache clear' command clears all caches."""
        with patch("stellium.cli.cache.clear_cache", return_value=42) as mock_clear:
            result = runner.invoke(cli, ["cache", "clear"])

        assert result.exit_code == 0
        assert "42 files" in result.output
        assert "all caches" in result.output
        mock_clear.assert_called_once_with()

    def test_cache_clear_specific_type(self, runner: CliRunner):
        """Test 'cache clear --type' clears specific cache type."""
        with patch("stellium.cli.cache.clear_cache", return_value=15) as mock_clear:
            result = runner.invoke(cli, ["cache", "clear", "--type", "ephemeris"])

        assert result.exit_code == 0
        assert "15 files" in result.output
        assert "ephemeris cache" in result.output
        mock_clear.assert_called_once_with("ephemeris")

    @pytest.mark.parametrize("cache_type", ["ephemeris", "geocoding", "general"])
    def test_cache_clear_valid_types(self, runner: CliRunner, cache_type: str):
        """Test that all valid cache types are accepted."""
        with patch("stellium.cli.cache.clear_cache", return_value=5):
            result = runner.invoke(cli, ["cache", "clear", "--type", cache_type])

        assert result.exit_code == 0
        assert cache_type in result.output

    def test_cache_clear_invalid_type(self, runner: CliRunner):
        """Test 'cache clear' with invalid type shows error."""
        result = runner.invoke(cli, ["cache", "clear", "--type", "invalid"])
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "Error" in result.output

    def test_cache_size_all(self, runner: CliRunner, mock_cache_size: dict):
        """Test 'cache size' command shows all sizes."""
        with patch("stellium.cli.cache.cache_size", return_value=mock_cache_size):
            result = runner.invoke(cli, ["cache", "size"])

        assert result.exit_code == 0
        assert "Cache Size Information" in result.output
        assert "ephemeris:" in result.output or "ephemeris" in result.output

    def test_cache_size_specific_type(self, runner: CliRunner):
        """Test 'cache size --type' shows specific cache size."""
        mock_size = {"ephemeris": 20}
        with patch("stellium.cli.cache.cache_size", return_value=mock_size):
            result = runner.invoke(cli, ["cache", "size", "--type", "ephemeris"])

        assert result.exit_code == 0
        assert "ephemeris" in result.output


# ============================================================================
# CHART COMMAND TESTS
# ============================================================================


class TestChartCommands:
    """Tests for chart generation commands."""

    def test_chart_group_help(self, runner: CliRunner):
        """Test chart group --help."""
        result = runner.invoke(cli, ["chart", "--help"])
        assert result.exit_code == 0
        assert "Generate and export charts" in result.output
        assert "from-registry" in result.output

    def test_chart_from_registry_svg(self, runner: CliRunner):
        """Test 'chart from-registry' command with SVG output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_chart.svg"

            result = runner.invoke(
                cli,
                ["chart", "from-registry", "Albert Einstein", "-o", str(output_path)],
            )

            assert result.exit_code == 0
            assert "Chart saved to" in result.output
            assert output_path.exists()
            # Verify it's an SVG file
            content = output_path.read_text()
            assert "<svg" in content or "svg" in content.lower()

    def test_chart_from_registry_default_filename(self, runner: CliRunner):
        """Test 'chart from-registry' with default filename."""
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["chart", "from-registry", "Albert Einstein"])

            assert result.exit_code == 0
            assert "Chart saved to" in result.output
            # Default filename should be based on name
            assert Path("albert_einstein.svg").exists()

    def test_chart_from_registry_terminal_output(self, runner: CliRunner):
        """Test 'chart from-registry' with terminal output."""
        result = runner.invoke(
            cli,
            ["chart", "from-registry", "Albert Einstein", "--format", "terminal"],
        )

        # Should succeed and print to terminal (via Rich tables)
        assert result.exit_code == 0

    def test_chart_from_registry_json_output(self, runner: CliRunner):
        """Test 'chart from-registry' with JSON output (not implemented)."""
        result = runner.invoke(
            cli,
            ["chart", "from-registry", "Albert Einstein", "--format", "json"],
        )

        # JSON is not implemented, should show message
        assert result.exit_code == 0
        assert "not yet implemented" in result.output

    def test_chart_from_registry_invalid_name(self, runner: CliRunner):
        """Test 'chart from-registry' with unknown name."""
        result = runner.invoke(
            cli, ["chart", "from-registry", "Nonexistent Person XYZ123"]
        )

        assert result.exit_code != 0
        assert "Error" in result.output or "Aborted" in result.output

    @pytest.mark.parametrize(
        "house_system", ["Placidus", "Whole Sign", "Koch", "Equal"]
    )
    def test_chart_from_registry_house_systems(
        self, runner: CliRunner, house_system: str
    ):
        """Test 'chart from-registry' with different house systems."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "chart",
                    "from-registry",
                    "Albert Einstein",
                    "--house-system",
                    house_system,
                ],
            )

            assert result.exit_code == 0
            assert "Chart saved to" in result.output

    def test_chart_from_registry_invalid_house_system(self, runner: CliRunner):
        """Test 'chart from-registry' with invalid house system."""
        result = runner.invoke(
            cli,
            [
                "chart",
                "from-registry",
                "Albert Einstein",
                "--house-system",
                "InvalidSystem",
            ],
        )

        assert result.exit_code != 0


# ============================================================================
# EPHEMERIS COMMAND TESTS
# ============================================================================


class TestEphemerisCommands:
    """Tests for ephemeris management commands."""

    def test_ephemeris_group_help(self, runner: CliRunner):
        """Test ephemeris group --help."""
        result = runner.invoke(cli, ["ephemeris", "--help"])
        assert result.exit_code == 0
        assert "Manage Swiss Ephemeris data files" in result.output
        assert "download" in result.output
        assert "list" in result.output

    def test_ephemeris_list_default(self, runner: CliRunner):
        """Test 'ephemeris list' shows all files."""
        result = runner.invoke(cli, ["ephemeris", "list"])

        assert result.exit_code == 0
        assert "Available files" in result.output
        # Should show some ephemeris filenames
        assert ".se1" in result.output
        assert "Total size:" in result.output

    def test_ephemeris_list_with_years(self, runner: CliRunner):
        """Test 'ephemeris list --years' shows filtered files."""
        result = runner.invoke(cli, ["ephemeris", "list", "--years", "1800-2400"])

        assert result.exit_code == 0
        assert "1800" in result.output
        assert "2400" in result.output
        # Should show files for that range
        assert ".se1" in result.output

    def test_ephemeris_list_invalid_years(self, runner: CliRunner):
        """Test 'ephemeris list' with invalid year format."""
        result = runner.invoke(cli, ["ephemeris", "list", "--years", "invalid"])

        assert result.exit_code != 0
        assert "Invalid year range" in result.output or "Aborted" in result.output

    def test_ephemeris_download_confirmation(self, runner: CliRunner):
        """Test 'ephemeris download' asks for confirmation."""
        result = runner.invoke(cli, ["ephemeris", "download"], input="n\n")

        # Should ask for confirmation and respect 'n'
        assert result.exit_code == 0
        assert (
            "Continue with download?" in result.output or "cancelled" in result.output
        )

    def test_ephemeris_download_force(self, runner: CliRunner):
        """Test 'ephemeris download --force' skips confirmation."""
        with patch("stellium.cli.ephemeris.download_file", return_value=True):
            with patch(
                "stellium.cli.ephemeris.get_required_files",
                return_value=["test_file.se1"],
            ):
                with patch(
                    "stellium.cli.ephemeris.calculate_download_size", return_value=1.0
                ):
                    result = runner.invoke(cli, ["ephemeris", "download", "--force"])

        # Should not ask for confirmation with --force
        assert result.exit_code == 0
        assert "Continue with download?" not in result.output

    def test_ephemeris_download_quiet(self, runner: CliRunner):
        """Test 'ephemeris download --quiet' suppresses output."""
        with patch("stellium.cli.ephemeris.download_file", return_value=True):
            with patch(
                "stellium.cli.ephemeris.get_required_files",
                return_value=["test_file.se1"],
            ):
                with patch(
                    "stellium.cli.ephemeris.calculate_download_size", return_value=1.0
                ):
                    result = runner.invoke(
                        cli, ["ephemeris", "download", "--force", "--quiet"]
                    )

        assert result.exit_code == 0
        # Should have minimal output in quiet mode
        assert "Swiss Ephemeris Data Downloader" not in result.output

    def test_ephemeris_download_with_years(self, runner: CliRunner):
        """Test 'ephemeris download --years' downloads specific range."""
        with patch("stellium.cli.ephemeris.download_file", return_value=True):
            with patch("stellium.cli.ephemeris.get_required_files") as mock_get_files:
                mock_get_files.return_value = ["sepl_18.se1"]
                with patch(
                    "stellium.cli.ephemeris.calculate_download_size", return_value=1.0
                ):
                    result = runner.invoke(
                        cli,
                        ["ephemeris", "download", "--force", "--years", "1800-2400"],
                    )

        assert result.exit_code == 0
        # Should call get_required_files with the year range
        mock_get_files.assert_called()

    def test_ephemeris_download_invalid_years(self, runner: CliRunner):
        """Test 'ephemeris download' with invalid year format."""
        result = runner.invoke(cli, ["ephemeris", "download", "--years", "not-a-range"])

        assert result.exit_code != 0
        assert "Invalid year range" in result.output or "Aborted" in result.output


# ============================================================================
# EPHEMERIS DOWNLOAD HELPER FUNCTION TESTS
# ============================================================================


class TestEphemerisDownloadHelpers:
    """Tests for ephemeris download helper functions."""

    def test_get_data_directory(self):
        """Test get_data_directory returns a valid path."""
        data_dir = get_data_directory()

        assert isinstance(data_dir, Path)
        assert data_dir.exists()
        assert "ephe" in str(data_dir)

    def test_get_required_files_default(self):
        """Test get_required_files returns all files by default."""
        files = get_required_files()

        assert isinstance(files, list)
        assert len(files) > 0
        # Should include multiple file types
        assert any(f.startswith("sepl") for f in files)
        assert any(f.startswith("semo") for f in files)
        assert any(f.startswith("seas") for f in files)

    def test_get_required_files_specific_range(self):
        """Test get_required_files filters by year range."""
        files = get_required_files(start_year=1800, end_year=2400)

        assert isinstance(files, list)
        assert len(files) > 0
        # Should be fewer files than the full range
        all_files = get_required_files()
        assert len(files) <= len(all_files)

    def test_get_required_files_narrow_range(self):
        """Test get_required_files with narrow year range."""
        files = get_required_files(start_year=1900, end_year=2000)

        assert isinstance(files, list)
        # Should include files covering 1900-2000
        # The 1800-2399 range file should be included
        assert any("18" in f or "_18" in f for f in files)

    def test_get_required_files_returns_unique(self):
        """Test that get_required_files returns unique filenames."""
        files = get_required_files()

        assert len(files) == len(set(files))

    def test_get_required_files_returns_sorted(self):
        """Test that get_required_files returns sorted filenames."""
        files = get_required_files()

        assert files == sorted(files)

    def test_calculate_download_size_empty(self):
        """Test calculate_download_size with empty list."""
        size = calculate_download_size([])

        assert size == 0.0

    def test_calculate_download_size_single_file(self):
        """Test calculate_download_size with single file."""
        # A planet file should be ~473KB
        size = calculate_download_size(["sepl_18.se1"])

        assert size > 0
        assert size < 1  # Less than 1MB for a single file

    def test_calculate_download_size_multiple_files(self):
        """Test calculate_download_size with multiple files."""
        files = ["sepl_18.se1", "semo_18.se1", "seas_18.se1"]
        size = calculate_download_size(files)

        assert size > 0
        # Moon files are largest (~1.2MB), so total should be > 1MB
        assert size > 1

    def test_calculate_download_size_unknown_prefix(self):
        """Test calculate_download_size ignores unknown file prefixes."""
        size = calculate_download_size(["unknown_file.se1"])

        # Unknown files contribute 0 to size
        assert size == 0.0

    def test_file_patterns_structure(self):
        """Test FILE_PATTERNS has expected structure."""
        assert "planets" in FILE_PATTERNS
        assert "moon" in FILE_PATTERNS
        assert "asteroids" in FILE_PATTERNS

        for _category, config in FILE_PATTERNS.items():
            assert "prefix" in config
            assert "description" in config
            assert "size_kb" in config
            assert isinstance(config["size_kb"], int)

    def test_year_ranges_structure(self):
        """Test YEAR_RANGES has expected structure."""
        assert len(YEAR_RANGES) > 0

        for entry in YEAR_RANGES:
            assert len(entry) == 3
            filename, start_year, end_year = entry
            assert isinstance(filename, str)
            assert filename.endswith(".se1")
            assert isinstance(start_year, int)
            assert isinstance(end_year, int)
            assert start_year < end_year

    def test_year_ranges_coverage(self):
        """Test YEAR_RANGES covers expected historical range."""
        all_starts = [entry[1] for entry in YEAR_RANGES]
        all_ends = [entry[2] for entry in YEAR_RANGES]

        min_year = min(all_starts)
        max_year = max(all_ends)

        # Should cover ancient history to far future
        assert min_year < -5000
        assert max_year > 15000

    def test_ephemeris_base_url(self):
        """Test EPHEMERIS_BASE_URL is valid."""
        assert EPHEMERIS_BASE_URL.startswith("https://")
        assert "astro.com" in EPHEMERIS_BASE_URL


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def test_full_workflow_chart_generation(self, runner: CliRunner):
        """Test complete workflow: generate chart from notable."""
        with runner.isolated_filesystem():
            # Generate chart
            result = runner.invoke(
                cli,
                ["chart", "from-registry", "Albert Einstein", "-o", "einstein.svg"],
            )

            assert result.exit_code == 0
            assert Path("einstein.svg").exists()

            # File should be valid SVG
            content = Path("einstein.svg").read_text()
            assert len(content) > 1000  # Non-trivial SVG

    def test_cache_workflow(self, runner: CliRunner):
        """Test cache info/size/clear workflow."""
        # Get info
        with patch(
            "stellium.cli.cache.cache_info",
            return_value={
                "cache_directory": "/tmp/.cache",
                "max_age_seconds": 86400,
                "total_cached_files": 10,
                "cache_size_mb": 1.0,
                "by_type": {"ephemeris": 5, "geocoding": 3, "general": 2},
            },
        ):
            result = runner.invoke(cli, ["cache", "info"])
            assert result.exit_code == 0

        # Get size
        with patch(
            "stellium.cli.cache.cache_size",
            return_value={"ephemeris": 5, "geocoding": 3, "general": 2},
        ):
            result = runner.invoke(cli, ["cache", "size"])
            assert result.exit_code == 0

        # Clear cache
        with patch("stellium.cli.cache.clear_cache", return_value=10):
            result = runner.invoke(cli, ["cache", "clear"])
            assert result.exit_code == 0

    def test_ephemeris_list_and_download_workflow(self, runner: CliRunner):
        """Test ephemeris list then download workflow."""
        # List files first
        result = runner.invoke(cli, ["ephemeris", "list", "--years", "1800-2400"])
        assert result.exit_code == 0
        assert ".se1" in result.output

        # Download with quiet and force (mocked)
        with patch("stellium.cli.ephemeris.download_file", return_value=True):
            with patch(
                "stellium.cli.ephemeris.get_required_files",
                return_value=["sepl_18.se1"],
            ):
                with patch(
                    "stellium.cli.ephemeris.calculate_download_size", return_value=0.5
                ):
                    result = runner.invoke(
                        cli,
                        [
                            "ephemeris",
                            "download",
                            "--years",
                            "1800-2400",
                            "--force",
                            "--quiet",
                        ],
                    )

        assert result.exit_code == 0
