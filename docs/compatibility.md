# Compatibility

KyMCM Full 1.0.0 recognizes exactly two explicit markers:

- Full: `{"workflow":"kymcm_full","version":1}`
- Lite v2 compatibility: `{"workflow":"checkpoint_lite","version":2}`

Malformed and unknown markers fail closed. Existing `.kymcm/checkpoint_lite/**` state paths are deliberately retained, and no automatic migration rewrites an existing workspace. `lite_checkpoint.py` delegates to the canonical `full_checkpoint.py` and is deprecated.

An absent marker may use retained Legacy Contract commands. Full commands will not operate on such a workspace.

KyMCM Lite 0.5.0 keeps the separate Lite v3 marker `{"workflow":"kymcm_lite","version":3}`, the existing eight START headings, seven RESULT headings, six commands, modeling checker semantics, and every valid 0.4.0 workspace. Existing workspaces do not need HANDOFF files to pass `doctor`, `check-result`, or appendix checks. When an old completed unit next enters real paper collaboration, create its matching HANDOFF manually after confirming RESULT and evidence are stable; historical RESULT files are not rewritten.

RESULT remains formal, concise, auditable, and the only downstream modeling inheritance surface. HANDOFF is a derived, complete paper-writer collaboration document under `problems/qN/notes/`, never a formal fact source or modeling dependency. Single HANDOFF uses `HANDOFF_QN.md`; split HANDOFF uses exact `HANDOFF_QN_K.md` identities without an aggregate. Appendix organization may reference but cannot copy HANDOFF.

Single/split behavior remains as introduced in 0.3.1. Each official question may use contiguous `QN_K` START units with matching RESULT units completed independently. Single and split contracts cannot coexist for one question. Dependencies name exact earlier-question single or split units; no bare-token expansion or same-question edge is added.

A 0.2.0 workspace needs one direct-dependency declaration in every START and completed START/RESULT contracts for declared predecessors. A legacy `FROZEN_CONTEXT.md`, including malformed or invalid UTF-8 content, is ignored by every command and may remain on disk. No automatic migration or deletion is provided. Converting an older question to split mode is manual: replace its unsuffixed contracts with contiguous suffixed contracts, fix titles and downstream exact dependency tokens, then run `doctor` and selected checks.

The optional appendix commands fail only when explicitly invoked and their contracts are absent or invalid. The modeling workflow has no FROZEN_CONTEXT surface; appendix organization may reference, but cannot copy, single or split START/RESULT contracts or matching HANDOFF collaboration documents.

Lite does not read Full v1, historical Lite v2, or marker-less Legacy workspaces. Full and Lite do not guess each other's mode, and no automatic migration is provided.
