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

from stellium.i18n import (
    available_locales_info,
    build_catalog,
    get_available_locales,
    namespaces,
)
from stellium.i18n.formats import DEFAULT_PATTERNS
from stellium.i18n.loader import _get_locale_strings

console = Console()


@click.group(name="i18n")
def i18n_group() -> None:
    """Inspect and extend the translation catalog."""


@i18n_group.command(name="locales")
def locales_cmd() -> None:
    """Show every available locale — coverage, fallback chain and font status."""
    from stellium import fonts

    table = Table(title="Available locales")
    table.add_column("Locale")
    table.add_column("Language")
    table.add_column("Status")
    table.add_column("Catalog", justify="right")
    table.add_column("Falls back through")
    table.add_column("Font")

    for row in available_locales_info():
        code = row["code"]
        done, total = row["coverage"]
        pct = 100 * done / total if total else 0
        chain = " → ".join(row["chain"][1:]) or "—"  # drop the locale itself

        script = fonts.locale_script(code)
        if script is None:
            font = "[dim]not needed[/dim]"
        elif fonts.is_installed(script):
            font = f"[green]{script} ✓[/green]"
        else:
            font = f"[yellow]{script} (run: stellium fonts download {script})[/yellow]"

        table.add_row(
            code,
            row["language"],
            row["status"],
            f"{done}/{total} ({pct:.0f}%)",
            chain,
            font,
        )

    console.print(table)
    console.print(
        "\nDetail one with [bold]stellium i18n coverage <locale>[/bold]. "
        "Catalog % counts the closed vocabulary resolved through the fallback chain; "
        "message and format strings degrade to English independently."
    )


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
    """Print a locale file skeleton, grouped by namespace, ready to translate.

    The shape matches a real locale file: catalog terms nested under their namespace,
    format patterns under ``format``. A translator fills in the empty values and drops
    the result at ``locales/<code>/strings.json``. Seeding from an existing locale keeps
    the translations already done and leaves only the gaps blank.
    """
    existing = _get_locale_strings(locale) if locale else {}

    # Catalog terms nest under their namespace: "body.Sun" -> groups["body"]["Sun"].
    groups: dict[str, dict[str, str]] = defaultdict(dict)
    for key in build_catalog():
        ns, rest = key.split(".", 1)
        groups[ns][rest] = existing.get(key, "")

    # Format patterns default to the English layout (a translator overrides what differs).
    for key, english in DEFAULT_PATTERNS.items():
        rest = key.split(".", 1)[1]
        groups["format"][rest] = existing.get(key, english)

    # Message keys (report labels, templates) are English strings the sections register,
    # not derivable from the catalog — so carry over what the seed locale has, or a
    # re-extract would silently drop them. The 'legacy' group is deliberately omitted:
    # it is scaffolding that Phase 3 removes, and a fresh translation should not inherit
    # it (translating the catalog makes it redundant).
    catalog_terms = {v for k, v in build_catalog().items() if not k.endswith(".short")}
    for full_key, value in existing.items():
        namespace = full_key.split(".", 1)[0]
        if namespace in groups or namespace == "format":
            continue  # already emitted as a catalog/format entry
        if "{" in full_key or full_key not in catalog_terms:
            groups.setdefault("message", {})[full_key] = value
        # else: a bare catalog duplicate — legacy scaffolding, skip.

    doc: dict[str, object] = {
        "metadata": {"language": locale or "??", "status": "draft"}
    }
    for ns in sorted(k for k in groups if k not in {"format", "message"}):
        doc[ns] = dict(sorted(groups[ns].items()))
    doc["format"] = dict(sorted(groups["format"].items()))
    if groups.get("message"):
        doc["message"] = dict(sorted(groups["message"].items()))

    click.echo(json.dumps(doc, indent=2, ensure_ascii=False))
