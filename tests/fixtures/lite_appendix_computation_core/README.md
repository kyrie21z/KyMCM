# Synthetic Appendix tests

The core_write/read_only snippets exercise static checker behavior only; they are
not independently runnable contest programs or evidence of actual reproduction.

The separate reproduce.py → search.cpp/search.hpp chain is a deterministic
synthetic formal implementation. settings.ini and input.csv specify target 7
(2 + 4 + 1), and exhaustive search over integers 0..10 must yield candidate 7
with squared-error objective 0. candidate.txt supplies the accepted candidate
only for the explicitly distinguished fixed-artifact recalculation path.

tests/lite/test_appendix_runtime.py packages these actual sources through the
existing whitelist mappings, builds and runs extracted copies with scrubbed
environment and independent output directories, checks known expected values,
and verifies original/frozen files stay unchanged. Missing source/header/config,
configuration drift and short-search mismatch are real negative cases.
All generated packages, binaries, logs and outputs use temporary directories.
This fixture is not competition material or a user submission.
