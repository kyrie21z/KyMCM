# System dependencies

Required for Lite runtime: Python 3.11–3.13. Git is optional for Lite and produces advisory diagnostics only. Python packages used by Full are listed in `requirements.txt`.

The repository exporter `scripts/export_kymcm_lite_full_spec.py` uses only the Python standard library and needs no network, Git command, credentials, or third-party package. It writes the deterministic ChatGPT Project Source only when explicitly invoked.

Optional: a LaTeX distribution for PDF compilation. KyMCM Full's built-in renderer retains its existing Microsoft YaHei/CJK sans-serif behavior. KyMCM Lite 0.9.4 final figures use the separate `nature-figure` Skill and require locally installed `Noto Serif CJK SC`, `Tinos`, and STIX mathtext; Lite does not download, bundle, or check those fonts in CI, and missing fonts stop formal rendering. OpenAI access is required only for the separate optional image-generation helper. CI and the checkpoint/figure test suites need neither network access nor credentials.
