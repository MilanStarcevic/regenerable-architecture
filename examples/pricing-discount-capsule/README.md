# Pricing Discount Capsule

A working example of a **capability capsule** in Regenerable Architecture.

This capsule calculates the discount percentage for a customer basket. It is intentionally simple—the point is to demonstrate the architectural lifecycle, not business complexity. A capsule in a real system would have the same structure but more sophisticated behavior.

## Capsule Contents

| File | Layer | Purpose |
|---|---|---|
| `intent.md` | **Durable** | Business intent and rules—the source of truth |
| `regeneration-recipe.md` | **Durable** | Step-by-step instructions for regenerating the implementation |
| `contracts/openapi.yaml` | **Durable** | Public API contract; callers depend on this |
| `tests/test_acceptance.py` | **Durable** | Behavioral tests against the public API |
| `tests/test_invariants.py` | **Durable** | Invariants that must hold for all inputs |
| `tests/test_contract.py` | **Durable** | Contract conformance tests |
| `fitness/slop_score.py` | **Durable** | Capsule-local fitness runner |
| `src/pricing_discount_service.py` | **Disposable** | Generated implementation |

The durable layer survives regeneration. The disposable layer does not need to.

## Business Rules

| Rule | Condition | Discount |
|---|---|---|
| Gold loyalty | Customer tier = Gold | +10% |
| Silver loyalty | Customer tier = Silver | +5% |
| Large basket | Basket total ≥ 500 | +3% |
| Active campaign | active_campaign = true | +2% |
| Maximum cap | Combined total ≥ 15% | capped at 15% |

See `intent.md` for the business rationale behind each rule.

## Running the Tests

From the repository root:

```bash
python3 -m pytest examples/pricing-discount-capsule/tests/ -v
```

Expected result: 43 tests pass across acceptance, invariant, and contract test suites.

## Running the Fitness Functions

```bash
python3 fitness-functions/slop_score.py examples/pricing-discount-capsule
```

Expected result: slop score of 0 (healthy), with `test_confidence_score` of 100 reflecting the comprehensive test coverage.

## Example Output

```python
from examples.pricing_discount_capsule.src.pricing_discount_service import calculate_discount

result = calculate_discount("gold", 600.0, True)
print(result)
# {
#     "discount_percentage": 15,
#     "explanation": [
#         "Gold customer discount applied: 10%",
#         "Large basket discount applied: 3%",
#         "Campaign discount applied: 2%",
#         "Maximum discount cap applied: 15%"
#     ]
# }
```

## The Lifecycle in This Capsule

1. **Specify** — `intent.md` and `contracts/openapi.yaml` were defined before any implementation was written
2. **Generate** — `src/pricing_discount_service.py` was generated to satisfy the tests and contract
3. **Operate** — the capsule runs; fitness functions measure slop
4. **Measure** — `make fitness` produces a composite slop score
5. **Regenerate** — when slop exceeds the threshold, `regeneration-recipe.md` guides safe regeneration

## What Makes This Capsule Regenerable

If you deleted `src/pricing_discount_service.py` right now and followed the regeneration recipe, the regenerated implementation would pass all 43 tests. The durable artifacts contain everything needed to produce a correct implementation:

- The business rules are in `intent.md`
- The API shape is in `contracts/openapi.yaml`
- The behavioral requirements are in `tests/test_acceptance.py`
- The invariants are in `tests/test_invariants.py`
- The generation instructions are in `regeneration-recipe.md`

The implementation is the only artifact that does not need to be preserved.
