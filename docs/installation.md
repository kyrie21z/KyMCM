# Installation

Use Python 3.11, 3.12, or 3.13. Copy either KyMCM Full 1.0.0 (`skills/kymcm-full`) or KyMCM Lite 0.9.12 (`skills/kymcm-lite`) into the Codex skills directory used by your installation; each copied Skill is self-contained.

KyMCM Full requires Git for Result review and uses the repository dependencies:

```bash
python -m pip install -r requirements.txt
```

KyMCM Lite core uses only the Python standard library. Git is optional and produces advisory diagnostics only.

Users who installed Lite by copying the directory must replace/reinstall the complete Skill after updating to 0.9.12 so the corrected full long-form flowchart references, routing metadata, unchanged `figure_exec.py`, and release metadata stay synchronized. Existing 0.9.11 and earlier contest workspaces require no migration and need not create new figure, Supplement, or AI-use files; old appendix packages are not rewritten automatically. Symlink installations need only update the repository and restart Codex.

From the repository root, generate the complete ChatGPT Project Source and verify it after normative changes:

```bash
python scripts/export_kymcm_lite_full_spec.py --output docs/lite-v3/KyMCM_Lite_FULL_SPEC.md
python scripts/export_kymcm_lite_full_spec.py --output docs/lite-v3/KyMCM_Lite_FULL_SPEC.md --check
```

Upload the generated file to ChatGPT Project Sources; do not hand-edit it or copy it into a contest workspace, evidence tree, or appendix.

The Lite core checker remains standalone. For formal Codex/Matplotlib figures, install `skills/kymcm-lite/requirements-figure.txt`; local figure scripts load the exact helper from the active Skill and keep output under the contest workspace's optional `figure/` root. ChatGPT/user performs normal semantic and visual acceptance. The separately installed `nature-figure` Skill is optional only when the user explicitly requests a read-only advisory review of an already-rendered artifact; it is not a normal installation requirement or renderer.

Existing PRE-free 0.5.1 workspaces require no structural or contract rewrite. To adopt PRE, create it in a new workspace with `init --preprocess` or add the exact documented tree and templates manually; historical QN contracts are not rewritten automatically.

For an existing 0.6.0 workspace, leave any legacy `paper/` directory in place or remove it manually; Lite ignores it. Migrate existing APPENDIX headings as documented in `compatibility.md`, replace any source rooted at `paper/`, and rewrite an old HANDOFF with the neutral template only when it next changes materially.

To migrate a 0.2.0 Lite workspace, add exactly one `**前问依赖：** ...` line to section 2 of every START, ensure every declared predecessor has a completed START and RESULT, and rerun `doctor`, `check-start`, and `check-result`. A legacy `FROZEN_CONTEXT.md` may be deleted manually or left in place; current Lite ignores it completely.

LaTeX is optional and needed only for final PDF compilation. For KyMCM Lite 0.9.12, XeLaTeX/TeX Live is an optional final-submission build dependency for the fixed AI-use PDF and is not a Lite runtime dependency. Formal Matplotlib data-figure execution optionally requires `matplotlib`, `cmcrameri`, `Noto Serif CJK SC`, `Tinos`, and STIX mathtext; the helper stops on missing requirements rather than silently falling back. Flowchart selection/content planning and human manual layout add no runtime dependency. For KyMCM Full's built-in renderer, Microsoft YaHei remains an optional existing CJK sans-serif choice and its historical fallback behavior is unchanged. Do not copy or download font files into this repository.

From the copied directory, run `python scripts/full_workspace.py doctor --workspace /path/to/contest` for Full or `python scripts/lite.py doctor --workspace /path/to/contest` for Lite.
