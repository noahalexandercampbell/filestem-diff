from __future__ import annotations

from difflib import Differ, unified_diff
from pathlib import Path
from typing import Optional


def build_unified_diff(old: Path, new: Path, fromfile: str, tofile: str, context: int = 3) -> str:
    lhs = old.read_text(encoding="utf-8", errors="replace").splitlines()
    rhs = new.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(
        unified_diff(lhs, rhs, fromfile=fromfile, tofile=tofile, n=context)
    ) + "\n"


def humanized_summary(additions: int, removals: int, net: int) -> str:
    parts = []
    if additions:
        parts.append(f"{additions} addition{'s' if additions != 1 else ''}")
    if removals:
        parts.append(f"{removals} removal{'s' if removals != 1 else ''}")
    significance = ["minor", "moderate", "moderate", "noticeable", "significant", "major"][
        min(len(parts), 5)
    ]
    if not parts:
        return "No lines changed."
    return f"{', '.join(parts)} — net {net:+d} ({significance} change)."


def contextual_lines(text: str, needle: str, context: int = 3) -> list[str]:
    lines = text.splitlines()
    hits = [idx for idx, line in enumerate(lines) if needle in line]
    result: list[str] = []
    for idx in hits:
        start = max(0, idx - context)
        end = min(len(lines), idx + context + 1)
        block = lines[start:end]
        if result and block == result[-1]:
            continue
        result.extend(block)
    return result
