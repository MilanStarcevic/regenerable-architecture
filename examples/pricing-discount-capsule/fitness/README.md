# Fitness Functions — Pricing Discount Capsule

This directory contains the reference Python implementation of the implementation decay fitness function interface for this capsule.

See [fitness-functions/README.md](../../../../fitness-functions/README.md) for the language-agnostic interface specification, the decay signals, and equivalent tools for other stacks (SonarQube, ESLint, Roslyn analyzers, etc.).

## Files

| File | Purpose |
|---|---|
| `decay_dashboard.py` | Signal dashboard runner — calls all six checks and outputs the per-signal status |
| `complexity_check.py` | Structural complexity: function length, branch count, nesting depth |
| `duplication_check.py` | Repeated lines and duplicate code blocks |
| `dependency_check.py` | Import health: count, external dependencies, discouraged libraries |
| `test_confidence_check.py` | Test quality: count, acceptance tests, invariants, pass status |
| `semantic_drift_check.py` | Alignment between implementation vocabulary and `intent.md` |
| `changeability_check.py` | Churn history and TODO/FIXME comment count |

## Running

From the repository root:

```bash
python3 examples/pricing-discount-capsule/fitness/decay_dashboard.py
```

From this capsule directory:

```bash
python3 fitness/decay_dashboard.py
```

With per-check detail:

```bash
python3 fitness/decay_dashboard.py --verbose
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
  "signals": {
    "complexity":              { "raw": 14.1,  "status": "healthy", "note": "5 file(s); 22 branches; max nesting 3" },
    "duplication":             { "raw": 9.9,   "status": "healthy", "note": "no duplicate blocks or lines detected" },
    "dependency_accumulation": { "raw": 16.7,  "status": "healthy", "note": "1 external import(s)" },
    "test_confidence":         { "raw": 100.0, "status": "healthy", "note": "43 tests; acceptance tests present; invariant tests present" },
    "changeability":           { "raw": 13.0,  "status": "healthy", "note": "no deferred markers; low recent churn" },
    "semantic_drift":          { "raw": 4.3,   "status": "healthy", "note": "vocabulary match: 93%; invariants covered", "kind": "judgment" }
  },
  "regeneration_indicated": false,
  "policy_reason": "all signals within acceptable thresholds"
}
```

## Adapting for Other Languages

These implementations are Python-specific. To implement the same checks for a different stack:

1. Each check must return `{"score": float, ...}` where score is 0–100
2. Wire your checks into a dashboard runner that maps each score to a status level
3. See [fitness-functions/README.md](../../../../fitness-functions/README.md) for tool recommendations per signal
