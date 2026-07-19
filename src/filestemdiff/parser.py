from __future__ import annotations

import itertools
from pathlib import Path
from typing import Iterator, Optional, Sequence, Tuple


class UnifiedParser:
    """Parse a single file's unified diff text into a normalized event stream."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.events: list[dict] = []
        self.hunks: list[dict] = []
        self._parse()

    def _parse(self) -> None:
        lines: list[str] = self.path.read_text(encoding="utf-8", errors="replace").splitlines()
        if not lines:
            return
        if not lines[0].startswith("--- ") or not lines[1].startswith("+++ "):
            raise ValueError(f"Missing unified diff headers in {self.path}")
        self.events.append({"type": "file_header", "old": lines[0][4:], "new": lines[1][4:]})
        self._parse_hunks(lines[2:])

    def _parse_hunks(self, lines: list[str]) -> None:
        hunks_iter = itertools.groupby(lines, lambda line: line.startswith("@@"))
        for is_hunk, group in hunks_iter:
            group_list = list(group)
            if is_hunk:
                self._start_hunk(group_list[0])
            else:
                self.hunks[-1]["lines"].extend([(line, self._op(line)) for line in group_list])

        for hunk in self.hunks:
            self.events.append({"type": "hunk", **hunk})
            remainder = self._compute_remainder(hunk)
            if remainder:
                self.events.append({"type": "hunk_remainder", "unchanged": remainder})

    def _start_hunk(self, header: str) -> None:
        old_range = new_range = None
        for item in header[2:].split():
            item = item.strip()
            if item.startswith("-"):
                old_range = item[1:].split(",")
            elif item.startswith("+"):
                new_range = item[1:].split(",")
        if not old_range or not new_range:
            raise ValueError(f"Unparseable hunk header: {header}")
        old_count = int(old_range[1]) if len(old_range) > 1 else 1
        new_count = int(new_range[1]) if len(new_range) > 1 else 1
        hunk = {
            "header": header,
            "old_start": int(old_range[0]),
            "old_count": int(old_range[1]) if len(old_range) > 1 else 1,
            "new_start": int(new_range[0]),
            "new_count": int(new_range[1]) if len(new_range) > 1 else 1,
            "lines": [],
        }
        self.hunks.append(hunk)

    @staticmethod
    def _op(line: str) -> str:
        if line.startswith("+"):
            return "add"
        if line.startswith("-"):
            return "remove"
        return "context"

    def _compute_remainder(self, hunk: dict) -> Optional[tuple[int, int]]:
        trailing_context = sum(1 for _, op in hunk["lines"] if op == "context")
        end = hunk["old_start"] + hunk["old_count"] + trailing_context
        return (end, 0) if trailing_context else None


class MultiFileParser:
    """Parse multiple files listing ---/+++ pairs into several UnifiedParser streams."""

    def __init__(self, paths: Sequence[Path | str]) -> None:
        self.paths = [Path(p) for p in paths]
        self.event_streams: list[list[dict]] = []
        self._run()

    def _run(self) -> None:
        for path in self.paths:
            try:
                p = UnifiedParser(path)
                self.event_streams.append(p.events)
            except Exception as exc:
                self.event_streams.append([{"type": "error", "path": str(path), "message": str(exc)}])

    @property
    def total_events(self) -> int:
        return sum(len(stream) for stream in self.event_streams)

    @property
    def total_hunks(self) -> int:
        return sum(len([e for e in stream if e.get("type") == "hunk"]) for stream in self.event_streams)
