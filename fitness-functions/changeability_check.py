"""
Changeability Check Fitness Function

Measures implementation stability and change history.

High churn may indicate either healthy evolution or implementation thrashing.
TODO/FIXME/HACK comments are signals that the implementation has known issues
that were deferred rather than resolved.

Metrics:
  - TODO/FIXME/HACK comment count
  - Recent git churn (files changed in last N commits, if git history exists)
  - Unstable file count (files touched more than once in recent history)

Returns a score from 0 (stable) to 100 (high changeability / thrashing risk).
If git history is not available, returns a neutral score with an explanation.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|NOQA|TEMP)\b", re.IGNORECASE)
GIT_LOG_DEPTH = 20


def _count_todos(directory: Path) -> int:
    total = 0
    for f in directory.rglob("*.py"):
        if any(part.startswith(".") for part in f.parts):
            continue
        try:
            source = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        total += len(TODO_PATTERN.findall(source))
    return total


def _git_churn(directory: Path, depth: int = GIT_LOG_DEPTH) -> tuple[list[str], bool]:
    """Returns (list of changed files in last N commits, git_available)."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{depth}", "--name-only", "--pretty=format:", "--", str(directory)],
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
        score += 10  # neutral penalty for missing history

    # TODO/FIXME penalty (up to 30)
    score += min(30, todo_count * 5)

    return {
        "todo_count": todo_count,
        "git_available": git_available,
        "git_note": git_note if not git_available else "",
        "churn_files_in_last_n_commits": len(churn_files) if git_available else None,
        "score": round(min(100.0, score), 1),
    }


if __name__ == "__main__":
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 70:
        sys.exit(1)
