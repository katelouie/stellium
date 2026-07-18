"""``stellium fonts`` — fetch the font packs that render non-Latin charts.

Mirrors ``stellium ephemeris download``: on-demand data the package does not bundle,
fetched into ``~/.stellium/`` and verified against a checksum.
"""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from stellium import fonts

console = Console()


@click.group(name="fonts")
def fonts_group() -> None:
    """Download and manage font packs for non-Latin chart rendering."""


@fonts_group.command(name="list")
def list_cmd() -> None:
    """Show the available font packs and which are installed."""
    packs = fonts.list_packs()
    if not packs:
        console.print("No font packs in the manifest.")
        return

    table = Table(title="Font packs")
    table.add_column("Script")
    table.add_column("Covers")
    table.add_column("Fonts")
    table.add_column("Installed")

    for script, pack in packs.items():
        roles = ", ".join(f"{f['role']}" for f in pack["fonts"])
        table.add_row(
            script,
            pack.get("covers") or "—",
            roles,
            "[green]yes[/green]" if pack["installed"] else "[dim]no[/dim]",
        )
    console.print(table)
    console.print(
        "\nInstall one with [bold]stellium fonts download <script>[/bold] "
        "(e.g. [bold]stellium fonts download zh[/bold])."
    )


@fonts_group.command(name="download")
@click.argument("script")
@click.option("--force", is_flag=True, help="Re-fetch even if already installed.")
def download_cmd(script: str, force: bool) -> None:
    """Fetch, verify and install the font pack for SCRIPT (e.g. zh, zh-hant)."""
    try:
        target = fonts.download_pack(
            script, force=force, on_progress=lambda m: console.print(f"  {m}")
        )
    except fonts.FontDownloadError as e:
        raise click.ClickException(str(e)) from e
    console.print(f"[green]✓[/green] {script} installed at {target}")


@fonts_group.command(name="remove")
@click.argument("script")
def remove_cmd(script: str) -> None:
    """Delete the installed font pack for SCRIPT."""
    if fonts.remove_pack(script):
        console.print(f"[green]✓[/green] removed {script}")
    else:
        console.print(f"{script} is not installed.")


@fonts_group.command(name="path")
def path_cmd() -> None:
    """Print the font directory (~/.stellium/fonts/)."""
    from stellium.data.paths import USER_FONTS_DIR

    console.print(str(USER_FONTS_DIR))
