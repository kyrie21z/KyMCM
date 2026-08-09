# KyMCM Lite `kymcm-figure-style-v1`

## Authority and scope

This is the frozen Lite style contract for Codex/Matplotlib data-driven final figures. Its byte-identical repository mirror is `docs/lite-v3/final_figure_style.md`. It does not govern macro or algorithm flowcharts, maps, structural illustrations, or manually edited vector illustrations. Read `final_figure_core_rules.md` and `final_figure_color.md` with it. Font families and missing-font behavior remain governed by `final_figure_typography.md`; this document repeats the frozen names only to keep rendering instructions readable.

This is documentation, not a plotting implementation. The `FIGURE_STYLE_V1` summary below is normative data for a future implementation and does not add a dependency, shared plotting module, checker, command, manifest, or workflow state.

## Physical canvas and typography

Generate the formal figure at its final physical size and insert it at the same width. The verified current paper width is 160 mm. Use only these whole-figure templates:

| Template | Final size |
| --- | --- |
| `F-WIDE` | 160 × 60 mm |
| `F-STANDARD` | 160 × 80 mm |
| `F-TALL` | 160 × 105 mm |
| `M-STANDARD` | 128 × 80 mm |

Do not treat 144 mm, 112 mm, or a standalone 80 mm canvas as a normal whole-figure width. The 80 mm value is only a conceptual half-panel scale inside a 160 mm composition. Avoid arbitrary secondary scaling.

Final visual text sizes are identical across all canvas templates:

- axis and colorbar labels: 9.5 pt;
- ticks, legend, and colorbar ticks: 8.5 pt;
- panel marker `(a)`, `(b)`, and so on: 9.5 pt, semibold or bold;
- necessary very-short panel label: 9 pt;
- necessary numeric annotation: 8 pt;
- absolute minimum figure text: 8 pt.

Never shrink fonts proportionally to fit a smaller canvas. Resolve overflow in this order: remove redundancy, reduce tick count, share a legend or colorbar, change the panel arrangement, switch the size template, then split panels that are logically weakly coupled.

Chinese and CJK punctuation use `Noto Serif CJK SC`; English and digits use `Tinos`; mathematics uses `STIX mathtext`. These names must remain consistent with and defer to `final_figure_typography.md`. There is no silent fallback or per-figure font substitution, and font files are not added or shared.

## Global rendering

- Use a pure white, nontransparent background.
- Use antialiasing.
- Use `layout="constrained"` or an explicit `GridSpec` by default.
- Do not combine constrained layout, `tight_layout`, and repeated ad-hoc subplot adjustment in one figure.
- Do not use `bbox_inches="tight"` when it changes the required PDF MediaBox.
- Set `axes.axisbelow = True`.
- Draw in this order: grid, confidence/background interval, main data, marker, error bar, necessary numeric annotation, legend.
- Use no shadows, gradient background, 3D borders, or decorative texture.

## Axes, ticks, and grids

For ordinary Cartesian plots, keep the left and bottom spines and hide the top and right. Heatmaps, matrices, maps, image panels, and special phase planes use their corresponding template or explicit exception rather than ad-hoc styling.

- spine width: 0.7 pt;
- major tick: 0.6 pt wide and 3.2 pt long;
- minor tick: 0.5 pt wide and 1.8 pt long;
- ticks point outward; minor ticks are off by default;
- major grid: solid, 0.4 pt, below data; minor grid is off;
- line, bar, and box plots: y major grid by default;
- scatter: x and y major grid;
- forest and interval plots: numerical-axis grid;
- horizontal bars: x major grid;
- heatmaps and image panels: no ordinary grid;
- explicit 0, 1, target, or constraint reference lines: 0.8–0.9 pt, dashed or dotted;
- ordinary continuous axes: 4–7 major ticks and normally no more than 8;
- label rotation defaults to 0°, then 30° or 45° when needed; reserve 90° for exceptional date or long-category axes.

## Lines, markers, and scatter

Line widths:

