"""Do the code blocks in our documentation run — and do they print what they claim?

Two different questions, and for a long time we only asked the first one.

**Does it run?** Catches ghost methods, renamed imports, changed signatures. This
test has done that since it was written.

**Does it print what the doc says it prints?** It did not check this at all. The
block was `exec`'d and its stdout thrown away, so a doc could assert any output it
liked and stay green forever. That is not hypothetical: the astrology guide claimed
William Lilly's Moon held triplicity in Virgo at `+3` and Venus scored `+7`. The
engine says Moon is `+0 peregrine` and Venus is `+10` — and it always did, because
Lilly has no birth time in the notables database, so his chart is a *noon*
`UnknownTimeChart`, which is unambiguously a **day** chart, whose Earth triplicity
ruler is Venus. The documented numbers require a *night* chart. They could never
have come from running the code. They were written to look right.

A reader cannot tell the difference. That is what makes a wrong output in a doc
worse than a wrong output in a test: the test has no audience.

So: any block may carry its expected output, and if it does, the output must match
**exactly**.

    ```python
    print(chart.get_strongest_planet())
    ```
    <!--pytest-codeblocks:expected-output-->
    ```
    ('Venus', 10)
    ```

You never write that block by hand — and that is the whole point. Run

    python scripts/update_doc_outputs.py

and the *library* fills it in. An author cannot fabricate an output they do not
author. If a library change alters a number, CI fails in the document that lied.

A block whose output is genuinely nondeterministic (anything keyed to "now") marks
itself `<!--doc-output:volatile-->` and is run but not compared. Say so out loud;
do not just leave the output unasserted and hope.

Marked slow: runs in CI and the full suite, not in the TDD loop.
"""

import contextlib
import io
import re
import warnings
from pathlib import Path

import pytest
from pytest_codeblocks import extract_from_file

pytestmark = [pytest.mark.slow, pytest.mark.docs]

REPO_ROOT = Path(__file__).parent.parent

DOC_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    # The four landing pages. The home page is the most-read page in the project and
    # its code was, until now, the only code on the site that nothing ran.
    "docs/index.md",
    "docs/README.md",
    "docs/for-developers.md",
    "docs/for-astrologers.md",
    "docs/api/exceptions.md",
    "docs/options_list.md",
    "docs/REPORTS.md",
    "docs/VISUALIZATION.md",
    "docs/PALETTE_GALLERY.md",
    "docs/THEME_GALLERY.md",
    # docs/ARCHITECTURE.md excluded — significantly stale (Nov 2025), has a warning banner
    "examples/README.md",
    "docs/images/README.md",
    "CLAUDE.md",
]

# The astrology guide is written chapter by chapter, so discover it rather than
# maintain a list that a new chapter can silently fall off.
GUIDE_GLOB = "docs/astrology/**/*.md"

# A block that says this is run but not output-compared: its output legitimately
# changes run to run (it reads the clock, or a transit for "today").
VOLATILE = "doc-output:volatile"

# `rich` sizes its tables to the terminal, reading COLUMNS — so the *same* report
# renders with different borders in your shell, under pytest, and in CI. That is not
# nondeterminism, but for a pinned snapshot it is just as fatal, so both the test and
# scripts/update_doc_outputs.py fix the width to the same value and neither inherits
# whatever the environment happened to have.
CONSOLE_WIDTH = "100"


def doc_files() -> list[str]:
    """Every documentation file under test, guide chapters included."""
    files = [f for f in DOC_FILES if (REPO_ROOT / f).exists()]
    files += sorted(str(p.relative_to(REPO_ROOT)) for p in REPO_ROOT.glob(GUIDE_GLOB))
    return files


def testable_blocks(doc_file: str):
    """The Python blocks in one doc that are self-contained enough to execute."""
    blocks = list(extract_from_file(str(REPO_ROOT / doc_file)))
    return [
        b
        for b in blocks
        if b.syntax == "python"
        and "from stellium" in b.code  # self-contained: brings its own imports
        and "pytest.mark.skip" not in (b.marks or [])
    ]


def volatile_linenos(doc_file: str) -> set[int]:
    """Line numbers of the ``` fences of blocks marked `<!--doc-output:volatile-->`.

    pytest-codeblocks only parses its own `<!--pytest.mark.*-->` comments, so our
    marker never reaches `block.marks` and has to be found here. The block still
    *runs* — it must not crash — it is only exempt from having its output pinned.
    """
    lines = (REPO_ROOT / doc_file).read_text(encoding="utf-8").split("\n")
    marked: set[int] = set()
    for i, line in enumerate(lines):
        if line.strip() != f"<!--{VOLATILE}-->":
            continue
        for j in range(i + 1, len(lines)):
            if lines[j].startswith("```"):
                marked.add(j + 1)  # block.lineno is 1-based, and points at the fence
                break
    return marked


