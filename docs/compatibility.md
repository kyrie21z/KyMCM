# Compatibility

KyMCM Full 1.0.0 recognizes exactly two explicit markers:

- Full: `{"workflow":"kymcm_full","version":1}`
- Lite v2 compatibility: `{"workflow":"checkpoint_lite","version":2}`

Malformed and unknown markers fail closed. Existing `.kymcm/checkpoint_lite/**` state paths are deliberately retained, and no automatic migration rewrites an existing workspace. `lite_checkpoint.py` delegates to the canonical `full_checkpoint.py` and is deprecated.

An absent marker may use retained Legacy Contract commands. Full commands will not operate on such a workspace.

KyMCM Lite 0.9.3 keeps the separate Lite v3 marker `{"workflow":"kymcm_lite","version":3}`, every base START/RESULT/PRE/HANDOFF/APPENDIX heading, START/RESULT single/split identities, partial split behavior, dependency token grammar, evidence scope, figure behavior, and eight public commands. Existing 0.8.1, 0.9.0, 0.9.1, and 0.9.2 workspaces remain valid and need no migration or Supplement files.

Historical 0.9.2 Supplement compatibility: after a complete checked base question, 0.9.2 retains the 0.9.0/0.9.1 behavior of optionally using one question-level `SUPPLEMENT_START_QN.md` / `SUPPLEMENT_RESULT_QN.md` pair in both single and split modes. S1/S2/... numbering remains continuous. The latest Sx may be edited and rerun in place only while it is unadopted, has no later Sy, and has no downstream or formal-delivery use; a material Start edit first removes/invalidates its old Result. Adopted, non-latest, or superseded-by-Sy entries and their artifacts remain frozen. Existing user-created same-name files are not migrated automatically. Supplement names are ignored by base START/RESULT discovery, and no checker, command, state, JSON, manifest, dependency token, followups directory, or PRE Supplement is added.

The 0.9.3 repository also contains a deterministic complete specification export at `docs/lite-v3/KyMCM_Lite_FULL_SPEC.md`. It is an external ChatGPT Project Source mirror, checked by `scripts/export_kymcm_lite_full_spec.py --check`, and does not change workspace or runtime compatibility. Python does not decide acceptance, adoption, Result invalidation, or artifact overwrite permission; those remain semantic review responsibilities.

`figure/` is an optional known root for explicitly requested final-figure work. Existing workspaces need not create it; init does not create it; an existing user-created root no longer appears as unknown. Lite does not inspect its contents, and it remains outside formal evidence and appendix source scope. Historical plotting code is not moved automatically.

Base RESULT remains the exact dependency-token entry. Current adopted state is base RESULT plus accepted Supplement Result entries applied in order and explicit scope. HANDOFF is a derived neutral technical-transfer document under `problems/qN/notes/`, never a formal fact source or modeling dependency. After each checked Result, stop for explicit user/ChatGPT acceptance; the existing HANDOFF remains the last accepted snapshot until a separate explicit HANDOFF task refreshes it. Appendix may read base RESULT, Supplement Result, and HANDOFF as context but cannot copy those Markdown contracts; current effective Supplement code and result assets remain eligible under existing mappings.

`paper/` is no longer a managed root or appendix source. A legacy directory remains on disk and is completely ignored, even if its contents are malformed, invalid UTF-8, or symlinked. Existing APPENDIX contracts must replace `论文引用、正式结果与认证边界` with `正式结果与认证边界`, replace `正式结果与论文一致性` with `正式结果一致性`, and remove or replace any `paper/...` source. Existing suffixed `HANDOFF_QN_K.md` files are not deleted, renamed, or merged; they remain ordinary notes until the next needed transfer creates the one current `HANDOFF_QN.md`.

Single/split behavior remains as introduced in 0.3.1. Each official question may use contiguous `QN_K` START units with matching RESULT units completed independently. Single and split contracts cannot coexist for one question. Dependencies name exact earlier-question single or split units; no bare-token expansion or same-question edge is added.

A 0.2.0 workspace needs one direct-dependency declaration in every START and completed START/RESULT contracts for declared predecessors. A legacy `FROZEN_CONTEXT.md`, including malformed or invalid UTF-8 content, is ignored by every command and may remain on disk. No automatic migration or deletion is provided. Converting an older question to split mode is manual: replace its unsuffixed contracts with contiguous suffixed contracts, fix titles and downstream exact dependency tokens, then run `doctor` and selected checks.

The optional appendix commands fail only when explicitly invoked and their contracts are absent or invalid. Operational source names such as scheduler, checkpoint, status, monitor, ledger, and audit are accepted as code; runtime checkpoint/status data, logs, caches, binaries, results/data in root `code/`, and unsafe paths remain forbidden. The checker does not classify plotting responsibility, originality, or external similarity. The modeling workflow has no FROZEN_CONTEXT surface; appendix organization may reference, but cannot copy, single or split START/RESULT contracts or matching HANDOFF collaboration documents.

Lite does not read Full v1, historical Lite v2, or marker-less Legacy workspaces. Full and Lite do not guess each other's mode, and no automatic migration is provided.
