# Synthetic Appendix computation-core fixture

This fixture supplies small, contest-free source snippets for Appendix curation
tests. `core_read_only.py` represents an allowed computation core that reads
inputs and assembles results in memory. `core_write.py` and `core_write.cpp`
represent explicit persistence APIs that the static checker must block. The
CSV is an independent formal-result asset; no fixture code regenerates it.
