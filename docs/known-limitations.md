# Known limitations

- Full v1.0.0 initializes exactly Q1–Q4; variable question counts are not supported.
- A contest workspace must be an independent Git repository before Result review.
- The workflow does not provide numerical solvers or choose a model automatically.
- PDF compilation requires a separately installed LaTeX toolchain.
- Chinese typography depends on locally installed fonts; Microsoft YaHei is preferred but never bundled.
- Legacy Contract compatibility is retained, but new functionality targets Full workspaces.

KyMCM Lite 0.5.1 limitations:

- Structural and evidence checks cannot validate mathematical correctness or decide whether an experiment plan is proportionate, operationally robust, or over-designed.
- Git diagnostics are advisory rather than revision bindings.
- Lite does not generate papers or figures, provide solvers, or migrate Full workspaces.
- Lite has no dynamic `add-problem` command; question count is fixed at initialization.
- Lite does not discover models or build/delete appendix trees automatically.
- Contract granularity is author-selected; Lite does not infer it from prose or printed subquestions, create split contracts, or compare sibling units automatically.
- Static dependency checks validate exact-token grammar and upstream contract availability, not mathematical consistency, transitive completeness, wildcard expansion, or semantic contradictions. Same-question dependencies remain unsupported.
- Direct-dependency completeness and contradiction decisions remain Codex/human responsibilities; successful reviews create no consistency report.
- L0/L1/L2 classification, smoke-test adequacy, cache/recovery design, nested-cost realism, and modeling-plan quality remain Codex/human responsibilities. The Python checker does not parse or enforce them.
- Python tools do not validate HANDOFF identity, completeness, synchronization, formal/auxiliary classification, evidence fidelity, or writing quality. Codex/ChatGPT and humans remain responsible, and final paper numbers require evidence-level review.
- HANDOFF is not an automatic paper generator and cannot be used as a downstream modeling dependency or formal certification source.
- Appendix checks do not prove semantic equivalence of results, resolve every dynamic import, interpret all CMake, or verify Excel formulas, cached values, merged cells, formatting, or numerical agreement.
- Appendix checks do not determine whether every formal solve source was included, reliably identify plotting responsibilities, verify code originality, query external similarity databases, or certify that CURATE preserved behavior. These require execution evidence and human review.
- Appendix work does not migrate Full or Lite v2 workspaces. The active modeling workflow has no global context file, and appendix organization may reference but cannot copy single or split START/RESULT contracts or matching HANDOFF collaboration documents.
