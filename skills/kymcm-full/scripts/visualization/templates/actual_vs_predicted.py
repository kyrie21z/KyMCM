"""Paired actual-versus-predicted comparison."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ._common import axis_metadata, finite_numeric, require_columns, require_mapping


def render(data, mapping: dict, brief: dict, theme):
    require_mapping(mapping, ("actual", "predicted"))
    finite_numeric(data, [mapping["actual"], mapping["predicted"]])
    if len(data) > 50000:
        raise ValueError("actual_vs_predicted supports at most 50000 points")
    group_column = mapping.get("group")
    if group_column:
        require_columns(data, [group_column])
        groups = list(data.groupby(group_column, sort=False, dropna=False))
    else:
        groups = [(None, data)]
    fig, ax = plt.subplots(figsize=theme.size_inches)
    for index, (name, frame) in enumerate(groups):
        label = str(name) if name is not None else None
        explicit_role = brief.get("series_roles", {}).get(label)
        style = theme.style_for_series(label or "series", index, explicit_role)
        ax.scatter(
            frame[mapping["actual"]], frame[mapping["predicted"]], s=18,
            alpha=0.7, color=style["color"], marker=style["marker"], edgecolors="white",
            linewidths=0.35, label=label,
        )
    actual = data[mapping["actual"]].to_numpy(dtype=float)
    predicted = data[mapping["predicted"]].to_numpy(dtype=float)
    low = float(min(actual.min(), predicted.min()))
    high = float(max(actual.max(), predicted.max()))
    ax.plot([low, high], [low, high], color="#374151", linestyle="--", linewidth=1, label="1:1")
    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    denominator = float(np.sum((actual - actual.mean()) ** 2))
    r2 = float(1 - np.sum((actual - predicted) ** 2) / denominator) if denominator else float("nan")
    annotation = f"RMSE = {rmse:.3g}" + (f"\nR² = {r2:.3f}" if np.isfinite(r2) else "")
    ax.text(0.03, 0.97, annotation, transform=ax.transAxes, va="top", ha="left")
    metadata = axis_metadata(
        brief, theme.text("actual"), theme.text("predicted"), len(groups) + 1,
    )
    metadata["metrics"] = {"rmse": rmse, "r2": r2 if np.isfinite(r2) else None}
    ax.set_xlabel(metadata["x_label"])
    ax.set_ylabel(metadata["y_label"])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.2)
    if group_column:
        ax.legend(frameon=False, loc="best")
    return fig, metadata, []