def _collect():
    params = []
    for doc_file in doc_files():
        for i, block in enumerate(testable_blocks(doc_file)):
            first_line = block.code.strip().split("\n")[0][:50]
            params.append(
                pytest.param(block, doc_file, id=f"{doc_file}:block{i} ({first_line})")
            )
    return params


@pytest.mark.parametrize("block,doc_file", _collect())
def test_doc_codeblock(block, doc_file, tmp_path, monkeypatch):
    """Execute a documented block, and hold it to the output it advertises."""
    monkeypatch.chdir(tmp_path)  # so a block that writes a file cannot litter the repo
    monkeypatch.setenv("COLUMNS", CONSOLE_WIDTH)

    stdout = io.StringIO()
    try:
        # `warnings.catch_warnings()` restores the global filter list afterwards.
        # A documented block is entitled to show `simplefilter("error", ...)` — that
        # is exactly how you are meant to escalate a StelliumWarning — but without
        # this, that one line would silently re-arm every block that ran after it,
        # in a different file, and the failure would surface nowhere near its cause.
        with warnings.catch_warnings(), contextlib.redirect_stdout(stdout):
            exec(compile(block.code, doc_file, "exec"), {"__name__": "__main__"})
    except NameError as e:
        # A fragment that continues an earlier block (`chart` defined above, etc.).
        pytest.skip(f"Fragment (undefined name): {e}")
    except FileNotFoundError:
        pytest.skip("File output path not available in test environment")
    except (ImportError, ModuleNotFoundError) as e:
        pytest.skip(f"Optional dependency missing: {e}")

    if block.expected_output is None:
        return  # no claim made, nothing to hold it to — it just has to run
    if block.lineno in volatile_linenos(doc_file):
        return

    actual = stdout.getvalue().rstrip("\n")
    expected = block.expected_output.rstrip("\n")
    assert actual == expected, (
        f"{doc_file} documents output it does not produce.\n\n"
        f"--- documented ---\n{expected}\n\n"
        f"--- actual ---\n{actual}\n\n"
        f"Do not hand-edit the expected output. Run:\n"
        f"    python scripts/update_doc_outputs.py {doc_file}\n"
        f"and read the diff — if a number moved, either the doc was wrong or the "
        f"library just changed behaviour, and both are worth knowing."
    )


# A float printed at full repr — 0.6048940312763954 — is not the same string on every
# machine: the last bits differ between x86 and arm, and a pinned output that carries
# them fails on the platform it was not generated on. The difference is ~1e-12°, a
# million times finer than Swiss Ephemeris resolves, so the value is not wrong — the
# expectation is too precise. Round at the print.
LONG_FLOAT = re.compile(r"\d+\.\d{7,}")


def test_no_pinned_output_depends_on_floating_point_noise():
    """No expected output may carry a float with more than 6 decimals."""
    offenders = []
    for doc_file in doc_files():
        for block in testable_blocks(doc_file):
            for value in LONG_FLOAT.findall(block.expected_output or ""):
                offenders.append(f"{doc_file}: {value}")

    assert not offenders, (
        "These pinned outputs print a float at a precision that is not reproducible "
        "across platforms:\n  " + "\n  ".join(offenders) + "\n\n"
        'Round it where it is printed — f"{value:.4f}" — then re-run '
        "`python scripts/update_doc_outputs.py <file>`."
    )


def test_every_doc_that_prints_is_held_to_its_output():
    """A block that prints but asserts nothing is a claim nobody is checking.

    This is the rule that would have caught the guide. It is a *warning* list rather
    than a hard failure, because plenty of legitimate blocks print a chart wheel's
    filename or a progress line that no one needs pinned — but the list should be
    short and deliberate, never a place things quietly accumulate.
    """
    unasserted = []
    for doc_file in doc_files():
        for block in testable_blocks(doc_file):
            if "print(" in block.code and block.expected_output is None:
                if block.lineno in volatile_linenos(doc_file):
                    continue
                unasserted.append(f"{doc_file}:{block.lineno}")

    # Not zero — see the docstring. But it must not grow silently.
    assert len(unasserted) <= 40, (
        f"{len(unasserted)} documented blocks print output that nothing verifies. "
        f"Run `python scripts/update_doc_outputs.py` to pin them:\n  "
        + "\n  ".join(unasserted[:20])
    )
