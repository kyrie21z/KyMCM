# System dependencies

Required for the Lite core runtime: Python 3.11–3.13 standard library only. Git is optional for Lite and produces advisory diagnostics only. Repository/test dependencies are listed in `requirements.txt`.

The repository exporter `scripts/export_kymcm_lite_full_spec.py` uses only the Python standard library and needs no network, Git command, credentials, or third-party package. It writes the deterministic ChatGPT Project Source only when explicitly invoked.

Optional formal Matplotlib figure execution uses only `matplotlib>=3.7,<4` and `cmcrameri>=1.9,<2` from `skills/kymcm-lite/requirements-figure.txt`, plus locally installed `Noto Serif CJK SC` and `Tinos`; STIX mathtext is configured through Matplotlib. No font is downloaded, copied, or bundled. The narrow test resolver seam validates fail-closed behavior in CI without font binaries, while real execution requires strict local lookup. Missing dependencies or fonts stop rendering.

Optional XeLaTeX-capable TeX Live builds the fixed final-submission `AI 工具使用详情.pdf` and is not a Lite runtime dependency. KyMCM Full's built-in renderer retains its existing Microsoft YaHei/CJK sans-serif behavior. Appendix side-effect checks and the exporter use only the standard library and do not execute submitted code. OpenAI access is required only for the separate optional image-generation helper.
