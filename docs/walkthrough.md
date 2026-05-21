# Walkthrough: One Regeneration Cycle

This document narrates a full regeneration cycle of the two-capsule system — pricing-discount-capsule
and order-capsule — across several months of production operation. It covers the dynamics the static
examples cannot show: decay accumulating, a detection decision, a pre-regeneration gate check, the
regeneration itself, what goes wrong, and what the aftermath looks like.

This is a scenario. The capsules and artifacts are the ones in this repository. The events are
constructed to be representative of what actually happens in production systems, not to be idealized.

---

## 1. Setup: five months in production

Both capsules have been in production for five months. In that time, pricing-discount-capsule has
received three feature additions:

- A `preferred_partner` tier was added, granting 7% discount. The rule was added to `intent.md`
  and the tests. The implementation was regenerated at that point and passed cleanly.

- A seasonal campaign override was added: when `active_campaign` is true and basket_total >= 1000,
  an additional 5% "high-value campaign" bonus applies. This was a late addition; it was implemented
  by editing the existing implementation rather than regenerating. The acceptance tests were updated.
  `intent.md` was not updated until two weeks later, by a different engineer.

- A minimum discount floor of 0% was made explicit (it was always 0% by implementation, but the
  invariant test was tightened to assert it explicitly after a question about edge cases in code
  review). No behavior changed, but a new invariant test was added.

Through this period, the regeneration recipe was not updated. It still describes the original five
discount rules. The "Known regeneration hazards" section still says "[Predicted] Off-by-one on the
large basket threshold" — no historical entry has been added because no failed regeneration has
occurred.

The order-capsule has not changed. It consumes pricing-discount-capsule at version 1.0 as declared
in `system.yaml`.

---

## 2. Detection: the signal dashboard

During the monthly architecture review, a team member runs `make fitness`. The pricing-discount-capsule
dashboard shows:

```json
{
  "signals": {
    "complexity": { "raw": 47.2, "status": "warning", ... },
    "duplication": { "raw": 9.9, "status": "healthy", ... },
    "dependency_accumulation": { "raw": 16.7, "status": "healthy", ... },
    "test_confidence": { "raw": 100.0, "status": "healthy", ... },
    "changeability": { "raw": 41.5, "status": "warning", ... },
    "semantic_drift": { "raw": 4.3, "status": "healthy", ..., "kind": "judgment" }
  },
  "regeneration_indicated": true,
  "policy_reason": "2 mechanical signals in warning: complexity, changeability"
}
```

Complexity is elevated because the high-value campaign addition was edited inline, adding two nested
conditionals to the already-branchy discount calculation. Changeability is elevated because the
file has been modified five times in the last twenty commits — the `intent.md` lag, the campaign
addition, two hotfixes for edge cases, and the test tightening.

The team considers the dashboard. The policy says regeneration is indicated: two mechanical signals
in `warning`. Before deciding, they run the pre-regeneration gate checks.

---

## 3. The pre-regeneration gate

The team runs two gate checks.

**Artifact drift check:**

```bash
python3 examples/pricing-discount-capsule/fitness/artifact_drift.py --verbose
```

The artifact drift score is 18 — above the block threshold of 16. The business rule parity check
flags a discrepancy: `intent.md` now has 7 business rules (the original 5 plus the preferred_partner
tier and the high-value campaign bonus), but `test_acceptance.py` has 38 test functions. The
rule-parity signal fires because the ratio is significantly imbalanced — 7 declared rules, but the
test count is roughly consistent with the original 5-rule structure. The recipe currency check
flags that `regeneration-recipe.md` still mentions five business rules and does not reference the
high-value campaign constraint.

The artifact drift score is above the block threshold. The team does not regenerate yet.

**Actions before regenerating:**

1. A team member updates `intent.md` to include the high-value campaign bonus rule clearly, with
   the threshold (basket_total >= 1000) stated precisely. They note this was already in the tests
   but missing from the intent.

2. The regeneration recipe is updated: the "Generation steps" section now explicitly says "implement
   the seven discount rules from `intent.md` in order" and adds the high-value campaign rule to the
   example prompt.

3. A new entry is added to "Known regeneration hazards": "[Predicted] Generator may apply the
   high-value campaign bonus before the 15% cap, producing a combined discount higher than 15%. The
   cap must be applied once, after all rules."

After these updates, the artifact drift score drops to 9 — below the block threshold.

**Semantic drift check:**

The team runs the LLM-judged semantic drift check at the gate:

```bash
python3 examples/pricing-discount-capsule/fitness/semantic_drift_check.py --llm
```

The LLM returns:

```json
{
  "drift_detected": false,
  "drifted_rules": [],
  "overall_confidence": "high",
  "rationale": "All seven business rules in intent.md are implemented correctly. The high-value campaign bonus applies correctly at basket_total >= 1000. The cap is applied after all discounts. No behavioral divergence detected."
}
```

