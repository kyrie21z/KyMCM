"""Deterministic hard-contract helpers for formal KyMCM Lite figures."""

from __future__ import annotations

import os, re, struct, tempfile
from pathlib import Path
from typing import Callable


EXECUTION_ID = "kymcm-figure-exec-v1"


class FigureContractError(RuntimeError):
    """Raised when a formal figure violates a machine-safe Lite rule."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FigureContractError(message)


MM_PER_INCH = 25.4
CANVAS_MM = {"F-WIDE": (160.0, 60.0), "F-STANDARD": (160.0, 80.0),
             "F-TALL": (160.0, 105.0), "M-STANDARD": (128.0, 80.0)}
TYPOGRAPHY_PT = {
    "axis_label": 9.5, "colorbar_label": 9.5, "tick": 8.5, "legend": 8.5,
    "colorbar_tick": 8.5, "panel_marker": 9.5, "panel_label": 9.0,
    "numeric_annotation": 8.0, "minimum": 8.0,
}
FONT_CJK, FONT_LATIN, MATHTEXT_FONTSET, PDF_FONTTYPE = "Noto Serif CJK SC", "Tinos", "stix", 42

FIGURE_STYLE_V1 = {
    "spine": 0.7, "major_tick_width": 0.6, "major_tick_length": 3.2,
    "minor_tick_width": 0.5, "minor_tick_length": 1.8, "grid": 0.4,
    "tick_direction": "out", "minor_grid": False, "axisbelow": True,
    "aux": 1.0, "secondary": 1.2, "primary": 1.5, "emphasis": 1.8,
    "reference": 0.85, "errorbar": 0.9, "max_normal": 2.0,
    "marker": 4.5, "emphasis_marker": 5.5, "marker_edge": 0.6,
    "single_bar": 0.68, "group_total": 0.78, "bar_edge": 0.6,
    "box_width": 0.52, "box_line": 0.9, "whisker": 0.8, "median": 1.4,
    "capsize": 2.5, "band_alpha": 0.16, "hgap_mm": 7.0, "vgap_mm": 8.0,
    "shared_axis_gap_mm": 5.5, "colorbar_gap_mm": 2.0, "png_dpi": 600,
    "transparent": False, "bbox_inches": None,
}
MARKER_SEQUENCE, LINE_STYLES = (("o", "s", "^", "D", "v", "P", "X"),
                                ("-", (0, (5, 2)), (0, (5, 2, 1.5, 2)), (0, (1.2, 1.8))))

KY_MCM_QUALITATIVE_V1 = (
    "#264653", "#E76F51", "#2A9D8F", "#7A77B9", "#8AB17D", "#E9C46A", "#F4A261",
)
SEMANTIC_COLORS = {
    "primary": "#264653", "comparison": "#E76F51", "baseline": "#7A7A7A",
    "risk": "#A61B29", "infeasible": "#303030", "missing": "#D9D9D9",
    "background": "#FFFFFF",
}
NEUTRAL_COLORS = {
    "text": "#303030", "spine": "#303030", "reference": "#7A7A7A", "grid": "#D9D9D9",
}
GRID_ALPHA, UNCERTAINTY_ALPHA_DEFAULT = 0.65, 0.16
UNCERTAINTY_ALPHA_RANGE = (0.14, 0.18)
MAX_QUALITATIVE_CATEGORIES, PRIORITY_CORE_COLORS, INFEASIBLE_HATCH = 7, 4, "///"
_SUPPORTED_AXIS_KINDS = {"line", "bar", "box", "scatter", "forest", "hbar", "heatmap", "image", "map"}
_CONFIGURED_FONT_RESOLVER, _CONFIGURED = None, False


def mm_to_inches(mm: float) -> float:
    return float(mm) / MM_PER_INCH


def canvas_inches(template: str) -> tuple[float, float]:
    try:
        return tuple(mm_to_inches(value) for value in CANVAS_MM[template])
    except KeyError as exc:
        raise FigureContractError(f"unknown canvas template: {template}") from exc


def figure_kwargs(template: str) -> dict[str, object]:
    return {"figsize": canvas_inches(template), "layout": "constrained", "facecolor": "white"}


def _matplotlib():
    try:
        import matplotlib
    except ImportError as exc:
        raise FigureContractError("Matplotlib is required for formal figure execution") from exc
    return matplotlib


def _cmcrameri():
    try:
        from cmcrameri import cm
        cm.batlow, cm.vik
    except (ImportError, AttributeError) as exc:
        raise FigureContractError("controlled cmcrameri batlow/vik maps are required") from exc
    return cm


def _verify_fonts(resolver: Callable[[str], object] | None) -> None:
    if resolver is None:
        from matplotlib import font_manager

        resolver = lambda name: font_manager.findfont(name, fallback_to_default=False)
    for name in (FONT_LATIN, FONT_CJK):
        try:
            resolved = resolver(name)
        except Exception as exc:
            raise FigureContractError(f"required font unavailable: {name}") from exc
        _require(resolved is not None and resolved is not False and resolved != "",
                 f"required font unavailable: {name}")


def configure_matplotlib(*, font_resolver: Callable[[str], object] | None = None) -> None:
    matplotlib = _matplotlib()
    _cmcrameri()
    _verify_fonts(font_resolver)
    matplotlib.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "savefig.transparent": False, "savefig.bbox": None, "axes.axisbelow": True,
        "font.family": [FONT_LATIN, FONT_CJK], "mathtext.fontset": MATHTEXT_FONTSET,
        "pdf.fonttype": PDF_FONTTYPE, "axes.unicode_minus": False,
        "axes.edgecolor": NEUTRAL_COLORS["spine"],
        "axes.labelcolor": NEUTRAL_COLORS["text"], "text.color": NEUTRAL_COLORS["text"],
        "xtick.color": NEUTRAL_COLORS["text"], "ytick.color": NEUTRAL_COLORS["text"],
        "axes.linewidth": FIGURE_STYLE_V1["spine"], "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.width": FIGURE_STYLE_V1["major_tick_width"],
        "ytick.major.width": FIGURE_STYLE_V1["major_tick_width"],
        "xtick.major.size": FIGURE_STYLE_V1["major_tick_length"],
        "ytick.major.size": FIGURE_STYLE_V1["major_tick_length"],
        "xtick.minor.width": FIGURE_STYLE_V1["minor_tick_width"],
        "ytick.minor.width": FIGURE_STYLE_V1["minor_tick_width"],
        "xtick.minor.size": FIGURE_STYLE_V1["minor_tick_length"],
        "ytick.minor.size": FIGURE_STYLE_V1["minor_tick_length"],
        "axes.prop_cycle": matplotlib.cycler(color=KY_MCM_QUALITATIVE_V1),
        "lines.linewidth": FIGURE_STYLE_V1["primary"], "lines.markersize": FIGURE_STYLE_V1["marker"],
        "grid.color": NEUTRAL_COLORS["grid"], "grid.alpha": GRID_ALPHA,
        "grid.linewidth": FIGURE_STYLE_V1["grid"], "grid.linestyle": "-",
        "axes.labelsize": TYPOGRAPHY_PT["axis_label"], "xtick.labelsize": TYPOGRAPHY_PT["tick"],
        "ytick.labelsize": TYPOGRAPHY_PT["tick"], "legend.fontsize": TYPOGRAPHY_PT["legend"],
        "legend.frameon": False, "legend.handlelength": 1.6, "legend.handletextpad": 0.5,
        "legend.columnspacing": 1.0, "legend.labelspacing": 0.35,
    })
    global _CONFIGURED_FONT_RESOLVER, _CONFIGURED
    _CONFIGURED_FONT_RESOLVER, _CONFIGURED = font_resolver, True


def apply_axis_style(ax, kind: str) -> None:
    _require(kind in _SUPPORTED_AXIS_KINDS, f"unsupported axis style kind: {kind}")
    for side, spine in ax.spines.items():
        spine.set_linewidth(FIGURE_STYLE_V1["spine"])
        spine.set_color(NEUTRAL_COLORS["spine"])
        spine.set_visible(kind != "map" and side in {"left", "bottom"})
    if kind != "map":
        ax.tick_params(which="major", direction=FIGURE_STYLE_V1["tick_direction"],
                       width=FIGURE_STYLE_V1["major_tick_width"], length=FIGURE_STYLE_V1["major_tick_length"],
                       colors=NEUTRAL_COLORS["text"])
        ax.tick_params(which="minor", direction=FIGURE_STYLE_V1["tick_direction"],
                       width=FIGURE_STYLE_V1["minor_tick_width"], length=FIGURE_STYLE_V1["minor_tick_length"],
                       colors=NEUTRAL_COLORS["text"])
        ax.minorticks_off()
    grid_axis = ({"line": "y", "bar": "y", "box": "y", "scatter": "both",
                  "forest": "x", "hbar": "x"}).get(kind)
    ax.grid(grid_axis is not None, axis=grid_axis or "both", which="major")
    if kind in {"bar", "hbar"}:
        for patch in ax.patches:
            patch.set_edgecolor(NEUTRAL_COLORS["spine"])
            patch.set_linewidth(FIGURE_STYLE_V1["bar_edge"])
    setattr(ax, "_kymcm_figure_exec_id", EXECUTION_ID)
    setattr(ax, "_kymcm_axis_kind", kind)


def semantic_color(role: str) -> str:
    try:
        return SEMANTIC_COLORS[role]
    except KeyError as exc:
        raise FigureContractError(f"unknown semantic color role: {role}") from exc


def qualitative_colors(n: int) -> tuple[str, ...]:
    _require(not isinstance(n, bool) and isinstance(n, int) and 0 <= n <= MAX_QUALITATIVE_CATEGORIES,
             "qualitative category count must be an integer from 0 through 7")
    return KY_MCM_QUALITATIVE_V1[:n]


def marker_every(n_points: int) -> int | list[int]:
    _require(n_points >= 0, "point count cannot be negative")
    return 1 if n_points <= 12 else 2 if n_points <= 30 else []


def series_encoding(index: int, *, n_points: int = 0) -> dict[str, object]:
    _require(not isinstance(index, bool) and isinstance(index, int) and 0 <= index < 7,
             "series index must be an integer from 0 through 6")
    return {
        "color": KY_MCM_QUALITATIVE_V1[index], "linestyle": LINE_STYLES[index % len(LINE_STYLES)],
        "marker": MARKER_SEQUENCE[index], "markevery": marker_every(n_points),
        "linewidth": FIGURE_STYLE_V1["primary"], "markersize": FIGURE_STYLE_V1["marker"],
        "markeredgewidth": FIGURE_STYLE_V1["marker_edge"],
    }


def scatter_kwargs(n_points: int) -> dict[str, object]:
    _require(n_points >= 0, "point count cannot be negative")
    if n_points <= 200:
        return {"s": 21.0, "alpha": 0.85, "edgecolors": NEUTRAL_COLORS["spine"], "linewidths": 0.4}
    if n_points <= 2000:
        return {"s": 11.0, "alpha": 0.55, "edgecolors": "none", "linewidths": 0.0}
    return {"s": 4.5, "alpha": 0.30, "edgecolors": "none", "linewidths": 0.0}


def bar_width(series_count: int) -> float:
    _require(not isinstance(series_count, bool) and isinstance(series_count, int) and
             1 <= series_count <= MAX_QUALITATIVE_CATEGORIES,
             "bar series count must be an integer from 1 through 7")
    return 0.68 if series_count == 1 else 0.78 / series_count


def boxplot_kwargs(*, color: str = KY_MCM_QUALITATIVE_V1[0]) -> dict[str, object]:
    _require(color.upper() in set(KY_MCM_QUALITATIVE_V1) | set(SEMANTIC_COLORS.values()) |
             set(NEUTRAL_COLORS.values()), f"unapproved boxplot color: {color}")
    return {
        "widths": 0.52, "patch_artist": True, "showmeans": False, "notch": False, "showfliers": True,
        "boxprops": {"facecolor": color, "edgecolor": NEUTRAL_COLORS["spine"], "linewidth": 0.9},
        "whiskerprops": {"color": NEUTRAL_COLORS["spine"], "linewidth": 0.8},
        "capprops": {"color": NEUTRAL_COLORS["spine"], "linewidth": 0.8},
        "medianprops": {"color": NEUTRAL_COLORS["spine"], "linewidth": 1.4},
        "flierprops": {"marker": "o", "markersize": 3.0, "alpha": 0.55, "color": color,
                       "markeredgecolor": color, "markerfacecolor": "none"},
    }


def errorbar_kwargs() -> dict[str, object]:
    return {"elinewidth": 0.9, "capsize": 2.5, "capthick": 0.9}


def font_kwargs(role: str) -> dict[str, object]:
    _require(role in TYPOGRAPHY_PT and role != "minimum", f"unknown typography role: {role}")
    result = {"fontsize": TYPOGRAPHY_PT[role], "fontfamily": [FONT_LATIN, FONT_CJK]}
    if role == "panel_marker":
        result["fontweight"] = "semibold"
    return result


def continuous_cmap(kind: str):
    name = {"sequential": "batlow", "diverging": "vik"}.get(kind)
    _require(name is not None, f"unknown continuous color-map kind: {kind}")
    try:
        return getattr(_cmcrameri(), name)
    except AttributeError as exc:
        raise FigureContractError(f"controlled cmcrameri color map unavailable: {name}") from exc


def diverging_norm(vmin: float, vmax: float, center: float, *, symmetric: bool = True):
    if symmetric:
        limit = max(abs(vmin - center), abs(vmax - center))
        vmin, vmax = center - limit, center + limit
    _require(vmin < center < vmax, "diverging limits must strictly bracket the center")
    from matplotlib.colors import TwoSlopeNorm
    return TwoSlopeNorm(vcenter=center, vmin=vmin, vmax=vmax)


def _rgba_allowed(color, *, alpha: float | None = None) -> bool:
    from matplotlib.colors import to_hex, to_rgba
    try:
        rgba = to_rgba(color)
    except (TypeError, ValueError):
        return False
    if (alpha is not None and alpha == 0) or rgba[3] == 0:
        return True
    return to_hex(rgba, keep_alpha=False).upper() in (
        set(KY_MCM_QUALITATIVE_V1) | set(SEMANTIC_COLORS.values()) | set(NEUTRAL_COLORS.values()))


def _audit_artist_colors(fig) -> None:
    from matplotlib.collections import Collection
    from matplotlib.contour import ContourSet
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    for artist in fig.findobj(match=lambda item: isinstance(item, (Line2D, Patch, Collection))):
        if not artist.get_visible():
            continue
        if isinstance(artist, ContourSet):
            _require(artist.get_cmap().name in {"batlow", "batlow_r", "vik"},
                     f"unapproved continuous color map: {artist.get_cmap().name}")
            continue
        cmap = getattr(artist, "get_cmap", lambda: None)()
        values = getattr(artist, "get_array", lambda: None)()
        if cmap is not None and cmap.name in {"batlow", "batlow_r", "vik"}:
            if values is None:
                continue
            getters = ("get_edgecolor", "get_edgecolors")
        elif cmap is not None and values is not None:
            _require(cmap.name in {"batlow", "batlow_r", "vik"},
                     f"unapproved continuous color map: {cmap.name}")
            getters = ()
        else:
            getters = ("get_color", "get_facecolor", "get_edgecolor", "get_facecolors", "get_edgecolors")
        for getter_name in getters:
            getter = getattr(artist, getter_name, None)
            if getter is None:
                continue
            colors = getter()
            if isinstance(colors, str) or not hasattr(colors, "__iter__"):
                colors = (colors,)
            elif len(colors) and isinstance(colors[0], (int, float)):
                colors = (colors,)
            for color in colors:
                if color is None or (isinstance(color, str) and color.lower() == "none"):
                    continue
                _require(_rgba_allowed(color, alpha=artist.get_alpha()),
                         f"unapproved visible artist color: {color}")


def _audit_colormaps(fig) -> None:
    bad = next((cmap.name for artist in fig.findobj()
                if (cmap := getattr(artist, "get_cmap", lambda: None)()) is not None
                and getattr(artist, "get_array", lambda: None)() is not None
                and cmap.name not in {"batlow", "batlow_r", "vik"}), None)
    _require(bad is None, f"unapproved continuous color map: {bad}")


def audit_hard_contract(fig, *, template: str) -> tuple[str, ...]:
    _require(_CONFIGURED, "configure_matplotlib() must run before hard audit")
    _verify_fonts(_CONFIGURED_FONT_RESOLVER)
    expected, actual = canvas_inches(template), tuple(float(value) for value in fig.get_size_inches())
    _require(not any(abs(left - right) > 1e-7 for left, right in zip(actual, expected)),
             f"figure size does not match {template}")
    _require(fig._suptitle is None or not fig._suptitle.get_text().strip(), "figure suptitle is prohibited")
    from matplotlib.colors import to_hex
    _require(to_hex(fig.get_facecolor()).upper() == SEMANTIC_COLORS["background"],
             "figure background must be pure white")
    for ax in fig.axes:
        _require(not any(ax.get_title(loc=location).strip() for location in ("center", "left", "right")),
                 "axes/subplot title is prohibited")
        _require(to_hex(ax.get_facecolor()).upper() == SEMANTIC_COLORS["background"],
                 "axes background must be pure white")
        _require(hasattr(ax, "_colorbar") or getattr(ax, "_kymcm_figure_exec_id", None) == EXECUTION_ID,
                 "ordinary axis was not passed through apply_axis_style()")
        if hasattr(ax, "_colorbar"):
            continue
        kind = ax._kymcm_axis_kind
        _require(ax.get_axisbelow() is True, "axis-below no longer matches the locked style")
        for side, spine in ax.spines.items():
            expected_visible = kind != "map" and side in {"left", "bottom"}
            _require(spine.get_visible() == expected_visible and
                     abs(spine.get_linewidth() - FIGURE_STYLE_V1["spine"]) <= 1e-7,
                     "axis spine no longer matches the locked style")
            _require(not spine.get_visible() or
                     to_hex(spine.get_edgecolor()).upper() == NEUTRAL_COLORS["spine"],
                     "axis spine color no longer matches the locked style")
        if kind != "map":
            for axis in (ax.xaxis, ax.yaxis):
                for tick in axis.get_major_ticks():
                    _require(tick._tickdir == FIGURE_STYLE_V1["tick_direction"],
                             "major tick direction no longer matches the locked style")
                    _require(abs(tick.tick1line.get_markersize() - FIGURE_STYLE_V1["major_tick_length"]) <= 1e-7,
                             "major tick length no longer matches the locked style")
                    _require(abs(tick.tick1line.get_markeredgewidth() - FIGURE_STYLE_V1["major_tick_width"]) <= 1e-7,
                             "major tick width no longer matches the locked style")
        for gridline in (*ax.get_xgridlines(), *ax.get_ygridlines()):
            visible = gridline.get_visible()
            _require(not visible or abs(gridline.get_linewidth() - FIGURE_STYLE_V1["grid"]) <= 1e-7,
                     "grid width no longer matches the locked style")
            _require(not visible or abs(gridline.get_alpha() - GRID_ALPHA) <= 1e-7,
                     "grid alpha no longer matches the locked style")
            _require(not visible or to_hex(gridline.get_color()).upper() == NEUTRAL_COLORS["grid"],
                     "grid color no longer matches the locked style")
            _require(not visible or gridline.get_linestyle() == "-",
                     "grid line style no longer matches the locked style")
        _require(kind not in {"bar", "hbar"} or not any(
            abs(patch.get_linewidth() - FIGURE_STYLE_V1["bar_edge"]) > 1e-7 for patch in ax.patches),
            "bar edge width no longer matches the locked style")
        if kind in {"bar", "hbar"}:
            widths, allowed = ([abs(patch.get_width() if kind == "bar" else patch.get_height())
                                for patch in ax.patches],
                               {FIGURE_STYLE_V1["single_bar"]} | {FIGURE_STYLE_V1["group_total"] / count
                                for count in range(2, MAX_QUALITATIVE_CATEGORIES + 1)})
            _require(not any(all(abs(width - candidate) > 1e-7 for candidate in allowed) for width in widths),
                     "bar width no longer matches the locked geometry")
        if kind == "box":
            median_spans = [(max(line.get_xdata()) - min(line.get_xdata()),
                             max(line.get_ydata()) - min(line.get_ydata())) for line in ax.lines
                            if abs(line.get_linewidth() - FIGURE_STYLE_V1["median"]) <= 1e-7]
            category_axes = {0 if x_span > 1e-7 and y_span <= 1e-7 else 1
                             for x_span, y_span in median_spans if x_span <= 1e-7 or y_span <= 1e-7}
            _require(len(category_axes) == 1, "box orientation could not be audited")
            category_axis = next(iter(category_axes))
            for patch in ax.patches:
                values = [vertex[category_axis] for vertex in patch.get_path().vertices]
                _require(abs((max(values) - min(values)) - FIGURE_STYLE_V1["box_width"]) <= 1e-7,
                         "box width no longer matches the locked geometry")
    from matplotlib.text import Text
    for text in fig.findobj(match=lambda item: isinstance(item, Text)):
        if text.get_visible() and text.get_text().strip():
            _require(text.get_fontsize() >= TYPOGRAPHY_PT["minimum"],
                     "rendered text is below the 8 pt minimum")
            _require(bool(text.get_fontfamily()) and
                     all(family in {FONT_LATIN, FONT_CJK} for family in text.get_fontfamily()),
                     "text uses an unapproved font family")
    from matplotlib.collections import Collection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    for artist in fig.findobj(match=lambda item: isinstance(item, (Line2D, Patch, Collection))):
        widths = artist.get_linewidths() if isinstance(artist, Collection) else (artist.get_linewidth(),)
        _require(not artist.get_visible() or
                 not any(width > FIGURE_STYLE_V1["max_normal"] for width in widths),
                 "ordinary artist line width exceeds 2.0 pt")
    allowed_line_widths = {FIGURE_STYLE_V1[name] for name in (
        "aux", "secondary", "primary", "emphasis", "reference", "errorbar", "max_normal",
        "bar_edge", "box_line", "whisker", "median",
    )}
    for ax in fig.axes:
        for line in ax.lines:
            _require(not line.get_visible() or line.get_linewidth() in allowed_line_widths,
                     "data line width is outside the locked hierarchy")
            if getattr(ax, "_kymcm_axis_kind", None) == "line" and line.get_marker() not in {"None", "none", "", " "}:
                _require(line.get_markersize() in {FIGURE_STYLE_V1["marker"], FIGURE_STYLE_V1["emphasis_marker"]},
                         "line marker size is outside the locked hierarchy")
                _require(abs(line.get_markeredgewidth() - FIGURE_STYLE_V1["marker_edge"]) <= 1e-7,
                         "line marker edge no longer matches the locked style")
    _audit_colormaps(fig)
    _audit_artist_colors(fig)
    return ("canvas", "background", "fonts", "titles", "text-size", "axis-style", "line-width", "colors", "colormaps")


def _pdf_media_box(path: Path) -> tuple[float, float]:
    match = re.search(rb"/MediaBox\s*\[\s*[-+0-9.]+\s+[-+0-9.]+\s+([-+0-9.]+)\s+([-+0-9.]+)\s*\]", path.read_bytes())
    _require(match is not None, "saved PDF MediaBox could not be inspected")
    return float(match.group(1)), float(match.group(2))


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    _require(header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR",
             "saved PNG header is invalid")
    return struct.unpack(">II", header[16:24])


def _replace_output_pair(temporary: tuple[Path, Path], final: tuple[Path, Path]) -> None:
    backups: dict[Path, Path] = {}
    installed: set[Path] = set()
    try:
        for destination in final:
            if destination.exists():
                handle, name = tempfile.mkstemp(prefix=f".{destination.name}-backup-", dir=destination.parent)
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


def save_formal_figure(fig, output_stem, *, template: str) -> dict[str, object]:
    stem = Path(output_stem)
    _require(not stem.suffix, "output_stem must not include a file extension")
    forbidden = next((suffix for suffix in (".svg", ".tif", ".tiff", ".jpg", ".jpeg", ".eps",
                                              ".ps", ".webp", ".bmp") if stem.with_suffix(suffix).exists()), None)
    _require(forbidden is None, f"forbidden same-stem formal format exists: {forbidden}")
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(*canvas_inches(template), forward=True)
    checks = audit_hard_contract(fig, template=template)
    temporary: list[Path] = []
    try:
        for suffix in (".pdf", ".png"):
            handle, name = tempfile.mkstemp(prefix=f".{stem.name}-", suffix=suffix, dir=stem.parent)
            os.close(handle)
            temporary.append(Path(name))
        pdf_temp, png_temp = temporary
        common = {"facecolor": "white", "edgecolor": "white", "transparent": False, "bbox_inches": None}
        fig.savefig(pdf_temp, format="pdf", **common)
        fig.savefig(png_temp, format="png", dpi=FIGURE_STYLE_V1["png_dpi"], **common)
        expected_points = tuple(mm_to_inches(value) * 72.0 for value in CANVAS_MM[template])
        media_box = _pdf_media_box(pdf_temp)
        _require(not any(abs(left - right) > 0.25 for left, right in zip(media_box, expected_points)),
                 "saved PDF MediaBox does not match the physical template")
        expected_pixels = tuple(round(value * FIGURE_STYLE_V1["png_dpi"]) for value in canvas_inches(template))
        pixels = _png_dimensions(png_temp)
        _require(not any(abs(left - right) > 1 for left, right in zip(pixels, expected_pixels)),
                 "saved PNG dimensions do not match 600 dpi template output")
        pdf, png = stem.with_suffix(".pdf"), stem.with_suffix(".png")
        _replace_output_pair((pdf_temp, png_temp), (pdf, png))
        temporary.clear()
        return {"pdf": pdf, "png": png, "checks": checks}
    except FigureContractError:
        raise
    except Exception as exc:
        raise FigureContractError(f"formal figure save failed: {exc}") from exc
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)
