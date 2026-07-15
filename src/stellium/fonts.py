"""On-demand font packs for rendering non-Latin charts.

The bundled fonts cover Latin text and astrological symbols. A chart whose text is in
another script — Chinese, and later Arabic, Devanagari, … — needs a font that covers it,
and bundling one per script would bloat the wheel for the Latin-only majority. So packs
are fetched on demand into ``~/.stellium/fonts/`` (sibling to the downloaded ephemeris),
verified against a checksum, and auto-discovered by the renderer.

This module owns the manifest and the download/verify/install/remove of packs. The
render-time resolution lives in :func:`stellium.presentation.typst_runtime.font_paths`
and :func:`stellium.data.paths.installed_font_dirs`.

See docs/development/specs/FONTS_AND_CHART_I18N.md.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

from stellium.data.paths import get_user_fonts_dir, installed_font_dirs

MANIFEST_PATH = Path(__file__).parent / "data" / "font_packs.json"

__all__ = [
    "load_manifest",
    "list_packs",
    "pack_dir",
    "is_installed",
    "download_pack",
    "remove_pack",
    "installed_font_dirs",
    "locale_script",
    "families_for_locale",
    "missing_font_packs",
    "FontDownloadError",
]


class FontDownloadError(RuntimeError):
    """A pack could not be fetched, or a file failed its checksum."""


def load_manifest() -> dict[str, Any]:
    """The bundled font-pack manifest (packs, families, checksums, release URL)."""
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def pack_dir(script: str) -> Path:
    """Where a script's pack installs — ``~/.stellium/fonts/<script>/``."""
    return get_user_fonts_dir() / script


def is_installed(script: str) -> bool:
    """True if the pack's every declared font is present on disk."""
    manifest = load_manifest()
    pack = manifest["packs"].get(script)
    if not pack:
        return False
    target = pack_dir(script)
    return all((target / f["name"]).exists() for f in pack["fonts"])


def list_packs() -> dict[str, dict[str, Any]]:
    """Every pack in the manifest, annotated with whether it is installed."""
    manifest = load_manifest()
    out: dict[str, dict[str, Any]] = {}
    for script, pack in manifest["packs"].items():
        out[script] = {
            **pack,
            "installed": is_installed(script),
            "install_dir": str(pack_dir(script)),
        }
    return out


def _download_bytes(url: str) -> bytes:
    """Fetch a URL's bytes. Injected point for tests (no live network in the suite)."""
    with urllib.request.urlopen(url) as response:  # noqa: S310 - fixed https release URLs
        return response.read()


def _verify(data: bytes, expected_sha256: str, name: str) -> None:
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected_sha256:
        raise FontDownloadError(
            f"{name}: checksum mismatch (expected {expected_sha256[:12]}…, "
            f"got {actual[:12]}…) — refusing to install a file that does not match the "
            f"manifest"
        )


def download_pack(
    script: str,
    *,
    force: bool = False,
    on_progress: Callable[[str], None] | None = None,
) -> Path:
    """Fetch, verify and install a font pack. Returns its install directory.

    Every file is downloaded to a temporary directory and checksum-verified *before*
    anything lands in ``~/.stellium/fonts/`` — so a failed or tampered download leaves no
    half-installed pack behind. Idempotent: an already-installed pack is a no-op unless
    ``force``. ``on_progress`` receives a line per step (the CLI prints them; the library
    itself stays quiet).
    """

    def report(message: str) -> None:
        if on_progress is not None:
            on_progress(message)

    manifest = load_manifest()
    pack = manifest["packs"].get(script)
    if pack is None:
        available = ", ".join(sorted(manifest["packs"])) or "(none)"
        raise FontDownloadError(f"no font pack {script!r}. Available: {available}")

    target = pack_dir(script)
    if is_installed(script) and not force:
        report(f"{script} already installed at {target}")
        return target

    base = manifest["base_url"].rstrip("/")
    entries = list(pack["fonts"]) + list(pack.get("files", []))

    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp)
        for entry in entries:
            report(f"fetching {entry['asset']} …")
            data = _download_bytes(f"{base}/{entry['asset']}")
            _verify(data, entry["sha256"], entry["asset"])
            (staged / entry["name"]).write_bytes(data)

        # Everything fetched and verified — now publish atomically.
        target.mkdir(parents=True, exist_ok=True)
        for entry in entries:
            shutil.copy(staged / entry["name"], target / entry["name"])

    report(f"installed {script} ({len(pack['fonts'])} fonts) to {target}")
    return target


def locale_script(locale: str) -> str | None:
    """The font-pack script code a locale needs, or None if Latin covers it.

    ``zh_CN`` → ``zh``; ``zh_Hant`` / ``zh_TW`` / ``zh_HK`` → ``zh-hant``. Extend as packs
    for other scripts are added.
    """
    low = locale.lower()
    if "hant" in low or low.replace("-", "_") in ("zh_tw", "zh_hk"):
        return "zh-hant"
    if low.startswith("zh"):
        return "zh"
    return None


def families_for_locale(locale: str) -> dict[str, str]:
    """``{role: family}`` of the installed pack covering this locale, or ``{}``.

    Empty when the locale needs no special font (Latin) or when the pack it needs is not
    downloaded — the renderer then leaves its Latin stack untouched, and the missing-font
    warning fires if the text turns out to need coverage.
    """
    script = locale_script(locale)
    if script is None or not is_installed(script):
        return {}
    pack = load_manifest()["packs"][script]
    return {f["role"]: f["family"] for f in pack["fonts"] if f.get("role") != "file"}


# CJK Unicode blocks (the scripts our packs cover). Extend as packs are added.
_CJK_RANGES = (
    (0x2E80, 0x2FDF),  # radicals
    (0x3000, 0x303F),  # CJK symbols & punctuation
    (0x3400, 0x4DBF),  # extension A
    (0x4E00, 0x9FFF),  # unified ideographs
    (0xF900, 0xFAFF),  # compatibility ideographs
    (0x20000, 0x2A6DF),  # extension B
)


def _has_cjk(text: str) -> bool:
    return any(any(lo <= ord(ch) <= hi for lo, hi in _CJK_RANGES) for ch in text)


def missing_font_packs(text: str, locale: str | None = None) -> list[str]:
    """Font packs ``text`` needs for full coverage but that are not installed.

    Empty when the bundled fonts already cover the text (Latin), or when a covering pack
    is installed. Otherwise the pack to suggest — the locale's script when known
    (``zh_Hant`` → ``zh-hant``), else Simplified as the common default. Used to warn
    before a chart rasterises to tofu; see :class:`stellium.exceptions.MissingFontWarning`.
    """
    needed: list[str] = []
    if _has_cjk(text) and not (is_installed("zh") or is_installed("zh-hant")):
        preferred = locale_script(locale) if locale else None
        needed.append(preferred if preferred in ("zh", "zh-hant") else "zh")
    return needed


def remove_pack(script: str) -> bool:
    """Delete an installed pack. Returns True if anything was removed."""
    target = pack_dir(script)
    if target.is_dir():
        shutil.rmtree(target)
        return True
    return False
