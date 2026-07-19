# Checkpoint Lite standalone MVP

Checkpoint Lite is a future production candidate for KyMCM, but this prototype is not connected to the production pipeline, CLI, schema, or any real contest workspace. It reads and writes only the root explicitly supplied to its standalone storage API; tests use temporary directories.

The design keeps three semantic objects—Problem Definition, Model Spec, and Result Record—plus minimal lifecycle files. The question workflow has six internal states, two stale reasons (`rerun_required` and `replan_required`), and one semantic hash (`spec_hash`). Users see natural-language Problem Definition, Start, and Result reviews.

Artifacts recursively detach and freeze their JSON-like content; exported payloads are fresh mutable copies. Start and Result acceptance rebinds and revalidates the current artifacts, while execution/review states require a valid active Model Spec. The file store rejects checkpoint-directory and artifact-file symlinks before any read or write.

Revision is excluded from `spec_hash`: the hash represents mathematical content only. A replan preserves the previous binding in exploration, and the replacement must both increase revision and change mathematical semantics before a new Start review.

Every newly submitted or accepted Start requires a problem-scoped, read-only pre-start data audit summary inside the existing Model Spec v3 `data_semantics`. It records scope, checks, actual findings, approved treatments, and an empty unresolved list. This content is already bound by `spec_hash`; it is not a fourth semantic object, separate hash, state, checkpoint, artifact, or approval.

Rerun cannot bypass Start review. A mathematical change replans through exploration and a new Start review. Result acceptance must match the existing `result_hash` submitted for review; every route that abandons that review clears the transient binding.

ResultRecord schema v2 is the only supported Result shape. Its deterministic Markdown uses a self-contained summary plus a technical layer, formats raw key values at render time, reads display-only tables from registered CSV evidence, embeds each registered PNG once, and numbers evidence by artifact order. The recommendation in ResultRecord is authoritative; Result CLI commands do not accept a second recommendation string.

The older Checkpoint Phase 0 prototype remains a formal reference. Lite does not import it and does not carry forward its signature state machines, successor-chain decisions, materiality policies, or fine-grained stale taxonomy. This MVP also provides no legacy projection or migration and performs no production integration.

Run its isolated tests from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/checkpoint_lite -v
```
