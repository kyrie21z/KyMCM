# Installation

Use Python 3.11, 3.12, or 3.13. Copy either KyMCM Full 1.0.0 (`skills/kymcm-full`) or KyMCM Lite 0.5.1 (`skills/kymcm-lite`) into the Codex skills directory used by your installation; each copied Skill is self-contained.

KyMCM Full requires Git for Result review and uses the repository dependencies:

```bash
python -m pip install -r requirements.txt
```

KyMCM Lite core uses only the Python standard library. Git is optional and produces advisory diagnostics only.

Users who installed Lite by copying the directory must replace/reinstall the complete Skill after updating to 0.5.1 so the appendix reference, templates, runtime rules, and release metadata stay synchronized. Symlink installations need only update the repository and restart Codex.

Existing 0.5.0 workspaces require no structural or contract rewrite for 0.5.1. Existing completed appendix packages are not rewritten automatically; apply the complete-formal-code and representative-paper-code policy when they are next reorganized or resubmitted.

To migrate a 0.2.0 Lite workspace, add exactly one `**前问依赖：** ...` line to section 2 of every START, ensure every declared predecessor has a completed START and RESULT, and rerun `doctor`, `check-start`, and `check-result`. A legacy `FROZEN_CONTEXT.md` may be deleted manually or left in place; current Lite ignores it completely.

LaTeX is optional and needed only for PDF compilation. Microsoft YaHei is optional; figures fall back to another installed CJK sans-serif font and issue a warning when no suitable font exists. Do not copy proprietary font files into this repository.

From the copied directory, run `python scripts/full_workspace.py doctor --workspace /path/to/contest` for Full or `python scripts/lite.py doctor --workspace /path/to/contest` for Lite.
