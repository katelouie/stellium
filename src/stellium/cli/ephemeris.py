"""Ephemeris management commands."""

import click

from stellium.cli.ephemeris_download import (
    EPHEMERIS_BASE_URL,
    calculate_download_size,
    download_file,
    get_data_directory,
    get_required_files,
)


@click.group(name="ephemeris")
def ephemeris_group():
    """Manage Swiss Ephemeris data files."""
    pass


@ephemeris_group.command("download")
@click.option("--force", is_flag=True, help="Overwrite existing files")
@click.option(
    "--years",
    type=str,
    metavar="START-END",
    help='Year range to download (e.g., "1000-3000")',
)
@click.option("--quiet", is_flag=True, help="Suppress progress output")
def ephemeris_download_cmd(force, years, quiet):
    """Download Swiss Ephemeris data files."""
    # Parse year range
    start_year, end_year = None, None
    if years:
        try:
            start_str, end_str = years.split("-")
            start_year, end_year = int(start_str), int(end_str)
        except ValueError:
            click.echo(
                "❌ Invalid year range format. Use: START-END (e.g., 1000-3000)",
                err=True,
            )
            raise click.Abort() from ValueError

    # Get required files
    required_files = get_required_files(start_year, end_year)
    total_size_mb = calculate_download_size(required_files)

    if not quiet:
        click.echo("🌟 Swiss Ephemeris Data Downloader")
        click.echo("=" * 50)
        click.echo(f"📅 Year range: {start_year or 'beginning'} to {end_year or 'end'}")
        click.echo(f"📁 Files to download: {len(required_files)}")
        click.echo(f"📊 Total size: ~{total_size_mb:.1f} MB")

    if not force and not quiet:
        if not click.confirm("\n🤔 Continue with download?"):
            click.echo("📤 Download cancelled")
            return

    # Download files
    data_dir = get_data_directory()
    success_count = 0

    if not quiet:
        click.echo(f"\n📥 Downloading to: {data_dir}")
        click.echo("-" * 50)

    with click.progressbar(required_files, label="Downloading") as files:
        for filename in files:
            url = f"{EPHEMERIS_BASE_URL}{filename}"
            filepath = data_dir / filename

            if download_file(url, filepath, force, quiet=quiet):
                success_count += 1

    if not quiet:
        click.echo("\n" + "=" * 50)
        click.echo(f"✅ Download complete: {success_count}/{len(required_files)} files")

        if success_count == len(required_files):
            click.echo("🎉 All ephemeris files downloaded successfully!")
        else:
            click.echo("⚠️  Some files failed to download.", err=True)


@ephemeris_group.command("list")
@click.option(
    "--years",
    type=str,
    metavar="START-END",
    help='Year range to list (e.g., "1000-3000")',
)
def ephemeris_list_cmd(years):
    """List available ephemeris files."""
    # Parse year range
    start_year, end_year = None, None
    if years:
        try:
            start_str, end_str = years.split("-")
            start_year, end_year = int(start_str), int(end_str)
        except ValueError:
            click.echo("❌ Invalid year range format.", err=True)
            raise click.Abort() from ValueError

    required_files = get_required_files(start_year, end_year)
    total_size_mb = calculate_download_size(required_files)

    click.echo(
        f"📋 Available files for range {start_year or 'beginning'} to {end_year or 'end'}:"
    )
    for filename in required_files:
        click.echo(f"   {filename}")
    click.echo(f"\n📊 Total size: ~{total_size_mb:.1f} MB")
