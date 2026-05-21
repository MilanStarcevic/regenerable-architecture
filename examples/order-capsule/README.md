# Order Capsule

**Role in the two-capsule pair:** Dependent capsule. Consumes the pricing-discount-capsule via a
declared outbound port. This is the more complex of the two examples. It shows outbound port
declarations, stub-driven acceptance tests, integration tests against a real dependency, and how
the system manifest captures inter-capsule relationships. It does not show how the minimal leaf
capsule structure looks — see the pricing-discount-capsule for that.

---

A working example of a **multi-capsule system** in Regenerable Architecture.

This capsule places customer orders and delegates discount calculation to the
`pricing-discount-capsule` via a declared outbound port. It demonstrates:

- **Outbound dependency declaration** — `ports/outbound/dependencies.yaml` records what this capsule consumes and how
- **Stub-driven unit tests** — acceptance tests inject a stub that satisfies the outbound contract, keeping tests isolated
- **Integration tests** — `tests/test_integration.py` verifies the real adapter against the live pricing-discount-capsule
- **Stateful capsule** — owns order records as canonical data (in-memory for this example)

See `system.yaml` at the repository root for the full dependency graph.

## Capsule Contents

| File | Layer | Purpose |
|---|---|---|
| `intent.md` | **Durable** | Business intent and rules |
| `regeneration-recipe.md` | **Durable** | Step-by-step instructions for regenerating the implementation |
| `ports/inbound/openapi.yaml` | **Durable** | Public API contract; callers depend on this |
| `ports/outbound/dependencies.yaml` | **Durable** | Outbound dependencies and stub behaviours |
| `tests/test_acceptance.py` | **Durable** | Behavioural tests using a stub discount service |
| `tests/test_invariants.py` | **Durable** | Invariants that must hold for all inputs |
| `tests/test_contract.py` | **Durable** | Contract conformance tests |
| `tests/test_integration.py` | **Durable** | Integration tests against the real pricing-discount-capsule |
| `fitness/` | **Durable** | Fitness function implementations |
| `src/order_service.py` | **Disposable** | Generated implementation |

## Business Rules

| Rule | Behaviour |
|---|---|
| Delegate discount | Always call the pricing-discount-capsule; never calculate inline |
| Final total formula | `final_total = basket_total − (basket_total × discount% ÷ 100)` |
| Final total floor | Floored at 0.00; never negative |
| Minimum one item | Empty items list is rejected |
| Non-negative basket | Negative basket_total is rejected |

## Running the Tests

```bash
# Unit tests only (uses stub discount service)
python3 -m pytest examples/order-capsule/tests/ --ignore=examples/order-capsule/tests/test_integration.py -v

# All tests including integration (requires pricing-discount-capsule)
python3 -m pytest examples/order-capsule/tests/ -v
```

## Running the Fitness Functions

```bash
python3 examples/order-capsule/fitness/decay_dashboard.py
```

## How the Outbound Port Works

The implementation never imports from the pricing-discount-capsule directly.
Instead, `build_order_service` accepts a `discount_service` callable:

```python
# Production: wire the real capsule
from pricing_discount_service import calculate_discount
place_order, get_order = build_order_service(calculate_discount)

# Tests: inject a stub satisfying the outbound contract
def stub_discount(tier, total, campaign):
    return {"discount_percentage": 10, "explanation": ["Gold: 10%"]}

place_order, get_order = build_order_service(stub_discount)
```

The outbound port contract (`ports/outbound/dependencies.yaml`) declares exactly what
the implementation may expect from `discount_service`: the inputs it sends and the
response fields it consumes. This contract drives both the stub and the integration tests.

## What Makes This Capsule Regenerable

If you deleted `src/order_service.py` and followed the regeneration recipe:

- The durable artifacts fully specify the implementation
- Unit tests verify all business behaviour without touching the pricing-discount-capsule
- Integration tests verify the real adapter after regeneration
- The outbound port declaration constrains the regenerated implementation to the same integration surface

The implementation is the only artifact that does not need to be preserved.
