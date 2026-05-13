# Concept: Regenerable Architecture

## The Central Insight

Software architecture has always grappled with the tension between change and stability. Most architectural thinking attempts to make change safe: loose coupling, dependency inversion, modular design, evolutionary architecture.

Regenerable Architecture asks a different question:

> What if the implementation did not need to survive at all? What if the knowledge needed to recreate it was more valuable than the implementation itself?

This is not a rhetorical question. It is a practical architectural position made viable by AI-assisted code generation.

## Why AI Changes the Calculus

Before AI coding tools, implementation was expensive. Writing a service from scratch required human-hours. Refactoring was cheaper than rewriting. Accumulated code was an asset—even bad code—because it represented time invested.

AI changes this. The cost of generating an implementation from a good specification is low. The cost of producing a trustworthy specification is not. The cost of writing tests that actually capture business behavior is not. The cost of defining clear contracts and data semantics is not.

This shifts the value distribution:

| Asset | Traditional Cost | AI-Assisted Cost |
|---|---|---|
| Writing implementation | High | Low |
| Writing specification | Medium | Medium (still human) |
| Writing behavioral tests | Medium | Medium (still human) |
| Defining contracts | Medium | Medium (still human) |
| Understanding data semantics | High | High (still human) |

When implementation is cheap, preserving implementation at the expense of correctness is a bad trade.

## What Regenerable Architecture Preserves

The architecture preserves the **knowledge layer**: everything a competent engineer—or a capable AI with good instructions—would need to recreate the implementation correctly.

This includes:

1. **Intent** — why the capsule exists, what business problem it solves, what it must never get wrong
2. **Contracts** — the public API commitment; what callers can rely on
3. **Behavioral tests** — proof of what the system must do, written against the contract and intent, not the implementation
4. **Invariants** — rules that must never be violated, expressed as property tests or explicit assertions
5. **Data semantics** — what each field means, who owns it, how it relates to the domain
6. **Operational expectations** — SLOs, error budgets, performance baselines
7. **Regeneration recipe** — explicit instructions for how to recreate the implementation from the above

## What Regenerable Architecture Discards

The architecture accepts that the **implementation layer** will be discarded and recreated:

1. **Generated implementation code** — the functions, classes, and modules that fulfill the contract
2. **Framework glue** — boilerplate that adapts the logic to a framework, runtime, or deployment target
3. **Local optimizations** — performance improvements that should be re-derived after regeneration

## The Lifecycle

```
Specify → Generate → Operate → Measure Slop → Regenerate
```

Each phase has a clear purpose:

**Specify**: Define or strengthen the durable artifacts before generating. Tests first. Contract first. Intent explicit.

**Generate**: Use AI tools to produce an implementation from the durable artifacts. The regeneration recipe guides the generation.

**Operate**: Run in production. Observe behavior. Collect metrics.

**Measure Slop**: Run fitness functions. Evaluate complexity, duplication, dependencies, semantic drift, and test confidence. Compute a slop score.

**Regenerate**: When the slop score crosses the threshold, discard the implementation and regenerate from the preserved durable artifacts.

## When Is Regeneration the Right Choice?

Regeneration is preferable to refactoring when:

- Slop has accumulated beyond the configured threshold
- The implementation has diverged far enough from intent that surgery is riskier than a clean start
- A significant requirement change makes the existing structure a poor foundation
- The generation tooling has improved enough that a fresh generation would produce meaningfully better code
- The team has strengthened the durable artifacts and wants to validate that regeneration works

Refactoring is preferable when:

- The slop score is moderate and the change is localized
- There is institutional knowledge in the current implementation that has not been captured in durable artifacts
- The durable artifacts are not yet strong enough to guide a safe regeneration

## The Discipline Required

Regenerable Architecture is not a license to delete code carelessly. It requires genuine discipline:

- Durable artifacts must be maintained with the same rigor as code
- Tests must be behavioral, not just structural
- Contracts must be explicit and versioned
- Data ownership must be clear before any capsule is disposable
- The regeneration recipe must be updated whenever intent changes

Without this discipline, "regenerable" becomes a euphemism for "undocumented rewrites."
