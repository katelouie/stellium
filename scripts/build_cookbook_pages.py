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

So the pages do not contain code. They `literalinclude` it by line range, so Sphinx
reads it out of the real script at build time and there is nothing to keep in sync.

A recipe's docstring is doing three jobs at once — titling it, explaining it, and
sitting inside the code — and the function is wrapped in terminal plumbing. Both come
apart:

    docstring line 1  -> the page heading
    docstring rest    -> prose, as Markdown, ABOVE the code
    docstring itself  -> sliced OUT of the code (it is now both of the above)
    section_header()  -> sliced out too: a banner announcing the example, on a page
                         whose heading already announces it
    def / indentation -> dedented away, so the snippet is code you can paste

What is left is the code, and only the code.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import os
import re
import shutil
import tempfile
import textwrap
import warnings
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXAMPLES = REPO / "examples"
OUT = REPO / "docs" / "cookbooks"

# Set STELLIUM_DOCS_FAST=1 to skip execution while iterating on the theme locally.
# CI and Read the Docs never set it: there, the outputs are always computed.
FAST = os.environ.get("STELLIUM_DOCS_FAST") == "1"

# The planner renders real PDFs through Typst: 11 recipes, 104 seconds — as much as
# the other 356 combined, four times over. Its output is a file path, not a table, so
# there is nothing on the page to gain by paying for it.
SKIP_EXECUTION = {"planner"}

# Output long enough to bury the next recipe. Keep the head, say what was cut.
MAX_OUTPUT_LINES = 40

# Where a recipe's rendered charts go. Generated, gitignored, rebuilt every build.
IMAGES = OUT / "images"

# Every cookbook resolves its output directory from __file__, not from the working
# directory:
#
#     SCRIPT_DIR = Path(__file__).resolve().parent
#     OUTPUT_DIR = SCRIPT_DIR / "charts"
#
# which means chdir'ing to a scratch directory does NOTHING to contain them — the
# first build-time run wrote straight into examples/charts/, examples/reports/ and
# examples/dials/, MODIFYING FILES THAT ARE COMMITTED. So the constant is rebound in
# the module namespace after import, which both contains the writes and puts the
# charts somewhere we can find them.
OUTPUT_DIR_NAME = "OUTPUT_DIR"

# What we can actually show on a page. A PDF is a download, not a figure.
RENDERABLE = {".svg", ".png"}

# "Example 1: Solar Arc Directions by Age" -> "Solar Arc Directions by Age".
# The number is already the heading's position on the page; repeating it is noise.
EXAMPLE_PREFIX = re.compile(r"^Example\s+\d+\s*[:.\-–]\s*", re.I)

# A rule underlining the docstring's title: ----- or ===== or ~~~~~.
RULE = re.compile(r"^[-=~_]{3,}\s*$", re.M)

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


# Plumbing, not recipes. Every cookbook has some, and several of them carry a
# docstring, so "has a docstring" is not enough to tell them apart from content.
HELPERS = {"main", "get_output_path", "setup"}


def is_plumbing(name: str) -> bool:
    """A helper, whatever it calls itself.

    `print_results`, `print_windows`, `subsection_header` all have docstrings and were
    being rendered as recipes.
    """
    return (
        name in HELPERS
        or name.startswith(("_", "print_"))
        or name.endswith(("_header", "_headers"))
    )


# The banner a recipe prints when the cookbook is run in a terminal. It exists to tell
# you which example you are looking at — which, on a page whose heading already says
# so, is the same sentence twice:
#
#     ## Solar Arc Directions to a Specific Date
#     ```python
#     section_header("Example 2: Solar Arc Directions to a Specific Date")   # <- this
#     ...
BANNER_CALLS = {"section_header", "print_header", "subsection_header", "header"}


def is_banner(node: ast.stmt) -> bool:
    """Is this statement pure terminal decoration?

    Either a call to one of the banner helpers, or a `print()` whose arguments are
    *entirely literal* — `print("\n" + "=" * 60)`, `print("EXAMPLE 1: SYNASTRY")`.

    The literal test is what keeps this honest: `print(f"Found {len(results)} results")`
    contains a Name and a Call, so it is real output and survives. Decoration is,
    definitionally, the stuff that does not look at the data.
    """
    if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
        return False
    func = node.value.func
    name = getattr(func, "id", None)
    if name in BANNER_CALLS:
        return True
    if name != "print":
        return False
    return not any(
        isinstance(child, ast.Name | ast.Attribute | ast.Call)
        for arg in node.value.args
        for child in ast.walk(arg)
    )


@dataclass(frozen=True)
class Recipe:
    """One recipe, taken apart into the three things a page wants from it."""

    name: str
    title: str  # the docstring's first line -> the page heading
    prose: str  # the rest of the docstring -> prose *above* the code
    first_line: int  # first line of the body AFTER the docstring
    last_line: int  # last line of the function


