# Parser Contracts

This document defines expected behavior for diff parser components.

- `UnifiedParser` accepts a single unified-diff file and produces event objects.
- Errors should be raised iff headers are missing or the file cannot be read.
- `MultiFileParser` aggregates multiple parser run results.
