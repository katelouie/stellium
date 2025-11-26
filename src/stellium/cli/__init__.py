"""Stellium command-line interface."""

import click

from stellium import __version__

# Import and register command groups
from stellium.cli.cache import cache_group
from stellium.cli.chart import chart_group
from stellium.cli.ephemeris import ephemeris_group


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Stellium - Professional Astrology Library

    A comprehensive toolkit for astrological calculations,
    chart generation, and visualization.
    """
    pass


cli.add_command(cache_group)
cli.add_command(ephemeris_group)
cli.add_command(chart_group)

if __name__ == "__main__":
    cli()
