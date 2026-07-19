#!/usr/bin/env python3
"""Stateless CLI for KyMCM Figure Briefs, rendering, audit, and gallery."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from visualization.audit import audit_workspace
from visualization.brief import load_figure_plan
from visualization.gallery import generate_gallery
from visualization.renderer import render_all, render_figure
from workspace_context import add_workspace_argument, resolve_workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KyMCM stateless Figure manager")
    add_workspace_argument(parser)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="validate the Figure Brief plan")
    commands.add_parser("list", help="list Figure Brief ids")
    render = commands.add_parser("render", help="render one Figure Brief")
    render.add_argument("figure_id")
    commands.add_parser("render-all", help="render every Figure Brief")
    commands.add_parser("audit", help="audit manifests and generated assets")
    commands.add_parser("gallery", help="generate the static HTML gallery")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workspace = resolve_workspace(args.workspace)
    try:
        if args.command in {"plan", "list"}:
            briefs = load_figure_plan(workspace)
            if args.command == "plan":
                print(f"[figure] valid plan: {len(briefs)} figures")
            else:
                for brief in briefs:
                    print(f"{brief['id']}\t{brief['chart_family']}\t{brief['paper_section']}")
        elif args.command == "render":
            manifest = render_figure(workspace, args.figure_id)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        elif args.command == "render-all":
            manifests = render_all(workspace)
            print(f"[figure] rendered: {len(manifests)}")
        elif args.command == "audit":
            report = audit_workspace(workspace)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            if report["status"] != "pass":
                raise SystemExit(1)
        elif args.command == "gallery":
            print(generate_gallery(workspace))
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f"[figure] rejected: {exc}")


if __name__ == "__main__":
    main()
