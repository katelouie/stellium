#!/usr/bin/env python3
"""apply_research_verdicts.py — write Deep Research's Phase-1 provenance
verdicts back into the Stellium notables birth YAMLs.

Standalone tooling for the rectification-corpus workflow. It is **not** part of
the stellium package: it adds no dependency to the project and imports nothing
from stellium. It only needs ``ruamel.yaml`` (round-trip, so your comments and
block style survive) in whatever interpreter you run it with::

    pip install ruamel.yaml   # already present in the `starlight` env

WHAT IT CONSUMES
    The two-section (or bucketed / flat) YAML that the research prompt
    (`rectification-corpus-research-prompt.md`) returns. Each verdict record:

        name: "Richard Feynman"
        rodden_rating_verified: "C"          # optional
        provenance_bucket: "rectified"       # optional
        source_note_quote: "...verbatim..."  # optional but wanted
        verdict: accept | accept_soft | reject | needs_manual_review
        reason: "one line"                   # optional
        adb_url: "..."                       # optional

    Accepted shapes (auto-detected):
      * {accepted: [...], rejected: [...], needs_manual_review: [...]}
      * {accept: [...],  reject: [...],  needs_manual_review: [...]}
      * {results: [ {verdict: ...}, ... ]}
      * a flat top-level list [ {verdict: ...}, ... ]
    A record's bucket key supplies its verdict when the record omits one.

WHAT IT WRITES  (only the fields below; everything else is left verbatim)
    accept / accept_soft -> has_reliable_time: true   (+ data_quality if a
                            verified rating is given)
    reject               -> has_reliable_time: false  (+ data_quality if given)
    needs_manual_review  -> data_quality kept, but any prior has_reliable_time
                            is CLEARED (a held time cannot keep claiming
                            reliability -> reads "unverified/pending" until you
                            adjudicate); a PENDING note is recorded. Never
                            auto-enters the corpus.
    verification_notes   -> your existing note is preserved; a deterministic
                            "[ADB-verified] ..." block is appended (and replaced
                            in place on re-runs, so the script is idempotent).

FILE RESOLUTION
    Research does not know which YAML each person lives in, so this script scans
    <data-dir>/births/*.yaml, NFC-normalizes names (so "Pelé" == "Pelé"),
    and matches. Anything it cannot match is reported LOUDLY with a close-match
    hint and never guessed at.

SAFETY
    * Dry-run is the DEFAULT. Nothing is written without --apply.
    * Each changed file is backed up to <file>.bak-<timestamp> (--no-backup off).
    * Idempotent: re-running produces the same target values -> 0 changes.

USAGE
    python apply_research_verdicts.py --verdicts research_output.yaml
    python apply_research_verdicts.py --verdicts research_output.yaml --apply
    python apply_research_verdicts.py --verdicts research_output.yaml \\
        --data-dir ../../../src/stellium/data/notables
"""

from __future__ import annotations

import argparse
import difflib
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.scalarstring import LiteralScalarString
except ImportError:  # pragma: no cover
    sys.exit(
        "This script needs ruamel.yaml (round-trip, to preserve your comments "
        "and block style).\n    pip install ruamel.yaml"
    )

# Default: the packaged notables dir, resolved relative to this script's home
# (docs/development/specs/ -> ../../../src/stellium/data/notables).
DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "stellium" / "data" / "notables"
)

VALID_VERDICTS = {"accept", "accept_soft", "reject", "needs_manual_review"}
BUCKET_TO_VERDICT = {
    "accepted": "accept",
    "accept": "accept",
    "accept_soft": "accept_soft",
    "rejected": "reject",
    "reject": "reject",
    "needs_manual_review": "needs_manual_review",
    "manual": "needs_manual_review",
    "review": "needs_manual_review",
}
NOTE_MARKER = "[ADB-verified]"

_yaml = YAML()  # round-trip
_yaml.preserve_quotes = True
_yaml.width = 4096
_yaml.indent(mapping=2, sequence=2, offset=0)


def norm(s: Any) -> str:
    """NFC-normalize + strip, so 'Pelé' matches 'Pelé'."""
    return unicodedata.normalize("NFC", str(s)).strip()


