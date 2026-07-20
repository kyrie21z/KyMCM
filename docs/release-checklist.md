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

- Lite marker is exactly `{"workflow":"kymcm_lite","version":3}` and commands are exactly `init`, `doctor`, `check-start`, and `check-result`.
- Lite runtime uses only the standard library and remains independent of Full.
- Unit, CLI, portability, Phase 1, release, and release-tree suites pass.
- Repository and standalone templates have byte parity.
- Doctor and both checkers preserve workspace fingerprints.
- Evidence control-character, scope, traversal, and symlink guards pass.
- A copied read-only Skill passes from an unrelated working directory.
- Lite tags use `lite-v<version>`; for 0.1.0 the intended tag is `lite-v0.1.0`.
