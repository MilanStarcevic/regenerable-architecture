"""
Test Confidence Check Fitness Function

Measures the quality of the test suite as a guide for safe regeneration.

High test confidence reduces slop risk. Low test confidence means regeneration
is dangerous — the regenerated implementation may diverge from business intent
without being caught.

Metrics:
  - Total test count
  - Presence of acceptance tests
  - Presence of invariant/property-style tests
  - Whether tests pass (via subprocess pytest call)

Returns a score from 0 (no test confidence) to 100 (high confidence).
Higher is better — this score is SUBTRACTED from the slop total.
"""
from __future__ import annotations

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
    """Run pytest and return (passed, output)."""
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

    # Find tests/ subdirectory if it exists
    test_dirs = list(directory.rglob("tests"))
    test_search = test_dirs[0] if test_dirs else directory

    total_tests, has_acceptance, has_invariants = _count_test_functions(test_search)

    tests_passed = None
    test_output = ""
    if run_tests:
        tests_passed, test_output = _run_tests(test_search)

    # Score calculation (higher = more confident = REDUCES slop score)
    score = 0.0

    # Test count contribution (up to 40 points)
    score += min(40, (total_tests / max(MIN_TESTS_FOR_CONFIDENCE, 1)) * 20)

    # Acceptance tests (20 points)
    if has_acceptance:
        score += 20

    # Invariant tests (20 points)
    if has_invariants:
        score += 20

    # Tests passing (20 points)
    if tests_passed is True:
        score += 20
    elif tests_passed is False:
        score -= 10  # Failing tests reduce confidence

    return {
        "total_tests": total_tests,
        "has_acceptance_tests": has_acceptance,
        "has_invariant_tests": has_invariants,
        "tests_passed": tests_passed,
        "test_output_summary": test_output.split("\n")[-1] if test_output else "",
        "score": round(min(100.0, max(0.0, score)), 1),
    }


if __name__ == "__main__":
    import json

    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = check_directory(target)
    print(json.dumps(result, indent=2))
