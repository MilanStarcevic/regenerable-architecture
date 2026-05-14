"""
Duplication Check — reference implementation.
See fitness-functions/README.md for the interface contract and tool alternatives.

Measures code duplication in Python source files.
Returns a score from 0 (no duplication) to 100 (high duplication).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

MIN_BLOCK_SIZE = 4


def _normalize_lines(source: str) -> list[str]:
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


def _collect_ngrams(lines: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(lines[i : i + n]) for i in range(len(lines) - n + 1)]


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    _SKIP = {"fitness", "fitness-functions"}
    py_files = [
        f for f in directory.rglob("*.py")
        if not any(part.startswith(".") for part in f.parts)
        and not any(part in _SKIP for part in f.parts)
    ]

    all_lines: list[str] = []
    file_lines: dict[str, list[str]] = {}

    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        normalized = _normalize_lines(source)
        file_lines[str(f)] = normalized
        all_lines.extend(normalized)

    if not all_lines:
        return {"files_checked": 0, "duplicate_lines": 0, "duplicate_blocks": 0, "score": 0}

    line_counts = Counter(all_lines)
    duplicate_line_count = sum(count - 1 for line, count in line_counts.items() if count > 1 and len(line) > 10)

    all_blocks = []
    for lines in file_lines.values():
        if len(lines) >= MIN_BLOCK_SIZE:
            all_blocks.extend(_collect_ngrams(lines, MIN_BLOCK_SIZE))

    block_counts = Counter(all_blocks)
    duplicate_block_count = sum(count - 1 for block, count in block_counts.items() if count > 1)

    total = len(all_lines)
    line_dup_ratio = duplicate_line_count / max(total, 1)
    block_dup_ratio = duplicate_block_count / max(len(all_blocks), 1) if all_blocks else 0

    score = min(100.0, (line_dup_ratio * 50) + (block_dup_ratio * 50))

    return {
        "files_checked": len(py_files),
        "total_lines": total,
        "duplicate_lines": duplicate_line_count,
        "duplicate_blocks": duplicate_block_count,
        "line_duplication_ratio": round(line_dup_ratio, 3),
        "score": round(score, 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
