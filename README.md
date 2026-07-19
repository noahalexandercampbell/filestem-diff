# FileStemDiff

A small, structured diff and word-level patch engine for file patches and inline text.

## About

`filestemdiff` combines two capabilities in a stdlib-first Python package:

1. A **structured diff/parser** over unified diffs: normalizes hunks, file headers, and line events for downstream tooling or JSON export.
2. A **word-level diff helper** for inline words between two texts, useful for patch previews and education.

The project targets CLI users and library authors who want deterministic, typed diff primitives without heavy dependencies.

## Features

- Parse one or more unified diff files into typed event streams (`file_header`, `hunk`, `hunk_remainder`).
- Summarize additions/removals/net-change for inline patch strings.
- Compute word-level diffs between two texts using stdlib `difflib`.
- Retrieve contextual code lines around a search token.
- Python 3.9+ friendly, type-annotated, minimal footprint.

## Installation

```bash
pip install filestemdiff
```

For development:

```bash
git clone https://github.com/your-org/filestemdiff
cd filestemdiff
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

### Structured unified-diff parsing

```python
from pathlib import Path
from filestemdiff import FileDiffer

differ = FileDiffer()
differ.add_patch(Path("changes.diff").read_text())
print(differ.to_text())
print(differ.summary())
```

### Word-level difference preview

```python
from filestemdiff.differ import FileDiffer

d = FileDiffer()
print(d.to_word_diff("Hello world", "Hello there"))
```

### Contextual hits

```python
from filestemdiff.formatter import contextual_lines

text = "# secrets\nAPI_KEY=abc\n# logs\nAPI_KEY=abc\n"
print(contextual_lines(text, "API_KEY", context=2))
```

## Project structure

```
filestemdiff/
  src/filestemdiff/
    __init__.py       # public exports
    differ.py         # FileDiffer and word diff helper
    formatter.py      # unified diff builders and human summary
    parser.py         # UnifiedParser / MultiFileParser event streams
  tests/
    test_filestemdiff.py
  docs/
    references/
      run-report-format.md
  pyproject.toml
  README.md
```

## Tags / keywords

`diff`, `patch`, `unified-diff`, `word-diff`, `cli`, `developer-tools`, `stdlib`
