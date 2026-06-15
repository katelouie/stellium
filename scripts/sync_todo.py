#!/usr/bin/env python3
"""
Sync TODO.md from Obsidian TaskNotes.

Reads task notes from the Obsidian vault, filters for Stellium project tasks,
and writes a sorted markdown list to TODO.md in the repo root.

Usage:
    python scripts/sync_todo.py

Reads from: ~/Obsidian/Vault KL/TaskNotes/Tasks/
Writes to:  ./TODO.md
"""

from pathlib import Path

import yaml

VAULT_TASKS_DIR = Path.home() / "Obsidian" / "Vault KL" / "TaskNotes" / "Tasks"
TODO_PATH = Path(__file__).resolve().parent.parent / "TODO.md"
PROJECT_FILTER = "Stellium"
EXCLUDE_STATUSES = {"done", "cancelled"}

PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3}


def parse_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    try:
        return yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None


def matches_project(frontmatter: dict) -> bool:
    """Check if task belongs to the target project."""
    projects = frontmatter.get("projects", [])
    return any(PROJECT_FILTER in str(p) for p in projects)


def collect_tasks() -> list[dict]:
    """Collect and filter tasks from Obsidian vault."""
    tasks = []

    for filepath in VAULT_TASKS_DIR.glob("*.md"):
        fm = parse_frontmatter(filepath)
        if fm is None:
            continue

        status = fm.get("status", "open")
        if status in EXCLUDE_STATUSES:
            continue

        if not matches_project(fm):
            continue

        if "private" in fm.get("tags", []):
            continue

        tasks.append(
            {
                "title": fm.get("title", filepath.stem),
                "status": status,
                "priority": fm.get("priority", "normal"),
                "due": fm.get("due", ""),
            }
        )

    # Sort: priority (critical first), then due date, then title
    tasks.sort(
        key=lambda t: (
            PRIORITY_ORDER.get(t["priority"], 99),
            t["due"] or "9999",
            t["title"],
        )
    )

    return tasks


def write_todo(tasks: list[dict]) -> None:
    """Write tasks to TODO.md."""
    lines = ["# TODO", "", f"*{len(tasks)} open tasks (synced from Obsidian)*", ""]

    # Group by priority
    current_priority = None
    for task in tasks:
        priority = task["priority"]
        if priority != current_priority:
            if current_priority is not None:
                lines.append("")
            lines.append(f"## {priority.capitalize()}")
            lines.append("")
            current_priority = priority

        due = f" (due {task['due']})" if task["due"] else ""
        status_tag = f" `{task['status']}`" if task["status"] != "open" else ""
        lines.append(f"- {task['title']}{due}{status_tag}")

    lines.append("")
    TODO_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(tasks)} tasks to {TODO_PATH}")


if __name__ == "__main__":
    if not VAULT_TASKS_DIR.exists():
        # Vault not present (CI, other machine) -- skip silently
        print("Obsidian vault not found, skipping TODO sync")
        raise SystemExit(0)

    tasks = collect_tasks()
    write_todo(tasks)
