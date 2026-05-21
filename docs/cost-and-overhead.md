# Cost and Overhead

Regenerable Architecture carries a real, ongoing documentation tax. This document describes that
tax honestly, identifies when paying it is worth it, and names the failure mode that results from
paying it without the benefit.

---

## What the pattern costs

Per capsule, the team must create and maintain:

- `intent.md` — updated whenever business rules change
- An inbound contract (`ports/inbound/openapi.yaml`) — updated when the API changes
- An outbound port declaration (`ports/outbound/dependencies.yaml`) — updated when dependencies change
- Behavioral acceptance tests — updated with every new business rule
- Invariant tests — updated when business invariants change
- Contract conformance tests — updated with the contract
- Integration tests — updated when the outbound adapter's expected behavior changes
- Data semantics documentation — maintained alongside any canonical data
- Operational SLOs — reviewed when performance expectations change
- A regeneration recipe — updated after every failed regeneration and whenever new prohibitions are discovered
- Signal dashboard thresholds — recalibrated as the team's baseline improves

All of this must stay current with business changes. A durable artifact that has not been updated
to reflect the current state of the domain is not durable — it is stale documentation that will
produce a wrong implementation when the recipe is followed.

---

## The implicit bet

The pattern's bet is that the cost of maintaining this durable layer is less than the cost of
debugging, refactoring, or rewriting decayed AI-generated code at a high rate. This is not always
true.

The bet pays off when:

- Regeneration cycles occur often enough that the investment in the durable layer is amortized
- The domain is stable enough that durable artifacts have a useful half-life between updates
- AI-generated code is a meaningful share of the implementation, and decay accumulates observably
- Behavioral correctness matters more than time to first commit

The bet does not pay off when:

- The team is small enough that one engineer holds the full system in memory and can rewrite it
  end-to-end faster than maintaining the artifact layer
- The product is in early discovery and intent itself is unstable — what the capsule is supposed
  to do changes weekly
- Regeneration is rare because the codebase is small and infrequently changed
- AI tools are used lightly, and decay accumulates slowly enough that ordinary refactoring handles it

---

## The regeneration recipe costs the most

Of all the durable artifacts, the regeneration recipe is the most expensive to maintain well —
and the one teams under-maintain most often.

The recipe is not a template that can be written once and reused. It accumulates value only through
actual regeneration experience. A recipe that has never been tested against a failed regeneration
contains only speculation about what could go wrong. A recipe that has been through three
regeneration cycles contains hard-won knowledge about what does go wrong.

Teams under-maintain the recipe in two ways:
1. They fail to update the "Known regeneration hazards" section after a failed regeneration —
   preferring to move on rather than to encode the lesson.
2. They treat the recipe as documentation of the current state rather than as instructions for
   the next regeneration — so it becomes a description of what was done, not what should be done.

The recipe is worth its maintenance cost when it prevents failures that would otherwise recur. It
is not worth its cost when it is consulted only in theory and never in practice.

---

## The failure mode: overhead without benefit

The worst outcome is adopting the pattern but not maintaining the durable layer. This produces a
capsule with `intent.md`, tests, and a recipe — but all three are stale. The implementation has
evolved through refactoring and editing, and the durable artifacts were never updated to reflect it.

When regeneration is attempted from these artifacts, it produces an implementation that:
- Satisfies the outdated requirements documented in `intent.md`
- Passes the stale tests (which verify old behavior, not current behavior)
- Follows a recipe that forbids patterns for reasons that no longer apply

The team now has implementation decay from the old code and artifact decay from the stale
documentation — the worst of both worlds. The regeneration overhead was paid. The regeneration
safety was not.

The anti-pattern is **Durable Artifact Neglect** — see
[docs/anti-patterns.md](anti-patterns.md). The only defense against it is treating durable
artifact updates as required steps in every change that affects behavior. Not optional, not
deferred, not "we'll update the docs later."

