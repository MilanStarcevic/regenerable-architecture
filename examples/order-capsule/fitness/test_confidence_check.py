"""
Test Confidence Check — reference implementation.
See fitness-functions/README.md for the interface contract and tool alternatives.

Measures test suite quality as a guide for safe regeneration.
Returns a score from 0 (no confidence) to 100 (high confidence).
Higher is better — this score is SUBTRACTED from the entropy total.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MIN_TESTS_FOR_CONFIDENCE = 5
ACCEPTANCE_TEST_PATTERNS = ["test_acceptance", "acceptance"]
INVARIANT_TEST_PATTERNS = ["test_invariant", "invariant", "test_property", "property"]


def _count_test_functions(directory: Path) -> tuple[int, bool, bool]:
    """Returns (total_tests, has_acceptance, has_invariants)."""
    total = 0
    has_acceptance = False
    has_invariants = False

    for f in directory.rglob("test_*.py"):
        if any(part.startswith(".") for part in f.parts):
            continue
        try:
            source = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        test_count = source.count("\ndef test_") + source.count("\n    def test_")
        total += test_count

        fname = f.stem.lower()
        if any(pat in fname for pat in ACCEPTANCE_TEST_PATTERNS):
            has_acceptance = True
        if any(pat in fname for pat in INVARIANT_TEST_PATTERNS):
            has_invariants = True

    return total, has_acceptance, has_invariants


def _run_tests(directory: Path) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(directory), "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        passed = result.returncode == 0
        output = (result.stdout + result.stderr).strip()
        return passed, output
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, str(e)


def check_directory(directory: str | Path, run_tests: bool = True) -> dict:
    directory = Path(directory)

    test_dirs = list(directory.rglob("tests"))
    test_search = test_dirs[0] if test_dirs else directory

    total_tests, has_acceptance, has_invariants = _count_test_functions(test_search)

    tests_passed = None
    test_output = ""
    if run_tests:
        tests_passed, test_output = _run_tests(test_search)

    score = 0.0

    score += min(40, (total_tests / max(MIN_TESTS_FOR_CONFIDENCE, 1)) * 20)

    if has_acceptance:
        score += 20

    if has_invariants:
        score += 20

    if tests_passed is True:
        score += 20
    elif tests_passed is False:
        score -= 10

    return {
        "total_tests": total_tests,
        "has_acceptance_tests": has_acceptance,
        "has_invariant_tests": has_invariants,
        "tests_passed": tests_passed,
        "test_output_summary": test_output.split("\n")[-1] if test_output else "",
        "score": round(min(100.0, max(0.0, score)), 1),
    }


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    result = check_directory(target)
    print(json.dumps(result, indent=2))
