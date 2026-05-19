"""
Stub Consistency Check — pricing-discount-capsule.
See fitness-functions/artifact-drift.md for the interface contract.

This capsule has no outbound dependencies (ports/outbound/dependencies.yaml
declares an empty list). The check trivially passes.

For a capsule that does have outbound dependencies, this check reads each
stub_behaviours entry, invokes the real dependency with the declared input,
and compares the actual output to the declared stub. See the order-capsule's
implementation for a working example.

Returns a score of 0 (no dependencies to check).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEPENDENCIES_PATH = "ports/outbound/dependencies.yaml"


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    deps_path = directory / DEPENDENCIES_PATH

    if not deps_path.exists():
        return {
            "dependencies_found": False,
            "stubs_checked": 0,
            "stubs_failed": 0,
            "score": 0.0,
            "note": f"{DEPENDENCIES_PATH} not found",
        }

    content = deps_path.read_text(encoding="utf-8")

    if "dependencies: []" in content:
        return {
            "dependencies_found": True,
            "stubs_checked": 0,
            "stubs_failed": 0,
            "score": 0.0,
            "note": "no outbound dependencies declared — nothing to verify",
        }

    # If this capsule gains outbound dependencies in future, implement
    # verification here following the order-capsule pattern.
    return {
        "dependencies_found": True,
        "stubs_checked": 0,
        "stubs_failed": 0,
        "score": 10.0,
        "note": "outbound dependencies declared but no adapter configured for verification",
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 20:
        sys.exit(1)
