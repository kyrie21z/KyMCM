# KyMCM

KyMCM is a Codex-native competition modeling workflow with two explicit modes:

- Legacy schema v4 Contract workflow when `.kymcm/mode.json` is absent.
- Checkpoint Lite Pilot v2 when the marker is exactly `{"workflow":"checkpoint_lite","version":2}`.

Invalid markers fail closed. The two modes never share commands or state artifacts. See [SKILL.md](SKILL.md) for mode selection and the Lite command entry point.

Lite v2 adds a whole-problem Definition gate, deterministic full Markdown review documents, structured mathematical Model Specs, lightweight brainstorming guidance, and enforced `problems/qN/` execution boundaries.

Embedded Brainstorming is a dependency-free writing policy inside Problem Definition and Start, not a workflow object or persistence protocol. Material non-unique choices are discussed in normal conversation and written directly into the formal mathematical fields before review.

## Legacy architecture

- Problem Contract for interpretation and the dependency DAG.
- Solution Contract Qi for each problem's mathematical and validation specification.
- User-selectable order among ready independent problems, with exactly one active problem.
- Machine-checkable `results/qN/validation.json` reports.
- Deterministic stale propagation through the dependency DAG.
- Stateless, data-driven paper figures with shared theme, manifests, audit, and gallery.
- One Final Paper Checkpoint before export.

Approved Contracts are versioned and bound by front matter identity plus SHA-256 hash. Contract identity is rechecked at approval, and pending human approval cannot coexist with an active problem. Solution Contracts snapshot their Problem Contract and direct dependency Solution versions. A new Problem Contract conservatively invalidates existing work; a new Solution Contract invalidates its DAG region. Validation and paper gates recheck file hashes and executable evidence. Implementation Plans are ordinary execution checklists and do not require approval. `state/pipeline.json` is the only state authority; `state/events.jsonl` is append-only audit evidence.

The Figure system reads YAML briefs and workspace-local CSV evidence, renders six common chart families to SVG/PDF/PNG, and writes source-hashed JSON manifests. It does not modify schema v4 or add an approval layer.

See [SKILL.md](SKILL.md) for commands, [KyMCM_SOP.md](KyMCM_SOP.md) for the operating procedure, and [the Figure architecture](../../docs/figure_architecture.md) for Brief and manifest interfaces.
