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
7. **Regeneration recipe** — explicit instructions for how to recreate the implementation from the above

## What Regenerable Architecture Discards

The architecture accepts that the **implementation layer** will periodically be discarded and
recreated:

1. **Generated implementation code** — the functions, classes, and modules that fulfill the contract
2. **Framework glue** — boilerplate that adapts the logic to a runtime or deployment target
3. **Local optimizations** — performance improvements that should be re-derived after regeneration, not carried forward from a decayed implementation

## The Lifecycle

```
Specify → Generate → Operate → Measure Entropy → Regenerate
```

**Specify**: Strengthen durable artifacts — contract first, tests first, intent explicit.
**Generate**: Produce an implementation from the durable artifacts using the regeneration recipe.
**Operate**: Run in production. **Measure Entropy**: Run fitness functions and compute a entropy score.
**Regenerate**: When the entropy score crosses the threshold, discard the implementation and
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

Implementation entropy fitness measures whether the implementation is decaying. Artifact drift fitness measures whether the artifacts from which we regenerate are still trustworthy.

A capsule can have a zero entropy score and still be unsafe to regenerate. If `intent.md` has drifted
from the tests, the recipe references files that no longer exist, or a dependency has changed
behavior while the declared stubs have not — regeneration will produce a new, clean implementation
guided by wrong inputs. The tests will pass. The behavior will be wrong.

Artifact drift checks run in two tiers:

**Tier 1 — Mechanical (CI, always run):** Artifact completeness, recipe file integrity, contract
field coverage, business rule count parity, stub consistency. Fast, no external dependencies.

**Tier 2 — LLM-assisted (pre-regeneration gate):** Intent-test alignment, contract-intent alignment,
recipe currency. These require semantic judgment that pattern matching cannot provide.

The two scores interact predictably:

| Entropy Score | Artifact Drift | Meaning |
|---|---|---|
| Low | Low | Healthy — maintain |
| High | Low | Decayed implementation — regeneration safe and indicated |
| Low | High | Artifacts drifted — do not regenerate; strengthen artifacts first |
| High | High | Most dangerous — regeneration needed but unsafe |

**Artifact drift must gate regeneration. Entropy scores alone do not.**

See [fitness-functions/artifact-drift.md](../fitness-functions/artifact-drift.md) for the full
signal specification, score formula, and implementation guidance.

## The Discipline Required

The safe path for both regeneration and refactoring is the same: strengthen the durable artifacts
first, then proceed. Durable artifacts must be maintained with the same rigor as code — when
business rules change, `intent.md`, tests, and the recipe change too. Tests must be behavioral, not
structural. Without this discipline, "regenerable" becomes a euphemism for undocumented rewrites.
