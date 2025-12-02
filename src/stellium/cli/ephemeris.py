"""Ephemeris management commands."""

import click

from stellium.cli.ephemeris_download import (
    COMMON_ASTEROIDS,
    EPHEMERIS_BASE_URL,
    calculate_download_size,
    download_asteroid_file,
    download_common_asteroids,
    download_file,
    get_asteroid_filename,
    get_asteroid_folder,
    get_data_directory,
    get_required_files,
    resolve_asteroid_input,
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


@ephemeris_group.command("download-asteroid")
@click.argument("asteroids", required=False)
@click.option("--force", is_flag=True, help="Overwrite existing files")
@click.option("--tnos", is_flag=True, help="Download all common TNO files")
@click.option("--list", "list_only", is_flag=True, help="List available asteroids")
def download_asteroid_cmd(asteroids, force, tnos, list_only):
    """
    Download asteroid ephemeris files.

    ASTEROIDS can be:

    \b
      - A number: 136199
      - Multiple numbers: 136199,90377,50000
      - A name: eris, sedna, makemake
      - Special keyword: tnos (all common TNOs)

    Examples:

    \b
      stellium ephemeris download-asteroid 136199
      stellium ephemeris download-asteroid eris
      stellium ephemeris download-asteroid --tnos
      stellium ephemeris download-asteroid 136199,90377
    """
    # List mode
    if list_only:
        click.echo("🌟 Common TNO/Dwarf Planet Asteroids")
        click.echo("=" * 50)
        for name, number in COMMON_ASTEROIDS.items():
            folder = get_asteroid_folder(number)
            filename = get_asteroid_filename(number)
            click.echo(f"   {name:12} #{number:>6}  ({folder}/{filename})")
        click.echo()
        click.echo("Usage: stellium ephemeris download-asteroid <number or name>")
        click.echo("       stellium ephemeris download-asteroid --tnos")
        return

    # Download all TNOs
    if tnos:
        download_common_asteroids(force=force)
        return

    # Need asteroids argument
    if not asteroids:
        click.echo("❌ Please specify asteroid number(s) or use --tnos")
        click.echo()
        click.echo("Examples:")
        click.echo("   stellium ephemeris download-asteroid 136199")
        click.echo("   stellium ephemeris download-asteroid eris")
        click.echo("   stellium ephemeris download-asteroid --tnos")
        click.echo()
        click.echo("Use --list to see common asteroids")
        raise click.Abort()

    # Resolve input to asteroid numbers
    numbers = resolve_asteroid_input(asteroids)

    if not numbers:
        click.echo(f"❌ Could not parse asteroid input: {asteroids}")
        raise click.Abort()

    # Download each asteroid
    click.echo("🌟 Downloading asteroid ephemeris files...")
    click.echo("-" * 50)

    success_count = 0
    for number in numbers:
        # Try to find a name for display
        name = None
        for n, num in COMMON_ASTEROIDS.items():
            if num == number:
                name = n
                break

        display = f"{name} (#{number})" if name else f"#{number}"
        click.echo(f"   {display}...")

        if download_asteroid_file(number, force=force, quiet=True):
            success_count += 1
            click.echo(f"   ✅ {display}")
        else:
            click.echo(f"   ❌ {display} (failed)")

    click.echo("-" * 50)
    click.echo(f"✅ Downloaded {success_count}/{len(numbers)} files")


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
