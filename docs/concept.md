# Concept: Regenerable Architecture

## The Central Insight

Most architectural thinking asks how to make systems easy to change. Regenerable Architecture asks a
different question: what if implementation did not need to survive at all, and the knowledge
required to recreate it was worth more than the code itself?

This is not a rhetorical position. It is a practical architectural stance made viable by AI-assisted
code generation.

## Why AI Changes the Calculus

Before AI coding tools, implementation was expensive. Refactoring was cheaper than rewriting.
Accumulated code was an asset because it represented investment.

AI changes this. Generating an implementation from a well-written specification is cheap. Writing a
trustworthy specification is not. Writing tests that genuinely capture business behavior is not.
Defining clear contracts and data semantics is not. When implementation is cheap, preserving a
degraded implementation at the expense of correctness is a bad trade.

## What Regenerable Architecture Preserves

The architecture preserves the **knowledge layer**: everything a competent engineer—or an AI tool
given clear instructions—would need to recreate the implementation correctly.

1. **Intent** — why the capsule exists, what business problem it solves, what it must never get wrong
2. **Contracts** — the public API commitment; what callers can rely on
3. **Behavioral tests** — proof of what the system must do, written against the contract and business intent, not against implementation details
4. **Invariants** — rules that must hold for all inputs, expressed as property tests or explicit assertions
5. **Data semantics** — what each field means, who owns it, how it relates to the domain
6. **Operational expectations** — SLOs, error budgets, performance baselines
7. **Regeneration recipe** — explicit instructions for how to recreate the implementation from the above, including prohibitions informed by what previous regenerations got wrong

## What Regenerable Architecture Discards

The architecture accepts that the **implementation layer** will periodically be discarded and
recreated:

1. **Generated implementation code** — the functions, classes, and modules that fulfill the contract
2. **Framework glue** — boilerplate that adapts the logic to a runtime or deployment target
3. **Local optimizations** — performance improvements that should be re-derived after regeneration, not carried forward from a decayed implementation

## The Lifecycle

```
Specify → Generate → Operate → Measure Decay Signals → Regenerate
```

**Specify**: Strengthen durable artifacts — contract first, tests first, intent explicit.
**Generate**: Produce an implementation from the durable artifacts using the regeneration recipe.
**Operate**: Run in production. **Measure**: Run fitness functions and evaluate the signal dashboard.
**Regenerate**: When the dashboard policy indicates regeneration, discard the implementation and
regenerate. Verify all tests pass.

## Ports: Inbound and Outbound Contracts

Every capsule has two contract surfaces, both durable:

**Inbound port** — what the capsule provides. The public API contract (`ports/inbound/openapi.yaml`)
that callers depend on. This is the commitment the capsule makes to the outside world. It must be
preserved across regenerations, and changes to it require versioning and consumer notification.

**Outbound port** — what the capsule consumes. A declaration (`ports/outbound/dependencies.yaml`) of
which other capsules this capsule calls, which operations it uses, and which response fields it
reads. This is equally durable: when the implementation is regenerated, the new code must satisfy
the same outbound contracts. The declaration also provides stub behaviours for unit tests, keeping
acceptance tests isolated from real dependencies.

This maps directly onto hexagonal architecture (ports and adapters):

| Hexagonal concept | Regenerable equivalent | Durability |
|---|---|---|
| Inbound port | `ports/inbound/openapi.yaml` | Durable |
| Outbound port | `ports/outbound/dependencies.yaml` | Durable |
| Inbound adapter | Framework glue receiving the call | Disposable |
| Outbound adapter | Client code calling another capsule | Disposable |
| Core / domain logic | Business implementation | Disposable |

### Extended Capsule Structure

```
capsule/
├── intent.md
├── regeneration-recipe.md
├── ports/
│   ├── inbound/
│   │   └── openapi.yaml          ← what this capsule provides
│   └── outbound/
│       └── dependencies.yaml     ← what this capsule consumes
├── tests/
│   ├── test_acceptance.py        ← uses stubs driven by outbound contract
│   ├── test_invariants.py
│   ├── test_contract.py
│   └── test_integration.py       ← verifies real adapter against live dependency
├── fitness/
└── src/                          ← disposable
```

A leaf capsule with no outbound dependencies (like `pricing-discount-capsule`) has an empty
`dependencies.yaml`. The structure is uniform regardless of complexity.

## Multi-Capsule Systems and the System Manifest

When capsules depend on each other, the dependency graph is a system-level durable artifact. A
`system.yaml` at the repository root declares all capsules and their relationships:

