"""Shared validation and semantic styling for templates."""

from __future__ import annotations

import numpy as np
import pandas as pd


PALETTE = ("#0072B2", "#6B7280", "#E69F00", "#009E73", "#D55E00", "#56B4E9", "#CC79A7")
LINESTYLES = ("-", "--", "-.", ":")
MARKERS = ("o", "s", "^", "D", "v", "P", "X")


def require_mapping(mapping: dict, required: tuple[str, ...]) -> None:
    missing = [field for field in required if field not in mapping]
    if missing:
        raise ValueError(f"Template mapping missing fields: {missing}")


def require_columns(data: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"Source data missing columns: {missing}")


def finite_numeric(data: pd.DataFrame, columns: list[str]) -> None:
    require_columns(data, columns)
    for column in columns:
        values = pd.to_numeric(data[column], errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"Column {column} must contain finite numeric values")


def series_style(index: int) -> dict:
    return {
        "color": PALETTE[index % len(PALETTE)],
        "linestyle": LINESTYLES[index % len(LINESTYLES)],
        "marker": MARKERS[index % len(MARKERS)],
    }


def axis_metadata(brief: dict, x_default: str, y_default: str, legend_items: int = 0) -> dict:
    return {
        "x_label": brief.get("x_label", x_default),
        "y_label": brief.get("y_label", y_default),
        "legend_items": legend_items,
        "has_large_title": False,
    }
