# Full workflow

KyMCM Full uses three reviewed semantic objects: a whole-problem Problem Definition, one Model Spec v3 per question, and one Result Record v2 per completed question. Their deterministic Markdown renderings are the complete human review surfaces.

The state sequence is Problem Definition draft → review → accepted, followed by each dependency-ready question exploring → Start review → approved implementation → Result review → completed. Explicit non-empty user wording is required at every acceptance gate. Hashes bind reviewed JSON, rendered Markdown, artifacts, and Result Git revision.

Pre-Start audit records the structure and meaning of data actually used; it does not fit models. Repair handles implementation failure without semantic change. Replan invalidates approval when interpretation, mathematics, inputs, or conclusions change.

New workspaces use `{"workflow":"kymcm_full","version":1}` and fixed Q1–Q4 directories.
