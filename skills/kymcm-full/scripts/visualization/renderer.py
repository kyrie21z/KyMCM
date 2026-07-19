"""Unified data-driven figure renderer and manifest writer."""

from __future__ import annotations

import json
import shutil
import warnings as python_warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from . import RENDERER_VERSION, THEME_VERSION
from .brief import find_brief, load_figure_plan, workspace_file
from .integrity import sha256_file, validate_output
from .selection import select_template
from .theme import FigureTheme
from .templates import (
    actual_vs_predicted,
    correlation_heatmap,
    grouped_bar_error,
    line_with_band,
    residual_diagnostics,
    sensitivity_curve,
)


TEMPLATE_REGISTRY = {
    "line_with_band": line_with_band.render,
    "grouped_bar_error": grouped_bar_error.render,
    "actual_vs_predicted": actual_vs_predicted.render,
    "residual_diagnostics": residual_diagnostics.render,
    "correlation_heatmap": correlation_heatmap.render,
    "sensitivity_curve": sensitivity_curve.render,
}


def _write_json_temp(path: Path, value: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    written = json.loads(temporary.read_text(encoding="utf-8"))
    if not isinstance(written, dict):
        raise ValueError(f"Figure manifest temporary file must contain an object: {temporary}")
    return temporary


def _add_exception_notes(error: BaseException, notes: list[str]) -> None:
    for note in notes:
        error.add_note(note)


def _cleanup_transaction_files(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        try:
            if path.is_file() or path.is_symlink():
                path.unlink()
        except OSError as exc:
            errors.append(f"failed to remove transaction file {path}: {exc}")
    return errors


def _restore_formal_artifacts(
    formal_paths: dict[str, Path],
    backup_paths: dict[str, Path],
    had_formal: set[str],
) -> list[str]:
    errors: list[str] = []
    for artifact_name in ("svg", "pdf", "png", "manifest"):
        formal_path = formal_paths[artifact_name]
        backup_path = backup_paths[artifact_name]
        try:
            if artifact_name in had_formal:
                if not backup_path.is_file():
                    raise FileNotFoundError(f"missing backup for {formal_path}")
                try:
                    backup_path.replace(formal_path)
                except OSError:
                    shutil.copy2(backup_path, formal_path)
            elif formal_path.is_file() or formal_path.is_symlink():
                formal_path.unlink()
        except Exception as exc:
            errors.append(f"failed to restore {artifact_name} output {formal_path}: {exc}")
    return errors


def _sha256(path: Path) -> str:
    return sha256_file(path)


def _load_source(path: Path) -> pd.DataFrame:
    if path.suffix.lower() != ".csv":
        raise ValueError(
            "P3.2 Figure Brief requires exactly one CSV evidence file; "
            "merge or export source data before rendering"
        )
    try:
        data = pd.read_csv(path)
    except Exception as exc:
        raise ValueError(f"Unable to read source CSV {path}: {exc}") from exc
    if data.empty:
        raise ValueError(f"Source CSV is empty: {path}")
    return data


def _ensure_output_directory(workspace: Path, path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if not path.resolve().is_relative_to(workspace.resolve()):
        raise ValueError(f"Figure output directory escapes workspace: {path}")


def _data_profile(brief: dict, data: pd.DataFrame) -> dict:
    numeric = len(data.select_dtypes(include=[np.number]).columns)
    mapping = brief.get("mapping", {})
    purpose = brief.get("purpose")
    if not purpose:
        if {"actual", "predicted"}.issubset(mapping):
            purpose = "prediction"
        elif "residual" in mapping:
            purpose = "residual"
        elif "columns" in mapping:
            purpose = "correlation"
        elif "parameter" in mapping:
            purpose = "sensitivity"
        elif "category" in mapping:
            purpose = "comparison"
        else:
            purpose = "trend"
    return {
        "purpose": purpose,
        "numeric_columns": numeric,
        "has_uncertainty": "lower" in mapping and "upper" in mapping,
    }


def render_figure(workspace: Path, figure_id: str) -> dict:
    workspace = workspace.resolve()
    brief = find_brief(workspace, figure_id)
    source_path = workspace_file(workspace, brief["evidence"][0])
    data = _load_source(source_path)
    template_id = select_template(brief, _data_profile(brief, data))
    render_template = TEMPLATE_REGISTRY[template_id]
    theme = FigureTheme(language=brief["language"], target_width=brief["target_width"])

    vector_dir = workspace / "figures" / "vector"
    preview_dir = workspace / "figures" / "preview"
    manifest_dir = workspace / "figures" / "manifests"
    for directory in (vector_dir, preview_dir, manifest_dir):
        _ensure_output_directory(workspace, directory)
    output_paths: dict[str, Path] = {
        "svg": vector_dir / f"{figure_id}.svg",
        "pdf": vector_dir / f"{figure_id}.pdf",
        "png": preview_dir / f"{figure_id}.png",
    }
    manifest_path = manifest_dir / f"{figure_id}.json"
    formal_paths = {**output_paths, "manifest": manifest_path}
    temporary_paths = {
        key: path.with_name(path.name + ".tmp") for key, path in formal_paths.items()
    }
    backup_paths = {
        key: path.with_name(path.name + ".bak") for key, path in formal_paths.items()
    }
    transaction_paths = [*temporary_paths.values(), *backup_paths.values()]

    captured: list[str] = []
    figure = None
    cleanup_done = False
    try:
        with python_warnings.catch_warnings(record=True) as emitted:
            python_warnings.simplefilter("always")
            with theme.context() as theme_warnings:
                figure, metadata, template_warnings = render_template(
                    data, brief["mapping"], brief, theme,
                )
                figure.tight_layout()
                figure.savefig(temporary_paths["svg"], format="svg")
                figure.savefig(temporary_paths["pdf"], format="pdf")
                figure.savefig(
                    temporary_paths["png"], format="png", dpi=theme.dpi,
                )
                captured.extend(theme_warnings)
                captured.extend(template_warnings)
            captured.extend(str(item.message) for item in emitted)
        validate_output(temporary_paths["svg"], "svg")
        validate_output(temporary_paths["pdf"], "pdf")
        png_size = validate_output(temporary_paths["png"], "png")
        assert png_size is not None
        width_px, height_px = png_size
        relative_sources = [str(source_path.relative_to(workspace))]
        relative_outputs = {
            key: str(path.relative_to(workspace)) for key, path in output_paths.items()
        }
        manifest = {
            "figure_id": figure_id,
            "problem": brief["problem"],
            "claim": brief["claim"],
            "template": template_id,
            "selection_reason": brief.get("selection_reason", "explicit Figure Brief selection"),
            "source_data": relative_sources,
            "source_data_sha256": {
                relative_sources[0]: _sha256(source_path)
            },
            "renderer_version": RENDERER_VERSION,
            "theme_version": THEME_VERSION,
            "target_width": brief["target_width"],
            "language": brief["language"],
            "output_paths": relative_outputs,
            "output_sha256": {
                key: _sha256(path) for key, path in temporary_paths.items()
                if key in output_paths
            },
            "output_sizes": {
                key: path.stat().st_size for key, path in temporary_paths.items()
                if key in output_paths
            },
            "output_dimensions": {
                "width_px": width_px, "height_px": height_px, "dpi": theme.dpi,
            },
            "mapping": brief["mapping"],
            "metadata": metadata,
            "paper_section": brief["paper_section"],
            "label": brief.get("label", f"fig:{figure_id.replace('_', '-') }"),
            "caption_draft": brief["caption_draft"],
            "preferred_asset": relative_outputs["pdf"],
            "audit_status": "pending",
            "warnings": sorted(set(captured)),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
        _write_json_temp(manifest_path, manifest)

        had_formal: set[str] = set()
        for artifact_name, formal_path in formal_paths.items():
            if formal_path.is_file():
                shutil.copy2(formal_path, backup_paths[artifact_name])
                had_formal.add(artifact_name)
        try:
            for artifact_name in ("svg", "pdf", "png", "manifest"):
                temporary_paths[artifact_name].replace(formal_paths[artifact_name])
        except Exception as exc:
            rollback_notes = _restore_formal_artifacts(
                formal_paths, backup_paths, had_formal,
            )
            cleanup_notes = _cleanup_transaction_files(transaction_paths)
            cleanup_done = True
            _add_exception_notes(exc, rollback_notes + cleanup_notes)
            raise
        cleanup_notes = _cleanup_transaction_files(transaction_paths)
        cleanup_done = True
        if cleanup_notes:
            raise OSError("; ".join(cleanup_notes))
        return manifest
    except Exception as exc:
        if not cleanup_done:
            cleanup_notes = _cleanup_transaction_files(transaction_paths)
            _add_exception_notes(exc, cleanup_notes)
        raise
    finally:
        if figure is not None:
            plt.close(figure)

def render_all(workspace: Path) -> list[dict]:
    return [render_figure(workspace, brief["id"]) for brief in load_figure_plan(workspace)]
