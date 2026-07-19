"""Deterministic figure provenance and paper-readiness audit."""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from .integrity import sha256_file, validate_output
from .theme import SIZE_PROFILES


def _atomic_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def _inside_file(workspace: Path, value: str) -> Path | None:
    path = (workspace / value).resolve()
    if not path.is_relative_to(workspace.resolve()) or not path.is_file():
        return None
    return path


def _audit_manifest(workspace: Path, manifest_path: Path) -> tuple[dict, dict]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, {
            "figure_id": manifest_path.stem, "status": "fail",
            "errors": [f"manifest is invalid: {exc}"], "warnings": [],
        }
    if not isinstance(manifest, dict):
        return {}, {
            "figure_id": manifest_path.stem, "status": "fail",
            "errors": ["manifest must be an object"], "warnings": [],
        }
    required = {
        "figure_id", "claim", "template", "source_data", "source_data_sha256",
        "output_paths", "output_sha256", "output_sizes", "output_dimensions", "paper_section", "label",
        "caption_draft", "preferred_asset", "target_width", "metadata",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        errors.append(f"manifest missing fields: {missing}")
    source_hashes = manifest.get("source_data_sha256")
    if not isinstance(source_hashes, dict):
        errors.append("source_data_sha256 must be an object")
        source_hashes = {}
    sources = manifest.get("source_data")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], str):
        errors.append("manifest requires exactly one source data file")
        sources = []
    for source in sources:
        if Path(source).suffix.lower() != ".csv":
            errors.append(f"source data must be a CSV file: {source}")
            continue
        path = _inside_file(workspace, source)
        if path is None:
            errors.append(f"source data missing: {source}")
            continue
        digest = sha256_file(path)
        if digest != source_hashes.get(source):
            errors.append(f"source data hash mismatch: {source}")
        try:
            data = pd.read_csv(path)
            numeric = data.select_dtypes(include=[np.number]).to_numpy(dtype=float)
            if numeric.size and not np.isfinite(numeric).all():
                errors.append(f"source data contains NaN or Inf: {source}")
        except Exception as exc:
            errors.append(f"source data is unreadable: {source}: {exc}")
    outputs = manifest.get("output_paths") if isinstance(manifest.get("output_paths"), dict) else {}
    output_hashes = manifest.get("output_sha256") if isinstance(manifest.get("output_sha256"), dict) else {}
    output_sizes = manifest.get("output_sizes") if isinstance(manifest.get("output_sizes"), dict) else {}
    png_dimensions: tuple[int, int] | None = None
    for format_name in ("svg", "pdf", "png"):
        relative = outputs.get(format_name)
        path = _inside_file(workspace, relative) if isinstance(relative, str) else None
        if path is None:
            errors.append(f"{format_name} output missing")
            continue
        actual_hash = sha256_file(path)
        if actual_hash != output_hashes.get(format_name):
            errors.append(f"{format_name} output hash mismatch")
        if path.stat().st_size != output_sizes.get(format_name):
            errors.append(f"{format_name} output size mismatch")
        try:
            dimensions = validate_output(path, format_name)
            if format_name == "png":
                assert dimensions is not None
                png_dimensions = dimensions
        except ValueError as exc:
            errors.append(str(exc))
    if png_dimensions:
        width, height = png_dimensions
        recorded = manifest.get("output_dimensions")
        if not isinstance(recorded, dict):
            errors.append("output_dimensions must be an object")
            recorded = {}
        if width != recorded.get("width_px") or height != recorded.get("height_px"):
            errors.append(
                f"PNG dimensions mismatch: actual {width}x{height}, "
                f"manifest {recorded.get('width_px')}x{recorded.get('height_px')}"
            )
        try:
            target_width = manifest.get("target_width")
            target = SIZE_PROFILES.get(target_width)
            if target is None:
                errors.append(f"target_width is invalid: {target_width}")
            else:
                min_width = math.floor(target[0] * 300 * 0.8)
                min_height = math.floor(target[1] * 300 * 0.7)
                if width < min_width or height < min_height:
                    errors.append(
                        f"PNG resolution {width}x{height} is below target {min_width}x{min_height}"
                    )
        except (TypeError, ValueError) as exc:
            errors.append(f"PNG resolution check failed: {exc}")
    if manifest.get("preferred_asset") != outputs.get("pdf"):
        errors.append("preferred_asset must equal the validated PDF output path")
    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
        metadata = {}
    for field in ("x_label", "y_label"):
        if not metadata.get(field):
            errors.append(f"axis metadata missing: {field}")
    if metadata.get("has_large_title"):
        warnings.append("large in-figure title should be removed")
    manifest_warnings = manifest.get("warnings", [])
    if isinstance(manifest_warnings, list):
        warnings.extend(str(item) for item in manifest_warnings)
    else:
        errors.append("warnings must be a list")
    status = "fail" if errors else "pass"
    manifest["audit_status"] = status
    manifest["audit_errors"] = errors
    manifest["audit_warnings"] = sorted(set(warnings))
    return manifest, {
        "figure_id": manifest.get("figure_id", manifest_path.stem),
        "status": status,
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }


def audit_workspace(workspace: Path) -> dict:
    workspace = workspace.resolve()
    manifests_dir = workspace / "figures" / "manifests"
    manifests = sorted(manifests_dir.glob("*.json")) if manifests_dir.is_dir() else []
    results: list[dict] = []
    for path in manifests:
        manifest, result = _audit_manifest(workspace, path)
        results.append(result)
        if manifest:
            _atomic_json(path, manifest)
    if not results:
        results.append({
            "figure_id": None, "status": "fail",
            "errors": ["no Figure manifests found"], "warnings": [],
        })
    report = {
        "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "figures": results,
    }
    figures_dir = workspace / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(figures_dir / "audit.json", report)
    return report
