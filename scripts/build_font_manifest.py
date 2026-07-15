"""Turn a folder of font packs into a checksummed manifest + a ready-to-upload folder.

The font provisioning system (docs/development/specs/FONTS_AND_CHART_I18N.md) fetches
per-script font packs from a GitHub Release and verifies each file's SHA-256 before
installing it. This script does the tedious half so the maintainer's job is just "drop
fonts in a folder, run this, upload the result".

**Input** — a staging directory with one subdirectory per script code, each holding the
font file(s) and the license, e.g.::

    staging/
        zh/       NotoSansSC-Regular.ttf   OFL.txt   [meta.json]
        zh-hant/  NotoSansTC-Regular.ttf   OFL.txt   [meta.json]

An optional ``meta.json`` in a pack directory supplies ``{"covers": "...",
"family": "..."}``; ``covers`` is the human description shown by ``stellium fonts list``
and cannot be sniffed, ``family`` overrides the name read from the font.

**Output** — two things:

1. ``font_packs.json`` (the manifest): for each pack, its family, coverage description, and
   every file's release-asset name, SHA-256 and byte size. This is committed into the
   package so the CLI can read it offline, and its URLs point at the release.
2. ``<upload-dir>/`` — a flat folder of the same files renamed ``<script>_<file>`` so they
   are unique across packs (a GitHub Release is a flat namespace). Upload it whole::

       gh release create fonts-v1 --repo katelouie/stellium <upload-dir>/* font_packs.json

Usage::

    python scripts/build_font_manifest.py staging/ [--base-url URL] [--version fonts-v1]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}
DEFAULT_BASE = "https://github.com/katelouie/stellium/releases/download"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _family_from_name_table(path: Path) -> str | None:
    """Read the font's family name (name ID 16 or 1) with no third-party dependency.

    A minimal sfnt/`name`-table reader — the format is stable, and keeping this dep-free
    means the script never breaks because fonttools isn't installed. Handles the common
    Windows (platform 3, UTF-16BE) and Mac (platform 1, Latin-1) records.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 12:
        return None
    num_tables = struct.unpack(">H", data[4:6])[0]
    name_off = None
    for i in range(num_tables):
        rec = 12 + i * 16
        tag = data[rec : rec + 4]
        if tag == b"name":
            name_off = struct.unpack(">I", data[rec + 8 : rec + 12])[0]
            break
    if name_off is None:
        return None

    count, string_off = struct.unpack(">HH", data[name_off + 2 : name_off + 6])
    strings_base = name_off + string_off
    best: dict[int, str] = {}
    for i in range(count):
        r = name_off + 6 + i * 12
        platform, _enc, _lang, name_id, length, offset = struct.unpack(
            ">HHHHHH", data[r : r + 12]
        )
        if name_id not in (1, 16):
            continue
        raw = data[strings_base + offset : strings_base + offset + length]
        try:
            text = raw.decode("utf-16-be") if platform == 3 else raw.decode("latin-1")
        except UnicodeDecodeError:
            continue
        text = text.strip("\x00").strip()
        if text:
            best[name_id] = text
    # Typographic family (16) wins over legacy family (1) when both are present.
    return best.get(16) or best.get(1)


def sniff_family(path: Path) -> str:
    try:
        from fontTools.ttLib import TTFont  # nicer if available, but not required

        with TTFont(path, fontNumber=0, lazy=True) as font:
            name = font["name"].getDebugName(16) or font["name"].getDebugName(1)
        if name:
            return name
    except Exception:
        pass
    return _family_from_name_table(path) or path.stem


def build_pack(pack_dir: Path, upload_dir: Path) -> dict:
    script = pack_dir.name
    meta = {}
    meta_file = pack_dir / "meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))

    files = sorted(
        p for p in pack_dir.iterdir() if p.is_file() and p.name != "meta.json"
    )
    fonts = [p for p in files if p.suffix.lower() in FONT_SUFFIXES]
    if not fonts:
        raise SystemExit(f"pack {script!r} has no font file (.ttf/.otf/.ttc)")

    family = meta.get("family") or sniff_family(fonts[0])
    covers = meta.get("covers")
    if not covers:
        print(
            f"  ! {script}: no 'covers' description — add meta.json with a 'covers' key"
        )

    file_entries = []
    for path in files:
        asset = f"{script}_{path.name}"  # unique in the flat release namespace
        shutil.copy(path, upload_dir / asset)
        file_entries.append(
            {
                "name": path.name,  # installed as fonts/<script>/<name>
                "asset": asset,  # release asset filename
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "is_font": path.suffix.lower() in FONT_SUFFIXES,
            }
        )

    return {"family": family, "covers": covers or "", "files": file_entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "staging", type=Path, help="dir with one subdir per script code"
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--version", default="fonts-v1", help="release tag")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent.parent / "src/stellium/data/font_packs.json",
    )
    parser.add_argument("--upload-dir", type=Path, default=Path("font_upload"))
    args = parser.parse_args()

    if not args.staging.is_dir():
        raise SystemExit(f"no such staging directory: {args.staging}")
    args.upload_dir.mkdir(parents=True, exist_ok=True)

    packs = {}
    for pack_dir in sorted(p for p in args.staging.iterdir() if p.is_dir()):
        print(f"  {pack_dir.name}:")
        packs[pack_dir.name] = build_pack(pack_dir, args.upload_dir)
        for f in packs[pack_dir.name]["files"]:
            print(f"      {f['asset']:32} {f['bytes']:>9,} B  {f['sha256'][:12]}…")

    manifest = {
        "version": args.version,
        "base_url": f"{args.base_url}/{args.version}",
        "packs": packs,
    }
    args.out.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"\nwrote manifest: {args.out}")
    print(
        f"upload folder:  {args.upload_dir}/  ({sum(len(p['files']) for p in packs.values())} files)"
    )
    print("\nNext:")
    print(f"  gh release create {args.version} --repo katelouie/stellium \\")
    print(
        f"    --title 'Font packs {args.version}' --notes 'Non-Latin chart fonts (OFL).' \\"
    )
    print(f"    {args.upload_dir}/*")
    print("  (then commit the updated font_packs.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