```yaml
capsules:
  - name: pricing-discount-capsule
    inbound_contract: ports/inbound/openapi.yaml
    inbound_version: "1.0"
    depends_on: []

  - name: order-capsule
    inbound_contract: ports/inbound/openapi.yaml
    inbound_version: "1.0"
    depends_on:
      - capsule: pricing-discount-capsule
        version: "1.0"
        operations: [calculateDiscount]
```

The manifest enables three things that are impossible without it:

1. **Impact analysis** — before regenerating any capsule, identify which consumers declare a dependency on it. Those consumers must re-run their integration tests after the regeneration.

2. **Safe sequencing** — when multiple capsules need regeneration, the manifest determines the order: dependencies before dependents.

3. **Contract compatibility checks** — the regenerated inbound contract must remain compatible with every consumer's declared version before the capsule can be safely deployed.

## Artifact Drift Fitness

Implementation decay fitness measures whether the implementation is decaying. Artifact drift fitness measures whether the artifacts from which we regenerate are still trustworthy.

A capsule can show a healthy signal dashboard and still be unsafe to regenerate. If `intent.md` has
drifted from the tests, the recipe references files that no longer exist, or a dependency has changed
behavior while the declared stubs have not — regeneration will produce a new, clean implementation
guided by wrong inputs. The tests will pass. The behavior will be wrong.

Artifact drift checks run in two tiers:

**Tier 1 — Mechanical (CI, always run):** Artifact completeness, recipe file integrity, contract
field coverage, business rule count parity, stub consistency. Fast, no external dependencies.

**Tier 2 — LLM-assisted (pre-regeneration gate):** Intent-test alignment, contract-intent alignment,
recipe currency. These require semantic judgment that pattern matching cannot provide.

The same two-tier structure applies to implementation decay fitness. The five mechanical signals
(complexity, duplication, dependency accumulation, test confidence, changeability) run continuously
in CI. Semantic drift — whether the implementation has behaviorally diverged from `intent.md` — is
a judgment signal that runs at the pre-regeneration gate, alongside the Tier 2 artifact drift
checks. Running it continuously would be expensive and would generate false positives as the
implementation evolves normally between regeneration cycles. At the gate, where a human team is
already reviewing the regeneration decision, the cost of an LLM call is justified.

A note on the evaluating LLM's reliability: the concern "how can you trust an LLM to evaluate
another LLM's output?" is reasonable, but the semantic drift check is a different task from
generation. The evaluating LLM is not generating behavior; it is comparing a specific implementation
against a specific `intent.md` that was written before the implementation existed. The ground truth
is fixed and external to the LLM. That is a significantly more constrained and verifiable task than
generation — and the structured output schema and confidence fields are designed to make the LLM's
reasoning auditable rather than opaque.

The two measures interact predictably:

| Signal Dashboard | Artifact Drift | Meaning |
|---|---|---|
| All healthy | Low | Healthy — maintain |
| Regeneration indicated | Low | Decayed implementation — regeneration safe and indicated |
| All healthy | High | Artifacts drifted — do not regenerate; strengthen artifacts first |
| Regeneration indicated | High | Most dangerous — regeneration needed but unsafe |

**Artifact drift must gate regeneration. The signal dashboard alone does not.**

See [fitness-functions/artifact-drift.md](../fitness-functions/artifact-drift.md) for the full
signal specification, score formula, and implementation guidance.

## The Regeneration Recipe

The regeneration recipe is the artifact that makes regeneration repeatable rather than ad hoc. It
contains: the explicit list of input artifacts (primary specifications and constraints); ordered,
concrete generation steps; a list of prohibited patterns; verification steps with expected outcomes;
and a "Known regeneration hazards" section that grows with each regeneration cycle.

The hazards section is the recipe's most valuable part. It captures what cannot be derived from
`intent.md` or the tests: the specific ways this particular capsule's generator has historically
failed. A recipe without a hazards section has not yet been used seriously. A recipe with three
historical hazard entries has been earned.

The recipe is the durable artifact; the LLM that reads it is the disposable executor. When a
regeneration fails because the LLM did not follow the recipe, the correct response is to strengthen
the recipe, not to retry with a better one-off prompt. The failure should be preventable in the
next regeneration.

See [`docs/regeneration-recipe-guide.md`](../docs/regeneration-recipe-guide.md) for guidance on
writing a good recipe.

## The Discipline Required

The safe path for both regeneration and refactoring is the same: strengthen the durable artifacts
first, then proceed. Durable artifacts must be maintained with the same rigor as code — when
business rules change, `intent.md`, tests, and the recipe change too. Tests must be behavioral, not
structural. Without this discipline, "regenerable" becomes a euphemism for undocumented rewrites.
