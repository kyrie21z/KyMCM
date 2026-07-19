"""Shared paper-oriented Matplotlib theme."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib

import matplotlib

matplotlib.use("Agg")
from matplotlib import font_manager, rc_context


SIZE_PROFILES = {
    "single": (3.35, 2.55),
    "double": (6.9, 3.8),
    "full": (7.2, 4.4),
}

COLORS = {
    "proposed": "#0072B2",
    "baseline": "#6B7280",
    "alternative": "#E69F00",
    "green": "#009E73",
    "vermilion": "#D55E00",
    "sky": "#56B4E9",
    "purple": "#CC79A7",
}

ROLE_ALIASES = {
    "proposed": {
        "proposed", "our method", "ours", "proposed model",
        "本文方法", "所提方法", "提出方法",
    },
    "baseline": {
        "baseline", "base", "reference", "基线", "基准", "对照",
    },
    "alternative": {
        "alternative", "alt", "备选方案", "替代方案",
    },
}

ROLE_STYLES = {
    "proposed": {"color": COLORS["proposed"], "linestyle": "-", "marker": "o", "hatch": ""},
    "baseline": {"color": COLORS["baseline"], "linestyle": "--", "marker": "s", "hatch": "//"},
    "alternative": {"color": COLORS["alternative"], "linestyle": "-.", "marker": "^", "hatch": ".."},
}

FALLBACK_COLORS = (
    COLORS["green"], COLORS["vermilion"], COLORS["sky"], COLORS["purple"],
    "#332288", "#88CCEE", "#AA4499", "#117733",
)
FALLBACK_LINESTYLES = ("-", "--", "-.", ":")
FALLBACK_MARKERS = ("o", "s", "^", "D", "v", "P", "X")
FALLBACK_HATCHES = ("", "//", "..", "xx", "\\\\", "++", "oo")

TEXT = {
    "en": {
        "actual": "Actual", "predicted": "Predicted", "residual": "Residual",
        "count": "Count", "pearson_correlation": "Pearson correlation",
        "baseline": "Baseline", "variables": "Variables", "parameter": "Parameter",
        "response": "Response", "category": "Category", "value": "Value",
        "input": "Input",
    },
    "zh": {
        "actual": "实际值", "predicted": "预测值", "residual": "残差",
        "count": "频数", "pearson_correlation": "皮尔逊相关系数",
        "baseline": "基准值", "variables": "变量", "parameter": "参数",
        "response": "响应值", "category": "类别", "value": "数值",
        "input": "输入",
    },
}

CJK_FONTS = (
    "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", "SimHei",
)
EN_FONTS = ("DejaVu Sans", "Arial", "Liberation Sans")


def _available_font(candidates: tuple[str, ...]) -> str | None:
    names = {font.name for font in font_manager.fontManager.ttflist}
    return next((name for name in candidates if name in names), None)


@dataclass(frozen=True)
class FigureTheme:
    language: str = "en"
    target_width: str = "double"
    dpi: int = 300

    @property
    def size_inches(self) -> tuple[float, float]:
        try:
            return SIZE_PROFILES[self.target_width]
        except KeyError as exc:
            raise ValueError(f"Unknown target width: {self.target_width}") from exc

    @property
    def colors(self) -> dict[str, str]:
        return dict(COLORS)

    def text(self, key: str) -> str:
        try:
            return TEXT[self.language][key]
        except KeyError as exc:
            raise ValueError(f"Unknown built-in Figure text: {self.language}.{key}") from exc

    def style_for_series(
        self, label: object, fallback_index: int = 0,
        explicit_role: str | None = None,
    ) -> dict[str, object]:
        normalized = " ".join(str(label).strip().lower().split())
        role = explicit_role.strip().lower() if isinstance(explicit_role, str) else None
        if role is None:
            role = next(
                (candidate for candidate, aliases in ROLE_ALIASES.items() if normalized in aliases),
                None,
            )
        if role is not None:
            if role not in ROLE_STYLES:
                raise ValueError(f"Unsupported semantic series role: {explicit_role}")
            return dict(ROLE_STYLES[role])
        digest = hashlib.sha256(normalized.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big")
        return {
            "color": FALLBACK_COLORS[index % len(FALLBACK_COLORS)],
            "linestyle": FALLBACK_LINESTYLES[index % len(FALLBACK_LINESTYLES)],
            "marker": FALLBACK_MARKERS[index % len(FALLBACK_MARKERS)],
            "hatch": FALLBACK_HATCHES[index % len(FALLBACK_HATCHES)],
        }

    @contextmanager
    def context(self):
        warnings: list[str] = []
        english = _available_font(EN_FONTS) or "DejaVu Sans"
        font_family = english
        if self.language == "zh":
            cjk = _available_font(CJK_FONTS)
            if cjk:
                font_family = cjk
            else:
                warnings.append("preferred CJK font unavailable; using sans-serif fallback")
        settings = {
            "font.family": "sans-serif",
            "font.sans-serif": [font_family, english, "DejaVu Sans"],
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8.5,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.4,
            "lines.markersize": 4,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "grid.alpha": 0.2,
            "grid.linewidth": 0.6,
            "savefig.transparent": False,
            "savefig.facecolor": "white",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "figure.dpi": self.dpi,
        }
        with rc_context(settings):
            yield warnings
