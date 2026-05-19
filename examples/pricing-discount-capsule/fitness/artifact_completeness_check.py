"""
Artifact Completeness Check — reference implementation.
See fitness-functions/artifact-drift.md for the interface contract.

Verifies that all required durable artifacts are present in the capsule.
A capsule missing any of these cannot be safely regenerated regardless of
its implementation entropy score.

Returns a score of 0 (all present) to 100 (all missing).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_ARTIFACTS = [
    "intent.md",
    "regeneration-recipe.md",
    "ports/inbound/openapi.yaml",
    "ports/outbound/dependencies.yaml",
    "tests/test_acceptance.py",
    "tests/test_invariants.py",
    "tests/test_contract.py",
]


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)

    missing = [f for f in REQUIRED_ARTIFACTS if not (directory / f).exists()]
    present = len(REQUIRED_ARTIFACTS) - len(missing)
    score = (len(missing) / len(REQUIRED_ARTIFACTS)) * 100

    return {
        "required": len(REQUIRED_ARTIFACTS),
        "present": present,
        "missing": missing,
        "score": round(score, 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 0:
        sys.exit(1)
