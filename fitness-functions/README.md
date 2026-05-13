# Fitness Functions

This directory contains the slop measurement fitness functions for Regenerable Architecture.

## Overview

Fitness functions are automated checks that evaluate whether a capability capsule meets the architectural health goals defined for it. In Regenerable Architecture, fitness functions measure **AI slop**—the accumulation of quality decay in generated implementations.

## Files

| File | Purpose |
|---|---|
| `slop_score.py` | Aggregator: runs all checks and produces a composite score |
| `complexity_check.py` | Measures structural complexity (function length, branches, nesting) |
| `duplication_check.py` | Detects duplicated lines and repeated code blocks |
| `dependency_check.py` | Measures import health (count, external deps, forbidden libs) |
| `test_confidence_check.py` | Evaluates test quality (count, acceptance tests, invariants, pass status) |
| `semantic_drift_check.py` | Checks alignment between implementation and intent.md |
| `changeability_check.py` | Measures churn and TODO/FIXME comment count |

## Usage

Run against a capsule directory:

```bash
python fitness-functions/slop_score.py examples/pricing-discount-capsule
```

With verbose output:

```bash
python fitness-functions/slop_score.py examples/pricing-discount-capsule --verbose
```

Run an individual check:

```bash
python fitness-functions/complexity_check.py examples/pricing-discount-capsule
python fitness-functions/duplication_check.py examples/pricing-discount-capsule
python fitness-functions/dependency_check.py examples/pricing-discount-capsule
python fitness-functions/test_confidence_check.py examples/pricing-discount-capsule
python fitness-functions/semantic_drift_check.py examples/pricing-discount-capsule
python fitness-functions/changeability_check.py examples/pricing-discount-capsule
```

## Slop Score Formula

```
Slop Score =
  complexity_score
+ duplication_score
+ dependency_score
+ semantic_drift_score
+ changeability_score
- test_confidence_score
```

Normalized to 0–100.

| Score | Status | Action |
|---|---|---|
| 0–30 | Healthy | Maintain |
| 31–50 | Watch | Monitor trends |
| 51–70 | Warning | Refactor |
| 71–85 | High | Regenerate |
| 86–100 | Critical | Urgent regeneration |

## Exit Codes

- `0`: Score below regeneration threshold (healthy / watch / warning)
- `1`: Score at or above regeneration threshold (71+)
- `2`: Usage error

## Extending the Fitness Functions

To add a new check:

1. Create a new `*_check.py` file in this directory
2. Implement a `check_directory(directory: str | Path) -> dict` function
3. Include a `"score"` key (0–100) in the return dict
4. Import and call it in `slop_score.py`
5. Add it to the formula with appropriate weighting

## Limitations

These fitness functions are heuristics. They are designed to demonstrate the concept and produce useful signals for the demo capsule. In production systems, you would want:

- **Complexity**: Use `radon` or `flake8` with complexity thresholds for more accurate cyclomatic complexity
- **Duplication**: Use `pylint` similarity checker or dedicated duplication detection tools
- **Semantic drift**: LLM-assisted review comparing intent.md to implementation behavior
- **Test confidence**: Coverage tools like `pytest-cov` for line/branch coverage measurement
- **Changeability**: CI integration to measure churn over longer time windows
