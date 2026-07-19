import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "kymcm-full" / "scripts"
FIGURE_CLI = SCRIPTS / "figure_manager.py"
sys.path.insert(0, str(SCRIPTS))

from visualization.audit import audit_workspace
from visualization.brief import load_figure_plan
from visualization.gallery import generate_gallery
import visualization.renderer as renderer_module
from visualization.renderer import TEMPLATE_REGISTRY, render_all, render_figure
from visualization.selection import select_template
from visualization.theme import FigureTheme


class FigureSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name) / "CUMCM_Workspace"
        (self.workspace / "figures").mkdir(parents=True)
        (self.workspace / "results").mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def write_plan(self, figures: list[dict]) -> Path:
        path = self.workspace / "figures" / "figure_plan.yaml"
        path.write_text(
            yaml.safe_dump({"figures": figures}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def brief(figure_id: str, evidence: str, family: str, mapping: dict) -> dict:
        return {
            "id": figure_id,
            "problem": 1,
            "claim": f"Synthetic evidence for {figure_id}",
            "evidence": [evidence],
            "chart_family": family,
            "paper_section": "model_results",
            "target_width": "double",
            "language": "en",
            "caption_draft": f"Synthetic {family} example.",
            "mapping": mapping,
            "x_label": "Input (unit)",
            "y_label": "Response (unit)",
        }

    def test_brief_requires_fields_and_rejects_workspace_escape(self):
        source = self.workspace / "results" / "data.csv"
        source.write_text("x,y\n1,2\n", encoding="utf-8")
        valid = self.brief("q1_line", "results/data.csv", "line_with_band", {"x": "x", "y": "y"})
        self.write_plan([valid])
        plan = load_figure_plan(self.workspace)
        self.assertEqual(plan[0]["id"], "q1_line")

        invalid = dict(valid)
        invalid.pop("claim")
        self.write_plan([invalid])
        with self.assertRaisesRegex(ValueError, "claim"):
            load_figure_plan(self.workspace)

        escaped = dict(valid, evidence=["../outside.csv"])
        self.write_plan([escaped])
        with self.assertRaisesRegex(ValueError, "inside workspace"):
            load_figure_plan(self.workspace)

        second = self.workspace / "results" / "second.csv"
        second.write_text("x,y\n1,3\n", encoding="utf-8")
        multiple = dict(valid, evidence=["results/data.csv", "results/second.csv"])
        self.write_plan([multiple])
        with self.assertRaisesRegex(ValueError, "exactly one CSV evidence"):
            load_figure_plan(self.workspace)

    def test_plan_rejects_non_csv_and_accepts_case_insensitive_csv_suffix(self):
        for suffix in ("txt", "json", "xlsx"):
            with self.subTest(suffix=suffix):
                source = self.workspace / "results" / f"data.{suffix}"
                source.write_text("x,y\n1,2\n", encoding="utf-8")
                self.write_plan([
                    self.brief(
                        "q1_line", f"results/data.{suffix}",
                        "line_with_band", {"x": "x", "y": "y"},
                    )
                ])
                result = subprocess.run(
                    [
                        sys.executable, str(FIGURE_CLI), "--workspace",
                        str(self.workspace), "plan",
                    ],
                    text=True, capture_output=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("exactly one CSV evidence file", result.stderr)

        for suffix in ("csv", "CSV"):
            with self.subTest(suffix=suffix):
                source = self.workspace / "results" / f"data.{suffix}"
                source.write_text("x,y\n1,2\n", encoding="utf-8")
                self.write_plan([
                    self.brief(
                        "q1_line", f"results/data.{suffix}",
                        "line_with_band", {"x": "x", "y": "y"},
                    )
                ])
                result = subprocess.run(
                    [
                        sys.executable, str(FIGURE_CLI), "--workspace",
                        str(self.workspace), "plan",
                    ],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_chart_selection_uses_explicit_family_and_bounded_rules(self):
        explicit = {"chart_family": "sensitivity_curve"}
        self.assertEqual(select_template(explicit, {}), "sensitivity_curve")
        self.assertEqual(
            select_template({"chart_family": "auto"}, {"purpose": "prediction"}),
            "actual_vs_predicted",
        )
        self.assertEqual(
            select_template(
                {"chart_family": "auto"},
                {"purpose": "trend", "has_uncertainty": True},
            ),
            "line_with_band",
        )
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            select_template({"chart_family": "radar"}, {})

    def test_theme_has_stable_profiles_and_font_warning(self):
        theme = FigureTheme(language="zh", target_width="single")
        self.assertEqual(theme.size_inches, (3.35, 2.55))
        self.assertEqual(theme.dpi, 300)
        self.assertIn("proposed", theme.colors)
        with theme.context() as warnings:
            self.assertIsInstance(warnings, list)

    def test_zh_theme_prefers_microsoft_yahei_when_cjk_fonts_coexist(self):
        installed = [
            SimpleNamespace(name="Noto Sans CJK SC"),
            SimpleNamespace(name="Microsoft YaHei"),
            SimpleNamespace(name="DejaVu Sans"),
        ]
        with mock.patch(
            "visualization.theme.font_manager.fontManager.ttflist", installed,
        ):
            with FigureTheme(language="zh").context():
                self.assertEqual(plt.rcParams["font.sans-serif"][0], "Microsoft YaHei")

    def test_en_theme_keeps_english_fallback_when_cjk_fonts_coexist(self):
        installed = [
            SimpleNamespace(name="Microsoft YaHei"),
            SimpleNamespace(name="Noto Sans CJK SC"),
            SimpleNamespace(name="DejaVu Sans"),
        ]
        with mock.patch(
            "visualization.theme.font_manager.fontManager.ttflist", installed,
        ):
            with FigureTheme(language="en").context():
                self.assertEqual(plt.rcParams["font.sans-serif"][0], "DejaVu Sans")

    def test_semantic_styles_and_unknown_fallback_are_order_independent(self):
        theme = FigureTheme()
        proposed = theme.style_for_series("Proposed", 9)
        baseline = theme.style_for_series("Baseline", 0)
        alternative = theme.style_for_series("Alternative", 0)
        self.assertEqual(proposed["color"], "#0072B2")
        self.assertEqual(baseline["color"], "#6B7280")
        self.assertEqual(alternative["color"], "#E69F00")
        self.assertEqual(theme.style_for_series("本文方法", 3), proposed)
        self.assertEqual(theme.style_for_series("基准", 3), baseline)

        first = theme.style_for_series("Model Z", 0)
        reordered = theme.style_for_series("Model Z", 8)
        self.assertEqual(first, reordered)
        self.assertIn("linestyle", first)
        self.assertIn("marker", first)

        explicit = theme.style_for_series(
            "Method X", 5, explicit_role="proposed"
        )
        self.assertEqual(explicit, proposed)

    def test_grouped_templates_use_semantic_styles_not_data_order(self):
        theme = FigureTheme()
        brief = {"x_label": "x", "y_label": "y"}
        reversed_groups = pd.DataFrame({
            "x": [0, 1, 0, 1], "y": [1, 2, 2, 3],
            "group": ["Baseline", "Baseline", "Proposed", "Proposed"],
        })
        bars = pd.DataFrame({
            "category": ["A", "B", "A", "B"], "value": [1, 2, 2, 3],
            "group": ["Baseline", "Baseline", "Proposed", "Proposed"],
        })
        prediction = pd.DataFrame({
            "actual": [1, 2, 1, 2], "predicted": [1.1, 1.9, 1.0, 2.1],
            "group": ["Baseline", "Baseline", "Proposed", "Proposed"],
        })
        with theme.context():
            line_fig, _, _ = TEMPLATE_REGISTRY["line_with_band"](
                reversed_groups, {"x": "x", "y": "y", "group": "group"}, brief, theme
            )
            sensitivity_fig, _, _ = TEMPLATE_REGISTRY["sensitivity_curve"](
                reversed_groups,
                {"parameter": "x", "response": "y", "scenario": "group"},
                brief, theme,
            )
            bar_fig, _, _ = TEMPLATE_REGISTRY["grouped_bar_error"](
                bars, {"category": "category", "value": "value", "group": "group"},
                brief, theme,
            )
            prediction_fig, _, _ = TEMPLATE_REGISTRY["actual_vs_predicted"](
                prediction,
                {"actual": "actual", "predicted": "predicted", "group": "group"},
                brief, theme,
            )
        for figure in (line_fig, sensitivity_fig):
            styles = {
                line.get_label(): (line.get_color(), line.get_linestyle(), line.get_marker())
                for line in figure.axes[0].lines if line.get_label() in {"Baseline", "Proposed"}
            }
            self.assertEqual(styles["Baseline"][0], "#6B7280")
            self.assertEqual(styles["Proposed"][0], "#0072B2")
        bar_styles = {
            container.get_label(): to_hex(container.patches[0].get_facecolor()).upper()
            for container in bar_fig.axes[0].containers
            if container.get_label() in {"Baseline", "Proposed"}
        }
        self.assertEqual(bar_styles, {"Baseline": "#6B7280", "Proposed": "#0072B2"})
        scatter_styles = {
            collection.get_label(): to_hex(collection.get_facecolor()[0]).upper()
            for collection in prediction_fig.axes[0].collections
            if collection.get_label() in {"Baseline", "Proposed"}
        }
        self.assertEqual(scatter_styles, {"Baseline": "#6B7280", "Proposed": "#0072B2"})
        for figure in (line_fig, sensitivity_fig, bar_fig, prediction_fig):
            plt.close(figure)

    def test_series_roles_override_labels_in_template(self):
        theme = FigureTheme()
        data = pd.DataFrame({
            "x": [0, 1, 0, 1], "y": [1, 2, 2, 3],
            "group": ["Model Y", "Model Y", "Model X", "Model X"],
        })
        brief = {
            "x_label": "x", "y_label": "y",
            "series_roles": {"Model X": "proposed", "Model Y": "baseline"},
        }
        with theme.context():
            figure, _, _ = TEMPLATE_REGISTRY["line_with_band"](
                data, {"x": "x", "y": "y", "group": "group"}, brief, theme
            )
        colors = {line.get_label(): line.get_color() for line in figure.axes[0].lines}
        self.assertEqual(colors["Model X"], "#0072B2")
        self.assertEqual(colors["Model Y"], "#6B7280")
        plt.close(figure)

    def test_builtin_template_text_respects_zh_and_en(self):
        data = pd.DataFrame({
            "predicted": [1.0, 2.0, 3.0], "residual": [-0.1, 0.0, 0.1],
            "a": [1.0, 2.0, 3.0], "b": [3.0, 2.0, 1.0],
            "parameter": [0.8, 1.0, 1.2], "response": [2.0, 2.2, 2.4],
            "baseline": [2.1, 2.1, 2.1],
        })
        for language, expected in (
            ("zh", {"residual": "残差", "count": "频数", "correlation": "皮尔逊相关系数", "baseline": "基准值"}),
            ("en", {"residual": "Residual", "count": "Count", "correlation": "Pearson correlation", "baseline": "Baseline"}),
        ):
            with self.subTest(language=language):
                theme = FigureTheme(language=language)
                brief = {}
                with theme.context():
                    residual_fig, _, _ = TEMPLATE_REGISTRY["residual_diagnostics"](
                        data, {"predicted": "predicted", "residual": "residual"}, brief, theme
                    )
                    correlation_fig, _, _ = TEMPLATE_REGISTRY["correlation_heatmap"](
                        data, {"columns": ["a", "b"]}, brief, theme
                    )
                    sensitivity_fig, _, _ = TEMPLATE_REGISTRY["sensitivity_curve"](
                        data,
                        {"parameter": "parameter", "response": "response", "baseline": "baseline"},
                        brief, theme,
                    )
                self.assertEqual(residual_fig.axes[1].get_xlabel(), expected["residual"])
                self.assertEqual(residual_fig.axes[1].get_ylabel(), expected["count"])
                self.assertEqual(correlation_fig.axes[-1].get_ylabel(), expected["correlation"])
                labels = [line.get_label() for line in sensitivity_fig.axes[0].lines]
                self.assertIn(expected["baseline"], labels)
                for figure in (residual_fig, correlation_fig, sensitivity_fig):
                    plt.close(figure)

    def test_every_template_rejects_missing_required_mapping(self):
        data = pd.DataFrame({"x": [1.0, 2.0], "y": [2.0, 3.0]})
        brief = {"x_label": "x", "y_label": "y"}
        theme = FigureTheme()
        with theme.context():
            for template_id, renderer in TEMPLATE_REGISTRY.items():
                with self.subTest(template=template_id):
                    with self.assertRaisesRegex(ValueError, "mapping"):
                        renderer(data, {}, brief, theme)

    def test_line_band_requires_paired_uncertainty_columns(self):
        source = self.workspace / "results" / "one_bound.csv"
        source.write_text("x,y,lower\n1,2,1.5\n2,3,2.5\n", encoding="utf-8")
        figure = self.brief(
            "one_bound", "results/one_bound.csv", "line_with_band",
            {"x": "x", "y": "y", "lower": "lower"},
        )
        self.write_plan([figure])
        with self.assertRaisesRegex(ValueError, "lower and upper"):
            render_figure(self.workspace, "one_bound")

    def test_renderer_rejects_output_directory_symlink_escape(self):
        figures = self._write_synthetic_sources()[:1]
        self.write_plan(figures)
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        vector = self.workspace / "figures" / "vector"
        vector.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "output directory"):
            render_figure(self.workspace, "line")

    def _write_synthetic_sources(self) -> list[dict]:
        x = np.arange(8, dtype=float)
        trend = pd.DataFrame({
            "x": np.tile(x, 2),
            "y": np.r_[1.2 * x + 2, 1.0 * x + 2.5],
            "lower": np.r_[1.2 * x + 1.5, 1.0 * x + 2.0],
            "upper": np.r_[1.2 * x + 2.5, 1.0 * x + 3.0],
            "group": ["Proposed"] * 8 + ["Baseline"] * 8,
        })
        trend.to_csv(self.workspace / "results" / "trend.csv", index=False)

        bars = pd.DataFrame({
            "category": ["A", "B", "C"] * 2,
            "value": [0.82, 0.76, 0.91, 0.71, 0.73, 0.84],
            "error": [0.03, 0.02, 0.02, 0.04, 0.03, 0.03],
            "group": ["Proposed"] * 3 + ["Baseline"] * 3,
        })
        bars.to_csv(self.workspace / "results" / "bars.csv", index=False)

        actual = np.linspace(2, 20, 40)
        predicted = actual * 0.94 + np.sin(actual) * 0.8 + 0.7
        prediction = pd.DataFrame({
            "actual": actual, "predicted": predicted,
            "residual": actual - predicted,
        })
        prediction.to_csv(self.workspace / "results" / "prediction.csv", index=False)

        correlation = pd.DataFrame({
            "alpha": x,
            "beta": x * 0.7 + np.cos(x),
            "gamma": np.sin(x) + x * 0.2,
        })
        correlation.to_csv(self.workspace / "results" / "correlation.csv", index=False)

        sensitivity = pd.DataFrame({
            "parameter": np.tile(np.linspace(0.5, 1.5, 9), 2),
            "response": np.r_[np.linspace(10, 12, 9), np.linspace(9.5, 12.5, 9)],
            "scenario": ["Proposed"] * 9 + ["Alternative"] * 9,
        })
        sensitivity.to_csv(self.workspace / "results" / "sensitivity.csv", index=False)

        return [
            self.brief("line", "results/trend.csv", "line_with_band", {
                "x": "x", "y": "y", "lower": "lower", "upper": "upper", "group": "group",
            }),
            self.brief("bars", "results/bars.csv", "grouped_bar_error", {
                "category": "category", "value": "value", "error": "error", "group": "group",
            }),
            self.brief("prediction", "results/prediction.csv", "actual_vs_predicted", {
                "actual": "actual", "predicted": "predicted",
            }),
            self.brief("residuals", "results/prediction.csv", "residual_diagnostics", {
                "predicted": "predicted", "residual": "residual",
            }),
            self.brief("correlation", "results/correlation.csv", "correlation_heatmap", {
                "columns": ["alpha", "beta", "gamma"],
            }),
            self.brief("sensitivity", "results/sensitivity.csv", "sensitivity_curve", {
                "parameter": "parameter", "response": "response", "scenario": "scenario",
            }),
        ]

    def test_six_templates_render_three_formats_and_manifests(self):
        figures = self._write_synthetic_sources()
        self.write_plan(figures)
        manifests = render_all(self.workspace)
        self.assertEqual(len(manifests), 6)
        for manifest in manifests:
            self.assertEqual(manifest["audit_status"], "pending")
            self.assertEqual(manifest["renderer_version"], "1.0")
            self.assertTrue(manifest["source_data_sha256"])
            self.assertEqual(set(manifest["output_sha256"]), {"svg", "pdf", "png"})
            self.assertEqual(set(manifest["output_sizes"]), {"svg", "pdf", "png"})
            self.assertEqual(manifest["preferred_asset"], manifest["output_paths"]["pdf"])
            for format_name, relative in manifest["output_paths"].items():
                path = self.workspace / relative
                self.assertTrue(path.is_file(), relative)
                self.assertGreater(path.stat().st_size, 100)
                self.assertEqual(
                    manifest["output_sha256"][format_name],
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
                self.assertEqual(manifest["output_sizes"][format_name], path.stat().st_size)
            png = self.workspace / manifest["output_paths"]["png"]
            with Image.open(png) as image:
                self.assertGreaterEqual(image.width, 1500)
                self.assertGreaterEqual(image.height, 700)
            manifest_path = self.workspace / "figures" / "manifests" / f"{manifest['figure_id']}.json"
            self.assertTrue(manifest_path.is_file())

        report = audit_workspace(self.workspace)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(report["figures"]), 6)
        self.assertTrue(all(item["status"] == "pass" for item in report["figures"]))
        gallery = generate_gallery(self.workspace)
        html = gallery.read_text(encoding="utf-8")
        self.assertIn("Synthetic evidence for line", html)
        self.assertIn("preview/line.png", html)
        self.assertNotIn("<script", html.lower())
        self.assertIn("min(100%, 360px)", html)

        first = manifests[0]
        repeated = render_figure(self.workspace, first["figure_id"])
        stable_fields = (
            "figure_id", "claim", "template", "source_data", "source_data_sha256",
            "renderer_version", "theme_version", "target_width", "output_paths",
            "output_dimensions", "mapping", "metadata", "paper_section", "label",
            "caption_draft", "preferred_asset",
        )
        self.assertEqual(
            {field: first[field] for field in stable_fields},
            {field: repeated[field] for field in stable_fields},
        )

    def test_renderer_rejects_nan_and_audit_detects_damage(self):
        source = self.workspace / "results" / "bad.csv"
        source.write_text("x,y\n1,2\n2,NaN\n", encoding="utf-8")
        figure = self.brief("bad", "results/bad.csv", "line_with_band", {"x": "x", "y": "y"})
        self.write_plan([figure])
        with self.assertRaisesRegex(ValueError, "finite"):
            render_figure(self.workspace, "bad")

        figures = self._write_synthetic_sources()[:1]
        self.write_plan(figures)
        manifest = render_figure(self.workspace, "line")
        png = self.workspace / manifest["output_paths"]["png"]
        with Image.open(png) as image:
            image.resize((120, 80)).save(png, dpi=(72, 72))
        report = audit_workspace(self.workspace)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("resolution" in issue for issue in report["figures"][0]["errors"]))

        render_figure(self.workspace, "line")
        source = self.workspace / "results" / "trend.csv"
        source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertTrue(any("hash" in issue for issue in report["figures"][0]["errors"]))

        source.unlink()
        report = audit_workspace(self.workspace)
        self.assertTrue(any("source data missing" in issue for issue in report["figures"][0]["errors"]))

        self._write_synthetic_sources()
        render_figure(self.workspace, "line")
        svg = self.workspace / "figures" / "vector" / "line.svg"
        svg.unlink()
        report = audit_workspace(self.workspace)
        self.assertTrue(any("svg output missing" in issue for issue in report["figures"][0]["errors"]))

    def test_audit_rejects_corrupt_output_formats_and_hash_tampering(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        corruptions = {
            "pdf": b"not a pdf",
            "svg": b"not xml",
            "png": b"not a png",
        }
        for format_name, payload in corruptions.items():
            with self.subTest(format=format_name):
                manifest = render_figure(self.workspace, "line")
                path = self.workspace / manifest["output_paths"][format_name]
                path.write_bytes(payload)
                report = audit_workspace(self.workspace)
                errors = " ".join(report["figures"][0]["errors"]).lower()
                self.assertEqual(report["status"], "fail")
                self.assertIn(format_name, errors)
                self.assertTrue("invalid" in errors or "hash mismatch" in errors)

        manifest = render_figure(self.workspace, "line")
        pdf = self.workspace / manifest["output_paths"]["pdf"]
        pdf.write_bytes(pdf.read_bytes() + b"\n")
        report = audit_workspace(self.workspace)
        self.assertTrue(any("pdf output hash mismatch" in issue.lower() for issue in report["figures"][0]["errors"]))

    def test_audit_checks_actual_png_dimensions_and_preferred_pdf(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        png = self.workspace / manifest["output_paths"]["png"]
        with Image.open(png) as image:
            image.resize((600, 300)).save(png, format="PNG", dpi=(300, 300))
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["output_sha256"]["png"] = hashlib.sha256(png.read_bytes()).hexdigest()
        manifest["output_sizes"]["png"] = png.stat().st_size
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = audit_workspace(self.workspace)
        errors = " ".join(report["figures"][0]["errors"]).lower()
        self.assertIn("dimensions mismatch", errors)
        self.assertIn("resolution", errors)

        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        manifest["preferred_asset"] = manifest["output_paths"]["svg"]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertTrue(any("preferred_asset" in issue for issue in report["figures"][0]["errors"]))

    def test_audit_rejects_manifest_with_multiple_sources(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        manifest["source_data"].append("results/bars.csv")
        manifest["source_data_sha256"]["results/bars.csv"] = hashlib.sha256(
            (self.workspace / "results" / "bars.csv").read_bytes()
        ).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertTrue(any("exactly one source" in issue for issue in report["figures"][0]["errors"]))

    def test_audit_rejects_non_csv_manifest_source(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        source = self.workspace / "results" / "trend.txt"
        source.write_bytes((self.workspace / "results" / "trend.csv").read_bytes())
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        manifest["source_data"] = ["results/trend.txt"]
        manifest["source_data_sha256"] = {
            "results/trend.txt": hashlib.sha256(source.read_bytes()).hexdigest()
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any(
            "source data must be a CSV file: results/trend.txt" in issue
            for issue in report["figures"][0]["errors"]
        ))

    def test_audit_reports_malformed_manifest_instead_of_crashing(self):
        manifests = self.workspace / "figures" / "manifests"
        manifests.mkdir(parents=True)
        malformed = manifests / "malformed.json"
        malformed.write_text("[]", encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("manifest must be an object" in issue for issue in report["figures"][0]["errors"]))

        malformed.write_text(json.dumps({
            "figure_id": "malformed", "source_data": ["results/x.csv"],
            "source_data_sha256": [], "output_paths": [], "output_sha256": [],
            "output_sizes": [], "output_dimensions": [], "metadata": [],
            "warnings": {}, "target_width": "double",
        }), encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("must be an object" in issue for issue in report["figures"][0]["errors"]))

    def test_audit_rejects_unknown_target_width(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        manifest["target_width"] = "bogus"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = audit_workspace(self.workspace)
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("target_width" in issue for issue in report["figures"][0]["errors"]))

    def test_failed_rerender_preserves_previous_outputs_and_manifest(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        before_manifest = manifest_path.read_bytes()
        before_outputs = {
            name: (self.workspace / relative).read_bytes()
            for name, relative in manifest["output_paths"].items()
        }
        original_savefig = plt.Figure.savefig
        calls = 0

        def fail_on_png(figure, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("synthetic PNG failure")
            return original_savefig(figure, *args, **kwargs)

        with mock.patch.object(plt.Figure, "savefig", new=fail_on_png):
            with self.assertRaisesRegex(OSError, "synthetic PNG failure"):
                render_figure(self.workspace, "line")
        self.assertEqual(manifest_path.read_bytes(), before_manifest)
        for name, relative in manifest["output_paths"].items():
            self.assertEqual((self.workspace / relative).read_bytes(), before_outputs[name])

    def test_temp_output_validation_failure_preserves_previous_generation(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        before = {manifest_path: manifest_path.read_bytes()}
        before.update({
            self.workspace / relative: (self.workspace / relative).read_bytes()
            for relative in manifest["output_paths"].values()
        })
        trend = self.workspace / "results" / "trend.csv"
        data = pd.read_csv(trend)
        data["y"] = data["y"] + 20
        data.to_csv(trend, index=False)
        original_validate_output = renderer_module.validate_output

        def fail_pdf_temp_validation(path, format_name):
            if path.name == "line.pdf.tmp":
                raise ValueError("synthetic PDF temp validation failure")
            return original_validate_output(path, format_name)

        with mock.patch.object(
            renderer_module, "validate_output", new=fail_pdf_temp_validation,
        ):
            with self.assertRaisesRegex(ValueError, "synthetic PDF temp validation failure"):
                render_figure(self.workspace, "line")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_no_transaction_files()

    def test_failed_output_replacement_rolls_back_all_formal_assets(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        original_replace = Path.replace

        for failed_format in ("svg", "pdf", "png"):
            with self.subTest(format=failed_format):
                before_manifest = manifest_path.read_bytes()
                before_outputs = {
                    name: (self.workspace / relative).read_bytes()
                    for name, relative in manifest["output_paths"].items()
                }

                def fail_during_output_replace(path, target):
                    if path.name == f"line.{failed_format}.tmp":
                        raise OSError(
                            f"synthetic {failed_format} replacement failure"
                        )
                    return original_replace(path, target)

                with mock.patch.object(
                    Path, "replace", new=fail_during_output_replace,
                ):
                    with self.assertRaisesRegex(
                        OSError, f"synthetic {failed_format} replacement failure",
                    ):
                        render_figure(self.workspace, "line")
                self.assertEqual(manifest_path.read_bytes(), before_manifest)
                for name, relative in manifest["output_paths"].items():
                    self.assertEqual(
                        (self.workspace / relative).read_bytes(), before_outputs[name]
                    )
                self.assert_no_transaction_files()

    def test_manifest_temp_write_failure_preserves_previous_generation(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        before = {manifest_path: manifest_path.read_bytes()}
        before.update({
            self.workspace / relative: (self.workspace / relative).read_bytes()
            for relative in manifest["output_paths"].values()
        })
        trend = self.workspace / "results" / "trend.csv"
        data = pd.read_csv(trend)
        data["y"] = data["y"] + 20
        data.to_csv(trend, index=False)
        original_write_text = Path.write_text

        def fail_manifest_temp_write(path, *args, **kwargs):
            if path.name == "line.json.tmp":
                raise OSError("synthetic manifest temp write failure")
            return original_write_text(path, *args, **kwargs)

        with mock.patch.object(Path, "write_text", new=fail_manifest_temp_write):
            with self.assertRaisesRegex(OSError, "synthetic manifest temp write failure"):
                render_figure(self.workspace, "line")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_no_transaction_files()

    def test_manifest_replace_failure_rolls_back_previous_generation(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        before = {manifest_path: manifest_path.read_bytes()}
        before.update({
            self.workspace / relative: (self.workspace / relative).read_bytes()
            for relative in manifest["output_paths"].values()
        })
        trend = self.workspace / "results" / "trend.csv"
        data = pd.read_csv(trend)
        data["y"] = data["y"] + 20
        data.to_csv(trend, index=False)
        original_replace = Path.replace

        def fail_manifest_replace(path, target):
            if path.name == "line.json.tmp" and Path(target).name == "line.json":
                raise OSError("synthetic manifest replacement failure")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", new=fail_manifest_replace):
            with self.assertRaisesRegex(OSError, "synthetic manifest replacement failure"):
                render_figure(self.workspace, "line")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_no_transaction_files()

    def test_rollback_continues_after_transient_backup_restore_failure(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        manifest_path = self.workspace / "figures" / "manifests" / "line.json"
        before = {manifest_path: manifest_path.read_bytes()}
        before.update({
            self.workspace / relative: (self.workspace / relative).read_bytes()
            for relative in manifest["output_paths"].values()
        })
        trend = self.workspace / "results" / "trend.csv"
        data = pd.read_csv(trend)
        data["y"] = data["y"] + 20
        data.to_csv(trend, index=False)
        original_replace = Path.replace
        failed_backup_restore = False

        def fail_manifest_and_one_backup_restore(path, target):
            nonlocal failed_backup_restore
            if path.name == "line.json.tmp" and Path(target).name == "line.json":
                raise OSError("synthetic manifest replacement failure")
            if path.name == "line.svg.bak" and not failed_backup_restore:
                failed_backup_restore = True
                raise OSError("synthetic transient backup restore failure")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", new=fail_manifest_and_one_backup_restore):
            with self.assertRaisesRegex(OSError, "synthetic manifest replacement failure"):
                render_figure(self.workspace, "line")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_no_transaction_files()

    def test_rollback_restore_failure_preserves_original_exception_and_cleans_transactions(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        manifest = render_figure(self.workspace, "line")
        trend = self.workspace / "results" / "trend.csv"
        data = pd.read_csv(trend)
        data["y"] = data["y"] + 20
        data.to_csv(trend, index=False)
        original_replace = Path.replace
        original_copy2 = renderer_module.shutil.copy2

        def fail_manifest_and_backup_replace(path, target):
            if path.name == "line.json.tmp" and Path(target).name == "line.json":
                raise OSError("synthetic manifest replacement failure")
            if path.name == "line.svg.bak":
                raise OSError("synthetic backup replace failure")
            return original_replace(path, target)

        def fail_svg_backup_copy(source, destination, *args, **kwargs):
            if Path(source).name == "line.svg.bak":
                raise OSError("synthetic backup copy failure")
            return original_copy2(source, destination, *args, **kwargs)

        with (
            mock.patch.object(Path, "replace", new=fail_manifest_and_backup_replace),
            mock.patch.object(renderer_module.shutil, "copy2", new=fail_svg_backup_copy),
        ):
            with self.assertRaisesRegex(
                OSError, "synthetic manifest replacement failure",
            ) as raised:
                render_figure(self.workspace, "line")
        self.assertTrue(any("failed to restore svg output" in note for note in raised.exception.__notes__))
        self.assert_no_transaction_files()

    def test_first_render_manifest_replace_failure_leaves_no_generation(self):
        self.write_plan(self._write_synthetic_sources()[:1])
        original_replace = Path.replace

        def fail_manifest_replace(path, target):
            if path.name == "line.json.tmp" and Path(target).name == "line.json":
                raise OSError("synthetic first manifest replacement failure")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", new=fail_manifest_replace):
            with self.assertRaisesRegex(OSError, "synthetic first manifest replacement failure"):
                render_figure(self.workspace, "line")
        for path in (
            self.workspace / "figures" / "vector" / "line.svg",
            self.workspace / "figures" / "vector" / "line.pdf",
            self.workspace / "figures" / "preview" / "line.png",
            self.workspace / "figures" / "manifests" / "line.json",
        ):
            self.assertFalse(path.exists(), path)
        self.assert_no_transaction_files()

    def assert_no_transaction_files(self):
        leftovers = [
            path for path in self.workspace.rglob("*")
            if path.name.endswith((".tmp", ".bak"))
        ]
        self.assertEqual(leftovers, [])

    def test_cli_lists_renders_audits_and_builds_gallery(self):
        figures = self._write_synthetic_sources()[:1]
        self.write_plan(figures)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for args in (("list",), ("render", "line"), ("audit",), ("gallery",)):
            result = subprocess.run(
                [sys.executable, str(FIGURE_CLI), "--workspace", str(self.workspace), *args],
                text=True, capture_output=True, env=env, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.workspace / "figures" / "gallery.html").is_file())

    def test_gallery_drops_tampered_nonlocal_asset_links(self):
        manifests = self.workspace / "figures" / "manifests"
        manifests.mkdir(parents=True)
        (manifests / "unsafe.json").write_text(json.dumps({
            "figure_id": "unsafe",
            "claim": "<script>alert(1)</script>",
            "template": "line_with_band",
            "source_data": [],
            "paper_section": "results",
            "caption_draft": "unsafe links are removed",
            "audit_status": "fail",
            "output_paths": {
                "png": "javascript:alert(1)",
                "svg": "../../outside.svg",
                "pdf": "https://example.com/file.pdf",
            },
        }), encoding="utf-8")
        gallery = generate_gallery(self.workspace)
        html = gallery.read_text(encoding="utf-8")
        self.assertNotIn("javascript:", html)
        self.assertNotIn("https://example.com", html)
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;alert", html)


if __name__ == "__main__":
    unittest.main()
