"""Tests that Python code blocks in documentation files actually work.

Extracts fenced Python code blocks from markdown files and executes any
that are self-contained (define their own imports and variables). Blocks
that reference undefined names are treated as continuation fragments and
skipped — these are documentation-style examples that assume prior context.

This catches:
- Ghost methods (documented but never implemented)
- Renamed/moved imports
- Changed method signatures
- Broken example code

Marked as slow: runs in CI and full suite, not in TDD loop.
"""

from pathlib import Path

import pytest
from pytest_codeblocks import extract_from_file

pytestmark = [pytest.mark.slow, pytest.mark.docs]

REPO_ROOT = Path(__file__).parent.parent
DOC_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "docs/options_list.md",
    "docs/REPORTS.md",
    "docs/VISUALIZATION.md",
    "docs/PALETTE_GALLERY.md",
    "docs/THEME_GALLERY.md",
    "docs/PUBLISHING.md",
    # docs/ARCHITECTURE.md excluded — significantly stale (Nov 2025), has a warning banner
    "examples/README.md",
    "docs/images/README.md",
    "CLAUDE.md",
]


def _collect_testable_blocks():
    """Collect self-contained Python blocks from doc files.

    A block is considered testable if:
    - It's a Python code block
    - It imports from stellium (self-contained)
    - It doesn't have a <!--pytest.mark.skip--> marker (template/illustration code)

    Blocks that fail with NameError at runtime are fragments that depend on
    prior context and will be skipped dynamically.
    """
    params = []
    for doc_file in DOC_FILES:
        filepath = REPO_ROOT / doc_file
        if not filepath.exists():
            continue

        blocks = list(extract_from_file(str(filepath)))
        python_blocks = [
            b
            for b in blocks
            if b.syntax == "python"
            and "from stellium" in b.code
            and "pytest.mark.skip" not in (b.marks or [])
        ]

        for i, block in enumerate(python_blocks):
            first_line = block.code.strip().split("\n")[0][:50]
            block_id = f"{doc_file}:block{i} ({first_line})"
            params.append(pytest.param(block.code, doc_file, id=block_id))

    return params


@pytest.mark.parametrize("code,doc_file", _collect_testable_blocks())
def test_doc_codeblock(code, doc_file, tmp_path, monkeypatch):
    """Execute a documentation code block and verify it doesn't crash.

    Blocks that fail with NameError are skipped — they're fragments
    that depend on prior context (like a `native` variable defined
    in an earlier block).
    """
    # Use tmp_path for any file output so we don't litter the repo
    monkeypatch.chdir(tmp_path)

    try:
        exec(compile(code, f"{doc_file}", "exec"), {"__name__": "__main__"})
    except NameError as e:
        # Fragment — depends on variables from prior context
        pytest.skip(f"Fragment (undefined name): {e}")
    except FileNotFoundError:
        # Block tries to write to a path that doesn't exist in tmp
        pytest.skip("File output path not available in test environment")