The semantic drift check is clean. The team proceeds with regeneration.

---

## 4. Regeneration

The team follows the recipe. They delete `src/pricing_discount_service.py` and regenerate using
the updated recipe's example prompt, with the current `intent.md` and tests as context.

The recipe's instructions now include:

- Implement all seven business rules in the order stated in `intent.md`
- Apply the 15% cap after summing all applicable discounts
- The high-value campaign bonus applies only when `basket_total >= 1000` AND `active_campaign` is true
- The preferred_partner tier receives 7% (not 10%, not 5%)
- No caching, no rule engines
- The `explanation` strings must match `intent.md` vocabulary

The generator produces a clean implementation in one pass.

---

## 5. What goes wrong

The team runs the full test suite:

```bash
python3 -m pytest examples/pricing-discount-capsule/tests/ -v
```

43 tests pass. But then they run the order-capsule integration test:

```bash
python3 -m pytest examples/order-capsule/tests/test_integration.py -v
```

One test fails:

```
FAILED test_integration.py::TestRealDiscountIntegration::test_preferred_partner_order
AssertionError: expected discount_percentage 7, got 0
```

The order-capsule integration test is calling the real pricing-discount-capsule with
`customer_tier="preferred_partner"`. The test was written when the preferred_partner tier was added —
but it was added to the integration test file without updating the stub in
`ports/outbound/dependencies.yaml`. The stub still has only Gold and Silver stubs. The stub
consistency check would have caught this if it had been run as part of the gate, but it was not.

The team investigates. The integration test sends `customer_tier="preferred_partner"` to the real
service. The real service now returns `discount_percentage: 7`. But the order-capsule's
`dependencies.yaml` stub still returns `discount_percentage: 0` for that tier (the default
fallback). The stub is stale.

**Is this a deliberate contract change?** Yes. The pricing-discount-capsule's behavior now
correctly includes preferred_partner. The order-capsule's stub needs to be updated to reflect this.

**Recovery:**

1. Update `examples/order-capsule/ports/outbound/dependencies.yaml` to add a stub for
   `preferred_partner` returning `discount_percentage: 7`.

2. Re-run the stub consistency check to confirm alignment:
   ```bash
   python3 examples/order-capsule/fitness/stub_consistency_check.py
   ```

3. Re-run the full order-capsule test suite:
   ```bash
   python3 -m pytest examples/order-capsule/tests/ -v
   ```
   All tests pass, including integration.

---

## 6. Aftermath

The recipe is updated with two new entries in "Known regeneration hazards":

> **[Historical, 2026-05-21]** Regeneration of pricing-discount-capsule with a new tier (preferred_partner)
> did not automatically update the order-capsule's `dependencies.yaml` stub. Integration test caught
> the discrepancy. Fix: before regenerating, run the stub consistency check explicitly and update stubs
> for any new tier or behavior added since last regeneration.
>
> **[Historical, 2026-05-21]** `dependencies.yaml` stubs must be updated whenever a new customer tier
> is added to pricing-discount-capsule. The integration test for the new tier exists in order-capsule
> but was added without a corresponding stub update, making the test always pass in stub mode (using
> the default 0% fallback) while the real behavior is 7%. The stub consistency check gates this.

The signal dashboard for pricing-discount-capsule after regeneration:

```json
{
  "signals": {
    "complexity":  { "raw": 13.8, "status": "healthy" },
    "changeability": { "raw": 11.0, "status": "healthy" },
    ...
  },
  "regeneration_indicated": false,
  "policy_reason": "all signals within acceptable thresholds"
}
```

Both complexity and changeability have returned to healthy. The regenerated implementation is
clean and direct. The six-branch implementation that accumulated through five months of edits has
been replaced by a seven-branch implementation that is explicit, readable, and matches
`intent.md` exactly.

**Cost of this regeneration:**

- Pre-gate artifact updates: approximately 45 minutes (updating `intent.md`, updating the recipe)
- Regeneration itself: approximately 10 minutes (one pass, no failures in pricing-discount-capsule)
- Integration failure and recovery: approximately 30 minutes
- Recipe updates: approximately 15 minutes

Total: approximately 100 minutes for a regeneration that eliminated five months of accumulated
decay and produced two new recipe entries that will prevent the stub-drift failure from recurring.

A team that had maintained the durable artifacts more rigorously — updating `intent.md` when the
high-value campaign was added, updating the stub when the preferred_partner tier was added — would
have spent approximately 30 minutes on the regeneration, with no integration failure. The 70 minutes
of extra work was the cost of the artifact maintenance debt accumulated over five months.

Whether this was a good trade depends on the team's capacity and discipline. The pattern does not
eliminate maintenance costs. It concentrates them at regeneration time, where they are visible and
bounded, rather than spreading them invisibly across months of debugging sessions.
