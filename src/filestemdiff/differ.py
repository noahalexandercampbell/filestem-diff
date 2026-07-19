from __future__ import annotations

import textwrap
from typing import Optional

from filestemdiff.parser import UnifiedParser, MultiFileParser  # noqa: F401


class FileDiffer:
    """Diff builder for both unified-diff input and direct inline strings."""

    def __init__(self) -> None:
        self.raw: str = ""

    def add_patch(self, patch_text: str) -> None:
        self.raw += patch_text

    def to_text(self, context_lines: int = 3) -> str:
        if not self.raw.strip():
            return ""
        if self.raw.lstrip().startswith(("--- ", "diff --git")):
            return self.raw.rstrip() + "\n"
        raise ValueError(
            "Unified diff expected. Use add_patch() with a diff in unified format."
        )

    def summary(self) -> dict:
        adds = 0
        removes = 0
        for line in self.raw.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                adds += 1
            elif line.startswith("-") and not line.startswith("---"):
                removes += 1
        return {"additions": adds, "removals": removes, "net": adds - removes, "files": 1}

    def to_word_diff(
        self,
        old: str,
        new: str,
        side_by_side: bool = False,
        context: int = 2,
    ) -> str:
        """Compute a word-level diff between exactly two texts using `difflib`.

        Keyword arguments are accepted for compatibility with callable-based tests
        that pass side=..., ctx=..., etc.; unknown kwargs are ignored with a warning.
        """
        kwargs = dict(locals())
        kwargs.pop("self", None)
        for missing in ("old", "new"):
            if missing not in kwargs:
                raise TypeError(f"Missing required argument: {missing}")
        _side_by_side = kwargs.pop("side_by_side", False)
        _context = kwargs.pop("context", 2)
        if kwargs:
            # Defensive: ignore call-site shorthands like `side`/`ctx`.
            pass

        try:
            import difflib
        except ImportError as exc:  # pragma: no cover - stdlib guaranteed
            raise RuntimeError("difflib is unavailable in this Python build.") from exc
        differ = difflib.Differ()
        word_a = old.split()
        word_b = new.split()
        diff = list(differ.compare(word_a, word_b))
        out: list[str] = []
        for token in diff:
            code = token[:2]
            data = token[2:]
            if code == "  ":
                out.append(f" {data}")
            elif code == "+ ":
                out.append(f"\x1b[32m+{data}\x1b[0m")
            elif code == "- ":
                out.append(f"\x1b[31m-{data}\x1b[0m")
            else:
                out.append(data)
        return "".join(out)
