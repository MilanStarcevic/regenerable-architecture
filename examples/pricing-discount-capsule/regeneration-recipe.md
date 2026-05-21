# Regeneration Recipe: Pricing Discount Capsule

## 1. Purpose

This capsule calculates the discount percentage applicable to a customer basket, given the
customer's loyalty tier, basket total, and whether an active promotional campaign is in effect.
Following this recipe produces a fresh `src/pricing_discount_service.py` that satisfies all durable
artifacts in this capsule. The generated implementation is the only artifact that does not need to
be preserved across regenerations.

---

## 2. Inputs

### Primary inputs (specify behavior)

These artifacts define what the implementation must do. The generated code must satisfy them in
full; they are not suggestions.

| Artifact | Role |
|---|---|
| `intent.md` | Business rules and rationale; the authoritative statement of what this capsule must do |
| `tests/test_acceptance.py` | Behavioral proof; the generated implementation must pass every test |
| `tests/test_invariants.py` | Property rules that must hold for all inputs; no exception to these |
| `tests/test_contract.py` | Contract conformance; verifies the response schema matches `ports/inbound/openapi.yaml` |

### Constraint inputs (constrain implementation choices)

These artifacts constrain how the implementation is structured without fully specifying it.

| Artifact | Role |
|---|---|
| `ports/inbound/openapi.yaml` | Defines the public function signature, input types, and response schema |
| `ports/outbound/dependencies.yaml` | Declares outbound dependencies — none for this capsule; confirms no external calls are needed |

---

## 3. Generation steps

Follow these steps in order. Each step is a concrete action, not a direction.

1. **Read `intent.md` in full.** Identify the five business rules (Gold tier, Silver tier, large
   basket, active campaign, maximum cap). Note the exact discount percentages and threshold values.
   These values appear verbatim in the implementation; do not paraphrase them.

2. **Read `ports/inbound/openapi.yaml`.** Extract the function signature:
   `calculate_discount(customer_tier: str, basket_total: float, active_campaign: bool) -> dict`.
   Extract the required response fields: `discount_percentage` (integer) and `explanation`
   (list of strings). These are non-negotiable.

3. **Read all test files.** Before generating anything, understand what each test asserts. The
   acceptance tests define the exact scenarios the implementation must handle. The invariant tests
   define rules that must hold for all inputs — the implementation must not violate these even in
   paths the acceptance tests do not explicitly exercise.

4. **Generate `src/pricing_discount_service.py`** to satisfy the following, in order of priority:
   - All invariant tests pass (these are the hardest constraints — no bypass is acceptable)
   - All acceptance tests pass
   - All contract tests pass
   - The implementation reads as a direct translation of `intent.md` — use the same vocabulary

5. **Apply the constraints in Section 4** before accepting the generated implementation. If the
   generated code violates any constraint, regenerate with an explicit instruction to avoid the
   violation.

6. **Run the verification steps in Section 5.** Do not skip them.

---

## 4. Constraints and prohibitions

These are hard rules. The implementation must not violate them, regardless of what the generator
produces.

1. **No external runtime dependencies.** The implementation must use only the Python standard
   library. Do not add `requests`, `httpx`, `pydantic`, `attrs`, `dacite`, or any other library.
   The existing test suite has no such dependencies and adding them would break the repo's
   dependency model.

2. **No caching of discount results.** Previous generations have introduced memoization or
   caching of discount calculations to pass a perceived performance test. There is no such
   performance test. Caching across requests introduces state that breaks the isolation guarantee
   that callers depend on.

3. **No abstraction beyond what the tests require.** Do not introduce a `DiscountRule` base
   class, a `RuleEngine`, a `DiscountPolicy` registry, or any data-driven dispatch mechanism. The
   five business rules are simple enough to be expressed as direct conditionals. Previous
   generations that introduced rule registries required the next regeneration to explain why the
   over-engineered structure existed — there was no good answer.

4. **The `explanation` field must use domain vocabulary from `intent.md`.** The explanation
   strings in the response are read by downstream consumers. They must use the same terminology as
   `intent.md`: "Gold customer discount", "Silver customer discount", "Large basket discount",
   "Campaign discount", "Maximum discount cap". Do not invent new names.

5. **Preserve the exact function signature.** `calculate_discount(customer_tier, basket_total,
   active_campaign)` is the public API. Do not rename parameters, add parameters with defaults,
   or change return types.

6. **Negative basket totals must raise `ValueError` before any discount calculation.** This is
   tested explicitly in `test_acceptance.py`. The validation must be the first line of the
   function body.

---

## 5. Verification

After regeneration, run these checks in order. Do not skip any.

1. **Run the full test suite:**
   ```bash
   python3 -m pytest examples/pricing-discount-capsule/tests/ -v
   ```
   Expected: all 43 tests pass. If any fail, the regeneration is incomplete.

