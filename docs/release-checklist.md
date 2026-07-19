# Release checklist

- Version, Skill name, display name, and Full marker agree.
- Core, CLI, portability, figure, Markdown, and release-tree tests pass on Python 3.11–3.13.
- Standalone Skill and independent external-Git smoke tests pass.
- Documentation links resolve and the release tree contains no forbidden inputs, caches, secrets, fonts, or personal paths.
- `git diff --check` passes and the repository is clean.
- The annotated release tag points to the intended commit.
- Remote history is inspected before push; pushing and GitHub Release creation require explicit authorization.
