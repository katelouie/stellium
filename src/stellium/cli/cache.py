"""Cache management commands."""

import os

import click

from stellium.data.paths import ENV_CACHE_PATH, ENV_EPHE_PATH, get_ephe_dir
from stellium.utils.cache import cache_info, cache_size, clear_cache


def _source(env_var: str) -> str:
    """Say *why* a path is what it is — the question behind most path bug reports."""
    if os.environ.get(env_var, "").strip():
        return f"set by {env_var}"
    return f"default — override with {env_var}"


@click.group(name="cache")
def cache_group():
    """Manage Stellium cache."""
    pass


@cache_group.command("info")
def cache_info_cmd():
    """Show where Stellium reads and writes, and what is cached."""
    info = cache_info()

    click.echo("🗂️  Stellium paths")
    click.echo("=" * 60)
    click.echo(f"Cache (disposable):  {info['cache_directory']}")
    click.echo(f"                     {_source(ENV_CACHE_PATH)}")
    click.echo(f"Ephemeris (data):    {get_ephe_dir()}")
    click.echo(f"                     {_source(ENV_EPHE_PATH)}")
    click.echo()
    click.echo("The cache is safe to delete at any time. The ephemeris directory is")
    click.echo("not — it holds any asteroid/TNO files you downloaded.")
    click.echo()
    click.echo("🗂️  Cache contents")
    click.echo("=" * 60)
    click.echo(
        f"Max Age: {info['max_age_seconds']} seconds "
        f"({info['max_age_seconds'] / 3600:.1f} hours)"
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
