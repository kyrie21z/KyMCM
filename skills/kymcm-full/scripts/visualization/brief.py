"""Figure Brief loading and workspace-bound path validation."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


REQUIRED_FIELDS = {
    "id", "problem", "claim", "evidence", "chart_family", "paper_section",
    "target_width", "language", "caption_draft", "mapping",
}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


def workspace_file(workspace: Path, value: str) -> Path:
    root = workspace.resolve()
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Figure path must remain inside workspace: {value}")
    if not path.is_file():
        raise ValueError(f"Figure source is unavailable: {value}")
    return path


def validate_brief(brief: dict, workspace: Path) -> dict:
    if not isinstance(brief, dict):
        raise ValueError("Every Figure Brief must be an object")
    missing = sorted(REQUIRED_FIELDS - brief.keys())
    if missing:
        raise ValueError(f"Figure Brief missing required fields: {missing}")
    if not isinstance(brief["id"], str) or not ID_PATTERN.fullmatch(brief["id"]):
        raise ValueError(f"Invalid Figure Brief id: {brief.get('id')}")
    if not isinstance(brief["problem"], int) or isinstance(brief["problem"], bool) or brief["problem"] < 1:
        raise ValueError("Figure Brief problem must be a positive integer")
    for field in ("claim", "chart_family", "paper_section", "caption_draft"):
        if not isinstance(brief[field], str) or not brief[field].strip():
            raise ValueError(f"Figure Brief {field} must be non-empty")
    if brief["target_width"] not in {"single", "double", "full"}:
        raise ValueError("Figure Brief target_width must be single, double, or full")
    if brief["language"] not in {"zh", "en"}:
        raise ValueError("Figure Brief language must be zh or en")
    if not isinstance(brief["mapping"], dict):
        raise ValueError("Figure Brief mapping must be an object")
    evidence = brief["evidence"]
    if (
        not isinstance(evidence, list)
        or len(evidence) != 1
        or not isinstance(evidence[0], str)
    ):
        raise ValueError(
            "P3.2 Figure Brief requires exactly one CSV evidence file; "
            "merge or export source data before rendering"
        )
    if Path(evidence[0]).suffix.lower() != ".csv":
        raise ValueError(
            "P3.2 Figure Brief requires exactly one CSV evidence file; "
            "merge or export source data before rendering"
        )
    for value in evidence:
        workspace_file(workspace, value)
    return brief


def load_figure_plan(workspace: Path, plan_path: Path | None = None) -> list[dict]:
    path = plan_path or workspace / "figures" / "figure_plan.yaml"
    if not path.is_file():
        raise ValueError(f"Figure plan is unavailable: {path}")
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Figure plan is invalid YAML: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("figures"), list):
        raise ValueError("Figure plan requires a figures list")
    figures = [validate_brief(item, workspace) for item in document["figures"]]
    identifiers = [item["id"] for item in figures]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Figure plan contains duplicate ids")
    return figures


def find_brief(workspace: Path, figure_id: str) -> dict:
    for brief in load_figure_plan(workspace):
        if brief["id"] == figure_id:
            return brief
    raise ValueError(f"Unknown Figure Brief: {figure_id}")
