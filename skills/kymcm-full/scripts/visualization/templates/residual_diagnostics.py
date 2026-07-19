"""Residual-versus-fitted and residual distribution diagnostics."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from ._common import PALETTE, axis_metadata, finite_numeric, require_mapping


def render(data, mapping: dict, brief: dict, theme):
    require_mapping(mapping, ("predicted",))
    if "residual" not in mapping and "actual" not in mapping:
        raise ValueError("residual_diagnostics needs residual or actual mapping")
    numeric = [mapping["predicted"]]
    numeric.append(mapping["residual"] if "residual" in mapping else mapping["actual"])
    finite_numeric(data, numeric)
    if len(data) > 50000:
        raise ValueError("residual_diagnostics supports at most 50000 points")
    predicted = data[mapping["predicted"]].to_numpy(dtype=float)
    residual = (
        data[mapping["residual"]].to_numpy(dtype=float)
        if "residual" in mapping
        else data[mapping["actual"]].to_numpy(dtype=float) - predicted
    )
    width, height = theme.size_inches
    fig, axes = plt.subplots(1, 2, figsize=(width, height))
    axes[0].scatter(predicted, residual, s=16, alpha=0.7, color=PALETTE[0], edgecolors="white", linewidths=0.3)
    axes[0].axhline(0, color="#374151", linestyle="--", linewidth=1)
    axes[0].set_xlabel(brief.get("x_label", theme.text("predicted")))
    axes[0].set_ylabel(brief.get("y_label", theme.text("residual")))
    axes[0].grid(alpha=0.2)
    bins = min(max(int(np.sqrt(len(residual))), 5), 30)
    axes[1].hist(residual, bins=bins, color=PALETTE[2], alpha=0.82, edgecolor="white")
    axes[1].axvline(0, color="#374151", linestyle="--", linewidth=1)
    axes[1].set_xlabel(theme.text("residual"))
    axes[1].set_ylabel(theme.text("count"))
    metadata = axis_metadata(brief, theme.text("predicted"), theme.text("residual"))
    metadata["residual_mean"] = float(np.mean(residual))
    return fig, metadata, []
