from __future__ import annotations

import builtins
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/kymcm-lite/figure_3d_exec.py"
BUNDLE_PATH = ROOT / "skills/kymcm-lite/figure_bundle.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


figure_3d = load_module("kymcm_lite_figure_3d_exec", MODULE_PATH)
figure_bundle = load_module("kymcm_lite_figure_bundle_for_3d", BUNDLE_PATH)


class FakeCamera:
    def __init__(self):
        self.parallel = False

    def GetParallelProjection(self):
        return int(self.parallel)


class FakeColor:
    float_rgb = (1.0, 1.0, 1.0)


class FakePlotter:
    def __init__(self, *, off_screen=True, window_size=(100, 100), lighting="light kit"):
        self.off_screen = off_screen
        self.window_size = list(window_size)
        self.lighting = lighting
        self.camera = FakeCamera()
        self.background_color = FakeColor()
        self.closed = False
        self.shadow_calls = 0
        self.ssao_calls = 0
        self.aa_calls = []

    def set_background(self, _color):
        self.background_color = FakeColor()

    def enable_anti_aliasing(self, mode):
        self.aa_calls.append(mode)

    def enable_shadows(self):
        self.shadow_calls += 1

    def enable_ssao(self):
        self.ssao_calls += 1

    def enable_parallel_projection(self):
        self.camera.parallel = True

    def disable_parallel_projection(self):
        self.camera.parallel = False

    def close(self):
        self.closed = True

    def screenshot(self, filename, **_kwargs):
        Path(filename).write_bytes(b"temporary-png")


class FakePyVista:
    Plotter = FakePlotter


