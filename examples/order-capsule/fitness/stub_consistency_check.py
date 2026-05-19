"""
Stub Consistency Check — order-capsule.
See fitness-functions/artifact-drift.md for the interface contract.

Reads each stub_behaviours entry in ports/outbound/dependencies.yaml,
invokes the real pricing-discount-capsule with the declared input, and
compares the actual output to the declared stub field by field.

This is the most valuable cross-capsule check: it detects when the real
dependency has changed behavior while the declared stubs have not, a failure
mode that unit tests (which use the stubs) will never catch.

Returns a score of 0 (all stubs consistent) to 100 (all stubs inconsistent).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEPENDENCIES_PATH = "ports/outbound/dependencies.yaml"
CAPSULE_DIR = Path(__file__).parent.parent
PRICING_CAPSULE_SRC = CAPSULE_DIR.parent / "pricing-discount-capsule" / "src"

sys.path.insert(0, str(PRICING_CAPSULE_SRC))

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from pricing_discount_service import calculate_discount
    ADAPTER_AVAILABLE = True
except ImportError:
    ADAPTER_AVAILABLE = False


def _compare_outputs(declared: dict, actual: dict, fields: list[str]) -> list[str]:
    """Return a list of field names where declared and actual differ."""
    mismatches = []
    for field in fields:
        if field not in declared or field not in actual:
            continue
        if declared[field] != actual[field]:
            mismatches.append(field)
    return mismatches


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

    if not YAML_AVAILABLE:
        return {
            "dependencies_found": True,
            "stubs_checked": 0,
            "stubs_failed": 0,
            "score": 10.0,
            "note": "pyyaml not available — install it to enable stub verification",
        }

    if not ADAPTER_AVAILABLE:
        return {
            "dependencies_found": True,
            "stubs_checked": 0,
            "stubs_failed": 0,
            "score": 10.0,
            "note": "pricing-discount-capsule not importable — stubs unverified",
        }

    content = deps_path.read_text(encoding="utf-8")
    deps_data = yaml.safe_load(content)
    dependencies = deps_data.get("dependencies", [])

    if not dependencies:
        return {
            "dependencies_found": True,
            "stubs_checked": 0,
            "stubs_failed": 0,
            "score": 0.0,
            "note": "no outbound dependencies declared",
        }

    stubs_checked = 0
    stubs_failed = 0
    failures = []

    for dep in dependencies:
        capsule_name = dep.get("capsule", "unknown")
        consumed_fields = [
            item["key"]
            for item in (
                {"key": k}
                for entry in dep.get("consumed_outputs", [])
                for k in entry.keys()
            )
        ]
        if not consumed_fields:
            consumed_fields = ["discount_percentage", "explanation"]

        for stub in dep.get("stub_behaviours", []):
            inp = stub.get("input", {})
            declared_output = stub.get("output", {})

            if not inp or not declared_output:
                continue

            stubs_checked += 1

            try:
                actual_output = calculate_discount(
                    customer_tier=inp["customer_tier"],
                    basket_total=inp["basket_total"],
                    active_campaign=inp["active_campaign"],
                )
            except Exception as exc:
                stubs_failed += 1
                failures.append({
                    "capsule": capsule_name,
                    "input": inp,
                    "error": str(exc),
                })
                continue

            mismatches = _compare_outputs(declared_output, actual_output, consumed_fields)
            if mismatches:
                stubs_failed += 1
                failures.append({
                    "capsule": capsule_name,
                    "input": inp,
                    "mismatched_fields": mismatches,
                    "declared": {f: declared_output.get(f) for f in mismatches},
                    "actual": {f: actual_output.get(f) for f in mismatches},
                })

    if stubs_checked == 0:
        score = 0.0
    else:
        score = (stubs_failed / stubs_checked) * 100

    result = {
        "dependencies_found": True,
        "stubs_checked": stubs_checked,
        "stubs_failed": stubs_failed,
        "score": round(score, 1),
    }
    if failures:
        result["failures"] = failures

    return result


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 0:
        sys.exit(1)
