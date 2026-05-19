# Regeneration Recipe: Order Capsule

This document tells an AI coding tool—or a developer—how to regenerate `src/order_service.py` from the durable artifacts in this capsule.

## When to Use This Recipe

Use this recipe when:

- The entropy score for this capsule exceeds the regeneration threshold (default: 71)
- A significant requirement change makes the current implementation a poor foundation
- The implementation has drifted from intent broadly enough that targeted editing is riskier than a clean start
- The generation tooling has improved and a fresh generation would produce meaningfully better code

Do not use this recipe if the durable artifacts (intent, tests, contracts) have not been reviewed and confirmed as current. Regenerating from outdated artifacts produces an implementation that satisfies outdated requirements.

## Pre-Regeneration Checklist

Before regenerating:

- [ ] `intent.md` reflects the current business intent and rules
- [ ] `ports/inbound/openapi.yaml` reflects the current public API
- [ ] `ports/outbound/dependencies.yaml` reflects the current outbound dependencies
- [ ] `tests/test_acceptance.py` covers all behaviours described in `intent.md`
- [ ] `tests/test_invariants.py` covers all invariants (final total non-negative, discount applied once)
- [ ] `tests/test_integration.py` passes against the real pricing-discount-capsule
- [ ] All tests pass against the current implementation
- [ ] The entropy score has been recorded for comparison after regeneration

Additionally, verify system-level safety before regenerating:

- [ ] `system.yaml` at the repository root is current
- [ ] No downstream capsule depends on this capsule's inbound contract with a version that this regeneration will break
- [ ] If `ports/outbound/dependencies.yaml` has changed, re-run `tests/test_integration.py` against the real dependencies after regeneration

## Source Artifacts

Regenerate `src/order_service.py` from:

1. **`intent.md`** — business intent and durable rules
2. **`ports/inbound/openapi.yaml`** — public API contract (input/output schema)
3. **`ports/outbound/dependencies.yaml`** — outbound dependencies and stub behaviours
4. **`tests/test_acceptance.py`** — behavioural acceptance tests
5. **`tests/test_invariants.py`** — invariant tests (must all pass)
6. **`tests/test_contract.py`** — contract conformance tests (must all pass)

## Generation Rules

1. **Preserve the public API.** The `build_order_service(discount_service)` factory signature must be preserved. It returns `(place_order, get_order)`. The return schema must match `ports/inbound/openapi.yaml`.

2. **Honour the outbound port.** The `discount_service` parameter is the sole point of contact with the pricing-discount-capsule. Never call `calculate_discount` directly from the implementation. Never compute discounts inline. The stub behaviours in `ports/outbound/dependencies.yaml` document what the implementation may expect from the adapter.

3. **Preserve all business behaviour.** All rules in `intent.md` must be implemented. All acceptance and invariant tests must pass.

4. **Isolate storage per service instance.** Each call to `build_order_service` must return an isolated order store. Tests depend on this isolation.

5. **No new external runtime dependencies.** The implementation uses only the Python standard library. Do not add `requests`, `httpx`, `pydantic`, or any other library.

6. **Keep the implementation explicit and simple.** No rule engines, no strategy patterns, no abstractions the tests do not require.

7. **All tests must pass.** `python3 -m pytest examples/order-capsule/tests/` must complete with zero failures.

8. **Entropy score must remain below threshold.** Run `python3 fitness/entropy_score.py` from the capsule directory and confirm the score is below 50.

## Post-Regeneration Verification

1. Run `python3 -m pytest examples/order-capsule/tests/` — all tests must pass, including `test_integration.py`
2. Run `python3 fitness/entropy_score.py` from the capsule directory — score must be below threshold
3. Read the new implementation against `intent.md` and confirm the vocabulary matches
4. Confirm the `discount_service` parameter is the only point of contact with the pricing-discount-capsule

## Example Prompt for AI Regeneration

Start with this prompt when using an AI coding tool (adapt paths as needed):

```
Regenerate src/order_service.py for the order-capsule.

Read these files first:
  - intent.md
  - ports/inbound/openapi.yaml
  - ports/outbound/dependencies.yaml
  - tests/test_acceptance.py
  - tests/test_invariants.py

Requirements:
  - Expose a build_order_service(discount_service) factory that returns (place_order, get_order)
  - place_order(customer_tier, basket_total, active_campaign, items) -> dict
  - get_order(order_id) -> dict | None
  - discount_service is the sole outbound adapter: call it exactly once per order placement
  - final_total = basket_total - (basket_total * discount_percentage / 100), floored at 0.0
  - Each build_order_service call gets isolated in-memory storage
  - No external runtime dependencies beyond the Python standard library
  - All tests in tests/ must pass

Do not add features or behaviour beyond what the tests and intent.md require.
```

## Known Good State

The capsule is in a known good state when:

- All tests pass, including integration tests
- Entropy score is below 30
- The implementation vocabulary matches `intent.md` — "order", "basket", "discount", "final", "total", "explanation", "items", "campaign"
- The `discount_service` parameter is the only reference to the pricing-discount-capsule in the implementation
- The implementation can be read and understood in under 10 minutes
