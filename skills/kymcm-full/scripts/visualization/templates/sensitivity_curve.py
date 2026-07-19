"""Parameter sensitivity curves with optional baseline."""

from __future__ import annotations

import matplotlib.pyplot as plt

from ._common import axis_metadata, finite_numeric, require_columns, require_mapping


def render(data, mapping: dict, brief: dict, theme):
    require_mapping(mapping, ("parameter", "response"))
    numeric = [mapping["parameter"], mapping["response"]]
    if "baseline" in mapping:
        numeric.append(mapping["baseline"])
    finite_numeric(data, numeric)
    scenario_column = mapping.get("scenario")
    if scenario_column:
        require_columns(data, [scenario_column])
        groups = list(data.groupby(scenario_column, sort=False, dropna=False))
    else:
        groups = [(None, data)]
    if len(groups) > 12:
        raise ValueError("sensitivity_curve supports at most 12 series")
    fig, ax = plt.subplots(figsize=theme.size_inches)
    for index, (name, frame) in enumerate(groups):
        frame = frame.sort_values(mapping["parameter"])
        label = str(name) if name is not None else None
        explicit_role = brief.get("series_roles", {}).get(label)
        style = theme.style_for_series(label or "series", index, explicit_role)
        ax.plot(
            frame[mapping["parameter"]], frame[mapping["response"]],
            label=label,
            **{key: style[key] for key in ("color", "linestyle", "marker")},
        )
    if "baseline" in mapping:
        baseline_values = data[mapping["baseline"]].dropna().unique()
        if len(baseline_values) == 1:
            style = theme.style_for_series("Baseline", explicit_role="baseline")
            ax.axhline(
                float(baseline_values[0]), color=style["color"],
                linestyle=style["linestyle"], label=theme.text("baseline"),
            )
    metadata = axis_metadata(
        brief, theme.text("parameter"), theme.text("response"),
        len(groups) if scenario_column else 0,
    )
    ax.set_xlabel(metadata["x_label"])
    ax.set_ylabel(metadata["y_label"])
    ax.grid(axis="y", alpha=0.2)
    if scenario_column or "baseline" in mapping:
        ax.legend(frameon=False, loc="best")
    return fig, metadata, []
