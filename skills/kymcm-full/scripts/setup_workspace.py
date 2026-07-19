#!/usr/bin/env python3
"""
KyMCM Workspace Setup
在当前目录创建标准化的竞赛工作区结构，并初始化必要的占位文件。

用法:
  python scripts/setup_workspace.py
  python scripts/setup_workspace.py --contest MCM
"""

import argparse
import shutil
from pathlib import Path

from workspace_context import add_workspace_argument, resolve_skill_root, resolve_workspace

def setup(contest: str = "CUMCM", workspace: str | Path | None = None):
    root = resolve_workspace(workspace)
    skill_root = resolve_skill_root()
    dirs = [
        root / "data",
        root / "contracts",
        root / "plans",
        root / "src" / "models",
        root / "src" / "verifications",
        root / "results",
        root / "figures" / "manifests",
        root / "figures" / "vector",
        root / "figures" / "preview",
        root / "latex" / "images",
        root / "state",
        root / "output",
    ]
    is_mcm = contest.upper() in {"MCM", "ICM"}
    label = "KyMCM MCM/ICM" if is_mcm else "KyMCM CUMCM"

    print("=" * 58)
    print(f"  {label}  工作区初始化")
    if is_mcm:
        print("  美赛模式 (MCM/ICM) — English paper + mcmthesis")
    print("=" * 58)

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  [创建] {d}")

    events_file = root / "state" / "events.jsonl"
    events_file.touch(exist_ok=True)

    # ── LaTeX 模板 ──────────────────────────────────────────────────────
    if is_mcm:
        template_src = skill_root / "templates" / "mcm_template.tex"
        memo_src     = skill_root / "templates" / "mcm_memo_template.tex"
        template_dst = root / "latex" / "main.tex"
        memo_dst     = root / "latex" / "memo.tex"

        if template_src.exists() and not template_dst.exists():
            shutil.copy(template_src, template_dst)
            print(f"  [复制] MCM 论文模板 → {template_dst}")
        elif not template_dst.exists():
            print(f"  [警告] 模板 {template_src} 不存在，请手动放置")

        if memo_src.exists() and not memo_dst.exists():
            shutil.copy(memo_src, memo_dst)
            print(f"  [复制] Memo 模板    → {memo_dst}")
    else:
        template_src = skill_root / "templates" / "latex_template.tex"
        template_dst = root / "latex" / "main.tex"
        if template_src.exists() and not template_dst.exists():
            shutil.copy(template_src, template_dst)
            print(f"  [复制] 国赛 LaTeX 模板 → {template_dst}")
        elif not template_dst.exists():
            print(f"  [警告] 模板 {template_src} 不存在，请手动放置")

    # ── src/__init__.py ─────────────────────────────────────────────────
    init_py = root / "src" / "__init__.py"
    if not init_py.exists():
        init_py.write_text("# source package\n", encoding="utf-8")

    print()
    print(f"  工作区初始化完成！竞赛: {'MCM/ICM (English)' if is_mcm else 'CUMCM (中文)'}")
    print(f"  工作目录：{root}")
    print("=" * 58)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_workspace_argument(parser)
    parser.add_argument("--contest", choices=["CUMCM", "MCM", "ICM"], default="CUMCM")
    args = parser.parse_args()
    setup(contest=args.contest, workspace=args.workspace)
