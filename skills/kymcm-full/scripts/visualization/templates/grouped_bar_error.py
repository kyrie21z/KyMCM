"""Grouped categorical bars with optional symmetric errors."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ._common import axis_metadata, finite_numeric, require_columns, require_mapping


def render(data, mapping: dict, brief: dict, theme):
    require_mapping(mapping, ("category", "value"))
    numeric = [mapping["value"]]
    if "error" in mapping:
        numeric.append(mapping["error"])
    finite_numeric(data, numeric)
    category_column = mapping["category"]
    require_columns(data, [category_column])
    categories = list(dict.fromkeys(data[category_column].astype(str)))
    if len(categories) > 20:
        raise ValueError("grouped_bar_error supports at most 20 categories")
    group_column = mapping.get("group")
    groups = list(dict.fromkeys(data[group_column].astype(str))) if group_column else ["Value"]
    if len(groups) > 8:
        raise ValueError("grouped_bar_error supports at most 8 series")
    x = np.arange(len(categories), dtype=float)
    width = min(0.8 / len(groups), 0.28)
    fig, ax = plt.subplots(figsize=theme.size_inches)
    for index, group in enumerate(groups):
        frame = data[data[group_column].astype(str) == group] if group_column else data
        indexed = frame.assign(_category=frame[category_column].astype(str)).set_index("_category")
        values = indexed.reindex(categories)[mapping["value"]].to_numpy(dtype=float)
        errors = (
            indexed.reindex(categories)[mapping["error"]].to_numpy(dtype=float)
            if "error" in mapping else None
        )
        offset = (index - (len(groups) - 1) / 2) * width
        explicit_role = brief.get("series_roles", {}).get(group)
        style = theme.style_for_series(group, index, explicit_role)
        ax.bar(
            x + offset, values, width=width, yerr=errors, capsize=2.5,
            label=group if group_column else None, color=style["color"],
            hatch=style["hatch"], edgecolor="#374151", linewidth=0.5,
        )
    metadata = axis_metadata(
        brief, theme.text("category"), theme.text("value"),
        len(groups) if group_column else 0,
    )
    ax.set_xlabel(metadata["x_label"])
    ax.set_ylabel(metadata["y_label"])
    ax.set_xticks(x, categories)
    ax.grid(axis="y", alpha=0.2)
    if group_column:
        ax.legend(frameon=False, loc="best")
    return fig, metadata, []
