# Concept: Regenerable Architecture

## The Central Insight

Most architectural thinking asks how to make systems easy to change. Regenerable Architecture asks a different question: what if implementation did not need to survive at all, and the knowledge required to recreate it was worth more than the code itself?

This is not a rhetorical position. It is a practical architectural stance made viable by AI-assisted code generation.

## Why AI Changes the Calculus

Before AI coding tools, implementation was expensive. Writing a service from scratch required significant engineering time. Refactoring was cheaper than rewriting. Accumulated code was an asset—even mediocre code—because it represented investment.

AI changes this. Generating an implementation from a well-written specification is cheap. Writing a trustworthy specification is not. Writing tests that genuinely capture business behavior is not. Defining clear contracts and data semantics is not.

This shifts the value distribution:

| Asset | Traditional Cost | AI-Assisted Cost |
|---|---|---|
| Writing implementation | High | Low |
| Writing specification | Medium | Medium (still human) |
| Writing behavioral tests | Medium | Medium (still human) |
| Defining contracts | Medium | Medium (still human) |
| Understanding data semantics | High | High (still human) |

When implementation is cheap, preserving a degraded implementation at the expense of correctness is a bad trade.

## What Regenerable Architecture Preserves

The architecture preserves the **knowledge layer**: everything a competent engineer—or an AI tool given clear instructions—would need to recreate the implementation correctly.

1. **Intent** — why the capsule exists, what business problem it solves, what it must never get wrong
2. **Contracts** — the public API commitment; what callers can rely on
3. **Behavioral tests** — proof of what the system must do, written against the contract and business intent, not against implementation details
4. **Invariants** — rules that must hold for all inputs, expressed as property tests or explicit assertions
5. **Data semantics** — what each field means, who owns it, how it relates to the domain
6. **Operational expectations** — SLOs, error budgets, performance baselines
7. **Regeneration recipe** — explicit instructions for how to recreate the implementation from the above

## What Regenerable Architecture Discards

The architecture accepts that the **implementation layer** will periodically be discarded and recreated:

1. **Generated implementation code** — the functions, classes, and modules that fulfill the contract
2. **Framework glue** — boilerplate that adapts the logic to a runtime or deployment target
3. **Local optimizations** — performance improvements that should be re-derived after regeneration, not carried forward from a decayed implementation

## The Lifecycle

```
Specify → Generate → Operate → Measure Slop → Regenerate
```

Each phase has a clear purpose:

**Specify**: Define or strengthen the durable artifacts before generating. Contract first. Tests first. Intent explicit.

**Generate**: Use AI tools to produce an implementation from the durable artifacts. The regeneration recipe provides the instructions.

**Operate**: Run in production. Observe behavior. Collect metrics.

**Measure Slop**: Run fitness functions. Evaluate complexity, duplication, dependencies, semantic drift, and test confidence. Compute a slop score.

**Regenerate**: When the slop score crosses the threshold, discard the implementation and regenerate from the preserved durable artifacts. Verify that all tests pass and the fitness score returns to healthy.

## When to Regenerate vs Refactor

Regeneration is preferable to refactoring when:

- Slop has accumulated beyond the configured threshold
- The implementation has diverged from intent broadly enough that targeted edits are riskier than a clean start
- A significant requirement change makes the existing structure a poor foundation for the new behavior
- The generation tooling has improved enough that a fresh generation produces meaningfully better code

Refactoring is preferable when:

- The slop score is moderate and the change is localized
- There is institutional knowledge in the current implementation that has not yet been captured in durable artifacts
- The durable artifacts are not strong enough to guide a safe regeneration

The safe path is the same in both cases: strengthen the durable artifacts first, then proceed.

## The Discipline Required

Regenerable Architecture is not a license to delete code carelessly. It requires genuine discipline:

- Durable artifacts must be maintained with the same rigor as code. When business rules change, `intent.md`, tests, and the regeneration recipe change too.
- Tests must be behavioral—verifying what the system does from the outside—not structural tests of how it does it.
- Contracts must be explicit, versioned, and updated when behavior changes.
- Data ownership must be clear before any capsule is considered disposable.

Without this discipline, "regenerable" becomes a euphemism for undocumented rewrites.
