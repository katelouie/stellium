#!/usr/bin/env python3
"""assemble_corpus.py — merge Phase-2 event batches into one rectification corpus.

Standalone tooling for the rectification workflow. Not part of the stellium
package: no dependency added, imports nothing from stellium (plain PyYAML only).

For every person in the batch files it:
  * matches the name to the verified notables DB (exact NFC, then
    parenthetical-stripped, then accent-folded — anything still unmatched is
    reported LOUDLY, never guessed),
  * takes birth_data AUTHORITATIVELY from the DB (the batch's echoed birth_data
    is ignored — Phase 1 froze the times), and
  * carries the batch's events + temperament + notes.

Re-run it with more batch files as they arrive; it rebuilds the whole corpus
from whatever batches you pass, and prints coverage (N / 63).

USAGE
    python assemble_corpus.py --batches ~/Downloads/events_batch*.yaml
    python assemble_corpus.py --batches a.yaml b.yaml --out corpus.yaml
"""

from __future__ import annotations

import argparse
import glob
import re
import unicodedata
from pathlib import Path

import yaml

DEFAULT_DATA_DIR = (
    Path(__file__).resolve().parents[5] / "src" / "stellium" / "data" / "notables"
)
DEFAULT_OUT = (
    Path(__file__).resolve().parent.parent / "data" / "rectification-corpus-events.yaml"
)

# Explicit batch-name -> DB-name aliases for variants that reorder tokens, add a
# middle name, or reword — cases fuzzy matching can't resolve safely. Extend as
# new batches surface new spellings; better an explicit map than a wrong guess.
ALIASES = {
    "Prince Philip, Duke of Edinburgh": "Prince Philip",
    "Diana, Princess of Wales": "Princess of Wales Diana",
    "Queen Victoria": "Queen of the United Kingdom Victoria",
    "Wolfgang Amadeus Mozart": "Wolfgang Mozart",
    "Osho (Rajneesh)": "Osho Rajneesh",
}


def norm(s: object) -> str:
    return unicodedata.normalize("NFC", str(s)).strip()


def strip_paren(s: str) -> str:
    return re.sub(r"\s*\(.*\)\s*$", "", s).strip()


def fold(s: str) -> str:
    """Accent-fold + lowercase for a last-resort fuzzy match (Dalí == Dali)."""
    d = unicodedata.normalize("NFKD", s)
    return "".join(c for c in d if not unicodedata.combining(c)).lower().strip()


def is_noon(e: dict) -> bool:
    return (e.get("hour"), e.get("minute", 0)) == (12, 0)


def reliable(e: dict) -> bool:
    if "has_reliable_time" in e:
        return bool(e["has_reliable_time"])
    return False


def load_db(data_dir: Path):
    """Return (by_norm, by_foldparen, corpus_names) for the 63 verified people."""
    by_norm, by_fold, names = {}, {}, []
    for f in sorted((data_dir / "births").glob("*.yaml")):
        for e in yaml.safe_load(f.read_text(encoding="utf-8")) or []:
            q = e.get("data_quality")
            if q in ("AA", "A") and reliable(e) and not is_noon(e):
                name = e["name"]
                names.append(name)
                bd = {
                    "date": f"{e['year']:04d}-{e.get('month', 0):02d}-{e.get('day', 0):02d}",
                    "time": f"{e.get('hour', 0):02d}:{e.get('minute', 0):02d}",
                    "timezone": e.get("timezone", ""),
                    "place": e.get("location_name", ""),
                    "latitude": e.get("latitude"),
                    "longitude": e.get("longitude"),
                    "rodden_rating": q,
                }
                by_norm[norm(name)] = (name, bd)
                by_fold[fold(strip_paren(name))] = (name, bd)
    return by_norm, by_fold, names


def match(raw: str, by_norm: dict, by_fold: dict):
    """(canonical_name, birth_data, how) or (None, None, None)."""
    if norm(raw) in by_norm:
        return (*by_norm[norm(raw)], "exact")
    if raw in ALIASES and norm(ALIASES[raw]) in by_norm:
        return (*by_norm[norm(ALIASES[raw])], "alias")
    if norm(strip_paren(raw)) in by_norm:
        return (*by_norm[norm(strip_paren(raw))], "paren-stripped")
    if fold(strip_paren(raw)) in by_fold:
        return (*by_fold[fold(strip_paren(raw))], "accent-folded")
    return (None, None, None)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "--batches", nargs="+", required=True, help="batch YAML files/globs"
    )
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)

    files: list[str] = []
    for pat in args.batches:
        hits = sorted(glob.glob(pat))
        files.extend(hits or [pat])

    by_norm, by_fold, corpus_names = load_db(args.data_dir)

    corpus: dict[str, dict] = {}
    misses, renamed = [], []
    for fp in files:
        doc = yaml.safe_load(Path(fp).read_text(encoding="utf-8")) or []
        for person in doc:
            raw = person.get("name", "")
            canonical, bd, how = match(raw, by_norm, by_fold)
            if canonical is None:
                misses.append((raw, Path(fp).name))
                continue
            if how != "exact":
                renamed.append((raw, canonical, how))
            corpus[canonical] = {
                "name": canonical,
                "birth_data": bd,  # authoritative, from the verified DB
                "events": person.get("events", []),
                "temperament": person.get("temperament", []),
                "notes": person.get("notes", ""),
            }

    ordered = [corpus[n] for n in sorted(corpus)]
    args.out.write_text(
        "# Rectification corpus — assembled by assemble_corpus.py.\n"
        "# birth_data is authoritative from the verified notables DB; events +\n"
        "# temperament come from the Phase-2 research batches.\n"
        + yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )

    have = set(corpus)
    missing = [n for n in corpus_names if n not in have]
    print(f"assembled {len(corpus)} / {len(corpus_names)} corpus people -> {args.out}")
    if renamed:
        print("\nname reconciliations:")
        for raw, canon, how in renamed:
            print(f"  {raw!r} -> {canon!r}  ({how})")
    if misses:
        print("\n! UNMATCHED batch people (NOT added — reconcile name):")
        for raw, fn in misses:
            print(f"  {raw!r}  (in {fn})")
    total_events = sum(len(p["events"]) for p in ordered)
    print(f"\nevents total: {total_events}   still missing events: {len(missing)}")
    if missing:
        print("  " + ", ".join(missing[:15]) + (" ..." if len(missing) > 15 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