class Figure3DUnitTests(unittest.TestCase):
    def plotter(self, template="F-WIDE"):
        with mock.patch.object(figure_3d, "_pyvista", return_value=FakePyVista):
            return figure_3d.create_formal_plotter(template)

    def test_import_is_lazy_and_missing_dependencies_fail_closed(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        prefix = source.split("def _pyvista():", 1)[0]
        self.assertNotIn("import pyvista", prefix)
        self.assertNotIn("import vtk", prefix)
        real_import = builtins.__import__

        def fail_optional(name, *args, **kwargs):
            if name in {"pyvista", "vtk"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=fail_optional):
            with self.assertRaisesRegex(figure_3d.Figure3DContractError, "PyVista and VTK"):
                figure_3d._pyvista()

    def test_canvas_math_matches_frozen_templates(self):
        expected = {
            "F-WIDE": (3780, 1417),
            "F-STANDARD": (3780, 1890),
            "F-TALL": (3780, 2480),
            "M-STANDARD": (3024, 1890),
        }
        self.assertEqual({name: figure_3d.canvas_pixels(name) for name in expected}, expected)
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "unknown canvas"):
            figure_3d.canvas_pixels("UNKNOWN")

    def test_plotter_defaults_are_offscreen_white_ssaa_and_not_decorative(self):
        plotter = self.plotter()
        self.assertTrue(plotter.off_screen)
        self.assertEqual(tuple(plotter.window_size), (3780, 1417))
        self.assertEqual(plotter.aa_calls, ["ssaa"])
        self.assertEqual(plotter.shadow_calls, 0)
        self.assertEqual(plotter.ssao_calls, 0)
        self.assertFalse(plotter._kymcm_figure_3d_meta["shadows"])
        self.assertFalse(plotter._kymcm_figure_3d_meta["ssao"])

    def test_camera_requires_finite_non_degenerate_explicit_values(self):
        valid = dict(position=(3, 2, 1), focal_point=(0, 0, 0), view_up=(0, 0, 1))
        for replacement in (
            {"position": (1, 2)},
            {"position": (float("nan"), 2, 1)},
            {"focal_point": (3, 2, 1)},
            {"view_up": (0, 0, 0)},
            {"view_up": (3, 2, 1)},
        ):
            with self.subTest(replacement=replacement):
                plotter = self.plotter()
                values = valid | replacement
                with self.assertRaises(figure_3d.Figure3DContractError):
                    figure_3d.apply_camera(plotter, **values)

        plotter = self.plotter()
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "projection"):
            figure_3d.apply_camera(plotter, **valid, projection="orthographic")

    def test_camera_metadata_and_projection_are_audited(self):
        plotter = self.plotter()
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "camera"):
            figure_3d.audit_3d_contract(plotter, template="F-WIDE")
        figure_3d.apply_camera(
            plotter,
            position=(3, 2, 1),
            focal_point=(0, 0, 0),
            view_up=(0, 0, 1),
            projection="parallel",
        )
        checks = figure_3d.audit_3d_contract(plotter, template="F-WIDE")
        self.assertIn("camera", checks)
        self.assertTrue(plotter.camera.GetParallelProjection())
        plotter.camera_position = [(4, 2, 1), (0, 0, 0), (0, 0, 1)]
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "camera"):
            figure_3d.audit_3d_contract(plotter, template="F-WIDE")

    def test_output_stem_and_forbidden_formats_fail_closed(self):
        plotter = self.plotter()
        figure_3d.apply_camera(
            plotter, position=(3, 2, 1), focal_point=(0, 0, 0), view_up=(0, 0, 1),
        )
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "formal"
            with self.assertRaisesRegex(figure_3d.Figure3DContractError, "extension"):
                figure_3d.audit_3d_contract(plotter, template="F-WIDE", output_stem=stem.with_suffix(".png"))
            forbidden = stem.with_suffix(".svg")
            forbidden.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(figure_3d.Figure3DContractError, "forbidden"):
                figure_3d.audit_3d_contract(plotter, template="F-WIDE", output_stem=stem)
            self.assertEqual(forbidden.read_text(encoding="utf-8"), "keep")

    def test_scalar_helpers_restrict_maps_and_ranges(self):
        plotter = self.plotter()
        for kind, name in (("sequential", "batlow"), ("diverging", "vik")):
            with self.subTest(kind=kind):
                options = figure_3d.surface_kwargs(plotter, kind=kind, scalar_range=(-1, 2))
                self.assertEqual(options["cmap"].name, name)
                self.assertEqual(options["clim"], (-1.0, 2.0))
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "unknown continuous"):
            figure_3d.continuous_cmap_3d("rainbow")
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "scalar range"):
            figure_3d.surface_kwargs(plotter, kind="sequential", scalar_range=(1, 1))
        with self.assertRaisesRegex(figure_3d.Figure3DContractError, "opacity"):
            figure_3d.surface_kwargs(plotter, kind="sequential", scalar_range=(0, 1), opacity="opaque")

    def test_executor_contains_no_matplotlib_3d_route_or_chart_templates(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("mplot3d", source.lower())
        self.assertNotIn("Axes3D", source)
        self.assertNotIn('projection="3d"', source)
        for forbidden_api in ("make_surface_chart", "plot_trajectory", "make_3d_bar"):
            self.assertNotIn(forbidden_api, source)

    def test_visual_pair_replace_failure_preserves_accepted_outputs(self):
        plotter = self.plotter()
        figure_3d.apply_camera(
            plotter, position=(3, 2, 1), focal_point=(0, 0, 0), view_up=(0, 0, 1),
        )
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "formal"
            pdf, png = stem.with_suffix(".pdf"), stem.with_suffix(".png")
            pdf.write_bytes(b"accepted-pdf")
            png.write_bytes(b"accepted-png")
            expected_points = tuple(value * 72.0 for value in figure_3d.canvas_inches("F-WIDE"))
            real_replace = os.replace
            failed = False

            def package(_png, destination, *, template):
                self.assertEqual(template, "F-WIDE")
                destination.write_bytes(b"temporary-pdf")

            def fail_second(source, destination):
                nonlocal failed
                source_path, destination_path = Path(source), Path(destination)
                if not failed and source_path.suffix == ".png" and destination_path == png:
                    failed = True
                    raise OSError("injected pair replacement failure")
                return real_replace(source, destination)

            with mock.patch.object(figure_3d, "_png_dimensions", return_value=(3780, 1417)), \
                 mock.patch.object(figure_3d, "_pdf_media_box", return_value=expected_points), \
                 mock.patch.object(figure_3d, "_package_raster_pdf", side_effect=package), \
                 mock.patch.object(figure_3d.os, "replace", side_effect=fail_second):
                with self.assertRaisesRegex(figure_3d.Figure3DContractError, "save failed"):
                    figure_3d.save_formal_3d_figure(plotter, stem, template="F-WIDE")
            self.assertEqual(pdf.read_bytes(), b"accepted-pdf")
            self.assertEqual(png.read_bytes(), b"accepted-png")


@unittest.skipUnless(
    os.environ.get("KYMCM_RUN_PYVISTA_INTEGRATION") == "1",
    "set KYMCM_RUN_PYVISTA_INTEGRATION=1 with optional 3D requirements installed",
)
class Figure3DIntegrationTests(unittest.TestCase):
    def test_real_offscreen_render_exact_geometry_and_bundle(self):
        pv = figure_3d._pyvista()
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "surface"
            source = stem.with_suffix(".py")
            source.write_text(
                "from pathlib import Path\nstem = Path(__file__).with_suffix(\"\")\n",
                encoding="utf-8",
            )
            plotter = figure_3d.create_formal_plotter("F-WIDE")
            try:
                if os.environ.get("VTK_DEFAULT_OPENGL_WINDOW") == "vtkEGLRenderWindow":
                    self.assertEqual(type(plotter.ren_win).__name__, "vtkEGLRenderWindow")
                mesh = pv.Sphere(theta_resolution=16, phi_resolution=16)
                mesh["height"] = mesh.points[:, 2]
                options = figure_3d.surface_kwargs(
                    plotter, kind="sequential", scalar_range=(-0.5, 0.5),
                )
                plotter.add_mesh(mesh, scalars="height", **options)
                figure_3d.apply_camera(
                    plotter,
                    position=(3.2, 2.4, 2.0),
                    focal_point=(0.0, 0.0, 0.0),
                    view_up=(0.0, 0.0, 1.0),
                    projection="perspective",
                )
                rendered = figure_3d.save_formal_3d_figure(plotter, stem, template="F-WIDE")
            finally:
                plotter.close()
            figure_bundle.write_figure_note(
                stem,
                title="球面高度分布",
                caption="表面颜色表示标准化高度，范围为 -0.5 至 0.5。",
            )
            bundle = figure_bundle.validate_figure_bundle(stem, source_path=source)
            self.assertEqual(rendered["pixels"], (3780, 1417))
            expected_points = tuple(value * 72.0 for value in figure_3d.canvas_inches("F-WIDE"))
            self.assertTrue(all(abs(left - right) <= 0.25 for left, right in zip(rendered["media_box"], expected_points)))
            self.assertEqual({path.name for path in Path(directory).iterdir()}, {
                "surface.pdf", "surface.png", "surface.py", "surface.txt",
            })
            self.assertEqual(set(bundle), {"pdf", "png", "py", "txt"})


if __name__ == "__main__":
    unittest.main()
