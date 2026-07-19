# Core Template Reference

All templates use `render(data, mapping, brief, theme)` internally and are invoked through `figure_manager.py`. Every Figure uses exactly one non-empty workspace-local CSV evidence file loaded as a pandas DataFrame. Required numeric columns must contain only finite values. When data originates from multiple files, modeling code must merge it and export one named, traceable intermediate CSV. Every template exports SVG/PDF/PNG through the shared renderer and never adds a large title.

For templates with `group` or `scenario`, semantic roles determine color and secondary encoding before fallback styling. Use optional `series_roles` in the Figure Brief when labels such as `Model X` do not reveal their role. Built-in labels follow the Brief's `language: zh|en`; explicit axis labels always win.

## line_with_band

- Required mapping: `x`, `y`.
- Optional mapping: `group`, paired `lower` and `upper`.
- Scale: at most 12 series.
- Use for: ordered trends and uncertainty.
- Do not use for: unordered category comparison.
- Brief example: `chart_family: line_with_band`, `mapping: {x: time, y: demand, lower: lo, upper: hi}`.
- Minimum test data: two ordered x/y rows; uncertainty requires both bounds.

## grouped_bar_error

- Required mapping: `category`, `value`.
- Optional mapping: `group`, `error`.
- Scale: at most 20 categories and 8 series.
- Use for: comparing alternatives across common categories.
- Do not use for: dense continuous trends or more categories than can be read at final width.
- Brief example: `mapping: {category: metric, value: score, group: method, error: sd}`.
- Minimum test data: one value per category and group.

## actual_vs_predicted

- Required mapping: `actual`, `predicted`.
- Optional mapping: `group`.
- Scale: at most 50,000 paired points.
- Use for: calibration and prediction agreement.
- Do not use for: unpaired samples or classification probabilities without an observed continuous target.
- Brief example: `mapping: {actual: observed, predicted: estimate}`.
- Minimum test data: two finite paired observations. RMSE and R2 are computed from plotted points.

## residual_diagnostics

- Required mapping: `predicted` plus either `residual` or `actual`.
- Optional mapping: `group` (reserved for future display refinement).
- Scale: at most 50,000 points.
- Use for: residual structure and distribution checks.
- Do not use for: residuals computed under a different data ordering than predictions.
- Brief example: `mapping: {predicted: estimate, residual: error}`.
- Minimum test data: two predicted/residual pairs.

## correlation_heatmap

- Required mapping: `columns`, as a YAML list or comma-separated string.
- Optional mapping: none.
- Scale: 2 to 30 numeric variables; cell annotations are omitted above 12 variables.
- Use for: exploratory linear association.
- Do not use for: causal claims, mixed nonnumeric variables, or nonlinear dependence conclusions.
- Brief example: `mapping: {columns: [temperature, demand, price]}`.
- Minimum test data: two finite numeric columns with at least two rows.

## sensitivity_curve

- Required mapping: `parameter`, `response`.
- Optional mapping: `scenario`, `baseline`.
- Scale: at most 12 series.
- Use for: robustness over an ordered parameter range.
- Do not use for: unordered parameter labels or two-dimensional parameter grids.
- Brief example: `mapping: {parameter: lambda, response: objective, scenario: method}`.
- Minimum test data: two parameter/response rows per scenario.
