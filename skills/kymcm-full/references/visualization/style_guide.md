# Figure Style Guide

## Output Profiles

| Target width | Size in inches | Typical use |
|---|---:|---|
| `single` | 3.35 × 2.55 | one-column figure |
| `double` | 6.9 × 3.8 | two-column figure |
| `full` | 7.2 × 4.4 | full-width or multi-panel figure |

PNG previews use 300 DPI. SVG and PDF are the editable and LaTeX-first assets. Figures do not contain a large title; the paper owns the caption.

## Typography

- English fallback: `DejaVu Sans`, `Arial`, `Liberation Sans`.
- Chinese fallback: `Microsoft YaHei`, `Noto Sans CJK SC`, `Source Han Sans SC`, `SimHei`, then available sans-serif fallback.
- For a Chinese-language paper, use Chinese by default for natural-language axis labels, legend labels, subplot titles, in-figure annotations, and the caption draft.
- Preserve established proper names, standard abbreviations, model names, mathematical variables, formulas, and units in their conventional English or Latin form where appropriate.
- Do not expose internal English CSV field names directly as display labels; provide readable Chinese labels in the Figure Brief.
- Prefer professional mixed Chinese-English expressions rather than mechanical full translation. Examples: `Panel 1 mean score` → `第一组平均评分`; `Panel 2 - Panel 1 (points)` → `第二组减第一组评分（分）`; `G coefficient` → `$G$ 系数`; `Spearman correlation` → `Spearman 相关系数`; `RMSE = 2.31` remains unchanged.
- Do not add font binaries to the repository.
- Record a warning when no preferred CJK font is available.
- Use 8.5-pt axes and legend text, 8-pt ticks, and 9-pt annotations at final size.

## Visual Encoding

- Proposed method: blue `#0072B2`.
- Baseline: neutral gray `#6B7280`.
- Alternatives: orange `#E69F00`, green `#009E73`, vermilion `#D55E00`, sky `#56B4E9`, purple `#CC79A7`.
- Semantic aliases are resolved before drawing, independent of CSV row or group order. English and Chinese aliases cover Proposed, Baseline, and Alternative roles.
- A Figure Brief may override inference with `series_roles: {display label: proposed|baseline|alternative}`.
- Unknown labels receive color, line style, marker, and hatch from a stable label hash; their style does not depend on first appearance.
- Do not rely on red/green alone. Reinforce important series with line style or marker.
- Use restrained horizontal/major grids where they aid value comparison; no decorative grid.
- Remove top and right spines unless a matrix plot requires a complete frame.
- Keep lines near 1.4 pt and markers near 4 pt at final size.
- Legends must not cover primary evidence; move outside when series count makes an internal legend unsafe.

## Paper Readiness

- Axis labels contain a variable name and unit where a unit exists.
- Uncertainty is visible when it is part of the evidence.
- Series colors retain the same semantics across the paper.
- Black-and-white interpretation should remain possible through luminance, markers, or line styles.
- Check readability at the target physical width, not only in a full-screen preview.
