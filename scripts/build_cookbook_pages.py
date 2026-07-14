#!/usr/bin/env python3
"""
Generate a documentation page for every cookbook in `examples/`.

    python scripts/build_cookbook_pages.py          # write docs/cookbooks/*.md
    python scripts/build_cookbook_pages.py --clean  # remove them

`docs/conf.py` calls this on `builder-inited`, so the pages are rebuilt from the
scripts on every Sphinx build — including on Read the Docs. Nothing is committed,
so nothing can go stale: **there is no copy of the code to drift.**

That matters here more than usual. There are 21 cookbooks holding **374 runnable
recipes**, and not one of them appeared anywhere in the documentation site. Hand-
copying that into Markdown would have created 374 code blocks with no connection to
the code they claim to show — which is exactly the failure the astrology guide made,
and exactly what `tests/test_doc_codeblocks.py` exists to prevent.

So the pages do not contain code. They `literalinclude` it, addressed by
`:pyobject:`, which means Sphinx reads the function out of the real script at build
time. Rename a recipe and the build tells you. Edit a recipe and the page follows.

Each cookbook is a module of `example_*` functions with a docstring apiece:

    def example_1_simplest_chart():
        \"\"\"Example 1: The simplest possible chart.\"\"\"
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = REPO / "examples"
OUT = REPO / "docs" / "cookbooks"

# "Example 1: Solar Arc Directions by Age" -> "Solar Arc Directions by Age".
# The number is already the heading's position on the page; repeating it is noise.
EXAMPLE_PREFIX = re.compile(r"^Example\s+\d+\s*[:.\-–]\s*", re.I)

# Every cookbook titles itself "<Topic> Cookbook — <something>", and the something is
# usually "Comprehensive Examples" or "Examples for Stellium <the topic again>". In a
# section called Cookbooks, on a page full of examples, none of that carries any
# information — it just makes the sidebar a column of near-identical strings:
#
#     Aspects & Orbs Cookbook — Comprehensive Examples
#     Dignities & Dispositors Cookbook — Comprehensive Examples
#     BaZi (Four Pillars / 八字) Cookbook — Comprehensive Examples
#
# So the topic becomes the title, and the subtitle survives only if it says something
# the topic does not.
TITLE = re.compile(r"^(?P<topic>.+?)\s+Cookbook\b\s*[-–—:]?\s*(?P<subtitle>.*)$", re.I)
BOILERPLATE = re.compile(
    r"^(Comprehensive\s+)?(Examples?|Recipes?)\s+(for|of)\s+|^Comprehensive\s+Examples?\.?$",
    re.I,
)


def split_title(raw: str) -> tuple[str, str]:
    """ "Aspects & Orbs Cookbook — Comprehensive Examples" -> ("Aspects & Orbs", "")."""
    match = TITLE.match(raw.strip())
    if not match:
        return raw.strip(), ""

    topic = match.group("topic").strip()
    subtitle = BOILERPLATE.sub("", match.group("subtitle").strip()).strip(" .")

    # What is left of "Examples for Stellium Chart Drawing" is "Stellium Chart
    # Drawing" — the topic again, wearing the project's name. Drop it.
    if subtitle.lower().startswith("stellium"):
        subtitle = ""
    return topic, subtitle[:1].upper() + subtitle[1:] if subtitle else ""


# Plumbing, not recipes. Every cookbook has some.
HELPERS = {
    "main",
    "get_output_path",
    "section_header",
    "header",
    "print_header",
    "setup",
}


def recipes(path: Path) -> list[tuple[str, str]]:
    """(function name, first docstring line) for each recipe, in source order.

    Most cookbooks name their recipes `example_1_…`, but not all: planner_cookbook
    uses `basic_planner()`, `full_planner()`, and so on. Keying on the `example_`
    prefix therefore found **nothing** in that file and silently emitted a page with
    zero recipes — a generator that produces an empty page and does not say so is the
    same shape of bug as everything else we have been deleting this week.

    So the rule is structural rather than lexical: a recipe is a top-level function
    with a docstring, that is not private and not plumbing. And `main()` asserts that
    every cookbook yields at least one, so a naming convention we have not met yet
    fails the build instead of quietly emptying a page.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name.startswith("_") or node.name in HELPERS:
            continue
        doc = ast.get_docstring(node)
        if not doc:
            continue  # no docstring, no heading — it is a helper in all but name
        title = EXAMPLE_PREFIX.sub("", doc.strip().split("\n")[0]).strip()
        found.append((node.name, title.rstrip(".") or node.name.replace("_", " ")))
    return found