@dataclass
class Change:
    file: str
    name: str
    field: str
    old: Any
    new: Any
    kind: str  # set | note | skip | miss

    def render(self) -> str:
        icon = {"set": "  ~", "note": "  ~", "skip": "  ·", "miss": "  !"}[self.kind]
        if self.kind == "miss":
            hint = f"  (did you mean: {self.new})" if self.new else ""
            return f"{icon} NO MATCH for {self.name!r}{hint}"
        if self.kind == "skip":
            return f"{icon} {self.name}: {self.new}"
        if self.kind == "note":
            return f"{icon} {self.name}: verification_notes updated"
        return f"{icon} {self.name}: {self.field}: {self.old!r} -> {self.new!r}"


# --- verdict-file parsing ----------------------------------------------------


def normalize_records(doc: Any) -> list[dict[str, Any]]:
    """Flatten any accepted shape into a list of records each carrying a verdict."""
    records: list[dict[str, Any]] = []

    def take(items: Any, default_verdict: str | None) -> None:
        if not isinstance(items, list):
            return
        for it in items:
            if not isinstance(it, dict) or "name" not in it:
                continue
            rec = dict(it)
            v = rec.get("verdict") or default_verdict
            if v in BUCKET_TO_VERDICT:  # allow a bucket name in the verdict field
                v = BUCKET_TO_VERDICT[v]
            rec["verdict"] = v
            records.append(rec)

    if isinstance(doc, list):
        take(doc, None)
    elif isinstance(doc, dict):
        if isinstance(doc.get("results"), list):
            take(doc["results"], None)
        for key, verdict in BUCKET_TO_VERDICT.items():
            if key in doc:
                take(doc[key], verdict)
    return records


# --- note merge (idempotent) -------------------------------------------------


def build_verified_line(rec: dict[str, Any]) -> str:
    verdict = rec["verdict"]
    bits = [f"{NOTE_MARKER} verdict={verdict}"]
    if rec.get("provenance_bucket"):
        bits.append(f"bucket={rec['provenance_bucket']}")
    if rec.get("rodden_rating_verified"):
        bits.append(f"rating={rec['rodden_rating_verified']}")
    head = " ".join(bits)
    tail_parts = []
    if rec.get("reason"):
        tail_parts.append(str(rec["reason"]).strip())
    if rec.get("source_note_quote"):
        tail_parts.append(f'"{str(rec["source_note_quote"]).strip()}"')
    if rec.get("adb_url"):
        tail_parts.append(str(rec["adb_url"]).strip())
    tail = " — ".join(tail_parts)
    return f"{head}: {tail}" if tail else head


def merge_note(existing: Any, verified_line: str) -> str:
    """Preserve any human note; replace a prior [ADB-verified] block in place."""
    text = "" if existing is None else str(existing)
    kept_lines: list[str] = []
    for line in text.splitlines():
        if NOTE_MARKER in line:
            break  # drop this line and everything after (the old verified block)
        kept_lines.append(line)
    human = "\n".join(kept_lines).rstrip()
    return f"{human}\n{verified_line}".strip() if human else verified_line


# --- apply one record --------------------------------------------------------


def apply_record(entry: Any, rec: dict[str, Any], *, filename: str) -> list[Change]:
    name = norm(rec["name"])
    verdict = rec.get("verdict")
    changes: list[Change] = []

    if verdict not in VALID_VERDICTS:
        return [
            Change(filename, name, "", None, f"unknown verdict {verdict!r}", "skip")
        ]

    # 1) has_reliable_time + data_quality (not for needs_manual_review).
    if verdict in ("accept", "accept_soft", "reject"):
        want_reliable = verdict != "reject"
        if entry.get("has_reliable_time") is not want_reliable:
            changes.append(
                Change(
                    filename,
                    name,
                    "has_reliable_time",
                    entry.get("has_reliable_time", "<absent>"),
                    want_reliable,
                    "set",
                )
            )
            entry["has_reliable_time"] = want_reliable

        rating = rec.get("rodden_rating_verified")
        if rating and norm(entry.get("data_quality", "")) != norm(rating):
            rating = norm(rating)  # plain unquoted str, matching DB style
            changes.append(
                Change(
                    filename,
                    name,
                    "data_quality",
                    entry.get("data_quality", "<absent>"),
                    rating,
                    "set",
                )
            )
            entry["data_quality"] = rating
    else:  # needs_manual_review — hold queue. Leave data_quality, but a held
        # time cannot keep claiming reliability: clear any prior flag so the
        # entry reads "unverified/pending" until adjudicated (never trusted).
        if "has_reliable_time" in entry:
            changes.append(
                Change(
                    filename,
                    name,
                    "has_reliable_time",
                    entry["has_reliable_time"],
                    "<cleared: pending review>",
                    "set",
                )
            )
            del entry["has_reliable_time"]
        changes.append(
            Change(
                filename,
                name,
                "",
                None,
                "held for manual review (data_quality kept, reliability -> pending)",
                "skip",
            )
        )

    # 2) verification_notes — preserve human note, refresh the verified block.
    merged = merge_note(entry.get("verification_notes"), build_verified_line(rec))
    if norm(entry.get("verification_notes")) != norm(merged):
        entry["verification_notes"] = LiteralScalarString(merged + "\n")
        changes.append(Change(filename, name, "verification_notes", None, None, "note"))

    return changes


