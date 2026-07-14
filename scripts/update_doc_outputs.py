#!/usr/bin/env python3
"""
Fill in the expected output of every documented code block, by running it.

    python scripts/update_doc_outputs.py                 # every doc under test
    python scripts/update_doc_outputs.py docs/REPORTS.md # just one
    python scripts/update_doc_outputs.py --check         # CI: fail if anything drifted

The point is that **a human never writes an expected output.** Documentation that
asserts its own results is documentation that can lie, and ours did: the astrology
guide claimed William Lilly's Venus scored `+7` with `['domicile', 'term']`. It
scores `+10` with `['domicile', 'triplicity_ruler', 'term']`, and always did. Nobody
ran it. A reader has no way to know.

So the library writes the answer and the author writes only the question. If a doc's
numbers move, that shows up as a diff here, which is exactly when you want to look:
either the doc was wrong, or the library's behaviour just changed under you.

The output goes in pytest-codeblocks' own convention, so `tests/test_doc_codeblocks.py`
gets it parsed for free:

    ```python
    print(chart.get_strongest_planet())
    ```
    <!--pytest-codeblocks:expected-output-->
    ```
    ('Venus', 10)
    ```

Blocks whose output legitimately changes run to run (anything reading the clock)
carry `<!--doc-output:volatile-->` and are executed but left alone.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))

from test_doc_codeblocks import (  # noqa: E402
    CONSOLE_WIDTH,
    doc_files,
    testable_blocks,
    volatile_linenos,
)

MARKER = "<!--pytest-codeblocks:expected-output-->"

# An expected-output fence sitting immediately after a block: our marker, then a
# plain ``` block. Anchored to the start of the remaining text so we can only ever
# replace the fence belonging to the block we just ran.
EXISTING_AT_START = re.compile(r"^\n" + re.escape(MARKER) + r"\n```\n.*?\n?```\n", re.S)


def run(code: str) -> str | None:
    """Execute a block and return what it printed. None if it cannot be run here.

    In a scratch directory, matching what the test does — plenty of documented blocks
    save an SVG or a PDF, and running them from the repo root would strew the output
    of the documentation across the working tree.
    """
    stdout = io.StringIO()
    cwd = os.getcwd()
    previous_columns = os.environ.get("COLUMNS")
    os.environ["COLUMNS"] = CONSOLE_WIDTH  # see the constant: rich sizes tables to this
    with tempfile.TemporaryDirectory() as scratch:
        try:
            os.chdir(scratch)
            with contextlib.redirect_stdout(stdout):
                exec(compile(code, "<doc>", "exec"), {"__name__": "__main__"})
        except NameError:
            return None  # a fragment continuing an earlier block
        except (ImportError, ModuleNotFoundError, FileNotFoundError):
            return None
        finally:
            os.chdir(cwd)
            if previous_columns is None:
                os.environ.pop("COLUMNS", None)
            else:
                os.environ["COLUMNS"] = previous_columns
    return stdout.getvalue().rstrip("\n")


def block_end(lines: list[str], start: int) -> int:
    """Index of the line after the closing ``` of the block opening at `start`."""
    i = start + 1
    while i < len(lines) and not lines[i].startswith("```"):
        i += 1
    return i + 1


def strip_fence(rest: list[str]) -> list[str]:
    """Remove an expected-output fence sitting at the head of `rest`, if any."""
    i = 0
    while i < len(rest) and not rest[i].strip():
        i += 1
    if i >= len(rest) or rest[i].strip() != MARKER:
        return rest
    i += 1
    if i >= len(rest) or not rest[i].startswith("```"):
        return rest
    i += 1
    while i < len(rest) and not rest[i].startswith("```"):
        i += 1
    return rest[i + 1 :]


def update(doc: Path, check: bool) -> tuple[int, int]:
    """Rewrite one doc's expected-output fences. Returns (changed, skipped)."""
    rel = doc.relative_to(REPO).as_posix()
    text = doc.read_text()
    changed = skipped = 0

    volatile = volatile_linenos(rel)
    for block in reversed(testable_blocks(rel)):  # reversed: edits don't shift earlier
        if block.lineno in volatile:
            continue

        output = run(block.code)
        if output is None:
            skipped += 1
            continue

        lines = text.split("\n")
        # block.lineno is 1-based and points at the ``` fence opening the block.
        after = block_end(lines, block.lineno - 1)
        head, rest = lines[:after], lines[after:]

        # Drop the fence already sitting there, so we *replace* rather than stack a
        # second one under the first. Working in lines rather than on the joined text,
        # because joining loses the separator and an anchored regex then never matches
        # — which is exactly how the first version came to emit two fences per block.
        rest = strip_fence(rest)

        fence = [MARKER, "```", *output.split("\n"), "```"] if output else []
        new = "\n".join(head + fence + rest)

        if new != text:
            changed += 1
        text = new

    if changed and not check:
        doc.write_text(text if text.endswith("\n") else text + "\n")
    return changed, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="docs to update (default: all)")
    parser.add_argument(
        "--check", action="store_true", help="report drift, write nothing (for CI)"
    )
    args = parser.parse_args()

    targets = args.files or doc_files()
    total_changed = total_skipped = 0
    for name in targets:
        doc = REPO / name
        if not doc.exists():
            sys.exit(f"no such doc: {name}")
        changed, skipped = update(doc, args.check)
        total_changed += changed
        total_skipped += skipped
        if changed:
            verb = "would update" if args.check else "updated"
            print(f"  {verb} {changed:2d} block(s) in {name}")

    print(
        f"\n{total_changed} block(s) {'drifted' if args.check else 'updated'}, "
        f"{total_skipped} not runnable standalone"
    )
    if args.check and total_changed:
        sys.exit(
            "documentation output is out of date — run scripts/update_doc_outputs.py"
        )


if __name__ == "__main__":
    main()
