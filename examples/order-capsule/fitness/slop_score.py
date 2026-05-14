"""
Slop Score — Pricing Discount Capsule

Reference implementation of the slop fitness function interface.
See fitness-functions/README.md for the interface specification and tool alternatives.

Usage:
  python3 fitness/slop_score.py [--verbose]
  python3 examples/pricing-discount-capsule/fitness/slop_score.py [--verbose]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from complexity_check import check_directory as complexity_check
from duplication_check import check_directory as duplication_check
from dependency_check import check_directory as dependency_check
from test_confidence_check import check_directory as test_confidence_check
from semantic_drift_check import check_directory as semantic_drift_check
from changeability_check import check_directory as changeability_check

CAPSULE_DIR = Path(__file__).parent.parent
REGENERATION_THRESHOLD = 71

THRESHOLDS = {
    (0, 30): ("healthy", "maintain"),
    (31, 50): ("watch", "monitor trends"),
    (51, 70): ("warning", "refactor"),
    (71, 85): ("high", "regenerate"),
    (86, 100): ("critical", "urgent regeneration"),
}


def _status(score: int) -> tuple[str, str]:
    for (low, high), (status, action) in THRESHOLDS.items():
        if low <= score <= high:
            return status, action
    return "critical", "urgent regeneration"


def compute_slop_score(directory: str | Path, verbose: bool = False) -> dict:
    directory = Path(directory)

    complexity = complexity_check(directory)
    duplication = duplication_check(directory)
    dependency = dependency_check(directory)
    test_confidence = test_confidence_check(directory)
    semantic_drift = semantic_drift_check(directory)
    changeability = changeability_check(directory)

    complexity_score = complexity.get("score", 0)
    duplication_score = duplication.get("score", 0)
    dependency_score = dependency.get("score", 0)
    test_confidence_score = test_confidence.get("score", 0)
    semantic_drift_score = semantic_drift.get("score", 0)
    changeability_score = changeability.get("score", 0)

    raw = (
        complexity_score
        + duplication_score
        + dependency_score
        + semantic_drift_score
        + changeability_score
        - test_confidence_score
    )

    slop_score = max(0, min(100, round(raw)))
    status, recommended_action = _status(slop_score)

    result = {
        "complexity_score": complexity_score,
        "duplication_score": duplication_score,
        "dependency_score": dependency_score,
        "semantic_drift_score": semantic_drift_score,
        "changeability_score": changeability_score,
        "test_confidence_score": test_confidence_score,
        "slop_score": slop_score,
        "status": status,
        "recommended_action": recommended_action,
    }

    if verbose:
        result["details"] = {
            "complexity": complexity,
            "duplication": duplication,
            "dependency": dependency,
            "test_confidence": test_confidence,
            "semantic_drift": semantic_drift,
            "changeability": changeability,
        }

    return result


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = compute_slop_score(CAPSULE_DIR, verbose=verbose)
    print(json.dumps(result, indent=2))

    if result["slop_score"] >= REGENERATION_THRESHOLD:
        print(
            f"\nWARNING: Slop score {result['slop_score']} >= regeneration threshold {REGENERATION_THRESHOLD}.",
            file=sys.stderr,
        )
        print(f"Recommended action: {result['recommended_action']}", file=sys.stderr)
        sys.exit(1)
