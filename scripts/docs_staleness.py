#!/usr/bin/env python3
"""Nag — gently, and never fatally — when the docs have drifted behind the code.

    python scripts/docs_staleness.py

Runs from a **post-commit** hook, so it cannot block a commit, cannot fail a push, and
cannot make anyone's day worse. It prints, or it says nothing.

The site is not just prose: it executes 421 cookbook recipes, a notebook, and every
pinned doc block. So "the docs still build" is a real assertion about the library, and
it is the kind that goes quietly false — a renamed method breaks a recipe, and nobody
finds out until Read the Docs turns red on a Sunday.

**There is no stamp file.** The build *is* the stamp: `docs/_build/html/index.html`
carries the moment the site last built on this machine. That is deliberate — a
timestamp we maintain ourselves is one more thing that can lie about the thing it
describes, which is the failure this whole file exists to catch.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILT = REPO / "docs" / "_build" / "html" / "index.html"

# Only what the docs actually read. A commit to .github/ or CHANGELOG.md cannot
# invalidate a cookbook page, and nagging about it would train you to ignore the nag.
WATCHED = ["src", "docs", "examples", "README.md", "CLAUDE.md"]

# Thresholds. Deliberately loose: a reminder you see every day is noise, and noise is
# how a real warning gets scrolled past.
MAX_COMMITS = 10
MAX_DAYS = 7

BUILD_CMD = "source ~/.zshrc && pyenv activate starlight && python -m sphinx -b html docs docs/_build/html"

BOLD, DIM, GOLD, ACCENT, RESET = "\033[1m", "\033[2m", "\033[33m", "\033[35m", "\033[0m"


def supports_colour() -> bool:
    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb"


def paint(text: str, *codes: str) -> str:
    return f"{''.join(codes)}{text}{RESET}" if supports_colour() else text


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
    ).stdout.strip()


def main() -> int:
    if not BUILT.exists():
        say(
            "The docs have never been built in this checkout.",
            "Worth doing once — the build executes every cookbook recipe, so it is "
            "the fastest check that the examples still match the library.",
        )
        return 0

    built_at = BUILT.stat().st_mtime
    commits = git(
        "rev-list", "--count", f"--since=@{int(built_at)}", "HEAD", "--", *WATCHED
    )
    n = int(commits) if commits.isdigit() else 0

    now = subprocess.run(["date", "+%s"], capture_output=True, text=True).stdout.strip()
    days = (int(now) - int(built_at)) / 86400 if now.isdigit() else 0

    if n < MAX_COMMITS and days < MAX_DAYS:
        return 0

    parts = []
    if n:
        parts.append(f"{n} commit{'s' if n != 1 else ''}")
    if days >= 1:
        parts.append(f"{int(days)} day{'s' if int(days) != 1 else ''}")
    since = " and ".join(parts) if parts else "a while"

    say(
        f"It has been {since} since the docs were last built.",
        "The build runs every cookbook recipe and every pinned example, so it is a "
        "real check on the library — not just on the prose.",
    )
    return 0


def say(headline: str, why: str) -> None:
    print()
    print(paint("  ☿  docs", BOLD, ACCENT), paint(f"— {headline}", BOLD))
    print(paint(f"     {why}", DIM))
    print()
    print(paint(f"     {BUILD_CMD}", GOLD))
    print(paint("     (never blocking — this is a reminder, not a gate)", DIM))
    print()


if __name__ == "__main__":
    sys.exit(main())
