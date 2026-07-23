# Compatibility

KyMCM Full 1.0.0 recognizes exactly two explicit markers:

- Full: `{"workflow":"kymcm_full","version":1}`
- Lite v2 compatibility: `{"workflow":"checkpoint_lite","version":2}`

Malformed and unknown markers fail closed. Existing `.kymcm/checkpoint_lite/**` state paths are deliberately retained, and no automatic migration rewrites an existing workspace. `lite_checkpoint.py` delegates to the canonical `full_checkpoint.py` and is deprecated.

An absent marker may use retained Legacy Contract commands. Full commands will not operate on such a workspace.

KyMCM Lite 0.2.0 keeps the separate Lite v3 marker `{"workflow":"kymcm_lite","version":3}`. Existing valid 0.1.0 workspaces continue to pass `doctor`, `check-start`, and `check-result` without appendix files. The optional appendix commands fail only when explicitly invoked and their contracts are absent or invalid; they do not read `FROZEN_CONTEXT.md`.

Lite does not read Full v1, historical Lite v2, or marker-less Legacy workspaces. Full and Lite do not guess each other's mode, and no automatic migration is provided.
