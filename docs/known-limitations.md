# Known limitations

- Full v1.0.0 initializes exactly Q1–Q4; variable question counts are not supported.
- A contest workspace must be an independent Git repository before Result review.
- The workflow does not provide numerical solvers or choose a model automatically.
- PDF compilation requires a separately installed LaTeX toolchain.
- Full Chinese typography depends on locally installed fonts; Microsoft YaHei is preferred by its existing built-in renderer but never bundled. This Full rule is unchanged by Lite 0.9.4.
- Legacy Contract compatibility is retained, but new functionality targets Full workspaces.

KyMCM Lite 0.9.4 limitations:

- Structural and evidence checks cannot validate mathematical correctness or decide whether an experiment plan is proportionate, operationally robust, or over-designed.
- PRE checks do not execute cleaning, infer whether a question should use PRE, validate EDA quality, or certify causal interpretation.
- Git diagnostics are advisory rather than revision bindings.
- Lite does not generate, plan, read, modify, or check contest manuscripts; infer which final graphics are needed; provide solvers; or migrate Full workspaces.
- Final figures require an explicit user request and the separately installed `nature-figure` Skill. Lite does not check `figure/` structure or asset quality, and figure work may not silently retrain or change formal results.
- Lite final figures additionally require `Noto Serif CJK SC` for Chinese/CJK punctuation, `Tinos` for English/Arabic numerals, and STIX mathtext (`mathtext.fontset = stix`) for formulas and symbols. The external `nature-figure` Skill discovers and audits actual fonts; Lite cannot enforce those fonts from its standard-library runtime, and missing requirements must stop formal rendering rather than silently falling back.
- Lite has no dynamic `add-problem` command; question count is fixed at initialization.
- Lite does not discover models or build/delete appendix trees automatically.
- Contract granularity is author-selected; Lite does not infer it from prose or printed subquestions, create split contracts, or compare sibling units automatically.
- Static dependency checks validate exact-token grammar and upstream contract availability, not mathematical consistency, transitive completeness, wildcard expansion, or semantic contradictions. Same-question dependencies remain unsupported.
- Direct-dependency completeness and contradiction decisions remain Codex/human responsibilities; successful reviews create no consistency report.
- L0/L1/L2 classification, smoke-test adequacy, cache/recovery design, nested-cost realism, and modeling-plan quality remain Codex/human responsibilities. The Python checker does not parse or enforce them.
- Python tools do not validate HANDOFF identity, completeness, synchronization, formal/auxiliary classification, or evidence fidelity. Semantic reviewers remain responsible.
- Python cannot enforce the human RESULT acceptance gate, distinguish an independent HANDOFF task, or prevent an agent from violating the timing boundary; a zero `check-result`/`check-preprocess-result`, green tests/CI, commit, or stable evidence is not semantic acceptance.
- Python tools do not validate Supplement Sx continuity, plan-before-execution, Start/Result correspondence, whether the latest Sx is editable or adopted, adoption triggers, Start/Result invalidation, Sx artifact overwrite permission, replacement scope, mathematical correctness, completed-entry immutability, downstream impact, or HANDOFF currency. Agent semantic review and final human review remain responsible.
- HANDOFF cannot be used as a downstream modeling dependency or formal certification source.
- Lite does not automatically merge or migrate legacy suffixed QN HANDOFF notes; a semantic reviewer must build the current problem-level HANDOFF after all split RESULT units pass and the complete Result set is accepted.
- Appendix checks do not prove semantic equivalence of results, resolve every dynamic import, interpret all CMake, or verify Excel formulas, cached values, merged cells, formatting, or numerical agreement.
- Appendix checks do not determine whether every formal solve source was included, reliably identify plotting responsibilities, verify code originality, query external similarity databases, or certify that CURATE preserved behavior. These require execution evidence and human review.
- Appendix work does not migrate Full or Lite v2 workspaces. The active modeling workflow has no global context file, and appendix organization may reference but cannot copy base START/RESULT, Supplement, or matching HANDOFF internal documents.
- The complete ChatGPT Project Source is a deterministic documentation mirror, not a proof of mathematical correctness or a substitute for Codex execution and human semantic review. Its `--check` mode verifies synchronization, not model claims.
