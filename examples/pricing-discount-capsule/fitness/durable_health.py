"""
Durable Health Score — Pricing Discount Capsule

Composite runner for the durable-layer fitness function.
See fitness-functions/durable-health.md for the interface specification.

Runs five mechanical checks against the capsule's durable artifacts and
produces a weighted composite score. A score above the block threshold
means the durable layer has drifted and regeneration should be gated.

Usage:
  python3 fitness/durable_health.py [--verbose]
  python3 examples/pricing-discount-capsule/fitness/durable_health.py [--verbose]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from artifact_completeness_check import check_directory as artifact_completeness_check
from recipe_integrity_check import check_directory as recipe_integrity_check
from contract_coverage_check import check_directory as contract_coverage_check
from rule_parity_check import check_directory as rule_parity_check
from stub_consistency_check import check_directory as stub_consistency_check

CAPSULE_DIR = Path(__file__).parent.parent

# Weights must sum to 1.0
WEIGHTS = {
    "artifact_completeness": 0.25,
    "recipe_integrity": 0.20,
    "contract_coverage": 0.20,
    "rule_parity": 0.15,
    "stub_consistency": 0.20,
}

# Score thresholds for regeneration gating
THRESHOLDS = {
    (0, 0): ("safe", "durable layer is consistent"),
    (1, 15): ("investigate", "minor drift — review before next change"),
    (16, 30): ("block", "regeneration should be gated until resolved"),
    (31, 100): ("urgently_unsafe", "durable artifacts are severely inconsistent"),
}

BLOCK_THRESHOLD = 16


def _status(score: float) -> tuple[str, str]:
    for (low, high), (status, note) in THRESHOLDS.items():
        if low <= score <= high:
            return status, note
    return "urgently_unsafe", "durable artifacts are severely inconsistent"


def compute_durable_health(directory: str | Path, verbose: bool = False) -> dict:
    directory = Path(directory)

    completeness = artifact_completeness_check(directory)
    recipe = recipe_integrity_check(directory)
    coverage = contract_coverage_check(directory)
    parity = rule_parity_check(directory)
    stubs = stub_consistency_check(directory)

    completeness_score = completeness.get("score", 0.0)
    recipe_score = recipe.get("score", 0.0)
    coverage_score = coverage.get("score", 0.0)
    parity_score = parity.get("score", 0.0)
    stubs_score = stubs.get("score", 0.0)

    composite = (
        completeness_score * WEIGHTS["artifact_completeness"]
        + recipe_score * WEIGHTS["recipe_integrity"]
        + coverage_score * WEIGHTS["contract_coverage"]
        + parity_score * WEIGHTS["rule_parity"]
        + stubs_score * WEIGHTS["stub_consistency"]
    )
    composite = round(max(0.0, min(100.0, composite)), 1)

    status, status_note = _status(composite)
    safe_to_regenerate = composite < BLOCK_THRESHOLD

    result = {
        "artifact_completeness_score": completeness_score,
        "recipe_integrity_score": recipe_score,
        "contract_coverage_score": coverage_score,
        "rule_parity_score": parity_score,
        "stub_consistency_score": stubs_score,
        "durable_health_score": composite,
        "status": status,
        "status_note": status_note,
        "safe_to_regenerate": safe_to_regenerate,
    }

    if verbose:
        result["details"] = {
            "artifact_completeness": completeness,
            "recipe_integrity": recipe,
            "contract_coverage": coverage,
            "rule_parity": parity,
            "stub_consistency": stubs,
        }

    return result


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = compute_durable_health(CAPSULE_DIR, verbose=verbose)
    print(json.dumps(result, indent=2))

    if not result["safe_to_regenerate"]:
        print(
            f"\nWARNING: Durable health score {result['durable_health_score']} >= block threshold {BLOCK_THRESHOLD}.",
            file=sys.stderr,
        )
        print(f"Status: {result['status']} — {result['status_note']}", file=sys.stderr)
        print("Resolve durable artifact drift before regenerating.", file=sys.stderr)
        sys.exit(1)
