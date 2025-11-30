"""Chart generation commands."""

import click


@click.group(name="chart")
def chart_group():
    """Generate and export charts."""
    pass


@chart_group.command("from-registry")
@click.argument("name")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--house-system",
    default="Placidus",
    type=click.Choice(["Placidus", "Whole Sign", "Koch", "Equal"]),
    help="House system to use",
)
@click.option(
    "--format",
    "output_format",
    default="svg",
    type=click.Choice(["svg", "terminal", "json"]),
    help="Output format",
)
def chart_from_registry_cmd(name, output, house_system, output_format):
    """
    Generate a chart from the birth registry.

    Example:
        stellium chart from-registry "Albert Einstein" -o einstein.svg
    """
    from stellium.core.builder import ChartBuilder
    from stellium.data.registry import get_notable_registry
    from stellium.engines.houses import (
        EqualHouses,
        KochHouses,
        PlacidusHouses,
        WholeSignHouses,
    )
    from stellium.presentation.builder import ReportBuilder

    # Map house system name to engine instance
    house_engines = {
        "Placidus": PlacidusHouses,
        "Whole Sign": WholeSignHouses,
        "Koch": KochHouses,
        "Equal": EqualHouses,
    }

    try:
        registry = get_notable_registry()
        notable = registry.get_by_name(name)
        # Build chart
        if notable:
            house_engine = house_engines[house_system]()
            chart = (
                ChartBuilder.from_native(notable)
                .with_house_systems([house_engine])
                .calculate()
            )
        else:
            raise ValueError(f"No Notable event or birth data exists for {name}")

        if output_format == "svg":
            output_path = output or f"{name.lower().replace(' ', '_')}.svg"
            chart.draw(output_path).save()
            click.echo(f"✅ Chart saved to: {output_path}")

        elif output_format == "terminal":
            _report = (
                ReportBuilder()
                .from_chart(chart)
                .with_chart_overview()
                .with_planet_positions()
                .with_aspects()
                .render("rich_table")
            )

        elif output_format == "json":
            # Export as JSON
            output_path = output or f"{name.lower().replace(' ', '_')}.json"
            # TODO:... implement JSON export
            # click.echo(f"✅ Chart data saved to: {output_path}")
            click.echo("❌ JSON output via CLI command not yet implemented.")

    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort() from ValueError
