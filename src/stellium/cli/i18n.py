"""``stellium i18n`` — tools for whoever is translating the library.

Two commands, and neither is a CI gate. An incomplete locale is a *valid* state: it
degrades to English, so gating on completeness would only mean a contributor cannot land
a partial language. These exist to give a translator a worklist.
"""

from __future__ import annotations

import json
from collections import defaultdict

import click
from rich.console import Console
from rich.table import Table

from stellium.i18n import build_catalog, get_available_locales, namespaces
from stellium.i18n.formats import DEFAULT_PATTERNS
from stellium.i18n.loader import _get_locale_strings

console = Console()


@click.group(name="i18n")
def i18n_group() -> None:
    """Inspect and extend the translation catalog."""


@i18n_group.command(name="coverage")
@click.argument("locale")
def coverage(locale: str) -> None:
    """Report what LOCALE has translated, and what it is missing, by namespace."""
    available = get_available_locales()
    if locale not in available:
        raise click.BadParameter(
            f"no locale {locale!r}. Available: {', '.join(available)}"
        )

    strings = _get_locale_strings(locale)

    table = Table(title=f"Catalog coverage — {locale}")
    table.add_column("Namespace")
    table.add_column("Done", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Missing", overflow="fold", style="dim")

    total_done = total_all = 0
    for ns, keys in namespaces().items():
        done = [k for k in keys if k in strings]
        missing = [k for k in keys if k not in strings]
        total_done += len(done)
        total_all += len(keys)
        table.add_row(
            ns,
            str(len(done)),
            str(len(keys)),
            ", ".join(k.split(".", 1)[1] for k in missing[:6])
            + (f" … +{len(missing) - 6}" if len(missing) > 6 else ""),
        )

    console.print(table)

    fmt_missing = [k for k in DEFAULT_PATTERNS if k not in strings]
    pct = (100 * total_done / total_all) if total_all else 0
    console.print(
        f"\n[bold]{total_done}/{total_all}[/bold] catalog terms ([bold]{pct:.0f}%[/bold])"
    )
    if fmt_missing:
        console.print(
            f"[yellow]{len(fmt_missing)}[/yellow] format patterns not overridden "
            f"(English layout will be used): {', '.join(fmt_missing)}"
        )

    # A translated template that invents or drops a slot renders as English rather than
    # crashing — but it is a bug in the locale file, so say so.
    broken = []
    for key, value in strings.items():
        if "{" not in key:
            continue
        want = {s.split("}")[0] for s in key.split("{")[1:]}
        got = {s.split("}")[0] for s in value.split("{")[1:]}
        if not want <= got:
            broken.append((key, sorted(want - got)))
    if broken:
        console.print(f"\n[red]{len(broken)} template(s) dropping slots:[/red]")
        for key, lost in broken:
            console.print(f"  {key!r} loses {lost}")


@i18n_group.command(name="extract")
@click.option("--locale", default=None, help="Seed from an existing locale's strings.")
def extract(locale: str | None) -> None:
    """Print a locale file skeleton containing every key, ready to translate."""
    existing = _get_locale_strings(locale) if locale else {}

    strings: dict[str, str] = {}
    grouped: dict[str, list[str]] = defaultdict(list)
    for key in build_catalog():
        grouped[key.split(".", 1)[0]].append(key)
    for ns in sorted(grouped):
        for key in sorted(grouped[ns]):
            strings[key] = existing.get(key, "")
    for key, english in DEFAULT_PATTERNS.items():
        strings[key] = existing.get(key, english)

    click.echo(
        json.dumps(
            {
                "metadata": {"language": locale or "??", "status": "draft"},
                "strings": strings,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
