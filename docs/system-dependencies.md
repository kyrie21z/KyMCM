# System dependencies

Required for Lite runtime: Python 3.11–3.13. Git is optional for Lite and produces advisory diagnostics only. Python packages used by Full are listed in `requirements.txt`.

The repository exporter `scripts/export_kymcm_lite_full_spec.py` uses only the Python standard library and needs no network, Git command, credentials, or third-party package. It writes the deterministic ChatGPT Project Source only when explicitly invoked.

Optional: a XeLaTeX-capable TeX Live distribution for final PDF compilation. KyMCM Lite 0.9.8 uses it only to build the fixed final-submission `AI 工具使用详情.pdf`; it is not a Lite runtime dependency, and no Python third-party package or font file is required or bundled. KyMCM Full's built-in renderer retains its existing Microsoft YaHei/CJK sans-serif behavior. Lite final figures use the separate `nature-figure` Skill and require locally installed `Noto Serif CJK SC`, `Tinos`, and STIX mathtext; Lite does not download, bundle, or check those fonts in CI, and missing fonts stop formal rendering. Appendix side-effect checks use only the Python standard library and do not execute submitted code. OpenAI access is required only for the separate optional image-generation helper. CI and the checkpoint/figure test suites need neither network access nor credentials.
