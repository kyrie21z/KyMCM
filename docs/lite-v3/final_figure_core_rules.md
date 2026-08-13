# KyMCM Lite final-figure core rules

## Authority and scope

This reference is the authoritative Lite-only core contract for final figures. Its byte-identical repository mirror is `docs/lite-v3/final_figure_core_rules.md`. It applies only to explicitly requested final-figure work after the relevant RESULT and Supplement Result entries have been accepted, any requested HANDOFF task has completed, and structured data and machine evidence are stable.

For a Codex/Matplotlib data-driven figure, first use `final_figure_selection.md` to choose WHAT/WHEN, then apply this reference together with `final_figure_style.md`, `final_figure_color.md`, the independent font-family authority `final_figure_typography.md`, and the execution authority `final_figure_execution.md`. The typography contract remains authoritative for font families. The style, color, and execution references do not replace its stop-on-missing-font rule.

These rules use the optional `figure_exec.py` only as a minimal parameterized executor for formal Codex/Matplotlib figures. They do not create a chart-template library, automatic chart selection, managed figure contract, manifest, workflow state, CLI command, or tool-routing design. The existing optional, non-managed workspace-level `figure/` semantics remain unchanged.

## Codex data-driven figures

1. Put no figure title inside an image. The paper layout owns the external figure name and caption.
2. Axis labels and legends default to Chinese. Keep English only when required for proper nouns, standard abbreviations, variable symbols, units, or terms that should remain English.
3. Put no explanatory paragraph, conclusion, or other body prose inside a figure.
4. Formal output formats are exactly PDF and PNG. PDF is preferred for paper layout.
5. A multi-panel composition may use `(a)`, `(b)`, `(c)`, and subsequent panel markers.
6. Independent subplot titles are absent by default. If axes and legend cannot identify a panel, append only an extremely short panel label such as `(a) 训练集`; sentence-like subtitles remain outside the image.

Allowed in-figure text is limited to axis labels, ticks, legends, panel markers, necessary very-short panel labels, necessary numeric annotations, short threshold/reference symbols, and statistical significance symbols.

## Macro modeling flowchart

Use the fixed **4 columns × 3 rows** macro modeling flowchart template. ChatGPT supplies only the text, nodes, and connection plan; it does not directly draw this macro flowchart under this contract. The template does not define or extend external-tool routing.

The data-chart selection hierarchy is defined only by `final_figure_selection.md`. Special-chart and tool routing and the final-figure workflow remain separate paused design topics. Do not infer or design them from this reference.

## Algorithm flowchart

Use a two-row serpentine layout by default:

1. The first row proceeds from left to right.
2. Its last node connects downward.
3. The second row proceeds from right to left.

Only three node shapes are permitted:

- rounded rectangle: start or end;
- rectangle: ordinary step;
- diamond: condition or judgment.

Do not introduce additional flowchart symbol families.

## Review gate

Before calling a data-driven figure final, confirm that its chart choice has a selection-v1 information rationale, it has no internal figure title or explanatory prose, it uses only PDF and PNG formal outputs, it follows the panel-label rule, its machine-safe rules passed `save_formal_figure()`, and it has been reviewed against the style, color, typography, and execution references.

For spatial data, selection-v1 governs WHAT/WHEN expression-level choice, including map + points, categorized spatial views, density views, same-basemap small multiples, and conditional density surfaces. It does not choose a mapping library, vector editor, external tool, or execution route; special-chart and tool routing remains paused. Ordinary Cartesian Pt2 geometry does not silently govern map geometry where Pt2 excludes it. Macro and algorithm flowcharts follow only the frozen Pt1 flowchart rules above. Manually edited structural illustrations remain outside automatic data-chart selection and style governance unless a later explicit specification says otherwise.
