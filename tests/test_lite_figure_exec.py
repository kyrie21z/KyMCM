from __future__ import annotations

import ast
import importlib.util
import inspect
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


os.environ.setdefault("MPLBACKEND", "Agg")
ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/kymcm-lite/figure_exec.py"


def load_module():
    spec = importlib.util.spec_from_file_location("kymcm_lite_figure_exec", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


figure_exec = load_module()


class LiteFigureExecParameterTests(unittest.TestCase):
    def test_execution_identity_and_physical_templates(self):
        self.assertEqual(figure_exec.EXECUTION_ID, "kymcm-figure-exec-v1")
        self.assertEqual(figure_exec.CANVAS_MM, {
            "F-WIDE": (160.0, 60.0), "F-STANDARD": (160.0, 80.0),
            "F-TALL": (160.0, 105.0), "M-STANDARD": (128.0, 80.0),
        })
        self.assertAlmostEqual(figure_exec.mm_to_inches(25.4), 1.0)
        self.assertEqual(figure_exec.figure_kwargs("F-WIDE")["layout"], "constrained")

    def test_module_import_is_lazy(self):
        code = (
            "import importlib.util,sys;"
            f"s=importlib.util.spec_from_file_location('lazy_exec',{str(MODULE_PATH)!r});"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "raise SystemExit('matplotlib' in sys.modules or 'cmcrameri' in sys.modules)"
        )
        result = subprocess.run([sys.executable, "-c", code], check=False)
        self.assertEqual(result.returncode, 0)

    def test_executor_remains_intentionally_small(self):
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        logical_statements = sum(isinstance(node, ast.stmt) for node in ast.walk(tree))
        self.assertLessEqual(logical_statements, 300)

    def test_typography_and_style_constants_are_exact(self):
        self.assertEqual(figure_exec.TYPOGRAPHY_PT, {
            "axis_label": 9.5, "colorbar_label": 9.5, "tick": 8.5,
            "legend": 8.5, "colorbar_tick": 8.5, "panel_marker": 9.5,
            "panel_label": 9.0, "numeric_annotation": 8.0, "minimum": 8.0,
        })
        expected = {
            "spine": 0.7, "major_tick_width": 0.6, "major_tick_length": 3.2,
            "minor_tick_width": 0.5, "minor_tick_length": 1.8, "grid": 0.4,
            "tick_direction": "out", "minor_grid": False, "axisbelow": True,
            "aux": 1.0, "secondary": 1.2, "primary": 1.5, "emphasis": 1.8,
            "reference": 0.85, "errorbar": 0.9, "max_normal": 2.0,
            "marker": 4.5, "emphasis_marker": 5.5, "marker_edge": 0.6,
            "single_bar": 0.68, "group_total": 0.78, "bar_edge": 0.6,
            "box_width": 0.52, "box_line": 0.9, "whisker": 0.8, "median": 1.4,
            "capsize": 2.5, "band_alpha": 0.16, "hgap_mm": 7.0,
            "vgap_mm": 8.0, "shared_axis_gap_mm": 5.5, "colorbar_gap_mm": 2.0,
            "png_dpi": 600, "transparent": False, "bbox_inches": None,
        }
        self.assertEqual(figure_exec.FIGURE_STYLE_V1, expected)

    def test_color_constants_are_exact_and_bounded(self):
        self.assertEqual(figure_exec.KY_MCM_QUALITATIVE_V1, (
            "#264653", "#E76F51", "#2A9D8F", "#7A77B9", "#8AB17D", "#E9C46A", "#F4A261",
        ))
        self.assertEqual(figure_exec.semantic_color("risk"), "#A61B29")
        self.assertEqual(figure_exec.NEUTRAL_COLORS["grid"], "#D9D9D9")
        self.assertEqual(figure_exec.GRID_ALPHA, 0.65)
        self.assertEqual(figure_exec.UNCERTAINTY_ALPHA_RANGE, (0.14, 0.18))
        self.assertEqual(figure_exec.UNCERTAINTY_ALPHA_DEFAULT, 0.16)
        self.assertEqual(figure_exec.PRIORITY_CORE_COLORS, 4)
        self.assertEqual(figure_exec.INFEASIBLE_HATCH, "///")
        self.assertEqual(len(figure_exec.qualitative_colors(7)), 7)
        with self.assertRaises(figure_exec.FigureContractError):
            figure_exec.qualitative_colors(8)

    def test_parameter_helpers_mirror_the_contract(self):
        self.assertEqual(figure_exec.marker_every(12), 1)
        self.assertEqual(figure_exec.marker_every(30), 2)
        self.assertEqual(figure_exec.marker_every(31), [])
        encoding = figure_exec.series_encoding(1, n_points=20)
        self.assertEqual((encoding["color"], encoding["marker"], encoding["markevery"]), ("#E76F51", "s", 2))
        self.assertEqual(encoding["linestyle"], (0, (5, 2)))
        self.assertEqual(figure_exec.series_encoding(1, n_points=31)["markevery"], [])
        self.assertEqual(figure_exec.scatter_kwargs(200), {"s": 21.0, "alpha": 0.85, "edgecolors": "#303030", "linewidths": 0.4})
        self.assertEqual(figure_exec.scatter_kwargs(1000)["s"], 11.0)
        self.assertEqual(figure_exec.scatter_kwargs(3000)["s"], 4.5)
        self.assertEqual(figure_exec.bar_width(1), 0.68)
        self.assertEqual(figure_exec.bar_width(3), 0.26)
        with self.assertRaises(figure_exec.FigureContractError):
            figure_exec.bar_width(8)
        self.assertEqual(figure_exec.boxplot_kwargs()["medianprops"]["linewidth"], 1.4)
        self.assertTrue(figure_exec.boxplot_kwargs()["showfliers"])
        self.assertFalse(figure_exec.boxplot_kwargs()["notch"])
        with self.assertRaises(figure_exec.FigureContractError):
            figure_exec.boxplot_kwargs(color="#123456")
        self.assertEqual(figure_exec.errorbar_kwargs(), {"elinewidth": 0.9, "capsize": 2.5, "capthick": 0.9})
        self.assertEqual(figure_exec.font_kwargs("panel_marker")["fontweight"], "semibold")
        self.assertEqual(figure_exec.font_kwargs("tick", script="latin")["fontfamily"], ["Tinos"])
        self.assertEqual(figure_exec.font_kwargs("tick", script="cjk")["fontfamily"], ["Noto Serif CJK SC"])
        self.assertEqual(
            figure_exec.font_kwargs("tick", script="mixed")["fontfamily"],
            ["Tinos", "Noto Serif CJK SC"],
        )
        with self.assertRaises(figure_exec.FigureContractError):
            figure_exec.font_kwargs("tick", script="unknown")

    def test_font_and_dependency_preflight_fail_closed(self):
        calls = []
        figure_exec.configure_matplotlib(font_resolver=lambda name: calls.append(name) or "/exact/font")
        self.assertEqual(calls, ["Tinos", "Noto Serif CJK SC"])
        with self.assertRaisesRegex(figure_exec.FigureContractError, "Tinos"):
            figure_exec.configure_matplotlib(font_resolver=lambda name: False if name == "Tinos" else True)
        with self.assertRaisesRegex(figure_exec.FigureContractError, "Noto Serif CJK SC"):
            figure_exec.configure_matplotlib(font_resolver=lambda name: False if name == "Noto Serif CJK SC" else True)
        with mock.patch.dict(sys.modules, {"cmcrameri": None}):
            with self.assertRaises(figure_exec.FigureContractError):
                figure_exec.continuous_cmap("sequential")
            with self.assertRaises(figure_exec.FigureContractError):
                figure_exec.configure_matplotlib(font_resolver=lambda _name: True)

    def test_controlled_color_maps_and_two_slope_normalization(self):
        self.assertEqual(figure_exec.continuous_cmap("sequential").name, "batlow")
        self.assertEqual(figure_exec.continuous_cmap("diverging").name, "vik")
        norm = figure_exec.diverging_norm(-1, 3, 0)
        self.assertEqual((norm.vmin, norm.vcenter, norm.vmax), (-3.0, 0, 3.0))
        nonsymmetric = figure_exec.diverging_norm(-1, 3, 0, symmetric=False)
        self.assertEqual((nonsymmetric.vmin, nonsymmetric.vmax), (-1.0, 3.0))


class LiteFigureExecArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        figure_exec.configure_matplotlib(font_resolver=lambda _name: "/ci/exact-font")
        import matplotlib.pyplot as plt
        cls.plt = plt

    def tearDown(self):
        self.plt.close("all")

    def compliant_figure(self, template="F-WIDE"):
        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs(template))
        ax.plot([0, 1, 2], [0, 1, 0], **figure_exec.series_encoding(0, n_points=3))
        ax.set_xlabel("x", **figure_exec.font_kwargs("axis_label"))
        ax.set_ylabel("y", **figure_exec.font_kwargs("axis_label"))
        figure_exec.apply_axis_style(ax, "line")
        return fig, ax

    def assert_audit_fails(self, mutate, phrase):
        fig, ax = self.compliant_figure()
        mutate(fig, ax)
        with self.assertRaisesRegex(figure_exec.FigureContractError, phrase):
            figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_compliant_frozen_figure_passes(self):
        fig, _ax = self.compliant_figure()
        checks = figure_exec.audit_hard_contract(fig, template="F-WIDE")
        self.assertIn("colors", checks)

    def test_long_series_disables_markers_in_real_matplotlib(self):
        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        line, = ax.plot(range(31), range(31), **figure_exec.series_encoding(0, n_points=31))
        self.assertEqual(line.get_markevery(), [])
        figure_exec.apply_axis_style(ax, "line")
        figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_boxplot_application_helper_is_matplotlib_compatible(self):
        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        ax.boxplot([[1, 2, 3], [2, 3, 4]], **figure_exec.boxplot_kwargs())
        figure_exec.apply_axis_style(ax, "box")
        figure_exec.audit_hard_contract(fig, template="F-WIDE")

        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        orientation = ({"orientation": "horizontal"} if "orientation" in inspect.signature(ax.boxplot).parameters
                       else {"vert": False})
        ax.boxplot([[1, 2, 3], [2, 3, 4]], **orientation, **figure_exec.boxplot_kwargs())
        figure_exec.apply_axis_style(ax, "box")
        figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_map_style_does_not_impose_cartesian_spines_or_grid(self):
        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        figure_exec.apply_axis_style(ax, "map")
        self.assertFalse(any(spine.get_visible() for spine in ax.spines.values()))
        self.assertFalse(any(line.get_visible() for line in (*ax.get_xgridlines(), *ax.get_ygridlines())))
        figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_suptitle_and_subplot_title_fail(self):
        self.assert_audit_fails(lambda fig, _ax: fig.suptitle("prohibited"), "suptitle")
        self.assert_audit_fails(lambda _fig, ax: ax.set_title("prohibited"), "title")
        self.assert_audit_fails(lambda _fig, ax: ax.set_title("prohibited", loc="left"), "title")
        self.assert_audit_fails(lambda _fig, ax: ax.set_title("prohibited", loc="right"), "title")

    def test_small_text_unknown_color_and_wide_line_fail(self):
        self.assert_audit_fails(
            lambda _fig, ax: ax.text(0.5, 0.5, "small", fontsize=7.9, color="#303030"),
            "below the 8 pt",
        )
        self.assert_audit_fails(
            lambda _fig, ax: ax.annotate("small", (0.5, 0.5), fontsize=6, color="#303030"),
            "below the 8 pt",
        )
        self.assert_audit_fails(lambda _fig, ax: ax.plot([0, 1], [1, 0], color="#123456"), "color")
        self.assert_audit_fails(
            lambda _fig, ax: ax.plot([0, 1], [1, 0], color="#264653", linewidth=2.1),
            "exceeds 2.0",
        )
        self.assert_audit_fails(
            lambda _fig, ax: ax.text(0.5, 0.5, "fallback", fontfamily="DejaVu Sans", color="#303030"),
            "font family",
        )
        self.assert_audit_fails(
            lambda _fig, ax: ax.text(0.5, 0.5, "fallback", fontfamily=["DejaVu Sans", "Tinos"], color="#303030"),
            "font family",
        )

    def test_declared_text_family_matches_visible_script(self):
        for value, family in (("中文：结果", "Tinos"), ("Accuracy 87.5%", "Noto Serif CJK SC")):
            self.assert_audit_fails(
                lambda _fig, ax, value=value, family=family: ax.text(
                    0.5, 0.5, value, fontfamily=family, color="#303030"
                ),
                "script routing",
            )
        for value, family in (
            ("模型 Accuracy = 87.5%", "Tinos"),
            ("模型 Accuracy = 87.5%", "Noto Serif CJK SC"),
        ):
            self.assert_audit_fails(
                lambda _fig, ax, value=value, family=family: ax.text(
                    0.5, 0.5, value, fontfamily=family, color="#303030"
                ),
                "script routing",
            )

        for value, script in (
            ("中文：结果", "cjk"),
            ("Accuracy 87.5%", "latin"),
            ("模型 Accuracy = 87.5%", "mixed"),
            (r"$f(x)=\alpha x^2+\beta$", "cjk"),
        ):
            fig, ax = self.compliant_figure()
            ax.text(0.5, 0.5, value, color="#303030", **figure_exec.font_kwargs("numeric_annotation", script=script))
            figure_exec.audit_hard_contract(fig, template="F-WIDE")
        self.assertEqual(self.plt.rcParams["mathtext.fontset"], "stix")

    def test_patch_width_and_nonwhite_background_fail(self):
        self.assert_audit_fails(
            lambda _fig, ax: ax.bar([0], [1], color="#264653", edgecolor="#303030", linewidth=5),
            "line width",
        )
        self.assert_audit_fails(lambda _fig, ax: ax.set_facecolor("#264653"), "background")
        self.assert_audit_fails(lambda fig, _ax: fig.set_facecolor("#264653"), "background")

    def test_locked_axis_and_artist_numbers_are_final_state_checks(self):
        self.assert_audit_fails(lambda _fig, ax: ax.spines["left"].set_linewidth(0.2), "spine")
        self.assert_audit_fails(lambda _fig, ax: ax.lines[0].set_linewidth(0.2), "line width")
        self.assert_audit_fails(lambda _fig, ax: ax.grid(True, linewidth=1.9), "grid width")
        self.assert_audit_fails(lambda _fig, ax: ax.grid(True, alpha=0.2), "grid alpha")
        self.assert_audit_fails(lambda _fig, ax: ax.grid(True, color="#264653"), "grid color")
        self.assert_audit_fails(lambda _fig, ax: ax.grid(True, linestyle="--"), "grid line style")
        self.assert_audit_fails(lambda _fig, ax: ax.tick_params(direction="in"), "tick direction")
        self.assert_audit_fails(lambda _fig, ax: ax.set_axisbelow(False), "axis-below")
        self.assert_audit_fails(lambda _fig, ax: ax.spines["left"].set_color("#264653"), "spine color")
        self.assert_audit_fails(lambda _fig, ax: ax.lines[0].set_markersize(3.0), "marker size")
        self.assert_audit_fails(lambda _fig, ax: ax.lines[0].set_markeredgewidth(0.2), "marker edge")

        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        ax.bar([0], [1], width=figure_exec.bar_width(1), color="#264653")
        figure_exec.apply_axis_style(ax, "bar")
        self.assertEqual(ax.patches[0].get_linewidth(), 0.6)
        figure_exec.audit_hard_contract(fig, template="F-WIDE")

        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        ax.bar([0], [1], width=0.2, color="#264653")
        figure_exec.apply_axis_style(ax, "bar")
        with self.assertRaisesRegex(figure_exec.FigureContractError, "bar width"):
            figure_exec.audit_hard_contract(fig, template="F-WIDE")

        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        ax.boxplot([[1, 2, 3]], widths=0.2, patch_artist=True,
                   boxprops={"facecolor": "#264653", "edgecolor": "#303030", "linewidth": 0.9},
                   whiskerprops={"color": "#303030", "linewidth": 0.8},
                   capprops={"color": "#303030", "linewidth": 0.8},
                   medianprops={"color": "#303030", "linewidth": 1.4},
                   flierprops={"marker": "o", "markersize": 3.0, "alpha": 0.55,
                               "color": "#264653", "markeredgecolor": "#264653", "markerfacecolor": "none"})
        figure_exec.apply_axis_style(ax, "box")
        with self.assertRaisesRegex(figure_exec.FigureContractError, "box width"):
            figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_approved_contour_and_contourf_color_maps_pass(self):
        import numpy as np
        x = np.linspace(-1, 1, 8)
        xx, yy = np.meshgrid(x, x)
        zz = xx * xx + yy * yy
        for method in ("contour", "contourf"):
            with self.subTest(method=method):
                fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
                getattr(ax, method)(xx, yy, zz, cmap=figure_exec.continuous_cmap("sequential"))
                figure_exec.apply_axis_style(ax, "heatmap")
                figure_exec.audit_hard_contract(fig, template="F-WIDE")
                self.plt.close(fig)

    def test_wrong_canvas_fails_before_formal_saver_normalization(self):
        fig, _ax = self.compliant_figure()
        fig.set_size_inches(4, 3)
        with self.assertRaisesRegex(figure_exec.FigureContractError, "size"):
            figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_unstyled_axis_and_uncontrolled_cmap_fail(self):
        def add_unstyled(fig, _ax):
            fig.add_subplot(122)
        self.assert_audit_fails(add_unstyled, "not passed through")

        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        ax.imshow([[0, 1], [1, 0]], cmap="viridis")
        figure_exec.apply_axis_style(ax, "heatmap")
        with self.assertRaisesRegex(figure_exec.FigureContractError, "color map"):
            figure_exec.audit_hard_contract(fig, template="F-WIDE")

        fig, ax = self.plt.subplots(**figure_exec.figure_kwargs("F-WIDE"))
        ax.scatter([0, 1], [0, 1], c=[0, 1], cmap=figure_exec.continuous_cmap("sequential"),
                   edgecolors="#123456")
        figure_exec.apply_axis_style(ax, "scatter")
        with self.assertRaisesRegex(figure_exec.FigureContractError, "color"):
            figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_legend_and_unicode_minus_defaults_are_locked(self):
        import matplotlib
        self.assertFalse(matplotlib.rcParams["axes.unicode_minus"])
        self.assertFalse(matplotlib.rcParams["legend.frameon"])
        self.assertEqual(matplotlib.rcParams["legend.handlelength"], 1.6)
        fig, ax = self.compliant_figure()
        ax.lines[0].set_label("series")
        ax.legend()
        figure_exec.audit_hard_contract(fig, template="F-WIDE")

    def test_formal_save_writes_only_pdf_and_png_at_exact_geometry(self):
        fig, _ax = self.compliant_figure("F-WIDE")
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "formal"
            result = figure_exec.save_formal_figure(fig, stem, template="F-WIDE")
            self.assertEqual({path.name for path in Path(directory).iterdir()}, {"formal.pdf", "formal.png"})
            self.assertEqual(result["pdf"], stem.with_suffix(".pdf"))
            with result["png"].open("rb") as stream:
                stream.seek(16)
                dimensions = struct.unpack(">II", stream.read(8))
            expected = tuple(round(value * 600) for value in figure_exec.canvas_inches("F-WIDE"))
            self.assertTrue(all(abs(left - right) <= 1 for left, right in zip(dimensions, expected)))
            points = figure_exec._pdf_media_box(result["pdf"])
            expected_points = tuple(value * 72 for value in figure_exec.canvas_inches("F-WIDE"))
            self.assertTrue(all(abs(left - right) <= 0.25 for left, right in zip(points, expected_points)))

    def test_forbidden_same_stem_format_fails_without_deletion(self):
        fig, _ax = self.compliant_figure()
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "formal"
            forbidden = stem.with_suffix(".svg")
            forbidden.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(figure_exec.FigureContractError, "forbidden"):
                figure_exec.save_formal_figure(fig, stem, template="F-WIDE")
            self.assertEqual(forbidden.read_text(encoding="utf-8"), "keep")

    def test_pair_replace_failure_restores_both_existing_outputs(self):
        fig, _ax = self.compliant_figure()
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "formal"
            pdf, png = stem.with_suffix(".pdf"), stem.with_suffix(".png")
            pdf.write_bytes(b"accepted-pdf")
            png.write_bytes(b"accepted-png")
            real_replace = os.replace
            failed = False

            def fail_second(source, destination):
                nonlocal failed
                source_path, destination_path = Path(source), Path(destination)
                if not failed and source_path.suffix == ".png" and destination_path == png:
                    failed = True
                    raise OSError("injected pair replacement failure")
                return real_replace(source, destination)

            with mock.patch.object(figure_exec.os, "replace", side_effect=fail_second):
                with self.assertRaisesRegex(figure_exec.FigureContractError, "save failed"):
                    figure_exec.save_formal_figure(fig, stem, template="F-WIDE")
            self.assertEqual(pdf.read_bytes(), b"accepted-pdf")
            self.assertEqual(png.read_bytes(), b"accepted-png")

    def test_core_runtime_never_imports_optional_execution_module(self):
        runtime = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "skills/kymcm-lite/scripts").rglob("*.py")
        )
        self.assertNotIn("figure_exec", runtime)
        self.assertNotIn("cmcrameri", runtime)
        self.assertNotIn("matplotlib", runtime)


if __name__ == "__main__":
    unittest.main()
