# System dependencies

Required for the Lite core runtime: Python 3.11–3.13 standard library only. Git is optional for Lite and produces advisory diagnostics only. Repository/test dependencies are listed in `requirements.txt`.

The repository exporter `scripts/export_kymcm_lite_full_spec.py` uses only the Python standard library and needs no network, Git command, credentials, or third-party package. It writes the deterministic ChatGPT Project Source only when explicitly invoked.

Optional formal Matplotlib figure execution uses only `matplotlib>=3.7,<4` and `cmcrameri>=1.9,<2` from `skills/kymcm-lite/requirements-figure.txt`, plus locally installed `Noto Serif CJK SC` and `Tinos`; STIX mathtext is configured through Matplotlib. No font is downloaded, copied, or bundled. The narrow test resolver seam validates fail-closed behavior in CI without font binaries, while real execution requires strict local lookup. Missing dependencies or fonts stop rendering.

Optional intrinsic-3D execution uses `skills/kymcm-lite/requirements-figure-3d.txt`: the existing figure requirements plus `pyvista>=0.48,<0.49` and `vtk>=9.5,<9.6`. PyVista/VTK renders the authoritative PNG off-screen with SSAA; Matplotlib only packages that raster into the exact physical-size PDF. Stock VTK wheels support Python 3.11–3.13, while Linux/WSL/server machines must provide a working headless EGL/OpenGL runtime. No Qt, trame, X server, downloaded dataset, mesh, or font is required by the executor.

Normal formal figures do not require `nature-figure`. That separately installed Skill is optional only when the user explicitly requests a read-only advisory specialist review of an already-rendered artifact; it is not a renderer, fallback, or acceptance authority for KyMCM Lite.

Optional XeLaTeX-capable TeX Live builds the final-submission `AI 工具使用详情.pdf` and is not a Lite runtime dependency. KyMCM Full's built-in renderer retains its existing Microsoft YaHei/CJK sans-serif behavior. Appendix structural/dependency checks and the exporter use only the standard library and do not execute submitted code. Actual Appendix reproduction uses the submitted package's declared compiler and dependencies, not the checker. Repository mixed-language tests use Python stdlib plus g++ with C++17; compiler absence is an explicit skip, and release requires a recorded real run. OpenAI access is required only for the separate optional image-generation helper.
