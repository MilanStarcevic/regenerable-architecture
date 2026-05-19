# Artifact Drift Fitness Functions

Artifact drift functions are automated checks that measure the internal consistency of the durable
artifact layer in a capability capsule. They answer a different question from implementation entropy fitness
functions: not "is the implementation decaying?" but "are the artifacts from which we regenerate
still trustworthy?"

This matters because a capsule can have a zero entropy score and still be unsafe to regenerate — if
`intent.md` has drifted from the tests, or the regeneration recipe points to files that no longer
exist, or a dependency's behavior has changed while the declared stubs have not. Implementation
fitness measures what was built. Artifact drift measures whether you could safely build it again.

This document defines:

1. **The interface contract** — what any artifact drift check must produce
2. **The two tiers** — mechanical checks and LLM-assisted checks, when to run each
3. **The eight signals** — what to measure, why it matters, and how to approach it
4. **The composite artifact drift score** — how signals combine into a regeneration gate
5. **The relationship to implementation entropy fitness** — how the two scores interact

---

## Interface Contract

Each artifact drift check takes a capsule directory as input and returns a JSON-compatible dict with
at minimum a `"score"` key:

```json
{
  "score": 0.0
}
```

- `score` is a float from 0 (fully consistent) to 100 (severely drifted)
- Additional keys provide supporting detail for diagnostics
- Any tool or script that produces this shape satisfies the interface

The composite artifact drift runner calls each check, combines scores using the formula below, and
outputs the aggregate result alongside a regeneration safety verdict.

---

## Two Tiers

Artifact drift checks divide into two tiers based on what they require to run.

### Tier 1 — Mechanical (always run)

Mechanical checks verify structural consistency. They do not interpret meaning; they verify that
references are valid, fields are covered, and counts are plausible. They run in milliseconds,
require no external services, and are suitable for CI on every commit.

Tier 1 checks: artifact completeness, recipe file integrity, contract field coverage, business rule
parity, stub consistency.

### Tier 2 — LLM-assisted (run before regeneration)

LLM-assisted checks verify semantic consistency. They interpret meaning: whether the tests actually
cover the intent, whether the contract faithfully represents the business rules, whether the recipe
is still accurate. They are slower, have external dependencies, and are appropriate as a
pre-regeneration gate rather than a continuous CI check.

Tier 2 checks: intent-test alignment, contract-intent alignment, recipe currency.

Both tiers use the same interface contract. A runner can execute them separately or together
depending on context.

---

## Artifact Drift Score Formula

```
Artifact Drift Score =
  artifact_completeness_score
+ recipe_integrity_score
+ contract_coverage_score
+ rule_parity_score
+ stub_consistency_score
+ intent_test_alignment_score     ← Tier 2, optional
+ contract_intent_alignment_score ← Tier 2, optional
+ recipe_currency_score           ← Tier 2, optional
```

Normalized to 0–100. All signals are additive penalties: a score of 0 means all checks pass.

| Score | Status | Action |
| --- | --- | --- |
| 0 | Fully consistent | Regeneration safe (subject to entropy threshold) |
| 1–15 | Minor drift | Investigate and resolve before next regeneration |
| 16–30 | Moderate drift | Resolve before regenerating; do not regenerate until addressed |
| 31–100 | Severe drift | Regeneration unsafe; strengthen durable artifacts first |

**The threshold for blocking regeneration is low.** A entropy score of 50 may still permit regeneration
with care. An artifact drift score of 20 should block it: artifacts that are wrong produce
implementations that are wrong in ways the tests will not catch. This is the failure mode the
architecture is specifically designed to avoid.

---

## The Eight Signals

### 1. Artifact Completeness

**What to measure:** Whether all required durable files are present in the capsule. Required files
are: `intent.md`, `regeneration-recipe.md`, `ports/inbound/openapi.yaml`,
`ports/outbound/dependencies.yaml`, `tests/test_acceptance.py`, `tests/test_invariants.py`,
`tests/test_contract.py`.

**Why it matters:** A capsule missing any of these is structurally not regenerable, regardless of
what the entropy score says. The regeneration recipe cannot be followed if the artifacts it references
do not exist. The score for this check is binary per file: each missing required artifact
contributes a fixed penalty.

**Approach:** Enumerate required paths. Check existence. Report missing files.

---

### 2. Recipe File Integrity

