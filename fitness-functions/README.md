# Fitness Functions

This directory contains the slop measurement fitness functions for Regenerable Architecture.

## Overview

Fitness functions are automated checks that evaluate whether a capability capsule meets the architectural health goals defined for it. In Regenerable Architecture, they measure **AI slop**—the accumulated quality decay in generated implementations—and determine whether the slop score has crossed the threshold that triggers regeneration.

## Files

| File | Purpose |
|---|---|
| `slop_score.py` | Aggregator: runs all checks and produces a composite score |
| `complexity_check.py` | Structural complexity: function length, branch count, nesting depth |
| `duplication_check.py` | Repeated lines and duplicate code blocks |
| `dependency_check.py` | Import health: count, external dependencies, discouraged libraries |
| `test_confidence_check.py` | Test quality: count, acceptance tests, invariants, pass status |
| `semantic_drift_check.py` | Alignment between implementation vocabulary and `intent.md` |
| `changeability_check.py` | Churn history and TODO/FIXME comment count |

## Usage

Run the composite score against a capsule directory:

```bash
python3 fitness-functions/slop_score.py examples/pricing-discount-capsule
```

With per-check detail:

```bash
python3 fitness-functions/slop_score.py examples/pricing-discount-capsule --verbose
```

Run an individual check:

```bash
python3 fitness-functions/complexity_check.py examples/pricing-discount-capsule
python3 fitness-functions/duplication_check.py examples/pricing-discount-capsule
python3 fitness-functions/dependency_check.py examples/pricing-discount-capsule
python3 fitness-functions/test_confidence_check.py examples/pricing-discount-capsule
python3 fitness-functions/semantic_drift_check.py examples/pricing-discount-capsule
python3 fitness-functions/changeability_check.py examples/pricing-discount-capsule
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

Normalized to 0–100. Test confidence is subtracted: strong tests reduce the risk that structural decay has caused undetected behavioral drift.

| Score | Status | Action |
|---|---|---|
| 0–30 | Healthy | Maintain |
| 31–50 | Watch | Monitor trends |
| 51–70 | Warning | Refactor |
| 71–85 | High | Regenerate |
| 86–100 | Critical | Urgent regeneration |

## Exit Codes

- `0`: Score below regeneration threshold
- `1`: Score at or above regeneration threshold (71+)
- `2`: Usage error

## Extending the Fitness Functions

To add a new check:

1. Create a new `*_check.py` file in this directory
2. Implement `check_directory(directory: str | Path) -> dict` returning a `"score"` key (0–100)
3. Import and call it in `slop_score.py`
4. Add it to the formula with a weight that reflects its relative importance

## Limitations

These implementations are heuristics designed to demonstrate the concept and produce meaningful signals for the example capsule. For production use, consider:

- **Complexity**: `radon cc` or `flake8-cognitive-complexity` for accurate cyclomatic complexity
- **Duplication**: `pylint` similarity checker or dedicated clone-detection tools
- **Semantic drift**: LLM-assisted review comparing `intent.md` to observed implementation behavior
- **Test confidence**: `pytest-cov` for line and branch coverage metrics
- **Changeability**: CI-integrated churn metrics over longer windows than the local git log
