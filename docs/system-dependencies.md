# System dependencies

Required for Lite runtime: Python 3.11–3.13. Git is optional for Lite and produces advisory diagnostics only. Python packages used by Full are listed in `requirements.txt`.

The repository exporter `scripts/export_kymcm_lite_full_spec.py` uses only the Python standard library and needs no network, Git command, credentials, or third-party package. It writes the deterministic ChatGPT Project Source only when explicitly invoked.

Optional: a LaTeX distribution for PDF compilation and an installed CJK font for Chinese figures. OpenAI access is required only for the separate optional image-generation helper. CI and the checkpoint/figure test suites need neither network access nor credentials.
