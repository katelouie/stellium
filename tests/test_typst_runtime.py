"""The shared Typst runtime — mostly a guard against the paths drifting apart again.

Three subsystems compile PDFs through Typst (report, planner, atlas) and each had
grown its own copy of "find the fonts". All three disagreed and two were wrong:

    typst_render._font_paths()   -> stellium/data/fonts        ✅ packaged
    planner._get_font_dirs()     -> <repo>/assets/fonts        ❌ not in the wheel
    atlas._get_font_dirs()       -> <repo>/src/assets/fonts    ❌ never existed at all

The atlas copy was one `dirname()` short, because it sits a directory deeper than the
planner it was copied from — so its fonts had never worked in *any* environment, and
nobody noticed, because Typst silently substitutes rather than complaining. A missing
font is not an error; it is just a different-looking PDF. That is exactly the kind of
bug a test has to catch, because a human never will.
"""

from pathlib import Path

import pytest

from stellium.presentation import typst_runtime as rt

PACKAGE_ROOT = Path(rt.__file__).resolve().parent.parent


class TestTheBundledPathsResolve:
    def test_font_path_is_the_packaged_font_directory(self):
        paths = rt.font_paths()
        assert paths, "no font directory found — the bundled fonts are the whole point"

        fonts = Path(paths[0])
        assert fonts == PACKAGE_ROOT / "data" / "fonts"
        assert fonts.is_dir()

    def test_the_font_directory_actually_contains_fonts(self):
        """`font_paths()` returns [] for a directory that does not exist, and Typst
        accepts an empty list without complaint — so "it returned something" is not
        enough. This is the assertion the atlas needed and never had.
        """
        fonts = Path(rt.font_paths()[0])
        faces = list(fonts.glob("*.ttf")) + list(fonts.glob("*.otf"))
        assert len(faces) >= 10, f"only {len(faces)} font faces bundled"

    def test_theme_dir_is_the_packaged_design_system(self):
        theme_dir = Path(rt.theme_dir())
        assert theme_dir == PACKAGE_ROOT / "presentation" / "typst_theme"
        assert theme_dir.is_dir()

    def test_every_design_system_module_exists(self):
        theme_dir = Path(rt.theme_dir())
        missing = [f for f in rt.DESIGN_SYSTEM if not (theme_dir / f).is_file()]
        assert not missing, f"design-system modules missing: {missing}"

    def test_the_paths_do_not_depend_on_the_working_directory(
        self, tmp_path, monkeypatch
    ):
        """They are package-relative. The planner and atlas copies walked up to the
        *repo root*, which is meaningless once installed.
        """
        before = (rt.font_paths(), rt.theme_dir())
        monkeypatch.chdir(tmp_path)
        assert (rt.font_paths(), rt.theme_dir()) == before


class TestEveryConsumerUsesTheSameFonts:
    """The point of the module: one answer, not three."""

    def test_report_planner_and_atlas_all_resolve_the_same_font_path(self):
        from stellium.planner import renderer as planner_renderer
        from stellium.presentation import typst_render
        from stellium.visualization.atlas import renderer as atlas_renderer

        # None of them may carry a private font-path helper any more.
        for module in (typst_render, planner_renderer, atlas_renderer):
            assert not hasattr(module, "_font_paths"), (
                f"{module.__name__} has grown its own _font_paths again"
            )
            assert not hasattr(module, "_get_font_dirs"), (
                f"{module.__name__} has grown its own _get_font_dirs again"
            )

    def test_no_module_reaches_for_a_repo_root_assets_directory(self):
        """`<repo>/assets/fonts` exists in a checkout and not in the wheel — which is
        why a planner installed from PyPI silently lost its typography.
        """
        import inspect

        from stellium.planner import renderer as planner_renderer
        from stellium.visualization.atlas import renderer as atlas_renderer

        for module in (planner_renderer, atlas_renderer):
            source = inspect.getsource(module)
            assert '"assets"' not in source, (
                f"{module.__name__} still points at the repo-root assets/ directory, "
                "which is not in the wheel"
            )


class TestThemeValidation:
    def test_a_known_theme_passes_through(self):
        assert rt.validate_theme("sepia") == "sepia"

    def test_an_unknown_theme_is_rejected_by_name(self):
        with pytest.raises(ValueError, match="Unknown theme"):
            rt.validate_theme("puce")

    def test_every_theme_has_a_label_and_a_wheel_mapping(self):
        for theme in rt.THEMES:
            assert theme in rt.THEME_LABELS
            assert theme in rt.THEME_WHEEL


class TestMaterializeSvgs:
    def test_inline_svg_becomes_a_file_reference(self, tmp_path):
        sections = [{"kind": "svg", "svg_content": "<svg/>"}]
        rt.materialize_svgs(sections, str(tmp_path))

        assert "svg_content" not in sections[0], "the inline markup should be dropped"
        written = tmp_path / sections[0]["svg_file"]
        assert written.read_text() == "<svg/>"

    def test_it_recurses_into_compound_subsections(self, tmp_path):
        sections = [
            {
                "kind": "compound",
                "sections": [
                    {"kind": "svg", "svg_content": "<svg id='a'/>"},
                    {"kind": "svg", "svg_content": "<svg id='b'/>"},
                ],
            }
        ]
        rt.materialize_svgs(sections, str(tmp_path))

        subs = sections[0]["sections"]
        names = {s["svg_file"] for s in subs}
        assert len(names) == 2, "each SVG needs its own filename"
        assert all((tmp_path / n).exists() for n in names)

    def test_a_section_with_no_svg_is_left_alone(self, tmp_path):
        sections = [{"kind": "table", "rows": []}]
        rt.materialize_svgs(sections, str(tmp_path))
        assert sections == [{"kind": "table", "rows": []}]


@pytest.mark.slow
class TestTypstDocument:
    def test_it_copies_the_design_system_into_the_project_root(self):
        with rt.TypstDocument("report.typ", "house") as doc:
            root = Path(doc.root)
            for module in rt.DESIGN_SYSTEM:
                assert (root / module).is_file()
            assert (root / "report.typ").is_file()

    def test_extra_templates_are_copied_too(self):
        """The planner brings its own component module."""
        with rt.TypstDocument(
            "planner.typ", "house", extra_templates=("planner_components.typ",)
        ) as doc:
            assert (Path(doc.root) / "planner_components.typ").is_file()

    def test_the_root_is_cleaned_up_on_exit(self):
        with rt.TypstDocument("report.typ", "house") as doc:
            root = Path(doc.root)
            assert root.is_dir()
        assert not root.exists()

    def test_an_unknown_theme_fails_before_any_work_happens(self):
        with pytest.raises(ValueError, match="Unknown theme"):
            rt.TypstDocument("report.typ", "puce")

    def test_add_file_puts_content_in_the_root(self):
        with rt.TypstDocument("report.typ", "house") as doc:
            name = doc.add_file("chart.svg", content="<svg/>")
            assert (Path(doc.root) / name).read_text() == "<svg/>"
