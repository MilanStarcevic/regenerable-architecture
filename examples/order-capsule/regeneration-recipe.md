# Regeneration Recipe: Order Capsule

## 1. Purpose

This capsule places customer orders. It accepts a customer tier, basket total, campaign flag, and
item list; delegates discount calculation to the pricing-discount-capsule via a declared outbound
port; and returns a confirmed order with a final total. Following this recipe produces a fresh
`src/order_service.py` that satisfies all durable artifacts in this capsule. Because this capsule
has an outbound dependency, regeneration requires additional steps to verify the adapter against the
real dependency.

---

## 2. Inputs

### Primary inputs (specify behavior)

| Artifact | Role |
|---|---|
| `intent.md` | Business rules and rationale; defines what the capsule must do |
| `tests/test_acceptance.py` | Behavioral proof using a stub discount service; must all pass |
| `tests/test_invariants.py` | Property rules for all inputs; must hold without exception |
| `tests/test_contract.py` | Contract conformance; verifies the response schema |
| `tests/test_integration.py` | Verifies the real outbound adapter against the live pricing-discount-capsule |

### Constraint inputs (constrain implementation choices)

| Artifact | Role |
|---|---|
| `ports/inbound/openapi.yaml` | Defines the public API: `place_order` signature and response schema |
| `ports/outbound/dependencies.yaml` | Declares the dependency on pricing-discount-capsule, stub behaviours, and which response fields the implementation consumes |
| `system.yaml` (repository root) | Declares the dependency graph; use this to verify contract version compatibility before regenerating |

---

## 3. Generation steps

Follow these steps in order.

1. **Read `intent.md` in full.** Identify the five business rules: delegate discount to the
   pricing-discount-capsule (never inline), apply the final total formula, floor at zero, reject
   empty items, reject negative basket totals.

2. **Read `ports/inbound/openapi.yaml`.** Extract the factory signature:
   `build_order_service(discount_service) -> (place_order, get_order)`. Extract the `place_order`
   and `get_order` signatures and response schemas.

3. **Read `ports/outbound/dependencies.yaml`.** Note exactly which fields the implementation may
   read from the discount service response: `discount_percentage` and `explanation`. Do not read
   any other fields — they are not declared in the outbound contract.

4. **Read all test files**, including `test_integration.py`. The acceptance tests use a stub
   discount service injected via `build_order_service`. The integration test uses the real capsule.
   Understand both before generating.

5. **Generate `src/order_service.py`** to satisfy the following:
   - `build_order_service(discount_service)` is the only public entry point
   - Each call to `build_order_service` returns an isolated in-memory order store (tests depend on this)
   - `discount_service` is called exactly once per `place_order` invocation
   - The final total formula is `basket_total - (basket_total * discount_percentage / 100)`, floored at 0.0
   - The `discount_service` parameter is the sole point of contact with pricing-discount-capsule

6. **Apply the constraints in Section 4** before accepting the generated implementation.

7. **Run the verification steps in Section 5.** The integration test requires the
   pricing-discount-capsule to be reachable. See Section 5 for how to handle this.

---

## 4. Constraints and prohibitions

1. **`discount_service` is the sole outbound adapter.** The implementation must never import from
   `pricing_discount_service` directly. Never call `calculate_discount` as a module import.
   Never compute discount logic inline. The `discount_service` callable is the entire interface.
   This constraint exists because the acceptance tests inject a stub, and anything that bypasses
   the injection breaks test isolation.

2. **No caching of discount results or order results.** Previous generations have cached the
   result of `discount_service` for a given set of inputs, reasoning that repeated identical calls
   are redundant. This breaks the observable contract: callers expect that placing two orders with
   the same inputs produces two separate order records, not a cached response.

3. **Each `build_order_service` call gets isolated storage.** The in-memory order store must be
   local to the closure returned by `build_order_service`. A shared module-level dict would cause
   test interference — tests that check order isolation would fail, and the failure mode is
   non-obvious.

