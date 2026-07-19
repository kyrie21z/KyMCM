"""Finite numeric Pearson correlation matrix heatmap."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ._common import axis_metadata, finite_numeric, require_mapping


def render(data, mapping: dict, brief: dict, theme):
    require_mapping(mapping, ("columns",))
    columns = mapping["columns"]
    if isinstance(columns, str):
        columns = [item.strip() for item in columns.split(",") if item.strip()]
    if not isinstance(columns, list) or len(columns) < 2:
        raise ValueError("correlation_heatmap requires at least two mapped columns")
    if len(columns) > 30:
        raise ValueError("correlation_heatmap supports at most 30 variables")
    finite_numeric(data, columns)
    matrix = data[columns].corr().to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=theme.size_inches)
    image = ax.imshow(matrix, vmin=-1, vmax=1, cmap="coolwarm", aspect="auto")
    ax.set_xticks(range(len(columns)), columns, rotation=45, ha="right")
    ax.set_yticks(range(len(columns)), columns)
    threshold = 12
    if len(columns) <= threshold:
        for row in range(len(columns)):
            for column in range(len(columns)):
                color = "white" if abs(matrix[row, column]) > 0.55 else "#111827"
                ax.text(column, row, f"{matrix[row, column]:.2f}", ha="center", va="center", color=color, fontsize=7)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label(theme.text("pearson_correlation"))
    metadata = axis_metadata(
        brief, theme.text("variables"), theme.text("variables"),
    )
    metadata["variable_count"] = len(columns)
    warnings = ["correlation annotations omitted for more than 12 variables"] if len(columns) > threshold else []
    return fig, metadata, warnings
