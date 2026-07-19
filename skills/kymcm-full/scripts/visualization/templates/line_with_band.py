"""Ordered line chart with optional uncertainty band."""

from __future__ import annotations

import matplotlib.pyplot as plt

from ._common import axis_metadata, finite_numeric, require_columns, require_mapping


def render(data, mapping: dict, brief: dict, theme):
    require_mapping(mapping, ("x", "y"))
    if ("lower" in mapping) != ("upper" in mapping):
        raise ValueError("line_with_band requires both lower and upper mappings")
    numeric = [mapping["x"], mapping["y"]]
    for field in ("lower", "upper"):
        if field in mapping:
            numeric.append(mapping[field])
    finite_numeric(data, numeric)
    group_column = mapping.get("group")
    if group_column:
        require_columns(data, [group_column])
        groups = list(data.groupby(group_column, sort=False, dropna=False))
    else:
        groups = [(None, data)]
    if len(groups) > 12:
        raise ValueError("line_with_band supports at most 12 series")
    fig, ax = plt.subplots(figsize=theme.size_inches)
    for index, (name, frame) in enumerate(groups):
        frame = frame.sort_values(mapping["x"])
        label = str(name) if name is not None else None
        explicit_role = brief.get("series_roles", {}).get(label)
        style = theme.style_for_series(label or "series", index, explicit_role)
        line_style = {key: style[key] for key in ("color", "linestyle", "marker")}
        ax.plot(frame[mapping["x"]], frame[mapping["y"]], label=label, **line_style)
        if "lower" in mapping and "upper" in mapping:
            ax.fill_between(
                frame[mapping["x"]], frame[mapping["lower"]], frame[mapping["upper"]],
                color=style["color"], alpha=0.16, linewidth=0,
            )
    metadata = axis_metadata(
        brief, theme.text("input"), theme.text("response"),
        len(groups) if group_column else 0,
    )
    ax.set_xlabel(metadata["x_label"])
    ax.set_ylabel(metadata["y_label"])
    ax.grid(axis="y", alpha=0.2)
    if group_column:
        ax.legend(frameon=False, loc="best")
    return fig, metadata, []
