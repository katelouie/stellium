"""Font provisioning — the resolution layer (spec FONTS_AND_CHART_I18N.md, Phase A1).

The load-bearing property: a font placed under ``~/.stellium/fonts/`` is found by the
render font path with no ``with_font()`` call, exactly as a downloaded ephemeris is found.
Everything the downloader will add later is plumbing around this.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from stellium.data import paths
from stellium.presentation import typst_runtime

BUNDLED = Path(__file__).parent.parent / "src/stellium/data/fonts"


def _a_bundled_font() -> Path:
    return next(BUNDLED.glob("*.ttf"))


def test_no_packs_installed_is_empty_and_cheap(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "USER_FONTS_DIR", tmp_path / "fonts")
    # Nothing downloaded: no user dirs, and font_paths is just the bundle.
    assert paths.installed_font_dirs() == []
    assert len(typst_runtime.font_paths()) == 1  # bundled only


def test_a_dropped_in_font_is_auto_discovered(tmp_path, monkeypatch):
    fonts = tmp_path / "fonts"
    monkeypatch.setattr(paths, "USER_FONTS_DIR", fonts)

    pack = fonts / "zh"
    pack.mkdir(parents=True)
    shutil.copy(_a_bundled_font(), pack / "font.ttf")

    # The pack directory is discovered...
    assert paths.installed_font_dirs() == [pack]
    # ...and appears in the render font path with no with_font() call.
    assert str(pack) in typst_runtime.font_paths()


def test_a_dir_without_a_font_file_is_ignored(tmp_path, monkeypatch):
    fonts = tmp_path / "fonts"
    monkeypatch.setattr(paths, "USER_FONTS_DIR", fonts)
    (fonts / "notes").mkdir(parents=True)
    (fonts / "notes" / "README.txt").write_text("not a font")
    assert paths.installed_font_dirs() == []


def test_explicit_extra_paths_are_appended(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "USER_FONTS_DIR", tmp_path / "fonts")
    result = typst_runtime.font_paths(extra=["/some/brand/fonts"])
    assert result[-1] == "/some/brand/fonts"
    # The bundle stays first — it is the authoritative Latin + symbol source.
    assert "data/fonts" in result[0] or "data\\fonts" in result[0]


# --- download / verify / install (spec Phase A2) ------------------------------------


def _fixture_manifest(monkeypatch, *files: bytes):
    """A one-pack manifest over the given file bytes, plus a fetcher that serves them."""
    from stellium import fonts

    entries = [
        {
            "role": "sans" if i == 0 else "file",
            "family": "Fixture Sans",
            "name": f"font{i}.ttf" if i == 0 else f"license{i}.txt",
            "asset": f"xx_font{i}",
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }
        for i, data in enumerate(files)
    ]
    manifest = {
        "version": "test",
        "base_url": "https://example.invalid/test",
        "packs": {
            "xx": {
                "covers": "Test",
                "fonts": [entries[0]],
                "files": entries[1:],
            }
        },
    }
    by_asset = {e["asset"]: data for e, data in zip(entries, files, strict=True)}
    monkeypatch.setattr(fonts, "load_manifest", lambda: manifest)
    monkeypatch.setattr(
        fonts, "_download_bytes", lambda url: by_asset[url.rsplit("/", 1)[-1]]
    )
    return fonts


def test_download_verifies_and_installs(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "USER_FONTS_DIR", tmp_path / "fonts")
    fonts = _fixture_manifest(monkeypatch, b"a-font", b"a-license")

    assert fonts.is_installed("xx") is False
    target = fonts.download_pack("xx")

    assert (target / "font0.ttf").read_bytes() == b"a-font"
    assert (target / "license1.txt").read_bytes() == b"a-license"
    assert fonts.is_installed("xx") is True
    # Auto-discovered, so a with_font()-free render would find it.
    assert target in paths.installed_font_dirs()


def test_download_rejects_a_bad_checksum_and_installs_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "USER_FONTS_DIR", tmp_path / "fonts")
    fonts = _fixture_manifest(monkeypatch, b"a-font")
    # Corrupt the bytes the fetcher returns; the manifest's checksum no longer matches.
    monkeypatch.setattr(fonts, "_download_bytes", lambda url: b"tampered")

    with pytest.raises(fonts.FontDownloadError, match="checksum"):
        fonts.download_pack("xx")
    # Verify-before-publish: nothing landed on disk.
    assert not (tmp_path / "fonts" / "xx").exists()


def test_download_is_idempotent_and_remove_works(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "USER_FONTS_DIR", tmp_path / "fonts")
    fonts = _fixture_manifest(monkeypatch, b"a-font")

    fonts.download_pack("xx")
    fetched = []
    monkeypatch.setattr(
        fonts, "_download_bytes", lambda url: fetched.append(url) or b""
    )
    fonts.download_pack("xx")  # already installed
    assert fetched == []  # no re-fetch

    assert fonts.remove_pack("xx") is True
    assert fonts.is_installed("xx") is False
    assert fonts.remove_pack("xx") is False  # already gone


def test_unknown_pack_lists_the_available_ones(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "USER_FONTS_DIR", tmp_path / "fonts")
    fonts = _fixture_manifest(monkeypatch, b"a-font")
    with pytest.raises(fonts.FontDownloadError, match="no font pack 'zz'.*xx"):
        fonts.download_pack("zz")


def test_shipped_manifest_is_valid_and_matches_the_paths():
    """The committed font_packs.json parses and its packs align with the pack dirs."""
    from stellium import fonts

    packs = fonts.list_packs()
    assert set(packs) >= {"zh", "zh-hant"}
    for script, pack in packs.items():
        assert pack["fonts"], f"{script} has no fonts"
        assert all("sha256" in f and "asset" in f for f in pack["fonts"])
        assert pack["install_dir"].endswith(f"fonts/{script}")
