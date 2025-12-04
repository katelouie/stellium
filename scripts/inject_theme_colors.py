#!/usr/bin/env python3
"""
Inject multiwheel colors into theme definitions.

This script reads a YAML file containing color definitions and injects them
into the themes.py file. It uses AST-based parsing to safely modify the
Python source code.

Usage:
    python scripts/inject_theme_colors.py [--dry-run] [--colors-file PATH]

The script:
1. Reads color definitions from theme_multiwheel_colors.yaml
2. Parses themes.py to find each theme function
3. Injects the new keys into the appropriate dicts
4. Writes the modified file back (or prints diff in dry-run mode)
"""

import argparse
import re
from pathlib import Path

import yaml


def load_colors(colors_file: Path) -> dict:
    """Load color definitions from YAML file."""
    with open(colors_file) as f:
        return yaml.safe_load(f)


def find_theme_function_range(content: str, theme_name: str) -> tuple[int, int] | None:
    """Find the start and end positions of a theme function in the source."""
    # Match the function definition
    pattern = rf"def _get_{theme_name}_theme\(\)[^:]*:"
    match = re.search(pattern, content)
    if not match:
        return None

    start = match.start()

    # Find the matching return statement and closing brace
    # We need to track brace depth from the first { after 'return'
    return_match = re.search(r"return\s*\{", content[start:])
    if not return_match:
        return None

    brace_start = start + return_match.end() - 1  # Position of opening {
    depth = 1
    pos = brace_start + 1

    while pos < len(content) and depth > 0:
        char = content[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        pos += 1

    return (start, pos)


def find_section_in_dict(
    content: str, section_name: str, start: int, end: int
) -> tuple[int, int] | None:
    """Find a section (like 'houses' or 'planets') within a dict range."""
    # Look for the section key
    pattern = rf'"{section_name}":\s*\{{'
    search_area = content[start:end]
    match = re.search(pattern, search_area)
    if not match:
        return None

    section_start = start + match.end() - 1  # Position of opening {
    depth = 1
    pos = section_start + 1

    while pos < end and depth > 0:
        char = content[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        pos += 1

    return (section_start, pos)


def find_last_entry_in_section(
    content: str, section_start: int, section_end: int
) -> int:
    """Find the position right before the closing brace where we can insert new entries."""
    # Find the last non-whitespace before the closing }
    section_content = content[section_start:section_end]

    # Find position just before the closing }
    # We want to insert after the last entry (after its trailing comma if present)
    last_brace = section_content.rfind("}")
    if last_brace == -1:
        return section_end - 1

    # Look backwards from the closing brace to find where to insert
    insert_pos = section_start + last_brace

    # Check if there's already content with a trailing comma
    _before_brace = section_content[:last_brace].rstrip()

    return insert_pos


def format_new_entries(entries: dict, indent: str = "            ") -> str:
    """Format new dictionary entries as Python source code."""
    lines = []
    for key, value in entries.items():
        # Check if value has a comment (stored in YAML as "value  # comment")
        if isinstance(value, str) and "  #" in value:
            val, comment = value.split("  #", 1)
            lines.append(f'{indent}"{key}": "{val.strip()}",  #{comment}')
        else:
            lines.append(f'{indent}"{key}": "{value}",')
    return "\n" + "\n".join(lines)


def check_if_already_injected(
    content: str, section_start: int, section_end: int, key: str
) -> bool:
    """Check if a key already exists in a section."""
    section_content = content[section_start:section_end]
    pattern = rf'"{key}":'
    return bool(re.search(pattern, section_content))


def inject_colors_into_theme(
    content: str, theme_name: str, colors: dict, verbose: bool = False
) -> str:
    """Inject colors for a single theme."""
    theme_range = find_theme_function_range(content, theme_name)
    if not theme_range:
        if verbose:
            print(f"  Warning: Could not find theme function for '{theme_name}'")
        return content

    theme_start, theme_end = theme_range

    # Process sections in reverse order of their position so insertions don't mess up positions
    insertions = []  # List of (position, text_to_insert)

    for section_name, entries in colors.items():
        section_range = find_section_in_dict(
            content, section_name, theme_start, theme_end
        )
        if not section_range:
            if verbose:
                print(
                    f"  Warning: Could not find section '{section_name}' in theme '{theme_name}'"
                )
            continue

        section_start, section_end = section_range

        # Check if already injected (check first key)
        first_key = next(iter(entries.keys()))
        if check_if_already_injected(content, section_start, section_end, first_key):
            if verbose:
                print(
                    f"  Skipping '{section_name}' in '{theme_name}' - already has multiwheel colors"
                )
            continue

        # Find insertion point (just before closing brace)
        insert_pos = find_last_entry_in_section(content, section_start, section_end)

        # Format new entries
        new_text = format_new_entries(entries)

        insertions.append((insert_pos, new_text))
        if verbose:
            print(
                f"  Adding {len(entries)} entries to '{section_name}' in '{theme_name}'"
            )

    # Apply insertions in reverse order (so positions stay valid)
    for pos, text in sorted(insertions, key=lambda x: x[0], reverse=True):
        content = content[:pos] + text + "\n        " + content[pos:]

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Inject multiwheel colors into themes.py"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print diff without modifying file"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print detailed progress"
    )
    parser.add_argument(
        "--colors-file",
        type=Path,
        default=Path(__file__).parent / "theme_multiwheel_colors.yaml",
        help="Path to colors YAML file",
    )
    parser.add_argument(
        "--themes-file",
        type=Path,
        default=Path(__file__).parent.parent / "src/stellium/visualization/themes.py",
        help="Path to themes.py file",
    )
    args = parser.parse_args()

    # Load colors
    if not args.colors_file.exists():
        print(f"Error: Colors file not found: {args.colors_file}")
        return 1

    colors = load_colors(args.colors_file)
    print(f"Loaded colors for {len(colors)} themes")

    # Load themes.py
    if not args.themes_file.exists():
        print(f"Error: Themes file not found: {args.themes_file}")
        return 1

    content = args.themes_file.read_text()
    original_content = content

    # Inject colors for each theme
    for theme_name, theme_colors in colors.items():
        if args.verbose:
            print(f"\nProcessing theme: {theme_name}")
        content = inject_colors_into_theme(
            content, theme_name, theme_colors, verbose=args.verbose
        )

    # Output results
    if content == original_content:
        print("\nNo changes needed - all themes already have multiwheel colors")
        return 0

    if args.dry_run:
        print("\n--- DRY RUN - would make these changes ---")
        # Show a simple diff
        orig_lines = original_content.splitlines()
        new_lines = content.splitlines()

        # Find and show changed sections
        import difflib

        diff = difflib.unified_diff(orig_lines, new_lines, lineterm="", n=3)
        for line in diff:
            print(line)
        print("\n--- END DRY RUN ---")
    else:
        args.themes_file.write_text(content)
        print(f"\nSuccessfully updated {args.themes_file}")

    return 0


if __name__ == "__main__":
    exit(main())