def page(path: Path) -> tuple[str, str, int, str]:
    """Render one cookbook page. Returns (slug, markdown, recipe count, title)."""
    slug = path.stem.removesuffix("_cookbook")
    module_doc = (
        ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    ).strip()

    lines = module_doc.split("\n")
    raw_title = lines[0].strip() if lines else slug.replace("_", " ").title()
    heading, subtitle = split_title(raw_title)

    # Keep only the prose. A cookbook's docstring also carries:
    #   * a "Usage: source ~/.zshrc && pyenv activate starlight" block — a note to
    #     us, not to a reader of the documentation; and
    #   * a hand-maintained "Contents:" list of the recipes — which the page's own
    #     headings already are, generated from the functions themselves. Reprinting
    #     it would put a second, hand-written copy of the same list on the page,
    #     free to fall out of step with the code. That is the whole failure this
    #     generator exists to avoid.
    stop = re.compile(
        r"^\s*(Usage|Run this script|For full documentation|Contents|Sections|Examples)\b[:\s]",
        re.I,
    )
    body: list[str] = []
    for line in lines[1:]:
        if stop.match(line):
            break
        body.append(line)
    intro = "\n".join(body).strip()

    found = recipes(path)
    out = [
        f"# {heading}",
        "",
    ]
    if subtitle:
        out += [f"*{subtitle}*", ""]
    out += [
        intro,
        "",
        ":::{note}",
        f"Every recipe below is read straight out of "
        f"[`examples/{path.name}`](https://github.com/katelouie/stellium/blob/main/examples/{path.name}) "
        f"at build time — the script is the source, so the page cannot drift from it. "
        f"Run the whole cookbook with `python examples/{path.name}`.",
        ":::",
        "",
    ]
    for name, title in found:
        out += [
            f"## {title}",
            "",
            f"```{{literalinclude}} ../../examples/{path.name}",
            ":pyobject: " + name,
            ":language: python",
            "```",
            "",
        ]
    return slug, "\n".join(out), len(found), heading


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--clean", action="store_true", help="delete the generated pages"
    )
    args = parser.parse_args()

    if args.clean:
        if OUT.exists():
            for f in OUT.glob("*.md"):
                f.unlink()
        print(f"cleaned {OUT.relative_to(REPO)}")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    written: list[tuple[str, str, int, str]] = []
    empty: list[str] = []
    for script in sorted(EXAMPLES.glob("*_cookbook.py")):
        slug, markdown, count, title = page(script)
        if count == 0:
            empty.append(script.name)
            continue
        (OUT / f"{slug}.md").write_text(markdown, encoding="utf-8")
        written.append((slug, script.name, count, title))

    # A cookbook with no recipes means we failed to recognise its functions, not that
    # it has none. Say so, loudly, rather than shipping an empty page.
    if empty:
        raise SystemExit(
            "no recipes found in: "
            + ", ".join(empty)
            + "\nA recipe is a top-level function with a docstring. Either these have "
            "none, or they are being mistaken for plumbing (see HELPERS)."
        )

    # An index, so the section has a landing page rather than a bare toctree.
    total = sum(c for _, _, c, _ in written)
    index = [
        "# Cookbooks",
        "",
        f"**{total} runnable recipes** across {len(written)} cookbooks. Each one is a real "
        "function in a real script in [`examples/`](https://github.com/katelouie/stellium/tree/main/examples) "
        "— run the file and every recipe on the page executes.",
        "",
        "| Cookbook | Recipes |",
        "|---|---|",
    ]
    for slug, _script, count, title in written:
        index.append(f"| [{title}]({slug}.md) | {count} |")
    index += [
        "",
        "```{toctree}",
        ":hidden:",
        ":maxdepth: 1",
        "",
    ]
    index += [slug for slug, _, _, _ in written]
    index += ["```", ""]
    (OUT / "index.md").write_text("\n".join(index), encoding="utf-8")

    for _slug, script, count, title in written:
        print(f"  {title:34} {count:3} recipes  <- {script}")
    print(f"\n  {len(written)} cookbooks, {total} recipes -> {OUT.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
