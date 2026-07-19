"""Bounded Figure Brief and data-profile chart selection."""

from __future__ import annotations


IMPLEMENTED_TEMPLATES = {
    "line_with_band", "grouped_bar_error", "actual_vs_predicted",
    "residual_diagnostics", "correlation_heatmap", "sensitivity_curve",
}

PURPOSE_RULES = {
    "trend": "line_with_band",
    "time_series": "line_with_band",
    "comparison": "grouped_bar_error",
    "prediction": "actual_vs_predicted",
    "residual": "residual_diagnostics",
    "correlation": "correlation_heatmap",
    "sensitivity": "sensitivity_curve",
}


def select_template(brief: dict, data_profile: dict) -> str:
    requested = brief.get("chart_family", "auto")
    if requested != "auto":
        if requested not in IMPLEMENTED_TEMPLATES:
            raise ValueError(f"Unsupported Figure template: {requested}")
        return requested
    purpose = data_profile.get("purpose")
    selected = PURPOSE_RULES.get(purpose)
    if selected:
        return selected
    if data_profile.get("has_uncertainty"):
        return "line_with_band"
    numeric = data_profile.get("numeric_columns", 0)
    if isinstance(numeric, int) and numeric >= 3:
        return "correlation_heatmap"
    raise ValueError("Chart selection needs an explicit family or recognized data purpose")
