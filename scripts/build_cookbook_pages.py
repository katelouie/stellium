#!/usr/bin/env python3
"""
Generate a documentation page for every cookbook in `examples/`.

    python scripts/build_cookbook_pages.py          # write docs/cookbooks/*.md
    python scripts/build_cookbook_pages.py --clean  # remove them

`docs/conf.py` calls this on `builder-inited`, so the pages are rebuilt from the
scripts on every Sphinx build — including on Read the Docs. Nothing is committed,
so nothing can go stale: **there is no copy of the code to drift.**

That matters here more than usual. There are 21 cookbooks holding **357 runnable
recipes**, and not one of them appeared anywhere in the documentation site. Hand-
copying that into Markdown would have created 357 code blocks with no connection to
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


def recipes(path: Path) -> list[tuple[str, str]]:
    """(function name, first docstring line) for each recipe, in source order."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("example"):
            continue
        doc = ast.get_docstring(node) or ""
        title = EXAMPLE_PREFIX.sub("", doc.strip().split("\n")[0]).strip()
        found.append((node.name, title or node.name.replace("_", " ")))
    return found


def page(path: Path) -> tuple[str, str, int]:
    """Render one cookbook page. Returns (slug, markdown, recipe count)."""
    slug = path.stem.removesuffix("_cookbook")
    module_doc = (
        ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    ).strip()

    lines = module_doc.split("\n")
    heading = lines[0].strip() if lines else slug.title()

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
    return slug, "\n".join(out), len(found)


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
    written: list[tuple[str, str, int]] = []
    for script in sorted(EXAMPLES.glob("*_cookbook.py")):
        slug, markdown, count = page(script)
        (OUT / f"{slug}.md").write_text(markdown, encoding="utf-8")
        written.append((slug, script.name, count))

    # An index, so the section has a landing page rather than a bare toctree.
    total = sum(c for _, _, c in written)
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
    for slug, _script, count in written:
        title = slug.replace("_", " ").title()
        index.append(f"| [{title}]({slug}.md) | {count} |")
    index += [
        "",
        "```{toctree}",
        ":hidden:",
        ":maxdepth: 1",
        "",
    ]
    index += [slug for slug, _, _ in written]
    index += ["```", ""]
    (OUT / "index.md").write_text("\n".join(index), encoding="utf-8")

    for slug, script, count in written:
        print(f"  {slug:22} {count:3} recipes  <- {script}")
    print(f"\n  {len(written)} cookbooks, {total} recipes -> {OUT.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
