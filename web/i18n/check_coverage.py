#!/usr/bin/env python3
"""Translation coverage checker for the Stellium web app.

Extracts every ``_("...")`` translator call from the web/ source tree (via the
AST, so implicit string concatenation and escaping are handled correctly) and
checks each string against every locale file in web/i18n/. Reports:

  * MISSING  -- strings used in code but absent from a locale (would fall back
                to English at runtime). Fails CI.
  * ORPHANED -- keys present in a locale but no longer used in code (warning
                only; helps prune stale translations).

Run:  python web/i18n/check_coverage.py
Exit code is non-zero if any locale has missing keys.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent
I18N_DIR = Path(__file__).resolve().parent

# Files/dirs that never contain UI strings to translate.
# Test files legitimately contain _() fixture strings that aren't app UI
# (e.g. asserting graceful fallback for an untranslated key), so they must
# not count toward translation coverage.
SKIP_DIRS = {"i18n", "tests", "__pycache__", ".venv", "node_modules"}


def extract_used_strings(py_file: Path) -> set[str]:
    """Return all literal strings passed to a single-arg ``_()`` call."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError as exc:  # pragma: no cover - surfaced to the user
        print(f"  ! syntax error parsing {py_file}: {exc}", file=sys.stderr)
        return set()

    used: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_"
            and len(node.args) == 1
            and not node.keywords
        ):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                used.add(arg.value)
    return used


def collect_used_strings() -> set[str]:
    used: set[str] = set()
    for py_file in WEB_DIR.rglob("*.py"):
        if any(part in SKIP_DIRS for part in py_file.relative_to(WEB_DIR).parts):
            continue
        used |= extract_used_strings(py_file)
    return used


def flatten_locale(path: Path) -> dict[str, str]:
    """Flatten a locale JSON the same way the runtime translator does."""
    data = json.loads(path.read_text(encoding="utf-8"))
    flat: dict[str, str] = {}

    def walk(d: dict) -> None:
        for key, value in d.items():
            if isinstance(value, str):
                flat[key] = value
            elif isinstance(value, dict):
                walk(value)
            # lists (e.g. home "features") are handled via wt_list, not flatten

    for key, value in data.items():
        if key in ("metadata", "excluded_categories"):
            continue
        if isinstance(value, dict):
            walk(value)
        elif isinstance(value, str):
            flat[key] = value
    return flat


def main() -> int:
    used = collect_used_strings()
    print(f"Found {len(used)} translatable strings used in web/ source.\n")

    locale_files = sorted(I18N_DIR.glob("*.json"))
    if not locale_files:
        print("No locale files found.")
        return 0

    failed = False
    for locale_file in locale_files:
        flat = flatten_locale(locale_file)
        missing = sorted(s for s in used if s not in flat)
        orphaned = sorted(k for k in flat if k not in used)

        print(f"=== {locale_file.name} ===")
        print(
            f"  keys: {len(flat)}  used: {len(used)}  "
            f"missing: {len(missing)}  orphaned: {len(orphaned)}"
        )
        if missing:
            failed = True
            print("  MISSING (used in code, no translation):")
            for s in missing:
                print(f"    - {s!r}")
        if orphaned:
            print("  orphaned (in locale, unused in code):")
            for s in orphaned:
                print(f"    - {s!r}")
        print()

    if failed:
        print("FAIL: some locales are missing translations.")
        return 1
    print("OK: all used strings are translated in every locale.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