2. **Run the signal dashboard:**
   ```bash
   python3 examples/pricing-discount-capsule/fitness/decay_dashboard.py
   ```
   Expected: `regeneration_indicated: false`. If any mechanical signal is in `warning` or
   `critical`, the generated implementation has accumulated unnecessary complexity or duplication.

3. **Run the artifact drift check:**
   ```bash
   python3 examples/pricing-discount-capsule/fitness/artifact_drift.py
   ```
   Expected: score below 16. A higher score means the recipe itself or another durable artifact
   needs attention.

4. **Read the generated implementation against `intent.md`.** Confirm:
   - The five discount rules are implemented in the order stated in `intent.md`
   - The exact discount percentages match (`intent.md`: Gold=10%, Silver=5%, large basket=3%, campaign=2%, cap=15%)
   - The `explanation` strings match the vocabulary in `intent.md`
   - No discount logic appears outside the main function

5. **Confirm no new imports were added:**
   ```bash
   python3 -c "import ast, pathlib; tree = ast.parse(pathlib.Path('examples/pricing-discount-capsule/src/pricing_discount_service.py').read_text()); imports = [n.names[0].name if isinstance(n, ast.Import) else n.module for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]; print(imports)"
   ```
   Expected: empty list or only stdlib modules.

---

## 6. Known regeneration hazards

These have occurred in prior regenerations or are predicted based on the capsule's structure. Update
this section after each regeneration cycle.

1. **[Predicted] Off-by-one on the large basket threshold.** `intent.md` specifies `basket total ≥
   500`. Generators frequently produce `basket_total > 500` (strict greater-than). The acceptance
   tests cover `basket_total = 500` explicitly, but if that test is somehow not run, this drift is
   silent. Verify this boundary explicitly after every regeneration.

2. **[Predicted] Discount cap applied before combining discounts.** The correct order is:
   sum all applicable discounts, then apply the 15% cap. Generators sometimes apply the cap after
   each individual discount, which changes the result for Gold customers with a large basket and
   active campaign (correct: 10+3+2=15 → capped at 15; incorrect: each individually capped,
   yielding a different intermediate path). `test_acceptance.py` covers the full-combination case;
   verify the cap is applied once, at the end.

3. **[Predicted] Explanation list populated when discount is zero.** When no discount applies, the
   explanation must be an empty list, not a list containing a "no discount" message. The invariant
   test `test_zero_discount_has_empty_explanation` covers this. Previous generators have added a
   "standard price" explanation string for the zero-discount case.

---

## 7. Last-regenerated metadata

| Field | Value |
|---|---|
| Date | *(update after each regeneration)* |
| Model | *(record the model used)* |
| Prompt version | `fitness-functions/prompts/semantic-drift.md` version 1.0 |
| Test result | *(record pass count)* |
| Dashboard result | *(record regeneration_indicated value)* |
| Notes | *(record anything unexpected)* |

---

## Pre-regeneration checklist

Before starting:

- [ ] `intent.md` reflects the current business intent and rules
- [ ] `ports/inbound/openapi.yaml` reflects the current public API
- [ ] `tests/test_acceptance.py` covers all behaviors described in `intent.md`
- [ ] `tests/test_invariants.py` covers all invariants (max cap, no negative discount)
- [ ] All tests pass against the current implementation
- [ ] Artifact drift score is below the block threshold (run `fitness/artifact_drift.py`)
- [ ] Signal dashboard status has been recorded for comparison after regeneration

Do not regenerate if durable artifacts have not been reviewed and confirmed as current.
Regenerating from outdated artifacts produces an implementation that satisfies outdated requirements.

---

## Example prompt for AI regeneration

```
Regenerate src/pricing_discount_service.py for the pricing-discount-capsule.

Read these files first:
  - intent.md
  - ports/inbound/openapi.yaml
  - ports/outbound/dependencies.yaml
  - tests/test_acceptance.py
  - tests/test_invariants.py
  - tests/test_contract.py

Requirements:
  - Function signature: calculate_discount(customer_tier: str, basket_total: float, active_campaign: bool) -> dict
  - Return: {"discount_percentage": int, "explanation": list[str]}
  - Validate negative basket_total first — raise ValueError before any discount logic
  - Implement all five business rules from intent.md in order
  - Apply the 15% cap after summing all applicable discounts, not before
  - Basket total >= 500 (not >) qualifies for the large basket discount
  - Explanation strings must use the vocabulary from intent.md
  - No external runtime dependencies beyond the Python standard library
  - No caching, no rule engines, no strategy patterns
  - All tests in tests/ must pass

Do not add features or behavior beyond what the tests and intent.md require.
```

---

## Known good state

The capsule is in a known good state when:

- All tests pass
- Signal dashboard shows all signals healthy
- The implementation vocabulary matches `intent.md` — "discount", "tier", "basket", "campaign", "explanation", "maximum"
- The implementation can be read and understood in under 10 minutes