4. **No retry logic around the discount service call.** Retry policy is the caller's
   responsibility, not the order capsule's. A generator that adds retry logic around the
   `discount_service` call is violating the single-responsibility boundary. If the discount service
   is unavailable, the `place_order` call should fail immediately.

5. **No external runtime dependencies.** The implementation uses only the Python standard library.

6. **Preserve the exact factory signature.** `build_order_service(discount_service)` returns
   `(place_order, get_order)`. Do not add parameters, change the return type, or wrap the factory
   in a class.

---

## 5. Verification

### 5a. Unit verification (no external dependencies)

```bash
python3 -m pytest examples/order-capsule/tests/ --ignore=examples/order-capsule/tests/test_integration.py -v
```

All non-integration tests must pass before proceeding to integration verification.

### 5b. Integration verification (requires pricing-discount-capsule)

```bash
python3 -m pytest examples/order-capsule/tests/test_integration.py -v
```

This test imports the real `pricing_discount_service.calculate_discount` and wires it via
`build_order_service`. If it fails after regeneration, the generated outbound adapter is not
consuming the real dependency correctly. Common causes:

- The implementation is reading response fields not declared in `ports/outbound/dependencies.yaml`
- The implementation is passing arguments to `discount_service` in the wrong order or type
- The implementation is calling `discount_service` more or fewer times than expected per order

### 5c. Signal dashboard

```bash
python3 examples/order-capsule/fitness/decay_dashboard.py
```

Expected: `regeneration_indicated: false`.

### 5d. Artifact drift check

```bash
python3 examples/order-capsule/fitness/artifact_drift.py
```

Expected: score below 16.

### 5e. Read the implementation against `intent.md`

Confirm:
- `discount_service` is called exactly once per `place_order`
- The final total formula matches `intent.md` exactly
- `get_order` returns None for unknown order IDs (not raises)
- Empty items list is rejected with a clear error before the discount call
- Negative basket total is rejected before any other logic

---

## 6. Handling the outbound dependency during regeneration

### Which port to consume

The implementation must consume `ports/outbound/dependencies.yaml`, not the pricing-discount-capsule
implementation directly. During regeneration, provide the stub from `dependencies.yaml` to the
generator explicitly:

```
discount_service accepts: (customer_tier: str, basket_total: float, active_campaign: bool)
discount_service returns: {"discount_percentage": int, "explanation": list[str]}
Read only discount_percentage and explanation. Do not read any other fields.
```

### Stub for acceptance tests

The acceptance tests already inject a stub via `build_order_service(stub_discount)`. The stub
must match the outbound contract signature exactly. If the generated implementation changes the
calling convention for `discount_service`, the stub-based tests will fail before integration tests
are even reached.

### Contract version compatibility

Before regenerating, verify that the pricing-discount-capsule's inbound contract version declared
in `system.yaml` is compatible with the version order-capsule expects:

```yaml
# system.yaml — order-capsule depends_on:
- capsule: pricing-discount-capsule
  version: "1.0"
```

If pricing-discount-capsule has been regenerated since the last order-capsule regeneration, check
whether its inbound contract changed. If the contract version bumped, update `dependencies.yaml`
and `system.yaml` before regenerating order-capsule, then re-run `test_integration.py` to verify
compatibility.

### If the pricing-discount-capsule contract has changed since last regeneration

1. Run `python3 examples/order-capsule/fitness/stub_consistency_check.py` to identify whether the
   declared stubs in `dependencies.yaml` still match the real pricing-discount-capsule responses.
2. If stubs have drifted, update `dependencies.yaml` to match the new contract behavior.
3. Review whether the change is backward-compatible. If not, consult `system.yaml` to identify
   all other consumers before proceeding.
4. Re-run `test_integration.py` to confirm the real adapter works with the updated contract.
5. Update the `version` field in `dependencies.yaml` and `system.yaml` to reflect the new
   dependency version.

