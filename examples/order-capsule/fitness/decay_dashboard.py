"""
Decay Dashboard — Order Capsule

Reference implementation of the implementation decay signal dashboard.
Each signal carries its own status (healthy/watch/warning/critical).
Regeneration is triggered by a policy over the dashboard, not by a single number.

See fitness-functions/README.md for the signal specification and tool alternatives.

Usage:
  python3 fitness/decay_dashboard.py [--verbose]
  python3 examples/order-capsule/fitness/decay_dashboard.py [--verbose]
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

# Status thresholds for each signal.
# For complexity, duplication, dependency_accumulation, and changeability,
# lower raw score is better. For test_confidence, higher is better.
THRESHOLDS: dict[str, list[tuple[float, float, str]]] = {
    "complexity": [
        (0.0, 25.0, "healthy"),
        (25.1, 45.0, "watch"),
        (45.1, 65.0, "warning"),
        (65.1, 100.0, "critical"),
    ],
    "duplication": [
        (0.0, 20.0, "healthy"),
        (20.1, 40.0, "watch"),
        (40.1, 65.0, "warning"),
        (65.1, 100.0, "critical"),
    ],
    "dependency_accumulation": [
        (0.0, 25.0, "healthy"),
        (25.1, 45.0, "watch"),
        (45.1, 70.0, "warning"),
        (70.1, 100.0, "critical"),
    ],
    "test_confidence": [
        (75.0, 100.0, "healthy"),
        (50.0, 74.9, "watch"),
        (25.0, 49.9, "warning"),
        (0.0, 24.9, "critical"),
    ],
    "changeability": [
        (0.0, 20.0, "healthy"),
        (20.1, 40.0, "watch"),
        (40.1, 65.0, "warning"),
        (65.1, 100.0, "critical"),
    ],
    "semantic_drift": [
        (0.0, 10.0, "healthy"),
        (10.1, 30.0, "watch"),
        (30.1, 60.0, "warning"),
        (60.1, 100.0, "critical"),
    ],
}

MECHANICAL_SIGNALS = [
    "complexity",
    "duplication",
    "dependency_accumulation",
    "test_confidence",
    "changeability",
]
JUDGMENT_SIGNALS = ["semantic_drift"]


def _signal_status(signal_name: str, raw: float) -> str:
    for low, high, status in THRESHOLDS[signal_name]:
        if low <= raw <= high:
            return status
    return "critical"


def _make_note(signal_name: str, details: dict) -> str:
    if signal_name == "complexity":
        files = details.get("files_checked", 0)
        branches = details.get("total_branches", 0)
        nesting = details.get("max_nesting", 0)
        long_fn = len(details.get("long_functions", []))
        parts = [f"{files} file(s); {branches} branches; max nesting {nesting}"]
        if long_fn:
            parts.append(f"{long_fn} overlong function(s)")
        return "; ".join(parts)
    elif signal_name == "duplication":
        dup_blocks = details.get("duplicate_blocks", 0)
        dup_lines = details.get("duplicate_lines", 0)
        if dup_blocks == 0 and dup_lines == 0:
            return "no duplicate blocks or lines detected"
        return f"{dup_blocks} duplicate block(s); {dup_lines} duplicate line(s)"
    elif signal_name == "dependency_accumulation":
        ext = details.get("external_imports", 0)
        forbidden = details.get("forbidden_found", [])
        base = f"{ext} external import(s)"
        if forbidden:
            return f"{base}; discouraged: {', '.join(forbidden)}"
        return base
    elif signal_name == "test_confidence":
        total = details.get("total_tests", 0)
        has_acc = details.get("has_acceptance_tests", False)
        has_inv = details.get("has_invariant_tests", False)
        passed = details.get("tests_passed", None)
        parts = [f"{total} tests"]
        parts.append("acceptance tests present" if has_acc else "no acceptance tests")
        parts.append("invariant tests present" if has_inv else "no invariant tests")
        if passed is False:
            parts.append("suite FAILING")
        return "; ".join(parts)
    elif signal_name == "changeability":
        todo = details.get("todo_count", 0)
        churn = details.get("churn_files_in_last_n_commits")
        if todo == 0 and (churn is None or churn == 0):
            return "no deferred markers; low recent churn"
        parts = [f"{todo} deferred marker(s)"]
        if churn is not None:
            parts.append(f"{churn} file changes in last 20 commits")
        return "; ".join(parts)
    elif signal_name == "semantic_drift":
        coverage = details.get("term_coverage", 1.0)
        invariants = details.get("invariants_covered", True)
        pct = round(coverage * 100)
        inv_str = "invariants covered" if invariants else "invariants not covered"
        return f"vocabulary match: {pct}%; {inv_str}"
    return ""


def compute_dashboard(directory: str | Path, verbose: bool = False) -> dict:
    directory = Path(directory)

    raw_checks: dict[str, dict] = {
        "complexity": complexity_check(directory),
        "duplication": duplication_check(directory),
        "dependency_accumulation": dependency_check(directory),
        "test_confidence": test_confidence_check(directory),
        "changeability": changeability_check(directory),
        "semantic_drift": semantic_drift_check(directory),
    }

    dashboard: dict = {}

    for sig in MECHANICAL_SIGNALS:
        details = raw_checks[sig]
        raw = details.get("score", 0.0)
        status = _signal_status(sig, raw)
        note = _make_note(sig, details)
        entry: dict = {"raw": raw, "status": status, "note": note}
        if verbose:
            entry["details"] = details
        dashboard[sig] = entry

    for sig in JUDGMENT_SIGNALS:
        details = raw_checks[sig]
        raw = details.get("score", 0.0)
        status = _signal_status(sig, raw)
        note = _make_note(sig, details)
        entry = {"raw": raw, "status": status, "note": note, "kind": "judgment"}
        if verbose:
            entry["details"] = details
        dashboard[sig] = entry

    trigger, reason = _evaluate_policy(dashboard)

    return {
        "signals": dashboard,
        "regeneration_indicated": trigger,
        "policy_reason": reason,
    }


def _evaluate_policy(dashboard: dict) -> tuple[bool, str]:
    """Default regeneration policy.

    Regenerate when any one of the following holds: a judgment signal is in
    warning or critical; two or more mechanical signals are in warning; any
    single mechanical signal is in critical. This policy is a calibration
    starting point. Teams should expect to adjust it after the first few
    regeneration cycles, based on observed false positives and false negatives.
    """
    for sig in JUDGMENT_SIGNALS:
        status = dashboard[sig]["status"]
        if status in ("warning", "critical"):
            return True, f"judgment signal '{sig}' returned {status}"

    warning_signals = [s for s in MECHANICAL_SIGNALS if dashboard[s]["status"] == "warning"]
    critical_signals = [s for s in MECHANICAL_SIGNALS if dashboard[s]["status"] == "critical"]

    if critical_signals:
        return True, f"mechanical signal in critical: {critical_signals[0]}"
    if len(warning_signals) >= 2:
        names = ", ".join(warning_signals)
        return True, f"{len(warning_signals)} mechanical signals in warning: {names}"

    return False, "all signals within acceptable thresholds"


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    result = compute_dashboard(CAPSULE_DIR, verbose=verbose)
    print(json.dumps(result, indent=2))

    if result["regeneration_indicated"]:
        print(
            f"\nWARNING: Regeneration indicated. Reason: {result['policy_reason']}",
            file=sys.stderr,
        )
        sys.exit(1)