- auxiliary: 1.0 pt;
- secondary: 1.2 pt;
- primary: 1.5 pt;
- emphasized/core: 1.8 pt;
- theoretical, baseline, or reference: 0.8–0.9 pt;
- error bar and cap: 0.9 pt;
- ordinary maximum: 1.8 pt; special maximum: 2.0 pt.

Line styles are primary `-`, comparison `(0,(5,2))`, secondary `(0,(5,2,1.5,2))`, and reference `(0,(1.2,1.8))`. A panel normally contains at most six comparable curves and four line styles. A confidence or uncertainty band requires real statistical meaning, has no border by default, and uses alpha 0.14–0.18 with 0.16 as default.

Marker sequence is `o, s, ^, D, v, P, X`. Ordinary markers are 4.5 pt, emphasis markers 5.5 pt, and marker edges 0.6 pt. Mark every point at 12 or fewer points per line, every 2–3 points from 13–30, and by default no points above 30 except meaningful key nodes.

Scatter rules:

| Density | Size | Alpha | Edge |
| --- | --- | --- | --- |
| low, about ≤200 | 18–24 pt² | 0.80–0.90 | 0.4 pt |
| medium, about 200–2000 | 8–14 pt² | 0.45–0.65 | normally none |
| high, above about 2000 | 3–6 pt² | 0.20–0.40 | none |

If dense points remain unreadable, change representation to hexbin, 2D density, contour, or a justified stratified display instead of indefinitely reducing point size. A trend or regression line must name its method, such as linear regression, LOESS, GAM, a theoretical relation, or model prediction; unexplained smoothing is invalid. The main trend line is about 1.5 pt.

## Bars and distributions

For bars:

- single-series width: 0.68 category spacing;
- grouped total width: 0.78; each bar width is `0.78 / series count`;
- edge: 0.6 pt without a heavy pure-black outline;
- ordinary numerical axis starts at zero; use a nonzero baseline only for differences, relative changes, or explicit interval plots;
- bar-top values only when there are about 12 or fewer bars and exact values matter; use 8 pt, 2–3 pt above the bar;
- prefer no more than about 10–12 vertical categories or 15–20 horizontal categories; use horizontal bars for long labels rather than extreme rotation.

For box and distribution plots:

- box width: 0.52 category spacing;
- box edge: 0.9 pt; whisker and cap: 0.8 pt; median: 1.4 pt;
- outlier marker: 2.8–3.2 pt, alpha 0.45–0.65;
- no mean marker and no notch by default;
- retain outliers and never silently use `showfliers=False`;
- for a small-sample overlay use 8–12 pt², alpha 0.35–0.55, and jitter no more than 8% of category spacing.

## Error bars, forest plots, and intervals

- interval line: 0.9–1.0 pt;
- center point: 4.5 pt; emphasized center: 5.5 pt;
- cap length: 2.5 pt; cap width: 0.9 pt;
- baseline vertical line: 0.8–0.9 pt.

Forest plots put labels on the y-axis, use one numerical scale, draw an explicit baseline, and keep each estimate and its interval at the same visual hierarchy.

## Heatmaps and colorbars

For matrices of about 10 × 10 or smaller, light 0.3–0.4 pt cell separators are optional; larger matrices have no cell borders. Show cell numbers only when the total is about 64–100 or fewer, 8 pt text fits physically, and exact values help. A colorbar is about 3–4% of the main axis width with an approximately 2 mm gap, 9.5 pt label, and 8.5 pt ticks. Panels showing the same quantity on the same scale share a colorbar; use separate colorbars only for genuinely different dimensions or ranges.

## Legends

- Omit a single-series legend when axes already communicate its meaning.
- Use one shared legend for repeated objects in a composition.
- Location priority is composition top, composition bottom, clear in-axes blank space, then reserved right-side area.
- Never cover important data.
- Fit an out-of-axes legend inside the fixed canvas without `bbox_inches="tight"`.
- Prefer one row for 1–4 items and no more than two rows for 5–8; redesign above 8.
- Use 8.5 pt text and normally no frame.
- Use approximately 1.6 em handle length, 0.5 em handle-text pad, 1.0 em column spacing, and 0.35 em label spacing.
- If overlap is unavoidable, use a near-white slightly opaque background and only an as-needed 0.5–0.6 pt light border.
- Order items by the paper argument: formal solution, main baseline, secondary baseline, theory/reference; do not sort alphabetically or by drawing order.