def recipes(path: Path) -> list[Recipe]:
    """Take each recipe apart: heading, prose, and the code without its docstring.

    A recipe's docstring is already doing three jobs — titling it, explaining it, and
    sitting inside the code. Rendered naively that means the title is printed twice
    (once as the page heading, once inside the snippet) and the explanation is trapped
    in a code block where it cannot be a paragraph, a list, or a link.

    So the docstring is *lifted out*: line one becomes the heading, the rest becomes
    prose above the code, and the code block is sliced to start after the docstring
    ends. The reader gets an explanation they can read and a snippet they can copy.

    On recognising a recipe at all: most cookbooks name theirs `example_1_…`, but not
    all — planner_cookbook uses `basic_planner()`, `full_planner()`. Keying on the
    `example_` prefix found **nothing** there and silently produced an empty page, so
    the rule is structural instead: a top-level function with a docstring, neither
    private nor plumbing. `main()` fails the build on a cookbook with zero recipes,
    because that means a convention we have not met, not a cookbook with no content.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[Recipe] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if is_plumbing(node.name):
            continue
        doc = ast.get_docstring(node)
        if not doc:
            continue  # no docstring, no heading — plumbing in all but name

        lines = doc.strip().split("\n")
        title = EXAMPLE_PREFIX.sub("", lines[0]).strip().rstrip(".")
        prose = textwrap.dedent("\n".join(lines[1:])).strip()

        # Some docstrings underline their title with a rule:
        #
        #     Example 1: Simplest Search with Lambda Conditions
        #     -------------------------------------------------
        #     The most basic way to use ElectionalSearch is...
        #
        # Lifted out, that rule becomes the FIRST thing in the section — which docutils
        # reads as a transition, and a section may not begin with one (43 build errors,
        # every one of them from a page this script generated). The title is a heading
        # now; it does not need underlining.
        prose = RULE.sub("", prose, count=1).strip()

        # Skip the docstring AND the banner statements that follow it, so the code
        # block starts at the first line that actually does something.
        body = node.body[1:]
        while body and is_banner(body[0]):
            body = body[1:]
        if not body:
            continue  # a docstring and a banner is not a recipe

        found.append(
            Recipe(
                name=node.name,
                title=title or node.name.replace("_", " "),
                prose=prose,
                first_line=body[0].lineno,
                last_line=node.end_lineno,
            )
        )
    return found


def run_recipes(
    path: Path, plan: list[Recipe]
) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Execute a cookbook and capture what each recipe prints.

    The library writes the answers; nobody hand-copies them. This is the same contract
    as scripts/update_doc_outputs.py — an author writes the question, the code writes
    the result — and it is the reason the documentation can be trusted at all.

    Each cookbook is exec'd once (for its imports and module-level setup), then each
    recipe is called and its stdout captured. It all happens in a scratch directory,
    because plenty of recipes save an SVG or a PDF and the repository is not the place
    for them.
    """
    if FAST or path.stem.removesuffix("_cookbook") in SKIP_EXECUTION:
        return {}, {}

    namespace: dict = {"__name__": "__cookbook__", "__file__": str(path)}
    captured: dict[str, str] = {}
    figures: dict[str, list[str]] = {}
    cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as scratch, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            os.chdir(scratch)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(
                    compile(path.read_text(encoding="utf-8"), str(path), "exec"),
                    namespace,
                )

            # Silence the banner helpers before calling anything. They print
            #     ========================================
            #       Example 1: Least (Minor) Years
            #     ========================================
            # which is how a cookbook tells you where you are as it scrolls past in a
            # terminal. On a page whose heading already says it, that is the same
            # sentence a third time — and since the call has been stripped from the
            # displayed code, the output would be announcing a line nobody can see.
            for helper in BANNER_CALLS:
                if callable(namespace.get(helper)):
                    namespace[helper] = lambda *args, **kwargs: None

            # Contain the writes. See OUTPUT_DIR_NAME above: without this, a recipe
            # saves its chart into examples/charts/ — inside the repository.
            drawn_into = Path(scratch) / "drawn"
            drawn_into.mkdir()
            # Remember where the recipe *would* have written, so the captured output
            # can say "examples/charts/01_simplest.svg" rather than leaking
            # /var/folders/…/T/tmpqmmfj3dx/drawn/ at the reader.
            declared = namespace.get(OUTPUT_DIR_NAME)
            real_output_dir = (
                Path(declared).relative_to(REPO).as_posix()
                if isinstance(declared, Path) and declared.is_relative_to(REPO)
                else "examples/output"
            )
            if OUTPUT_DIR_NAME in namespace:
                namespace[OUTPUT_DIR_NAME] = drawn_into

            slug = path.stem.removesuffix("_cookbook")
            for recipe in plan:
                function = namespace.get(recipe.name)
                if not callable(function):
                    continue

                before = {f for f in drawn_into.rglob("*") if f.is_file()}
                buffer = io.StringIO()
                try:
                    with contextlib.redirect_stdout(buffer):
                        function()
                except Exception as exc:
                    raise SystemExit(
                        f"{path.name}::{recipe.name} raised {type(exc).__name__}: {exc}\n"
                        f"A cookbook recipe that does not run is a recipe the docs "
                        f"should not be showing."
                    ) from exc

                text = (
                    buffer.getvalue()
                    .strip("\n")
                    .replace(str(drawn_into), real_output_dir)
                )
                if text.strip():
                    captured[recipe.name] = text

                # Whatever it drew, put it on the page next to the code that drew it.
                new = sorted(
                    f
                    for f in drawn_into.rglob("*")
                    if f.is_file()
                    and f not in before
                    and f.suffix.lower() in RENDERABLE
                )
                for index, source in enumerate(new):
                    target_dir = IMAGES / slug
                    target_dir.mkdir(parents=True, exist_ok=True)
                    suffix = f"_{index}" if len(new) > 1 else ""
                    target = (
                        target_dir / f"{recipe.name}{suffix}{source.suffix.lower()}"
                    )
                    shutil.copy2(source, target)
                    figures.setdefault(recipe.name, []).append(
                        f"images/{slug}/{target.name}"
                    )
        finally:
            os.chdir(cwd)
    return captured, figures


