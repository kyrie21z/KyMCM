# Installation

Use Python 3.11, 3.12, or 3.13 and Git. Install `requirements.txt`, then copy `skills/kymcm-full` into the Codex skills directory used by your installation. The copied directory is self-contained.

LaTeX is optional and needed only for PDF compilation. Microsoft YaHei is optional; figures fall back to another installed CJK sans-serif font and issue a warning when no suitable font exists. Do not copy proprietary font files into this repository.

Run `python scripts/full_workspace.py doctor --workspace /path/to/contest` from the copied Skill directory to diagnose dependencies, marker, layout, Git, symlinks, and Python compatibility.
