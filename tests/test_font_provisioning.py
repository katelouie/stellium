"""Font provisioning — the resolution layer (spec FONTS_AND_CHART_I18N.md, Phase A1).

The load-bearing property: a font placed under ``~/.stellium/fonts/`` is found by the
render font path with no ``with_font()`` call, exactly as a downloaded ephemeris is found.
Everything the downloader will add later is plumbing around this.
"""

from __future__ import annotations

import shutil
from pathlib import Path

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
