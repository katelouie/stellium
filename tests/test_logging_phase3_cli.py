"""Phase 3: CLI/tooling output goes through click.echo, not bare print.

Covers the migration of the CLI and tooling prints to ``click.echo``
(``docs/development/specs/STRUCTURED_LOGGING_SPEC.md`` Phase 3), and the
removal of the redundant ``stellium.utils.cache_utils`` display module (its
job is done by the ``stellium cache`` CLI command).
"""

import pytest
from click.testing import CliRunner

from stellium.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_download_file_skip_uses_click_echo(tmp_path, capsys):
    """download_file echoes progress via click.echo (no network on the skip path)."""
    from stellium.cli.ephemeris_download import download_file

    existing = tmp_path / "sepl_18.se1"
    existing.write_text("already here")

    # File exists and force=False -> returns immediately, echoing "Skipping".
    result = download_file("https://example.invalid/x", existing)

    assert result is True
    assert "Skipping" in capsys.readouterr().out


def test_download_file_quiet_suppresses_output(tmp_path, capsys):
    from stellium.cli.ephemeris_download import download_file

    existing = tmp_path / "sepl_18.se1"
    existing.write_text("already here")

    download_file("https://example.invalid/x", existing, quiet=True)

    assert capsys.readouterr().out == ""


def test_cli_ephemeris_group_help(runner):
    """The ephemeris CLI group loads and renders help via click (hermetic)."""
    result = runner.invoke(cli, ["ephemeris", "--help"])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_cli_cache_group_help(runner):
    """The cache CLI group loads and renders help via click (hermetic)."""
    result = runner.invoke(cli, ["cache", "--help"])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_cache_utils_module_removed():
    """The redundant display module is gone and no longer a public export."""
    import stellium.utils as utils

    assert not hasattr(utils, "print_cache_info")
    with pytest.raises(ImportError):
        from stellium.utils import cache_utils  # noqa: F401