**What to measure:** Whether every file path explicitly referenced in `regeneration-recipe.md`
exists on disk. Recipe documents typically list source artifacts in structured sections ("Read these
files first:", "Source Artifacts:") and in the example prompt. Extract all path-like references and
verify each one.

**Why it matters:** Recipes drift silently. When the capsule is restructured — for example, moving
`contracts/openapi.yaml` to `ports/inbound/openapi.yaml` — the recipe may not be updated. A recipe
with broken paths will produce a failed regeneration attempt or, worse, a regeneration guided by the
wrong artifacts.

**Approach:** Parse the recipe for path references using pattern matching on common path forms
(forward slashes, file extensions, backtick-quoted strings). Verify each candidate path. Account for
paths relative to the capsule root and to the repository root.

---

### 3. Contract Field Coverage

**What to measure:** Whether every required field declared in the inbound OpenAPI contract has at
least one corresponding test in `test_contract.py`. Parse the contract's response schema for
`required` fields. Check whether each field name appears as a string literal in the contract test
file.

**Why it matters:** Contract tests are the specification of what callers can depend on. If the
contract declares a field and no test verifies it, that field is unverified behavior. When the
capsule is regenerated, the implementation may omit or mistype the field without any test catching
it.

**Approach:** Parse the OpenAPI YAML for `required` arrays in response schemas. For each required
field name, search `test_contract.py` for that string. Missing fields are penalized proportionally.

**Limitations:** String presence is a heuristic. A field named `status` may appear in the test file
without being meaningfully tested. Treat this as a floor, not a ceiling.

---

### 4. Business Rule Parity

**What to measure:** The ratio of business rules declared in `intent.md` to acceptance tests in
`test_acceptance.py`. Count rows in the `| Rule |` markdown table in `intent.md`. Count test methods
in `test_acceptance.py`.

**Why it matters:** A significant volume divergence — many rules, few tests, or many tests, few
declared rules — is a signal that intent and tests have drifted. Intent may have grown without tests
following, or tests may have been written for behavior not declared in intent. Neither case is safe
for regeneration.

**Approach:** Count table rows in `intent.md` under the business rules heading. Count `def test_`
occurrences in `test_acceptance.py`. Compute a ratio. Penalize significant divergence (more than
roughly 2:1 in either direction).

**Limitations:** This is a count signal, not a content signal. It catches volume drift, not semantic
drift. Semantic drift is addressed by intent-test alignment (Tier 2).

---

### 5. Stub Consistency

**What to measure:** Whether the stub behaviours declared in `ports/outbound/dependencies.yaml` are
consistent with what the real dependency currently returns. For each `stub_behaviours` entry, call
the real dependency with the declared inputs and compare the actual output to the declared stub
output.

**Why it matters:** This is the only check that crosses capsule boundaries. It detects when a
dependency has changed behavior and this capsule's declared expectations of it are now wrong. Unit
tests that use the stubs will continue to pass. Integration will silently break. The stub
consistency check surfaces this before any regeneration attempt exposes it in production.

**How stubs become stale:** The pricing-discount-capsule changes its discount for Gold customers
from 10% to 12%. It updates its own tests, passes, and is regenerated. The order-capsule's
`dependencies.yaml` still declares a stub that returns 10% for Gold customers. Order-capsule unit
tests pass. Its integration test (`test_integration.py`) would catch this — but only if it is run.
The stub consistency check catches it automatically, without running the integration test suite.

**Approach:** For each entry in `dependencies.yaml` `stub_behaviours`, invoke the real dependency
with the declared input and compare the response to the declared output field by field. Report
discrepancies by field. Score proportionally to the fraction of stubs that are inconsistent.

**Requirement:** The capsule's outbound adapter must be directly invocable in the check's runtime
environment. For Python capsules with in-process dependencies, this is straightforward. For
HTTP-based dependencies, the check requires a running instance and is more appropriately a
pre-deployment gate.

---

### 6. Intent-Test Alignment *(Tier 2)*

**What to measure:** Whether the acceptance tests in `test_acceptance.py` collectively cover all the
business rules declared in `intent.md`. For each rule in the intent document, verify that a
corresponding test exists — not by string matching, but by semantic understanding of what the rule
requires and what the test verifies.

**Why it matters:** This is the core semantic check that mechanical checks cannot perform. A capsule
can have a rule parity count of 1:1 and still have complete misalignment: every test covers one
rule, but it is the wrong rule for each. `intent.md` says "Gold customers receive 10%"; the test
says "discount is non-negative." Both are present, both pass, neither validates the other.

**Approach:** Provide the LLM with `intent.md` and `test_acceptance.py`. Ask it to map each business
rule to the tests that verify it, identify rules with no coverage, and identify tests that verify
behavior not declared in intent. Return a structured assessment: rules fully covered, rules
partially covered, rules not covered, tests without intent backing.

**Score:** Penalize proportionally to uncovered rules and tests without intent backing. A capsule
where 20% of business rules have no test coverage should score significantly above zero.

---

### 7. Contract-Intent Alignment *(Tier 2)*

**What to measure:** Whether the inbound OpenAPI contract faithfully represents the business intent
declared in `intent.md`. Check for divergence in: field semantics (a field type or range that
contradicts the intent), missing business concepts (a rule in intent that has no representation in
the contract schema or examples), and contract claims that exceed what intent declares.

**Why it matters:** The contract is what callers depend on. If it diverges from intent, regeneration
will produce an implementation that satisfies the contract but not the intent — or satisfies the
intent but breaks callers who rely on the contract. Both are failures. The contract should be a
faithful translation of intent into a machine-readable form; this check verifies that translation.

**Approach:** Provide the LLM with `intent.md` and `ports/inbound/openapi.yaml`. Ask whether the
contract schema, field descriptions, constraints, and examples are consistent with the business
rules and invariants in intent. Ask whether any business rule is missing from the contract and
whether any contract claim has no basis in intent.

---

### 8. Recipe Currency *(Tier 2)*

**What to measure:** Whether `regeneration-recipe.md` accurately reflects the current state of the
capsule's durable artifacts and generation constraints. A recipe becomes stale when: new required
artifacts are added but not mentioned, the capsule structure changes, a new invariant is added to
`intent.md` without being reflected in the generation rules, or a new outbound dependency is
declared without being captured in the prompt.

**Why it matters:** The recipe is the instructions given to an AI tool during regeneration. A stale
recipe produces a generation that misses constraints or reads from the wrong sources. This is
particularly dangerous because the failure is silent: the AI follows the recipe faithfully and
produces an implementation that satisfies the recipe, not the current reality.

**Approach:** Provide the LLM with the current capsule structure (file listing), `intent.md`,
`ports/inbound/openapi.yaml`, `ports/outbound/dependencies.yaml`, and `regeneration-recipe.md`. Ask
whether the recipe's source artifacts list is complete, whether its generation rules reflect the
current constraints, and whether the example prompt would produce a correct implementation given the
current durable artifacts.

---

## Relationship to Implementation Entropy Fitness

The two scores measure orthogonal things and should be read together, not averaged.

| Entropy Score | Artifact Drift Score | Meaning |
| --- | --- | --- |
| Low | Low | Healthy. Maintain. |
| High | Low | Implementation has decayed. Regeneration is safe and indicated. |
| Low | High | Implementation looks healthy but artifacts are drifted. **Do not regenerate.** Strengthen durable artifacts first. |
| High | High | Most dangerous state. Regeneration is needed but unsafe. Strengthen durable artifacts first, then regenerate. |

The high implementation entropy / high artifact drift case is the failure mode the architecture most needs to protect
against. An undisciplined team facing this condition is tempted to regenerate because the entropy is
high. The regeneration fails silently: a new, clean implementation guided by inconsistent artifacts.
The result is an implementation that passes old tests, satisfies a drifted contract, and does not
match current business intent.

**Artifact drift must gate regeneration. Entropy scores alone do not.**

---

## Using SonarQube and Existing Tools

Existing tools do not directly address artifact drift. SonarQube, ESLint, and similar tools measure
implementation quality. The signals described here require reading and interpreting durable
artifacts, which no general-purpose static analysis tool currently does.

| Signal | Existing tool coverage |
| --- | --- |
| Artifact completeness | File system checks — trivially implementable without tooling |
| Recipe file integrity | Custom check only |
| Contract field coverage | Partial: OpenAPI validators check contract syntax, not test coverage |
| Business rule parity | Custom check only |
| Stub consistency | Custom check only; consumer-driven contract tools (Pact) address a related problem |
| Intent-test alignment | LLM-assisted only; no existing tool addresses this directly |
| Contract-intent alignment | LLM-assisted only |
| Recipe currency | LLM-assisted only |

The Tier 1 checks are straightforward to implement in any language that can parse YAML, markdown,
and file paths. The Tier 2 checks require an LLM API call and a structured prompt. See the
implementation guidance in each capsule's `regeneration-recipe.md` for the `claude -p` pattern used
in this repository.

---

## Reference Implementation

Working Python implementations of all five Tier 1 checks live in both example capsules:

| Check | File |
| --- | --- |
| Artifact completeness | `examples/pricing-discount-capsule/fitness/artifact_completeness_check.py` |
| Recipe integrity | `examples/pricing-discount-capsule/fitness/recipe_integrity_check.py` |
| Contract field coverage | `examples/pricing-discount-capsule/fitness/contract_coverage_check.py` |
| Business rule parity | `examples/pricing-discount-capsule/fitness/rule_parity_check.py` |
| Stub consistency (no deps) | `examples/pricing-discount-capsule/fitness/stub_consistency_check.py` |
| Stub consistency (with deps) | `examples/order-capsule/fitness/stub_consistency_check.py` |

The composite runner `artifact_drift.py` imports all five checks, applies the weights defined in
this document, and outputs the regeneration safety verdict:

```
python3 examples/pricing-discount-capsule/fitness/artifact_drift.py [--verbose]
python3 examples/order-capsule/fitness/artifact_drift.py [--verbose]
```

The `pricing-discount-capsule` implementation is the simpler reference (leaf capsule, no outbound
dependencies). The `order-capsule` implementation shows stub consistency verification against a real
upstream capsule.

The Tier 2 checks require an LLM and are demonstrated in `scripts/regenerate-example.sh` via `claude
-p`. The interface contract above applies to both tiers.
