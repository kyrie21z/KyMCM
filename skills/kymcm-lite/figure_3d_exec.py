"""Deterministic PyVista hard-contract helpers for intrinsic-3D figures."""

from __future__ import annotations

import math
import os
import re
import struct
import tempfile
from pathlib import Path


EXECUTION_3D_ID = "kymcm-figure-3d-exec-v1"
MM_PER_INCH = 25.4
PNG_DPI = 600
CANVAS_MM = {
    "F-WIDE": (160.0, 60.0),
    "F-STANDARD": (160.0, 80.0),
    "F-TALL": (160.0, 105.0),
    "M-STANDARD": (128.0, 80.0),
}
ANTI_ALIASING_MODE = "ssaa"
APPROVED_CMAPS = {"sequential": "batlow", "diverging": "vik"}
FORBIDDEN_IMAGE_SUFFIXES = (
    ".svg", ".tif", ".tiff", ".jpg", ".jpeg", ".eps", ".ps", ".webp", ".bmp",
)


class Figure3DContractError(RuntimeError):
    """A formal intrinsic-3D figure violates the executable contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Figure3DContractError(message)


def _pyvista():
    try:
        import pyvista
        import vtk
    except ImportError as exc:
        raise Figure3DContractError(
            "PyVista and VTK are required for formal intrinsic-3D execution",
        ) from exc
    return pyvista


def canvas_inches(template: str) -> tuple[float, float]:
    try:
        return tuple(value / MM_PER_INCH for value in CANVAS_MM[template])
    except KeyError as exc:
        raise Figure3DContractError(f"unknown canvas template: {template}") from exc


def canvas_pixels(template: str) -> tuple[int, int]:
    return tuple(round(value * PNG_DPI) for value in canvas_inches(template))


def _vector3(value, *, name: str) -> tuple[float, float, float]:
    _require(not isinstance(value, (str, bytes)), f"{name} must be a finite numeric 3-vector")
    try:
        items = tuple(float(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise Figure3DContractError(f"{name} must be a finite numeric 3-vector") from exc
    _require(len(items) == 3 and all(math.isfinite(item) for item in items),
             f"{name} must be a finite numeric 3-vector")
    return items


def create_formal_plotter(template: str, *, shadows: bool = False, ssao: bool = False):
    """Create an off-screen, exact-pixel PyVista plotter with restrained defaults."""
    _require(isinstance(shadows, bool) and isinstance(ssao, bool),
             "shadows and ssao flags must be boolean")
    pixels = canvas_pixels(template)
    pv = _pyvista()
    try:
        plotter = pv.Plotter(
            off_screen=True,
            window_size=pixels,
            lighting="light kit",
        )
        plotter.set_background("white")
        plotter.enable_anti_aliasing(ANTI_ALIASING_MODE)
    except Exception as exc:
        if "plotter" in locals():
            plotter.close()
        raise Figure3DContractError(
            f"formal off-screen PyVista setup with {ANTI_ALIASING_MODE.upper()} failed",
        ) from exc
    if shadows:
        try:
            plotter.enable_shadows()
        except Exception as exc:
            plotter.close()
            raise Figure3DContractError("requested shadows are unavailable") from exc
    if ssao:
        try:
            plotter.enable_ssao()
        except Exception as exc:
            plotter.close()
            raise Figure3DContractError("requested SSAO is unavailable") from exc
    plotter._kymcm_figure_3d_meta = {
        "execution_id": EXECUTION_3D_ID,
        "template": template,
        "anti_aliasing": ANTI_ALIASING_MODE,
        "camera_explicit": False,
        "projection": None,
        "shadows": shadows,
        "ssao": ssao,
        "helper_title": False,
        "scalar_contracts": [],
    }
    return plotter


def apply_camera(
    plotter,
    *,
    position,
    focal_point,
    view_up,
    projection: str = "perspective",
) -> None:
    """Apply a reproducible camera chosen by the figure-specific entrypoint."""
    _require(projection in {"perspective", "parallel"}, "unknown camera projection mode")
    position = _vector3(position, name="camera position")
    focal_point = _vector3(focal_point, name="camera focal point")
    view_up = _vector3(view_up, name="camera view-up")
    direction = tuple(focal - eye for focal, eye in zip(focal_point, position))
    _require(sum(value * value for value in direction) > 0.0,
             "camera position and focal point must differ")
    _require(sum(value * value for value in view_up) > 0.0,
             "camera view-up vector must be non-zero")
    cross = (
        direction[1] * view_up[2] - direction[2] * view_up[1],
        direction[2] * view_up[0] - direction[0] * view_up[2],
        direction[0] * view_up[1] - direction[1] * view_up[0],
    )
    _require(sum(value * value for value in cross) > 1e-20,
             "camera view-up vector must not be parallel to the view direction")
    metadata = getattr(plotter, "_kymcm_figure_3d_meta", None)
    _require(isinstance(metadata, dict) and metadata.get("execution_id") == EXECUTION_3D_ID,
             "plotter was not created by create_formal_plotter()")
    plotter.camera_position = [position, focal_point, view_up]
    if projection == "parallel":
        plotter.enable_parallel_projection()
    else:
        plotter.disable_parallel_projection()
    applied = tuple(tuple(float(value) for value in vector) for vector in plotter.camera_position)
    metadata.update({
        "camera_explicit": True,
        "projection": projection,
        "camera": applied,
    })


def continuous_cmap_3d(kind: str):
    name = APPROVED_CMAPS.get(kind)
    _require(name is not None, f"unknown continuous color-map kind: {kind}")
    try:
        from cmcrameri import cm
        return getattr(cm, name)
    except (ImportError, AttributeError) as exc:
        raise Figure3DContractError(
            f"controlled cmcrameri color map unavailable: {name}",
        ) from exc


def surface_kwargs(
    plotter,
    *,
    kind: str,
    scalar_range,
    show_edges: bool = False,
    opacity: float = 1.0,
) -> dict[str, object]:
    """Return audited scalar-surface options without constructing a chart."""
    _require(isinstance(show_edges, bool), "show_edges must be boolean")
    try:
        opacity = float(opacity)
    except (TypeError, ValueError) as exc:
        raise Figure3DContractError("surface opacity must be finite and in (0, 1]") from exc
    _require(math.isfinite(opacity) and 0.0 < opacity <= 1.0,
             "surface opacity must be finite and in (0, 1]")
    try:
        limits = tuple(float(value) for value in scalar_range)
    except (TypeError, ValueError) as exc:
        raise Figure3DContractError("scalar range must contain two finite values") from exc
    _require(len(limits) == 2 and all(math.isfinite(value) for value in limits)
             and limits[0] < limits[1], "scalar range must increase between two finite values")
    cmap = continuous_cmap_3d(kind)
    metadata = getattr(plotter, "_kymcm_figure_3d_meta", None)
    _require(isinstance(metadata, dict) and metadata.get("execution_id") == EXECUTION_3D_ID,
             "plotter was not created by create_formal_plotter()")
    metadata["scalar_contracts"].append({
        "kind": kind,
        "cmap": APPROVED_CMAPS[kind],
        "range": limits,
        "show_edges": show_edges,
        "opacity": opacity,
    })
    return {
        "cmap": cmap,
        "clim": limits,
        "smooth_shading": True,
        "show_edges": show_edges,
        "opacity": opacity,
    }


def _background_is_white(plotter) -> bool:
    color = plotter.background_color
    values = getattr(color, "float_rgb", color)
    try:
        return all(abs(float(value) - 1.0) <= 1e-7 for value in values[:3])
    except (TypeError, ValueError):
        return False


def _stem_path(output_stem) -> Path:
    stem = Path(output_stem)
    _require(not stem.suffix, "output_stem must not include a file extension")
    forbidden = None
    if stem.parent.is_dir():
        forbidden = next((
            candidate.name[len(stem.name):]
            for candidate in stem.parent.iterdir()
            if candidate.name.startswith(stem.name)
            and candidate.name[len(stem.name):].lower() in FORBIDDEN_IMAGE_SUFFIXES
        ), None)
    _require(forbidden is None, f"forbidden same-stem formal format exists: {forbidden}")
    return stem


def audit_3d_contract(plotter, *, template: str, output_stem=None) -> tuple[str, ...]:
    """Audit the machine-safe final state before authoritative rendering."""
    expected = canvas_pixels(template)
    metadata = getattr(plotter, "_kymcm_figure_3d_meta", None)
    _require(isinstance(metadata, dict) and metadata.get("execution_id") == EXECUTION_3D_ID,
             "plotter was not created by create_formal_plotter()")
    _require(metadata.get("template") == template, "plotter template metadata does not match")
    _require(bool(plotter.off_screen), "formal 3D renderer must be off-screen")
    _require(tuple(int(value) for value in plotter.window_size) == expected,
             "3D window size does not match the physical template")
    _require(_background_is_white(plotter), "3D background must be pure white")
    gradient = getattr(getattr(plotter, "renderer", None), "GetGradientBackground", lambda: 0)()
    _require(not bool(gradient), "3D gradient background is prohibited")
    _require(metadata.get("anti_aliasing") == ANTI_ALIASING_MODE,
             "approved anti-aliasing was not enabled through the helper")
    _require(metadata.get("camera_explicit") is True, "formal 3D camera must be explicit")
    projection = metadata.get("projection")
    _require(projection in {"perspective", "parallel"}, "formal 3D projection is invalid")
    actual_parallel = bool(plotter.camera.GetParallelProjection())
    _require(actual_parallel == (projection == "parallel"),
             "camera projection no longer matches the explicit contract")
    actual_camera = tuple(tuple(float(value) for value in vector) for vector in plotter.camera_position)
    expected_camera = metadata.get("camera", ())
    _require(len(expected_camera) == 3 and all(
        abs(actual - expected) <= 1e-7
        for actual_vector, expected_vector in zip(actual_camera, expected_camera)
        for actual, expected in zip(actual_vector, expected_vector)
    ), "camera no longer matches the explicit contract")
    _require(metadata.get("helper_title") is False, "helper-owned title is prohibited")
    for contract in metadata.get("scalar_contracts", ()):
        _require(contract.get("cmap") in APPROVED_CMAPS.values(),
                 "unapproved helper scalar color map")
        limits = contract.get("range", ())
        _require(len(limits) == 2 and limits[0] < limits[1], "invalid helper scalar range")
    if output_stem is not None:
        _stem_path(output_stem)
    return (
        "template", "off-screen", "pixels", "background", "anti-aliasing",
        "camera", "projection", "scalar-contract",
    )


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    _require(header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR",
             "rendered PNG header is invalid")
    return struct.unpack(">II", header[16:24])


def _pdf_media_box(path: Path) -> tuple[float, float]:
    match = re.search(
        rb"/MediaBox\s*\[\s*[-+0-9.]+\s+[-+0-9.]+\s+([-+0-9.]+)\s+([-+0-9.]+)\s*\]",
        path.read_bytes(),
    )
    _require(match is not None, "packaged PDF MediaBox could not be inspected")
    return float(match.group(1)), float(match.group(2))


def _package_raster_pdf(png_path: Path, pdf_path: Path, *, template: str) -> None:
    try:
        import matplotlib.image as mpimg
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
    except ImportError as exc:
        raise Figure3DContractError(
            "Matplotlib is required only for exact-size 3D PDF packaging",
        ) from exc
    figure = Figure(figsize=canvas_inches(template), facecolor="white", frameon=False)
    FigureCanvasAgg(figure)
    axis = figure.add_axes((0.0, 0.0, 1.0, 1.0), frameon=False)
    axis.imshow(mpimg.imread(png_path), aspect="equal", interpolation="none")
    axis.set_axis_off()
    figure.savefig(
        pdf_path,
        format="pdf",
        facecolor="white",
        edgecolor="white",
        transparent=False,
        bbox_inches=None,
        pad_inches=0,
    )


def _replace_output_pair(temporary: tuple[Path, Path], final: tuple[Path, Path]) -> None:
    backups: dict[Path, Path] = {}
    installed: set[Path] = set()
    try:
        for destination in final:
            if destination.exists():
                handle, name = tempfile.mkstemp(prefix=f".{destination.name}-accepted-", dir=destination.parent)
                os.close(handle)
                backup = Path(name)
                backup.unlink()
                os.replace(destination, backup)
                backups[destination] = backup
        for source, destination in zip(temporary, final):
            os.replace(source, destination)
            installed.add(destination)
    except Exception:
        for destination in installed:
            destination.unlink(missing_ok=True)
        for destination, backup in backups.items():
            os.replace(backup, destination)
        raise
    finally:
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def save_formal_3d_figure(plotter, output_stem, *, template: str) -> dict[str, object]:
    """Render an authoritative PNG and package it in an exact-size PDF."""
    stem = _stem_path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    checks = audit_3d_contract(plotter, template=template, output_stem=stem)
    temporary: list[Path] = []
    try:
        for suffix in (".png", ".pdf"):
            handle, name = tempfile.mkstemp(prefix=f".{stem.name}-", suffix=suffix, dir=stem.parent)
            os.close(handle)
            temporary.append(Path(name))
        png_temp, pdf_temp = temporary
        plotter.screenshot(
            filename=str(png_temp),
            transparent_background=False,
            return_img=False,
            window_size=canvas_pixels(template),
        )
        expected_pixels = canvas_pixels(template)
        actual_pixels = _png_dimensions(png_temp)
        _require(not any(abs(left - right) > 1 for left, right in zip(actual_pixels, expected_pixels)),
                 "rendered PNG dimensions do not match 600 dpi-equivalent template output")
        _package_raster_pdf(png_temp, pdf_temp, template=template)
        expected_points = tuple(value * 72.0 for value in canvas_inches(template))
        media_box = _pdf_media_box(pdf_temp)
        _require(not any(abs(left - right) > 0.25 for left, right in zip(media_box, expected_points)),
                 "packaged PDF MediaBox does not match the physical template")
        pdf, png = stem.with_suffix(".pdf"), stem.with_suffix(".png")
        _replace_output_pair((pdf_temp, png_temp), (pdf, png))
        temporary.clear()
        return {
            "pdf": pdf,
            "png": png,
            "checks": checks,
            "pixels": actual_pixels,
            "media_box": media_box,
        }
    except Figure3DContractError:
        raise
    except Exception as exc:
        raise Figure3DContractError(f"formal 3D figure save failed: {exc}") from exc
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)
