# KyMCM Lite final-figure core rules

## Authority and scope

This reference is the authoritative Lite-only core contract for final figures. Its byte-identical repository mirror is `docs/lite-v3/final_figure_core_rules.md`. It applies only to explicitly requested final-figure work after the relevant RESULT and Supplement Result entries have been accepted, any requested HANDOFF task has completed, and structured data and machine evidence are stable.

For a programmatically rendered data figure, first use `final_figure_selection.md` to choose WHAT/WHEN and whether a two-dimensional expression is adequate. Ordinary 2D figures then use `final_figure_style.md`, `final_figure_color.md`, the independent font-family authority `final_figure_typography.md`, and `final_figure_execution.md`; intrinsic-3D figures instead use `final_figure_3d.md` and `figure_3d_exec.py`. The typography contract remains authoritative for Matplotlib font families, while the honest VTK-native text boundary is stated in `final_figure_3d.md`.

The optional `figure_exec.py` and `figure_3d_exec.py` are minimal parameterized visual executors; `figure_bundle.py` validates delivery completeness. They do not create a chart-template library, automatic chart selection, managed figure contract, manifest, workflow state, CLI command, or tool-routing design. The existing optional, non-managed workspace-level `figure/` semantics remain unchanged.

## Codex data-driven figures

1. Put no figure title inside an image. Store the paper-facing title and caption in the same-stem TXT file; the paper layout owns numbering and placement.
2. Axis labels and legends default to Chinese. Keep English only when required for proper nouns, standard abbreviations, variable symbols, units, or terms that should remain English.
3. Put no explanatory paragraph, conclusion, or other body prose inside a figure.
4. Formal visual artifact formats are exactly PDF and PNG. A complete formal programmatic delivery is one same-stem `PDF + PNG + PY + TXT` bundle: PDF is the paper-placement artifact, PNG is the high-resolution raster artifact, PY is the canonical reproducible entrypoint, and TXT owns the paper-facing title and caption.
5. A multi-panel composition may use `(a)`, `(b)`, `(c)`, and subsequent panel markers.
6. Independent subplot titles are absent by default. If axes and legend cannot identify a panel, append only an extremely short panel label such as `(a) 训练集`; sentence-like subtitles remain outside the image.

Allowed in-figure text is limited to axis labels, ticks, legends, panel markers, necessary very-short panel labels, necessary numeric annotations, short threshold/reference symbols, and statistical significance symbols.

The same-stem PY is the canonical figure-specific entrypoint and must satisfy `Path(source_path).resolve() == Path(output_stem).with_suffix(".py").resolve()`. It may load stable prepared data or local helpers from the optional unmanaged `figure/` root.

The same-stem TXT is plain UTF-8 text with one deterministic trailing newline and this exact grammar:

```text
图题：<single non-empty line without paper figure numbering>
图注：
<one or more non-empty caption lines>
```

The caption may explain axes, encodings, units, statistical meaning, thresholds, and `(a)(b)(c)` panel identities, but it cannot fabricate evidence. Final TXT contains no `TODO`, `TBD`, or `待补充` placeholder.

## Macro and algorithm flowchart boundary

A requested macro or algorithm flowchart is not selected by `final_figure_selection.md` and is not rendered or audited by `figure_exec.py`.

1. Read `kymcm-flowchart-selection-v1.md` first to decide whether a flowchart is appropriate and choose one primary M1–M6 or A1–A6 type.
2. Then read `kymcm-flowchart-content-v1.md` to plan node roles, node count, text density, and evidence-aware overload restructuring.
3. ChatGPT or Codex may produce the semantic plan: selected type, nodes, roles, labels, directed connections and branch meanings, stage or subprocess semantics, and content-budget review.
4. Stop before final spatial layout. The user/human author owns final layout judgment and manual drawing.

KyMCM Lite provides no fixed macro grid, default algorithm serpentine, automatic layout engine, renderer/tool route, or active flowchart symbol-family hard rule. Data-driven Pt2 style, Pt3 color, typography, and `figure_exec.py` rules do not silently apply to manually drawn flowcharts. Manually drawn flowcharts have no canonical Python renderer and are outside the four-file programmatic bundle requirement.

## Review gate

Before calling a programmatic data figure final, confirm that its chart choice has a selection-v1 information rationale, it has no internal figure title or explanatory prose, its visual output is PDF/PNG only, its same-stem PY/TXT are present, the TXT contains a non-empty `图题：` and `图注：`, its backend hard audit passed, `validate_figure_bundle()` passed, and ChatGPT/user completed semantic and visual review.

For spatial data, selection-v1 governs WHAT/WHEN expression-level choice, including map + points, categorized spatial views, density views, same-basemap small multiples, and conditional density surfaces. It does not choose a mapping library or vector editor; it routes an already-selected intrinsic-3D information structure to the dedicated PyVista executor. Ordinary Cartesian Pt2 geometry does not silently govern map or VTK geometry where Pt2 excludes it. Macro and algorithm flowcharts use `kymcm-flowchart-selection-v1.md` followed by `kymcm-flowchart-content-v1.md`, then stop at the human-owned final-layout boundary. Manually edited structural illustrations remain outside automatic data-chart selection and style governance unless a later explicit specification says otherwise.
