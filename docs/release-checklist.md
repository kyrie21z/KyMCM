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

- Lite 0.5.0 keeps marker `{"workflow":"kymcm_lite","version":3}` and exposes exactly `init`, `doctor`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result`; only the two modeling checks accept optional `--subproblem`.
- Both `modeling_plan_design.md` references match the supplied SHA-256 `3c508dc1a48a697efcc8b220cde5187727b8b49ba4b81570ca3ab8750e09120b`, and SKILL requires reading the standalone reference.
- Modeling-plan review covers minimum deliverable, preflight, smoke test, staged artifacts/recovery, explicit nested cost, and L0/L1/L2 without adding state, commands, diagnostics, or success artifacts.
- `paper_handoff.md` and HANDOFF template mirrors have byte parity; the template has one exact identity, formal upstream declaration, and eight frozen headings.
- RESULT remains the formal contract and only downstream modeling inheritance surface; HANDOFF is the sole complete paper collaboration medium, separates formal/auxiliary material, maps evidence, and bounds paper expression.
- `check-result` remains independent of HANDOFF, no HANDOFF command/state/checker exists, and single/split HANDOFF files are explicitly rejected as appendix sources.
- Lite runtime uses only the standard library and remains independent of Full.
- Unit, modeling CLI, appendix CLI, portability, Phase 1, release, and release-tree suites pass.
- Repository and standalone templates have byte parity.
- Doctor and all four checkers preserve workspace fingerprints; all five read-only commands ignore a legacy invalid-UTF-8 `FROZEN_CONTEXT.md`.
- Single/split layout, contiguous START suffixes, partial RESULT completion, exact selected titles, and exact upstream unit availability are covered; semantic contradiction review remains a Codex/human responsibility and creates no success artifact.
- Evidence control-character, scope, traversal, and symlink guards pass.
- A copied read-only Skill passes from an unrelated working directory.
- Lite tags use `lite-v<version>`; a 0.5.0 tag requires separate release authorization.