# --- driver ------------------------------------------------------------------


def build_name_index(
    data_dir: Path,
) -> tuple[dict[str, tuple[Path, Any]], dict[Path, Any]]:
    """name -> (path, entry-node); plus path -> loaded doc (for writing back)."""
    docs: dict[Path, Any] = {}
    index: dict[str, tuple[Path, Any]] = {}
    births = data_dir / "births"
    for path in sorted(births.glob("*.yaml")):
        with path.open(encoding="utf-8") as fh:
            doc = _yaml.load(fh)
        docs[path] = doc
        for entry in doc or []:
            if isinstance(entry, dict) and "name" in entry:
                index[norm(entry["name"])] = (path, entry)
    return index, docs


def run(verdicts_path: Path, data_dir: Path, *, apply: bool, backup: bool) -> int:
    with verdicts_path.open(encoding="utf-8") as fh:
        doc = _yaml.load(fh)
    records = normalize_records(doc)
    if not records:
        sys.exit("No verdict records found — check the --verdicts file shape.")

    index, docs = build_name_index(data_dir)
    all_names = list(index.keys())

    changes: list[Change] = []
    touched: set[Path] = set()
    for rec in records:
        name = norm(rec["name"])
        hit = index.get(name)
        if hit is None:
            close = difflib.get_close_matches(name, all_names, n=2, cutoff=0.8)
            changes.append(
                Change("?", rec["name"], "", None, ", ".join(close) or None, "miss")
            )
            continue
        path, entry = hit
        recs = apply_record(entry, rec, filename=path.name)
        changes += recs
        if any(c.kind in ("set", "note") for c in recs):
            touched.add(path)

    # report, grouped by file
    by_file: dict[str, list[Change]] = {}
    for c in changes:
        by_file.setdefault(c.file, []).append(c)
    for filename in sorted(by_file):
        print(f"\n=== {filename} ===")
        for c in by_file[filename]:
            print(c.render())

    n_set = sum(c.kind == "set" for c in changes)
    n_note = sum(c.kind == "note" for c in changes)
    n_skip = sum(c.kind == "skip" for c in changes)
    n_miss = sum(c.kind == "miss" for c in changes)
    print("\n" + "-" * 60)
    print(
        f"records: {len(records)}   field-sets: {n_set}   notes: {n_note}   "
        f"held/skipped: {n_skip}   UNMATCHED: {n_miss}"
    )
    if n_miss:
        print("  ! Unmatched names were NOT applied — reconcile spelling and re-run.")

    if not apply:
        print("\nDRY RUN — nothing written. Re-run with --apply to commit.")
        return 0

    if not touched:
        print("\nNothing to write.")
        return 0
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    print()
    for path in sorted(touched):
        if backup:
            bak = path.with_suffix(path.suffix + f".bak-{stamp}")
            bak.write_bytes(path.read_bytes())
            print(f"  backed up -> {bak.name}")
        with path.open("w", encoding="utf-8") as fh:
            _yaml.dump(docs[path], fh)
        print(f"  wrote {path.name}")
    print(
        f"\nDone. {n_set} field-set(s) + {n_note} note(s) across {len(touched)} file(s)."
    )
    if n_miss:
        print(f"{n_miss} unmatched name(s) still need reconciliation.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--verdicts", type=Path, required=True, help="Research Phase-1 YAML"
    )
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    ap.add_argument("--no-backup", action="store_true", help="skip .bak files")
    args = ap.parse_args(argv)

    if not args.verdicts.exists():
        sys.exit(f"verdicts file not found: {args.verdicts}")
    if not (args.data_dir / "births").exists():
        sys.exit(f"no births/ under data dir: {args.data_dir}")
    return run(
        args.verdicts, args.data_dir, apply=args.apply, backup=not args.no_backup
    )


if __name__ == "__main__":
    raise SystemExit(main())