def output_block(text: str) -> list[str]:
    """Render captured stdout, truncated if it would swamp the page."""
    lines = text.split("\n")
    if len(lines) > MAX_OUTPUT_LINES:
        cut = len(lines) - MAX_OUTPUT_LINES
        lines = lines[:MAX_OUTPUT_LINES] + [
            "",
            f"… {cut} more lines — run the recipe to see them",
        ]
    return ["```{code-block} text", ":caption: Output", "", *lines, "```", ""]


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
    outputs, figures = run_recipes(path, found)

    for recipe in found:
        out += [f"## {recipe.title}", ""]
        if recipe.prose:
            out += [recipe.prose, ""]
        out += [
            # :lines: skips the docstring, which is already the heading and the prose
            # above. :dedent: unwraps the function body so the snippet is code you can
            # paste, not code you have to unindent first. It is still a literalinclude,
            # so Sphinx reads it out of the real script at build time.
            f"```{{literalinclude}} ../../examples/{path.name}",
            f":lines: {recipe.first_line}-{recipe.last_line}",
            ":dedent:",  # bare = strip the COMMON indent. ":dedent: 4" strips exactly
            #                4 chars, which mangles a recipe holding a triple-quoted
            #                string whose content starts at column 0 (io_cookbook).
            ":language: python",
            "```",
            "",
        ]
        # What it actually prints, captured by running it — never transcribed.
        if recipe.name in outputs:
            out += output_block(outputs[recipe.name])
        # And what it actually draws.
        for image in figures.get(recipe.name, []):
            out += [
                f"```{{figure}} {image}",
                ":class: cookbook-figure",
                "",
                "Rendered by the code above.",
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

    # The analysis cookbook is a *notebook*, stored as MyST Markdown rather than
    # .ipynb: it reads as a document on GitHub, diffs as plain text, and carries no
    # stored outputs to go stale — it used to ship 52 of them, and they were wrong
    # ("Calculated 146 charts" from a registry that now holds 211). myst-nb executes it
    # at build time (conf.py, nb_execution_mode="force"), so its DataFrames are
    # computed for the exact commit being rendered.
    notebook = EXAMPLES / "analysis_cookbook.md"
    notebook_cells = 0
    if notebook.exists():
        text = notebook.read_text(encoding="utf-8")
        shutil.copy2(notebook, OUT / "analysis.md")
        notebook_cells = text.count("```{code-cell}")

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
    total = sum(c for _, _, c, _ in written) + notebook_cells
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
    if notebook_cells:
        index.append(
            f"| [Analysis & DataFrames](analysis.md) — *executed notebook* | {notebook_cells} |"
        )
    index += [
        "",
        "```{toctree}",
        ":hidden:",
        ":maxdepth: 1",
        "",
    ]
    index += [slug for slug, _, _, _ in written]
    if notebook_cells:
        index.append("analysis")
    index += ["```", ""]
    (OUT / "index.md").write_text("\n".join(index), encoding="utf-8")

    for _slug, script, count, title in written:
        print(f"  {title:34} {count:3} recipes  <- {script}")
    if notebook_cells:
        print(
            f"  {'Analysis & DataFrames':34} {notebook_cells:3} cells    <- analysis_cookbook.md (executed by myst-nb)"
        )
    print(
        f"\n  {len(written) + bool(notebook_cells)} cookbooks, {total} recipes -> {OUT.relative_to(REPO)}/"
    )


if __name__ == "__main__":
    main()
