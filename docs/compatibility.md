# Compatibility

KyMCM Full 1.0.0 recognizes exactly two explicit markers:

- Full: `{"workflow":"kymcm_full","version":1}`
- Lite v2 compatibility: `{"workflow":"checkpoint_lite","version":2}`

Malformed and unknown markers fail closed. Existing `.kymcm/checkpoint_lite/**` state paths are deliberately retained, and no automatic migration rewrites an existing workspace. `lite_checkpoint.py` delegates to the canonical `full_checkpoint.py` and is deprecated.

An absent marker may use retained Legacy Contract commands. Full commands will not operate on such a workspace.

KyMCM Lite 0.3.1 keeps the separate Lite v3 marker `{"workflow":"kymcm_lite","version":3}`, the existing eight START headings, seven RESULT headings, and all valid 0.3.0 single-mode workspaces. Each official question may instead use contiguous `QN_K` START units with matching RESULT units completed independently. Single and split contracts cannot coexist for one question. Dependencies name exact earlier-question single or split units; no bare-token expansion or same-question edge is added.

A 0.2.0 workspace needs one direct-dependency declaration in every START and completed START/RESULT contracts for declared predecessors. A legacy `FROZEN_CONTEXT.md`, including malformed or invalid UTF-8 content, is ignored by every command and may remain on disk. No automatic migration or deletion is provided. Converting a 0.3.0 question to split mode is manual: replace its unsuffixed contracts with contiguous suffixed contracts, fix titles and downstream exact dependency tokens, then run `doctor` and selected checks.

The optional appendix commands fail only when explicitly invoked and their contracts are absent or invalid. The modeling workflow has no FROZEN_CONTEXT surface; appendix organization may reference, but cannot copy, single or split START/RESULT contracts.

Lite does not read Full v1, historical Lite v2, or marker-less Legacy workspaces. Full and Lite do not guess each other's mode, and no automatic migration is provided.
