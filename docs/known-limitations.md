# Known limitations

- Full v1.0.0 initializes exactly Q1–Q4; variable question counts are not supported.
- A contest workspace must be an independent Git repository before Result review.
- The workflow does not provide numerical solvers or choose a model automatically.
- PDF compilation requires a separately installed LaTeX toolchain.
- Chinese typography depends on locally installed fonts; Microsoft YaHei is preferred but never bundled.
- Legacy Contract compatibility is retained, but new functionality targets Full workspaces.

KyMCM Lite 0.2.0 limitations:

- Structural and evidence checks cannot validate mathematical correctness.
- Git diagnostics are advisory rather than revision bindings.
- Lite does not generate papers or figures, provide solvers, or migrate Full workspaces.
- Lite has no dynamic `add-problem` command; question count is fixed at initialization.
- Lite does not discover models or build/delete appendix trees automatically.
- Appendix checks do not prove semantic equivalence of results, resolve every dynamic import, interpret all CMake, or verify Excel formulas, cached values, merged cells, formatting, or numerical agreement.
- Appendix work does not migrate Full or Lite v2 workspaces and never depends on `FROZEN_CONTEXT.md`.
