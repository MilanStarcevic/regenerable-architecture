"""
Contract Coverage Check — reference implementation.
See fitness-functions/artifact-drift.md for the interface contract.

Verifies that every required field declared in ports/inbound/openapi.yaml
has at least one reference in tests/test_contract.py. An uncovered required
field is an unverified contract claim: regeneration may omit or mistype it
without any test catching it.

Returns a score of 0 (all fields covered) to 100 (no fields covered).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

OPENAPI_PATH = "ports/inbound/openapi.yaml"
CONTRACT_TEST_PATH = "tests/test_contract.py"

# Match YAML block-style required list:
#   required:
#     - field_name
_BLOCK_REQUIRED = re.compile(
    r"required:\s*\n((?:[ \t]+-[ \t]+\S+\n)+)",
    re.MULTILINE,
)

# Match YAML inline-style required list:
#   required: [field1, field2]
_INLINE_REQUIRED = re.compile(r"required:\s*\[([^\]]+)\]")


def _extract_required_fields(yaml_content: str) -> list[str]:
    fields: set[str] = set()

    for match in _BLOCK_REQUIRED.finditer(yaml_content):
        for item in re.findall(r"-\s+(\S+)", match.group(1)):
            fields.add(item.strip())

    for match in _INLINE_REQUIRED.finditer(yaml_content):
        for item in re.split(r"[,\s]+", match.group(1)):
            item = item.strip()
            if item:
                fields.add(item)

    return sorted(fields)


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    openapi_path = directory / OPENAPI_PATH
    test_path = directory / CONTRACT_TEST_PATH

    if not openapi_path.exists():
        return {
            "contract_found": False,
            "fields_checked": 0,
            "uncovered_fields": [],
            "score": 50.0,
            "note": f"{OPENAPI_PATH} not found",
        }

    if not test_path.exists():
        return {
            "contract_found": True,
            "test_found": False,
            "fields_checked": 0,
            "uncovered_fields": [],
            "score": 100.0,
            "note": f"{CONTRACT_TEST_PATH} not found",
        }

    yaml_content = openapi_path.read_text(encoding="utf-8")
    test_content = test_path.read_text(encoding="utf-8")
    required_fields = _extract_required_fields(yaml_content)

    if not required_fields:
        return {
            "contract_found": True,
            "test_found": True,
            "fields_checked": 0,
            "uncovered_fields": [],
            "score": 0.0,
            "note": "no required fields found in contract",
        }

    uncovered = [f for f in required_fields if f not in test_content]
    score = (len(uncovered) / len(required_fields)) * 100

    return {
        "contract_found": True,
        "test_found": True,
        "fields_checked": len(required_fields),
        "covered": len(required_fields) - len(uncovered),
        "uncovered_fields": uncovered,
        "score": round(score, 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 0:
        sys.exit(1)
