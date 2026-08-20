# KyMCM Lite `kymcm-figure-exec-v1`

## Authority and boundary

This reference is the ordinary 2D execution authority for formal Codex/Matplotlib data-driven figures. Its byte-identical repository mirror is `docs/lite-v3/final_figure_execution.md`. The executable visual authority is `skills/kymcm-lite/figure_exec.py` in the active KyMCM Lite Skill installation. Intrinsic-3D figures use `final_figure_3d.md` and `figure_3d_exec.py` instead.

The execution helper applies and audits the machine-safe hard subset of the accepted Pt1 core, Pt2 style, Pt3 color, and typography contracts. It does not choose a chart family, alter data, recompute a model, decide a statistic, invent a semantic layout, route a special tool, or create workflow state. It is a small parameterized executor, not a chart-template library.

Lite core commands under `scripts/` remain standard-library-only. Formal Matplotlib execution is optional and requires the packages in `requirements-figure.txt` plus locally installed `Tinos` and `Noto Serif CJK SC`. Importing `figure_exec.py` does not eagerly import Matplotlib or `cmcrameri`. The standalone standard-library-only `figure_bundle.py` is the separate delivery authority for both programmatic backends.

## Machine-enforced rules

`figure_exec.py` fails closed on the machine-safe rules it owns:

- the four physical canvas templates and their exact final size;
- strict availability of `Tinos` and `Noto Serif CJK SC`, script-aware declared `Text`-family routing, the base font stack, STIX mathtext, and PDF font type 42;
- the 8 pt absolute minimum for rendered text;
- absence of figure titles and subplot/axes titles;
- fixed tick, spine, grid, line, marker, bar, box, error-bar, gap, and uncertainty constants;
- the frozen qualitative, semantic, neutral, missing, and infeasible color helpers;
- common visible Matplotlib artist colors and the 2.0 pt ordinary line maximum;
- controlled `cmcrameri` lookup for `batlow` and `vik`, without a substitute color map;
- use of `apply_axis_style()` by every applicable ordinary axis;
- the visual pair as same-layout PDF and PNG only, PNG at 600 dpi;
- a white nontransparent background and `bbox_inches=None`;
- a PDF MediaBox and PNG dimensions consistent with the selected physical template.

Missing dependencies, missing fonts, unknown qualitative colors, more than seven qualitative categories, an uncontrolled continuous map, an unstyled applicable axis, or another failed hard check stops formal rendering. The helper does not download, copy, vendor, or substitute fonts.

## Semantic and visual review

The following remain explicit semantic or visual judgments and are not presented as machine-decidable:

- whether English is genuinely necessary instead of Chinese;
- whether an annotation is necessary numeric or threshold text rather than prohibited explanatory prose;
- whether a semantic color role is conceptually correct;
- whether a confidence or uncertainty band has valid statistical meaning;
- whether the selected chart family and information level answer the named information need;
- whether legends overlap data or the complete composition is broadly readable;
- whether the final rendered mixed Chinese/Latin text is visually correct beyond declared-family routing;
- whether a spatial exception or non-Matplotlib tool route is justified.

ChatGPT and the user retain responsibility for these judgments in the normal path. Passing the hard audit is necessary but is not semantic or visual acceptance.

## Required formal sequence

For a formal Codex/Matplotlib data-driven figure, execute this sequence:

```text
selection-v1 chooses WHAT/WHEN
→ read Pt1 core, Pt2 style, Pt3 color, typography, and execution-v1
→ load figure_exec.py from the active Skill installation
→ configure_matplotlib()
→ construct the selected figure using helpers without redeclaring locked constants
→ apply_axis_style() to every applicable axis
→ save_formal_figure() performs the 2D hard audit and writes the PDF + PNG visual pair
→ the same-stem PY calls write_figure_note() for 图题/图注 TXT
→ validate_figure_bundle(stem, source_path=__file__) verifies PDF + PNG + PY + TXT
→ ChatGPT/user performs semantic and visual review of the rendered artifact
→ only then call the output final
```

This is an execution sequence, not stored workflow state. `nature-figure` is not required for it. If the active Skill directory is not importable, load that exact `figure_exec.py` by absolute path. Do not copy it or rewrite its constants in the contest workspace. Local plotting code may choose only the adaptive options already documented by Pt2/Pt3 and may not override locked values.

If the user explicitly requests an independent specialist review, the separately installed `nature-figure` Skill may inspect the already-rendered PDF/PNG read-only. It is advisory only: it cannot choose or reclassify the chart family, apply its own contract/theme/rcParams/palette/typography/canvas/export defaults, rerender, restyle, export, overwrite, or replace the KyMCM artifact or its acceptance authority. Recommendations return to Codex, are implemented through the KyMCM plotting code and `figure_exec.py`, pass the hard audit again, and then return to ChatGPT/user review.

The figure-specific entrypoint name is the desired output stem: for example, `figure/foo.py` regenerates `figure/foo.pdf`, `figure/foo.png`, and `figure/foo.txt`. Formal 2D delivery code must call `save_formal_figure()` instead of calling `fig.savefig()` or `plt.savefig()` directly, then call the bundle helpers. A PDF/PNG pair that has not passed the bundle audit is not a complete final programmatic figure. Existing accepted output remains authoritative when a new attempt fails. Flowcharts and non-programmatic manually edited illustrations do not use these helpers.

## Public product boundary

`kymcm-figure-exec-v1` and `kymcm-figure-bundle-v1` add no public CLI command, managed figure root, checker command, state, manifest, content JSON, approval record, hash ledger, chart-template API, automatic chart selection, or KyMCM Full behavior. The public Lite CLI remains exactly eight commands, and the workspace-level `figure/` directory remains optional and unmanaged.
