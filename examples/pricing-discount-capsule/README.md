# Pricing Discount Capsule

A working example of a **capability capsule** in Regenerable Architecture.

This capsule calculates the discount percentage for a customer basket.
It is intentionally simple—the point is to demonstrate the architectural lifecycle, not business complexity.

## Capsule Contents

| File | Layer | Purpose |
|---|---|---|
| `intent.md` | **Durable** | Business intent and rules |
| `regeneration-recipe.md` | **Durable** | How to regenerate the implementation |
| `contracts/openapi.yaml` | **Durable** | Public API contract |
| `tests/test_acceptance.py` | **Durable** | Behavioral acceptance tests |
| `tests/test_invariants.py` | **Durable** | Invariant tests (must always hold) |
| `tests/test_contract.py` | **Durable** | Contract conformance tests |
| `fitness/slop_score.py` | **Durable** | Capsule-local slop measurement |
| `src/pricing_discount_service.py` | **Disposable** | Generated implementation |

## Business Rules

| Rule | Condition | Discount |
|---|---|---|
| Gold loyalty | Customer tier = Gold | +10% |
| Silver loyalty | Customer tier = Silver | +5% |
| Large basket | Basket total ≥ 500 | +3% |
| Active campaign | active_campaign = true | +2% |
| Maximum cap | Combined total > 15% | capped at 15% |

## Running Tests

```bash
pytest examples/pricing-discount-capsule/tests/
```

## Running Fitness Functions

```bash
python fitness-functions/slop_score.py examples/pricing-discount-capsule
```

## Example Usage

```python
from examples.pricing_discount_capsule.src.pricing_discount_service import calculate_discount

result = calculate_discount("gold", 600.0, True)
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

## The Lifecycle

This capsule is a demonstration of the regenerable lifecycle:

1. **Intent** was defined in `intent.md` before any code was written.
2. **Contract** was defined in `contracts/openapi.yaml`.
3. **Tests** were written to specify behavior (acceptance, invariants, contract).
4. **Implementation** was generated to satisfy the tests.
5. **Fitness functions** can be run at any time to measure slop accumulation.
6. When slop exceeds the threshold, the `regeneration-recipe.md` guides safe regeneration.

## What Makes This Capsule Regenerable

- All business rules are in `intent.md`
- All behavioral requirements are in tests
- The contract is explicit in `openapi.yaml`
- The regeneration recipe tells an AI tool exactly what to do
- Fitness functions will catch implementation drift

If you deleted `src/pricing_discount_service.py` right now and followed the regeneration recipe, all tests would pass with the regenerated implementation.