## Multi-panel layouts

Recommended arrangements are `F-WIDE` 1×3 or compact 1×2, `F-STANDARD` 1×2 or one core plot, `F-TALL` 2×2 or 2×1, and `M-STANDARD` one panel. Normally avoid `F-WIDE` 2×2, `M-STANDARD` multi-panel, and `F-STANDARD` 1×4.

Physical gaps are 6–8 mm horizontally (7 mm default), 7–9 mm vertically (8 mm default), about 5–6 mm for shared axes (5.5 mm default), and about 2 mm for a colorbar. Share axes or labels only when variable, units, and scale all match. Put the panel marker at the top-left, preferably just outside the axes, approximately 1–2 mm away, and align markers across panels. An ordinary Cartesian plotting area should normally be at least about 40 mm wide × 30–32 mm high.

## Output and allowed adaptation

PDF output keeps text, lines, and basic shapes as vectors; embeds fonts; uses a MediaBox exactly matching the selected physical template; and has a white, nontransparent background. Above roughly 5,000–10,000 scatter points, only the scatter collection may use `rasterized=True`; text, axes, legends, and other lines remain vector.

PNG output is 600 dpi with the same pure-white layout as PDF and no independent re-layout. Formal formats are exactly PDF and PNG, with PDF preferred for paper layout.

Fixed properties are font families and sizes, physical canvas, spine/tick widths, line hierarchy, marker edge, bar width rules, box line widths, legend typography and basic style, panel marker, 8 pt minimum text, and output formats. Explicitly adaptive properties are scatter size/alpha, marker frequency, tick count, legend rows, heatmap cell numbers, shared axes, panel arrangement, and a justified switch to hexbin or density.

## Exceptions

Maps, networks, terrain, image comparisons, 3D geometry, phase plots, complex matrices, and large labeled structural graphics may relax ordinary Cartesian geometry only when the figure:

1. states why the ordinary template is unsuitable;
2. overrides only necessary parameters;
3. retains the font families and at least 8 pt text;
4. retains the physical output size and PDF/PNG requirements;
5. does not silently invent a new style.

No exception may use text below 8 pt, ordinary lines above 2.0 pt, an internal figure title, explanatory prose, or formal formats other than PDF and PNG.

## Normative parameter summary

`FIGURE_STYLE_V1` records:

```text
spine=0.7
major_tick_width=0.6; major_tick_length=3.2
minor_tick_width=0.5; minor_tick_length=1.8
tick_direction="out"; grid=0.4; minor_grid=false; axisbelow=true
aux=1.0; secondary=1.2; primary=1.5; emphasis=1.8
reference=0.85; errorbar=0.9; max_normal=2.0
marker=4.5; emphasis_marker=5.5; marker_edge=0.6
marker_sequence=["o","s","^","D","v","P","X"]
single_bar=0.68; group_total=0.78; bar_edge=0.6
box_width=0.52; box_line=0.9; whisker=0.8; median=1.4
capsize=2.5; band_alpha=0.16
hgap_mm=7.0; vgap_mm=8.0; shared_axis_gap_mm=5.5; colorbar_gap_mm=2.0
png_dpi=600; transparent=false; bbox_inches=none
```

## Acceptance checklist

Before accepting a formal data-driven figure, verify all eleven conditions:

1. PDF physical size exactly matches its template.
2. Text is readable at 100% display size.
3. Every text element is at least 8 pt.
4. There is no clipping, overlap, or abnormal whitespace.
5. Geometry parameters match this contract.
6. Repeated legends, colorbars, and labels are shared where required.
7. The legend hides no important data.
8. Dense scatter does not become an unreadable block.
9. The image has no figure title or explanatory prose.
10. Formal outputs are only PDF and PNG.
11. No local parameter silently overrides the contract.
