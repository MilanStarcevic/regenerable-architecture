"""
Changeability Check — reference implementation.
See fitness-functions/README.md for the interface contract and tool alternatives.

Measures implementation stability via git churn and deferred-problem markers.
Returns a score from 0 (stable) to 100 (high changeability / thrashing risk).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|NOQA|TEMP)\b", re.IGNORECASE)
GIT_LOG_DEPTH = 20


_SKIP = {"fitness", "fitness-functions"}


def _count_todos(directory: Path) -> int:
    total = 0
    for f in directory.rglob("*.py"):
        if any(part.startswith(".") for part in f.parts):
            continue
        if any(part in _SKIP for part in f.parts):
            continue
        try:
            source = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        total += len(TODO_PATTERN.findall(source))
    return total


def _git_churn(directory: Path, depth: int = GIT_LOG_DEPTH) -> tuple[list[str], bool]:
    try:
        result = subprocess.run(
            ["git", "log", f"-{depth}", "--name-only", "--pretty=format:", "--",
             str(directory / "src"), str(directory / "tests")],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=directory,
        )
        if result.returncode != 0:
            return [], False
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return files, True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return [], False


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    todo_count = _count_todos(directory)
    churn_files, git_available = _git_churn(directory)

    score = 0.0
    git_note = ""

    if git_available:
        from collections import Counter
        file_counts = Counter(churn_files)
        total_changes = len(churn_files)
        unstable_files = sum(1 for c in file_counts.values() if c > 1)
        churn_score = min(40, (total_changes / max(GIT_LOG_DEPTH, 1)) * 20)
        unstable_score = min(30, unstable_files * 5)
        score += churn_score + unstable_score
    else:
        git_note = "git history not available; churn metrics skipped"
        score += 10

    score += min(30, todo_count * 5)

    return {
        "todo_count": todo_count,
        "git_available": git_available,
        "git_note": git_note if not git_available else "",
        "churn_files_in_last_n_commits": len(churn_files) if git_available else None,
        "score": round(min(100.0, score), 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
