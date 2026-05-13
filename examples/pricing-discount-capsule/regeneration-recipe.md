# Regeneration Recipe: Pricing Discount Capsule

This document tells an AI coding tool—or a developer—how to regenerate `src/pricing_discount_service.py` from the durable artifacts in this capsule.

## When to Use This Recipe

Use this recipe when:

- The slop score for this capsule exceeds the regeneration threshold (default: 71)
- A significant requirement change makes the current implementation a poor foundation
- The implementation has drifted from intent broadly enough that targeted editing is riskier than a clean start
- The generation tooling has improved and a fresh generation would produce meaningfully better code

Do not use this recipe if the durable artifacts (intent, tests, contracts) have not been reviewed and confirmed as current. Regenerating from outdated artifacts produces an implementation that satisfies outdated requirements.

## Pre-Regeneration Checklist

Before regenerating:

- [ ] `intent.md` reflects the current business intent and rules
- [ ] `contracts/openapi.yaml` reflects the current public API
- [ ] `tests/test_acceptance.py` covers all behaviors described in `intent.md`
- [ ] `tests/test_invariants.py` covers all invariants (max cap, no negative discount)
- [ ] All tests pass against the current implementation
- [ ] The slop score has been recorded for comparison after regeneration

## Source Artifacts

Regenerate `src/pricing_discount_service.py` from:

1. **`intent.md`** — business intent and durable rules
2. **`contracts/openapi.yaml`** — public API contract (input/output schema)
3. **`tests/test_acceptance.py`** — behavioral acceptance tests
4. **`tests/test_invariants.py`** — invariant tests (must all pass)
5. **`tests/test_contract.py`** — contract conformance tests (must all pass)

## Generation Rules

1. **Preserve the public API.** The function signature `calculate_discount(customer_tier, basket_total, active_campaign)` must be preserved. The return schema must match `contracts/openapi.yaml`.

2. **Preserve all business behavior.** All rules in `intent.md` must be implemented. All acceptance and invariant tests must pass.

3. **No new external runtime dependencies.** The implementation uses only the Python standard library. Do not add `requests`, `httpx`, `pydantic`, or any other library.

4. **Keep the implementation explicit and simple.** Prefer straightforward conditionals over rule engines, strategy patterns, or data-driven dispatch. The pricing rules are simple enough to be expressed directly. Do not add abstractions the tests do not require.

5. **All tests must pass.** `python3 -m pytest examples/pricing-discount-capsule/tests/` must complete with zero failures.

6. **Slop score must remain below threshold.** Run `python3 fitness-functions/slop_score.py examples/pricing-discount-capsule` and confirm the score is below 50.

## Post-Regeneration Verification

1. Run `python3 -m pytest examples/pricing-discount-capsule/tests/` — all tests must pass
2. Run `python3 fitness-functions/slop_score.py examples/pricing-discount-capsule` — score must be below threshold
3. Read the new implementation against `intent.md` and confirm the vocabulary matches
4. Confirm the explanation strings in the output match the rules described in `intent.md`

## Example Prompt for AI Regeneration

Start with this prompt when using an AI coding tool (adapt paths as needed):

```
Regenerate src/pricing_discount_service.py for the pricing-discount-capsule.

Read these files first:
  - intent.md
  - contracts/openapi.yaml
  - tests/test_acceptance.py
  - tests/test_invariants.py

Requirements:
  - Function signature: calculate_discount(customer_tier: str, basket_total: float, active_campaign: bool) -> dict
  - Return: {"discount_percentage": int, "explanation": list[str]}
  - Implement all business rules from intent.md
  - Keep the implementation simple and explicit — no rule engines or strategy patterns
  - No external runtime dependencies beyond the Python standard library
  - All tests in tests/ must pass

Do not add features or behavior beyond what the tests and intent.md require.
```

## Known Good State

The capsule is in a known good state when:

- All tests pass
- Slop score is below 30
- The implementation vocabulary matches `intent.md` — "discount", "tier", "basket", "campaign", "explanation", "maximum"
- The implementation can be read and understood in under 10 minutes
