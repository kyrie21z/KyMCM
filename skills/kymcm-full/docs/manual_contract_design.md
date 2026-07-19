# KyMCM Contract Design

Schema v4 has two Contract layers: one Problem Contract and one Solution Contract per problem. Human approval controls mathematical decisions; executable validation controls implementation correctness.

Contract states are `draft`, `pending_review`, `approved`, and `superseded`. Approved content is immutable and hash-locked. A changed decision creates a new version, whose approval supersedes the previous version. Only one Contract may be pending review, and only one problem may be running or blocked.

The Problem Contract owns the dependency DAG and stable topological display order. Independent ready problems may be selected in any order; execution never becomes parallel. A new Problem Contract version conservatively invalidates all existing work.

Solution Contracts own mathematical details and machine-checkable validation criteria. Approval snapshots the current Problem Contract and direct dependency Solution versions. A replacement invalidates its problem and DAG successors, and stale downstream snapshots must be renewed. Implementation Plans are not Contracts, and schema v4 has no micro-stage state.

Validation is structured executable evidence, not AI self-assessment. Problem and global reports are hash-bound and revalidated whenever used. The only non-Contract human gate is the Final Paper Checkpoint after all problems and global consistency validation pass; both submit and approve recheck upstream evidence.
