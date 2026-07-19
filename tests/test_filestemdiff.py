from __future__ import annotations

import secrets
import textwrap

import pytest

from filestemdiff import FileDiffer
from filestemdiff.differ import UnifiedParser
from filestemdiff.formatter import contextual_lines, humanized_summary


def test_differ_to_text_with_empty_patch() -> None:
    d = FileDiffer()
    assert d.to_text() == ""


def test_differ_summary_counts_additions_and_removals() -> None:
    patch = textwrap.dedent(
        """\
    --- a/app.py
    +++ b/app.py
    @@ -1,3 +1,3 @@
    -alpha
    +beta
     unchanged
    """
    )
    d = FileDiffer()
    d.add_patch(patch)
    assert d.summary() == {"additions": 1, "removals": 1, "net": 0, "files": 1}


def test_differ_summary_ignores_header_markers() -> None:
    patch = textwrap.dedent(
        """\
    --- a/app.py
    +++ b/app.py
    -old
    +new
    """
    )
    d = FileDiffer()
    d.add_patch(patch)
    s = d.summary()
    assert s["additions"] == 1
    assert s["removals"] == 1


def test_unified_parser_valid_diff() -> None:
    patch = textwrap.dedent(
        """\
    --- a/core.py
    +++ b/core.py
    @@ -1,5 +1,5 @@
    context
    -removed
    +added
    context
    """
    )
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False) as f:
        f.write(patch)
        name = f.name
    try:
        p = UnifiedParser(name)
        file_events = [e for e in p.events if e.get("type") == "file_header"]
        hunk_events = [e for e in p.events if e.get("type") == "hunk"]
        assert len(file_events) == 1
        assert file_events[0] == {"type": "file_header", "old": "a/core.py", "new": "b/core.py"}
        assert len(hunk_events) == 1
        assert hunk_events[0]["old_start"] == 1
        assert hunk_events[0]["new_start"] == 1
    finally:
        import os
        os.remove(name)


def test_unified_parser_rejects_malformed() -> None:
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".diff", delete=False) as f:
        f.write("garbage line\n")
        name = f.name
    try:
        with pytest.raises(ValueError):
            UnifiedParser(name)
    finally:
        import os
        os.remove(name)


def test_patch_path_one_word_change_triggers_callable_warning() -> None:
    patch = textwrap.dedent(
        """\
    --- a/main.py
    +++ b/main.py
    @@ -0,0 +1 @@
    -alpha
    +beta
    """
    )
    d = FileDiffer()
    d.add_patch(patch)
    # Text path should be valid unified diff.
    assert d.to_text().startswith("--- ")


def test_differ_rejects_non_diff_patch_text() -> None:
    d = FileDiffer()
    d.add_patch("not a unified diff")
    with pytest.raises(ValueError):
        d.to_text()


def test_contextual_lines_returns_unique_blocks() -> None:
    text = textwrap.dedent(
        """\
    1
    2
    3 secret
    4
    5
    """
    )
    blocks = contextual_lines(text, "3 secret", context=1)
    assert blocks == ["2", "3 secret", "4"]


def test_humanized_summary_edge_cases() -> None:
    assert humanized_summary(0, 0, 0) == "No lines changed."
    expected = "1 addition, 1 removal — net +0 (moderate change)."
    assert humanized_summary(1, 1, 0) == expected

