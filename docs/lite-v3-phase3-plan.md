# KyMCM Lite v3 Phase 3 Release Plan

Target release: KyMCM Lite `0.1.0`
Future annotated tag: `lite-v0.1.0`

## Release boundary

Phase 3 hardens the accepted Lite v3 MVP, freezes its public contract, aligns release documentation, and produces an uncommitted release candidate for review. It does not publish, commit, push, tag, merge, or create a GitHub Release.

## Hardening scope

- Ignore fenced examples and HTML comments when checking active Markdown semantics.
- Reject malformed, control-character, absolute, traversing, cross-question, missing, directory, and symlink evidence paths safely.
- Roll back every path created by a failed initialization while preserving existing ancestors and unrelated content.
- Verify copied, read-only Skill operation from unrelated directories and non-ASCII paths.
- Keep Git checks advisory and read-only.

## Frozen contract

The commands remain exactly `init`, `doctor`, `check-start`, and `check-result`. The marker remains exactly `{"workflow":"kymcm_lite","version":3}`. Exit codes remain 0 for valid or warnings-only results, 1 for contract/evidence failures, and 2 for tool/environment failures. Lite core remains Python-standard-library-only and independent of Full.

## Verification and isolation

Release tests cover version identity, diagnostics, marker bytes, command surface, template parity, safe paths, rollback, standalone copying, and release-tree hygiene. Lite, Phase 1, release-tree, and Full suites run on the local supported interpreter, while CI retains Python 3.11–3.13. Full source hashes must match the pre-hardening inventory.

## Version freeze and review checkpoint

After focused hardening passes on `0.1.0-dev`, promote `skills/kymcm-lite/VERSION` and current release-facing documentation to `0.1.0`, add dated changelogs and release notes, rerun all gates, and stop with the complete diff uncommitted for user review.

## Conditional publication

Only after separate authorization: inspect and fetch the remote, rerun all gates, commit the reviewed files, push the feature branch, open a PR, wait for CI and merge authorization, then create `lite-v0.1.0` on the reviewed main-branch release commit. A GitHub Release requires another explicit authorization.

## Non-goals

No migration, solver orchestration, model discovery, paper or figure generation, JSON diagnostics, configuration framework, telemetry, network service, multi-agent scheduling, `add-problem`, package publication, or mathematical-correctness claim is added in 0.1.0.
