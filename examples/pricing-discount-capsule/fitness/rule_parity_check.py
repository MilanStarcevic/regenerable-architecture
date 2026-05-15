"""
Rule Parity Check — reference implementation.
See fitness-functions/durable-health.md for the interface contract.

Compares the count of business rules declared in intent.md against the count
of acceptance test methods in tests/test_acceptance.py. Each rule is expected
to produce several tests (positive case, edge cases, combinations), so a
ratio of 2–8 tests per rule is treated as normal. Significant divergence in
either direction signals that intent and tests have drifted.

Returns a score of 0 (well-matched ratio) to 100 (severe mismatch).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

INTENT_FILENAME = "intent.md"
TEST_ACCEPTANCE_PATH = "tests/test_acceptance.py"

# Expected tests per rule: [low, high]. Outside this range is penalised.
TESTS_PER_RULE_LOW = 2
TESTS_PER_RULE_HIGH = 8


def _count_intent_rules(content: str) -> int:
    """Count data rows in the '| Rule |' business rules table in intent.md."""
    in_rule_table = False
    count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_rule_table:
                break
            continue
        # Detect the header row containing "Rule"
        if re.search(r"\|\s*Rule\s*\|", stripped, re.IGNORECASE):
            in_rule_table = True
            continue
        # Skip the separator row (---|---|---)
        if re.match(r"^\|[-| ]+\|$", stripped):
            continue
        if in_rule_table:
            count += 1
    return count


def _count_test_methods(content: str) -> int:
    """Count test method definitions in a test file."""
    return len(re.findall(r"^\s{4,}def test_", content, re.MULTILINE))


def check_directory(directory: str | Path) -> dict:
    directory = Path(directory)
    intent_path = directory / INTENT_FILENAME
    test_path = directory / TEST_ACCEPTANCE_PATH

    rule_count = 0
    test_count = 0

    if intent_path.exists():
        rule_count = _count_intent_rules(intent_path.read_text(encoding="utf-8"))
    if test_path.exists():
        test_count = _count_test_methods(test_path.read_text(encoding="utf-8"))

    if rule_count == 0 and test_count == 0:
        return {
            "intent_rules": 0,
            "test_methods": 0,
            "score": 50.0,
            "note": "no rules found in intent.md and no tests in test_acceptance.py",
        }

    if rule_count == 0 or test_count == 0:
        return {
            "intent_rules": rule_count,
            "test_methods": test_count,
            "score": 75.0,
            "note": "one side is empty — rules or tests are completely missing",
        }

    low = rule_count * TESTS_PER_RULE_LOW
    high = rule_count * TESTS_PER_RULE_HIGH

    if low <= test_count <= high:
        score = 0.0
        note = "test count within expected range for rule count"
    elif test_count < low:
        deficit = low - test_count
        score = min(100.0, (deficit / max(low, 1)) * 100)
        note = f"under-tested: expected at least {low} tests for {rule_count} rules"
    else:
        excess = test_count - high
        # Over-testing is a milder signal — may include implementation-level tests
        score = min(50.0, (excess / max(high, 1)) * 50)
        note = f"possible implementation tests mixed in: {test_count} tests for {rule_count} rules"

    return {
        "intent_rules": rule_count,
        "test_methods": test_count,
        "expected_range": [low, high],
        "score": round(score, 1),
        "note": note,
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
    if result["score"] > 30:
        sys.exit(1)
