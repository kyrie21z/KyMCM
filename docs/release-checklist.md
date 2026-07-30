# Release checklist

## Shared checks

- Version, Skill name, and display name agree across release-facing surfaces.
- CI passes on Python 3.11–3.13; Markdown is UTF-8 and repository-relative links resolve.
- The release tree contains no secrets, private data, fonts, caches, bytecode, symlinks, or oversized files.
- `git diff --check` passes and the intended tree is clean before tagging.
- Inspect remote history and existing tags; commit, push, tag, and GitHub Release actions require explicit authorization.

## KyMCM Full checks

- Full version is `1.0.0` and its marker is exactly `{"workflow":"kymcm_full","version":1}`.
- Core, CLI, portability, figure, and Markdown suites pass.
- The independent external-Git Result workflow passes.
- Existing `full-v1.0.0` tag identity and release history remain unchanged.

## KyMCM Lite checks

- Lite 0.8.1 keeps marker `{"workflow":"kymcm_lite","version":3}` and exposes exactly `init`, `doctor`, `check-preprocess-start`, `check-preprocess-result`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result`; only the two QN modeling checks accept optional `--subproblem`.
- Both `modeling_plan_design.md` references have byte parity, and SKILL requires reading the standalone reference.
- Modeling-plan review covers minimum deliverable, preflight, smoke test, staged artifacts/recovery, explicit nested cost, and L0/L1/L2 without adding state, commands, diagnostics, or success artifacts.
- `technical_handoff.md` and HANDOFF template mirrors have byte parity; QN uses one problem-level identity and an ordered formal-upstream list while preserving all eight frozen headings.
- RESULT remains the formal contract and only downstream modeling inheritance surface; HANDOFF is a neutral technical transfer that separates formal/auxiliary material, maps evidence, and states use boundaries.
- `check-result` remains independent of HANDOFF; single and split modes use one `HANDOFF_QN.md`, split requires complete checked RESULT coverage, and no HANDOFF command/state/checker exists.
- Current `HANDOFF_QN.md`, legacy `HANDOFF_QN_K.md`, and HANDOFF_PRE are all rejected as appendix sources; legacy suffixed notes are retained without automatic migration.
- Appendix code covers the complete formal solve pipeline with plotting excluded; root `code/` selects authentic representative core/non-core implementation, including applicable scheduling, recovery, and audit.
- APPENDIX_START/RESULT keep the 0.7.0 certification headings; whitelist grammar is unchanged, and operational source names pass while runtime data, caches, logs, binaries, unsafe paths, and root-code data remain rejected.
- Init and doctor do not require `paper/`; legacy directories are ignored without reads or deletion, and appendix sources are limited to `problems/` and `input/`.
- Formal PRE/QN work is non-visual by default, structured evidence is preferred, and any diagnostic is the smallest one needed for a named risk that non-visual evidence cannot resolve; final figures never count as L0/L1/L2 or formal validation budget.
- `figure/` is exactly one optional known root: init does not create it, doctor ignores arbitrary contents without status or unknown-root output, and it is absent from managed roots, evidence scope, dependencies, contracts, appendix sources, and every checker.
- Explicitly requested final figures use the separate `nature-figure` skill only after RESULT/HANDOFF/data/evidence stabilize; Lite neither bundles/imports it nor adds figure structure, state, JSON, manifests, commands, or silent model reruns.
- Copying, obfuscation, junk/dead code, and similarity-driven rewrites are explicitly forbidden; no external similarity service or automatic originality/plotting checker is added.
- Lite runtime uses only the standard library and remains independent of Full.
- Unit, modeling CLI, appendix CLI, portability, Phase 1, release, and release-tree suites pass.
- Repository and standalone templates have byte parity.
- Doctor and all six checkers preserve workspace fingerprints; all seven read-only commands ignore a legacy invalid-UTF-8 `FROZEN_CONTEXT.md`.
- Single/split layout, contiguous START suffixes, partial RESULT completion, exact selected titles, and exact upstream unit availability are covered; semantic contradiction review remains a Codex/human responsibility and creates no success artifact.
- Evidence control-character, scope, traversal, and symlink guards pass.
- A copied read-only Skill passes from an unrelated working directory.
- Lite tags use `lite-v<version>`; a 0.8.1 tag requires separate release authorization.