---

## 7. Known regeneration hazards

1. **[Predicted] Generator imports `calculate_discount` directly instead of using the injected
   callable.** This is the most common failure in early regenerations. The generator sees
   `pricing_discount_service.calculate_discount` referenced in tests or context and infers it should
   be imported directly. The acceptance tests will still pass if the stub is not used — but the
   integration tests will also pass, masking the violation. The violation is detected when tests are
   run in isolation without the pricing-discount-capsule available. Add an explicit instruction:
   "Do not import from pricing_discount_service. Use only the discount_service parameter."

2. **[Predicted] Shared order store across `build_order_service` calls.** When a generator uses
   a module-level dict or a class attribute instead of a closure-local dict, tests that call
   `build_order_service` multiple times will interfere with each other. The symptom is that tests
   pass individually but fail when the full suite runs. The fix is explicit: use a `dict` created
   inside the factory function, captured by the returned closures.

3. **[Predicted] `discount_service` called with keyword arguments.** The stub in
   `dependencies.yaml` is a positional interface. Some generators call `discount_service(tier=...,
   total=..., campaign=...)` using keyword arguments, which fails if the stub or real service does
   not accept them. The calling convention must be positional.

---

## 8. Last-regenerated metadata

| Field | Value |
|---|---|
| Date | *(update after each regeneration)* |
| Model | *(record the model used)* |
| Prompt version | `fitness-functions/prompts/semantic-drift.md` version 1.0 |
| Test result | *(record pass count, including integration)* |
| Dashboard result | *(record regeneration_indicated value)* |
| Notes | *(record anything unexpected)* |

---

## Pre-regeneration checklist

Before starting:

- [ ] `intent.md` reflects the current business intent and rules
- [ ] `ports/inbound/openapi.yaml` reflects the current public API
- [ ] `ports/outbound/dependencies.yaml` reflects the current outbound dependencies
- [ ] `tests/test_acceptance.py` covers all behaviours described in `intent.md`
- [ ] `tests/test_invariants.py` covers all invariants (final total non-negative, discount applied once)
- [ ] `tests/test_integration.py` passes against the real pricing-discount-capsule
- [ ] All tests pass against the current implementation
- [ ] Artifact drift score is below the block threshold
- [ ] Signal dashboard status has been recorded for comparison after regeneration

Additionally, verify system-level safety:

- [ ] `system.yaml` at the repository root is current
- [ ] No downstream capsule depends on this capsule's inbound contract with a version that this regeneration will break
- [ ] Stub consistency check confirms `dependencies.yaml` stubs match current pricing-discount-capsule responses

---

## Example prompt for AI regeneration

```
Regenerate src/order_service.py for the order-capsule.

Read these files first:
  - intent.md
  - ports/inbound/openapi.yaml
  - ports/outbound/dependencies.yaml
  - tests/test_acceptance.py
  - tests/test_invariants.py
  - tests/test_contract.py

Requirements:
  - Expose build_order_service(discount_service) factory that returns (place_order, get_order)
  - place_order(customer_tier, basket_total, active_campaign, items) -> dict
  - get_order(order_id) -> dict | None
  - discount_service is the ONLY contact point with pricing-discount-capsule
  - Do NOT import from pricing_discount_service — use only the injected discount_service parameter
  - Call discount_service exactly once per place_order with positional args: (customer_tier, basket_total, active_campaign)
  - final_total = basket_total - (basket_total * discount_percentage / 100), floored at 0.0
  - Each build_order_service call gets isolated in-memory storage (closure-local dict, not module-level)
  - Reject empty items list and negative basket_total before calling discount_service
  - No external runtime dependencies beyond the Python standard library
  - No retry logic, no caching, no strategy patterns
  - All tests in tests/ must pass

Do not add features or behaviour beyond what the tests and intent.md require.
```
