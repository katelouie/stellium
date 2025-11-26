"""Cache management commands."""

import click

from stellium.utils.cache import cache_info, cache_size, clear_cache


@click.group(name="cache")
def cache_group():
    """Manage Stellium cache."""
    pass


@cache_group.command("info")
def cache_info_cmd():
    """Show cache information."""
    info = cache_info()

    click.echo("🗂️  Stellium Cache Information")
    click.echo("=" * 40)
    click.echo(f"Cache Directory: {info['cache_directory']}")
    click.echo(
        f"Max Age: {info['max_age_seconds']} seconds ({info['max_age_seconds'] / 3600:.1f} hours)"
    )
    click.echo(f"Total Files: {info['total_cached_files']}")
    click.echo(f"Total Size: {info['cache_size_mb']} MB")
    click.echo()
    click.echo("By Type:")
    for cache_type, count in info["by_type"].items():
        click.echo(f"  {cache_type}: {count} files")


@cache_group.command("clear")
@click.option(
    "--type",
    "cache_type",
    type=click.Choice(["ephemeris", "geocoding", "general"]),
    help="Cache type to clear (default: all)",
)
def cache_clear_cmd(cache_type):
    """Clear cache files."""
    if cache_type:
        removed = clear_cache(cache_type)
        click.echo(f"🗑️  Cleared {removed} files from {cache_type} cache")
    else:
        removed = clear_cache()
        click.echo(f"🗑️  Cleared {removed} files from all caches")


@cache_group.command("size")
@click.option(
    "--type",
    "cache_type",
    type=click.Choice(["ephemeris", "geocoding", "general"]),
    help="Cache type to check",
)
def cache_size_cmd(cache_type):
    """Show cache size information."""
    sizes = cache_size(cache_type)

    click.echo("📊 Cache Size Information")
    click.echo("=" * 30)
    for cache_type, count in sizes.items():
        click.echo(f"{cache_type}: {count} files")
