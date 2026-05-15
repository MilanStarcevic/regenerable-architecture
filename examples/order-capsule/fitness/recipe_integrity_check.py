"""
Recipe Integrity Check — reference implementation.
See fitness-functions/durable-health.md for the interface contract.

Verifies that every file path explicitly referenced in regeneration-recipe.md
exists on disk relative to the capsule root. Detects the silent drift that
occurs when the capsule is restructured but the recipe is not updated.

Returns a score of 0 (all paths valid) to 100 (all paths broken).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RECIPE_FILENAME = "regeneration-recipe.md"

# Match backtick-quoted paths and bold-backtick paths containing a slash.
# Require a slash so we skip bare filenames already covered by artifact_completeness.
_BACKTICK_PATH = re.compile(r"`([a-zA-Z0-9_./-]+/[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,5})`")

# Match bullet-list items that look like paths: "  - ports/inbound/openapi.yaml"
_BULLET_PATH = re.compile(
    r"^\s{2,}-\s+([a-zA-Z0-9_./-]+/[a-zA-Z0-9_.-]+\.[a-zA-Z]{2,5})\s*$",
    re.MULTILINE,
)

# Skip shell-variable expansions and command-line prefixes
_SKIP_PREFIXES = ("$", "python", "make", "pytest", "http")


def _extract_paths(content: str) -> list[str]:
    candidates: set[str] = set()
    for pattern in (_BACKTICK_PATH, _BULLET_PATH):
        for match in pattern.finditer(content):
            candidate = match.group(1)
            if not any(candidate.startswith(p) for p in _SKIP_PREFIXES):
                candidates.add(candidate)
    return sorted(candidates)


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    recipe_path = directory / RECIPE_FILENAME

    if not recipe_path.exists():
        return {
            "recipe_found": False,
            "paths_checked": 0,
            "broken_paths": [],
            "score": 100.0,
            "note": f"{RECIPE_FILENAME} not found",
        }

    content = recipe_path.read_text(encoding="utf-8")
    candidates = _extract_paths(content)

    if not candidates:
        return {
            "recipe_found": True,
            "paths_checked": 0,
            "broken_paths": [],
            "score": 0.0,
            "note": "no path references found in recipe",
        }

    broken = [p for p in candidates if not (directory / p).exists()]
    score = (len(broken) / len(candidates)) * 100

    return {
        "recipe_found": True,
        "paths_checked": len(candidates),
        "broken_paths": broken,
        "score": round(score, 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 0:
        sys.exit(1)
