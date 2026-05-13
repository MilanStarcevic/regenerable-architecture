# Regeneration Recipe: Pricing Discount Capsule

This document tells an AI coding tool—or a developer—how to regenerate `src/pricing_discount_service.py` from the durable artifacts in this capsule.

## When to Use This Recipe

Use this recipe when:

- The slop score for this capsule exceeds the regeneration threshold (default: 71)
- A significant requirement change makes the current implementation a poor foundation
- The implementation has drifted from intent and the drift is too widespread to fix by editing
- The generation tooling has improved and a fresh generation would produce meaningfully better code

Do not use this recipe if the durable artifacts (intent, tests, contracts) have not been reviewed and confirmed as current.

## Pre-Regeneration Checklist

Before running this recipe:

- [ ] `intent.md` is current and reflects the actual business intent
- [ ] `contracts/openapi.yaml` reflects the actual public API
- [ ] `tests/test_acceptance.py` covers all business behaviors in `intent.md`
- [ ] `tests/test_invariants.py` covers all invariants (max cap, no negative)
- [ ] All tests are currently passing against the old implementation
- [ ] The slop score has been measured and recorded for comparison after regeneration

## Source Artifacts

Regenerate `src/pricing_discount_service.py` from:

1. **`intent.md`** — business intent and durable rules
2. **`contracts/openapi.yaml`** — public API contract (input/output schema)
3. **`tests/test_acceptance.py`** — behavioral acceptance tests
4. **`tests/test_invariants.py`** — invariant tests (must all pass)
5. **`tests/test_contract.py`** — contract tests (must all pass)
6. **`fitness/slop_score.py`** — slop measurement (score must stay below threshold)

## Generation Rules

When regenerating the implementation, follow these rules:

1. **Preserve the public API contract.** The function signature `calculate_discount(customer_tier, basket_total, active_campaign)` must be preserved. The return schema must match `contracts/openapi.yaml`.

2. **Preserve all business behavior.** All rules in `intent.md` must be implemented. All acceptance tests in `test_acceptance.py` must pass.

3. **Do not introduce external runtime dependencies.** The implementation should use only Python standard library. Do not add `requests`, `httpx`, `pydantic`, or any other library unless it was already a dependency.

4. **Keep implementation simple.** Prefer explicit, readable rule evaluation over clever abstraction. The pricing rules are simple enough to be expressed as straightforward conditionals.

5. **Prefer explicit rule evaluation.** Do not represent rules as data structures, rule engines, or strategy patterns unless the number of rules genuinely requires it. A simple function with clear conditionals is preferred.

6. **All tests must pass.** `pytest examples/pricing-discount-capsule/tests/` must complete with zero failures.

7. **Slop score must stay below threshold.** After regeneration, run `python fitness-functions/slop_score.py examples/pricing-discount-capsule` and verify the score is below 50.

## Post-Regeneration Verification

After regenerating:

1. Run `pytest examples/pricing-discount-capsule/tests/` — all tests must pass
2. Run `python fitness-functions/slop_score.py examples/pricing-discount-capsule` — score must be below threshold
3. Manually review the implementation against `intent.md` for semantic alignment
4. Compare the output of the key test cases before and after regeneration
5. Update the slop score history in this document if maintaining a history

## Example Prompt for AI Regeneration

If using an AI coding tool, start with this prompt (adapt as needed):

```
Regenerate src/pricing_discount_service.py for the pricing-discount-capsule.

Read the following files first:
- intent.md
- contracts/openapi.yaml
- tests/test_acceptance.py
- tests/test_invariants.py

Rules:
- Function signature: calculate_discount(customer_tier: str, basket_total: float, active_campaign: bool) -> dict
- Return: {"discount_percentage": int, "explanation": list[str]}
- Implement all business rules from intent.md
- Keep the implementation simple and explicit
- No external runtime dependencies
- All tests in tests/ must pass

Do not add features beyond what the tests require.
```

## Known Good State Reference

The capsule is considered in a known good state when:

- All tests pass
- Slop score is below 30
- The implementation can be read and understood in under 10 minutes
- The implementation vocabulary matches the vocabulary in `intent.md`
