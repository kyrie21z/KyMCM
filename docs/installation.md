# Installation

Use Python 3.11, 3.12, or 3.13. Copy either KyMCM Full 1.0.0 (`skills/kymcm-full`) or KyMCM Lite 0.1.0 (`skills/kymcm-lite`) into the Codex skills directory used by your installation; each copied Skill is self-contained.

KyMCM Full requires Git for Result review and uses the repository dependencies:

```bash
python -m pip install -r requirements.txt
```

KyMCM Lite core uses only the Python standard library. Git is optional and produces advisory diagnostics only.

LaTeX is optional and needed only for PDF compilation. Microsoft YaHei is optional; figures fall back to another installed CJK sans-serif font and issue a warning when no suitable font exists. Do not copy proprietary font files into this repository.

From the copied directory, run `python scripts/full_workspace.py doctor --workspace /path/to/contest` for Full or `python scripts/lite.py doctor --workspace /path/to/contest` for Lite.
