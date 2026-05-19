# Fitness Functions — Pricing Discount Capsule

This directory contains the reference Python implementation of the implementation entropy fitness function interface for this capsule.

See [fitness-functions/README.md](../../../../fitness-functions/README.md) for the language-agnostic interface specification, the six entropy signals, and equivalent tools for other stacks (SonarQube, ESLint, Roslyn analyzers, etc.).

## Files

| File | Purpose |
|---|---|
| `entropy_score.py` | Composite score runner — calls all six checks and outputs the aggregate result |
| `complexity_check.py` | Structural complexity: function length, branch count, nesting depth |
| `duplication_check.py` | Repeated lines and duplicate code blocks |
| `dependency_check.py` | Import health: count, external dependencies, discouraged libraries |
| `test_confidence_check.py` | Test quality: count, acceptance tests, invariants, pass status |
| `semantic_drift_check.py` | Alignment between implementation vocabulary and `intent.md` |
| `changeability_check.py` | Churn history and TODO/FIXME comment count |

## Running

From the repository root:

```bash
python3 examples/pricing-discount-capsule/fitness/entropy_score.py
```

From this capsule directory:

```bash
python3 fitness/entropy_score.py
```

With per-check detail:

```bash
python3 fitness/entropy_score.py --verbose
```

Run an individual check:

```bash
python3 fitness/complexity_check.py
python3 fitness/semantic_drift_check.py
```

## Expected Result

A healthy capsule with 43 passing tests:

```json
{
  "complexity_score": 11.3,
  "duplication_score": 12.1,
  "dependency_score": 12.3,
  "semantic_drift_score": 4.3,
  "changeability_score": 0.0,
  "test_confidence_score": 100.0,
  "entropy_score": 0,
  "status": "healthy",
  "recommended_action": "maintain"
}
```

## Adapting for Other Languages

These implementations are Python-specific. To implement the same checks for a different stack:

1. Each check must return `{"score": float, ...}` where score is 0–100
2. Wire your checks into a composite runner that applies the entropy score formula
3. See [fitness-functions/README.md](../../../../fitness-functions/README.md) for tool recommendations per signal
